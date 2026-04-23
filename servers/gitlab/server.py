#!/usr/bin/env python3
"""
GitLab MCP Server

API Info:
- API License: CC BY-SA 4.0 (https://gitlab.com/gitlab-org/gitlab/-/blob/master/LICENSE)
- Terms of Service: https://about.gitlab.com/terms/

Generated: 2026-04-23 21:19:47 UTC
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
    "gitlab_host": os.getenv("SERVER_GITLAB_HOST", ""),
}
BASE_URL = os.getenv("BASE_URL", "https://{gitlab_host}/api/v4".format_map(collections.defaultdict(str, _SERVER_VARS)))
SERVER_NAME = "GitLab"
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
    'ApiKeyAuth',
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
try:
    _auth_handlers["ApiKeyAuth"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="Private-Token")
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

mcp = FastMCP("GitLab", middleware=[_JsonCoercionMiddleware()])

# Tags: badges
@mcp.tool()
async def get_group_badge(
    id_: str = Field(..., alias="id", description="The ID or URL-encoded path of the group. This identifies which group owns the badge you want to retrieve."),
    badge_id: str = Field(..., description="The unique identifier of the badge within the group."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a specific badge belonging to a group. This allows you to fetch details about a badge that has been assigned to a group."""

    _badge_id = _parse_int(badge_id)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4GroupsIdBadgesBadgeIdRequest(
            path=_models.GetApiV4GroupsIdBadgesBadgeIdRequestPath(id_=id_, badge_id=_badge_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_group_badge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}/badges/{badge_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}/badges/{badge_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_group_badge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_group_badge", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_group_badge",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: badges
@mcp.tool()
async def update_group_badge(
    id_: str = Field(..., alias="id", description="The ID or URL-encoded path of the group owned by the authenticated user."),
    badge_id: str = Field(..., description="The unique identifier of the badge to update."),
    link_url: str | None = Field(None, description="The URL where the badge link should direct users."),
    image_url: str | None = Field(None, description="The URL of the image to display as the badge."),
    name: str | None = Field(None, description="A descriptive name for the badge."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing badge for a group. Allows modification of the badge's name, image URL, and link URL."""

    _badge_id = _parse_int(badge_id)

    # Construct request model with validation
    try:
        _request = _models.PutApiV4GroupsIdBadgesBadgeIdRequest(
            path=_models.PutApiV4GroupsIdBadgesBadgeIdRequestPath(id_=id_, badge_id=_badge_id),
            body=_models.PutApiV4GroupsIdBadgesBadgeIdRequestBody(link_url=link_url, image_url=image_url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_group_badge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}/badges/{badge_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}/badges/{badge_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_group_badge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_group_badge", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_group_badge",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: badges
@mcp.tool()
async def remove_group_badge(
    id_: str = Field(..., alias="id", description="The ID or URL-encoded path of the group. This identifies which group the badge should be removed from."),
    badge_id: str = Field(..., description="The unique identifier of the badge to remove from the group."),
) -> dict[str, Any] | ToolResult:
    """Removes a badge from a group. This allows administrators to delete badges that are no longer needed or relevant to the group."""

    _badge_id = _parse_int(badge_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteApiV4GroupsIdBadgesBadgeIdRequest(
            path=_models.DeleteApiV4GroupsIdBadgesBadgeIdRequestPath(id_=id_, badge_id=_badge_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_badge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}/badges/{badge_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}/badges/{badge_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_group_badge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_group_badge", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_group_badge",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: badges
@mcp.tool()
async def list_group_badges(
    id_: str = Field(..., alias="id", description="The ID or URL-encoded path of the group. This identifies which group's badges to retrieve."),
    per_page: str | None = Field(None, description="Number of badges to return per page for pagination."),
    name: str | None = Field(None, description="Filter badges by name. Returns only badges matching the specified name."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of badges for a group that are viewable by the authenticated user. Introduced in GitLab 10.6."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4GroupsIdBadgesRequest(
            path=_models.GetApiV4GroupsIdBadgesRequestPath(id_=id_),
            query=_models.GetApiV4GroupsIdBadgesRequestQuery(per_page=_per_page, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_badges: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}/badges", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}/badges"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_group_badges")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_group_badges", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_group_badges",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: badges
@mcp.tool()
async def add_group_badge(
    id_: str = Field(..., alias="id", description="The ID or URL-encoded path of the group. You can use either the numeric group ID or the full URL-encoded group path (e.g., 'my-group' or 'parent-group%2Fchild-group')."),
    link_url: str = Field(..., description="The URL where the badge image links to when clicked. This should be a valid HTTP or HTTPS URL."),
    image_url: str = Field(..., description="The URL of the badge image to display. This should be a valid HTTP or HTTPS URL pointing to an image file."),
    name: str | None = Field(None, description="A descriptive name for the badge to help identify its purpose. This is displayed as alt text and in the group's badge management interface."),
) -> dict[str, Any] | ToolResult:
    """Adds a badge to a group to display custom branding or status indicators. The badge will be visible on the group's profile page."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV4GroupsIdBadgesRequest(
            path=_models.PostApiV4GroupsIdBadgesRequestPath(id_=id_),
            body=_models.PostApiV4GroupsIdBadgesRequestBody(link_url=link_url, image_url=image_url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_group_badge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}/badges", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}/badges"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_group_badge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_group_badge", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_group_badge",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_requests
@mcp.tool()
async def deny_group_access_request(
    id_: str = Field(..., alias="id", description="The ID or URL-encoded path of the group. This identifies which group's access request should be denied."),
    user_id: str = Field(..., description="The user ID of the person whose access request is being denied."),
) -> dict[str, Any] | ToolResult:
    """Denies an access request from a user to join a group. The access request is removed and the user is not granted group membership."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteApiV4GroupsIdAccessRequestsUserIdRequest(
            path=_models.DeleteApiV4GroupsIdAccessRequestsUserIdRequestPath(id_=id_, user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for deny_group_access_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}/access_requests/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}/access_requests/{user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("deny_group_access_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("deny_group_access_request", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="deny_group_access_request",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_requests
@mcp.tool()
async def approve_group_access_request(
    id_: str = Field(..., alias="id", description="The ID or URL-encoded path of the group. Use the numeric group ID or the full URL-encoded path (e.g., 'my-group' or 'parent-group%2Fmy-group')."),
    user_id: str = Field(..., description="The numeric ID of the user whose access request is being approved."),
    access_level: str | None = Field(None, description="The access level to grant the user upon approval. Specifies the user's role and permissions within the group (e.g., Developer, Maintainer)."),
) -> dict[str, Any] | ToolResult:
    """Approves a pending access request for a user to join a group. The authenticated user must own the group to perform this action."""

    _user_id = _parse_int(user_id)
    _access_level = _parse_int(access_level)

    # Construct request model with validation
    try:
        _request = _models.PutApiV4GroupsIdAccessRequestsUserIdApproveRequest(
            path=_models.PutApiV4GroupsIdAccessRequestsUserIdApproveRequestPath(id_=id_, user_id=_user_id),
            body=_models.PutApiV4GroupsIdAccessRequestsUserIdApproveRequestBody(access_level=_access_level)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for approve_group_access_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}/access_requests/{user_id}/approve", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}/access_requests/{user_id}/approve"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("approve_group_access_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("approve_group_access_request", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="approve_group_access_request",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_requests
@mcp.tool()
async def list_group_access_requests(
    id_: str = Field(..., alias="id", description="The ID or URL-encoded path of the group. This identifies which group's access requests to retrieve."),
    per_page: str | None = Field(None, description="Number of access requests to return per page for pagination."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of pending access requests for a group. This allows group owners to review and manage user requests to join the group."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4GroupsIdAccessRequestsRequest(
            path=_models.GetApiV4GroupsIdAccessRequestsRequestPath(id_=id_),
            query=_models.GetApiV4GroupsIdAccessRequestsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_group_access_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}/access_requests", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}/access_requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_group_access_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_group_access_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_group_access_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_requests
@mcp.tool()
async def request_group_access(id_: str = Field(..., alias="id", description="The ID or URL-encoded path of the group to request access for.")) -> dict[str, Any] | ToolResult:
    """Submit an access request for the authenticated user to join a group. The group owner can then review and approve or deny the request."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV4GroupsIdAccessRequestsRequest(
            path=_models.PostApiV4GroupsIdAccessRequestsRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for request_group_access: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/groups/{id}/access_requests", _request.path.model_dump(by_alias=True)) if _request.path else "/groups/{id}/access_requests"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("request_group_access")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("request_group_access", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="request_group_access",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: branches
@mcp.tool()
async def delete_merged_branches(id_: str = Field(..., alias="id", description="The project identifier, which can be either the numeric project ID or the URL-encoded project path (e.g., group%2Fproject-name).")) -> dict[str, Any] | ToolResult:
    """Delete all branches that have been merged into the project's default branch. This operation permanently removes merged branches to clean up the repository."""

    # Construct request model with validation
    try:
        _request = _models.DeleteApiV4ProjectsIdRepositoryMergedBranchesRequest(
            path=_models.DeleteApiV4ProjectsIdRepositoryMergedBranchesRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_merged_branches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/repository/merged_branches", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/repository/merged_branches"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_merged_branches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_merged_branches", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_merged_branches",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: branches
@mcp.tool()
async def get_branch(
    id_: str = Field(..., alias="id", description="The project identifier, which can be a numeric ID or URL-encoded project path (e.g., group/subgroup/project)."),
    branch: str = Field(..., description="The name of the branch to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific branch in a repository. Returns branch information including commit details and protection status."""

    _branch = _parse_int(branch)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4ProjectsIdRepositoryBranchesBranchRequest(
            path=_models.GetApiV4ProjectsIdRepositoryBranchesBranchRequestPath(id_=id_, branch=_branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/repository/branches/{branch}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/repository/branches/{branch}"
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

# Tags: branches
@mcp.tool()
async def delete_branch(
    id_: str = Field(..., alias="id", description="The project identifier, which can be either the numeric project ID or the URL-encoded project path."),
    branch: str = Field(..., description="The name of the branch to delete."),
) -> dict[str, Any] | ToolResult:
    """Delete a branch from a project repository. This operation permanently removes the specified branch."""

    # Construct request model with validation
    try:
        _request = _models.DeleteApiV4ProjectsIdRepositoryBranchesBranchRequest(
            path=_models.DeleteApiV4ProjectsIdRepositoryBranchesBranchRequestPath(id_=id_, branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/repository/branches/{branch}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/repository/branches/{branch}"
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

# Tags: branches
@mcp.tool()
async def check_branch_exists(
    id_: str = Field(..., alias="id", description="The project identifier, which can be either the numeric project ID or the URL-encoded path of the project."),
    branch: str = Field(..., description="The name of the branch to check for existence in the repository."),
) -> dict[str, Any] | ToolResult:
    """Verify whether a specific branch exists in a project repository. Returns a successful response if the branch is found, otherwise returns a 404 error."""

    # Construct request model with validation
    try:
        _request = _models.HeadApiV4ProjectsIdRepositoryBranchesBranchRequest(
            path=_models.HeadApiV4ProjectsIdRepositoryBranchesBranchRequestPath(id_=id_, branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for check_branch_exists: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/repository/branches/{branch}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/repository/branches/{branch}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("check_branch_exists")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("check_branch_exists", "HEAD", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="check_branch_exists",
        method="HEAD",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: branches
@mcp.tool()
async def list_repository_branches(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., 'group%2Fproject')."),
    per_page: str | None = Field(None, description="Number of branches to return per page for pagination."),
    sort: Literal["name_asc", "updated_asc", "updated_desc"] | None = Field(None, description="Sort the returned branches by name in ascending order, or by last update time in ascending or descending order."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of branches from a project's repository. Supports pagination and sorting by branch name or last update time."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4ProjectsIdRepositoryBranchesRequest(
            path=_models.GetApiV4ProjectsIdRepositoryBranchesRequestPath(id_=id_),
            query=_models.GetApiV4ProjectsIdRepositoryBranchesRequestQuery(per_page=_per_page, sort=sort)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_repository_branches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/repository/branches", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/repository/branches"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_repository_branches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_repository_branches", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_repository_branches",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: branches
@mcp.tool()
async def create_branch(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject for group/project)."),
    branch: str = Field(..., description="The name for the new branch to be created."),
    ref: str = Field(..., description="The commit SHA or existing branch name from which to create the new branch."),
) -> dict[str, Any] | ToolResult:
    """Create a new branch in a project from a specified commit SHA or existing branch. The new branch will be created with the given name and point to the specified reference."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV4ProjectsIdRepositoryBranchesRequest(
            path=_models.PostApiV4ProjectsIdRepositoryBranchesRequestPath(id_=id_),
            query=_models.PostApiV4ProjectsIdRepositoryBranchesRequestQuery(branch=branch, ref=ref)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/repository/branches", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/repository/branches"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: branches
@mcp.tool()
async def unprotect_branch(
    id_: str = Field(..., alias="id", description="The project identifier, which can be either the numeric project ID or the URL-encoded project path (e.g., group/subgroup/project)."),
    branch: str = Field(..., description="The name of the branch to unprotect."),
) -> dict[str, Any] | ToolResult:
    """Remove protection from a branch in a project, allowing it to be modified or deleted. This operation reverses any branch protection rules that were previously applied."""

    # Construct request model with validation
    try:
        _request = _models.PutApiV4ProjectsIdRepositoryBranchesBranchUnprotectRequest(
            path=_models.PutApiV4ProjectsIdRepositoryBranchesBranchUnprotectRequestPath(id_=id_, branch=branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for unprotect_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/repository/branches/{branch}/unprotect", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/repository/branches/{branch}/unprotect"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("unprotect_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("unprotect_branch", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="unprotect_branch",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: branches
@mcp.tool()
async def protect_branch(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path."),
    branch: str = Field(..., description="The name of the branch to protect."),
    developers_can_push: bool | None = Field(None, description="Allow developers to push commits to this branch."),
    developers_can_merge: bool | None = Field(None, description="Allow developers to merge pull requests into this branch."),
) -> dict[str, Any] | ToolResult:
    """Protect a branch by restricting push and merge permissions. Configure whether developers can push to or merge into the specified branch."""

    # Construct request model with validation
    try:
        _request = _models.PutApiV4ProjectsIdRepositoryBranchesBranchProtectRequest(
            path=_models.PutApiV4ProjectsIdRepositoryBranchesBranchProtectRequestPath(id_=id_, branch=branch),
            body=_models.PutApiV4ProjectsIdRepositoryBranchesBranchProtectRequestBody(developers_can_push=developers_can_push, developers_can_merge=developers_can_merge)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for protect_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/repository/branches/{branch}/protect", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/repository/branches/{branch}/protect"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("protect_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("protect_branch", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="protect_branch",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: badges
@mcp.tool()
async def get_project_badge(
    id_: str = Field(..., alias="id", description="The project identifier, which can be either the numeric project ID or the URL-encoded project path (e.g., group/subgroup/project)."),
    badge_id: str = Field(..., description="The unique identifier of the badge to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a specific badge associated with a project. This allows you to fetch details about a project badge by its ID."""

    _badge_id = _parse_int(badge_id)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4ProjectsIdBadgesBadgeIdRequest(
            path=_models.GetApiV4ProjectsIdBadgesBadgeIdRequestPath(id_=id_, badge_id=_badge_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project_badge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/badges/{badge_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/badges/{badge_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_project_badge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_project_badge", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_project_badge",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: badges
@mcp.tool()
async def update_project_badge(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path."),
    badge_id: str = Field(..., description="The unique identifier of the badge to update."),
    link_url: str | None = Field(None, description="The URL that the badge links to when clicked."),
    image_url: str | None = Field(None, description="The URL of the image to display as the badge."),
    name: str | None = Field(None, description="A descriptive name for the badge."),
) -> dict[str, Any] | ToolResult:
    """Updates an existing badge for a project. Allows modification of the badge's name, image URL, and link URL."""

    _badge_id = _parse_int(badge_id)

    # Construct request model with validation
    try:
        _request = _models.PutApiV4ProjectsIdBadgesBadgeIdRequest(
            path=_models.PutApiV4ProjectsIdBadgesBadgeIdRequestPath(id_=id_, badge_id=_badge_id),
            body=_models.PutApiV4ProjectsIdBadgesBadgeIdRequestBody(link_url=link_url, image_url=image_url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_badge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/badges/{badge_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/badges/{badge_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_badge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_badge", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_badge",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: badges
@mcp.tool()
async def delete_badge(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject for group/project)."),
    badge_id: str = Field(..., description="The unique identifier of the badge to remove from the project."),
) -> dict[str, Any] | ToolResult:
    """Removes a badge from a project. This operation permanently deletes the specified badge and its association with the project."""

    _badge_id = _parse_int(badge_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteApiV4ProjectsIdBadgesBadgeIdRequest(
            path=_models.DeleteApiV4ProjectsIdBadgesBadgeIdRequestPath(id_=id_, badge_id=_badge_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_badge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/badges/{badge_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/badges/{badge_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_badge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_badge", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_badge",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: badges
@mcp.tool()
async def list_project_badges(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject for group/project)."),
    per_page: str | None = Field(None, description="Number of badges to return per page for pagination."),
    name: str | None = Field(None, description="Filter badges by name. Returns only badges whose name matches the provided value."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a paginated list of badges for a project that are visible to the authenticated user. This endpoint was introduced in GitLab 10.6."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4ProjectsIdBadgesRequest(
            path=_models.GetApiV4ProjectsIdBadgesRequestPath(id_=id_),
            query=_models.GetApiV4ProjectsIdBadgesRequestQuery(per_page=_per_page, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_project_badges: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/badges", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/badges"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_project_badges")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_project_badges", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_project_badges",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: badges
@mcp.tool()
async def create_project_badge(
    id_: str = Field(..., alias="id", description="The ID or URL-encoded path of the project. Accepts both integer IDs and string paths."),
    link_url: str = Field(..., description="The URL that the badge links to when clicked."),
    image_url: str = Field(..., description="The URL of the badge image to display."),
    name: str | None = Field(None, description="A descriptive name for the badge to identify its purpose."),
) -> dict[str, Any] | ToolResult:
    """Adds a new badge to a project. Badges are visual indicators that can link to external URLs and are displayed on the project page."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV4ProjectsIdBadgesRequest(
            path=_models.PostApiV4ProjectsIdBadgesRequestPath(id_=id_),
            body=_models.PostApiV4ProjectsIdBadgesRequestBody(link_url=link_url, image_url=image_url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_project_badge: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/badges", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/badges"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_project_badge")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_project_badge", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_project_badge",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_requests
@mcp.tool()
async def deny_access_request(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path."),
    user_id: str = Field(..., description="The numeric ID of the user whose access request should be denied."),
) -> dict[str, Any] | ToolResult:
    """Denies an access request from a user for the specified project. This removes the user's pending access request and prevents them from gaining project access through this request."""

    _user_id = _parse_int(user_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteApiV4ProjectsIdAccessRequestsUserIdRequest(
            path=_models.DeleteApiV4ProjectsIdAccessRequestsUserIdRequestPath(id_=id_, user_id=_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for deny_access_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/access_requests/{user_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/access_requests/{user_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("deny_access_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("deny_access_request", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="deny_access_request",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_requests
@mcp.tool()
async def approve_access_request(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path."),
    user_id: str = Field(..., description="The user ID of the person whose access request is being approved."),
    access_level: str | None = Field(None, description="The access level to grant the user upon approval. Valid levels range from 10 (Guest) to 50 (Owner)."),
) -> dict[str, Any] | ToolResult:
    """Approves a pending access request for a user to join the project. Optionally specify the access level to grant; defaults to Developer role."""

    _user_id = _parse_int(user_id)
    _access_level = _parse_int(access_level)

    # Construct request model with validation
    try:
        _request = _models.PutApiV4ProjectsIdAccessRequestsUserIdApproveRequest(
            path=_models.PutApiV4ProjectsIdAccessRequestsUserIdApproveRequestPath(id_=id_, user_id=_user_id),
            body=_models.PutApiV4ProjectsIdAccessRequestsUserIdApproveRequestBody(access_level=_access_level)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for approve_access_request: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/access_requests/{user_id}/approve", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/access_requests/{user_id}/approve"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("approve_access_request")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("approve_access_request", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="approve_access_request",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_requests
@mcp.tool()
async def list_access_requests(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject)."),
    per_page: str | None = Field(None, description="Number of access requests to return per page for pagination."),
) -> dict[str, Any] | ToolResult:
    """Retrieves a list of access requests for a project. Access requests allow users to request membership in a project."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4ProjectsIdAccessRequestsRequest(
            path=_models.GetApiV4ProjectsIdAccessRequestsRequestPath(id_=id_),
            query=_models.GetApiV4ProjectsIdAccessRequestsRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_access_requests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/access_requests", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/access_requests"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_access_requests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_access_requests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_access_requests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: access_requests
@mcp.tool()
async def request_project_access(id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject for group/project).")) -> dict[str, Any] | ToolResult:
    """Request access to a project as the authenticated user. This allows users to formally request membership or elevated permissions for a project they don't currently have access to."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV4ProjectsIdAccessRequestsRequest(
            path=_models.PostApiV4ProjectsIdAccessRequestsRequestPath(id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for request_project_access: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/access_requests", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/access_requests"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("request_project_access")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("request_project_access", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="request_project_access",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: alert_management
@mcp.tool()
async def update_alert_metric_image(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path."),
    alert_iid: str = Field(..., description="The internal ID of the alert containing the metric image."),
    metric_image_id: str = Field(..., description="The unique identifier of the metric image to update."),
    url: str | None = Field(None, description="The URL where the metric image or additional metric information can be viewed."),
    url_text: str | None = Field(None, description="A descriptive label or caption for the metric image or its associated URL."),
) -> dict[str, Any] | ToolResult:
    """Update the metric image associated with an alert, including its display URL and descriptive text for reference."""

    _alert_iid = _parse_int(alert_iid)
    _metric_image_id = _parse_int(metric_image_id)

    # Construct request model with validation
    try:
        _request = _models.PutApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequest(
            path=_models.PutApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequestPath(id_=id_, alert_iid=_alert_iid, metric_image_id=_metric_image_id),
            body=_models.PutApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequestBody(url=url, url_text=url_text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_alert_metric_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/alert_management_alerts/{alert_iid}/metric_images/{metric_image_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/alert_management_alerts/{alert_iid}/metric_images/{metric_image_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_alert_metric_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_alert_metric_image", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_alert_metric_image",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: alert_management
@mcp.tool()
async def delete_alert_metric_image(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path."),
    alert_iid: str = Field(..., description="The internal ID (IID) of the alert from which to remove the metric image."),
    metric_image_id: str = Field(..., description="The numeric ID of the metric image to delete."),
) -> dict[str, Any] | ToolResult:
    """Remove a metric image associated with an alert in a project. This operation permanently deletes the specified metric image from the alert's collection."""

    _alert_iid = _parse_int(alert_iid)
    _metric_image_id = _parse_int(metric_image_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequest(
            path=_models.DeleteApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesMetricImageIdRequestPath(id_=id_, alert_iid=_alert_iid, metric_image_id=_metric_image_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_alert_metric_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/alert_management_alerts/{alert_iid}/metric_images/{metric_image_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/alert_management_alerts/{alert_iid}/metric_images/{metric_image_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_alert_metric_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_alert_metric_image", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_alert_metric_image",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: alert_management
@mcp.tool()
async def list_alert_metric_images(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path."),
    alert_iid: str = Field(..., description="The internal ID of the alert for which to retrieve associated metric images."),
) -> dict[str, Any] | ToolResult:
    """Retrieve metric images associated with a specific alert in a project. Metric images provide visual context for alert conditions and their impact."""

    _alert_iid = _parse_int(alert_iid)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequest(
            path=_models.GetApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequestPath(id_=id_, alert_iid=_alert_iid)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_alert_metric_images: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/alert_management_alerts/{alert_iid}/metric_images", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/alert_management_alerts/{alert_iid}/metric_images"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_alert_metric_images")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_alert_metric_images", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_alert_metric_images",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: alert_management
@mcp.tool()
async def upload_alert_metric_image(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path."),
    alert_iid: str = Field(..., description="The internal ID of the alert to attach the metric image to."),
    file_: str = Field(..., alias="file", description="The image file to upload. Supported formats are typically PNG, JPG, and GIF."),
    url: str | None = Field(None, description="Optional URL to view additional metric information or the source of the metric data."),
    url_text: str | None = Field(None, description="Optional descriptive text explaining the metric image content or the linked URL."),
) -> dict[str, Any] | ToolResult:
    """Upload a metric image to an alert for visualization and documentation purposes. Optionally include a URL and description to provide context about the metric data."""

    _alert_iid = _parse_int(alert_iid)

    # Construct request model with validation
    try:
        _request = _models.PostApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequest(
            path=_models.PostApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequestPath(id_=id_, alert_iid=_alert_iid),
            body=_models.PostApiV4ProjectsIdAlertManagementAlertsAlertIidMetricImagesRequestBody(file_=file_, url=url, url_text=url_text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_alert_metric_image: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/alert_management_alerts/{alert_iid}/metric_images", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/alert_management_alerts/{alert_iid}/metric_images"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_alert_metric_image")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_alert_metric_image", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_alert_metric_image",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        multipart_file_fields=["file"],
        headers=_http_headers,
    )

    return _response_data

# Tags: batched_background_migrations
@mcp.tool()
async def pause_batched_background_migration(
    id_: str = Field(..., alias="id", description="The unique identifier of the batched background migration to pause."),
    database: Literal["main", "ci", "embedding", "geo"] | None = Field(None, description="The database instance where the batched background migration is running. Defaults to 'main' if not specified."),
) -> dict[str, Any] | ToolResult:
    """Pause an active batched background migration by its ID. The migration can be resumed later from where it was paused."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.PutApiV4AdminBatchedBackgroundMigrationsIdPauseRequest(
            path=_models.PutApiV4AdminBatchedBackgroundMigrationsIdPauseRequestPath(id_=_id_),
            body=_models.PutApiV4AdminBatchedBackgroundMigrationsIdPauseRequestBody(database=database)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for pause_batched_background_migration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/batched_background_migrations/{id}/pause", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/batched_background_migrations/{id}/pause"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("pause_batched_background_migration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("pause_batched_background_migration", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="pause_batched_background_migration",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: pipeline_composition
@mcp.tool()
async def get_admin_ci_variable(key: str = Field(..., description="The unique identifier key of the instance-level CI/CD variable to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve the details of a specific instance-level CI/CD variable by its key. This operation returns the variable's configuration and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetApiV4AdminCiVariablesKeyRequest(
            path=_models.GetApiV4AdminCiVariablesKeyRequestPath(key=key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_admin_ci_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/ci/variables/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/ci/variables/{key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_admin_ci_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_admin_ci_variable", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_admin_ci_variable",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: pipeline_composition
@mcp.tool()
async def delete_instance_variable(key: str = Field(..., description="The unique identifier key of the instance-level variable to delete.")) -> dict[str, Any] | ToolResult:
    """Delete an instance-level CI/CD variable by its key. This removes the variable from the GitLab instance configuration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteApiV4AdminCiVariablesKeyRequest(
            path=_models.DeleteApiV4AdminCiVariablesKeyRequestPath(key=key)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_instance_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/ci/variables/{key}", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/ci/variables/{key}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_instance_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_instance_variable", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_instance_variable",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: pipeline_composition
@mcp.tool()
async def list_instance_variables(per_page: str | None = Field(None, description="Maximum number of variables to return per page. Use this to control pagination when retrieving large result sets.")) -> dict[str, Any] | ToolResult:
    """Retrieve all instance-level CI/CD variables available across the GitLab instance. These variables are accessible to all projects and groups."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4AdminCiVariablesRequest(
            query=_models.GetApiV4AdminCiVariablesRequestQuery(per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_instance_variables: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/ci/variables"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_instance_variables")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_instance_variables", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_instance_variables",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: pipeline_composition
@mcp.tool()
async def create_instance_variable(
    key: str = Field(..., description="The unique identifier for the variable. Maximum 255 characters."),
    value: str = Field(..., description="The value assigned to the variable."),
    protected: bool | None = Field(None, description="When enabled, the variable is only available to protected branches and tags, preventing exposure in unprotected environments."),
    masked: bool | None = Field(None, description="When enabled, the variable value is masked in job logs and API responses to prevent accidental exposure of sensitive data."),
    raw: bool | None = Field(None, description="When enabled, the variable value is treated as a literal string and not expanded. When disabled, variable references are expanded during job execution."),
    variable_type: Literal["env_var", "file"] | None = Field(None, description="Specifies whether the variable stores an environment value or a file path."),
) -> dict[str, Any] | ToolResult:
    """Create a new instance-level CI/CD variable that is available to all projects. Instance variables are useful for storing secrets and configuration values needed across your entire GitLab instance."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV4AdminCiVariablesRequest(
            body=_models.PostApiV4AdminCiVariablesRequestBody(key=key, value=value, protected=protected, masked=masked, raw=raw, variable_type=variable_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_instance_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/ci/variables"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_instance_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_instance_variable", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_instance_variable",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: clusters
@mcp.tool()
async def get_cluster(cluster_id: str = Field(..., description="The unique identifier of the cluster to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details for a single instance cluster by its ID. This operation requires GitLab 13.2 or later."""

    _cluster_id = _parse_int(cluster_id)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4AdminClustersClusterIdRequest(
            path=_models.GetApiV4AdminClustersClusterIdRequestPath(cluster_id=_cluster_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_cluster: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/clusters/{cluster_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/clusters/{cluster_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_cluster")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_cluster", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_cluster",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: clusters
@mcp.tool()
async def update_cluster(
    cluster_id: str = Field(..., description="The unique identifier of the cluster to update."),
    name: str | None = Field(None, description="The display name for the cluster."),
    enabled: bool | None = Field(None, description="Enable or disable GitLab's connection to the Kubernetes cluster."),
    environment_scope: str | None = Field(None, description="The environment associated with this cluster deployment."),
    namespace_per_environment: bool | None = Field(None, description="When enabled, each environment is deployed to a separate Kubernetes namespace for isolation."),
    domain: str | None = Field(None, description="The base domain for the cluster, used for generating application URLs."),
    management_project_id: str | None = Field(None, description="The ID of the GitLab project that manages this cluster's resources and configurations."),
    managed: bool | None = Field(None, description="When enabled, GitLab automatically manages Kubernetes namespaces and service accounts for this cluster."),
) -> dict[str, Any] | ToolResult:
    """Update an existing instance cluster configuration. Modify cluster settings such as name, connectivity status, environment scope, and management preferences."""

    _cluster_id = _parse_int(cluster_id)
    _management_project_id = _parse_int(management_project_id)

    # Construct request model with validation
    try:
        _request = _models.PutApiV4AdminClustersClusterIdRequest(
            path=_models.PutApiV4AdminClustersClusterIdRequestPath(cluster_id=_cluster_id),
            body=_models.PutApiV4AdminClustersClusterIdRequestBody(name=name, enabled=enabled, environment_scope=environment_scope, namespace_per_environment=namespace_per_environment, domain=domain, management_project_id=_management_project_id, managed=managed)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_cluster: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/clusters/{cluster_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/clusters/{cluster_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_cluster")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_cluster", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_cluster",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: clusters
@mcp.tool()
async def delete_cluster(cluster_id: str = Field(..., description="The unique identifier of the cluster to delete.")) -> dict[str, Any] | ToolResult:
    """Delete an instance cluster from GitLab. This removes the cluster configuration but does not delete any resources within the connected Kubernetes cluster itself."""

    _cluster_id = _parse_int(cluster_id)

    # Construct request model with validation
    try:
        _request = _models.DeleteApiV4AdminClustersClusterIdRequest(
            path=_models.DeleteApiV4AdminClustersClusterIdRequestPath(cluster_id=_cluster_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_cluster: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/admin/clusters/{cluster_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/admin/clusters/{cluster_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_cluster")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_cluster", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_cluster",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: clusters
@mcp.tool()
async def add_kubernetes_cluster(
    name: str = Field(..., description="The display name for the Kubernetes cluster."),
    platform_kubernetes_attributes_api_url: str = Field(..., description="The URL endpoint to access the Kubernetes API server."),
    platform_kubernetes_attributes_token: str = Field(..., description="The authentication token or bearer token used to authenticate requests to the Kubernetes API."),
    enabled: bool | None = Field(None, description="Whether the cluster is active and available for deployments."),
    environment_scope: str | None = Field(None, description="The environment scope this cluster is associated with, such as production or staging. Use * to match all environments."),
    namespace_per_environment: bool | None = Field(None, description="Whether to deploy each environment to its own isolated Kubernetes namespace for better resource separation and security."),
    domain: str | None = Field(None, description="The base domain for applications deployed to this cluster."),
    management_project_id: str | None = Field(None, description="The GitLab project ID that will manage this cluster's namespaces and service accounts."),
    managed: bool | None = Field(None, description="Whether GitLab automatically manages Kubernetes namespaces and service accounts for this cluster."),
    platform_kubernetes_attributes_authorization_type: Literal["unknown_authorization", "rbac", "abac"] | None = Field(None, description="The authorization mechanism used by the Kubernetes cluster for access control."),
) -> dict[str, Any] | ToolResult:
    """Register an existing Kubernetes cluster as an instance cluster in GitLab. This allows GitLab to deploy applications and manage resources on the cluster."""

    _management_project_id = _parse_int(management_project_id)

    # Construct request model with validation
    try:
        _request = _models.PostApiV4AdminClustersAddRequest(
            body=_models.PostApiV4AdminClustersAddRequestBody(name=name, enabled=enabled, environment_scope=environment_scope, namespace_per_environment=namespace_per_environment, domain=domain, management_project_id=_management_project_id, managed=managed, platform_kubernetes_attributes_api_url=platform_kubernetes_attributes_api_url, platform_kubernetes_attributes_token=platform_kubernetes_attributes_token, platform_kubernetes_attributes_authorization_type=platform_kubernetes_attributes_authorization_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_kubernetes_cluster: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/admin/clusters/add"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_kubernetes_cluster")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_kubernetes_cluster", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_kubernetes_cluster",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: clusters
@mcp.tool()
async def list_clusters() -> dict[str, Any] | ToolResult:
    """Retrieve a list of all instance clusters configured in GitLab. This operation provides an overview of cluster infrastructure available at the instance level."""

    # Extract parameters for API call
    _http_path = "/admin/clusters"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_clusters")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_clusters", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_clusters",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: applications
@mcp.tool()
async def delete_application(id_: str = Field(..., alias="id", description="The unique identifier of the application to delete.")) -> dict[str, Any] | ToolResult:
    """Permanently delete a specific application by its ID. This action cannot be undone."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteApiV4ApplicationsIdRequest(
            path=_models.DeleteApiV4ApplicationsIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_application: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/applications/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/applications/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_application")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_application", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_application",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: avatar
@mcp.tool()
async def get_user_avatar(
    email: str = Field(..., description="The public email address of the user whose avatar should be retrieved."),
    size: str | None = Field(None, description="The width and height in pixels for the returned avatar image. Larger sizes provide higher resolution avatars."),
) -> dict[str, Any] | ToolResult:
    """Retrieve the avatar URL for a user based on their email address. Optionally specify a custom image size for the avatar."""

    _size = _parse_int(size)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4AvatarRequest(
            query=_models.GetApiV4AvatarRequestQuery(email=email, size=_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_user_avatar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/avatar"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_user_avatar")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_user_avatar", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_user_avatar",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: broadcast_messages
@mcp.tool()
async def get_broadcast_message(id_: str = Field(..., alias="id", description="The unique identifier of the broadcast message to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve a specific broadcast message by its ID. Broadcast messages are system-wide announcements visible to all users."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4BroadcastMessagesIdRequest(
            path=_models.GetApiV4BroadcastMessagesIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_broadcast_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/broadcast_messages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/broadcast_messages/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_broadcast_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_broadcast_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_broadcast_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: broadcast_messages
@mcp.tool()
async def delete_broadcast_message(id_: str = Field(..., alias="id", description="The unique identifier of the broadcast message to delete.")) -> dict[str, Any] | ToolResult:
    """Delete a broadcast message by its ID. This operation permanently removes the specified broadcast message from the system."""

    _id_ = _parse_int(id_)

    # Construct request model with validation
    try:
        _request = _models.DeleteApiV4BroadcastMessagesIdRequest(
            path=_models.DeleteApiV4BroadcastMessagesIdRequestPath(id_=_id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_broadcast_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/broadcast_messages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/broadcast_messages/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_broadcast_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_broadcast_message", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_broadcast_message",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: bulk_imports
@mcp.tool()
async def get_migration_entity(
    import_id: str = Field(..., description="The unique identifier of the GitLab Migration batch containing the entity you want to retrieve."),
    entity_id: str = Field(..., description="The unique identifier of the specific entity within the migration whose details you want to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve detailed information about a specific entity within a GitLab Migration. This allows you to inspect the status and properties of individual migrated items."""

    _import_id = _parse_int(import_id)
    _entity_id = _parse_int(entity_id)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4BulkImportsImportIdEntitiesEntityIdRequest(
            path=_models.GetApiV4BulkImportsImportIdEntitiesEntityIdRequestPath(import_id=_import_id, entity_id=_entity_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_migration_entity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bulk_imports/{import_id}/entities/{entity_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bulk_imports/{import_id}/entities/{entity_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_migration_entity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_migration_entity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_migration_entity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: bulk_imports
@mcp.tool()
async def list_migration_entities(
    import_id: str = Field(..., description="The unique identifier of the GitLab Migration import job to retrieve entities from."),
    status: Literal["created", "started", "finished", "timeout", "failed"] | None = Field(None, description="Filter entities by their current processing status in the migration workflow."),
    per_page: str | None = Field(None, description="Number of entities to return per page for pagination. Defaults to 20 items per page."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of entities from a GitLab Migration import job. Filter by status and paginate through results to monitor migration progress."""

    _import_id = _parse_int(import_id)
    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4BulkImportsImportIdEntitiesRequest(
            path=_models.GetApiV4BulkImportsImportIdEntitiesRequestPath(import_id=_import_id),
            query=_models.GetApiV4BulkImportsImportIdEntitiesRequestQuery(status=status, per_page=_per_page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_migration_entities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bulk_imports/{import_id}/entities", _request.path.model_dump(by_alias=True)) if _request.path else "/bulk_imports/{import_id}/entities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_migration_entities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_migration_entities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_migration_entities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: bulk_imports
@mcp.tool()
async def get_bulk_import(import_id: str = Field(..., description="The unique identifier of the bulk import migration to retrieve.")) -> dict[str, Any] | ToolResult:
    """Retrieve details about a GitLab Migration bulk import job, including its status and progress information."""

    _import_id = _parse_int(import_id)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4BulkImportsImportIdRequest(
            path=_models.GetApiV4BulkImportsImportIdRequestPath(import_id=_import_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_bulk_import: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/bulk_imports/{import_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/bulk_imports/{import_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_bulk_import")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_bulk_import", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_bulk_import",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: bulk_imports
@mcp.tool()
async def list_migration_entities_all(
    per_page: str | None = Field(None, description="Maximum number of entities to return per page for pagination purposes."),
    sort: Literal["asc", "desc"] | None = Field(None, description="Order in which to sort the returned entities by creation date."),
    status: Literal["created", "started", "finished", "timeout", "failed"] | None = Field(None, description="Filter entities by their current migration status to view only those in a specific state."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of all entities from GitLab Migrations. This operation supports pagination, sorting, and filtering by migration status to help track the progress of bulk import operations."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4BulkImportsEntitiesRequest(
            query=_models.GetApiV4BulkImportsEntitiesRequestQuery(per_page=_per_page, sort=sort, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_migration_entities_all: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bulk_imports/entities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_migration_entities_all")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_migration_entities_all", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_migration_entities_all",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: bulk_imports
@mcp.tool()
async def list_migrations(
    per_page: str | None = Field(None, description="Number of migration records to return per page for pagination."),
    sort: Literal["asc", "desc"] | None = Field(None, description="Sort migrations by creation date in ascending or descending order."),
    status: Literal["created", "started", "finished", "timeout", "failed"] | None = Field(None, description="Filter migrations by their current status in the migration lifecycle."),
) -> dict[str, Any] | ToolResult:
    """Retrieve a list of all GitLab Migrations with optional filtering and sorting. This feature was introduced in GitLab 14.1."""

    _per_page = _parse_int(per_page)

    # Construct request model with validation
    try:
        _request = _models.GetApiV4BulkImportsRequest(
            query=_models.GetApiV4BulkImportsRequestQuery(per_page=_per_page, sort=sort, status=status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_migrations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bulk_imports"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_migrations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_migrations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_migrations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: bulk_imports
@mcp.tool()
async def start_bulk_migration(
    configuration_url: str = Field(..., description="URL of the source GitLab instance to migrate from (e.g., https://source.gitlab.com)"),
    configuration_access_token: str = Field(..., description="Personal access token or project access token from the source GitLab instance with sufficient permissions to read the entities being migrated"),
    entities_source_type: list[Literal["group_entity", "project_entity"]] = Field(..., description="Array of entity types to migrate from the source instance. Each element specifies the type of resource (group or project) being imported"),
    entities_source_full_path: list[str] = Field(..., description="Array of relative paths for source entities to import. Each path corresponds to the entity at the same index in entities_source_type. Paths should be in the format of full project or group paths on the source instance"),
    entities_destination_namespace: list[str] = Field(..., description="Array of destination namespaces where entities will be imported. Each namespace corresponds to the entity at the same index. Specify the target group or namespace path on the destination instance"),
    entities_destination_slug: list[str] | None = Field(None, description="Array of optional destination slugs for imported entities. When provided, overrides the default slug derived from the source entity name. Each slug corresponds to the entity at the same index"),
    entities_migrate_projects: list[bool] | None = Field(None, description="Array of boolean flags indicating whether to include nested projects during group migration. Each flag corresponds to the group at the same index in entities_source_type"),
) -> dict[str, Any] | ToolResult:
    """Initiate a bulk migration of GitLab entities from a source instance to the destination. This operation supports migrating groups and projects with their nested resources between GitLab instances."""

    # Construct request model with validation
    try:
        _request = _models.PostApiV4BulkImportsRequest(
            body=_models.PostApiV4BulkImportsRequestBody(configuration_url=configuration_url, configuration_access_token=configuration_access_token, entities_source_type=entities_source_type, entities_source_full_path=entities_source_full_path, entities_destination_namespace=entities_destination_namespace, entities_destination_slug=entities_destination_slug, entities_migrate_projects=entities_migrate_projects)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for start_bulk_migration: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/bulk_imports"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("start_bulk_migration")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("start_bulk_migration", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="start_bulk_migration",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="application/x-www-form-urlencoded",
        headers=_http_headers,
    )

    return _response_data

# Tags: jobs
@mcp.tool()
async def list_jobs(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded project path (e.g., group/subgroup/project)."),
    scope: list[str] | None = Field(None, description="Filter results to include only jobs with the specified statuses. Provide as an array of status values; order is not significant."),
) -> dict[str, Any] | ToolResult:
    """Retrieve all jobs for a specified project, with optional filtering by job status. Use this to monitor job execution, track pipeline progress, or retrieve job details."""

    # Construct request model with validation
    try:
        _request = _models.ListProjectJobsRequest(
            path=_models.ListProjectJobsRequestPath(id_=id_),
            query=_models.ListProjectJobsRequestQuery(scope=scope)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_jobs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/jobs", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/jobs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_jobs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_jobs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_jobs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: jobs
@mcp.tool()
async def get_job(
    id_: str = Field(..., alias="id", description="The project identifier, which can be a numeric ID or URL-encoded project path (e.g., group/subgroup/project)."),
    job_id: int = Field(..., description="The numeric identifier of the job to retrieve."),
) -> dict[str, Any] | ToolResult:
    """Retrieve details for a specific job within a project. Returns comprehensive job information including status, logs, and execution details."""

    # Construct request model with validation
    try:
        _request = _models.GetSingleJobRequest(
            path=_models.GetSingleJobRequestPath(id_=id_, job_id=job_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/jobs/{job_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/jobs/{job_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_job", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_job",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: jobs
@mcp.tool()
async def execute_manual_job(
    id_: str = Field(..., alias="id", description="The project identifier, either as a numeric ID or URL-encoded path (e.g., group%2Fproject for group/project)."),
    job_id: int = Field(..., description="The numeric ID of the manual job to execute."),
    job_variables_attributes: list[str] | None = Field(None, description="Optional array of custom variables to make available to the job during execution. Variables are applied in the order provided."),
) -> dict[str, Any] | ToolResult:
    """Execute a manual job for a project. Optionally provide custom variables to override job defaults during execution."""

    # Construct request model with validation
    try:
        _request = _models.TriggerManualJobRequest(
            path=_models.TriggerManualJobRequestPath(id_=id_, job_id=job_id),
            query=_models.TriggerManualJobRequestQuery(job_variables_attributes=job_variables_attributes)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for execute_manual_job: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/projects/{id}/jobs/{job_id}/play", _request.path.model_dump(by_alias=True)) if _request.path else "/projects/{id}/jobs/{job_id}/play"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("execute_manual_job")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("execute_manual_job", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="execute_manual_job",
        method="POST",
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
        print("  python git_lab_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="GitLab MCP Server")

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
    logger.info("Starting GitLab MCP Server")
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

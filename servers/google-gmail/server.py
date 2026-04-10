#!/usr/bin/env python3
"""
Google Gmail MCP Server

API Info:
- API License: Creative Commons Attribution 3.0 (http://creativecommons.org/licenses/by/3.0/)
- Contact: Google (https://google.com)
- Terms of Service: https://developers.google.com/terms/

Generated: 2026-04-09 17:23:45 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import logging
import os
import random
import sys
import time
import uuid
from dataclasses import dataclass
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from enum import Enum
from pathlib import Path
from typing import Any, Literal, overload

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
from pydantic import Field

BASE_URL = os.getenv("BASE_URL", "https://gmail.googleapis.com")
SERVER_NAME = "Google Gmail"
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

async def _make_request(
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    body: Any = None,
    body_content_type: str | None = None,
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
    if method.upper() in ("POST", "PUT", "PATCH") and (body_content_type is None or body_content_type == "application/json"):
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
            _data = body if body_content_type in ("application/x-www-form-urlencoded", "multipart/form-data") else None
            _content = None
            if body_content_type is not None and body_content_type not in ("application/json", "application/x-www-form-urlencoded", "multipart/form-data"):
                _raw = body
                _content = json.dumps(_raw).encode() if isinstance(_raw, (dict, list)) else _raw
            response = await client.request(
                method=method,
                url=path,
                params=params,
                json=_json,
                data=_data,
                content=_content,
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
                    raise ValueError(error_message)

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
        raise ValueError(error_message)

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
                    try:
                        context.message.arguments[key] = json.loads(value)
                    except (json.JSONDecodeError, ValueError):
                        pass
        return await call_next(context)


# ============================================================================
# Helper Functions
# ============================================================================

def build_raw_message(email_from: str | None = None, email_to: str | None = None, email_cc: str | None = None, email_bcc: str | None = None, email_subject: str | None = None, email_body: str | None = None, email_body_is_html: bool | None = None, email_reply_to: str | None = None, email_in_reply_to: str | None = None, email_references: str | None = None) -> str | None:
    """Helper function for parameter transformation"""
    if all(v is None for v in [email_from, email_to, email_cc, email_bcc, email_subject, email_body, email_body_is_html, email_reply_to, email_in_reply_to, email_references]):
        return None

    try:
        is_html = email_body_is_html if email_body_is_html is not None else False
        body_subtype = 'html' if is_html else 'plain'
        msg = MIMEText(email_body or '', _subtype=body_subtype)
        
        if email_from:
            msg['From'] = email_from
        if email_to:
            msg['To'] = email_to
        if email_cc:
            msg['Cc'] = email_cc
        if email_subject:
            msg['Subject'] = email_subject
        if email_reply_to:
            msg['Reply-To'] = email_reply_to
        if email_in_reply_to:
            msg['In-Reply-To'] = email_in_reply_to
        if email_references:
            msg['References'] = email_references
        
        msg['Date'] = formatdate(localtime=False)
        msg['Message-ID'] = make_msgid()
        
        raw_bytes = msg.as_bytes()
        encoded = base64.urlsafe_b64encode(raw_bytes).decode('ascii')
        return encoded
    except Exception as e:
        raise ValueError(f"Failed to build RFC 2822 message: {e}") from e

def build_gmail_query(from_address: str | None = None, to_address: str | None = None, subject_contains: str | None = None, has_attachment: bool | None = None, is_unread: bool | None = None, is_starred: bool | None = None, before_date: str | None = None, after_date: str | None = None, custom_query: str | None = None) -> str | None:
    """Helper function for parameter transformation"""
    if all(v is None for v in [from_address, to_address, subject_contains, has_attachment, is_unread, is_starred, before_date, after_date, custom_query]):
        return None

    query_parts = []

    if from_address:
        query_parts.append(f'from:{from_address}')
    if to_address:
        query_parts.append(f'to:{to_address}')
    if subject_contains:
        query_parts.append(f'subject:{subject_contains}')
    if has_attachment:
        query_parts.append('has:attachment')
    if is_unread:
        query_parts.append('is:unread')
    if is_starred:
        query_parts.append('is:starred')
    if before_date:
        query_parts.append(f'before:{before_date}')
    if after_date:
        query_parts.append(f'after:{after_date}')
    if custom_query:
        query_parts.append(custom_query)

    return ' '.join(query_parts)

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
    headers: dict[str, str] | None = None,
    cookies: dict[str, str] | None = None,
    raw_querystring: str | None = None,
) -> tuple[dict[str, Any], int]:
    """
    Execute tool request with timeout handling and metrics recording.

    Returns:
        Tuple of (normalized_response_data, status_code).
        Response data is normalized to dict format for Pydantic validation.
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

mcp = FastMCP("Google Gmail", middleware=[_JsonCoercionMiddleware()])

# Tags: users
@mcp.tool()
async def get_profile(user_id: str = Field(..., alias="userId", description="The user's email address or the special value `me` to refer to the authenticated user.")) -> dict[str, Any]:
    """Retrieves the Gmail profile information for the authenticated user or a specified user, including account details and settings."""

    # Construct request model with validation
    try:
        _request = _models.GetProfileRequest(
            path=_models.GetProfileRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_profile: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/profile", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/profile"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_profile")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_profile", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_profile",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_drafts(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    include_spam_trash: bool | None = Field(None, alias="includeSpamTrash", description="Whether to include draft messages from the SPAM and TRASH folders in the results."),
    max_results: int | None = Field(None, alias="maxResults", description="Maximum number of drafts to return. The default is 100 and the maximum allowed value is 500."),
    q: str | None = Field(None, description="Filter draft messages using Gmail search query syntax. Supports the same query operators as the Gmail search box (e.g., from:, rfc822msgid:, is:unread)."),
) -> dict[str, Any]:
    """Retrieves a list of draft messages from the user's mailbox. Supports filtering by search query and optional inclusion of drafts from spam and trash folders."""

    # Construct request model with validation
    try:
        _request = _models.DraftsListRequest(
            path=_models.DraftsListRequestPath(user_id=user_id),
            query=_models.DraftsListRequestQuery(include_spam_trash=include_spam_trash, max_results=max_results, q=q)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_drafts: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/drafts", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/drafts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_drafts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_drafts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_drafts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def create_draft(
    user_id: str = Field(..., alias="userId", description="The user's email address or the special value 'me' to indicate the authenticated user."),
    classification_label_values: list[_models.ClassificationLabelValue] | None = Field(None, alias="classificationLabelValues", description="Classification label values to apply to the draft message. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only available for Google Workspace accounts."),
    label_ids: list[str] | None = Field(None, alias="labelIds", description="List of label IDs to apply to the draft message. Labels are applied in the order provided."),
    email_from: str | None = Field(None, description="Sender email address (From header)"),
    email_to: str | None = Field(None, description="Recipient email address (To header)"),
    email_cc: str | None = Field(None, description="Carbon copy recipients (Cc header), comma-separated"),
    email_bcc: str | None = Field(None, description="Blind carbon copy recipients (Bcc header), comma-separated"),
    email_subject: str | None = Field(None, description="Email subject line"),
    email_body: str | None = Field(None, description="Email body content (plain text or HTML)"),
    email_body_is_html: bool | None = Field(None, description="Whether email_body is HTML (True) or plain text (False)"),
    email_reply_to: str | None = Field(None, description="Reply-To header address"),
    email_in_reply_to: str | None = Field(None, description="In-Reply-To header (Message-ID of original message)"),
    email_references: str | None = Field(None, description="References header (Message-IDs of related messages), space-separated"),
) -> dict[str, Any]:
    """Creates a new email draft with the DRAFT label in Gmail. The draft can optionally include classification labels and custom label IDs."""

    # Call helper functions
    raw = build_raw_message(email_from, email_to, email_cc, email_bcc, email_subject, email_body, email_body_is_html, email_reply_to, email_in_reply_to, email_references)

    # Construct request model with validation
    try:
        _request = _models.DraftsCreateRequest(
            path=_models.DraftsCreateRequestPath(user_id=user_id),
            body=_models.DraftsCreateRequestBody(message=_models.DraftsCreateRequestBodyMessage(classification_label_values=classification_label_values, label_ids=label_ids, raw=raw) if any(v is not None for v in [classification_label_values, label_ids, raw]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_draft: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/drafts", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/drafts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "message/cpim"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_draft")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_draft", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_draft",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="message/cpim",
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_draft(
    user_id: str = Field(..., alias="userId", description="The user's email address or the special value 'me' to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the draft message to retrieve."),
    format_: Literal["minimal", "full", "raw", "metadata"] | None = Field(None, alias="format", description="The format in which to return the draft message content and metadata."),
) -> dict[str, Any]:
    """Retrieves a specific draft message by ID. Returns the draft in the requested format for viewing or further editing."""

    # Construct request model with validation
    try:
        _request = _models.DraftsGetRequest(
            path=_models.DraftsGetRequestPath(user_id=user_id, id_=id_),
            query=_models.DraftsGetRequestQuery(format_=format_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_draft: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/drafts/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/drafts/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_draft")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_draft", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_draft",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def update_draft(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the draft message to update."),
    classification_label_values: list[_models.ClassificationLabelValue] | None = Field(None, alias="classificationLabelValues", description="Classification label values to apply to the message. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only available for Google Workspace accounts. Classification label schemas can be queried using the Google Drive Labels API."),
    label_ids: list[str] | None = Field(None, alias="labelIds", description="List of label IDs to apply to this message. Labels are used to organize and categorize messages in Gmail."),
    email_from: str | None = Field(None, description="Sender email address (From header)"),
    email_to: str | None = Field(None, description="Recipient email address (To header)"),
    email_cc: str | None = Field(None, description="Carbon copy recipients (Cc header), comma-separated"),
    email_bcc: str | None = Field(None, description="Blind carbon copy recipients (Bcc header), comma-separated"),
    email_subject: str | None = Field(None, description="Email subject line"),
    email_body: str | None = Field(None, description="Email body content (plain text or HTML)"),
    email_body_is_html: bool | None = Field(None, description="Whether email_body is HTML (True) or plain text (False)"),
    email_reply_to: str | None = Field(None, description="Reply-To header address"),
    email_in_reply_to: str | None = Field(None, description="In-Reply-To header (Message-ID of original message)"),
    email_references: str | None = Field(None, description="References header (Message-IDs of related messages), space-separated"),
) -> dict[str, Any]:
    """Updates the content of an existing draft message. Replaces the draft's message body and metadata with the provided values."""

    # Call helper functions
    raw = build_raw_message(email_from, email_to, email_cc, email_bcc, email_subject, email_body, email_body_is_html, email_reply_to, email_in_reply_to, email_references)

    # Construct request model with validation
    try:
        _request = _models.DraftsUpdateRequest(
            path=_models.DraftsUpdateRequestPath(user_id=user_id, id_=id_),
            body=_models.DraftsUpdateRequestBody(message=_models.DraftsUpdateRequestBodyMessage(classification_label_values=classification_label_values, label_ids=label_ids, raw=raw) if any(v is not None for v in [classification_label_values, label_ids, raw]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_draft: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/drafts/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/drafts/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "message/cpim"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_draft")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_draft", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_draft",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="message/cpim",
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_draft(
    user_id: str = Field(..., alias="userId", description="The email address of the user whose draft should be deleted. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the draft message to delete."),
) -> dict[str, Any]:
    """Permanently deletes a draft message without moving it to trash. This action is immediate and irreversible."""

    # Construct request model with validation
    try:
        _request = _models.DraftsDeleteRequest(
            path=_models.DraftsDeleteRequestPath(user_id=user_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_draft: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/drafts/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/drafts/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_draft")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_draft", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_draft",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def send_draft(
    user_id: str = Field(..., alias="userId", description="The user's email address or the special value `me` to indicate the authenticated user."),
    classification_label_values: list[_models.ClassificationLabelValue] | None = Field(None, alias="classificationLabelValues", description="Classification label values to apply to the message. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only available for Google Workspace accounts."),
    label_ids: list[str] | None = Field(None, alias="labelIds", description="List of label IDs to apply to this message. Labels are applied in the order provided."),
    email_from: str | None = Field(None, description="Sender email address (From header)"),
    email_to: str | None = Field(None, description="Recipient email address (To header)"),
    email_cc: str | None = Field(None, description="Carbon copy recipients (Cc header), comma-separated"),
    email_bcc: str | None = Field(None, description="Blind carbon copy recipients (Bcc header), comma-separated"),
    email_subject: str | None = Field(None, description="Email subject line"),
    email_body: str | None = Field(None, description="Email body content (plain text or HTML)"),
    email_body_is_html: bool | None = Field(None, description="Whether email_body is HTML (True) or plain text (False)"),
    email_reply_to: str | None = Field(None, description="Reply-To header address"),
    email_in_reply_to: str | None = Field(None, description="In-Reply-To header (Message-ID of original message)"),
    email_references: str | None = Field(None, description="References header (Message-IDs of related messages), space-separated"),
    id_: str | None = Field(None, alias="id", description="The immutable ID of the draft."),
) -> dict[str, Any]:
    """Sends an existing draft message to recipients specified in the To, Cc, and Bcc headers. The draft must already exist and contain valid recipient information."""

    # Call helper functions
    raw = build_raw_message(email_from, email_to, email_cc, email_bcc, email_subject, email_body, email_body_is_html, email_reply_to, email_in_reply_to, email_references)

    # Construct request model with validation
    try:
        _request = _models.DraftsSendRequest(
            path=_models.DraftsSendRequestPath(user_id=user_id),
            body=_models.DraftsSendRequestBody(id_=id_,
                message=_models.DraftsSendRequestBodyMessage(classification_label_values=classification_label_values, label_ids=label_ids, raw=raw) if any(v is not None for v in [classification_label_values, label_ids, raw]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_draft: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/drafts/send", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/drafts/send"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "message/cpim"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_draft")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_draft", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_draft",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="message/cpim",
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_mailbox_history(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    history_types: list[Literal["messageAdded", "messageDeleted", "labelAdded", "labelRemoved"]] | None = Field(None, alias="historyTypes", description="Types of history events to include in results. When specified, only changes matching these types are returned."),
    label_id: str | None = Field(None, alias="labelId", description="Filter results to only include messages with a specific label ID."),
    max_results: int | None = Field(None, alias="maxResults", description="Maximum number of history records to return per request. Defaults to 100 if not specified."),
    start_history_id: str | None = Field(None, alias="startHistoryId", description="Starting point for retrieving history records. Provide a historyId from a previous response or message to retrieve all changes after that point. History IDs are valid for at least a week but may expire sooner in rare cases. If an HTTP 404 error occurs, perform a full sync. Omit this parameter for the initial sync request."),
) -> dict[str, Any]:
    """Retrieves the chronological history of all changes to a mailbox, including message additions, deletions, and label modifications. Results are returned in chronological order by historyId and support pagination for efficient sync operations."""

    # Construct request model with validation
    try:
        _request = _models.HistoryListRequest(
            path=_models.HistoryListRequestPath(user_id=user_id),
            query=_models.HistoryListRequestQuery(history_types=history_types, label_id=label_id, max_results=max_results, start_history_id=start_history_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_mailbox_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/history", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_mailbox_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_mailbox_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_mailbox_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_labels(user_id: str = Field(..., alias="userId", description="The user's email address or the special value `me` to refer to the authenticated user.")) -> dict[str, Any]:
    """Retrieves all labels in the user's mailbox. Labels are used to organize and categorize emails in Gmail."""

    # Construct request model with validation
    try:
        _request = _models.LabelsListRequest(
            path=_models.LabelsListRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_labels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/labels", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/labels"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_labels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_labels", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_labels",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def create_label(
    user_id: str = Field(..., alias="userId", description="The user's email address or the special value `me` to indicate the authenticated user."),
    label_list_visibility: Literal["labelShow", "labelShowIfUnread", "labelHide"] | None = Field(None, alias="labelListVisibility", description="Controls whether this label appears in the label list in Gmail's web interface."),
    message_list_visibility: Literal["show", "hide"] | None = Field(None, alias="messageListVisibility", description="Controls whether messages with this label are visible in the message list in Gmail's web interface."),
    name: str | None = Field(None, description="The display name for the label as it appears in Gmail."),
    type_: Literal["system", "user"] | None = Field(None, alias="type", description="The owner type for the label. User labels are created and managed by the user and can be applied to any message or thread. System labels are internally created and cannot be modified or deleted by users."),
) -> dict[str, Any]:
    """Creates a new custom label in Gmail for organizing messages and threads. Labels can be configured with specific visibility settings in the Gmail web interface."""

    # Construct request model with validation
    try:
        _request = _models.LabelsCreateRequest(
            path=_models.LabelsCreateRequestPath(user_id=user_id),
            body=_models.LabelsCreateRequestBody(label_list_visibility=label_list_visibility, message_list_visibility=message_list_visibility, name=name, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/labels", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/labels"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_label", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_label",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_label(
    user_id: str = Field(..., alias="userId", description="The user's email address or the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the label to retrieve."),
) -> dict[str, Any]:
    """Retrieves a specific Gmail label by its ID. Use this to fetch detailed information about a label, such as its name, visibility settings, and other metadata."""

    # Construct request model with validation
    try:
        _request = _models.LabelsGetRequest(
            path=_models.LabelsGetRequestPath(user_id=user_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/labels/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/labels/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_label", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_label",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def update_label(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the label to update."),
    label_list_visibility: Literal["labelShow", "labelShowIfUnread", "labelHide"] | None = Field(None, alias="labelListVisibility", description="Controls whether the label appears in the label list in Gmail's web interface."),
    message_list_visibility: Literal["show", "hide"] | None = Field(None, alias="messageListVisibility", description="Controls whether messages with this label are visible in the message list in Gmail's web interface."),
    name: str | None = Field(None, description="The display name of the label as shown to the user in Gmail."),
    type_: Literal["system", "user"] | None = Field(None, alias="type", description="The owner type of the label. User labels can be modified and deleted; system labels are managed by Gmail and cannot be altered."),
) -> dict[str, Any]:
    """Updates an existing Gmail label with new properties such as display name and visibility settings. Only user-created labels can be modified; system labels cannot be changed."""

    # Construct request model with validation
    try:
        _request = _models.LabelsUpdateRequest(
            path=_models.LabelsUpdateRequestPath(user_id=user_id, id_=id_),
            body=_models.LabelsUpdateRequestBody(label_list_visibility=label_list_visibility, message_list_visibility=message_list_visibility, name=name, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/labels/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/labels/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_label", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_label",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def update_label_partial(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the label to update."),
    label_list_visibility: Literal["labelShow", "labelShowIfUnread", "labelHide"] | None = Field(None, alias="labelListVisibility", description="Controls whether this label appears in the label list within Gmail's web interface."),
    message_list_visibility: Literal["show", "hide"] | None = Field(None, alias="messageListVisibility", description="Controls whether messages with this label are visible in the message list within Gmail's web interface."),
    name: str | None = Field(None, description="The human-readable name displayed for this label in the Gmail interface."),
    type_: Literal["system", "user"] | None = Field(None, alias="type", description="Indicates whether this is a system label (created and managed by Gmail) or a user label (created and managed by the user). System labels cannot be modified or deleted, while user labels can be fully customized."),
) -> dict[str, Any]:
    """Update properties of a Gmail label using partial update semantics. Modify visibility settings, display name, or other label attributes without replacing the entire label configuration."""

    # Construct request model with validation
    try:
        _request = _models.LabelsPatchRequest(
            path=_models.LabelsPatchRequestPath(user_id=user_id, id_=id_),
            body=_models.LabelsPatchRequestBody(label_list_visibility=label_list_visibility, message_list_visibility=message_list_visibility, name=name, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_label_partial: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/labels/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/labels/{id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_label_partial")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_label_partial", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_label_partial",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_label(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the label to delete."),
) -> dict[str, Any]:
    """Permanently deletes a label and removes it from all messages and threads it is applied to. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.LabelsDeleteRequest(
            path=_models.LabelsDeleteRequestPath(user_id=user_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_label: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/labels/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/labels/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_label")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_label", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_label",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_messages_batch(
    user_id: str = Field(..., alias="userId", description="The user's email address or the special value `me` to indicate the authenticated user."),
    ids: list[str] | None = Field(None, description="An array of message IDs to delete. The order of IDs is not significant."),
) -> dict[str, Any]:
    """Permanently deletes multiple messages by their IDs. Note that this operation provides no guarantees about message existence or prior deletion status."""

    # Construct request model with validation
    try:
        _request = _models.MessagesBatchDeleteRequest(
            path=_models.MessagesBatchDeleteRequestPath(user_id=user_id),
            body=_models.MessagesBatchDeleteRequestBody(ids=ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_messages_batch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages/batchDelete", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages/batchDelete"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_messages_batch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_messages_batch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_messages_batch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def update_message_labels_batch(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    add_label_ids: list[str] | None = Field(None, alias="addLabelIds", description="Label IDs to add to the specified messages. Order is not significant."),
    ids: list[str] | None = Field(None, description="The message IDs to modify. Maximum of 1000 IDs per request."),
    remove_label_ids: list[str] | None = Field(None, alias="removeLabelIds", description="Label IDs to remove from the specified messages. Order is not significant."),
) -> dict[str, Any]:
    """Modifies labels on specified messages by adding and/or removing label IDs. Supports batch operations on up to 1000 messages per request."""

    # Construct request model with validation
    try:
        _request = _models.MessagesBatchModifyRequest(
            path=_models.MessagesBatchModifyRequestPath(user_id=user_id),
            body=_models.MessagesBatchModifyRequestBody(add_label_ids=add_label_ids, ids=ids, remove_label_ids=remove_label_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_message_labels_batch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages/batchModify", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages/batchModify"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_message_labels_batch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_message_labels_batch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_message_labels_batch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_message(
    user_id: str = Field(..., alias="userId", description="The user's email address or the special value `me` to indicate the authenticated user."),
    id_: str = Field(..., alias="id", description="The ID of the message to retrieve, typically obtained from messages.list, messages.insert, or messages.import operations."),
    format_: Literal["minimal", "full", "raw", "metadata"] | None = Field(None, alias="format", description="The format in which to return the message content and structure."),
    metadata_headers: list[str] | None = Field(None, alias="metadataHeaders", description="When format is set to `metadata`, specify which message headers to include in the response. Headers should be provided as an array of header names."),
) -> dict[str, Any]:
    """Retrieves a specific message by ID from the user's mailbox. Supports multiple output formats including full message content, headers only, or raw RFC 2822 format."""

    # Construct request model with validation
    try:
        _request = _models.MessagesGetRequest(
            path=_models.MessagesGetRequestPath(user_id=user_id, id_=id_),
            query=_models.MessagesGetRequestQuery(format_=format_, metadata_headers=metadata_headers)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_message", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_message",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_message(
    user_id: str = Field(..., alias="userId", description="The email address of the user whose message will be deleted. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the message to delete."),
) -> dict[str, Any]:
    """Permanently and immediately deletes a specified message. This action cannot be undone; consider using trash_message for recoverable deletion instead."""

    # Construct request model with validation
    try:
        _request = _models.MessagesDeleteRequest(
            path=_models.MessagesDeleteRequestPath(user_id=user_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_message", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_message",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def import_message(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value 'me' to reference the authenticated user."),
    deleted: bool | None = Field(None, description="Mark the message as permanently deleted and only visible to Google Vault administrators. Only applicable for Google Workspace accounts."),
    internal_date_source: Literal["receivedTime", "dateHeader"] | None = Field(None, alias="internalDateSource", description="Determines the source for Gmail's internal date assignment to the message."),
    never_mark_spam: bool | None = Field(None, alias="neverMarkSpam", description="Prevent Gmail's spam classifier from marking this message as SPAM, regardless of its classification decision."),
    process_for_calendar: bool | None = Field(None, alias="processForCalendar", description="Automatically process calendar invitations in the message and add any extracted meetings to the user's Google Calendar."),
    classification_label_values: list[_models.ClassificationLabelValue] | None = Field(None, alias="classificationLabelValues", description="Classification label values to apply to the message. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only applicable for Google Workspace accounts. Available schemas can be queried using the Google Drive Labels API."),
    label_ids: list[str] | None = Field(None, alias="labelIds", description="List of label IDs to apply to the imported message. Labels are applied in the order provided."),
    email_from: str | None = Field(None, description="Sender email address (From header)"),
    email_to: str | None = Field(None, description="Recipient email address (To header)"),
    email_cc: str | None = Field(None, description="Carbon copy recipients (Cc header), comma-separated"),
    email_bcc: str | None = Field(None, description="Blind carbon copy recipients (Bcc header), comma-separated"),
    email_subject: str | None = Field(None, description="Email subject line"),
    email_body: str | None = Field(None, description="Email body content (plain text or HTML)"),
    email_body_is_html: bool | None = Field(None, description="Whether email_body is HTML (True) or plain text (False)"),
    email_reply_to: str | None = Field(None, description="Reply-To header address"),
    email_in_reply_to: str | None = Field(None, description="In-Reply-To header (Message-ID of original message)"),
    email_references: str | None = Field(None, description="References header (Message-IDs of related messages), space-separated"),
) -> dict[str, Any]:
    """Imports a message into the user's mailbox with standard email delivery scanning and classification. The message is processed similarly to SMTP delivery, with a maximum size limit of 150MB."""

    # Call helper functions
    raw = build_raw_message(email_from, email_to, email_cc, email_bcc, email_subject, email_body, email_body_is_html, email_reply_to, email_in_reply_to, email_references)

    # Construct request model with validation
    try:
        _request = _models.MessagesImportRequest(
            path=_models.MessagesImportRequestPath(user_id=user_id),
            query=_models.MessagesImportRequestQuery(deleted=deleted, internal_date_source=internal_date_source, never_mark_spam=never_mark_spam, process_for_calendar=process_for_calendar),
            body=_models.MessagesImportRequestBody(classification_label_values=classification_label_values, label_ids=label_ids, raw=raw)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for import_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages/import", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages/import"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "message/cpim"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("import_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("import_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="import_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="message/cpim",
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_messages(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    include_spam_trash: bool | None = Field(None, alias="includeSpamTrash", description="Include messages from SPAM and TRASH folders in the results. Defaults to false if not specified."),
    label_ids: list[str] | None = Field(None, alias="labelIds", description="Filter results to only include messages with labels matching all specified label IDs. Messages within the same thread may have different labels. Provide as an array of label ID strings."),
    max_results: int | None = Field(None, alias="maxResults", description="Maximum number of messages to return per request. Defaults to 100 if not specified."),
    from_address: str | None = Field(None, description="Filter messages from a specific sender email address"),
    to_address: str | None = Field(None, description="Filter messages to a specific recipient email address"),
    subject_contains: str | None = Field(None, description="Filter messages with subject containing this text"),
    has_attachment: bool | None = Field(None, description="Filter messages that have attachments"),
    is_unread: bool | None = Field(None, description="Filter unread messages only"),
    is_starred: bool | None = Field(None, description="Filter starred messages only"),
    before_date: str | None = Field(None, description="Filter messages before this date (YYYY/MM/DD format)"),
    after_date: str | None = Field(None, description="Filter messages after this date (YYYY/MM/DD format)"),
    custom_query: str | None = Field(None, description="Custom Gmail query string for advanced filters (e.g., 'rfc822msgid:<id>')"),
) -> dict[str, Any]:
    """Retrieves a list of messages from the user's mailbox, with optional filtering by labels and inclusion of spam/trash folders. Supports pagination through the maxResults parameter."""

    # Call helper functions
    q = build_gmail_query(from_address, to_address, subject_contains, has_attachment, is_unread, is_starred, before_date, after_date, custom_query)

    # Construct request model with validation
    try:
        _request = _models.MessagesListRequest(
            path=_models.MessagesListRequestPath(user_id=user_id),
            query=_models.MessagesListRequestQuery(include_spam_trash=include_spam_trash, label_ids=label_ids, max_results=max_results, q=q)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_messages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def insert_message(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value 'me' to refer to the authenticated user."),
    deleted: bool | None = Field(None, description="Mark the message as permanently deleted and only visible to Google Vault administrators. Only applicable for Google Workspace accounts."),
    internal_date_source: Literal["receivedTime", "dateHeader"] | None = Field(None, alias="internalDateSource", description="Determines the source for Gmail's internal date assigned to the message."),
    classification_label_values: list[_models.ClassificationLabelValue] | None = Field(None, alias="classificationLabelValues", description="Classification label values to apply to the message. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only applicable for Google Workspace accounts. Available schemas can be queried via the Google Drive Labels API."),
    label_ids: list[str] | None = Field(None, alias="labelIds", description="List of label IDs to apply to this message. Labels are applied in the order provided."),
    email_from: str | None = Field(None, description="Sender email address (From header)"),
    email_to: str | None = Field(None, description="Recipient email address (To header)"),
    email_cc: str | None = Field(None, description="Carbon copy recipients (Cc header), comma-separated"),
    email_bcc: str | None = Field(None, description="Blind carbon copy recipients (Bcc header), comma-separated"),
    email_subject: str | None = Field(None, description="Email subject line"),
    email_body: str | None = Field(None, description="Email body content (plain text or HTML)"),
    email_body_is_html: bool | None = Field(None, description="Whether email_body is HTML (True) or plain text (False)"),
    email_reply_to: str | None = Field(None, description="Reply-To header address"),
    email_in_reply_to: str | None = Field(None, description="In-Reply-To header (Message-ID of original message)"),
    email_references: str | None = Field(None, description="References header (Message-IDs of related messages), space-separated"),
) -> dict[str, Any]:
    """Inserts a message directly into the user's mailbox, bypassing scanning and classification, similar to IMAP APPEND. This operation does not send a message but adds it to the mailbox with optional metadata."""

    # Call helper functions
    raw = build_raw_message(email_from, email_to, email_cc, email_bcc, email_subject, email_body, email_body_is_html, email_reply_to, email_in_reply_to, email_references)

    # Construct request model with validation
    try:
        _request = _models.MessagesInsertRequest(
            path=_models.MessagesInsertRequestPath(user_id=user_id),
            query=_models.MessagesInsertRequestQuery(deleted=deleted, internal_date_source=internal_date_source),
            body=_models.MessagesInsertRequestBody(classification_label_values=classification_label_values, label_ids=label_ids, raw=raw)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for insert_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "message/cpim"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("insert_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("insert_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="insert_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="message/cpim",
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def update_message_labels(
    user_id: str = Field(..., alias="userId", description="The email address of the user whose message will be modified. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the message to modify."),
    add_label_ids: list[str] | None = Field(None, alias="addLabelIds", description="A list of label IDs to add to the message. Maximum of 100 labels can be added in a single request."),
    remove_label_ids: list[str] | None = Field(None, alias="removeLabelIds", description="A list of label IDs to remove from the message. Maximum of 100 labels can be removed in a single request."),
) -> dict[str, Any]:
    """Updates the labels applied to a specific message by adding and/or removing label IDs. You can modify up to 100 labels per request."""

    # Construct request model with validation
    try:
        _request = _models.MessagesModifyRequest(
            path=_models.MessagesModifyRequestPath(user_id=user_id, id_=id_),
            body=_models.MessagesModifyRequestBody(add_label_ids=add_label_ids, remove_label_ids=remove_label_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_message_labels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages/{id}/modify", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages/{id}/modify"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_message_labels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_message_labels", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_message_labels",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def send_message(
    user_id: str = Field(..., alias="userId", description="The email address of the user sending the message. Use the special value `me` to refer to the authenticated user."),
    classification_label_values: list[_models.ClassificationLabelValue] | None = Field(None, alias="classificationLabelValues", description="Classification labels to apply to the message for organizational purposes. Each classification label ID must be unique; duplicate IDs will be deduplicated arbitrarily. Only available for Google Workspace accounts."),
    label_ids: list[str] | None = Field(None, alias="labelIds", description="IDs of labels to apply to the message. Labels help organize and categorize messages in Gmail."),
    email_from: str | None = Field(None, description="Sender email address (From header)"),
    email_to: str | None = Field(None, description="Recipient email address (To header)"),
    email_cc: str | None = Field(None, description="Carbon copy recipients (Cc header), comma-separated"),
    email_bcc: str | None = Field(None, description="Blind carbon copy recipients (Bcc header), comma-separated"),
    email_subject: str | None = Field(None, description="Email subject line"),
    email_body: str | None = Field(None, description="Email body content (plain text or HTML)"),
    email_body_is_html: bool | None = Field(None, description="Whether email_body is HTML (True) or plain text (False)"),
    email_reply_to: str | None = Field(None, description="Reply-To header address"),
    email_in_reply_to: str | None = Field(None, description="In-Reply-To header (Message-ID of original message)"),
    email_references: str | None = Field(None, description="References header (Message-IDs of related messages), space-separated"),
) -> dict[str, Any]:
    """Sends an email message to recipients specified in the To, Cc, and Bcc headers. The message is delivered immediately to all specified recipients."""

    # Call helper functions
    raw = build_raw_message(email_from, email_to, email_cc, email_bcc, email_subject, email_body, email_body_is_html, email_reply_to, email_in_reply_to, email_references)

    # Construct request model with validation
    try:
        _request = _models.MessagesSendRequest(
            path=_models.MessagesSendRequestPath(user_id=user_id),
            body=_models.MessagesSendRequestBody(classification_label_values=classification_label_values, label_ids=label_ids, raw=raw)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages/send", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages/send"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}
    _http_headers["Content-Type"] = "message/cpim"

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="message/cpim",
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def move_message_to_trash(
    user_id: str = Field(..., alias="userId", description="The user's email address or the special value `me` to reference the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the message to move to trash."),
) -> dict[str, Any]:
    """Moves a specified message to the trash folder. The message can be restored from trash before permanent deletion."""

    # Construct request model with validation
    try:
        _request = _models.MessagesTrashRequest(
            path=_models.MessagesTrashRequestPath(user_id=user_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_message_to_trash: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages/{id}/trash", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages/{id}/trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_message_to_trash")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_message_to_trash", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_message_to_trash",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def remove_message_from_trash(
    user_id: str = Field(..., alias="userId", description="The email address of the user whose message should be restored. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the message to restore from trash."),
) -> dict[str, Any]:
    """Restores a message from the trash by removing it from the trash folder. The message will be returned to its previous labels or inbox."""

    # Construct request model with validation
    try:
        _request = _models.MessagesUntrashRequest(
            path=_models.MessagesUntrashRequestPath(user_id=user_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_message_from_trash: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages/{id}/untrash", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages/{id}/untrash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_message_from_trash")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_message_from_trash", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_message_from_trash",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_message_attachment(
    user_id: str = Field(..., alias="userId", description="The email address of the account owner. Use the special value `me` to refer to the authenticated user's account."),
    message_id: str = Field(..., alias="messageId", description="The unique identifier of the message containing the attachment."),
    id_: str = Field(..., alias="id", description="The unique identifier of the attachment to retrieve."),
) -> dict[str, Any]:
    """Retrieves a specific attachment from a Gmail message. Use this to download or access attachment metadata by providing the message ID and attachment ID."""

    # Construct request model with validation
    try:
        _request = _models.MessagesAttachmentsGetRequest(
            path=_models.MessagesAttachmentsGetRequestPath(user_id=user_id, message_id=message_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_message_attachment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/messages/{messageId}/attachments/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/messages/{messageId}/attachments/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_message_attachment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_message_attachment", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_message_attachment",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_auto_forwarding(user_id: str = Field(..., alias="userId", description="The Gmail account identifier. Use the email address associated with the account, or use the special value \"me\" to refer to the authenticated user's account.")) -> dict[str, Any]:
    """Retrieves the auto-forwarding configuration for the specified Gmail account. This includes the forwarding address and whether auto-forwarding is enabled."""

    # Construct request model with validation
    try:
        _request = _models.SettingsGetAutoForwardingRequest(
            path=_models.SettingsGetAutoForwardingRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_auto_forwarding: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/autoForwarding", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/autoForwarding"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_auto_forwarding")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_auto_forwarding", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_auto_forwarding",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_vacation_settings(user_id: str = Field(..., alias="userId", description="The Gmail user account identifier. Use 'me' to refer to the authenticated user, or provide a specific email address.")) -> dict[str, Any]:
    """Retrieves the vacation responder settings for a Gmail account, including whether auto-reply is enabled and the message content."""

    # Construct request model with validation
    try:
        _request = _models.SettingsGetVacationRequest(
            path=_models.SettingsGetVacationRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_vacation_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/vacation", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/vacation"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_vacation_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_vacation_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_vacation_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_cse_identities(
    user_id: str = Field(..., alias="userId", description="The user's primary email address. Use the special value `me` to refer to the authenticated user."),
    page_size: int | None = Field(None, alias="pageSize", description="Maximum number of identities to return per page. If not specified, defaults to 20 entries."),
) -> dict[str, Any]:
    """Retrieves all client-side encrypted identities for an authenticated user. Administrators with domain-wide delegation can manage identities for their organization, while users managing their own identities require hardware key encryption to be enabled."""

    # Construct request model with validation
    try:
        _request = _models.SettingsCseIdentitiesListRequest(
            path=_models.SettingsCseIdentitiesListRequestPath(user_id=user_id),
            query=_models.SettingsCseIdentitiesListRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_cse_identities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/cse/identities", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/cse/identities"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_cse_identities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_cse_identities", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_cse_identities",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def create_cse_identity(
    user_id: str = Field(..., alias="userId", description="The requester's primary email address. Use the special value `me` to indicate the authenticated user."),
    email_address: str | None = Field(None, alias="emailAddress", description="The email address for the sending identity. Must be the primary email address of the authenticated user."),
) -> dict[str, Any]:
    """Creates and configures a client-side encryption identity for sending encrypted mail from a user account. The S/MIME certificate is published to a shared domain-wide directory, enabling secure communication within a Google Workspace organization."""

    # Construct request model with validation
    try:
        _request = _models.SettingsCseIdentitiesCreateRequest(
            path=_models.SettingsCseIdentitiesCreateRequestPath(user_id=user_id),
            body=_models.SettingsCseIdentitiesCreateRequestBody(email_address=email_address)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_cse_identity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/cse/identities", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/cse/identities"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_cse_identity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_cse_identity", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_cse_identity",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_cse_identity(
    user_id: str = Field(..., alias="userId", description="The requester's primary email address. Use the special value `me` to refer to the authenticated user."),
    cse_email_address: str = Field(..., alias="cseEmailAddress", description="The primary email address associated with the client-side encryption identity configuration to retrieve."),
) -> dict[str, Any]:
    """Retrieves a client-side encryption identity configuration for a specified email address. Administrators require service account with domain-wide delegation authority, while users require hardware key encryption to be enabled."""

    # Construct request model with validation
    try:
        _request = _models.SettingsCseIdentitiesGetRequest(
            path=_models.SettingsCseIdentitiesGetRequestPath(user_id=user_id, cse_email_address=cse_email_address)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_cse_identity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/cse/identities/{cseEmailAddress}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/cse/identities/{cseEmailAddress}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_cse_identity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_cse_identity", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_cse_identity",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_cse_identity(
    user_id: str = Field(..., alias="userId", description="The user's primary email address. Use the special value `me` to refer to the authenticated user."),
    cse_email_address: str = Field(..., alias="cseEmailAddress", description="The primary email address associated with the client-side encryption identity to be deleted."),
) -> dict[str, Any]:
    """Permanently deletes a client-side encryption identity, preventing further use for sending encrypted messages. The identity cannot be restored; create a new identity with the same configuration if needed."""

    # Construct request model with validation
    try:
        _request = _models.SettingsCseIdentitiesDeleteRequest(
            path=_models.SettingsCseIdentitiesDeleteRequestPath(user_id=user_id, cse_email_address=cse_email_address)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_cse_identity: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/cse/identities/{cseEmailAddress}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/cse/identities/{cseEmailAddress}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_cse_identity")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_cse_identity", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_cse_identity",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def update_cse_identity_keypair(
    user_id: str = Field(..., alias="userId", description="The user identifier. Use the special value `me` to refer to the authenticated user, or provide the user's primary email address."),
    email_address: str = Field(..., alias="emailAddress", description="The email address of the client-side encryption identity to update."),
    email_address2: str | None = Field(None, alias="emailAddress", description="The email address for the sending identity. Must be the primary email address of the authenticated user."),
) -> dict[str, Any]:
    """Associates a new key pair with an existing client-side encryption identity. The updated key pair must validate against Google's S/MIME certificate profiles. Requires either domain-wide delegation authority for administrators or hardware key encryption enabled for individual users."""

    # Construct request model with validation
    try:
        _request = _models.SettingsCseIdentitiesPatchRequest(
            path=_models.SettingsCseIdentitiesPatchRequestPath(user_id=user_id, email_address=email_address),
            body=_models.SettingsCseIdentitiesPatchRequestBody(email_address2=email_address2)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_cse_identity_keypair: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/cse/identities/{emailAddress}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/cse/identities/{emailAddress}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_cse_identity_keypair")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_cse_identity_keypair", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_cse_identity_keypair",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_cse_keypairs(
    user_id: str = Field(..., alias="userId", description="The user's primary email address. Use the special value `me` to refer to the authenticated user."),
    page_size: int | None = Field(None, alias="pageSize", description="Maximum number of key pairs to return per page. If not specified, defaults to 20 entries."),
) -> dict[str, Any]:
    """Retrieves all client-side encryption key pairs for a user. Administrators with domain-wide delegation can manage keypairs for users in their organization, while individual users require hardware key encryption to be enabled."""

    # Construct request model with validation
    try:
        _request = _models.SettingsCseKeypairsListRequest(
            path=_models.SettingsCseKeypairsListRequestPath(user_id=user_id),
            query=_models.SettingsCseKeypairsListRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_cse_keypairs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/cse/keypairs", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/cse/keypairs"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_cse_keypairs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_cse_keypairs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_cse_keypairs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def create_cse_keypair(
    user_id: str = Field(..., alias="userId", description="The user's primary email address. Use the special value `me` to refer to the authenticated user."),
    pkcs7: str | None = Field(None, description="The public key and its certificate chain in PKCS#7 format with PEM encoding and ASCII armor."),
    private_key_metadata: list[_models.CsePrivateKeyMetadata] | None = Field(None, alias="privateKeyMetadata", description="An ordered array of metadata objects for instances of this key pair's private key. Order significance and item structure should follow the API specification."),
) -> dict[str, Any]:
    """Creates and uploads a client-side encryption S/MIME public key certificate chain and private key metadata for Gmail. Requires either domain-wide delegation authority for administrators or hardware key encryption enabled for individual users."""

    # Construct request model with validation
    try:
        _request = _models.SettingsCseKeypairsCreateRequest(
            path=_models.SettingsCseKeypairsCreateRequestPath(user_id=user_id),
            body=_models.SettingsCseKeypairsCreateRequestBody(pkcs7=pkcs7, private_key_metadata=private_key_metadata)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_cse_keypair: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/cse/keypairs", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/cse/keypairs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_cse_keypair")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_cse_keypair", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_cse_keypair",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def disable_cse_keypair(
    user_id: str = Field(..., alias="userId", description="The user's primary email address. Use the special value 'me' to refer to the authenticated user."),
    key_pair_id: str = Field(..., alias="keyPairId", description="The unique identifier of the key pair to disable."),
) -> dict[str, Any]:
    """Disables a client-side encryption key pair, preventing the user from decrypting incoming CSE messages or signing outgoing CSE mail. The key pair can be re-enabled later using enable_cse_keypair, or permanently deleted after 30 days using obliterate_cse_keypair."""

    # Construct request model with validation
    try:
        _request = _models.SettingsCseKeypairsDisableRequest(
            path=_models.SettingsCseKeypairsDisableRequestPath(user_id=user_id, key_pair_id=key_pair_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for disable_cse_keypair: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/cse/keypairs/{keyPairId}:disable", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/cse/keypairs/{keyPairId}:disable"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("disable_cse_keypair")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("disable_cse_keypair", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="disable_cse_keypair",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def enable_cse_keypair(
    user_id: str = Field(..., alias="userId", description="The user's primary email address. Use the special value `me` to refer to the authenticated user."),
    key_pair_id: str = Field(..., alias="keyPairId", description="The unique identifier of the key pair to reactivate."),
) -> dict[str, Any]:
    """Reactivates a previously disabled client-side encryption key pair for use with associated encryption identities. Administrators require service account with domain-wide delegation authority; end users require hardware key encryption to be enabled."""

    # Construct request model with validation
    try:
        _request = _models.SettingsCseKeypairsEnableRequest(
            path=_models.SettingsCseKeypairsEnableRequestPath(user_id=user_id, key_pair_id=key_pair_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for enable_cse_keypair: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/cse/keypairs/{keyPairId}:enable", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/cse/keypairs/{keyPairId}:enable"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("enable_cse_keypair")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("enable_cse_keypair", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="enable_cse_keypair",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_cse_keypair(
    user_id: str = Field(..., alias="userId", description="The email address of the user whose key pair is being retrieved. Use the special value `me` to refer to the authenticated user."),
    key_pair_id: str = Field(..., alias="keyPairId", description="The unique identifier of the encryption key pair to retrieve."),
) -> dict[str, Any]:
    """Retrieves a client-side encryption key pair for Gmail. Administrators require service account authorization with domain-wide delegation, while users must have hardware key encryption enabled."""

    # Construct request model with validation
    try:
        _request = _models.SettingsCseKeypairsGetRequest(
            path=_models.SettingsCseKeypairsGetRequestPath(user_id=user_id, key_pair_id=key_pair_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_cse_keypair: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/cse/keypairs/{keyPairId}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/cse/keypairs/{keyPairId}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_cse_keypair")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_cse_keypair", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_cse_keypair",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_cse_keypair_permanently(
    user_id: str = Field(..., alias="userId", description="The email address of the user whose key pair will be obliterated. Use the special value `me` to refer to the authenticated user."),
    key_pair_id: str = Field(..., alias="keyPairId", description="The unique identifier of the key pair to permanently delete."),
) -> dict[str, Any]:
    """Permanently and immediately deletes a client-side encryption key pair. The key pair must be disabled for at least 30 days before obliteration. Once obliterated, all messages encrypted with this key become permanently inaccessible to all users."""

    # Construct request model with validation
    try:
        _request = _models.SettingsCseKeypairsObliterateRequest(
            path=_models.SettingsCseKeypairsObliterateRequestPath(user_id=user_id, key_pair_id=key_pair_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_cse_keypair_permanently: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/cse/keypairs/{keyPairId}:obliterate", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/cse/keypairs/{keyPairId}:obliterate"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_cse_keypair_permanently")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_cse_keypair_permanently", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_cse_keypair_permanently",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_delegates(user_id: str = Field(..., alias="userId", description="The Gmail user account identifier. Use the special value 'me' to refer to the authenticated user, or provide the user's full email address.")) -> dict[str, Any]:
    """Retrieves the list of delegates for the specified Gmail account. This operation requires service account credentials with domain-wide delegation authority."""

    # Construct request model with validation
    try:
        _request = _models.SettingsDelegatesListRequest(
            path=_models.SettingsDelegatesListRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_delegates: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/delegates", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/delegates"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_delegates")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_delegates", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_delegates",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_delegate(
    user_id: str = Field(..., alias="userId", description="The email address of the user whose delegates are being queried. Use the special value 'me' to refer to the authenticated user."),
    delegate_email: str = Field(..., alias="delegateEmail", description="The primary email address of the delegate whose relationship details should be retrieved. Email aliases cannot be used; the primary email address is required."),
) -> dict[str, Any]:
    """Retrieves the delegate relationship for a specified email address. This operation requires service account clients with domain-wide authority and uses the delegate's primary email address (not aliases)."""

    # Construct request model with validation
    try:
        _request = _models.SettingsDelegatesGetRequest(
            path=_models.SettingsDelegatesGetRequestPath(user_id=user_id, delegate_email=delegate_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_delegate: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/delegates/{delegateEmail}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/delegates/{delegateEmail}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_delegate")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_delegate", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_delegate",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_filters(user_id: str = Field(..., alias="userId", description="The Gmail user account identifier. Use the special value 'me' to refer to the authenticated user, or provide a specific email address.")) -> dict[str, Any]:
    """Retrieves all message filters configured for a Gmail account. Filters define rules for automatically organizing, labeling, or processing incoming messages."""

    # Construct request model with validation
    try:
        _request = _models.SettingsFiltersListRequest(
            path=_models.SettingsFiltersListRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_filters: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/filters", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/filters"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_filters")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_filters", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_filters",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_filter(
    user_id: str = Field(..., alias="userId", description="The Gmail account identifier. Use 'me' to refer to the authenticated user, or provide the user's email address."),
    id_: str = Field(..., alias="id", description="The unique identifier of the filter to retrieve."),
) -> dict[str, Any]:
    """Retrieves a specific Gmail filter by its ID. Use this to fetch the configuration and rules of an existing filter."""

    # Construct request model with validation
    try:
        _request = _models.SettingsFiltersGetRequest(
            path=_models.SettingsFiltersGetRequestPath(user_id=user_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_filter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/filters/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/filters/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_filter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_filter", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_filter",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_filter(
    user_id: str = Field(..., alias="userId", description="The email address of the user whose filter will be deleted. Use the special value \"me\" to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the filter to be deleted."),
) -> dict[str, Any]:
    """Permanently deletes a specified Gmail filter. This action is immediate and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.SettingsFiltersDeleteRequest(
            path=_models.SettingsFiltersDeleteRequestPath(user_id=user_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_filter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/filters/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/filters/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_filter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_filter", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_filter",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_forwarding_addresses(user_id: str = Field(..., alias="userId", description="The Gmail account identifier. Use the authenticated user's email address, or specify 'me' to refer to the currently authenticated user.")) -> dict[str, Any]:
    """Retrieves all forwarding addresses configured for the specified Gmail account. Forwarding addresses are alternative email addresses where incoming messages can be automatically sent."""

    # Construct request model with validation
    try:
        _request = _models.SettingsForwardingAddressesListRequest(
            path=_models.SettingsForwardingAddressesListRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_forwarding_addresses: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/forwardingAddresses", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/forwardingAddresses"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_forwarding_addresses")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_forwarding_addresses", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_forwarding_addresses",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_forwarding_address(
    user_id: str = Field(..., alias="userId", description="The Gmail account identifier. Use the special value 'me' to refer to the authenticated user's account, or provide the user's full email address."),
    forwarding_email: str = Field(..., alias="forwardingEmail", description="The email address for which forwarding configuration should be retrieved."),
) -> dict[str, Any]:
    """Retrieves the configuration details for a specified forwarding address associated with a Gmail account. Use this to view forwarding settings for a particular email address."""

    # Construct request model with validation
    try:
        _request = _models.SettingsForwardingAddressesGetRequest(
            path=_models.SettingsForwardingAddressesGetRequestPath(user_id=user_id, forwarding_email=forwarding_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_forwarding_address: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/forwardingAddresses/{forwardingEmail}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/forwardingAddresses/{forwardingEmail}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_forwarding_address")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_forwarding_address", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_forwarding_address",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_forwarding_address(
    user_id: str = Field(..., alias="userId", description="The user's email address or 'me' to reference the authenticated user."),
    forwarding_email: str = Field(..., alias="forwardingEmail", description="The forwarding email address to delete."),
) -> dict[str, Any]:
    """Deletes a forwarding address and revokes any associated verification. This operation requires service account credentials with domain-wide delegation authority."""

    # Construct request model with validation
    try:
        _request = _models.SettingsForwardingAddressesDeleteRequest(
            path=_models.SettingsForwardingAddressesDeleteRequestPath(user_id=user_id, forwarding_email=forwarding_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_forwarding_address: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/forwardingAddresses/{forwardingEmail}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/forwardingAddresses/{forwardingEmail}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_forwarding_address")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_forwarding_address", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_forwarding_address",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_send_as_aliases(user_id: str = Field(..., alias="userId", description="The Gmail account identifier. Use 'me' to reference the authenticated user's account.")) -> dict[str, Any]:
    """Retrieves all send-as aliases configured for the specified Gmail account, including the primary email address and any custom 'from' aliases."""

    # Construct request model with validation
    try:
        _request = _models.SettingsSendAsListRequest(
            path=_models.SettingsSendAsListRequestPath(user_id=user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_send_as_aliases: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/sendAs", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/sendAs"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_send_as_aliases")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_send_as_aliases", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_send_as_aliases",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_send_as_alias(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value 'me' to refer to the authenticated user."),
    send_as_email: str = Field(..., alias="sendAsEmail", description="The email address of the send-as alias to retrieve."),
) -> dict[str, Any]:
    """Retrieves a specific send-as alias configuration for a user. Returns an HTTP 404 error if the specified email address is not configured as a send-as alias."""

    # Construct request model with validation
    try:
        _request = _models.SettingsSendAsGetRequest(
            path=_models.SettingsSendAsGetRequestPath(user_id=user_id, send_as_email=send_as_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_send_as_alias: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_send_as_alias")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_send_as_alias", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_send_as_alias",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def update_send_as_alias(
    user_id: str = Field(..., alias="userId", description="The Gmail user's email address. Use the special value 'me' to refer to the authenticated user."),
    send_as_email: str = Field(..., alias="sendAsEmail", description="The email address of the send-as alias to be updated."),
    send_as_email2: str | None = Field(None, alias="sendAsEmail", description="The email address displayed in the 'From:' header for messages sent using this alias. This field is read-only and cannot be modified after creation."),
    display_name: str | None = Field(None, alias="displayName", description="The display name shown in the 'From:' header for messages sent using this alias. If empty for custom addresses, Gmail will use the primary account's name. Updates to this field may be silently ignored if the admin has restricted name format changes."),
    is_default: bool | None = Field(None, alias="isDefault", description="Whether this alias is the default 'From:' address for new messages and auto-replies. Only 'true' can be written; setting this to true automatically sets the previous default address to false. Every Gmail account must have exactly one default send-as address."),
    reply_to_address: str | None = Field(None, alias="replyToAddress", description="An optional email address to include in the 'Reply-To:' header for messages sent using this alias. Leave empty to omit the 'Reply-To:' header."),
    signature: str | None = Field(None, description="An optional HTML signature appended to new emails composed with this alias in Gmail's web interface. Gmail will sanitize the HTML before saving."),
    host: str | None = Field(None, description="The hostname of the SMTP server used for sending mail through this alias."),
    password: str | None = Field(None, description="The password for SMTP authentication. This write-only field is used only during creation or updates and is never returned in responses."),
    port: str | None = Field(None, description="The port number of the SMTP server."),
    security_mode: Literal["securityModeUnspecified", "none", "ssl", "starttls"] | None = Field(None, alias="securityMode", description="The security protocol for SMTP communication."),
    username: str | None = Field(None, description="The username for SMTP authentication. This write-only field is used only during creation or updates and is never returned in responses."),
    treat_as_alias: bool | None = Field(None, alias="treatAsAlias", description="Whether Gmail should treat this address as an alias for the user's primary email address. This setting applies only to custom 'from' aliases."),
) -> dict[str, Any]:
    """Updates a send-as alias configuration for a Gmail account, including display name, reply-to address, and optional HTML signature. Service accounts with domain-wide delegation can update non-primary addresses; standard users can only modify their own aliases."""

    _port = _parse_int(port)

    # Construct request model with validation
    try:
        _request = _models.SettingsSendAsUpdateRequest(
            path=_models.SettingsSendAsUpdateRequestPath(user_id=user_id, send_as_email=send_as_email),
            body=_models.SettingsSendAsUpdateRequestBody(send_as_email=send_as_email2, display_name=display_name, is_default=is_default, reply_to_address=reply_to_address, signature=signature, treat_as_alias=treat_as_alias,
                smtp_msa=_models.SettingsSendAsUpdateRequestBodySmtpMsa(host=host, password=password, port=_port, security_mode=security_mode, username=username) if any(v is not None for v in [host, password, port, security_mode, username]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_send_as_alias: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_send_as_alias")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_send_as_alias", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_send_as_alias",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def update_send_as_alias_partial(
    user_id: str = Field(..., alias="userId", description="The Gmail account identifier. Use 'me' to refer to the authenticated user, or provide a specific email address."),
    send_as_email: str = Field(..., alias="sendAsEmail", description="The email address of the send-as alias to update."),
    send_as_email2: str | None = Field(None, alias="sendAsEmail", description="The email address displayed in the 'From:' header for messages sent using this alias. This field is read-only for updates and can only be set during alias creation."),
    display_name: str | None = Field(None, alias="displayName", description="The display name shown in the 'From:' header for messages sent using this alias. If empty, Gmail uses the primary account's name. Updates may be silently ignored if the admin has restricted name format changes."),
    is_default: bool | None = Field(None, alias="isDefault", description="Set to true to make this the default 'From:' address for new messages and auto-replies. Only true is a valid value for updates; setting this true automatically sets the previous default to false."),
    reply_to_address: str | None = Field(None, alias="replyToAddress", description="An optional email address to include in the 'Reply-To:' header for messages sent using this alias. Leave empty to omit the Reply-To header."),
    signature: str | None = Field(None, description="An optional HTML signature appended to new emails composed with this alias in Gmail's web interface. This signature is not added to replies or forwarded messages."),
    host: str | None = Field(None, description="The hostname of the SMTP server used to send mail through this alias."),
    password: str | None = Field(None, description="The password for SMTP authentication. This write-only field is never returned in responses and must be provided when configuring SMTP settings."),
    port: str | None = Field(None, description="The port number of the SMTP server. Common values are 25, 465, or 587 depending on the security mode."),
    security_mode: Literal["securityModeUnspecified", "none", "ssl", "starttls"] | None = Field(None, alias="securityMode", description="The security protocol for SMTP communication. Determines how the connection to the SMTP server is encrypted or secured."),
    username: str | None = Field(None, description="The username for SMTP authentication. This write-only field is never returned in responses and must be provided when configuring SMTP settings."),
    treat_as_alias: bool | None = Field(None, alias="treatAsAlias", description="Whether Gmail should treat this address as an alias for the user's primary email address. This setting only applies to custom 'from' aliases and affects how Gmail handles replies and threading."),
) -> dict[str, Any]:
    """Partially update a send-as alias configuration for a Gmail account. Use this to modify display name, default status, reply-to address, signature, SMTP settings, or alias treatment without replacing the entire resource."""

    _port = _parse_int(port)

    # Construct request model with validation
    try:
        _request = _models.SettingsSendAsPatchRequest(
            path=_models.SettingsSendAsPatchRequestPath(user_id=user_id, send_as_email=send_as_email),
            body=_models.SettingsSendAsPatchRequestBody(send_as_email=send_as_email2, display_name=display_name, is_default=is_default, reply_to_address=reply_to_address, signature=signature, treat_as_alias=treat_as_alias,
                smtp_msa=_models.SettingsSendAsPatchRequestBodySmtpMsa(host=host, password=password, port=_port, security_mode=security_mode, username=username) if any(v is not None for v in [host, password, port, security_mode, username]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_send_as_alias_partial: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_send_as_alias_partial")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_send_as_alias_partial", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_send_as_alias_partial",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def send_verification_email_to_send_as_alias(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value 'me' to refer to the authenticated user."),
    send_as_email: str = Field(..., alias="sendAsEmail", description="The send-as alias email address that requires verification."),
) -> dict[str, Any]:
    """Sends a verification email to a send-as alias address to confirm ownership. The alias must have a pending verification status and requires service account with domain-wide delegation authority."""

    # Construct request model with validation
    try:
        _request = _models.SettingsSendAsVerifyRequest(
            path=_models.SettingsSendAsVerifyRequestPath(user_id=user_id, send_as_email=send_as_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_verification_email_to_send_as_alias: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/verify", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/verify"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_verification_email_to_send_as_alias")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_verification_email_to_send_as_alias", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_verification_email_to_send_as_alias",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_smime_info(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    send_as_email: str = Field(..., alias="sendAsEmail", description="The email address that appears in the From header for messages sent using this send-as alias."),
    id_: str = Field(..., alias="id", description="The immutable identifier for the S/MIME configuration."),
) -> dict[str, Any]:
    """Retrieves the S/MIME configuration for a specified send-as alias. This allows you to access the details of a specific S/MIME certificate associated with an email alias."""

    # Construct request model with validation
    try:
        _request = _models.SettingsSendAsSmimeInfoGetRequest(
            path=_models.SettingsSendAsSmimeInfoGetRequestPath(user_id=user_id, send_as_email=send_as_email, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_smime_info: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/smimeInfo/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/smimeInfo/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_smime_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_smime_info", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_smime_info",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_send_as_smime_config(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    send_as_email: str = Field(..., alias="sendAsEmail", description="The email address that appears in the From header for messages sent using this send-as alias."),
    id_: str = Field(..., alias="id", description="The immutable identifier for the S/MIME configuration to delete."),
) -> dict[str, Any]:
    """Deletes the S/MIME configuration for a specified send-as alias. This removes the security certificate associated with the alias used for signing and encrypting outgoing emails."""

    # Construct request model with validation
    try:
        _request = _models.SettingsSendAsSmimeInfoDeleteRequest(
            path=_models.SettingsSendAsSmimeInfoDeleteRequestPath(user_id=user_id, send_as_email=send_as_email, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_send_as_smime_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/smimeInfo/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/smimeInfo/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_send_as_smime_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_send_as_smime_config", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_send_as_smime_config",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_smime_configs(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    send_as_email: str = Field(..., alias="sendAsEmail", description="The email address configured as a send-as alias. This is the address that appears in the From header for emails sent using this alias."),
) -> dict[str, Any]:
    """Lists all S/MIME configurations for a specified send-as alias. S/MIME configs define the certificates and encryption settings used when sending emails from this alias."""

    # Construct request model with validation
    try:
        _request = _models.SettingsSendAsSmimeInfoListRequest(
            path=_models.SettingsSendAsSmimeInfoListRequestPath(user_id=user_id, send_as_email=send_as_email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_smime_configs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/smimeInfo", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/smimeInfo"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_smime_configs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_smime_configs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_smime_configs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def create_smime_config(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    send_as_email: str = Field(..., alias="sendAsEmail", description="The email address that will appear in the From header for messages sent using this S/MIME alias."),
    encrypted_key_password: str | None = Field(None, alias="encryptedKeyPassword", description="Password for the encrypted private key, required if the PKCS#12 certificate is password-protected."),
    expiration: str | None = Field(None, description="Certificate expiration timestamp in milliseconds since epoch (Unix time)."),
    is_default: bool | None = Field(None, alias="isDefault", description="Whether to set this S/MIME certificate as the default for this send-as address."),
    pkcs12: str | None = Field(None, description="The S/MIME certificate in PKCS#12 format. Must contain a single private/public key pair and certificate chain. The private key may be encrypted; if so, provide the password in encryptedKeyPassword."),
) -> dict[str, Any]:
    """Upload and configure an S/MIME certificate for a send-as alias. The certificate must be provided in PKCS#12 format containing a private/public key pair and certificate chain."""

    # Construct request model with validation
    try:
        _request = _models.SettingsSendAsSmimeInfoInsertRequest(
            path=_models.SettingsSendAsSmimeInfoInsertRequestPath(user_id=user_id, send_as_email=send_as_email),
            body=_models.SettingsSendAsSmimeInfoInsertRequestBody(encrypted_key_password=encrypted_key_password, expiration=expiration, is_default=is_default, pkcs12=pkcs12)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_smime_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/smimeInfo", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/smimeInfo"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_smime_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_smime_config", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_smime_config",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def set_default_smime_config(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    send_as_email: str = Field(..., alias="sendAsEmail", description="The email address that appears in the From header for mail sent using this send-as alias."),
    id_: str = Field(..., alias="id", description="The immutable identifier for the S/MIME configuration to set as default."),
) -> dict[str, Any]:
    """Sets the default S/MIME configuration for the specified send-as alias. This determines which S/MIME certificate will be used by default when sending emails from this alias."""

    # Construct request model with validation
    try:
        _request = _models.SettingsSendAsSmimeInfoSetDefaultRequest(
            path=_models.SettingsSendAsSmimeInfoSetDefaultRequestPath(user_id=user_id, send_as_email=send_as_email, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for set_default_smime_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/smimeInfo/{id}/setDefault", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/settings/sendAs/{sendAsEmail}/smimeInfo/{id}/setDefault"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("set_default_smime_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("set_default_smime_config", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="set_default_smime_config",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def get_thread(
    user_id: str = Field(..., alias="userId", description="The email address of the user whose thread should be retrieved. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the thread to retrieve."),
    format_: Literal["full", "metadata", "minimal"] | None = Field(None, alias="format", description="The format in which to return thread messages. Controls the level of detail included in the response."),
    metadata_headers: list[str] | None = Field(None, alias="metadataHeaders", description="When format is set to metadata, specify which email headers to include in the response. Headers should be provided as an array of header names."),
) -> dict[str, Any]:
    """Retrieves a specific email thread by ID. Returns thread messages in the requested format with optional filtering of metadata headers."""

    # Construct request model with validation
    try:
        _request = _models.ThreadsGetRequest(
            path=_models.ThreadsGetRequestPath(user_id=user_id, id_=id_),
            query=_models.ThreadsGetRequestQuery(format_=format_, metadata_headers=metadata_headers)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_thread: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/threads/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/threads/{id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_thread")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_thread", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_thread",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def delete_thread(
    user_id: str = Field(..., alias="userId", description="The email address of the user whose thread will be deleted. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the thread to delete."),
) -> dict[str, Any]:
    """Permanently deletes a thread and all messages within it. This action cannot be undone; consider using trash_thread as a safer alternative."""

    # Construct request model with validation
    try:
        _request = _models.ThreadsDeleteRequest(
            path=_models.ThreadsDeleteRequestPath(user_id=user_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_thread: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/threads/{id}", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/threads/{id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_thread")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_thread", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_thread",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def list_threads(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    include_spam_trash: bool | None = Field(None, alias="includeSpamTrash", description="Include threads from the SPAM and TRASH folders in the results."),
    label_ids: list[str] | None = Field(None, alias="labelIds", description="Filter results to only return threads that have all of the specified label IDs. Provide as an array of label ID strings."),
    max_results: int | None = Field(None, alias="maxResults", description="Maximum number of threads to return in the response."),
    q: str | None = Field(None, description="Filter results using Gmail search query syntax (e.g., sender, subject, date filters, read status). Not supported when using the gmail.metadata scope."),
) -> dict[str, Any]:
    """Retrieves a list of message threads from the user's mailbox, with optional filtering by labels, search query, and inclusion of spam/trash folders."""

    # Construct request model with validation
    try:
        _request = _models.ThreadsListRequest(
            path=_models.ThreadsListRequestPath(user_id=user_id),
            query=_models.ThreadsListRequestQuery(include_spam_trash=include_spam_trash, label_ids=label_ids, max_results=max_results, q=q)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_threads: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/threads", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/threads"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_threads")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_threads", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_threads",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def update_thread_labels(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The ID of the thread to modify."),
    add_label_ids: list[str] | None = Field(None, alias="addLabelIds", description="A list of label IDs to add to this thread. Up to 100 labels can be added per request."),
    remove_label_ids: list[str] | None = Field(None, alias="removeLabelIds", description="A list of label IDs to remove from this thread. Up to 100 labels can be removed per request."),
) -> dict[str, Any]:
    """Modifies the labels applied to a thread, affecting all messages within it. Supports adding and removing labels in a single operation."""

    # Construct request model with validation
    try:
        _request = _models.ThreadsModifyRequest(
            path=_models.ThreadsModifyRequestPath(user_id=user_id, id_=id_),
            body=_models.ThreadsModifyRequestBody(add_label_ids=add_label_ids, remove_label_ids=remove_label_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_thread_labels: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/threads/{id}/modify", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/threads/{id}/modify"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_thread_labels")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_thread_labels", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_thread_labels",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def move_thread_to_trash(
    user_id: str = Field(..., alias="userId", description="The user's email address or the special value 'me' to reference the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the thread to move to trash."),
) -> dict[str, Any]:
    """Moves a thread and all its associated messages to the trash. The thread and its messages can be permanently deleted or recovered from trash."""

    # Construct request model with validation
    try:
        _request = _models.ThreadsTrashRequest(
            path=_models.ThreadsTrashRequestPath(user_id=user_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_thread_to_trash: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/threads/{id}/trash", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/threads/{id}/trash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_thread_to_trash")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_thread_to_trash", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_thread_to_trash",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: users
@mcp.tool()
async def remove_thread_from_trash(
    user_id: str = Field(..., alias="userId", description="The user's email address. Use the special value `me` to refer to the authenticated user."),
    id_: str = Field(..., alias="id", description="The unique identifier of the thread to restore from trash."),
) -> dict[str, Any]:
    """Restores a thread from trash by removing it and all its associated messages from the trash folder."""

    # Construct request model with validation
    try:
        _request = _models.ThreadsUntrashRequest(
            path=_models.ThreadsUntrashRequestPath(user_id=user_id, id_=id_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_thread_from_trash: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/gmail/v1/users/{userId}/threads/{id}/untrash", _request.path.model_dump(by_alias=True)) if _request.path else "/gmail/v1/users/{userId}/threads/{id}/untrash"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_thread_from_trash")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_thread_from_trash", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_thread_from_trash",
        method="POST",
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
        print("  python gmail_api_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="Google Gmail MCP Server")

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
    logger.info("Starting Google Gmail MCP Server")
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

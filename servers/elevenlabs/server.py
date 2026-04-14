#!/usr/bin/env python3
"""
ElevenLabs MCP Server
Generated: 2026-04-14 18:20:45 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

import argparse
import asyncio
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
from typing import Annotated, Any, Literal

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
from pydantic import AfterValidator, Field

BASE_URL = os.getenv("BASE_URL", "")
SERVER_NAME = "ElevenLabs"
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

def build_voice_settings(stability: float | None = None, similarity_boost: float | None = None, style: float | None = None, use_speaker_boost: bool | None = None) -> str | None:
    """Helper function for parameter transformation"""
    if all(v is None for v in [stability, similarity_boost, style, use_speaker_boost]):
        return None
    try:
        settings = {}
        if stability is not None:
            if not 0.0 <= stability <= 1.0:
                raise ValueError(f"stability must be between 0.0 and 1.0, got {stability}")
            settings['stability'] = stability
        if similarity_boost is not None:
            if not 0.0 <= similarity_boost <= 1.0:
                raise ValueError(f"similarity_boost must be between 0.0 and 1.0, got {similarity_boost}")
            settings['similarity_boost'] = similarity_boost
        if style is not None:
            if not 0.0 <= style <= 1.0:
                raise ValueError(f"style must be between 0.0 and 1.0, got {style}")
            settings['style'] = style
        if use_speaker_boost is not None:
            settings['use_speaker_boost'] = use_speaker_boost
        return json.dumps(settings)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to build voice settings: {e}") from e

def build_content_json(content_chapters: list[dict] | None = None, content_blocks: list[dict] | None = None, content_nodes: list[dict] | None = None) -> str | None:
    """Helper function for parameter transformation"""
    if content_chapters is None and content_blocks is None and content_nodes is None:
        return None

    try:
        chapters = content_chapters or []
        blocks = content_blocks or []
        nodes = content_nodes or []
        
        if not chapters:
            return None
        
        for chapter in chapters:
            if 'blocks' not in chapter:
                chapter['blocks'] = []
            for block in chapter['blocks']:
                if 'nodes' not in block:
                    block['nodes'] = []
                for node in block['nodes']:
                    if 'type' not in node:
                        node['type'] = 'tts_node'
        
        result = json.dumps(chapters)
        return result
    except Exception as e:
        raise ValueError(f"Failed to build content JSON structure: {e}") from e

def build_pronunciation_dictionary_locators(pronunciation_dict_ids: list[str] | None = None, pronunciation_dict_versions: list[str] | None = None) -> list[str] | None:
    """Helper function for parameter transformation"""
    if pronunciation_dict_ids is None and pronunciation_dict_versions is None:
        return None

    if not pronunciation_dict_ids:
        return None

    try:
        dict_ids = pronunciation_dict_ids or []
        dict_versions = pronunciation_dict_versions or []
        
        if len(dict_ids) != len(dict_versions):
            raise ValueError("pronunciation_dict_ids and pronunciation_dict_versions must have the same length")
        
        locators = []
        for dict_id, version_id in zip(dict_ids, dict_versions):
            locator_obj = {
                "pronunciation_dictionary_id": dict_id,
                "version_id": version_id
            }
            locators.append(json.dumps(locator_obj))
        
        return locators
    except Exception as e:
        raise ValueError(f"Failed to build pronunciation dictionary locators: {e}") from e

def parse_player_colors(value: str | None = None) -> dict | None:
    """Helper function for parameter transformation"""
    if value is None:
        return None
    parts = value.split(',')
    if len(parts) != 2:
        raise ValueError('player_colors must be in format "text_color,background_color"') from None
    text_color, background_color = parts[0].strip(), parts[1].strip()
    if not (text_color.startswith('#') and len(text_color) == 7):
        raise ValueError(f'text_color must be a valid hex color code, got {text_color}') from None
    if not (background_color.startswith('#') and len(background_color) == 7):
        raise ValueError(f'background_color must be a valid hex color code, got {background_color}') from None
    try:
        int(text_color[1:], 16)
        int(background_color[1:], 16)
    except ValueError as e:
        raise ValueError('player_colors must contain valid hex color codes') from e
    return {'text_color': text_color, 'background_color': background_color}

def build_rules(alias_rules: list[dict] | None = None, phoneme_rules: list[dict] | None = None) -> list[dict] | None:
    """Helper function for parameter transformation"""
    if alias_rules is None and phoneme_rules is None:
        return None

    rules = []

    if alias_rules:
        for rule in alias_rules:
            if not isinstance(rule, dict) or 'string_to_replace' not in rule or 'alias' not in rule:
                raise ValueError(f"Invalid alias rule: {rule}. Must contain 'string_to_replace' and 'alias' keys.") from None
            rules.append({
                'string_to_replace': rule['string_to_replace'],
                'type': 'alias',
                'alias': rule['alias']
            })

    if phoneme_rules:
        for rule in phoneme_rules:
            if not isinstance(rule, dict) or 'string_to_replace' not in rule or 'phoneme' not in rule or 'alphabet' not in rule:
                raise ValueError(f"Invalid phoneme rule: {rule}. Must contain 'string_to_replace', 'phoneme', and 'alphabet' keys.") from None
            rules.append({
                'string_to_replace': rule['string_to_replace'],
                'type': 'phoneme',
                'phoneme': rule['phoneme'],
                'alphabet': rule['alphabet']
            })

    return rules if rules else None

def _check_unique_items(v: list) -> list:
    """Validate that array items are unique (OAS uniqueItems: true)."""
    seen = []
    for item in v:
        if item in seen:
            raise ValueError("array items must be unique")
        seen.append(item)
    return v

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
    'xi_api_key',
]

# Initialize authentication handlers at server startup
_auth_handlers: dict[str, Any] = {}
try:
    _auth_handlers["xi_api_key"] = _auth.APIKeyAuth(env_var="API_KEY", location="header", param_name="xi-api-key")
    logging.info("Authentication configured: xi_api_key")
except ValueError as e:
    # Extract credential names from error message (first sentence before "Leave empty")
    error_msg = str(e).split("Leave empty")[0].strip()
    logging.warning(f"Credentials for xi_api_key not configured: {error_msg}")
    _auth_handlers["xi_api_key"] = None

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

mcp = FastMCP("ElevenLabs", middleware=[_JsonCoercionMiddleware()])

# Tags: speech-history
@mcp.tool()
async def list_speech_history(
    page_size: int | None = Field(None, description="Maximum number of history items to return per request. Useful for controlling response size and pagination."),
    start_after_history_item_id: str | None = Field(None, description="History item ID to start pagination after. Use this to fetch subsequent pages of results when working with large collections."),
    voice_id: str | None = Field(None, description="Filter results to a specific voice. Retrieve available voice IDs from the list voices endpoint."),
    model_id: str | None = Field(None, description="Filter results to a specific text-to-speech model."),
    date_before_unix: int | None = Field(None, description="Filter to history items created before this date (exclusive). Provide as a Unix timestamp."),
    date_after_unix: int | None = Field(None, description="Filter to history items created on or after this date (inclusive). Provide as a Unix timestamp."),
    sort_direction: Literal["asc", "desc"] | None = Field(None, description="Order results by creation date in ascending or descending order."),
    source: Literal["TTS", "STS"] | None = Field(None, description="Filter results by the source that generated the audio item."),
) -> dict[str, Any]:
    """Retrieve a paginated list of your generated audio items with optional filtering by voice, model, date range, and source. Results are ordered by creation date."""

    # Construct request model with validation
    try:
        _request = _models.GetSpeechHistoryRequest(
            query=_models.GetSpeechHistoryRequestQuery(page_size=page_size, start_after_history_item_id=start_after_history_item_id, voice_id=voice_id, model_id=model_id, date_before_unix=date_before_unix, date_after_unix=date_after_unix, sort_direction=sort_direction, source=source)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_speech_history: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/history"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_speech_history")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_speech_history", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_speech_history",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: speech-history
@mcp.tool()
async def get_speech_history_item(history_item_id: str = Field(..., description="The unique identifier of the history item to retrieve. You can obtain available history item IDs by calling the list speech history operation.")) -> dict[str, Any]:
    """Retrieves a specific speech synthesis history item by its ID. Use this to access details about a previously generated speech synthesis request."""

    # Construct request model with validation
    try:
        _request = _models.GetSpeechHistoryItemByIdRequest(
            path=_models.GetSpeechHistoryItemByIdRequestPath(history_item_id=history_item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_speech_history_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/history/{history_item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/history/{history_item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_speech_history_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_speech_history_item", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_speech_history_item",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: speech-history
@mcp.tool()
async def delete_history_item(history_item_id: str = Field(..., description="The unique identifier of the history item to delete. You can retrieve available history item IDs using the list history items endpoint.")) -> dict[str, Any]:
    """Delete a speech history item by its ID. This removes the item from your speech synthesis history."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSpeechHistoryItemRequest(
            path=_models.DeleteSpeechHistoryItemRequestPath(history_item_id=history_item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_history_item: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/history/{history_item_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/history/{history_item_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_history_item")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_history_item", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_history_item",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: speech-history
@mcp.tool()
async def get_speech_history_audio(history_item_id: str = Field(..., description="The unique identifier of the speech history item from which to retrieve the audio file.")) -> dict[str, Any]:
    """Retrieve the audio file associated with a specific speech synthesis history item. Use the history item ID obtained from the speech history list to download the generated audio."""

    # Construct request model with validation
    try:
        _request = _models.GetAudioFullFromSpeechHistoryItemRequest(
            path=_models.GetAudioFullFromSpeechHistoryItemRequestPath(history_item_id=history_item_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_speech_history_audio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/history/{history_item_id}/audio", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/history/{history_item_id}/audio"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_speech_history_audio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_speech_history_audio", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_speech_history_audio",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: speech-history
@mcp.tool()
async def download_speech_items(
    history_item_ids: list[str] = Field(..., description="List of history item IDs to download. Retrieve available IDs and metadata from the list speech history endpoint. Order is preserved in the output archive."),
    output_format: str | None = Field(None, description="Audio file format for transcoding. Specify the desired output format for the downloaded audio files."),
) -> dict[str, Any]:
    """Download one or more speech history items as audio files. Single items are returned as individual audio files, while multiple items are packaged into a .zip archive."""

    # Construct request model with validation
    try:
        _request = _models.DownloadSpeechHistoryItemsRequest(
            body=_models.DownloadSpeechHistoryItemsRequestBody(history_item_ids=history_item_ids, output_format=output_format)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_speech_items: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/history/download"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_speech_items")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_speech_items", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_speech_items",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: sound-generation
@mcp.tool()
async def generate_sound(
    text: str = Field(..., description="Detailed text description of the sound effect to generate. Be descriptive about the audio characteristics, environment, and desired qualities."),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio codec, sample rate, and bitrate for the generated sound. Higher bitrates and sample rates require appropriate subscription tiers."),
    loop: bool | None = Field(None, description="Enable seamless looping for the generated sound effect. Only supported with the eleven_text_to_sound_v2 model."),
    duration_seconds: float | None = Field(None, description="Target duration of the generated sound in seconds. If not specified, the optimal duration will be automatically determined from the text description."),
    prompt_influence: float | None = Field(None, description="Controls how strictly the generation adheres to the text description. Higher values produce more consistent results but less variation; lower values allow more creative freedom."),
    model_id: str | None = Field(None, description="The AI model to use for sound generation. Determines the quality and capabilities of the generated audio."),
) -> dict[str, Any]:
    """Generate realistic sound effects from text descriptions using advanced AI models. Perfect for video production, voice-overs, and game audio."""

    # Construct request model with validation
    try:
        _request = _models.SoundGenerationRequest(
            query=_models.SoundGenerationRequestQuery(output_format=output_format),
            body=_models.SoundGenerationRequestBody(text=text, loop=loop, duration_seconds=duration_seconds, prompt_influence=prompt_influence, model_id=model_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_sound: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/sound-generation"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_sound")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_sound", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_sound",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: audio-isolation
@mcp.tool()
async def isolate_audio(audio: str = Field(..., description="The audio file to process for noise removal and vocal/speech isolation. Accepts binary audio data in common formats.")) -> dict[str, Any]:
    """Removes background noise and isolates vocals or speech from an audio file. Returns the cleaned audio with background noise suppressed."""

    # Construct request model with validation
    try:
        _request = _models.AudioIsolationRequest(
            body=_models.AudioIsolationRequestBody(audio=audio)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for isolate_audio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/audio-isolation"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("isolate_audio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("isolate_audio", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="isolate_audio",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: audio-isolation
@mcp.tool()
async def isolate_audio_stream(audio: str = Field(..., description="The audio file to process for isolation. The audio data should be provided in binary format.")) -> dict[str, Any]:
    """Removes background noise from audio and streams the isolated vocals or speech. Processes the provided audio file and returns the cleaned result as a stream."""

    # Construct request model with validation
    try:
        _request = _models.AudioIsolationStreamRequest(
            body=_models.AudioIsolationStreamRequestBody(audio=audio)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for isolate_audio_stream: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/audio-isolation/stream"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("isolate_audio_stream")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("isolate_audio_stream", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="isolate_audio_stream",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: samples
@mcp.tool()
async def delete_voice_sample(
    voice_id: str = Field(..., description="The unique identifier of the voice containing the sample to delete."),
    sample_id: str = Field(..., description="The unique identifier of the sample to delete from the specified voice."),
) -> dict[str, Any]:
    """Permanently removes a sample from a voice by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSampleRequest(
            path=_models.DeleteSampleRequestPath(voice_id=voice_id, sample_id=sample_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_voice_sample: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/{voice_id}/samples/{sample_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/{voice_id}/samples/{sample_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_voice_sample")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_voice_sample", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_voice_sample",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: samples
@mcp.tool()
async def retrieve_voice_sample_audio(
    voice_id: str = Field(..., description="The unique identifier of the voice containing the sample. You can retrieve available voice IDs from the voices list endpoint."),
    sample_id: str = Field(..., description="The unique identifier of the sample within the specified voice. You can retrieve available sample IDs by fetching the voice details endpoint."),
) -> dict[str, Any]:
    """Retrieves the audio file associated with a specific sample attached to a voice. Use this to download or access audio data for voice samples."""

    # Construct request model with validation
    try:
        _request = _models.GetAudioFromSampleRequest(
            path=_models.GetAudioFromSampleRequestPath(voice_id=voice_id, sample_id=sample_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retrieve_voice_sample_audio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/{voice_id}/samples/{sample_id}/audio", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/{voice_id}/samples/{sample_id}/audio"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retrieve_voice_sample_audio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retrieve_voice_sample_audio", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retrieve_voice_sample_audio",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-speech
@mcp.tool()
async def generate_speech(
    voice_id: str = Field(..., description="The unique identifier of the voice to use for speech generation. Available voices can be retrieved from the voices endpoint."),
    text: str = Field(..., description="The text content to be converted into speech."),
    output_format: Literal["alaw_8000", "mp3_22050_32", "mp3_24000_48", "mp3_44100_128", "mp3_44100_192", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "opus_48000_128", "opus_48000_192", "opus_48000_32", "opus_48000_64", "opus_48000_96", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "pcm_8000", "ulaw_8000", "wav_16000", "wav_22050", "wav_24000", "wav_32000", "wav_44100", "wav_48000", "wav_8000"] | None = Field(None, description="The audio format and quality for the generated speech, specified as codec_sample_rate_bitrate. Higher bitrates and sample rates require higher subscription tiers. Defaults to MP3 at 44.1kHz with 128kbps bitrate."),
    model_id: str | None = Field(None, description="The AI model to use for speech generation. The model must support text-to-speech capability. Defaults to the multilingual v2 model."),
    language_code: str | None = Field(None, description="ISO 639-1 language code to enforce a specific language for the model and text normalization. The model must support the specified language or an error will be returned."),
    stability: float | None = Field(None, description="Controls voice consistency and emotional range. Lower values (closer to 0) produce more varied emotional expression, while higher values (closer to 1) create more consistent but potentially monotonous speech.", ge=0.0, le=1.0),
    similarity_boost: float | None = Field(None, description="Controls how closely the generated speech adheres to the original voice characteristics. Higher values maintain stronger voice similarity, while lower values allow more variation.", ge=0.0, le=1.0),
    style: float | None = Field(None, description="Amplifies the stylistic characteristics of the voice. A value of 0 applies no style exaggeration. Higher values increase style intensity but may increase latency and computational usage."),
    speed: float | None = Field(None, description="Adjusts speech playback speed. A value of 1.0 is normal speed; values below 1.0 slow down speech, while values above 1.0 speed it up."),
    pronunciation_dictionary_locators: list[_models.PronunciationDictionaryVersionLocatorRequestModel] | None = Field(None, description="A list of pronunciation dictionary locators to apply to the text in order. Each locator contains a pronunciation_dictionary_id and version_id. Maximum of 3 locators per request."),
    previous_request_ids: list[str] | None = Field(None, description="Request IDs of previously generated audio samples to maintain continuity when splitting large tasks. Improves speech flow when combining multiple generations. Maximum of 3 request IDs. Works best with the same model across generations."),
    next_request_ids: list[str] | None = Field(None, description="Request IDs of audio samples that follow this generation. Useful for maintaining natural flow when regenerating a sample within a sequence. Maximum of 3 request IDs. Works best with the same model across generations."),
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(None, description="Controls text normalization behavior. 'auto' lets the system decide, 'on' always applies normalization (e.g., spelling out numbers), and 'off' skips normalization entirely."),
    apply_language_text_normalization: bool | None = Field(None, description="Enables language-specific text normalization for improved pronunciation in supported languages. Currently only supported for Japanese. Warning: may significantly increase request latency."),
) -> dict[str, Any]:
    """Converts text into natural-sounding speech using a selected voice and returns audio in your preferred format. Supports voice customization through stability, similarity, style, and speed controls, with optional pronunciation dictionaries and continuity features for multi-part audio generation."""

    # Construct request model with validation
    try:
        _request = _models.TextToSpeechFullRequest(
            path=_models.TextToSpeechFullRequestPath(voice_id=voice_id),
            query=_models.TextToSpeechFullRequestQuery(output_format=output_format),
            body=_models.TextToSpeechFullRequestBody(text=text, model_id=model_id, language_code=language_code, pronunciation_dictionary_locators=pronunciation_dictionary_locators, previous_request_ids=previous_request_ids, next_request_ids=next_request_ids, apply_text_normalization=apply_text_normalization, apply_language_text_normalization=apply_language_text_normalization,
                voice_settings=_models.TextToSpeechFullRequestBodyVoiceSettings(stability=stability, similarity_boost=similarity_boost, style=style, speed=speed) if any(v is not None for v in [stability, similarity_boost, style, speed]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_speech: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/text-to-speech/{voice_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/text-to-speech/{voice_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_speech")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_speech", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_speech",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-speech
@mcp.tool()
async def generate_speech_with_timestamps(
    voice_id: str = Field(..., description="The voice identifier to use for speech generation. Available voices can be retrieved from the voices endpoint."),
    text: str = Field(..., description="The text content to convert into speech audio."),
    output_format: Literal["alaw_8000", "mp3_22050_32", "mp3_24000_48", "mp3_44100_128", "mp3_44100_192", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "opus_48000_128", "opus_48000_192", "opus_48000_32", "opus_48000_64", "opus_48000_96", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "pcm_8000", "ulaw_8000", "wav_16000", "wav_22050", "wav_24000", "wav_32000", "wav_44100", "wav_48000", "wav_8000"] | None = Field(None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and certain formats require higher subscription tiers."),
    model_id: str | None = Field(None, description="The AI model identifier to use for text-to-speech conversion. The model must support text-to-speech capability."),
    language_code: str | None = Field(None, description="ISO 639-1 language code to enforce language processing and text normalization. The model must support the specified language."),
    stability: float | None = Field(None, description="Voice stability control ranging from 0 (high emotional range) to 1 (monotonous). Lower values produce more expressive speech with greater variation.", ge=0.0, le=1.0),
    similarity_boost: float | None = Field(None, description="Voice similarity control ranging from 0 to 1. Higher values make the AI adhere more closely to the original voice characteristics.", ge=0.0, le=1.0),
    style: float | None = Field(None, description="Style exaggeration level for the voice. Non-zero values amplify the speaker's style but increase computational resources and latency."),
    speed: float | None = Field(None, description="Speech speed multiplier where 1.0 is normal speed, values below 1.0 slow down speech, and values above 1.0 speed it up."),
    pronunciation_dictionary_locators: list[_models.PronunciationDictionaryVersionLocatorRequestModel] | None = Field(None, description="List of pronunciation dictionary locators to apply to the text in order. Each locator contains a pronunciation_dictionary_id and version_id. Maximum of 3 locators per request."),
    previous_request_ids: list[str] | None = Field(None, description="Request IDs of previously generated speech samples to maintain continuity. Used when splitting large tasks across multiple requests. Maximum of 3 request IDs. Results are best when using the same model across generations."),
    next_request_ids: list[str] | None = Field(None, description="Request IDs of subsequent speech samples to maintain continuity. Useful for regenerating a sample while preserving natural flow with following audio. Maximum of 3 request IDs. Results are best when using the same model across generations."),
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(None, description="Text normalization mode: 'auto' applies normalization automatically, 'on' always applies it, 'off' disables it. Normalization handles conversions like spelling out numbers."),
    apply_language_text_normalization: bool | None = Field(None, description="Enable language-specific text normalization for proper pronunciation. Currently supported for Japanese only. Warning: may significantly increase request latency."),
) -> dict[str, Any]:
    """Convert text to speech audio with precise character-level timing information for synchronizing audio playback with text. Returns audio file and timestamp data for each character."""

    # Construct request model with validation
    try:
        _request = _models.TextToSpeechFullWithTimestampsRequest(
            path=_models.TextToSpeechFullWithTimestampsRequestPath(voice_id=voice_id),
            query=_models.TextToSpeechFullWithTimestampsRequestQuery(output_format=output_format),
            body=_models.TextToSpeechFullWithTimestampsRequestBody(text=text, model_id=model_id, language_code=language_code, pronunciation_dictionary_locators=pronunciation_dictionary_locators, previous_request_ids=previous_request_ids, next_request_ids=next_request_ids, apply_text_normalization=apply_text_normalization, apply_language_text_normalization=apply_language_text_normalization,
                voice_settings=_models.TextToSpeechFullWithTimestampsRequestBodyVoiceSettings(stability=stability, similarity_boost=similarity_boost, style=style, speed=speed) if any(v is not None for v in [stability, similarity_boost, style, speed]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_speech_with_timestamps: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/text-to-speech/{voice_id}/with-timestamps", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/text-to-speech/{voice_id}/with-timestamps"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_speech_with_timestamps")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_speech_with_timestamps", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_speech_with_timestamps",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-speech
@mcp.tool()
async def generate_speech_stream(
    voice_id: str = Field(..., description="The voice to use for speech generation. Available voices can be retrieved from the voices endpoint."),
    text: str = Field(..., description="The text content to convert into speech."),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and PCM formats require higher subscription tiers."),
    model_id: str | None = Field(None, description="The AI model to use for speech generation. Must support text-to-speech capability. Query available models via the models endpoint."),
    language_code: str | None = Field(None, description="ISO 639-1 language code to enforce language processing and text normalization. The model must support the specified language."),
    stability: float | None = Field(None, description="Voice stability control between 0.0 and 1.0. Lower values increase emotional range and variation; higher values produce more consistent, monotonous speech.", ge=0.0, le=1.0),
    similarity_boost: float | None = Field(None, description="Voice similarity adherence between 0.0 and 1.0. Controls how closely the generated speech matches the original voice characteristics.", ge=0.0, le=1.0),
    style: float | None = Field(None, description="Style exaggeration intensity. Amplifies the speaker's original style characteristics. Non-zero values increase computational cost and latency."),
    speed: float | None = Field(None, description="Speech speed multiplier. Use 1.0 for normal speed, values below 1.0 to slow down, and values above 1.0 to speed up."),
    pronunciation_dictionary_locators: list[_models.PronunciationDictionaryVersionLocatorRequestModel] | None = Field(None, description="Pronunciation dictionary locators to apply custom pronunciation rules. Specified as objects with pronunciation_dictionary_id and version_id. Applied in order, maximum 3 per request."),
    previous_request_ids: list[str] | None = Field(None, description="Request IDs from previously generated samples to maintain speech continuity. Improves flow when splitting large tasks across multiple requests. Maximum 3 IDs, best results with consistent model."),
    next_request_ids: list[str] | None = Field(None, description="Request IDs from samples that follow this generation. Maintains natural flow when regenerating a sample within a sequence. Maximum 3 IDs, best results with consistent model."),
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(None, description="Text normalization mode: 'auto' applies normalization automatically, 'on' always applies it, 'off' disables it. Normalization handles number spelling and similar conversions."),
    apply_language_text_normalization: bool | None = Field(None, description="Enable language-specific text normalization for proper pronunciation. Currently supported for Japanese only. Warning: significantly increases request latency."),
) -> dict[str, Any]:
    """Converts text into streaming audio using a specified voice. Returns audio as a continuous stream in your chosen format, ideal for real-time playback or large content."""

    # Construct request model with validation
    try:
        _request = _models.TextToSpeechStreamRequest(
            path=_models.TextToSpeechStreamRequestPath(voice_id=voice_id),
            query=_models.TextToSpeechStreamRequestQuery(output_format=output_format),
            body=_models.TextToSpeechStreamRequestBody(text=text, model_id=model_id, language_code=language_code, pronunciation_dictionary_locators=pronunciation_dictionary_locators, previous_request_ids=previous_request_ids, next_request_ids=next_request_ids, apply_text_normalization=apply_text_normalization, apply_language_text_normalization=apply_language_text_normalization,
                voice_settings=_models.TextToSpeechStreamRequestBodyVoiceSettings(stability=stability, similarity_boost=similarity_boost, style=style, speed=speed) if any(v is not None for v in [stability, similarity_boost, style, speed]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_speech_stream: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/text-to-speech/{voice_id}/stream", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/text-to-speech/{voice_id}/stream"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_speech_stream")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_speech_stream", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_speech_stream",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-speech
@mcp.tool()
async def generate_speech_stream_with_timestamps(
    voice_id: str = Field(..., description="The voice identifier to use for speech synthesis. Available voices can be retrieved from the voices endpoint."),
    text: str = Field(..., description="The text content to convert into speech audio."),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and PCM formats require higher subscription tiers."),
    model_id: str | None = Field(None, description="The model identifier for speech synthesis. The model must support text-to-speech conversion. Available models can be queried from the models endpoint."),
    language_code: str | None = Field(None, description="ISO 639-1 language code to enforce language-specific processing and text normalization. The model must support the specified language."),
    stability: float | None = Field(None, description="Voice stability control ranging from 0 (high emotional range) to 1 (monotonous). Lower values produce more expressive speech with greater variation.", ge=0.0, le=1.0),
    similarity_boost: float | None = Field(None, description="Voice similarity control ranging from 0 to 1, determining how closely the synthesis adheres to the original voice characteristics.", ge=0.0, le=1.0),
    style: float | None = Field(None, description="Style exaggeration level (0 to 1+) that amplifies the speaker's original style. Non-zero values increase computational cost and latency."),
    speed: float | None = Field(None, description="Speech speed multiplier where 1.0 is normal speed, values below 1.0 slow down speech, and values above 1.0 accelerate it."),
    pronunciation_dictionary_locators: list[_models.PronunciationDictionaryVersionLocatorRequestModel] | None = Field(None, description="Pronunciation dictionary locators to apply custom pronunciation rules. Accepts up to 3 locators applied in order, each containing a pronunciation_dictionary_id and version_id."),
    previous_request_ids: list[str] | None = Field(None, description="Request IDs from previously generated speech samples to maintain continuity. Accepts up to 3 IDs applied in order. Improves flow when splitting large tasks across multiple requests."),
    next_request_ids: list[str] | None = Field(None, description="Request IDs from subsequent speech samples to maintain continuity. Accepts up to 3 IDs applied in order. Useful when regenerating a sample while preserving natural flow with following content."),
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(None, description="Text normalization mode: 'auto' applies normalization when appropriate, 'on' always applies it, 'off' disables it. Normalization handles conversions like spelling out numbers."),
    apply_language_text_normalization: bool | None = Field(None, description="Enable language-specific text normalization for improved pronunciation in supported languages. Currently only supports Japanese. Warning: may significantly increase request latency."),
) -> dict[str, Any]:
    """Converts text to speech audio and returns a stream of JSON objects containing base64-encoded audio chunks with character-level timing information, enabling precise synchronization of audio with text."""

    # Construct request model with validation
    try:
        _request = _models.TextToSpeechStreamWithTimestampsRequest(
            path=_models.TextToSpeechStreamWithTimestampsRequestPath(voice_id=voice_id),
            query=_models.TextToSpeechStreamWithTimestampsRequestQuery(output_format=output_format),
            body=_models.TextToSpeechStreamWithTimestampsRequestBody(text=text, model_id=model_id, language_code=language_code, pronunciation_dictionary_locators=pronunciation_dictionary_locators, previous_request_ids=previous_request_ids, next_request_ids=next_request_ids, apply_text_normalization=apply_text_normalization, apply_language_text_normalization=apply_language_text_normalization,
                voice_settings=_models.TextToSpeechStreamWithTimestampsRequestBodyVoiceSettings(stability=stability, similarity_boost=similarity_boost, style=style, speed=speed) if any(v is not None for v in [stability, similarity_boost, style, speed]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_speech_stream_with_timestamps: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/text-to-speech/{voice_id}/stream/with-timestamps", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/text-to-speech/{voice_id}/stream/with-timestamps"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_speech_stream_with_timestamps")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_speech_stream_with_timestamps", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_speech_stream_with_timestamps",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-dialogue
@mcp.tool()
async def generate_dialogue(
    inputs: list[_models.DialogueInput] = Field(..., description="Array of dialogue segments, each containing text and a voice ID. Order is preserved in the output. Maximum of 10 unique voice IDs per request."),
    output_format: Literal["wav_8000", "wav_16000", "wav_22050", "wav_24000", "wav_32000", "wav_44100", "wav_48000"] | Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). MP3 192kbps requires Creator tier or above; PCM and WAV at 44.1kHz require Pro tier or above. μ-law format is commonly used for Twilio integrations."),
    model_id: str | None = Field(None, description="Model identifier for text-to-speech conversion. Query available models via GET /v1/models and verify can_do_text_to_speech capability."),
    language_code: str | None = Field(None, description="ISO 639-1 language code to enforce language for the model and text normalization. Returns an error if the model does not support the specified language."),
    stability: float | None = Field(None, description="Voice stability control between 0.0 and 1.0. Lower values increase emotional range and variation; higher values produce more monotonous, consistent speech.", ge=0.0, le=1.0),
    pronunciation_dictionary_locators: list[_models.PronunciationDictionaryVersionLocatorRequestModel] | None = Field(None, description="List of pronunciation dictionary locators to apply in order. Each locator contains a pronunciation_dictionary_id and version_id. Maximum of 3 locators per request."),
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(None, description="Text normalization mode: 'auto' applies normalization based on system decision, 'on' always applies it, 'off' disables it. Normalization handles cases like spelling out numbers."),
) -> dict[str, Any]:
    """Converts a list of text and voice ID pairs into multi-voice dialogue audio. Supports up to 10 unique voices per request with configurable audio format, model, stability, and text normalization settings."""

    # Construct request model with validation
    try:
        _request = _models.TextToDialogueRequest(
            query=_models.TextToDialogueRequestQuery(output_format=output_format),
            body=_models.TextToDialogueRequestBody(inputs=inputs, model_id=model_id, language_code=language_code, pronunciation_dictionary_locators=pronunciation_dictionary_locators, apply_text_normalization=apply_text_normalization,
                settings=_models.TextToDialogueRequestBodySettings(stability=stability) if any(v is not None for v in [stability]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_dialogue: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/text-to-dialogue"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_dialogue")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_dialogue", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_dialogue",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-dialogue
@mcp.tool()
async def generate_dialogue_stream(
    inputs: list[_models.DialogueInput] = Field(..., description="Array of dialogue turns, each containing text to speak and the voice ID to use. Order matters—items are processed sequentially to create the dialogue flow. Maximum of 10 unique voice IDs per request."),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Some formats require higher subscription tiers: MP3 192kbps requires Creator tier or above, PCM 44.1kHz requires Pro tier or above. μ-law format is commonly used for Twilio integrations."),
    model_id: str | None = Field(None, description="Model identifier for text-to-speech processing. The model must support text-to-speech capability. Query available models via GET /v1/models and check the can_do_text_to_speech property."),
    language_code: str | None = Field(None, description="ISO 639-1 language code to enforce language processing and text normalization. If the selected model doesn't support the specified language, an error will be returned."),
    stability: float | None = Field(None, description="Voice stability control between 0.0 and 1.0. Lower values increase emotional range and variability; higher values produce more consistent, monotonous speech.", ge=0.0, le=1.0),
    pronunciation_dictionary_locators: list[_models.PronunciationDictionaryVersionLocatorRequestModel] | None = Field(None, description="List of pronunciation dictionary locators to apply in order. Each locator contains a pronunciation_dictionary_id and version_id. Maximum of 3 locators per request."),
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(None, description="Text normalization mode: 'auto' applies normalization automatically based on content (e.g., spelling out numbers), 'on' always applies normalization, 'off' disables it entirely."),
) -> dict[str, Any]:
    """Converts a list of text and voice ID pairs into multi-voice dialogue speech and streams the audio. Useful for creating conversations, interviews, or multi-speaker content with different voices."""

    # Construct request model with validation
    try:
        _request = _models.TextToDialogueStreamRequest(
            query=_models.TextToDialogueStreamRequestQuery(output_format=output_format),
            body=_models.TextToDialogueStreamRequestBody(inputs=inputs, model_id=model_id, language_code=language_code, pronunciation_dictionary_locators=pronunciation_dictionary_locators, apply_text_normalization=apply_text_normalization,
                settings=_models.TextToDialogueStreamRequestBodySettings(stability=stability) if any(v is not None for v in [stability]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_dialogue_stream: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/text-to-dialogue/stream"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_dialogue_stream")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_dialogue_stream", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_dialogue_stream",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-dialogue
@mcp.tool()
async def generate_dialogue_stream_with_timestamps(
    inputs: list[_models.DialogueInput] = Field(..., description="Array of dialogue turn objects, each pairing text content with a voice ID. Processed in order to create sequential dialogue. Maximum of 10 unique voice IDs per request."),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio codec, sample rate, and bitrate configuration. Format is codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and PCM formats require elevated subscription tiers."),
    model_id: str | None = Field(None, description="The TTS model to use for synthesis. Query available models via GET /v1/models and verify can_do_text_to_speech capability."),
    language_code: str | None = Field(None, description="ISO 639-1 language code to enforce language processing and text normalization. The selected model must support the specified language."),
    stability: float | None = Field(None, description="Controls voice consistency and emotional variation. Lower values (closer to 0) produce greater emotional range and variability. Higher values (closer to 1) produce more consistent, monotonous delivery.", ge=0.0, le=1.0),
    pronunciation_dictionary_locators: list[_models.PronunciationDictionaryVersionLocatorRequestModel] | None = Field(None, description="Ordered list of pronunciation dictionary references to apply custom pronunciations. Applied sequentially in the order provided. Maximum of 3 locators per request."),
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(None, description="Controls text normalization behavior. 'auto' lets the system decide, 'on' always normalizes (e.g., converts numbers to words), 'off' disables normalization."),
) -> dict[str, Any]:
    """Converts text and voice ID pairs into streamed dialogue audio with precise timestamps. Returns a continuous stream of JSON objects containing base64-encoded audio chunks and their corresponding timing information."""

    # Construct request model with validation
    try:
        _request = _models.TextToDialogueStreamWithTimestampsRequest(
            query=_models.TextToDialogueStreamWithTimestampsRequestQuery(output_format=output_format),
            body=_models.TextToDialogueStreamWithTimestampsRequestBody(inputs=inputs, model_id=model_id, language_code=language_code, pronunciation_dictionary_locators=pronunciation_dictionary_locators, apply_text_normalization=apply_text_normalization,
                settings=_models.TextToDialogueStreamWithTimestampsRequestBodySettings(stability=stability) if any(v is not None for v in [stability]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_dialogue_stream_with_timestamps: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/text-to-dialogue/stream/with-timestamps"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_dialogue_stream_with_timestamps")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_dialogue_stream_with_timestamps", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_dialogue_stream_with_timestamps",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-dialogue
@mcp.tool()
async def generate_dialogue_with_timestamps(
    inputs: list[_models.DialogueInput] = Field(..., description="List of dialogue turns, each containing text to be spoken and the voice ID to use for that turn. Maximum of 10 unique voice IDs per request. Turns are processed in order."),
    output_format: Literal["wav_8000", "wav_16000", "wav_22050", "wav_24000", "wav_32000", "wav_44100", "wav_48000"] | Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio codec, sample rate, and bitrate format. Format is specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and certain formats require higher subscription tiers."),
    model_id: str | None = Field(None, description="The text-to-speech model to use for generation. Must support text-to-speech capability. Query available models via GET /v1/models to verify can_do_text_to_speech property."),
    language_code: str | None = Field(None, description="ISO 639-1 language code to enforce language for the model and text normalization. If the model does not support the specified language, an error will be returned."),
    stability: float | None = Field(None, description="Voice stability control affecting emotional range and consistency. Lower values produce broader emotional variation; higher values result in more monotonous, emotionally limited speech.", ge=0.0, le=1.0),
    pronunciation_dictionary_locators: list[_models.PronunciationDictionaryVersionLocatorRequestModel] | None = Field(None, description="Custom pronunciation dictionary rules to apply to the text in order. Each locator references a specific dictionary version. Maximum of 3 locators per request."),
    apply_text_normalization: Literal["auto", "on", "off"] | None = Field(None, description="Text normalization mode: 'auto' applies normalization based on system decision, 'on' always applies it, 'off' disables it. Normalization handles cases like spelling out numbers."),
) -> dict[str, Any]:
    """Generate dialogue from text with precise character-level timing information for audio-text synchronization. Each dialogue turn is converted to speech using specified voice IDs and returned with exact timestamp markers."""

    # Construct request model with validation
    try:
        _request = _models.TextToDialogueFullWithTimestampsRequest(
            query=_models.TextToDialogueFullWithTimestampsRequestQuery(output_format=output_format),
            body=_models.TextToDialogueFullWithTimestampsRequestBody(inputs=inputs, model_id=model_id, language_code=language_code, pronunciation_dictionary_locators=pronunciation_dictionary_locators, apply_text_normalization=apply_text_normalization,
                settings=_models.TextToDialogueFullWithTimestampsRequestBodySettings(stability=stability) if any(v is not None for v in [stability]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_dialogue_with_timestamps: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/text-to-dialogue/with-timestamps"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_dialogue_with_timestamps")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_dialogue_with_timestamps", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_dialogue_with_timestamps",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: speech-to-speech
@mcp.tool()
async def convert_voice(
    voice_id: str = Field(..., description="The target voice to apply to the audio. Use the voices endpoint to discover available voices and their characteristics."),
    audio: str = Field(..., description="The source audio file containing the content and emotional expression to transfer to the target voice."),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio encoding format specified as codec_sample_rate_bitrate (e.g., mp3_44100_128). Higher bitrates and PCM formats require higher subscription tiers."),
    model_id: str | None = Field(None, description="The speech-to-speech model to use for conversion. Query available models to verify speech conversion support via the can_do_voice_conversion property."),
    remove_background_noise: bool | None = Field(None, description="Enable background noise removal from the input audio using audio isolation. Only applicable when using the Voice Changer model."),
    stability: float | None = Field(None, description="Controls the stability of the voice. Higher values produce more consistent output. Range: 0.0 to 1.0"),
    similarity_boost: float | None = Field(None, description="Controls how closely the voice matches the original. Higher values increase similarity. Range: 0.0 to 1.0"),
    style: float | None = Field(None, description="Controls the style exaggeration of the voice. Range: 0.0 to 1.0"),
    use_speaker_boost: bool | None = Field(None, description="Whether to apply speaker boost for enhanced clarity and presence"),
) -> dict[str, Any]:
    """Transform audio from one voice to another while preserving the original emotion, timing, and delivery characteristics. The input audio's content and emotional qualities control the output speech generation."""

    # Call helper functions
    voice_settings = build_voice_settings(stability, similarity_boost, style, use_speaker_boost)

    # Construct request model with validation
    try:
        _request = _models.SpeechToSpeechFullRequest(
            path=_models.SpeechToSpeechFullRequestPath(voice_id=voice_id),
            query=_models.SpeechToSpeechFullRequestQuery(output_format=output_format),
            body=_models.SpeechToSpeechFullRequestBody(audio=audio, model_id=model_id, remove_background_noise=remove_background_noise, voice_settings=voice_settings)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_voice: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-speech/{voice_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-speech/{voice_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_voice")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_voice", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_voice",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: speech-to-speech
@mcp.tool()
async def convert_speech_to_speech_stream(
    voice_id: str = Field(..., description="The target voice identifier to apply to the input audio. Use the voices endpoint to discover available voices."),
    audio: str = Field(..., description="The source audio file containing the content and emotional characteristics that will control the generated speech output."),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio encoding format for the response, specified as codec_sample_rate_bitrate. Higher bitrates and sample rates may require elevated subscription tiers."),
    model_id: str | None = Field(None, description="The model identifier to use for voice conversion. Verify the model supports speech-to-speech conversion via the can_do_voice_conversion property."),
    remove_background_noise: bool | None = Field(None, description="Enable background noise removal from the input audio using audio isolation. Only applicable when using the Voice Changer model."),
    stability: float | None = Field(None, description="Controls the stability of the voice. Higher values produce more consistent output. Range: 0.0 to 1.0"),
    similarity_boost: float | None = Field(None, description="Controls how closely the voice matches the original. Higher values increase similarity. Range: 0.0 to 1.0"),
    style: float | None = Field(None, description="Controls the style exaggeration of the voice. Range: 0.0 to 1.0"),
    use_speaker_boost: bool | None = Field(None, description="Whether to apply speaker boost for enhanced clarity and presence"),
) -> dict[str, Any]:
    """Convert audio from one voice to another with streaming output, maintaining full control over emotion, timing, and delivery. The input audio's content and emotional characteristics drive the generated speech in the target voice."""

    # Call helper functions
    voice_settings = build_voice_settings(stability, similarity_boost, style, use_speaker_boost)

    # Construct request model with validation
    try:
        _request = _models.SpeechToSpeechStreamRequest(
            path=_models.SpeechToSpeechStreamRequestPath(voice_id=voice_id),
            query=_models.SpeechToSpeechStreamRequestQuery(output_format=output_format),
            body=_models.SpeechToSpeechStreamRequestBody(audio=audio, model_id=model_id, remove_background_noise=remove_background_noise, voice_settings=voice_settings)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_speech_to_speech_stream: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-speech/{voice_id}/stream", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-speech/{voice_id}/stream"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_speech_to_speech_stream")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_speech_to_speech_stream", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_speech_to_speech_stream",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-voice
@mcp.tool()
async def generate_voice_previews(
    voice_description: str = Field(..., description="Detailed description of the desired voice characteristics. The system uses this to generate voice previews matching your specifications.", min_length=20, max_length=1000),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio codec, sample rate, and bitrate for the generated preview samples. Higher bitrates and sample rates provide better quality but require higher subscription tiers."),
    loudness: float | None = Field(None, description="Volume level of the generated voice samples, ranging from quietest to loudest. A value of 0 corresponds to approximately -24 LUFS.", ge=-1.0, le=1.0),
    quality: float | None = Field(None, description="Voice quality level that balances output fidelity with variety. Higher values produce more consistent, polished voices with less variation across previews.", ge=-1.0, le=1.0),
    should_enhance: bool | None = Field(None, description="Automatically expand and refine the voice description using AI to add detail and improve generation quality. Useful for simple or brief descriptions."),
) -> dict[str, Any]:
    """Generate multiple voice preview samples based on a text description to help you select a custom voice. Each preview includes a unique voice ID and audio sample that can be used to create the final voice."""

    # Construct request model with validation
    try:
        _request = _models.TextToVoiceRequest(
            query=_models.TextToVoiceRequestQuery(output_format=output_format),
            body=_models.TextToVoiceRequestBody(voice_description=voice_description, loudness=loudness, quality=quality, should_enhance=should_enhance)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_voice_previews: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/text-to-voice/create-previews"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_voice_previews")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_voice_previews", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_voice_previews",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-voice
@mcp.tool()
async def create_voice(
    voice_name: str = Field(..., description="The name for the new voice being created."),
    voice_description: str = Field(..., description="A detailed description of the voice characteristics and use case. Must be between 20 and 1000 characters.", min_length=20, max_length=1000),
    generated_voice_id: str = Field(..., description="The ID of the generated voice preview to finalize. Obtain this from the response of POST /v1/text-to-voice/design or POST /v1/text-to-voice/:voice_id/remix operations."),
    labels: dict[str, str] | None = Field(None, description="Optional metadata tags to associate with the created voice for organization and filtering purposes."),
) -> dict[str, Any]:
    """Create a persistent voice from a previously generated voice preview. This endpoint finalizes a voice design by converting a generated_voice_id (obtained from design or remix operations) into a named voice asset."""

    # Construct request model with validation
    try:
        _request = _models.CreateVoiceRequest(
            body=_models.CreateVoiceRequestBody(voice_name=voice_name, voice_description=voice_description, generated_voice_id=generated_voice_id, labels=labels)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_voice: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/text-to-voice"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_voice")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_voice", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_voice",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-voice
@mcp.tool()
async def design_voice(
    voice_description: str = Field(..., description="Detailed description of the desired voice characteristics. Used to guide voice generation and should include personality, tone, and acoustic qualities.", min_length=20, max_length=1000),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio codec, sample rate, and bitrate for the generated voice samples. Higher bitrates and sample rates require appropriate subscription tiers."),
    model_id: Literal["eleven_multilingual_ttv_v2", "eleven_ttv_v3"] | None = Field(None, description="AI model version to use for voice generation. Different models may produce varying quality and multilingual support."),
    loudness: float | None = Field(None, description="Volume level adjustment for the generated voice, where -1 is quietest and 1 is loudest. A value of 0 corresponds to approximately -24 LUFS.", ge=-1.0, le=1.0),
    stream_previews: bool | None = Field(None, description="When enabled, voice previews are streamed separately via the stream endpoint instead of being included in the response. Useful for reducing response payload size."),
    should_enhance: bool | None = Field(None, description="Automatically enhance the voice description with AI-generated details to improve voice generation quality and variety. Expands simple prompts into more comprehensive descriptions."),
    quality: float | None = Field(None, description="Quality level for voice generation, where higher values produce better output but with less variation across previews.", ge=-1.0, le=1.0),
) -> dict[str, Any]:
    """Generate voice design previews based on a detailed description. Returns multiple voice options with audio samples that can be used to create a custom voice."""

    # Construct request model with validation
    try:
        _request = _models.TextToVoiceDesignRequest(
            query=_models.TextToVoiceDesignRequestQuery(output_format=output_format),
            body=_models.TextToVoiceDesignRequestBody(voice_description=voice_description, model_id=model_id, loudness=loudness, stream_previews=stream_previews, should_enhance=should_enhance, quality=quality)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for design_voice: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/text-to-voice/design"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("design_voice")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("design_voice", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="design_voice",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-voice
@mcp.tool()
async def remix_voice(
    voice_id: str = Field(..., description="The ID of the voice to remix. Use the voices list endpoint to discover available voices."),
    voice_description: str = Field(..., description="Detailed description of the voice modifications to apply. Be specific about desired characteristics such as pitch, tone, pace, or emotional qualities.", min_length=5, max_length=1000),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio output format specified as codec_sample_rate_bitrate. MP3 at 192kbps requires Creator tier or higher. PCM at 44.1kHz requires Pro tier or higher. μ-law format is compatible with Twilio."),
    loudness: float | None = Field(None, description="Volume level of the generated voice, ranging from -1 (quietest) to 1 (loudest), with 0 corresponding to approximately -24 LUFS.", ge=-1.0, le=1.0),
    stream_previews: bool | None = Field(None, description="When true, returns only generated voice IDs without audio previews in the response. Audio can then be streamed separately via the stream endpoint."),
) -> dict[str, Any]:
    """Generate voice previews by remixing an existing voice based on a descriptive prompt. Returns multiple voice preview options with generated voice IDs that can be used to create new voices."""

    # Construct request model with validation
    try:
        _request = _models.TextToVoiceRemixRequest(
            path=_models.TextToVoiceRemixRequestPath(voice_id=voice_id),
            query=_models.TextToVoiceRemixRequestQuery(output_format=output_format),
            body=_models.TextToVoiceRemixRequestBody(voice_description=voice_description, loudness=loudness, stream_previews=stream_previews)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remix_voice: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/text-to-voice/{voice_id}/remix", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/text-to-voice/{voice_id}/remix"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remix_voice")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remix_voice", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remix_voice",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: text-to-voice
@mcp.tool()
async def stream_voice_preview(generated_voice_id: str = Field(..., description="The unique identifier of the generated voice preview to stream.")) -> dict[str, Any]:
    """Stream audio data for a voice preview that was previously generated using the voice design endpoint. This operation returns the audio content as a continuous stream."""

    # Construct request model with validation
    try:
        _request = _models.TextToVoicePreviewStreamRequest(
            path=_models.TextToVoicePreviewStreamRequestPath(generated_voice_id=generated_voice_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for stream_voice_preview: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/text-to-voice/{generated_voice_id}/stream", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/text-to-voice/{generated_voice_id}/stream"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("stream_voice_preview")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("stream_voice_preview", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="stream_voice_preview",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def get_subscription_info() -> dict[str, Any]:
    """Retrieves detailed information about the user's current subscription, including plan details, billing status, and entitlements."""

    # Extract parameters for API call
    _http_path = "/v1/user/subscription"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_subscription_info")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_subscription_info", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_subscription_info",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def get_user() -> dict[str, Any]:
    """Retrieves the authenticated user's profile information and account details."""

    # Extract parameters for API call
    _http_path = "/v1/user"
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

# Tags: voices
@mcp.tool()
async def list_voices(
    next_page_token: str | None = Field(None, description="Token for retrieving the next page of results. Use this with the has_more flag from the previous response to implement reliable pagination."),
    page_size: int | None = Field(None, description="Maximum number of voices to return per page. Must not exceed 100. Note that page 0 may include additional default voices."),
    sort: str | None = Field(None, description="Field to sort results by. Use 'created_at_unix' for chronological ordering or 'name' for alphabetical ordering. Note that 'created_at_unix' may not be available for older voices."),
    sort_direction: str | None = Field(None, description="Direction to sort results in. Use 'asc' for ascending or 'desc' for descending order."),
    voice_type: str | None = Field(None, description="Filter voices by type. 'non-default' includes all voices except default voices. 'saved' includes non-default voices plus any default voices added to collections."),
    category: str | None = Field(None, description="Filter voices by their creation category or source."),
    fine_tuning_state: str | None = Field(None, description="Filter professional voice clones by their fine-tuning state. Only applicable to professional voices."),
    collection_id: str | None = Field(None, description="Filter voices to only those belonging to a specific collection by its ID."),
    include_total_count: bool | None = Field(None, description="Include the total count of matching voices in the response. Note that this count is a live snapshot and may change between requests. Use the has_more flag for pagination instead. Only enable when you need the total count for display purposes, as it incurs a performance cost."),
    voice_ids: list[str] | None = Field(None, description="Retrieve specific voices by their IDs. Accepts up to 100 voice IDs in a single request."),
) -> dict[str, Any]:
    """Retrieve a paginated list of available voices with advanced filtering, sorting, and search capabilities. Supports filtering by voice type, category, fine-tuning state, and collection membership."""

    # Construct request model with validation
    try:
        _request = _models.GetUserVoicesV2Request(
            query=_models.GetUserVoicesV2RequestQuery(next_page_token=next_page_token, page_size=page_size, sort=sort, sort_direction=sort_direction, voice_type=voice_type, category=category, fine_tuning_state=fine_tuning_state, collection_id=collection_id, include_total_count=include_total_count, voice_ids=voice_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_voices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v2/voices"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_voices")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_voices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_voices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: voices
@mcp.tool()
async def get_default_voice_settings() -> dict[str, Any]:
    """Retrieve the default voice settings for all voices, including similarity boost (Clarity + Similarity Enhancement) and stability parameters that control voice characteristics."""

    # Extract parameters for API call
    _http_path = "/v1/voices/settings/default"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_default_voice_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_default_voice_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_default_voice_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: voices
@mcp.tool()
async def get_voice_settings(voice_id: str = Field(..., description="The unique identifier of the voice whose settings you want to retrieve. Use the list voices endpoint to discover available voice IDs.")) -> dict[str, Any]:
    """Retrieve the configuration settings for a specific voice, including similarity boost (Clarity + Similarity Enhancement) and stability parameters that control voice quality characteristics."""

    # Construct request model with validation
    try:
        _request = _models.GetVoiceSettingsRequest(
            path=_models.GetVoiceSettingsRequestPath(voice_id=voice_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_voice_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/{voice_id}/settings", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/{voice_id}/settings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_voice_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_voice_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_voice_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: voices
@mcp.tool()
async def get_voice(voice_id: str = Field(..., description="The unique identifier of the voice to retrieve. You can list all available voices to discover valid IDs.")) -> dict[str, Any]:
    """Retrieve detailed metadata for a specific voice, including its properties and configuration. Use this to get information about a voice before using it for text-to-speech synthesis."""

    # Construct request model with validation
    try:
        _request = _models.GetVoiceByIdRequest(
            path=_models.GetVoiceByIdRequestPath(voice_id=voice_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_voice: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/{voice_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/{voice_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_voice")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_voice", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_voice",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: voices
@mcp.tool()
async def delete_voice(voice_id: str = Field(..., description="The unique identifier of the voice to delete. You can retrieve available voice IDs from the list voices endpoint.")) -> dict[str, Any]:
    """Permanently deletes a voice by its ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteVoiceRequest(
            path=_models.DeleteVoiceRequestPath(voice_id=voice_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_voice: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/{voice_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/{voice_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_voice")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_voice", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_voice",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: voices
@mcp.tool()
async def configure_voice_settings(
    voice_id: str = Field(..., description="The unique identifier of the voice to configure. Use the list voices endpoint to discover available voice IDs."),
    stability: float | None = Field(None, description="Controls voice consistency and emotional range. Lower values (closer to 0) produce more varied emotional expression, while higher values (closer to 1) result in more consistent but potentially monotonous output.", ge=0.0, le=1.0),
    similarity_boost: float | None = Field(None, description="Controls how closely the generated voice matches the original voice characteristics. Higher values enforce stricter adherence to the original voice, while lower values allow more deviation.", ge=0.0, le=1.0),
    style: float | None = Field(None, description="Amplifies the stylistic characteristics of the original speaker. Non-zero values increase computational resource usage and may increase latency."),
    speed: float | None = Field(None, description="Adjusts speech playback speed relative to normal rate. Use 1.0 for default speed, values below 1.0 to slow down, and values above 1.0 to speed up."),
) -> dict[str, Any]:
    """Configure voice parameters for a specific voice, including stability, similarity, style, and speed adjustments. These settings control how the voice is generated and how closely it adheres to the original voice characteristics."""

    # Construct request model with validation
    try:
        _request = _models.EditVoiceSettingsRequest(
            path=_models.EditVoiceSettingsRequestPath(voice_id=voice_id),
            body=_models.EditVoiceSettingsRequestBody(stability=stability, similarity_boost=similarity_boost, style=style, speed=speed)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for configure_voice_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/{voice_id}/settings/edit", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/{voice_id}/settings/edit"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("configure_voice_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("configure_voice_settings", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="configure_voice_settings",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: voices
@mcp.tool()
async def create_voice_sample(
    name: str = Field(..., description="The display name for this voice, shown in selection dropdowns and voice management interfaces."),
    files: list[str] = Field(..., description="Audio file paths for voice cloning samples. Provide multiple recordings to improve voice quality and consistency. Order does not affect processing."),
    remove_background_noise: bool | None = Field(None, description="Enable background noise removal using audio isolation processing. Only use if your samples contain background noise, as it may degrade quality for clean recordings."),
    description: str | None = Field(None, description="Optional metadata describing the voice characteristics, tone, and intended use cases."),
    labels: dict[str, str] | str | None = Field(None, description="Categorical metadata for voice classification. Supports language code, accent variant, gender, and age range to help organize and filter voices."),
) -> dict[str, Any]:
    """Create a new voice in VoiceLab by uploading audio samples for voice cloning. The voice will be added to your collection and available for use in voice synthesis."""

    # Construct request model with validation
    try:
        _request = _models.AddVoiceRequest(
            body=_models.AddVoiceRequestBody(name=name, files=files, remove_background_noise=remove_background_noise, description=description, labels=labels)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_voice_sample: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/voices/add"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_voice_sample")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_voice_sample", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_voice_sample",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: voices
@mcp.tool()
async def update_voice(
    voice_id: str = Field(..., description="The unique identifier of the voice to update."),
    name: str = Field(..., description="The display name for this voice, shown in voice selection dropdowns."),
    files: list[str] | None = Field(None, description="Audio files to add to the voice. Supported formats include MP3, WAV, and other common audio formats."),
    remove_background_noise: bool | None = Field(None, description="Enable automatic background noise removal from audio samples using audio isolation. Only use if samples contain background noise, as it may degrade quality otherwise."),
    description: str | None = Field(None, description="A brief description of the voice characteristics, tone, and intended use cases."),
    labels: dict[str, str] | str | None = Field(None, description="Metadata labels describing the voice. Supported keys include language (ISO 639-1 code), accent (BCP 47 tag), gender, and age."),
) -> dict[str, Any]:
    """Update the name, description, labels, and audio samples of a voice you created. Optionally apply background noise removal to improve audio quality."""

    # Construct request model with validation
    try:
        _request = _models.EditVoiceRequest(
            path=_models.EditVoiceRequestPath(voice_id=voice_id),
            body=_models.EditVoiceRequestBody(name=name, files=files, remove_background_noise=remove_background_noise, description=description, labels=labels)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_voice: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/{voice_id}/edit", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/{voice_id}/edit"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_voice")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_voice", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_voice",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: voices
@mcp.tool()
async def add_shared_voice(
    public_user_id: str = Field(..., description="The public user ID of the ElevenLabs user who owns the shared voice."),
    voice_id: str = Field(..., description="The unique identifier of the voice to add to your collection."),
    new_name: str = Field(..., description="The display name for this voice in your voice collection. This name will appear in your voice selection dropdown."),
    bookmarked: bool | None = Field(None, description="Whether to bookmark this voice for quick access in your collection."),
) -> dict[str, Any]:
    """Add a shared voice from another user to your personal voice collection. The voice will be displayed in your voice dropdown with a custom name you assign."""

    # Construct request model with validation
    try:
        _request = _models.AddSharingVoiceRequest(
            path=_models.AddSharingVoiceRequestPath(public_user_id=public_user_id, voice_id=voice_id),
            body=_models.AddSharingVoiceRequestBody(new_name=new_name, bookmarked=bookmarked)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_shared_voice: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/add/{public_user_id}/{voice_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/add/{public_user_id}/{voice_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_shared_voice")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_shared_voice", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_shared_voice",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def generate_podcast(
    model_id: str = Field(..., description="The voice model to use for audio generation. Query GET /v1/models to see all available models."),
    mode: _models.PodcastConversationMode | _models.PodcastBulletinMode = Field(..., description="The podcast format type. 'conversation' generates dialogue between two voices (host and guest), while 'bulletin' generates a single-voice monologue."),
    source: _models.PodcastTextSource | _models.PodcastUrlSource | list[_models.PodcastTextSource | _models.PodcastUrlSource] = Field(..., description="The content source for podcast generation. Can be a URL, text content, or other supported source formats."),
    quality_preset: Literal["standard", "high", "highest", "ultra", "ultra_lossless"] | None = Field(None, description="Audio output quality level. Higher quality settings provide better audio fidelity with improved processing."),
    duration_scale: Literal["short", "default", "long"] | None = Field(None, description="Target podcast length. Controls the amount of content included in the generated podcast."),
    language: str | None = Field(None, description="Two-letter ISO 639-1 language code for the podcast content and voice generation.", min_length=2, max_length=2),
    intro: str | None = Field(None, description="Optional opening text to prepend to the podcast. Useful for branding or context-setting.", max_length=1500),
    outro: str | None = Field(None, description="Optional closing text to append to the podcast. Useful for calls-to-action or sign-offs.", max_length=1500),
    instructions_prompt: str | None = Field(None, description="Custom instructions to guide the podcast generation style, tone, and content treatment. Use this to enforce accuracy, adjust formality, or specify audience appropriateness.", max_length=3000),
    highlights: list[str] | None = Field(None, description="Key themes or highlights summarizing the podcast content. Each highlight should be a brief phrase between 10-70 characters."),
    callback_url: str | None = Field(None, description="Webhook URL for conversion status notifications. The service will POST status updates when the project and chapters complete processing, including success/error details."),
    apply_text_normalization: Literal["auto", "on", "off", "apply_english"] | None = Field(None, description="Controls text normalization behavior. 'auto' lets the system decide, 'on' always normalizes, 'apply_english' normalizes assuming English text, and 'off' disables normalization."),
) -> dict[str, Any]:
    """Generate a podcast by converting source content into audio using AI-powered text-to-speech. Supports both conversational (two-voice dialogue) and bulletin (monologue) formats with customizable quality, duration, language, and styling options."""

    # Construct request model with validation
    try:
        _request = _models.CreatePodcastRequest(
            body=_models.CreatePodcastRequestBody(model_id=model_id, mode=mode, source=source, quality_preset=quality_preset, duration_scale=duration_scale, language=language, intro=intro, outro=outro, instructions_prompt=instructions_prompt, highlights=highlights, callback_url=callback_url, apply_text_normalization=apply_text_normalization)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_podcast: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/studio/podcasts"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_podcast")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_podcast", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_podcast",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def apply_pronunciation_dictionaries(
    project_id: str = Field(..., description="The unique identifier of the Studio project to which pronunciation dictionaries will be applied."),
    pronunciation_dictionary_locators: list[_models.PronunciationDictionaryVersionLocatorDbModel] = Field(..., description="An ordered list of pronunciation dictionary references to apply to the project. Each reference must include the dictionary ID and its version ID. Multiple dictionaries can be specified as separate form entries."),
    invalidate_affected_text: bool | None = Field(None, description="Whether to automatically mark text in the project for reconversion when dictionaries are applied or removed."),
) -> dict[str, Any]:
    """Apply pronunciation dictionaries to a Studio project. The operation automatically marks affected text for reconversion when dictionaries are added or removed."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePronunciationDictionariesRequest(
            path=_models.UpdatePronunciationDictionariesRequestPath(project_id=project_id),
            body=_models.UpdatePronunciationDictionariesRequestBody(pronunciation_dictionary_locators=pronunciation_dictionary_locators, invalidate_affected_text=invalidate_affected_text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for apply_pronunciation_dictionaries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/pronunciation-dictionaries", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/pronunciation-dictionaries"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("apply_pronunciation_dictionaries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("apply_pronunciation_dictionaries", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="apply_pronunciation_dictionaries",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def list_projects() -> dict[str, Any]:
    """Retrieve a list of all Studio projects with their metadata. Use this to discover available projects and their details."""

    # Extract parameters for API call
    _http_path = "/v1/studio/projects"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_projects")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_projects", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_projects",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def create_studio_project(
    name: str = Field(..., description="The name of the Studio project used for identification and display purposes."),
    default_title_voice_id: str | None = Field(None, description="The voice ID to use as the default voice for new titles in this project."),
    default_paragraph_voice_id: str | None = Field(None, description="The voice ID to use as the default voice for new paragraphs in this project."),
    default_model_id: str | None = Field(None, description="The model ID to use for audio generation in this project. Query GET /v1/models to list available models."),
    quality_preset: Literal["standard", "high", "ultra", "ultra_lossless"] | None = Field(None, description="The output quality level for generated audio, ranging from standard (128kbps) to ultra lossless (705.6kbps, fully lossless)."),
    author: str | None = Field(None, description="The author name to include as metadata in downloaded audio files."),
    description: str | None = Field(None, description="A description of the Studio project's content and purpose."),
    genres: list[str] | None = Field(None, description="A list of genres associated with this project for categorization and discovery."),
    target_audience: Literal["children", "young adult", "adult", "all ages"] | None = Field(None, description="The intended audience demographic for this project's content."),
    language: str | None = Field(None, description="The primary language of the project content as a two-letter ISO 639-1 language code.", min_length=2, max_length=2),
    content_type: str | None = Field(None, description="The type of content in this project (e.g., Book, Article, Screenplay)."),
    original_publication_date: str | None = Field(None, description="The original publication date of the content in YYYY-MM-DD or YYYY format.", pattern="^\\d{4}-\\d{2}-\\d{2}$|^\\d{4}$"),
    mature_content: bool | None = Field(None, description="Whether this project contains mature content that may not be suitable for all audiences."),
    isbn_number: str | None = Field(None, description="The ISBN number of the project to include as metadata in downloaded audio files."),
    volume_normalization: bool | None = Field(None, description="Whether to apply postprocessing to normalize audio volume to audiobook standards when downloading the project."),
    callback_url: str | None = Field(None, description="A webhook URL that receives conversion status notifications for the project and its chapters. Notifications include success/error status with project and chapter IDs."),
    fiction: Literal["fiction", "non-fiction"] | None = Field(None, description="Whether the content is fiction or non-fiction."),
    apply_text_normalization: Literal["auto", "on", "off", "apply_english"] | None = Field(None, description="Controls text normalization behavior: 'auto' decides automatically, 'on' always applies, 'apply_english' applies with English assumption, 'off' disables normalization."),
    auto_convert: bool | None = Field(None, description="Whether to automatically convert the project to audio immediately upon creation."),
    auto_assign_voices: bool | None = Field(None, description="Whether to automatically assign voices to phrases during project creation. This is an alpha feature."),
    source_type: Literal["blank", "book", "article", "genfm", "video", "screenplay"] | None = Field(None, description="The initialization type for the project: blank (empty), book (from document), article, genfm, video, or screenplay."),
    create_publishing_read: bool | None = Field(None, description="Whether to create a corresponding read for direct publishing in draft state alongside the project."),
    content_chapters: list[dict[str, Any]] | None = Field(None, description="List of chapter objects, each with 'name' (string) and 'blocks' (list of block objects)"),
    content_blocks: list[dict[str, Any]] | None = Field(None, description="List of block objects, each with 'sub_type' (e.g., 'p', 'h1', 'h2') and 'nodes' (list of node objects)"),
    content_nodes: list[dict[str, Any]] | None = Field(None, description="List of TTS node objects, each with 'type' ('tts_node'), 'text' (string), and 'voice_id' (string)"),
    pronunciation_dict_ids: list[str] | None = Field(None, description="List of pronunciation_dictionary_id values"),
    pronunciation_dict_versions: list[str] | None = Field(None, description="List of version_id values corresponding to each pronunciation_dictionary_id (must be same length as pronunciation_dict_ids)"),
    stability: float | None = Field(None, description="Controls the stability of the voice. Higher values produce more consistent output. Range: 0.0 to 1.0"),
    similarity_boost: float | None = Field(None, description="Controls how closely the voice matches the original. Higher values increase similarity. Range: 0.0 to 1.0"),
    style: float | None = Field(None, description="Controls the style exaggeration of the voice. Range: 0.0 to 1.0"),
    use_speaker_boost: bool | None = Field(None, description="Whether to apply speaker boost for enhanced clarity and presence"),
) -> dict[str, Any]:
    """Creates a new Studio project for audio content generation. Projects can be initialized as blank, from a document, or from a URL, with customizable voices, audio quality, and metadata."""

    # Call helper functions
    from_content_json = build_content_json(content_chapters, content_blocks, content_nodes)
    pronunciation_dictionary_locators = build_pronunciation_dictionary_locators(pronunciation_dict_ids, pronunciation_dict_versions)
    voice_settings = build_voice_settings(stability, similarity_boost, style, use_speaker_boost)

    # Construct request model with validation
    try:
        _request = _models.AddProjectRequest(
            body=_models.AddProjectRequestBody(name=name, default_title_voice_id=default_title_voice_id, default_paragraph_voice_id=default_paragraph_voice_id, default_model_id=default_model_id, quality_preset=quality_preset, author=author, description=description, genres=genres, target_audience=target_audience, language=language, content_type=content_type, original_publication_date=original_publication_date, mature_content=mature_content, isbn_number=isbn_number, volume_normalization=volume_normalization, callback_url=callback_url, fiction=fiction, apply_text_normalization=apply_text_normalization, auto_convert=auto_convert, auto_assign_voices=auto_assign_voices, source_type=source_type, create_publishing_read=create_publishing_read, from_content_json=from_content_json, pronunciation_dictionary_locators=pronunciation_dictionary_locators, voice_settings=voice_settings)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_studio_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/studio/projects"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_studio_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_studio_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_studio_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def get_project(
    project_id: str = Field(..., description="The unique identifier of the Studio project to retrieve."),
    share_id: str | None = Field(None, description="Optional share identifier to access a shared version of the project."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific Studio project. Returns comprehensive project metadata including configuration, settings, and other project-specific details."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectByIdRequest(
            path=_models.GetProjectByIdRequestPath(project_id=project_id),
            query=_models.GetProjectByIdRequestQuery(share_id=share_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def update_studio_project(
    project_id: str = Field(..., description="The unique identifier of the Studio project to update."),
    name: str = Field(..., description="The display name of the Studio project used for identification and organization."),
    default_title_voice_id: str = Field(..., description="The voice ID to use as the default voice for newly created title sections."),
    default_paragraph_voice_id: str = Field(..., description="The voice ID to use as the default voice for newly created paragraph sections."),
    author: str | None = Field(None, description="Optional author name that will be embedded as metadata in exported MP3 files when the project or chapters are downloaded."),
    isbn_number: str | None = Field(None, description="Optional ISBN number that will be embedded as metadata in exported MP3 files when the project or chapters are downloaded."),
    volume_normalization: bool | None = Field(None, description="When enabled, applies audio postprocessing to downloaded files to ensure compliance with audiobook volume normalization standards."),
) -> dict[str, Any]:
    """Updates a Studio project with new metadata, voice settings, and audio processing preferences. Changes apply to the project configuration and affect how new content is generated and exported."""

    # Construct request model with validation
    try:
        _request = _models.EditProjectRequest(
            path=_models.EditProjectRequestPath(project_id=project_id),
            body=_models.EditProjectRequestBody(name=name, default_title_voice_id=default_title_voice_id, default_paragraph_voice_id=default_paragraph_voice_id, author=author, isbn_number=isbn_number, volume_normalization=volume_normalization)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_studio_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_studio_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_studio_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_studio_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def delete_project(project_id: str = Field(..., description="The unique identifier of the Studio project to delete.")) -> dict[str, Any]:
    """Permanently deletes a Studio project and all associated data. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteProjectRequest(
            path=_models.DeleteProjectRequestPath(project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}"
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

# Tags: studio
@mcp.tool()
async def update_project_content(
    project_id: str = Field(..., description="The unique identifier of the Studio project to update."),
    auto_convert: bool | None = Field(None, description="Whether to automatically convert the Studio project to audio format. Defaults to false if not specified."),
    content_chapters: list[dict[str, Any]] | None = Field(None, description="List of chapter objects, each with 'name' (string) and 'blocks' (list of block objects)"),
    content_blocks: list[dict[str, Any]] | None = Field(None, description="List of block objects, each with 'sub_type' (e.g., 'p', 'h1', 'h2') and 'nodes' (list of node objects)"),
    content_nodes: list[dict[str, Any]] | None = Field(None, description="List of TTS node objects, each with 'type' ('tts_node'), 'text' (string), and 'voice_id' (string)"),
) -> dict[str, Any]:
    """Updates the content of a Studio project. Optionally converts the project to audio format during the update."""

    # Call helper functions
    from_content_json = build_content_json(content_chapters, content_blocks, content_nodes)

    # Construct request model with validation
    try:
        _request = _models.EditProjectContentRequest(
            path=_models.EditProjectContentRequestPath(project_id=project_id),
            body=_models.EditProjectContentRequestBody(auto_convert=auto_convert, from_content_json=from_content_json)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_project_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/content", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/content"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_project_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_project_content", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_project_content",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def convert_studio_project(project_id: str = Field(..., description="The unique identifier of the Studio project to convert.")) -> dict[str, Any]:
    """Initiates conversion of a Studio project and all of its associated chapters. This operation processes the entire project structure for conversion."""

    # Construct request model with validation
    try:
        _request = _models.ConvertProjectEndpointRequest(
            path=_models.ConvertProjectEndpointRequestPath(project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_studio_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/convert", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/convert"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_studio_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_studio_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_studio_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def list_snapshots(project_id: str = Field(..., description="The unique identifier of the Studio project for which to retrieve snapshots.")) -> dict[str, Any]:
    """Retrieves a list of all snapshots for a specified Studio project. Snapshots capture the state of a project at a point in time."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectSnapshotsRequest(
            path=_models.GetProjectSnapshotsRequestPath(project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_snapshots: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/snapshots", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/snapshots"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def get_snapshot(
    project_id: str = Field(..., description="The unique identifier of the Studio project containing the snapshot."),
    project_snapshot_id: str = Field(..., description="The unique identifier of the project snapshot to retrieve."),
) -> dict[str, Any]:
    """Retrieves a specific project snapshot by its ID. Use this to access saved project state and configuration data."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectSnapshotEndpointRequest(
            path=_models.GetProjectSnapshotEndpointRequestPath(project_id=project_id, project_snapshot_id=project_snapshot_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/snapshots/{project_snapshot_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/snapshots/{project_snapshot_id}"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def stream_project_snapshot_audio(
    project_id: str = Field(..., description="The unique identifier of the Studio project containing the snapshot."),
    project_snapshot_id: str = Field(..., description="The unique identifier of the project snapshot whose audio should be streamed."),
    convert_to_mpeg: bool | None = Field(None, description="Whether to convert the streamed audio to MPEG format. Defaults to false, streaming in the original format."),
) -> dict[str, Any]:
    """Stream audio from a Studio project snapshot. Optionally convert the audio to MPEG format during streaming."""

    # Construct request model with validation
    try:
        _request = _models.StreamProjectSnapshotAudioEndpointRequest(
            path=_models.StreamProjectSnapshotAudioEndpointRequestPath(project_id=project_id, project_snapshot_id=project_snapshot_id),
            body=_models.StreamProjectSnapshotAudioEndpointRequestBody(convert_to_mpeg=convert_to_mpeg)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for stream_project_snapshot_audio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/snapshots/{project_snapshot_id}/stream", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/snapshots/{project_snapshot_id}/stream"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("stream_project_snapshot_audio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("stream_project_snapshot_audio", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="stream_project_snapshot_audio",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def download_snapshot_archive(
    project_id: str = Field(..., description="The unique identifier of the Studio project containing the snapshot to archive."),
    project_snapshot_id: str = Field(..., description="The unique identifier of the project snapshot to archive and download."),
) -> dict[str, Any]:
    """Downloads a compressed archive containing all audio files from a specific Studio project snapshot. Returns the archive as a binary stream ready for download."""

    # Construct request model with validation
    try:
        _request = _models.StreamProjectSnapshotArchiveEndpointRequest(
            path=_models.StreamProjectSnapshotArchiveEndpointRequestPath(project_id=project_id, project_snapshot_id=project_snapshot_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_snapshot_archive: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/snapshots/{project_snapshot_id}/archive", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/snapshots/{project_snapshot_id}/archive"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_snapshot_archive")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_snapshot_archive", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_snapshot_archive",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def list_chapters(project_id: str = Field(..., description="The unique identifier of the Studio project whose chapters you want to retrieve.")) -> dict[str, Any]:
    """Retrieves all chapters for a specified Studio project. Returns a list of chapters with their metadata and properties."""

    # Construct request model with validation
    try:
        _request = _models.GetChaptersRequest(
            path=_models.GetChaptersRequestPath(project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_chapters: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/chapters", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/chapters"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_chapters")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_chapters", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_chapters",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def create_chapter(
    project_id: str = Field(..., description="The unique identifier of the Studio project where the chapter will be created."),
    name: str = Field(..., description="The display name for the chapter used for identification and organization within the project."),
) -> dict[str, Any]:
    """Creates a new chapter in a Studio project, either as a blank chapter or populated from a URL source."""

    # Construct request model with validation
    try:
        _request = _models.AddChapterRequest(
            path=_models.AddChapterRequestPath(project_id=project_id),
            body=_models.AddChapterRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_chapter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/chapters", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/chapters"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_chapter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_chapter", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_chapter",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def get_chapter(
    project_id: str = Field(..., description="The unique identifier of the Studio project containing the chapter."),
    chapter_id: str = Field(..., description="The unique identifier of the chapter to retrieve."),
) -> dict[str, Any]:
    """Retrieves detailed information about a specific chapter within a Studio project."""

    # Construct request model with validation
    try:
        _request = _models.GetChapterByIdEndpointRequest(
            path=_models.GetChapterByIdEndpointRequestPath(project_id=project_id, chapter_id=chapter_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_chapter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/chapters/{chapter_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/chapters/{chapter_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_chapter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_chapter", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_chapter",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def update_chapter(
    project_id: str = Field(..., description="The unique identifier of the Studio project containing the chapter."),
    chapter_id: str = Field(..., description="The unique identifier of the chapter to update."),
    blocks: list[_models.ChapterContentBlockInputModel] = Field(..., description="An ordered array of content blocks that comprise the chapter. Each block defines a section of content within the chapter."),
    name: str | None = Field(None, description="The display name of the chapter for identification purposes."),
) -> dict[str, Any]:
    """Updates an existing chapter in a Studio project, including its name and content blocks."""

    # Construct request model with validation
    try:
        _request = _models.EditChapterRequest(
            path=_models.EditChapterRequestPath(project_id=project_id, chapter_id=chapter_id),
            body=_models.EditChapterRequestBody(name=name,
                content=_models.EditChapterRequestBodyContent(blocks=blocks))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_chapter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/chapters/{chapter_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/chapters/{chapter_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_chapter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_chapter", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_chapter",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def delete_chapter(
    project_id: str = Field(..., description="The unique identifier of the Studio project containing the chapter to delete."),
    chapter_id: str = Field(..., description="The unique identifier of the chapter to delete."),
) -> dict[str, Any]:
    """Permanently deletes a chapter from a Studio project. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteChapterEndpointRequest(
            path=_models.DeleteChapterEndpointRequestPath(project_id=project_id, chapter_id=chapter_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_chapter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/chapters/{chapter_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/chapters/{chapter_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_chapter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_chapter", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_chapter",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def convert_chapter(
    project_id: str = Field(..., description="The unique identifier of the Studio project containing the chapter to convert."),
    chapter_id: str = Field(..., description="The unique identifier of the chapter to be converted."),
) -> dict[str, Any]:
    """Initiates the conversion process for a specific chapter within a Studio project. This asynchronous operation transforms the chapter content into the desired output format."""

    # Construct request model with validation
    try:
        _request = _models.ConvertChapterEndpointRequest(
            path=_models.ConvertChapterEndpointRequestPath(project_id=project_id, chapter_id=chapter_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for convert_chapter: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/chapters/{chapter_id}/convert", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/chapters/{chapter_id}/convert"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("convert_chapter")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("convert_chapter", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="convert_chapter",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def list_chapter_snapshots(
    project_id: str = Field(..., description="The unique identifier of the Studio project containing the chapter."),
    chapter_id: str = Field(..., description="The unique identifier of the chapter for which to retrieve snapshots."),
) -> dict[str, Any]:
    """Retrieves all snapshots for a chapter, which are audio versions automatically created whenever the chapter is converted. Each snapshot can be downloaded as audio."""

    # Construct request model with validation
    try:
        _request = _models.GetChapterSnapshotsRequest(
            path=_models.GetChapterSnapshotsRequestPath(project_id=project_id, chapter_id=chapter_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_chapter_snapshots: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/chapters/{chapter_id}/snapshots", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/chapters/{chapter_id}/snapshots"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_chapter_snapshots")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_chapter_snapshots", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_chapter_snapshots",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def get_chapter_snapshot(
    project_id: str = Field(..., description="The unique identifier of the Studio project containing the chapter."),
    chapter_id: str = Field(..., description="The unique identifier of the chapter within the project."),
    chapter_snapshot_id: str = Field(..., description="The unique identifier of the specific chapter snapshot to retrieve."),
) -> dict[str, Any]:
    """Retrieves a specific chapter snapshot from a Studio project. Use this to access saved states or versions of a chapter."""

    # Construct request model with validation
    try:
        _request = _models.GetChapterSnapshotEndpointRequest(
            path=_models.GetChapterSnapshotEndpointRequestPath(project_id=project_id, chapter_id=chapter_id, chapter_snapshot_id=chapter_snapshot_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_chapter_snapshot: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/chapters/{chapter_id}/snapshots/{chapter_snapshot_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/chapters/{chapter_id}/snapshots/{chapter_snapshot_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_chapter_snapshot")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_chapter_snapshot", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_chapter_snapshot",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def get_chapter_snapshot_audio(
    project_id: str = Field(..., description="The unique identifier of the Studio project containing the chapter."),
    chapter_id: str = Field(..., description="The unique identifier of the chapter within the project."),
    chapter_snapshot_id: str = Field(..., description="The unique identifier of the chapter snapshot to stream."),
    convert_to_mpeg: bool | None = Field(None, description="Whether to convert the streamed audio to MPEG format. Defaults to false, returning the original audio format."),
) -> dict[str, Any]:
    """Retrieve and stream audio from a chapter snapshot. Use the list snapshots endpoint to discover available snapshots for a chapter."""

    # Construct request model with validation
    try:
        _request = _models.StreamChapterSnapshotAudioRequest(
            path=_models.StreamChapterSnapshotAudioRequestPath(project_id=project_id, chapter_id=chapter_id, chapter_snapshot_id=chapter_snapshot_id),
            body=_models.StreamChapterSnapshotAudioRequestBody(convert_to_mpeg=convert_to_mpeg)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_chapter_snapshot_audio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/chapters/{chapter_id}/snapshots/{chapter_snapshot_id}/stream", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/chapters/{chapter_id}/snapshots/{chapter_snapshot_id}/stream"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_chapter_snapshot_audio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_chapter_snapshot_audio", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_chapter_snapshot_audio",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: studio
@mcp.tool()
async def list_muted_tracks(project_id: str = Field(..., description="The unique identifier of the Studio project to query for muted tracks.")) -> dict[str, Any]:
    """Retrieves a list of chapter IDs that have muted tracks in a Studio project. Use this to identify which chapters contain audio that has been muted."""

    # Construct request model with validation
    try:
        _request = _models.GetProjectMutedTracksEndpointRequest(
            path=_models.GetProjectMutedTracksEndpointRequestPath(project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_muted_tracks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/studio/projects/{project_id}/muted-tracks", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/studio/projects/{project_id}/muted-tracks"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_muted_tracks")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_muted_tracks", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_muted_tracks",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def get_dubbing_resource(dubbing_id: str = Field(..., description="The unique identifier of the dubbing project created from the dubbing endpoint with studio mode enabled.")) -> dict[str, Any]:
    """Retrieves the dubbing resource for a given dubbing project ID that was created with studio enabled. Use this to access the generated dubbing output and associated metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetDubbingResourceRequest(
            path=_models.GetDubbingResourceRequestPath(dubbing_id=dubbing_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dubbing_resource: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dubbing_resource")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dubbing_resource", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dubbing_resource",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def add_dubbing_language(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project to which the language will be added."),
    language: str | None = Field(..., description="The target language code in ElevenLabs Turbo V2/V2.5 format to add to the dubbing resource."),
) -> dict[str, Any]:
    """Add a supported language to a dubbing project resource. The language is registered but does not automatically generate transcripts, translations, or audio content."""

    # Construct request model with validation
    try:
        _request = _models.AddLanguageRequest(
            path=_models.AddLanguageRequestPath(dubbing_id=dubbing_id),
            body=_models.AddLanguageRequestBody(language=language)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_dubbing_language: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/language", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/language"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_dubbing_language")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_dubbing_language", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_dubbing_language",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def create_segment(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project containing the speaker."),
    speaker_id: str = Field(..., description="The unique identifier of the speaker within the dubbing project."),
    start_time: float = Field(..., description="The start time of the segment in seconds (relative to the media timeline)."),
    end_time: float = Field(..., description="The end time of the segment in seconds (relative to the media timeline). Must be greater than the start time."),
    translations: dict[str, str] | None = Field(None, description="Optional translations for the segment content, organized by language code. Specify translations for any languages beyond the default project language."),
) -> dict[str, Any]:
    """Creates a new segment for a speaker in a dubbing project with specified start and end times across all available languages. The segment is created without automatically generating transcripts, translations, or audio content."""

    # Construct request model with validation
    try:
        _request = _models.CreateClipRequest(
            path=_models.CreateClipRequestPath(dubbing_id=dubbing_id, speaker_id=speaker_id),
            body=_models.CreateClipRequestBody(start_time=start_time, end_time=end_time, translations=translations)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/speaker/{speaker_id}/segment", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/speaker/{speaker_id}/segment"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_segment", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_segment",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def update_segment_language(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project containing the segment to modify."),
    segment_id: str = Field(..., description="The unique identifier of the segment within the dubbing project to be updated."),
    language: str = Field(..., description="The language identifier for which the segment content should be modified."),
    start_time: float | None = Field(None, description="The start time of the segment in seconds. Defines when the segment begins in the audio timeline."),
    end_time: float | None = Field(None, description="The end time of the segment in seconds. Defines when the segment ends in the audio timeline."),
) -> dict[str, Any]:
    """Modify the text and/or timing of a specific segment in a particular language within a dubbing project. Changes are applied only to the specified language and do not automatically trigger dub regeneration."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSegmentLanguageRequest(
            path=_models.UpdateSegmentLanguageRequestPath(dubbing_id=dubbing_id, segment_id=segment_id, language=language),
            body=_models.UpdateSegmentLanguageRequestBody(start_time=start_time, end_time=end_time)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_segment_language: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/segment/{segment_id}/{language}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/segment/{segment_id}/{language}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_segment_language")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_segment_language", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_segment_language",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def reassign_segments(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project containing the segments to reassign."),
    segment_ids: list[str] = Field(..., description="Array of segment identifiers to reassign to the target speaker. Order is preserved as provided."),
    speaker_id: str = Field(..., description="The unique identifier of the speaker to assign the segments to."),
) -> dict[str, Any]:
    """Reassign one or more segments in a dubbing project to a different speaker. This operation changes the speaker attribution for the specified segments."""

    # Construct request model with validation
    try:
        _request = _models.MigrateSegmentsRequest(
            path=_models.MigrateSegmentsRequestPath(dubbing_id=dubbing_id),
            body=_models.MigrateSegmentsRequestBody(segment_ids=segment_ids, speaker_id=speaker_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for reassign_segments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/migrate-segments", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/migrate-segments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("reassign_segments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("reassign_segments", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="reassign_segments",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def delete_dubbing_segment(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project containing the segment to be deleted."),
    segment_id: str = Field(..., description="The unique identifier of the segment to be deleted from the dubbing project."),
) -> dict[str, Any]:
    """Removes a single segment from a dubbing project. This operation permanently deletes the specified segment and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSegmentRequest(
            path=_models.DeleteSegmentRequestPath(dubbing_id=dubbing_id, segment_id=segment_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_dubbing_segment: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/segment/{segment_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/segment/{segment_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_dubbing_segment")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_dubbing_segment", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_dubbing_segment",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def regenerate_segment_transcriptions(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project containing the segments to transcribe."),
    segments: list[str] = Field(..., description="An array of segment identifiers to regenerate transcriptions for. Order is preserved as provided."),
) -> dict[str, Any]:
    """Regenerate transcriptions for specified segments within a dubbing project. This operation updates only the transcription text and does not affect existing translations or dubs."""

    # Construct request model with validation
    try:
        _request = _models.TranscribeRequest(
            path=_models.TranscribeRequestPath(dubbing_id=dubbing_id),
            body=_models.TranscribeRequestBody(segments=segments)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for regenerate_segment_transcriptions: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/transcribe", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/transcribe"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("regenerate_segment_transcriptions")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("regenerate_segment_transcriptions", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="regenerate_segment_transcriptions",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def translate_dubbing_segments(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project to translate."),
    segments: list[str] = Field(..., description="List of segment identifiers to translate. Only these segments will be processed; order is preserved as provided."),
    languages: list[str] = Field(..., description="List of target language codes to translate for each specified segment. Only these languages will be generated."),
) -> dict[str, Any]:
    """Regenerate translations for specified segments and languages in a dubbing project. Automatically transcribes any missing transcriptions but does not regenerate dubs."""

    # Construct request model with validation
    try:
        _request = _models.TranslateRequest(
            path=_models.TranslateRequestPath(dubbing_id=dubbing_id),
            body=_models.TranslateRequestBody(segments=segments, languages=languages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for translate_dubbing_segments: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/translate", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/translate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("translate_dubbing_segments")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("translate_dubbing_segments", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="translate_dubbing_segments",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def regenerate_dubs(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project to regenerate dubs for."),
    segments: list[str] = Field(..., description="List of segment identifiers to dub. Only the specified segments will be processed; order is preserved as provided."),
    languages: list[str] = Field(..., description="List of language codes to dub for each segment. Only the specified languages will be processed; order is preserved as provided."),
) -> dict[str, Any]:
    """Regenerate dubs for specified segments and languages in a dubbing project. Automatically transcribes and translates any missing transcriptions and translations."""

    # Construct request model with validation
    try:
        _request = _models.DubRequest(
            path=_models.DubRequestPath(dubbing_id=dubbing_id),
            body=_models.DubRequestBody(segments=segments, languages=languages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for regenerate_dubs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/dub", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/dub"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("regenerate_dubs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("regenerate_dubs", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="regenerate_dubs",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def update_speaker(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project containing the speaker."),
    speaker_id: str = Field(..., description="The unique identifier of the speaker to update."),
    speaker_name: str | None = Field(None, description="The display name to assign to this speaker."),
    voice_id: str | None = Field(None, description="The voice identifier, either from the ElevenLabs voice library or a cloning option ('track-clone' or 'clip-clone')."),
    voice_style: float | None = Field(None, description="The voice style intensity for supported models. Valid range is 0.0 to 1.0, defaults to 1.0."),
    languages: list[str] | None = Field(None, description="List of language codes to apply these speaker changes to. If empty or omitted, changes apply to all languages in the project."),
) -> dict[str, Any]:
    """Update speaker metadata in a dubbing project, including voice selection and styling. Supports both ElevenLabs library voices and voice cloning options."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSpeakerRequest(
            path=_models.UpdateSpeakerRequestPath(dubbing_id=dubbing_id, speaker_id=speaker_id),
            body=_models.UpdateSpeakerRequestBody(speaker_name=speaker_name, voice_id=voice_id, voice_style=voice_style, languages=languages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_speaker: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/speaker/{speaker_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/speaker/{speaker_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_speaker")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_speaker", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_speaker",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def add_speaker(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project to which the speaker will be added."),
    speaker_name: str | None = Field(None, description="A human-readable label for this speaker to identify it within the dubbing project."),
    voice_id: str | None = Field(None, description="The voice identifier to use for this speaker. Can be a voice from the ElevenLabs voice library or a special clone type for custom voice cloning."),
    voice_style: float | None = Field(None, description="The voice style intensity for models that support style control. Valid range is 0.0 to 1.0, with 1.0 as the default."),
) -> dict[str, Any]:
    """Add a new speaker to a dubbing project with a specified voice and optional styling. Each speaker represents a distinct voice track within the dubbing resource."""

    # Construct request model with validation
    try:
        _request = _models.CreateSpeakerRequest(
            path=_models.CreateSpeakerRequestPath(dubbing_id=dubbing_id),
            body=_models.CreateSpeakerRequestBody(speaker_name=speaker_name, voice_id=voice_id, voice_style=voice_style)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_speaker: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/speaker", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/speaker"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_speaker")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_speaker", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_speaker",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def list_similar_voices(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project containing the speaker."),
    speaker_id: str = Field(..., description="The unique identifier of the speaker within the dubbing project to find similar voices for."),
) -> dict[str, Any]:
    """Retrieve the top 10 voices from the ElevenLabs library that are most similar to a specified speaker in a dubbing project. Results include voice IDs, names, descriptions, and sample audio recordings where available."""

    # Construct request model with validation
    try:
        _request = _models.GetSimilarVoicesForSpeakerRequest(
            path=_models.GetSimilarVoicesForSpeakerRequestPath(dubbing_id=dubbing_id, speaker_id=speaker_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_similar_voices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/speaker/{speaker_id}/similar-voices", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/speaker/{speaker_id}/similar-voices"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_similar_voices")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_similar_voices", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_similar_voices",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, resource, segment, enterprise
@mcp.tool()
async def render_dubbing(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project to render."),
    language: str = Field(..., description="The target language code for rendering (e.g., 'es' for Spanish). Use 'original' to render the source track."),
    render_type: Literal["mp4", "aac", "mp3", "wav", "aaf", "tracks_zip", "clips_zip"] = Field(..., description="The output format for the rendered media."),
    normalize_volume: bool | None = Field(None, description="Whether to apply volume normalization to the rendered audio."),
) -> dict[str, Any]:
    """Generate output media for a specific language in a dubbing project using the current Studio state. All segments must be dubbed before rendering to be included in the output; renders are processed asynchronously."""

    # Construct request model with validation
    try:
        _request = _models.RenderRequest(
            path=_models.RenderRequestPath(dubbing_id=dubbing_id, language=language),
            body=_models.RenderRequestBody(render_type=render_type, normalize_volume=normalize_volume)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for render_dubbing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/resource/{dubbing_id}/render/{language}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/resource/{dubbing_id}/render/{language}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("render_dubbing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("render_dubbing", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="render_dubbing",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, dubbing
@mcp.tool()
async def list_dubs(
    page_size: int | None = Field(None, description="Maximum number of dubs to return per request. Defaults to 100 if not specified.", ge=1, le=200),
    dubbing_status: Literal["dubbing", "dubbed", "failed"] | None = Field(None, description="Filter results by the current processing state of the dub."),
    filter_by_creator: Literal["personal", "others", "all"] | None = Field(None, description="Filter results by creator: show only your dubs, dubs shared by others, or all dubs you have access to."),
    order_by: Literal["created_at"] | None = Field(None, description="Specify which field to use for ordering the results."),
    order_direction: Literal["DESCENDING", "ASCENDING"] | None = Field(None, description="Specify the sort direction for the ordered results."),
) -> dict[str, Any]:
    """Retrieve a list of dubs you have access to, with filtering and sorting options. Results can be filtered by status, creator, and ordered by specified fields."""

    # Construct request model with validation
    try:
        _request = _models.ListDubsRequest(
            query=_models.ListDubsRequestQuery(page_size=page_size, dubbing_status=dubbing_status, filter_by_creator=filter_by_creator, order_by=order_by, order_direction=order_direction)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dubs: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/dubbing"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dubs")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dubs", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dubs",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, dubbing
@mcp.tool()
async def dub_media(
    csv_file: str | None = Field(None, description="CSV file containing transcription and translation metadata for manual dubbing mode. Used to override automatic transcription and provide custom timing and speaker information."),
    name: str | None = Field(None, description="Human-readable name for the dubbing project to help organize and identify the job."),
    source_url: str | None = Field(None, description="URL pointing to the source video or audio file to be dubbed. Must be publicly accessible."),
    source_lang: str | None = Field(None, description="Language code of the source content using ISO 639-1 or ISO 639-3 format. Set to 'auto' to automatically detect the language."),
    target_lang: str | None = Field(None, description="Language code for the target dub using ISO 639-1 or ISO 639-3 format. Determines which language the content will be dubbed into."),
    target_accent: str | None = Field(None, description="Optional accent preference to apply when selecting voices and informing translation dialect. This is an experimental feature."),
    num_speakers: int | None = Field(None, description="Number of distinct speakers to use in the dubbing. Set to 0 to automatically detect the speaker count from the source audio."),
    watermark: bool | None = Field(None, description="Whether to add a watermark overlay to the output video file."),
    start_time: int | None = Field(None, description="Start time in seconds from which to begin dubbing the source file. Useful for processing only a segment of the content."),
    end_time: int | None = Field(None, description="End time in seconds at which to stop dubbing the source file. Useful for processing only a segment of the content."),
    highest_resolution: bool | None = Field(None, description="Whether to process and output the video at the highest available resolution. May increase processing time and resource usage."),
    drop_background_audio: bool | None = Field(None, description="Whether to remove background audio from the final dub. Recommended for content like speeches or monologues where background noise should not be preserved."),
    use_profanity_filter: bool | None = Field(None, description="Whether to censor profanities in transcripts by replacing them with '[censored]'. This is a beta feature."),
    dubbing_studio: bool | None = Field(None, description="Whether to prepare the output for editing in the dubbing studio interface or as a dubbing resource for further processing."),
    disable_voice_cloning: bool | None = Field(None, description="Whether to use similar voices from the ElevenLabs Voice Library instead of cloning the original speaker's voice. Requires 'add_voice_from_voice_library' workspace permission and consumes available custom voice slots."),
    mode: Literal["automatic", "manual"] | None = Field(None, description="Processing mode for the dubbing job. Use 'automatic' for standard processing or 'manual' when providing a custom CSV transcript. Manual mode is experimental and not recommended for production use."),
    csv_fps: float | None = Field(None, description="Frames per second value to use when parsing timecodes in the CSV file. If omitted, FPS will be automatically inferred from the timecode data."),
) -> dict[str, Any]:
    """Dubs an audio or video file into a target language with automatic speaker detection and voice synthesis. Supports advanced options for quality control, voice customization, and manual transcript editing."""

    # Construct request model with validation
    try:
        _request = _models.CreateDubbingRequest(
            body=_models.CreateDubbingRequestBody(csv_file=csv_file, name=name, source_url=source_url, source_lang=source_lang, target_lang=target_lang, target_accent=target_accent, num_speakers=num_speakers, watermark=watermark, start_time=start_time, end_time=end_time, highest_resolution=highest_resolution, drop_background_audio=drop_background_audio, use_profanity_filter=use_profanity_filter, dubbing_studio=dubbing_studio, disable_voice_cloning=disable_voice_cloning, mode=mode, csv_fps=csv_fps)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for dub_media: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/dubbing"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("dub_media")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("dub_media", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="dub_media",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, dubbing
@mcp.tool()
async def get_dubbing(dubbing_id: str = Field(..., description="The unique identifier of the dubbing project to retrieve metadata for.")) -> dict[str, Any]:
    """Retrieve metadata about a dubbing project, including its current processing status and completion state."""

    # Construct request model with validation
    try:
        _request = _models.GetDubbedMetadataRequest(
            path=_models.GetDubbedMetadataRequestPath(dubbing_id=dubbing_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_dubbing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/{dubbing_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/{dubbing_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_dubbing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_dubbing", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_dubbing",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, dubbing
@mcp.tool()
async def delete_dubbing(dubbing_id: str = Field(..., description="The unique identifier of the dubbing project to delete.")) -> dict[str, Any]:
    """Permanently deletes a dubbing project and all associated data. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteDubbingRequest(
            path=_models.DeleteDubbingRequestPath(dubbing_id=dubbing_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_dubbing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/{dubbing_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/{dubbing_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_dubbing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_dubbing", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_dubbing",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, dubbing
@mcp.tool()
async def download_dubbed_audio(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project containing the dubbed content."),
    language_code: str = Field(..., description="The language code specifying which dubbed audio track to retrieve."),
) -> dict[str, Any]:
    """Download the dubbed audio file in MP3 or MP4 format for a specific language. Returns the original automatic dub result; for edited dubs created in Dubbing Studio, use the render endpoint instead."""

    # Construct request model with validation
    try:
        _request = _models.GetDubbedFileRequest(
            path=_models.GetDubbedFileRequestPath(dubbing_id=dubbing_id, language_code=language_code)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_dubbed_audio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/{dubbing_id}/audio/{language_code}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/{dubbing_id}/audio/{language_code}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_dubbed_audio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_dubbed_audio", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_dubbed_audio",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: dubbing, dubbing, dubbing
@mcp.tool()
async def get_transcript_dubbing(
    dubbing_id: str = Field(..., description="The unique identifier of the dubbing project containing the transcript to retrieve."),
    language_code: str = Field(..., description="The language for which to retrieve the transcript. Use 'source' to fetch the original media transcript, or provide an ISO 639 language code."),
    format_type: Literal["srt", "webvtt", "json"] = Field(..., description="The output format for the transcript. Use 'srt' or 'webvtt' for subtitle formats, or 'json' for a full transcript (JSON format is not yet supported for Dubbing Studio)."),
) -> dict[str, Any]:
    """Retrieve the transcript for a specific language in a dubbing project. Supports multiple output formats including subtitle formats (SRT, WebVTT) and JSON transcripts."""

    # Construct request model with validation
    try:
        _request = _models.GetDubbingTranscriptsRequest(
            path=_models.GetDubbingTranscriptsRequestPath(dubbing_id=dubbing_id, language_code=language_code, format_type=format_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_transcript_dubbing: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/dubbing/{dubbing_id}/transcripts/{language_code}/format/{format_type}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/dubbing/{dubbing_id}/transcripts/{language_code}/format/{format_type}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_transcript_dubbing")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_transcript_dubbing", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_transcript_dubbing",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: models
@mcp.tool()
async def list_models() -> dict[str, Any]:
    """Retrieves a list of all available models that can be used for API operations."""

    # Extract parameters for API call
    _http_path = "/v1/models"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_models")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_models", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_models",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: audio-native
@mcp.tool()
async def create_audio_project(
    name: str = Field(..., description="The name of the audio project."),
    author: str | None = Field(None, description="The author name displayed in the audio player and at the start of the article. Uses the default author from Player settings if not specified."),
    voice_id: str | None = Field(None, description="The voice ID used for text-to-speech synthesis. Uses the default voice from Player settings if not specified."),
    model_id: str | None = Field(None, description="The TTS model ID used by the player. Uses the default model from Player settings if not specified."),
    auto_convert: bool | None = Field(None, description="Whether to automatically convert the project content to audio upon creation."),
    apply_text_normalization: Literal["auto", "on", "off", "apply_english"] | None = Field(None, description="Controls text normalization behavior. 'auto' lets the system decide, 'on' always applies normalization, 'apply_english' applies normalization assuming English text, and 'off' disables normalization."),
    pronunciation_dictionary_locators: list[str] | None = Field(None, description="A list of pronunciation dictionary locators, each containing a pronunciation_dictionary_id and version_id pair. Multiple dictionaries can be applied to customize pronunciation of specific terms."),
    player_colors: str | None = Field(None, description="Player colors as a comma-separated pair of hex color codes in format 'text_color,background_color' (e.g., '#FFFFFF,#000000'). If not provided, default colors set in Player settings are used."),
) -> dict[str, Any]:
    """Creates an Audio Native enabled project with optional automatic conversion to audio. Returns a project ID and embeddable HTML snippet for audio playback."""

    # Call helper functions
    player_colors_parsed = parse_player_colors(player_colors)

    # Construct request model with validation
    try:
        _request = _models.CreateAudioNativeProjectRequest(
            body=_models.CreateAudioNativeProjectRequestBody(name=name, author=author, voice_id=voice_id, model_id=model_id, auto_convert=auto_convert, apply_text_normalization=apply_text_normalization, pronunciation_dictionary_locators=pronunciation_dictionary_locators, text_color=player_colors_parsed.get('text_color') if player_colors_parsed else None, background_color=player_colors_parsed.get('background_color') if player_colors_parsed else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_audio_project: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/audio-native"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_audio_project")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_audio_project", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_audio_project",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: audio-native
@mcp.tool()
async def get_audio_native_settings(project_id: str = Field(..., description="The unique identifier of the Studio project for which to retrieve Audio Native settings.")) -> dict[str, Any]:
    """Retrieve player settings and configuration for an Audio Native project. Use this to access the current settings applied to a specific project."""

    # Construct request model with validation
    try:
        _request = _models.GetAudioNativeProjectSettingsEndpointRequest(
            path=_models.GetAudioNativeProjectSettingsEndpointRequestPath(project_id=project_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_audio_native_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/audio-native/{project_id}/settings", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/audio-native/{project_id}/settings"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_audio_native_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_audio_native_settings", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_audio_native_settings",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: audio-native
@mcp.tool()
async def update_audio_native_content(
    project_id: str = Field(..., description="The unique identifier of the Studio project to update."),
    auto_convert: bool | None = Field(None, description="Automatically convert the project to audio format after content update."),
    auto_publish: bool | None = Field(None, description="Automatically publish a new project snapshot after conversion completes. Only applies when auto_convert is enabled."),
) -> dict[str, Any]:
    """Updates content for an Audio-Native project with optional automatic conversion and publishing. Use this to modify project content and trigger downstream processing workflows."""

    # Construct request model with validation
    try:
        _request = _models.AudioNativeProjectUpdateContentEndpointRequest(
            path=_models.AudioNativeProjectUpdateContentEndpointRequestPath(project_id=project_id),
            body=_models.AudioNativeProjectUpdateContentEndpointRequestBody(auto_convert=auto_convert, auto_publish=auto_publish)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_audio_native_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/audio-native/{project_id}/content", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/audio-native/{project_id}/content"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_audio_native_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_audio_native_content", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_audio_native_content",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: audio-native
@mcp.tool()
async def update_audio_native_content_from_url(
    url: str = Field(..., description="The web page URL from which to extract content for the AudioNative project."),
    author: str | None = Field(None, description="Optional author name to display in the player and insert at the start of the article. Uses the default author from Player settings if not provided."),
) -> dict[str, Any]:
    """Extracts content from a provided URL, updates the matching AudioNative project, and queues it for conversion and auto-publishing."""

    # Construct request model with validation
    try:
        _request = _models.AudioNativeUpdateContentFromUrlRequest(
            body=_models.AudioNativeUpdateContentFromUrlRequestBody(url=url, author=author)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_audio_native_content_from_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/audio-native/content"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_audio_native_content_from_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_audio_native_content_from_url", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_audio_native_content_from_url",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: voices
@mcp.tool()
async def list_voices_shared(
    page_size: int | None = Field(None, description="Maximum number of voices to return per page. Limited to 100 voices maximum."),
    category: Literal["professional", "famous", "high_quality"] | None = Field(None, description="Filter voices by category type."),
    gender: str | None = Field(None, description="Filter voices by gender."),
    age: str | None = Field(None, description="Filter voices by age group."),
    accent: str | None = Field(None, description="Filter voices by accent."),
    language: str | None = Field(None, description="Filter voices by language code."),
    locale: str | None = Field(None, description="Filter voices by locale code."),
    use_cases: list[str] | None = Field(None, description="Filter voices by one or more use cases. Multiple use cases can be specified to find voices suitable for specific applications."),
    featured: bool | None = Field(None, description="When enabled, returns only voices marked as featured."),
    min_notice_period_days: int | None = Field(None, description="Filter voices that require a minimum notice period before use, specified in days."),
    include_custom_rates: bool | None = Field(None, description="When enabled, includes voices that have custom pricing rates."),
    include_live_moderated: bool | None = Field(None, description="When enabled, includes voices that are live moderated."),
    reader_app_enabled: bool | None = Field(None, description="When enabled, returns only voices that are enabled for the reader app."),
    owner_id: str | None = Field(None, description="Filter voices by the public owner ID of the voice creator."),
    sort: str | None = Field(None, description="Sort results by the specified criteria."),
    page: int | None = Field(None, description="Page number for pagination, starting from 0."),
) -> dict[str, Any]:
    """Retrieves a paginated list of shared voices with optional filtering by category, demographics, language, use cases, and other attributes. Useful for discovering available voices for text-to-speech applications."""

    # Construct request model with validation
    try:
        _request = _models.GetLibraryVoicesRequest(
            query=_models.GetLibraryVoicesRequestQuery(page_size=page_size, category=category, gender=gender, age=age, accent=accent, language=language, locale=locale, use_cases=use_cases, featured=featured, min_notice_period_days=min_notice_period_days, include_custom_rates=include_custom_rates, include_live_moderated=include_live_moderated, reader_app_enabled=reader_app_enabled, owner_id=owner_id, sort=sort, page=page)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_voices_shared: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/shared-voices"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_voices_shared")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_voices_shared", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_voices_shared",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: voices
@mcp.tool()
async def find_similar_voices(
    audio_file: str | None = Field(None, description="Audio sample file to match against library voices. Used as the reference for similarity comparison."),
    similarity_threshold: float | None = Field(None, description="Similarity threshold for filtering results. Lower values return more similar voices. Valid range is 0 to 2."),
    top_k: int | None = Field(None, description="Maximum number of similar voices to return. If similarity_threshold is also specified, fewer voices may be returned. Valid range is 1 to 100."),
) -> dict[str, Any]:
    """Find voices from the library that are similar to a provided audio sample. Returns a ranked list of matching voices based on similarity scoring."""

    # Construct request model with validation
    try:
        _request = _models.GetSimilarLibraryVoicesRequest(
            body=_models.GetSimilarLibraryVoicesRequestBody(audio_file=audio_file, similarity_threshold=similarity_threshold, top_k=top_k)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for find_similar_voices: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/similar-voices"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("find_similar_voices")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("find_similar_voices", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="find_similar_voices",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def get_character_usage_metrics(
    start_unix: int = Field(..., description="Start of the usage window as a UTC Unix timestamp in milliseconds. Use 00:00:00 of the first day to include it in the results."),
    end_unix: int = Field(..., description="End of the usage window as a UTC Unix timestamp in milliseconds. Use 23:59:59 of the last day to include it in the results."),
    include_workspace_metrics: bool | None = Field(None, description="Include usage statistics for the entire workspace in addition to user-specific metrics."),
    breakdown_type: Literal["none", "voice", "voice_multiplier", "user", "groups", "api_keys", "all_api_keys", "product_type", "model", "resource", "request_queue", "region", "subresource_id", "reporting_workspace_id", "has_api_key", "request_source"] | None = Field(None, description="Dimension to break down usage metrics by. The 'user' breakdown requires include_workspace_metrics to be true."),
    aggregation_bucket_size: int | None = Field(None, description="Custom aggregation interval in seconds. When specified, overrides the default daily aggregation."),
    metric: Literal["credits", "tts_characters", "minutes_used", "request_count", "ttfb_avg", "ttfb_p95", "fiat_units_spent", "concurrency", "concurrency_average"] | None = Field(None, description="The usage metric to aggregate and return in the results."),
) -> dict[str, Any]:
    """Retrieve character usage metrics for the current user or entire workspace over a specified time period. Results can be aggregated by time interval and broken down by various dimensions such as voice, user, or API key."""

    # Construct request model with validation
    try:
        _request = _models.UsageCharactersRequest(
            query=_models.UsageCharactersRequestQuery(start_unix=start_unix, end_unix=end_unix, include_workspace_metrics=include_workspace_metrics, breakdown_type=breakdown_type, aggregation_bucket_size=aggregation_bucket_size, metric=metric)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_character_usage_metrics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/usage/character-stats"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_character_usage_metrics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_character_usage_metrics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_character_usage_metrics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pronunciation Dictionary
@mcp.tool()
async def create_pronunciation_dictionary(
    name: str = Field(..., description="The name of the pronunciation dictionary used for identification and reference within the system."),
    description: str | None = Field(None, description="An optional description of the pronunciation dictionary to provide additional context about its contents or purpose."),
    workspace_access: Literal["admin", "editor", "commenter", "viewer"] | None = Field(None, description="The workspace access level that determines permissions for other users to interact with this dictionary. If not provided, defaults to no access."),
) -> dict[str, Any]:
    """Creates a new pronunciation dictionary from a lexicon .PLS file. The dictionary can be configured with access permissions for workspace collaboration."""

    # Construct request model with validation
    try:
        _request = _models.AddFromFileRequest(
            body=_models.AddFromFileRequestBody(name=name, description=description, workspace_access=workspace_access)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pronunciation_dictionary: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pronunciation-dictionaries/add-from-file"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pronunciation_dictionary")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pronunciation_dictionary", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pronunciation_dictionary",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Pronunciation Dictionary
@mcp.tool()
async def create_pronunciation_dictionary_from_rules(
    name: str = Field(..., description="The name of the pronunciation dictionary used for identification and reference purposes."),
    description: str | None = Field(None, description="An optional description of the pronunciation dictionary to provide additional context about its contents or purpose."),
    workspace_access: Literal["admin", "editor", "commenter", "viewer"] | None = Field(None, description="The access level for workspace users. Determines whether users can administer, edit, comment on, or only view the dictionary. Defaults to no access if not specified."),
    alias_rules: list[dict[str, Any]] | None = Field(None, description="List of alias rules. Each rule is a dict with 'string_to_replace' (str) and 'alias' (str) keys."),
    phoneme_rules: list[dict[str, Any]] | None = Field(None, description="List of phoneme rules. Each rule is a dict with 'string_to_replace' (str), 'phoneme' (str), and 'alphabet' (str) keys."),
) -> dict[str, Any]:
    """Creates a new pronunciation dictionary from provided rules. The dictionary can be configured with access permissions for workspace collaboration."""

    # Call helper functions
    rules = build_rules(alias_rules, phoneme_rules)

    # Construct request model with validation
    try:
        _request = _models.AddFromRulesRequest(
            body=_models.AddFromRulesRequestBody(name=name, description=description, workspace_access=workspace_access, rules=rules)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_pronunciation_dictionary_from_rules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pronunciation-dictionaries/add-from-rules"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_pronunciation_dictionary_from_rules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_pronunciation_dictionary_from_rules", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_pronunciation_dictionary_from_rules",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pronunciation Dictionary
@mcp.tool()
async def get_pronunciation_dictionary(pronunciation_dictionary_id: str = Field(..., description="The unique identifier of the pronunciation dictionary to retrieve metadata for.")) -> dict[str, Any]:
    """Retrieve metadata for a specific pronunciation dictionary by its ID. Returns configuration details and properties of the pronunciation dictionary."""

    # Construct request model with validation
    try:
        _request = _models.GetPronunciationDictionaryMetadataRequest(
            path=_models.GetPronunciationDictionaryMetadataRequestPath(pronunciation_dictionary_id=pronunciation_dictionary_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_pronunciation_dictionary: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_pronunciation_dictionary")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_pronunciation_dictionary", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_pronunciation_dictionary",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pronunciation Dictionary
@mcp.tool()
async def update_pronunciation_dictionary(
    pronunciation_dictionary_id: str = Field(..., description="The unique identifier of the pronunciation dictionary to update."),
    archived: bool | None = Field(None, description="Set whether the pronunciation dictionary should be archived. Archived dictionaries are retained but no longer active."),
    name: str | None = Field(None, description="A human-readable name for the pronunciation dictionary used for identification and organization purposes."),
) -> dict[str, Any]:
    """Partially update a pronunciation dictionary by modifying its name or archive status without affecting the version. Only specified fields will be updated."""

    # Construct request model with validation
    try:
        _request = _models.PatchPronunciationDictionaryRequest(
            path=_models.PatchPronunciationDictionaryRequestPath(pronunciation_dictionary_id=pronunciation_dictionary_id),
            body=_models.PatchPronunciationDictionaryRequestBody(archived=archived, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_pronunciation_dictionary: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_pronunciation_dictionary")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_pronunciation_dictionary", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_pronunciation_dictionary",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pronunciation Dictionary
@mcp.tool()
async def replace_pronunciation_rules(
    pronunciation_dictionary_id: str = Field(..., description="The unique identifier of the pronunciation dictionary to update."),
    rules: list[_models.PronunciationDictionaryAliasRuleRequestModel | _models.PronunciationDictionaryPhonemeRuleRequestModel] = Field(..., description="An ordered list of pronunciation rules to apply. Each rule maps a string to either an alias (another string) or a phoneme (with a specified alphabet such as IPA). All existing rules will be replaced with this list."),
) -> dict[str, Any]:
    """Replace all pronunciation rules in a dictionary with a new set of rules. Rules can define phonetic aliases or phoneme mappings using specified alphabets."""

    # Construct request model with validation
    try:
        _request = _models.SetRulesRequest(
            path=_models.SetRulesRequestPath(pronunciation_dictionary_id=pronunciation_dictionary_id),
            body=_models.SetRulesRequestBody(rules=rules)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for replace_pronunciation_rules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}/set-rules", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}/set-rules"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("replace_pronunciation_rules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("replace_pronunciation_rules", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="replace_pronunciation_rules",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pronunciation Dictionary
@mcp.tool()
async def add_pronunciation_rules(
    pronunciation_dictionary_id: str = Field(..., description="The unique identifier of the pronunciation dictionary to modify."),
    rules: list[_models.PronunciationDictionaryAliasRuleRequestModel | _models.PronunciationDictionaryPhonemeRuleRequestModel] = Field(..., description="An ordered list of pronunciation rules to add or update. Each rule must be either an alias rule (mapping one string to another alias) or a phoneme rule (mapping a string to a phoneme in a specified alphabet such as IPA)."),
) -> dict[str, Any]:
    """Add or update pronunciation rules in a dictionary. Rules with duplicate string_to_replace values will replace existing rules."""

    # Construct request model with validation
    try:
        _request = _models.AddRulesRequest(
            path=_models.AddRulesRequestPath(pronunciation_dictionary_id=pronunciation_dictionary_id),
            body=_models.AddRulesRequestBody(rules=rules)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_pronunciation_rules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}/add-rules", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}/add-rules"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_pronunciation_rules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_pronunciation_rules", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_pronunciation_rules",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pronunciation Dictionary
@mcp.tool()
async def delete_pronunciation_rules(
    pronunciation_dictionary_id: str = Field(..., description="The unique identifier of the pronunciation dictionary from which rules will be removed."),
    rule_strings: list[str] = Field(..., description="An array of rule strings to remove from the pronunciation dictionary. Each string represents a rule to be deleted. Order is not significant."),
) -> dict[str, Any]:
    """Remove one or more pronunciation rules from a pronunciation dictionary. Specify the dictionary ID and provide the list of rule strings to be deleted."""

    # Construct request model with validation
    try:
        _request = _models.RemoveRulesRequest(
            path=_models.RemoveRulesRequestPath(pronunciation_dictionary_id=pronunciation_dictionary_id),
            body=_models.RemoveRulesRequestBody(rule_strings=rule_strings)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_pronunciation_rules: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}/remove-rules", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pronunciation-dictionaries/{pronunciation_dictionary_id}/remove-rules"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_pronunciation_rules")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_pronunciation_rules", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_pronunciation_rules",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pronunciation Dictionary
@mcp.tool()
async def download_pronunciation_dictionary_version(
    dictionary_id: str = Field(..., description="The unique identifier of the pronunciation dictionary to retrieve."),
    version_id: str = Field(..., description="The unique identifier of the specific version of the pronunciation dictionary to download."),
) -> dict[str, Any]:
    """Download a PLS (Pronunciation Lexicon Specification) file containing the rules for a specific version of a pronunciation dictionary."""

    # Construct request model with validation
    try:
        _request = _models.GetPronunciationDictionaryVersionPlsRequest(
            path=_models.GetPronunciationDictionaryVersionPlsRequestPath(dictionary_id=dictionary_id, version_id=version_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for download_pronunciation_dictionary_version: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/pronunciation-dictionaries/{dictionary_id}/{version_id}/download", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/pronunciation-dictionaries/{dictionary_id}/{version_id}/download"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("download_pronunciation_dictionary_version")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("download_pronunciation_dictionary_version", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="download_pronunciation_dictionary_version",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Pronunciation Dictionary
@mcp.tool()
async def list_pronunciation_dictionaries(
    page_size: int | None = Field(None, description="Maximum number of pronunciation dictionaries to return per request. Must be between 1 and 100.", ge=1, le=100),
    sort: Literal["creation_time_unix", "name"] | None = Field(None, description="Field to sort the results by. Choose between creation time or alphabetical name ordering."),
    sort_direction: str | None = Field(None, description="Direction to sort the results in. Use ascending for oldest-first or newest-first, descending for newest-first or Z-to-A ordering."),
) -> dict[str, Any]:
    """Retrieve a paginated list of pronunciation dictionaries you have access to, with sorting and filtering options. Returns metadata for each dictionary including creation date and name."""

    # Construct request model with validation
    try:
        _request = _models.GetPronunciationDictionariesMetadataRequest(
            query=_models.GetPronunciationDictionariesMetadataRequestQuery(page_size=page_size, sort=sort, sort_direction=sort_direction)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_pronunciation_dictionaries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/pronunciation-dictionaries"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_pronunciation_dictionaries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_pronunciation_dictionaries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_pronunciation_dictionaries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def list_service_account_api_keys(service_account_user_id: str = Field(..., description="The unique identifier of the service account for which to retrieve API keys.")) -> dict[str, Any]:
    """Retrieve all API keys associated with a specific service account. Use this to view and manage authentication credentials for programmatic access."""

    # Construct request model with validation
    try:
        _request = _models.GetServiceAccountApiKeysRouteRequest(
            path=_models.GetServiceAccountApiKeysRouteRequestPath(service_account_user_id=service_account_user_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_service_account_api_keys: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/service-accounts/{service_account_user_id}/api-keys", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/service-accounts/{service_account_user_id}/api-keys"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_service_account_api_keys")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_service_account_api_keys", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_service_account_api_keys",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def create_service_account_api_key(
    service_account_user_id: str = Field(..., description="The unique identifier of the service account for which to create the API key."),
    name: str = Field(..., description="A human-readable name for the API key to help identify its purpose or usage context."),
    permissions: list[Literal["text_to_speech", "speech_to_speech", "speech_to_text", "models_read", "models_write", "voices_read", "voices_write", "speech_history_read", "speech_history_write", "sound_generation", "audio_isolation", "voice_generation", "dubbing_read", "dubbing_write", "pronunciation_dictionaries_read", "pronunciation_dictionaries_write", "user_read", "user_write", "projects_read", "projects_write", "audio_native_read", "audio_native_write", "workspace_read", "workspace_write", "forced_alignment", "convai_read", "convai_write", "music_generation", "image_video_generation", "add_voice_from_voice_library", "create_instant_voice_clone", "create_professional_voice_clone", "publish_voice_to_voice_library", "share_voice_externally", "create_user_api_key", "workspace_analytics_full_read", "webhooks_write", "service_account_write", "group_members_manage", "workspace_members_read", "workspace_members_invite", "workspace_members_remove", "terms_of_service_accept"]] | Literal["all"] = Field(..., description="The set of permissions to grant this API key, controlling which XI API operations it can perform."),
    character_limit: int | None = Field(None, description="Optional monthly character limit for this API key. When set, requests that would exceed this limit will be rejected, preventing unexpected usage charges."),
) -> dict[str, Any]:
    """Generate a new API key for a service account with specified permissions and optional usage limits. The created key can be used to authenticate requests to the XI API on behalf of the service account."""

    # Construct request model with validation
    try:
        _request = _models.CreateServiceAccountApiKeyRequest(
            path=_models.CreateServiceAccountApiKeyRequestPath(service_account_user_id=service_account_user_id),
            body=_models.CreateServiceAccountApiKeyRequestBody(name=name, permissions=permissions, character_limit=character_limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_service_account_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/service-accounts/{service_account_user_id}/api-keys", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/service-accounts/{service_account_user_id}/api-keys"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_service_account_api_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_service_account_api_key", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_service_account_api_key",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def revoke_service_account_api_key(
    service_account_user_id: str = Field(..., description="The unique identifier of the service account that owns the API key to be deleted."),
    api_key_id: str = Field(..., description="The unique identifier of the API key to be revoked and deleted."),
) -> dict[str, Any]:
    """Revoke and permanently delete an API key associated with a service account. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteServiceAccountApiKeyRequest(
            path=_models.DeleteServiceAccountApiKeyRequestPath(service_account_user_id=service_account_user_id, api_key_id=api_key_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_service_account_api_key: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/service-accounts/{service_account_user_id}/api-keys/{api_key_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/service-accounts/{service_account_user_id}/api-keys/{api_key_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_service_account_api_key")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_service_account_api_key", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_service_account_api_key",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def list_auth_connections() -> dict[str, Any]:
    """Retrieve all authentication connections configured for the workspace. Returns a list of all connected auth providers and their configurations."""

    # Extract parameters for API call
    _http_path = "/v1/workspace/auth-connections"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_auth_connections")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_auth_connections", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_auth_connections",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def delete_auth_connection(auth_connection_id: str = Field(..., description="The unique identifier of the authentication connection to delete.")) -> dict[str, Any]:
    """Delete an authentication connection from the workspace. This removes the stored credentials and configuration for the specified auth connection."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAuthConnectionRequest(
            path=_models.DeleteAuthConnectionRequestPath(auth_connection_id=auth_connection_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_auth_connection: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workspace/auth-connections/{auth_connection_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workspace/auth-connections/{auth_connection_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_auth_connection")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_auth_connection", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_auth_connection",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def list_service_accounts() -> dict[str, Any]:
    """Retrieve all service accounts configured in the workspace. Service accounts are used for programmatic access and automation within the workspace."""

    # Extract parameters for API call
    _http_path = "/v1/service-accounts"
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
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def list_groups() -> dict[str, Any]:
    """Retrieve all groups in the workspace. Returns a complete list of groups available to the authenticated user."""

    # Extract parameters for API call
    _http_path = "/v1/workspace/groups"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_groups")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_groups", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_groups",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def find_group(name: str = Field(..., description="The name of the user group to search for. The search will match against group names in the workspace.")) -> dict[str, Any]:
    """Searches for user groups in the workspace by name. Returns matching group(s) or an empty result if no groups are found."""

    # Construct request model with validation
    try:
        _request = _models.SearchGroupsRequest(
            query=_models.SearchGroupsRequestQuery(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for find_group: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/workspace/groups/search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("find_group")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("find_group", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="find_group",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def remove_group_member(
    group_id: str = Field(..., description="The unique identifier of the group from which the member will be removed."),
    email: str = Field(..., description="The email address of the workspace member to remove from the group."),
) -> dict[str, Any]:
    """Remove a member from a user group. Requires `group_members_manage` permission to perform this action."""

    # Construct request model with validation
    try:
        _request = _models.RemoveMemberRequest(
            path=_models.RemoveMemberRequestPath(group_id=group_id),
            body=_models.RemoveMemberRequestBody(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_group_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workspace/groups/{group_id}/members/remove", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workspace/groups/{group_id}/members/remove"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_group_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_group_member", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_group_member",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def add_group_member(
    group_id: str = Field(..., description="The unique identifier of the group to which the member will be added."),
    email: str = Field(..., description="The email address of the workspace member to add to the group."),
) -> dict[str, Any]:
    """Adds a workspace member to a user group. Requires group_members_manage permission."""

    # Construct request model with validation
    try:
        _request = _models.AddMemberRequest(
            path=_models.AddMemberRequestPath(group_id=group_id),
            body=_models.AddMemberRequestBody(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_group_member: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workspace/groups/{group_id}/members", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workspace/groups/{group_id}/members"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_group_member")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_group_member", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_group_member",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def send_workspace_invite(
    email: str = Field(..., description="The email address of the user to invite to the workspace."),
    seat_type: Literal["workspace_admin", "workspace_member", "workspace_lite_member"] | None = Field(None, description="The permission level to assign the invited user within the workspace."),
    group_ids: list[str] | None = Field(None, description="List of group IDs to assign the invited user to. Groups determine access permissions and organizational structure within the workspace."),
) -> dict[str, Any]:
    """Sends an email invitation to join the workspace. The recipient will be prompted to create an account if needed, and upon acceptance will be added as a workspace user consuming one available seat. Requires WORKSPACE_MEMBERS_INVITE permission."""

    # Construct request model with validation
    try:
        _request = _models.InviteUserRequest(
            body=_models.InviteUserRequestBody(email=email, seat_type=seat_type, group_ids=group_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_workspace_invite: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/workspace/invites/add"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_workspace_invite")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_workspace_invite", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_workspace_invite",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def send_workspace_invitations(
    emails: list[str] = Field(..., description="List of email addresses to invite. All emails must belong to verified domains associated with your workspace."),
    seat_type: Literal["workspace_admin", "workspace_member", "workspace_lite_member"] | None = Field(None, description="The permission level to assign to invited users within the workspace."),
    group_ids: list[str] | None = Field(None, description="List of group IDs to assign the invited users to upon acceptance. Groups organize users and manage permissions within the workspace."),
) -> dict[str, Any]:
    """Send email invitations to multiple users to join your workspace. Invitees must have email addresses from verified domains, and accepted invitations will add them as workspace users consuming available seats."""

    # Construct request model with validation
    try:
        _request = _models.InviteUsersBulkRequest(
            body=_models.InviteUsersBulkRequestBody(emails=emails, seat_type=seat_type, group_ids=group_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_workspace_invitations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/workspace/invites/add-bulk"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_workspace_invitations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_workspace_invitations", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_workspace_invitations",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def revoke_workspace_invitation(email: str = Field(..., description="The email address of the invitation recipient whose invitation should be revoked.")) -> dict[str, Any]:
    """Revoke an existing workspace invitation by email address. The invitation will remain visible in the recipient's inbox but will no longer be activatable to join the workspace. Only workspace members with WORKSPACE_MEMBERS_INVITE permission can perform this action."""

    # Construct request model with validation
    try:
        _request = _models.DeleteInviteRequest(
            body=_models.DeleteInviteRequestBody(email=email)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_workspace_invitation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/workspace/invites"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_workspace_invitation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_workspace_invitation", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_workspace_invitation",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def get_resource(
    resource_id: str = Field(..., description="The unique identifier of the resource to retrieve."),
    resource_type: Literal["voice", "voice_collection", "pronunciation_dictionary", "dubbing", "project", "convai_agents", "convai_knowledge_base_documents", "convai_tools", "convai_settings", "convai_secrets", "workspace_auth_connections", "convai_phone_numbers", "convai_mcp_servers", "convai_api_integration_connections", "convai_api_integration_trigger_connections", "convai_batch_calls", "convai_agent_response_tests", "convai_test_suite_invocations", "convai_crawl_jobs", "convai_crawl_tasks", "convai_whatsapp_accounts", "convai_agent_versions", "convai_agent_branches", "convai_agent_versions_deployments", "convai_memory_entries", "convai_coaching_proposals", "dashboard", "dashboard_configuration", "convai_agent_drafts", "resource_locators", "assets", "content_generations", "content_templates", "songs"] = Field(..., description="The category of the resource. Determines which resource type's metadata will be returned."),
) -> dict[str, Any]:
    """Retrieves metadata for a specific resource by its ID and type. Use this to fetch detailed information about any resource in your workspace."""

    # Construct request model with validation
    try:
        _request = _models.GetResourceMetadataRequest(
            path=_models.GetResourceMetadataRequestPath(resource_id=resource_id),
            query=_models.GetResourceMetadataRequestQuery(resource_type=resource_type)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_resource: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workspace/resources/{resource_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workspace/resources/{resource_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_resource")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_resource", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_resource",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def grant_resource_access(
    resource_id: str = Field(..., description="The unique identifier of the resource to share."),
    role: Literal["admin", "editor", "commenter", "viewer"] = Field(..., description="The access level to grant to the principal. Determines what actions the principal can perform on the resource."),
    resource_type: Literal["voice", "voice_collection", "pronunciation_dictionary", "dubbing", "project", "convai_agents", "convai_knowledge_base_documents", "convai_tools", "convai_settings", "convai_secrets", "workspace_auth_connections", "convai_phone_numbers", "convai_mcp_servers", "convai_api_integration_connections", "convai_api_integration_trigger_connections", "convai_batch_calls", "convai_agent_response_tests", "convai_test_suite_invocations", "convai_crawl_jobs", "convai_crawl_tasks", "convai_whatsapp_accounts", "convai_agent_versions", "convai_agent_branches", "convai_agent_versions_deployments", "convai_memory_entries", "convai_coaching_proposals", "dashboard", "dashboard_configuration", "convai_agent_drafts", "resource_locators", "assets", "content_generations", "content_templates", "songs"] = Field(..., description="The category of resource being shared. Determines the type of object referenced by resource_id."),
    user_email: str | None = Field(None, description="The email address of the user or service account to grant access to. The principal must already exist in your workspace."),
    group_id: str | None = Field(None, description="The unique identifier of the group to grant access to. Use the special value 'default' to target the default permissions principals have on this resource."),
    workspace_api_key_id: str | None = Field(None, description="The unique identifier of the workspace API key to grant access to. This is the key ID found in workspace settings, not the API key credential itself. Access will be granted to the service account associated with this key."),
) -> dict[str, Any]:
    """Grant or update a role on a workspace resource for a user, service account, group, or API key. This operation overrides any existing role the principal has on the resource. You must have admin access to the resource to perform this action."""

    # Construct request model with validation
    try:
        _request = _models.ShareResourceEndpointRequest(
            path=_models.ShareResourceEndpointRequestPath(resource_id=resource_id),
            body=_models.ShareResourceEndpointRequestBody(role=role, resource_type=resource_type, user_email=user_email, group_id=group_id, workspace_api_key_id=workspace_api_key_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for grant_resource_access: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workspace/resources/{resource_id}/share", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workspace/resources/{resource_id}/share"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("grant_resource_access")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("grant_resource_access", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="grant_resource_access",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def revoke_resource_access(
    resource_id: str = Field(..., description="The unique identifier of the workspace resource to revoke access from."),
    resource_type: Literal["voice", "voice_collection", "pronunciation_dictionary", "dubbing", "project", "convai_agents", "convai_knowledge_base_documents", "convai_tools", "convai_settings", "convai_secrets", "workspace_auth_connections", "convai_phone_numbers", "convai_mcp_servers", "convai_api_integration_connections", "convai_api_integration_trigger_connections", "convai_batch_calls", "convai_agent_response_tests", "convai_test_suite_invocations", "convai_crawl_jobs", "convai_crawl_tasks", "convai_whatsapp_accounts", "convai_agent_versions", "convai_agent_branches", "convai_agent_versions_deployments", "convai_memory_entries", "convai_coaching_proposals", "dashboard", "dashboard_configuration", "convai_agent_drafts", "resource_locators", "assets", "content_generations", "content_templates", "songs"] = Field(..., description="The category of the workspace resource being modified."),
    user_email: str | None = Field(None, description="The email address of the user or service account to revoke access from. The user or service account must exist in your workspace."),
    group_id: str | None = Field(None, description="The identifier of the group to revoke access from. Use 'default' to target default permissions principals have on this resource."),
    workspace_api_key_id: str | None = Field(None, description="The identifier of the workspace API key to revoke access from. This is the key ID found in workspace settings, not the authentication key itself. Access will be revoked from the service account associated with this API key."),
) -> dict[str, Any]:
    """Removes all access permissions for a user, service account, group, or workspace API key to a workspace resource. The requester must have admin access to the resource."""

    # Construct request model with validation
    try:
        _request = _models.UnshareResourceEndpointRequest(
            path=_models.UnshareResourceEndpointRequestPath(resource_id=resource_id),
            body=_models.UnshareResourceEndpointRequestBody(resource_type=resource_type, user_email=user_email, group_id=group_id, workspace_api_key_id=workspace_api_key_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_resource_access: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/workspace/resources/{resource_id}/unshare", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/workspace/resources/{resource_id}/unshare"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_resource_access")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_resource_access", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_resource_access",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: workspace
@mcp.tool()
async def list_workspace_webhooks(include_usages: bool | None = Field(None, description="Include active usage statistics for each webhook. Only accessible to workspace administrators.")) -> dict[str, Any]:
    """Retrieve all webhooks configured for a workspace. Optionally include active usage statistics for each webhook (admin-only feature)."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspaceWebhooksRouteRequest(
            query=_models.GetWorkspaceWebhooksRouteRequestQuery(include_usages=include_usages)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_workspace_webhooks: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/workspace/webhooks"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: speech-to-text
@mcp.tool()
async def transcribe_audio(
    model_id: Literal["scribe_v1", "scribe_v2"] = Field(..., description="The transcription model to use. Choose between scribe_v1 (standard) or scribe_v2 (enhanced with additional features like verbatim control)."),
    language_code: str | None = Field(None, description="ISO-639-1 or ISO-639-3 language code of the audio content. Providing the language can improve transcription accuracy; if omitted, language is automatically detected."),
    tag_audio_events: bool | None = Field(None, description="Whether to identify and tag audio events such as laughter, footsteps, and other non-speech sounds in the transcript."),
    num_speakers: int | None = Field(None, description="Maximum number of speakers expected in the audio. Helps the model predict speaker transitions more accurately. If not specified, the model uses its maximum supported speaker count (up to 32).", ge=1, le=32),
    timestamps_granularity: Literal["none", "word", "character"] | None = Field(None, description="Timestamp precision level in the transcript. 'word' provides timestamps for each word, 'character' provides character-level timestamps within words, and 'none' omits timestamps."),
    diarize: bool | None = Field(None, description="Whether to perform speaker diarization to identify and label which speaker is talking at each point in the transcript."),
    diarization_threshold: float | None = Field(None, description="Sensitivity threshold for speaker diarization (only applies when diarize is true and num_speakers is not specified). Higher values reduce speaker fragmentation but increase the risk of merging distinct speakers; lower values do the opposite. The model selects a default threshold based on the chosen model_id if not provided.", ge=0.1, le=0.4),
    additional_formats: list[_models.ExportOptions] | None = Field(None, description="List of additional output formats to generate alongside the default transcript. Each format can optionally include speaker labels and timestamps. Maximum of 10 formats per request.", max_length=10),
    cloud_storage_url: str | None = Field(None, description="HTTPS URL of the audio or video file to transcribe. The file must be publicly accessible and under 2GB. Supports cloud storage URLs (S3, Google Cloud Storage, Cloudflare R2) and pre-signed URLs with authentication tokens. Exactly one of file or cloud_storage_url must be provided."),
    webhook: bool | None = Field(None, description="Whether to process the request asynchronously and deliver results via configured webhooks. When enabled, the request returns immediately without the transcription result."),
    webhook_id: str | None = Field(None, description="ID of a specific webhook endpoint to receive the transcription result. Only valid when webhook is true. If omitted, results are sent to all configured speech-to-text webhooks."),
    use_multi_channel: bool | None = Field(None, description="Whether to transcribe multi-channel audio independently, treating each channel as a separate speaker. Supports up to 5 channels; each word in the response includes a channel_index field indicating its source channel."),
    webhook_metadata: str | dict[str, Any] | None = Field(None, description="Custom metadata to include in webhook responses for request correlation and tracking. Must be a JSON object with maximum depth of 2 levels and total size under 16KB. Useful for associating results with internal IDs or job references."),
    entity_detection: str | list[str] | None = Field(None, description="Entity detection configuration to identify and extract entities from the transcript. Accepts 'all' for all entity types, specific entity type names, or a list of types/categories (pii, phi, pci, other, offensive_language). Detected entities are returned with their text, type, and character positions. Incurs additional costs."),
    no_verbatim: bool | None = Field(None, description="Whether to remove filler words, false starts, and non-speech sounds from the transcript for a cleaner output. Only supported with the scribe_v2 model."),
    entity_redaction: str | list[str] | None = Field(None, description="Entity types or categories to redact from the transcript text. Accepts the same format as entity_detection ('all', specific categories like 'pii' or 'phi', or a list of entity types). Must be a subset of entity_detection if both are specified. When redaction is enabled, the entities field is not returned."),
    keyterms: list[str] | None = Field(None, description="List of domain-specific words or phrases to bias the model toward recognizing with higher accuracy. Each keyterm must be under 50 characters and contain at most 5 words. Maximum 1000 keyterms per request. Requests with over 100 keyterms incur a minimum 20-second billable duration. Incurs additional costs."),
) -> dict[str, Any]:
    """Transcribe audio or video files to text with support for speaker diarization, multi-channel processing, and entity detection. Supports synchronous responses or asynchronous webhook delivery with optional custom metadata for request tracking."""

    # Construct request model with validation
    try:
        _request = _models.SpeechToTextRequest(
            body=_models.SpeechToTextRequestBody(model_id=model_id, language_code=language_code, tag_audio_events=tag_audio_events, num_speakers=num_speakers, timestamps_granularity=timestamps_granularity, diarize=diarize, diarization_threshold=diarization_threshold, additional_formats=additional_formats, cloud_storage_url=cloud_storage_url, webhook=webhook, webhook_id=webhook_id, use_multi_channel=use_multi_channel, webhook_metadata=webhook_metadata, entity_detection=entity_detection, no_verbatim=no_verbatim, entity_redaction=entity_redaction, keyterms=keyterms)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for transcribe_audio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/speech-to-text"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("transcribe_audio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("transcribe_audio", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="transcribe_audio",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: speech-to-text
@mcp.tool()
async def get_transcript(transcription_id: str = Field(..., description="The unique identifier of the transcript to retrieve.")) -> dict[str, Any]:
    """Retrieve a previously generated transcript by its unique identifier. Use this operation to access transcription results after they have been processed."""

    # Construct request model with validation
    try:
        _request = _models.GetTranscriptByIdRequest(
            path=_models.GetTranscriptByIdRequestPath(transcription_id=transcription_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_transcript: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-text/transcripts/{transcription_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-text/transcripts/{transcription_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_transcript")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_transcript", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_transcript",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: speech-to-text
@mcp.tool()
async def delete_transcript(transcription_id: str = Field(..., description="The unique identifier of the transcript to delete.")) -> dict[str, Any]:
    """Permanently delete a transcript by its unique ID. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteTranscriptByIdRequest(
            path=_models.DeleteTranscriptByIdRequestPath(transcription_id=transcription_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_transcript: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-text/transcripts/{transcription_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-text/transcripts/{transcription_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_transcript")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_transcript", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_transcript",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def list_evaluation_criteria() -> dict[str, Any]:
    """Retrieve all available evaluation criteria for speech-to-text assessment. Use this to understand the metrics and standards available for evaluating transcription quality."""

    # Extract parameters for API call
    _http_path = "/v1/speech-to-text/evaluation/eval-criteria"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_evaluation_criteria")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_evaluation_criteria", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_evaluation_criteria",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def get_evaluation_criterion(criterion_id: str = Field(..., description="The unique identifier of the evaluation criterion to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific evaluation criterion by its ID for speech-to-text evaluation tasks. Use this to fetch detailed information about a criterion used in assessment workflows."""

    # Construct request model with validation
    try:
        _request = _models.GetEvalCriterionRouteRequest(
            path=_models.GetEvalCriterionRouteRequestPath(criterion_id=criterion_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_evaluation_criterion: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-text/evaluation/eval-criteria/{criterion_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-text/evaluation/eval-criteria/{criterion_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_evaluation_criterion")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_evaluation_criterion", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_evaluation_criterion",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def update_eval_criterion(
    criterion_id: str = Field(..., description="The unique identifier of the evaluation criterion to update."),
    fields: list[_models.DataExtractionFieldRequest] = Field(..., description="An array of field identifiers or definitions associated with this evaluation criterion. Specifies which fields are evaluated."),
    name: str | None = Field(None, description="The name of the evaluation criterion. Must be between 1 and 200 characters.", min_length=1, max_length=200),
    criteria: list[_models.CriterionItemRequest] | None = Field(None, description="An array of evaluation criteria details. Order and structure should match the evaluation framework requirements."),
) -> dict[str, Any]:
    """Update an existing evaluation criterion for speech-to-text assessment. Modify the criterion name, evaluation criteria details, and associated fields."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEvalCriterionRouteRequest(
            path=_models.UpdateEvalCriterionRouteRequestPath(criterion_id=criterion_id),
            body=_models.UpdateEvalCriterionRouteRequestBody(name=name, criteria=criteria,
                data_extraction_config=_models.UpdateEvalCriterionRouteRequestBodyDataExtractionConfig(fields=fields))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_eval_criterion: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-text/evaluation/eval-criteria/{criterion_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-text/evaluation/eval-criteria/{criterion_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_eval_criterion")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_eval_criterion", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_eval_criterion",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def delete_evaluation_criterion(criterion_id: str = Field(..., description="The unique identifier of the evaluation criterion to delete.")) -> dict[str, Any]:
    """Delete a specific evaluation criterion from the speech-to-text evaluation system. This operation permanently removes the criterion and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteEvalCriterionRouteRequest(
            path=_models.DeleteEvalCriterionRouteRequestPath(criterion_id=criterion_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_evaluation_criterion: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-text/evaluation/eval-criteria/{criterion_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-text/evaluation/eval-criteria/{criterion_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_evaluation_criterion")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_evaluation_criterion", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_evaluation_criterion",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def list_evaluations(
    agent_id: str | None = Field(None, description="Filter evaluations by the agent ID that created or is associated with the evaluation."),
    eval_criterion_id: str | None = Field(None, description="Filter evaluations by the evaluation criterion ID used to assess performance."),
    status: str | None = Field(None, description="Filter evaluations by their current status (e.g., pending, completed, failed)."),
    created_after: str | None = Field(None, description="Filter evaluations created on or after this date. Use ISO 8601 format."),
    created_before: str | None = Field(None, description="Filter evaluations created on or before this date. Use ISO 8601 format."),
    sort_by: str | None = Field(None, description="Sort results by a specific field (e.g., created_at, status, agent_id)."),
    sort_dir: str | None = Field(None, description="Sort direction for results: ascending or descending order."),
    page_size: int | None = Field(None, description="Number of evaluations to return per page for pagination."),
) -> dict[str, Any]:
    """Retrieve a list of speech-to-text evaluations with filtering, sorting, and pagination options. Filter by agent, evaluation criterion, status, and creation date range."""

    # Construct request model with validation
    try:
        _request = _models.ListEvaluationsRouteRequest(
            query=_models.ListEvaluationsRouteRequestQuery(agent_id=agent_id, eval_criterion_id=eval_criterion_id, status=status, created_after=created_after, created_before=created_before, sort_by=sort_by, sort_dir=sort_dir, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_evaluations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/speech-to-text/evaluation/evaluations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_evaluations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_evaluations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_evaluations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def create_evaluation(
    transcript_id: str = Field(..., description="The unique identifier of the transcript to be evaluated."),
    agent_id: str = Field(..., description="The unique identifier of the agent performing the evaluation."),
    eval_criterion_id: str = Field(..., description="The unique identifier of the evaluation criterion to apply during the evaluation."),
    labels: dict[str, str] | None = Field(None, description="Custom labels or metadata to attach to the evaluation as key-value pairs."),
    agent_name: str | None = Field(None, description="The display name of the agent performing the evaluation for reference purposes."),
) -> dict[str, Any]:
    """Trigger a new evaluation for a speech-to-text transcript by specifying the transcript, evaluating agent, and evaluation criteria. Optionally provide custom labels and agent name for context."""

    # Construct request model with validation
    try:
        _request = _models.TriggerEvaluationRouteRequest(
            body=_models.TriggerEvaluationRouteRequestBody(transcript_id=transcript_id, agent_id=agent_id, eval_criterion_id=eval_criterion_id, labels=labels, agent_name=agent_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_evaluation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/speech-to-text/evaluation/evaluations"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_evaluation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_evaluation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_evaluation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def get_evaluation(evaluation_id: str = Field(..., description="The unique identifier of the evaluation to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific speech-to-text evaluation by its unique identifier."""

    # Construct request model with validation
    try:
        _request = _models.GetEvaluationRouteRequest(
            path=_models.GetEvaluationRouteRequestPath(evaluation_id=evaluation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_evaluation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-text/evaluation/evaluations/{evaluation_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-text/evaluation/evaluations/{evaluation_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_evaluation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_evaluation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_evaluation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def list_human_agents(page_size: int | None = Field(None, description="Number of human agents to return per page. Controls pagination size for the results.")) -> dict[str, Any]:
    """Retrieve a paginated list of human agents available for speech-to-text evaluation tasks. Use pagination to control the number of results returned per request."""

    # Construct request model with validation
    try:
        _request = _models.ListHumanAgentsRouteRequest(
            query=_models.ListHumanAgentsRouteRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_human_agents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/speech-to-text/evaluation/human-agents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_human_agents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_human_agents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_human_agents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def get_human_agent(agent_id: str = Field(..., description="The unique identifier of the human agent to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific human agent in the speech-to-text evaluation system. Use this to access agent profiles and evaluation data."""

    # Construct request model with validation
    try:
        _request = _models.GetHumanAgentRouteRequest(
            path=_models.GetHumanAgentRouteRequestPath(agent_id=agent_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_human_agent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-text/evaluation/human-agents/{agent_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-text/evaluation/human-agents/{agent_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_human_agent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_human_agent", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_human_agent",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def delete_human_agent(agent_id: str = Field(..., description="The unique identifier of the human agent to delete.")) -> dict[str, Any]:
    """Remove a human agent from the speech-to-text evaluation system. This operation permanently deletes the agent and their associated routing configuration."""

    # Construct request model with validation
    try:
        _request = _models.DeleteHumanAgentRouteRequest(
            path=_models.DeleteHumanAgentRouteRequestPath(agent_id=agent_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_human_agent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-text/evaluation/human-agents/{agent_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-text/evaluation/human-agents/{agent_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_human_agent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_human_agent", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_human_agent",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def list_evaluation_analytics(
    created_after: str | None = Field(None, description="Filter results to include only evaluations created on or after this date. Specify in ISO 8601 format."),
    created_before: str | None = Field(None, description="Filter results to include only evaluations created on or before this date. Specify in ISO 8601 format."),
) -> dict[str, Any]:
    """Retrieve analytics data for speech-to-text evaluations, optionally filtered by creation date range. Use this to analyze evaluation metrics and performance trends over time."""

    # Construct request model with validation
    try:
        _request = _models.GetEvaluationAnalyticsRouteRequest(
            query=_models.GetEvaluationAnalyticsRouteRequestQuery(created_after=created_after, created_before=created_before)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_evaluation_analytics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/speech-to-text/evaluation/analytics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_evaluation_analytics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_evaluation_analytics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_evaluation_analytics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def get_criterion_analytics(
    criterion_id: str = Field(..., description="The unique identifier of the evaluation criterion to retrieve analytics for."),
    created_after: str | None = Field(None, description="Filter analytics to include only records created on or after this date. Specify in ISO 8601 format."),
    created_before: str | None = Field(None, description="Filter analytics to include only records created on or before this date. Specify in ISO 8601 format."),
) -> dict[str, Any]:
    """Retrieve analytics data for a specific evaluation criterion, with optional filtering by creation date range. Use this to analyze performance metrics and insights for a particular criterion."""

    # Construct request model with validation
    try:
        _request = _models.GetCriterionAnalyticsRouteRequest(
            path=_models.GetCriterionAnalyticsRouteRequestPath(criterion_id=criterion_id),
            query=_models.GetCriterionAnalyticsRouteRequestQuery(created_after=created_after, created_before=created_before)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_criterion_analytics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-text/evaluation/eval-criteria/{criterion_id}/analytics", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-text/evaluation/eval-criteria/{criterion_id}/analytics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_criterion_analytics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_criterion_analytics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_criterion_analytics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Speech To Text - Evaluation
@mcp.tool()
async def get_agent_analytics(
    agent_id: str = Field(..., description="The unique identifier of the human agent for which to retrieve analytics."),
    created_after: str | None = Field(None, description="Filter to include only analytics created on or after this date. Specify in ISO 8601 format."),
    created_before: str | None = Field(None, description="Filter to include only analytics created on or before this date. Specify in ISO 8601 format."),
) -> dict[str, Any]:
    """Retrieve analytics data for a specific human agent in the speech-to-text evaluation system. Optionally filter results by creation date range."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentAnalyticsRouteRequest(
            path=_models.GetAgentAnalyticsRouteRequestPath(agent_id=agent_id),
            query=_models.GetAgentAnalyticsRouteRequestQuery(created_after=created_after, created_before=created_before)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_agent_analytics: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/speech-to-text/evaluation/human-agents/{agent_id}/analytics", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/speech-to-text/evaluation/human-agents/{agent_id}/analytics"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_agent_analytics")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_agent_analytics", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_agent_analytics",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: forced-alignment
@mcp.tool()
async def align_audio_to_text(
    file_: str = Field(..., alias="file", description="The audio file to align with the transcript. Supports all major audio formats with a maximum file size of 1GB."),
    text: str = Field(..., description="The text transcript to align with the audio. Can be in any text format; diarization (speaker identification) is not currently supported."),
    enabled_spooled_file: bool | None = Field(None, description="Enable streaming processing for large files that cannot fit in memory. When true, the file is streamed to the server and processed in chunks."),
) -> dict[str, Any]:
    """Synchronize an audio file with a text transcript to extract precise timing information for each character and word. Supports all major audio formats up to 1GB in size."""

    # Construct request model with validation
    try:
        _request = _models.ForcedAlignmentRequest(
            body=_models.ForcedAlignmentRequestBody(file_=file_, text=text, enabled_spooled_file=enabled_spooled_file)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for align_audio_to_text: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/forced-alignment"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("align_audio_to_text")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("align_audio_to_text", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="align_audio_to_text",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_agent_conversation_signed_link(
    agent_id: str = Field(..., description="The unique identifier of the agent with which to start the conversation."),
    include_conversation_id: bool | None = Field(None, description="Whether to include a unique conversation ID in the response. When enabled, the signed URL can only be used once."),
    branch_id: str | None = Field(None, description="The specific branch variant of the agent to use for the conversation."),
) -> dict[str, Any]:
    """Generate a signed URL to initiate a conversation with an authorized agent. The signed URL provides secure access to start a new conversation session."""

    # Construct request model with validation
    try:
        _request = _models.GetConversationSignedLinkRequest(
            query=_models.GetConversationSignedLinkRequestQuery(agent_id=agent_id, include_conversation_id=include_conversation_id, branch_id=branch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_agent_conversation_signed_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/conversation/get-signed-url"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_agent_conversation_signed_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_agent_conversation_signed_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_agent_conversation_signed_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def initiate_outbound_call(
    agent_id: str = Field(..., description="Unique identifier of the AI agent that will handle the call."),
    agent_phone_number_id: str = Field(..., description="Identifier of the Twilio phone number resource to use as the caller."),
    to_number: str = Field(..., description="The destination phone number to call in E.164 format or standard phone number format."),
    soft_timeout_config: dict[str, Any] | None = Field(None, description="Configuration for soft timeout feedback, allowing the agent to provide immediate responses (e.g., acknowledgments) while processing longer LLM responses."),
    voice_id: str | None = Field(None, description="Identifier for the text-to-speech voice to use for agent responses."),
    stability: float | None = Field(None, description="Controls the consistency of the generated speech, with higher values producing more stable output."),
    speed: float | None = Field(None, description="Controls the playback speed of generated speech, where higher values increase speech rate."),
    similarity_boost: float | None = Field(None, description="Controls how closely the generated speech matches the target voice characteristics."),
    first_message: str | None = Field(None, description="Optional initial message the agent will speak when the call connects. If omitted, the agent waits for the caller to speak first."),
    language: str | None = Field(None, description="Language code for the agent's automatic speech recognition and text-to-speech processing."),
    prompt: dict[str, Any] | None = Field(None, description="Configuration object specifying the LLM model and system prompt that defines the agent's behavior and knowledge."),
    user_id: str | None = Field(None, description="Identifier for the end user or customer participating in this call, used for tracking and attribution by the agent owner."),
    source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(None, description="The platform or integration through which the call was initiated."),
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(None, description="Key-value pairs of custom variables that can be referenced in the agent's prompt or system instructions to personalize the conversation."),
    call_recording_enabled: bool | None = Field(None, description="Whether Twilio should record the audio of this call for compliance, quality assurance, or archival purposes."),
) -> dict[str, Any]:
    """Initiate an outbound phone call through Twilio with AI agent capabilities, including voice synthesis, language support, and optional call recording."""

    # Construct request model with validation
    try:
        _request = _models.HandleTwilioOutboundCallRequest(
            body=_models.HandleTwilioOutboundCallRequestBody(agent_id=agent_id, agent_phone_number_id=agent_phone_number_id, to_number=to_number, call_recording_enabled=call_recording_enabled,
                conversation_initiation_client_data=_models.HandleTwilioOutboundCallRequestBodyConversationInitiationClientData(user_id=user_id, dynamic_variables=dynamic_variables,
                    conversation_config_override=_models.HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverride(turn=_models.HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn(soft_timeout_config=soft_timeout_config) if any(v is not None for v in [soft_timeout_config]) else None,
                        tts=_models.HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts(voice_id=voice_id, stability=stability, speed=speed, similarity_boost=similarity_boost) if any(v is not None for v in [voice_id, stability, speed, similarity_boost]) else None,
                        agent=_models.HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent(first_message=first_message, language=language, prompt=prompt) if any(v is not None for v in [first_message, language, prompt]) else None) if any(v is not None for v in [soft_timeout_config, voice_id, stability, speed, similarity_boost, first_message, language, prompt]) else None,
                    source_info=_models.HandleTwilioOutboundCallRequestBodyConversationInitiationClientDataSourceInfo(source=source) if any(v is not None for v in [source]) else None) if any(v is not None for v in [soft_timeout_config, voice_id, stability, speed, similarity_boost, first_message, language, prompt, user_id, source, dynamic_variables]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for initiate_outbound_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/twilio/outbound-call"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("initiate_outbound_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("initiate_outbound_call", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="initiate_outbound_call",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def initiate_twilio_call(
    agent_id: str = Field(..., description="Unique identifier of the AI agent that will handle this call."),
    from_number: str = Field(..., description="The phone number initiating the call (caller ID for outbound, destination for inbound)."),
    to_number: str = Field(..., description="The phone number receiving the call (destination for outbound, caller ID for inbound)."),
    direction: Literal["inbound", "outbound"] | None = Field(None, description="Direction of the call flow. Inbound calls originate from external parties; outbound calls are initiated by the system."),
    soft_timeout_config: dict[str, Any] | None = Field(None, description="Configuration for soft timeout feedback, allowing the agent to provide immediate acknowledgment messages while processing longer LLM responses."),
    voice_id: str | None = Field(None, description="Identifier for the text-to-speech voice model to use for agent responses."),
    stability: float | None = Field(None, description="Controls the consistency of generated speech output, affecting how natural and varied the voice sounds."),
    speed: float | None = Field(None, description="Controls the playback speed of generated speech, where higher values increase speech rate."),
    similarity_boost: float | None = Field(None, description="Controls how closely the generated speech matches the target voice characteristics."),
    first_message: str | None = Field(None, description="Opening message the agent will speak when the call connects. If empty, the agent waits for the caller to speak first."),
    language: str | None = Field(None, description="Language code for automatic speech recognition (ASR) and text-to-speech (TTS) processing during the call."),
    prompt: dict[str, Any] | None = Field(None, description="Configuration object containing the LLM model identifier and system prompt that defines the agent's behavior and knowledge domain."),
    user_id: str | None = Field(None, description="Identifier for the end user or customer participating in this call, used by the agent owner for tracking and analytics."),
    source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(None, description="Channel or platform through which this call was initiated, used for analytics and routing decisions."),
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(None, description="Custom key-value variables that can be passed to the agent prompt for dynamic personalization or context injection during the conversation."),
) -> dict[str, Any]:
    """Initiate a Twilio voice call with an AI agent and return TwiML configuration for call routing. Supports both inbound and outbound call directions with customizable agent behavior, voice settings, and conversation parameters."""

    # Construct request model with validation
    try:
        _request = _models.RegisterTwilioCallRequest(
            body=_models.RegisterTwilioCallRequestBody(agent_id=agent_id, from_number=from_number, to_number=to_number, direction=direction,
                conversation_initiation_client_data=_models.RegisterTwilioCallRequestBodyConversationInitiationClientData(user_id=user_id, dynamic_variables=dynamic_variables,
                    conversation_config_override=_models.RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverride(turn=_models.RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn(soft_timeout_config=soft_timeout_config) if any(v is not None for v in [soft_timeout_config]) else None,
                        tts=_models.RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts(voice_id=voice_id, stability=stability, speed=speed, similarity_boost=similarity_boost) if any(v is not None for v in [voice_id, stability, speed, similarity_boost]) else None,
                        agent=_models.RegisterTwilioCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent(first_message=first_message, language=language, prompt=prompt) if any(v is not None for v in [first_message, language, prompt]) else None) if any(v is not None for v in [soft_timeout_config, voice_id, stability, speed, similarity_boost, first_message, language, prompt]) else None,
                    source_info=_models.RegisterTwilioCallRequestBodyConversationInitiationClientDataSourceInfo(source=source) if any(v is not None for v in [source]) else None) if any(v is not None for v in [soft_timeout_config, voice_id, stability, speed, similarity_boost, first_message, language, prompt, user_id, source, dynamic_variables]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for initiate_twilio_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/twilio/register-call"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("initiate_twilio_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("initiate_twilio_call", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="initiate_twilio_call",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def initiate_whatsapp_call(
    whatsapp_phone_number_id: str = Field(..., description="The WhatsApp Business Account phone number ID that will be used to make the outbound call."),
    whatsapp_user_id: str = Field(..., description="The WhatsApp user ID of the recipient who will receive the outbound call."),
    whatsapp_call_permission_request_template_name: str = Field(..., description="The name of the WhatsApp-approved call permission request template to use for initiating the call."),
    whatsapp_call_permission_request_template_language_code: str = Field(..., description="The language code of the call permission request template (e.g., 'en_US', 'es_ES')."),
    agent_id: str = Field(..., description="The ID of the AI agent that will handle the conversation during the call."),
    soft_timeout_config: dict[str, Any] | None = Field(None, description="Configuration for soft timeout feedback, allowing the agent to send intermediate messages while processing longer LLM responses to keep the conversation feeling responsive."),
    voice_id: str | None = Field(None, description="The voice ID to use for text-to-speech synthesis during the call."),
    stability: float | None = Field(None, description="The stability parameter for speech synthesis, controlling consistency of the generated voice."),
    speed: float | None = Field(None, description="The speed parameter for speech synthesis, controlling how fast the agent speaks."),
    similarity_boost: float | None = Field(None, description="The similarity boost parameter for speech synthesis, controlling how closely the voice matches the selected voice ID."),
    first_message: str | None = Field(None, description="The initial message the agent will speak when the call connects. If empty, the agent will wait for the user to speak first."),
    language: str | None = Field(None, description="The language code for the agent's automatic speech recognition and text-to-speech (e.g., 'en-US', 'es-ES')."),
    prompt: dict[str, Any] | None = Field(None, description="The system prompt that defines the agent's behavior, personality, and instructions for handling the conversation."),
    user_id: str | None = Field(None, description="The ID of the end user initiating this call, used by the agent owner for tracking and identifying conversation participants."),
    source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(None, description="The source or channel through which the call was initiated."),
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(None, description="Dynamic variables that can be passed to customize the agent's behavior and responses during the call."),
) -> dict[str, Any]:
    """Initiate an outbound voice call to a WhatsApp user through a configured WhatsApp Business Account. The call uses a pre-approved permission request template and connects to an AI agent for conversation."""

    # Construct request model with validation
    try:
        _request = _models.WhatsappOutboundCallRequest(
            body=_models.WhatsappOutboundCallRequestBody(whatsapp_phone_number_id=whatsapp_phone_number_id, whatsapp_user_id=whatsapp_user_id, whatsapp_call_permission_request_template_name=whatsapp_call_permission_request_template_name, whatsapp_call_permission_request_template_language_code=whatsapp_call_permission_request_template_language_code, agent_id=agent_id,
                conversation_initiation_client_data=_models.WhatsappOutboundCallRequestBodyConversationInitiationClientData(user_id=user_id, dynamic_variables=dynamic_variables,
                    conversation_config_override=_models.WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverride(turn=_models.WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn(soft_timeout_config=soft_timeout_config) if any(v is not None for v in [soft_timeout_config]) else None,
                        tts=_models.WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts(voice_id=voice_id, stability=stability, speed=speed, similarity_boost=similarity_boost) if any(v is not None for v in [voice_id, stability, speed, similarity_boost]) else None,
                        agent=_models.WhatsappOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent(first_message=first_message, language=language, prompt=prompt) if any(v is not None for v in [first_message, language, prompt]) else None) if any(v is not None for v in [soft_timeout_config, voice_id, stability, speed, similarity_boost, first_message, language, prompt]) else None,
                    source_info=_models.WhatsappOutboundCallRequestBodyConversationInitiationClientDataSourceInfo(source=source) if any(v is not None for v in [source]) else None) if any(v is not None for v in [soft_timeout_config, voice_id, stability, speed, similarity_boost, first_message, language, prompt, user_id, source, dynamic_variables]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for initiate_whatsapp_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/whatsapp/outbound-call"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("initiate_whatsapp_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("initiate_whatsapp_call", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="initiate_whatsapp_call",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def send_whatsapp_message(
    whatsapp_phone_number_id: str = Field(..., description="The WhatsApp phone number ID associated with your business account that will send the message."),
    whatsapp_user_id: str = Field(..., description="The WhatsApp user ID (recipient) who will receive the message."),
    template_name: str = Field(..., description="The name of the WhatsApp message template to use for this outbound message."),
    template_language_code: str = Field(..., description="The language code for the template (e.g., 'en', 'es', 'fr'). Must match the template's supported languages."),
    template_params: list[_models.WhatsAppTemplateHeaderComponentParams | _models.WhatsAppTemplateBodyComponentParams | _models.WhatsAppTemplateButtonComponentParams] = Field(..., description="An ordered array of parameter values to substitute into the template placeholders. Order and format must match the template definition."),
    agent_id: str = Field(..., description="The ID of the AI agent that will handle the conversation if this message initiates an interactive session."),
    soft_timeout_config: dict[str, Any] | None = Field(None, description="Configuration for soft timeout feedback, allowing the agent to send intermediate messages (e.g., acknowledgments) while processing longer responses."),
    voice_id: str | None = Field(None, description="The voice ID to use for text-to-speech synthesis when the agent responds with audio."),
    stability: float | None = Field(None, description="Controls the consistency of the generated speech, ranging from low variability to high variability."),
    speed: float | None = Field(None, description="Controls the speed of generated speech playback."),
    similarity_boost: float | None = Field(None, description="Controls how closely the generated speech matches the selected voice characteristics."),
    first_message: str | None = Field(None, description="The initial message the agent will send to start the conversation. If empty, the agent waits for the user to send the first message."),
    language: str | None = Field(None, description="The language for the agent's automatic speech recognition (ASR) and text-to-speech (TTS) processing."),
    prompt: dict[str, Any] | None = Field(None, description="Configuration object containing the LLM model and system prompt that defines the agent's behavior and capabilities."),
    user_id: str | None = Field(None, description="Identifier for the end user participating in this conversation, used by the agent owner for tracking and analytics."),
    source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(None, description="The channel or platform through which this conversation was initiated."),
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(None, description="Additional dynamic variables to be substituted into the template or used by the agent during the conversation."),
) -> dict[str, Any]:
    """Send an outbound message to a WhatsApp user using a predefined template with optional AI agent configuration for interactive conversations."""

    # Construct request model with validation
    try:
        _request = _models.WhatsappOutboundMessageRequest(
            body=_models.WhatsappOutboundMessageRequestBody(whatsapp_phone_number_id=whatsapp_phone_number_id, whatsapp_user_id=whatsapp_user_id, template_name=template_name, template_language_code=template_language_code, template_params=template_params, agent_id=agent_id,
                conversation_initiation_client_data=_models.WhatsappOutboundMessageRequestBodyConversationInitiationClientData(user_id=user_id, dynamic_variables=dynamic_variables,
                    conversation_config_override=_models.WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverride(turn=_models.WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn(soft_timeout_config=soft_timeout_config) if any(v is not None for v in [soft_timeout_config]) else None,
                        tts=_models.WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverrideTts(voice_id=voice_id, stability=stability, speed=speed, similarity_boost=similarity_boost) if any(v is not None for v in [voice_id, stability, speed, similarity_boost]) else None,
                        agent=_models.WhatsappOutboundMessageRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent(first_message=first_message, language=language, prompt=prompt) if any(v is not None for v in [first_message, language, prompt]) else None) if any(v is not None for v in [soft_timeout_config, voice_id, stability, speed, similarity_boost, first_message, language, prompt]) else None,
                    source_info=_models.WhatsappOutboundMessageRequestBodyConversationInitiationClientDataSourceInfo(source=source) if any(v is not None for v in [source]) else None) if any(v is not None for v in [soft_timeout_config, voice_id, stability, speed, similarity_boost, first_message, language, prompt, user_id, source, dynamic_variables]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for send_whatsapp_message: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/whatsapp/outbound-message"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("send_whatsapp_message")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("send_whatsapp_message", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="send_whatsapp_message",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def create_agent_route(
    name: str | None = Field(None, description="A name to make the agent easier to find"),
    tags: list[str] | None = Field(None, description="Tags to help classify and filter the agent"),
    platform_settings: _models.CreateAgentRouteBodyPlatformSettings | None = Field(None, description="Platform settings including widget config, auth, privacy, guardrails, and evaluation"),
    conversation_config: _models.CreateAgentRouteBodyConversationConfig | None = Field(None, description="Conversation configuration including ASR, TTS, turn handling, and agent prompt settings"),
    workflow: _models.CreateAgentRouteBodyWorkflow | None = Field(None, description="Workflow definition with nodes and edges"),
) -> dict[str, Any]:
    """Create Agent"""

    # Construct request model with validation
    try:
        _request = _models.CreateAgentRouteRequest(
            body=_models.CreateAgentRouteRequestBody(name=name, tags=tags, platform_settings=platform_settings, conversation_config=conversation_config, workflow=workflow)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_agent_route: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/agents/create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_agent_route")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_agent_route", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_agent_route",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_agent_summaries(agent_ids: list[str] = Field(..., description="List of agent IDs to retrieve summaries for. Order is not significant. Each ID should be a valid agent identifier.")) -> dict[str, Any]:
    """Retrieve summaries for the specified agents. Provide a list of agent IDs to get their summary information."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentSummariesRouteRequest(
            query=_models.GetAgentSummariesRouteRequestQuery(agent_ids=agent_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_agent_summaries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/agents/summaries"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_agent_summaries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_agent_summaries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_agent_summaries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_agent(
    agent_id: str = Field(..., description="The unique identifier of the agent to retrieve."),
    version_id: str | None = Field(None, description="The specific version of the agent to retrieve. If not provided, the latest version is used."),
    branch_id: str | None = Field(None, description="The specific branch of the agent to retrieve. If not provided, the default branch is used."),
) -> dict[str, Any]:
    """Retrieve the configuration and settings for a specific agent. Optionally specify a particular version or branch to retrieve."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentRouteRequest(
            path=_models.GetAgentRouteRequestPath(agent_id=agent_id),
            query=_models.GetAgentRouteRequestQuery(version_id=version_id, branch_id=branch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_agent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_agent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_agent", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_agent",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def update_agent_settings(
    agent_id: str = Field(..., description="The unique identifier of the agent to update."),
    enable_versioning_if_not_enabled: bool | None = Field(None, description="Automatically enable versioning for this agent if not already enabled, allowing you to track and manage configuration changes."),
    branch_id: str | None = Field(None, description="The branch identifier to target for updates. If not specified, updates apply to the main agent configuration."),
    conversation_config: dict[str, Any] | None = Field(None, description="Configuration settings that control conversation behavior, orchestration, and interaction patterns."),
    platform_settings: dict[str, Any] | None = Field(None, description="Platform-level settings for deployment, integrations, and non-conversation features."),
    edges: dict[str, _models.WorkflowEdgeModelInput] | None = Field(None, description="Workflow edges defining connections and transitions between nodes in the agent's conversation flow."),
    nodes: dict[str, _models.WorkflowStartNodeModelInput | _models.WorkflowEndNodeModelInput | _models.WorkflowPhoneNumberNodeModelInput | _models.WorkflowOverrideAgentNodeModelInput | _models.WorkflowStandaloneAgentNodeModelInput | _models.WorkflowToolNodeModelInput] | None = Field(None, description="Workflow nodes representing conversation states, actions, or processing steps in the agent's logic.", min_length=1),
    name: str | None = Field(None, description="A human-readable name for the agent to improve discoverability and organization."),
    tags: list[str] | None = Field(None, description="Classification tags for organizing and filtering agents by category or function."),
    version_description: str | None = Field(None, description="A description of the changes in this version, used when publishing updates to versioned agents."),
) -> dict[str, Any]:
    """Updates agent settings including conversation configuration, platform settings, workflow structure, metadata, and versioning. Changes are applied to the specified agent or branch."""

    # Construct request model with validation
    try:
        _request = _models.PatchAgentSettingsRouteRequest(
            path=_models.PatchAgentSettingsRouteRequestPath(agent_id=agent_id),
            query=_models.PatchAgentSettingsRouteRequestQuery(enable_versioning_if_not_enabled=enable_versioning_if_not_enabled, branch_id=branch_id),
            body=_models.PatchAgentSettingsRouteRequestBody(conversation_config=conversation_config, platform_settings=platform_settings, name=name, tags=tags, version_description=version_description,
                workflow=_models.PatchAgentSettingsRouteRequestBodyWorkflow(edges=edges, nodes=nodes) if any(v is not None for v in [edges, nodes]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_agent_settings: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_agent_settings")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_agent_settings", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_agent_settings",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_agent(agent_id: str = Field(..., description="The unique identifier of the agent to delete.")) -> dict[str, Any]:
    """Permanently delete an agent and remove it from the system. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAgentRouteRequest(
            path=_models.DeleteAgentRouteRequestPath(agent_id=agent_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_agent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_agent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_agent", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_agent",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_agent_widget_config(
    agent_id: str = Field(..., description="The unique identifier of the agent whose widget configuration you want to retrieve."),
    conversation_signature: str | None = Field(None, description="An optional expiring token that enables WebSocket conversation initiation. Generate tokens using the conversation signed URL endpoint."),
) -> dict[str, Any]:
    """Retrieve the widget configuration for a specific agent, including settings needed to embed or display the agent's conversational interface."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentWidgetRouteRequest(
            path=_models.GetAgentWidgetRouteRequestPath(agent_id=agent_id),
            query=_models.GetAgentWidgetRouteRequestQuery(conversation_signature=conversation_signature)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_agent_widget_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/widget", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/widget"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_agent_widget_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_agent_widget_config", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_agent_widget_config",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_agent_share_link(agent_id: str = Field(..., description="The unique identifier of the agent for which to retrieve the share link.")) -> dict[str, Any]:
    """Retrieve the shareable link for an agent that can be used to share the agent with others."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentLinkRouteRequest(
            path=_models.GetAgentLinkRouteRequestPath(agent_id=agent_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_agent_share_link: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/link", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/link"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_agent_share_link")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_agent_share_link", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_agent_share_link",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def upload_agent_avatar(
    agent_id: str = Field(..., description="The unique identifier of the agent to update with the new avatar image."),
    avatar_file: str = Field(..., description="An image file to use as the agent's avatar. The file will be processed and stored for display in the widget."),
) -> dict[str, Any]:
    """Upload and set a profile image for an agent that will be displayed in the chat widget."""

    # Construct request model with validation
    try:
        _request = _models.PostAgentAvatarRouteRequest(
            path=_models.PostAgentAvatarRouteRequestPath(agent_id=agent_id),
            body=_models.PostAgentAvatarRouteRequestBody(avatar_file=avatar_file)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_agent_avatar: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/avatar", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/avatar"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_agent_avatar")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_agent_avatar", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_agent_avatar",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_agents(
    page_size: int | None = Field(None, description="Maximum number of agents to return per request. Must be between 1 and 100.", ge=1, le=100),
    archived: bool | None = Field(None, description="Filter results to show only archived or active agents."),
    created_by_user_id: str | None = Field(None, description="Filter agents by the user ID of their creator. Use '@me' to refer to the authenticated user. Takes precedence over other ownership filters."),
    sort_direction: Literal["asc", "desc"] | None = Field(None, description="Order direction for sorting results in ascending or descending sequence."),
    sort_by: Literal["name", "created_at"] | None = Field(None, description="Field to sort results by. Choose between agent name or creation timestamp."),
) -> dict[str, Any]:
    """Retrieve a paginated list of your agents with their metadata. Results can be filtered by archived status and creator, and sorted by name or creation date."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentsRouteRequest(
            query=_models.GetAgentsRouteRequestQuery(page_size=page_size, archived=archived, created_by_user_id=created_by_user_id, sort_direction=sort_direction, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_agents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/agents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_agents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_agents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_agents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_knowledge_base_size(agent_id: str = Field(..., description="The unique identifier of the agent whose knowledge base size you want to retrieve.")) -> dict[str, Any]:
    """Retrieves the total number of pages stored in an agent's knowledge base. Use this to understand the size and scope of the knowledge base associated with a specific agent."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentKnowledgeBaseSizeRequest(
            path=_models.GetAgentKnowledgeBaseSizeRequestPath(agent_id=agent_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_knowledge_base_size: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agent/{agent_id}/knowledge-base/size", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agent/{agent_id}/knowledge-base/size"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_knowledge_base_size")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_knowledge_base_size", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_knowledge_base_size",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def estimate_agent_llm_cost(
    agent_id: str = Field(..., description="The unique identifier of the agent for which to calculate expected LLM token usage."),
    prompt_length: int | None = Field(None, description="The length of the input prompt in characters. Used to estimate token consumption for the prompt component."),
    number_of_pages: int | None = Field(None, description="The total number of pages in PDF documents or URLs indexed in the agent's Knowledge Base. Used to estimate token consumption for RAG retrieval and context injection."),
    rag_enabled: bool | None = Field(None, description="Whether Retrieval-Augmented Generation (RAG) is enabled for the agent. When enabled, additional tokens are consumed for knowledge base retrieval and context augmentation."),
) -> dict[str, Any]:
    """Estimates the expected number of LLM tokens required for an agent based on prompt length, knowledge base content, and RAG configuration. Use this to forecast token consumption and associated costs before deployment."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentLlmExpectedCostCalculationRequest(
            path=_models.GetAgentLlmExpectedCostCalculationRequestPath(agent_id=agent_id),
            body=_models.GetAgentLlmExpectedCostCalculationRequestBody(prompt_length=prompt_length, number_of_pages=number_of_pages, rag_enabled=rag_enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for estimate_agent_llm_cost: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agent/{agent_id}/llm-usage/calculate", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agent/{agent_id}/llm-usage/calculate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("estimate_agent_llm_cost")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("estimate_agent_llm_cost", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="estimate_agent_llm_cost",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def duplicate_agent(
    agent_id: str = Field(..., description="The unique identifier of the agent to duplicate."),
    name: str | None = Field(None, description="An optional custom name for the duplicated agent to help identify it."),
) -> dict[str, Any]:
    """Create a new agent by duplicating an existing agent. The new agent will have the same configuration as the source agent, with an optional custom name."""

    # Construct request model with validation
    try:
        _request = _models.DuplicateAgentRouteRequest(
            path=_models.DuplicateAgentRouteRequestPath(agent_id=agent_id),
            body=_models.DuplicateAgentRouteRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for duplicate_agent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/duplicate", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/duplicate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("duplicate_agent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("duplicate_agent", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="duplicate_agent",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def simulate_agent_conversation(
    agent_id: str = Field(..., description="The unique identifier of the agent to simulate. This ID is provided when the agent is created."),
    first_message: str | None = Field(None, description="Optional opening message for the agent to deliver. If provided, the agent speaks first; if empty, the simulated user initiates the conversation."),
    language: str | None = Field(None, description="Language code for the agent's speech recognition and text-to-speech capabilities."),
    hinglish_mode: bool | None = Field(None, description="Enable Hinglish (Hindi-English mix) responses when language is set to Hindi."),
    disable_first_message_interruptions: bool | None = Field(None, description="Prevent the simulated user from interrupting the agent while the first message is being delivered."),
    prompt: str | None = Field(None, description="System prompt that guides the agent's behavior, personality, and response style."),
    llm: Literal["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.2-chat-latest", "gpt-5-mini", "gpt-5-nano", "gpt-3.5-turbo", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "claude-sonnet-4-5", "claude-sonnet-4-6", "claude-sonnet-4", "claude-haiku-4-5", "claude-3-7-sonnet", "claude-3-5-sonnet", "claude-3-5-sonnet-v1", "claude-3-haiku", "grok-beta", "custom-llm", "qwen3-4b", "qwen3-30b-a3b", "gpt-oss-20b", "gpt-oss-120b", "glm-45-air-fp8", "gemini-2.5-flash-preview-09-2025", "gemini-2.5-flash-lite-preview-09-2025", "gemini-2.5-flash-preview-05-20", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-lite-preview-06-17", "gemini-2.0-flash-lite-001", "gemini-2.0-flash-001", "gemini-1.5-flash-002", "gemini-1.5-flash-001", "gemini-1.5-pro-002", "gemini-1.5-pro-001", "claude-sonnet-4@20250514", "claude-sonnet-4-5@20250929", "claude-haiku-4-5@20251001", "claude-3-7-sonnet@20250219", "claude-3-5-sonnet@20240620", "claude-3-5-sonnet-v2@20241022", "claude-3-haiku@20240307", "gpt-5-2025-08-07", "gpt-5.1-2025-11-13", "gpt-5.2-2025-12-11", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-0613", "gpt-4-0314", "gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "watt-tool-8b", "watt-tool-70b"] | None = Field(None, description="The language model to use for generating agent responses. Ensure the selected model is supported in your data residency environment if applicable."),
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] | None = Field(None, description="Control the model's reasoning depth. Higher effort levels enable more complex reasoning but may increase latency. Only supported by certain models."),
    thinking_budget: int | None = Field(None, description="Maximum number of tokens allocated for the model's internal reasoning process. Set to 0 to disable thinking if the model supports it."),
    max_tokens: int | None = Field(None, description="Maximum number of tokens the model can generate in its response. Use -1 for unlimited tokens (respects model defaults)."),
    built_in_tools: dict[str, Any] | None = Field(None, description="System tools available to the agent during the conversation, such as web search, calculator, or database lookup."),
    native_mcp_server_ids: list[str] | None = Field(None, description="List of Native MCP (Model Context Protocol) server IDs that provide additional capabilities and integrations to the agent.", max_length=10),
    knowledge_base: list[_models.KnowledgeBaseLocator] | None = Field(None, description="Knowledge bases the agent can reference to retrieve relevant information and context during conversations."),
    custom_llm: dict[str, Any] | None = Field(None, description="Custom LLM configuration details when using a proprietary or self-hosted language model. Required if llm is set to 'custom-llm'."),
    ignore_default_personality: bool | None = Field(None, description="Exclude the default personality and behavioral guidelines from the system prompt, allowing full control via the custom prompt parameter."),
    rag: dict[str, Any] | None = Field(None, description="Retrieval-Augmented Generation (RAG) settings to enable the agent to search and cite information from external sources."),
    timezone_: str | None = Field(None, alias="timezone", description="Timezone for displaying the current time in the system prompt. Use standard timezone identifiers to ensure accurate time context in agent responses."),
    backup_llm_config: _models.BackupLlmDefault | _models.BackupLlmDisabled | _models.BackupLlmOverride | None = Field(None, description="Fallback LLM configuration for automatic cascading if the primary model fails or times out. Can be disabled, use system defaults, or specify a custom priority order."),
    cascade_timeout_seconds: float | None = Field(None, description="Time in seconds to wait before cascading to a backup LLM if the primary model does not respond.", ge=2.0, le=15.0),
    tool_mock_config: dict[str, _models.ToolMockConfig] | None = Field(None, description="Mock configurations for tools to simulate tool responses without making actual external calls."),
    partial_conversation_history: list[_models.ConversationHistoryTranscriptCommonModelInput] | None = Field(None, description="Pre-existing conversation history to resume from. Allows testing agent behavior in the context of an ongoing conversation rather than starting fresh."),
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(None, description="Dynamic variables to inject into the prompt and conversation context, enabling parameterized testing scenarios."),
    extra_evaluation_criteria: list[_models.PromptEvaluationCriteria] | None = Field(None, description="Custom evaluation criteria to assess agent performance during the simulation, such as response quality, accuracy, or adherence to guidelines."),
    new_turns_limit: int | None = Field(None, description="Maximum number of conversation turns to generate in the simulation. Prevents excessively long simulations."),
) -> dict[str, Any]:
    """Simulate a conversation between an AI agent and a simulated user to test agent behavior, responses, and conversation flow. Useful for validating agent configurations, prompts, and tool integrations before deployment."""

    # Construct request model with validation
    try:
        _request = _models.RunConversationSimulationRouteRequest(
            path=_models.RunConversationSimulationRouteRequestPath(agent_id=agent_id),
            body=_models.RunConversationSimulationRouteRequestBody(extra_evaluation_criteria=extra_evaluation_criteria, new_turns_limit=new_turns_limit,
                simulation_specification=_models.RunConversationSimulationRouteRequestBodySimulationSpecification(tool_mock_config=tool_mock_config, partial_conversation_history=partial_conversation_history, dynamic_variables=dynamic_variables,
                    simulated_user_config=_models.RunConversationSimulationRouteRequestBodySimulationSpecificationSimulatedUserConfig(first_message=first_message, language=language, hinglish_mode=hinglish_mode, disable_first_message_interruptions=disable_first_message_interruptions,
                        prompt=_models.RunConversationSimulationRouteRequestBodySimulationSpecificationSimulatedUserConfigPrompt(prompt=prompt, llm=llm, reasoning_effort=reasoning_effort, thinking_budget=thinking_budget, max_tokens=max_tokens, built_in_tools=built_in_tools, native_mcp_server_ids=native_mcp_server_ids, knowledge_base=knowledge_base, custom_llm=custom_llm, ignore_default_personality=ignore_default_personality, rag=rag, timezone_=timezone_, backup_llm_config=backup_llm_config, cascade_timeout_seconds=cascade_timeout_seconds) if any(v is not None for v in [prompt, llm, reasoning_effort, thinking_budget, max_tokens, built_in_tools, native_mcp_server_ids, knowledge_base, custom_llm, ignore_default_personality, rag, timezone_, backup_llm_config, cascade_timeout_seconds]) else None) if any(v is not None for v in [first_message, language, hinglish_mode, disable_first_message_interruptions, prompt, llm, reasoning_effort, thinking_budget, max_tokens, built_in_tools, native_mcp_server_ids, knowledge_base, custom_llm, ignore_default_personality, rag, timezone_, backup_llm_config, cascade_timeout_seconds]) else None) if any(v is not None for v in [first_message, language, hinglish_mode, disable_first_message_interruptions, prompt, llm, reasoning_effort, thinking_budget, max_tokens, built_in_tools, native_mcp_server_ids, knowledge_base, custom_llm, ignore_default_personality, rag, timezone_, backup_llm_config, cascade_timeout_seconds, tool_mock_config, partial_conversation_history, dynamic_variables]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for simulate_agent_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/simulate-conversation", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/simulate-conversation"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("simulate_agent_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("simulate_agent_conversation", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="simulate_agent_conversation",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def simulate_conversation_stream(
    agent_id: str = Field(..., description="The unique identifier of the agent to simulate the conversation with."),
    first_message: str | None = Field(None, description="Optional initial message for the agent to speak. If empty, the agent waits for the simulated user to initiate the conversation."),
    language: str | None = Field(None, description="Language code for the agent's speech recognition and text-to-speech processing."),
    hinglish_mode: bool | None = Field(None, description="Enable Hinglish (Hindi-English mix) responses when language is set to Hindi."),
    disable_first_message_interruptions: bool | None = Field(None, description="Prevent the simulated user from interrupting the agent while the first message is being delivered."),
    prompt: str | None = Field(None, description="System prompt that guides the agent's behavior and responses during the conversation."),
    llm: Literal["gpt-4o-mini", "gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.2-chat-latest", "gpt-5-mini", "gpt-5-nano", "gpt-3.5-turbo", "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-3.1-flash-lite-preview", "claude-sonnet-4-5", "claude-sonnet-4-6", "claude-sonnet-4", "claude-haiku-4-5", "claude-3-7-sonnet", "claude-3-5-sonnet", "claude-3-5-sonnet-v1", "claude-3-haiku", "grok-beta", "custom-llm", "qwen3-4b", "qwen3-30b-a3b", "gpt-oss-20b", "gpt-oss-120b", "glm-45-air-fp8", "gemini-2.5-flash-preview-09-2025", "gemini-2.5-flash-lite-preview-09-2025", "gemini-2.5-flash-preview-05-20", "gemini-2.5-flash-preview-04-17", "gemini-2.5-flash-lite-preview-06-17", "gemini-2.0-flash-lite-001", "gemini-2.0-flash-001", "gemini-1.5-flash-002", "gemini-1.5-flash-001", "gemini-1.5-pro-002", "gemini-1.5-pro-001", "claude-sonnet-4@20250514", "claude-sonnet-4-5@20250929", "claude-haiku-4-5@20251001", "claude-3-7-sonnet@20250219", "claude-3-5-sonnet@20240620", "claude-3-5-sonnet-v2@20241022", "claude-3-haiku@20240307", "gpt-5-2025-08-07", "gpt-5.1-2025-11-13", "gpt-5.2-2025-12-11", "gpt-5-mini-2025-08-07", "gpt-5-nano-2025-08-07", "gpt-4.1-2025-04-14", "gpt-4.1-mini-2025-04-14", "gpt-4.1-nano-2025-04-14", "gpt-4o-mini-2024-07-18", "gpt-4o-2024-11-20", "gpt-4o-2024-08-06", "gpt-4o-2024-05-13", "gpt-4-0613", "gpt-4-0314", "gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "watt-tool-8b", "watt-tool-70b"] | None = Field(None, description="The language model to use for generating agent responses. Must be supported in your data residency environment if applicable."),
    reasoning_effort: Literal["none", "minimal", "low", "medium", "high"] | None = Field(None, description="Level of reasoning effort for the model. Only applicable to models that support extended reasoning."),
    thinking_budget: int | None = Field(None, description="Maximum number of tokens allocated for model thinking. Set to 0 to disable thinking if supported by the model."),
    max_tokens: int | None = Field(None, description="Maximum number of tokens the model can generate in its response. Use -1 for no limit."),
    built_in_tools: dict[str, Any] | None = Field(None, description="Built-in system tools available to the agent during the conversation (e.g., web search, calculator, file operations)."),
    native_mcp_server_ids: list[str] | None = Field(None, description="List of Native MCP server identifiers to integrate with the agent for extended functionality.", max_length=10),
    knowledge_base: list[_models.KnowledgeBaseLocator] | None = Field(None, description="List of knowledge bases the agent can reference to provide informed responses."),
    custom_llm: dict[str, Any] | None = Field(None, description="Configuration object for a custom LLM provider. Required when llm parameter is set to 'custom-llm'."),
    ignore_default_personality: bool | None = Field(None, description="Exclude default personality traits and behavioral guidelines from the system prompt."),
    rag: dict[str, Any] | None = Field(None, description="Configuration for Retrieval-Augmented Generation to enhance agent responses with external data sources."),
    timezone_: str | None = Field(None, alias="timezone", description="Timezone identifier for displaying current time in the system prompt. Use standard timezone names to ensure accurate time context."),
    backup_llm_config: _models.BackupLlmDefault | _models.BackupLlmDisabled | _models.BackupLlmOverride | None = Field(None, description="Configuration for fallback LLM cascading behavior when the primary model is unavailable or times out."),
    cascade_timeout_seconds: float | None = Field(None, description="Time in seconds to wait before cascading to a backup LLM if the primary model does not respond.", ge=2.0, le=15.0),
    tool_mock_config: dict[str, _models.ToolMockConfig] | None = Field(None, description="Configuration for mocking tool responses during simulation to test agent behavior without executing real tools."),
    partial_conversation_history: list[_models.ConversationHistoryTranscriptCommonModelInput] | None = Field(None, description="Existing conversation history to resume from. If empty, the simulation starts fresh. Messages should be in chronological order."),
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(None, description="Dynamic variables to inject into the agent's context and prompts during the conversation simulation."),
    extra_evaluation_criteria: list[_models.PromptEvaluationCriteria] | None = Field(None, description="List of custom evaluation criteria to assess the agent's performance during the conversation simulation."),
    new_turns_limit: int | None = Field(None, description="Maximum number of new conversation turns to generate before ending the simulation."),
) -> dict[str, Any]:
    """Simulate a conversation between an agent and a simulated user with streamed responses. The response streams partial message lists that should be concatenated, concluding with a final message containing conversation analysis."""

    # Construct request model with validation
    try:
        _request = _models.RunConversationSimulationRouteStreamRequest(
            path=_models.RunConversationSimulationRouteStreamRequestPath(agent_id=agent_id),
            body=_models.RunConversationSimulationRouteStreamRequestBody(extra_evaluation_criteria=extra_evaluation_criteria, new_turns_limit=new_turns_limit,
                simulation_specification=_models.RunConversationSimulationRouteStreamRequestBodySimulationSpecification(tool_mock_config=tool_mock_config, partial_conversation_history=partial_conversation_history, dynamic_variables=dynamic_variables,
                    simulated_user_config=_models.RunConversationSimulationRouteStreamRequestBodySimulationSpecificationSimulatedUserConfig(first_message=first_message, language=language, hinglish_mode=hinglish_mode, disable_first_message_interruptions=disable_first_message_interruptions,
                        prompt=_models.RunConversationSimulationRouteStreamRequestBodySimulationSpecificationSimulatedUserConfigPrompt(prompt=prompt, llm=llm, reasoning_effort=reasoning_effort, thinking_budget=thinking_budget, max_tokens=max_tokens, built_in_tools=built_in_tools, native_mcp_server_ids=native_mcp_server_ids, knowledge_base=knowledge_base, custom_llm=custom_llm, ignore_default_personality=ignore_default_personality, rag=rag, timezone_=timezone_, backup_llm_config=backup_llm_config, cascade_timeout_seconds=cascade_timeout_seconds) if any(v is not None for v in [prompt, llm, reasoning_effort, thinking_budget, max_tokens, built_in_tools, native_mcp_server_ids, knowledge_base, custom_llm, ignore_default_personality, rag, timezone_, backup_llm_config, cascade_timeout_seconds]) else None) if any(v is not None for v in [first_message, language, hinglish_mode, disable_first_message_interruptions, prompt, llm, reasoning_effort, thinking_budget, max_tokens, built_in_tools, native_mcp_server_ids, knowledge_base, custom_llm, ignore_default_personality, rag, timezone_, backup_llm_config, cascade_timeout_seconds]) else None) if any(v is not None for v in [first_message, language, hinglish_mode, disable_first_message_interruptions, prompt, llm, reasoning_effort, thinking_budget, max_tokens, built_in_tools, native_mcp_server_ids, knowledge_base, custom_llm, ignore_default_personality, rag, timezone_, backup_llm_config, cascade_timeout_seconds, tool_mock_config, partial_conversation_history, dynamic_variables]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for simulate_conversation_stream: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/simulate-conversation/stream", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/simulate-conversation/stream"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("simulate_conversation_stream")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("simulate_conversation_stream", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="simulate_conversation_stream",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def create_agent_test(
    name: str = Field(..., description="Human-readable name for this test case."),
    from_conversation_metadata: _models.TestFromConversationMetadataInput | None = Field(None, description="Metadata from the source conversation if this test was derived from an existing conversation."),
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(None, description="Key-value pairs to substitute into the agent configuration during test execution, enabling parameterized testing."),
    chat_history: list[_models.ConversationHistoryTranscriptCommonModelInput] | None = Field(None, description="Conversation history to provide context for the agent's response. Ordered list of messages representing the dialogue leading up to the test.", max_length=200),
    type_: Literal["llm"] | None = Field(None, alias="type", description="Type of test to execute. Determines whether the test evaluates LLM responses or simulated conversations."),
    success_condition: str | None = Field(None, description="Evaluation prompt that determines test success. Should be a boolean-returning prompt that assesses whether the agent's response meets expectations."),
    success_examples: list[_models.AgentSuccessfulResponseExample] | None = Field(None, description="Reference responses demonstrating successful agent behavior. Used to validate that the agent produces similar quality responses.", max_length=5),
    failure_examples: list[_models.AgentFailureResponseExample] | None = Field(None, description="Reference responses demonstrating failed agent behavior. Used to ensure the agent avoids producing similar problematic responses.", max_length=5),
    tool_call_parameters: _models.UnitTestToolCallEvaluationModelInput | None = Field(None, description="Criteria for evaluating tool calls made by the agent. Leave empty to skip tool call validation."),
    check_any_tool_matches: bool | None = Field(None, description="When true, the test passes if any tool call matches the criteria. When false, the test fails if the agent returns multiple tool calls."),
    simulation_scenario: str | None = Field(None, description="Description of the simulated user scenario and persona for simulation-based tests. Provides context for multi-turn conversation evaluation."),
    simulation_max_turns: int | None = Field(None, description="Maximum number of conversation turns to execute in simulation tests. Controls test duration and complexity.", ge=1, le=50),
    simulation_environment: str | None = Field(None, description="Execution environment for the simulation test. Defaults to production if not specified."),
) -> dict[str, Any]:
    """Creates a new test case for evaluating agent responses. Tests can validate response quality, tool usage, or simulate multi-turn conversations with configurable success criteria."""

    # Construct request model with validation
    try:
        _request = _models.CreateAgentResponseTestRouteRequest(
            body=_models.CreateAgentResponseTestRouteRequestBody(from_conversation_metadata=from_conversation_metadata, dynamic_variables=dynamic_variables, chat_history=chat_history, type_=type_, success_condition=success_condition, success_examples=success_examples, failure_examples=failure_examples, name=name, tool_call_parameters=tool_call_parameters, check_any_tool_matches=check_any_tool_matches, simulation_scenario=simulation_scenario, simulation_max_turns=simulation_max_turns, simulation_environment=simulation_environment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_agent_test: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/agent-testing/create"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_agent_test")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_agent_test", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_agent_test",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def get_agent_test(test_id: str = Field(..., description="The unique identifier of the agent response test to retrieve.")) -> dict[str, Any]:
    """Retrieves a specific agent response test by its ID. Use this to fetch details about a previously created test."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentResponseTestRouteRequest(
            path=_models.GetAgentResponseTestRouteRequestPath(test_id=test_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_agent_test: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agent-testing/{test_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agent-testing/{test_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_agent_test")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_agent_test", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_agent_test",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def update_agent_test(
    test_id: str = Field(..., description="The unique identifier of the agent response test to update."),
    name: str = Field(..., description="A descriptive name for the test."),
    from_conversation_metadata: _models.TestFromConversationMetadataInput | None = Field(None, description="Metadata from the conversation this test was originally created from, if applicable."),
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(None, description="Key-value pairs of dynamic variables to substitute into the agent configuration during test execution."),
    chat_history: list[_models.ConversationHistoryTranscriptCommonModelInput] | None = Field(None, description="Conversation history to use as context for the test. Ordered list of messages exchanged before the agent response being tested.", max_length=200),
    type_: Literal["llm"] | None = Field(None, alias="type", description="The type of test to run. Determines how the agent response is evaluated."),
    success_condition: str | None = Field(None, description="A prompt that evaluates whether the agent's response meets success criteria. Should return a boolean value (True for success, False for failure)."),
    success_examples: list[_models.AgentSuccessfulResponseExample] | None = Field(None, description="List of example responses that should be considered successful outcomes. Used to validate test behavior.", max_length=5),
    failure_examples: list[_models.AgentFailureResponseExample] | None = Field(None, description="List of example responses that should be considered failures. Used to validate test behavior.", max_length=5),
    tool_call_parameters: _models.UnitTestToolCallEvaluationModelInput | None = Field(None, description="Criteria for evaluating tool calls made by the agent. If not provided, tool call validation is skipped."),
    check_any_tool_matches: bool | None = Field(None, description="When True, the test passes if any tool call matches the criteria. When False, the test fails if the agent returns multiple tool calls."),
    simulation_scenario: str | None = Field(None, description="Description of the simulation scenario and user persona for simulation-based tests."),
    simulation_max_turns: int | None = Field(None, description="Maximum number of conversation turns allowed in simulation tests. Controls test duration and complexity.", ge=1, le=50),
    simulation_environment: str | None = Field(None, description="The environment context for running the simulation test. Defaults to production if not specified."),
) -> dict[str, Any]:
    """Updates an agent response test configuration by ID. Allows modification of test criteria, success/failure examples, dynamic variables, and simulation settings."""

    # Construct request model with validation
    try:
        _request = _models.UpdateAgentResponseTestRouteRequest(
            path=_models.UpdateAgentResponseTestRouteRequestPath(test_id=test_id),
            body=_models.UpdateAgentResponseTestRouteRequestBody(from_conversation_metadata=from_conversation_metadata, dynamic_variables=dynamic_variables, chat_history=chat_history, type_=type_, success_condition=success_condition, success_examples=success_examples, failure_examples=failure_examples, name=name, tool_call_parameters=tool_call_parameters, check_any_tool_matches=check_any_tool_matches, simulation_scenario=simulation_scenario, simulation_max_turns=simulation_max_turns, simulation_environment=simulation_environment)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_agent_test: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agent-testing/{test_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agent-testing/{test_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_agent_test")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_agent_test", "PUT", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_agent_test",
        method="PUT",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def delete_agent_test(test_id: str = Field(..., description="The unique identifier of the agent response test to delete.")) -> dict[str, Any]:
    """Deletes an agent response test by its ID. This removes the test configuration and associated test data from the system."""

    # Construct request model with validation
    try:
        _request = _models.DeleteChatResponseTestRouteRequest(
            path=_models.DeleteChatResponseTestRouteRequestPath(test_id=test_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_agent_test: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agent-testing/{test_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agent-testing/{test_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_agent_test")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_agent_test", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_agent_test",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def fetch_agent_response_test_summaries(test_ids: list[str] = Field(..., description="List of unique test IDs to retrieve summaries for. Each ID identifies a specific agent response test.")) -> dict[str, Any]:
    """Retrieve summaries for multiple agent response tests by their IDs. Returns a mapping of test IDs to their corresponding test summary data."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentResponseTestsSummariesRouteRequest(
            body=_models.GetAgentResponseTestsSummariesRouteRequestBody(test_ids=test_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for fetch_agent_response_test_summaries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/agent-testing/summaries"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("fetch_agent_response_test_summaries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("fetch_agent_response_test_summaries", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="fetch_agent_response_test_summaries",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def list_agent_tests(
    page_size: int | None = Field(None, description="Maximum number of tests to return per request. Must be between 1 and 100.", ge=1, le=100),
    types: list[Literal["llm", "tool", "simulation", "folder"]] | None = Field(None, description="Filter results to include only tests and folders matching the specified types. When provided, only items of these types are returned."),
    sort_mode: Literal["default", "folders_first"] | None = Field(None, description="Determines the sort order for results. Use 'folders_first' to display folders before tests, or 'default' for standard ordering."),
) -> dict[str, Any]:
    """Retrieve a paginated list of agent response tests with optional filtering by test type and custom sorting. Supports organizing results with folders displayed first if needed."""

    # Construct request model with validation
    try:
        _request = _models.ListChatResponseTestsRouteRequest(
            query=_models.ListChatResponseTestsRouteRequestQuery(page_size=page_size, types=types, sort_mode=sort_mode)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_agent_tests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/agent-testing"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_agent_tests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_agent_tests", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_agent_tests",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def list_test_invocations(
    agent_id: str = Field(..., description="The unique identifier of the agent whose test invocations should be retrieved."),
    page_size: int | None = Field(None, description="Maximum number of test invocations to return per request. Defaults to 30 if not specified.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve a paginated list of test invocations for a specific agent. Supports optional pagination control to manage result set size."""

    # Construct request model with validation
    try:
        _request = _models.ListTestInvocationsRouteRequest(
            query=_models.ListTestInvocationsRouteRequestQuery(agent_id=agent_id, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_test_invocations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/test-invocations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_test_invocations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_test_invocations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_test_invocations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def run_agent_tests(
    agent_id: str = Field(..., description="The unique identifier of the agent to test."),
    tests: list[_models.SingleTestRunRequestModel] = Field(..., description="Array of test configurations to execute. Each test validates specific agent behaviors or criteria.", min_length=1, max_length=1000),
    branch_id: str | None = Field(None, description="Agent branch identifier to test against. If omitted, tests run on the default agent configuration."),
    agent_config_override: _models.RunAgentTestSuiteRouteBodyAgentConfigOverride | None = Field(None, description="Agent configuration overrides for test execution"),
) -> dict[str, Any]:
    """Execute a suite of tests against a conversational AI agent with optional configuration overrides. Tests validate agent behavior, quality, and compliance against specified criteria."""

    # Construct request model with validation
    try:
        _request = _models.RunAgentTestSuiteRouteRequest(
            path=_models.RunAgentTestSuiteRouteRequestPath(agent_id=agent_id),
            body=_models.RunAgentTestSuiteRouteRequestBody(tests=tests, branch_id=branch_id, agent_config_override=agent_config_override)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for run_agent_tests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/run-tests", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/run-tests"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("run_agent_tests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("run_agent_tests", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="run_agent_tests",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def get_test_invocation(test_invocation_id: str = Field(..., description="The unique identifier of the test invocation to retrieve. This ID is provided when tests are executed.")) -> dict[str, Any]:
    """Retrieves a specific test invocation by its ID. Use this to fetch details about a test invocation that was previously executed."""

    # Construct request model with validation
    try:
        _request = _models.GetTestInvocationRouteRequest(
            path=_models.GetTestInvocationRouteRequestPath(test_invocation_id=test_invocation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_test_invocation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/test-invocations/{test_invocation_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/test-invocations/{test_invocation_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_test_invocation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_test_invocation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_test_invocation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data


@mcp.tool()
async def resubmit_tests(
    test_invocation_id: str = Field(..., description="The unique identifier of the test invocation containing the test runs to resubmit. This ID is returned when tests are initially executed."),
    test_run_ids: list[str] = Field(..., description="List of test run IDs to resubmit. Each ID identifies a specific test case within the invocation to be re-executed.", min_length=1, max_length=1000),
    agent_id: str = Field(..., description="The unique identifier of the agent whose tests should be resubmitted."),
    branch_id: str | None = Field(None, description="Branch ID for running tests against a specific agent variant or configuration. If omitted, tests run against the agent's default configuration."),
    agent_config_override: _models.ResubmitTestsRouteBodyAgentConfigOverride | None = Field(None, description="Agent configuration overrides for test resubmission"),
) -> dict[str, Any]:
    """Resubmit specific test runs from a completed test invocation to re-evaluate agent performance with potentially updated configurations. Allows selective resubmission of individual test cases within a test batch."""

    # Construct request model with validation
    try:
        _request = _models.ResubmitTestsRouteRequest(
            path=_models.ResubmitTestsRouteRequestPath(test_invocation_id=test_invocation_id),
            body=_models.ResubmitTestsRouteRequestBody(test_run_ids=test_run_ids, agent_id=agent_id, branch_id=branch_id, agent_config_override=agent_config_override)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for resubmit_tests: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/test-invocations/{test_invocation_id}/resubmit", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/test-invocations/{test_invocation_id}/resubmit"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("resubmit_tests")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("resubmit_tests", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="resubmit_tests",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_conversations(
    agent_id: str | None = Field(None, description="Filter conversations to a specific agent by its unique identifier."),
    call_successful: Literal["success", "failure", "unknown"] | None = Field(None, description="Filter conversations by the result of the success evaluation."),
    call_duration_min_secs: int | None = Field(None, description="Filter conversations with a minimum call duration in seconds."),
    call_duration_max_secs: int | None = Field(None, description="Filter conversations with a maximum call duration in seconds."),
    rating_max: int | None = Field(None, description="Filter conversations with a maximum overall rating on a scale of 1-5.", ge=1, le=5),
    rating_min: int | None = Field(None, description="Filter conversations with a minimum overall rating on a scale of 1-5.", ge=1, le=5),
    has_feedback_comment: bool | None = Field(None, description="Filter to only conversations that include user feedback comments."),
    user_id: str | None = Field(None, description="Filter conversations by the user ID who initiated them."),
    evaluation_params: list[str] | None = Field(None, description="Filter by evaluation criteria results. Specify as criteria_id:result pairs; parameter can be repeated for multiple criteria."),
    data_collection_params: list[str] | None = Field(None, description="Filter by data collection fields using comparison operators. Format: id:op:value where op is one of eq, neq, gt, gte, lt, lte, in, exists, or missing. For 'in' operator, pipe-delimit multiple values. Parameter can be repeated for multiple filters."),
    tool_names: list[str] | None = Field(None, description="Filter conversations by the names of tools used during the call. Specify multiple tool names as separate array items."),
    main_languages: list[str] | None = Field(None, description="Filter conversations by detected main language using language codes. Specify multiple languages as separate array items."),
    page_size: int | None = Field(None, description="Maximum number of conversations to return per request. Cannot exceed 100.", ge=1, le=100),
    summary_mode: Literal["exclude", "include"] | None = Field(None, description="Include or exclude transcript summaries in the response."),
    conversation_initiation_source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(None, description="Filter conversations by their initiation source (SDK, integration, or communication platform)."),
    branch_id: str | None = Field(None, description="Filter conversations by branch ID."),
) -> dict[str, Any]:
    """Retrieve all conversations for agents owned by the user, with extensive filtering options by agent, call metrics, ratings, evaluation results, and conversation metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetConversationHistoriesRouteRequest(
            query=_models.GetConversationHistoriesRouteRequestQuery(agent_id=agent_id, call_successful=call_successful, call_duration_min_secs=call_duration_min_secs, call_duration_max_secs=call_duration_max_secs, rating_max=rating_max, rating_min=rating_min, has_feedback_comment=has_feedback_comment, user_id=user_id, evaluation_params=evaluation_params, data_collection_params=data_collection_params, tool_names=tool_names, main_languages=main_languages, page_size=page_size, summary_mode=summary_mode, conversation_initiation_source=conversation_initiation_source, branch_id=branch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_conversations: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/conversations"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_conversations")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_conversations", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_conversations",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_conversation_users(
    agent_id: str | None = Field(None, description="The ID of the agent to filter conversations by."),
    branch_id: str | None = Field(None, description="Filter conversations to a specific branch by its ID."),
    page_size: int | None = Field(None, description="Maximum number of users to return per page. Valid range is 1 to 100.", ge=1, le=100),
    sort_by: Literal["last_contact_unix_secs", "conversation_count"] | None = Field(None, description="Field to sort results by. Choose between most recent contact time or total conversation count."),
) -> dict[str, Any]:
    """Retrieve a paginated list of distinct users from conversations, with options to filter by agent and branch, and sort by contact recency or conversation frequency."""

    # Construct request model with validation
    try:
        _request = _models.GetConversationUsersRouteRequest(
            query=_models.GetConversationUsersRouteRequestQuery(agent_id=agent_id, branch_id=branch_id, page_size=page_size, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_conversation_users: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/users"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_conversation_users")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_conversation_users", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_conversation_users",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_conversation(conversation_id: str = Field(..., description="The unique identifier of the conversation to retrieve.")) -> dict[str, Any]:
    """Retrieve the full details and history of a specific conversation by its ID. Use this to access conversation metadata, messages, and related information."""

    # Construct request model with validation
    try:
        _request = _models.GetConversationHistoryRouteRequest(
            path=_models.GetConversationHistoryRouteRequestPath(conversation_id=conversation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/conversations/{conversation_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/conversations/{conversation_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_conversation", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_conversation",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_conversation(conversation_id: str = Field(..., description="The unique identifier of the conversation to delete.")) -> dict[str, Any]:
    """Permanently delete a conversation and all associated data. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteConversationRouteRequest(
            path=_models.DeleteConversationRouteRequestPath(conversation_id=conversation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_conversation: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/conversations/{conversation_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/conversations/{conversation_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_conversation")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_conversation", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_conversation",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_conversation_audio(conversation_id: str = Field(..., description="The unique identifier of the conversation whose audio recording you want to retrieve.")) -> dict[str, Any]:
    """Retrieve the audio recording of a specific conversation. Returns the audio file associated with the conversation ID."""

    # Construct request model with validation
    try:
        _request = _models.GetConversationAudioRouteRequest(
            path=_models.GetConversationAudioRouteRequestPath(conversation_id=conversation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_conversation_audio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/conversations/{conversation_id}/audio", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/conversations/{conversation_id}/audio"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_conversation_audio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_conversation_audio", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_conversation_audio",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def submit_conversation_feedback(
    conversation_id: str = Field(..., description="The unique identifier of the conversation to provide feedback for."),
    feedback: Literal["like", "dislike"] | None = Field(None, description="The feedback sentiment for the conversation, either positive or negative."),
) -> dict[str, Any]:
    """Submit feedback for a conversation to indicate user satisfaction. Feedback can be positive ('like') or negative ('dislike')."""

    # Construct request model with validation
    try:
        _request = _models.PostConversationFeedbackRouteRequest(
            path=_models.PostConversationFeedbackRouteRequestPath(conversation_id=conversation_id),
            body=_models.PostConversationFeedbackRouteRequestBody(feedback=feedback)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for submit_conversation_feedback: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/conversations/{conversation_id}/feedback", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/conversations/{conversation_id}/feedback"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("submit_conversation_feedback")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("submit_conversation_feedback", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="submit_conversation_feedback",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def search_conversation_messages(
    text_query: str = Field(..., description="The search query text to match against conversation messages using full-text and fuzzy search algorithms."),
    agent_id: str | None = Field(None, description="Filter results to conversations handled by a specific agent."),
    call_successful: Literal["success", "failure", "unknown"] | None = Field(None, description="Filter results by the outcome of the conversation (success, failure, or unknown)."),
    call_duration_min_secs: int | None = Field(None, description="Filter conversations with a minimum duration in seconds."),
    call_duration_max_secs: int | None = Field(None, description="Filter conversations with a maximum duration in seconds."),
    rating_max: int | None = Field(None, description="Filter conversations with a maximum overall rating on a scale of 1-5.", ge=1, le=5),
    rating_min: int | None = Field(None, description="Filter conversations with a minimum overall rating on a scale of 1-5.", ge=1, le=5),
    has_feedback_comment: bool | None = Field(None, description="Include only conversations that have user feedback comments."),
    user_id: str | None = Field(None, description="Filter conversations by the user ID who initiated them."),
    evaluation_params: list[str] | None = Field(None, description="Filter by evaluation criteria results. Specify as criteria_id:result pairs (repeatable parameter)."),
    data_collection_params: list[str] | None = Field(None, description="Filter by data collection fields using comparison operators. Format: id:operator:value where operator is eq, neq, gt, gte, lt, lte, in, exists, or missing. Use pipe-delimited values for 'in' operator (repeatable parameter)."),
    tool_names: list[str] | None = Field(None, description="Filter conversations by the names of tools used during the call (repeatable parameter)."),
    main_languages: list[str] | None = Field(None, description="Filter conversations by detected primary language using language codes (repeatable parameter)."),
    page_size: int | None = Field(None, description="Number of results to return per page.", ge=1, le=50),
    summary_mode: Literal["exclude", "include"] | None = Field(None, description="Include or exclude transcript summaries in the response."),
    conversation_initiation_source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(None, description="Filter conversations by their initiation source (SDK, integration, or communication platform)."),
    branch_id: str | None = Field(None, description="Filter conversations by branch ID."),
) -> dict[str, Any]:
    """Search conversation transcripts using full-text and fuzzy matching with optional filtering by agent, user, call metrics, ratings, language, and other conversation attributes."""

    # Construct request model with validation
    try:
        _request = _models.TextSearchConversationMessagesRouteRequest(
            query=_models.TextSearchConversationMessagesRouteRequestQuery(text_query=text_query, agent_id=agent_id, call_successful=call_successful, call_duration_min_secs=call_duration_min_secs, call_duration_max_secs=call_duration_max_secs, rating_max=rating_max, rating_min=rating_min, has_feedback_comment=has_feedback_comment, user_id=user_id, evaluation_params=evaluation_params, data_collection_params=data_collection_params, tool_names=tool_names, main_languages=main_languages, page_size=page_size, summary_mode=summary_mode, conversation_initiation_source=conversation_initiation_source, branch_id=branch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_conversation_messages: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/conversations/messages/text-search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_conversation_messages")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_conversation_messages", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_conversation_messages",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def search_conversation_messages_semantic(
    text_query: str = Field(..., description="The search query text to match against conversation messages using semantic similarity. Accepts natural language queries describing intent, topics, or specific requests."),
    agent_id: str | None = Field(None, description="Filter results to messages from a specific agent. If omitted, searches across all agents in the conversation."),
    page_size: int | None = Field(None, description="Number of results to return per page. Controls pagination size for large result sets.", ge=1, le=50),
) -> dict[str, Any]:
    """Search conversation transcripts using semantic similarity to find relevant messages based on meaning and intent rather than exact keyword matches. Returns the most contextually relevant messages from conversation history."""

    # Construct request model with validation
    try:
        _request = _models.SmartSearchConversationMessagesRouteRequest(
            query=_models.SmartSearchConversationMessagesRouteRequestQuery(text_query=text_query, agent_id=agent_id, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for search_conversation_messages_semantic: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/conversations/messages/smart-search"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("search_conversation_messages_semantic")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("search_conversation_messages_semantic", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="search_conversation_messages_semantic",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_phone_numbers() -> dict[str, Any]:
    """Retrieve all phone numbers associated with your account. Returns a complete list of configured phone numbers available for use in voice conversations."""

    # Extract parameters for API call
    _http_path = "/v1/convai/phone-numbers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_phone_numbers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_phone_numbers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_phone_numbers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def import_phone_number(
    phone_number: str = Field(..., description="The phone number to import in E.164 format or provider-specific format."),
    label: str = Field(..., description="A descriptive label for this phone number to identify it in your system."),
    provider: Literal["twilio"] | None = Field(None, description="The telecommunications provider to import from. Defaults to Twilio if not specified."),
    sid: str | None = Field(None, description="Your Twilio Account SID for authentication. Required when provider is set to Twilio."),
    token: str | None = Field(None, description="Your Twilio Auth Token for authentication. Required when provider is set to Twilio."),
    region_config: _models.RegionConfigRequest | None = Field(None, description="Additional Twilio region configuration settings to optimize call routing and compliance for specific geographic regions."),
    inbound_trunk_config: _models.InboundSipTrunkConfigRequestModel | None = Field(None, description="SIP trunk configuration for inbound call routing, including server address, port, and authentication credentials."),
    outbound_trunk_config: _models.OutboundSipTrunkConfigRequestModel | None = Field(None, description="SIP trunk configuration for outbound call routing, including server address, port, and authentication credentials."),
) -> dict[str, Any]:
    """Import a phone number from your provider configuration (Twilio or SIP trunk) to enable inbound and outbound calling capabilities."""

    # Construct request model with validation
    try:
        _request = _models.CreatePhoneNumberRouteRequest(
            body=_models.CreatePhoneNumberRouteRequestBody(phone_number=phone_number, label=label, provider=provider, sid=sid, token=token, region_config=region_config, inbound_trunk_config=inbound_trunk_config, outbound_trunk_config=outbound_trunk_config)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for import_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/phone-numbers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("import_phone_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("import_phone_number", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="import_phone_number",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_phone_number(phone_number_id: str = Field(..., description="The unique identifier of the phone number to retrieve.")) -> dict[str, Any]:
    """Retrieve details for a specific phone number by its ID. Returns the phone number configuration and associated metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetPhoneNumberRouteRequest(
            path=_models.GetPhoneNumberRouteRequestPath(phone_number_id=phone_number_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/phone-numbers/{phone_number_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/phone-numbers/{phone_number_id}"
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

# Tags: Agents Platform
@mcp.tool()
async def update_phone_number(
    phone_number_id: str = Field(..., description="The unique identifier of the phone number to update."),
    inbound_trunk_config_credentials_username: str = Field(..., alias="inbound_trunk_configCredentialsUsername", description="Username credential for inbound SIP trunk authentication."),
    outbound_trunk_config_credentials_username: str = Field(..., alias="outbound_trunk_configCredentialsUsername", description="Username credential for outbound SIP trunk authentication."),
    address: str = Field(..., description="Hostname or IP address where SIP INVITE requests are routed."),
    agent_id: str | None = Field(None, description="The ID of the agent to assign to this phone number for handling incoming calls."),
    label: str | None = Field(None, description="A human-readable label or name for this phone number."),
    allowed_addresses: list[str] | None = Field(None, description="List of IP addresses or CIDR blocks permitted to use this trunk. Each entry can be a single IP address or a CIDR notation block."),
    allowed_numbers: list[str] | None = Field(None, description="List of phone numbers authorized to use this trunk."),
    media_encryption: Literal["disabled", "allowed", "required"] | None = Field(None, description="Media encryption policy for outbound calls. Controls whether RTP traffic is encrypted."),
    password: str | None = Field(None, description="Password credential for outbound SIP trunk authentication. If omitted, the existing password remains unchanged."),
    remote_domains: list[str] | None = Field(None, description="List of remote SIP server domains used for validating TLS certificates during secure connections."),
    transport: Literal["auto", "udp", "tcp", "tls"] | None = Field(None, description="SIP transport protocol for signaling. Auto-detection attempts to select the optimal protocol."),
    headers: dict[str, str] | None = Field(None, description="Custom SIP X-* headers to include in INVITE requests. Useful for identifying calls or passing metadata to the SIP provider."),
    livekit_stack: Literal["standard", "static"] | None = Field(None, description="LiveKit media server stack configuration for call handling."),
) -> dict[str, Any]:
    """Update the routing configuration and credentials for a phone number, including assigned agent, SIP trunk settings, and security policies."""

    # Construct request model with validation
    try:
        _request = _models.UpdatePhoneNumberRouteRequest(
            path=_models.UpdatePhoneNumberRouteRequestPath(phone_number_id=phone_number_id),
            body=_models.UpdatePhoneNumberRouteRequestBody(agent_id=agent_id, label=label, livekit_stack=livekit_stack,
                inbound_trunk_config=_models.UpdatePhoneNumberRouteRequestBodyInboundTrunkConfig(
                    allowed_addresses=allowed_addresses, allowed_numbers=allowed_numbers, remote_domains=remote_domains,
                    credentials=_models.UpdatePhoneNumberRouteRequestBodyInboundTrunkConfigCredentials(username=inbound_trunk_config_credentials_username)
                ),
                outbound_trunk_config=_models.UpdatePhoneNumberRouteRequestBodyOutboundTrunkConfig(
                    media_encryption=media_encryption, address=address, transport=transport, headers=headers,
                    credentials=_models.UpdatePhoneNumberRouteRequestBodyOutboundTrunkConfigCredentials(username=outbound_trunk_config_credentials_username, password=password)
                ))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/phone-numbers/{phone_number_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/phone-numbers/{phone_number_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_phone_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_phone_number", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_phone_number",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_phone_number(phone_number_id: str = Field(..., description="The unique identifier of the phone number to delete.")) -> dict[str, Any]:
    """Delete a phone number from your ConvAI account by its ID. This action is permanent and cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeletePhoneNumberRouteRequest(
            path=_models.DeletePhoneNumberRouteRequestPath(phone_number_id=phone_number_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_phone_number: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/phone-numbers/{phone_number_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/phone-numbers/{phone_number_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_phone_number")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_phone_number", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_phone_number",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def calculate_llm_expected_cost(
    prompt_length: int = Field(..., description="The length of the input prompt in characters. This determines the token consumption for the initial request."),
    number_of_pages: int = Field(..., description="The total number of pages in PDF documents or URLs indexed in the agent's knowledge base. Used to estimate retrieval and processing costs when RAG is enabled."),
    rag_enabled: bool = Field(..., description="Whether Retrieval-Augmented Generation (RAG) is enabled. When enabled, the cost calculation includes knowledge base retrieval and context augmentation overhead."),
) -> dict[str, Any]:
    """Calculate the expected cost of using various LLM models based on prompt length, knowledge base size, and RAG configuration. Returns a list of available models with their associated usage costs."""

    # Construct request model with validation
    try:
        _request = _models.GetPublicLlmExpectedCostCalculationRequest(
            body=_models.GetPublicLlmExpectedCostCalculationRequestBody(prompt_length=prompt_length, number_of_pages=number_of_pages, rag_enabled=rag_enabled)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for calculate_llm_expected_cost: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/llm-usage/calculate"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("calculate_llm_expected_cost")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("calculate_llm_expected_cost", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="calculate_llm_expected_cost",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_llms() -> dict[str, Any]:
    """Retrieve a list of available LLM models that can be used with agents, including their capabilities and deprecation status. The response is filtered based on your deployment's data residency and workspace compliance requirements (e.g., HIPAA)."""

    # Extract parameters for API call
    _http_path = "/v1/convai/llm/list"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_llms")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_llms", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_llms",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def upload_file(
    conversation_id: str = Field(..., description="The unique identifier of the conversation to which the file will be uploaded."),
    file_: str = Field(..., alias="file", description="The image or PDF file to upload. Supported formats include common image types (JPEG, PNG, etc.) and PDF documents."),
) -> dict[str, Any]:
    """Upload an image or PDF file to a conversation. Returns a unique file ID for referencing the file in subsequent conversation messages."""

    # Construct request model with validation
    try:
        _request = _models.UploadFileRouteRequest(
            path=_models.UploadFileRouteRequestPath(conversation_id=conversation_id),
            body=_models.UploadFileRouteRequestBody(file_=file_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/conversations/{conversation_id}/files", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/conversations/{conversation_id}/files"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_file", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_file",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_conversation_file(
    conversation_id: str = Field(..., description="The unique identifier of the conversation containing the file to be deleted."),
    file_id: str = Field(..., description="The unique identifier of the file upload to be removed from the conversation."),
) -> dict[str, Any]:
    """Remove a file upload from a conversation. This operation is only available if the file has not yet been used within the conversation."""

    # Construct request model with validation
    try:
        _request = _models.CancelFileUploadRouteRequest(
            path=_models.CancelFileUploadRouteRequestPath(conversation_id=conversation_id, file_id=file_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_conversation_file: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/conversations/{conversation_id}/files/{file_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/conversations/{conversation_id}/files/{file_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_conversation_file")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_conversation_file", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_conversation_file",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_conversation_live_count(agent_id: str | None = Field(None, description="Filter the live count to conversations handled by a specific agent. Omit to get the total count across all agents.")) -> dict[str, Any]:
    """Retrieve the current count of active ongoing conversations. Optionally filter results to a specific agent."""

    # Construct request model with validation
    try:
        _request = _models.GetLiveCountRequest(
            query=_models.GetLiveCountRequestQuery(agent_id=agent_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_conversation_live_count: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/analytics/live-count"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_conversation_live_count")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_conversation_live_count", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_conversation_live_count",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_knowledge_base_summaries(document_ids: list[str] = Field(..., description="List of knowledge base document IDs to retrieve summaries for. IDs must be valid document identifiers from your knowledge base.", min_length=1, max_length=100)) -> dict[str, Any]:
    """Retrieve summaries for multiple knowledge base documents by their IDs. Useful for quickly accessing document metadata and content previews without loading full documents."""

    # Construct request model with validation
    try:
        _request = _models.GetAgentKnowledgeBaseSummariesRouteRequest(
            query=_models.GetAgentKnowledgeBaseSummariesRouteRequestQuery(document_ids=document_ids)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_knowledge_base_summaries: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/knowledge-base/summaries"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_knowledge_base_summaries")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_knowledge_base_summaries", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_knowledge_base_summaries",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_knowledge_bases(
    page_size: int | None = Field(None, description="Maximum number of documents to return per page. Defaults to 30 documents.", ge=1, le=100),
    created_by_user_id: str | None = Field(None, description="Filter results to documents created by a specific user. Use '@me' to refer to the authenticated user. Takes precedence over ownership filters."),
    types: list[Literal["file", "url", "text", "folder"]] | None = Field(None, description="Filter results to only include documents of specified types. Provide as an array of type identifiers."),
    folders_first: bool | None = Field(None, description="Whether to display folder documents before other document types in the results."),
    sort_direction: Literal["asc", "desc"] | None = Field(None, description="Order direction for sorting results in ascending or descending sequence."),
    sort_by: Literal["name", "created_at", "updated_at", "size"] | None = Field(None, description="Field to sort results by. Choose from document name, creation date, last update date, or file size."),
) -> dict[str, Any]:
    """Retrieve a paginated list of available knowledge base documents with filtering and sorting options. Results can be filtered by creator, document type, and sorted by various fields."""

    # Construct request model with validation
    try:
        _request = _models.GetKnowledgeBaseListRouteRequest(
            query=_models.GetKnowledgeBaseListRouteRequestQuery(page_size=page_size, created_by_user_id=created_by_user_id, types=types, folders_first=folders_first, sort_direction=sort_direction, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_knowledge_bases: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/knowledge-base"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_knowledge_bases")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_knowledge_bases", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_knowledge_bases",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def create_knowledge_base_document_from_url(
    url: str = Field(..., description="The complete URL of the webpage to scrape and add to the knowledge base. Must be a valid, publicly accessible web address."),
    name: str | None = Field(None, description="A human-readable label for this document within the knowledge base. Helps identify and organize the document for agent reference.", min_length=1),
) -> dict[str, Any]:
    """Create a knowledge base document by scraping and indexing content from a specified webpage. The agent will use this document to access and reference the webpage content when interacting with users."""

    # Construct request model with validation
    try:
        _request = _models.CreateUrlDocumentRouteRequest(
            body=_models.CreateUrlDocumentRouteRequestBody(url=url, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_knowledge_base_document_from_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/knowledge-base/url"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_knowledge_base_document_from_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_knowledge_base_document_from_url", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_knowledge_base_document_from_url",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def upload_knowledge_base_document(
    file_: str = Field(..., alias="file", description="The file content to upload as a knowledge base document. Accepts binary file formats for documentation."),
    name: str | None = Field(None, description="A human-readable name for the document. If not provided, a default name will be generated.", min_length=1),
) -> dict[str, Any]:
    """Upload a file to create a new knowledge base document that the agent can access and reference when interacting with users."""

    # Construct request model with validation
    try:
        _request = _models.CreateFileDocumentRouteRequest(
            body=_models.CreateFileDocumentRouteRequestBody(file_=file_, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_knowledge_base_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/knowledge-base/file"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_knowledge_base_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_knowledge_base_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_knowledge_base_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def add_text_document(
    text: str = Field(..., description="The text content to be added to the knowledge base. This will be indexed for search and retrieval."),
    name: str | None = Field(None, description="A human-readable name for the document. If not provided, a default name will be generated.", min_length=1),
) -> dict[str, Any]:
    """Add a text document to the knowledge base. The document will be indexed and made available for retrieval and analysis."""

    # Construct request model with validation
    try:
        _request = _models.CreateTextDocumentRouteRequest(
            body=_models.CreateTextDocumentRouteRequestBody(text=text, name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_text_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/knowledge-base/text"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_text_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_text_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_text_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversational AI
@mcp.tool()
async def create_folder(name: str = Field(..., description="A human-readable name for the folder. Used to identify and organize document groups within the knowledge base.", min_length=1)) -> dict[str, Any]:
    """Create a new folder in the knowledge base for organizing and grouping related documents together."""

    # Construct request model with validation
    try:
        _request = _models.CreateFolderRouteRequest(
            body=_models.CreateFolderRouteRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_folder: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/knowledge-base/folder"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_folder")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_folder", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_folder",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def retrieve_knowledge_base_document(
    documentation_id: str = Field(..., description="The unique identifier of the document to retrieve from the knowledge base."),
    agent_id: str | None = Field(None, description="Optional agent identifier to scope the knowledge base query to a specific agent."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific document from the agent's knowledge base. Use the documentation ID returned when the document was added to access its content and metadata."""

    # Construct request model with validation
    try:
        _request = _models.GetDocumentationFromKnowledgeBaseRequest(
            path=_models.GetDocumentationFromKnowledgeBaseRequestPath(documentation_id=documentation_id),
            query=_models.GetDocumentationFromKnowledgeBaseRequestQuery(agent_id=agent_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retrieve_knowledge_base_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{documentation_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{documentation_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retrieve_knowledge_base_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retrieve_knowledge_base_document", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retrieve_knowledge_base_document",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def rename_document(
    documentation_id: str = Field(..., description="The unique identifier of the document to rename. This ID is provided when the document is initially added to the knowledge base."),
    name: str = Field(..., description="A human-readable name for the document. Must be at least one character long.", min_length=1),
) -> dict[str, Any]:
    """Rename a document in the knowledge base by updating its display name."""

    # Construct request model with validation
    try:
        _request = _models.UpdateDocumentRouteRequest(
            path=_models.UpdateDocumentRouteRequestPath(documentation_id=documentation_id),
            body=_models.UpdateDocumentRouteRequestBody(name=name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for rename_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{documentation_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{documentation_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("rename_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("rename_document", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="rename_document",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_knowledge_base_document(
    documentation_id: str = Field(..., description="The unique identifier of the document or folder to delete from the knowledge base."),
    force: bool | None = Field(None, description="Force deletion of the document or folder even if it is currently used by agents. When enabled, the document will be removed from all dependent agents, and all child documents and folders within non-empty folders will also be deleted."),
) -> dict[str, Any]:
    """Permanently delete a document or folder from the knowledge base. Optionally force deletion even if the document is in use by agents, which will also remove it from dependent agents and delete all child documents in non-empty folders."""

    # Construct request model with validation
    try:
        _request = _models.DeleteKnowledgeBaseDocumentRequest(
            path=_models.DeleteKnowledgeBaseDocumentRequestPath(documentation_id=documentation_id),
            query=_models.DeleteKnowledgeBaseDocumentRequestQuery(force=force)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_knowledge_base_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{documentation_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{documentation_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_knowledge_base_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_knowledge_base_document", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_knowledge_base_document",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_rag_index_overview() -> dict[str, Any]:
    """Retrieves metadata about RAG (Retrieval-Augmented Generation) indexes used by the knowledge base, including total size and other index statistics."""

    # Extract parameters for API call
    _http_path = "/v1/convai/knowledge-base/rag-index"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_rag_index_overview")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_rag_index_overview", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_rag_index_overview",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def batch_compute_rag_indexes(items: list[_models.GetOrCreateRagIndexRequestModel] = Field(..., description="Array of RAG index requests for knowledge base documents. Each item specifies a document to index. Order is preserved in the response.", min_length=1, max_length=100)) -> dict[str, Any]:
    """Computes and retrieves RAG (Retrieval-Augmented Generation) indexes for multiple knowledge base documents in a single batch operation. Supports up to 100 documents per request for efficient index creation and retrieval."""

    # Construct request model with validation
    try:
        _request = _models.GetOrCreateRagIndexesRequest(
            body=_models.GetOrCreateRagIndexesRequestBody(items=items)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for batch_compute_rag_indexes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/knowledge-base/rag-index"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("batch_compute_rag_indexes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("batch_compute_rag_indexes", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="batch_compute_rag_indexes",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def refresh_knowledge_base_document(documentation_id: str = Field(..., description="The unique identifier of the document in the knowledge base to refresh. This ID is provided when the document is initially added.")) -> dict[str, Any]:
    """Manually refresh a URL-based document in the knowledge base by re-fetching its content from the source URL. Use this to update stale or outdated document content."""

    # Construct request model with validation
    try:
        _request = _models.RefreshUrlDocumentRouteRequest(
            path=_models.RefreshUrlDocumentRouteRequestPath(documentation_id=documentation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for refresh_knowledge_base_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{documentation_id}/refresh", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{documentation_id}/refresh"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("refresh_knowledge_base_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("refresh_knowledge_base_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="refresh_knowledge_base_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_rag_indexes(documentation_id: str = Field(..., description="The unique identifier of the knowledge base document for which to retrieve RAG indexes.")) -> dict[str, Any]:
    """Retrieve all RAG indexes associated with a specified knowledge base document. Returns metadata about each index configured for the document."""

    # Construct request model with validation
    try:
        _request = _models.GetRagIndexesRequest(
            path=_models.GetRagIndexesRequestPath(documentation_id=documentation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_rag_indexes: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{documentation_id}/rag-index", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{documentation_id}/rag-index"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_rag_indexes")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_rag_indexes", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_rag_indexes",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def index_knowledge_base_document(
    documentation_id: str = Field(..., description="The unique identifier of the document in the knowledge base that you want to index or check the indexing status for."),
    model: Literal["e5_mistral_7b_instruct", "multilingual_e5_large_instruct"] = Field(..., description="The embedding model to use for RAG indexing. This determines how the document content will be vectorized for semantic search."),
) -> dict[str, Any]:
    """Trigger or retrieve the RAG indexing status for a knowledge base document. If the document hasn't been indexed yet, this operation initiates the indexing task; otherwise, it returns the current indexing status."""

    # Construct request model with validation
    try:
        _request = _models.RagIndexStatusRequest(
            path=_models.RagIndexStatusRequestPath(documentation_id=documentation_id),
            body=_models.RagIndexStatusRequestBody(model=model)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for index_knowledge_base_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{documentation_id}/rag-index", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{documentation_id}/rag-index"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("index_knowledge_base_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("index_knowledge_base_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="index_knowledge_base_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_rag_index(
    documentation_id: str = Field(..., description="The unique identifier of the knowledge base document whose RAG index will be deleted."),
    rag_index_id: str = Field(..., description="The unique identifier of the RAG index to delete for the specified document."),
) -> dict[str, Any]:
    """Delete a RAG index associated with a knowledge base document. This removes the indexed data used for retrieval-augmented generation on that document."""

    # Construct request model with validation
    try:
        _request = _models.DeleteRagIndexRequest(
            path=_models.DeleteRagIndexRequestPath(documentation_id=documentation_id, rag_index_id=rag_index_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_rag_index: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{documentation_id}/rag-index/{rag_index_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{documentation_id}/rag-index/{rag_index_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_rag_index")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_rag_index", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_rag_index",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_dependent_agents(
    documentation_id: str = Field(..., description="The unique identifier of the knowledge base document for which to retrieve dependent agents."),
    dependent_type: Literal["direct", "transitive", "all"] | None = Field(None, description="Filter results by dependency relationship type. Use 'direct' for agents directly referencing this document, 'transitive' for agents indirectly depending on it, or 'all' to include both."),
    page_size: int | None = Field(None, description="Maximum number of agents to return per request. Must be between 1 and 100.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve a list of agents that depend on a specific knowledge base document. Supports filtering by dependency type (direct, transitive, or all) with pagination."""

    # Construct request model with validation
    try:
        _request = _models.GetKnowledgeBaseDependentAgentsRequest(
            path=_models.GetKnowledgeBaseDependentAgentsRequestPath(documentation_id=documentation_id),
            query=_models.GetKnowledgeBaseDependentAgentsRequestQuery(dependent_type=dependent_type, page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dependent_agents: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{documentation_id}/dependent-agents", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{documentation_id}/dependent-agents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dependent_agents")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dependent_agents", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dependent_agents",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def retrieve_knowledge_base_document_content(documentation_id: str = Field(..., description="The unique identifier of the document in the knowledge base, provided when the document was initially added.")) -> dict[str, Any]:
    """Retrieve the complete content of a document stored in the knowledge base. Use the documentation ID returned when the document was added to access its full text."""

    # Construct request model with validation
    try:
        _request = _models.GetKnowledgeBaseContentRequest(
            path=_models.GetKnowledgeBaseContentRequestPath(documentation_id=documentation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retrieve_knowledge_base_document_content: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{documentation_id}/content", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{documentation_id}/content"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retrieve_knowledge_base_document_content")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retrieve_knowledge_base_document_content", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retrieve_knowledge_base_document_content",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_knowledge_base_source_file_url(documentation_id: str = Field(..., description="The unique identifier of the knowledge base document. This ID is provided when the document is initially added to the knowledge base.")) -> dict[str, Any]:
    """Retrieve a signed URL to download the original source file of a document stored in the knowledge base. The URL is temporary and can be used to access the file directly."""

    # Construct request model with validation
    try:
        _request = _models.GetKnowledgeBaseSourceFileUrlRequest(
            path=_models.GetKnowledgeBaseSourceFileUrlRequestPath(documentation_id=documentation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_knowledge_base_source_file_url: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{documentation_id}/source-file-url", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{documentation_id}/source-file-url"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_knowledge_base_source_file_url")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_knowledge_base_source_file_url", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_knowledge_base_source_file_url",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def retrieve_knowledge_base_chunk(
    documentation_id: str = Field(..., description="The unique identifier of the document in the knowledge base. This ID is provided when the document is initially added to the knowledge base."),
    chunk_id: str = Field(..., description="The unique identifier of the specific chunk within the document. Chunks are sequential segments of a document created during RAG processing."),
    embedding_model: Literal["e5_mistral_7b_instruct", "multilingual_e5_large_instruct"] | None = Field(None, description="The embedding model used to generate and retrieve the chunk. Determines the vector representation used for semantic search and retrieval."),
) -> dict[str, Any]:
    """Retrieve a specific chunk from a knowledge base document used by the RAG system. Returns the chunk content and metadata for the specified documentation and chunk identifiers."""

    # Construct request model with validation
    try:
        _request = _models.GetDocumentationChunkFromKnowledgeBaseRequest(
            path=_models.GetDocumentationChunkFromKnowledgeBaseRequestPath(documentation_id=documentation_id, chunk_id=chunk_id),
            query=_models.GetDocumentationChunkFromKnowledgeBaseRequestQuery(embedding_model=embedding_model)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retrieve_knowledge_base_chunk: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{documentation_id}/chunk/{chunk_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{documentation_id}/chunk/{chunk_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retrieve_knowledge_base_chunk")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retrieve_knowledge_base_chunk", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retrieve_knowledge_base_chunk",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversational AI
@mcp.tool()
async def move_knowledge_base_document(
    document_id: str = Field(..., description="The unique identifier of the document to move within the knowledge base."),
    move_to: str | None = Field(None, description="The destination folder identifier where the document should be moved. Omit this parameter to move the document to the root folder."),
) -> dict[str, Any]:
    """Moves a knowledge base document from its current location to a specified folder. If no destination folder is provided, the document is moved to the root folder."""

    # Construct request model with validation
    try:
        _request = _models.PostKnowledgeBaseMoveRouteRequest(
            path=_models.PostKnowledgeBaseMoveRouteRequestPath(document_id=document_id),
            body=_models.PostKnowledgeBaseMoveRouteRequestBody(move_to=move_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_knowledge_base_document: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/knowledge-base/{document_id}/move", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/knowledge-base/{document_id}/move"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_knowledge_base_document")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_knowledge_base_document", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_knowledge_base_document",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Conversational AI
@mcp.tool()
async def move_knowledge_base_entities(
    document_ids: Annotated[list[str], AfterValidator(_check_unique_items)] = Field(..., description="The IDs of the documents or folders to move. Accepts between 1 and 20 entity IDs in a single operation.", min_length=1, max_length=20),
    move_to: str | None = Field(None, description="The destination folder ID where entities will be moved. Omit this parameter to move entities to the root folder."),
) -> dict[str, Any]:
    """Moves multiple documents or folders within a knowledge base to a specified destination folder. If no destination is provided, entities are moved to the root folder."""

    # Construct request model with validation
    try:
        _request = _models.PostKnowledgeBaseBulkMoveRouteRequest(
            body=_models.PostKnowledgeBaseBulkMoveRouteRequestBody(document_ids=document_ids, move_to=move_to)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for move_knowledge_base_entities: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/knowledge-base/bulk-move"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("move_knowledge_base_entities")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("move_knowledge_base_entities", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="move_knowledge_base_entities",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_tools(
    page_size: int | None = Field(None, description="Maximum number of tools to return per request. Must be between 1 and 100.", ge=1, le=100),
    created_by_user_id: str | None = Field(None, description="Filter results to tools created by a specific user. Use '@me' to refer to the authenticated user. Takes precedence over ownership filters."),
    types: list[Literal["webhook", "client", "api_integration_webhook"]] | None = Field(None, description="Filter results to include only tools of specified types. Provide as an array of tool type values."),
    sort_direction: Literal["asc", "desc"] | None = Field(None, description="Order direction for sorting results in ascending or descending sequence."),
    sort_by: Literal["name", "created_at"] | None = Field(None, description="Field to sort results by. Choose between tool name or creation timestamp."),
) -> dict[str, Any]:
    """Retrieve all available tools in the workspace with optional filtering by creator, type, and sorting capabilities."""

    # Construct request model with validation
    try:
        _request = _models.GetToolsRouteRequest(
            query=_models.GetToolsRouteRequestQuery(page_size=page_size, created_by_user_id=created_by_user_id, types=types, sort_direction=sort_direction, sort_by=sort_by)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_tools: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/tools"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_tools")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_tools", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_tools",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def create_tool(tool_config: _models.WebhookToolConfigInput | _models.ClientToolConfigInput | _models.SystemToolConfigInput | _models.McpToolConfigInput = Field(..., description="The tool configuration object that defines the tool's metadata, input parameters, and behavior. This should include the tool name, description, parameter schema, and any other required configuration properties.")) -> dict[str, Any]:
    """Register a new tool in the workspace to make it available for use in conversations. The tool configuration defines its name, description, parameters, and execution behavior."""

    # Construct request model with validation
    try:
        _request = _models.AddToolRouteRequest(
            body=_models.AddToolRouteRequestBody(tool_config=tool_config)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/tools"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_tool", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_tool",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_tool(tool_id: str = Field(..., description="The unique identifier of the tool to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific tool available in the workspace by its ID. Use this to fetch tool details and configuration."""

    # Construct request model with validation
    try:
        _request = _models.GetToolRouteRequest(
            path=_models.GetToolRouteRequestPath(tool_id=tool_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/tools/{tool_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/tools/{tool_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tool", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tool",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def update_tool(
    tool_id: str = Field(..., description="The unique identifier of the tool to be updated."),
    tool_config: _models.WebhookToolConfigInput | _models.ClientToolConfigInput | _models.SystemToolConfigInput | _models.McpToolConfigInput = Field(..., description="The configuration object containing the tool's settings and parameters to be updated."),
) -> dict[str, Any]:
    """Update the configuration of an existing tool in the workspace. Modify tool settings and behavior by providing updated configuration parameters."""

    # Construct request model with validation
    try:
        _request = _models.UpdateToolRouteRequest(
            path=_models.UpdateToolRouteRequestPath(tool_id=tool_id),
            body=_models.UpdateToolRouteRequestBody(tool_config=tool_config)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/tools/{tool_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/tools/{tool_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_tool", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_tool",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_tool(
    tool_id: str = Field(..., description="The unique identifier of the tool to delete."),
    force: bool | None = Field(None, description="Force deletion of the tool even if it is currently used by agents or branches. When enabled, the tool will be automatically removed from all dependent agents and branches."),
) -> dict[str, Any]:
    """Delete a tool from the workspace. Optionally force deletion to remove the tool from all dependent agents and branches regardless of current usage."""

    # Construct request model with validation
    try:
        _request = _models.DeleteToolRouteRequest(
            path=_models.DeleteToolRouteRequestPath(tool_id=tool_id),
            query=_models.DeleteToolRouteRequestQuery(force=force)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/tools/{tool_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/tools/{tool_id}"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_tool", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_tool",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_dependent_agents_tool(
    tool_id: str = Field(..., description="The unique identifier of the tool for which to retrieve dependent agents."),
    page_size: int | None = Field(None, description="Maximum number of agents to return per request. Useful for pagination control.", ge=1, le=100),
) -> dict[str, Any]:
    """Retrieve a paginated list of agents that depend on a specific tool. Use this to understand tool usage and impact across your agent ecosystem."""

    # Construct request model with validation
    try:
        _request = _models.GetToolDependentAgentsRouteRequest(
            path=_models.GetToolDependentAgentsRouteRequestPath(tool_id=tool_id),
            query=_models.GetToolDependentAgentsRouteRequestQuery(page_size=page_size)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_dependent_agents_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/tools/{tool_id}/dependent-agents", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/tools/{tool_id}/dependent-agents"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_dependent_agents_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_dependent_agents_tool", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_dependent_agents_tool",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def create_workspace_secret(
    type_: Literal["new"] = Field(..., alias="type", description="The category or classification of the secret (e.g., API key, password, token, connection string). Determines how the secret is handled and validated."),
    name: str = Field(..., description="A unique identifier for the secret within the workspace. Used to reference the secret in configurations and workflows."),
    value: str = Field(..., description="The sensitive value to be securely stored. This value is encrypted and not returned in subsequent API responses."),
) -> dict[str, Any]:
    """Create a new secret for the Convai workspace. Secrets are securely stored credentials or sensitive values that can be referenced in workspace configurations."""

    # Construct request model with validation
    try:
        _request = _models.CreateSecretRouteRequest(
            body=_models.CreateSecretRouteRequestBody(type_=type_, name=name, value=value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_workspace_secret: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/secrets"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_workspace_secret")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_workspace_secret", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_workspace_secret",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def update_secret(
    secret_id: str = Field(..., description="The unique identifier of the secret to update."),
    type_: Literal["update"] = Field(..., alias="type", description="The type or category of the secret (e.g., API key, password, token)."),
    name: str = Field(..., description="The display name or label for the secret."),
    value: str = Field(..., description="The secret value or credential data to store."),
) -> dict[str, Any]:
    """Update an existing secret in the Convai workspace. Modify the secret's type, name, or value by providing the secret ID and updated details."""

    # Construct request model with validation
    try:
        _request = _models.UpdateSecretRouteRequest(
            path=_models.UpdateSecretRouteRequestPath(secret_id=secret_id),
            body=_models.UpdateSecretRouteRequestBody(type_=type_, name=name, value=value)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_secret: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/secrets/{secret_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/secrets/{secret_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_secret")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_secret", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_secret",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_secret(secret_id: str = Field(..., description="The unique identifier of the secret to delete.")) -> dict[str, Any]:
    """Delete a workspace secret. The secret must not be in use by any active configurations before deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteSecretRouteRequest(
            path=_models.DeleteSecretRouteRequestPath(secret_id=secret_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_secret: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/secrets/{secret_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/secrets/{secret_id}"
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

# Tags: Agents Platform
@mcp.tool()
async def submit_batch_calls(
    call_name: str = Field(..., description="Display name or identifier for this batch call campaign."),
    agent_id: str = Field(..., description="Unique identifier of the conversational AI agent to use for the calls."),
    recipients: list[_models.OutboundCallRecipient] = Field(..., description="List of recipient phone numbers or contact identifiers to call. Order is preserved for sequential processing.", max_length=10000),
    whatsapp_call_permission_request_template_name: str = Field(..., description="Name of the WhatsApp message template to use for requesting call permissions from recipients."),
    whatsapp_call_permission_request_template_language_code: str = Field(..., description="Language code for the WhatsApp permission request template (e.g., en, es, fr). Must match a supported language for the specified template."),
    scheduled_time_unix: int | None = Field(None, description="Unix timestamp (seconds since epoch) for when to start executing the batch calls. If omitted, calls begin immediately."),
    agent_phone_number_id: str | None = Field(None, description="Phone number identifier associated with the agent making the calls. Required for certain call routing configurations."),
    timezone_: str | None = Field(None, alias="timezone", description="Timezone identifier (e.g., America/New_York, Europe/London) for interpreting scheduled_time_unix in local context."),
    target_concurrency_limit: int | None = Field(None, description="Maximum number of simultaneous calls allowed in this batch. When set, this limit takes precedence over workspace or agent-level capacity settings.", ge=1),
) -> dict[str, Any]:
    """Submit a batch call request to schedule multiple outbound calls to recipients. Supports scheduling, concurrency limits, and WhatsApp permission request templates."""

    # Construct request model with validation
    try:
        _request = _models.CreateBatchCallRequest(
            body=_models.CreateBatchCallRequestBody(call_name=call_name, agent_id=agent_id, recipients=recipients, scheduled_time_unix=scheduled_time_unix, agent_phone_number_id=agent_phone_number_id, timezone_=timezone_, target_concurrency_limit=target_concurrency_limit,
                whatsapp_params=_models.CreateBatchCallRequestBodyWhatsappParams(whatsapp_call_permission_request_template_name=whatsapp_call_permission_request_template_name, whatsapp_call_permission_request_template_language_code=whatsapp_call_permission_request_template_language_code))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for submit_batch_calls: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/batch-calling/submit"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("submit_batch_calls")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("submit_batch_calls", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="submit_batch_calls",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_batch_calls(
    limit: int | None = Field(None, description="Maximum number of batch calls to return per request. Controls pagination size for the result set."),
    last_doc: str | None = Field(None, description="Cursor token for pagination. Provide the last document identifier from a previous request to retrieve the next page of results."),
) -> dict[str, Any]:
    """Retrieve all batch calls for the current workspace with pagination support. Use limit and last_doc parameters to control result set size and navigate through pages."""

    # Construct request model with validation
    try:
        _request = _models.GetWorkspaceBatchCallsRequest(
            query=_models.GetWorkspaceBatchCallsRequestQuery(limit=limit, last_doc=last_doc)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_batch_calls: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/batch-calling/workspace"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_batch_calls")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_batch_calls", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_batch_calls",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_batch_call(batch_id: str = Field(..., description="The unique identifier of the batch call to retrieve.")) -> dict[str, Any]:
    """Retrieve detailed information about a specific batch call, including all recipients and their call status."""

    # Construct request model with validation
    try:
        _request = _models.GetBatchCallRequest(
            path=_models.GetBatchCallRequestPath(batch_id=batch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_batch_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/batch-calling/{batch_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/batch-calling/{batch_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_batch_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_batch_call", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_batch_call",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_batch_call(batch_id: str = Field(..., description="The unique identifier of the batch call to delete.")) -> dict[str, Any]:
    """Permanently delete a batch call and all associated recipient records. Note that conversation history will be retained even after deletion."""

    # Construct request model with validation
    try:
        _request = _models.DeleteBatchCallRequest(
            path=_models.DeleteBatchCallRequestPath(batch_id=batch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_batch_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/batch-calling/{batch_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/batch-calling/{batch_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_batch_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_batch_call", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_batch_call",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def cancel_batch_call(batch_id: str = Field(..., description="The unique identifier of the batch call to cancel.")) -> dict[str, Any]:
    """Cancel a running batch call and set all recipients to cancelled status. This operation terminates the batch calling process immediately."""

    # Construct request model with validation
    try:
        _request = _models.CancelBatchCallRequest(
            path=_models.CancelBatchCallRequestPath(batch_id=batch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for cancel_batch_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/batch-calling/{batch_id}/cancel", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/batch-calling/{batch_id}/cancel"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("cancel_batch_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("cancel_batch_call", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="cancel_batch_call",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def retry_batch_call(batch_id: str = Field(..., description="The unique identifier of the batch call to retry. This specifies which batch's failed and no-response recipients should be called again.")) -> dict[str, Any]:
    """Retry a failed batch call by re-attempting to reach recipients who did not respond or experienced call failures. This operation allows you to reprocess a specific batch without creating a new batch call."""

    # Construct request model with validation
    try:
        _request = _models.RetryBatchCallRequest(
            path=_models.RetryBatchCallRequestPath(batch_id=batch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for retry_batch_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/batch-calling/{batch_id}/retry", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/batch-calling/{batch_id}/retry"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("retry_batch_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("retry_batch_call", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="retry_batch_call",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def initiate_outbound_sip_call(
    agent_id: str = Field(..., description="Unique identifier of the AI agent that will handle the outbound call."),
    agent_phone_number_id: str = Field(..., description="Unique identifier of the phone number resource associated with the agent for this call."),
    to_number: str = Field(..., description="The destination phone number to call in E.164 format or standard phone number format."),
    soft_timeout_config: dict[str, Any] | None = Field(None, description="Configuration for soft timeout feedback, allowing the agent to provide immediate responses (e.g., acknowledgments) while processing longer LLM responses."),
    voice_id: str | None = Field(None, description="The voice ID to use for text-to-speech synthesis. Determines the voice characteristics of the agent's spoken responses."),
    stability: float | None = Field(None, description="Controls the consistency of the generated speech, ranging from low variability to high variability in tone and delivery."),
    speed: float | None = Field(None, description="Controls the speed of the generated speech, where lower values slow down speech and higher values speed it up."),
    similarity_boost: float | None = Field(None, description="Controls how closely the generated speech matches the selected voice ID, balancing between voice similarity and speech quality."),
    first_message: str | None = Field(None, description="The initial message the agent will speak when the call connects. If empty, the agent waits for the caller to speak first."),
    language: str | None = Field(None, description="The language code for the agent's automatic speech recognition (ASR) and text-to-speech (TTS) processing."),
    prompt: dict[str, Any] | None = Field(None, description="Configuration for the LLM behavior, including the model selection and system prompt that defines the agent's personality and capabilities."),
    user_id: str | None = Field(None, description="Identifier for the end user or customer participating in this call, used by the agent owner for tracking and user identification."),
    source: Literal["unknown", "android_sdk", "node_js_sdk", "react_native_sdk", "react_sdk", "js_sdk", "python_sdk", "widget", "sip_trunk", "twilio", "genesys", "swift_sdk", "whatsapp", "flutter_sdk", "zendesk_integration", "slack_integration", "template_preview"] | None = Field(None, description="The source or channel through which the call was initiated, used for analytics and tracking purposes."),
    dynamic_variables: dict[str, str | float | int | bool] | None = Field(None, description="Custom variables that can be passed to the agent and used within the prompt or conversation context for dynamic behavior."),
) -> dict[str, Any]:
    """Initiates an outbound call through a SIP trunk with an AI agent. The agent can be configured with custom voice settings, initial messaging, and LLM behavior to handle the conversation."""

    # Construct request model with validation
    try:
        _request = _models.HandleSipTrunkOutboundCallRequest(
            body=_models.HandleSipTrunkOutboundCallRequestBody(agent_id=agent_id, agent_phone_number_id=agent_phone_number_id, to_number=to_number,
                conversation_initiation_client_data=_models.HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientData(user_id=user_id, dynamic_variables=dynamic_variables,
                    conversation_config_override=_models.HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverride(turn=_models.HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTurn(soft_timeout_config=soft_timeout_config) if any(v is not None for v in [soft_timeout_config]) else None,
                        tts=_models.HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideTts(voice_id=voice_id, stability=stability, speed=speed, similarity_boost=similarity_boost) if any(v is not None for v in [voice_id, stability, speed, similarity_boost]) else None,
                        agent=_models.HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataConversationConfigOverrideAgent(first_message=first_message, language=language, prompt=prompt) if any(v is not None for v in [first_message, language, prompt]) else None) if any(v is not None for v in [soft_timeout_config, voice_id, stability, speed, similarity_boost, first_message, language, prompt]) else None,
                    source_info=_models.HandleSipTrunkOutboundCallRequestBodyConversationInitiationClientDataSourceInfo(source=source) if any(v is not None for v in [source]) else None) if any(v is not None for v in [soft_timeout_config, voice_id, stability, speed, similarity_boost, first_message, language, prompt, user_id, source, dynamic_variables]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for initiate_outbound_sip_call: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/sip-trunk/outbound-call"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("initiate_outbound_sip_call")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("initiate_outbound_sip_call", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="initiate_outbound_sip_call",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_mcp_servers() -> dict[str, Any]:
    """Retrieve all MCP server configurations available in the workspace. Returns a list of configured MCP servers with their settings and connection details."""

    # Extract parameters for API call
    _http_path = "/v1/convai/mcp-servers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_mcp_servers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_mcp_servers", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_mcp_servers",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def register_mcp_server(
    url: str | _models.ConvAiSecretLocator = Field(..., description="The HTTPS endpoint URL where the MCP server is hosted. If the URL contains sensitive credentials, store it as a workspace secret reference instead of a plain string."),
    name: str = Field(..., description="Display name for this MCP server configuration. Used to identify the server in your workspace and in agent logs."),
    approval_policy: Literal["auto_approve_all", "require_approval_all", "require_approval_per_tool"] | None = Field(None, description="Approval policy that determines whether tools from this server require manual approval before execution. Choose 'auto_approve_all' to execute immediately, 'require_approval_all' to require approval for every tool call, or 'require_approval_per_tool' to configure approval on a per-tool basis."),
    tool_approval_hashes: list[_models.McpToolApprovalHash] | None = Field(None, description="List of tool approval hashes that are pre-approved for execution. Only used when approval_policy is set to 'require_approval_per_tool'. Each hash corresponds to a specific tool that should skip approval."),
    transport: Literal["SSE", "STREAMABLE_HTTP"] | None = Field(None, description="Communication protocol used to connect to the MCP server. SSE (Server-Sent Events) is the default for real-time streaming, while STREAMABLE_HTTP is an alternative transport option."),
    secret_token: _models.ConvAiSecretLocator | _models.ConvAiUserSecretDbModel | None = Field(None, description="Authorization token sent in the request header to authenticate with the MCP server. Store sensitive tokens as workspace secrets rather than plain text."),
    request_headers: dict[str, str | _models.ConvAiSecretLocator | _models.ConvAiDynamicVariable | _models.ConvAiEnvVarLocator] | None = Field(None, description="Custom HTTP headers to include in all requests to the MCP server. Useful for passing additional authentication credentials or metadata required by the server."),
    auth_connection: _models.AuthConnectionLocator | _models.EnvironmentAuthConnectionLocator | None = Field(None, description="Reference to a pre-configured authentication connection in your workspace. Use this to leverage existing auth credentials instead of providing token or headers directly."),
    description: str | None = Field(None, description="Optional description explaining the purpose and capabilities of this MCP server."),
    force_pre_tool_speech: bool | None = Field(None, description="If enabled, the agent will speak before executing any tool from this server, allowing the user to hear what action is about to be taken."),
    disable_interruptions: bool | None = Field(None, description="If enabled, users cannot interrupt the agent while any tool from this server is executing. Useful for critical operations that must complete without interruption."),
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="Predefined sound effect to play when tools from this server begin execution. Helps provide audio feedback during tool execution."),
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field(None, description="Controls when the tool call sound plays: 'auto' plays the sound only when appropriate, 'always' plays it every time a tool executes."),
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field(None, description="Execution timing for tools from this server: 'immediate' runs the tool right away, 'post_tool_speech' waits for the agent to finish speaking first, 'async' runs in the background without blocking the agent."),
    tool_config_overrides: list[_models.McpToolConfigOverride] | None = Field(None, description="List of per-tool configuration overrides that customize behavior for specific tools, superseding the server-level defaults. Each override targets a tool by identifier and applies custom settings."),
    disable_compression: bool | None = Field(None, description="If enabled, HTTP compression is disabled for requests to this MCP server. Enable this only if the server does not properly support compressed responses."),
) -> dict[str, Any]:
    """Register a new MCP (Model Context Protocol) server in your workspace to enable tool execution through that server. Configure authentication, approval policies, and execution behavior for all tools provided by this server."""

    # Construct request model with validation
    try:
        _request = _models.CreateMcpServerRouteRequest(
            body=_models.CreateMcpServerRouteRequestBody(config=_models.CreateMcpServerRouteRequestBodyConfig(approval_policy=approval_policy, tool_approval_hashes=tool_approval_hashes, transport=transport, url=url, secret_token=secret_token, request_headers=request_headers, auth_connection=auth_connection, name=name, description=description, force_pre_tool_speech=force_pre_tool_speech, disable_interruptions=disable_interruptions, tool_call_sound=tool_call_sound, tool_call_sound_behavior=tool_call_sound_behavior, execution_mode=execution_mode, tool_config_overrides=tool_config_overrides, disable_compression=disable_compression))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for register_mcp_server: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/mcp-servers"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("register_mcp_server")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("register_mcp_server", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="register_mcp_server",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_mcp_server(mcp_server_id: str = Field(..., description="The unique identifier of the MCP server to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific MCP server configuration from your workspace. Use this to access detailed settings and metadata for a configured MCP server."""

    # Construct request model with validation
    try:
        _request = _models.GetMcpRouteRequest(
            path=_models.GetMcpRouteRequestPath(mcp_server_id=mcp_server_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_mcp_server: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/mcp-servers/{mcp_server_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/mcp-servers/{mcp_server_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_mcp_server")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_mcp_server", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_mcp_server",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def configure_mcp_server(
    mcp_server_id: str = Field(..., description="The unique identifier of the MCP server to configure."),
    secret_id: str = Field(..., description="The secret identifier for credentials or API keys used to authenticate with this MCP server."),
    approval_policy: Literal["auto_approve_all", "require_approval_all", "require_approval_per_tool"] | None = Field(None, description="The approval workflow mode for tool execution from this server. Controls whether tools require manual approval before execution."),
    force_pre_tool_speech: bool | None = Field(None, description="When enabled, forces the system to speak tool descriptions aloud before execution, overriding the server's default setting."),
    disable_interruptions: bool | None = Field(None, description="When enabled, prevents user interruptions during tool execution, overriding the server's default setting."),
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="The sound effect to play during tool execution for all tools from this server."),
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field(None, description="Controls when the tool call sound plays during execution."),
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field(None, description="Determines the execution timing for tools from this server. Immediate executes right away, post_tool_speech waits for narration, and async runs in the background."),
    request_headers: dict[str, str | _models.ConvAiSecretLocator | _models.ConvAiDynamicVariable | _models.ConvAiEnvVarLocator] | None = Field(None, description="HTTP headers to include in all requests sent to this MCP server, such as custom authentication or tracking headers."),
    disable_compression: bool | None = Field(None, description="When enabled, disables HTTP compression for requests to this MCP server to reduce processing overhead."),
    auth_connection: _models.AuthConnectionLocator | _models.EnvironmentAuthConnectionLocator | None = Field(None, description="Optional authentication connection configuration for establishing secure communication with this MCP server."),
) -> dict[str, Any]:
    """Update configuration settings for an MCP server, including approval policies, audio behavior, execution modes, and authentication. Changes apply to all tools provided by this server."""

    # Construct request model with validation
    try:
        _request = _models.UpdateMcpServerConfigRouteRequest(
            path=_models.UpdateMcpServerConfigRouteRequestPath(mcp_server_id=mcp_server_id),
            body=_models.UpdateMcpServerConfigRouteRequestBody(approval_policy=approval_policy, force_pre_tool_speech=force_pre_tool_speech, disable_interruptions=disable_interruptions, tool_call_sound=tool_call_sound, tool_call_sound_behavior=tool_call_sound_behavior, execution_mode=execution_mode, request_headers=request_headers, disable_compression=disable_compression, auth_connection=auth_connection,
                secret_token=_models.UpdateMcpServerConfigRouteRequestBodySecretToken(secret_id=secret_id))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for configure_mcp_server: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/mcp-servers/{mcp_server_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/mcp-servers/{mcp_server_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("configure_mcp_server")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("configure_mcp_server", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="configure_mcp_server",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_mcp_server(mcp_server_id: str = Field(..., description="The unique identifier of the MCP server to delete.")) -> dict[str, Any]:
    """Remove a specific MCP server configuration from the workspace. This action permanently deletes the server and its associated settings."""

    # Construct request model with validation
    try:
        _request = _models.DeleteMcpServerRouteRequest(
            path=_models.DeleteMcpServerRouteRequestPath(mcp_server_id=mcp_server_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_mcp_server: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/mcp-servers/{mcp_server_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/mcp-servers/{mcp_server_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_mcp_server")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_mcp_server", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_mcp_server",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_mcp_server_tools(mcp_server_id: str = Field(..., description="The unique identifier of the MCP server for which to retrieve available tools.")) -> dict[str, Any]:
    """Retrieve all tools available for a specific MCP server configuration. Returns a complete list of tools that can be invoked through the specified MCP server."""

    # Construct request model with validation
    try:
        _request = _models.ListMcpServerToolsRouteRequest(
            path=_models.ListMcpServerToolsRouteRequestPath(mcp_server_id=mcp_server_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_mcp_server_tools: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/mcp-servers/{mcp_server_id}/tools", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/mcp-servers/{mcp_server_id}/tools"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_mcp_server_tools")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_mcp_server_tools", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_mcp_server_tools",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def approve_mcp_server_tool(
    mcp_server_id: str = Field(..., description="The unique identifier of the MCP Server to which the tool approval applies."),
    tool_name: str = Field(..., description="The name of the MCP tool being approved for use."),
    tool_description: str = Field(..., description="A human-readable description of what the MCP tool does and its purpose."),
    input_schema: dict[str, Any] | None = Field(None, description="The input schema that defines the parameters and structure expected by the MCP tool, as defined on the MCP server before any ElevenLabs processing."),
    approval_policy: Literal["auto_approved", "requires_approval"] | None = Field(None, description="The approval policy that determines whether this tool requires explicit approval before each use or is automatically approved."),
) -> dict[str, Any]:
    """Grant approval for a specific MCP tool when the server is configured to use per-tool approval mode. This enables fine-grained control over which tools are available for use."""

    # Construct request model with validation
    try:
        _request = _models.AddMcpServerToolApprovalRouteRequest(
            path=_models.AddMcpServerToolApprovalRouteRequestPath(mcp_server_id=mcp_server_id),
            body=_models.AddMcpServerToolApprovalRouteRequestBody(tool_name=tool_name, tool_description=tool_description, input_schema=input_schema, approval_policy=approval_policy)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for approve_mcp_server_tool: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/mcp-servers/{mcp_server_id}/tool-approvals", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/mcp-servers/{mcp_server_id}/tool-approvals"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("approve_mcp_server_tool")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("approve_mcp_server_tool", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="approve_mcp_server_tool",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def revoke_mcp_server_tool_approval(
    mcp_server_id: str = Field(..., description="The unique identifier of the MCP Server from which to revoke tool approval."),
    tool_name: str = Field(..., description="The name of the MCP tool to revoke approval for."),
) -> dict[str, Any]:
    """Revoke approval for a specific MCP tool on a server when using per-tool approval mode. This removes the tool from the approved list, preventing its use until re-approved."""

    # Construct request model with validation
    try:
        _request = _models.RemoveMcpServerToolApprovalRouteRequest(
            path=_models.RemoveMcpServerToolApprovalRouteRequestPath(mcp_server_id=mcp_server_id, tool_name=tool_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for revoke_mcp_server_tool_approval: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/mcp-servers/{mcp_server_id}/tool-approvals/{tool_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/mcp-servers/{mcp_server_id}/tool-approvals/{tool_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("revoke_mcp_server_tool_approval")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("revoke_mcp_server_tool_approval", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="revoke_mcp_server_tool_approval",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def create_tool_config_override(
    mcp_server_id: str = Field(..., description="The unique identifier of the MCP server containing the tool to configure."),
    tool_name: str = Field(..., description="The exact name of the MCP tool within the server to apply these configuration overrides to."),
    force_pre_tool_speech: bool | None = Field(None, description="When enabled, forces the system to speak a message before executing this tool, overriding the server's default setting."),
    disable_interruptions: bool | None = Field(None, description="When enabled, prevents user interruptions during this tool's execution, overriding the server's default setting."),
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="The sound effect to play when this tool is invoked, overriding the server's default sound setting."),
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field(None, description="Controls when the tool call sound plays: automatically based on context or always when the tool executes."),
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field(None, description="Determines when this tool executes relative to speech output: immediately, after tool speech completes, or asynchronously."),
    assignments: list[_models.DynamicVariableAssignment] | None = Field(None, description="Dynamic variable assignments that will be available to this MCP tool during execution. Order is preserved as specified."),
    input_overrides: dict[str, _models.ConstantSchemaOverride | _models.DynamicVariableSchemaOverride | _models.LlmSchemaOverride] | None = Field(None, description="JSON path mappings to override specific input parameters for this tool, allowing selective input transformation or substitution."),
) -> dict[str, Any]:
    """Create configuration overrides for a specific MCP tool, allowing fine-grained control over tool execution behavior, audio feedback, and input handling independent of server-level settings."""

    # Construct request model with validation
    try:
        _request = _models.AddMcpToolConfigOverrideRouteRequest(
            path=_models.AddMcpToolConfigOverrideRouteRequestPath(mcp_server_id=mcp_server_id),
            body=_models.AddMcpToolConfigOverrideRouteRequestBody(force_pre_tool_speech=force_pre_tool_speech, disable_interruptions=disable_interruptions, tool_call_sound=tool_call_sound, tool_call_sound_behavior=tool_call_sound_behavior, execution_mode=execution_mode, assignments=assignments, input_overrides=input_overrides, tool_name=tool_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_tool_config_override: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/mcp-servers/{mcp_server_id}/tool-configs", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/mcp-servers/{mcp_server_id}/tool-configs"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_tool_config_override")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_tool_config_override", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_tool_config_override",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_tool_config_override(
    mcp_server_id: str = Field(..., description="The unique identifier of the MCP server containing the tool."),
    tool_name: str = Field(..., description="The name of the MCP tool for which to retrieve configuration overrides."),
) -> dict[str, Any]:
    """Retrieve configuration overrides for a specific MCP tool within an MCP server. Use this to fetch customized tool settings that differ from default configurations."""

    # Construct request model with validation
    try:
        _request = _models.GetMcpToolConfigOverrideRouteRequest(
            path=_models.GetMcpToolConfigOverrideRouteRequestPath(mcp_server_id=mcp_server_id, tool_name=tool_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_tool_config_override: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/mcp-servers/{mcp_server_id}/tool-configs/{tool_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/mcp-servers/{mcp_server_id}/tool-configs/{tool_name}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_tool_config_override")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_tool_config_override", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_tool_config_override",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def override_mcp_tool_config(
    mcp_server_id: str = Field(..., description="The unique identifier of the MCP server containing the tool to configure."),
    tool_name: str = Field(..., description="The name of the MCP tool whose configuration overrides should be updated."),
    force_pre_tool_speech: bool | None = Field(None, description="Force the system to speak before executing this tool, overriding the server's default setting."),
    disable_interruptions: bool | None = Field(None, description="Prevent user interruptions during this tool's execution, overriding the server's default setting."),
    tool_call_sound: Literal["typing", "elevator1", "elevator2", "elevator3", "elevator4"] | None = Field(None, description="The sound to play when this tool is invoked, overriding the server's default sound."),
    tool_call_sound_behavior: Literal["auto", "always"] | None = Field(None, description="Control when the tool call sound plays: automatically based on context or always when the tool executes."),
    execution_mode: Literal["immediate", "post_tool_speech", "async"] | None = Field(None, description="Specify when this tool executes: immediately, after speech completes, or asynchronously."),
    assignments: list[_models.DynamicVariableAssignment] | None = Field(None, description="Dynamic variable assignments to pass to this MCP tool during execution. Order is preserved if significant for the tool's logic."),
    input_overrides: dict[str, _models.ConstantSchemaOverride | _models.DynamicVariableSchemaOverride | _models.LlmSchemaOverride] | None = Field(None, description="JSON path mappings that override specific input fields for this tool, allowing selective parameter customization."),
) -> dict[str, Any]:
    """Override configuration settings for a specific MCP tool, allowing fine-grained control over behavior like speech timing, interruptions, and execution mode independent of server-level defaults."""

    # Construct request model with validation
    try:
        _request = _models.UpdateMcpToolConfigOverrideRouteRequest(
            path=_models.UpdateMcpToolConfigOverrideRouteRequestPath(mcp_server_id=mcp_server_id, tool_name=tool_name),
            body=_models.UpdateMcpToolConfigOverrideRouteRequestBody(force_pre_tool_speech=force_pre_tool_speech, disable_interruptions=disable_interruptions, tool_call_sound=tool_call_sound, tool_call_sound_behavior=tool_call_sound_behavior, execution_mode=execution_mode, assignments=assignments, input_overrides=input_overrides)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for override_mcp_tool_config: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/mcp-servers/{mcp_server_id}/tool-configs/{tool_name}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/mcp-servers/{mcp_server_id}/tool-configs/{tool_name}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("override_mcp_tool_config")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("override_mcp_tool_config", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="override_mcp_tool_config",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_whatsapp_account(phone_number_id: str = Field(..., description="The unique identifier for the WhatsApp phone number associated with the account.")) -> dict[str, Any]:
    """Retrieve details for a specific WhatsApp account using its phone number ID. Returns account configuration and status information."""

    # Construct request model with validation
    try:
        _request = _models.GetWhatsappAccountRequest(
            path=_models.GetWhatsappAccountRequestPath(phone_number_id=phone_number_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_whatsapp_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/whatsapp-accounts/{phone_number_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/whatsapp-accounts/{phone_number_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_whatsapp_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_whatsapp_account", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_whatsapp_account",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def update_whatsapp_account(
    phone_number_id: str = Field(..., description="The unique identifier for the WhatsApp phone number account to update."),
    assigned_agent_id: str | None = Field(None, description="The ID of the agent to assign to this WhatsApp account for handling conversations."),
    enable_messaging: bool | None = Field(None, description="Enable or disable messaging functionality for this WhatsApp account."),
    enable_audio_message_response: bool | None = Field(None, description="Enable or disable automatic audio message response capability for this WhatsApp account."),
) -> dict[str, Any]:
    """Update configuration settings for a WhatsApp account, including agent assignment and messaging capabilities. Changes take effect immediately."""

    # Construct request model with validation
    try:
        _request = _models.UpdateWhatsappAccountRequest(
            path=_models.UpdateWhatsappAccountRequestPath(phone_number_id=phone_number_id),
            body=_models.UpdateWhatsappAccountRequestBody(assigned_agent_id=assigned_agent_id, enable_messaging=enable_messaging, enable_audio_message_response=enable_audio_message_response)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_whatsapp_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/whatsapp-accounts/{phone_number_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/whatsapp-accounts/{phone_number_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_whatsapp_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_whatsapp_account", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_whatsapp_account",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_whatsapp_account(phone_number_id: str = Field(..., description="The unique identifier for the WhatsApp phone number account to delete.")) -> dict[str, Any]:
    """Permanently delete a WhatsApp account and remove it from the ConvAI platform. This action cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeleteWhatsappAccountRequest(
            path=_models.DeleteWhatsappAccountRequestPath(phone_number_id=phone_number_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_whatsapp_account: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/whatsapp-accounts/{phone_number_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/whatsapp-accounts/{phone_number_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_whatsapp_account")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_whatsapp_account", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_whatsapp_account",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_whatsapp_accounts() -> dict[str, Any]:
    """Retrieve all WhatsApp accounts associated with your ConvAI workspace. This operation returns a complete list of configured WhatsApp business accounts available for messaging and automation."""

    # Extract parameters for API call
    _http_path = "/v1/convai/whatsapp-accounts"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_whatsapp_accounts")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_whatsapp_accounts", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_whatsapp_accounts",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_agent_branches(
    agent_id: str = Field(..., description="The unique identifier of the agent whose branches should be retrieved."),
    include_archived: bool | None = Field(None, description="Whether to include archived branches in the results. Defaults to excluding archived branches."),
    limit: int | None = Field(None, description="Maximum number of branches to return in the response. Must be between 2 and 100 inclusive.", le=100, gt=1),
) -> dict[str, Any]:
    """Retrieves a list of branches for a specified agent. Optionally includes archived branches and supports result limiting."""

    # Construct request model with validation
    try:
        _request = _models.GetBranchesRouteRequest(
            path=_models.GetBranchesRouteRequestPath(agent_id=agent_id),
            query=_models.GetBranchesRouteRequestQuery(include_archived=include_archived, limit=limit)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_agent_branches: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/branches", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/branches"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("list_agent_branches")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("list_agent_branches", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="list_agent_branches",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def create_agent_branch(
    agent_id: str = Field(..., description="The unique identifier of the agent to create a branch for."),
    parent_version_id: str = Field(..., description="The version ID of the main branch to use as the base for this new branch."),
    name: str = Field(..., description="The name of the new branch. Must be unique within the agent and cannot exceed 140 characters.", max_length=140),
    description: str = Field(..., description="A description of the branch's purpose or contents. Cannot exceed 4096 characters.", max_length=4096),
    conversation_config: dict[str, Any] | None = Field(None, description="Optional configuration changes to apply to conversation settings for this branch."),
    platform_settings: dict[str, Any] | None = Field(None, description="Optional platform-specific settings changes to apply to this branch."),
    edges: dict[str, _models.WorkflowEdgeModelInput] | None = Field(None, description="Optional edge definitions for the agent's conversation flow in this branch."),
    nodes: dict[str, _models.WorkflowStartNodeModelInput | _models.WorkflowEndNodeModelInput | _models.WorkflowPhoneNumberNodeModelInput | _models.WorkflowOverrideAgentNodeModelInput | _models.WorkflowStandaloneAgentNodeModelInput | _models.WorkflowToolNodeModelInput] | None = Field(None, description="Optional node definitions for the agent's conversation flow in this branch.", min_length=1),
) -> dict[str, Any]:
    """Create a new branch from a specified version of an agent's main branch. Branches allow you to develop and test agent configurations independently before merging changes back to the main branch."""

    # Construct request model with validation
    try:
        _request = _models.CreateBranchRouteRequest(
            path=_models.CreateBranchRouteRequestPath(agent_id=agent_id),
            body=_models.CreateBranchRouteRequestBody(parent_version_id=parent_version_id, name=name, description=description, conversation_config=conversation_config, platform_settings=platform_settings,
                workflow=_models.CreateBranchRouteRequestBodyWorkflow(edges=edges, nodes=nodes) if any(v is not None for v in [edges, nodes]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_agent_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/branches", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/branches"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_agent_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_agent_branch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_agent_branch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def get_agent_branch(
    agent_id: str = Field(..., description="The unique identifier of the agent that contains the branch."),
    branch_id: str = Field(..., description="The unique identifier of the branch to retrieve."),
) -> dict[str, Any]:
    """Retrieve detailed information about a specific agent branch, including its configuration and settings."""

    # Construct request model with validation
    try:
        _request = _models.GetBranchRouteRequest(
            path=_models.GetBranchRouteRequestPath(agent_id=agent_id, branch_id=branch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_agent_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/branches/{branch_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/branches/{branch_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_agent_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_agent_branch", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_agent_branch",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def update_branch(
    agent_id: str = Field(..., description="The unique identifier of the agent that owns the branch."),
    branch_id: str = Field(..., description="The unique identifier of the branch to update."),
    name: str | None = Field(None, description="New name for the branch. Must be unique within the agent.", min_length=1, max_length=140),
    is_archived: bool | None = Field(None, description="Whether to archive the branch. Archived branches are hidden from normal operations but retain their data."),
    protection_status: Literal["writer_perms_required", "admin_perms_required"] | None = Field(None, description="The access control level required to modify the branch."),
) -> dict[str, Any]:
    """Update agent branch properties including name, archival status, and access control permissions. Allows modification of branch configuration and protection levels."""

    # Construct request model with validation
    try:
        _request = _models.UpdateBranchRouteRequest(
            path=_models.UpdateBranchRouteRequestPath(agent_id=agent_id, branch_id=branch_id),
            body=_models.UpdateBranchRouteRequestBody(name=name, is_archived=is_archived, protection_status=protection_status)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/branches/{branch_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/branches/{branch_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_branch", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_branch",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def merge_branch(
    agent_id: str = Field(..., description="The unique identifier of the agent containing the branches to merge."),
    source_branch_id: str = Field(..., description="The unique identifier of the source branch to merge from."),
    target_branch_id: str = Field(..., description="The unique identifier of the target branch to merge into. Must be the main branch."),
    archive_source_branch: bool | None = Field(None, description="Whether to archive the source branch after a successful merge."),
) -> dict[str, Any]:
    """Merge a source branch into a target branch, optionally archiving the source branch after the merge completes."""

    # Construct request model with validation
    try:
        _request = _models.MergeBranchIntoTargetRequest(
            path=_models.MergeBranchIntoTargetRequestPath(agent_id=agent_id, source_branch_id=source_branch_id),
            query=_models.MergeBranchIntoTargetRequestQuery(target_branch_id=target_branch_id),
            body=_models.MergeBranchIntoTargetRequestBody(archive_source_branch=archive_source_branch)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for merge_branch: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/branches/{source_branch_id}/merge", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/branches/{source_branch_id}/merge"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("merge_branch")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("merge_branch", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="merge_branch",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def deploy_agent(
    agent_id: str = Field(..., description="The unique identifier of the agent for which to create or update deployments."),
    requests: list[_models.AgentDeploymentRequestItem] = Field(..., description="An ordered list of deployment configurations, each specifying a branch and its traffic allocation strategy. Order may affect deployment precedence."),
) -> dict[str, Any]:
    """Create or update deployments for an agent, specifying which branches to deploy and how to distribute traffic across them."""

    # Construct request model with validation
    try:
        _request = _models.CreateAgentDeploymentRouteRequest(
            path=_models.CreateAgentDeploymentRouteRequestPath(agent_id=agent_id),
            body=_models.CreateAgentDeploymentRouteRequestBody(deployment_request=_models.CreateAgentDeploymentRouteRequestBodyDeploymentRequest(requests=requests))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for deploy_agent: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/deployments", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/deployments"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("deploy_agent")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("deploy_agent", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="deploy_agent",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def create_agent_draft(
    agent_id: str = Field(..., description="The unique identifier of the agent for which to create a draft."),
    branch_id: str = Field(..., description="The unique identifier of the agent branch where the draft will be created."),
    conversation_config: dict[str, Any] = Field(..., description="Configuration object defining conversation behavior, including parameters for dialogue flow, response handling, and interaction settings."),
    platform_settings: dict[str, Any] = Field(..., description="Configuration object specifying platform-specific settings such as deployment targets, feature flags, and integration parameters."),
    name: str = Field(..., description="A human-readable name for the draft to help identify and organize different versions."),
    edges: dict[str, _models.WorkflowEdgeModelInput] | None = Field(None, description="Workflow connections defining how nodes interact. Each edge represents a transition or data flow between nodes in the agent's workflow graph."),
    nodes: dict[str, _models.WorkflowStartNodeModelInput | _models.WorkflowEndNodeModelInput | _models.WorkflowPhoneNumberNodeModelInput | _models.WorkflowOverrideAgentNodeModelInput | _models.WorkflowStandaloneAgentNodeModelInput | _models.WorkflowToolNodeModelInput] | None = Field(None, description="Workflow nodes representing individual components or steps in the agent's logic. Nodes define actions, decision points, or processing stages.", min_length=1),
    tags: list[str] | None = Field(None, description="Optional labels for categorizing and filtering the agent draft. Tags enable organization by use case, domain, or other classification criteria."),
) -> dict[str, Any]:
    """Create a new draft version of an agent with specified configuration, platform settings, and workflow structure. Drafts allow you to develop and test agent changes before publishing."""

    # Construct request model with validation
    try:
        _request = _models.CreateAgentDraftRouteRequest(
            path=_models.CreateAgentDraftRouteRequestPath(agent_id=agent_id),
            query=_models.CreateAgentDraftRouteRequestQuery(branch_id=branch_id),
            body=_models.CreateAgentDraftRouteRequestBody(conversation_config=conversation_config, platform_settings=platform_settings, name=name, tags=tags,
                workflow=_models.CreateAgentDraftRouteRequestBodyWorkflow(edges=edges, nodes=nodes) if any(v is not None for v in [edges, nodes]) else None)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_agent_draft: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/drafts", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/drafts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_agent_draft")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_agent_draft", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_agent_draft",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def delete_agent_draft(
    agent_id: str = Field(..., description="The unique identifier of the agent whose draft should be deleted."),
    branch_id: str = Field(..., description="The identifier of the agent branch containing the draft to delete."),
) -> dict[str, Any]:
    """Delete a draft version of an agent. This removes the unpublished changes associated with the specified agent and branch."""

    # Construct request model with validation
    try:
        _request = _models.DeleteAgentDraftRouteRequest(
            path=_models.DeleteAgentDraftRouteRequestPath(agent_id=agent_id),
            query=_models.DeleteAgentDraftRouteRequestQuery(branch_id=branch_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for delete_agent_draft: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/agents/{agent_id}/drafts", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/agents/{agent_id}/drafts"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("delete_agent_draft")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("delete_agent_draft", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="delete_agent_draft",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def list_environment_variables(
    page_size: int | None = Field(None, description="Maximum number of environment variables to return per request. Useful for pagination when working with large variable sets.", ge=1, le=100),
    label: str | None = Field(None, description="Filter results to return only environment variables matching this exact label value."),
    type_: Literal["string", "secret", "auth_connection"] | None = Field(None, alias="type", description="Filter results by variable type to narrow down to specific categories of environment variables."),
) -> dict[str, Any]:
    """Retrieve all environment variables configured in your workspace with optional filtering by label or variable type. Results are paginated for efficient data retrieval."""

    # Construct request model with validation
    try:
        _request = _models.ListEnvironmentVariablesRequest(
            query=_models.ListEnvironmentVariablesRequestQuery(page_size=page_size, label=label, type_=type_)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for list_environment_variables: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/environment-variables"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
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
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def create_environment_variable(
    type_: Literal["string"] = Field(..., alias="type", description="The type or category of the environment variable, determining how it will be processed and used within the workspace."),
    label: str = Field(..., description="A unique identifier label for this environment variable within the workspace. Used to reference the variable in configurations and deployments."),
    values: dict[str, str] = Field(..., description="A mapping of environment names to their corresponding values. Must include at least a 'production' key with its associated value for production deployments."),
) -> dict[str, Any]:
    """Create a new environment variable for the workspace with environment-specific values. Environment variables enable dynamic configuration management across different deployment environments."""

    # Construct request model with validation
    try:
        _request = _models.CreateEnvironmentVariableRequest(
            body=_models.CreateEnvironmentVariableRequestBody(type_=type_, label=label, values=values)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_environment_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/convai/environment-variables"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
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

# Tags: Agents Platform
@mcp.tool()
async def get_environment_variable(env_var_id: str = Field(..., description="The unique identifier of the environment variable to retrieve.")) -> dict[str, Any]:
    """Retrieve a specific environment variable by its unique identifier. Use this to fetch configuration values stored in your environment."""

    # Construct request model with validation
    try:
        _request = _models.GetEnvironmentVariableRequest(
            path=_models.GetEnvironmentVariableRequestPath(env_var_id=env_var_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_environment_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/environment-variables/{env_var_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/environment-variables/{env_var_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_environment_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_environment_variable", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_environment_variable",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: Agents Platform
@mcp.tool()
async def update_environment_variable(
    env_var_id: str = Field(..., description="The unique identifier of the environment variable to update."),
    values: dict[str, str | _models.EnvironmentVariableSecretValueRequest | _models.EnvironmentVariableAuthConnectionValueRequest] = Field(..., description="A mapping of environment names to their values. Set an environment's value to null to remove it from the variable (production environment is required and cannot be removed)."),
) -> dict[str, Any]:
    """Update an environment variable's values across different environments. Set values to null to remove a specific environment (production environment cannot be removed)."""

    # Construct request model with validation
    try:
        _request = _models.UpdateEnvironmentVariableRequest(
            path=_models.UpdateEnvironmentVariableRequestPath(env_var_id=env_var_id),
            body=_models.UpdateEnvironmentVariableRequestBody(values=values)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_environment_variable: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/convai/environment-variables/{env_var_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/convai/environment-variables/{env_var_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_environment_variable")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_environment_variable", "PATCH", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_environment_variable",
        method="PATCH",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: music-generation
@mcp.tool()
async def generate_composition_plan(
    prompt: str = Field(..., description="Text prompt describing the desired composition, musical style, mood, and any specific creative direction.", max_length=4100),
    positive_global_styles: list[str] = Field(..., description="Array of musical styles and directions that should be emphasized throughout the entire composition. Specify in English for optimal results.", max_length=50),
    negative_global_styles: list[str] = Field(..., description="Array of musical styles and directions to exclude from the entire composition. Specify in English for optimal results.", max_length=50),
    sections: list[_models.SongSection] = Field(..., description="Array of song sections defining the structure and progression of the composition. Order matters and determines the sequence of sections in the final output.", max_length=30),
    music_length_ms: int | None = Field(None, description="Target duration for the composition in milliseconds. If omitted, the model will automatically determine an appropriate length based on the prompt.", ge=3000, le=600000),
    model_id: Literal["music_v1"] | None = Field(None, description="The AI model version to use for generating the composition plan."),
) -> dict[str, Any]:
    """Generate a detailed composition plan from a text prompt, specifying musical structure, styles, and duration for music generation."""

    # Construct request model with validation
    try:
        _request = _models.ComposePlanRequest(
            body=_models.ComposePlanRequestBody(prompt=prompt, music_length_ms=music_length_ms, model_id=model_id,
                source_composition_plan=_models.ComposePlanRequestBodySourceCompositionPlan(positive_global_styles=positive_global_styles, negative_global_styles=negative_global_styles, sections=sections))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for generate_composition_plan: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/music/plan"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("generate_composition_plan")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("generate_composition_plan", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="generate_composition_plan",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: music-generation
@mcp.tool()
async def compose_song(
    music_prompt_positive_global_styles: list[str] = Field(..., alias="music_promptPositive_global_styles", description="Array of musical styles and directions to include throughout the entire song. Specify in English for optimal results.", max_length=50),
    composition_plan_positive_global_styles: list[str] = Field(..., alias="composition_planPositive_global_styles", description="Array of musical styles and directions to include throughout the entire song. Specify in English for optimal results.", max_length=50),
    music_prompt_negative_global_styles: list[str] = Field(..., alias="music_promptNegative_global_styles", description="Array of musical styles and directions to exclude from the entire song. Specify in English for optimal results.", max_length=50),
    composition_plan_negative_global_styles: list[str] = Field(..., alias="composition_planNegative_global_styles", description="Array of musical styles and directions to exclude from the entire song. Specify in English for optimal results.", max_length=50),
    music_prompt_sections: list[_models.SongSection] = Field(..., alias="music_promptSections", description="Ordered array defining the song structure, including individual sections with their characteristics and durations.", max_length=30),
    composition_plan_sections: list[_models.SongSection] = Field(..., alias="composition_planSections", description="Ordered array defining the song structure, including individual sections with their characteristics and durations.", max_length=30),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio output format specified as codec_sample_rate_bitrate (e.g., mp3 at 44.1kHz with 128kbps bitrate). Higher bitrates and PCM formats require appropriate subscription tier."),
    prompt: str | None = Field(None, description="Simple text description of the song to generate. Cannot be combined with composition_plan. Use this for quick, straightforward song generation.", max_length=4100),
    music_length_ms: int | None = Field(None, description="Target song duration in milliseconds. Only used with prompt-based generation. The model will adjust to fit this duration if provided.", ge=3000, le=600000),
    model_id: Literal["music_v1"] | None = Field(None, description="AI model version to use for music generation."),
    force_instrumental: bool | None = Field(None, description="When enabled, ensures the generated song contains no vocals and is purely instrumental. Only applicable with prompt-based generation."),
    use_phonetic_names: bool | None = Field(None, description="When enabled, proper names in the prompt are phonetically spelled for improved lyrical pronunciation while preserving original names in word-level timestamps."),
    respect_sections_durations: bool | None = Field(None, description="Controls section duration enforcement in composition plans. When true, strictly respects each section's specified duration. When false, allows duration adjustments for improved quality and latency while maintaining total song length."),
) -> dict[str, Any]:
    """Generate a complete song from either a text prompt or a detailed composition plan, with control over musical style, structure, and audio output format."""

    # Construct request model with validation
    try:
        _request = _models.GenerateRequest(
            query=_models.GenerateRequestQuery(output_format=output_format),
            body=_models.GenerateRequestBody(prompt=prompt, music_length_ms=music_length_ms, model_id=model_id, force_instrumental=force_instrumental, use_phonetic_names=use_phonetic_names, respect_sections_durations=respect_sections_durations,
                music_prompt=_models.GenerateRequestBodyMusicPrompt(positive_global_styles=music_prompt_positive_global_styles, negative_global_styles=music_prompt_negative_global_styles, sections=music_prompt_sections),
                composition_plan=_models.GenerateRequestBodyCompositionPlan(positive_global_styles=composition_plan_positive_global_styles, negative_global_styles=composition_plan_negative_global_styles, sections=composition_plan_sections))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for compose_song: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/music"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("compose_song")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("compose_song", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="compose_song",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: music-generation
@mcp.tool()
async def compose_song_detailed(
    music_prompt_positive_global_styles: list[str] = Field(..., alias="music_promptPositive_global_styles", description="Musical styles and directions to include throughout the entire song. Use English language for optimal results.", max_length=50),
    composition_plan_positive_global_styles: list[str] = Field(..., alias="composition_planPositive_global_styles", description="Musical styles and directions to include throughout the entire song when using composition_plan. Use English language for optimal results.", max_length=50),
    music_prompt_negative_global_styles: list[str] = Field(..., alias="music_promptNegative_global_styles", description="Musical styles and directions to exclude from the entire song. Use English language for optimal results.", max_length=50),
    composition_plan_negative_global_styles: list[str] = Field(..., alias="composition_planNegative_global_styles", description="Musical styles and directions to exclude from the entire song when using composition_plan. Use English language for optimal results.", max_length=50),
    music_prompt_sections: list[_models.SongSection] = Field(..., alias="music_promptSections", description="Ordered array of song sections, each with duration, style, and lyrical content specifications. Order determines playback sequence.", max_length=30),
    composition_plan_sections: list[_models.SongSection] = Field(..., alias="composition_planSections", description="Ordered array of song sections for composition_plan, each with duration, style, and lyrical content specifications. Order determines playback sequence.", max_length=30),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio output format specified as codec, sample rate, and bitrate. Higher bitrates and sample rates may require elevated subscription tiers."),
    prompt: str | None = Field(None, description="Text-based prompt describing the song to generate. Mutually exclusive with composition_plan. Provide creative direction, mood, genre, and lyrical themes.", max_length=4100),
    music_length_ms: int | None = Field(None, description="Target song duration in milliseconds. Only applicable with prompt-based generation. If omitted, the model automatically determines length based on prompt content.", ge=3000, le=600000),
    model_id: Literal["music_v1"] | None = Field(None, description="AI model version to use for music generation."),
    force_instrumental: bool | None = Field(None, description="When enabled, ensures the generated song contains no vocals. Only works with prompt-based generation."),
    use_phonetic_names: bool | None = Field(None, description="When enabled, proper names in the prompt are phonetically spelled for improved lyrical pronunciation while preserving original names in word timestamps."),
    respect_sections_durations: bool | None = Field(None, description="Controls section duration enforcement in composition_plan. When true, strictly respects each section's specified duration. When false, allows duration flexibility for improved quality and latency while maintaining total song length."),
    with_timestamps: bool | None = Field(None, description="When enabled, the response includes precise word-level timestamps indicating when each lyric occurs in the generated audio."),
) -> dict[str, Any]:
    """Generate a complete song with detailed metadata from either a text prompt or a structured composition plan. Returns audio file and optional word-level timestamps."""

    # Construct request model with validation
    try:
        _request = _models.ComposeDetailedRequest(
            query=_models.ComposeDetailedRequestQuery(output_format=output_format),
            body=_models.ComposeDetailedRequestBody(prompt=prompt, music_length_ms=music_length_ms, model_id=model_id, force_instrumental=force_instrumental, use_phonetic_names=use_phonetic_names, respect_sections_durations=respect_sections_durations, with_timestamps=with_timestamps,
                music_prompt=_models.ComposeDetailedRequestBodyMusicPrompt(positive_global_styles=music_prompt_positive_global_styles, negative_global_styles=music_prompt_negative_global_styles, sections=music_prompt_sections),
                composition_plan=_models.ComposeDetailedRequestBodyCompositionPlan(positive_global_styles=composition_plan_positive_global_styles, negative_global_styles=composition_plan_negative_global_styles, sections=composition_plan_sections))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for compose_song_detailed: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/music/detailed"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("compose_song_detailed")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("compose_song_detailed", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="compose_song_detailed",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: music-generation
@mcp.tool()
async def compose_music(
    music_prompt_positive_global_styles: list[str] = Field(..., alias="music_promptPositive_global_styles", description="Musical styles and directions to include throughout the entire composition. Use English language for best results.", max_length=50),
    composition_plan_positive_global_styles: list[str] = Field(..., alias="composition_planPositive_global_styles", description="Musical styles and directions to include throughout the entire composition. Use English language for best results.", max_length=50),
    music_prompt_negative_global_styles: list[str] = Field(..., alias="music_promptNegative_global_styles", description="Musical styles and directions to exclude from the entire composition. Use English language for best results.", max_length=50),
    composition_plan_negative_global_styles: list[str] = Field(..., alias="composition_planNegative_global_styles", description="Musical styles and directions to exclude from the entire composition. Use English language for best results.", max_length=50),
    music_prompt_sections: list[_models.SongSection] = Field(..., alias="music_promptSections", description="Ordered array defining distinct sections of the song, each with its own musical characteristics and transitions.", max_length=30),
    composition_plan_sections: list[_models.SongSection] = Field(..., alias="composition_planSections", description="Ordered array defining distinct sections of the song, each with its own musical characteristics and transitions.", max_length=30),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Audio output format specified as codec, sample rate, and bitrate. Higher bitrates and sample rates may require elevated subscription tiers."),
    prompt: str | None = Field(None, description="Simple text description to generate a song from. Mutually exclusive with composition_plan. Use English for optimal results.", max_length=4100),
    music_length_ms: int | None = Field(None, description="Target duration for the generated composition in milliseconds. Only applicable when using prompt-based generation. If omitted, the model determines length based on the prompt.", ge=3000, le=600000),
    model_id: Literal["music_v1"] | None = Field(None, description="The generative model version to use for music composition."),
    force_instrumental: bool | None = Field(None, description="When enabled, ensures the generated composition contains no vocals. Only applicable with prompt-based generation."),
    use_phonetic_names: bool | None = Field(None, description="When enabled, proper names in the prompt are phonetically spelled for improved lyrical pronunciation while preserving original names in word-level timestamps."),
) -> dict[str, Any]:
    """Generate and stream composed music from either a text prompt or a detailed composition plan. Supports various audio formats and customizable musical styles."""

    # Construct request model with validation
    try:
        _request = _models.StreamComposeRequest(
            query=_models.StreamComposeRequestQuery(output_format=output_format),
            body=_models.StreamComposeRequestBody(prompt=prompt, music_length_ms=music_length_ms, model_id=model_id, force_instrumental=force_instrumental, use_phonetic_names=use_phonetic_names,
                music_prompt=_models.StreamComposeRequestBodyMusicPrompt(positive_global_styles=music_prompt_positive_global_styles, negative_global_styles=music_prompt_negative_global_styles, sections=music_prompt_sections),
                composition_plan=_models.StreamComposeRequestBodyCompositionPlan(positive_global_styles=composition_plan_positive_global_styles, negative_global_styles=composition_plan_negative_global_styles, sections=composition_plan_sections))
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for compose_music: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/music/stream"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("compose_music")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("compose_music", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="compose_music",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: music-generation
@mcp.tool()
async def upload_song(
    file_: str = Field(..., alias="file", description="The audio file to upload in binary format."),
    extract_composition_plan: bool | None = Field(None, description="Whether to generate and return the composition plan for the uploaded song. Enabling this increases response latency."),
) -> dict[str, Any]:
    """Upload a music file for use in inpainting workflows. This operation is restricted to enterprise clients with access to the inpainting feature."""

    # Construct request model with validation
    try:
        _request = _models.UploadSongRequest(
            body=_models.UploadSongRequestBody(file_=file_, extract_composition_plan=extract_composition_plan)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for upload_song: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/music/upload"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("upload_song")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("upload_song", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="upload_song",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: music-generation
@mcp.tool()
async def separate_song_stems(
    file_: str = Field(..., alias="file", description="The audio file to separate into individual stems. Provide the binary audio data."),
    output_format: Literal["mp3_22050_32", "mp3_24000_48", "mp3_44100_32", "mp3_44100_64", "mp3_44100_96", "mp3_44100_128", "mp3_44100_192", "pcm_8000", "pcm_16000", "pcm_22050", "pcm_24000", "pcm_32000", "pcm_44100", "pcm_48000", "ulaw_8000", "alaw_8000", "opus_48000_32", "opus_48000_64", "opus_48000_96", "opus_48000_128", "opus_48000_192"] | None = Field(None, description="Output format for the separated stems, specified as codec_sample_rate_bitrate. MP3 192kbps requires Creator tier or above; PCM 44.1kHz requires Pro tier or above. μ-law format is commonly used for Twilio audio inputs."),
    stem_variation_id: Literal["two_stems_v1", "six_stems_v1"] | None = Field(None, description="The stem separation model variation to use. Two-stem splits into vocals and instruments; six-stem provides more granular separation."),
) -> dict[str, Any]:
    """Separate an audio file into individual musical stems (vocals, drums, bass, etc.). This operation may have high latency depending on audio file length."""

    # Construct request model with validation
    try:
        _request = _models.SeparateSongStemsRequest(
            query=_models.SeparateSongStemsRequestQuery(output_format=output_format),
            body=_models.SeparateSongStemsRequestBody(file_=file_, stem_variation_id=stem_variation_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for separate_song_stems: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/music/stem-separation"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("separate_song_stems")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("separate_song_stems", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="separate_song_stems",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def create_voice_pvc(
    name: str = Field(..., description="The display name for this voice, shown in voice selection dropdowns and UI.", max_length=100),
    language: str = Field(..., description="The language code for the voice samples and voice model training."),
    description: str | None = Field(None, description="Optional description providing context about the voice characteristics and intended use cases.", max_length=500),
    labels: dict[str, str] | None = Field(None, description="Optional metadata labels to categorize and describe the voice. Supports language, accent, gender, and age attributes."),
) -> dict[str, Any]:
    """Creates a new PVC voice with metadata. Voice samples can be added later to train the voice model."""

    # Construct request model with validation
    try:
        _request = _models.CreatePvcVoiceRequest(
            body=_models.CreatePvcVoiceRequestBody(name=name, language=language, description=description, labels=labels)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for create_voice_pvc: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = "/v1/voices/pvc"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("create_voice_pvc")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("create_voice_pvc", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="create_voice_pvc",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def update_voice_pvc(
    voice_id: str = Field(..., description="The unique identifier of the voice to update."),
    name: str | None = Field(None, description="Display name for the voice as shown in voice selection interfaces.", max_length=100),
    language: str | None = Field(None, description="Language code of the voice samples (e.g., 'en' for English)."),
    description: str | None = Field(None, description="Detailed description of the voice characteristics and intended use cases.", max_length=500),
    labels: dict[str, str] | None = Field(None, description="Classification labels for the voice including language, accent, gender, and age characteristics."),
) -> dict[str, Any]:
    """Update metadata for a PVC (Professional Voice Clone) voice, including name, language, description, and classification labels."""

    # Construct request model with validation
    try:
        _request = _models.EditPvcVoiceRequest(
            path=_models.EditPvcVoiceRequestPath(voice_id=voice_id),
            body=_models.EditPvcVoiceRequestBody(name=name, language=language, description=description, labels=labels)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_voice_pvc: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/pvc/{voice_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/pvc/{voice_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_voice_pvc")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_voice_pvc", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_voice_pvc",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def add_voice_samples(
    voice_id: str = Field(..., description="The unique identifier of the PVC voice to add samples to. Use the voices list endpoint to retrieve available voice IDs."),
    files: list[str] = Field(..., description="Audio files to add to the voice. Provide one or more audio files in supported formats to expand the voice training dataset."),
    remove_background_noise: bool | None = Field(None, description="Enable automatic background noise removal from audio samples using audio isolation. Disable if samples contain minimal background noise, as processing may reduce quality."),
) -> dict[str, Any]:
    """Add audio samples to a PVC (Personal Voice Clone) to enhance voice quality and training data. Optionally remove background noise from samples to improve voice clarity."""

    # Construct request model with validation
    try:
        _request = _models.AddPvcVoiceSamplesRequest(
            path=_models.AddPvcVoiceSamplesRequestPath(voice_id=voice_id),
            body=_models.AddPvcVoiceSamplesRequestBody(files=files, remove_background_noise=remove_background_noise)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for add_voice_samples: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/pvc/{voice_id}/samples", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/pvc/{voice_id}/samples"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("add_voice_samples")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("add_voice_samples", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="add_voice_samples",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def update_voice_sample(
    voice_id: str = Field(..., description="The unique identifier of the voice model containing the sample to update."),
    sample_id: str = Field(..., description="The unique identifier of the voice sample to update."),
    remove_background_noise: bool | None = Field(None, description="Enable background noise removal using audio isolation. Only apply if the sample contains background noise, as it may degrade quality otherwise."),
    selected_speaker_ids: list[str] | None = Field(None, description="List of speaker IDs to use for PVC training. Sending a new list will replace any previously selected speakers for this sample."),
    trim_start_time: int | None = Field(None, description="The start time of the audio segment to use for PVC training, specified in milliseconds from the beginning of the file."),
    trim_end_time: int | None = Field(None, description="The end time of the audio segment to use for PVC training, specified in milliseconds from the beginning of the file."),
    file_name: str | None = Field(None, description="The name to assign to the audio file for PVC training purposes."),
) -> dict[str, Any]:
    """Update a PVC voice sample by applying noise removal, selecting speakers, adjusting trim times, or changing the file name. Changes are applied to the specified sample within a voice model."""

    # Construct request model with validation
    try:
        _request = _models.EditPvcVoiceSampleRequest(
            path=_models.EditPvcVoiceSampleRequestPath(voice_id=voice_id, sample_id=sample_id),
            body=_models.EditPvcVoiceSampleRequestBody(remove_background_noise=remove_background_noise, selected_speaker_ids=selected_speaker_ids, trim_start_time=trim_start_time, trim_end_time=trim_end_time, file_name=file_name)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for update_voice_sample: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/pvc/{voice_id}/samples/{sample_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/pvc/{voice_id}/samples/{sample_id}"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("update_voice_sample")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("update_voice_sample", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="update_voice_sample",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def remove_voice_sample(
    voice_id: str = Field(..., description="The unique identifier of the PVC voice from which to remove the sample."),
    sample_id: str = Field(..., description="The unique identifier of the sample to be deleted from the voice."),
) -> dict[str, Any]:
    """Remove a sample from a PVC (Professional Voice Clone) voice. This permanently deletes the specified sample, which cannot be undone."""

    # Construct request model with validation
    try:
        _request = _models.DeletePvcVoiceSampleRequest(
            path=_models.DeletePvcVoiceSampleRequestPath(voice_id=voice_id, sample_id=sample_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for remove_voice_sample: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/pvc/{voice_id}/samples/{sample_id}", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/pvc/{voice_id}/samples/{sample_id}"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("remove_voice_sample")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("remove_voice_sample", "DELETE", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="remove_voice_sample",
        method="DELETE",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def get_voice_sample_audio(
    voice_id: str = Field(..., description="The unique identifier of the voice whose sample audio you want to retrieve."),
    sample_id: str = Field(..., description="The unique identifier of the specific voice sample to retrieve."),
    remove_background_noise: bool | None = Field(None, description="Enable background noise removal using audio isolation. Note: applying this to samples without background noise may degrade audio quality."),
) -> dict[str, Any]:
    """Retrieve the first 30 seconds of audio from a voice sample, with optional background noise removal using audio isolation technology."""

    # Construct request model with validation
    try:
        _request = _models.GetPvcSampleAudioRequest(
            path=_models.GetPvcSampleAudioRequestPath(voice_id=voice_id, sample_id=sample_id),
            query=_models.GetPvcSampleAudioRequestQuery(remove_background_noise=remove_background_noise)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_voice_sample_audio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/pvc/{voice_id}/samples/{sample_id}/audio", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/pvc/{voice_id}/samples/{sample_id}/audio"
    _http_query = _request.query.model_dump(by_alias=True, exclude_none=True) if _request.query else {}
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_voice_sample_audio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_voice_sample_audio", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_voice_sample_audio",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        params=_http_query,
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def get_voice_sample_waveform(
    voice_id: str = Field(..., description="The unique identifier of the voice whose sample waveform you want to retrieve."),
    sample_id: str = Field(..., description="The unique identifier of the voice sample whose waveform you want to retrieve."),
) -> dict[str, Any]:
    """Retrieve the visual waveform representation of a specific voice sample. This waveform can be used to visualize the audio characteristics of the sample."""

    # Construct request model with validation
    try:
        _request = _models.GetPvcSampleVisualWaveformRequest(
            path=_models.GetPvcSampleVisualWaveformRequestPath(voice_id=voice_id, sample_id=sample_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_voice_sample_waveform: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/pvc/{voice_id}/samples/{sample_id}/waveform", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/pvc/{voice_id}/samples/{sample_id}/waveform"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_voice_sample_waveform")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_voice_sample_waveform", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_voice_sample_waveform",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def get_speaker_separation_status(
    voice_id: str = Field(..., description="The unique identifier of the voice whose sample is being analyzed."),
    sample_id: str = Field(..., description="The unique identifier of the voice sample undergoing speaker separation analysis."),
) -> dict[str, Any]:
    """Retrieve the current status of speaker separation processing for a voice sample and list any detected speakers if the process is complete."""

    # Construct request model with validation
    try:
        _request = _models.GetPvcSampleSpeakersRequest(
            path=_models.GetPvcSampleSpeakersRequestPath(voice_id=voice_id, sample_id=sample_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_speaker_separation_status: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/pvc/{voice_id}/samples/{sample_id}/speakers", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/pvc/{voice_id}/samples/{sample_id}/speakers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_speaker_separation_status")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_speaker_separation_status", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_speaker_separation_status",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def separate_speakers(
    voice_id: str = Field(..., description="The unique identifier of the voice to be used for the separation process."),
    sample_id: str = Field(..., description="The unique identifier of the audio sample to be processed for speaker separation."),
) -> dict[str, Any]:
    """Initiate speaker separation processing for an audio sample, which identifies and isolates individual speakers within the sample."""

    # Construct request model with validation
    try:
        _request = _models.StartSpeakerSeparationRequest(
            path=_models.StartSpeakerSeparationRequestPath(voice_id=voice_id, sample_id=sample_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for separate_speakers: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/pvc/{voice_id}/samples/{sample_id}/separate-speakers", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/pvc/{voice_id}/samples/{sample_id}/separate-speakers"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("separate_speakers")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("separate_speakers", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="separate_speakers",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def get_speaker_audio(
    voice_id: str = Field(..., description="The unique identifier of the voice. Use the voices list endpoint to discover available voice IDs."),
    sample_id: str = Field(..., description="The unique identifier of the sample within the specified voice."),
    speaker_id: str = Field(..., description="The unique identifier of the speaker whose audio should be extracted. Use the speakers list endpoint for the voice and sample to discover available speaker IDs."),
) -> dict[str, Any]:
    """Retrieve the isolated audio track for a specific speaker from a voice sample. This operation extracts and returns only the audio corresponding to the designated speaker."""

    # Construct request model with validation
    try:
        _request = _models.GetSpeakerAudioRequest(
            path=_models.GetSpeakerAudioRequestPath(voice_id=voice_id, sample_id=sample_id, speaker_id=speaker_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for get_speaker_audio: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/pvc/{voice_id}/samples/{sample_id}/speakers/{speaker_id}/audio", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/pvc/{voice_id}/samples/{sample_id}/speakers/{speaker_id}/audio"
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("get_speaker_audio")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("get_speaker_audio", "GET", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="get_speaker_audio",
        method="GET",
        path=_http_path,
        request_id=_request_id,
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def train_voice(
    voice_id: str = Field(..., description="The unique identifier of the voice to train. You can retrieve available voices from the voices list endpoint."),
    model_id: str | None = Field(None, description="The AI model version to use for training. Specifies which voice conversion model architecture to apply during the training process."),
) -> dict[str, Any]:
    """Start a PVC (Personal Voice Cloning) training process for a specified voice. This initiates the model training that enables voice customization and optimization."""

    # Construct request model with validation
    try:
        _request = _models.RunPvcVoiceTrainingRequest(
            path=_models.RunPvcVoiceTrainingRequestPath(voice_id=voice_id),
            body=_models.RunPvcVoiceTrainingRequestBody(model_id=model_id)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for train_voice: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/pvc/{voice_id}/train", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/pvc/{voice_id}/train"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("train_voice")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("train_voice", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="train_voice",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        headers=_http_headers,
    )

    return _response_data

# Tags: pvc-voices
@mcp.tool()
async def submit_voice_verification(
    voice_id: str = Field(..., description="The unique identifier of the voice to be verified. Use the voices list endpoint to retrieve available voice IDs."),
    files: list[str] = Field(..., description="Array of verification document files to submit for manual review. Documents should be in a supported format and clearly demonstrate voice ownership or authorization."),
    extra_text: str | None = Field(None, description="Optional additional context or information to support the verification request, such as clarification about the voice or usage intent."),
) -> dict[str, Any]:
    """Submit verification documents for manual review of a PVC (Premium Voice Clone) voice. This process validates the voice identity before it can be used in production."""

    # Construct request model with validation
    try:
        _request = _models.RequestPvcManualVerificationRequest(
            path=_models.RequestPvcManualVerificationRequestPath(voice_id=voice_id),
            body=_models.RequestPvcManualVerificationRequestBody(files=files, extra_text=extra_text)
        )
    except pydantic.ValidationError as _validation_err:
        logging.error(f"Parameter validation failed for submit_voice_verification: {_validation_err}")
        raise ValueError(f"Invalid parameters: {_validation_err.errors()}") from _validation_err

    # Extract parameters for API call
    _http_path = _build_path("/v1/voices/pvc/{voice_id}/verification", _request.path.model_dump(by_alias=True)) if _request.path else "/v1/voices/pvc/{voice_id}/verification"
    _http_body = _request.body.model_dump(by_alias=True, exclude_none=True) if _request.body else None
    _http_headers = {}

    # Inject per-operation authentication
    _auth = await _get_auth_for_operation("submit_voice_verification")
    _http_headers.update(_auth.get("headers", {}))

    _request_id = str(uuid.uuid4())
    _log_tool_invocation("submit_voice_verification", "POST", _http_path, _request_id)

    # Execute request (returns normalized dict and status code)
    _response_data, _ = await _execute_tool_request(
        tool_name="submit_voice_verification",
        method="POST",
        path=_http_path,
        request_id=_request_id,
        body=_http_body,
        body_content_type="multipart/form-data",
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
        print("  python eleven_labs_server.py", file=sys.stderr)
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

    parser = argparse.ArgumentParser(description="ElevenLabs MCP Server")

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
    logger.info("Starting ElevenLabs MCP Server")
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

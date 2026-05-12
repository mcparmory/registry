"""
Authentication module for Semrush AppCenter MCP server.

Generated: 2026-05-12 12:44:24 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)

This module contains:
1. Authentication class implementations (OAuth2)
2. Operation-to-auth requirements mapping (OPERATION_AUTH_MAP)
"""

from __future__ import annotations

import logging
import os
import time

logger = logging.getLogger(__name__)

__all__ = [
    "JWTBearerAuth",
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Authentication Classes
# ============================================================================

class JWTBearerAuth:
    """
    JWT Bearer authentication for Semrush AppCenter API.

    Generates short-lived JWTs (RFC 7523).
    This variant signs JWTs with a shared secret (typically HS256).
    Supports two modes:
    - Direct JWT: signed token used directly as Bearer token (e.g. GitHub Apps)
    - Token exchange: signed JWT exchanged at a token URL for an access token
      (e.g. Google service accounts)

    Configuration (environment variables):
        - JWT_SHARED_SECRET: Shared signing secret (required)
        - JWT_ISSUER_ID: Issuer claim value — App ID, Team ID, etc. (required)
        - JWT_ALGORITHM: Signing algorithm (default: HS256)
        - JWT_EXPIRY: Token lifetime in seconds (default: 600)
        - JWT_AUDIENCE: Audience claim (optional)
        - JWT_KEY_ID: Key ID for JWT header kid field (optional)
        - JWT_TOKEN_URL: Token exchange endpoint (optional — if set, exchanges JWT for access token)
        - JWT_SCOPES: Comma-separated scopes for token exchange (optional)
    """

    def __init__(self):
        """Initialize JWT Bearer authentication from environment variables."""
        import jwt as pyjwt  # PyJWT

        self._pyjwt = pyjwt

        # Required signing material
        raw_secret = os.getenv("JWT_SHARED_SECRET", "").strip()
        if not raw_secret:
            raise ValueError(
                "JWT_SHARED_SECRET environment variable not set. "
                "Leave empty in .env to disable JWT Bearer auth."
            )
        self._signing_key = raw_secret

        self._issuer = os.getenv("JWT_ISSUER_ID", "").strip()
        if not self._issuer:
            raise ValueError(
                "JWT_ISSUER_ID environment variable not set. "
                "Leave empty in .env to disable JWT Bearer auth."
            )

        # Optional — empty values fall back to defaults
        self._algorithm = os.getenv("JWT_ALGORITHM", "").strip() or "HS256"
        self._expiry = int(os.getenv("JWT_EXPIRY", "").strip() or "600")
        raw_audience = os.getenv("JWT_AUDIENCE", "").strip()
        if raw_audience.lower() in {"none", "null"}:
            raw_audience = ""
        self._audience = raw_audience or "app-center"
        self._key_id = os.getenv("JWT_KEY_ID", "").strip() or None
        raw_token_url = os.getenv("JWT_TOKEN_URL", "").strip()
        if raw_token_url.lower() in {"none", "null"}:
            raw_token_url = ""
        self._token_url = raw_token_url or "https://api.semrush.com/app-center-api/v2/jwt-token/"
        self._scopes = os.getenv("JWT_SCOPES", "").strip() or None

        # Token cache
        self._cached_token: str | None = None
        self._token_expires_at: float = 0

    def _generate_jwt(self) -> str:
        """Generate a signed JWT."""
        now = int(time.time())
        payload: dict = {
            "iat": now,
            "exp": now + self._expiry,
            "iss": self._issuer,
        }
        if self._audience:
            payload["aud"] = self._audience

        headers: dict = {}
        if self._key_id:
            headers["kid"] = self._key_id

        return self._pyjwt.encode(
            payload,
            self._signing_key,
            algorithm=self._algorithm,
            headers=headers or None,
        )

    def _is_token_expired(self) -> bool:
        """Check if cached token is expired or near-expiry (30s buffer)."""
        return time.time() >= (self._token_expires_at - 30)

    def _get_token(self) -> str:
        """Get a valid token, generating/exchanging as needed."""
        if self._cached_token and not self._is_token_expired():
            return self._cached_token

        jwt_token = self._generate_jwt()

        if self._token_url:
            # Exchange JWT for access token at token endpoint
            import httpx
            response = httpx.post(self._token_url, json={"jwt": jwt_token})
            response.raise_for_status()
            token_data = response.json()
            token = token_data["jwt"]
            expires_in = token_data.get("expires_in", self._expiry)
            self._token_expires_at = time.time() + expires_in
        else:
            # Direct JWT — use as-is
            token = jwt_token
            self._token_expires_at = time.time() + self._expiry

        self._cached_token = token
        return token

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests."""
        return {"Authorization": f"Bearer {self._get_token()}"}

    def clear_token(self) -> None:
        """Clear cached token (called on 401 response)."""
        self._cached_token = None
        self._token_expires_at = 0


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "get_viewer_status": [["jwtIssuerToken"]],
    "list_subscriptions": [["jwtIssuerToken"]],
    "get_user_subscription": [["jwtIssuerToken"]],
    "send_event_notification": [["jwtIssuerToken"]],
    "get_event_status": [["jwtIssuerToken"]]
}

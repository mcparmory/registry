"""
Authentication module for Figma API MCP server.

Generated: 2026-03-31 11:06:56 UTC
Generator: MCP Blacksmith v1.0.0 (https://mcpblacksmith.com)

This module contains:
1. Authentication class implementations (OAuth2)
2. Operation-to-auth requirements mapping (OPERATION_AUTH_MAP)
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import threading
import time
import webbrowser
from pathlib import Path

from authlib.common.security import generate_token
from authlib.integrations.httpx_client import OAuth2Client

logger = logging.getLogger(__name__)

__all__ = [
    "OAuth2Auth",
    "OrgOAuth2Auth",
    "APIKeyAuth",
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Callback Port Configuration
# ============================================================================

# OAuth2/OIDC callback server ports (configured in .env)
# Each auth scheme uses a different port to avoid conflicts when multiple
# schemes are active simultaneously (e.g., OAuth2 + OIDC).
OAUTH2_CALLBACK_PORT = int(os.environ.get("OAUTH2_CALLBACK_PORT", 9400))
ORG_OAUTH2_CALLBACK_PORT = int(os.environ.get("ORG_OAUTH2_CALLBACK_PORT", 9401))

# ============================================================================
# Authentication Classes
# ============================================================================

class OAuth2Auth:
    """
    OAuth 2.0 authentication for Figma API.

    Flow: authorizationCode
    Uses: authlib for OAuth2 protocol handling

    NOTE: Authorization scheme prefix ("Bearer ") is automatically inserted.
    Access tokens are obtained automatically through OAuth2 flow.

    Configuration (environment variables):
        - OAUTH2_CLIENT_ID: OAuth2 client ID (required)
        - OAUTH2_CLIENT_SECRET: OAuth2 client secret (required)
        - OAUTH2_SCOPES: Comma-separated scopes (required)
    Redirect URI:
        - Fixed: http://localhost:<OAUTH2_CALLBACK_PORT>/callback
        - Configured via OAUTH2_CALLBACK_PORT in .env (default: 9400)
        - Must match redirect URI in your OAuth application configuration
    Token Storage:
        Location: ./tokens/oauth2_tokens.json
        Permissions: 0o600 (owner read/write only)
        Format: JSON with access_token, refresh_token, expires_at

    URLs:
        Authorization URL: https://www.figma.com/oauth
        Token URL: https://api.figma.com/v1/oauth/token
        Refresh URL: https://api.figma.com/v1/oauth/refresh

    Available Scopes (configure via OAUTH2_SCOPES):
        - current_user:read
        - file_comments:read
        - file_comments:write
        - file_content:read
        - file_dev_resources:read
        - file_dev_resources:write
        - file_metadata:read
        - file_variables:read
        - file_variables:write
        - file_versions:read
        - files:read
        - library_analytics:read
        - library_assets:read
        - library_content:read
        - projects:read
        - team_library_content:read
        - webhooks:read
        - webhooks:write
    """

    def __init__(self):
        """Initialize OAuth2 authentication with authlib."""
        # Store flow type for lifecycle management
        self.flow_type = "authorizationCode"

        # Load configuration from environment
        self.client_id = os.getenv("OAUTH2_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("OAUTH2_CLIENT_SECRET", "").strip()

        # Validate required credentials
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "OAUTH2_CLIENT_ID and OAUTH2_CLIENT_SECRET must be set. "
                "Leave empty in .env to disable OAuth2."
            )

        # Detect common placeholder patterns
        placeholders = ["placeholder", "your-", "example", "change-me", "todo"]
        if any(p in self.client_id.lower() for p in placeholders):
            raise ValueError(
                f"OAUTH2_CLIENT_ID appears to be a placeholder ({self.client_id[:20]}...). "
                "Please set real credentials or leave empty to disable OAuth2."
            )
        if any(p in self.client_secret.lower() for p in placeholders):
            raise ValueError(
                "OAUTH2_CLIENT_SECRET appears to be a placeholder. "
                "Please set real credentials or leave empty to disable OAuth2."
            )

        # Parse scopes from environment (required)
        scopes_env = os.getenv("OAUTH2_SCOPES", "").strip()
        self.scopes = [s.strip() for s in scopes_env.split(",") if s.strip()]
        # Redirect URI for authorization flows (hardcoded port, change in auth.py if needed)
        self.callback_port = OAUTH2_CALLBACK_PORT
        self.redirect_uri = f"http://localhost:{OAUTH2_CALLBACK_PORT}/callback"

        # OAuth2 token URL (required for all flows that fetch tokens)
        self.token_url = "https://api.figma.com/v1/oauth/token"
        self.auth_url = "https://www.figma.com/oauth"
        self.refresh_url = "https://api.figma.com/v1/oauth/refresh"

        # Token storage (secure file-based)
        self.token_dir = Path(__file__).parent / "tokens"
        self.token_file = self.token_dir / "oauth2_tokens.json"
        self.client: OAuth2Client | None = None
        self.token: dict | None = None

        # Load existing token if available
        self._load_token()

    def _load_token(self) -> None:
        """Load saved token from disk."""
        if self.token_file.exists():
            try:
                data = json.loads(self.token_file.read_text())
                if data.get("access_token"):
                    self.token = data
            except (json.JSONDecodeError, IOError):
                pass

    def _save_token(self, token: dict) -> None:
        """Save token to disk with restricted permissions."""
        self.token_dir.mkdir(parents=True, exist_ok=True)
        self.token_file.write_text(json.dumps(token, indent=2))
        self.token_file.chmod(0o600)
        self.token = token

    def _create_client(self) -> OAuth2Client:
        """Create authlib OAuth2Client."""
        return OAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_endpoint_auth_method="client_secret_post",
        )

    def _is_token_expired(self) -> bool:
        """Check if current token is expired or about to expire."""
        if not self.token:
            return True
        expires_at = self.token.get("expires_at")
        if expires_at is None:
            return False  # No expiry info — assume valid
        return time.time() > (expires_at - 300)  # 5-minute buffer

    async def _refresh_token(self) -> bool:
        """Try to refresh the access token using the refresh token."""
        if not self.token or not self.token.get("refresh_token"):
            return False
        if not self.token_url:
            return False

        try:
            client = self._create_client()
            new_token = client.refresh_token(
                self.token_url,
                refresh_token=self.token.get("refresh_token"),
            )
            if new_token and new_token.get("access_token"):
                self._save_token(dict(new_token))
                return True
        except Exception:
            pass
        return False

    async def authorize(self, port: int | None = None) -> dict:
        """
        Run OAuth2 authorization code flow with local callback server.

        Starts a temporary HTTP server on localhost to receive the callback,
        opens the browser to the authorization URL, and waits for the user
        to authorize.

        Args:
            port: Local callback server port (default: from OAUTH2_CALLBACK_PORT env or 9400)

        Returns:
            OAuth2 token dict with access_token, refresh_token, etc.

        Raises:
            ValueError: If authorization fails or is denied
            TimeoutError: If user doesn't complete authorization in 120 seconds
        """
        import http.server
        import urllib.parse

        port = port or self.callback_port
        redirect_uri = f"http://localhost:{port}/callback"

        client = self._create_client()

        # Generate PKCE challenge
        code_verifier = generate_token(48)
        import base64
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode()

        # Build authorization URL
        auth_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.scopes),
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        auth_url = f"{self.auth_url}?{urllib.parse.urlencode(auth_params)}"

        # Capture authorization code via local HTTP callback server
        result: dict = {}

        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)
                if "code" in params:
                    result["code"] = params["code"][0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html><body><h2>Authorization successful!</h2><p>You can close this tab.</p></body></html>")
                elif "error" in params:
                    result["error"] = params.get("error", ["unknown"])[0]
                    result["error_description"] = params.get("error_description", [""])[0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    error_desc = result.get("error_description", "")
                    self.wfile.write(f"<html><body><h2>Authorization failed</h2><p>{error_desc}</p></body></html>".encode())

            def log_message(self, format, *args):
                pass  # Suppress server logs

        server = http.server.HTTPServer(("localhost", port), CallbackHandler)
        server_thread = threading.Thread(target=server.handle_request, daemon=True)
        server_thread.start()

        # Open browser for user authorization
        webbrowser.open(auth_url)

        # Wait for callback (120s timeout)
        server_thread.join(timeout=120)
        server.server_close()

        if "error" in result:
            raise ValueError(
                f"Authorization denied: {result['error']} — {result.get('error_description', '')}"
            )
        if "code" not in result:
            raise TimeoutError(
                "Authorization timed out (120s). "
                "Please try again and complete authorization in the browser."
            )

        # Exchange code for token
        token = client.fetch_token(
            self.token_url,
            code=result["code"],
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )

        if not token or not token.get("access_token"):
            raise ValueError("Token exchange failed — no access_token received")

        self._save_token(dict(token))
        return dict(token)

    async def get_auth_headers(self) -> dict:
        """
        Get authorization headers for API requests.

        Handles token lifecycle:
        1. If no token, trigger authorization flow
        2. If token expired, try refresh first
        3. If refresh fails, re-authorize

        Returns:
            Dict with Authorization header (Bearer token)
        """
        # No token at all — need initial authorization
        if not self.token:
            await self.authorize()

        # Token expired — try refresh, then re-authorize
        if self._is_token_expired():
            if not await self._refresh_token():
                await self.authorize()

        if not self.token or not self.token.get("access_token"):
            raise ValueError("Failed to obtain access token after authorization attempt")

        return {"Authorization": f"Bearer {self.token['access_token']}"}

    def get_auth_params(self) -> dict:
        """OAuth2 uses headers, not query params."""
        return {}

class OrgOAuth2Auth:
    """
    OAuth 2.0 authentication for Figma API.

    Flow: authorizationCode
    Uses: authlib for OAuth2 protocol handling

    NOTE: Authorization scheme prefix ("Bearer ") is automatically inserted.
    Access tokens are obtained automatically through OAuth2 flow.

    Configuration (environment variables):
        - ORG_OAUTH2_CLIENT_ID: OAuth2 client ID (required)
        - ORG_OAUTH2_CLIENT_SECRET: OAuth2 client secret (required)
        - ORG_OAUTH2_SCOPES: Comma-separated scopes (required)
    Redirect URI:
        - Fixed: http://localhost:<ORG_OAUTH2_CALLBACK_PORT>/callback
        - Configured via ORG_OAUTH2_CALLBACK_PORT in .env (default: 9400)
        - Must match redirect URI in your OAuth application configuration
    Token Storage:
        Location: ./tokens/oauth2_tokens.json
        Permissions: 0o600 (owner read/write only)
        Format: JSON with access_token, refresh_token, expires_at

    URLs:
        Authorization URL: https://www.figma.com/oauth
        Token URL: https://api.figma.com/v1/oauth/token
        Refresh URL: https://api.figma.com/v1/oauth/refresh

    Available Scopes (configure via ORG_OAUTH2_SCOPES):
        - org:activity_log_read
    """

    def __init__(self):
        """Initialize OAuth2 authentication with authlib."""
        # Store flow type for lifecycle management
        self.flow_type = "authorizationCode"

        # Load configuration from environment
        self.client_id = os.getenv("ORG_OAUTH2_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("ORG_OAUTH2_CLIENT_SECRET", "").strip()

        # Validate required credentials
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "ORG_OAUTH2_CLIENT_ID and ORG_OAUTH2_CLIENT_SECRET must be set. "
                "Leave empty in .env to disable OAuth2."
            )

        # Detect common placeholder patterns
        placeholders = ["placeholder", "your-", "example", "change-me", "todo"]
        if any(p in self.client_id.lower() for p in placeholders):
            raise ValueError(
                f"ORG_OAUTH2_CLIENT_ID appears to be a placeholder ({self.client_id[:20]}...). "
                "Please set real credentials or leave empty to disable OAuth2."
            )
        if any(p in self.client_secret.lower() for p in placeholders):
            raise ValueError(
                "ORG_OAUTH2_CLIENT_SECRET appears to be a placeholder. "
                "Please set real credentials or leave empty to disable OAuth2."
            )

        # Parse scopes from environment (required)
        scopes_env = os.getenv("ORG_OAUTH2_SCOPES", "").strip()
        self.scopes = [s.strip() for s in scopes_env.split(",") if s.strip()]
        # Redirect URI for authorization flows (hardcoded port, change in auth.py if needed)
        self.callback_port = ORG_OAUTH2_CALLBACK_PORT
        self.redirect_uri = f"http://localhost:{ORG_OAUTH2_CALLBACK_PORT}/callback"

        # OAuth2 token URL (required for all flows that fetch tokens)
        self.token_url = "https://api.figma.com/v1/oauth/token"
        self.auth_url = "https://www.figma.com/oauth"
        self.refresh_url = "https://api.figma.com/v1/oauth/refresh"

        # Token storage (secure file-based)
        self.token_dir = Path(__file__).parent / "tokens"
        self.token_file = self.token_dir / "oauth2_tokens.json"
        self.client: OAuth2Client | None = None
        self.token: dict | None = None

        # Load existing token if available
        self._load_token()

    def _load_token(self) -> None:
        """Load saved token from disk."""
        if self.token_file.exists():
            try:
                data = json.loads(self.token_file.read_text())
                if data.get("access_token"):
                    self.token = data
            except (json.JSONDecodeError, IOError):
                pass

    def _save_token(self, token: dict) -> None:
        """Save token to disk with restricted permissions."""
        self.token_dir.mkdir(parents=True, exist_ok=True)
        self.token_file.write_text(json.dumps(token, indent=2))
        self.token_file.chmod(0o600)
        self.token = token

    def _create_client(self) -> OAuth2Client:
        """Create authlib OAuth2Client."""
        return OAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_endpoint_auth_method="client_secret_post",
        )

    def _is_token_expired(self) -> bool:
        """Check if current token is expired or about to expire."""
        if not self.token:
            return True
        expires_at = self.token.get("expires_at")
        if expires_at is None:
            return False  # No expiry info — assume valid
        return time.time() > (expires_at - 300)  # 5-minute buffer

    async def _refresh_token(self) -> bool:
        """Try to refresh the access token using the refresh token."""
        if not self.token or not self.token.get("refresh_token"):
            return False
        if not self.token_url:
            return False

        try:
            client = self._create_client()
            new_token = client.refresh_token(
                self.token_url,
                refresh_token=self.token.get("refresh_token"),
            )
            if new_token and new_token.get("access_token"):
                self._save_token(dict(new_token))
                return True
        except Exception:
            pass
        return False

    async def authorize(self, port: int | None = None) -> dict:
        """
        Run OAuth2 authorization code flow with local callback server.

        Starts a temporary HTTP server on localhost to receive the callback,
        opens the browser to the authorization URL, and waits for the user
        to authorize.

        Args:
            port: Local callback server port (default: from ORG_OAUTH2_CALLBACK_PORT env or 9400)

        Returns:
            OAuth2 token dict with access_token, refresh_token, etc.

        Raises:
            ValueError: If authorization fails or is denied
            TimeoutError: If user doesn't complete authorization in 120 seconds
        """
        import http.server
        import urllib.parse

        port = port or self.callback_port
        redirect_uri = f"http://localhost:{port}/callback"

        client = self._create_client()

        # Generate PKCE challenge
        code_verifier = generate_token(48)
        import hashlib
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode()

        # Build authorization URL
        auth_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.scopes),
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        auth_url = f"{self.auth_url}?{urllib.parse.urlencode(auth_params)}"

        # Capture authorization code via local HTTP callback server
        result: dict = {}

        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)
                if "code" in params:
                    result["code"] = params["code"][0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"<html><body><h2>Authorization successful!</h2><p>You can close this tab.</p></body></html>")
                elif "error" in params:
                    result["error"] = params.get("error", ["unknown"])[0]
                    result["error_description"] = params.get("error_description", [""])[0]
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    error_desc = result.get("error_description", "")
                    self.wfile.write(f"<html><body><h2>Authorization failed</h2><p>{error_desc}</p></body></html>".encode())

            def log_message(self, format, *args):
                pass  # Suppress server logs

        server = http.server.HTTPServer(("localhost", port), CallbackHandler)
        server_thread = threading.Thread(target=server.handle_request, daemon=True)
        server_thread.start()

        # Open browser for user authorization
        webbrowser.open(auth_url)

        # Wait for callback (120s timeout)
        server_thread.join(timeout=120)
        server.server_close()

        if "error" in result:
            raise ValueError(
                f"Authorization denied: {result['error']} — {result.get('error_description', '')}"
            )
        if "code" not in result:
            raise TimeoutError(
                "Authorization timed out (120s). "
                "Please try again and complete authorization in the browser."
            )

        # Exchange code for token
        token = client.fetch_token(
            self.token_url,
            code=result["code"],
            redirect_uri=redirect_uri,
            code_verifier=code_verifier,
        )

        if not token or not token.get("access_token"):
            raise ValueError("Token exchange failed — no access_token received")

        self._save_token(dict(token))
        return dict(token)

    async def get_auth_headers(self) -> dict:
        """
        Get authorization headers for API requests.

        Handles token lifecycle:
        1. If no token, trigger authorization flow
        2. If token expired, try refresh first
        3. If refresh fails, re-authorize

        Returns:
            Dict with Authorization header (Bearer token)
        """
        # No token at all — need initial authorization
        if not self.token:
            await self.authorize()

        # Token expired — try refresh, then re-authorize
        if self._is_token_expired():
            if not await self._refresh_token():
                await self.authorize()

        if not self.token or not self.token.get("access_token"):
            raise ValueError("Failed to obtain access token after authorization attempt")

        return {"Authorization": f"Bearer {self.token['access_token']}"}

    def get_auth_params(self) -> dict:
        """OAuth2 uses headers, not query params."""
        return {}

class APIKeyAuth:
    """
    API Key authentication for Figma API.

    Supports header, query parameter, and cookie-based API key injection.
    Configure location and parameter name via constructor arguments.
    """

    def __init__(self, env_var: str = "API_KEY", location: str = "header",
                 param_name: str = "Authorization", prefix: str = ""):
        """Initialize API key authentication from environment variable.

        Args:
            env_var: Environment variable name containing the API key.
            location: Where to inject the key - 'header', 'query', or 'cookie'.
            param_name: Name of the header, query parameter, or cookie.
            prefix: Optional prefix before the key value (e.g., 'Bearer').
        """
        self.location = location
        self.param_name = param_name
        self.prefix = prefix
        self.api_key = os.getenv(env_var, "").strip()

        # Check for empty API key
        if not self.api_key:
            raise ValueError(
                f"{env_var} environment variable not set. "
                "Leave empty in .env to disable API Key auth."
            )

        # Detect common placeholder patterns
        placeholders = ["placeholder", "your-", "example", "change-me", "todo", "bot placeholder"]
        api_key_lower = self.api_key.lower()

        if any(p in api_key_lower for p in placeholders):
            raise ValueError(
                f"API key appears to be a placeholder ({self.api_key[:20]}...). "
                "Please set a real API key or leave empty to disable API Key auth."
            )

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests."""
        if self.location != "header":
            return {}
        if self.param_name == "Authorization":
            # Use explicit prefix if set; otherwise send the key raw (no Bearer assumption —
            # apiKey schemes that happen to use the Authorization header don't imply Bearer)
            prefix = self.prefix + " " if self.prefix else ""
            return {"Authorization": f"{prefix}{self.api_key}"}
        value = f"{self.prefix} {self.api_key}" if self.prefix else self.api_key
        return {self.param_name: value}

    def get_auth_params(self) -> dict[str, str]:
        """Get authentication query parameters."""
        if self.location != "query":
            return {}
        return {self.param_name: self.api_key}

    def get_auth_cookies(self) -> dict[str, str]:
        """Get authentication cookies."""
        if self.location != "cookie":
            return {}
        return {self.param_name: self.api_key}


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "export_file_json": [["OAuth2"], ["PersonalAccessToken"]],
    "get_file_nodes": [["OAuth2"], ["PersonalAccessToken"]],
    "render_node_images": [["OAuth2"], ["PersonalAccessToken"]],
    "list_image_fills": [["OAuth2"], ["PersonalAccessToken"]],
    "get_file_metadata": [["OAuth2"], ["PersonalAccessToken"]],
    "list_team_projects": [["OAuth2"], ["PersonalAccessToken"]],
    "list_project_files": [["OAuth2"], ["PersonalAccessToken"]],
    "list_file_versions": [["OAuth2"], ["PersonalAccessToken"]],
    "list_file_comments": [["OAuth2"], ["PersonalAccessToken"]],
    "add_file_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "list_comment_reactions": [["OAuth2"], ["PersonalAccessToken"]],
    "add_comment_reaction": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_comment_reaction": [["OAuth2"], ["PersonalAccessToken"]],
    "get_current_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_team_components": [["OAuth2"], ["PersonalAccessToken"]],
    "list_file_components": [["OAuth2"], ["PersonalAccessToken"]],
    "get_component": [["OAuth2"], ["PersonalAccessToken"]],
    "list_component_sets": [["OAuth2"], ["PersonalAccessToken"]],
    "list_component_sets_file": [["OAuth2"], ["PersonalAccessToken"]],
    "get_component_set": [["OAuth2"], ["PersonalAccessToken"]],
    "list_team_styles": [["OAuth2"], ["PersonalAccessToken"]],
    "list_file_styles": [["OAuth2"], ["PersonalAccessToken"]],
    "get_style": [["OAuth2"], ["PersonalAccessToken"]],
    "list_webhooks": [["OAuth2"], ["PersonalAccessToken"]],
    "create_webhook": [["OAuth2"], ["PersonalAccessToken"]],
    "get_webhook": [["OAuth2"], ["PersonalAccessToken"]],
    "update_webhook": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_webhook": [["OAuth2"], ["PersonalAccessToken"]],
    "list_webhook_requests": [["OAuth2"], ["PersonalAccessToken"]],
    "list_activity_logs": [["OrgOAuth2"]],
    "list_payments": [["PersonalAccessToken"]],
    "list_local_variables": [["OAuth2"], ["PersonalAccessToken"]],
    "list_published_variables": [["OAuth2"], ["PersonalAccessToken"]],
    "bulk_modify_variables": [["OAuth2"], ["PersonalAccessToken"]],
    "list_dev_resources": [["OAuth2"], ["PersonalAccessToken"]],
    "create_dev_resources": [["OAuth2"], ["PersonalAccessToken"]],
    "update_dev_resources": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_dev_resource": [["OAuth2"], ["PersonalAccessToken"]],
    "list_library_component_actions": [["OAuth2"], ["PersonalAccessToken"]],
    "list_library_component_usages": [["OAuth2"], ["PersonalAccessToken"]],
    "list_library_style_actions": [["OAuth2"], ["PersonalAccessToken"]],
    "list_library_style_usages": [["OAuth2"], ["PersonalAccessToken"]],
    "list_library_variable_actions": [["OAuth2"], ["PersonalAccessToken"]],
    "list_library_variable_usages": [["OAuth2"], ["PersonalAccessToken"]]
}

"""
Authentication module for Google Drive API MCP server.

Generated: 2026-04-01 16:01:15 UTC
Generator: MCP Blacksmith v1.0.0 (https://mcpblacksmith.com)

This module contains:
1. Authentication class implementations (OAuth2)
2. Operation-to-auth requirements mapping (OPERATION_AUTH_MAP)
"""

from __future__ import annotations

import asyncio
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
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Callback Port Configuration
# ============================================================================

# OAuth2/OIDC callback server ports (configured in .env)
# Each auth scheme uses a different port to avoid conflicts when multiple
# schemes are active simultaneously (e.g., OAuth2 + OIDC).
OAUTH2_CALLBACK_PORT = int(os.environ.get("OAUTH2_CALLBACK_PORT", 9400))

# ============================================================================
# Authentication Classes
# ============================================================================

class OAuth2Auth:
    """
    OAuth 2.0 authentication for Google Drive API.

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
        Authorization URL: https://accounts.google.com/o/oauth2/auth
        Token URL: https://accounts.google.com/o/oauth2/token

    Available Scopes (configure via OAUTH2_SCOPES):
        - https://www.googleapis.com/auth/drive
        - https://www.googleapis.com/auth/drive.appdata
        - https://www.googleapis.com/auth/drive.apps.readonly
        - https://www.googleapis.com/auth/drive.file
        - https://www.googleapis.com/auth/drive.meet.readonly
        - https://www.googleapis.com/auth/drive.metadata
        - https://www.googleapis.com/auth/drive.metadata.readonly
        - https://www.googleapis.com/auth/drive.photos.readonly
        - https://www.googleapis.com/auth/drive.readonly
        - https://www.googleapis.com/auth/drive.scripts
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
        self.token_url = "https://accounts.google.com/o/oauth2/token"
        self.auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.refresh_url = None

        # Token storage (secure file-based, unique per scheme)
        self.token_dir = Path(__file__).parent / "tokens"
        self.token_file = self.token_dir / "oauth2_tokens.json"
        self.client: OAuth2Client | None = None
        self.token: dict | None = None
        self._auth_lock = asyncio.Lock()  # Prevents concurrent auth flows (dual browser tabs)

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
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode()

        # Build authorization URL
        # state param required by many providers (e.g., Figma) for CSRF protection
        from authlib.common.security import generate_token as _gen_token
        state = _gen_token(30)
        auth_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
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
                    # Verify state matches to prevent CSRF
                    callback_state = params.get("state", [None])[0]
                    if callback_state != state:
                        result["error"] = "state_mismatch"
                        result["error_description"] = "OAuth2 state parameter mismatch (possible CSRF)"
                        self.send_response(400)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(b"<html><body><h2>Authorization failed</h2><p>State mismatch</p></body></html>")
                        return
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
        # Serialize auth flow — prevent duplicate browser tabs from concurrent calls
        async with self._auth_lock:
            # Re-check after acquiring lock (another call may have completed auth)
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


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "get_user_info": [["OAuth2"]],
    "get_access_proposal": [["OAuth2"]],
    "list_access_proposals": [["OAuth2"]],
    "resolve_access_proposal": [["OAuth2"]],
    "get_approval": [["OAuth2"]],
    "list_approvals": [["OAuth2"]],
    "get_app": [["OAuth2"]],
    "list_apps": [["OAuth2"]],
    "get_change_start_page_token": [["OAuth2"]],
    "list_changes": [["OAuth2"]],
    "subscribe_to_changes": [["OAuth2"]],
    "stop_channel": [["OAuth2"]],
    "list_comments": [["OAuth2"]],
    "create_comment": [["OAuth2"]],
    "get_comment": [["OAuth2"]],
    "update_comment": [["OAuth2"]],
    "delete_comment": [["OAuth2"]],
    "list_shared_drives": [["OAuth2"]],
    "create_shared_drive": [["OAuth2"]],
    "get_shared_drive": [["OAuth2"]],
    "update_shared_drive": [["OAuth2"]],
    "delete_shared_drive": [["OAuth2"]],
    "hide_shared_drive": [["OAuth2"]],
    "unhide_shared_drive": [["OAuth2"]],
    "copy_file": [["OAuth2"]],
    "list_files": [["OAuth2"]],
    "create_file": [["OAuth2"]],
    "get_file": [["OAuth2"]],
    "update_file": [["OAuth2"]],
    "delete_file": [["OAuth2"]],
    "download_file": [["OAuth2"]],
    "empty_trash": [["OAuth2"]],
    "export_document": [["OAuth2"]],
    "generate_file_ids": [["OAuth2"]],
    "list_file_labels": [["OAuth2"]],
    "update_file_labels": [["OAuth2"]],
    "subscribe_file_changes": [["OAuth2"]],
    "get_operation": [["OAuth2"]],
    "list_file_permissions": [["OAuth2"]],
    "create_file_permission": [["OAuth2"]],
    "get_permission": [["OAuth2"]],
    "update_file_permission": [["OAuth2"]],
    "delete_permission": [["OAuth2"]],
    "list_replies": [["OAuth2"]],
    "create_comment_reply": [["OAuth2"]],
    "get_reply": [["OAuth2"]],
    "update_reply": [["OAuth2"]],
    "delete_reply": [["OAuth2"]],
    "get_file_revision": [["OAuth2"]],
    "update_file_revision": [["OAuth2"]],
    "delete_file_revision": [["OAuth2"]],
    "list_file_revisions": [["OAuth2"]],
    "list_team_drives": [["OAuth2"]],
    "create_team_drive": [["OAuth2"]],
    "get_team_drive": [["OAuth2"]],
    "update_team_drive": [["OAuth2"]],
    "delete_team_drive": [["OAuth2"]]
}

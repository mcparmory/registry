"""
Authentication module for Atlassian Confluence MCP server.

Generated: 2026-04-23 20:59:52 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)

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
import time
import webbrowser
from pathlib import Path

from authlib.common.security import generate_token
from authlib.integrations.httpx_client import OAuth2Client

logger = logging.getLogger(__name__)

__all__ = [
    "OAuth2Auth",
    "BasicAuth",
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
    OAuth 2.0 authentication for The Confluence Cloud REST API.

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
        Location: ./tokens/oauthdefinitions_tokens.json
        Permissions: 0o600 (owner read/write only)
        Format: JSON with access_token, refresh_token, expires_at

    URLs:
        Authorization URL: https://auth.atlassian.com/authorize
        Token URL: https://auth.atlassian.com/oauth/token

    Available Scopes (configure via OAUTH2_SCOPES):
        - write:confluence-content
        - read:confluence-space.summary
        - write:confluence-space
        - write:confluence-file
        - read:confluence-props
        - write:confluence-props
        - manage:confluence-configuration
        - read:confluence-content.all
        - read:confluence-content.summary
        - search:confluence
        - read:confluence-content.permission
        - read:confluence-user
        - read:confluence-groups
        - write:confluence-groups
        - readonly:content.attachment:confluence
        - read:content:confluence
        - write:content:confluence
        - read:content-details:confluence
        - read:space-details:confluence
        - delete:content:confluence
        - read:audit-log:confluence
        - write:audit-log:confluence
        - read:page:confluence
        - write:page:confluence
        - delete:page:confluence
        - read:attachment:confluence
        - write:attachment:confluence
        - delete:attachment:confluence
        - read:blogpost:confluence
        - write:blogpost:confluence
        - delete:blogpost:confluence
        - read:custom-content:confluence
        - write:custom-content:confluence
        - delete:custom-content:confluence
        - read:comment:confluence
        - write:comment:confluence
        - delete:comment:confluence
        - read:template:confluence
        - write:template:confluence
        - read:label:confluence
        - write:label:confluence
        - read:watcher:confluence
        - write:watcher:confluence
        - read:group:confluence
        - write:group:confluence
        - read:relation:confluence
        - write:relation:confluence
        - read:user:confluence
        - read:configuration:confluence
        - write:configuration:confluence
        - read:space:confluence
        - write:space:confluence
        - delete:space:confluence
        - read:space.permission:confluence
        - write:space.permission:confluence
        - read:space.property:confluence
        - write:space.property:confluence
        - read:user.property:confluence
        - write:user.property:confluence
        - read:space.setting:confluence
        - write:space.setting:confluence
        - read:analytics.content:confluence
        - read:content.permission:confluence
        - read:content.property:confluence
        - write:content.property:confluence
        - read:content.restriction:confluence
        - write:content.restriction:confluence
        - read:content.metadata:confluence
        - read:inlinetask:confluence
        - write:inlinetask:confluence
        - read:task:confluence
        - write:task:confluence
        - read:permission:confluence
        - read:whiteboard:confluence
        - write:whiteboard:confluence
        - delete:whiteboard:confluence
        - read:database:confluence
        - write:database:confluence
        - delete:database:confluence
        - read:embed:confluence
        - write:embed:confluence
        - delete:embed:confluence
        - read:folder:confluence
        - write:folder:confluence
        - delete:folder:confluence
        - read:app-data:confluence
        - write:app-data:confluence
        - read:email-address:confluence
        - read:hierarchical-content:confluence
        - read:forge-app:confluence
        - write:forge-app:confluence
        - moderate:core-content:confluence
        - moderate:comment:confluence
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
        # Redirect URI for authorization flows
        self.callback_port = int(os.getenv("OAUTH2_CALLBACK_PORT", "9400"))
        self.redirect_uri = f"http://localhost:{self.callback_port}/callback"

        # OAuth2 token URL (required for all flows that fetch tokens)
        self.token_url = "https://auth.atlassian.com/oauth/token"
        self.auth_url = "https://auth.atlassian.com/authorize"
        self.refresh_url = None

        # Token storage (secure file-based, unique per scheme)
        self.token_dir = Path(__file__).parent / "tokens"
        self.token_file = self.token_dir / "oauthdefinitions_tokens.json"
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
        normalized = dict(token)
        # Only set expires_at when expires_in is positive. A value of 0 (some
        # providers return this for non-expiring tokens) would otherwise mark
        # the token as immediately expired on every request.
        if "expires_at" not in normalized:
            expires_in = normalized.get("expires_in")
            if isinstance(expires_in, (int, float)) and expires_in > 0:
                normalized["expires_at"] = time.time() + int(expires_in)
        self.token_dir.mkdir(parents=True, exist_ok=True)
        self.token_file.write_text(json.dumps(normalized, indent=2))
        self.token_file.chmod(0o600)
        self.token = normalized

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
            return False  # Caller handles missing token separately
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

        loop = asyncio.get_running_loop()
        refresh_token_val = self.token["refresh_token"]

        for auth_method in ("client_secret_post", "client_secret_basic"):
            try:
                client = OAuth2Client(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    token_endpoint_auth_method=auth_method,
                )
                new_token = await loop.run_in_executor(
                    None,
                    lambda c=client: c.refresh_token(
                        self.token_url,
                        refresh_token=refresh_token_val,
                    ),
                )
                if new_token and new_token.get("access_token"):
                    self._save_token(dict(new_token))
                    return True
            except Exception as exc:
                err = str(exc).lower()
                if auth_method == "client_secret_post" and ("invalid_client" in err or "401" in err):
                    continue
                logger.debug("Token refresh failed (%s): %s", auth_method, exc)
                break
        return False

    async def authorize(self, port: int | None = None) -> dict:
        """
        Run OAuth2 authorization code flow with async local callback server.

        Starts an asyncio TCP server on localhost to receive the callback,
        opens the browser to the authorization URL, and waits for the user
        to authorize. Retries up to 5 adjacent ports if the primary port is in use.

        Args:
            port: Local callback server port (default: from OAUTH2_CALLBACK_PORT env or 9400)

        Returns:
            OAuth2 token dict with access_token, refresh_token, etc.

        Raises:
            ValueError: If authorization fails or is denied
            TimeoutError: If user doesn't complete authorization in 120 seconds
        """
        import errno
        import html as _html
        import urllib.parse

        base_port = port or self.callback_port

        # PKCE
        code_verifier = generate_token(48)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode()
        state = generate_token(30)

        callback_done: asyncio.Event = asyncio.Event()
        result: dict = {}

        async def _handle_connection(
            reader: asyncio.StreamReader, writer: asyncio.StreamWriter
        ) -> None:
            try:
                request_line = (await reader.readline()).decode(errors="replace").strip()
                while True:
                    line = await reader.readline()
                    if not line or line == b"\r\n":
                        break

                path = request_line.split(" ", 2)[1] if request_line.startswith("GET ") else ""
                parsed = urllib.parse.urlparse(path)
                params = urllib.parse.parse_qs(parsed.query)

                if parsed.path == "/callback" and ("code" in params or "error" in params):
                    if "error" in params:
                        result["error"] = params["error"][0]
                        result["error_description"] = params.get("error_description", [""])[0]
                        status = "400 Bad Request"
                        title = "Authorization failed"
                        body = f"<p style='color:#ff8787'>{_html.escape(result.get('error_description') or result['error'])}</p>"
                    else:
                        cb_state = params.get("state", [None])[0]
                        if cb_state != state:
                            result["error"] = "state_mismatch"
                            result["error_description"] = "OAuth2 state parameter mismatch (possible CSRF)"
                            status = "400 Bad Request"
                            title = "Authorization failed"
                            body = "<p style='color:#ff8787'>State mismatch — possible CSRF attack.</p>"
                        else:
                            result["code"] = params["code"][0]
                            status = "200 OK"
                            title = "Authorization successful"
                            body = "<p>You can close this window.</p>"
                    callback_done.set()
                else:
                    status, title, body = "200 OK", "Please wait\u2026", ""

                html = (
                    "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'>"
                    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
                    f"<title>{title}</title>"
                    "<style>*{margin:0;padding:0;box-sizing:border-box}"
                    "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;"
                    "background:#1a1a1a;color:#e8e8e8;display:flex;align-items:center;"
                    "justify-content:center;min-height:100vh}"
                    ".card{background:#242424;border:1px solid #333;border-radius:16px;"
                    "padding:48px 40px;text-align:center;max-width:420px;width:90%;"
                    "box-shadow:0 8px 32px rgba(0,0,0,.4)}"
                    ".logo{width:64px;height:64px;margin-bottom:32px;border-radius:12px}"
                    "h1{font-size:28px;font-weight:600;margin-bottom:10px}"
                    "p{font-size:15px;color:#888;line-height:1.5}"
                    ".footer{margin-top:32px;padding-top:20px;border-top:1px solid #333}"
                    ".footer a{color:#ff5722;text-decoration:none;font-size:13px}</style>"
                    "</head><body><div class='card'>"
                    "<img src='https://wjxawmrpsfuivlicnepc.supabase.co/storage/v1/object/public/newsletter/logo-blacksmith.png'"
                    " alt='MCP Blacksmith' class='logo'>"
                    f"<h1>{title}</h1>{body}"
                    "<div class='footer'><a href='https://mcpblacksmith.com'>mcpblacksmith.com</a></div>"
                    "</div></body></html>"
                )
                payload = html.encode()
                response = (
                    f"HTTP/1.1 {status}\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    f"Content-Length: {len(payload)}\r\n"
                    "Connection: close\r\n\r\n"
                ).encode() + payload
                writer.write(response)
                await writer.drain()
            finally:
                writer.close()
                await writer.wait_closed()

        # Bind to port with retry on EADDRINUSE
        bound_port = base_port
        server = None
        for attempt in range(5):
            try:
                server = await asyncio.start_server(
                    _handle_connection, "localhost", base_port + attempt
                )
                bound_port = base_port + attempt
                break
            except OSError as exc:
                if exc.errno != errno.EADDRINUSE or attempt == 4:
                    raise
        if server is None:
            raise OSError(f"Could not bind to any port in range {base_port}–{base_port + 4}")

        redirect_uri = f"http://localhost:{bound_port}/callback"

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

        async with server:
            logger.info("OAuth2 callback server listening on port %d", bound_port)
            print(f"\nAuthorize this application:\n\n  {auth_url}\n")
            webbrowser.open(auth_url)
            try:
                await asyncio.wait_for(callback_done.wait(), timeout=120)
            except asyncio.TimeoutError:
                raise TimeoutError(
                    "Authorization timed out (120s). "
                    "Please try again and complete authorization in the browser."
                )

        if "error" in result:
            raise ValueError(
                f"Authorization denied: {result['error']} — {result.get('error_description', '')}"
            )
        if "code" not in result:
            raise ValueError("Authorization failed: no code received after callback")

        # Token exchange with client_secret_post / client_secret_basic fallback
        loop = asyncio.get_running_loop()
        token = None
        last_exc: Exception | None = None

        for auth_method in ("client_secret_post", "client_secret_basic"):
            try:
                client = OAuth2Client(
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    token_endpoint_auth_method=auth_method,
                )
                token = await loop.run_in_executor(
                    None,
                    lambda c=client: c.fetch_token(
                        self.token_url,
                        code=result["code"],
                        redirect_uri=redirect_uri,
                        code_verifier=code_verifier,
                    ),
                )
                break
            except Exception as exc:
                last_exc = exc
                err = str(exc).lower()
                if auth_method == "client_secret_post" and ("invalid_client" in err or "401" in err):
                    continue
                raise

        if not token or not token.get("access_token"):
            raise ValueError(
                "Token exchange failed — no access_token received"
                + (f": {last_exc}" if last_exc else "")
            )

        # Scope validation — warn only, don't fail
        returned_scope = token.get("scope", "")
        if returned_scope:
            missing = set(self.scopes) - set(returned_scope.split())
            if missing:
                logger.warning(
                    "OAuth2 provider returned fewer scopes than requested. "
                    "Missing: %s. Some API operations may fail.",
                    ", ".join(sorted(missing)),
                )

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
            # elif: skip expiry check if authorize() just ran above (prevents double browser tab)
            elif self._is_token_expired():
                if not await self._refresh_token():
                    await self.authorize()

        if not self.token or not self.token.get("access_token"):
            raise ValueError("Failed to obtain access token after authorization attempt")

        return {"Authorization": f"Bearer {self.token['access_token']}"}

    def get_auth_params(self) -> dict:
        """OAuth2 uses headers, not query params."""
        return {}

class BasicAuth:
    """
    HTTP Basic Authentication for The Confluence Cloud REST API.

    Configuration:
        Credentials are automatically Base64-encoded.
        Provide raw username and password via environment variables.

    Security Note:
        Basic Auth transmits credentials in Base64 encoding (NOT encryption).
        Always use HTTPS to protect credentials in transit.
    """

    def __init__(self, env_var_username: str = "BASIC_AUTH_USERNAME",
                 env_var_password: str = "BASIC_AUTH_PASSWORD"):
        """Initialize Basic Auth from environment variables.

        Args:
            env_var_username: Environment variable name for the username.
            env_var_password: Environment variable name for the password.
        """
        self.username = os.getenv(env_var_username, "").strip()
        self.password = os.getenv(env_var_password, "").strip()

        # Check for empty username (password may be empty for API-key-as-username auth)
        if not self.username:
            raise ValueError(
                f"{env_var_username} environment variable must be set. "
                "Leave empty in .env to disable Basic Auth."
            )

        # Detect common placeholder patterns
        placeholders = ["placeholder", "your-", "example", "change-me", "todo"]
        username_lower = self.username.lower()
        password_lower = self.password.lower()

        if any(p in username_lower or p in password_lower for p in placeholders):
            raise ValueError(
                f"Basic Auth credentials appear to be placeholders (username: {self.username[:20]}...). "
                "Please set real credentials or leave empty to disable Basic Auth."
            )

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers with Basic Auth credentials."""
        # Encode credentials
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

        return {
            'Authorization': f'Basic {encoded_credentials}',
        }


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "list_audit_records": [["oAuthDefinitions"], ["basicAuth"]],
    "archive_pages": [["oAuthDefinitions"], ["basicAuth"]],
    "publish_blueprint_draft": [["oAuthDefinitions"], ["basicAuth"]],
    "publish_blueprint_draft_shared": [["oAuthDefinitions"], ["basicAuth"]],
    "search_content": [["oAuthDefinitions"], ["basicAuth"]],
    "delete_page_tree": [["oAuthDefinitions"], ["basicAuth"]],
    "move_page": [["oAuthDefinitions"], ["basicAuth"]],
    "add_attachment": [["oAuthDefinitions"], ["basicAuth"]],
    "upload_attachment": [["oAuthDefinitions"], ["basicAuth"]],
    "replace_attachment_data": [["oAuthDefinitions"], ["basicAuth"]],
    "download_attachment": [["oAuthDefinitions"], ["basicAuth"]],
    "get_macro_body": [["oAuthDefinitions"], ["basicAuth"]],
    "get_macro_body_converted": [["oAuthDefinitions"], ["basicAuth"]],
    "convert_macro_body_async": [["oAuthDefinitions"], ["basicAuth"]],
    "add_labels_to_content": [["oAuthDefinitions"], ["basicAuth"]],
    "remove_label_from_content": [["oAuthDefinitions"], ["basicAuth"]],
    "remove_label_from_content_by_path": [["oAuthDefinitions"], ["basicAuth"]],
    "list_page_watches": [["oAuthDefinitions"], ["basicAuth"]],
    "list_space_watches": [["oAuthDefinitions"], ["basicAuth"]],
    "copy_page_hierarchy": [["oAuthDefinitions"], ["basicAuth"]],
    "copy_page": [["oAuthDefinitions"], ["basicAuth"]],
    "verify_content_permission": [["oAuthDefinitions"], ["basicAuth"]],
    "list_content_restrictions": [["oAuthDefinitions"], ["basicAuth"]],
    "add_content_restrictions": [["oAuthDefinitions"], ["basicAuth"]],
    "replace_content_restrictions": [["oAuthDefinitions"], ["basicAuth"]],
    "remove_content_restrictions": [["oAuthDefinitions"], ["basicAuth"]],
    "list_content_restrictions_by_operation": [["oAuthDefinitions"], ["basicAuth"]],
    "get_content_restriction_for_operation": [["oAuthDefinitions"], ["basicAuth"]],
    "check_group_content_restriction": [["oAuthDefinitions"], ["basicAuth"]],
    "grant_group_content_restriction": [["oAuthDefinitions"], ["basicAuth"]],
    "revoke_group_content_restriction": [["oAuthDefinitions"], ["basicAuth"]],
    "check_content_restriction_for_user": [["oAuthDefinitions"], ["basicAuth"]],
    "grant_user_content_restriction": [["oAuthDefinitions"], ["basicAuth"]],
    "revoke_user_content_restriction": [["oAuthDefinitions"], ["basicAuth"]],
    "get_content_state": [["oAuthDefinitions"], ["basicAuth"]],
    "publish_content_with_state": [["oAuthDefinitions"], ["basicAuth"]],
    "publish_content_without_state": [["oAuthDefinitions"], ["basicAuth"]],
    "list_available_content_states": [["oAuthDefinitions"], ["basicAuth"]],
    "restore_content_version": [["oAuthDefinitions"], ["basicAuth"]],
    "delete_content_version": [["oAuthDefinitions"], ["basicAuth"]],
    "list_custom_content_states": [["oAuthDefinitions"], ["basicAuth"]],
    "convert_content_body_async": [["oAuthDefinitions"], ["basicAuth"]],
    "get_async_content_conversion": [["oAuthDefinitions"], ["basicAuth"]],
    "get_bulk_content_conversion_results": [["oAuthDefinitions"], ["basicAuth"]],
    "convert_content_bodies_async_bulk": [["oAuthDefinitions"], ["basicAuth"]],
    "list_label_contents": [["oAuthDefinitions"], ["basicAuth"]],
    "list_groups": [["oAuthDefinitions"], ["basicAuth"]],
    "create_group": [["oAuthDefinitions"], ["basicAuth"]],
    "get_group": [["oAuthDefinitions"], ["basicAuth"]],
    "delete_group": [["oAuthDefinitions"], ["basicAuth"]],
    "search_groups": [["oAuthDefinitions"], ["basicAuth"]],
    "list_group_members": [["oAuthDefinitions"], ["basicAuth"]],
    "add_user_to_group": [["oAuthDefinitions"], ["basicAuth"]],
    "remove_user_from_group": [["oAuthDefinitions"], ["basicAuth"]],
    "get_longtask": [["oAuthDefinitions"], ["basicAuth"]],
    "list_related_entities": [["oAuthDefinitions"], ["basicAuth"]],
    "check_relationship": [["oAuthDefinitions"], ["basicAuth"]],
    "create_relationship": [["oAuthDefinitions"], ["basicAuth"]],
    "delete_relationship": [["oAuthDefinitions"], ["basicAuth"]],
    "list_related_sources": [["oAuthDefinitions"], ["basicAuth"]],
    "search_content_global": [["oAuthDefinitions"], ["basicAuth"]],
    "search_users": [["oAuthDefinitions"], ["basicAuth"]],
    "create_space": [["oAuthDefinitions"], ["basicAuth"]],
    "create_private_space": [["oAuthDefinitions"], ["basicAuth"]],
    "update_space": [["oAuthDefinitions"], ["basicAuth"]],
    "delete_space": [["oAuthDefinitions"], ["basicAuth"]],
    "grant_custom_content_permission": [["oAuthDefinitions"], ["basicAuth"]],
    "delete_space_permission": [["oAuthDefinitions"], ["basicAuth"]],
    "list_space_content_states": [["oAuthDefinitions"], ["basicAuth"]],
    "list_space_content_by_state": [["oAuthDefinitions"], ["basicAuth"]],
    "get_space_theme": [["oAuthDefinitions"], ["basicAuth"]],
    "apply_space_theme": [["oAuthDefinitions"], ["basicAuth"]],
    "list_space_watchers": [["oAuthDefinitions"], ["basicAuth"]],
    "list_space_labels": [["oAuthDefinitions"], ["basicAuth"]],
    "add_space_labels": [["oAuthDefinitions"], ["basicAuth"]],
    "remove_label_from_space": [["oAuthDefinitions"], ["basicAuth"]],
    "create_template": [["oAuthDefinitions"], ["basicAuth"]],
    "update_template": [["oAuthDefinitions"], ["basicAuth"]],
    "list_blueprint_templates": [["oAuthDefinitions"], ["basicAuth"]],
    "list_templates": [["oAuthDefinitions"], ["basicAuth"]],
    "get_template": [["oAuthDefinitions"], ["basicAuth"]],
    "delete_template": [["oAuthDefinitions"], ["basicAuth"]],
    "get_user": [["oAuthDefinitions"], ["basicAuth"]],
    "get_anonymous_user": [["oAuthDefinitions"], ["basicAuth"]],
    "get_current_user": [["oAuthDefinitions"], ["basicAuth"]],
    "list_user_groups": [["oAuthDefinitions"], ["basicAuth"]],
    "list_users": [["oAuthDefinitions"], ["basicAuth"]],
    "check_content_watch_status": [["oAuthDefinitions"], ["basicAuth"]],
    "watch_content": [["oAuthDefinitions"], ["basicAuth"]],
    "unwatch_content": [["oAuthDefinitions"], ["basicAuth"]],
    "check_label_watch_status": [["oAuthDefinitions"], ["basicAuth"]],
    "watch_label": [["oAuthDefinitions"], ["basicAuth"]],
    "unwatch_label": [["oAuthDefinitions"], ["basicAuth"]],
    "check_space_watch_status": [["oAuthDefinitions"], ["basicAuth"]],
    "watch_space": [["oAuthDefinitions"], ["basicAuth"]],
    "unwatch_space": [["oAuthDefinitions"], ["basicAuth"]],
    "fetch_user_emails_bulk": [["oAuthDefinitions"], ["basicAuth"]],
    "get_content_views": [["oAuthDefinitions"], ["basicAuth"]],
    "get_content_viewers": [["oAuthDefinitions"], ["basicAuth"]],
    "list_user_properties": [["oAuthDefinitions"], ["basicAuth"]],
    "get_user_property": [["oAuthDefinitions"], ["basicAuth"]],
    "set_user_property": [["oAuthDefinitions"], ["basicAuth"]],
    "set_user_property_value": [["oAuthDefinitions"], ["basicAuth"]],
    "remove_user_property": [["oAuthDefinitions"], ["basicAuth"]]
}

"""
Authentication module for Atlassian Jira MCP server.

Generated: 2026-04-14 18:15:24 UTC
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
    OAuth 2.0 authentication for The Jira Cloud platform REST API.

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
        Authorization URL: https://auth.atlassian.com/authorize
        Token URL: https://auth.atlassian.com/oauth/token

    Available Scopes (configure via OAUTH2_SCOPES):
        - delete:async-task:jira
        - delete:attachment:jira
        - delete:avatar:jira
        - delete:comment.property:jira
        - delete:comment:jira
        - delete:dashboard.property:jira
        - delete:dashboard:jira
        - delete:field-configuration-scheme:jira
        - delete:field-configuration:jira
        - delete:field.option:jira
        - delete:field:jira
        - delete:filter.column:jira
        - delete:filter:jira
        - delete:group:jira
        - delete:issue-link-type:jira
        - delete:issue-link:jira
        - delete:issue-type-scheme:jira
        - delete:issue-type-screen-scheme:jira
        - delete:issue-type.property:jira
        - delete:issue-type:jira
        - delete:issue-worklog.property:jira
        - delete:issue-worklog:jira
        - delete:issue.property:jira
        - delete:issue.remote-link:jira
        - delete:issue:jira
        - delete:permission-scheme:jira
        - delete:permission:jira
        - delete:project-category:jira
        - delete:project-role:jira
        - delete:project-version:jira
        - delete:project.avatar:jira
        - delete:project.component:jira
        - delete:project.property:jira
        - delete:project:jira
        - delete:screen-scheme:jira
        - delete:screen-tab:jira
        - delete:screen:jira
        - delete:screenable-field:jira
        - delete:user-configuration:jira
        - delete:user.property:jira
        - delete:webhook:jira
        - delete:workflow-scheme:jira
        - delete:workflow.property:jira
        - delete:workflow:jira
        - manage:jira-configuration
        - manage:jira-project
        - manage:jira-webhook
        - read:app-data:jira
        - read:application-role:jira
        - read:attachment:jira
        - read:audit-log:jira
        - read:avatar:jira
        - read:comment.property:jira
        - read:comment:jira
        - read:custom-field-contextual-configuration:jira
        - read:dashboard.property:jira
        - read:dashboard:jira
        - read:email-address:jira
        - read:field-configuration-scheme:jira
        - read:field-configuration:jira
        - read:field.default-value:jira
        - read:field.option:jira
        - read:field.options:jira
        - read:field:jira
        - read:filter.column:jira
        - read:filter.default-share-scope:jira
        - read:filter:jira
        - read:group:jira
        - read:instance-configuration:jira
        - read:issue-details:jira
        - read:issue-event:jira
        - read:issue-field-values:jira
        - read:issue-link-type:jira
        - read:issue-link:jira
        - read:issue-meta:jira
        - read:issue-security-level:jira
        - read:issue-security-scheme:jira
        - read:issue-status:jira
        - read:issue-type-hierarchy:jira
        - read:issue-type-scheme:jira
        - read:issue-type-screen-scheme:jira
        - read:issue-type.property:jira
        - read:issue-type:jira
        - read:issue-worklog.property:jira
        - read:issue-worklog:jira
        - read:issue.changelog:jira
        - read:issue.property:jira
        - read:issue.remote-link:jira
        - read:issue.time-tracking:jira
        - read:issue.transition:jira
        - read:issue.vote:jira
        - read:issue.votes:jira
        - read:issue.watcher:jira
        - read:issue:jira
        - read:jira-expressions:jira
        - read:jira-user
        - read:jira-work
        - read:jql:jira
        - read:label:jira
        - read:license:jira
        - read:notification-scheme:jira
        - read:permission-scheme:jira
        - read:permission:jira
        - read:priority:jira
        - read:project-category:jira
        - read:project-role:jira
        - read:project-type:jira
        - read:project-version:jira
        - read:project.avatar:jira
        - read:project.component:jira
        - read:project.email:jira
        - read:project.feature:jira
        - read:project.property:jira
        - read:project:jira
        - read:resolution:jira
        - read:role:jira
        - read:screen-field:jira
        - read:screen-scheme:jira
        - read:screen-tab:jira
        - read:screen:jira
        - read:screenable-field:jira
        - read:status:jira
        - read:user-configuration:jira
        - read:user.columns:jira
        - read:user.property:jira
        - read:user:jira
        - read:webhook:jira
        - read:workflow-scheme:jira
        - read:workflow.property:jira
        - read:workflow:jira
        - send:notification:jira
        - validate:jql:jira
        - write:app-data:jira
        - write:attachment:jira
        - write:avatar:jira
        - write:comment.property:jira
        - write:comment:jira
        - write:custom-field-contextual-configuration:jira
        - write:dashboard.property:jira
        - write:dashboard:jira
        - write:field-configuration-scheme:jira
        - write:field-configuration:jira
        - write:field.default-value:jira
        - write:field.option:jira
        - write:field:jira
        - write:filter.column:jira
        - write:filter.default-share-scope:jira
        - write:filter:jira
        - write:group:jira
        - write:instance-configuration:jira
        - write:issue-link-type:jira
        - write:issue-link:jira
        - write:issue-type-scheme:jira
        - write:issue-type-screen-scheme:jira
        - write:issue-type.property:jira
        - write:issue-type:jira
        - write:issue-worklog.property:jira
        - write:issue-worklog:jira
        - write:issue.property:jira
        - write:issue.remote-link:jira
        - write:issue.time-tracking:jira
        - write:issue.vote:jira
        - write:issue.watcher:jira
        - write:issue:jira
        - write:jira-work
        - write:permission-scheme:jira
        - write:permission:jira
        - write:project-category:jira
        - write:project-role:jira
        - write:project-version:jira
        - write:project.avatar:jira
        - write:project.component:jira
        - write:project.email:jira
        - write:project.feature:jira
        - write:project.property:jira
        - write:project:jira
        - write:screen-scheme:jira
        - write:screen-tab:jira
        - write:screen:jira
        - write:screenable-field:jira
        - write:user-configuration:jira
        - write:user.property:jira
        - write:webhook:jira
        - write:workflow-scheme:jira
        - write:workflow.property:jira
        - write:workflow:jira
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
    HTTP Basic Authentication for The Jira Cloud platform REST API.

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
    "update_custom_field_values": [["OAuth2"], ["basicAuth"]],
    "update_custom_field_value": [["OAuth2"], ["basicAuth"]],
    "download_attachment": [["OAuth2"], ["basicAuth"]],
    "get_attachment_thumbnail": [["OAuth2"], ["basicAuth"]],
    "get_attachment": [["OAuth2"], ["basicAuth"]],
    "delete_attachment": [["OAuth2"], ["basicAuth"]],
    "get_attachment_metadata_with_contents": [["OAuth2"], ["basicAuth"]],
    "get_archive_contents_metadata": [["OAuth2"], ["basicAuth"]],
    "list_system_avatars": [["OAuth2"], ["basicAuth"]],
    "delete_issues_bulk": [["OAuth2"], ["basicAuth"]],
    "list_bulk_editable_fields": [["OAuth2"], ["basicAuth"]],
    "bulk_edit_issues": [["OAuth2"], ["basicAuth"]],
    "move_issues_bulk": [["OAuth2"], ["basicAuth"]],
    "list_issue_transitions": [["OAuth2"], ["basicAuth"]],
    "transition_issues_bulk": [["OAuth2"], ["basicAuth"]],
    "unwatch_issues_bulk": [["OAuth2"], ["basicAuth"]],
    "watch_issues": [["OAuth2"], ["basicAuth"]],
    "get_bulk_operation_progress": [["OAuth2"], ["basicAuth"]],
    "fetch_issue_changelogs": [["OAuth2"], ["basicAuth"]],
    "list_classification_levels": [["OAuth2"], ["basicAuth"]],
    "list_comments": [["OAuth2"], ["basicAuth"]],
    "list_comment_property_keys": [["OAuth2"], ["basicAuth"]],
    "get_comment_property": [["OAuth2"], ["basicAuth"]],
    "delete_comment_property": [["OAuth2"], ["basicAuth"]],
    "list_components": [["OAuth2"], ["basicAuth"]],
    "create_component": [["OAuth2"], ["basicAuth"]],
    "get_component": [["OAuth2"], ["basicAuth"]],
    "update_component": [["OAuth2"], ["basicAuth"]],
    "delete_component": [["OAuth2"], ["basicAuth"]],
    "get_component_issue_counts": [["OAuth2"], ["basicAuth"]],
    "get_custom_field_option": [["OAuth2"], ["basicAuth"]],
    "list_dashboards": [["OAuth2"], ["basicAuth"]],
    "create_dashboard": [["OAuth2"], ["basicAuth"]],
    "update_dashboards_bulk": [["OAuth2"], ["basicAuth"]],
    "list_dashboard_gadgets": [["OAuth2"], ["basicAuth"]],
    "search_dashboards": [["OAuth2"], ["basicAuth"]],
    "update_dashboard_gadget": [["OAuth2"], ["basicAuth"]],
    "remove_gadget": [["OAuth2"], ["basicAuth"]],
    "list_dashboard_item_property_keys": [["OAuth2"], ["basicAuth"]],
    "get_dashboard_item_property": [["OAuth2"], ["basicAuth"]],
    "remove_dashboard_item_property": [["OAuth2"], ["basicAuth"]],
    "get_dashboard": [["OAuth2"], ["basicAuth"]],
    "update_dashboard": [["OAuth2"], ["basicAuth"]],
    "delete_dashboard": [["OAuth2"], ["basicAuth"]],
    "duplicate_dashboard": [["OAuth2"], ["basicAuth"]],
    "list_events": [["OAuth2"], ["basicAuth"]],
    "evaluate_jira_expression": [["OAuth2"], ["basicAuth"]],
    "list_fields": [["OAuth2"], ["basicAuth"]],
    "list_fields_search": [["OAuth2"], ["basicAuth"]],
    "list_trashed_fields": [["OAuth2"], ["basicAuth"]],
    "list_custom_field_context_issue_type_mappings": [["OAuth2"], ["basicAuth"]],
    "list_custom_field_options": [["OAuth2"], ["basicAuth"]],
    "create_custom_field_options": [["OAuth2"], ["basicAuth"]],
    "update_custom_field_options": [["OAuth2"], ["basicAuth"]],
    "reorder_custom_field_options": [["OAuth2"], ["basicAuth"]],
    "delete_custom_field_option": [["OAuth2"], ["basicAuth"]],
    "list_field_screens": [["OAuth2"], ["basicAuth"]],
    "list_field_options": [["OAuth2"], ["basicAuth"]],
    "add_field_option": [["OAuth2"], ["basicAuth"]],
    "list_field_option_suggestions": [["OAuth2"], ["basicAuth"]],
    "search_field_options": [["OAuth2"], ["basicAuth"]],
    "get_field_option": [["OAuth2"], ["basicAuth"]],
    "replace_field_option": [["OAuth2"], ["basicAuth"]],
    "delete_custom_field": [["OAuth2"], ["basicAuth"]],
    "restore_custom_field": [["OAuth2"], ["basicAuth"]],
    "move_custom_field_to_trash": [["OAuth2"], ["basicAuth"]],
    "create_filter": [["OAuth2"], ["basicAuth"]],
    "get_default_share_scope": [["OAuth2"], ["basicAuth"]],
    "list_favorite_filters": [["OAuth2"], ["basicAuth"]],
    "list_my_filters": [["OAuth2"], ["basicAuth"]],
    "search_filters": [["OAuth2"], ["basicAuth"]],
    "get_filter": [["OAuth2"], ["basicAuth"]],
    "update_filter": [["OAuth2"], ["basicAuth"]],
    "delete_filter": [["OAuth2"], ["basicAuth"]],
    "list_filter_columns": [["OAuth2"], ["basicAuth"]],
    "add_filter_to_favorites": [["OAuth2"], ["basicAuth"]],
    "remove_filter_favorite": [["OAuth2"], ["basicAuth"]],
    "transfer_filter_ownership": [["OAuth2"], ["basicAuth"]],
    "list_filter_permissions": [["OAuth2"], ["basicAuth"]],
    "grant_filter_share_permission": [["OAuth2"], ["basicAuth"]],
    "get_filter_share_permission": [["OAuth2"], ["basicAuth"]],
    "remove_filter_share_permission": [["OAuth2"], ["basicAuth"]],
    "create_group": [["OAuth2"], ["basicAuth"]],
    "delete_group": [["OAuth2"], ["basicAuth"]],
    "list_groups": [["OAuth2"], ["basicAuth"]],
    "list_group_members": [["OAuth2"], ["basicAuth"]],
    "add_user_to_group": [["OAuth2"], ["basicAuth"]],
    "search_groups": [["OAuth2"], ["basicAuth"]],
    "search_users_and_groups": [["OAuth2"], ["basicAuth"]],
    "create_issue": [["OAuth2"], ["basicAuth"]],
    "archive_issues_by_jql": [["OAuth2"], ["basicAuth"]],
    "archive_issues": [["OAuth2"], ["basicAuth"]],
    "create_issues_bulk": [["OAuth2"], ["basicAuth"]],
    "fetch_issues": [["OAuth2"], ["basicAuth"]],
    "list_issue_types_for_creation": [["OAuth2"], ["basicAuth"]],
    "get_issue_creation_fields": [["OAuth2"], ["basicAuth"]],
    "list_issue_limit_violations": [["OAuth2"], ["basicAuth"]],
    "search_issues_picker": [["OAuth2"], ["basicAuth"]],
    "set_issue_properties_bulk": [["OAuth2"], ["basicAuth"]],
    "set_issue_properties_bulk_per_issue": [["OAuth2"], ["basicAuth"]],
    "set_issue_property_bulk": [["OAuth2"], ["basicAuth"]],
    "delete_issue_property_bulk": [["OAuth2"], ["basicAuth"]],
    "restore_issues": [["OAuth2"], ["basicAuth"]],
    "check_watched_issues_bulk": [["OAuth2"], ["basicAuth"]],
    "retrieve_issue": [["OAuth2"], ["basicAuth"]],
    "update_issue": [["OAuth2"], ["basicAuth"]],
    "delete_issue": [["OAuth2"], ["basicAuth"]],
    "assign_issue": [["OAuth2"], ["basicAuth"]],
    "attach_files": [["OAuth2"], ["basicAuth"]],
    "list_issue_changelogs": [["OAuth2"], ["basicAuth"]],
    "fetch_changelogs": [["OAuth2"], ["basicAuth"]],
    "list_issue_comments": [["OAuth2"], ["basicAuth"]],
    "add_comment": [["OAuth2"], ["basicAuth"]],
    "get_comment": [["OAuth2"], ["basicAuth"]],
    "update_comment": [["OAuth2"], ["basicAuth"]],
    "delete_comment": [["OAuth2"], ["basicAuth"]],
    "get_issue_editable_fields": [["OAuth2"], ["basicAuth"]],
    "send_issue_notification": [["OAuth2"], ["basicAuth"]],
    "list_issue_property_keys": [["OAuth2"], ["basicAuth"]],
    "get_issue_property": [["OAuth2"], ["basicAuth"]],
    "remove_issue_property": [["OAuth2"], ["basicAuth"]],
    "list_remote_issue_links": [["OAuth2"], ["basicAuth"]],
    "link_remote_issue": [["OAuth2"], ["basicAuth"]],
    "get_remote_link": [["OAuth2"], ["basicAuth"]],
    "update_remote_link": [["OAuth2"], ["basicAuth"]],
    "delete_remote_link_by_id": [["OAuth2"], ["basicAuth"]],
    "list_issue_transitions_single": [["OAuth2"], ["basicAuth"]],
    "transition_issue": [["OAuth2"], ["basicAuth"]],
    "retrieve_issue_votes": [["OAuth2"], ["basicAuth"]],
    "vote_issue": [["OAuth2"], ["basicAuth"]],
    "remove_vote": [["OAuth2"], ["basicAuth"]],
    "list_issue_watchers": [["OAuth2"], ["basicAuth"]],
    "add_issue_watcher": [["OAuth2"], ["basicAuth"]],
    "remove_issue_watcher": [["OAuth2"], ["basicAuth"]],
    "list_issue_worklogs": [["OAuth2"], ["basicAuth"]],
    "record_worklog": [["OAuth2"], ["basicAuth"]],
    "delete_worklogs": [["OAuth2"], ["basicAuth"]],
    "move_worklogs": [["OAuth2"], ["basicAuth"]],
    "get_worklog": [["OAuth2"], ["basicAuth"]],
    "update_worklog": [["OAuth2"], ["basicAuth"]],
    "remove_worklog": [["OAuth2"], ["basicAuth"]],
    "list_worklog_property_keys": [["OAuth2"], ["basicAuth"]],
    "get_worklog_property": [["OAuth2"], ["basicAuth"]],
    "remove_worklog_property": [["OAuth2"], ["basicAuth"]],
    "create_issue_link": [["OAuth2"], ["basicAuth"]],
    "get_issue_link": [["OAuth2"], ["basicAuth"]],
    "remove_issue_link": [["OAuth2"], ["basicAuth"]],
    "list_issue_link_types": [["OAuth2"], ["basicAuth"]],
    "get_issue_link_type": [["OAuth2"], ["basicAuth"]],
    "delete_issue_link_type": [["OAuth2"], ["basicAuth"]],
    "export_archived_issues": [["OAuth2"], ["basicAuth"]],
    "list_issue_types": [["OAuth2"], ["basicAuth"]],
    "list_issue_types_project": [["OAuth2"], ["basicAuth"]],
    "get_issue_type": [["OAuth2"], ["basicAuth"]],
    "delete_issue_type": [["OAuth2"], ["basicAuth"]],
    "list_alternative_issue_types": [["OAuth2"], ["basicAuth"]],
    "upload_issue_type_avatar": [["OAuth2"], ["basicAuth"]],
    "list_issue_type_property_keys": [["OAuth2"], ["basicAuth"]],
    "get_issue_type_property": [["OAuth2"], ["basicAuth"]],
    "list_issue_type_schemes": [["OAuth2"], ["basicAuth"]],
    "list_issue_type_schemes_for_projects": [["OAuth2"], ["basicAuth"]],
    "list_jql_autocomplete_data": [["OAuth2"], ["basicAuth"]],
    "list_jql_autocomplete_data_filtered": [["OAuth2"], ["basicAuth"]],
    "get_jql_autocomplete_suggestions": [["OAuth2"], ["basicAuth"]],
    "filter_issues_by_jql": [["OAuth2"], ["basicAuth"]],
    "validate_jql_queries": [["OAuth2"], ["basicAuth"]],
    "list_labels": [["OAuth2"], ["basicAuth"]],
    "check_permissions": [["OAuth2"], ["basicAuth"]],
    "get_user_preference": [["OAuth2"], ["basicAuth"]],
    "get_locale": [["OAuth2"], ["basicAuth"]],
    "get_current_user": [["OAuth2"], ["basicAuth"]],
    "list_notification_scheme_project_mappings": [["OAuth2"], ["basicAuth"]],
    "list_permissions": [["OAuth2"], ["basicAuth"]],
    "check_permissions_bulk": [["OAuth2"], ["basicAuth"]],
    "list_permitted_projects": [["OAuth2"], ["basicAuth"]],
    "list_plans": [["OAuth2"], ["basicAuth"]],
    "create_plan": [["OAuth2"], ["basicAuth"]],
    "retrieve_plan": [["OAuth2"], ["basicAuth"]],
    "update_plan": [["OAuth2"], ["basicAuth"]],
    "archive_plan": [["OAuth2"], ["basicAuth"]],
    "duplicate_plan": [["OAuth2"], ["basicAuth"]],
    "list_plan_teams": [["OAuth2"], ["basicAuth"]],
    "add_team_to_plan": [["OAuth2"], ["basicAuth"]],
    "get_team": [["OAuth2"], ["basicAuth"]],
    "update_team_planning_settings": [["OAuth2"], ["basicAuth"]],
    "remove_team_from_plan": [["OAuth2"], ["basicAuth"]],
    "create_plan_only_team": [["OAuth2"], ["basicAuth"]],
    "get_plan_only_team": [["OAuth2"], ["basicAuth"]],
    "update_plan_team": [["OAuth2"], ["basicAuth"]],
    "remove_plan_only_team": [["OAuth2"], ["basicAuth"]],
    "trash_plan": [["OAuth2"], ["basicAuth"]],
    "get_priority": [["OAuth2"], ["basicAuth"]],
    "remove_priority": [["OAuth2"], ["basicAuth"]],
    "list_available_priorities": [["OAuth2"], ["basicAuth"]],
    "list_priorities": [["OAuth2"], ["basicAuth"]],
    "create_project": [["OAuth2"], ["basicAuth"]],
    "create_project_from_template": [["OAuth2"], ["basicAuth"]],
    "list_recent_projects": [["OAuth2"], ["basicAuth"]],
    "list_projects": [["OAuth2"], ["basicAuth"]],
    "list_project_types": [["OAuth2"], ["basicAuth"]],
    "list_accessible_project_types": [["OAuth2"], ["basicAuth"]],
    "get_project_type": [["OAuth2"], ["basicAuth"]],
    "get_accessible_project_type": [["OAuth2"], ["basicAuth"]],
    "get_project": [["OAuth2"], ["basicAuth"]],
    "update_project": [["OAuth2"], ["basicAuth"]],
    "delete_project": [["OAuth2"], ["basicAuth"]],
    "archive_project": [["OAuth2"], ["basicAuth"]],
    "set_project_avatar": [["OAuth2"], ["basicAuth"]],
    "remove_project_avatar": [["OAuth2"], ["basicAuth"]],
    "upload_project_avatar": [["OAuth2"], ["basicAuth"]],
    "list_project_avatars": [["OAuth2"], ["basicAuth"]],
    "get_project_classification": [["OAuth2"], ["basicAuth"]],
    "list_project_components": [["OAuth2"], ["basicAuth"]],
    "get_project_components_all": [["OAuth2"], ["basicAuth"]],
    "delete_project_async": [["OAuth2"], ["basicAuth"]],
    "list_project_features": [["OAuth2"], ["basicAuth"]],
    "list_project_property_keys": [["OAuth2"], ["basicAuth"]],
    "get_project_property": [["OAuth2"], ["basicAuth"]],
    "remove_project_property": [["OAuth2"], ["basicAuth"]],
    "restore_project": [["OAuth2"], ["basicAuth"]],
    "list_project_roles": [["OAuth2"], ["basicAuth"]],
    "get_project_role": [["OAuth2"], ["basicAuth"]],
    "add_project_role_actors": [["OAuth2"], ["basicAuth"]],
    "replace_project_role_actors": [["OAuth2"], ["basicAuth"]],
    "remove_actor_from_project_role": [["OAuth2"], ["basicAuth"]],
    "list_project_roles_with_details": [["OAuth2"], ["basicAuth"]],
    "list_project_statuses": [["OAuth2"], ["basicAuth"]],
    "list_project_versions": [["OAuth2"], ["basicAuth"]],
    "list_project_versions_all": [["OAuth2"], ["basicAuth"]],
    "get_project_email": [["OAuth2"], ["basicAuth"]],
    "get_issue_type_hierarchy": [["OAuth2"], ["basicAuth"]],
    "list_security_levels_project": [["OAuth2"], ["basicAuth"]],
    "list_project_categories": [["OAuth2"], ["basicAuth"]],
    "create_project_category": [["OAuth2"], ["basicAuth"]],
    "get_project_category": [["OAuth2"], ["basicAuth"]],
    "update_project_category": [["OAuth2"], ["basicAuth"]],
    "delete_project_category": [["OAuth2"], ["basicAuth"]],
    "list_project_fields": [["OAuth2"], ["basicAuth"]],
    "validate_project_key": [["OAuth2"], ["basicAuth"]],
    "validate_project_key_generate": [["OAuth2"], ["basicAuth"]],
    "validate_project_name": [["OAuth2"], ["basicAuth"]],
    "redact_issue_fields": [["basicAuth"]],
    "list_resolutions": [["OAuth2"], ["basicAuth"]],
    "get_resolution": [["OAuth2"], ["basicAuth"]],
    "update_resolution": [["OAuth2"], ["basicAuth"]],
    "delete_resolution": [["OAuth2"], ["basicAuth"]],
    "list_project_roles_global": [["OAuth2"], ["basicAuth"]],
    "get_project_role_global": [["OAuth2"], ["basicAuth"]],
    "update_project_role": [["OAuth2"], ["basicAuth"]],
    "update_project_role_full": [["OAuth2"], ["basicAuth"]],
    "delete_project_role": [["OAuth2"], ["basicAuth"]],
    "list_screen_fields": [["OAuth2"], ["basicAuth"]],
    "count_issues": [["OAuth2"], ["basicAuth"]],
    "search_issues": [["OAuth2"], ["basicAuth"]],
    "search_issues_jql": [["OAuth2"], ["basicAuth"]],
    "get_security_level": [["OAuth2"], ["basicAuth"]],
    "list_statuses": [["OAuth2"], ["basicAuth"]],
    "get_status": [["OAuth2"], ["basicAuth"]],
    "list_status_categories": [["OAuth2"], ["basicAuth"]],
    "get_status_category": [["OAuth2"], ["basicAuth"]],
    "list_statuses_bulk": [["OAuth2"], ["basicAuth"]],
    "delete_statuses": [["OAuth2"], ["basicAuth"]],
    "list_statuses_by_name": [["OAuth2"], ["basicAuth"]],
    "search_statuses": [["OAuth2"], ["basicAuth"]],
    "list_issue_type_usages": [["OAuth2"], ["basicAuth"]],
    "list_project_usages_by_status": [["OAuth2"], ["basicAuth"]],
    "list_workflow_usages_by_status": [["OAuth2"], ["basicAuth"]],
    "get_task": [["OAuth2"], ["basicAuth"]],
    "cancel_task": [["OAuth2"], ["basicAuth"]],
    "list_avatars": [["OAuth2"], ["basicAuth"]],
    "upload_avatar": [["OAuth2"], ["basicAuth"]],
    "delete_avatar": [["OAuth2"], ["basicAuth"]],
    "get_avatar_image_by_avatar_id": [["OAuth2"], ["basicAuth"]],
    "get_avatar_image_by_entity": [["OAuth2"], ["basicAuth"]],
    "get_user": [["OAuth2"], ["basicAuth"]],
    "create_user": [["OAuth2"], ["basicAuth"]],
    "delete_user": [["OAuth2"], ["basicAuth"]],
    "list_assignable_users_multiproject": [["OAuth2"], ["basicAuth"]],
    "list_assignable_users": [["OAuth2"], ["basicAuth"]],
    "list_users_by_account_ids": [["OAuth2"], ["basicAuth"]],
    "list_user_account_ids": [["OAuth2"], ["basicAuth"]],
    "list_user_default_columns": [["OAuth2"], ["basicAuth"]],
    "list_user_groups": [["OAuth2"], ["basicAuth"]],
    "search_users_by_permissions": [["OAuth2"], ["basicAuth"]],
    "search_users_picker": [["OAuth2"], ["basicAuth"]],
    "list_user_property_keys": [["OAuth2"], ["basicAuth"]],
    "get_user_property": [["OAuth2"], ["basicAuth"]],
    "remove_user_property": [["OAuth2"], ["basicAuth"]],
    "search_users": [["OAuth2"], ["basicAuth"]],
    "search_users_query": [["OAuth2"], ["basicAuth"]],
    "search_users_by_query": [["OAuth2"], ["basicAuth"]],
    "search_browsable_users": [["OAuth2"], ["basicAuth"]],
    "list_users_default": [["OAuth2"], ["basicAuth"]],
    "list_users": [["OAuth2"], ["basicAuth"]],
    "create_version": [["OAuth2"], ["basicAuth"]],
    "get_version": [["OAuth2"], ["basicAuth"]],
    "update_version": [["OAuth2"], ["basicAuth"]],
    "merge_versions": [["OAuth2"], ["basicAuth"]],
    "reorder_version": [["OAuth2"], ["basicAuth"]],
    "count_version_related_issues": [["OAuth2"], ["basicAuth"]],
    "list_related_work": [["OAuth2"], ["basicAuth"]],
    "create_related_work": [["OAuth2"], ["basicAuth"]],
    "update_related_work": [["OAuth2"], ["basicAuth"]],
    "delete_and_replace_version": [["OAuth2"], ["basicAuth"]],
    "get_version_unresolved_issues": [["OAuth2"], ["basicAuth"]],
    "delete_related_work": [["OAuth2"], ["basicAuth"]],
    "list_workflow_history": [["OAuth2"], ["basicAuth"]],
    "list_workflow_issue_type_usages": [["OAuth2"], ["basicAuth"]],
    "list_workflow_projects": [["OAuth2"], ["basicAuth"]],
    "list_workflow_capabilities": [["OAuth2"], ["basicAuth"]],
    "get_workflow_default_editor": [["OAuth2"], ["basicAuth"]],
    "preview_workflows": [["OAuth2"], ["basicAuth"]],
    "list_workflow_schemes_by_projects": [["OAuth2"], ["basicAuth"]],
    "list_workflow_scheme_projects": [["OAuth2"], ["basicAuth"]],
    "list_deleted_worklogs": [["OAuth2"], ["basicAuth"]],
    "get_worklogs": [["OAuth2"], ["basicAuth"]],
    "list_worklogs_modified_since": [["OAuth2"], ["basicAuth"]]
}

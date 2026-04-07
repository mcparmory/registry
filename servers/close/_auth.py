"""
Authentication module for Close API MCP server.

Generated: 2026-04-07 08:42:04 UTC
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
    OAuth 2.0 authentication for Close API.

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
        Authorization URL: https://app.close.com/oauth2/authorize/
        Token URL: https://api.close.com/oauth2/token/
        Refresh URL: https://api.close.com/oauth2/token/

    Available Scopes (configure via OAUTH2_SCOPES):
        - all.full_access
        - offline_access
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
        self.token_url = "https://api.close.com/oauth2/token/"
        self.auth_url = "https://app.close.com/oauth2/authorize/"
        self.refresh_url = "https://api.close.com/oauth2/token/"

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
        if "expires_in" in normalized and "expires_at" not in normalized:
            normalized["expires_at"] = time.time() + int(normalized["expires_in"])
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
    HTTP Basic Authentication for Close API.

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
            'Content-Type': 'application/json'
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
    "list_leads": [["oauth2"], ["basicAuth"]],
    "create_lead": [["oauth2"], ["basicAuth"]],
    "get_lead": [["oauth2"], ["basicAuth"]],
    "update_lead": [["oauth2"], ["basicAuth"]],
    "delete_lead": [["oauth2"], ["basicAuth"]],
    "merge_leads": [["oauth2"], ["basicAuth"]],
    "list_contacts": [["oauth2"], ["basicAuth"]],
    "create_contact": [["oauth2"], ["basicAuth"]],
    "get_contact": [["oauth2"], ["basicAuth"]],
    "update_contact": [["oauth2"], ["basicAuth"]],
    "delete_contact": [["oauth2"], ["basicAuth"]],
    "list_activities": [["oauth2"], ["basicAuth"]],
    "list_calls": [["oauth2"], ["basicAuth"]],
    "log_call_activity": [["oauth2"], ["basicAuth"]],
    "get_call": [["oauth2"], ["basicAuth"]],
    "update_call": [["oauth2"], ["basicAuth"]],
    "delete_call": [["oauth2"], ["basicAuth"]],
    "list_created_activities": [["oauth2"], ["basicAuth"]],
    "get_activity": [["oauth2"], ["basicAuth"]],
    "list_email_activities": [["oauth2"], ["basicAuth"]],
    "create_activity_email": [["oauth2"], ["basicAuth"]],
    "get_email_activity": [["oauth2"], ["basicAuth"]],
    "update_email_activity": [["oauth2"], ["basicAuth"]],
    "delete_email_activity": [["oauth2"], ["basicAuth"]],
    "list_email_threads": [["oauth2"], ["basicAuth"]],
    "get_email_thread": [["oauth2"], ["basicAuth"]],
    "delete_email_thread": [["oauth2"], ["basicAuth"]],
    "list_lead_status_changes": [["oauth2"], ["basicAuth"]],
    "log_lead_status_change": [["oauth2"], ["basicAuth"]],
    "get_lead_status_change": [["oauth2"], ["basicAuth"]],
    "delete_lead_status_change": [["oauth2"], ["basicAuth"]],
    "search_meetings": [["oauth2"], ["basicAuth"]],
    "get_meeting": [["oauth2"], ["basicAuth"]],
    "update_meeting": [["oauth2"], ["basicAuth"]],
    "delete_meeting": [["oauth2"], ["basicAuth"]],
    "create_or_update_meeting_integration": [["oauth2"], ["basicAuth"]],
    "list_notes": [["oauth2"], ["basicAuth"]],
    "create_note": [["oauth2"], ["basicAuth"]],
    "get_note": [["oauth2"], ["basicAuth"]],
    "update_note": [["oauth2"], ["basicAuth"]],
    "delete_activity_note": [["oauth2"], ["basicAuth"]],
    "list_opportunity_status_changes": [["oauth2"], ["basicAuth"]],
    "log_opportunity_status_change": [["oauth2"], ["basicAuth"]],
    "get_opportunity_status_change": [["oauth2"], ["basicAuth"]],
    "delete_opportunity_status_change": [["oauth2"], ["basicAuth"]],
    "list_sms_activities": [["oauth2"], ["basicAuth"]],
    "create_sms_activity": [["oauth2"], ["basicAuth"]],
    "get_sms_activity": [["oauth2"], ["basicAuth"]],
    "update_sms_activity": [["oauth2"], ["basicAuth"]],
    "delete_sms_activity": [["oauth2"], ["basicAuth"]],
    "list_completed_activities": [["oauth2"], ["basicAuth"]],
    "get_completed_task": [["oauth2"], ["basicAuth"]],
    "delete_completed_task": [["oauth2"], ["basicAuth"]],
    "list_lead_merges": [["oauth2"], ["basicAuth"]],
    "get_lead_merge": [["oauth2"], ["basicAuth"]],
    "list_whatsapp_messages": [["oauth2"], ["basicAuth"]],
    "create_whatsapp_message": [["oauth2"], ["basicAuth"]],
    "get_whatsapp_message": [["oauth2"], ["basicAuth"]],
    "update_whatsapp_message": [["oauth2"], ["basicAuth"]],
    "delete_whatsapp_message": [["oauth2"], ["basicAuth"]],
    "list_form_submissions": [["oauth2"], ["basicAuth"]],
    "get_form_submission": [["oauth2"], ["basicAuth"]],
    "delete_form_submission": [["oauth2"], ["basicAuth"]],
    "list_opportunities": [["oauth2"], ["basicAuth"]],
    "create_opportunity": [["oauth2"], ["basicAuth"]],
    "get_opportunity": [["oauth2"], ["basicAuth"]],
    "update_opportunity": [["oauth2"], ["basicAuth"]],
    "delete_opportunity": [["oauth2"], ["basicAuth"]],
    "list_tasks": [["oauth2"], ["basicAuth"]],
    "create_task": [["oauth2"], ["basicAuth"]],
    "update_tasks": [["oauth2"], ["basicAuth"]],
    "get_task": [["oauth2"], ["basicAuth"]],
    "update_task": [["oauth2"], ["basicAuth"]],
    "delete_task": [["oauth2"], ["basicAuth"]],
    "list_outcomes": [["oauth2"], ["basicAuth"]],
    "create_outcome": [["oauth2"], ["basicAuth"]],
    "get_outcome": [["oauth2"], ["basicAuth"]],
    "update_outcome": [["oauth2"], ["basicAuth"]],
    "delete_outcome": [["oauth2"], ["basicAuth"]],
    "update_membership": [["oauth2"], ["basicAuth"]],
    "provision_membership": [["oauth2"], ["basicAuth"]],
    "bulk_update_memberships": [["oauth2"], ["basicAuth"]],
    "list_pinned_views": [["oauth2"], ["basicAuth"]],
    "set_membership_pinned_views": [["oauth2"], ["basicAuth"]],
    "get_current_user": [["oauth2"], ["basicAuth"]],
    "get_user": [["oauth2"], ["basicAuth"]],
    "list_users": [["oauth2"], ["basicAuth"]],
    "list_user_availability": [["oauth2"], ["basicAuth"]],
    "get_organization": [["oauth2"], ["basicAuth"]],
    "update_organization": [["oauth2"], ["basicAuth"]],
    "get_role": [["oauth2"], ["basicAuth"]],
    "list_roles": [["oauth2"], ["basicAuth"]],
    "create_role": [["oauth2"], ["basicAuth"]],
    "update_role": [["oauth2"], ["basicAuth"]],
    "delete_role": [["oauth2"], ["basicAuth"]],
    "list_lead_statuses": [["oauth2"], ["basicAuth"]],
    "create_lead_status": [["oauth2"], ["basicAuth"]],
    "rename_lead_status": [["oauth2"], ["basicAuth"]],
    "delete_lead_status": [["oauth2"], ["basicAuth"]],
    "list_opportunity_statuses": [["oauth2"], ["basicAuth"]],
    "create_opportunity_status": [["oauth2"], ["basicAuth"]],
    "rename_opportunity_status": [["oauth2"], ["basicAuth"]],
    "delete_opportunity_status": [["oauth2"], ["basicAuth"]],
    "list_pipelines": [["oauth2"], ["basicAuth"]],
    "create_pipeline": [["oauth2"], ["basicAuth"]],
    "update_pipeline": [["oauth2"], ["basicAuth"]],
    "delete_pipeline": [["oauth2"], ["basicAuth"]],
    "list_groups": [["oauth2"], ["basicAuth"]],
    "create_group": [["oauth2"], ["basicAuth"]],
    "get_group": [["oauth2"], ["basicAuth"]],
    "rename_group": [["oauth2"], ["basicAuth"]],
    "delete_group": [["oauth2"], ["basicAuth"]],
    "add_user_to_group": [["oauth2"], ["basicAuth"]],
    "remove_group_member": [["oauth2"], ["basicAuth"]],
    "list_activity_metrics": [["oauth2"], ["basicAuth"]],
    "generate_activity_report": [["oauth2"], ["basicAuth"]],
    "list_sent_emails_report": [["oauth2"], ["basicAuth"]],
    "get_lead_status_report": [["oauth2"], ["basicAuth"]],
    "get_opportunity_status_report": [["oauth2"], ["basicAuth"]],
    "generate_custom_report": [["oauth2"], ["basicAuth"]],
    "list_custom_report_fields": [["oauth2"], ["basicAuth"]],
    "get_funnel_opportunity_totals": [["oauth2"], ["basicAuth"]],
    "get_opportunity_funnel_stages_report": [["oauth2"], ["basicAuth"]],
    "list_email_templates": [["oauth2"], ["basicAuth"]],
    "create_email_template": [["oauth2"], ["basicAuth"]],
    "get_email_template": [["oauth2"], ["basicAuth"]],
    "update_email_template": [["oauth2"], ["basicAuth"]],
    "delete_email_template": [["oauth2"], ["basicAuth"]],
    "render_email_template": [["oauth2"], ["basicAuth"]],
    "list_sms_templates": [["oauth2"], ["basicAuth"]],
    "create_sms_template": [["oauth2"], ["basicAuth"]],
    "get_sms_template": [["oauth2"], ["basicAuth"]],
    "update_sms_template": [["oauth2"], ["basicAuth"]],
    "delete_sms_template": [["oauth2"], ["basicAuth"]],
    "list_connected_accounts": [["oauth2"], ["basicAuth"]],
    "get_connected_account": [["oauth2"], ["basicAuth"]],
    "list_send_as_associations": [["oauth2"], ["basicAuth"]],
    "grant_send_as_permission": [["oauth2"], ["basicAuth"]],
    "revoke_send_as_permission": [["oauth2"], ["basicAuth"]],
    "get_send_as": [["oauth2"], ["basicAuth"]],
    "delete_send_as": [["oauth2"], ["basicAuth"]],
    "update_send_as_permissions": [["oauth2"], ["basicAuth"]],
    "list_sequences": [["oauth2"], ["basicAuth"]],
    "create_sequence": [["oauth2"], ["basicAuth"]],
    "get_sequence": [["oauth2"], ["basicAuth"]],
    "update_sequence": [["oauth2"], ["basicAuth"]],
    "delete_sequence": [["oauth2"], ["basicAuth"]],
    "list_sequence_subscriptions": [["oauth2"], ["basicAuth"]],
    "subscribe_contact_to_sequence": [["oauth2"], ["basicAuth"]],
    "get_sequence_subscription": [["oauth2"], ["basicAuth"]],
    "update_sequence_subscription": [["oauth2"], ["basicAuth"]],
    "list_dialer_sessions": [["oauth2"], ["basicAuth"]],
    "get_dialer": [["oauth2"], ["basicAuth"]],
    "list_smart_views": [["oauth2"], ["basicAuth"]],
    "create_smart_view": [["oauth2"], ["basicAuth"]],
    "get_smart_view": [["oauth2"], ["basicAuth"]],
    "update_smart_view": [["oauth2"], ["basicAuth"]],
    "delete_smart_view": [["oauth2"], ["basicAuth"]],
    "list_bulk_emails": [["oauth2"], ["basicAuth"]],
    "send_bulk_email": [["oauth2"], ["basicAuth"]],
    "get_bulk_email": [["oauth2"], ["basicAuth"]],
    "list_sequence_subscriptions_bulk_action": [["oauth2"], ["basicAuth"]],
    "apply_sequence_subscription_bulk_action": [["oauth2"], ["basicAuth"]],
    "get_sequence_subscription_bulk_action": [["oauth2"], ["basicAuth"]],
    "list_bulk_deletes": [["oauth2"], ["basicAuth"]],
    "delete_leads_bulk": [["oauth2"], ["basicAuth"]],
    "get_bulk_delete": [["oauth2"], ["basicAuth"]],
    "list_bulk_edits": [["oauth2"], ["basicAuth"]],
    "bulk_edit_leads": [["oauth2"], ["basicAuth"]],
    "get_bulk_edit": [["oauth2"], ["basicAuth"]],
    "list_integration_links": [["oauth2"], ["basicAuth"]],
    "create_integration_link": [["oauth2"], ["basicAuth"]],
    "get_integration_link": [["oauth2"], ["basicAuth"]],
    "update_integration_link": [["oauth2"], ["basicAuth"]],
    "delete_integration_link": [["oauth2"], ["basicAuth"]],
    "export_leads": [["oauth2"], ["basicAuth"]],
    "export_opportunities": [["oauth2"], ["basicAuth"]],
    "get_export": [["oauth2"], ["basicAuth"]],
    "list_exports": [["oauth2"], ["basicAuth"]],
    "list_phone_numbers": [["oauth2"], ["basicAuth"]],
    "get_phone_number": [["oauth2"], ["basicAuth"]],
    "update_phone_number": [["oauth2"], ["basicAuth"]],
    "delete_phone_number": [["oauth2"], ["basicAuth"]],
    "rent_phone_number": [["oauth2"], ["basicAuth"]],
    "generate_file_upload_credentials": [["oauth2"], ["basicAuth"]],
    "list_comment_threads": [["oauth2"], ["basicAuth"]],
    "get_comment_thread": [["oauth2"], ["basicAuth"]],
    "list_comments": [["oauth2"], ["basicAuth"]],
    "create_comment": [["oauth2"], ["basicAuth"]],
    "get_comment": [["oauth2"], ["basicAuth"]],
    "update_comment": [["oauth2"], ["basicAuth"]],
    "delete_comment": [["oauth2"], ["basicAuth"]],
    "get_event": [["oauth2"], ["basicAuth"]],
    "list_events": [["oauth2"], ["basicAuth"]],
    "list_webhooks": [["oauth2"], ["basicAuth"]],
    "create_webhook": [["oauth2"], ["basicAuth"]],
    "get_webhook": [["oauth2"], ["basicAuth"]],
    "update_webhook": [["oauth2"], ["basicAuth"]],
    "delete_webhook": [["oauth2"], ["basicAuth"]],
    "list_scheduling_links": [["oauth2"], ["basicAuth"]],
    "create_scheduling_link": [["oauth2"], ["basicAuth"]],
    "get_scheduling_link": [["oauth2"], ["basicAuth"]],
    "update_scheduling_link": [["oauth2"], ["basicAuth"]],
    "delete_scheduling_link": [["oauth2"], ["basicAuth"]],
    "upsert_scheduling_link": [["oauth2"], ["basicAuth"]],
    "delete_scheduling_link_oauth": [["oauth2"], ["basicAuth"]],
    "list_scheduling_links_shared": [["oauth2"], ["basicAuth"]],
    "create_scheduling_link_shared": [["oauth2"], ["basicAuth"]],
    "get_scheduling_link_shared": [["oauth2"], ["basicAuth"]],
    "update_scheduling_link_shared": [["oauth2"], ["basicAuth"]],
    "delete_scheduling_link_shared": [["oauth2"], ["basicAuth"]],
    "associate_shared_scheduling_link": [["oauth2"], ["basicAuth"]],
    "disable_shared_scheduling_link": [["oauth2"], ["basicAuth"]],
    "list_lead_custom_fields": [["oauth2"], ["basicAuth"]],
    "create_lead_custom_field": [["oauth2"], ["basicAuth"]],
    "get_lead_custom_field": [["oauth2"], ["basicAuth"]],
    "update_lead_custom_field": [["oauth2"], ["basicAuth"]],
    "delete_lead_custom_field": [["oauth2"], ["basicAuth"]],
    "list_contact_custom_fields": [["oauth2"], ["basicAuth"]],
    "create_contact_custom_field": [["oauth2"], ["basicAuth"]],
    "get_contact_custom_field": [["oauth2"], ["basicAuth"]],
    "update_contact_custom_field": [["oauth2"], ["basicAuth"]],
    "delete_contact_custom_field": [["oauth2"], ["basicAuth"]],
    "list_opportunity_custom_fields": [["oauth2"], ["basicAuth"]],
    "create_opportunity_custom_field": [["oauth2"], ["basicAuth"]],
    "get_opportunity_custom_field": [["oauth2"], ["basicAuth"]],
    "update_opportunity_custom_field": [["oauth2"], ["basicAuth"]],
    "delete_opportunity_custom_field": [["oauth2"], ["basicAuth"]],
    "list_activity_custom_fields": [["oauth2"], ["basicAuth"]],
    "create_activity_custom_field": [["oauth2"], ["basicAuth"]],
    "get_activity_custom_field": [["oauth2"], ["basicAuth"]],
    "update_activity_custom_field": [["oauth2"], ["basicAuth"]],
    "delete_activity_custom_field": [["oauth2"], ["basicAuth"]],
    "list_custom_object_custom_fields": [["oauth2"], ["basicAuth"]],
    "create_custom_object_field": [["oauth2"], ["basicAuth"]],
    "get_custom_field": [["oauth2"], ["basicAuth"]],
    "update_custom_field": [["oauth2"], ["basicAuth"]],
    "delete_custom_field": [["oauth2"], ["basicAuth"]],
    "list_shared_custom_fields": [["oauth2"], ["basicAuth"]],
    "create_shared_custom_field": [["oauth2"], ["basicAuth"]],
    "update_shared_custom_field": [["oauth2"], ["basicAuth"]],
    "delete_custom_field_shared": [["oauth2"], ["basicAuth"]],
    "associate_shared_custom_field": [["oauth2"], ["basicAuth"]],
    "update_shared_custom_field_association": [["oauth2"], ["basicAuth"]],
    "remove_shared_custom_field_association": [["oauth2"], ["basicAuth"]],
    "get_custom_field_schema": [["oauth2"], ["basicAuth"]],
    "reorder_custom_fields": [["oauth2"], ["basicAuth"]],
    "enrich_field": [["oauth2"], ["basicAuth"]],
    "list_custom_activities": [["oauth2"], ["basicAuth"]],
    "create_custom_activity_type": [["oauth2"], ["basicAuth"]],
    "get_custom_activity": [["oauth2"], ["basicAuth"]],
    "update_custom_activity": [["oauth2"], ["basicAuth"]],
    "delete_custom_activity": [["oauth2"], ["basicAuth"]],
    "list_custom_activities_instances": [["oauth2"], ["basicAuth"]],
    "create_custom_activity": [["oauth2"], ["basicAuth"]],
    "get_custom_activity_instance": [["oauth2"], ["basicAuth"]],
    "update_custom_activity_instance": [["oauth2"], ["basicAuth"]],
    "delete_custom_activity_instance": [["oauth2"], ["basicAuth"]],
    "list_custom_object_types": [["oauth2"], ["basicAuth"]],
    "create_custom_object_type": [["oauth2"], ["basicAuth"]],
    "get_custom_object_type": [["oauth2"], ["basicAuth"]],
    "update_custom_object_type": [["oauth2"], ["basicAuth"]],
    "delete_custom_object_type": [["oauth2"], ["basicAuth"]],
    "list_custom_objects": [["oauth2"], ["basicAuth"]],
    "create_custom_object": [["oauth2"], ["basicAuth"]],
    "get_custom_object": [["oauth2"], ["basicAuth"]],
    "update_custom_object": [["oauth2"], ["basicAuth"]],
    "delete_custom_object": [["oauth2"], ["basicAuth"]],
    "list_unsubscribed_emails": [["oauth2"], ["basicAuth"]],
    "unsubscribe_email": [["oauth2"], ["basicAuth"]],
    "resubscribe_email": [["oauth2"], ["basicAuth"]],
    "search_contacts_and_leads": [["oauth2"], ["basicAuth"]]
}

"""
Authentication module for Miro MCP server.

Generated: 2026-04-23 21:28:15 UTC
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
    OAuth 2.0 authentication for Miro Developer Platform.

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
        Location: ./tokens/oauth2authcode_tokens.json
        Permissions: 0o600 (owner read/write only)
        Format: JSON with access_token, refresh_token, expires_at

    URLs:
        Authorization URL: https://miro.com/oauth/authorize
        Token URL: https://api.miro.com/v1/oauth/token

    Available Scopes (configure via OAUTH2_SCOPES):
        - boards:read
        - boards:write
        - microphone:listen
        - screen:record
        - webcam:record
        - organizations:read
        - organizations:teams:read
        - organizations:teams:write
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
        self.token_url = "https://api.miro.com/v1/oauth/token"
        self.auth_url = "https://miro.com/oauth/authorize"
        self.refresh_url = None

        # Token storage (secure file-based, unique per scheme)
        self.token_dir = Path(__file__).parent / "tokens"
        self.token_file = self.token_dir / "oauth2authcode_tokens.json"
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


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "get_access_token_info": [["oAuth2AuthCode"]],
    "list_audit_logs": [["oAuth2AuthCode"]],
    "update_team_boards_classification_bulk": [["oAuth2AuthCode"]],
    "get_board_data_classification": [["oAuth2AuthCode"]],
    "create_markdown_doc": [["oAuth2AuthCode"]],
    "get_doc_format_item": [["oAuth2AuthCode"]],
    "delete_doc_format_item": [["oAuth2AuthCode"]],
    "list_cases": [["oAuth2AuthCode"]],
    "create_case": [["oAuth2AuthCode"]],
    "get_case": [["oAuth2AuthCode"]],
    "update_case": [["oAuth2AuthCode"]],
    "close_case": [["oAuth2AuthCode"]],
    "list_legal_holds_in_case": [["oAuth2AuthCode"]],
    "create_legal_hold_for_case": [["oAuth2AuthCode"]],
    "list_legal_hold_export_jobs": [["oAuth2AuthCode"]],
    "get_legal_hold": [["oAuth2AuthCode"]],
    "update_legal_hold": [["oAuth2AuthCode"]],
    "close_legal_hold": [["oAuth2AuthCode"]],
    "list_legal_hold_content_items": [["oAuth2AuthCode"]],
    "list_board_export_jobs": [["oAuth2AuthCode"]],
    "create_board_export_job": [["oAuth2AuthCode"]],
    "get_board_export_job_status": [["oAuth2AuthCode"]],
    "get_board_export_job_results": [["oAuth2AuthCode"]],
    "cancel_board_export_job": [["oAuth2AuthCode"]],
    "list_board_export_job_tasks": [["oAuth2AuthCode"]],
    "create_board_export_task_download_link": [["oAuth2AuthCode"]],
    "list_board_item_content_logs": [["oAuth2AuthCode"]],
    "delete_user_all_sessions": [["oAuth2AuthCode"]],
    "list_users": [["oAuth2AuthCode"]],
    "create_user": [["oAuth2AuthCode"]],
    "get_user": [["oAuth2AuthCode"]],
    "update_user": [["oAuth2AuthCode"]],
    "update_user_partial": [["oAuth2AuthCode"]],
    "delete_user": [["oAuth2AuthCode"]],
    "list_groups": [["oAuth2AuthCode"]],
    "get_group": [["oAuth2AuthCode"]],
    "update_group_members_and_details": [["oAuth2AuthCode"]],
    "list_resource_types": [["oAuth2AuthCode"]],
    "get_resource_type": [["oAuth2AuthCode"]],
    "list_schemas": [["oAuth2AuthCode"]],
    "get_schema": [["oAuth2AuthCode"]],
    "get_organization": [["oAuth2AuthCode"]],
    "enterprise_get_organization_members": [["oAuth2AuthCode"]],
    "get_organization_member": [["oAuth2AuthCode"]],
    "list_boards": [["oAuth2AuthCode"]],
    "create_board": [["oAuth2AuthCode"]],
    "create_board_copy": [["oAuth2AuthCode"]],
    "get_board": [["oAuth2AuthCode"]],
    "update_board": [["oAuth2AuthCode"]],
    "delete_board": [["oAuth2AuthCode"]],
    "create_app_card": [["oAuth2AuthCode"]],
    "get_app_card_item": [["oAuth2AuthCode"]],
    "update_app_card_item": [["oAuth2AuthCode"]],
    "delete_app_card_item": [["oAuth2AuthCode"]],
    "create_card_item": [["oAuth2AuthCode"]],
    "get_card_item": [["oAuth2AuthCode"]],
    "update_card_item": [["oAuth2AuthCode"]],
    "delete_card_item": [["oAuth2AuthCode"]],
    "list_connectors_for_board": [["oAuth2AuthCode"]],
    "create_connector": [["oAuth2AuthCode"]],
    "get_connector": [["oAuth2AuthCode"]],
    "update_connector": [["oAuth2AuthCode"]],
    "delete_connector": [["oAuth2AuthCode"]],
    "add_document_to_board": [["oAuth2AuthCode"]],
    "get_document_item": [["oAuth2AuthCode"]],
    "update_document_item": [["oAuth2AuthCode"]],
    "delete_document_item": [["oAuth2AuthCode"]],
    "add_embed_item_to_board": [["oAuth2AuthCode"]],
    "get_embed_item": [["oAuth2AuthCode"]],
    "update_embed_item": [["oAuth2AuthCode"]],
    "delete_embed_item": [["oAuth2AuthCode"]],
    "add_image_to_board": [["oAuth2AuthCode"]],
    "get_image_item": [["oAuth2AuthCode"]],
    "update_image_item": [["oAuth2AuthCode"]],
    "delete_image_item": [["oAuth2AuthCode"]],
    "list_board_items": [["oAuth2AuthCode"]],
    "get_item": [["oAuth2AuthCode"]],
    "update_item_position_or_parent": [["oAuth2AuthCode"]],
    "delete_item": [["oAuth2AuthCode"]],
    "list_board_members": [["oAuth2AuthCode"]],
    "invite_members_to_board": [["oAuth2AuthCode"]],
    "get_board_member": [["oAuth2AuthCode"]],
    "update_board_member_role": [["oAuth2AuthCode"]],
    "remove_board_member": [["oAuth2AuthCode"]],
    "add_shape_to_board": [["oAuth2AuthCode"]],
    "get_shape_item": [["oAuth2AuthCode"]],
    "update_shape_item": [["oAuth2AuthCode"]],
    "delete_shape_item": [["oAuth2AuthCode"]],
    "add_sticky_note": [["oAuth2AuthCode"]],
    "get_sticky_note_item": [["oAuth2AuthCode"]],
    "update_sticky_note": [["oAuth2AuthCode"]],
    "delete_sticky_note_item": [["oAuth2AuthCode"]],
    "add_text_to_board": [["oAuth2AuthCode"]],
    "get_text_item": [["oAuth2AuthCode"]],
    "update_text_item": [["oAuth2AuthCode"]],
    "delete_text_item": [["oAuth2AuthCode"]],
    "create_items_bulk": [["oAuth2AuthCode"]],
    "add_frame_to_board": [["oAuth2AuthCode"]],
    "get_frame": [["oAuth2AuthCode"]],
    "update_frame": [["oAuth2AuthCode"]],
    "delete_frame": [["oAuth2AuthCode"]],
    "list_items_in_frame": [["oAuth2AuthCode"]],
    "get_app_metrics": [["oAuth2AuthCode"]],
    "get_app_metrics_total": [["oAuth2AuthCode"]],
    "get_mindmap_node": [["oAuth2AuthCode"]],
    "delete_mindmap_node": [["oAuth2AuthCode"]],
    "list_mindmap_nodes": [["oAuth2AuthCode"]],
    "create_mindmap_node": [["oAuth2AuthCode"]],
    "list_board_items_experimental": [["oAuth2AuthCode"]],
    "get_board_item": [["oAuth2AuthCode"]],
    "delete_item_beta": [["oAuth2AuthCode"]],
    "add_shape_to_board_flowchart": [["oAuth2AuthCode"]],
    "get_shape_item_experimental": [["oAuth2AuthCode"]],
    "update_shape_item_flowchart": [["oAuth2AuthCode"]],
    "delete_shape_item_experimental": [["oAuth2AuthCode"]],
    "create_document_item_from_file": [["oAuth2AuthCode"]],
    "update_document_item_with_file": [["oAuth2AuthCode"]],
    "create_image_item_from_local_file": [["oAuth2AuthCode"]],
    "update_image_item_from_file": [["oAuth2AuthCode"]],
    "list_groups_on_board": [["oAuth2AuthCode"]],
    "list_items_in_group": [["oAuth2AuthCode"]],
    "get_group_by_id": [["oAuth2AuthCode"]],
    "update_group": [["oAuth2AuthCode"]],
    "remove_items_from_group": [["oAuth2AuthCode"]],
    "delete_group": [["oAuth2AuthCode"]],
    "list_tags_for_item": [["oAuth2AuthCode"]],
    "list_tags_from_board": [["oAuth2AuthCode"]],
    "create_tag": [["oAuth2AuthCode"]],
    "get_tag": [["oAuth2AuthCode"]],
    "update_tag": [["oAuth2AuthCode"]],
    "delete_tag": [["oAuth2AuthCode"]],
    "list_items_by_tag": [["oAuth2AuthCode"]],
    "add_tag_to_item": [["oAuth2AuthCode"]],
    "remove_tag_from_item": [["oAuth2AuthCode"]],
    "list_projects_in_team": [["oAuth2AuthCode"]],
    "create_project_in_team": [["oAuth2AuthCode"]],
    "get_project_in_team": [["oAuth2AuthCode"]],
    "update_project": [["oAuth2AuthCode"]],
    "delete_project_in_team": [["oAuth2AuthCode"]],
    "list_project_members": [["oAuth2AuthCode"]],
    "add_project_member": [["oAuth2AuthCode"]],
    "get_project_member": [["oAuth2AuthCode"]],
    "update_project_member_role": [["oAuth2AuthCode"]],
    "remove_project_member": [["oAuth2AuthCode"]],
    "list_organization_teams": [["oAuth2AuthCode"]],
    "create_team": [["oAuth2AuthCode"]],
    "get_team": [["oAuth2AuthCode"]],
    "update_team": [["oAuth2AuthCode"]],
    "delete_team": [["oAuth2AuthCode"]],
    "list_team_members": [["oAuth2AuthCode"]],
    "add_team_member": [["oAuth2AuthCode"]],
    "get_team_member": [["oAuth2AuthCode"]],
    "update_team_member_role": [["oAuth2AuthCode"]],
    "remove_team_member": [["oAuth2AuthCode"]],
    "list_groups_enterprise": [["oAuth2AuthCode"]],
    "create_group_organization": [["oAuth2AuthCode"]],
    "get_group_enterprise": [["oAuth2AuthCode"]],
    "update_group_org": [["oAuth2AuthCode"]],
    "delete_group_organization": [["oAuth2AuthCode"]],
    "list_group_members": [["oAuth2AuthCode"]],
    "add_member_to_group": [["oAuth2AuthCode"]],
    "update_group_members": [["oAuth2AuthCode"]],
    "get_group_member": [["oAuth2AuthCode"]],
    "remove_group_member": [["oAuth2AuthCode"]],
    "list_teams_for_group": [["oAuth2AuthCode"]],
    "get_group_team": [["oAuth2AuthCode"]],
    "list_groups_for_team": [["oAuth2AuthCode"]],
    "add_user_group_to_team": [["oAuth2AuthCode"]],
    "get_team_group": [["oAuth2AuthCode"]],
    "remove_group_from_team": [["oAuth2AuthCode"]],
    "list_board_groups": [["oAuth2AuthCode"]],
    "share_board_with_groups": [["oAuth2AuthCode"]],
    "remove_group_from_board": [["oAuth2AuthCode"]],
    "list_project_groups": [["oAuth2AuthCode"]],
    "share_project_with_groups": [["oAuth2AuthCode"]],
    "remove_group_from_project": [["oAuth2AuthCode"]]
}

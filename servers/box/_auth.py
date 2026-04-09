"""
Authentication module for Box MCP server.

Generated: 2026-04-09 17:15:54 UTC
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
    OAuth 2.0 authentication for Box Platform API.

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
        Location: ./tokens/oauth2security_tokens.json
        Permissions: 0o600 (owner read/write only)
        Format: JSON with access_token, refresh_token, expires_at

    URLs:
        Authorization URL: https://account.box.com/api/oauth2/authorize
        Token URL: https://api.box.com/oauth2/token

    Available Scopes (configure via OAUTH2_SCOPES):
        - root_readonly
        - root_readwrite
        - manage_app_users
        - manage_managed_users
        - manage_groups
        - manage_webhook
        - manage_enterprise_properties
        - manage_data_retention
        - manage_legal_hold
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
        self.token_url = "https://api.box.com/oauth2/token"
        self.auth_url = "https://account.box.com/api/oauth2/authorize"
        self.refresh_url = None

        # Token storage (secure file-based, unique per scheme)
        self.token_dir = Path(__file__).parent / "tokens"
        self.token_file = self.token_dir / "oauth2security_tokens.json"
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


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "get_file": [["OAuth2Security"]],
    "restore_file": [["OAuth2Security"]],
    "update_file": [["OAuth2Security"]],
    "delete_file": [["OAuth2Security"]],
    "list_file_app_item_associations": [["OAuth2Security"]],
    "download_file": [["OAuth2Security"]],
    "upload_file_version": [["OAuth2Security"]],
    "upload_file": [["OAuth2Security"]],
    "create_upload_session": [["OAuth2Security"]],
    "create_file_upload_session": [["OAuth2Security"]],
    "get_upload_session": [["OAuth2Security"]],
    "upload_file_part": [["OAuth2Security"]],
    "abort_upload_session": [["OAuth2Security"]],
    "list_upload_session_parts": [["OAuth2Security"]],
    "commit_upload_session": [["OAuth2Security"]],
    "copy_file": [["OAuth2Security"]],
    "get_file_thumbnail": [["OAuth2Security"]],
    "list_file_collaborations": [["OAuth2Security"]],
    "list_file_comments": [["OAuth2Security"]],
    "list_file_tasks": [["OAuth2Security"]],
    "get_trashed_file": [["OAuth2Security"]],
    "permanently_delete_trashed_file": [["OAuth2Security"]],
    "list_file_versions": [["OAuth2Security"]],
    "get_file_version": [["OAuth2Security"]],
    "restore_file_version": [["OAuth2Security"]],
    "delete_file_version": [["OAuth2Security"]],
    "promote_file_version": [["OAuth2Security"]],
    "list_file_metadata": [["OAuth2Security"]],
    "get_file_classification": [["OAuth2Security"]],
    "add_file_classification": [["OAuth2Security"]],
    "update_file_classification": [["OAuth2Security"]],
    "remove_file_classification": [["OAuth2Security"]],
    "get_file_metadata_instance": [["OAuth2Security"]],
    "create_file_metadata": [["OAuth2Security"]],
    "update_file_metadata": [["OAuth2Security"]],
    "delete_file_metadata": [["OAuth2Security"]],
    "list_file_skills_cards": [["OAuth2Security"]],
    "create_skill_cards": [["OAuth2Security"]],
    "update_skill_cards": [["OAuth2Security"]],
    "remove_file_skills_cards": [["OAuth2Security"]],
    "get_file_watermark": [["OAuth2Security"]],
    "apply_file_watermark": [["OAuth2Security"]],
    "remove_file_watermark": [["OAuth2Security"]],
    "get_file_request": [["OAuth2Security"]],
    "update_file_request": [["OAuth2Security"]],
    "delete_file_request": [["OAuth2Security"]],
    "copy_file_request": [["OAuth2Security"]],
    "get_folder": [["OAuth2Security"]],
    "restore_folder": [["OAuth2Security"]],
    "update_folder": [["OAuth2Security"]],
    "delete_folder": [["OAuth2Security"]],
    "list_folder_app_item_associations": [["OAuth2Security"]],
    "list_folder_items": [["OAuth2Security"]],
    "create_folder": [["OAuth2Security"]],
    "copy_folder": [["OAuth2Security"]],
    "list_folder_collaborations": [["OAuth2Security"]],
    "get_trashed_folder": [["OAuth2Security"]],
    "permanently_delete_trashed_folder": [["OAuth2Security"]],
    "list_folder_metadata": [["OAuth2Security"]],
    "get_folder_classification": [["OAuth2Security"]],
    "add_folder_classification": [["OAuth2Security"]],
    "update_folder_classification": [["OAuth2Security"]],
    "remove_folder_classification": [["OAuth2Security"]],
    "get_folder_metadata_instance": [["OAuth2Security"]],
    "create_folder_metadata": [["OAuth2Security"]],
    "update_folder_metadata": [["OAuth2Security"]],
    "delete_folder_metadata": [["OAuth2Security"]],
    "list_trash_items": [["OAuth2Security"]],
    "get_folder_watermark": [["OAuth2Security"]],
    "apply_folder_watermark": [["OAuth2Security"]],
    "remove_folder_watermark": [["OAuth2Security"]],
    "list_folder_locks": [["OAuth2Security"]],
    "lock_folder": [["OAuth2Security"]],
    "delete_folder_lock": [["OAuth2Security"]],
    "find_metadata_template_by_instance": [["OAuth2Security"]],
    "list_classifications": [["OAuth2Security"]],
    "get_metadata_template": [["OAuth2Security"]],
    "update_metadata_template": [["OAuth2Security"]],
    "delete_metadata_template": [["OAuth2Security"]],
    "get_metadata_template_by_id": [["OAuth2Security"]],
    "list_global_metadata_templates": [["OAuth2Security"]],
    "list_enterprise_metadata_templates": [["OAuth2Security"]],
    "create_metadata_template": [["OAuth2Security"]],
    "initialize_classifications": [["OAuth2Security"]],
    "list_metadata_cascade_policies": [["OAuth2Security"]],
    "create_metadata_cascade_policy": [["OAuth2Security"]],
    "get_metadata_cascade_policy": [["OAuth2Security"]],
    "apply_metadata_cascade_policy": [["OAuth2Security"]],
    "query_items_by_metadata": [["OAuth2Security"]],
    "get_comment": [["OAuth2Security"]],
    "update_comment": [["OAuth2Security"]],
    "delete_comment": [["OAuth2Security"]],
    "create_comment": [["OAuth2Security"]],
    "get_collaboration": [["OAuth2Security"]],
    "update_collaboration": [["OAuth2Security"]],
    "delete_collaboration": [["OAuth2Security"]],
    "list_pending_collaborations": [["OAuth2Security"]],
    "create_collaboration": [["OAuth2Security"]],
    "search_content": [["OAuth2Security"]],
    "create_task": [["OAuth2Security"]],
    "get_task": [["OAuth2Security"]],
    "update_task": [["OAuth2Security"]],
    "delete_task": [["OAuth2Security"]],
    "list_task_assignments": [["OAuth2Security"]],
    "assign_task": [["OAuth2Security"]],
    "get_task_assignment": [["OAuth2Security"]],
    "update_task_assignment": [["OAuth2Security"]],
    "delete_task_assignment": [["OAuth2Security"]],
    "get_shared_link_file": [["OAuth2Security"]],
    "get_file_shared_link": [["OAuth2Security"]],
    "add_file_shared_link": [["OAuth2Security"]],
    "update_file_shared_link": [["OAuth2Security"]],
    "remove_file_shared_link": [["OAuth2Security"]],
    "get_folder_from_shared_link": [["OAuth2Security"]],
    "get_folder_shared_link": [["OAuth2Security"]],
    "add_folder_shared_link": [["OAuth2Security"]],
    "update_folder_shared_link": [["OAuth2Security"]],
    "remove_folder_shared_link": [["OAuth2Security"]],
    "create_web_link": [["OAuth2Security"]],
    "get_web_link": [["OAuth2Security"]],
    "restore_web_link": [["OAuth2Security"]],
    "update_web_link": [["OAuth2Security"]],
    "delete_web_link": [["OAuth2Security"]],
    "get_trashed_web_link": [["OAuth2Security"]],
    "permanently_delete_web_link": [["OAuth2Security"]],
    "get_web_link_from_shared_link": [["OAuth2Security"]],
    "get_web_link_shared_link": [["OAuth2Security"]],
    "add_web_link_shared_link": [["OAuth2Security"]],
    "update_web_link_shared_link": [["OAuth2Security"]],
    "remove_web_link_shared_link": [["OAuth2Security"]],
    "get_app_item_from_shared_link": [["OAuth2Security"]],
    "list_users": [["OAuth2Security"]],
    "create_user": [["OAuth2Security"]],
    "get_current_user": [["OAuth2Security"]],
    "terminate_user_sessions": [["OAuth2Security"]],
    "get_user": [["OAuth2Security"]],
    "update_user": [["OAuth2Security"]],
    "delete_user": [["OAuth2Security"]],
    "get_user_avatar": [["OAuth2Security"]],
    "upload_user_avatar": [["OAuth2Security"]],
    "delete_user_avatar": [["OAuth2Security"]],
    "transfer_user_folders": [["OAuth2Security"]],
    "list_user_email_aliases": [["OAuth2Security"]],
    "create_email_alias": [["OAuth2Security"]],
    "remove_user_email_alias": [["OAuth2Security"]],
    "list_user_memberships": [["OAuth2Security"]],
    "invite_enterprise_user": [["OAuth2Security"]],
    "get_invite": [["OAuth2Security"]],
    "list_groups": [["OAuth2Security"]],
    "create_group": [["OAuth2Security"]],
    "terminate_group_sessions": [["OAuth2Security"]],
    "get_group": [["OAuth2Security"]],
    "update_group": [["OAuth2Security"]],
    "delete_group": [["OAuth2Security"]],
    "list_group_members": [["OAuth2Security"]],
    "list_group_collaborations": [["OAuth2Security"]],
    "add_user_to_group": [["OAuth2Security"]],
    "get_group_membership": [["OAuth2Security"]],
    "update_group_membership": [["OAuth2Security"]],
    "remove_group_member": [["OAuth2Security"]],
    "list_webhooks": [["OAuth2Security"]],
    "get_webhook": [["OAuth2Security"]],
    "delete_webhook": [["OAuth2Security"]],
    "update_skill_cards_on_file": [["OAuth2Security"]],
    "list_events": [["OAuth2Security"]],
    "list_collections": [["OAuth2Security"]],
    "list_collection_items": [["OAuth2Security"]],
    "get_collection": [["OAuth2Security"]],
    "list_recent_items": [["OAuth2Security"]],
    "list_retention_policies": [["OAuth2Security"]],
    "get_retention_policy": [["OAuth2Security"]],
    "update_retention_policy": [["OAuth2Security"]],
    "delete_retention_policy": [["OAuth2Security"]],
    "list_retention_policy_assignments": [["OAuth2Security"]],
    "assign_retention_policy": [["OAuth2Security"]],
    "get_retention_policy_assignment": [["OAuth2Security"]],
    "delete_retention_policy_assignment": [["OAuth2Security"]],
    "list_files_under_retention": [["OAuth2Security"]],
    "list_file_versions_under_retention": [["OAuth2Security"]],
    "list_legal_hold_policies": [["OAuth2Security"]],
    "get_legal_hold_policy": [["OAuth2Security"]],
    "update_legal_hold_policy": [["OAuth2Security"]],
    "delete_legal_hold_policy": [["OAuth2Security"]],
    "list_legal_hold_policy_assignments": [["OAuth2Security"]],
    "assign_legal_hold_policy": [["OAuth2Security"]],
    "get_legal_hold_policy_assignment": [["OAuth2Security"]],
    "remove_legal_hold_policy_assignment": [["OAuth2Security"]],
    "list_legal_hold_assignment_files": [["OAuth2Security"]],
    "list_legal_hold_assignment_file_versions": [["OAuth2Security"]],
    "get_file_version_legal_hold": [["OAuth2Security"]],
    "list_file_version_legal_holds": [["OAuth2Security"]],
    "get_information_barrier": [["OAuth2Security"]],
    "update_shield_barrier_status": [["OAuth2Security"]],
    "list_shield_information_barriers": [["OAuth2Security"]],
    "create_shield_information_barrier": [["OAuth2Security"]],
    "list_barrier_reports": [["OAuth2Security"]],
    "create_barrier_report": [["OAuth2Security"]],
    "get_barrier_report": [["OAuth2Security"]],
    "get_barrier_segment": [["OAuth2Security"]],
    "update_barrier_segment": [["OAuth2Security"]],
    "delete_barrier_segment": [["OAuth2Security"]],
    "list_barrier_segments": [["OAuth2Security"]],
    "create_barrier_segment": [["OAuth2Security"]],
    "get_barrier_segment_member": [["OAuth2Security"]],
    "delete_barrier_segment_member": [["OAuth2Security"]],
    "list_barrier_segment_members": [["OAuth2Security"]],
    "add_barrier_segment_member": [["OAuth2Security"]],
    "get_barrier_segment_restriction": [["OAuth2Security"]],
    "list_barrier_segment_restrictions": [["OAuth2Security"]],
    "get_device_pin": [["OAuth2Security"]],
    "delete_device_pin": [["OAuth2Security"]],
    "list_enterprise_device_pins": [["OAuth2Security"]],
    "list_terms_of_service_user_statuses": [["OAuth2Security"]],
    "create_terms_of_service_user_status": [["OAuth2Security"]],
    "update_terms_of_service_user_status": [["OAuth2Security"]],
    "get_collaboration_whitelist_entry": [["OAuth2Security"]],
    "list_storage_policy_assignments": [["OAuth2Security"]],
    "assign_storage_policy": [["OAuth2Security"]],
    "get_storage_policy_assignment": [["OAuth2Security"]],
    "delete_storage_policy_assignment": [["OAuth2Security"]],
    "create_zip_download": [["OAuth2Security"]],
    "download_zip_archive": [],
    "get_zip_download_status": [["OAuth2Security"]],
    "cancel_sign_request": [["OAuth2Security"]],
    "resend_sign_request": [["OAuth2Security"]],
    "get_sign_request": [["OAuth2Security"]],
    "list_sign_requests": [["OAuth2Security"]],
    "create_sign_request": [["OAuth2Security"]],
    "list_workflows": [["OAuth2Security"]],
    "start_workflow": [["OAuth2Security"]],
    "list_sign_templates": [["OAuth2Security"]],
    "get_sign_template": [["OAuth2Security"]],
    "list_slack_integration_mappings": [["OAuth2Security"]],
    "list_teams_integration_mappings": [["OAuth2Security"]],
    "create_teams_integration_mapping": [["OAuth2Security"]],
    "extract_metadata_freeform": [["OAuth2Security"]],
    "extract_structured_metadata": [["OAuth2Security"]],
    "list_ai_agents": [["OAuth2Security"]],
    "create_ai_agent": [["OAuth2Security"]],
    "get_ai_agent": [["OAuth2Security"]],
    "list_metadata_taxonomies": [["OAuth2Security"]],
    "get_metadata_taxonomy": [["OAuth2Security"]],
    "list_taxonomy_nodes": [["OAuth2Security"]],
    "get_taxonomy_node": [["OAuth2Security"]],
    "delete_taxonomy_node": [["OAuth2Security"]],
    "list_taxonomy_field_options": [["OAuth2Security"]]
}

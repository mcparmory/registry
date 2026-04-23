"""
Authentication module for BambooHR MCP server.

Generated: 2026-04-23 21:01:58 UTC
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
    OAuth 2.0 authentication for BambooHR API.

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
        Location: ./tokens/oauth_tokens.json
        Permissions: 0o600 (owner read/write only)
        Format: JSON with access_token, refresh_token, expires_at

    URLs:
        Authorization URL: https://{companyDomain}.bamboohr.com/authorize.php
        Token URL: https://{companyDomain}.bamboohr.com/token.php

    Available Scopes (configure via OAUTH2_SCOPES):
        - openid
        - offline_access
        - employee
        - employee.write
        - employee:job
        - employee:compensation
        - employee:contact
        - time_off
        - time_tracking
        - report
        - user
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
        self.token_url = "https://{companyDomain}.bamboohr.com/token.php"
        self.auth_url = "https://{companyDomain}.bamboohr.com/authorize.php"
        self.refresh_url = None

        # Token storage (secure file-based, unique per scheme)
        self.token_dir = Path(__file__).parent / "tokens"
        self.token_file = self.token_dir / "oauth_tokens.json"
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
    HTTP Basic Authentication for BambooHR API.

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
    "create_project": [["oauth"], ["basic"]],
    "list_break_assessments": [["oauth"], ["basic"]],
    "get_break": [["oauth"], ["basic"]],
    "update_break": [["oauth"], ["basic"]],
    "delete_break": [["oauth"], ["basic"]],
    "list_break_policy_breaks": [["oauth"], ["basic"]],
    "create_break": [["oauth"], ["basic"]],
    "replace_break_policy_breaks": [["oauth"], ["basic"]],
    "assign_employees_to_break_policy": [["oauth"], ["basic"]],
    "assign_break_policy_employees": [["oauth"], ["basic"]],
    "unassign_employees_from_break_policy": [["oauth"], ["basic"]],
    "get_break_policy": [["oauth"], ["basic"]],
    "update_break_policy": [["oauth"], ["basic"]],
    "delete_break_policy": [["oauth"], ["basic"]],
    "list_break_policies": [["oauth"], ["basic"]],
    "create_break_policy": [["oauth"], ["basic"]],
    "list_employee_break_availabilities": [["oauth"], ["basic"]],
    "list_employee_break_policies": [["oauth"], ["basic"]],
    "list_break_policy_employees": [["oauth"], ["basic"]],
    "replace_break_policy": [["oauth"], ["basic"]],
    "delete_clock_entries": [["oauth"], ["basic"]],
    "delete_hour_entries": [["oauth"], ["basic"]],
    "list_timesheet_entries": [["oauth"], ["basic"]],
    "clock_in_employee": [["oauth"], ["basic"]],
    "clock_out_employee": [["oauth"], ["basic"]],
    "bulk_upsert_clock_entries": [["oauth"], ["basic"]],
    "bulk_upsert_timesheet_entries": [["oauth"], ["basic"]],
    "list_webhooks": [["oauth"], ["basic"]],
    "get_webhook": [["oauth"], ["basic"]],
    "delete_webhook": [["oauth"], ["basic"]],
    "list_webhook_logs": [["oauth"], ["basic"]],
    "list_webhook_monitor_fields": [["oauth"], ["basic"]],
    "list_webhook_post_fields": [["oauth"], ["basic"]],
    "query_dataset": [["oauth"], ["basic"]],
    "get_custom_report": [["oauth"], ["basic"]],
    "list_datasets": [["oauth"], ["basic"]],
    "list_dataset_fields": [["oauth"], ["basic"]],
    "list_custom_reports": [["oauth"], ["basic"]],
    "get_field_options": [["oauth"], ["basic"]],
    "list_datasets_v1_2": [["oauth"], ["basic"]],
    "list_dataset_fields_v1_2": [["oauth"], ["basic"]],
    "get_field_options_rfc7807": [["oauth"], ["basic"]],
    "list_applications": [["oauth"], ["basic"]],
    "list_applicant_statuses": [["oauth"], ["basic"]],
    "list_job_locations": [["oauth"], ["basic"]],
    "list_hiring_leads": [["oauth"], ["basic"]],
    "create_candidate": [["oauth"], ["basic"]],
    "create_job_opening": [["oauth"], ["basic"]],
    "list_company_benefits": [["oauth"], ["basic"]],
    "list_employee_benefits": [["oauth"], ["basic"]],
    "list_member_benefit_events": [["oauth"], ["basic"]],
    "list_member_benefits": [["oauth"], ["basic"]],
    "list_benefit_deduction_types": [["oauth"], ["basic"]],
    "get_company_profile": [["oauth"], ["basic"]],
    "list_enabled_integrations": [["oauth"], ["basic"]],
    "list_employees": [["oauth"], ["basic"]],
    "create_employee": [["oauth"], ["basic"]],
    "update_employee_table_row": [["oauth"], ["basic"]],
    "delete_employee_table_row": [["oauth"], ["basic"]],
    "download_company_file": [["oauth"], ["basic"]],
    "update_company_file": [["oauth"], ["basic"]],
    "delete_company_file": [["oauth"], ["basic"]],
    "download_employee_file": [["oauth"], ["basic"]],
    "update_employee_file": [["oauth"], ["basic"]],
    "delete_employee_file": [["oauth"], ["basic"]],
    "list_employee_goals": [["oauth"], ["basic"]],
    "create_employee_goal": [["oauth"], ["basic"]],
    "delete_employee_goal": [["oauth"], ["basic"]],
    "update_goal_progress": [["oauth"], ["basic"]],
    "update_milestone_progress": [["oauth"], ["basic"]],
    "set_goal_sharing": [["oauth"], ["basic"]],
    "list_goal_share_options": [["oauth"], ["basic"]],
    "list_goal_comments": [["oauth"], ["basic"]],
    "add_goal_comment": [["oauth"], ["basic"]],
    "update_goal_comment": [["oauth"], ["basic"]],
    "delete_goal_comment": [["oauth"], ["basic"]],
    "get_goal_aggregate": [["oauth"], ["basic"]],
    "list_goal_alignment_options": [["oauth"], ["basic"]],
    "close_goal": [["oauth"], ["basic"]],
    "reopen_goal": [["oauth"], ["basic"]],
    "update_goal_with_milestones": [["oauth"], ["basic"]],
    "get_goal_filters": [["oauth"], ["basic"]],
    "get_employee_goals_aggregate": [["oauth"], ["basic"]],
    "get_time_tracking_record": [["oauth"], ["basic"]],
    "create_time_entry": [["oauth"], ["basic"]],
    "upsert_hour_records": [["oauth"], ["basic"]],
    "update_time_entry": [["oauth"], ["basic"]],
    "delete_time_tracking_record": [["oauth"], ["basic"]],
    "list_country_states": [["oauth"], ["basic"]],
    "list_countries": [["oauth"], ["basic"]],
    "list_timezones": [["basic"], ["oauth"]],
    "list_employee_fields": [["oauth"], ["basic"]],
    "list_users": [["oauth"], ["basic"]],
    "get_employee": [["oauth"], ["basic"]],
    "update_employee": [["oauth"], ["basic"]],
    "list_changed_employee_table_rows": [["oauth"], ["basic"]],
    "list_employee_table_rows": [["oauth"], ["basic"]],
    "create_employee_table_row": [["oauth"], ["basic"]],
    "update_employee_table_row_v1_1": [["oauth"], ["basic"]],
    "create_employee_table_row_v1_1": [["oauth"], ["basic"]],
    "list_changed_employees": [["oauth"], ["basic"]],
    "get_employee_photo": [["oauth"], ["basic"]],
    "create_employee_file_categories": [["oauth"], ["basic"]],
    "create_file_categories": [["oauth"], ["basic"]],
    "upload_employee_file": [["oauth"], ["basic"]],
    "upload_file": [["oauth"], ["basic"]],
    "list_employee_time_off_policies": [["oauth"], ["basic"]],
    "assign_employee_time_off_policies": [["oauth"], ["basic"]],
    "list_employee_time_off_policies_extended": [["oauth"], ["basic"]],
    "assign_time_off_policies": [["oauth"], ["basic"]],
    "get_application": [["oauth"], ["basic"]],
    "add_application_comment": [["oauth"], ["basic"]],
    "list_jobs": [["oauth"], ["basic"]],
    "update_application_status": [["oauth"], ["basic"]],
    "list_benefit_coverages": [["oauth"], ["basic"]],
    "get_employee_dependent": [["oauth"], ["basic"]],
    "update_dependent": [["oauth"], ["basic"]],
    "list_employee_dependents": [["oauth"], ["basic"]],
    "create_employee_dependent": [["oauth"], ["basic"]],
    "get_employee_directory": [["oauth"], ["basic"]],
    "list_company_files": [["oauth"], ["basic"]],
    "list_employee_files": [["oauth"], ["basic"]],
    "list_list_fields": [["oauth"], ["basic"]],
    "update_list_field_options": [["oauth"], ["basic"]],
    "list_tabular_fields": [["oauth"], ["basic"]],
    "get_employee_time_off_balance": [["oauth"], ["basic"]],
    "create_time_off_history_entry": [["oauth"], ["basic"]],
    "adjust_time_off_balance": [["oauth"], ["basic"]],
    "list_time_off_policies": [["oauth"], ["basic"]],
    "create_time_off_request": [["oauth"], ["basic"]],
    "update_time_off_request_status": [["oauth"], ["basic"]],
    "list_time_off_requests": [["oauth"], ["basic"]],
    "list_time_off_types": [["oauth"], ["basic"]],
    "list_training_types": [["oauth"], ["basic"]],
    "create_training_type": [["oauth"], ["basic"]],
    "update_training_type": [["oauth"], ["basic"]],
    "delete_training_type": [["oauth"], ["basic"]],
    "list_training_categories": [["oauth"], ["basic"]],
    "create_training_category": [["oauth"], ["basic"]],
    "update_training_category": [["oauth"], ["basic"]],
    "delete_training_category": [["oauth"], ["basic"]],
    "list_employee_training_records": [["oauth"], ["basic"]],
    "create_employee_training_record": [["oauth"], ["basic"]],
    "update_training_record": [["oauth"], ["basic"]],
    "delete_training_record": [["oauth"], ["basic"]],
    "upload_employee_photo": [["oauth"], ["basic"]],
    "list_whos_out": [["oauth"], ["basic"]]
}

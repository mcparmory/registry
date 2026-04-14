"""
Authentication module for Bitbucket MCP server.

Generated: 2026-04-14 18:16:06 UTC
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

# ============================================================================
# Authentication Classes
# ============================================================================

class OAuth2Auth:
    """
    OAuth 2.0 authentication for Bitbucket API.

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
        Authorization URL: https://bitbucket.org/site/oauth2/authorize
        Token URL: https://bitbucket.org/site/oauth2/access_token

    Available Scopes (configure via OAUTH2_SCOPES):
        - repository
        - repository:write
        - repository:admin
        - repository:delete
        - project
        - project:admin
        - email
        - account
        - account:write
        - team
        - team:write
        - pipeline
        - pipeline:write
        - pipeline:variable
        - runner
        - runner:write
        - test
        - test:write
        - pullrequest
        - pullrequest:write
        - webhook
        - issue
        - issue:write
        - snippet
        - snippet:write
        - wiki
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
        self.token_url = "https://bitbucket.org/site/oauth2/access_token"
        self.auth_url = "https://bitbucket.org/site/oauth2/authorize"
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
    HTTP Basic Authentication for Bitbucket API.

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

class APIKeyAuth:
    """
    API Key authentication for Bitbucket API.

    Supports header, query parameter, cookie, and path-based API key injection.
    Configure location and parameter name via constructor arguments.
    """

    def __init__(self, env_var: str = "API_KEY", location: str = "header",
                 param_name: str = "Authorization", prefix: str = ""):
        """Initialize API key authentication from environment variable.

        Args:
            env_var: Environment variable name containing the API key.
            location: Where to inject the key - 'header', 'query', 'cookie', or 'path'.
            param_name: Name of the header, query parameter, cookie, or path placeholder.
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

    def get_auth_path_params(self) -> dict[str, str]:
        """Get authentication path parameters for URL template substitution."""
        if self.location != "path":
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
    "list_webhook_event_types": [["oauth2"], ["basic"], ["api_key"]],
    "list_webhook_event_types_by_subject": [["oauth2"], ["basic"], ["api_key"]],
    "list_workspace_repositories": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository": [["oauth2"], ["basic"], ["api_key"]],
    "create_repository": [["oauth2"], ["basic"], ["api_key"]],
    "update_repository": [["oauth2"], ["basic"], ["api_key"]],
    "delete_repository": [["oauth2"], ["basic"], ["api_key"]],
    "list_branch_restrictions": [["oauth2"], ["basic"], ["api_key"]],
    "create_branch_restriction": [["oauth2"], ["basic"], ["api_key"]],
    "get_branch_restriction": [["oauth2"], ["basic"], ["api_key"]],
    "update_branch_restriction": [["oauth2"], ["basic"], ["api_key"]],
    "delete_branch_restriction": [["oauth2"], ["basic"], ["api_key"]],
    "get_branching_model": [["oauth2"], ["basic"], ["api_key"]],
    "get_branching_model_settings": [["oauth2"], ["basic"], ["api_key"]],
    "update_branching_model_settings": [["oauth2"], ["basic"], ["api_key"]],
    "get_commit": [["oauth2"], ["basic"], ["api_key"]],
    "approve_commit": [["oauth2"], ["basic"], ["api_key"]],
    "unapprove_commit": [["oauth2"], ["basic"], ["api_key"]],
    "list_commit_comments": [["oauth2"], ["basic"], ["api_key"]],
    "create_commit_comment": [["oauth2"], ["basic"], ["api_key"]],
    "get_commit_comment": [["oauth2"], ["basic"], ["api_key"]],
    "update_commit_comment": [["oauth2"], ["basic"], ["api_key"]],
    "delete_commit_comment": [["oauth2"], ["basic"], ["api_key"]],
    "get_commit_property": [["oauth2"], ["basic"], ["api_key"]],
    "update_commit_property": [["oauth2"], ["basic"], ["api_key"]],
    "delete_commit_property": [["oauth2"], ["basic"], ["api_key"]],
    "list_commit_pull_requests": [["oauth2"], ["basic"], ["api_key"]],
    "list_commit_reports": [["oauth2"], ["basic"], ["api_key"]],
    "get_commit_report": [["oauth2"], ["basic"], ["api_key"]],
    "create_or_update_commit_report": [["oauth2"], ["basic"], ["api_key"]],
    "delete_commit_report": [["oauth2"], ["basic"], ["api_key"]],
    "list_commit_report_annotations": [["oauth2"], ["basic"], ["api_key"]],
    "bulk_create_annotations": [["oauth2"], ["basic"], ["api_key"]],
    "get_commit_report_annotation": [["oauth2"], ["basic"], ["api_key"]],
    "upsert_commit_report_annotation": [["oauth2"], ["basic"], ["api_key"]],
    "delete_commit_annotation": [["oauth2"], ["basic"], ["api_key"]],
    "list_commit_statuses": [["oauth2"], ["basic"], ["api_key"]],
    "create_commit_build_status": [["oauth2"], ["basic"], ["api_key"]],
    "get_commit_build_status": [["oauth2"], ["basic"], ["api_key"]],
    "update_commit_build_status": [["oauth2"], ["basic"], ["api_key"]],
    "list_commits": [["oauth2"], ["basic"], ["api_key"]],
    "list_commits_with_filters": [["oauth2"], ["basic"], ["api_key"]],
    "list_commits_by_revision": [["oauth2"], ["basic"], ["api_key"]],
    "list_commits_by_revision_post": [["oauth2"], ["basic"], ["api_key"]],
    "list_default_reviewers": [["oauth2"], ["basic"], ["api_key"]],
    "get_default_reviewer": [["oauth2"], ["basic"], ["api_key"]],
    "add_default_reviewer": [["oauth2"], ["basic"], ["api_key"]],
    "remove_default_reviewer": [["oauth2"], ["basic"], ["api_key"]],
    "list_deploy_keys": [["oauth2"], ["basic"], ["api_key"]],
    "add_deploy_key": [["oauth2"], ["basic"], ["api_key"]],
    "get_deploy_key": [["oauth2"], ["basic"], ["api_key"]],
    "update_deploy_key": [["oauth2"], ["basic"], ["api_key"]],
    "delete_deploy_key": [["oauth2"], ["basic"], ["api_key"]],
    "list_deployments": [["oauth2"], ["basic"], ["api_key"]],
    "get_deployment": [["oauth2"], ["basic"], ["api_key"]],
    "list_environment_variables": [["oauth2"], ["basic"], ["api_key"]],
    "create_environment_variable": [["oauth2"], ["basic"], ["api_key"]],
    "update_environment_variable": [["oauth2"], ["basic"], ["api_key"]],
    "delete_environment_variable": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository_diff": [["oauth2"], ["basic"], ["api_key"]],
    "get_diffstat": [["oauth2"], ["basic"], ["api_key"]],
    "list_download_artifacts": [["oauth2"], ["basic"], ["api_key"]],
    "upload_download_artifact": [["oauth2"], ["basic"], ["api_key"]],
    "get_download_artifact": [["oauth2"], ["basic"], ["api_key"]],
    "delete_download_artifact": [["oauth2"], ["basic"], ["api_key"]],
    "get_effective_branching_model": [["oauth2"], ["basic"], ["api_key"]],
    "list_effective_default_reviewers": [["oauth2"], ["basic"], ["api_key"]],
    "list_environments": [["oauth2"], ["basic"], ["api_key"]],
    "create_environment": [["oauth2"], ["basic"], ["api_key"]],
    "get_environment": [["oauth2"], ["basic"], ["api_key"]],
    "delete_environment": [["oauth2"], ["basic"], ["api_key"]],
    "update_environment": [["oauth2"], ["basic"], ["api_key"]],
    "list_file_history": [["oauth2"], ["basic"], ["api_key"]],
    "list_repository_forks": [["oauth2"], ["basic"], ["api_key"]],
    "fork_repository": [["oauth2"], ["basic"], ["api_key"]],
    "list_repository_webhooks": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository_webhook": [["oauth2"], ["basic"], ["api_key"]],
    "update_repository_webhook": [["oauth2"], ["basic"], ["api_key"]],
    "delete_repository_webhook": [["oauth2"], ["basic"], ["api_key"]],
    "get_merge_base": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository_override_settings": [["oauth2"], ["basic"], ["api_key"]],
    "set_repository_override_settings": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository_patch": [["oauth2"], ["basic"], ["api_key"]],
    "list_repository_group_permissions": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository_group_permission": [["oauth2"], ["basic"], ["api_key"]],
    "list_repository_user_permissions": [["oauth2"], ["basic"], ["api_key"]],
    "get_user_repository_permission": [["oauth2"], ["basic"], ["api_key"]],
    "delete_user_repository_permission": [["oauth2"], ["basic"], ["api_key"]],
    "list_pipelines": [["oauth2"], ["basic"], ["api_key"]],
    "trigger_pipeline": [["oauth2"], ["basic"], ["api_key"]],
    "list_pipeline_caches": [["oauth2"], ["basic"], ["api_key"]],
    "delete_pipeline_caches": [["oauth2"], ["basic"], ["api_key"]],
    "delete_pipeline_cache": [["oauth2"], ["basic"], ["api_key"]],
    "get_pipeline_cache_content_uri": [["oauth2"], ["basic"], ["api_key"]],
    "list_repository_runners": [["oauth2"], ["basic"], ["api_key"]],
    "create_repository_runner": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository_runner": [["oauth2"], ["basic"], ["api_key"]],
    "update_repository_runner": [["oauth2"], ["basic"], ["api_key"]],
    "delete_repository_runner": [["oauth2"], ["basic"], ["api_key"]],
    "get_pipeline": [["oauth2"], ["basic"], ["api_key"]],
    "list_pipeline_steps": [["oauth2"], ["basic"], ["api_key"]],
    "get_pipeline_step": [["oauth2"], ["basic"], ["api_key"]],
    "get_pipeline_step_log": [["oauth2"], ["basic"], ["api_key"]],
    "get_pipeline_step_log_container": [["oauth2"], ["basic"], ["api_key"]],
    "get_pipeline_step_test_report": [["oauth2"], ["basic"], ["api_key"]],
    "list_pipeline_step_test_cases": [["oauth2"], ["basic"], ["api_key"]],
    "list_test_case_reasons": [["oauth2"], ["basic"], ["api_key"]],
    "stop_pipeline": [["oauth2"], ["basic"], ["api_key"]],
    "get_pipelines_config": [["oauth2"], ["basic"], ["api_key"]],
    "set_pipeline_next_build_number": [["oauth2"], ["basic"], ["api_key"]],
    "list_pipeline_schedules": [["oauth2"], ["basic"], ["api_key"]],
    "create_pipeline_schedule": [["oauth2"], ["basic"], ["api_key"]],
    "get_pipeline_schedule": [["oauth2"], ["basic"], ["api_key"]],
    "update_pipeline_schedule": [["oauth2"], ["basic"], ["api_key"]],
    "delete_pipeline_schedule": [["oauth2"], ["basic"], ["api_key"]],
    "list_schedule_executions": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository_ssh_key_pair": [["oauth2"], ["basic"], ["api_key"]],
    "set_repository_ssh_key_pair": [["oauth2"], ["basic"], ["api_key"]],
    "delete_repository_ssh_key_pair": [["oauth2"], ["basic"], ["api_key"]],
    "list_pipeline_ssh_known_hosts": [["oauth2"], ["basic"], ["api_key"]],
    "create_ssh_known_host": [["oauth2"], ["basic"], ["api_key"]],
    "get_pipeline_ssh_known_host": [["oauth2"], ["basic"], ["api_key"]],
    "update_pipeline_known_host": [["oauth2"], ["basic"], ["api_key"]],
    "delete_known_host": [["oauth2"], ["basic"], ["api_key"]],
    "list_repository_pipeline_variables": [["oauth2"], ["basic"], ["api_key"]],
    "create_repository_pipeline_variable": [["oauth2"], ["basic"], ["api_key"]],
    "get_pipeline_variable": [["oauth2"], ["basic"], ["api_key"]],
    "update_repository_pipeline_variable": [["oauth2"], ["basic"], ["api_key"]],
    "delete_repository_pipeline_variable": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository_property": [["oauth2"], ["basic"], ["api_key"]],
    "update_repository_property": [["oauth2"], ["basic"], ["api_key"]],
    "delete_repository_property": [["oauth2"], ["basic"], ["api_key"]],
    "list_pull_requests": [["oauth2"], ["basic"], ["api_key"]],
    "create_pull_request": [["oauth2"], ["basic"], ["api_key"]],
    "list_pull_request_activity": [["oauth2"], ["basic"], ["api_key"]],
    "get_pull_request": [["oauth2"], ["basic"], ["api_key"]],
    "update_pull_request": [["oauth2"], ["basic"], ["api_key"]],
    "list_pull_request_activity_by_id": [["oauth2"], ["basic"], ["api_key"]],
    "approve_pull_request": [["oauth2"], ["basic"], ["api_key"]],
    "unapprove_pull_request": [["oauth2"], ["basic"], ["api_key"]],
    "list_pull_request_comments": [["oauth2"], ["basic"], ["api_key"]],
    "create_pull_request_comment": [["oauth2"], ["basic"], ["api_key"]],
    "get_pull_request_comment": [["oauth2"], ["basic"], ["api_key"]],
    "update_pull_request_comment": [["oauth2"], ["basic"], ["api_key"]],
    "delete_pull_request_comment": [["oauth2"], ["basic"], ["api_key"]],
    "resolve_pull_request_comment": [["oauth2"], ["basic"], ["api_key"]],
    "reopen_pull_request_comment_thread": [["oauth2"], ["basic"], ["api_key"]],
    "list_pull_request_commits": [["oauth2"], ["basic"], ["api_key"]],
    "decline_pull_request": [["oauth2"], ["basic"], ["api_key"]],
    "get_pull_request_diff": [["oauth2"], ["basic"], ["api_key"]],
    "get_pull_request_diffstat": [["oauth2"], ["basic"], ["api_key"]],
    "merge_pull_request": [["oauth2"], ["basic"], ["api_key"]],
    "get_pull_request_merge_task_status": [["oauth2"], ["basic"], ["api_key"]],
    "get_pull_request_patch": [["oauth2"], ["basic"], ["api_key"]],
    "request_pull_request_changes": [["oauth2"], ["basic"], ["api_key"]],
    "remove_pull_request_change_request": [["oauth2"], ["basic"], ["api_key"]],
    "list_pull_request_statuses": [["oauth2"], ["basic"], ["api_key"]],
    "list_pull_request_tasks": [["oauth2"], ["basic"], ["api_key"]],
    "create_pull_request_task": [["oauth2"], ["basic"], ["api_key"]],
    "get_pull_request_task": [["oauth2"], ["basic"], ["api_key"]],
    "update_pull_request_task": [["oauth2"], ["basic"], ["api_key"]],
    "delete_pull_request_task": [["oauth2"], ["basic"], ["api_key"]],
    "get_pull_request_property": [["oauth2"], ["basic"], ["api_key"]],
    "update_pull_request_property": [["oauth2"], ["basic"], ["api_key"]],
    "delete_pull_request_property": [["oauth2"], ["basic"], ["api_key"]],
    "list_repository_refs": [["oauth2"], ["basic"], ["api_key"]],
    "list_branches": [["oauth2"], ["basic"], ["api_key"]],
    "create_branch": [["oauth2"], ["basic"], ["api_key"]],
    "get_branch": [["oauth2"], ["basic"], ["api_key"]],
    "delete_branch": [["oauth2"], ["basic"], ["api_key"]],
    "list_repository_tags": [["oauth2"], ["basic"], ["api_key"]],
    "create_tag": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository_tag": [["oauth2"], ["basic"], ["api_key"]],
    "delete_tag": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository_root_src": [["oauth2"], ["basic"], ["api_key"]],
    "create_commit_with_files": [["oauth2"], ["basic"], ["api_key"]],
    "get_repository_src": [["oauth2"], ["basic"], ["api_key"]],
    "list_repository_watchers": [["oauth2"], ["basic"], ["api_key"]],
    "create_snippet": [["oauth2"], ["basic"], ["api_key"]],
    "list_workspace_snippets": [["oauth2"], ["basic"], ["api_key"]],
    "create_workspace_snippet": [["oauth2"], ["basic"], ["api_key"]],
    "get_snippet": [["oauth2"], ["basic"], ["api_key"]],
    "update_snippet": [["oauth2"], ["basic"], ["api_key"]],
    "delete_snippet": [["oauth2"], ["basic"], ["api_key"]],
    "list_snippet_comments": [["oauth2"], ["basic"], ["api_key"]],
    "create_snippet_comment": [["oauth2"], ["basic"], ["api_key"]],
    "get_snippet_comment": [["oauth2"], ["basic"], ["api_key"]],
    "update_snippet_comment": [["oauth2"], ["basic"], ["api_key"]],
    "delete_snippet_comment": [["oauth2"], ["basic"], ["api_key"]],
    "list_snippet_commits": [["oauth2"], ["basic"], ["api_key"]],
    "get_snippet_commit_changes": [["oauth2"], ["basic"], ["api_key"]],
    "get_snippet_file_content": [["oauth2"], ["basic"], ["api_key"]],
    "check_snippet_watch_status": [["oauth2"], ["basic"], ["api_key"]],
    "watch_snippet": [["oauth2"], ["basic"], ["api_key"]],
    "unwatch_snippet": [["oauth2"], ["basic"], ["api_key"]],
    "get_snippet_revision": [["oauth2"], ["basic"], ["api_key"]],
    "update_snippet_at_revision": [["oauth2"], ["basic"], ["api_key"]],
    "delete_snippet_revision": [["oauth2"], ["basic"], ["api_key"]],
    "get_snippet_file_contents": [["oauth2"], ["basic"], ["api_key"]],
    "get_snippet_diff": [["oauth2"], ["basic"], ["api_key"]],
    "get_snippet_patch": [["oauth2"], ["basic"], ["api_key"]],
    "search_team_code": [["oauth2"], ["basic"], ["api_key"]],
    "get_current_user": [["oauth2"], ["basic"], ["api_key"]],
    "list_user_emails": [["oauth2"], ["basic"], ["api_key"]],
    "get_email": [["oauth2"], ["basic"], ["api_key"]],
    "list_workspaces": [["oauth2"], ["basic"], ["api_key"]],
    "get_workspace_permission": [["oauth2"], ["basic"], ["api_key"]],
    "list_workspace_repository_permissions_for_user": [["oauth2"], ["basic"], ["api_key"]],
    "get_user": [["oauth2"], ["basic"], ["api_key"]],
    "list_user_gpg_keys": [["oauth2"], ["basic"], ["api_key"]],
    "add_gpg_key": [["oauth2"], ["basic"], ["api_key"]],
    "get_user_gpg_key": [["oauth2"], ["basic"], ["api_key"]],
    "delete_user_gpg_key": [["oauth2"], ["basic"], ["api_key"]],
    "get_user_app_property": [["oauth2"], ["basic"], ["api_key"]],
    "update_user_app_property": [["oauth2"], ["basic"], ["api_key"]],
    "delete_user_app_property": [["oauth2"], ["basic"], ["api_key"]],
    "search_user_code": [["oauth2"], ["basic"], ["api_key"]],
    "list_user_ssh_keys": [["oauth2"], ["basic"], ["api_key"]],
    "add_ssh_key": [["oauth2"], ["basic"], ["api_key"]],
    "get_user_ssh_key": [["oauth2"], ["basic"], ["api_key"]],
    "update_ssh_key": [["oauth2"], ["basic"], ["api_key"]],
    "delete_user_ssh_key": [["oauth2"], ["basic"], ["api_key"]],
    "get_workspace": [["oauth2"], ["basic"], ["api_key"]],
    "list_workspace_webhooks": [["oauth2"], ["basic"], ["api_key"]],
    "get_workspace_webhook": [["oauth2"], ["basic"], ["api_key"]],
    "update_workspace_webhook": [["oauth2"], ["basic"], ["api_key"]],
    "delete_workspace_webhook": [["oauth2"], ["basic"], ["api_key"]],
    "list_workspace_members": [["oauth2"], ["basic"], ["api_key"]],
    "get_workspace_member": [["oauth2"], ["basic"], ["api_key"]],
    "list_workspace_permissions": [["oauth2"], ["basic"], ["api_key"]],
    "list_workspace_repository_permissions": [["oauth2"], ["basic"], ["api_key"]],
    "list_repository_user_permissions_workspace": [["oauth2"], ["basic"], ["api_key"]],
    "list_workspace_runners": [["oauth2"], ["basic"], ["api_key"]],
    "create_workspace_runner": [["oauth2"], ["basic"], ["api_key"]],
    "get_workspace_runner": [["oauth2"], ["basic"], ["api_key"]],
    "update_workspace_runner": [["oauth2"], ["basic"], ["api_key"]],
    "delete_workspace_runner": [["oauth2"], ["basic"], ["api_key"]],
    "list_workspace_pipeline_variables": [["oauth2"], ["basic"], ["api_key"]],
    "create_pipeline_variable": [["oauth2"], ["basic"], ["api_key"]],
    "get_workspace_pipeline_variable": [["oauth2"], ["basic"], ["api_key"]],
    "update_workspace_pipeline_variable": [["oauth2"], ["basic"], ["api_key"]],
    "delete_workspace_pipeline_variable": [["oauth2"], ["basic"], ["api_key"]],
    "list_workspace_projects": [["oauth2"], ["basic"], ["api_key"]],
    "create_project": [["oauth2"], ["basic"], ["api_key"]],
    "get_project": [["oauth2"], ["basic"], ["api_key"]],
    "update_project": [["oauth2"], ["basic"], ["api_key"]],
    "delete_project": [["oauth2"], ["basic"], ["api_key"]],
    "get_project_branching_model": [["oauth2"], ["basic"], ["api_key"]],
    "get_project_branching_model_settings": [["oauth2"], ["basic"], ["api_key"]],
    "list_project_default_reviewers": [["oauth2"], ["basic"], ["api_key"]],
    "get_project_default_reviewer": [["oauth2"], ["basic"], ["api_key"]],
    "add_project_default_reviewer": [["oauth2"], ["basic"], ["api_key"]],
    "remove_project_default_reviewer": [["oauth2"], ["basic"], ["api_key"]],
    "list_project_deploy_keys": [["oauth2"], ["basic"], ["api_key"]],
    "create_project_deploy_key": [["oauth2"], ["basic"], ["api_key"]],
    "get_project_deploy_key": [["oauth2"], ["basic"], ["api_key"]],
    "delete_project_deploy_key": [["oauth2"], ["basic"], ["api_key"]],
    "list_project_group_permissions": [["oauth2"], ["basic"], ["api_key"]],
    "list_project_user_permissions": [["oauth2"], ["basic"], ["api_key"]],
    "list_user_pull_requests_in_workspace": [["oauth2"], ["basic"], ["api_key"]],
    "search_workspace_code": [["oauth2"], ["basic"], ["api_key"]]
}

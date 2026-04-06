"""
Authentication module for GitHub MCP server.

Generated: 2026-04-06 14:24:48 UTC
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
    "BearerTokenAuth",
    "JWTBearerAuth",
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
    OAuth 2.0 authentication for GitHub v3 REST API.

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
        Authorization URL: https://github.com/login/oauth/authorize
        Token URL: https://github.com/login/oauth/access_token

    Available Scopes (configure via OAUTH2_SCOPES):
        - repo
        - repo:status
        - repo_deployment
        - public_repo
        - repo:invite
        - security_events
        - admin:repo_hook
        - write:repo_hook
        - read:repo_hook
        - admin:org
        - write:org
        - read:org
        - admin:public_key
        - write:public_key
        - read:public_key
        - admin:org_hook
        - gist
        - notifications
        - user
        - read:user
        - user:email
        - user:follow
        - project
        - read:project
        - delete_repo
        - write:packages
        - read:packages
        - delete:packages
        - admin:gpg_key
        - write:gpg_key
        - read:gpg_key
        - codespace
        - workflow
        - read:audit_log
        - read:discussion
        - write:discussion
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
        self.token_url = "https://github.com/login/oauth/access_token"
        self.auth_url = "https://github.com/login/oauth/authorize"
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

class BearerTokenAuth:
    """
    Bearer token authentication for GitHub v3 REST API.

    Configuration:
        Provide the raw token in the environment variable.
        The authorization scheme prefix is automatically inserted.
    """

    def __init__(self, env_var: str = "BEARER_TOKEN", token_format: str = "Bearer"):
        """Initialize bearer token authentication from environment variable.

        Args:
            env_var: Environment variable name containing the bearer token.
            token_format: Authorization scheme prefix (e.g., 'Bearer').
        """
        self.token_format = token_format
        self.token = os.getenv(env_var, "").strip()

        # Check for empty token
        if not self.token:
            raise ValueError(
                f"{env_var} environment variable not set. "
                "Leave empty in .env to disable Bearer Token auth."
            )

        # Detect common placeholder patterns
        placeholders = ["placeholder", "your-", "example", "change-me", "todo", "sk_test_placeholder"]
        token_lower = self.token.lower()

        if any(p in token_lower for p in placeholders):
            raise ValueError(
                f"Bearer token appears to be a placeholder ({self.token[:20]}...). "
                "Please set a real token or leave empty to disable Bearer Token auth."
            )

    def get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for API requests."""
        return {
            'Authorization': f'{self.token_format} {self.token}'
        }

class JWTBearerAuth:
    """
    JWT Bearer authentication for GitHub v3 REST API.

    Generates short-lived JWTs signed with a private key (RFC 7523).
    Supports two modes:
    - Direct JWT: signed token used directly as Bearer token (e.g. GitHub Apps)
    - Token exchange: signed JWT exchanged at a token URL for an access token
      (e.g. Google service accounts)

    Configuration (environment variables):
        - JWT_PRIVATE_KEY: Absolute path to .pem file OR inline PEM key (required).
          Inline: encode newlines as literal \\n for single-line .env storage.
        - JWT_ISSUER_ID: Issuer claim value — App ID, Team ID, etc. (required)
        - JWT_ALGORITHM: Signing algorithm (default: RS256)
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

        # Required
        raw_key = os.getenv("JWT_PRIVATE_KEY", "").strip()
        if not raw_key:
            raise ValueError(
                "JWT_PRIVATE_KEY environment variable not set. "
                "Leave empty in .env to disable JWT Bearer auth."
            )
        # Support both inline PEM and file path:
        # - Starts with "-----BEGIN" → inline PEM (newlines may be escaped as \n)
        # - Otherwise → treat as file path to .pem file
        if raw_key.startswith("-----"):
            self._private_key = raw_key.replace("\\n", "\n")
        else:
            key_path = Path(raw_key)
            # Resolve relative paths against the server directory (where .env lives)
            if not key_path.is_absolute():
                key_path = Path(__file__).parent / key_path
            if not key_path.exists():
                raise ValueError(
                    f"JWT_PRIVATE_KEY points to '{raw_key}' but file not found. "
                    "Provide either an inline PEM key or a valid file path."
                )
            self._private_key = key_path.read_text()

        self._issuer = os.getenv("JWT_ISSUER_ID", "").strip()
        if not self._issuer:
            raise ValueError(
                "JWT_ISSUER_ID environment variable not set. "
                "Leave empty in .env to disable JWT Bearer auth."
            )

        # Optional — empty values fall back to defaults
        self._algorithm = os.getenv("JWT_ALGORITHM", "").strip() or "RS256"
        self._expiry = int(os.getenv("JWT_EXPIRY", "").strip() or "600")
        self._audience = os.getenv("JWT_AUDIENCE", "").strip() or None
        self._key_id = os.getenv("JWT_KEY_ID", "").strip() or None
        self._token_url = os.getenv("JWT_TOKEN_URL", "").strip() or None
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
            self._private_key,
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
            data: dict = {
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": jwt_token,
            }
            if self._scopes:
                data["scope"] = self._scopes

            response = httpx.post(self._token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            token = token_data["access_token"]
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
    "get_api_root": [["bearer_token"], ["oauth2"]],
    "list_advisories": [["bearer_token"], ["oauth2"]],
    "get_authenticated_app": [["jwt_bearer"]],
    "complete_github_app_manifest": [["bearer_token"], ["oauth2"]],
    "get_webhook_config": [["jwt_bearer"]],
    "configure_app_webhook": [["jwt_bearer"]],
    "list_webhook_deliveries_app": [["jwt_bearer"]],
    "get_webhook_delivery_app": [["jwt_bearer"]],
    "redeliver_webhook_delivery_app": [["jwt_bearer"]],
    "list_installation_requests": [["jwt_bearer"]],
    "list_app_installations": [["jwt_bearer"]],
    "get_app_installation": [["jwt_bearer"]],
    "uninstall_app": [["jwt_bearer"]],
    "create_installation_access_token": [["jwt_bearer"]],
    "suspend_app_installation": [["jwt_bearer"]],
    "unsuspend_app_installation": [["jwt_bearer"]],
    "revoke_app_authorization": [["bearer_token"], ["oauth2"]],
    "validate_token": [["bearer_token"], ["oauth2"]],
    "reset_application_token": [["bearer_token"], ["oauth2"]],
    "revoke_application_token": [["bearer_token"], ["oauth2"]],
    "create_scoped_token": [["bearer_token"], ["oauth2"]],
    "get_app": [["bearer_token"], ["oauth2"]],
    "get_assignment": [["bearer_token"], ["oauth2"]],
    "list_accepted_assignments": [["bearer_token"], ["oauth2"]],
    "list_assignment_grades": [["bearer_token"], ["oauth2"]],
    "list_classrooms": [["bearer_token"], ["oauth2"]],
    "get_classroom": [["bearer_token"], ["oauth2"]],
    "list_assignments": [["bearer_token"], ["oauth2"]],
    "list_codes_of_conduct": [["bearer_token"], ["oauth2"]],
    "get_conduct_code": [["bearer_token"], ["oauth2"]],
    "revoke_credentials": [["bearer_token"], ["oauth2"]],
    "list_emojis": [["bearer_token"], ["oauth2"]],
    "list_code_security_configurations": [["bearer_token"], ["oauth2"]],
    "create_enterprise_code_security_configuration": [["bearer_token"], ["oauth2"]],
    "list_enterprise_code_security_default_configurations": [["bearer_token"], ["oauth2"]],
    "get_code_security_configuration_enterprise": [["bearer_token"], ["oauth2"]],
    "update_code_security_configuration_enterprise": [["bearer_token"], ["oauth2"]],
    "delete_code_security_configuration_enterprise": [["bearer_token"], ["oauth2"]],
    "attach_code_security_configuration": [["bearer_token"], ["oauth2"]],
    "set_code_security_configuration_as_default": [["bearer_token"], ["oauth2"]],
    "list_code_security_configuration_repositories": [["bearer_token"], ["oauth2"]],
    "list_dependabot_alerts": [["bearer_token"], ["oauth2"]],
    "list_teams_enterprise": [["bearer_token"], ["oauth2"]],
    "create_enterprise_team": [["bearer_token"], ["oauth2"]],
    "list_enterprise_team_members": [["bearer_token"], ["oauth2"]],
    "add_team_members": [["bearer_token"], ["oauth2"]],
    "remove_team_members": [["bearer_token"], ["oauth2"]],
    "check_enterprise_team_membership": [["bearer_token"], ["oauth2"]],
    "add_team_member": [["bearer_token"], ["oauth2"]],
    "remove_team_member": [["bearer_token"], ["oauth2"]],
    "get_enterprise_team": [["bearer_token"], ["oauth2"]],
    "update_enterprise_team": [["bearer_token"], ["oauth2"]],
    "delete_enterprise_team": [["bearer_token"], ["oauth2"]],
    "list_events": [["bearer_token"], ["oauth2"]],
    "list_feeds": [["bearer_token"], ["oauth2"]],
    "list_gists": [["bearer_token"], ["oauth2"]],
    "create_gist": [["bearer_token"], ["oauth2"]],
    "list_public_gists": [["bearer_token"], ["oauth2"]],
    "list_starred_gists": [["bearer_token"], ["oauth2"]],
    "get_gist": [["bearer_token"], ["oauth2"]],
    "update_gist": [["bearer_token"], ["oauth2"]],
    "delete_gist": [["bearer_token"], ["oauth2"]],
    "list_gist_comments": [["bearer_token"], ["oauth2"]],
    "create_gist_comment": [["bearer_token"], ["oauth2"]],
    "get_gist_comment": [["bearer_token"], ["oauth2"]],
    "update_gist_comment": [["bearer_token"], ["oauth2"]],
    "delete_gist_comment": [["bearer_token"], ["oauth2"]],
    "list_gist_commits": [["bearer_token"], ["oauth2"]],
    "list_gist_forks": [["bearer_token"], ["oauth2"]],
    "fork_gist": [["bearer_token"], ["oauth2"]],
    "check_gist_starred": [["bearer_token"], ["oauth2"]],
    "star_gist": [["bearer_token"], ["oauth2"]],
    "remove_gist_star": [["bearer_token"], ["oauth2"]],
    "get_gist_revision": [["bearer_token"], ["oauth2"]],
    "list_gitignore_templates": [["bearer_token"], ["oauth2"]],
    "get_gitignore_template": [["bearer_token"], ["oauth2"]],
    "list_installation_repositories": [["bearer_token"], ["oauth2"]],
    "revoke_installation_token": [["bearer_token"], ["oauth2"]],
    "list_issues": [["bearer_token"], ["oauth2"]],
    "list_licenses": [["bearer_token"], ["oauth2"]],
    "get_license": [["bearer_token"], ["oauth2"]],
    "render_markdown": [["bearer_token"], ["oauth2"]],
    "render_markdown_raw": [["bearer_token"], ["oauth2"]],
    "get_subscription_plan": [["jwt_bearer"]],
    "list_marketplace_plans": [["jwt_bearer"]],
    "list_plan_accounts": [["jwt_bearer"]],
    "get_subscription_plan_stubbed": [["jwt_bearer"]],
    "list_marketplace_plans_stubbed": [["jwt_bearer"]],
    "list_plan_accounts_stubbed": [["jwt_bearer"]],
    "get_github_meta": [["bearer_token"], ["oauth2"]],
    "list_network_events": [["bearer_token"], ["oauth2"]],
    "list_notifications": [["bearer_token"], ["oauth2"]],
    "mark_notifications_as_read": [["bearer_token"], ["oauth2"]],
    "get_notification_thread": [["bearer_token"], ["oauth2"]],
    "mark_notification_thread_as_read": [["bearer_token"], ["oauth2"]],
    "mark_notification_thread_as_done": [["bearer_token"], ["oauth2"]],
    "get_thread_subscription": [["bearer_token"], ["oauth2"]],
    "configure_thread_notification": [["bearer_token"], ["oauth2"]],
    "mute_thread_subscription": [["bearer_token"], ["oauth2"]],
    "get_octocat": [["bearer_token"], ["oauth2"]],
    "list_organizations": [["bearer_token"], ["oauth2"]],
    "list_dependabot_repository_access": [["bearer_token"], ["oauth2"]],
    "update_dependabot_repository_access": [["bearer_token"], ["oauth2"]],
    "configure_dependabot_default_repository_access": [["bearer_token"], ["oauth2"]],
    "get_organization_billing_usage": [["bearer_token"], ["oauth2"]],
    "get_organization": [["bearer_token"], ["oauth2"]],
    "update_organization": [["bearer_token"], ["oauth2"]],
    "delete_organization": [["bearer_token"], ["oauth2"]],
    "get_actions_cache_usage_for_org": [["bearer_token"], ["oauth2"]],
    "list_actions_cache_usage_by_repository": [["bearer_token"], ["oauth2"]],
    "list_hosted_runners": [["bearer_token"], ["oauth2"]],
    "create_hosted_runner": [["bearer_token"], ["oauth2"]],
    "list_github_owned_runner_images": [["bearer_token"], ["oauth2"]],
    "list_partner_runner_images": [["bearer_token"], ["oauth2"]],
    "get_hosted_runners_limits": [["bearer_token"], ["oauth2"]],
    "list_hosted_runner_machine_specs": [["bearer_token"], ["oauth2"]],
    "list_hosted_runner_platforms": [["bearer_token"], ["oauth2"]],
    "get_hosted_runner": [["bearer_token"], ["oauth2"]],
    "update_hosted_runner": [["bearer_token"], ["oauth2"]],
    "delete_hosted_runner": [["bearer_token"], ["oauth2"]],
    "get_oidc_subject_claim_template": [["bearer_token"], ["oauth2"]],
    "configure_oidc_subject_claim_template": [["bearer_token"], ["oauth2"]],
    "get_organization_actions_permissions": [["bearer_token"], ["oauth2"]],
    "configure_organization_actions_permissions": [["bearer_token"], ["oauth2"]],
    "get_artifact_and_log_retention_settings": [["bearer_token"], ["oauth2"]],
    "configure_artifact_and_log_retention": [["bearer_token"], ["oauth2"]],
    "get_fork_pull_request_contributor_approval_policy": [["bearer_token"], ["oauth2"]],
    "configure_fork_pr_approval_policy": [["bearer_token"], ["oauth2"]],
    "get_fork_pr_workflow_settings_organization": [["bearer_token"], ["oauth2"]],
    "configure_fork_pull_request_workflows_for_private_repos": [["bearer_token"], ["oauth2"]],
    "list_organization_github_actions_repositories": [["bearer_token"], ["oauth2"]],
    "enable_actions_repositories": [["bearer_token"], ["oauth2"]],
    "enable_repository_github_actions": [["bearer_token"], ["oauth2"]],
    "disable_repository_github_actions": [["bearer_token"], ["oauth2"]],
    "list_organization_allowed_actions": [["bearer_token"], ["oauth2"]],
    "configure_organization_allowed_actions": [["bearer_token"], ["oauth2"]],
    "get_organization_self_hosted_runners_permissions": [["bearer_token"], ["oauth2"]],
    "configure_organization_self_hosted_runner_permissions": [["bearer_token"], ["oauth2"]],
    "list_organization_self_hosted_runner_repositories": [["bearer_token"], ["oauth2"]],
    "configure_self_hosted_runner_repositories": [["bearer_token"], ["oauth2"]],
    "enable_repository_self_hosted_runners": [["bearer_token"], ["oauth2"]],
    "remove_repository_from_self_hosted_runners": [["bearer_token"], ["oauth2"]],
    "get_organization_workflow_permissions": [["bearer_token"], ["oauth2"]],
    "configure_organization_workflow_permissions": [["bearer_token"], ["oauth2"]],
    "list_runner_groups": [["bearer_token"], ["oauth2"]],
    "create_runner_group": [["bearer_token"], ["oauth2"]],
    "get_runner_group": [["bearer_token"], ["oauth2"]],
    "update_runner_group": [["bearer_token"], ["oauth2"]],
    "delete_runner_group": [["bearer_token"], ["oauth2"]],
    "list_github_hosted_runners_in_group": [["bearer_token"], ["oauth2"]],
    "list_runner_group_repositories": [["bearer_token"], ["oauth2"]],
    "update_runner_group_repository_access": [["bearer_token"], ["oauth2"]],
    "grant_runner_group_repository_access": [["bearer_token"], ["oauth2"]],
    "revoke_runner_group_repository_access": [["bearer_token"], ["oauth2"]],
    "list_runners_in_group": [["bearer_token"], ["oauth2"]],
    "update_runner_group_runners": [["bearer_token"], ["oauth2"]],
    "add_runner_to_group": [["bearer_token"], ["oauth2"]],
    "remove_runner_from_group": [["bearer_token"], ["oauth2"]],
    "list_organization_runners": [["bearer_token"], ["oauth2"]],
    "list_runner_applications": [["bearer_token"], ["oauth2"]],
    "generate_runner_jitconfig": [["bearer_token"], ["oauth2"]],
    "generate_runner_registration_token": [["bearer_token"], ["oauth2"]],
    "generate_runner_removal_token": [["bearer_token"], ["oauth2"]],
    "get_runner": [["bearer_token"], ["oauth2"]],
    "remove_runner_from_organization": [["bearer_token"], ["oauth2"]],
    "list_runner_labels": [["bearer_token"], ["oauth2"]],
    "add_labels_to_runner": [["bearer_token"], ["oauth2"]],
    "update_runner_labels": [["bearer_token"], ["oauth2"]],
    "remove_all_custom_labels_from_runner": [["bearer_token"], ["oauth2"]],
    "remove_custom_label_from_runner": [["bearer_token"], ["oauth2"]],
    "list_organization_secrets": [["bearer_token"], ["oauth2"]],
    "get_organization_public_key": [["bearer_token"], ["oauth2"]],
    "get_organization_secret": [["bearer_token"], ["oauth2"]],
    "create_or_update_organization_secret": [["bearer_token"], ["oauth2"]],
    "delete_organization_secret": [["bearer_token"], ["oauth2"]],
    "list_organization_secret_repositories": [["bearer_token"], ["oauth2"]],
    "update_organization_secret_repositories": [["bearer_token"], ["oauth2"]],
    "grant_repository_access_to_organization_secret": [["bearer_token"], ["oauth2"]],
    "remove_repository_from_organization_secret": [["bearer_token"], ["oauth2"]],
    "list_organization_variables": [["bearer_token"], ["oauth2"]],
    "create_organization_variable": [["bearer_token"], ["oauth2"]],
    "get_organization_variable": [["bearer_token"], ["oauth2"]],
    "update_organization_variable": [["bearer_token"], ["oauth2"]],
    "delete_organization_variable": [["bearer_token"], ["oauth2"]],
    "list_organization_variable_repositories": [["bearer_token"], ["oauth2"]],
    "update_org_variable_repositories": [["bearer_token"], ["oauth2"]],
    "add_repository_to_org_variable": [["bearer_token"], ["oauth2"]],
    "remove_repository_from_org_variable": [["bearer_token"], ["oauth2"]],
    "register_artifact_storage": [["bearer_token"], ["oauth2"]],
    "list_artifact_storage_records": [["bearer_token"], ["oauth2"]],
    "list_attestations_by_digests": [["bearer_token"], ["oauth2"]],
    "delete_attestations": [["bearer_token"], ["oauth2"]],
    "delete_attestation_by_subject_digest": [["bearer_token"], ["oauth2"]],
    "delete_attestation": [["bearer_token"], ["oauth2"]],
    "list_attestations_organization": [["bearer_token"], ["oauth2"]],
    "list_blocked_users": [["bearer_token"], ["oauth2"]],
    "check_blocked_user": [["bearer_token"], ["oauth2"]],
    "block_user_organization": [["bearer_token"], ["oauth2"]],
    "unblock_user_organization": [["bearer_token"], ["oauth2"]],
    "list_campaigns": [["bearer_token"], ["oauth2"]],
    "create_campaign": [["bearer_token"], ["oauth2"]],
    "get_campaign": [["bearer_token"], ["oauth2"]],
    "update_campaign": [["bearer_token"], ["oauth2"]],
    "delete_campaign": [["bearer_token"], ["oauth2"]],
    "list_code_scanning_alerts": [["bearer_token"], ["oauth2"]],
    "list_code_security_configurations_for_org": [["bearer_token"], ["oauth2"]],
    "create_security_configuration": [["bearer_token"], ["oauth2"]],
    "list_default_code_security_configurations": [["bearer_token"], ["oauth2"]],
    "detach_security_configurations": [["bearer_token"], ["oauth2"]],
    "get_code_security_configuration": [["bearer_token"], ["oauth2"]],
    "update_code_security_configuration": [["bearer_token"], ["oauth2"]],
    "delete_code_security_configuration": [["bearer_token"], ["oauth2"]],
    "attach_security_configuration": [["bearer_token"], ["oauth2"]],
    "set_code_security_configuration_as_default_for_organization": [["bearer_token"], ["oauth2"]],
    "list_security_configuration_repositories": [["bearer_token"], ["oauth2"]],
    "list_organization_codespaces": [["bearer_token"], ["oauth2"]],
    "list_organization_secrets_codespaces": [["bearer_token"], ["oauth2"]],
    "get_organization_codespaces_public_key": [["bearer_token"], ["oauth2"]],
    "get_organization_secret_codespace": [["bearer_token"], ["oauth2"]],
    "create_or_update_organization_secret_codespaces": [["bearer_token"], ["oauth2"]],
    "delete_organization_secret_codespace": [["bearer_token"], ["oauth2"]],
    "list_organization_secret_repositories_codespaces": [["bearer_token"], ["oauth2"]],
    "update_organization_secret_repositories_codespaces": [["bearer_token"], ["oauth2"]],
    "add_repository_to_organization_secret": [["bearer_token"], ["oauth2"]],
    "remove_repository_from_organization_secret_codespaces": [["bearer_token"], ["oauth2"]],
    "get_copilot_billing": [["bearer_token"], ["oauth2"]],
    "list_copilot_seats": [["bearer_token"], ["oauth2"]],
    "grant_copilot_seats_to_teams": [["bearer_token"], ["oauth2"]],
    "revoke_copilot_access_from_teams": [["bearer_token"], ["oauth2"]],
    "grant_copilot_seats_to_users": [["bearer_token"], ["oauth2"]],
    "revoke_copilot_seat_assignments": [["bearer_token"], ["oauth2"]],
    "get_copilot_metrics": [["bearer_token"], ["oauth2"]],
    "list_organization_dependabot_alerts": [["bearer_token"], ["oauth2"]],
    "list_organization_secrets_dependabot": [["bearer_token"], ["oauth2"]],
    "get_organization_dependabot_public_key": [["bearer_token"], ["oauth2"]],
    "get_organization_secret_dependabot": [["bearer_token"], ["oauth2"]],
    "create_or_update_organization_secret_dependabot": [["bearer_token"], ["oauth2"]],
    "delete_organization_secret_dependabot": [["bearer_token"], ["oauth2"]],
    "list_organization_secret_repositories_dependabot": [["bearer_token"], ["oauth2"]],
    "update_organization_secret_repositories_dependabot": [["bearer_token"], ["oauth2"]],
    "add_repository_to_organization_secret_dependabot": [["bearer_token"], ["oauth2"]],
    "remove_repository_from_organization_secret_dependabot": [["bearer_token"], ["oauth2"]],
    "list_docker_migration_conflicts": [["bearer_token"], ["oauth2"]],
    "list_organization_events": [["bearer_token"], ["oauth2"]],
    "list_failed_invitations": [["bearer_token"], ["oauth2"]],
    "list_webhooks": [["bearer_token"], ["oauth2"]],
    "create_webhook": [["bearer_token"], ["oauth2"]],
    "get_organization_webhook": [["bearer_token"], ["oauth2"]],
    "update_webhook": [["bearer_token"], ["oauth2"]],
    "delete_webhook": [["bearer_token"], ["oauth2"]],
    "get_webhook_config_organization": [["bearer_token"], ["oauth2"]],
    "update_webhook_config": [["bearer_token"], ["oauth2"]],
    "list_webhook_deliveries_organization": [["bearer_token"], ["oauth2"]],
    "get_webhook_delivery_organization": [["bearer_token"], ["oauth2"]],
    "redeliver_webhook_delivery_organization": [["bearer_token"], ["oauth2"]],
    "ping_webhook": [["bearer_token"], ["oauth2"]],
    "list_route_stats_by_actor": [["bearer_token"], ["oauth2"]],
    "list_api_request_stats": [["bearer_token"], ["oauth2"]],
    "get_api_summary_stats": [["bearer_token"], ["oauth2"]],
    "get_user_api_stats": [["bearer_token"], ["oauth2"]],
    "get_api_stats_by_actor": [["bearer_token"], ["oauth2"]],
    "get_api_request_stats": [["bearer_token"], ["oauth2"]],
    "get_user_api_time_stats": [["bearer_token"], ["oauth2"]],
    "get_api_request_stats_by_actor": [["bearer_token"], ["oauth2"]],
    "get_user_api_stats_by_access_type": [["bearer_token"], ["oauth2"]],
    "get_app_organization_installation": [["bearer_token"], ["oauth2"]],
    "list_app_installations_organization": [["bearer_token"], ["oauth2"]],
    "get_organization_interaction_restrictions": [["bearer_token"], ["oauth2"]],
    "restrict_org_interactions": [["bearer_token"], ["oauth2"]],
    "remove_organization_interaction_restrictions": [["bearer_token"], ["oauth2"]],
    "list_pending_invitations": [["bearer_token"], ["oauth2"]],
    "invite_organization_member": [["bearer_token"], ["oauth2"]],
    "cancel_invitation": [["bearer_token"], ["oauth2"]],
    "list_invitation_teams": [["bearer_token"], ["oauth2"]],
    "list_issue_types": [["bearer_token"], ["oauth2"]],
    "create_issue_type": [["bearer_token"], ["oauth2"]],
    "update_issue_type": [["bearer_token"], ["oauth2"]],
    "delete_issue_type": [["bearer_token"], ["oauth2"]],
    "list_organization_issues": [["bearer_token"], ["oauth2"]],
    "list_organization_members": [["bearer_token"], ["oauth2"]],
    "check_organization_membership": [["bearer_token"], ["oauth2"]],
    "remove_organization_member": [["bearer_token"], ["oauth2"]],
    "list_organization_member_codespaces": [["bearer_token"], ["oauth2"]],
    "delete_codespace_from_organization": [["bearer_token"], ["oauth2"]],
    "stop_codespace": [["bearer_token"], ["oauth2"]],
    "get_copilot_seat_details": [["bearer_token"], ["oauth2"]],
    "get_organization_membership": [["bearer_token"], ["oauth2"]],
    "set_organization_membership": [["bearer_token"], ["oauth2"]],
    "remove_organization_membership": [["bearer_token"], ["oauth2"]],
    "list_organization_migrations": [["bearer_token"], ["oauth2"]],
    "initiate_organization_migration": [["bearer_token"], ["oauth2"]],
    "get_migration_status": [["bearer_token"], ["oauth2"]],
    "download_migration_archive": [["bearer_token"], ["oauth2"]],
    "delete_migration_archive": [["bearer_token"], ["oauth2"]],
    "unlock_migration_repository": [["bearer_token"], ["oauth2"]],
    "list_migration_repositories": [["bearer_token"], ["oauth2"]],
    "list_organization_roles": [["bearer_token"], ["oauth2"]],
    "revoke_team_organization_roles": [["bearer_token"], ["oauth2"]],
    "assign_organization_role_to_team": [["bearer_token"], ["oauth2"]],
    "remove_organization_role_from_team": [["bearer_token"], ["oauth2"]],
    "revoke_all_organization_roles_from_user": [["bearer_token"], ["oauth2"]],
    "assign_organization_role_to_user": [["bearer_token"], ["oauth2"]],
    "revoke_organization_role_from_user": [["bearer_token"], ["oauth2"]],
    "get_organization_role": [["bearer_token"], ["oauth2"]],
    "list_organization_role_teams": [["bearer_token"], ["oauth2"]],
    "list_organization_role_users": [["bearer_token"], ["oauth2"]],
    "list_outside_collaborators": [["bearer_token"], ["oauth2"]],
    "convert_member_to_outside_collaborator": [["bearer_token"], ["oauth2"]],
    "remove_outside_collaborator": [["bearer_token"], ["oauth2"]],
    "list_organization_packages": [["bearer_token"], ["oauth2"]],
    "get_organization_package": [["bearer_token"], ["oauth2"]],
    "delete_organization_package": [["bearer_token"], ["oauth2"]],
    "restore_organization_package": [["bearer_token"], ["oauth2"]],
    "list_organization_package_versions": [["bearer_token"], ["oauth2"]],
    "get_organization_package_version": [["bearer_token"], ["oauth2"]],
    "delete_package_version": [["bearer_token"], ["oauth2"]],
    "restore_package_version": [["bearer_token"], ["oauth2"]],
    "list_pat_grant_requests": [["bearer_token"], ["oauth2"]],
    "review_pat_grant_requests": [["bearer_token"], ["oauth2"]],
    "review_pat_grant_request": [["bearer_token"], ["oauth2"]],
    "list_pat_request_repositories": [["bearer_token"], ["oauth2"]],
    "list_organization_pat_grants": [["bearer_token"], ["oauth2"]],
    "revoke_organization_pat_access": [["bearer_token"], ["oauth2"]],
    "revoke_org_pat_access": [["bearer_token"], ["oauth2"]],
    "list_pat_repositories": [["bearer_token"], ["oauth2"]],
    "list_organization_private_registries": [["bearer_token"], ["oauth2"]],
    "create_organization_private_registry": [["bearer_token"], ["oauth2"]],
    "get_private_registry_public_key": [["bearer_token"], ["oauth2"]],
    "get_private_registry": [["bearer_token"], ["oauth2"]],
    "update_organization_private_registry": [["bearer_token"], ["oauth2"]],
    "delete_org_private_registry": [["bearer_token"], ["oauth2"]],
    "list_organization_projects": [["bearer_token"], ["oauth2"]],
    "get_organization_project": [["bearer_token"], ["oauth2"]],
    "list_project_fields": [["bearer_token"], ["oauth2"]],
    "get_project_field": [["bearer_token"], ["oauth2"]],
    "list_project_items": [["bearer_token"], ["oauth2"]],
    "add_item_to_project": [["bearer_token"], ["oauth2"]],
    "get_project_item": [["bearer_token"], ["oauth2"]],
    "update_project_item": [["bearer_token"], ["oauth2"]],
    "delete_project_item": [["bearer_token"], ["oauth2"]],
    "list_organization_custom_property_definitions": [["bearer_token"], ["oauth2"]],
    "batch_upsert_organization_custom_properties": [["bearer_token"], ["oauth2"]],
    "get_organization_custom_property": [["bearer_token"], ["oauth2"]],
    "define_organization_custom_property": [["bearer_token"], ["oauth2"]],
    "delete_organization_custom_property": [["bearer_token"], ["oauth2"]],
    "list_organization_repository_custom_properties": [["bearer_token"], ["oauth2"]],
    "batch_update_repository_custom_properties": [["bearer_token"], ["oauth2"]],
    "list_organization_public_members": [["bearer_token"], ["oauth2"]],
    "check_public_organization_membership": [["bearer_token"], ["oauth2"]],
    "publicize_organization_membership": [["bearer_token"], ["oauth2"]],
    "remove_public_organization_membership": [["bearer_token"], ["oauth2"]],
    "list_organization_repositories": [["bearer_token"], ["oauth2"]],
    "create_organization_repository": [["bearer_token"], ["oauth2"]],
    "list_organization_rulesets": [["bearer_token"], ["oauth2"]],
    "create_organization_ruleset": [["bearer_token"], ["oauth2"]],
    "list_organization_rule_suites": [["bearer_token"], ["oauth2"]],
    "get_organization_rule_suite": [["bearer_token"], ["oauth2"]],
    "get_organization_ruleset": [["bearer_token"], ["oauth2"]],
    "update_organization_ruleset": [["bearer_token"], ["oauth2"]],
    "delete_organization_ruleset": [["bearer_token"], ["oauth2"]],
    "list_ruleset_history": [["bearer_token"], ["oauth2"]],
    "get_ruleset_version": [["bearer_token"], ["oauth2"]],
    "list_secret_scanning_alerts": [["bearer_token"], ["oauth2"]],
    "list_secret_scanning_patterns": [["bearer_token"], ["oauth2"]],
    "update_secret_scanning_patterns": [["bearer_token"], ["oauth2"]],
    "list_organization_security_advisories": [["bearer_token"], ["oauth2"]],
    "list_network_configurations": [["bearer_token"], ["oauth2"]],
    "create_network_configuration": [["bearer_token"], ["oauth2"]],
    "get_network_configuration": [["bearer_token"], ["oauth2"]],
    "update_network_configuration": [["bearer_token"], ["oauth2"]],
    "delete_network_configuration": [["bearer_token"], ["oauth2"]],
    "get_network_settings": [["bearer_token"], ["oauth2"]],
    "get_team_copilot_metrics": [["bearer_token"], ["oauth2"]],
    "list_teams": [["bearer_token"], ["oauth2"]],
    "create_team": [["bearer_token"], ["oauth2"]],
    "get_team": [["bearer_token"], ["oauth2"]],
    "update_team": [["bearer_token"], ["oauth2"]],
    "delete_team": [["bearer_token"], ["oauth2"]],
    "list_team_invitations": [["bearer_token"], ["oauth2"]],
    "list_team_members": [["bearer_token"], ["oauth2"]],
    "get_team_membership": [["bearer_token"], ["oauth2"]],
    "add_or_update_team_membership": [["bearer_token"], ["oauth2"]],
    "remove_team_member_org": [["bearer_token"], ["oauth2"]],
    "list_team_repositories": [["bearer_token"], ["oauth2"]],
    "verify_team_repository_permissions": [["bearer_token"], ["oauth2"]],
    "set_team_repository_permission": [["bearer_token"], ["oauth2"]],
    "remove_repository_from_team": [["bearer_token"], ["oauth2"]],
    "list_child_teams": [["bearer_token"], ["oauth2"]],
    "get_rate_limit_status": [["bearer_token"], ["oauth2"]],
    "get_repository": [["bearer_token"], ["oauth2"]],
    "update_repository": [["bearer_token"], ["oauth2"]],
    "delete_repository": [["bearer_token"], ["oauth2"]],
    "list_artifacts": [["bearer_token"], ["oauth2"]],
    "get_artifact": [["bearer_token"], ["oauth2"]],
    "delete_artifact": [["bearer_token"], ["oauth2"]],
    "download_artifact": [["bearer_token"], ["oauth2"]],
    "get_actions_cache_usage": [["bearer_token"], ["oauth2"]],
    "list_caches": [["bearer_token"], ["oauth2"]],
    "delete_actions_cache_by_key": [["bearer_token"], ["oauth2"]],
    "delete_actions_cache": [["bearer_token"], ["oauth2"]],
    "get_workflow_job": [["bearer_token"], ["oauth2"]],
    "get_workflow_job_logs": [["bearer_token"], ["oauth2"]],
    "rerun_workflow_job": [["bearer_token"], ["oauth2"]],
    "get_oidc_subject_claim_customization": [["bearer_token"], ["oauth2"]],
    "configure_oidc_subject_claim": [["bearer_token"], ["oauth2"]],
    "list_organization_secrets_available_to_repository": [["bearer_token"], ["oauth2"]],
    "list_organization_variables_shared": [["bearer_token"], ["oauth2"]],
    "get_repository_actions_permissions": [["bearer_token"], ["oauth2"]],
    "configure_repository_actions_permissions": [["bearer_token"], ["oauth2"]],
    "get_workflow_repository_access": [["bearer_token"], ["oauth2"]],
    "configure_workflow_access_level": [["bearer_token"], ["oauth2"]],
    "get_artifact_and_log_retention_settings_repository": [["bearer_token"], ["oauth2"]],
    "configure_artifact_retention": [["bearer_token"], ["oauth2"]],
    "get_fork_pull_request_approval_permissions": [["bearer_token"], ["oauth2"]],
    "configure_fork_pr_approval_policy_repository": [["bearer_token"], ["oauth2"]],
    "get_fork_pr_workflow_settings": [["bearer_token"], ["oauth2"]],
    "configure_fork_pull_request_workflow_settings": [["bearer_token"], ["oauth2"]],
    "list_allowed_actions": [["bearer_token"], ["oauth2"]],
    "configure_allowed_actions": [["bearer_token"], ["oauth2"]],
    "get_workflow_permissions": [["bearer_token"], ["oauth2"]],
    "configure_workflow_permissions": [["bearer_token"], ["oauth2"]],
    "list_runners": [["bearer_token"], ["oauth2"]],
    "list_runner_downloads": [["bearer_token"], ["oauth2"]],
    "generate_runner_jitconfig_for_repo": [["bearer_token"], ["oauth2"]],
    "create_runner_registration_token": [["bearer_token"], ["oauth2"]],
    "generate_runner_removal_token_repository": [["bearer_token"], ["oauth2"]],
    "get_runner_repo": [["bearer_token"], ["oauth2"]],
    "remove_runner_from_repository": [["bearer_token"], ["oauth2"]],
    "list_runner_labels_for_repo": [["bearer_token"], ["oauth2"]],
    "add_labels_to_runner_for_repo": [["bearer_token"], ["oauth2"]],
    "update_runner_labels_repo": [["bearer_token"], ["oauth2"]],
    "remove_all_custom_labels_from_runner_for_repo": [["bearer_token"], ["oauth2"]],
    "remove_runner_label": [["bearer_token"], ["oauth2"]],
    "list_workflow_runs": [["bearer_token"], ["oauth2"]],
    "get_workflow_run": [["bearer_token"], ["oauth2"]],
    "delete_workflow_run": [["bearer_token"], ["oauth2"]],
    "list_workflow_run_approvals": [["bearer_token"], ["oauth2"]],
    "approve_workflow_run": [["bearer_token"], ["oauth2"]],
    "list_workflow_run_artifacts": [["bearer_token"], ["oauth2"]],
    "get_workflow_run_attempt": [["bearer_token"], ["oauth2"]],
    "list_workflow_run_attempt_jobs": [["bearer_token"], ["oauth2"]],
    "download_workflow_run_attempt_logs": [["bearer_token"], ["oauth2"]],
    "cancel_workflow_run": [["bearer_token"], ["oauth2"]],
    "review_deployment_protection_rule": [["bearer_token"], ["oauth2"]],
    "force_cancel_workflow_run": [["bearer_token"], ["oauth2"]],
    "list_workflow_run_jobs": [["bearer_token"], ["oauth2"]],
    "get_workflow_run_logs_download_url": [["bearer_token"], ["oauth2"]],
    "delete_workflow_run_logs": [["bearer_token"], ["oauth2"]],
    "list_pending_deployments": [["bearer_token"], ["oauth2"]],
    "review_pending_deployments": [["bearer_token"], ["oauth2"]],
    "rerun_workflow": [["bearer_token"], ["oauth2"]],
    "rerun_workflow_failed_jobs": [["bearer_token"], ["oauth2"]],
    "get_workflow_run_usage": [["bearer_token"], ["oauth2"]],
    "list_repository_secrets": [["bearer_token"], ["oauth2"]],
    "get_repository_public_key": [["bearer_token"], ["oauth2"]],
    "get_repository_secret": [["bearer_token"], ["oauth2"]],
    "create_or_update_repository_secret": [["bearer_token"], ["oauth2"]],
    "delete_repository_secret": [["bearer_token"], ["oauth2"]],
    "list_repository_variables": [["bearer_token"], ["oauth2"]],
    "create_repository_variable": [["bearer_token"], ["oauth2"]],
    "get_repository_variable": [["bearer_token"], ["oauth2"]],
    "update_repository_variable": [["bearer_token"], ["oauth2"]],
    "delete_repository_variable": [["bearer_token"], ["oauth2"]],
    "list_workflows": [["bearer_token"], ["oauth2"]],
    "get_workflow": [["bearer_token"], ["oauth2"]],
    "disable_workflow": [["bearer_token"], ["oauth2"]],
    "trigger_workflow": [["bearer_token"], ["oauth2"]],
    "enable_workflow": [["bearer_token"], ["oauth2"]],
    "list_workflow_runs_for_workflow": [["bearer_token"], ["oauth2"]],
    "get_workflow_usage": [["bearer_token"], ["oauth2"]],
    "list_repository_activities": [["bearer_token"], ["oauth2"]],
    "list_assignees": [["bearer_token"], ["oauth2"]],
    "verify_assignee_permission": [["bearer_token"], ["oauth2"]],
    "create_attestation": [["bearer_token"], ["oauth2"]],
    "list_attestations": [["bearer_token"], ["oauth2"]],
    "list_autolinks": [["bearer_token"], ["oauth2"]],
    "create_autolink": [["bearer_token"], ["oauth2"]],
    "get_autolink": [["bearer_token"], ["oauth2"]],
    "delete_autolink": [["bearer_token"], ["oauth2"]],
    "get_automated_security_fixes_status": [["bearer_token"], ["oauth2"]],
    "enable_automated_security_fixes": [["bearer_token"], ["oauth2"]],
    "disable_automated_security_fixes": [["bearer_token"], ["oauth2"]],
    "list_branches": [["bearer_token"], ["oauth2"]],
    "get_branch": [["bearer_token"], ["oauth2"]],
    "get_branch_protection": [["bearer_token"], ["oauth2"]],
    "configure_branch_protection": [["bearer_token"], ["oauth2"]],
    "remove_branch_protection": [["bearer_token"], ["oauth2"]],
    "get_branch_admin_protection": [["bearer_token"], ["oauth2"]],
    "enforce_admin_branch_protection": [["bearer_token"], ["oauth2"]],
    "disable_admin_branch_protection": [["bearer_token"], ["oauth2"]],
    "get_pull_request_review_protection": [["bearer_token"], ["oauth2"]],
    "configure_pull_request_review_protection": [["bearer_token"], ["oauth2"]],
    "remove_pull_request_review_protection": [["bearer_token"], ["oauth2"]],
    "check_branch_signature_protection": [["bearer_token"], ["oauth2"]],
    "enable_branch_signature_protection": [["bearer_token"], ["oauth2"]],
    "disable_branch_signature_protection": [["bearer_token"], ["oauth2"]],
    "get_branch_status_checks_protection": [["bearer_token"], ["oauth2"]],
    "update_status_check_protection": [["bearer_token"], ["oauth2"]],
    "disable_branch_status_check_protection": [["bearer_token"], ["oauth2"]],
    "list_status_check_contexts": [["bearer_token"], ["oauth2"]],
    "add_required_status_check_contexts": [["bearer_token"], ["oauth2"]],
    "configure_required_status_check_contexts": [["bearer_token"], ["oauth2"]],
    "remove_branch_protection_status_check_contexts": [["bearer_token"], ["oauth2"]],
    "list_branch_access_restrictions": [["bearer_token"], ["oauth2"]],
    "remove_branch_protection_restrictions": [["bearer_token"], ["oauth2"]],
    "list_apps_with_protected_branch_access": [["bearer_token"], ["oauth2"]],
    "grant_app_push_access": [["bearer_token"], ["oauth2"]],
    "update_branch_protection_app_restrictions": [["bearer_token"], ["oauth2"]],
    "revoke_app_branch_push_access": [["bearer_token"], ["oauth2"]],
    "list_teams_with_branch_access": [["bearer_token"], ["oauth2"]],
    "grant_team_branch_push_access": [["bearer_token"], ["oauth2"]],
    "replace_branch_protection_team_restrictions": [["bearer_token"], ["oauth2"]],
    "revoke_team_branch_push_access": [["bearer_token"], ["oauth2"]],
    "list_branch_protection_users": [["bearer_token"], ["oauth2"]],
    "grant_user_push_access": [["bearer_token"], ["oauth2"]],
    "replace_branch_protection_user_restrictions": [["bearer_token"], ["oauth2"]],
    "revoke_user_branch_access": [["bearer_token"], ["oauth2"]],
    "rename_branch": [["bearer_token"], ["oauth2"]],
    "create_check_run": [["bearer_token"], ["oauth2"]],
    "get_check_run": [["bearer_token"], ["oauth2"]],
    "update_check_run": [["bearer_token"], ["oauth2"]],
    "list_check_run_annotations": [["bearer_token"], ["oauth2"]],
    "trigger_check_run_recheck": [["bearer_token"], ["oauth2"]],
    "create_check_suite": [["bearer_token"], ["oauth2"]],
    "configure_check_suite_automation": [["bearer_token"], ["oauth2"]],
    "get_check_suite": [["bearer_token"], ["oauth2"]],
    "list_check_runs": [["bearer_token"], ["oauth2"]],
    "rerun_check_suite": [["bearer_token"], ["oauth2"]],
    "list_code_scanning_alerts_repository": [["bearer_token"], ["oauth2"]],
    "get_code_scanning_alert": [["bearer_token"], ["oauth2"]],
    "update_code_scanning_alert": [["bearer_token"], ["oauth2"]],
    "get_autofix_status": [["bearer_token"], ["oauth2"]],
    "create_code_scanning_autofix": [["bearer_token"], ["oauth2"]],
    "commit_code_scanning_autofix": [["bearer_token"], ["oauth2"]],
    "list_code_scanning_alert_instances": [["bearer_token"], ["oauth2"]],
    "list_code_scanning_analyses": [["bearer_token"], ["oauth2"]],
    "get_code_scanning_analysis": [["bearer_token"], ["oauth2"]],
    "delete_code_scanning_analysis": [["bearer_token"], ["oauth2"]],
    "list_codeql_databases": [["bearer_token"], ["oauth2"]],
    "get_codeql_database": [["bearer_token"], ["oauth2"]],
    "delete_codeql_database": [["bearer_token"], ["oauth2"]],
    "create_variant_analysis": [["bearer_token"], ["oauth2"]],
    "get_variant_analysis": [["bearer_token"], ["oauth2"]],
    "get_variant_analysis_repository_status": [["bearer_token"], ["oauth2"]],
    "get_code_scanning_default_setup": [["bearer_token"], ["oauth2"]],
    "configure_code_scanning_default_setup": [["bearer_token"], ["oauth2"]],
    "upload_sarif": [["bearer_token"], ["oauth2"]],
    "get_sarif_upload": [["bearer_token"], ["oauth2"]],
    "get_repository_code_security_configuration": [["bearer_token"], ["oauth2"]],
    "list_codeowners_errors": [["bearer_token"], ["oauth2"]],
    "list_codespaces_in_repository": [["bearer_token"], ["oauth2"]],
    "create_codespace": [["bearer_token"], ["oauth2"]],
    "list_devcontainers": [["bearer_token"], ["oauth2"]],
    "list_codespace_machines": [["bearer_token"], ["oauth2"]],
    "get_codespace_defaults": [["bearer_token"], ["oauth2"]],
    "validate_devcontainer_permissions": [["bearer_token"], ["oauth2"]],
    "list_codespace_secrets": [["bearer_token"], ["oauth2"]],
    "get_codespace_public_key": [["bearer_token"], ["oauth2"]],
    "get_codespace_secret": [["bearer_token"], ["oauth2"]],
    "create_or_update_codespace_secret_repository": [["bearer_token"], ["oauth2"]],
    "delete_codespace_secret": [["bearer_token"], ["oauth2"]],
    "list_collaborators": [["bearer_token"], ["oauth2"]],
    "verify_repository_collaborator": [["bearer_token"], ["oauth2"]],
    "add_collaborator": [["bearer_token"], ["oauth2"]],
    "remove_collaborator": [["bearer_token"], ["oauth2"]],
    "get_collaborator_permission": [["bearer_token"], ["oauth2"]],
    "list_commit_comments": [["bearer_token"], ["oauth2"]],
    "get_commit_comment": [["bearer_token"], ["oauth2"]],
    "update_commit_comment": [["bearer_token"], ["oauth2"]],
    "delete_commit_comment": [["bearer_token"], ["oauth2"]],
    "list_commit_comment_reactions": [["bearer_token"], ["oauth2"]],
    "add_commit_comment_reaction": [["bearer_token"], ["oauth2"]],
    "remove_commit_comment_reaction": [["bearer_token"], ["oauth2"]],
    "list_commits": [["bearer_token"], ["oauth2"]],
    "list_branches_for_commit": [["bearer_token"], ["oauth2"]],
    "list_commit_comments_by_sha": [["bearer_token"], ["oauth2"]],
    "create_commit_comment": [["bearer_token"], ["oauth2"]],
    "list_pull_requests_for_commit": [["bearer_token"], ["oauth2"]],
    "get_commit": [["bearer_token"], ["oauth2"]],
    "list_check_runs_for_ref": [["bearer_token"], ["oauth2"]],
    "list_check_suites": [["bearer_token"], ["oauth2"]],
    "get_commit_status": [["bearer_token"], ["oauth2"]],
    "list_commit_statuses": [["bearer_token"], ["oauth2"]],
    "get_repository_community_profile": [["bearer_token"], ["oauth2"]],
    "compare_commits": [["bearer_token"], ["oauth2"]],
    "get_repository_content": [["bearer_token"], ["oauth2"]],
    "create_or_update_file": [["bearer_token"], ["oauth2"]],
    "delete_file": [["bearer_token"], ["oauth2"]],
    "list_contributors": [["bearer_token"], ["oauth2"]],
    "list_dependabot_alerts_repository": [["bearer_token"], ["oauth2"]],
    "get_dependabot_alert": [["bearer_token"], ["oauth2"]],
    "update_dependabot_alert": [["bearer_token"], ["oauth2"]],
    "list_dependabot_secrets": [["bearer_token"], ["oauth2"]],
    "get_dependabot_public_key": [["bearer_token"], ["oauth2"]],
    "get_dependabot_secret": [["bearer_token"], ["oauth2"]],
    "create_or_update_dependabot_secret": [["bearer_token"], ["oauth2"]],
    "delete_dependabot_secret": [["bearer_token"], ["oauth2"]],
    "compare_dependency_changes": [["bearer_token"], ["oauth2"]],
    "export_sbom": [["bearer_token"], ["oauth2"]],
    "submit_dependency_snapshot": [["bearer_token"], ["oauth2"]],
    "list_deployments": [["bearer_token"], ["oauth2"]],
    "create_deployment": [["bearer_token"], ["oauth2"]],
    "get_deployment": [["bearer_token"], ["oauth2"]],
    "delete_deployment": [["bearer_token"], ["oauth2"]],
    "list_deployment_statuses": [["bearer_token"], ["oauth2"]],
    "create_deployment_status": [["bearer_token"], ["oauth2"]],
    "get_deployment_status": [["bearer_token"], ["oauth2"]],
    "trigger_repository_dispatch_event": [["bearer_token"], ["oauth2"]],
    "list_environments": [["bearer_token"], ["oauth2"]],
    "get_environment": [["bearer_token"], ["oauth2"]],
    "configure_environment": [["bearer_token"], ["oauth2"]],
    "delete_environment": [["bearer_token"], ["oauth2"]],
    "list_deployment_branch_policies": [["bearer_token"], ["oauth2"]],
    "create_deployment_branch_policy": [["bearer_token"], ["oauth2"]],
    "get_deployment_branch_policy": [["bearer_token"], ["oauth2"]],
    "update_deployment_branch_policy": [["bearer_token"], ["oauth2"]],
    "delete_deployment_branch_policy": [["bearer_token"], ["oauth2"]],
    "list_deployment_protection_rules": [["bearer_token"], ["oauth2"]],
    "enable_deployment_protection_rule": [["bearer_token"], ["oauth2"]],
    "list_deployment_rule_integrations": [["bearer_token"], ["oauth2"]],
    "get_deployment_protection_rule": [["bearer_token"], ["oauth2"]],
    "disable_deployment_protection_rule": [["bearer_token"], ["oauth2"]],
    "list_environment_secrets": [["bearer_token"], ["oauth2"]],
    "get_environment_public_key": [["bearer_token"], ["oauth2"]],
    "get_environment_secret": [["bearer_token"], ["oauth2"]],
    "create_or_update_environment_secret": [["bearer_token"], ["oauth2"]],
    "delete_environment_secret": [["bearer_token"], ["oauth2"]],
    "list_environment_variables": [["bearer_token"], ["oauth2"]],
    "create_environment_variable": [["bearer_token"], ["oauth2"]],
    "get_environment_variable": [["bearer_token"], ["oauth2"]],
    "update_environment_variable": [["bearer_token"], ["oauth2"]],
    "delete_environment_variable": [["bearer_token"], ["oauth2"]],
    "list_repository_events": [["bearer_token"], ["oauth2"]],
    "list_repository_forks": [["bearer_token"], ["oauth2"]],
    "fork_repository": [["bearer_token"], ["oauth2"]],
    "create_blob": [["bearer_token"], ["oauth2"]],
    "get_blob": [["bearer_token"], ["oauth2"]],
    "create_commit": [["bearer_token"], ["oauth2"]],
    "get_commit_object": [["bearer_token"], ["oauth2"]],
    "list_git_refs": [["bearer_token"], ["oauth2"]],
    "get_git_reference": [["bearer_token"], ["oauth2"]],
    "create_git_ref": [["bearer_token"], ["oauth2"]],
    "update_git_ref": [["bearer_token"], ["oauth2"]],
    "delete_git_ref": [["bearer_token"], ["oauth2"]],
    "create_tag": [["bearer_token"], ["oauth2"]],
    "get_tag": [["bearer_token"], ["oauth2"]],
    "create_tree": [["bearer_token"], ["oauth2"]],
    "fetch_tree": [["bearer_token"], ["oauth2"]],
    "list_webhooks_repository": [["bearer_token"], ["oauth2"]],
    "create_webhook_repository": [["bearer_token"], ["oauth2"]],
    "get_webhook": [["bearer_token"], ["oauth2"]],
    "update_webhook_repository": [["bearer_token"], ["oauth2"]],
    "delete_webhook_repository": [["bearer_token"], ["oauth2"]],
    "get_webhook_config_repository": [["bearer_token"], ["oauth2"]],
    "update_webhook_config_repository": [["bearer_token"], ["oauth2"]],
    "list_webhook_deliveries": [["bearer_token"], ["oauth2"]],
    "get_webhook_delivery": [["bearer_token"], ["oauth2"]],
    "redeliver_webhook_delivery": [["bearer_token"], ["oauth2"]],
    "trigger_webhook_ping": [["bearer_token"], ["oauth2"]],
    "trigger_webhook_test": [["bearer_token"], ["oauth2"]],
    "get_app_installation_repository": [["bearer_token"], ["oauth2"]],
    "get_repository_interaction_restrictions": [["bearer_token"], ["oauth2"]],
    "restrict_repository_interactions": [["bearer_token"], ["oauth2"]],
    "remove_interaction_restrictions": [["bearer_token"], ["oauth2"]],
    "list_repository_invitations": [["bearer_token"], ["oauth2"]],
    "update_repository_invitation": [["bearer_token"], ["oauth2"]],
    "delete_repository_invitation": [["bearer_token"], ["oauth2"]],
    "list_issues_repository": [["bearer_token"], ["oauth2"]],
    "create_issue": [["bearer_token"], ["oauth2"]],
    "list_issue_comments_for_repository": [["bearer_token"], ["oauth2"]],
    "get_issue_comment": [["bearer_token"], ["oauth2"]],
    "update_issue_comment": [["bearer_token"], ["oauth2"]],
    "delete_issue_comment": [["bearer_token"], ["oauth2"]],
    "list_comment_reactions": [["bearer_token"], ["oauth2"]],
    "add_issue_comment_reaction": [["bearer_token"], ["oauth2"]],
    "remove_issue_comment_reaction": [["bearer_token"], ["oauth2"]],
    "list_issue_events": [["bearer_token"], ["oauth2"]],
    "get_issue_event": [["bearer_token"], ["oauth2"]],
    "get_issue": [["bearer_token"], ["oauth2"]],
    "update_issue": [["bearer_token"], ["oauth2"]],
    "assign_issue_users": [["bearer_token"], ["oauth2"]],
    "remove_issue_assignees": [["bearer_token"], ["oauth2"]],
    "verify_issue_assignee": [["bearer_token"], ["oauth2"]],
    "list_issue_comments": [["bearer_token"], ["oauth2"]],
    "add_issue_comment": [["bearer_token"], ["oauth2"]],
    "list_blocking_issues": [["bearer_token"], ["oauth2"]],
    "mark_issue_blocked_by": [["bearer_token"], ["oauth2"]],
    "remove_issue_blocking_dependency": [["bearer_token"], ["oauth2"]],
    "list_blocking_dependencies": [["bearer_token"], ["oauth2"]],
    "list_issue_events_for_issue": [["bearer_token"], ["oauth2"]],
    "list_issue_labels": [["bearer_token"], ["oauth2"]],
    "add_issue_labels": [["bearer_token"], ["oauth2"]],
    "replace_issue_labels": [["bearer_token"], ["oauth2"]],
    "remove_all_issue_labels": [["bearer_token"], ["oauth2"]],
    "remove_issue_label": [["bearer_token"], ["oauth2"]],
    "lock_issue": [["bearer_token"], ["oauth2"]],
    "unlock_issue": [["bearer_token"], ["oauth2"]],
    "get_parent_issue": [["bearer_token"], ["oauth2"]],
    "list_issue_reactions": [["bearer_token"], ["oauth2"]],
    "add_issue_reaction": [["bearer_token"], ["oauth2"]],
    "delete_issue_reaction": [["bearer_token"], ["oauth2"]],
    "unlink_sub_issue": [["bearer_token"], ["oauth2"]],
    "list_sub_issues": [["bearer_token"], ["oauth2"]],
    "link_sub_issue": [["bearer_token"], ["oauth2"]],
    "reorder_sub_issue": [["bearer_token"], ["oauth2"]],
    "list_issue_timeline_events": [["bearer_token"], ["oauth2"]],
    "list_deploy_keys": [["bearer_token"], ["oauth2"]],
    "create_deploy_key": [["bearer_token"], ["oauth2"]],
    "get_deploy_key": [["bearer_token"], ["oauth2"]],
    "delete_deploy_key": [["bearer_token"], ["oauth2"]],
    "list_labels": [["bearer_token"], ["oauth2"]],
    "create_label": [["bearer_token"], ["oauth2"]],
    "get_label": [["bearer_token"], ["oauth2"]],
    "update_label": [["bearer_token"], ["oauth2"]],
    "delete_label": [["bearer_token"], ["oauth2"]],
    "list_repository_languages": [["bearer_token"], ["oauth2"]],
    "get_repository_license": [["bearer_token"], ["oauth2"]],
    "sync_fork_with_upstream": [["bearer_token"], ["oauth2"]],
    "merge_branch": [["bearer_token"], ["oauth2"]],
    "list_milestones": [["bearer_token"], ["oauth2"]],
    "create_milestone": [["bearer_token"], ["oauth2"]],
    "get_milestone": [["bearer_token"], ["oauth2"]],
    "update_milestone": [["bearer_token"], ["oauth2"]],
    "delete_milestone": [["bearer_token"], ["oauth2"]],
    "list_milestone_labels": [["bearer_token"], ["oauth2"]],
    "list_notifications_repository": [["bearer_token"], ["oauth2"]],
    "mark_repository_notifications_as_read": [["bearer_token"], ["oauth2"]],
    "get_pages_site": [["bearer_token"], ["oauth2"]],
    "enable_pages_site": [["bearer_token"], ["oauth2"]],
    "configure_pages_site": [["bearer_token"], ["oauth2"]],
    "delete_pages_site": [["bearer_token"], ["oauth2"]],
    "list_pages_builds": [["bearer_token"], ["oauth2"]],
    "trigger_pages_build": [["bearer_token"], ["oauth2"]],
    "get_latest_pages_build": [["bearer_token"], ["oauth2"]],
    "get_pages_build": [["bearer_token"], ["oauth2"]],
    "deploy_pages": [["bearer_token"], ["oauth2"]],
    "get_pages_deployment": [["bearer_token"], ["oauth2"]],
    "cancel_pages_deployment": [["bearer_token"], ["oauth2"]],
    "check_pages_health": [["bearer_token"], ["oauth2"]],
    "check_private_vulnerability_reporting": [["bearer_token"], ["oauth2"]],
    "enable_private_vulnerability_reporting": [["bearer_token"], ["oauth2"]],
    "disable_vulnerability_reporting": [["bearer_token"], ["oauth2"]],
    "list_repository_custom_properties": [["bearer_token"], ["oauth2"]],
    "set_repository_custom_properties": [["bearer_token"], ["oauth2"]],
    "list_pull_requests": [["bearer_token"], ["oauth2"]],
    "create_pull_request": [["bearer_token"], ["oauth2"]],
    "list_pull_request_review_comments_for_repo": [["bearer_token"], ["oauth2"]],
    "get_pull_request_review_comment": [["bearer_token"], ["oauth2"]],
    "update_pull_request_review_comment": [["bearer_token"], ["oauth2"]],
    "delete_pull_request_review_comment": [["bearer_token"], ["oauth2"]],
    "list_pull_request_review_comment_reactions": [["bearer_token"], ["oauth2"]],
    "add_reaction_to_pull_request_comment": [["bearer_token"], ["oauth2"]],
    "remove_pull_request_comment_reaction": [["bearer_token"], ["oauth2"]],
    "get_pull_request": [["bearer_token"], ["oauth2"]],
    "update_pull_request": [["bearer_token"], ["oauth2"]],
    "create_codespace_from_pull_request": [["bearer_token"], ["oauth2"]],
    "list_pull_request_review_comments": [["bearer_token"], ["oauth2"]],
    "create_pull_request_review_comment": [["bearer_token"], ["oauth2"]],
    "reply_to_review_comment": [["bearer_token"], ["oauth2"]],
    "list_pull_request_commits": [["bearer_token"], ["oauth2"]],
    "list_pull_request_files": [["bearer_token"], ["oauth2"]],
    "check_pull_request_merged": [["bearer_token"], ["oauth2"]],
    "merge_pull_request": [["bearer_token"], ["oauth2"]],
    "list_pull_request_requested_reviewers": [["bearer_token"], ["oauth2"]],
    "request_pull_request_reviewers": [["bearer_token"], ["oauth2"]],
    "remove_pull_request_reviewers": [["bearer_token"], ["oauth2"]],
    "list_pull_request_reviews": [["bearer_token"], ["oauth2"]],
    "create_pull_request_review": [["bearer_token"], ["oauth2"]],
    "get_pull_request_review": [["bearer_token"], ["oauth2"]],
    "update_pull_request_review": [["bearer_token"], ["oauth2"]],
    "delete_pending_review": [["bearer_token"], ["oauth2"]],
    "list_review_comments": [["bearer_token"], ["oauth2"]],
    "dismiss_pull_request_review": [["bearer_token"], ["oauth2"]],
    "submit_pull_request_review": [["bearer_token"], ["oauth2"]],
    "sync_pull_request_branch": [["bearer_token"], ["oauth2"]],
    "get_repository_readme": [["bearer_token"], ["oauth2"]],
    "get_readme": [["bearer_token"], ["oauth2"]],
    "list_releases": [["bearer_token"], ["oauth2"]],
    "create_release": [["bearer_token"], ["oauth2"]],
    "download_release_asset": [["bearer_token"], ["oauth2"]],
    "update_release_asset": [["bearer_token"], ["oauth2"]],
    "delete_release_asset": [["bearer_token"], ["oauth2"]],
    "generate_release_notes": [["bearer_token"], ["oauth2"]],
    "get_latest_release": [["bearer_token"], ["oauth2"]],
    "get_release_by_tag": [["bearer_token"], ["oauth2"]],
    "get_release": [["bearer_token"], ["oauth2"]],
    "update_release": [["bearer_token"], ["oauth2"]],
    "delete_release": [["bearer_token"], ["oauth2"]],
    "list_release_assets": [["bearer_token"], ["oauth2"]],
    "upload_release_asset": [["bearer_token"], ["oauth2"]],
    "list_release_reactions": [["bearer_token"], ["oauth2"]],
    "add_release_reaction": [["bearer_token"], ["oauth2"]],
    "delete_release_reaction": [["bearer_token"], ["oauth2"]],
    "list_branch_rules": [["bearer_token"], ["oauth2"]],
    "list_repository_rulesets": [["bearer_token"], ["oauth2"]],
    "create_ruleset": [["bearer_token"], ["oauth2"]],
    "list_rule_suites": [["bearer_token"], ["oauth2"]],
    "get_rule_suite": [["bearer_token"], ["oauth2"]],
    "get_ruleset": [["bearer_token"], ["oauth2"]],
    "update_ruleset": [["bearer_token"], ["oauth2"]],
    "delete_ruleset": [["bearer_token"], ["oauth2"]],
    "list_ruleset_history_repository": [["bearer_token"], ["oauth2"]],
    "get_ruleset_version_repository": [["bearer_token"], ["oauth2"]],
    "list_secret_scanning_alerts_repository": [["bearer_token"], ["oauth2"]],
    "get_secret_scanning_alert": [["bearer_token"], ["oauth2"]],
    "update_secret_scanning_alert": [["bearer_token"], ["oauth2"]],
    "list_secret_alert_locations": [["bearer_token"], ["oauth2"]],
    "bypass_push_protection": [["bearer_token"], ["oauth2"]],
    "list_secret_scan_history": [["bearer_token"], ["oauth2"]],
    "list_security_advisories": [["bearer_token"], ["oauth2"]],
    "create_security_advisory": [["bearer_token"], ["oauth2"]],
    "report_security_vulnerability": [["bearer_token"], ["oauth2"]],
    "get_security_advisory_repository": [["bearer_token"], ["oauth2"]],
    "update_security_advisory": [["bearer_token"], ["oauth2"]],
    "request_cve_for_advisory": [["bearer_token"], ["oauth2"]],
    "create_security_advisory_fork": [["bearer_token"], ["oauth2"]],
    "list_stargazers": [["bearer_token"], ["oauth2"]],
    "get_code_frequency_stats": [["bearer_token"], ["oauth2"]],
    "list_commit_activity_stats": [["bearer_token"], ["oauth2"]],
    "list_contributor_stats": [["bearer_token"], ["oauth2"]],
    "get_repository_participation_stats": [["bearer_token"], ["oauth2"]],
    "get_commit_punch_card": [["bearer_token"], ["oauth2"]],
    "create_commit_status": [["bearer_token"], ["oauth2"]],
    "list_watchers": [["bearer_token"], ["oauth2"]],
    "get_repository_subscription": [["bearer_token"], ["oauth2"]],
    "configure_repository_subscription": [["bearer_token"], ["oauth2"]],
    "unwatch_repository": [["bearer_token"], ["oauth2"]],
    "list_tags": [["bearer_token"], ["oauth2"]],
    "download_repository_archive": [["bearer_token"], ["oauth2"]],
    "list_repository_teams": [["bearer_token"], ["oauth2"]],
    "list_repository_topics": [["bearer_token"], ["oauth2"]],
    "update_repository_topics": [["bearer_token"], ["oauth2"]],
    "list_repository_clones": [["bearer_token"], ["oauth2"]],
    "list_popular_paths": [["bearer_token"], ["oauth2"]],
    "list_top_referrers": [["bearer_token"], ["oauth2"]],
    "get_repository_views": [["bearer_token"], ["oauth2"]],
    "transfer_repository": [["bearer_token"], ["oauth2"]],
    "get_vulnerability_alerts_status": [["bearer_token"], ["oauth2"]],
    "enable_vulnerability_alerts": [["bearer_token"], ["oauth2"]],
    "disable_vulnerability_alerts": [["bearer_token"], ["oauth2"]],
    "download_repository_archive_zip": [["bearer_token"], ["oauth2"]],
    "create_repository_from_template": [["bearer_token"], ["oauth2"]],
    "list_public_repositories": [["bearer_token"], ["oauth2"]],
    "search_code": [["bearer_token"], ["oauth2"]],
    "search_commits": [["bearer_token"], ["oauth2"]],
    "search_issues": [["bearer_token"], ["oauth2"]],
    "search_labels": [["bearer_token"], ["oauth2"]],
    "search_repositories": [["bearer_token"], ["oauth2"]],
    "search_topics": [["bearer_token"], ["oauth2"]],
    "search_users": [["bearer_token"], ["oauth2"]],
    "get_authenticated_user": [["bearer_token"], ["oauth2"]],
    "update_user": [["bearer_token"], ["oauth2"]],
    "list_blocked_users_personal": [["bearer_token"], ["oauth2"]],
    "check_user_blocked": [["bearer_token"], ["oauth2"]],
    "block_user": [["bearer_token"], ["oauth2"]],
    "unblock_user": [["bearer_token"], ["oauth2"]],
    "list_codespaces": [["bearer_token"], ["oauth2"]],
    "create_codespace_from_pull_request_2": [["bearer_token"], ["oauth2"]],
    "list_codespace_secrets_for_user": [["bearer_token"], ["oauth2"]],
    "get_codespaces_public_key": [["bearer_token"], ["oauth2"]],
    "get_codespace_secret_for_user": [["bearer_token"], ["oauth2"]],
    "create_or_update_codespace_secret": [["bearer_token"], ["oauth2"]],
    "delete_codespace_secret_for_user": [["bearer_token"], ["oauth2"]],
    "list_repositories_for_secret": [["bearer_token"], ["oauth2"]],
    "update_secret_repositories": [["bearer_token"], ["oauth2"]],
    "add_repository_to_codespace_secret": [["bearer_token"], ["oauth2"]],
    "remove_repository_from_codespace_secret": [["bearer_token"], ["oauth2"]],
    "get_codespace": [["bearer_token"], ["oauth2"]],
    "update_codespace": [["bearer_token"], ["oauth2"]],
    "delete_codespace": [["bearer_token"], ["oauth2"]],
    "export_codespace": [["bearer_token"], ["oauth2"]],
    "get_codespace_export_details": [["bearer_token"], ["oauth2"]],
    "list_codespace_machines_available": [["bearer_token"], ["oauth2"]],
    "publish_codespace": [["bearer_token"], ["oauth2"]],
    "start_codespace": [["bearer_token"], ["oauth2"]],
    "stop_codespace_authenticated": [["bearer_token"], ["oauth2"]],
    "set_primary_email_visibility": [["bearer_token"], ["oauth2"]],
    "list_emails": [["bearer_token"], ["oauth2"]],
    "add_email": [["bearer_token"], ["oauth2"]],
    "delete_email": [["bearer_token"], ["oauth2"]],
    "list_followers": [["bearer_token"], ["oauth2"]],
    "list_followed_users": [["bearer_token"], ["oauth2"]],
    "check_user_is_followed": [["bearer_token"], ["oauth2"]],
    "follow_user": [["bearer_token"], ["oauth2"]],
    "unfollow_user": [["bearer_token"], ["oauth2"]],
    "list_gpg_keys": [["bearer_token"], ["oauth2"]],
    "add_gpg_key": [["bearer_token"], ["oauth2"]],
    "get_gpg_key": [["bearer_token"], ["oauth2"]],
    "delete_gpg_key": [["bearer_token"], ["oauth2"]],
    "list_app_installations_user": [["bearer_token"], ["oauth2"]],
    "list_installation_repositories_for_user": [["bearer_token"], ["oauth2"]],
    "add_repository_to_installation": [["bearer_token"], ["oauth2"]],
    "remove_repository_from_app_installation": [["bearer_token"], ["oauth2"]],
    "get_interaction_restrictions": [["bearer_token"], ["oauth2"]],
    "restrict_user_interactions": [["bearer_token"], ["oauth2"]],
    "remove_interaction_restrictions_user": [["bearer_token"], ["oauth2"]],
    "list_issues_assigned": [["bearer_token"], ["oauth2"]],
    "list_ssh_keys": [["bearer_token"], ["oauth2"]],
    "add_ssh_key": [["bearer_token"], ["oauth2"]],
    "get_ssh_key": [["bearer_token"], ["oauth2"]],
    "delete_ssh_key": [["bearer_token"], ["oauth2"]],
    "list_subscriptions": [["bearer_token"], ["oauth2"]],
    "list_subscriptions_stubbed": [["bearer_token"], ["oauth2"]],
    "list_organization_memberships": [["bearer_token"], ["oauth2"]],
    "get_organization_membership_authenticated": [["bearer_token"], ["oauth2"]],
    "activate_organization_membership": [["bearer_token"], ["oauth2"]],
    "list_migrations": [["bearer_token"], ["oauth2"]],
    "start_user_migration": [["bearer_token"], ["oauth2"]],
    "get_migration_status_user": [["bearer_token"], ["oauth2"]],
    "download_migration_archive_user": [["bearer_token"], ["oauth2"]],
    "delete_migration_archive_user": [["bearer_token"], ["oauth2"]],
    "unlock_migration_repository_user": [["bearer_token"], ["oauth2"]],
    "list_migration_repositories_user": [["bearer_token"], ["oauth2"]],
    "list_organizations_authenticated": [["bearer_token"], ["oauth2"]],
    "list_packages": [["bearer_token"], ["oauth2"]],
    "get_package": [["bearer_token"], ["oauth2"]],
    "delete_package": [["bearer_token"], ["oauth2"]],
    "restore_package": [["bearer_token"], ["oauth2"]],
    "list_package_versions": [["bearer_token"], ["oauth2"]],
    "get_package_version": [["bearer_token"], ["oauth2"]],
    "delete_package_version_authenticated": [["bearer_token"], ["oauth2"]],
    "restore_package_version_for_authenticated_user": [["bearer_token"], ["oauth2"]],
    "list_public_emails": [["bearer_token"], ["oauth2"]],
    "list_repositories": [["bearer_token"], ["oauth2"]],
    "create_repository": [["bearer_token"], ["oauth2"]],
    "list_repository_invitations_for_user": [["bearer_token"], ["oauth2"]],
    "accept_repository_invitation": [["bearer_token"], ["oauth2"]],
    "decline_repository_invitation": [["bearer_token"], ["oauth2"]],
    "list_social_accounts": [["bearer_token"], ["oauth2"]],
    "add_social_accounts": [["bearer_token"], ["oauth2"]],
    "delete_social_accounts": [["bearer_token"], ["oauth2"]],
    "list_starred_repositories": [["bearer_token"], ["oauth2"]],
    "check_repository_starred": [["bearer_token"], ["oauth2"]],
    "star_repository": [["bearer_token"], ["oauth2"]],
    "unstar_repository": [["bearer_token"], ["oauth2"]],
    "list_watched_repositories": [["bearer_token"], ["oauth2"]],
    "list_teams_authenticated": [["bearer_token"], ["oauth2"]],
    "get_user": [["bearer_token"], ["oauth2"]],
    "list_users": [["bearer_token"], ["oauth2"]],
    "get_user_by_username": [["bearer_token"], ["oauth2"]],
    "list_attestations_by_digests_user": [["bearer_token"], ["oauth2"]],
    "delete_attestations_user": [["bearer_token"], ["oauth2"]],
    "delete_attestation_by_subject_digest_user": [["bearer_token"], ["oauth2"]],
    "delete_attestation_user": [["bearer_token"], ["oauth2"]],
    "list_attestations_user": [["bearer_token"], ["oauth2"]],
    "list_user_events": [["bearer_token"], ["oauth2"]],
    "list_organization_events_for_user": [["bearer_token"], ["oauth2"]],
    "list_user_public_events": [["bearer_token"], ["oauth2"]],
    "list_followers_by_username": [["bearer_token"], ["oauth2"]],
    "list_following": [["bearer_token"], ["oauth2"]],
    "check_user_following": [["bearer_token"], ["oauth2"]],
    "list_user_gists": [["bearer_token"], ["oauth2"]],
    "list_gpg_keys_by_username": [["bearer_token"], ["oauth2"]],
    "get_user_hovercard": [["bearer_token"], ["oauth2"]],
    "get_user_installation": [["bearer_token"], ["oauth2"]],
    "list_public_keys": [["bearer_token"], ["oauth2"]],
    "list_user_organizations": [["bearer_token"], ["oauth2"]],
    "list_user_packages": [["bearer_token"], ["oauth2"]],
    "get_package_public": [["bearer_token"], ["oauth2"]],
    "delete_user_package": [["bearer_token"], ["oauth2"]],
    "restore_package_for_user": [["bearer_token"], ["oauth2"]],
    "list_package_versions_public": [["bearer_token"], ["oauth2"]],
    "get_package_version_public": [["bearer_token"], ["oauth2"]],
    "delete_package_version_user": [["bearer_token"], ["oauth2"]],
    "restore_package_version_for_user": [["bearer_token"], ["oauth2"]],
    "list_user_projects": [["bearer_token"], ["oauth2"]],
    "get_user_project": [["bearer_token"], ["oauth2"]],
    "list_project_fields_user": [["bearer_token"], ["oauth2"]],
    "get_project_field_user": [["bearer_token"], ["oauth2"]],
    "list_project_items_user": [["bearer_token"], ["oauth2"]],
    "add_item_to_project_user": [["bearer_token"], ["oauth2"]],
    "get_project_item_user": [["bearer_token"], ["oauth2"]],
    "update_project_item_user": [["bearer_token"], ["oauth2"]],
    "delete_project_item_user": [["bearer_token"], ["oauth2"]],
    "list_received_events": [["bearer_token"], ["oauth2"]],
    "list_user_public_received_events": [["bearer_token"], ["oauth2"]],
    "list_user_repositories": [["bearer_token"], ["oauth2"]],
    "get_billing_usage_report": [["bearer_token"], ["oauth2"]],
    "list_social_accounts_public": [["bearer_token"], ["oauth2"]],
    "list_ssh_signing_keys_for_user": [["bearer_token"], ["oauth2"]],
    "list_starred_repositories_by_user": [["bearer_token"], ["oauth2"]],
    "list_watched_repositories_by_user": [["bearer_token"], ["oauth2"]],
    "list_versions": [["bearer_token"], ["oauth2"]],
    "get_zen": [["bearer_token"], ["oauth2"]],
    "add_issue_field_values": [["bearer_token"], ["oauth2"]],
    "add_oidc_custom_property": [["bearer_token"], ["oauth2"]],
    "add_oidc_custom_property_org": [["bearer_token"], ["oauth2"]],
    "add_project_field": [["bearer_token"], ["oauth2"]],
    "add_project_field_user": [["bearer_token"], ["oauth2"]],
    "add_ssh_signing_key": [["bearer_token"], ["oauth2"]],
    "assign_team_to_organization": [["bearer_token"], ["oauth2"]],
    "assign_team_to_organizations": [["bearer_token"], ["oauth2"]],
    "configure_actions_cache_retention": [["bearer_token"], ["oauth2"]],
    "configure_actions_cache_storage_limit": [["bearer_token"], ["oauth2"]],
    "configure_copilot_coding_agent_permissions": [["bearer_token"], ["oauth2"]],
    "configure_copilot_content_exclusion": [["bearer_token"], ["oauth2"]],
    "configure_immutable_releases": [["bearer_token"], ["oauth2"]],
    "create_draft_item": [["bearer_token"], ["oauth2"]],
    "create_draft_item_user": [["bearer_token"], ["oauth2"]],
    "create_issue_field": [["bearer_token"], ["oauth2"]],
    "create_project_view": [["bearer_token"], ["oauth2"]],
    "create_project_view_user": [["bearer_token"], ["oauth2"]],
    "delete_budget": [["bearer_token"], ["oauth2"]],
    "delete_custom_image_version": [["bearer_token"], ["oauth2"]],
    "delete_custom_runner_image": [["bearer_token"], ["oauth2"]],
    "delete_issue_field": [["bearer_token"], ["oauth2"]],
    "delete_issue_field_value": [["bearer_token"], ["oauth2"]],
    "delete_ssh_signing_key": [["bearer_token"], ["oauth2"]],
    "disable_copilot_coding_agent_for_repository": [["bearer_token"], ["oauth2"]],
    "disable_immutable_releases": [["bearer_token"], ["oauth2"]],
    "enable_copilot_coding_agent_for_repository": [["bearer_token"], ["oauth2"]],
    "enable_immutable_releases": [["bearer_token"], ["oauth2"]],
    "enable_repository_immutable_releases": [["bearer_token"], ["oauth2"]],
    "get_actions_cache_retention_limit": [["bearer_token"], ["oauth2"]],
    "get_actions_cache_storage_limit": [["bearer_token"], ["oauth2"]],
    "get_actions_cache_storage_limit_repository": [["bearer_token"], ["oauth2"]],
    "get_billing_usage_summary": [["bearer_token"], ["oauth2"]],
    "get_billing_usage_summary_user": [["bearer_token"], ["oauth2"]],
    "get_budget": [["bearer_token"], ["oauth2"]],
    "get_cache_retention_limit": [["bearer_token"], ["oauth2"]],
    "get_custom_runner_image": [["bearer_token"], ["oauth2"]],
    "get_custom_runner_image_version": [["bearer_token"], ["oauth2"]],
    "get_enterprise_actions_cache_retention_limit": [["bearer_token"], ["oauth2"]],
    "get_enterprise_actions_cache_storage_limit": [["bearer_token"], ["oauth2"]],
    "get_immutable_releases": [["bearer_token"], ["oauth2"]],
    "get_immutable_releases_settings": [["bearer_token"], ["oauth2"]],
    "get_premium_request_usage_report": [["bearer_token"], ["oauth2"]],
    "get_premium_request_usage_report_user": [["bearer_token"], ["oauth2"]],
    "get_security_advisory": [["bearer_token"], ["oauth2"]],
    "get_ssh_signing_key": [["bearer_token"], ["oauth2"]],
    "list_artifact_deployment_records": [["bearer_token"], ["oauth2"]],
    "list_attestation_repositories": [["bearer_token"], ["oauth2"]],
    "list_copilot_coding_agent_permissions": [["bearer_token"], ["oauth2"]],
    "list_copilot_coding_agent_repositories": [["bearer_token"], ["oauth2"]],
    "list_copilot_content_exclusions": [["bearer_token"], ["oauth2"]],
    "list_custom_image_versions": [["bearer_token"], ["oauth2"]],
    "list_custom_runner_images": [["bearer_token"], ["oauth2"]],
    "list_docker_migration_conflicts_for_authenticated_user": [["bearer_token"], ["oauth2"]],
    "list_docker_migration_conflicts_for_user": [["bearer_token"], ["oauth2"]],
    "list_immutable_release_repositories": [["bearer_token"], ["oauth2"]],
    "list_issue_field_values": [["bearer_token"], ["oauth2"]],
    "list_issue_fields": [["bearer_token"], ["oauth2"]],
    "list_oidc_custom_property_inclusions": [["bearer_token"], ["oauth2"]],
    "list_oidc_custom_property_inclusions_for_org": [["bearer_token"], ["oauth2"]],
    "list_organization_assignments": [["bearer_token"], ["oauth2"]],
    "list_organization_budgets": [["bearer_token"], ["oauth2"]],
    "list_project_view_items": [["bearer_token"], ["oauth2"]],
    "list_project_view_items_user": [["bearer_token"], ["oauth2"]],
    "list_ssh_signing_keys": [["bearer_token"], ["oauth2"]],
    "pin_issue_comment": [["bearer_token"], ["oauth2"]],
    "record_artifact_deployment": [["bearer_token"], ["oauth2"]],
    "record_cluster_deployments": [["bearer_token"], ["oauth2"]],
    "remove_oidc_custom_property": [["bearer_token"], ["oauth2"]],
    "remove_oidc_custom_property_for_org": [["bearer_token"], ["oauth2"]],
    "remove_repository_from_immutable_releases": [["bearer_token"], ["oauth2"]],
    "set_actions_cache_retention_limit": [["bearer_token"], ["oauth2"]],
    "set_actions_cache_retention_limit_for_organization": [["bearer_token"], ["oauth2"]],
    "set_actions_cache_storage_limit": [["bearer_token"], ["oauth2"]],
    "set_actions_cache_storage_limit_for_repository": [["bearer_token"], ["oauth2"]],
    "set_immutable_releases_repositories": [["bearer_token"], ["oauth2"]],
    "set_issue_field_values": [["bearer_token"], ["oauth2"]],
    "unassign_team_from_organization": [["bearer_token"], ["oauth2"]],
    "unassign_team_from_organizations": [["bearer_token"], ["oauth2"]],
    "unpin_issue_comment": [["bearer_token"], ["oauth2"]],
    "update_budget": [["bearer_token"], ["oauth2"]],
    "update_copilot_coding_agent_repositories": [["bearer_token"], ["oauth2"]],
    "update_issue_field": [["bearer_token"], ["oauth2"]],
    "verify_team_organization_assignment": [["bearer_token"], ["oauth2"]]
}

"""
Authentication module for GitHub MCP server.

Generated: 2026-05-11 19:50:43 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)

This module contains:
1. Authentication class implementations (OAuth2)
2. Operation-to-auth requirements mapping (OPERATION_AUTH_MAP)
"""

from __future__ import annotations

import asyncio
import base64
import collections
import hashlib
import json
import logging
import os
import re
import ssl
import time
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

from authlib.common.security import generate_token
from authlib.integrations.httpx_client import OAuth2Client

logger = logging.getLogger(__name__)

__all__ = [
    "OAuth2Auth",
    "BearerTokenAuth",
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

    NOTE: Access tokens are obtained automatically through OAuth2 flow.
    By default they are sent as "Authorization: Bearer <token>", but some
    providers use a custom header instead.

    Configuration (environment variables):
        - OAUTH2_CLIENT_ID: OAuth2 client ID (required)
        - OAUTH2_CLIENT_SECRET: OAuth2 client secret (required)
        - OAUTH2_SCOPES: Comma-separated scopes (required)

    Redirect URI:
        - Default: http://localhost:<OAUTH2_CALLBACK_PORT>/callback
        - Configured via OAUTH2_CALLBACK_PORT in .env (default: 9400)        - Must match redirect URI in your OAuth application configuration
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
    """

    def __init__(self):
        """Initialize OAuth2 authentication with authlib."""
        # Store flow type for lifecycle management
        self.flow_type = "authorizationCode"

        # Load configuration from environment
        self.client_id = os.getenv("OAUTH2_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("OAUTH2_CLIENT_SECRET", "").strip()
        self.access_token_header_name = "Authorization"
        self.access_token_header_prefix = "Bearer" if self.access_token_header_name == "Authorization" else None

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
        self.extra_scope_params = {}
        # Redirect URI for authorization flows
        self.callback_port = int(os.getenv("OAUTH2_CALLBACK_PORT", "9400"))
        self.tls_cert_file = ""
        self.tls_key_file = ""
        self.redirect_uri = self._build_callback_redirect_uri()

        # OAuth2 token URL (required for all flows that fetch tokens)
        self.token_url = self._resolve_url_template("https://github.com/login/oauth/access_token")
        self.auth_url = self._resolve_url_template("https://github.com/login/oauth/authorize")
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

    def _resolve_url_template(self, url: str | None) -> str:
        """Resolve {server_var} placeholders from SERVER_* environment variables."""
        if not url or "{" not in url:
            return url or ""
        replacements: dict[str, str] = {}
        for var_name in re.findall(r"\{([^}]+)\}", url):
            env_var = "SERVER_" + re.sub(r"[^A-Za-z0-9_]", "_", var_name).upper()
            raw_value = os.getenv(env_var, "").strip()
            replacements[var_name] = self._resolve_template_host_value(url, var_name, env_var, raw_value)
        return url.format_map(collections.defaultdict(str, replacements))

    def _resolve_template_host_value(
        self,
        url: str,
        var_name: str,
        env_var: str,
        raw_value: str,
    ) -> str:
        """Normalize and validate env values used inside the URL host."""
        parsed_template = urlparse(url)
        template_host = parsed_template.hostname or parsed_template.netloc or ""
        token = "{" + var_name + "}"
        if not raw_value:
            if token in template_host:
                logger.warning(
                    "%s is blank; OAuth URL template %r still requires placeholder %s. "
                    "Authorization may fail until this server variable is configured.",
                    env_var,
                    url,
                    var_name,
                )
            return ""
        if token not in template_host:
            return raw_value

        prefix, _, suffix = template_host.partition(token)
        parsed_value = urlparse(raw_value)
        host = parsed_value.hostname or raw_value

        if host:
            host_matches = (not prefix or host.startswith(prefix)) and (not suffix or host.endswith(suffix))
            if host_matches:
                start = len(prefix)
                end = len(host) - len(suffix) if suffix else len(host)
                extracted = host[start:end].strip(".")
                if extracted:
                    return extracted

        looks_like_urlish_value = bool(
            parsed_value.scheme
            or parsed_value.netloc
            or parsed_value.path.strip("/") != raw_value.strip("/")
            or "/" in raw_value
            or "." in raw_value
        )
        if looks_like_urlish_value:
            raise ValueError(
                f"{env_var} must contain only the value for '{var_name}' in {url!r}, "
                f"not {raw_value!r}."
            )
        return raw_value

    def _build_callback_redirect_uri(self, port: int | None = None) -> str:
        """Build the local callback redirect URI."""
        default_scheme = "https" if False else "http"
        callback_port = port or self.callback_port
        default_port = 443 if default_scheme == "https" else 80
        netloc = "localhost" if callback_port == default_port else f"localhost:{callback_port}"
        return f"{default_scheme}://{netloc}/callback"

    def _build_callback_ssl_context(self, redirect_uri: str) -> ssl.SSLContext | None:
        """Create TLS context for HTTPS localhost callbacks when configured."""
        parsed = urlparse(redirect_uri)
        if parsed.scheme != "https":
            return None
        if not self.tls_cert_file:
            raise ValueError(
                "HTTPS OAuth2 redirect URI requires a TLS certificate file."
            )

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            if self.tls_key_file:
                context.load_cert_chain(self.tls_cert_file, self.tls_key_file)
            else:
                context.load_cert_chain(self.tls_cert_file)
        except OSError as exc:
            raise ValueError(
                f"Failed to load OAuth2 callback TLS certificate for {redirect_uri}: {exc}"
            ) from exc
        return context

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

        redirect_template = self._build_callback_redirect_uri()
        parsed_redirect = urlparse(redirect_template)
        callback_host = parsed_redirect.hostname or "localhost"
        callback_path = parsed_redirect.path or "/callback"
        callback_ssl = self._build_callback_ssl_context(redirect_template)
        base_port = port or parsed_redirect.port or self.callback_port

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

                if parsed.path == callback_path and ("code" in params or "error" in params):
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
                    _handle_connection,
                    callback_host,
                    base_port + attempt,
                    ssl=callback_ssl,
                )
                bound_port = base_port + attempt
                break
            except OSError as exc:
                if exc.errno != errno.EADDRINUSE or attempt == 4:
                    raise
        if server is None:
            raise OSError(f"Could not bind to any port in range {base_port}–{base_port + 4}")

        redirect_uri = self._build_callback_redirect_uri(port=bound_port)

        auth_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.scopes),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        for _param_name, _scopes in self.extra_scope_params.items():
            if _scopes:
                auth_params[_param_name] = " ".join(_scopes)
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
            Dict with authentication header for the provider
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

        access_token = self.token["access_token"]
        if self.access_token_header_prefix:
            return {
                self.access_token_header_name: (
                    f"{self.access_token_header_prefix} {access_token}"
                )
            }
        return {self.access_token_header_name: access_token}

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


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "list_advisories": [["OAuth2"], ["PersonalAccessToken"]],
    "get_authenticated_app": [["OAuth2"], ["PersonalAccessToken"]],
    "get_webhook_config": [["OAuth2"], ["PersonalAccessToken"]],
    "list_webhook_deliveries_app": [["OAuth2"], ["PersonalAccessToken"]],
    "get_webhook_delivery_app": [["OAuth2"], ["PersonalAccessToken"]],
    "redeliver_webhook_delivery_app": [["OAuth2"], ["PersonalAccessToken"]],
    "list_installation_requests": [["OAuth2"], ["PersonalAccessToken"]],
    "list_app_installations": [["OAuth2"], ["PersonalAccessToken"]],
    "get_app_installation": [["OAuth2"], ["PersonalAccessToken"]],
    "uninstall_app": [["OAuth2"], ["PersonalAccessToken"]],
    "suspend_app_installation": [["OAuth2"], ["PersonalAccessToken"]],
    "unsuspend_app_installation": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_app_authorization": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_application_token": [["OAuth2"], ["PersonalAccessToken"]],
    "create_scoped_token": [["OAuth2"], ["PersonalAccessToken"]],
    "get_assignment": [["OAuth2"], ["PersonalAccessToken"]],
    "list_accepted_assignments": [["OAuth2"], ["PersonalAccessToken"]],
    "list_assignment_grades": [["OAuth2"], ["PersonalAccessToken"]],
    "list_classrooms": [["OAuth2"], ["PersonalAccessToken"]],
    "get_classroom": [["OAuth2"], ["PersonalAccessToken"]],
    "list_assignments": [["OAuth2"], ["PersonalAccessToken"]],
    "list_codes_of_conduct": [["OAuth2"], ["PersonalAccessToken"]],
    "get_conduct_code": [["OAuth2"], ["PersonalAccessToken"]],
    "list_code_security_configurations": [["OAuth2"], ["PersonalAccessToken"]],
    "list_enterprise_code_security_default_configurations": [["OAuth2"], ["PersonalAccessToken"]],
    "get_code_security_configuration_enterprise": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_code_security_configuration_enterprise": [["OAuth2"], ["PersonalAccessToken"]],
    "attach_code_security_configuration": [["OAuth2"], ["PersonalAccessToken"]],
    "list_code_security_configuration_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "list_dependabot_alerts": [["OAuth2"], ["PersonalAccessToken"]],
    "list_teams_enterprise": [["OAuth2"], ["PersonalAccessToken"]],
    "create_enterprise_team": [["OAuth2"], ["PersonalAccessToken"]],
    "list_enterprise_team_members": [["OAuth2"], ["PersonalAccessToken"]],
    "add_team_members": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_team_members": [["OAuth2"], ["PersonalAccessToken"]],
    "check_enterprise_team_membership": [["OAuth2"], ["PersonalAccessToken"]],
    "add_team_member": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_team_member": [["OAuth2"], ["PersonalAccessToken"]],
    "get_enterprise_team": [["OAuth2"], ["PersonalAccessToken"]],
    "update_enterprise_team": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_enterprise_team": [["OAuth2"], ["PersonalAccessToken"]],
    "list_events": [["OAuth2"], ["PersonalAccessToken"]],
    "list_feeds": [["OAuth2"], ["PersonalAccessToken"]],
    "list_gists": [["OAuth2"], ["PersonalAccessToken"]],
    "create_gist": [["OAuth2"], ["PersonalAccessToken"]],
    "list_public_gists": [["OAuth2"], ["PersonalAccessToken"]],
    "list_starred_gists": [["OAuth2"], ["PersonalAccessToken"]],
    "get_gist": [["OAuth2"], ["PersonalAccessToken"]],
    "update_gist": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_gist": [["OAuth2"], ["PersonalAccessToken"]],
    "list_gist_comments": [["OAuth2"], ["PersonalAccessToken"]],
    "create_gist_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "get_gist_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "update_gist_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_gist_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "list_gist_commits": [["OAuth2"], ["PersonalAccessToken"]],
    "list_gist_forks": [["OAuth2"], ["PersonalAccessToken"]],
    "fork_gist": [["OAuth2"], ["PersonalAccessToken"]],
    "check_gist_starred": [["OAuth2"], ["PersonalAccessToken"]],
    "star_gist": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_gist_star": [["OAuth2"], ["PersonalAccessToken"]],
    "get_gist_revision": [["OAuth2"], ["PersonalAccessToken"]],
    "list_gitignore_templates": [["OAuth2"], ["PersonalAccessToken"]],
    "get_gitignore_template": [["OAuth2"], ["PersonalAccessToken"]],
    "list_installation_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "list_issues": [["OAuth2"], ["PersonalAccessToken"]],
    "list_licenses": [["OAuth2"], ["PersonalAccessToken"]],
    "get_license": [["OAuth2"], ["PersonalAccessToken"]],
    "get_subscription_plan": [["OAuth2"], ["PersonalAccessToken"]],
    "list_marketplace_plans": [["OAuth2"], ["PersonalAccessToken"]],
    "get_subscription_plan_stubbed": [["OAuth2"], ["PersonalAccessToken"]],
    "list_marketplace_plans_stubbed": [["OAuth2"], ["PersonalAccessToken"]],
    "list_network_events": [["OAuth2"], ["PersonalAccessToken"]],
    "list_notifications": [["OAuth2"], ["PersonalAccessToken"]],
    "mark_notifications_as_read": [["OAuth2"], ["PersonalAccessToken"]],
    "get_notification_thread": [["OAuth2"], ["PersonalAccessToken"]],
    "mark_notification_thread_as_read": [["OAuth2"], ["PersonalAccessToken"]],
    "mark_notification_thread_as_done": [["OAuth2"], ["PersonalAccessToken"]],
    "get_thread_subscription": [["OAuth2"], ["PersonalAccessToken"]],
    "configure_thread_notification": [["OAuth2"], ["PersonalAccessToken"]],
    "mute_thread_subscription": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organizations": [["OAuth2"], ["PersonalAccessToken"]],
    "list_dependabot_repository_access": [["OAuth2"], ["PersonalAccessToken"]],
    "update_dependabot_repository_access": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_billing_usage": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "update_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "get_actions_cache_usage_for_org": [["OAuth2"], ["PersonalAccessToken"]],
    "list_actions_cache_usage_by_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "list_hosted_runners": [["OAuth2"], ["PersonalAccessToken"]],
    "create_hosted_runner": [["OAuth2"], ["PersonalAccessToken"]],
    "list_github_owned_runner_images": [["OAuth2"], ["PersonalAccessToken"]],
    "list_partner_runner_images": [["OAuth2"], ["PersonalAccessToken"]],
    "get_hosted_runners_limits": [["OAuth2"], ["PersonalAccessToken"]],
    "list_hosted_runner_machine_specs": [["OAuth2"], ["PersonalAccessToken"]],
    "list_hosted_runner_platforms": [["OAuth2"], ["PersonalAccessToken"]],
    "get_hosted_runner": [["OAuth2"], ["PersonalAccessToken"]],
    "update_hosted_runner": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_hosted_runner": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_github_actions_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_self_hosted_runner_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_repository_from_self_hosted_runners": [["OAuth2"], ["PersonalAccessToken"]],
    "list_runner_groups": [["OAuth2"], ["PersonalAccessToken"]],
    "create_runner_group": [["OAuth2"], ["PersonalAccessToken"]],
    "get_runner_group": [["OAuth2"], ["PersonalAccessToken"]],
    "update_runner_group": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_runner_group": [["OAuth2"], ["PersonalAccessToken"]],
    "list_github_hosted_runners_in_group": [["OAuth2"], ["PersonalAccessToken"]],
    "list_runner_group_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "update_runner_group_repository_access": [["OAuth2"], ["PersonalAccessToken"]],
    "grant_runner_group_repository_access": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_runner_group_repository_access": [["OAuth2"], ["PersonalAccessToken"]],
    "list_runners_in_group": [["OAuth2"], ["PersonalAccessToken"]],
    "update_runner_group_runners": [["OAuth2"], ["PersonalAccessToken"]],
    "add_runner_to_group": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_runner_from_group": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_runners": [["OAuth2"], ["PersonalAccessToken"]],
    "list_runner_applications": [["OAuth2"], ["PersonalAccessToken"]],
    "generate_runner_registration_token": [["OAuth2"], ["PersonalAccessToken"]],
    "generate_runner_removal_token": [["OAuth2"], ["PersonalAccessToken"]],
    "get_runner": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_runner_from_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "list_runner_labels": [["OAuth2"], ["PersonalAccessToken"]],
    "add_labels_to_runner": [["OAuth2"], ["PersonalAccessToken"]],
    "update_runner_labels": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_all_custom_labels_from_runner": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_custom_label_from_runner": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_secrets": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_public_key": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "create_or_update_organization_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_organization_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_secret_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "update_organization_secret_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "grant_repository_access_to_organization_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_repository_from_organization_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_variables": [["OAuth2"], ["PersonalAccessToken"]],
    "create_organization_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "update_organization_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_organization_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_variable_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "update_org_variable_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "add_repository_to_org_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_repository_from_org_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "register_artifact_storage": [["OAuth2"], ["PersonalAccessToken"]],
    "list_artifact_storage_records": [["OAuth2"], ["PersonalAccessToken"]],
    "list_attestations_by_digests": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_attestations": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_attestation_by_subject_digest": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_attestation": [["OAuth2"], ["PersonalAccessToken"]],
    "list_attestations_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "list_blocked_users": [["OAuth2"], ["PersonalAccessToken"]],
    "check_blocked_user": [["OAuth2"], ["PersonalAccessToken"]],
    "unblock_user_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "list_campaigns": [["OAuth2"], ["PersonalAccessToken"]],
    "create_campaign": [["OAuth2"], ["PersonalAccessToken"]],
    "get_campaign": [["OAuth2"], ["PersonalAccessToken"]],
    "update_campaign": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_campaign": [["OAuth2"], ["PersonalAccessToken"]],
    "list_code_scanning_alerts": [["OAuth2"], ["PersonalAccessToken"]],
    "list_code_security_configurations_for_org": [["OAuth2"], ["PersonalAccessToken"]],
    "list_default_code_security_configurations": [["OAuth2"], ["PersonalAccessToken"]],
    "detach_security_configurations": [["OAuth2"], ["PersonalAccessToken"]],
    "get_code_security_configuration": [["OAuth2"], ["PersonalAccessToken"]],
    "update_code_security_configuration": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_code_security_configuration": [["OAuth2"], ["PersonalAccessToken"]],
    "attach_security_configuration": [["OAuth2"], ["PersonalAccessToken"]],
    "list_security_configuration_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_codespaces": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_secrets_codespaces": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_secret_codespace": [["OAuth2"], ["PersonalAccessToken"]],
    "create_or_update_organization_secret_codespaces": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_organization_secret_codespace": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_secret_repositories_codespaces": [["OAuth2"], ["PersonalAccessToken"]],
    "update_organization_secret_repositories_codespaces": [["OAuth2"], ["PersonalAccessToken"]],
    "add_repository_to_organization_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_repository_from_organization_secret_codespaces": [["OAuth2"], ["PersonalAccessToken"]],
    "get_copilot_billing": [["OAuth2"], ["PersonalAccessToken"]],
    "list_copilot_seats": [["OAuth2"], ["PersonalAccessToken"]],
    "grant_copilot_seats_to_teams": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_copilot_access_from_teams": [["OAuth2"], ["PersonalAccessToken"]],
    "grant_copilot_seats_to_users": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_copilot_seat_assignments": [["OAuth2"], ["PersonalAccessToken"]],
    "get_copilot_metrics": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_dependabot_alerts": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_secrets_dependabot": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_dependabot_public_key": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_secret_dependabot": [["OAuth2"], ["PersonalAccessToken"]],
    "create_or_update_organization_secret_dependabot": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_organization_secret_dependabot": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_secret_repositories_dependabot": [["OAuth2"], ["PersonalAccessToken"]],
    "update_organization_secret_repositories_dependabot": [["OAuth2"], ["PersonalAccessToken"]],
    "add_repository_to_organization_secret_dependabot": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_repository_from_organization_secret_dependabot": [["OAuth2"], ["PersonalAccessToken"]],
    "list_docker_migration_conflicts": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_events": [["OAuth2"], ["PersonalAccessToken"]],
    "list_failed_invitations": [["OAuth2"], ["PersonalAccessToken"]],
    "list_webhooks": [["OAuth2"], ["PersonalAccessToken"]],
    "create_webhook": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_webhook": [["OAuth2"], ["PersonalAccessToken"]],
    "update_webhook": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_webhook": [["OAuth2"], ["PersonalAccessToken"]],
    "get_webhook_config_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "update_webhook_config": [["OAuth2"], ["PersonalAccessToken"]],
    "list_webhook_deliveries_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "get_webhook_delivery_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "redeliver_webhook_delivery_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "list_api_request_stats": [["OAuth2"], ["PersonalAccessToken"]],
    "get_api_summary_stats": [["OAuth2"], ["PersonalAccessToken"]],
    "get_api_stats_by_actor": [["OAuth2"], ["PersonalAccessToken"]],
    "get_api_request_stats": [["OAuth2"], ["PersonalAccessToken"]],
    "get_user_api_time_stats": [["OAuth2"], ["PersonalAccessToken"]],
    "get_api_request_stats_by_actor": [["OAuth2"], ["PersonalAccessToken"]],
    "get_user_api_stats_by_access_type": [["OAuth2"], ["PersonalAccessToken"]],
    "get_app_organization_installation": [["OAuth2"], ["PersonalAccessToken"]],
    "list_app_installations_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_interaction_restrictions": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pending_invitations": [["OAuth2"], ["PersonalAccessToken"]],
    "invite_organization_member": [["OAuth2"], ["PersonalAccessToken"]],
    "cancel_invitation": [["OAuth2"], ["PersonalAccessToken"]],
    "list_invitation_teams": [["OAuth2"], ["PersonalAccessToken"]],
    "list_issue_types": [["OAuth2"], ["PersonalAccessToken"]],
    "create_issue_type": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_issue_type": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_issues": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_members": [["OAuth2"], ["PersonalAccessToken"]],
    "check_organization_membership": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_member_codespaces": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_codespace_from_organization": [["OAuth2"], ["PersonalAccessToken"]],
    "stop_codespace": [["OAuth2"], ["PersonalAccessToken"]],
    "get_copilot_seat_details": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_membership": [["OAuth2"], ["PersonalAccessToken"]],
    "set_organization_membership": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_organization_membership": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_migrations": [["OAuth2"], ["PersonalAccessToken"]],
    "get_migration_status": [["OAuth2"], ["PersonalAccessToken"]],
    "download_migration_archive": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_migration_archive": [["OAuth2"], ["PersonalAccessToken"]],
    "unlock_migration_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "list_migration_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_roles": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_team_organization_roles": [["OAuth2"], ["PersonalAccessToken"]],
    "assign_organization_role_to_team": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_organization_role_from_team": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_all_organization_roles_from_user": [["OAuth2"], ["PersonalAccessToken"]],
    "assign_organization_role_to_user": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_organization_role_from_user": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_role": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_role_teams": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_role_users": [["OAuth2"], ["PersonalAccessToken"]],
    "list_outside_collaborators": [["OAuth2"], ["PersonalAccessToken"]],
    "convert_member_to_outside_collaborator": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_outside_collaborator": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_packages": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_package": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_organization_package": [["OAuth2"], ["PersonalAccessToken"]],
    "restore_organization_package": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_package_versions": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_package_version": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_package_version": [["OAuth2"], ["PersonalAccessToken"]],
    "restore_package_version": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pat_grant_requests": [["OAuth2"], ["PersonalAccessToken"]],
    "review_pat_grant_requests": [["OAuth2"], ["PersonalAccessToken"]],
    "review_pat_grant_request": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pat_request_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_pat_grants": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_organization_pat_access": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_org_pat_access": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pat_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_private_registries": [["OAuth2"], ["PersonalAccessToken"]],
    "create_organization_private_registry": [["OAuth2"], ["PersonalAccessToken"]],
    "get_private_registry_public_key": [["OAuth2"], ["PersonalAccessToken"]],
    "get_private_registry": [["OAuth2"], ["PersonalAccessToken"]],
    "update_organization_private_registry": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_org_private_registry": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_projects": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_project": [["OAuth2"], ["PersonalAccessToken"]],
    "list_project_fields": [["OAuth2"], ["PersonalAccessToken"]],
    "get_project_field": [["OAuth2"], ["PersonalAccessToken"]],
    "list_project_items": [["OAuth2"], ["PersonalAccessToken"]],
    "add_item_to_project": [["OAuth2"], ["PersonalAccessToken"]],
    "get_project_item": [["OAuth2"], ["PersonalAccessToken"]],
    "update_project_item": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_project_item": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_custom_property_definitions": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_custom_property": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_repository_custom_properties": [["OAuth2"], ["PersonalAccessToken"]],
    "batch_update_repository_custom_properties": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_public_members": [["OAuth2"], ["PersonalAccessToken"]],
    "check_public_organization_membership": [["OAuth2"], ["PersonalAccessToken"]],
    "publicize_organization_membership": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_public_organization_membership": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "create_organization_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_rulesets": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_rule_suites": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_rule_suite": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_ruleset": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_organization_ruleset": [["OAuth2"], ["PersonalAccessToken"]],
    "list_ruleset_history": [["OAuth2"], ["PersonalAccessToken"]],
    "get_ruleset_version": [["OAuth2"], ["PersonalAccessToken"]],
    "list_secret_scanning_alerts": [["OAuth2"], ["PersonalAccessToken"]],
    "list_secret_scanning_patterns": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_security_advisories": [["OAuth2"], ["PersonalAccessToken"]],
    "list_network_configurations": [["OAuth2"], ["PersonalAccessToken"]],
    "get_network_configuration": [["OAuth2"], ["PersonalAccessToken"]],
    "update_network_configuration": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_network_configuration": [["OAuth2"], ["PersonalAccessToken"]],
    "get_network_settings": [["OAuth2"], ["PersonalAccessToken"]],
    "get_team_copilot_metrics": [["OAuth2"], ["PersonalAccessToken"]],
    "list_teams": [["OAuth2"], ["PersonalAccessToken"]],
    "create_team": [["OAuth2"], ["PersonalAccessToken"]],
    "get_team": [["OAuth2"], ["PersonalAccessToken"]],
    "update_team": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_team": [["OAuth2"], ["PersonalAccessToken"]],
    "list_team_invitations": [["OAuth2"], ["PersonalAccessToken"]],
    "list_team_members": [["OAuth2"], ["PersonalAccessToken"]],
    "get_team_membership": [["OAuth2"], ["PersonalAccessToken"]],
    "add_or_update_team_membership": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_team_member_org": [["OAuth2"], ["PersonalAccessToken"]],
    "list_team_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "verify_team_repository_permissions": [["OAuth2"], ["PersonalAccessToken"]],
    "set_team_repository_permission": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_repository_from_team": [["OAuth2"], ["PersonalAccessToken"]],
    "list_child_teams": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "update_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "list_artifacts": [["OAuth2"], ["PersonalAccessToken"]],
    "get_artifact": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_artifact": [["OAuth2"], ["PersonalAccessToken"]],
    "download_artifact": [["OAuth2"], ["PersonalAccessToken"]],
    "get_actions_cache_usage": [["OAuth2"], ["PersonalAccessToken"]],
    "list_caches": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_actions_cache_by_key": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_actions_cache": [["OAuth2"], ["PersonalAccessToken"]],
    "get_workflow_job": [["OAuth2"], ["PersonalAccessToken"]],
    "get_workflow_job_logs": [["OAuth2"], ["PersonalAccessToken"]],
    "rerun_workflow_job": [["OAuth2"], ["PersonalAccessToken"]],
    "get_oidc_subject_claim_customization": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_secrets_available_to_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_variables_shared": [["OAuth2"], ["PersonalAccessToken"]],
    "list_runners": [["OAuth2"], ["PersonalAccessToken"]],
    "list_runner_downloads": [["OAuth2"], ["PersonalAccessToken"]],
    "generate_runner_removal_token_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "get_runner_repo": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_runner_from_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "list_runner_labels_for_repo": [["OAuth2"], ["PersonalAccessToken"]],
    "add_labels_to_runner_for_repo": [["OAuth2"], ["PersonalAccessToken"]],
    "update_runner_labels_repo": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_all_custom_labels_from_runner_for_repo": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_runner_label": [["OAuth2"], ["PersonalAccessToken"]],
    "list_workflow_runs": [["OAuth2"], ["PersonalAccessToken"]],
    "get_workflow_run": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_workflow_run": [["OAuth2"], ["PersonalAccessToken"]],
    "list_workflow_run_approvals": [["OAuth2"], ["PersonalAccessToken"]],
    "approve_workflow_run": [["OAuth2"], ["PersonalAccessToken"]],
    "list_workflow_run_artifacts": [["OAuth2"], ["PersonalAccessToken"]],
    "get_workflow_run_attempt": [["OAuth2"], ["PersonalAccessToken"]],
    "list_workflow_run_attempt_jobs": [["OAuth2"], ["PersonalAccessToken"]],
    "download_workflow_run_attempt_logs": [["OAuth2"], ["PersonalAccessToken"]],
    "cancel_workflow_run": [["OAuth2"], ["PersonalAccessToken"]],
    "review_deployment_protection_rule": [["OAuth2"], ["PersonalAccessToken"]],
    "force_cancel_workflow_run": [["OAuth2"], ["PersonalAccessToken"]],
    "list_workflow_run_jobs": [["OAuth2"], ["PersonalAccessToken"]],
    "get_workflow_run_logs_download_url": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_workflow_run_logs": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pending_deployments": [["OAuth2"], ["PersonalAccessToken"]],
    "review_pending_deployments": [["OAuth2"], ["PersonalAccessToken"]],
    "rerun_workflow": [["OAuth2"], ["PersonalAccessToken"]],
    "rerun_workflow_failed_jobs": [["OAuth2"], ["PersonalAccessToken"]],
    "get_workflow_run_usage": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_secrets": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_public_key": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_repository_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_variables": [["OAuth2"], ["PersonalAccessToken"]],
    "create_repository_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "update_repository_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_repository_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "list_workflows": [["OAuth2"], ["PersonalAccessToken"]],
    "get_workflow": [["OAuth2"], ["PersonalAccessToken"]],
    "disable_workflow": [["OAuth2"], ["PersonalAccessToken"]],
    "trigger_workflow": [["OAuth2"], ["PersonalAccessToken"]],
    "enable_workflow": [["OAuth2"], ["PersonalAccessToken"]],
    "list_workflow_runs_for_workflow": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_activities": [["OAuth2"], ["PersonalAccessToken"]],
    "list_assignees": [["OAuth2"], ["PersonalAccessToken"]],
    "verify_assignee_permission": [["OAuth2"], ["PersonalAccessToken"]],
    "create_attestation": [["OAuth2"], ["PersonalAccessToken"]],
    "list_attestations": [["OAuth2"], ["PersonalAccessToken"]],
    "list_autolinks": [["OAuth2"], ["PersonalAccessToken"]],
    "create_autolink": [["OAuth2"], ["PersonalAccessToken"]],
    "get_autolink": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_autolink": [["OAuth2"], ["PersonalAccessToken"]],
    "get_automated_security_fixes_status": [["OAuth2"], ["PersonalAccessToken"]],
    "enable_automated_security_fixes": [["OAuth2"], ["PersonalAccessToken"]],
    "disable_automated_security_fixes": [["OAuth2"], ["PersonalAccessToken"]],
    "list_branches": [["OAuth2"], ["PersonalAccessToken"]],
    "get_branch": [["OAuth2"], ["PersonalAccessToken"]],
    "get_branch_protection": [["OAuth2"], ["PersonalAccessToken"]],
    "configure_branch_protection": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_branch_protection": [["OAuth2"], ["PersonalAccessToken"]],
    "get_branch_admin_protection": [["OAuth2"], ["PersonalAccessToken"]],
    "enforce_admin_branch_protection": [["OAuth2"], ["PersonalAccessToken"]],
    "disable_admin_branch_protection": [["OAuth2"], ["PersonalAccessToken"]],
    "check_branch_signature_protection": [["OAuth2"], ["PersonalAccessToken"]],
    "disable_branch_signature_protection": [["OAuth2"], ["PersonalAccessToken"]],
    "get_branch_status_checks_protection": [["OAuth2"], ["PersonalAccessToken"]],
    "disable_branch_status_check_protection": [["OAuth2"], ["PersonalAccessToken"]],
    "list_status_check_contexts": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_branch_protection_status_check_contexts": [["OAuth2"], ["PersonalAccessToken"]],
    "list_branch_access_restrictions": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_branch_protection_restrictions": [["OAuth2"], ["PersonalAccessToken"]],
    "list_apps_with_protected_branch_access": [["OAuth2"], ["PersonalAccessToken"]],
    "update_branch_protection_app_restrictions": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_app_branch_push_access": [["OAuth2"], ["PersonalAccessToken"]],
    "list_teams_with_branch_access": [["OAuth2"], ["PersonalAccessToken"]],
    "grant_team_branch_push_access": [["OAuth2"], ["PersonalAccessToken"]],
    "replace_branch_protection_team_restrictions": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_team_branch_push_access": [["OAuth2"], ["PersonalAccessToken"]],
    "list_branch_protection_users": [["OAuth2"], ["PersonalAccessToken"]],
    "grant_user_push_access": [["OAuth2"], ["PersonalAccessToken"]],
    "revoke_user_branch_access": [["OAuth2"], ["PersonalAccessToken"]],
    "rename_branch": [["OAuth2"], ["PersonalAccessToken"]],
    "create_check_run": [["OAuth2"], ["PersonalAccessToken"]],
    "get_check_run": [["OAuth2"], ["PersonalAccessToken"]],
    "update_check_run": [["OAuth2"], ["PersonalAccessToken"]],
    "list_check_run_annotations": [["OAuth2"], ["PersonalAccessToken"]],
    "trigger_check_run_recheck": [["OAuth2"], ["PersonalAccessToken"]],
    "create_check_suite": [["OAuth2"], ["PersonalAccessToken"]],
    "get_check_suite": [["OAuth2"], ["PersonalAccessToken"]],
    "list_check_runs": [["OAuth2"], ["PersonalAccessToken"]],
    "rerun_check_suite": [["OAuth2"], ["PersonalAccessToken"]],
    "list_code_scanning_alerts_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "get_code_scanning_alert": [["OAuth2"], ["PersonalAccessToken"]],
    "update_code_scanning_alert": [["OAuth2"], ["PersonalAccessToken"]],
    "get_autofix_status": [["OAuth2"], ["PersonalAccessToken"]],
    "create_code_scanning_autofix": [["OAuth2"], ["PersonalAccessToken"]],
    "commit_code_scanning_autofix": [["OAuth2"], ["PersonalAccessToken"]],
    "list_code_scanning_alert_instances": [["OAuth2"], ["PersonalAccessToken"]],
    "list_code_scanning_analyses": [["OAuth2"], ["PersonalAccessToken"]],
    "get_code_scanning_analysis": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_code_scanning_analysis": [["OAuth2"], ["PersonalAccessToken"]],
    "list_codeql_databases": [["OAuth2"], ["PersonalAccessToken"]],
    "get_codeql_database": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_codeql_database": [["OAuth2"], ["PersonalAccessToken"]],
    "create_variant_analysis": [["OAuth2"], ["PersonalAccessToken"]],
    "get_variant_analysis": [["OAuth2"], ["PersonalAccessToken"]],
    "get_variant_analysis_repository_status": [["OAuth2"], ["PersonalAccessToken"]],
    "get_code_scanning_default_setup": [["OAuth2"], ["PersonalAccessToken"]],
    "upload_sarif": [["OAuth2"], ["PersonalAccessToken"]],
    "get_sarif_upload": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_code_security_configuration": [["OAuth2"], ["PersonalAccessToken"]],
    "list_codeowners_errors": [["OAuth2"], ["PersonalAccessToken"]],
    "list_codespaces_in_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "create_codespace": [["OAuth2"], ["PersonalAccessToken"]],
    "list_devcontainers": [["OAuth2"], ["PersonalAccessToken"]],
    "list_codespace_machines": [["OAuth2"], ["PersonalAccessToken"]],
    "get_codespace_defaults": [["OAuth2"], ["PersonalAccessToken"]],
    "list_codespace_secrets": [["OAuth2"], ["PersonalAccessToken"]],
    "get_codespace_public_key": [["OAuth2"], ["PersonalAccessToken"]],
    "get_codespace_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "create_or_update_codespace_secret_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_codespace_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "list_collaborators": [["OAuth2"], ["PersonalAccessToken"]],
    "verify_repository_collaborator": [["OAuth2"], ["PersonalAccessToken"]],
    "add_collaborator": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_collaborator": [["OAuth2"], ["PersonalAccessToken"]],
    "get_collaborator_permission": [["OAuth2"], ["PersonalAccessToken"]],
    "list_commit_comments": [["OAuth2"], ["PersonalAccessToken"]],
    "get_commit_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "update_commit_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_commit_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "list_commit_comment_reactions": [["OAuth2"], ["PersonalAccessToken"]],
    "add_commit_comment_reaction": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_commit_comment_reaction": [["OAuth2"], ["PersonalAccessToken"]],
    "list_commits": [["OAuth2"], ["PersonalAccessToken"]],
    "list_branches_for_commit": [["OAuth2"], ["PersonalAccessToken"]],
    "list_commit_comments_by_sha": [["OAuth2"], ["PersonalAccessToken"]],
    "create_commit_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pull_requests_for_commit": [["OAuth2"], ["PersonalAccessToken"]],
    "get_commit": [["OAuth2"], ["PersonalAccessToken"]],
    "list_check_runs_for_ref": [["OAuth2"], ["PersonalAccessToken"]],
    "list_check_suites": [["OAuth2"], ["PersonalAccessToken"]],
    "get_commit_status": [["OAuth2"], ["PersonalAccessToken"]],
    "list_commit_statuses": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_community_profile": [["OAuth2"], ["PersonalAccessToken"]],
    "compare_commits": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_content": [["OAuth2"], ["PersonalAccessToken"]],
    "create_or_update_file": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_file": [["OAuth2"], ["PersonalAccessToken"]],
    "list_contributors": [["OAuth2"], ["PersonalAccessToken"]],
    "list_dependabot_alerts_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "get_dependabot_alert": [["OAuth2"], ["PersonalAccessToken"]],
    "update_dependabot_alert": [["OAuth2"], ["PersonalAccessToken"]],
    "list_dependabot_secrets": [["OAuth2"], ["PersonalAccessToken"]],
    "get_dependabot_public_key": [["OAuth2"], ["PersonalAccessToken"]],
    "get_dependabot_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "create_or_update_dependabot_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_dependabot_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "compare_dependency_changes": [["OAuth2"], ["PersonalAccessToken"]],
    "export_sbom": [["OAuth2"], ["PersonalAccessToken"]],
    "submit_dependency_snapshot": [["OAuth2"], ["PersonalAccessToken"]],
    "list_deployments": [["OAuth2"], ["PersonalAccessToken"]],
    "create_deployment": [["OAuth2"], ["PersonalAccessToken"]],
    "get_deployment": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_deployment": [["OAuth2"], ["PersonalAccessToken"]],
    "list_deployment_statuses": [["OAuth2"], ["PersonalAccessToken"]],
    "create_deployment_status": [["OAuth2"], ["PersonalAccessToken"]],
    "get_deployment_status": [["OAuth2"], ["PersonalAccessToken"]],
    "list_environments": [["OAuth2"], ["PersonalAccessToken"]],
    "get_environment": [["OAuth2"], ["PersonalAccessToken"]],
    "configure_environment": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_environment": [["OAuth2"], ["PersonalAccessToken"]],
    "list_deployment_branch_policies": [["OAuth2"], ["PersonalAccessToken"]],
    "create_deployment_branch_policy": [["OAuth2"], ["PersonalAccessToken"]],
    "get_deployment_branch_policy": [["OAuth2"], ["PersonalAccessToken"]],
    "update_deployment_branch_policy": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_deployment_branch_policy": [["OAuth2"], ["PersonalAccessToken"]],
    "list_deployment_protection_rules": [["OAuth2"], ["PersonalAccessToken"]],
    "list_deployment_rule_integrations": [["OAuth2"], ["PersonalAccessToken"]],
    "get_deployment_protection_rule": [["OAuth2"], ["PersonalAccessToken"]],
    "disable_deployment_protection_rule": [["OAuth2"], ["PersonalAccessToken"]],
    "list_environment_secrets": [["OAuth2"], ["PersonalAccessToken"]],
    "get_environment_public_key": [["OAuth2"], ["PersonalAccessToken"]],
    "get_environment_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_environment_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "list_environment_variables": [["OAuth2"], ["PersonalAccessToken"]],
    "create_environment_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "get_environment_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "update_environment_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_environment_variable": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_events": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_forks": [["OAuth2"], ["PersonalAccessToken"]],
    "fork_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "create_blob": [["OAuth2"], ["PersonalAccessToken"]],
    "get_blob": [["OAuth2"], ["PersonalAccessToken"]],
    "create_commit": [["OAuth2"], ["PersonalAccessToken"]],
    "get_commit_object": [["OAuth2"], ["PersonalAccessToken"]],
    "list_git_refs": [["OAuth2"], ["PersonalAccessToken"]],
    "get_git_reference": [["OAuth2"], ["PersonalAccessToken"]],
    "create_git_ref": [["OAuth2"], ["PersonalAccessToken"]],
    "update_git_ref": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_git_ref": [["OAuth2"], ["PersonalAccessToken"]],
    "create_tag": [["OAuth2"], ["PersonalAccessToken"]],
    "get_tag": [["OAuth2"], ["PersonalAccessToken"]],
    "create_tree": [["OAuth2"], ["PersonalAccessToken"]],
    "fetch_tree": [["OAuth2"], ["PersonalAccessToken"]],
    "list_webhooks_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "create_webhook_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "get_webhook": [["OAuth2"], ["PersonalAccessToken"]],
    "update_webhook_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_webhook_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "get_webhook_config_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "update_webhook_config_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "list_webhook_deliveries": [["OAuth2"], ["PersonalAccessToken"]],
    "get_webhook_delivery": [["OAuth2"], ["PersonalAccessToken"]],
    "redeliver_webhook_delivery": [["OAuth2"], ["PersonalAccessToken"]],
    "trigger_webhook_ping": [["OAuth2"], ["PersonalAccessToken"]],
    "trigger_webhook_test": [["OAuth2"], ["PersonalAccessToken"]],
    "get_app_installation_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_interaction_restrictions": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_interaction_restrictions": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_invitations": [["OAuth2"], ["PersonalAccessToken"]],
    "update_repository_invitation": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_repository_invitation": [["OAuth2"], ["PersonalAccessToken"]],
    "list_issues_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "create_issue": [["OAuth2"], ["PersonalAccessToken"]],
    "list_issue_comments_for_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "get_issue_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "update_issue_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_issue_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "list_comment_reactions": [["OAuth2"], ["PersonalAccessToken"]],
    "add_issue_comment_reaction": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_issue_comment_reaction": [["OAuth2"], ["PersonalAccessToken"]],
    "list_issue_events": [["OAuth2"], ["PersonalAccessToken"]],
    "get_issue_event": [["OAuth2"], ["PersonalAccessToken"]],
    "get_issue": [["OAuth2"], ["PersonalAccessToken"]],
    "update_issue": [["OAuth2"], ["PersonalAccessToken"]],
    "assign_issue_users": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_issue_assignees": [["OAuth2"], ["PersonalAccessToken"]],
    "verify_issue_assignee": [["OAuth2"], ["PersonalAccessToken"]],
    "list_issue_comments": [["OAuth2"], ["PersonalAccessToken"]],
    "add_issue_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "list_blocking_issues": [["OAuth2"], ["PersonalAccessToken"]],
    "mark_issue_blocked_by": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_issue_blocking_dependency": [["OAuth2"], ["PersonalAccessToken"]],
    "list_blocking_dependencies": [["OAuth2"], ["PersonalAccessToken"]],
    "list_issue_events_for_issue": [["OAuth2"], ["PersonalAccessToken"]],
    "list_issue_labels": [["OAuth2"], ["PersonalAccessToken"]],
    "add_issue_labels": [["OAuth2"], ["PersonalAccessToken"]],
    "replace_issue_labels": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_all_issue_labels": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_issue_label": [["OAuth2"], ["PersonalAccessToken"]],
    "lock_issue": [["OAuth2"], ["PersonalAccessToken"]],
    "unlock_issue": [["OAuth2"], ["PersonalAccessToken"]],
    "get_parent_issue": [["OAuth2"], ["PersonalAccessToken"]],
    "list_issue_reactions": [["OAuth2"], ["PersonalAccessToken"]],
    "add_issue_reaction": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_issue_reaction": [["OAuth2"], ["PersonalAccessToken"]],
    "unlink_sub_issue": [["OAuth2"], ["PersonalAccessToken"]],
    "list_sub_issues": [["OAuth2"], ["PersonalAccessToken"]],
    "link_sub_issue": [["OAuth2"], ["PersonalAccessToken"]],
    "reorder_sub_issue": [["OAuth2"], ["PersonalAccessToken"]],
    "list_issue_timeline_events": [["OAuth2"], ["PersonalAccessToken"]],
    "list_deploy_keys": [["OAuth2"], ["PersonalAccessToken"]],
    "create_deploy_key": [["OAuth2"], ["PersonalAccessToken"]],
    "get_deploy_key": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_deploy_key": [["OAuth2"], ["PersonalAccessToken"]],
    "list_labels": [["OAuth2"], ["PersonalAccessToken"]],
    "create_label": [["OAuth2"], ["PersonalAccessToken"]],
    "get_label": [["OAuth2"], ["PersonalAccessToken"]],
    "update_label": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_label": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_languages": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_license": [["OAuth2"], ["PersonalAccessToken"]],
    "sync_fork_with_upstream": [["OAuth2"], ["PersonalAccessToken"]],
    "merge_branch": [["OAuth2"], ["PersonalAccessToken"]],
    "list_milestones": [["OAuth2"], ["PersonalAccessToken"]],
    "create_milestone": [["OAuth2"], ["PersonalAccessToken"]],
    "get_milestone": [["OAuth2"], ["PersonalAccessToken"]],
    "update_milestone": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_milestone": [["OAuth2"], ["PersonalAccessToken"]],
    "list_milestone_labels": [["OAuth2"], ["PersonalAccessToken"]],
    "list_notifications_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "mark_repository_notifications_as_read": [["OAuth2"], ["PersonalAccessToken"]],
    "get_pages_site": [["OAuth2"], ["PersonalAccessToken"]],
    "enable_pages_site": [["OAuth2"], ["PersonalAccessToken"]],
    "configure_pages_site": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_pages_site": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pages_builds": [["OAuth2"], ["PersonalAccessToken"]],
    "trigger_pages_build": [["OAuth2"], ["PersonalAccessToken"]],
    "get_latest_pages_build": [["OAuth2"], ["PersonalAccessToken"]],
    "get_pages_build": [["OAuth2"], ["PersonalAccessToken"]],
    "deploy_pages": [["OAuth2"], ["PersonalAccessToken"]],
    "get_pages_deployment": [["OAuth2"], ["PersonalAccessToken"]],
    "cancel_pages_deployment": [["OAuth2"], ["PersonalAccessToken"]],
    "check_private_vulnerability_reporting": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_custom_properties": [["OAuth2"], ["PersonalAccessToken"]],
    "set_repository_custom_properties": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pull_requests": [["OAuth2"], ["PersonalAccessToken"]],
    "create_pull_request": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pull_request_review_comments_for_repo": [["OAuth2"], ["PersonalAccessToken"]],
    "get_pull_request_review_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "update_pull_request_review_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_pull_request_review_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pull_request_review_comment_reactions": [["OAuth2"], ["PersonalAccessToken"]],
    "add_reaction_to_pull_request_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_pull_request_comment_reaction": [["OAuth2"], ["PersonalAccessToken"]],
    "get_pull_request": [["OAuth2"], ["PersonalAccessToken"]],
    "update_pull_request": [["OAuth2"], ["PersonalAccessToken"]],
    "create_codespace_from_pull_request": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pull_request_review_comments": [["OAuth2"], ["PersonalAccessToken"]],
    "create_pull_request_review_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "reply_to_review_comment": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pull_request_commits": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pull_request_files": [["OAuth2"], ["PersonalAccessToken"]],
    "check_pull_request_merged": [["OAuth2"], ["PersonalAccessToken"]],
    "merge_pull_request": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pull_request_requested_reviewers": [["OAuth2"], ["PersonalAccessToken"]],
    "request_pull_request_reviewers": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_pull_request_reviewers": [["OAuth2"], ["PersonalAccessToken"]],
    "list_pull_request_reviews": [["OAuth2"], ["PersonalAccessToken"]],
    "create_pull_request_review": [["OAuth2"], ["PersonalAccessToken"]],
    "get_pull_request_review": [["OAuth2"], ["PersonalAccessToken"]],
    "update_pull_request_review": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_pending_review": [["OAuth2"], ["PersonalAccessToken"]],
    "list_review_comments": [["OAuth2"], ["PersonalAccessToken"]],
    "dismiss_pull_request_review": [["OAuth2"], ["PersonalAccessToken"]],
    "submit_pull_request_review": [["OAuth2"], ["PersonalAccessToken"]],
    "sync_pull_request_branch": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_readme": [["OAuth2"], ["PersonalAccessToken"]],
    "get_readme": [["OAuth2"], ["PersonalAccessToken"]],
    "list_releases": [["OAuth2"], ["PersonalAccessToken"]],
    "create_release": [["OAuth2"], ["PersonalAccessToken"]],
    "download_release_asset": [["OAuth2"], ["PersonalAccessToken"]],
    "update_release_asset": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_release_asset": [["OAuth2"], ["PersonalAccessToken"]],
    "generate_release_notes": [["OAuth2"], ["PersonalAccessToken"]],
    "get_latest_release": [["OAuth2"], ["PersonalAccessToken"]],
    "get_release_by_tag": [["OAuth2"], ["PersonalAccessToken"]],
    "get_release": [["OAuth2"], ["PersonalAccessToken"]],
    "update_release": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_release": [["OAuth2"], ["PersonalAccessToken"]],
    "list_release_assets": [["OAuth2"], ["PersonalAccessToken"]],
    "upload_release_asset": [["OAuth2"], ["PersonalAccessToken"]],
    "list_release_reactions": [["OAuth2"], ["PersonalAccessToken"]],
    "add_release_reaction": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_release_reaction": [["OAuth2"], ["PersonalAccessToken"]],
    "list_branch_rules": [["OAuth2"], ["PersonalAccessToken"]],
    "list_rule_suites": [["OAuth2"], ["PersonalAccessToken"]],
    "get_rule_suite": [["OAuth2"], ["PersonalAccessToken"]],
    "get_ruleset": [["OAuth2"], ["PersonalAccessToken"]],
    "list_ruleset_history_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "get_ruleset_version_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "list_secret_scanning_alerts_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "get_secret_scanning_alert": [["OAuth2"], ["PersonalAccessToken"]],
    "update_secret_scanning_alert": [["OAuth2"], ["PersonalAccessToken"]],
    "list_secret_alert_locations": [["OAuth2"], ["PersonalAccessToken"]],
    "bypass_push_protection": [["OAuth2"], ["PersonalAccessToken"]],
    "list_secret_scan_history": [["OAuth2"], ["PersonalAccessToken"]],
    "list_security_advisories": [["OAuth2"], ["PersonalAccessToken"]],
    "create_security_advisory": [["OAuth2"], ["PersonalAccessToken"]],
    "report_security_vulnerability": [["OAuth2"], ["PersonalAccessToken"]],
    "get_security_advisory_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "update_security_advisory": [["OAuth2"], ["PersonalAccessToken"]],
    "request_cve_for_advisory": [["OAuth2"], ["PersonalAccessToken"]],
    "create_security_advisory_fork": [["OAuth2"], ["PersonalAccessToken"]],
    "list_stargazers": [["OAuth2"], ["PersonalAccessToken"]],
    "get_code_frequency_stats": [["OAuth2"], ["PersonalAccessToken"]],
    "list_commit_activity_stats": [["OAuth2"], ["PersonalAccessToken"]],
    "list_contributor_stats": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_participation_stats": [["OAuth2"], ["PersonalAccessToken"]],
    "get_commit_punch_card": [["OAuth2"], ["PersonalAccessToken"]],
    "create_commit_status": [["OAuth2"], ["PersonalAccessToken"]],
    "list_watchers": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_subscription": [["OAuth2"], ["PersonalAccessToken"]],
    "configure_repository_subscription": [["OAuth2"], ["PersonalAccessToken"]],
    "unwatch_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "list_tags": [["OAuth2"], ["PersonalAccessToken"]],
    "download_repository_archive": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_teams": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_topics": [["OAuth2"], ["PersonalAccessToken"]],
    "update_repository_topics": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_clones": [["OAuth2"], ["PersonalAccessToken"]],
    "list_popular_paths": [["OAuth2"], ["PersonalAccessToken"]],
    "get_repository_views": [["OAuth2"], ["PersonalAccessToken"]],
    "transfer_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "get_vulnerability_alerts_status": [["OAuth2"], ["PersonalAccessToken"]],
    "enable_vulnerability_alerts": [["OAuth2"], ["PersonalAccessToken"]],
    "disable_vulnerability_alerts": [["OAuth2"], ["PersonalAccessToken"]],
    "download_repository_archive_zip": [["OAuth2"], ["PersonalAccessToken"]],
    "create_repository_from_template": [["OAuth2"], ["PersonalAccessToken"]],
    "list_public_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "search_code": [["OAuth2"], ["PersonalAccessToken"]],
    "search_commits": [["OAuth2"], ["PersonalAccessToken"]],
    "search_issues": [["OAuth2"], ["PersonalAccessToken"]],
    "search_labels": [["OAuth2"], ["PersonalAccessToken"]],
    "search_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "search_topics": [["OAuth2"], ["PersonalAccessToken"]],
    "search_users": [["OAuth2"], ["PersonalAccessToken"]],
    "get_authenticated_user": [["OAuth2"], ["PersonalAccessToken"]],
    "update_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_blocked_users_personal": [["OAuth2"], ["PersonalAccessToken"]],
    "check_user_blocked": [["OAuth2"], ["PersonalAccessToken"]],
    "block_user": [["OAuth2"], ["PersonalAccessToken"]],
    "unblock_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_codespaces": [["OAuth2"], ["PersonalAccessToken"]],
    "create_codespace_from_pull_request_2": [["OAuth2"], ["PersonalAccessToken"]],
    "list_codespace_secrets_for_user": [["OAuth2"], ["PersonalAccessToken"]],
    "get_codespaces_public_key": [["OAuth2"], ["PersonalAccessToken"]],
    "get_codespace_secret_for_user": [["OAuth2"], ["PersonalAccessToken"]],
    "create_or_update_codespace_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_codespace_secret_for_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repositories_for_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "update_secret_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "add_repository_to_codespace_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_repository_from_codespace_secret": [["OAuth2"], ["PersonalAccessToken"]],
    "get_codespace": [["OAuth2"], ["PersonalAccessToken"]],
    "update_codespace": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_codespace": [["OAuth2"], ["PersonalAccessToken"]],
    "export_codespace": [["OAuth2"], ["PersonalAccessToken"]],
    "get_codespace_export_details": [["OAuth2"], ["PersonalAccessToken"]],
    "list_codespace_machines_available": [["OAuth2"], ["PersonalAccessToken"]],
    "publish_codespace": [["OAuth2"], ["PersonalAccessToken"]],
    "start_codespace": [["OAuth2"], ["PersonalAccessToken"]],
    "stop_codespace_authenticated": [["OAuth2"], ["PersonalAccessToken"]],
    "set_primary_email_visibility": [["OAuth2"], ["PersonalAccessToken"]],
    "list_emails": [["OAuth2"], ["PersonalAccessToken"]],
    "add_email": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_email": [["OAuth2"], ["PersonalAccessToken"]],
    "list_followers": [["OAuth2"], ["PersonalAccessToken"]],
    "list_followed_users": [["OAuth2"], ["PersonalAccessToken"]],
    "check_user_is_followed": [["OAuth2"], ["PersonalAccessToken"]],
    "follow_user": [["OAuth2"], ["PersonalAccessToken"]],
    "unfollow_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_gpg_keys": [["OAuth2"], ["PersonalAccessToken"]],
    "add_gpg_key": [["OAuth2"], ["PersonalAccessToken"]],
    "get_gpg_key": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_gpg_key": [["OAuth2"], ["PersonalAccessToken"]],
    "list_app_installations_user": [["OAuth2"], ["PersonalAccessToken"]],
    "add_repository_to_installation": [["OAuth2"], ["PersonalAccessToken"]],
    "remove_repository_from_app_installation": [["OAuth2"], ["PersonalAccessToken"]],
    "get_interaction_restrictions": [["OAuth2"], ["PersonalAccessToken"]],
    "list_issues_assigned": [["OAuth2"], ["PersonalAccessToken"]],
    "list_ssh_keys": [["OAuth2"], ["PersonalAccessToken"]],
    "add_ssh_key": [["OAuth2"], ["PersonalAccessToken"]],
    "get_ssh_key": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_ssh_key": [["OAuth2"], ["PersonalAccessToken"]],
    "list_subscriptions": [["OAuth2"], ["PersonalAccessToken"]],
    "list_subscriptions_stubbed": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_memberships": [["OAuth2"], ["PersonalAccessToken"]],
    "get_organization_membership_authenticated": [["OAuth2"], ["PersonalAccessToken"]],
    "activate_organization_membership": [["OAuth2"], ["PersonalAccessToken"]],
    "list_migrations": [["OAuth2"], ["PersonalAccessToken"]],
    "get_migration_status_user": [["OAuth2"], ["PersonalAccessToken"]],
    "download_migration_archive_user": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_migration_archive_user": [["OAuth2"], ["PersonalAccessToken"]],
    "unlock_migration_repository_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_migration_repositories_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organizations_authenticated": [["OAuth2"], ["PersonalAccessToken"]],
    "list_packages": [["OAuth2"], ["PersonalAccessToken"]],
    "get_package": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_package": [["OAuth2"], ["PersonalAccessToken"]],
    "restore_package": [["OAuth2"], ["PersonalAccessToken"]],
    "list_package_versions": [["OAuth2"], ["PersonalAccessToken"]],
    "get_package_version": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_package_version_authenticated": [["OAuth2"], ["PersonalAccessToken"]],
    "restore_package_version_for_authenticated_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_public_emails": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "create_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "list_repository_invitations_for_user": [["OAuth2"], ["PersonalAccessToken"]],
    "accept_repository_invitation": [["OAuth2"], ["PersonalAccessToken"]],
    "decline_repository_invitation": [["OAuth2"], ["PersonalAccessToken"]],
    "list_social_accounts": [["OAuth2"], ["PersonalAccessToken"]],
    "add_social_accounts": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_social_accounts": [["OAuth2"], ["PersonalAccessToken"]],
    "list_starred_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "check_repository_starred": [["OAuth2"], ["PersonalAccessToken"]],
    "star_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "unstar_repository": [["OAuth2"], ["PersonalAccessToken"]],
    "list_watched_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "list_teams_authenticated": [["OAuth2"], ["PersonalAccessToken"]],
    "get_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_users": [["OAuth2"], ["PersonalAccessToken"]],
    "get_user_by_username": [["OAuth2"], ["PersonalAccessToken"]],
    "list_attestations_by_digests_user": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_attestations_user": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_attestation_by_subject_digest_user": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_attestation_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_attestations_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_user_events": [["OAuth2"], ["PersonalAccessToken"]],
    "list_organization_events_for_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_user_public_events": [["OAuth2"], ["PersonalAccessToken"]],
    "list_followers_by_username": [["OAuth2"], ["PersonalAccessToken"]],
    "list_following": [["OAuth2"], ["PersonalAccessToken"]],
    "check_user_following": [["OAuth2"], ["PersonalAccessToken"]],
    "list_user_gists": [["OAuth2"], ["PersonalAccessToken"]],
    "list_gpg_keys_by_username": [["OAuth2"], ["PersonalAccessToken"]],
    "get_user_hovercard": [["OAuth2"], ["PersonalAccessToken"]],
    "get_user_installation": [["OAuth2"], ["PersonalAccessToken"]],
    "list_public_keys": [["OAuth2"], ["PersonalAccessToken"]],
    "list_user_organizations": [["OAuth2"], ["PersonalAccessToken"]],
    "list_user_packages": [["OAuth2"], ["PersonalAccessToken"]],
    "get_package_public": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_user_package": [["OAuth2"], ["PersonalAccessToken"]],
    "restore_package_for_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_package_versions_public": [["OAuth2"], ["PersonalAccessToken"]],
    "get_package_version_public": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_package_version_user": [["OAuth2"], ["PersonalAccessToken"]],
    "restore_package_version_for_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_user_projects": [["OAuth2"], ["PersonalAccessToken"]],
    "get_user_project": [["OAuth2"], ["PersonalAccessToken"]],
    "list_project_fields_user": [["OAuth2"], ["PersonalAccessToken"]],
    "get_project_field_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_project_items_user": [["OAuth2"], ["PersonalAccessToken"]],
    "add_item_to_project_user": [["OAuth2"], ["PersonalAccessToken"]],
    "get_project_item_user": [["OAuth2"], ["PersonalAccessToken"]],
    "update_project_item_user": [["OAuth2"], ["PersonalAccessToken"]],
    "delete_project_item_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_received_events": [["OAuth2"], ["PersonalAccessToken"]],
    "list_user_public_received_events": [["OAuth2"], ["PersonalAccessToken"]],
    "list_user_repositories": [["OAuth2"], ["PersonalAccessToken"]],
    "get_billing_usage_report": [["OAuth2"], ["PersonalAccessToken"]],
    "list_social_accounts_public": [["OAuth2"], ["PersonalAccessToken"]],
    "list_ssh_signing_keys_for_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_starred_repositories_by_user": [["OAuth2"], ["PersonalAccessToken"]],
    "list_watched_repositories_by_user": [["OAuth2"], ["PersonalAccessToken"]],
    "get_enterprise_actions_cache_storage_limit": [["PersonalAccessToken"], ["OAuth2"]],
    "list_oidc_custom_property_inclusions": [["PersonalAccessToken"], ["OAuth2"]],
    "add_oidc_custom_property": [["PersonalAccessToken"], ["OAuth2"]],
    "list_organization_assignments": [["PersonalAccessToken"], ["OAuth2"]],
    "assign_team_to_organizations": [["PersonalAccessToken"], ["OAuth2"]],
    "unassign_team_from_organizations": [["PersonalAccessToken"], ["OAuth2"]],
    "verify_team_organization_assignment": [["PersonalAccessToken"], ["OAuth2"]],
    "assign_team_to_organization": [["PersonalAccessToken"], ["OAuth2"]],
    "unassign_team_from_organization": [["PersonalAccessToken"], ["OAuth2"]],
    "get_actions_cache_storage_limit": [["PersonalAccessToken"], ["OAuth2"]],
    "list_organization_budgets": [["PersonalAccessToken"], ["OAuth2"]],
    "get_budget": [["PersonalAccessToken"], ["OAuth2"]],
    "update_budget": [["PersonalAccessToken"], ["OAuth2"]],
    "delete_budget": [["PersonalAccessToken"], ["OAuth2"]],
    "get_premium_request_usage_report": [["PersonalAccessToken"], ["OAuth2"]],
    "get_billing_usage_summary": [["PersonalAccessToken"], ["OAuth2"]],
    "list_custom_runner_images": [["PersonalAccessToken"], ["OAuth2"]],
    "get_custom_runner_image": [["PersonalAccessToken"], ["OAuth2"]],
    "delete_custom_runner_image": [["PersonalAccessToken"], ["OAuth2"]],
    "list_custom_image_versions": [["PersonalAccessToken"], ["OAuth2"]],
    "get_custom_runner_image_version": [["PersonalAccessToken"], ["OAuth2"]],
    "delete_custom_image_version": [["PersonalAccessToken"], ["OAuth2"]],
    "list_oidc_custom_property_inclusions_for_org": [["PersonalAccessToken"], ["OAuth2"]],
    "add_oidc_custom_property_org": [["PersonalAccessToken"], ["OAuth2"]],
    "record_artifact_deployment": [["PersonalAccessToken"], ["OAuth2"]],
    "record_cluster_deployments": [["PersonalAccessToken"], ["OAuth2"]],
    "list_artifact_deployment_records": [["PersonalAccessToken"], ["OAuth2"]],
    "list_attestation_repositories": [["PersonalAccessToken"], ["OAuth2"]],
    "list_copilot_coding_agent_permissions": [["PersonalAccessToken"], ["OAuth2"]],
    "list_copilot_coding_agent_repositories": [["PersonalAccessToken"], ["OAuth2"]],
    "enable_copilot_coding_agent_for_repository": [["PersonalAccessToken"], ["OAuth2"]],
    "list_copilot_content_exclusions": [["PersonalAccessToken"], ["OAuth2"]],
    "list_issue_fields": [["PersonalAccessToken"], ["OAuth2"]],
    "create_issue_field": [["PersonalAccessToken"], ["OAuth2"]],
    "delete_issue_field": [["PersonalAccessToken"], ["OAuth2"]],
    "create_draft_item": [["PersonalAccessToken"], ["OAuth2"]],
    "add_project_field": [["PersonalAccessToken"], ["OAuth2"]],
    "create_project_view": [["PersonalAccessToken"], ["OAuth2"]],
    "list_project_view_items": [["PersonalAccessToken"], ["OAuth2"]],
    "list_immutable_release_repositories": [["PersonalAccessToken"], ["OAuth2"]],
    "enable_repository_immutable_releases": [["PersonalAccessToken"], ["OAuth2"]],
    "remove_repository_from_immutable_releases": [["PersonalAccessToken"], ["OAuth2"]],
    "get_cache_retention_limit": [["PersonalAccessToken"], ["OAuth2"]],
    "get_actions_cache_storage_limit_repository": [["PersonalAccessToken"], ["OAuth2"]],
    "get_immutable_releases": [["PersonalAccessToken"], ["OAuth2"]],
    "pin_issue_comment": [["PersonalAccessToken"], ["OAuth2"]],
    "unpin_issue_comment": [["PersonalAccessToken"], ["OAuth2"]],
    "add_issue_field_values": [["PersonalAccessToken"], ["OAuth2"]],
    "set_issue_field_values": [["PersonalAccessToken"], ["OAuth2"]],
    "delete_issue_field_value": [["PersonalAccessToken"], ["OAuth2"]],
    "create_draft_item_user": [["PersonalAccessToken"], ["OAuth2"]],
    "create_project_view_user": [["PersonalAccessToken"], ["OAuth2"]],
    "add_project_field_user": [["PersonalAccessToken"], ["OAuth2"]],
    "list_project_view_items_user": [["PersonalAccessToken"], ["OAuth2"]],
    "get_premium_request_usage_report_user": [["PersonalAccessToken"], ["OAuth2"]],
    "get_billing_usage_summary_user": [["PersonalAccessToken"], ["OAuth2"]]
}

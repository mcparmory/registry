"""
Authentication module for Canvas MCP server.

Generated: 2026-05-05 14:35:11 UTC
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
    OAuth 2.0 authentication for Canvas API.

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
        Authorization URL: https://{canvas_domain}/login/oauth2/auth
        Token URL: https://{canvas_domain}/login/oauth2/token

    Available Scopes (configure via OAUTH2_SCOPES):
        (Check API documentation for available scopes)
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
        self.token_url = self._resolve_url_template("https://{canvas_domain}/login/oauth2/token")
        self.auth_url = self._resolve_url_template("https://{canvas_domain}/login/oauth2/auth")
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
    Bearer token authentication for Canvas API.

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
    "get_assignment_lti": [["OAuth2"], ["bearerAuth"]],
    "get_originality_report": [["OAuth2"], ["bearerAuth"]],
    "update_originality_report": [["OAuth2"], ["bearerAuth"]],
    "get_submission": [["OAuth2"], ["bearerAuth"]],
    "list_submission_attempts": [["OAuth2"], ["bearerAuth"]],
    "submit_originality_report": [["OAuth2"], ["bearerAuth"]],
    "get_originality_report_submission": [["OAuth2"], ["bearerAuth"]],
    "update_originality_report_submission": [["OAuth2"], ["bearerAuth"]],
    "get_group_members_lti": [["OAuth2"], ["bearerAuth"]],
    "list_webhook_subscriptions": [["OAuth2"], ["bearerAuth"]],
    "get_webhook_subscription": [["OAuth2"], ["bearerAuth"]],
    "delete_webhook_subscription": [["OAuth2"], ["bearerAuth"]],
    "get_lti_user": [["OAuth2"], ["bearerAuth"]],
    "list_sis_export_assignments": [["OAuth2"], ["bearerAuth"]],
    "list_sis_export_assignments_by_course": [["OAuth2"], ["bearerAuth"]],
    "disable_sis_grade_exports": [["OAuth2"], ["bearerAuth"]],
    "list_accounts": [["OAuth2"], ["bearerAuth"]],
    "search_domains": [["OAuth2"], ["bearerAuth"]],
    "list_active_notifications": [["OAuth2"], ["bearerAuth"]],
    "create_notification": [["OAuth2"], ["bearerAuth"]],
    "get_notification": [["OAuth2"], ["bearerAuth"]],
    "update_notification": [["OAuth2"], ["bearerAuth"]],
    "dismiss_notification": [["OAuth2"], ["bearerAuth"]],
    "list_admins": [["OAuth2"], ["bearerAuth"]],
    "promote_account_admin": [["OAuth2"], ["bearerAuth"]],
    "list_department_participation_completed": [["OAuth2"], ["bearerAuth"]],
    "list_department_grade_distribution_completed": [["OAuth2"], ["bearerAuth"]],
    "get_department_statistics": [["OAuth2"], ["bearerAuth"]],
    "list_department_participation_data": [["OAuth2"], ["bearerAuth"]],
    "list_department_grade_distribution": [["OAuth2"], ["bearerAuth"]],
    "get_department_statistics_current": [["OAuth2"], ["bearerAuth"]],
    "list_department_participation_by_term": [["OAuth2"], ["bearerAuth"]],
    "list_department_grade_distributions": [["OAuth2"], ["bearerAuth"]],
    "get_department_statistics_term": [["OAuth2"], ["bearerAuth"]],
    "list_authentication_providers": [["OAuth2"], ["bearerAuth"]],
    "get_authentication_provider": [["OAuth2"], ["bearerAuth"]],
    "list_content_migrations": [["OAuth2"], ["bearerAuth"]],
    "initiate_content_migration": [["OAuth2"], ["bearerAuth"]],
    "list_migration_systems": [["OAuth2"], ["bearerAuth"]],
    "list_migration_issues": [["OAuth2"], ["bearerAuth"]],
    "get_migration_issue": [["OAuth2"], ["bearerAuth"]],
    "resolve_migration_issue": [["OAuth2"], ["bearerAuth"]],
    "get_content_migration": [["OAuth2"], ["bearerAuth"]],
    "update_content_migration": [["OAuth2"], ["bearerAuth"]],
    "list_courses_by_account": [["OAuth2"], ["bearerAuth"]],
    "create_course": [["OAuth2"], ["bearerAuth"]],
    "bulk_update_courses": [["OAuth2"], ["bearerAuth"]],
    "get_course_account": [["OAuth2"], ["bearerAuth"]],
    "get_enrollment": [["OAuth2"], ["bearerAuth"]],
    "list_external_tools": [["OAuth2"], ["bearerAuth"]],
    "create_external_tool": [["OAuth2"], ["bearerAuth"]],
    "get_external_tool_sessionless_launch_url": [["OAuth2"], ["bearerAuth"]],
    "get_external_tool": [["OAuth2"], ["bearerAuth"]],
    "update_external_tool": [["OAuth2"], ["bearerAuth"]],
    "remove_external_tool": [["OAuth2"], ["bearerAuth"]],
    "list_account_features": [["OAuth2"], ["bearerAuth"]],
    "list_enabled_features": [["OAuth2"], ["bearerAuth"]],
    "get_feature_flag": [["OAuth2"], ["bearerAuth"]],
    "list_grading_periods": [["OAuth2"], ["bearerAuth"]],
    "delete_grading_period": [["OAuth2"], ["bearerAuth"]],
    "list_grading_standards": [["OAuth2"], ["bearerAuth"]],
    "create_grading_standard": [["OAuth2"], ["bearerAuth"]],
    "get_grading_standard": [["OAuth2"], ["bearerAuth"]],
    "list_group_categories": [["OAuth2"], ["bearerAuth"]],
    "create_group_category": [["OAuth2"], ["bearerAuth"]],
    "list_groups_in_account": [["OAuth2"], ["bearerAuth"]],
    "list_logins": [["OAuth2"], ["bearerAuth"]],
    "create_login": [["OAuth2"], ["bearerAuth"]],
    "update_user_login": [["OAuth2"], ["bearerAuth"]],
    "list_outcome_links": [["OAuth2"], ["bearerAuth"]],
    "list_outcome_groups": [["OAuth2"], ["bearerAuth"]],
    "get_outcome_group_account": [["OAuth2"], ["bearerAuth"]],
    "update_outcome_group": [["OAuth2"], ["bearerAuth"]],
    "delete_outcome_group_account": [["OAuth2"], ["bearerAuth"]],
    "copy_outcome_group": [["OAuth2"], ["bearerAuth"]],
    "list_outcomes_account": [["OAuth2"], ["bearerAuth"]],
    "link_outcome": [["OAuth2"], ["bearerAuth"]],
    "link_outcome_existing": [["OAuth2"], ["bearerAuth"]],
    "unlink_outcome": [["OAuth2"], ["bearerAuth"]],
    "list_subgroups": [["OAuth2"], ["bearerAuth"]],
    "create_outcome_subgroup": [["OAuth2"], ["bearerAuth"]],
    "import_outcomes": [["OAuth2"], ["bearerAuth"]],
    "get_outcome_import_status": [["OAuth2"], ["bearerAuth"]],
    "list_proficiency_ratings": [["OAuth2"], ["bearerAuth"]],
    "set_proficiency_ratings": [["OAuth2"], ["bearerAuth"]],
    "check_account_permissions": [["OAuth2"], ["bearerAuth"]],
    "list_reports": [["OAuth2"], ["bearerAuth"]],
    "list_reports_by_type": [["OAuth2"], ["bearerAuth"]],
    "generate_report": [["OAuth2"], ["bearerAuth"]],
    "get_report_status": [["OAuth2"], ["bearerAuth"]],
    "delete_report": [["OAuth2"], ["bearerAuth"]],
    "list_roles": [["OAuth2"], ["bearerAuth"]],
    "get_role": [["OAuth2"], ["bearerAuth"]],
    "deactivate_role": [["OAuth2"], ["bearerAuth"]],
    "reactivate_role": [["OAuth2"], ["bearerAuth"]],
    "get_root_outcome_group_account": [["OAuth2"], ["bearerAuth"]],
    "list_rubrics": [["OAuth2"], ["bearerAuth"]],
    "get_rubric": [["OAuth2"], ["bearerAuth"]],
    "list_scopes": [["OAuth2"], ["bearerAuth"]],
    "register_user": [["OAuth2"], ["bearerAuth"]],
    "create_shared_theme": [["OAuth2"], ["bearerAuth"]],
    "update_shared_theme": [["OAuth2"], ["bearerAuth"]],
    "list_sis_import_errors": [["OAuth2"], ["bearerAuth"]],
    "list_sis_imports": [["OAuth2"], ["bearerAuth"]],
    "abort_pending_sis_imports": [["OAuth2"], ["bearerAuth"]],
    "get_sis_import_status": [["OAuth2"], ["bearerAuth"]],
    "abort_sis_import": [["OAuth2"], ["bearerAuth"]],
    "list_sis_import_errors_by_import": [["OAuth2"], ["bearerAuth"]],
    "restore_sis_import_workflow_states": [["OAuth2"], ["bearerAuth"]],
    "list_sub_accounts": [["OAuth2"], ["bearerAuth"]],
    "create_sub_account": [["OAuth2"], ["bearerAuth"]],
    "delete_sub_account": [["OAuth2"], ["bearerAuth"]],
    "list_enrollment_terms": [["OAuth2"], ["bearerAuth"]],
    "create_term": [["OAuth2"], ["bearerAuth"]],
    "update_enrollment_term": [["OAuth2"], ["bearerAuth"]],
    "delete_enrollment_term": [["OAuth2"], ["bearerAuth"]],
    "list_account_users": [["OAuth2"], ["bearerAuth"]],
    "create_user": [["OAuth2"], ["bearerAuth"]],
    "remove_user_from_account": [["OAuth2"], ["bearerAuth"]],
    "get_account": [["OAuth2"], ["bearerAuth"]],
    "update_account": [["OAuth2"], ["bearerAuth"]],
    "list_announcements": [["OAuth2"], ["bearerAuth"]],
    "list_appointment_groups": [["OAuth2"], ["bearerAuth"]],
    "create_appointment_group": [["OAuth2"], ["bearerAuth"]],
    "list_next_appointments": [["OAuth2"], ["bearerAuth"]],
    "get_appointment_group": [["OAuth2"], ["bearerAuth"]],
    "update_appointment_group": [["OAuth2"], ["bearerAuth"]],
    "cancel_appointment_group": [["OAuth2"], ["bearerAuth"]],
    "list_appointment_group_participants": [["OAuth2"], ["bearerAuth"]],
    "list_appointment_group_participants_users": [["OAuth2"], ["bearerAuth"]],
    "list_authentication_events_by_account": [["OAuth2"], ["bearerAuth"]],
    "list_authentication_events_by_login": [["OAuth2"], ["bearerAuth"]],
    "list_authentication_events_by_user": [["OAuth2"], ["bearerAuth"]],
    "list_course_events": [["OAuth2"], ["bearerAuth"]],
    "list_grade_changes_by_assignment": [["OAuth2"], ["bearerAuth"]],
    "list_grade_changes_by_course": [["OAuth2"], ["bearerAuth"]],
    "list_grade_changes_by_grader": [["OAuth2"], ["bearerAuth"]],
    "list_grade_changes_by_student": [["OAuth2"], ["bearerAuth"]],
    "list_events": [["OAuth2"], ["bearerAuth"]],
    "create_calendar_event": [["OAuth2"], ["bearerAuth"]],
    "get_calendar_event": [["OAuth2"], ["bearerAuth"]],
    "update_event": [["OAuth2"], ["bearerAuth"]],
    "delete_calendar_event": [["OAuth2"], ["bearerAuth"]],
    "reserve_appointment_slot": [["OAuth2"], ["bearerAuth"]],
    "reserve_time_slot": [["OAuth2"], ["bearerAuth"]],
    "list_collaboration_members": [["OAuth2"], ["bearerAuth"]],
    "list_messages": [["OAuth2"], ["bearerAuth"]],
    "list_conversations": [["OAuth2"], ["bearerAuth"]],
    "create_conversation_thread": [["OAuth2"], ["bearerAuth"]],
    "update_conversations_batch": [["OAuth2"], ["bearerAuth"]],
    "list_conversation_batches": [["OAuth2"], ["bearerAuth"]],
    "list_message_recipients": [["OAuth2"], ["bearerAuth"]],
    "mark_all_conversations_as_read": [["OAuth2"], ["bearerAuth"]],
    "get_unread_conversation_count": [["OAuth2"], ["bearerAuth"]],
    "retrieve_conversation": [["OAuth2"], ["bearerAuth"]],
    "update_conversation": [["OAuth2"], ["bearerAuth"]],
    "delete_conversation": [["OAuth2"], ["bearerAuth"]],
    "send_message": [["OAuth2"], ["bearerAuth"]],
    "add_conversation_recipients": [["OAuth2"], ["bearerAuth"]],
    "remove_messages": [["OAuth2"], ["bearerAuth"]],
    "list_accounts_by_course_admin": [["OAuth2"], ["bearerAuth"]],
    "list_courses": [["OAuth2"], ["bearerAuth"]],
    "list_course_activities": [["OAuth2"], ["bearerAuth"]],
    "get_course_activity_summary": [["OAuth2"], ["bearerAuth"]],
    "get_course_participation_analytics": [["OAuth2"], ["bearerAuth"]],
    "list_assignment_analytics": [["OAuth2"], ["bearerAuth"]],
    "list_course_student_summaries": [["OAuth2"], ["bearerAuth"]],
    "get_student_course_participation": [["OAuth2"], ["bearerAuth"]],
    "list_student_assignment_analytics": [["OAuth2"], ["bearerAuth"]],
    "get_course_student_messaging_analytics": [["OAuth2"], ["bearerAuth"]],
    "list_assignment_groups": [["OAuth2"], ["bearerAuth"]],
    "create_assignment_group": [["OAuth2"], ["bearerAuth"]],
    "get_assignment_group": [["OAuth2"], ["bearerAuth"]],
    "update_assignment_group": [["OAuth2"], ["bearerAuth"]],
    "delete_assignment_group": [["OAuth2"], ["bearerAuth"]],
    "list_assignments": [["OAuth2"], ["bearerAuth"]],
    "create_assignment": [["OAuth2"], ["bearerAuth"]],
    "list_gradeable_students_for_assignments": [["OAuth2"], ["bearerAuth"]],
    "retrieve_assignment_overrides": [["OAuth2"], ["bearerAuth"]],
    "create_assignment_overrides": [["OAuth2"], ["bearerAuth"]],
    "update_assignment_overrides": [["OAuth2"], ["bearerAuth"]],
    "check_provisional_grade_status_anonymous": [["OAuth2"], ["bearerAuth"]],
    "list_gradeable_students": [["OAuth2"], ["bearerAuth"]],
    "list_moderated_students": [["OAuth2"], ["bearerAuth"]],
    "select_moderation_students": [["OAuth2"], ["bearerAuth"]],
    "list_assignment_overrides": [["OAuth2"], ["bearerAuth"]],
    "create_assignment_override": [["OAuth2"], ["bearerAuth"]],
    "get_assignment_override": [["OAuth2"], ["bearerAuth"]],
    "update_assignment_override": [["OAuth2"], ["bearerAuth"]],
    "remove_assignment_override": [["OAuth2"], ["bearerAuth"]],
    "list_peer_reviews": [["OAuth2"], ["bearerAuth"]],
    "finalize_provisional_grades": [["OAuth2"], ["bearerAuth"]],
    "publish_assignment_grades": [["OAuth2"], ["bearerAuth"]],
    "check_provisional_grade_status": [["OAuth2"], ["bearerAuth"]],
    "copy_provisional_grade_to_final_mark": [["OAuth2"], ["bearerAuth"]],
    "finalize_provisional_grade": [["OAuth2"], ["bearerAuth"]],
    "get_assignment_submission_summary": [["OAuth2"], ["bearerAuth"]],
    "list_assignment_submissions": [["OAuth2"], ["bearerAuth"]],
    "submit_assignment": [["OAuth2"], ["bearerAuth"]],
    "grade_submissions": [["OAuth2"], ["bearerAuth"]],
    "list_peer_reviews_submission": [["OAuth2"], ["bearerAuth"]],
    "assign_peer_reviewer": [["OAuth2"], ["bearerAuth"]],
    "remove_peer_review": [["OAuth2"], ["bearerAuth"]],
    "get_submission_by_user": [["OAuth2"], ["bearerAuth"]],
    "grade_submission": [["OAuth2"], ["bearerAuth"]],
    "upload_submission_comment_file": [["OAuth2"], ["bearerAuth"]],
    "upload_submission_file": [["OAuth2"], ["bearerAuth"]],
    "mark_submission_as_read": [["OAuth2"], ["bearerAuth"]],
    "mark_submission_as_unread": [["OAuth2"], ["bearerAuth"]],
    "get_assignment": [["OAuth2"], ["bearerAuth"]],
    "update_assignment": [["OAuth2"], ["bearerAuth"]],
    "delete_assignment": [["OAuth2"], ["bearerAuth"]],
    "list_blueprint_subscriptions": [["OAuth2"], ["bearerAuth"]],
    "list_blueprint_imports": [["OAuth2"], ["bearerAuth"]],
    "get_blueprint_import": [["OAuth2"], ["bearerAuth"]],
    "list_blueprint_migration_details": [["OAuth2"], ["bearerAuth"]],
    "get_blueprint_template": [["OAuth2"], ["bearerAuth"]],
    "list_blueprint_associated_courses": [["OAuth2"], ["bearerAuth"]],
    "list_blueprint_migrations": [["OAuth2"], ["bearerAuth"]],
    "push_blueprint_to_associated_courses": [["OAuth2"], ["bearerAuth"]],
    "get_blueprint_migration": [["OAuth2"], ["bearerAuth"]],
    "list_blueprint_migration_changes": [["OAuth2"], ["bearerAuth"]],
    "update_blueprint_object_restrictions": [["OAuth2"], ["bearerAuth"]],
    "list_blueprint_unsynced_changes": [["OAuth2"], ["bearerAuth"]],
    "update_blueprint_template_associations": [["OAuth2"], ["bearerAuth"]],
    "get_course_timetable": [["OAuth2"], ["bearerAuth"]],
    "schedule_course_timetable": [["OAuth2"], ["bearerAuth"]],
    "create_or_update_timetable_events": [["OAuth2"], ["bearerAuth"]],
    "list_collaborations": [["OAuth2"], ["bearerAuth"]],
    "list_conferences": [["OAuth2"], ["bearerAuth"]],
    "list_content_exports": [["OAuth2"], ["bearerAuth"]],
    "initiate_course_export": [["OAuth2"], ["bearerAuth"]],
    "get_content_export": [["OAuth2"], ["bearerAuth"]],
    "list_content_licenses": [["OAuth2"], ["bearerAuth"]],
    "list_content_migrations_course": [["OAuth2"], ["bearerAuth"]],
    "initiate_content_migration_course": [["OAuth2"], ["bearerAuth"]],
    "list_migration_systems_course": [["OAuth2"], ["bearerAuth"]],
    "list_migration_issues_course": [["OAuth2"], ["bearerAuth"]],
    "get_migration_issue_in_course": [["OAuth2"], ["bearerAuth"]],
    "resolve_migration_issue_course": [["OAuth2"], ["bearerAuth"]],
    "get_content_migration_course": [["OAuth2"], ["bearerAuth"]],
    "update_content_migration_course": [["OAuth2"], ["bearerAuth"]],
    "duplicate_course_content": [["OAuth2"], ["bearerAuth"]],
    "update_gradebook_column_data": [["OAuth2"], ["bearerAuth"]],
    "list_custom_gradebook_columns": [["OAuth2"], ["bearerAuth"]],
    "create_gradebook_column": [["OAuth2"], ["bearerAuth"]],
    "reorder_custom_columns": [["OAuth2"], ["bearerAuth"]],
    "update_gradebook_column": [["OAuth2"], ["bearerAuth"]],
    "delete_gradebook_column": [["OAuth2"], ["bearerAuth"]],
    "list_column_entries": [["OAuth2"], ["bearerAuth"]],
    "set_gradebook_column_entry": [["OAuth2"], ["bearerAuth"]],
    "list_discussion_topics": [["OAuth2"], ["bearerAuth"]],
    "create_discussion_topic": [["OAuth2"], ["bearerAuth"]],
    "reorder_pinned_discussion_topics": [["OAuth2"], ["bearerAuth"]],
    "get_discussion_topic": [["OAuth2"], ["bearerAuth"]],
    "update_discussion_topic": [["OAuth2"], ["bearerAuth"]],
    "delete_discussion_topic": [["OAuth2"], ["bearerAuth"]],
    "list_discussion_entries": [["OAuth2"], ["bearerAuth"]],
    "create_discussion_entry": [["OAuth2"], ["bearerAuth"]],
    "rate_discussion_entry": [["OAuth2"], ["bearerAuth"]],
    "mark_discussion_entry_as_read": [["OAuth2"], ["bearerAuth"]],
    "mark_discussion_entry_unread": [["OAuth2"], ["bearerAuth"]],
    "list_discussion_replies": [["OAuth2"], ["bearerAuth"]],
    "create_discussion_reply": [["OAuth2"], ["bearerAuth"]],
    "update_discussion_entry": [["OAuth2"], ["bearerAuth"]],
    "delete_discussion_entry": [["OAuth2"], ["bearerAuth"]],
    "list_discussion_entries_by_ids": [["OAuth2"], ["bearerAuth"]],
    "mark_discussion_topic_as_read": [["OAuth2"], ["bearerAuth"]],
    "unread_discussion_topic": [["OAuth2"], ["bearerAuth"]],
    "mark_all_discussion_entries_as_read": [["OAuth2"], ["bearerAuth"]],
    "mark_discussion_entries_as_unread": [["OAuth2"], ["bearerAuth"]],
    "subscribe_to_discussion_topic": [["OAuth2"], ["bearerAuth"]],
    "unsubscribe_from_discussion_topic": [["OAuth2"], ["bearerAuth"]],
    "get_discussion_topic_view": [["OAuth2"], ["bearerAuth"]],
    "list_assignment_due_dates": [["OAuth2"], ["bearerAuth"]],
    "list_enrollments": [["OAuth2"], ["bearerAuth"]],
    "enroll_user_in_course": [["OAuth2"], ["bearerAuth"]],
    "modify_enrollment": [["OAuth2"], ["bearerAuth"]],
    "accept_course_enrollment": [["OAuth2"], ["bearerAuth"]],
    "reactivate_enrollment": [["OAuth2"], ["bearerAuth"]],
    "reject_enrollment": [["OAuth2"], ["bearerAuth"]],
    "initiate_epub_export": [["OAuth2"], ["bearerAuth"]],
    "get_epub_export": [["OAuth2"], ["bearerAuth"]],
    "list_external_feeds": [["OAuth2"], ["bearerAuth"]],
    "create_external_feed": [["OAuth2"], ["bearerAuth"]],
    "remove_external_feed": [["OAuth2"], ["bearerAuth"]],
    "list_external_tools_course": [["OAuth2"], ["bearerAuth"]],
    "create_external_tool_course": [["OAuth2"], ["bearerAuth"]],
    "get_external_tool_sessionless_launch_url_course": [["OAuth2"], ["bearerAuth"]],
    "get_external_tool_course": [["OAuth2"], ["bearerAuth"]],
    "update_external_tool_course": [["OAuth2"], ["bearerAuth"]],
    "remove_external_tool_course": [["OAuth2"], ["bearerAuth"]],
    "list_course_features": [["OAuth2"], ["bearerAuth"]],
    "get_feature_flag_course": [["OAuth2"], ["bearerAuth"]],
    "list_course_files": [["OAuth2"], ["bearerAuth"]],
    "get_course_storage_quota": [["OAuth2"], ["bearerAuth"]],
    "get_file_course": [["OAuth2"], ["bearerAuth"]],
    "list_folders": [["OAuth2"], ["bearerAuth"]],
    "create_folder": [["OAuth2"], ["bearerAuth"]],
    "get_folder_path": [["OAuth2"], ["bearerAuth"]],
    "get_folder": [["OAuth2"], ["bearerAuth"]],
    "get_course_front_page": [["OAuth2"], ["bearerAuth"]],
    "update_course_front_page": [["OAuth2"], ["bearerAuth"]],
    "list_gradebook_history_days": [["OAuth2"], ["bearerAuth"]],
    "list_submission_versions": [["OAuth2"], ["bearerAuth"]],
    "list_gradebook_history_details": [["OAuth2"], ["bearerAuth"]],
    "list_submission_versions_by_grader": [["OAuth2"], ["bearerAuth"]],
    "list_grading_periods_course": [["OAuth2"], ["bearerAuth"]],
    "get_grading_period": [["OAuth2"], ["bearerAuth"]],
    "update_grading_period": [["OAuth2"], ["bearerAuth"]],
    "delete_grading_period_course": [["OAuth2"], ["bearerAuth"]],
    "list_grading_standards_course": [["OAuth2"], ["bearerAuth"]],
    "create_grading_standard_course": [["OAuth2"], ["bearerAuth"]],
    "get_grading_standard_course": [["OAuth2"], ["bearerAuth"]],
    "list_group_categories_course": [["OAuth2"], ["bearerAuth"]],
    "create_group_category_course": [["OAuth2"], ["bearerAuth"]],
    "list_groups_in_course": [["OAuth2"], ["bearerAuth"]],
    "list_assessments": [["OAuth2"], ["bearerAuth"]],
    "create_or_find_live_assessment": [["OAuth2"], ["bearerAuth"]],
    "list_assessment_results": [["OAuth2"], ["bearerAuth"]],
    "submit_live_assessment_result": [["OAuth2"], ["bearerAuth"]],
    "get_module_item_sequence": [["OAuth2"], ["bearerAuth"]],
    "list_modules": [["OAuth2"], ["bearerAuth"]],
    "create_module": [["OAuth2"], ["bearerAuth"]],
    "get_module": [["OAuth2"], ["bearerAuth"]],
    "update_module": [["OAuth2"], ["bearerAuth"]],
    "delete_module": [["OAuth2"], ["bearerAuth"]],
    "relock_module_progressions": [["OAuth2"], ["bearerAuth"]],
    "list_module_items": [["OAuth2"], ["bearerAuth"]],
    "add_module_item": [["OAuth2"], ["bearerAuth"]],
    "get_module_item": [["OAuth2"], ["bearerAuth"]],
    "update_module_item": [["OAuth2"], ["bearerAuth"]],
    "delete_module_item": [["OAuth2"], ["bearerAuth"]],
    "toggle_module_item_completion": [["OAuth2"], ["bearerAuth"]],
    "mark_module_item_read": [["OAuth2"], ["bearerAuth"]],
    "assign_mastery_path": [["OAuth2"], ["bearerAuth"]],
    "list_outcome_aligned_assignments": [["OAuth2"], ["bearerAuth"]],
    "list_outcome_links_course": [["OAuth2"], ["bearerAuth"]],
    "list_outcome_groups_course": [["OAuth2"], ["bearerAuth"]],
    "get_outcome_group_course": [["OAuth2"], ["bearerAuth"]],
    "update_outcome_group_course": [["OAuth2"], ["bearerAuth"]],
    "delete_outcome_group_course": [["OAuth2"], ["bearerAuth"]],
    "import_outcome_group": [["OAuth2"], ["bearerAuth"]],
    "list_outcomes_course": [["OAuth2"], ["bearerAuth"]],
    "link_outcome_course": [["OAuth2"], ["bearerAuth"]],
    "link_outcome_course_existing": [["OAuth2"], ["bearerAuth"]],
    "remove_outcome_from_group": [["OAuth2"], ["bearerAuth"]],
    "list_outcome_subgroups": [["OAuth2"], ["bearerAuth"]],
    "create_outcome_subgroup_course": [["OAuth2"], ["bearerAuth"]],
    "import_outcomes_course": [["OAuth2"], ["bearerAuth"]],
    "get_outcome_import_status_course": [["OAuth2"], ["bearerAuth"]],
    "list_outcome_results": [["OAuth2"], ["bearerAuth"]],
    "list_outcome_rollups": [["OAuth2"], ["bearerAuth"]],
    "list_course_pages": [["OAuth2"], ["bearerAuth"]],
    "create_wiki_page": [["OAuth2"], ["bearerAuth"]],
    "get_course_page": [["OAuth2"], ["bearerAuth"]],
    "update_wiki_page": [["OAuth2"], ["bearerAuth"]],
    "delete_page": [["OAuth2"], ["bearerAuth"]],
    "duplicate_page": [["OAuth2"], ["bearerAuth"]],
    "list_page_revisions": [["OAuth2"], ["bearerAuth"]],
    "get_page_revision_latest": [["OAuth2"], ["bearerAuth"]],
    "get_page_revision": [["OAuth2"], ["bearerAuth"]],
    "revert_page_to_revision": [["OAuth2"], ["bearerAuth"]],
    "check_course_permissions": [["OAuth2"], ["bearerAuth"]],
    "list_course_collaborators": [["OAuth2"], ["bearerAuth"]],
    "preview_course_html": [["OAuth2"], ["bearerAuth"]],
    "grant_quiz_extensions": [["OAuth2"], ["bearerAuth"]],
    "list_quizzes": [["OAuth2"], ["bearerAuth"]],
    "create_quiz": [["OAuth2"], ["bearerAuth"]],
    "list_quiz_override_dates": [["OAuth2"], ["bearerAuth"]],
    "get_quiz": [["OAuth2"], ["bearerAuth"]],
    "update_quiz": [["OAuth2"], ["bearerAuth"]],
    "delete_quiz": [["OAuth2"], ["bearerAuth"]],
    "reorder_quiz_questions": [["OAuth2"], ["bearerAuth"]],
    "send_quiz_message_to_users": [["OAuth2"], ["bearerAuth"]],
    "grant_quiz_extensions_specific": [["OAuth2"], ["bearerAuth"]],
    "create_question_group": [["OAuth2"], ["bearerAuth"]],
    "get_quiz_group": [["OAuth2"], ["bearerAuth"]],
    "update_question_group": [["OAuth2"], ["bearerAuth"]],
    "delete_question_group": [["OAuth2"], ["bearerAuth"]],
    "reorder_question_groups": [["OAuth2"], ["bearerAuth"]],
    "list_quiz_ip_filters": [["OAuth2"], ["bearerAuth"]],
    "list_quiz_questions": [["OAuth2"], ["bearerAuth"]],
    "create_quiz_question": [["OAuth2"], ["bearerAuth"]],
    "get_quiz_question": [["OAuth2"], ["bearerAuth"]],
    "update_quiz_question": [["OAuth2"], ["bearerAuth"]],
    "remove_quiz_question": [["OAuth2"], ["bearerAuth"]],
    "list_quiz_reports": [["OAuth2"], ["bearerAuth"]],
    "generate_quiz_report": [["OAuth2"], ["bearerAuth"]],
    "get_quiz_report": [["OAuth2"], ["bearerAuth"]],
    "cancel_or_delete_quiz_report": [["OAuth2"], ["bearerAuth"]],
    "get_quiz_statistics": [["OAuth2"], ["bearerAuth"]],
    "get_quiz_submission": [["OAuth2"], ["bearerAuth"]],
    "list_quiz_submissions": [["OAuth2"], ["bearerAuth"]],
    "start_quiz_submission": [["OAuth2"], ["bearerAuth"]],
    "upload_quiz_submission_file": [["OAuth2"], ["bearerAuth"]],
    "retrieve_quiz_submission": [["OAuth2"], ["bearerAuth"]],
    "grade_quiz_submission": [["OAuth2"], ["bearerAuth"]],
    "submit_quiz": [["OAuth2"], ["bearerAuth"]],
    "list_submission_events": [["OAuth2"], ["bearerAuth"]],
    "record_quiz_submission_events": [["OAuth2"], ["bearerAuth"]],
    "get_quiz_submission_time": [["OAuth2"], ["bearerAuth"]],
    "list_students_by_recent_login": [["OAuth2"], ["bearerAuth"]],
    "reset_course": [["OAuth2"], ["bearerAuth"]],
    "get_root_outcome_group_course": [["OAuth2"], ["bearerAuth"]],
    "list_rubrics_course": [["OAuth2"], ["bearerAuth"]],
    "get_rubric_course": [["OAuth2"], ["bearerAuth"]],
    "search_course_users": [["OAuth2"], ["bearerAuth"]],
    "list_sections": [["OAuth2"], ["bearerAuth"]],
    "create_section": [["OAuth2"], ["bearerAuth"]],
    "get_section": [["OAuth2"], ["bearerAuth"]],
    "get_course_settings": [["OAuth2"], ["bearerAuth"]],
    "list_submissions": [["OAuth2"], ["bearerAuth"]],
    "bulk_grade_submissions": [["OAuth2"], ["bearerAuth"]],
    "list_course_tabs": [["OAuth2"], ["bearerAuth"]],
    "update_course_tab": [["OAuth2"], ["bearerAuth"]],
    "list_course_todos": [["OAuth2"], ["bearerAuth"]],
    "set_file_usage_rights": [["OAuth2"], ["bearerAuth"]],
    "remove_file_usage_rights": [["OAuth2"], ["bearerAuth"]],
    "list_course_users": [["OAuth2"], ["bearerAuth"]],
    "get_user": [["OAuth2"], ["bearerAuth"]],
    "update_student_last_attended_date": [["OAuth2"], ["bearerAuth"]],
    "get_course": [["OAuth2"], ["bearerAuth"]],
    "update_course": [["OAuth2"], ["bearerAuth"]],
    "conclude_or_delete_course": [["OAuth2"], ["bearerAuth"]],
    "get_late_policy": [["OAuth2"], ["bearerAuth"]],
    "create_late_policy": [["OAuth2"], ["bearerAuth"]],
    "update_course_late_policy": [["OAuth2"], ["bearerAuth"]],
    "list_courses_with_latest_epub_export": [["OAuth2"], ["bearerAuth"]],
    "submit_error_report": [["OAuth2"], ["bearerAuth"]],
    "get_file": [["OAuth2"], ["bearerAuth"]],
    "update_file": [["OAuth2"], ["bearerAuth"]],
    "delete_file": [["OAuth2"], ["bearerAuth"]],
    "get_file_preview_url": [["OAuth2"], ["bearerAuth"]],
    "copy_file": [["OAuth2"], ["bearerAuth"]],
    "copy_folder": [["OAuth2"], ["bearerAuth"]],
    "upload_file": [["OAuth2"], ["bearerAuth"]],
    "create_folder_nested": [["OAuth2"], ["bearerAuth"]],
    "get_folder_nested": [["OAuth2"], ["bearerAuth"]],
    "update_folder": [["OAuth2"], ["bearerAuth"]],
    "delete_folder": [["OAuth2"], ["bearerAuth"]],
    "list_files": [["OAuth2"], ["bearerAuth"]],
    "list_subfolders": [["OAuth2"], ["bearerAuth"]],
    "get_outcome_group": [["OAuth2"], ["bearerAuth"]],
    "update_outcome_group_global": [["OAuth2"], ["bearerAuth"]],
    "delete_outcome_group": [["OAuth2"], ["bearerAuth"]],
    "import_outcome_group_global": [["OAuth2"], ["bearerAuth"]],
    "list_outcomes": [["OAuth2"], ["bearerAuth"]],
    "link_outcome_global": [["OAuth2"], ["bearerAuth"]],
    "link_outcome_global_existing": [["OAuth2"], ["bearerAuth"]],
    "unlink_outcome_global": [["OAuth2"], ["bearerAuth"]],
    "list_outcome_subgroups_global": [["OAuth2"], ["bearerAuth"]],
    "create_outcome_subgroup_global": [["OAuth2"], ["bearerAuth"]],
    "get_root_outcome_group": [["OAuth2"], ["bearerAuth"]],
    "get_group_category": [["OAuth2"], ["bearerAuth"]],
    "update_group_category": [["OAuth2"], ["bearerAuth"]],
    "delete_group_category": [["OAuth2"], ["bearerAuth"]],
    "distribute_unassigned_members": [["OAuth2"], ["bearerAuth"]],
    "create_group_in_category": [["OAuth2"], ["bearerAuth"]],
    "list_group_category_users": [["OAuth2"], ["bearerAuth"]],
    "create_group": [["OAuth2"], ["bearerAuth"]],
    "get_group": [["OAuth2"], ["bearerAuth"]],
    "update_group": [["OAuth2"], ["bearerAuth"]],
    "delete_group": [["OAuth2"], ["bearerAuth"]],
    "list_group_activities": [["OAuth2"], ["bearerAuth"]],
    "get_group_activity_summary": [["OAuth2"], ["bearerAuth"]],
    "get_assignment_override_for_group": [["OAuth2"], ["bearerAuth"]],
    "list_group_collaborations": [["OAuth2"], ["bearerAuth"]],
    "list_conferences_group": [["OAuth2"], ["bearerAuth"]],
    "list_content_exports_group": [["OAuth2"], ["bearerAuth"]],
    "initiate_group_content_export": [["OAuth2"], ["bearerAuth"]],
    "get_content_export_group": [["OAuth2"], ["bearerAuth"]],
    "list_content_licenses_group": [["OAuth2"], ["bearerAuth"]],
    "list_content_migrations_group": [["OAuth2"], ["bearerAuth"]],
    "initiate_content_migration_group": [["OAuth2"], ["bearerAuth"]],
    "list_migration_systems_group": [["OAuth2"], ["bearerAuth"]],
    "list_migration_issues_group": [["OAuth2"], ["bearerAuth"]],
    "get_migration_issue_in_group": [["OAuth2"], ["bearerAuth"]],
    "resolve_migration_issue_group": [["OAuth2"], ["bearerAuth"]],
    "get_content_migration_group": [["OAuth2"], ["bearerAuth"]],
    "update_content_migration_group": [["OAuth2"], ["bearerAuth"]],
    "list_discussion_topics_group": [["OAuth2"], ["bearerAuth"]],
    "create_discussion_topic_group": [["OAuth2"], ["bearerAuth"]],
    "reorder_pinned_discussion_topics_group": [["OAuth2"], ["bearerAuth"]],
    "get_discussion_topic_group": [["OAuth2"], ["bearerAuth"]],
    "update_discussion_topic_group": [["OAuth2"], ["bearerAuth"]],
    "delete_discussion_topic_group": [["OAuth2"], ["bearerAuth"]],
    "list_discussion_entries_group": [["OAuth2"], ["bearerAuth"]],
    "create_discussion_entry_group": [["OAuth2"], ["bearerAuth"]],
    "rate_discussion_entry_group": [["OAuth2"], ["bearerAuth"]],
    "mark_discussion_entry_as_read_in_group": [["OAuth2"], ["bearerAuth"]],
    "mark_discussion_entry_unread_group": [["OAuth2"], ["bearerAuth"]],
    "list_discussion_replies_group": [["OAuth2"], ["bearerAuth"]],
    "create_discussion_reply_group": [["OAuth2"], ["bearerAuth"]],
    "update_discussion_entry_group": [["OAuth2"], ["bearerAuth"]],
    "delete_discussion_entry_group": [["OAuth2"], ["bearerAuth"]],
    "list_discussion_entries_group_by_ids": [["OAuth2"], ["bearerAuth"]],
    "mark_discussion_topic_as_read_group": [["OAuth2"], ["bearerAuth"]],
    "mark_discussion_topic_unread": [["OAuth2"], ["bearerAuth"]],
    "mark_discussion_entries_as_read": [["OAuth2"], ["bearerAuth"]],
    "mark_all_discussion_entries_as_unread": [["OAuth2"], ["bearerAuth"]],
    "subscribe_to_discussion_topic_group": [["OAuth2"], ["bearerAuth"]],
    "unsubscribe_from_discussion_topic_group": [["OAuth2"], ["bearerAuth"]],
    "get_discussion_topic_group_view": [["OAuth2"], ["bearerAuth"]],
    "list_external_feeds_group": [["OAuth2"], ["bearerAuth"]],
    "create_external_feed_group": [["OAuth2"], ["bearerAuth"]],
    "delete_external_feed": [["OAuth2"], ["bearerAuth"]],
    "list_external_tools_group": [["OAuth2"], ["bearerAuth"]],
    "upload_file_group": [["OAuth2"], ["bearerAuth"]],
    "get_group_quota": [["OAuth2"], ["bearerAuth"]],
    "get_file_group": [["OAuth2"], ["bearerAuth"]],
    "list_folders_group": [["OAuth2"], ["bearerAuth"]],
    "create_folder_group": [["OAuth2"], ["bearerAuth"]],
    "list_folder_path_group": [["OAuth2"], ["bearerAuth"]],
    "get_folder_group": [["OAuth2"], ["bearerAuth"]],
    "get_group_front_page": [["OAuth2"], ["bearerAuth"]],
    "update_group_front_page": [["OAuth2"], ["bearerAuth"]],
    "send_group_invitations": [["OAuth2"], ["bearerAuth"]],
    "list_group_members": [["OAuth2"], ["bearerAuth"]],
    "join_group": [["OAuth2"], ["bearerAuth"]],
    "get_group_membership": [["OAuth2"], ["bearerAuth"]],
    "update_group_membership": [["OAuth2"], ["bearerAuth"]],
    "leave_group": [["OAuth2"], ["bearerAuth"]],
    "list_pages": [["OAuth2"], ["bearerAuth"]],
    "create_wiki_page_group": [["OAuth2"], ["bearerAuth"]],
    "get_page": [["OAuth2"], ["bearerAuth"]],
    "update_wiki_page_group": [["OAuth2"], ["bearerAuth"]],
    "delete_wiki_page": [["OAuth2"], ["bearerAuth"]],
    "list_page_revisions_group": [["OAuth2"], ["bearerAuth"]],
    "get_page_revision_latest_group": [["OAuth2"], ["bearerAuth"]],
    "get_page_revision_group": [["OAuth2"], ["bearerAuth"]],
    "revert_page_to_revision_group": [["OAuth2"], ["bearerAuth"]],
    "check_group_permissions": [["OAuth2"], ["bearerAuth"]],
    "list_potential_collaborators": [["OAuth2"], ["bearerAuth"]],
    "preview_group_html": [["OAuth2"], ["bearerAuth"]],
    "list_group_tabs": [["OAuth2"], ["bearerAuth"]],
    "assign_file_usage_rights": [["OAuth2"], ["bearerAuth"]],
    "remove_usage_rights": [["OAuth2"], ["bearerAuth"]],
    "list_group_users": [["OAuth2"], ["bearerAuth"]],
    "get_group_membership_user": [["OAuth2"], ["bearerAuth"]],
    "update_group_membership_user": [["OAuth2"], ["bearerAuth"]],
    "remove_user_from_group": [["OAuth2"], ["bearerAuth"]],
    "get_outcome": [["OAuth2"], ["bearerAuth"]],
    "update_outcome": [["OAuth2"], ["bearerAuth"]],
    "list_planner_items": [["OAuth2"], ["bearerAuth"]],
    "list_planner_overrides": [["OAuth2"], ["bearerAuth"]],
    "override_planner_item": [["OAuth2"], ["bearerAuth"]],
    "get_planner_override": [["OAuth2"], ["bearerAuth"]],
    "update_planner_override": [["OAuth2"], ["bearerAuth"]],
    "delete_override": [["OAuth2"], ["bearerAuth"]],
    "list_notes": [["OAuth2"], ["bearerAuth"]],
    "create_planner_note": [["OAuth2"], ["bearerAuth"]],
    "get_planner_note": [["OAuth2"], ["bearerAuth"]],
    "update_planner_note": [["OAuth2"], ["bearerAuth"]],
    "delete_note": [["OAuth2"], ["bearerAuth"]],
    "list_closed_poll_sessions": [["OAuth2"], ["bearerAuth"]],
    "list_poll_sessions": [["OAuth2"], ["bearerAuth"]],
    "list_polls": [["OAuth2"], ["bearerAuth"]],
    "create_poll": [["OAuth2"], ["bearerAuth"]],
    "get_poll": [["OAuth2"], ["bearerAuth"]],
    "update_poll": [["OAuth2"], ["bearerAuth"]],
    "delete_poll": [["OAuth2"], ["bearerAuth"]],
    "list_poll_choices": [["OAuth2"], ["bearerAuth"]],
    "add_poll_choice": [["OAuth2"], ["bearerAuth"]],
    "get_poll_choice": [["OAuth2"], ["bearerAuth"]],
    "update_poll_choice": [["OAuth2"], ["bearerAuth"]],
    "delete_poll_choice": [["OAuth2"], ["bearerAuth"]],
    "list_poll_sessions_by_poll": [["OAuth2"], ["bearerAuth"]],
    "create_poll_session": [["OAuth2"], ["bearerAuth"]],
    "get_poll_session_results": [["OAuth2"], ["bearerAuth"]],
    "update_poll_session": [["OAuth2"], ["bearerAuth"]],
    "delete_poll_session": [["OAuth2"], ["bearerAuth"]],
    "close_poll_session": [["OAuth2"], ["bearerAuth"]],
    "open_poll_session": [["OAuth2"], ["bearerAuth"]],
    "submit_poll_response": [["OAuth2"], ["bearerAuth"]],
    "get_poll_submission": [["OAuth2"], ["bearerAuth"]],
    "get_job_progress": [["OAuth2"], ["bearerAuth"]],
    "list_quiz_submission_questions": [["OAuth2"], ["bearerAuth"]],
    "submit_quiz_answers": [["OAuth2"], ["bearerAuth"]],
    "flag_question": [["OAuth2"], ["bearerAuth"]],
    "remove_question_flag": [["OAuth2"], ["bearerAuth"]],
    "search_courses": [["OAuth2"], ["bearerAuth"]],
    "search_recipients": [["OAuth2"], ["bearerAuth"]],
    "get_assignment_override_for_section": [["OAuth2"], ["bearerAuth"]],
    "get_section_standalone": [["OAuth2"], ["bearerAuth"]],
    "update_section": [["OAuth2"], ["bearerAuth"]],
    "delete_section": [["OAuth2"], ["bearerAuth"]],
    "remove_section_crosslist": [["OAuth2"], ["bearerAuth"]],
    "move_section_to_course": [["OAuth2"], ["bearerAuth"]],
    "list_peer_reviews_section": [["OAuth2"], ["bearerAuth"]],
    "get_submission_summary": [["OAuth2"], ["bearerAuth"]],
    "list_assignment_submissions_section": [["OAuth2"], ["bearerAuth"]],
    "submit_assignment_section": [["OAuth2"], ["bearerAuth"]],
    "grade_submissions_section": [["OAuth2"], ["bearerAuth"]],
    "list_peer_reviews_section_submission": [["OAuth2"], ["bearerAuth"]],
    "assign_peer_reviewer_section": [["OAuth2"], ["bearerAuth"]],
    "remove_peer_review_section": [["OAuth2"], ["bearerAuth"]],
    "get_submission_by_user_section": [["OAuth2"], ["bearerAuth"]],
    "grade_submission_section": [["OAuth2"], ["bearerAuth"]],
    "upload_submission_file_section": [["OAuth2"], ["bearerAuth"]],
    "mark_submission_as_read_section": [["OAuth2"], ["bearerAuth"]],
    "mark_submission_unread": [["OAuth2"], ["bearerAuth"]],
    "list_section_enrollments": [["OAuth2"], ["bearerAuth"]],
    "enroll_user_in_section": [["OAuth2"], ["bearerAuth"]],
    "list_submissions_section": [["OAuth2"], ["bearerAuth"]],
    "update_submission_grades": [["OAuth2"], ["bearerAuth"]],
    "create_kaltura_session": [["OAuth2"], ["bearerAuth"]],
    "revoke_brand_config_share": [["OAuth2"], ["bearerAuth"]],
    "list_activity_stream": [["OAuth2"], ["bearerAuth"]],
    "list_activity_stream_current_user": [["OAuth2"], ["bearerAuth"]],
    "hide_all_activity_stream_items": [["OAuth2"], ["bearerAuth"]],
    "get_activity_stream_summary": [["OAuth2"], ["bearerAuth"]],
    "hide_activity_stream_item": [["OAuth2"], ["bearerAuth"]],
    "list_bookmarks": [["OAuth2"], ["bearerAuth"]],
    "create_bookmark": [["OAuth2"], ["bearerAuth"]],
    "get_bookmark": [["OAuth2"], ["bearerAuth"]],
    "update_bookmark": [["OAuth2"], ["bearerAuth"]],
    "delete_bookmark": [["OAuth2"], ["bearerAuth"]],
    "delete_push_notification_endpoint": [["OAuth2"], ["bearerAuth"]],
    "update_notification_preference": [["OAuth2"], ["bearerAuth"]],
    "list_course_nicknames": [["OAuth2"], ["bearerAuth"]],
    "delete_course_nicknames": [["OAuth2"], ["bearerAuth"]],
    "get_course_nickname": [["OAuth2"], ["bearerAuth"]],
    "set_course_nickname": [["OAuth2"], ["bearerAuth"]],
    "delete_course_nickname": [["OAuth2"], ["bearerAuth"]],
    "list_favorite_courses": [["OAuth2"], ["bearerAuth"]],
    "reset_course_favorites": [["OAuth2"], ["bearerAuth"]],
    "favorite_course": [["OAuth2"], ["bearerAuth"]],
    "unfavorite_course": [["OAuth2"], ["bearerAuth"]],
    "list_favorite_groups": [["OAuth2"], ["bearerAuth"]],
    "clear_group_favorites": [["OAuth2"], ["bearerAuth"]],
    "favorite_group": [["OAuth2"], ["bearerAuth"]],
    "unfavorite_group": [["OAuth2"], ["bearerAuth"]],
    "list_groups": [["OAuth2"], ["bearerAuth"]],
    "list_todos": [["OAuth2"], ["bearerAuth"]],
    "get_todo_item_counts": [["OAuth2"], ["bearerAuth"]],
    "list_upcoming_events": [["OAuth2"], ["bearerAuth"]],
    "get_user_permissions": [["OAuth2"], ["bearerAuth"]],
    "update_user": [["OAuth2"], ["bearerAuth"]],
    "list_user_colors": [["OAuth2"], ["bearerAuth"]],
    "get_custom_color": [["OAuth2"], ["bearerAuth"]],
    "set_custom_color": [["OAuth2"], ["bearerAuth"]],
    "merge_user_into_another_user": [["OAuth2"], ["bearerAuth"]],
    "merge_user": [["OAuth2"], ["bearerAuth"]],
    "split_user": [["OAuth2"], ["bearerAuth"]],
    "list_avatars": [["OAuth2"], ["bearerAuth"]],
    "list_calendar_events": [["OAuth2"], ["bearerAuth"]],
    "list_communication_channels": [["OAuth2"], ["bearerAuth"]],
    "add_communication_channel": [["OAuth2"], ["bearerAuth"]],
    "list_notification_preference_categories": [["OAuth2"], ["bearerAuth"]],
    "list_notification_preferences": [["OAuth2"], ["bearerAuth"]],
    "get_notification_preference": [["OAuth2"], ["bearerAuth"]],
    "delete_communication_channel": [["OAuth2"], ["bearerAuth"]],
    "delete_communication_channel_by_address": [["OAuth2"], ["bearerAuth"]],
    "list_notification_preferences_by_type": [["OAuth2"], ["bearerAuth"]],
    "get_notification_preference_by_address": [["OAuth2"], ["bearerAuth"]],
    "list_content_exports_user": [["OAuth2"], ["bearerAuth"]],
    "initiate_content_export": [["OAuth2"], ["bearerAuth"]],
    "get_content_export_user": [["OAuth2"], ["bearerAuth"]],
    "list_content_licenses_user": [["OAuth2"], ["bearerAuth"]],
    "list_content_migrations_user": [["OAuth2"], ["bearerAuth"]],
    "initiate_content_migration_user": [["OAuth2"], ["bearerAuth"]],
    "list_migration_systems_user": [["OAuth2"], ["bearerAuth"]],
    "list_migration_issues_user": [["OAuth2"], ["bearerAuth"]],
    "get_migration_issue_in_user": [["OAuth2"], ["bearerAuth"]],
    "resolve_migration_issue_user": [["OAuth2"], ["bearerAuth"]],
    "get_content_migration_user": [["OAuth2"], ["bearerAuth"]],
    "update_content_migration_user": [["OAuth2"], ["bearerAuth"]],
    "list_courses_by_user": [["OAuth2"], ["bearerAuth"]],
    "list_assignments_by_user": [["OAuth2"], ["bearerAuth"]],
    "retrieve_custom_data": [["OAuth2"], ["bearerAuth"]],
    "store_custom_data": [["OAuth2"], ["bearerAuth"]],
    "delete_custom_data": [["OAuth2"], ["bearerAuth"]],
    "list_user_enrollments": [["OAuth2"], ["bearerAuth"]],
    "list_user_features": [["OAuth2"], ["bearerAuth"]],
    "list_enabled_features_user": [["OAuth2"], ["bearerAuth"]],
    "get_feature_flag_user": [["OAuth2"], ["bearerAuth"]],
    "upload_file_personal": [["OAuth2"], ["bearerAuth"]],
    "get_user_storage_quota": [["OAuth2"], ["bearerAuth"]],
    "get_file_user": [["OAuth2"], ["bearerAuth"]],
    "list_folders_user": [["OAuth2"], ["bearerAuth"]],
    "create_folder_user": [["OAuth2"], ["bearerAuth"]],
    "get_folder_path_user": [["OAuth2"], ["bearerAuth"]],
    "get_folder_user": [["OAuth2"], ["bearerAuth"]],
    "list_logins_user": [["OAuth2"], ["bearerAuth"]],
    "delete_login": [["OAuth2"], ["bearerAuth"]],
    "list_overdue_assignments": [["OAuth2"], ["bearerAuth"]],
    "list_observees": [["OAuth2"], ["bearerAuth"]],
    "create_observee": [["OAuth2"], ["bearerAuth"]],
    "get_observee": [["OAuth2"], ["bearerAuth"]],
    "create_observation_link": [["OAuth2"], ["bearerAuth"]],
    "unobserve_user": [["OAuth2"], ["bearerAuth"]],
    "list_page_views": [["OAuth2"], ["bearerAuth"]],
    "get_user_profile": [["OAuth2"], ["bearerAuth"]],
    "assign_usage_rights": [["OAuth2"], ["bearerAuth"]],
    "remove_file_usage_rights_user": [["OAuth2"], ["bearerAuth"]]
}

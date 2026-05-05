"""
Authentication module for Klaviyo MCP server.

Generated: 2026-05-05 15:22:41 UTC
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
    OAuth 2.0 authentication for Klaviyo API.

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
        Authorization URL: https://www.klaviyo.com/oauth/authorize
        Token URL: https://a.klaviyo.com/oauth/token

    Available Scopes (configure via OAUTH2_SCOPES):
        - accounts:read
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
        self.token_url = self._resolve_url_template("https://a.klaviyo.com/oauth/token")
        self.auth_url = self._resolve_url_template("https://www.klaviyo.com/oauth/authorize")
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

class APIKeyAuth:
    """
    API Key authentication for Klaviyo API.

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
    "get_accounts": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_account": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_campaigns": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_campaign": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_campaign": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_campaign": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_campaign_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_campaign_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_campaign_send_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_campaign_send_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_campaign_recipient_estimation_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_campaign_recipient_estimation": [["OAuth2"], ["Klaviyo-API-Key"]],
    "clone_campaign": [["OAuth2"], ["Klaviyo-API-Key"]],
    "assign_template_to_campaign_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "send_campaign": [["OAuth2"], ["Klaviyo-API-Key"]],
    "trigger_campaign_recipient_estimation": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_campaign_for_campaign_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_campaign_id_for_campaign_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_template_for_campaign_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_template_id_for_campaign_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_image_for_campaign_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_image_id_for_campaign_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_image_for_campaign_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_tags_for_campaign": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_tag_ids_for_campaign": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_messages_for_campaign": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_message_ids_for_campaign": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_catalog_items": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_item": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_catalog_item": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_catalog_item": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_catalog_item": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_catalog_variants": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_variant": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_catalog_variant": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_catalog_variant": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_catalog_variant": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_catalog_categories": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_category": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_catalog_category": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_catalog_category": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_catalog_category": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_bulk_create_catalog_items_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_items_bulk_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_create_catalog_items_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_catalog_item_bulk_update_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_item_bulk_update_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_update_catalog_items_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_bulk_delete_catalog_items_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_item_bulk_delete_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_delete_catalog_items_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_bulk_create_variants_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_variants_bulk": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_create_variants_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_bulk_update_variants_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_variant_bulk_update_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_update_variants_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_bulk_delete_variants_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_variant_bulk_delete_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_delete_variants_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_bulk_create_categories_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_categories_bulk_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_create_categories_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_bulk_update_categories_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_category_bulk_update_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_update_categories_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_bulk_delete_categories_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_catalog_category_bulk_delete_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_delete_categories_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_back_in_stock_subscription": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_items_for_catalog_category": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_item_ids_for_catalog_category": [["OAuth2"], ["Klaviyo-API-Key"]],
    "add_items_to_catalog_category": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_items_for_catalog_category": [["OAuth2"], ["Klaviyo-API-Key"]],
    "remove_items_from_catalog_category": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_variants_for_catalog_item": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_variant_ids_for_catalog_item": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_categories_for_catalog_item": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_category_ids_for_catalog_item": [["OAuth2"], ["Klaviyo-API-Key"]],
    "add_categories_to_catalog_item": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_categories_for_catalog_item": [["OAuth2"], ["Klaviyo-API-Key"]],
    "remove_categories_from_catalog_item": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_coupons": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_coupon": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_coupon": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_coupon": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_coupon": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_coupon_codes": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_coupon_code": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_coupon_code": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_coupon_code": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_coupon_code": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_coupon_code_bulk_create_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_coupon_code_bulk_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_coupon_code_bulk_create_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_coupon_for_coupon_code": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_coupon_relationship_for_coupon_code": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_coupon_codes_for_coupon": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_coupon_code_ids_for_coupon": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_data_sources": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_data_source": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_data_source": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_data_source": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_data_source_records_bulk": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_data_source_record": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_profile_deletion_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_events": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_event": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_event": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_events_bulk": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_metric_for_event": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_metrics_for_event": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_profile_for_event": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_profile_id_for_event": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_flows": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_flow": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_flow_status": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_flow": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_flow_action": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_flow_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_actions_for_flow": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_action_ids_for_flow": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_tags_for_flow": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_tag_ids_for_flow": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_flow_for_flow_action": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_flow_relationship_for_flow_action": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_flow_action_messages": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_message_ids_for_flow_action": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_flow_action_for_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_flow_action_for_flow_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_template_for_flow_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_template_id_for_flow_message": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_forms": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_form": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_form": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_form": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_form_version": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_versions_for_form": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_version_ids_for_form": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_form_for_form_version": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_form_id_for_form_version": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_images": [["OAuth2"], ["Klaviyo-API-Key"]],
    "import_image_from_url": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_image": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_image": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_image_from_file": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_lists": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_tags_for_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_tag_ids_for_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_profiles_for_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_profile_ids_for_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "add_profiles_to_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "remove_profiles_from_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_flows_triggered_by_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_flow_trigger_ids_for_list": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_metrics": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_metric_property": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_custom_metrics": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_custom_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_custom_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_custom_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_custom_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_mapped_metrics": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_mapped_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_mapped_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "query_metric_aggregates": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_flows_triggered_by_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_flow_ids_triggered_by_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_metric_properties": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_property_ids_for_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_metric_for_metric_property": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_metric_id_for_metric_property": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_metrics_for_custom_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_metrics_for_custom_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_metric_for_mapped_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_metric_id_for_mapped_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_custom_metric_for_mapped_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_custom_metric_id_for_mapped_metric": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_profiles": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_profile": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_profile": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_profile": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_bulk_import_profiles_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_profile_bulk_import_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_import_profiles_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_bulk_suppress_profiles_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_profile_suppression_bulk_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_suppress_profiles_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_bulk_unsuppress_profiles_jobs": [["OAuth2"], ["Klaviyo-API-Key"]],
    "remove_profile_suppressions_bulk": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_bulk_unsuppress_profiles_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_push_tokens": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_or_update_push_token": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_push_token": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_push_token": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_or_update_profile": [["OAuth2"], ["Klaviyo-API-Key"]],
    "merge_profiles": [["OAuth2"], ["Klaviyo-API-Key"]],
    "subscribe_profiles_bulk": [["OAuth2"], ["Klaviyo-API-Key"]],
    "unsubscribe_profiles_bulk": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_push_tokens_for_profile": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_push_token_ids_for_profile": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_lists_for_profile": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_lists_for_profile_relationship": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_segments_for_profile": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_segment_ids_for_profile": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_lists_for_bulk_import_profiles_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_list_ids_for_bulk_import_profiles_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_profiles_for_bulk_import_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_profile_ids_for_bulk_import_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_import_errors_for_bulk_import_profiles_job": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_profile_for_push_token": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_profile_id_for_push_token": [["OAuth2"], ["Klaviyo-API-Key"]],
    "query_campaign_values_report": [["OAuth2"], ["Klaviyo-API-Key"]],
    "query_flow_values_report": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_flow_series_analytics": [["OAuth2"], ["Klaviyo-API-Key"]],
    "query_form_values_report": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_form_series_analytics": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_segment_values_report": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_segment_series_report": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_reviews": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_review": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_review": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_segments": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_segment": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_segment": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_segment": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_segment": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_tags_for_segment": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_tag_ids_for_segment": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_profiles_for_segment": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_profile_ids_for_segment": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_flows_triggered_by_segment": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_flow_ids_triggered_by_segment": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_tags": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_tag_groups": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_tag_group": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_tag_group": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_tag_group": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_tag_group": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_flows_for_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "add_flows_to_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "remove_tag_from_flows": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_campaign_ids_for_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "add_campaigns_to_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "remove_tag_from_campaigns": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_lists_for_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "associate_lists_with_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "remove_tag_from_lists": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_segment_ids_for_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "add_segments_to_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "remove_tag_from_segments": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_tag_group_for_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_tag_group_id_for_tag": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_tags_for_tag_group": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_tag_ids_for_tag_group": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_templates": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_template": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_template": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_template": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_template": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_universal_content": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_universal_content": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_universal_content": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_template_universal_content": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_universal_content": [["OAuth2"], ["Klaviyo-API-Key"]],
    "render_template": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_template_clone": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_tracking_settings": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_tracking_setting": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_web_feeds": [["OAuth2"], ["Klaviyo-API-Key"]],
    "create_web_feed": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_web_feed": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_web_feed": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_web_feed": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_webhooks": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_webhook": [["OAuth2"], ["Klaviyo-API-Key"]],
    "update_webhook": [["OAuth2"], ["Klaviyo-API-Key"]],
    "delete_webhook": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_webhook_topics": [["OAuth2"], ["Klaviyo-API-Key"]],
    "get_webhook_topic": [["OAuth2"], ["Klaviyo-API-Key"]],
    "list_client_review_values_reports": [["Klaviyo-API-Key"], ["OAuth2"]],
    "list_client_reviews": [["Klaviyo-API-Key"], ["OAuth2"]],
    "create_client_review": [["Klaviyo-API-Key"], ["OAuth2"]],
    "create_client_subscription": [["Klaviyo-API-Key"], ["OAuth2"]],
    "create_or_update_client_profile": [["Klaviyo-API-Key"], ["OAuth2"]],
    "subscribe_profile_to_back_in_stock_notifications": [["Klaviyo-API-Key"], ["OAuth2"]]
}

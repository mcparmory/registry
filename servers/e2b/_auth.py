"""
Authentication module for E2B MCP server.

Generated: 2026-04-14 18:20:03 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)

This module contains:
1. Authentication class implementations (OAuth2)
2. Operation-to-auth requirements mapping (OPERATION_AUTH_MAP)
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

__all__ = [
    "APIKeyAuth",
    "BearerTokenAuth",
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Authentication Classes
# ============================================================================

class APIKeyAuth:
    """
    API Key authentication for E2B API.

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

class BearerTokenAuth:
    """
    Bearer token authentication for E2B API.

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
    "list_teams": [["AccessTokenAuth"], ["Supabase1TokenAuth"]],
    "get_team_metrics": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "get_team_metrics_maximum": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "create_sandbox": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "list_sandboxes": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "list_sandbox_metrics": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "list_sandbox_logs": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "get_sandbox": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "terminate_sandbox": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "get_sandbox_metrics": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "pause_sandbox": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "connect_sandbox": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "set_sandbox_timeout": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "refresh_sandbox": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "create_sandbox_snapshot": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "list_snapshots": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "create_template": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "get_template_files_upload_link": [["AccessTokenAuth"], ["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "list_templates": [["AccessTokenAuth"], ["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "list_template_builds": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "delete_template": [["AccessTokenAuth"], ["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "start_template_build": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "update_template": [["AccessTokenAuth"], ["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "get_template_build_status": [["AccessTokenAuth"], ["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "list_template_build_logs": [["AccessTokenAuth"], ["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "assign_template_tags": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "remove_template_tags": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "list_template_tags": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "check_template_alias": [["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "list_nodes": [["AdminTokenAuth"]],
    "get_node": [["AdminTokenAuth"]],
    "update_node_status": [["AdminTokenAuth"]],
    "terminate_team_sandboxes": [["AdminTokenAuth"]],
    "create_access_token": [["Supabase1TokenAuth"]],
    "revoke_access_token": [["Supabase1TokenAuth"]],
    "list_api_keys": [["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "create_api_key": [["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "update_api_key": [["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "delete_api_key": [["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "list_volumes": [["AccessTokenAuth"], ["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "create_volume": [["AccessTokenAuth"], ["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "get_volume": [["AccessTokenAuth"], ["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]],
    "delete_volume": [["AccessTokenAuth"], ["ApiKeyAuth"], ["Supabase1TokenAuth", "Supabase2TeamAuth"]]
}

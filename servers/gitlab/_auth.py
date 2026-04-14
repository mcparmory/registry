"""
Authentication module for GitLab MCP server.

Generated: 2026-04-14 18:22:56 UTC
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
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Authentication Classes
# ============================================================================

class APIKeyAuth:
    """
    API Key authentication for GitLab API.

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
    "get_group_badge": [["ApiKeyAuth"]],
    "update_group_badge": [["ApiKeyAuth"]],
    "remove_group_badge": [["ApiKeyAuth"]],
    "list_group_badges": [["ApiKeyAuth"]],
    "add_group_badge": [["ApiKeyAuth"]],
    "deny_group_access_request": [["ApiKeyAuth"]],
    "approve_group_access_request": [["ApiKeyAuth"]],
    "list_group_access_requests": [["ApiKeyAuth"]],
    "request_group_access": [["ApiKeyAuth"]],
    "delete_merged_branches": [["ApiKeyAuth"]],
    "get_branch": [["ApiKeyAuth"]],
    "delete_branch": [["ApiKeyAuth"]],
    "check_branch_exists": [["ApiKeyAuth"]],
    "list_repository_branches": [["ApiKeyAuth"]],
    "create_branch": [["ApiKeyAuth"]],
    "unprotect_branch": [["ApiKeyAuth"]],
    "protect_branch": [["ApiKeyAuth"]],
    "get_project_badge": [["ApiKeyAuth"]],
    "update_project_badge": [["ApiKeyAuth"]],
    "delete_badge": [["ApiKeyAuth"]],
    "list_project_badges": [["ApiKeyAuth"]],
    "create_project_badge": [["ApiKeyAuth"]],
    "deny_access_request": [["ApiKeyAuth"]],
    "approve_access_request": [["ApiKeyAuth"]],
    "list_access_requests": [["ApiKeyAuth"]],
    "request_project_access": [["ApiKeyAuth"]],
    "update_alert_metric_image": [["ApiKeyAuth"]],
    "delete_alert_metric_image": [["ApiKeyAuth"]],
    "list_alert_metric_images": [["ApiKeyAuth"]],
    "upload_alert_metric_image": [["ApiKeyAuth"]],
    "pause_batched_background_migration": [["ApiKeyAuth"]],
    "get_admin_ci_variable": [["ApiKeyAuth"]],
    "delete_instance_variable": [["ApiKeyAuth"]],
    "list_instance_variables": [["ApiKeyAuth"]],
    "create_instance_variable": [["ApiKeyAuth"]],
    "get_cluster": [["ApiKeyAuth"]],
    "update_cluster": [["ApiKeyAuth"]],
    "delete_cluster": [["ApiKeyAuth"]],
    "add_kubernetes_cluster": [["ApiKeyAuth"]],
    "list_clusters": [["ApiKeyAuth"]],
    "delete_application": [["ApiKeyAuth"]],
    "get_user_avatar": [["ApiKeyAuth"]],
    "get_broadcast_message": [["ApiKeyAuth"]],
    "delete_broadcast_message": [["ApiKeyAuth"]],
    "get_migration_entity": [["ApiKeyAuth"]],
    "list_migration_entities": [["ApiKeyAuth"]],
    "get_bulk_import": [["ApiKeyAuth"]],
    "list_migration_entities_all": [["ApiKeyAuth"]],
    "list_migrations": [["ApiKeyAuth"]],
    "start_bulk_migration": [["ApiKeyAuth"]],
    "list_jobs": [["ApiKeyAuth"]],
    "get_job": [["ApiKeyAuth"]],
    "execute_manual_job": [["ApiKeyAuth"]]
}

"""
Authentication module for Postman MCP server.

Generated: 2026-04-23 21:41:31 UTC
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
    API Key authentication for Postman API.

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
    "list_apis": [["ApiKeyAuth"]],
    "create_api": [["ApiKeyAuth"]],
    "get_api": [["ApiKeyAuth"]],
    "update_api": [["ApiKeyAuth"]],
    "delete_api": [["ApiKeyAuth"]],
    "list_api_versions": [["ApiKeyAuth"]],
    "create_api_version": [["ApiKeyAuth"]],
    "get_api_version": [["ApiKeyAuth"]],
    "update_api_version": [["ApiKeyAuth"]],
    "delete_api_version": [["ApiKeyAuth"]],
    "list_contract_test_relations": [["ApiKeyAuth"]],
    "get_documentation_relations": [["ApiKeyAuth"]],
    "get_environment_relations_for_api_version": [["ApiKeyAuth"]],
    "list_integration_test_relations": [["ApiKeyAuth"]],
    "list_monitor_relations": [["ApiKeyAuth"]],
    "list_linked_relations": [["ApiKeyAuth"]],
    "add_relations_to_api_version": [["ApiKeyAuth"]],
    "create_schema": [["ApiKeyAuth"]],
    "get_schema": [["ApiKeyAuth"]],
    "update_schema": [["ApiKeyAuth"]],
    "create_collection_from_schema": [["ApiKeyAuth"]],
    "list_test_suite_relations": [["ApiKeyAuth"]],
    "sync_relation_with_schema": [["ApiKeyAuth"]],
    "list_collections": [["ApiKeyAuth"]],
    "create_collection": [["ApiKeyAuth"]],
    "create_fork_of_collection": [["ApiKeyAuth"]],
    "merge_fork_to_collection": [["ApiKeyAuth"]],
    "get_collection": [["ApiKeyAuth"]],
    "update_collection": [["ApiKeyAuth"]],
    "delete_collection": [["ApiKeyAuth"]],
    "list_environments": [["ApiKeyAuth"]],
    "create_environment": [["ApiKeyAuth"]],
    "get_environment": [["ApiKeyAuth"]],
    "update_environment": [["ApiKeyAuth"]],
    "delete_environment": [["ApiKeyAuth"]],
    "get_authenticated_user": [["ApiKeyAuth"]],
    "list_mocks": [["ApiKeyAuth"]],
    "create_mock": [["ApiKeyAuth"]],
    "get_mock": [["ApiKeyAuth"]],
    "update_mock": [["ApiKeyAuth"]],
    "delete_mock": [["ApiKeyAuth"]],
    "publish_mock": [["ApiKeyAuth"]],
    "delete_mock_publication": [["ApiKeyAuth"]],
    "list_monitors": [["ApiKeyAuth"]],
    "create_monitor": [["ApiKeyAuth"]],
    "get_monitor": [["ApiKeyAuth"]],
    "update_monitor": [["ApiKeyAuth"]],
    "delete_monitor": [["ApiKeyAuth"]],
    "run_monitor": [["ApiKeyAuth"]],
    "create_webhook": [["ApiKeyAuth"]],
    "list_workspaces": [["ApiKeyAuth"]],
    "create_workspace": [["ApiKeyAuth"]],
    "get_workspace": [["ApiKeyAuth"]],
    "update_workspace": [["ApiKeyAuth"]],
    "delete_workspace": [["ApiKeyAuth"]]
}

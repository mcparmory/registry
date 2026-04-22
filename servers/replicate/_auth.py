"""
Authentication module for Replicate MCP server.

Generated: 2026-04-22 21:49:25 UTC
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
    "BearerTokenAuth",
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Authentication Classes
# ============================================================================

class BearerTokenAuth:
    """
    Bearer token authentication for Replicate HTTP API.

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
    "get_account": [["bearerAuth"]],
    "list_collections": [["bearerAuth"]],
    "get_collection": [["bearerAuth"]],
    "list_deployments": [["bearerAuth"]],
    "create_deployment": [["bearerAuth"]],
    "get_deployment": [["bearerAuth"]],
    "update_deployment": [["bearerAuth"]],
    "delete_deployment": [["bearerAuth"]],
    "create_deployment_prediction": [["bearerAuth"]],
    "list_files": [["bearerAuth"]],
    "create_file": [["bearerAuth"]],
    "get_file": [["bearerAuth"]],
    "delete_file": [["bearerAuth"]],
    "get_file_download": [["bearerAuth"]],
    "list_available_hardware": [["bearerAuth"]],
    "list_models": [["bearerAuth"]],
    "create_model": [["bearerAuth"]],
    "search_models": [["bearerAuth"]],
    "get_model": [["bearerAuth"]],
    "update_model_metadata": [["bearerAuth"]],
    "delete_model": [["bearerAuth"]],
    "list_model_examples": [["bearerAuth"]],
    "create_prediction_for_official_model": [["bearerAuth"]],
    "get_model_readme": [["bearerAuth"]],
    "list_model_versions": [["bearerAuth"]],
    "get_model_version": [["bearerAuth"]],
    "delete_model_version": [["bearerAuth"]],
    "create_training": [["bearerAuth"]],
    "list_predictions": [["bearerAuth"]],
    "create_prediction": [["bearerAuth"]],
    "get_prediction": [["bearerAuth"]],
    "cancel_prediction": [["bearerAuth"]],
    "search_models_collections_and_docs": [["bearerAuth"]],
    "list_trainings": [["bearerAuth"]],
    "get_training": [["bearerAuth"]],
    "cancel_training": [["bearerAuth"]],
    "get_default_webhook_secret": [["bearerAuth"]]
}

"""
Authentication module for Mailtrap MCP server.

Generated: 2026-05-12 11:52:23 UTC
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
    Bearer token authentication for Email Sending.

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
    "list_sending_domains": [["BearerAuth"]],
    "create_sending_domain": [["BearerAuth"]],
    "get_sending_domain": [["BearerAuth"]],
    "delete_sending_domain": [["BearerAuth"]],
    "send_sending_domain_setup_instructions": [["BearerAuth"]],
    "list_suppressions": [["BearerAuth"]],
    "delete_suppression": [["BearerAuth"]],
    "get_account_sending_stats": [["BearerAuth"]],
    "get_account_sending_stats_by_domains": [["BearerAuth"]],
    "get_sending_stats_by_categories": [["BearerAuth"]],
    "get_account_sending_stats_by_email_service_providers": [["BearerAuth"]],
    "get_account_sending_stats_by_date": [["BearerAuth"]],
    "list_email_logs": [["BearerAuth"]],
    "get_email_log_message": [["BearerAuth"]]
}

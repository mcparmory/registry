"""
Authentication module for Customer.io Journeys Track MCP server.

Generated: 2026-05-12 11:10:46 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)

This module contains:
1. Authentication class implementations (OAuth2)
2. Operation-to-auth requirements mapping (OPERATION_AUTH_MAP)
"""

from __future__ import annotations

import base64
import logging
import os

logger = logging.getLogger(__name__)

__all__ = [
    "BasicAuth",
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Authentication Classes
# ============================================================================

class BasicAuth:
    """
    HTTP Basic Authentication for Journeys Track API.

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


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "get_account_region": [["Tracking-API-Key"]],
    "upsert_customer": [["Tracking-API-Key"]],
    "delete_customer": [["Tracking-API-Key"]],
    "register_device": [["Tracking-API-Key"]],
    "remove_device": [["Tracking-API-Key"]],
    "suppress_customer": [["Tracking-API-Key"]],
    "unsuppress_customer": [["Tracking-API-Key"]],
    "mark_delivery_unsubscribed": [["Tracking-API-Key"]],
    "track_customer_event": [["Tracking-API-Key"]],
    "log_anonymous_event": [["Tracking-API-Key"]],
    "submit_form": [["Tracking-API-Key"]],
    "merge_customers": [["Tracking-API-Key"]],
    "report_metric": [["Tracking-API-Key"]],
    "add_customers_to_segment": [["Tracking-API-Key"]],
    "remove_customers_from_segment": [["Tracking-API-Key"]],
    "manage_entity": [["Tracking-API-Key"]],
    "batch_entities": [["Tracking-API-Key"]]
}

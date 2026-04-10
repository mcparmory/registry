"""
Authentication module for NetLicensing MCP server.

Generated: 2026-04-09 17:28:31 UTC
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
    HTTP Basic Authentication for NetLicensing.

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
    "list_products": [["basicAuth"]],
    "create_product": [["basicAuth"]],
    "get_product": [["basicAuth"]],
    "update_product": [["basicAuth"]],
    "delete_product": [["basicAuth"]],
    "list_product_modules": [["basicAuth"]],
    "create_product_module": [["basicAuth"]],
    "get_product_module": [["basicAuth"]],
    "update_product_module": [["basicAuth"]],
    "delete_product_module": [["basicAuth"]],
    "list_license_templates": [["basicAuth"]],
    "create_license_template": [["basicAuth"]],
    "get_license_template": [["basicAuth"]],
    "update_license_template": [["basicAuth"]],
    "delete_license_template": [["basicAuth"]],
    "list_licensees": [["basicAuth"]],
    "create_licensee": [["basicAuth"]],
    "get_licensee": [["basicAuth"]],
    "update_licensee": [["basicAuth"]],
    "delete_licensee": [["basicAuth"]],
    "validate_licensee": [["basicAuth"]],
    "transfer_licenses_between_licensees": [["basicAuth"]],
    "list_licenses": [["basicAuth"]],
    "create_license": [["basicAuth"]],
    "get_license": [["basicAuth"]],
    "update_license": [["basicAuth"]],
    "delete_license": [["basicAuth"]],
    "list_transactions": [["basicAuth"]],
    "create_transaction": [["basicAuth"]],
    "get_transaction": [["basicAuth"]],
    "update_transaction": [["basicAuth"]],
    "list_tokens": [["basicAuth"]],
    "create_token": [["basicAuth"]],
    "get_token": [["basicAuth"]],
    "delete_token": [["basicAuth"]],
    "list_payment_methods": [["basicAuth"]],
    "get_payment_method": [["basicAuth"]],
    "update_payment_method": [["basicAuth"]],
    "list_licensing_models": [["basicAuth"]],
    "list_license_types": [["basicAuth"]]
}

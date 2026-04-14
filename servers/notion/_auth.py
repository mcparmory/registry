"""
Authentication module for Notion MCP server.

Generated: 2026-04-14 18:27:11 UTC
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
    "BearerTokenAuth",
    "BasicAuth",
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Authentication Classes
# ============================================================================

class BearerTokenAuth:
    """
    Bearer token authentication for Notion API.

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

class BasicAuth:
    """
    HTTP Basic Authentication for Notion API.

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
    "get_self": [["bearerAuth"]],
    "get_user": [["bearerAuth"]],
    "list_users": [["bearerAuth"]],
    "create_page": [["bearerAuth"]],
    "get_page": [["bearerAuth"]],
    "update_page": [["bearerAuth"]],
    "move_page": [["bearerAuth"]],
    "get_page_property": [["bearerAuth"]],
    "get_page_markdown": [["bearerAuth"]],
    "update_page_markdown": [["bearerAuth"]],
    "get_block": [["bearerAuth"]],
    "update_block": [["bearerAuth"]],
    "delete_block": [["bearerAuth"]],
    "list_block_children": [["bearerAuth"]],
    "append_block_children": [["bearerAuth"]],
    "get_data_source": [["bearerAuth"]],
    "update_data_source": [["bearerAuth"]],
    "query_data_source": [["bearerAuth"]],
    "create_data_source": [["bearerAuth"]],
    "list_data_source_templates": [["bearerAuth"]],
    "get_database": [["bearerAuth"]],
    "update_database": [["bearerAuth"]],
    "create_database": [["bearerAuth"]],
    "search_pages_by_property": [["bearerAuth"]],
    "list_comments": [["bearerAuth"]],
    "create_comment": [["bearerAuth"]],
    "get_comment": [["bearerAuth"]],
    "list_file_uploads": [["bearerAuth"]],
    "create_file_upload": [["bearerAuth"]],
    "send_file_upload": [["bearerAuth"]],
    "complete_file_upload": [["bearerAuth"]],
    "get_file_upload": [["bearerAuth"]],
    "list_custom_emojis": [["bearerAuth"]],
    "list_views": [["bearerAuth"]],
    "create_view": [["bearerAuth"]],
    "get_view": [["bearerAuth"]],
    "update_view": [["bearerAuth"]],
    "delete_view": [["bearerAuth"]],
    "create_view_query": [["bearerAuth"]],
    "get_view_query_results": [["bearerAuth"]],
    "delete_view_query": [["bearerAuth"]]
}

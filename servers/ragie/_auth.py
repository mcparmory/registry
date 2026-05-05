"""
Authentication module for Ragie MCP server.

Generated: 2026-05-05 16:03:55 UTC
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
    Bearer token authentication for Ragie API.

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
    "list_documents": [["auth"]],
    "create_document": [["auth"]],
    "create_document_from_text": [["auth"]],
    "ingest_document_from_url": [["auth"]],
    "get_document": [["auth"]],
    "delete_document": [["auth"]],
    "update_document_file": [["auth"]],
    "update_document_raw": [["auth"]],
    "update_document_from_url": [["auth"]],
    "update_document_metadata": [["auth"]],
    "list_document_chunks": [["auth"]],
    "get_document_chunk": [["auth"]],
    "get_document_chunk_content": [["auth"]],
    "get_document_content": [["auth"]],
    "get_document_source": [["auth"]],
    "search_document_chunks": [["auth"]],
    "get_document_summary": [["auth"]],
    "list_instructions": [["auth"]],
    "create_instruction": [["auth"]],
    "update_instruction": [["auth"]],
    "delete_instruction": [["auth"]],
    "list_entities_by_instruction": [["auth"]],
    "list_instruction_entity_extraction_logs": [["auth"]],
    "list_entities_by_document": [["auth"]],
    "create_connection": [["auth"]],
    "list_connections": [["auth"]],
    "create_oauth_redirect_url": [["auth"]],
    "list_connection_source_types": [["auth"]],
    "update_connection_enabled_status": [["auth"]],
    "get_connection": [["auth"]],
    "update_connection": [["auth"]],
    "get_connection_stats": [["auth"]],
    "update_connection_page_limit": [["auth"]],
    "delete_connection": [["auth"]],
    "trigger_connection_sync": [["auth"]],
    "list_webhook_endpoints": [["auth"]],
    "get_webhook_endpoint": [["auth"]],
    "update_webhook_endpoint": [["auth"]],
    "list_partitions": [["auth"]],
    "create_partition": [["auth"]],
    "get_partition": [["auth"]],
    "update_partition": [["auth"]],
    "delete_partition": [["auth"]],
    "update_partition_limits": [["auth"]],
    "list_authenticators": [["auth"]],
    "create_authenticator": [["auth"]],
    "create_authenticator_connection": [["auth"]],
    "delete_authenticator": [["auth"]],
    "create_response": [["auth"]],
    "get_response": [["auth"]],
    "list_document_elements": [["auth"]],
    "get_element": [["auth"]]
}

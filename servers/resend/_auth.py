"""
Authentication module for Resend MCP server.

Generated: 2026-05-12 12:27:18 UTC
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
    Bearer token authentication for Resend.

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
    "list_emails": [["bearerAuth"]],
    "send_email": [["bearerAuth"]],
    "get_email": [["bearerAuth"]],
    "cancel_email": [["bearerAuth"]],
    "send_emails_batch": [["bearerAuth"]],
    "list_attachments_for_email": [["bearerAuth"]],
    "get_email_attachment": [["bearerAuth"]],
    "list_emails_receiving": [["bearerAuth"]],
    "get_received_email": [["bearerAuth"]],
    "list_email_attachments": [["bearerAuth"]],
    "get_received_email_attachment": [["bearerAuth"]],
    "list_domains": [["bearerAuth"]],
    "create_domain": [["bearerAuth"]],
    "get_domain": [["bearerAuth"]],
    "update_domain": [["bearerAuth"]],
    "delete_domain": [["bearerAuth"]],
    "verify_domain": [["bearerAuth"]],
    "list_api_keys": [["bearerAuth"]],
    "create_api_key": [["bearerAuth"]],
    "delete_api_key": [["bearerAuth"]],
    "list_templates": [["bearerAuth"]],
    "create_template": [["bearerAuth"]],
    "get_template": [["bearerAuth"]],
    "update_template": [["bearerAuth"]],
    "delete_template": [["bearerAuth"]],
    "publish_template": [["bearerAuth"]],
    "duplicate_template": [["bearerAuth"]],
    "list_contacts": [["bearerAuth"]],
    "create_contact": [["bearerAuth"]],
    "get_contact": [["bearerAuth"]],
    "update_contact": [["bearerAuth"]],
    "delete_contact": [["bearerAuth"]],
    "list_broadcasts": [["bearerAuth"]],
    "create_broadcast": [["bearerAuth"]],
    "get_broadcast": [["bearerAuth"]],
    "update_broadcast": [["bearerAuth"]],
    "delete_broadcast": [["bearerAuth"]],
    "send_broadcast": [["bearerAuth"]],
    "list_webhooks": [["bearerAuth"]],
    "create_webhook": [["bearerAuth"]],
    "get_webhook": [["bearerAuth"]],
    "update_webhook": [["bearerAuth"]],
    "delete_webhook": [["bearerAuth"]],
    "list_segments": [["bearerAuth"]],
    "create_segment": [["bearerAuth"]],
    "get_segment": [["bearerAuth"]],
    "delete_segment": [["bearerAuth"]],
    "list_topics": [["bearerAuth"]],
    "create_topic": [["bearerAuth"]],
    "get_topic": [["bearerAuth"]],
    "update_topic": [["bearerAuth"]],
    "delete_topic": [["bearerAuth"]],
    "list_contact_properties": [["bearerAuth"]],
    "create_contact_property": [["bearerAuth"]],
    "get_contact_property": [["bearerAuth"]],
    "update_contact_property": [["bearerAuth"]],
    "delete_contact_property": [["bearerAuth"]],
    "list_contact_segments": [["bearerAuth"]],
    "add_contact_to_segment": [["bearerAuth"]],
    "remove_contact_from_segment": [["bearerAuth"]],
    "list_contact_topics": [["bearerAuth"]],
    "list_logs": [["bearerAuth"]],
    "get_log": [["bearerAuth"]]
}

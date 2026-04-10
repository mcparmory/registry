"""
Authentication module for Contentful Management MCP server.

Generated: 2026-04-09 17:18:29 UTC
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
    Bearer token authentication for Contentful Management.

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
    "list_spaces": [["bearerAuth"]],
    "create_space": [["bearerAuth"]],
    "get_space": [["bearerAuth"]],
    "delete_space": [["bearerAuth"]],
    "list_environments": [["bearerAuth"]],
    "create_environment": [["bearerAuth"]],
    "get_environment": [["bearerAuth"]],
    "update_environment": [["bearerAuth"]],
    "delete_environment": [["bearerAuth"]],
    "list_environment_aliases": [["bearerAuth"]],
    "get_environment_alias": [["bearerAuth"]],
    "create_or_update_environment_alias": [["bearerAuth"]],
    "delete_environment_alias": [["bearerAuth"]],
    "list_organizations": [["bearerAuth"]],
    "list_content_types": [["bearerAuth"]],
    "create_content_type": [["bearerAuth"]],
    "get_content_type": [["bearerAuth"]],
    "create_or_update_content_type": [["bearerAuth"]],
    "delete_content_type": [["bearerAuth"]],
    "publish_content_type": [["bearerAuth"]],
    "deactivate_content_type": [["bearerAuth"]],
    "list_content_types_published": [["bearerAuth"]],
    "list_extensions": [["bearerAuth"]],
    "get_extension": [["bearerAuth"]],
    "create_or_update_extension": [["bearerAuth"]],
    "delete_extension": [["bearerAuth"]],
    "list_entries": [["bearerAuth"]],
    "create_entry": [["bearerAuth"]],
    "get_entry": [["bearerAuth"]],
    "upsert_entry": [["bearerAuth"]],
    "update_entry": [["bearerAuth"]],
    "delete_entry": [["bearerAuth"]],
    "list_entry_references": [["bearerAuth"]],
    "publish_entry": [["bearerAuth"]],
    "unpublish_entry": [["bearerAuth"]],
    "archive_entry": [["bearerAuth"]],
    "unarchive_entry": [["bearerAuth"]],
    "upload_file": [["bearerAuth"]],
    "get_upload": [["bearerAuth"]],
    "delete_upload": [["bearerAuth"]],
    "list_assets": [["bearerAuth"]],
    "create_asset": [["bearerAuth"]],
    "list_published_assets": [["bearerAuth"]],
    "get_asset": [["bearerAuth"]],
    "create_or_update_asset": [["bearerAuth"]],
    "delete_asset": [["bearerAuth"]],
    "process_asset_file": [["bearerAuth"]],
    "publish_asset": [["bearerAuth"]],
    "unpublish_asset": [["bearerAuth"]],
    "archive_asset": [["bearerAuth"]],
    "unarchive_asset": [["bearerAuth"]],
    "create_asset_key": [["bearerAuth"]],
    "list_locales": [["bearerAuth"]],
    "create_locale": [["bearerAuth"]],
    "get_locale": [["bearerAuth"]],
    "update_locale": [["bearerAuth"]],
    "delete_locale": [["bearerAuth"]],
    "list_environment_tags": [["bearerAuth"]],
    "get_tag": [["bearerAuth"]],
    "create_tag": [["bearerAuth"]],
    "update_tag": [["bearerAuth"]],
    "delete_tag": [["bearerAuth"]],
    "list_webhooks": [["bearerAuth"]],
    "list_webhook_calls": [["bearerAuth"]],
    "get_webhook_call": [["bearerAuth"]],
    "check_webhook_health": [["bearerAuth"]],
    "get_webhook_definition": [["bearerAuth"]],
    "delete_role": [["bearerAuth"]],
    "list_entry_snapshots": [["bearerAuth"]],
    "list_content_type_snapshots": [["bearerAuth"]],
    "get_content_type_snapshot": [["bearerAuth"]],
    "get_entry_snapshot": [["bearerAuth"]],
    "list_space_memberships": [["bearerAuth"]],
    "create_space_membership": [["bearerAuth"]],
    "get_space_membership": [["bearerAuth"]],
    "update_space_membership": [["bearerAuth"]],
    "remove_space_member": [["bearerAuth"]],
    "list_teams": [["bearerAuth"]],
    "get_delivery_api_key": [["bearerAuth"]],
    "update_delivery_api_key": [["bearerAuth"]],
    "delete_delivery_api_key": [["bearerAuth"]],
    "list_delivery_api_keys": [["bearerAuth"]],
    "create_delivery_api_key": [["bearerAuth"]],
    "list_preview_api_keys": [["bearerAuth"]],
    "get_preview_api_key": [["bearerAuth"]],
    "list_access_tokens": [["bearerAuth"]],
    "get_access_token": [["bearerAuth"]],
    "revoke_access_token": [["bearerAuth"]],
    "get_current_user": [["bearerAuth"]],
    "list_entry_tasks": [["bearerAuth"]],
    "create_entry_task": [["bearerAuth"]],
    "get_task": [["bearerAuth"]],
    "update_task": [["bearerAuth"]],
    "delete_task": [["bearerAuth"]],
    "list_scheduled_actions": [["bearerAuth"]],
    "create_scheduled_action": [["bearerAuth"]],
    "update_scheduled_action": [["bearerAuth"]],
    "cancel_scheduled_action": [["bearerAuth"]],
    "list_releases": [["bearerAuth"]],
    "create_environment_release": [["bearerAuth"]],
    "validate_release": [["bearerAuth"]],
    "list_release_actions": [["bearerAuth"]],
    "get_release_action": [["bearerAuth"]],
    "publish_release": [["bearerAuth"]],
    "unpublish_release": [["bearerAuth"]],
    "get_release": [["bearerAuth"]],
    "update_release": [["bearerAuth"]],
    "delete_release": [["bearerAuth"]],
    "get_bulk_action": [["bearerAuth"]],
    "publish_scheduled_actions": [["bearerAuth"]],
    "unpublish_scheduled_actions": [["bearerAuth"]],
    "validate_scheduled_bulk_action": [["bearerAuth"]],
    "list_app_definitions": [["bearerAuth"]],
    "delete_app_definition": [["bearerAuth"]],
    "get_app_signing_secret": [["bearerAuth"]],
    "set_app_signing_secret": [["bearerAuth"]],
    "revoke_app_signing_secret": [["bearerAuth"]],
    "list_app_keys": [["bearerAuth"]],
    "delete_app_key": [["bearerAuth"]],
    "list_app_installations": [["bearerAuth"]],
    "uninstall_app": [["bearerAuth"]],
    "issue_app_installation_access_token": [["bearerAuth"]],
    "list_organization_usage_metrics": [["bearerAuth"]],
    "list_space_periodic_usages": [["bearerAuth"]]
}

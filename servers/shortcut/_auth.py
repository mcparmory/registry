"""
Authentication module for Shortcut MCP server.

Generated: 2026-04-25 15:35:28 UTC
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
    API Key authentication for Shortcut API.

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
    "list_categories": [["api_token"]],
    "create_category": [["api_token"]],
    "get_category": [["api_token"]],
    "update_category": [["api_token"]],
    "delete_category": [["api_token"]],
    "list_milestones_for_category": [["api_token"]],
    "list_objectives_for_category": [["api_token"]],
    "list_custom_fields": [["api_token"]],
    "get_custom_field": [["api_token"]],
    "update_custom_field": [["api_token"]],
    "delete_custom_field": [["api_token"]],
    "list_documents": [["api_token"]],
    "create_document": [["api_token"]],
    "get_doc": [["api_token"]],
    "update_document": [["api_token"]],
    "delete_doc": [["api_token"]],
    "list_document_epics": [["api_token"]],
    "link_document_to_epic": [["api_token"]],
    "remove_document_from_epic": [["api_token"]],
    "list_entity_templates": [["api_token"]],
    "get_entity_template": [["api_token"]],
    "list_epics": [["api_token"]],
    "create_epic": [["api_token"]],
    "list_epics_paginated": [["api_token"]],
    "get_epic": [["api_token"]],
    "update_epic": [["api_token"]],
    "delete_epic": [["api_token"]],
    "list_epic_comments": [["api_token"]],
    "create_epic_comment": [["api_token"]],
    "get_epic_comment": [["api_token"]],
    "create_reply_to_epic_comment": [["api_token"]],
    "update_epic_comment": [["api_token"]],
    "delete_epic_comment": [["api_token"]],
    "list_epic_documents": [["api_token"]],
    "get_epic_health": [["api_token"]],
    "create_epic_health": [["api_token"]],
    "list_epic_health_history": [["api_token"]],
    "list_epic_stories": [["api_token"]],
    "remove_productboard_from_epic": [["api_token"]],
    "list_stories_by_external_link": [["api_token"]],
    "list_files": [["api_token"]],
    "upload_files": [["api_token"]],
    "get_file": [["api_token"]],
    "update_file": [["api_token"]],
    "delete_file": [["api_token"]],
    "list_groups": [["api_token"]],
    "create_group": [["api_token"]],
    "get_group": [["api_token"]],
    "update_group": [["api_token"]],
    "list_group_stories": [["api_token"]],
    "update_health": [["api_token"]],
    "get_webhook_integration": [["api_token"]],
    "delete_webhook_integration": [["api_token"]],
    "list_iterations": [["api_token"]],
    "create_iteration": [["api_token"]],
    "get_iteration": [["api_token"]],
    "update_iteration": [["api_token"]],
    "delete_iteration": [["api_token"]],
    "list_iteration_stories": [["api_token"]],
    "get_key_result": [["api_token"]],
    "update_key_result": [["api_token"]],
    "list_labels": [["api_token"]],
    "create_label": [["api_token"]],
    "get_label": [["api_token"]],
    "update_label": [["api_token"]],
    "delete_label": [["api_token"]],
    "list_epics_for_label": [["api_token"]],
    "list_stories_by_label": [["api_token"]],
    "list_linked_files": [["api_token"]],
    "create_linked_file": [["api_token"]],
    "get_linked_file": [["api_token"]],
    "update_linked_file": [["api_token"]],
    "delete_linked_file": [["api_token"]],
    "get_current_member": [["api_token"]],
    "list_workspace_members": [["api_token"]],
    "get_member": [["api_token"]],
    "list_milestones": [["api_token"]],
    "create_milestone": [["api_token"]],
    "get_milestone": [["api_token"]],
    "update_milestone": [["api_token"]],
    "delete_milestone": [["api_token"]],
    "list_epics_for_milestone": [["api_token"]],
    "list_objectives": [["api_token"]],
    "create_objective": [["api_token"]],
    "get_objective": [["api_token"]],
    "update_objective": [["api_token"]],
    "delete_objective": [["api_token"]],
    "list_epics_for_objective": [["api_token"]],
    "list_projects": [["api_token"]],
    "create_project": [["api_token"]],
    "get_project": [["api_token"]],
    "update_project": [["api_token"]],
    "delete_project": [["api_token"]],
    "list_stories": [["api_token"]],
    "list_repositories": [["api_token"]],
    "get_repository": [["api_token"]],
    "search_epics_and_stories": [["api_token"]],
    "search_documents": [["api_token"]],
    "search_epics": [["api_token"]],
    "search_iterations": [["api_token"]],
    "search_milestones": [["api_token"]],
    "search_objectives": [["api_token"]],
    "search_stories": [["api_token"]],
    "create_story": [["api_token"]],
    "create_stories": [["api_token"]],
    "update_multiple_stories": [["api_token"]],
    "delete_stories_bulk": [["api_token"]],
    "create_story_from_template": [["api_token"]],
    "search_stories_advanced": [["api_token"]],
    "get_story": [["api_token"]],
    "update_story": [["api_token"]],
    "delete_story": [["api_token"]],
    "list_story_comments": [["api_token"]],
    "create_story_comment": [["api_token"]],
    "get_story_comment": [["api_token"]],
    "update_story_comment": [["api_token"]],
    "delete_story_comment": [["api_token"]],
    "add_reaction_to_story_comment": [["api_token"]],
    "remove_reaction_from_story_comment": [["api_token"]],
    "remove_comment_slack_link": [["api_token"]],
    "get_story_history": [["api_token"]],
    "list_story_sub_tasks": [["api_token"]],
    "create_task_in_story": [["api_token"]],
    "get_task": [["api_token"]],
    "update_task": [["api_token"]],
    "delete_task": [["api_token"]],
    "create_story_link": [["api_token"]],
    "get_story_link": [["api_token"]],
    "update_story_link": [["api_token"]],
    "delete_story_link": [["api_token"]],
    "get_workflow": [["api_token"]]
}

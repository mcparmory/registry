"""
Authentication module for ClickUp MCP server.

Generated: 2026-04-14 18:17:58 UTC
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
    API Key authentication for ClickUp API v2 Reference.

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
    "upload_task_attachment": [["Authorization_Token"]],
    "get_current_user": [["Authorization_Token"]],
    "list_workspaces": [["Authorization_Token"]],
    "create_checklist": [["Authorization_Token"]],
    "update_checklist": [["Authorization_Token"]],
    "delete_checklist": [["Authorization_Token"]],
    "create_checklist_item": [["Authorization_Token"]],
    "update_checklist_item": [["Authorization_Token"]],
    "delete_checklist_item": [["Authorization_Token"]],
    "list_task_comments": [["Authorization_Token"]],
    "add_task_comment": [["Authorization_Token"]],
    "list_chat_view_comments": [["Authorization_Token"]],
    "create_chat_view_comment": [["Authorization_Token"]],
    "list_comments": [["Authorization_Token"]],
    "add_list_comment": [["Authorization_Token"]],
    "update_comment": [["Authorization_Token"]],
    "delete_comment": [["Authorization_Token"]],
    "list_comment_replies": [["Authorization_Token"]],
    "reply_to_comment": [["Authorization_Token"]],
    "list_custom_fields": [["Authorization_Token"]],
    "list_folder_custom_fields": [["Authorization_Token"]],
    "list_space_custom_fields": [["Authorization_Token"]],
    "list_workspace_custom_fields": [["Authorization_Token"]],
    "set_task_custom_field_value": [["Authorization_Token"]],
    "clear_task_custom_field_value": [["Authorization_Token"]],
    "add_task_dependency": [["Authorization_Token"]],
    "delete_task_dependency": [["Authorization_Token"]],
    "link_task": [["Authorization_Token"]],
    "delete_task_link": [["Authorization_Token"]],
    "list_folders": [["Authorization_Token"]],
    "create_folder": [["Authorization_Token"]],
    "get_folder": [["Authorization_Token"]],
    "rename_folder": [["Authorization_Token"]],
    "delete_folder": [["Authorization_Token"]],
    "list_goals": [["Authorization_Token"]],
    "create_goal": [["Authorization_Token"]],
    "get_goal": [["Authorization_Token"]],
    "update_goal": [["Authorization_Token"]],
    "delete_goal": [["Authorization_Token"]],
    "create_key_result": [["Authorization_Token"]],
    "update_key_result": [["Authorization_Token"]],
    "delete_key_result": [["Authorization_Token"]],
    "invite_workspace_guest": [["Authorization_Token"]],
    "get_guest": [["Authorization_Token"]],
    "update_workspace_guest": [["Authorization_Token"]],
    "remove_workspace_guest": [["Authorization_Token"]],
    "add_guest_to_task": [["Authorization_Token"]],
    "remove_task_guest": [["Authorization_Token"]],
    "add_guest_to_list": [["Authorization_Token"]],
    "remove_list_guest": [["Authorization_Token"]],
    "add_guest_to_folder": [["Authorization_Token"]],
    "remove_folder_guest": [["Authorization_Token"]],
    "list_folder_lists": [["Authorization_Token"]],
    "create_list": [["Authorization_Token"]],
    "create_folder_from_template": [["Authorization_Token"]],
    "list_folderless_lists": [["Authorization_Token"]],
    "create_folderless_list": [["Authorization_Token"]],
    "get_list": [["Authorization_Token"]],
    "update_list": [["Authorization_Token"]],
    "delete_list": [["Authorization_Token"]],
    "add_task_to_list": [["Authorization_Token"]],
    "remove_task_from_list": [["Authorization_Token"]],
    "list_task_members": [["Authorization_Token"]],
    "list_list_members": [["Authorization_Token"]],
    "list_custom_roles": [["Authorization_Token"]],
    "list_shared_hierarchy": [["Authorization_Token"]],
    "list_spaces": [["Authorization_Token"]],
    "create_space": [["Authorization_Token"]],
    "get_space": [["Authorization_Token"]],
    "update_space": [["Authorization_Token"]],
    "delete_space": [["Authorization_Token"]],
    "list_space_tags": [["Authorization_Token"]],
    "create_space_tag": [["Authorization_Token"]],
    "update_space_tag": [["Authorization_Token"]],
    "delete_space_tag": [["Authorization_Token"]],
    "add_tag_to_task": [["Authorization_Token"]],
    "remove_task_tag": [["Authorization_Token"]],
    "list_tasks": [["Authorization_Token"]],
    "create_task": [["Authorization_Token"]],
    "get_task": [["Authorization_Token"]],
    "update_task": [["Authorization_Token"]],
    "delete_task": [["Authorization_Token"]],
    "list_tasks_by_team": [["Authorization_Token"]],
    "merge_tasks": [["Authorization_Token"]],
    "get_task_time_in_status": [["Authorization_Token"]],
    "get_bulk_tasks_time_in_status": [["Authorization_Token"]],
    "list_task_templates": [["Authorization_Token"]],
    "list_templates": [["Authorization_Token"]],
    "list_folder_templates": [["Authorization_Token"]],
    "create_task_from_template": [["Authorization_Token"]],
    "create_list_from_template_in_folder": [["Authorization_Token"]],
    "create_list_from_template": [["Authorization_Token"]],
    "get_workspace_seats": [["Authorization_Token"]],
    "get_workspace_plan": [["Authorization_Token"]],
    "create_user_group": [["Authorization_Token"]],
    "list_custom_task_types": [["Authorization_Token"]],
    "update_user_group": [["Authorization_Token"]],
    "delete_user_group": [["Authorization_Token"]],
    "list_user_groups": [["Authorization_Token"]],
    "get_task_tracked_time": [["Authorization_Token"]],
    "track_task_time": [["Authorization_Token"]],
    "update_time_entry_legacy": [["Authorization_Token"]],
    "delete_tracked_time_interval": [["Authorization_Token"]],
    "list_time_entries": [["Authorization_Token"]],
    "create_time_entry": [["Authorization_Token"]],
    "get_time_entry": [["Authorization_Token"]],
    "update_time_entry": [["Authorization_Token"]],
    "delete_time_entry": [["Authorization_Token"]],
    "get_time_entry_history": [["Authorization_Token"]],
    "get_running_time_entry": [["Authorization_Token"]],
    "list_time_entry_tags": [["Authorization_Token"]],
    "add_tags_to_time_entries": [["Authorization_Token"]],
    "rename_time_entry_tag": [["Authorization_Token"]],
    "remove_tags_from_time_entries": [["Authorization_Token"]],
    "start_time_entry": [["Authorization_Token"]],
    "stop_time_entry": [["Authorization_Token"]],
    "invite_workspace_member": [["Authorization_Token"]],
    "get_workspace_user": [["Authorization_Token"]],
    "update_workspace_user": [["Authorization_Token"]],
    "remove_workspace_user": [["Authorization_Token"]],
    "list_workspace_views": [["Authorization_Token"]],
    "create_workspace_view": [["Authorization_Token"]],
    "list_space_views": [["Authorization_Token"]],
    "create_space_view": [["Authorization_Token"]],
    "list_folder_views": [["Authorization_Token"]],
    "create_folder_view": [["Authorization_Token"]],
    "list_views": [["Authorization_Token"]],
    "create_list_view": [["Authorization_Token"]],
    "get_view": [["Authorization_Token"]],
    "update_view": [["Authorization_Token"]],
    "delete_view": [["Authorization_Token"]],
    "list_view_tasks": [["Authorization_Token"]],
    "list_webhooks": [["Authorization_Token"]],
    "delete_webhook": [["Authorization_Token"]]
}

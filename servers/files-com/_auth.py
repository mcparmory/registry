"""
Authentication module for Files.com MCP server.

Generated: 2026-04-09 17:20:43 UTC
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
    API Key authentication for Files.com API.

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
    "list_action_notification_export_results": [],
    "export_action_notifications": [],
    "get_action_notification_export": [],
    "retry_webhook_failure": [],
    "get_current_api_key": [],
    "list_api_keys": [],
    "create_api_key": [],
    "get_api_key": [],
    "update_api_key_by_id": [],
    "delete_api_key": [],
    "list_apps": [],
    "list_as2_incoming_messages": [],
    "list_as2_outgoing_messages": [],
    "list_as2_partners": [],
    "create_as2_partner": [],
    "get_as2_partner": [],
    "update_as2_partner": [],
    "delete_as2_partner": [],
    "list_as2_stations": [],
    "create_as2_station": [],
    "get_as2_station": [],
    "update_as2_station": [],
    "delete_as2_station": [],
    "list_automation_runs": [],
    "get_automation_run": [],
    "list_automations": [],
    "get_automation": [],
    "update_automation": [],
    "delete_automation": [],
    "list_bandwidth_snapshots": [],
    "list_behaviors_by_path": [],
    "get_behavior": [],
    "delete_behavior": [],
    "list_bundle_downloads": [],
    "list_bundle_notifications": [],
    "get_bundle_notification": [],
    "update_bundle_notification": [],
    "delete_bundle_notification": [],
    "list_bundle_recipients": [],
    "share_bundle_with_recipient": [],
    "list_bundle_registrations": [],
    "list_bundles": [],
    "create_bundle": [],
    "get_bundle": [],
    "update_bundle": [],
    "delete_bundle": [],
    "share_bundle": [],
    "list_clickwraps": [],
    "create_clickwrap": [],
    "get_clickwrap": [],
    "update_clickwrap": [],
    "delete_clickwrap": [],
    "list_dns_records": [],
    "list_external_events": [],
    "create_external_event": [],
    "get_external_event": [],
    "initiate_file_upload": [],
    "copy_file": [],
    "get_file_metadata": [],
    "move_file": [],
    "add_file_comment_reaction": [],
    "remove_file_comment_reaction": [],
    "update_file_comment": [],
    "delete_file_comment": [],
    "get_file_migration": [],
    "download_file": [],
    "upload_file": [],
    "update_file_metadata": [],
    "delete_file": [],
    "list_folders": [],
    "create_folder": [],
    "list_form_field_sets": [],
    "create_form_field_set": [],
    "get_form_field_set": [],
    "update_form_field_set": [],
    "delete_form_field_set": [],
    "list_group_users": [],
    "add_user_to_group": [],
    "update_group_user": [],
    "remove_user_from_group": [],
    "list_groups": [],
    "create_group": [],
    "update_group_membership": [],
    "remove_group_member": [],
    "list_group_permissions": [],
    "list_group_members": [],
    "create_group_user": [],
    "get_group": [],
    "update_group": [],
    "delete_group": [],
    "list_history": [],
    "list_file_history": [],
    "list_folder_history": [],
    "list_logins": [],
    "list_user_history": [],
    "list_history_export_results": [],
    "create_history_export": [],
    "get_history_export": [],
    "list_inbox_recipients": [],
    "share_inbox_with_recipient": [],
    "list_inbox_registrations": [],
    "list_inbox_uploads": [],
    "list_invoices": [],
    "get_invoice": [],
    "list_ip_addresses": [],
    "list_exavault_reserved_ip_addresses": [],
    "list_reserved_ip_addresses": [],
    "list_locks": [],
    "release_lock": [],
    "list_message_comment_reactions": [],
    "get_message_comment_reaction": [],
    "remove_message_comment_reaction": [],
    "list_message_comments": [],
    "get_message_comment": [],
    "update_message_comment": [],
    "delete_message_comment": [],
    "list_message_reactions": [],
    "get_message_reaction": [],
    "remove_message_reaction": [],
    "list_messages": [],
    "create_message": [],
    "get_message": [],
    "update_message": [],
    "delete_message": [],
    "list_notifications": [],
    "create_notification": [],
    "get_notification": [],
    "update_notification": [],
    "delete_notification": [],
    "list_payments": [],
    "get_payment": [],
    "list_permissions": [],
    "create_permission": [],
    "delete_permission": [],
    "create_project": [],
    "get_project": [],
    "delete_project": [],
    "list_public_keys": [],
    "create_public_key": [],
    "get_public_key": [],
    "update_public_key": [],
    "delete_public_key": [],
    "list_bandwidth_snapshots_remote": [],
    "list_remote_servers": [],
    "create_remote_server": [],
    "get_remote_server": [],
    "update_remote_server": [],
    "delete_remote_server": [],
    "download_remote_server_configuration": [],
    "update_remote_server_configuration": [],
    "list_requests": [],
    "request_file": [],
    "list_requests_folder": [],
    "delete_request": [],
    "list_sftp_host_keys": [],
    "create_sftp_host_key": [],
    "get_sftp_host_key": [],
    "update_sftp_host_key": [],
    "delete_sftp_host_key": [],
    "list_api_keys_site": [],
    "create_api_key_site": [],
    "list_dns_records_site": [],
    "list_site_ip_addresses": [],
    "get_site_usage": [],
    "get_sso_strategy": [],
    "sync_sso_strategy": [],
    "update_style": [],
    "delete_style": [],
    "list_usage_snapshots_daily": [],
    "list_usage_snapshots": [],
    "update_user": [],
    "list_api_keys_current_user": [],
    "create_api_key_user": [],
    "list_user_groups": [],
    "list_public_keys_current_user": [],
    "add_public_key": [],
    "list_cipher_uses": [],
    "list_requests_user": [],
    "create_user_request": [],
    "get_user_request": [],
    "delete_user_request": [],
    "list_users": [],
    "create_user": [],
    "get_user": [],
    "update_user_account": [],
    "delete_user": [],
    "reset_user_2fa": [],
    "resend_welcome_email": [],
    "unlock_user": [],
    "list_api_keys_for_user": [],
    "create_api_key_admin": [],
    "list_cipher_uses_by_user": [],
    "list_user_groups_2": [],
    "list_user_permissions": [],
    "list_public_keys_by_user": [],
    "create_public_key_for_user": [],
    "test_webhook": []
}

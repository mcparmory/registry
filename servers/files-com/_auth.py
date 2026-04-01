"""
Authentication module for Files.com API MCP server.

Generated: 2026-04-01 18:20:53 UTC
Generator: MCP Blacksmith v1.0.0 (https://mcpblacksmith.com)

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

    Supports header, query parameter, and cookie-based API key injection.
    Configure location and parameter name via constructor arguments.
    """

    def __init__(self, env_var: str = "API_KEY", location: str = "header",
                 param_name: str = "Authorization", prefix: str = ""):
        """Initialize API key authentication from environment variable.

        Args:
            env_var: Environment variable name containing the API key.
            location: Where to inject the key - 'header', 'query', or 'cookie'.
            param_name: Name of the header, query parameter, or cookie.
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


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "list_action_notification_export_results": [["api_key"]],
    "export_action_notifications": [["api_key"]],
    "get_action_notification_export": [["api_key"]],
    "retry_webhook_failure": [["api_key"]],
    "get_current_api_key": [["api_key"]],
    "update_api_key": [["api_key"]],
    "delete_api_key_current": [["api_key"]],
    "list_api_keys": [["api_key"]],
    "create_api_key": [["api_key"]],
    "get_api_key": [["api_key"]],
    "update_api_key_by_id": [["api_key"]],
    "delete_api_key": [["api_key"]],
    "list_apps": [["api_key"]],
    "list_as2_incoming_messages": [["api_key"]],
    "list_as2_outgoing_messages": [["api_key"]],
    "list_as2_partners": [["api_key"]],
    "create_as2_partner": [["api_key"]],
    "get_as2_partner": [["api_key"]],
    "update_as2_partner": [["api_key"]],
    "delete_as2_partner": [["api_key"]],
    "list_as2_stations": [["api_key"]],
    "create_as2_station": [["api_key"]],
    "get_as2_station": [["api_key"]],
    "update_as2_station": [["api_key"]],
    "delete_as2_station": [["api_key"]],
    "list_automation_runs": [["api_key"]],
    "get_automation_run": [["api_key"]],
    "list_automations": [["api_key"]],
    "create_automation": [["api_key"]],
    "get_automation": [["api_key"]],
    "update_automation": [["api_key"]],
    "delete_automation": [["api_key"]],
    "list_bandwidth_snapshots": [["api_key"]],
    "list_behaviors": [["api_key"]],
    "create_behavior": [["api_key"]],
    "list_behaviors_by_path": [["api_key"]],
    "test_webhook_behavior": [["api_key"]],
    "get_behavior": [["api_key"]],
    "update_behavior": [["api_key"]],
    "delete_behavior": [["api_key"]],
    "list_bundle_downloads": [["api_key"]],
    "list_bundle_notifications": [["api_key"]],
    "create_bundle_notification": [["api_key"]],
    "get_bundle_notification": [["api_key"]],
    "update_bundle_notification": [["api_key"]],
    "delete_bundle_notification": [["api_key"]],
    "list_bundle_recipients": [["api_key"]],
    "share_bundle_with_recipient": [["api_key"]],
    "list_bundle_registrations": [["api_key"]],
    "list_bundles": [["api_key"]],
    "create_bundle": [["api_key"]],
    "get_bundle": [["api_key"]],
    "update_bundle": [["api_key"]],
    "delete_bundle": [["api_key"]],
    "share_bundle": [["api_key"]],
    "list_clickwraps": [["api_key"]],
    "create_clickwrap": [["api_key"]],
    "get_clickwrap": [["api_key"]],
    "update_clickwrap": [["api_key"]],
    "delete_clickwrap": [["api_key"]],
    "list_dns_records": [["api_key"]],
    "list_external_events": [["api_key"]],
    "create_external_event": [["api_key"]],
    "get_external_event": [["api_key"]],
    "initiate_file_upload": [["api_key"]],
    "copy_file": [["api_key"]],
    "get_file_metadata": [["api_key"]],
    "move_file": [["api_key"]],
    "add_file_comment_reaction": [["api_key"]],
    "remove_file_comment_reaction": [["api_key"]],
    "update_file_comment": [["api_key"]],
    "delete_file_comment": [["api_key"]],
    "get_file_migration": [["api_key"]],
    "download_file": [["api_key"]],
    "upload_file": [["api_key"]],
    "update_file_metadata": [["api_key"]],
    "delete_file": [["api_key"]],
    "list_folders": [["api_key"]],
    "create_folder": [["api_key"]],
    "list_form_field_sets": [["api_key"]],
    "create_form_field_set": [["api_key"]],
    "get_form_field_set": [["api_key"]],
    "update_form_field_set": [["api_key"]],
    "delete_form_field_set": [["api_key"]],
    "list_group_users": [["api_key"]],
    "add_user_to_group": [["api_key"]],
    "update_group_user": [["api_key"]],
    "remove_user_from_group": [["api_key"]],
    "list_groups": [["api_key"]],
    "create_group": [["api_key"]],
    "update_group_membership": [["api_key"]],
    "remove_group_member": [["api_key"]],
    "list_group_permissions": [["api_key"]],
    "list_group_members": [["api_key"]],
    "create_group_user": [["api_key"]],
    "get_group": [["api_key"]],
    "update_group": [["api_key"]],
    "delete_group": [["api_key"]],
    "list_history": [["api_key"]],
    "list_file_history": [["api_key"]],
    "list_folder_history": [["api_key"]],
    "list_logins": [["api_key"]],
    "list_user_history": [["api_key"]],
    "list_history_export_results": [["api_key"]],
    "create_history_export": [["api_key"]],
    "get_history_export": [["api_key"]],
    "list_inbox_recipients": [["api_key"]],
    "share_inbox_with_recipient": [["api_key"]],
    "list_inbox_registrations": [["api_key"]],
    "list_inbox_uploads": [["api_key"]],
    "list_invoices": [["api_key"]],
    "get_invoice": [["api_key"]],
    "list_ip_addresses": [["api_key"]],
    "list_exavault_reserved_ip_addresses": [["api_key"]],
    "list_reserved_ip_addresses": [["api_key"]],
    "list_locks": [["api_key"]],
    "release_lock": [["api_key"]],
    "list_message_comment_reactions": [["api_key"]],
    "get_message_comment_reaction": [["api_key"]],
    "remove_message_comment_reaction": [["api_key"]],
    "list_message_comments": [["api_key"]],
    "get_message_comment": [["api_key"]],
    "update_message_comment": [["api_key"]],
    "delete_message_comment": [["api_key"]],
    "list_message_reactions": [["api_key"]],
    "get_message_reaction": [["api_key"]],
    "remove_message_reaction": [["api_key"]],
    "list_messages": [["api_key"]],
    "create_message": [["api_key"]],
    "get_message": [["api_key"]],
    "update_message": [["api_key"]],
    "delete_message": [["api_key"]],
    "list_notifications": [["api_key"]],
    "create_notification": [["api_key"]],
    "get_notification": [["api_key"]],
    "update_notification": [["api_key"]],
    "delete_notification": [["api_key"]],
    "list_payments": [["api_key"]],
    "get_payment": [["api_key"]],
    "list_permissions": [["api_key"]],
    "create_permission": [["api_key"]],
    "delete_permission": [["api_key"]],
    "create_project": [["api_key"]],
    "get_project": [["api_key"]],
    "delete_project": [["api_key"]],
    "list_public_keys": [["api_key"]],
    "create_public_key": [["api_key"]],
    "get_public_key": [["api_key"]],
    "update_public_key": [["api_key"]],
    "delete_public_key": [["api_key"]],
    "list_bandwidth_snapshots_remote": [["api_key"]],
    "list_remote_servers": [["api_key"]],
    "create_remote_server": [["api_key"]],
    "get_remote_server": [["api_key"]],
    "update_remote_server": [["api_key"]],
    "delete_remote_server": [["api_key"]],
    "download_remote_server_configuration": [["api_key"]],
    "update_remote_server_configuration": [["api_key"]],
    "list_requests": [["api_key"]],
    "request_file": [["api_key"]],
    "list_requests_folder": [["api_key"]],
    "delete_request": [["api_key"]],
    "create_session": [["api_key"]],
    "logout_user": [["api_key"]],
    "list_settings_changes": [["api_key"]],
    "list_sftp_host_keys": [["api_key"]],
    "create_sftp_host_key": [["api_key"]],
    "get_sftp_host_key": [["api_key"]],
    "update_sftp_host_key": [["api_key"]],
    "delete_sftp_host_key": [["api_key"]],
    "get_site_settings": [["api_key"]],
    "update_site_settings": [["api_key"]],
    "list_api_keys_site": [["api_key"]],
    "create_api_key_site": [["api_key"]],
    "list_dns_records_site": [["api_key"]],
    "list_site_ip_addresses": [["api_key"]],
    "test_webhook_site": [["api_key"]],
    "get_site_usage": [["api_key"]],
    "list_sso_strategies": [["api_key"]],
    "get_sso_strategy": [["api_key"]],
    "sync_sso_strategy": [["api_key"]],
    "get_style": [["api_key"]],
    "update_style": [["api_key"]],
    "delete_style": [["api_key"]],
    "list_usage_snapshots_daily": [["api_key"]],
    "list_usage_snapshots": [["api_key"]],
    "update_user": [["api_key"]],
    "list_api_keys_current_user": [["api_key"]],
    "create_api_key_user": [["api_key"]],
    "list_user_groups": [["api_key"]],
    "list_public_keys_current_user": [["api_key"]],
    "add_public_key": [["api_key"]],
    "list_cipher_uses": [["api_key"]],
    "list_requests_user": [["api_key"]],
    "create_user_request": [["api_key"]],
    "get_user_request": [["api_key"]],
    "delete_user_request": [["api_key"]],
    "list_users": [["api_key"]],
    "create_user": [["api_key"]],
    "get_user": [["api_key"]],
    "update_user_account": [["api_key"]],
    "delete_user": [["api_key"]],
    "reset_user_2fa": [["api_key"]],
    "resend_welcome_email": [["api_key"]],
    "unlock_user": [["api_key"]],
    "list_api_keys_for_user": [["api_key"]],
    "create_api_key_admin": [["api_key"]],
    "list_cipher_uses_by_user": [["api_key"]],
    "list_user_groups_2": [["api_key"]],
    "list_user_permissions": [["api_key"]],
    "list_public_keys_by_user": [["api_key"]],
    "create_public_key_for_user": [["api_key"]],
    "test_webhook": [["api_key"]]
}

"""
Authentication module for Grafana MCP server.

Generated: 2026-04-09 17:24:44 UTC
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
    Bearer token authentication for Grafana HTTP API..

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
    HTTP Basic Authentication for Grafana HTTP API..

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
    "list_roles": [["basic"], ["api_key"]],
    "get_role": [["basic"], ["api_key"]],
    "list_role_assignments": [["basic"], ["api_key"]],
    "list_team_roles_search": [["basic"], ["api_key"]],
    "list_team_roles": [["basic"], ["api_key"]],
    "assign_team_role": [["basic"], ["api_key"]],
    "update_team_roles": [["basic"], ["api_key"]],
    "remove_team_role": [["basic"], ["api_key"]],
    "search_user_roles": [["basic"], ["api_key"]],
    "list_user_roles": [["basic"], ["api_key"]],
    "revoke_user_role": [["basic"], ["api_key"]],
    "assign_resource_permissions": [["basic"], ["api_key"]],
    "grant_team_resource_permissions": [["basic"], ["api_key"]],
    "grant_resource_permission": [["basic"], ["api_key"]],
    "sync_ldap_user": [["basic"]],
    "lookup_ldap_user": [["basic"]],
    "create_user": [["basic"]],
    "delete_user": [["basic"]],
    "list_user_auth_tokens": [["basic"]],
    "disable_user": [["basic"]],
    "enable_user": [["basic"]],
    "revoke_user_sessions": [["basic"]],
    "set_user_password": [["basic"]],
    "get_user_quota": [["basic"]],
    "update_user_quota": [["basic"]],
    "revoke_user_auth_token": [["basic"]],
    "list_annotations": [["basic"], ["api_key"]],
    "create_annotation": [["basic"], ["api_key"]],
    "create_graphite_annotation": [["basic"], ["api_key"]],
    "delete_annotations": [["basic"], ["api_key"]],
    "list_annotation_tags": [["basic"], ["api_key"]],
    "get_annotation": [["basic"], ["api_key"]],
    "update_annotation": [["basic"], ["api_key"]],
    "update_annotation_partial": [["basic"], ["api_key"]],
    "delete_annotation": [["basic"], ["api_key"]],
    "list_devices": [["basic"], ["api_key"]],
    "list_devices_search": [["basic"], ["api_key"]],
    "list_migration_sessions": [["basic"], ["api_key"]],
    "create_migration_session": [["basic"], ["api_key"]],
    "get_migration_session": [["basic"], ["api_key"]],
    "delete_migration_session": [["basic"], ["api_key"]],
    "create_migration_snapshot": [["basic"], ["api_key"]],
    "get_snapshot": [["basic"], ["api_key"]],
    "cancel_snapshot": [["basic"], ["api_key"]],
    "upload_snapshot": [["basic"], ["api_key"]],
    "list_snapshots": [["basic"], ["api_key"]],
    "list_resource_dependencies": [["basic"], ["api_key"]],
    "fetch_cloud_migration_token": [["basic"], ["api_key"]],
    "revoke_cloud_migration_token": [["basic"], ["api_key"]],
    "list_prometheus_alert_rules": [["basic"], ["api_key"]],
    "convert_prometheus_rules_to_grafana": [["basic"], ["api_key"]],
    "list_prometheus_alert_rules_by_namespace": [["basic"], ["api_key"]],
    "convert_prometheus_rule_group": [["basic"], ["api_key"]],
    "delete_prometheus_rules_by_namespace": [["basic"], ["api_key"]],
    "get_prometheus_rule_group": [["basic"], ["api_key"]],
    "delete_prometheus_rule_group": [["basic"], ["api_key"]],
    "list_prometheus_alert_rules_from_config": [["basic"], ["api_key"]],
    "convert_prometheus_rules": [["basic"], ["api_key"]],
    "get_prometheus_alert_rules": [["basic"], ["api_key"]],
    "convert_prometheus_rule_group_config": [["basic"], ["api_key"]],
    "delete_prometheus_rules_namespace": [["basic"], ["api_key"]],
    "get_prometheus_rule_group_config": [["basic"], ["api_key"]],
    "delete_prometheus_rule_group_config": [["basic"], ["api_key"]],
    "list_dashboard_snapshots": [["basic"], ["api_key"]],
    "import_dashboard": [["basic"], ["api_key"]],
    "list_dashboards": [["basic"], ["api_key"]],
    "get_public_dashboard": [["basic"], ["api_key"]],
    "create_public_dashboard": [["basic"], ["api_key"]],
    "update_public_dashboard": [["basic"], ["api_key"]],
    "delete_public_dashboard": [["basic"], ["api_key"]],
    "list_data_sources": [["basic"], ["api_key"]],
    "create_datasource": [["basic"], ["api_key"]],
    "list_correlations": [["basic"], ["api_key"]],
    "list_correlations_by_source": [["basic"], ["api_key"]],
    "create_correlation": [["basic"], ["api_key"]],
    "get_correlation": [["basic"], ["api_key"]],
    "update_correlation": [["basic"], ["api_key"]],
    "get_datasource": [["basic"], ["api_key"]],
    "update_datasource": [["basic"], ["api_key"]],
    "delete_datasource": [["basic"], ["api_key"]],
    "delete_correlation": [["basic"], ["api_key"]],
    "check_datasource_health": [["basic"], ["api_key"]],
    "fetch_datasource_resource": [["basic"], ["api_key"]],
    "get_datasource_cache_config": [["basic"], ["api_key"]],
    "configure_datasource_cache": [["basic"], ["api_key"]],
    "disable_datasource_cache": [["basic"], ["api_key"]],
    "enable_datasource_cache": [["basic"], ["api_key"]],
    "query_metrics": [["basic"], ["api_key"]],
    "set_folder_permissions": [["basic"], ["api_key"]],
    "list_mapped_groups": [["basic"], ["api_key"]],
    "list_group_roles": [["basic"], ["api_key"]],
    "list_library_elements": [["basic"], ["api_key"]],
    "create_library_element": [["basic"], ["api_key"]],
    "get_library_element_by_name": [["basic"], ["api_key"]],
    "get_library_element": [["basic"], ["api_key"]],
    "update_library_element": [["basic"], ["api_key"]],
    "delete_library_element": [["basic"], ["api_key"]],
    "list_library_element_connections": [["basic"], ["api_key"]],
    "create_license_token": [["basic"], ["api_key"]],
    "remove_license_token": [["basic"], ["api_key"]],
    "get_organization": [["basic"], ["api_key"]],
    "update_organization_current": [["basic"], ["api_key"]],
    "update_organization_address": [["basic"], ["api_key"]],
    "list_pending_org_invites": [["basic"], ["api_key"]],
    "invite_organization_member": [["basic"], ["api_key"]],
    "revoke_invitation": [["basic"], ["api_key"]],
    "get_organization_quota": [["basic"], ["api_key"]],
    "list_organization_users": [["basic"], ["api_key"]],
    "add_user_to_organization": [["basic"], ["api_key"]],
    "list_organization_users_lookup": [["basic"], ["api_key"]],
    "update_org_user_role": [["basic"], ["api_key"]],
    "remove_organization_user": [["basic"], ["api_key"]],
    "list_organizations": [["basic"]],
    "create_organization": [["basic"], ["api_key"]],
    "get_organization_by_name": [["basic"]],
    "get_organization_by_id": [["basic"]],
    "update_organization": [["basic"]],
    "delete_organization": [["basic"]],
    "update_organization_address_by_id": [["basic"], ["api_key"]],
    "get_organization_quota_by_id": [["basic"], ["api_key"]],
    "update_org_quota": [["basic"]],
    "list_organization_users_by_id": [["basic"]],
    "add_organization_user": [["basic"], ["api_key"]],
    "search_organization_users": [["basic"]],
    "update_organization_user_role": [["basic"], ["api_key"]],
    "remove_organization_user_by_id": [["basic"], ["api_key"]],
    "get_public_dashboard_access": [["basic"], ["api_key"]],
    "list_dashboard_annotations": [["basic"], ["api_key"]],
    "query_dashboard_panel": [["basic"], ["api_key"]],
    "list_queries": [["basic"], ["api_key"]],
    "save_query": [["basic"], ["api_key"]],
    "star_query_history": [["basic"], ["api_key"]],
    "remove_query_star": [["basic"], ["api_key"]],
    "update_query_comment": [["basic"], ["api_key"]],
    "delete_query_history": [["basic"], ["api_key"]],
    "list_recording_rules": [["basic"], ["api_key"]],
    "create_recording_rule": [["basic"], ["api_key"]],
    "update_recording_rule": [["basic"], ["api_key"]],
    "test_recording_rule": [["basic"], ["api_key"]],
    "create_remote_write_target": [["basic"], ["api_key"]],
    "delete_recording_write_target": [["basic"], ["api_key"]],
    "delete_recording_rule": [["basic"], ["api_key"]],
    "list_reports": [["basic"], ["api_key"]],
    "create_report": [["basic"], ["api_key"]],
    "list_reports_by_dashboard": [["basic"], ["api_key"]],
    "send_report": [["basic"], ["api_key"]],
    "retrieve_branding_image": [["basic"], ["api_key"]],
    "download_csv_report": [["basic"], ["api_key"]],
    "render_report_pdfs": [["basic"], ["api_key"]],
    "send_test_report_email": [["basic"], ["api_key"]],
    "search_dashboards": [["basic"], ["api_key"]],
    "list_sort_options": [["basic"], ["api_key"]],
    "create_service_account": [["basic"], ["api_key"]],
    "list_service_accounts": [["basic"], ["api_key"]],
    "get_service_account": [["basic"], ["api_key"]],
    "update_service_account": [["basic"], ["api_key"]],
    "delete_service_account": [["basic"], ["api_key"]],
    "list_service_account_tokens": [["basic"], ["api_key"]],
    "create_service_account_token": [["basic"], ["api_key"]],
    "revoke_service_account_token": [["basic"], ["api_key"]],
    "list_snapshot_sharing_options": [["basic"], ["api_key"]],
    "create_snapshot": [["basic"], ["api_key"]],
    "delete_snapshot_by_delete_key": [["basic"], ["api_key"]],
    "get_snapshot_by_key": [["basic"], ["api_key"]],
    "delete_snapshot": [["basic"], ["api_key"]],
    "create_team": [["basic"], ["api_key"]],
    "list_teams": [["basic"], ["api_key"]],
    "list_team_groups": [["basic"], ["api_key"]],
    "add_group_to_team": [["basic"], ["api_key"]],
    "remove_team_group": [["basic"], ["api_key"]],
    "search_groups": [["basic"], ["api_key"]],
    "get_team": [["basic"], ["api_key"]],
    "update_team": [["basic"], ["api_key"]],
    "delete_team": [["basic"], ["api_key"]],
    "list_team_members": [["basic"], ["api_key"]],
    "add_team_member": [["basic"], ["api_key"]],
    "update_team_members": [["basic"], ["api_key"]],
    "update_team_member": [["basic"], ["api_key"]],
    "remove_team_member": [["basic"], ["api_key"]],
    "get_team_preferences": [["basic"], ["api_key"]],
    "get_current_user": [["basic"], ["api_key"]],
    "update_user_profile": [["basic"], ["api_key"]],
    "list_auth_tokens": [["basic"], ["api_key"]],
    "clear_help_flags": [["basic"], ["api_key"]],
    "enable_help_flag": [["basic"], ["api_key"]],
    "list_user_organizations": [["basic"]],
    "get_user_preferences": [["basic"], ["api_key"]],
    "update_user_preferences_partial": [["basic"], ["api_key"]],
    "list_user_quotas": [["basic"], ["api_key"]],
    "star_dashboard": [["basic"], ["api_key"]],
    "remove_dashboard_star": [["basic"], ["api_key"]],
    "list_user_teams": [["basic"], ["api_key"]],
    "switch_organization": [["basic"], ["api_key"]],
    "list_users": [["basic"], ["api_key"]],
    "lookup_user": [["basic"], ["api_key"]],
    "list_users_paginated": [["basic"], ["api_key"]],
    "get_user": [["basic"], ["api_key"]],
    "update_user": [["basic"], ["api_key"]],
    "list_user_organizations_by_id": [["basic"], ["api_key"]],
    "list_user_teams_by_id": [["basic"], ["api_key"]],
    "export_alert_rules": [["basic"], ["api_key"]],
    "export_alert_rule": [["basic"], ["api_key"]],
    "list_contact_points": [["basic"], ["api_key"]],
    "create_contact_point": [["basic"], ["api_key"]],
    "export_contact_points": [["basic"], ["api_key"]],
    "update_contact_point": [["basic"], ["api_key"]],
    "delete_contact_point": [["basic"], ["api_key"]],
    "export_alert_rule_group": [["basic"], ["api_key"]],
    "list_mute_timings": [["basic"], ["api_key"]],
    "export_mute_timings": [["basic"], ["api_key"]],
    "get_mute_timing": [["basic"], ["api_key"]],
    "update_mute_timing": [["basic"], ["api_key"]],
    "delete_mute_timing": [["basic"], ["api_key"]],
    "export_mute_timing": [["basic"], ["api_key"]],
    "list_notification_templates": [["basic"], ["api_key"]],
    "get_notification_template": [["basic"], ["api_key"]],
    "update_notification_template": [["basic"], ["api_key"]],
    "delete_notification_template": [["basic"], ["api_key"]]
}

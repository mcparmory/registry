"""
Authentication module for Grafana MCP server.

Generated: 2026-04-23 21:23:28 UTC
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


# ============================================================================
# Operation Auth Requirements Map
# ============================================================================

"""
Operation-to-authentication requirements mapping.

This dictionary defines which authentication schemes are required for each operation,
using OR/AND relationships (outer list = OR, inner list = AND).
"""
OPERATION_AUTH_MAP: dict[str, list[list[str]]] = {
    "list_roles": [["api_key"]],
    "get_role": [["api_key"]],
    "list_role_assignments": [["api_key"]],
    "list_team_roles_search": [["api_key"]],
    "list_team_roles": [["api_key"]],
    "assign_team_role": [["api_key"]],
    "update_team_roles": [["api_key"]],
    "remove_team_role": [["api_key"]],
    "search_user_roles": [["api_key"]],
    "list_user_roles": [["api_key"]],
    "revoke_user_role": [["api_key"]],
    "assign_resource_permissions": [["api_key"]],
    "grant_team_resource_permissions": [["api_key"]],
    "grant_resource_permission": [["api_key"]],
    "sync_ldap_user": [["api_key"]],
    "lookup_ldap_user": [["api_key"]],
    "create_user": [["api_key"]],
    "delete_user": [["api_key"]],
    "list_user_auth_tokens": [["api_key"]],
    "disable_user": [["api_key"]],
    "enable_user": [["api_key"]],
    "revoke_user_sessions": [["api_key"]],
    "set_user_password": [["api_key"]],
    "get_user_quota": [["api_key"]],
    "update_user_quota": [["api_key"]],
    "revoke_user_auth_token": [["api_key"]],
    "list_annotations": [["api_key"]],
    "create_annotation": [["api_key"]],
    "create_graphite_annotation": [["api_key"]],
    "delete_annotations": [["api_key"]],
    "list_annotation_tags": [["api_key"]],
    "get_annotation": [["api_key"]],
    "update_annotation": [["api_key"]],
    "update_annotation_partial": [["api_key"]],
    "delete_annotation": [["api_key"]],
    "list_devices": [["api_key"]],
    "list_devices_search": [["api_key"]],
    "list_migration_sessions": [["api_key"]],
    "create_migration_session": [["api_key"]],
    "get_migration_session": [["api_key"]],
    "delete_migration_session": [["api_key"]],
    "create_migration_snapshot": [["api_key"]],
    "get_snapshot": [["api_key"]],
    "cancel_snapshot": [["api_key"]],
    "upload_snapshot": [["api_key"]],
    "list_snapshots": [["api_key"]],
    "list_resource_dependencies": [["api_key"]],
    "fetch_cloud_migration_token": [["api_key"]],
    "revoke_cloud_migration_token": [["api_key"]],
    "list_prometheus_alert_rules": [["api_key"]],
    "convert_prometheus_rules_to_grafana": [["api_key"]],
    "list_prometheus_alert_rules_by_namespace": [["api_key"]],
    "convert_prometheus_rule_group": [["api_key"]],
    "delete_prometheus_rules_by_namespace": [["api_key"]],
    "get_prometheus_rule_group": [["api_key"]],
    "delete_prometheus_rule_group": [["api_key"]],
    "list_prometheus_alert_rules_from_config": [["api_key"]],
    "convert_prometheus_rules": [["api_key"]],
    "get_prometheus_alert_rules": [["api_key"]],
    "convert_prometheus_rule_group_config": [["api_key"]],
    "delete_prometheus_rules_namespace": [["api_key"]],
    "get_prometheus_rule_group_config": [["api_key"]],
    "delete_prometheus_rule_group_config": [["api_key"]],
    "list_dashboard_snapshots": [["api_key"]],
    "import_dashboard": [["api_key"]],
    "list_dashboards": [["api_key"]],
    "get_public_dashboard": [["api_key"]],
    "create_public_dashboard": [["api_key"]],
    "update_public_dashboard": [["api_key"]],
    "delete_public_dashboard": [["api_key"]],
    "list_data_sources": [["api_key"]],
    "create_datasource": [["api_key"]],
    "list_correlations": [["api_key"]],
    "list_correlations_by_source": [["api_key"]],
    "create_correlation": [["api_key"]],
    "get_correlation": [["api_key"]],
    "update_correlation": [["api_key"]],
    "get_datasource": [["api_key"]],
    "update_datasource": [["api_key"]],
    "delete_datasource": [["api_key"]],
    "delete_correlation": [["api_key"]],
    "check_datasource_health": [["api_key"]],
    "fetch_datasource_resource": [["api_key"]],
    "get_datasource_cache_config": [["api_key"]],
    "configure_datasource_cache": [["api_key"]],
    "disable_datasource_cache": [["api_key"]],
    "enable_datasource_cache": [["api_key"]],
    "query_metrics": [["api_key"]],
    "set_folder_permissions": [["api_key"]],
    "list_mapped_groups": [["api_key"]],
    "list_group_roles": [["api_key"]],
    "list_library_elements": [["api_key"]],
    "create_library_element": [["api_key"]],
    "get_library_element_by_name": [["api_key"]],
    "get_library_element": [["api_key"]],
    "update_library_element": [["api_key"]],
    "delete_library_element": [["api_key"]],
    "list_library_element_connections": [["api_key"]],
    "create_license_token": [["api_key"]],
    "remove_license_token": [["api_key"]],
    "get_organization": [["api_key"]],
    "update_organization_current": [["api_key"]],
    "update_organization_address": [["api_key"]],
    "list_pending_org_invites": [["api_key"]],
    "invite_organization_member": [["api_key"]],
    "revoke_invitation": [["api_key"]],
    "get_organization_quota": [["api_key"]],
    "list_organization_users": [["api_key"]],
    "add_user_to_organization": [["api_key"]],
    "list_organization_users_lookup": [["api_key"]],
    "update_org_user_role": [["api_key"]],
    "remove_organization_user": [["api_key"]],
    "list_organizations": [["api_key"]],
    "create_organization": [["api_key"]],
    "get_organization_by_name": [["api_key"]],
    "get_organization_by_id": [["api_key"]],
    "update_organization": [["api_key"]],
    "delete_organization": [["api_key"]],
    "update_organization_address_by_id": [["api_key"]],
    "get_organization_quota_by_id": [["api_key"]],
    "update_org_quota": [["api_key"]],
    "list_organization_users_by_id": [["api_key"]],
    "add_organization_user": [["api_key"]],
    "search_organization_users": [["api_key"]],
    "update_organization_user_role": [["api_key"]],
    "remove_organization_user_by_id": [["api_key"]],
    "get_public_dashboard_access": [["api_key"]],
    "list_dashboard_annotations": [["api_key"]],
    "query_dashboard_panel": [["api_key"]],
    "list_queries": [["api_key"]],
    "save_query": [["api_key"]],
    "star_query_history": [["api_key"]],
    "remove_query_star": [["api_key"]],
    "update_query_comment": [["api_key"]],
    "delete_query_history": [["api_key"]],
    "list_recording_rules": [["api_key"]],
    "create_recording_rule": [["api_key"]],
    "update_recording_rule": [["api_key"]],
    "test_recording_rule": [["api_key"]],
    "create_remote_write_target": [["api_key"]],
    "delete_recording_write_target": [["api_key"]],
    "delete_recording_rule": [["api_key"]],
    "list_reports": [["api_key"]],
    "create_report": [["api_key"]],
    "list_reports_by_dashboard": [["api_key"]],
    "send_report": [["api_key"]],
    "retrieve_branding_image": [["api_key"]],
    "download_csv_report": [["api_key"]],
    "render_report_pdfs": [["api_key"]],
    "send_test_report_email": [["api_key"]],
    "search_dashboards": [["api_key"]],
    "list_sort_options": [["api_key"]],
    "create_service_account": [["api_key"]],
    "list_service_accounts": [["api_key"]],
    "get_service_account": [["api_key"]],
    "update_service_account": [["api_key"]],
    "delete_service_account": [["api_key"]],
    "list_service_account_tokens": [["api_key"]],
    "create_service_account_token": [["api_key"]],
    "revoke_service_account_token": [["api_key"]],
    "list_snapshot_sharing_options": [["api_key"]],
    "create_snapshot": [["api_key"]],
    "delete_snapshot_by_delete_key": [["api_key"]],
    "get_snapshot_by_key": [["api_key"]],
    "delete_snapshot": [["api_key"]],
    "create_team": [["api_key"]],
    "list_teams": [["api_key"]],
    "list_team_groups": [["api_key"]],
    "add_group_to_team": [["api_key"]],
    "remove_team_group": [["api_key"]],
    "search_groups": [["api_key"]],
    "get_team": [["api_key"]],
    "update_team": [["api_key"]],
    "delete_team": [["api_key"]],
    "list_team_members": [["api_key"]],
    "add_team_member": [["api_key"]],
    "update_team_members": [["api_key"]],
    "update_team_member": [["api_key"]],
    "remove_team_member": [["api_key"]],
    "get_team_preferences": [["api_key"]],
    "get_current_user": [["api_key"]],
    "update_user_profile": [["api_key"]],
    "list_auth_tokens": [["api_key"]],
    "clear_help_flags": [["api_key"]],
    "enable_help_flag": [["api_key"]],
    "list_user_organizations": [["api_key"]],
    "get_user_preferences": [["api_key"]],
    "update_user_preferences_partial": [["api_key"]],
    "list_user_quotas": [["api_key"]],
    "star_dashboard": [["api_key"]],
    "remove_dashboard_star": [["api_key"]],
    "list_user_teams": [["api_key"]],
    "switch_organization": [["api_key"]],
    "list_users": [["api_key"]],
    "lookup_user": [["api_key"]],
    "list_users_paginated": [["api_key"]],
    "get_user": [["api_key"]],
    "update_user": [["api_key"]],
    "list_user_organizations_by_id": [["api_key"]],
    "list_user_teams_by_id": [["api_key"]],
    "export_alert_rules": [["api_key"]],
    "export_alert_rule": [["api_key"]],
    "list_contact_points": [["api_key"]],
    "create_contact_point": [["api_key"]],
    "export_contact_points": [["api_key"]],
    "update_contact_point": [["api_key"]],
    "delete_contact_point": [["api_key"]],
    "export_alert_rule_group": [["api_key"]],
    "list_mute_timings": [["api_key"]],
    "export_mute_timings": [["api_key"]],
    "get_mute_timing": [["api_key"]],
    "update_mute_timing": [["api_key"]],
    "delete_mute_timing": [["api_key"]],
    "export_mute_timing": [["api_key"]],
    "list_notification_templates": [["api_key"]],
    "get_notification_template": [["api_key"]],
    "update_notification_template": [["api_key"]],
    "delete_notification_template": [["api_key"]]
}

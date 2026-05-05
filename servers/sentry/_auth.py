"""
Authentication module for API Reference MCP server.

Generated: 2026-05-05 16:19:13 UTC
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
    Bearer token authentication for API Reference.

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
    "list_organizations": [["auth_token"]],
    "get_organization": [["auth_token"]],
    "update_organization": [["auth_token"]],
    "update_metric_alert_rule": [["auth_token"]],
    "list_integration_providers": [["auth_token"]],
    "list_organization_dashboards": [["auth_token"]],
    "create_dashboard": [["auth_token"]],
    "get_organization_dashboard": [["auth_token"]],
    "update_organization_dashboard": [["auth_token"]],
    "delete_organization_dashboard": [["auth_token"]],
    "list_organization_monitors": [["auth_token"]],
    "update_organization_monitors_enabled_state": [["auth_token"]],
    "delete_monitors_bulk": [["auth_token"]],
    "get_monitor_detector": [["auth_token"]],
    "update_monitor_detector": [["auth_token"]],
    "delete_monitor": [["auth_token"]],
    "list_organization_discover_saved_queries": [["auth_token"]],
    "create_saved_query": [["auth_token"]],
    "get_discover_saved_query": [["auth_token"]],
    "update_discover_saved_query": [["auth_token"]],
    "delete_discover_saved_query": [["auth_token"]],
    "list_organization_environments": [["auth_token"]],
    "resolve_event_id": [["auth_token"]],
    "search_events_in_table_format": [["auth_token"]],
    "get_events_timeseries": [["auth_token"]],
    "link_external_user": [["auth_token"]],
    "update_external_user": [["auth_token"]],
    "delete_external_user": [["auth_token"]],
    "list_data_forwarders_for_organization": [["auth_token"]],
    "create_data_forwarder_for_organization": [["auth_token"]],
    "update_data_forwarder": [["auth_token"]],
    "delete_data_forwarder_for_organization": [["auth_token"]],
    "list_organization_integrations": [["auth_token"]],
    "get_organization_integration": [["auth_token"]],
    "delete_organization_integration": [["auth_token"]],
    "list_organization_issues": [["auth_token"]],
    "bulk_update_issues": [["auth_token"]],
    "delete_organization_issues": [["auth_token"]],
    "list_organization_members": [["auth_token"]],
    "add_member_to_organization": [["auth_token"]],
    "get_organization_member": [["auth_token"]],
    "update_organization_member_roles": [["auth_token"]],
    "delete_organization_member": [["auth_token"]],
    "add_member_to_team": [["auth_token"]],
    "update_organization_member_team_role": [["auth_token"]],
    "remove_member_from_team": [["auth_token"]],
    "list_monitors_for_organization": [["auth_token"]],
    "create_monitor": [["auth_token"]],
    "get_monitor": [["auth_token"]],
    "update_monitor": [["auth_token"]],
    "delete_monitor_or_monitor_environments": [["auth_token"]],
    "list_checkins_for_monitor": [["auth_token"]],
    "list_spike_protection_notifications": [["auth_token"]],
    "get_spike_protection_notification_action": [["auth_token"]],
    "get_artifact_install_details": [["auth_token"]],
    "get_artifact_size_analysis": [["auth_token"]],
    "list_repositories_for_owner": [["auth_token"]],
    "get_repository_sync_status": [["auth_token"]],
    "sync_repositories_for_owner": [["auth_token"]],
    "list_repository_tokens_for_owner": [["auth_token"]],
    "get_repository": [["auth_token"]],
    "list_repository_branches": [["auth_token"]],
    "list_test_results_for_repository": [["auth_token"]],
    "get_test_results_aggregates_for_repository": [["auth_token"]],
    "list_test_suites_for_repository": [["auth_token"]],
    "regenerate_repository_upload_token": [["auth_token"]],
    "list_organization_client_keys": [["auth_token"]],
    "list_organization_projects": [["auth_token"]],
    "create_metric_monitor_for_project": [["auth_token"]],
    "list_organization_trusted_relays": [["auth_token"]],
    "list_release_threshold_statuses": [["auth_token"]],
    "get_organization_release": [["auth_token"]],
    "update_organization_release": [["auth_token"]],
    "delete_organization_release": [["auth_token"]],
    "list_release_deploys": [["auth_token"]],
    "create_deploy_for_release": [["auth_token"]],
    "get_replay_count_for_issues_or_transactions": [["auth_token"]],
    "list_organization_replay_selectors": [["auth_token"]],
    "list_organization_replays": [["auth_token"]],
    "get_replay_instance": [["auth_token"]],
    "list_repository_commits": [["auth_token"]],
    "list_organization_teams_scim": [["auth_token"]],
    "create_team_in_organization": [["auth_token"]],
    "list_organization_scim_members": [["auth_token"]],
    "create_organization_member": [["auth_token"]],
    "list_sentry_apps": [["auth_token"]],
    "list_release_health_session_statistics": [["auth_token"]],
    "resolve_short_id": [["auth_token"]],
    "get_organization_events_count_by_project": [["auth_token"]],
    "get_event_counts_for_organization": [["auth_token"]],
    "list_organization_teams": [["auth_token"]],
    "create_team": [["auth_token"]],
    "list_user_teams_in_organization": [["auth_token"]],
    "list_alerts": [["auth_token"]],
    "create_alert_for_organization": [["auth_token"]],
    "update_organization_alerts_bulk": [["auth_token"]],
    "delete_alerts_bulk": [["auth_token"]],
    "get_alert": [["auth_token"]],
    "update_alert": [["auth_token"]],
    "delete_alert": [["auth_token"]],
    "get_project": [["auth_token"]],
    "update_project": [["auth_token"]],
    "delete_project": [["auth_token"]],
    "list_project_environments": [["auth_token"]],
    "get_project_environment": [["auth_token"]],
    "update_project_environment_visibility": [["auth_token"]],
    "list_project_error_events": [["auth_token"]],
    "get_source_map_debug_for_event": [["auth_token"]],
    "list_project_filters": [["auth_token"]],
    "update_inbound_data_filter": [["auth_token"]],
    "list_project_client_keys": [["auth_token"]],
    "create_project_client_key": [["auth_token"]],
    "get_client_key": [["auth_token"]],
    "update_client_key": [["auth_token"]],
    "delete_client_key": [["auth_token"]],
    "list_project_members": [["auth_token"]],
    "get_monitor_project": [["auth_token"]],
    "update_monitor_project": [["auth_token"]],
    "delete_monitor_for_project": [["auth_token"]],
    "list_checkins_for_monitor_in_project": [["auth_token"]],
    "get_project_ownership_configuration": [["auth_token"]],
    "update_project_ownership_configuration": [["auth_token"]],
    "get_latest_installable_build": [["auth_token"]],
    "delete_replay": [["auth_token"]],
    "list_clicked_nodes": [["auth_token"]],
    "list_replay_recording_segments": [["auth_token"]],
    "get_recording_segment": [["auth_token"]],
    "list_users_who_viewed_replay": [["auth_token"]],
    "list_replay_deletion_jobs": [["auth_token"]],
    "create_replay_deletion_job": [["auth_token"]],
    "get_replay_deletion_job": [["auth_token"]],
    "get_issue_alert_rule": [["auth_token"]],
    "update_issue_alert_rule": [["auth_token"]],
    "delete_issue_alert_rule": [["auth_token"]],
    "list_project_symbol_sources": [["auth_token"]],
    "add_symbol_source_to_project": [["auth_token"]],
    "update_project_symbol_source": [["auth_token"]],
    "delete_symbol_source": [["auth_token"]],
    "list_teams_for_project": [["auth_token"]],
    "add_team_to_project": [["auth_token"]],
    "delete_team_from_project": [["auth_token"]],
    "get_custom_integration": [["auth_token"]],
    "delete_custom_integration": [["auth_token"]],
    "get_team": [["auth_token"]],
    "update_team": [["auth_token"]],
    "delete_team": [["auth_token"]],
    "link_external_team": [["auth_token"]],
    "update_external_team": [["auth_token"]],
    "delete_external_team_link": [["auth_token"]],
    "list_team_members": [["auth_token"]],
    "list_team_projects": [["auth_token"]],
    "create_project_for_team": [["auth_token"]],
    "list_organization_repositories": [["auth_token"]],
    "list_debug_information_files": [["auth_token"]],
    "upload_dsym_file": [["auth_token"]],
    "delete_debug_information_file": [["auth_token"]],
    "list_project_users": [["auth_token"]],
    "list_tag_values": [["auth_token"]],
    "get_event_counts_for_project": [["auth_token"]],
    "list_project_user_feedback": [["auth_token"]],
    "submit_user_feedback": [["auth_token"]],
    "list_project_service_hooks": [["auth_token"]],
    "get_service_hook": [["auth_token"]],
    "update_service_hook": [["auth_token"]],
    "remove_service_hook": [["auth_token"]],
    "get_event": [["auth_token"]],
    "list_project_issues": [["auth_token"]],
    "update_issues_bulk": [["auth_token"]],
    "delete_issues": [["auth_token"]],
    "list_tag_values_for_issue": [["auth_token"]],
    "list_issue_hashes": [["auth_token"]],
    "get_issue": [["auth_token"]],
    "update_issue": [["auth_token"]],
    "delete_issue": [["auth_token"]],
    "list_organization_releases": [["auth_token"]],
    "create_release_for_organization": [["auth_token"]],
    "list_release_files": [["auth_token"]],
    "upload_release_file": [["auth_token"]],
    "list_release_files_for_project": [["auth_token"]],
    "upload_release_file_project": [["auth_token"]],
    "get_release_file": [["auth_token"]],
    "update_organization_release_file": [["auth_token"]],
    "delete_release_file": [["auth_token"]],
    "get_release_file_project": [["auth_token"]],
    "update_release_file": [["auth_token"]],
    "delete_release_file_for_project": [["auth_token"]],
    "list_release_commits": [["auth_token"]],
    "list_release_commits_for_project": [["auth_token"]],
    "list_files_changed_in_release_commits": [["auth_token"]],
    "list_organization_sentry_app_installations": [["auth_token"]],
    "create_or_update_external_issue": [["auth_token"]],
    "delete_external_issue": [["auth_token"]],
    "enable_spike_protection_for_projects": [["auth_token"]],
    "disable_spike_protection_for_projects": [["auth_token"]],
    "get_issue_autofix_state": [["auth_token"]],
    "trigger_issue_autofix": [["auth_token"]],
    "list_issue_events": [["auth_token"]],
    "get_issue_event": [["auth_token"]],
    "list_external_issues_for_issue": [["auth_token"]],
    "get_tag_values_for_issue": [["auth_token"]]
}

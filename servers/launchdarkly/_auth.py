"""
Authentication module for LaunchDarkly MCP server.

Generated: 2026-05-05 15:24:31 UTC
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
    API Key authentication for LaunchDarkly REST API.

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
    "list_relay_proxy_configs": [["ApiKey"]],
    "create_relay_proxy_config": [["ApiKey"]],
    "get_relay_proxy_config": [["ApiKey"]],
    "update_relay_auto_config": [["ApiKey"]],
    "delete_relay_auto_config": [["ApiKey"]],
    "reset_relay_auto_config": [["ApiKey"]],
    "list_applications": [["ApiKey"]],
    "get_application": [["ApiKey"]],
    "update_application": [["ApiKey"]],
    "delete_application": [["ApiKey"]],
    "list_application_versions": [["ApiKey"]],
    "update_application_version": [["ApiKey"]],
    "delete_application_version": [["ApiKey"]],
    "list_approval_requests": [["ApiKey"]],
    "create_approval_request": [["ApiKey"]],
    "get_approval_request": [["ApiKey"]],
    "update_approval_request": [["ApiKey"]],
    "delete_approval_request": [["ApiKey"]],
    "apply_approval_request": [["ApiKey"]],
    "submit_approval_request_review": [["ApiKey"]],
    "list_audit_log_entries": [["ApiKey"]],
    "search_audit_log_entries": [["ApiKey"]],
    "get_audit_log_entry": [["ApiKey"]],
    "get_caller_identity": [["ApiKey"]],
    "list_extinctions": [["ApiKey"]],
    "list_repositories": [["ApiKey"]],
    "create_repository": [["ApiKey"]],
    "get_repository": [["ApiKey"]],
    "update_repository": [["ApiKey"]],
    "delete_repository": [["ApiKey"]],
    "delete_branches": [["ApiKey"]],
    "list_branches": [["ApiKey"]],
    "get_branch": [["ApiKey"]],
    "upsert_branch": [["ApiKey"]],
    "create_extinction_event": [["ApiKey"]],
    "list_code_reference_statistics": [["ApiKey"]],
    "get_code_references_statistics": [["ApiKey"]],
    "list_destinations": [["ApiKey"]],
    "generate_warehouse_destination_key_pair": [["ApiKey"]],
    "create_data_export_destination": [["ApiKey"]],
    "get_destination": [["ApiKey"]],
    "update_destination": [["ApiKey"]],
    "delete_destination": [["ApiKey"]],
    "get_feature_flag_status_across_environments": [["ApiKey"]],
    "list_feature_flag_statuses": [["ApiKey"]],
    "get_feature_flag_status": [["ApiKey"]],
    "list_feature_flags": [["ApiKey"]],
    "create_feature_flag": [["ApiKey"]],
    "get_feature_flag": [["ApiKey"]],
    "update_feature_flag": [["ApiKey"]],
    "delete_feature_flag": [["ApiKey"]],
    "copy_feature_flag_between_environments": [["ApiKey"]],
    "list_expiring_context_targets": [["ApiKey"]],
    "update_expiring_context_targets": [["ApiKey"]],
    "list_expiring_user_targets_for_feature_flag": [["ApiKey"]],
    "schedule_user_target_removal_on_flag": [["ApiKey"]],
    "list_flag_triggers": [["ApiKey"]],
    "create_flag_trigger": [["ApiKey"]],
    "get_trigger_workflow_by_id": [["ApiKey"]],
    "update_flag_trigger": [["ApiKey"]],
    "delete_trigger_for_flag": [["ApiKey"]],
    "get_release_by_flag_key": [["ApiKey"]],
    "update_release_phase_status_by_flag_key": [["ApiKey"]],
    "delete_release_for_flag": [["ApiKey"]],
    "list_audit_subscriptions_by_integration": [["ApiKey"]],
    "get_audit_log_subscription": [["ApiKey"]],
    "update_audit_log_subscription": [["ApiKey"]],
    "delete_audit_log_subscription": [["ApiKey"]],
    "list_members": [["ApiKey"]],
    "invite_members": [["ApiKey"]],
    "update_members_bulk": [["ApiKey"]],
    "get_member": [["ApiKey"]],
    "update_member": [["ApiKey"]],
    "delete_member": [["ApiKey"]],
    "add_member_to_teams": [["ApiKey"]],
    "list_metrics": [["ApiKey"]],
    "create_metric": [["ApiKey"]],
    "get_metric": [["ApiKey"]],
    "update_metric": [["ApiKey"]],
    "delete_metric": [["ApiKey"]],
    "list_oauth_clients": [["ApiKey"]],
    "get_oauth_client_by_id": [["ApiKey"]],
    "update_oauth_client": [["ApiKey"]],
    "delete_oauth_client": [["ApiKey"]],
    "list_projects": [["ApiKey"]],
    "create_project": [["ApiKey"]],
    "get_project": [["ApiKey"]],
    "update_project": [["ApiKey"]],
    "delete_project": [["ApiKey"]],
    "list_context_kinds_by_project": [["ApiKey"]],
    "update_context_kind": [["ApiKey"]],
    "list_environments_by_project": [["ApiKey"]],
    "create_environment": [["ApiKey"]],
    "get_environment": [["ApiKey"]],
    "update_environment": [["ApiKey"]],
    "delete_environment": [["ApiKey"]],
    "reset_environment_sdk_key": [["ApiKey"]],
    "list_context_attribute_names": [["ApiKey"]],
    "get_context_attribute_values": [["ApiKey"]],
    "search_context_instances": [["ApiKey"]],
    "get_context_instance": [["ApiKey"]],
    "delete_context_instance": [["ApiKey"]],
    "search_contexts": [["ApiKey"]],
    "update_flag_setting_for_context": [["ApiKey"]],
    "get_context": [["ApiKey"]],
    "list_experiments": [["ApiKey"]],
    "create_experiment": [["ApiKey"]],
    "get_experiment": [["ApiKey"]],
    "update_experiment": [["ApiKey"]],
    "list_flag_followers_by_project_environment": [["ApiKey"]],
    "reset_mobile_key_for_environment": [["ApiKey"]],
    "evaluate_context_instance_segment_memberships": [["ApiKey"]],
    "get_experimentation_settings": [["ApiKey"]],
    "update_experimentation_settings": [["ApiKey"]],
    "list_experiments_project": [["ApiKey"]],
    "get_flag_defaults_for_project": [["ApiKey"]],
    "update_flag_defaults_for_project": [["ApiKey"]],
    "update_flag_defaults_for_project_partial": [["ApiKey"]],
    "list_approval_requests_for_flag": [["ApiKey"]],
    "create_approval_request_for_feature_flag": [["ApiKey"]],
    "create_flag_copy_approval_request": [["ApiKey"]],
    "get_approval_request_for_flag": [["ApiKey"]],
    "delete_approval_request_for_flag": [["ApiKey"]],
    "apply_approval_request_for_flag": [["ApiKey"]],
    "review_approval_request_for_flag": [["ApiKey"]],
    "list_flag_followers": [["ApiKey"]],
    "add_flag_follower": [["ApiKey"]],
    "remove_flag_follower": [["ApiKey"]],
    "list_scheduled_changes_for_flag": [["ApiKey"]],
    "create_scheduled_changes_for_flag": [["ApiKey"]],
    "get_scheduled_change_for_feature_flag": [["ApiKey"]],
    "update_scheduled_flag_change": [["ApiKey"]],
    "delete_scheduled_flag_changes": [["ApiKey"]],
    "list_workflows_for_feature_flag": [["ApiKey"]],
    "get_custom_workflow": [["ApiKey"]],
    "delete_workflow": [["ApiKey"]],
    "get_migration_safety_issues": [["ApiKey"]],
    "add_flag_to_release_pipeline": [["ApiKey"]],
    "update_release_phase_status": [["ApiKey"]],
    "list_layers": [["ApiKey"]],
    "create_layer": [["ApiKey"]],
    "update_layer": [["ApiKey"]],
    "list_metric_groups": [["ApiKey"]],
    "create_metric_group": [["ApiKey"]],
    "get_metric_group": [["ApiKey"]],
    "update_metric_group": [["ApiKey"]],
    "delete_metric_group": [["ApiKey"]],
    "list_release_pipelines": [["ApiKey"]],
    "create_release_pipeline": [["ApiKey"]],
    "get_release_pipeline_by_key": [["ApiKey"]],
    "update_release_pipeline": [["ApiKey"]],
    "delete_release_pipeline": [["ApiKey"]],
    "list_release_progressions_for_pipeline": [["ApiKey"]],
    "list_custom_roles": [["ApiKey"]],
    "get_custom_role": [["ApiKey"]],
    "update_custom_role": [["ApiKey"]],
    "delete_custom_role": [["ApiKey"]],
    "list_segments": [["ApiKey"]],
    "create_segment": [["ApiKey"]],
    "get_segment": [["ApiKey"]],
    "update_segment": [["ApiKey"]],
    "delete_segment": [["ApiKey"]],
    "update_big_segment_context_targets": [["ApiKey"]],
    "get_segment_membership_for_context": [["ApiKey"]],
    "create_big_segment_export": [["ApiKey"]],
    "get_big_segment_export": [["ApiKey"]],
    "create_big_segment_import": [["ApiKey"]],
    "get_big_segment_import": [["ApiKey"]],
    "update_big_segment_user_targets": [["ApiKey"]],
    "get_user_segment_membership": [["ApiKey"]],
    "list_expiring_targets_for_segment": [["ApiKey"]],
    "update_segment_expiring_targets": [["ApiKey"]],
    "list_expiring_user_targets_for_segment": [["ApiKey"]],
    "update_expiring_user_targets_for_segment": [["ApiKey"]],
    "list_teams": [["ApiKey"]],
    "create_team": [["ApiKey"]],
    "get_team": [["ApiKey"]],
    "update_team": [["ApiKey"]],
    "delete_team": [["ApiKey"]],
    "list_team_maintainers": [["ApiKey"]],
    "add_members_to_team": [["ApiKey"]],
    "list_team_roles": [["ApiKey"]],
    "list_workflow_templates": [["ApiKey"]],
    "get_token": [["ApiKey"]],
    "update_token": [["ApiKey"]],
    "delete_token": [["ApiKey"]],
    "reset_token": [["ApiKey"]],
    "get_events_usage_by_type": [["ApiKey"]],
    "list_webhooks": [["ApiKey"]],
    "get_webhook": [["ApiKey"]],
    "update_webhook": [["ApiKey"]],
    "delete_webhook": [["ApiKey"]],
    "list_tags": [["ApiKey"]],
    "get_ai_config_targeting": [["ApiKey"]],
    "update_ai_config_targeting": [["ApiKey"]],
    "list_ai_configs": [["ApiKey"]],
    "create_ai_config": [["ApiKey"]],
    "get_ai_config": [["ApiKey"]],
    "update_ai_config": [["ApiKey"]],
    "delete_ai_config": [["ApiKey"]],
    "create_ai_config_variation": [["ApiKey"]],
    "get_ai_config_variation": [["ApiKey"]],
    "update_ai_config_variation": [["ApiKey"]],
    "delete_ai_config_variation": [["ApiKey"]],
    "get_ai_config_quick_stats": [["ApiKey"]],
    "get_ai_config_metrics": [["ApiKey"]],
    "get_ai_config_metrics_by_variation": [["ApiKey"]],
    "add_restricted_models": [["ApiKey"]],
    "remove_restricted_models": [["ApiKey"]],
    "list_model_configs": [["ApiKey"]],
    "create_model_config": [["ApiKey"]],
    "get_model_config": [["ApiKey"]],
    "delete_model_config": [["ApiKey"]],
    "list_ai_tools": [["ApiKey"]],
    "create_ai_tool": [["ApiKey"]],
    "list_ai_tool_versions": [["ApiKey"]],
    "get_ai_tool": [["ApiKey"]],
    "update_ai_tool": [["ApiKey"]],
    "delete_ai_tool": [["ApiKey"]],
    "list_prompt_snippets": [["ApiKey"]],
    "create_prompt_snippet": [["ApiKey"]],
    "get_prompt_snippet": [["ApiKey"]],
    "update_prompt_snippet": [["ApiKey"]],
    "delete_prompt_snippet": [["ApiKey"]],
    "list_prompt_snippet_references": [["ApiKey"]],
    "list_agent_graphs": [["ApiKey"]],
    "create_agent_graph": [["ApiKey"]],
    "get_agent_graph": [["ApiKey"]],
    "update_agent_graph": [["ApiKey"]],
    "delete_agent_graph": [["ApiKey"]],
    "list_agent_optimizations": [["ApiKey"]],
    "create_agent_optimization": [["ApiKey"]],
    "get_agent_optimization": [["ApiKey"]],
    "update_agent_optimization": [["ApiKey"]],
    "delete_agent_optimization": [["ApiKey"]],
    "list_announcements": [["ApiKey"]],
    "create_announcement": [["ApiKey"]],
    "update_announcement": [["ApiKey"]],
    "delete_announcement": [["ApiKey"]],
    "update_approval_request_settings_for_project_environment": [["ApiKey"]],
    "list_views": [["ApiKey"]],
    "create_view": [["ApiKey"]],
    "get_view": [["ApiKey"]],
    "update_view": [["ApiKey"]],
    "delete_view": [["ApiKey"]],
    "link_resources_to_view": [["ApiKey"]],
    "delete_view_resource_links": [["ApiKey"]],
    "list_linked_resources_for_view": [["ApiKey"]],
    "list_linked_views_for_resource": [["ApiKey"]],
    "list_release_policies": [["ApiKey"]],
    "reorder_release_policies": [["ApiKey"]],
    "get_release_policy": [["ApiKey"]],
    "update_release_policy": [["ApiKey"]],
    "delete_release_policy": [["ApiKey"]],
    "get_deployment_frequency_chart": [["ApiKey"]],
    "get_stale_flags_chart": [["ApiKey"]],
    "get_flag_status_chart": [["ApiKey"]],
    "get_lead_time_chart": [["ApiKey"]],
    "get_release_frequency_chart": [["ApiKey"]],
    "create_deployment_event": [["ApiKey"]],
    "list_deployments": [["ApiKey"]],
    "get_deployment": [["ApiKey"]],
    "update_deployment": [["ApiKey"]],
    "list_flag_events": [["ApiKey"]],
    "create_insight_group": [["ApiKey"]],
    "list_insight_groups": [["ApiKey"]],
    "get_insight_group": [["ApiKey"]],
    "update_insight_group": [["ApiKey"]],
    "delete_insight_group": [["ApiKey"]],
    "get_insights_scores": [["ApiKey"]],
    "list_pull_requests": [["ApiKey"]],
    "list_repositories_insights": [["ApiKey"]],
    "associate_repositories_with_projects": [["ApiKey"]],
    "remove_repository_project_association": [["ApiKey"]]
}

"""
Authentication module for PagerDuty MCP server.

Generated: 2026-04-14 18:28:21 UTC
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
    API Key authentication for PagerDuty API.

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
    "add_and_remove_tags_for_entity": [["api_key"]],
    "list_tags_for_entity": [["api_key"]],
    "list_abilities": [["api_key"]],
    "check_account_ability": [["api_key"]],
    "get_addon": [["api_key"]],
    "get_alert_grouping_setting": [["api_key"]],
    "get_incident_analytics_aggregated": [["api_key"]],
    "get_escalation_policy_incident_metrics": [["api_key"]],
    "get_escalation_policy_incident_metrics_aggregated": [["api_key"]],
    "get_service_incident_analytics": [["api_key"]],
    "get_aggregated_incident_metrics_across_services": [["api_key"]],
    "get_team_incident_analytics": [["api_key"]],
    "get_analytics_metrics_incidents_for_all_teams": [["api_key"]],
    "get_pd_advance_usage_metrics": [["api_key"]],
    "get_analytics_metrics_for_all_responders": [["api_key"]],
    "get_analytics_metrics_responders_by_team": [["api_key"]],
    "get_analytics_metrics_for_all_users": [["api_key"]],
    "list_analytics_incidents": [["api_key"]],
    "get_incident_analytics": [["api_key"]],
    "get_incident_response_analytics": [["api_key"]],
    "list_responder_incidents": [["api_key"]],
    "list_analytics_users": [["api_key"]],
    "list_audit_records": [["api_key"]],
    "list_automation_actions": [["api_key"]],
    "create_automation_action": [["api_key"]],
    "get_automation_action": [["api_key"]],
    "update_automation_action": [["api_key"]],
    "delete_automation_action": [["api_key"]],
    "invoke_automation_action": [["api_key"]],
    "list_automation_action_service_associations": [["api_key"]],
    "associate_automation_action_with_service": [["api_key"]],
    "get_automation_action_service_association": [["api_key"]],
    "remove_automation_action_service_association": [["api_key"]],
    "list_automation_action_team_associations": [["api_key"]],
    "add_automation_action_team": [["api_key"]],
    "get_automation_action_team_association": [["api_key"]],
    "remove_automation_action_team_association": [["api_key"]],
    "list_automation_action_invocations": [["api_key"]],
    "get_automation_action_invocation": [["api_key"]],
    "list_automation_action_runners": [["api_key"]],
    "create_automation_runner": [["api_key"]],
    "get_automation_actions_runner": [["api_key"]],
    "update_automation_actions_runner": [["api_key"]],
    "delete_automation_actions_runner": [["api_key"]],
    "list_runner_team_associations": [["api_key"]],
    "associate_runner_with_team": [["api_key"]],
    "get_runner_team_association": [["api_key"]],
    "remove_runner_from_team": [["api_key"]],
    "list_business_services": [["api_key"]],
    "create_business_service": [["api_key"]],
    "get_business_service": [["api_key"]],
    "update_business_service": [["api_key"]],
    "delete_business_service": [["api_key"]],
    "subscribe_account_to_business_service": [["api_key"]],
    "remove_business_service_account_subscription": [["api_key"]],
    "list_business_service_subscribers": [["api_key"]],
    "add_subscribers_to_business_service": [["api_key"]],
    "list_supporting_service_impacts": [["api_key"]],
    "remove_business_service_notification_subscribers": [["api_key"]],
    "list_business_service_impactors": [["api_key"]],
    "list_business_services_by_impact": [["api_key"]],
    "get_business_service_priority_thresholds": [["api_key"]],
    "list_change_events": [["api_key"]],
    "send_change_event": [["api_key"]],
    "get_change_event": [["api_key"]],
    "update_change_event": [["api_key"]],
    "list_escalation_policies": [["api_key"]],
    "create_escalation_policy": [["api_key"]],
    "get_escalation_policy": [["api_key"]],
    "update_escalation_policy": [["api_key"]],
    "delete_escalation_policy": [["api_key"]],
    "list_escalation_policy_audit_records": [["api_key"]],
    "list_event_orchestrations": [["api_key"]],
    "create_event_orchestration": [["api_key"]],
    "get_orchestration": [["api_key"]],
    "delete_orchestration": [["api_key"]],
    "list_integrations_for_event_orchestration": [["api_key"]],
    "create_integration_for_event_orchestration": [["api_key"]],
    "get_integration_for_orchestration": [["api_key"]],
    "update_event_orchestration_integration": [["api_key"]],
    "delete_orchestration_integration": [["api_key"]],
    "move_integration_between_orchestrations": [["api_key"]],
    "get_event_orchestration_global": [["api_key"]],
    "get_event_orchestration_router": [["api_key"]],
    "get_unrouted_orchestration": [["api_key"]],
    "get_service_orchestration": [["api_key"]],
    "get_service_orchestration_active_status": [["api_key"]],
    "update_service_orchestration_active_status": [["api_key"]],
    "list_cache_variables_for_global_orchestration": [["api_key"]],
    "create_cache_variable_for_global_orchestration": [["api_key"]],
    "get_cache_variable_for_global_orchestration": [["api_key"]],
    "update_cache_variable_for_global_orchestration": [["api_key"]],
    "delete_cache_variable_from_global_orchestration": [["api_key"]],
    "get_external_data_cache_variable_data": [["api_key"]],
    "update_cache_variable_external_data": [["api_key"]],
    "delete_external_data_cache_variable_data": [["api_key"]],
    "list_cache_variables_for_service_orchestration": [["api_key"]],
    "create_cache_variable_for_service_orchestration": [["api_key"]],
    "get_cache_variable_for_service_orchestration": [["api_key"]],
    "update_cache_variable_for_service_orchestration": [["api_key"]],
    "delete_cache_variable_for_service_orchestration": [["api_key"]],
    "get_cache_variable_data_on_service_orchestration": [["api_key"]],
    "update_cache_variable_data": [["api_key"]],
    "delete_cache_variable_data_on_service_orchestration": [["api_key"]],
    "list_event_orchestration_enablements": [["api_key"]],
    "update_event_orchestration_feature_enablement": [["api_key"]],
    "list_extension_schemas": [["api_key"]],
    "get_extension_schema": [["api_key"]],
    "list_extensions": [["api_key"]],
    "create_extension": [["api_key"]],
    "get_extension": [["api_key"]],
    "update_extension": [["api_key"]],
    "delete_extension": [["api_key"]],
    "enable_extension": [["api_key"]],
    "delete_incident_workflow": [["api_key"]],
    "create_incident_workflow_instance": [["api_key"]],
    "list_incident_workflow_actions": [["api_key"]],
    "get_incident_workflow_action": [["api_key"]],
    "list_incident_workflow_triggers": [["api_key"]],
    "delete_incident_workflow_trigger": [["api_key"]],
    "add_service_to_incident_workflow_trigger": [["api_key"]],
    "remove_service_from_incident_workflow_trigger": [["api_key"]],
    "list_incidents": [["api_key"]],
    "create_incident": [["api_key"]],
    "update_incidents": [["api_key"]],
    "get_incident": [["api_key"]],
    "update_incident": [["api_key"]],
    "list_incident_alerts": [["api_key"]],
    "update_incident_alerts": [["api_key"]],
    "get_incident_alert": [["api_key"]],
    "update_incident_alert": [["api_key"]],
    "update_incident_business_service_impact": [["api_key"]],
    "list_business_services_impacted_by_incident": [["api_key"]],
    "get_incident_custom_field_values": [["api_key"]],
    "update_incident_custom_field_values": [["api_key"]],
    "list_incident_log_entries": [["api_key"]],
    "merge_incidents": [["api_key"]],
    "list_incident_notes": [["api_key"]],
    "add_note_to_incident": [["api_key"]],
    "update_incident_note": [["api_key"]],
    "delete_incident_note": [["api_key"]],
    "get_outlier_incident": [["api_key"]],
    "list_past_incidents": [["api_key"]],
    "list_incident_related_change_events": [["api_key"]],
    "get_related_incidents": [["api_key"]],
    "send_responder_request_for_incident": [["api_key"]],
    "cancel_incident_responder_requests": [["api_key"]],
    "snooze_incident": [["api_key"]],
    "create_incident_status_update": [["api_key"]],
    "list_incident_notification_subscribers": [["api_key"]],
    "add_incident_status_update_subscribers": [["api_key"]],
    "remove_incident_notification_subscribers": [["api_key"]],
    "list_incident_types": [["api_key"]],
    "create_incident_type": [["api_key"]],
    "get_incident_type": [["api_key"]],
    "update_incident_type": [["api_key"]],
    "list_incident_type_custom_fields": [["api_key"]],
    "create_incident_type_custom_field": [["api_key"]],
    "get_incident_type_custom_field": [["api_key"]],
    "update_incident_type_custom_field": [["api_key"]],
    "delete_incident_type_custom_field": [["api_key"]],
    "list_incident_type_custom_field_options": [["api_key"]],
    "create_incident_type_custom_field_option": [["api_key"]],
    "get_incident_type_custom_field_option": [["api_key"]],
    "update_incident_type_custom_field_option": [["api_key"]],
    "delete_incident_type_custom_field_option": [["api_key"]],
    "list_license_allocations": [["api_key"]],
    "list_licenses": [["api_key"]],
    "list_incident_log_entries_account": [["api_key"]],
    "get_log_entry": [["api_key"]],
    "update_log_entry_channel": [["api_key"]],
    "list_maintenance_windows": [["api_key"]],
    "create_maintenance_window": [["api_key"]],
    "get_maintenance_window": [["api_key"]],
    "update_maintenance_window": [["api_key"]],
    "delete_maintenance_window": [["api_key"]],
    "list_notifications": [["api_key"]],
    "revoke_user_oauth_delegations": [["api_key"]],
    "list_oncalls": [["api_key"]],
    "list_paused_incident_report_alerts": [["api_key"]],
    "list_paused_incident_report_counts": [["api_key"]],
    "list_priorities": [["api_key"]],
    "delete_ruleset_event_rule": [["api_key"]],
    "list_schedules_audit_records": [["api_key"]],
    "list_schedule_users": [["api_key"]],
    "preview_schedule": [["api_key"]],
    "associate_service_dependencies": [["api_key"]],
    "get_business_service_dependencies": [["api_key"]],
    "remove_service_dependencies": [["api_key"]],
    "get_technical_service_dependencies": [["api_key"]],
    "list_services": [["api_key"]],
    "create_service": [["api_key"]],
    "get_service": [["api_key"]],
    "update_service": [["api_key"]],
    "delete_service": [["api_key"]],
    "list_service_audit_records": [["api_key"]],
    "list_service_change_events": [["api_key"]],
    "create_service_integration": [["api_key"]],
    "get_service_integration": [["api_key"]],
    "update_service_integration": [["api_key"]],
    "list_service_event_rules": [["api_key"]],
    "delete_service_event_rule": [["api_key"]],
    "list_service_custom_fields": [["api_key"]],
    "get_service_custom_field": [["api_key"]],
    "update_service_custom_field": [["api_key"]],
    "delete_service_custom_field": [["api_key"]],
    "list_custom_field_options": [["api_key"]],
    "create_service_custom_field_option": [["api_key"]],
    "get_service_custom_field_option": [["api_key"]],
    "delete_service_custom_field_option": [["api_key"]],
    "get_service_custom_field_values": [["api_key"]],
    "update_service_custom_field_values": [["api_key"]],
    "list_service_feature_enablements": [["api_key"]],
    "update_service_feature_enablement": [["api_key"]],
    "list_standards": [["api_key"]],
    "update_standard": [["api_key"]],
    "list_standards_scores_for_services": [["api_key"]],
    "list_resource_standards_scores": [["api_key"]],
    "list_status_dashboards": [["api_key"]],
    "get_status_dashboard": [["api_key"]],
    "get_service_impacts_for_status_dashboard": [["api_key"]],
    "get_status_dashboard_by_url_slug": [["api_key"]],
    "get_service_impacts_for_status_dashboard_by_url_slug": [["api_key"]],
    "list_status_pages": [["api_key"]],
    "list_status_page_impacts": [["api_key"]],
    "get_status_page_impact": [["api_key"]],
    "list_status_page_services": [["api_key"]],
    "get_status_page_service": [["api_key"]],
    "list_status_page_severities": [["api_key"]],
    "get_status_page_severity": [["api_key"]],
    "list_status_page_statuses": [["api_key"]],
    "get_status_page_status": [["api_key"]],
    "list_status_page_posts": [["api_key"]],
    "create_status_page_post": [["api_key"]],
    "get_status_page_post": [["api_key"]],
    "update_status_page_post": [["api_key"]],
    "delete_status_page_post": [["api_key"]],
    "list_status_page_post_updates": [["api_key"]],
    "create_post_update_for_status_page_post": [["api_key"]],
    "get_post_update": [["api_key"]],
    "update_status_page_post_update": [["api_key"]],
    "delete_post_update": [["api_key"]],
    "get_postmortem_for_post": [["api_key"]],
    "create_postmortem_for_status_page_post": [["api_key"]],
    "update_status_page_post_postmortem": [["api_key"]],
    "delete_postmortem_for_status_page_post": [["api_key"]],
    "list_status_page_subscriptions": [["api_key"]],
    "create_status_page_subscription": [["api_key"]],
    "get_status_page_subscription": [["api_key"]],
    "delete_status_page_subscription": [["api_key"]],
    "list_sre_memories": [["api_key"]],
    "update_sre_memory": [["api_key"]],
    "delete_sre_memory": [["api_key"]],
    "list_tags": [["api_key"]],
    "create_tag": [["api_key"]],
    "get_tag": [["api_key"]],
    "delete_tag": [["api_key"]],
    "list_entities_by_tag": [["api_key"]],
    "list_teams": [["api_key"]],
    "create_team": [["api_key"]],
    "get_team": [["api_key"]],
    "update_team": [["api_key"]],
    "delete_team": [["api_key"]],
    "list_teams_audit_records": [["api_key"]],
    "add_escalation_policy_to_team": [["api_key"]],
    "remove_escalation_policy_from_team": [["api_key"]],
    "list_team_members": [["api_key"]],
    "list_team_notification_subscriptions": [["api_key"]],
    "remove_team_notification_subscriptions": [["api_key"]],
    "add_user_to_team": [["api_key"]],
    "remove_user_from_team": [["api_key"]],
    "list_templates": [["api_key"]],
    "create_status_update_template": [["api_key"]],
    "get_template": [["api_key"]],
    "update_template": [["api_key"]],
    "delete_template": [["api_key"]],
    "render_template": [["api_key"]],
    "list_template_fields": [["api_key"]],
    "list_users": [["api_key"]],
    "create_user": [["api_key"]],
    "get_user": [["api_key"]],
    "update_user": [["api_key"]],
    "delete_user": [["api_key"]],
    "list_user_audit_records": [["api_key"]],
    "list_user_contact_methods": [["api_key"]],
    "create_user_contact_method": [["api_key"]],
    "get_user_contact_method": [["api_key"]],
    "update_user_contact_method": [["api_key"]],
    "delete_user_contact_method": [["api_key"]],
    "list_user_oauth_delegations": [["api_key"]],
    "get_user_oauth_delegation": [["api_key"]],
    "get_user_license": [["api_key"]],
    "list_user_notification_rules": [["api_key"]],
    "get_user_notification_rule": [["api_key"]],
    "update_user_notification_rule": [["api_key"]],
    "delete_user_notification_rule": [["api_key"]],
    "list_user_notification_subscriptions": [["api_key"]],
    "create_user_notification_subscriptions": [["api_key"]],
    "remove_user_notification_subscriptions": [["api_key"]],
    "get_user_oncall_handoff_notification_rule": [["api_key"]],
    "delete_user_oncall_handoff_notification_rule": [["api_key"]],
    "delete_user_status_update_notification_rule": [["api_key"]],
    "get_current_user": [["api_key"]],
    "list_vendors": [["api_key"]],
    "list_schedules": [["api_key"]],
    "create_schedule": [["api_key"]],
    "get_schedule_with_final_assignments": [["api_key"]],
    "update_schedule": [["api_key"]],
    "delete_schedule": [["api_key"]],
    "list_custom_shifts": [["api_key"]],
    "create_custom_shifts": [["api_key"]],
    "get_custom_shift": [["api_key"]],
    "update_custom_shift": [["api_key"]],
    "delete_custom_shift": [["api_key"]],
    "list_schedule_overrides": [["api_key"]],
    "create_schedule_overrides": [["api_key"]],
    "get_override": [["api_key"]],
    "update_schedule_override": [["api_key"]],
    "delete_schedule_override": [["api_key"]],
    "list_rotations": [["api_key"]],
    "create_rotation_for_schedule": [["api_key"]],
    "get_rotation": [["api_key"]],
    "delete_rotation": [["api_key"]],
    "list_rotation_events": [["api_key"]],
    "create_rotation_event": [["api_key"]],
    "get_event_in_rotation": [["api_key"]],
    "update_rotation_event": [["api_key"]],
    "delete_rotation_event": [["api_key"]],
    "get_vendor": [["api_key"]],
    "list_webhook_subscriptions": [["api_key"]],
    "get_webhook_subscription": [["api_key"]],
    "update_webhook_subscription": [["api_key"]],
    "enable_webhook_subscription": [["api_key"]],
    "send_webhook_subscription_test_ping": [["api_key"]],
    "list_workflow_integrations": [["api_key"]],
    "get_workflow_integration": [["api_key"]],
    "list_workflow_integration_connections": [["api_key"]],
    "list_workflow_integration_connections_for_integration": [["api_key"]],
    "create_workflow_integration_connection": [["api_key"]],
    "get_workflow_integration_connection": [["api_key"]],
    "update_workflow_integration_connection": [["api_key"]],
    "delete_workflow_integration_connection": [["api_key"]]
}

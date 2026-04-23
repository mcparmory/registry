"""
Authentication module for Codacy MCP server.

Generated: 2026-04-23 21:09:17 UTC
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
    API Key authentication for Codacy API.

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
    "list_organization_repositories_with_analysis": [["ApiKeyAuth"]],
    "search_organization_repositories": [["ApiKeyAuth"]],
    "get_repository_analysis": [["ApiKeyAuth"]],
    "list_repository_tools": [["ApiKeyAuth"]],
    "list_tool_conflicts": [["ApiKeyAuth"]],
    "configure_repository_tool": [["ApiKeyAuth"]],
    "list_repository_tool_patterns": [["ApiKeyAuth"]],
    "bulk_update_repository_tool_patterns": [["ApiKeyAuth"]],
    "get_repository_tool_pattern_config": [["ApiKeyAuth"]],
    "get_tool_patterns_overview": [["ApiKeyAuth"]],
    "list_tool_pattern_conflicts": [["ApiKeyAuth"]],
    "get_repository_analysis_progress": [["ApiKeyAuth"]],
    "list_pull_requests": [["ApiKeyAuth"]],
    "get_pull_request": [["ApiKeyAuth"]],
    "get_pull_request_coverage": [["ApiKeyAuth"]],
    "list_pull_request_file_coverage": [["ApiKeyAuth"]],
    "reanalyze_pull_request_coverage": [["ApiKeyAuth"]],
    "list_pull_request_commits": [["ApiKeyAuth"]],
    "bypass_pull_request_analysis": [["ApiKeyAuth"]],
    "trigger_pull_request_ai_review": [["ApiKeyAuth"]],
    "list_pull_request_coverage_reports": [["ApiKeyAuth"]],
    "list_pull_request_issues": [["ApiKeyAuth"]],
    "list_pull_request_clones": [["ApiKeyAuth"]],
    "list_commit_clones": [["ApiKeyAuth"]],
    "list_pull_request_logs": [["ApiKeyAuth"]],
    "list_commit_analysis_logs": [["ApiKeyAuth"]],
    "list_commit_files": [["ApiKeyAuth"]],
    "list_pull_request_files": [["ApiKeyAuth"]],
    "follow_repository": [["ApiKeyAuth"]],
    "unfollow_repository": [["ApiKeyAuth"]],
    "update_repository_quality_settings": [["ApiKeyAuth"]],
    "regenerate_repository_ssh_user_key": [["ApiKeyAuth"]],
    "regenerate_repository_ssh_key": [["ApiKeyAuth"]],
    "get_repository_ssh_key": [["ApiKeyAuth"]],
    "sync_repository": [["ApiKeyAuth"]],
    "get_build_server_analysis_setting": [["ApiKeyAuth"]],
    "list_repository_languages": [["ApiKeyAuth"]],
    "configure_repository_language_settings": [["ApiKeyAuth"]],
    "get_repository_commit_quality_settings": [["ApiKeyAuth"]],
    "reset_repository_commit_quality_settings": [["ApiKeyAuth"]],
    "reset_repository_quality_settings": [["ApiKeyAuth"]],
    "list_organization_pull_requests": [["ApiKeyAuth"]],
    "list_commit_statistics": [["ApiKeyAuth"]],
    "list_repository_category_overviews": [["ApiKeyAuth"]],
    "search_repository_issues": [["ApiKeyAuth"]],
    "bulk_ignore_repository_issues": [["ApiKeyAuth"]],
    "get_repository_issues_overview": [["ApiKeyAuth"]],
    "get_repository_issue": [["ApiKeyAuth"]],
    "set_issue_ignored_state": [["ApiKeyAuth"]],
    "ignore_issue_false_positive": [["ApiKeyAuth"]],
    "list_ignored_issues": [["ApiKeyAuth"]],
    "list_repository_commits": [["ApiKeyAuth"]],
    "get_commit_analysis": [["ApiKeyAuth"]],
    "get_commit_delta_statistics": [["ApiKeyAuth"]],
    "list_commit_delta_issues": [["ApiKeyAuth"]],
    "get_authenticated_user": [["ApiKeyAuth"]],
    "update_current_user": [["ApiKeyAuth"]],
    "list_organizations": [["ApiKeyAuth"]],
    "list_organizations_by_provider": [["ApiKeyAuth"]],
    "get_organization_for_user": [["ApiKeyAuth"]],
    "list_emails": [["ApiKeyAuth"]],
    "remove_user_email": [["ApiKeyAuth"]],
    "set_default_email": [["ApiKeyAuth"]],
    "list_integrations": [["ApiKeyAuth"]],
    "delete_integration": [["ApiKeyAuth"]],
    "get_organization": [["ApiKeyAuth"]],
    "delete_organization": [["ApiKeyAuth"]],
    "get_organization_by_installation_id": [["ApiKeyAuth"]],
    "get_organization_billing": [["ApiKeyAuth"]],
    "update_organization_billing": [["ApiKeyAuth"]],
    "get_organization_billing_card": [["ApiKeyAuth"]],
    "add_billing_card": [["ApiKeyAuth"]],
    "estimate_organization_billing": [["ApiKeyAuth"]],
    "change_organization_billing_plan": [["ApiKeyAuth"]],
    "apply_organization_provider_settings": [["ApiKeyAuth"]],
    "get_provider_settings": [["ApiKeyAuth"]],
    "configure_provider_settings": [["ApiKeyAuth"]],
    "get_repository_provider_integration_settings": [["ApiKeyAuth"]],
    "update_repository_integration_settings": [["ApiKeyAuth"]],
    "create_post_commit_hook": [["ApiKeyAuth"]],
    "refresh_repository_provider_integration": [["ApiKeyAuth"]],
    "list_organization_repositories": [["ApiKeyAuth"]],
    "get_organization_onboarding_progress": [["ApiKeyAuth"]],
    "list_organization_people": [["ApiKeyAuth"]],
    "add_organization_members": [["ApiKeyAuth"]],
    "export_organization_people_csv": [["ApiKeyAuth"]],
    "remove_organization_members": [["ApiKeyAuth"]],
    "get_git_provider_app_permissions": [["ApiKeyAuth"]],
    "list_organization_people_suggestions": [["ApiKeyAuth"]],
    "reanalyze_commit": [["ApiKeyAuth"]],
    "get_repository": [["ApiKeyAuth"]],
    "delete_repository": [["ApiKeyAuth"]],
    "list_repository_people_suggestions": [["ApiKeyAuth"]],
    "list_repository_branches": [["ApiKeyAuth"]],
    "configure_branch_analysis": [["ApiKeyAuth"]],
    "set_organization_join_mode": [["ApiKeyAuth"]],
    "set_default_branch": [["ApiKeyAuth"]],
    "list_branch_required_checks": [["ApiKeyAuth"]],
    "add_codacy_badge": [["ApiKeyAuth"]],
    "check_organization_leave_eligibility": [["ApiKeyAuth"]],
    "list_organization_join_requests": [["ApiKeyAuth"]],
    "join_organization": [["ApiKeyAuth"]],
    "decline_organization_join_requests": [["ApiKeyAuth"]],
    "delete_organization_join_request": [["ApiKeyAuth"]],
    "add_repository": [["ApiKeyAuth"]],
    "add_organization": [["ApiKeyAuth"]],
    "delete_enterprise_token": [["ApiKeyAuth"]],
    "list_enterprise_provider_tokens": [["ApiKeyAuth"]],
    "add_enterprise_token": [["ApiKeyAuth"]],
    "list_api_tokens": [["ApiKeyAuth"]],
    "create_api_token": [["ApiKeyAuth"]],
    "delete_user_token": [["ApiKeyAuth"]],
    "delete_billing_subscription": [["ApiKeyAuth"]],
    "list_provider_integrations": [["ApiKeyAuth"]],
    "search_entities": [["ApiKeyAuth"]],
    "delete_dormant_accounts": [["ApiKeyAuth"]],
    "list_tool_supported_languages": [["ApiKeyAuth"]],
    "list_tools": [["ApiKeyAuth"]],
    "list_tool_patterns": [["ApiKeyAuth"]],
    "submit_pattern_feedback": [["ApiKeyAuth"]],
    "get_pattern": [["ApiKeyAuth"]],
    "list_duplication_tools": [["ApiKeyAuth"]],
    "list_metrics_tools": [["ApiKeyAuth"]],
    "start_organization_metrics_collection": [["ApiKeyAuth"]],
    "list_ready_metrics": [["ApiKeyAuth"]],
    "get_latest_metric_value": [["ApiKeyAuth"]],
    "get_latest_grouped_metric_values": [["ApiKeyAuth"]],
    "get_metric_period_value": [["ApiKeyAuth"]],
    "get_grouped_metric_values_for_period": [["ApiKeyAuth"]],
    "get_metric_time_range_values": [["ApiKeyAuth"]],
    "list_ready_enterprise_metrics": [["ApiKeyAuth"]],
    "get_latest_enterprise_metric_values": [["ApiKeyAuth"]],
    "list_enterprise_metric_latest_values_grouped": [["ApiKeyAuth"]],
    "get_enterprise_metric_by_period": [["ApiKeyAuth"]],
    "get_enterprise_metric_grouped_by_period": [["ApiKeyAuth"]],
    "get_enterprise_metric_timeseries": [["ApiKeyAuth"]],
    "list_repository_files": [["ApiKeyAuth"]],
    "list_ignored_files": [["ApiKeyAuth"]],
    "get_file_analysis": [["ApiKeyAuth"]],
    "list_file_clones": [["ApiKeyAuth"]],
    "list_file_issues": [["ApiKeyAuth"]],
    "get_ai_risk_checklist": [["ApiKeyAuth"]],
    "list_coding_standards": [["ApiKeyAuth"]],
    "create_coding_standard": [["ApiKeyAuth"]],
    "create_compliance_standard": [["ApiKeyAuth"]],
    "create_coding_standard_from_preset": [["ApiKeyAuth"]],
    "get_coding_standard": [["ApiKeyAuth"]],
    "delete_coding_standard": [["ApiKeyAuth"]],
    "duplicate_coding_standard": [["ApiKeyAuth"]],
    "list_coding_standard_tools": [["ApiKeyAuth"]],
    "set_default_coding_standard": [["ApiKeyAuth"]],
    "list_coding_standard_tool_patterns": [["ApiKeyAuth"]],
    "get_coding_standard_tool_patterns_overview": [["ApiKeyAuth"]],
    "bulk_update_coding_standard_tool_patterns": [["ApiKeyAuth"]],
    "configure_coding_standard_tool": [["ApiKeyAuth"]],
    "list_coding_standard_repositories": [["ApiKeyAuth"]],
    "update_coding_standard_repositories": [["ApiKeyAuth"]],
    "set_default_gate_policy": [["ApiKeyAuth"]],
    "set_default_gate_policy_to_codacy_builtin": [["ApiKeyAuth"]],
    "get_gate_policy": [["ApiKeyAuth"]],
    "update_gate_policy": [["ApiKeyAuth"]],
    "delete_gate_policy": [["ApiKeyAuth"]],
    "list_gate_policies": [["ApiKeyAuth"]],
    "create_gate_policy": [["ApiKeyAuth"]],
    "sync_organization_name": [["ApiKeyAuth"]],
    "check_submodules_enabled": [["ApiKeyAuth"]],
    "list_gate_policy_repositories": [["ApiKeyAuth"]],
    "update_gate_policy_repositories": [["ApiKeyAuth"]],
    "promote_coding_standard": [["ApiKeyAuth"]],
    "list_repository_api_tokens": [["ApiKeyAuth"]],
    "create_repository_token": [["ApiKeyAuth"]],
    "delete_repository_token": [["ApiKeyAuth"]],
    "list_coverage_reports": [["ApiKeyAuth"]],
    "list_commit_coverage_reports": [["ApiKeyAuth"]],
    "get_commit_coverage_report": [["ApiKeyAuth"]],
    "get_file_content": [["ApiKeyAuth"]],
    "get_file_coverage": [["ApiKeyAuth"]],
    "set_file_ignored_state": [["ApiKeyAuth"]],
    "ignore_security_item": [["ApiKeyAuth"]],
    "unignore_security_item": [["ApiKeyAuth"]],
    "get_security_item": [["ApiKeyAuth"]],
    "search_security_items": [["ApiKeyAuth"]],
    "get_security_dashboard_metrics": [["ApiKeyAuth"]],
    "search_repositories_with_security_findings": [["ApiKeyAuth"]],
    "search_security_findings_history": [["ApiKeyAuth"]],
    "search_security_category_finding": [["ApiKeyAuth"]],
    "upload_dast_report": [["ApiKeyAuth"]],
    "list_dast_reports": [["ApiKeyAuth"]],
    "list_security_managers": [["ApiKeyAuth"]],
    "assign_security_manager": [["ApiKeyAuth"]],
    "revoke_security_manager": [["ApiKeyAuth"]],
    "list_repositories_with_security_issues": [["ApiKeyAuth"]],
    "list_security_categories": [["ApiKeyAuth"]],
    "search_sbom_dependencies": [["ApiKeyAuth"]],
    "search_dependency_repositories": [["ApiKeyAuth"]],
    "search_sbom_repositories": [["ApiKeyAuth"]],
    "get_repository_sbom_download_url": [["ApiKeyAuth"]],
    "upload_image_sbom": [["ApiKeyAuth"]],
    "delete_image_sboms": [["ApiKeyAuth"]],
    "delete_image_tag_sbom": [["ApiKeyAuth"]],
    "list_organization_images": [["ApiKeyAuth"]],
    "list_image_tags": [["ApiKeyAuth"]],
    "list_jira_tickets": [["ApiKeyAuth"]],
    "create_jira_ticket": [["ApiKeyAuth"]],
    "unlink_jira_ticket": [["ApiKeyAuth"]],
    "get_jira_integration": [["ApiKeyAuth"]],
    "delete_jira_integration": [["ApiKeyAuth"]],
    "list_jira_projects": [["ApiKeyAuth"]],
    "list_jira_issue_types": [["ApiKeyAuth"]],
    "list_jira_issue_type_fields": [["ApiKeyAuth"]],
    "get_slack_integration": [["ApiKeyAuth"]],
    "get_pull_request_diff": [["ApiKeyAuth"]],
    "get_commit_diff": [["ApiKeyAuth"]],
    "get_commit_diff_between": [["ApiKeyAuth"]],
    "export_organization_security_items": [["ApiKeyAuth"]],
    "export_security_items_csv": [["ApiKeyAuth"]],
    "get_commit": [["ApiKeyAuth"]],
    "check_repository_quickfix_suggestions": [["ApiKeyAuth"]],
    "get_issue_quickfixes_patch": [["ApiKeyAuth"]],
    "get_pull_request_issues_patch": [["ApiKeyAuth"]],
    "list_organization_audit_logs": [["ApiKeyAuth"]],
    "get_segment_sync_status": [["ApiKeyAuth"]],
    "list_segment_keys": [["ApiKeyAuth"]],
    "list_segment_keys_with_ids": [["ApiKeyAuth"]],
    "list_segment_values": [["ApiKeyAuth"]],
    "list_dast_targets": [["ApiKeyAuth"]],
    "create_dast_target": [["ApiKeyAuth"]],
    "delete_dast_target": [["ApiKeyAuth"]],
    "trigger_dast_analysis": [["ApiKeyAuth"]],
    "list_enterprise_organizations": [["ApiKeyAuth"]],
    "list_enterprises": [["ApiKeyAuth"]],
    "get_enterprise": [["ApiKeyAuth"]],
    "list_enterprise_seats": [["ApiKeyAuth"]],
    "export_enterprise_seats_csv": [["ApiKeyAuth"]],
    "list_payment_plans": [["ApiKeyAuth"]],
    "get_ossf_scorecard": [["ApiKeyAuth"]]
}

"""
Authentication module for CircleCI MCP server.

Generated: 2026-05-05 14:37:07 UTC
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
    API Key authentication for CircleCI API.

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
    "get_project_workflow_summary": [["api_key_header"]],
    "list_job_timeseries": [["api_key_header"]],
    "get_org_summary": [["api_key_header"]],
    "list_project_branches": [["api_key_header"]],
    "list_flaky_tests": [["api_key_header"]],
    "list_workflow_metrics": [["api_key_header"]],
    "list_workflow_runs": [["api_key_header"]],
    "list_workflow_job_metrics": [["api_key_header"]],
    "get_workflow_summary": [["api_key_header"]],
    "get_workflow_test_metrics": [["api_key_header"]],
    "cancel_job": [["api_key_header"]],
    "get_current_user": [["api_key_header"]],
    "list_collaborations": [["api_key_header"]],
    "create_organization": [["api_key_header"]],
    "get_organization": [["api_key_header"]],
    "delete_organization": [["api_key_header"]],
    "create_project": [["api_key_header"]],
    "list_url_orb_allow_list_entries": [["api_key_header"]],
    "create_url_orb_allow_list_entry": [["api_key_header"]],
    "delete_url_orb_allow_list_entry": [["api_key_header"]],
    "list_pipelines": [["api_key_header"]],
    "continue_pipeline": [["api_key_header"]],
    "get_pipeline": [["api_key_header"]],
    "get_pipeline_config": [["api_key_header"]],
    "get_pipeline_values": [["api_key_header"]],
    "list_pipeline_workflows": [["api_key_header"]],
    "get_project": [["api_key_header"]],
    "delete_project": [["api_key_header"]],
    "list_checkout_keys": [["api_key_header"]],
    "create_checkout_key": [["api_key_header"]],
    "get_checkout_key": [["api_key_header"]],
    "delete_checkout_key": [["api_key_header"]],
    "list_env_vars": [["api_key_header"]],
    "create_env_var": [["api_key_header"]],
    "get_env_var": [["api_key_header"]],
    "delete_env_var": [["api_key_header"]],
    "get_job_details": [["api_key_header"]],
    "cancel_job_by_number": [["api_key_header"]],
    "list_project_pipelines": [["api_key_header"]],
    "trigger_pipeline": [["api_key_header"]],
    "list_my_pipelines": [["api_key_header"]],
    "get_pipeline_by_number": [["api_key_header"]],
    "list_project_schedules": [["api_key_header"]],
    "create_schedule": [["api_key_header"]],
    "list_job_artifacts": [["api_key_header"]],
    "list_job_tests": [["api_key_header"]],
    "get_schedule": [["api_key_header"]],
    "update_schedule": [["api_key_header"]],
    "delete_schedule": [["api_key_header"]],
    "get_user": [["api_key_header"]],
    "list_webhooks": [["api_key_header"]],
    "create_webhook": [["api_key_header"]],
    "get_webhook": [["api_key_header"]],
    "update_webhook": [["api_key_header"]],
    "delete_webhook": [["api_key_header"]],
    "get_workflow": [["api_key_header"]],
    "approve_workflow_job": [["api_key_header"]],
    "cancel_workflow": [["api_key_header"]],
    "list_workflow_jobs": [["api_key_header"]],
    "rerun_workflow": [["api_key_header"]],
    "list_org_oidc_custom_claims": [["api_key_header"]],
    "update_org_oidc_claims": [["api_key_header"]],
    "delete_org_oidc_claims": [["api_key_header"]],
    "get_project_oidc_claims": [["api_key_header"]],
    "update_project_oidc_claims": [["api_key_header"]],
    "delete_project_oidc_claims": [["api_key_header"]],
    "list_decision_logs": [["api_key_header"]],
    "get_decision_log": [["api_key_header"]],
    "get_decision_policy_bundle": [["api_key_header"]],
    "get_policy_bundle": [["api_key_header"]],
    "list_contexts": [["api_key_header"]],
    "create_context": [["api_key_header"]],
    "get_context": [["api_key_header"]],
    "delete_context": [["api_key_header"]],
    "list_context_environment_variables": [["api_key_header"]],
    "set_context_environment_variable": [["api_key_header"]],
    "delete_context_environment_variable": [["api_key_header"]],
    "list_context_restrictions": [["api_key_header"]],
    "add_context_restriction": [["api_key_header"]],
    "delete_context_restriction": [["api_key_header"]],
    "get_project_settings": [["api_key_header"]],
    "update_project_settings": [["api_key_header"]],
    "list_organization_groups": [["api_key_header"]],
    "create_group": [["api_key_header"]],
    "get_group": [["api_key_header"]],
    "delete_group": [["api_key_header"]],
    "create_usage_export": [["api_key_header"]],
    "get_usage_export_job": [["api_key_header"]],
    "trigger_pipeline_run": [["api_key_header"]],
    "list_pipeline_definitions": [["api_key_header"]],
    "create_pipeline_definition": [["api_key_header"]],
    "get_pipeline_definition": [["api_key_header"]],
    "update_pipeline_definition": [["api_key_header"]],
    "delete_pipeline_definition": [["api_key_header"]],
    "list_pipeline_definition_triggers": [["api_key_header"]],
    "create_pipeline_trigger": [["api_key_header"]],
    "get_trigger": [["api_key_header"]],
    "update_trigger": [["api_key_header"]],
    "delete_trigger": [["api_key_header"]],
    "rollback_project": [["api_key_header"]],
    "list_environments": [["api_key_header"]],
    "get_environment": [["api_key_header"]],
    "list_components": [["api_key_header"]],
    "get_component": [["api_key_header"]],
    "list_component_versions": [["api_key_header"]],
    "list_otel_exporters": [["api_key_header"]],
    "create_otlp_exporter": [["api_key_header"]],
    "delete_otlp_exporter": [["api_key_header"]]
}

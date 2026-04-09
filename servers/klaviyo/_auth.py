"""
Authentication module for Klaviyo API MCP server.

Generated: 2026-04-09 15:46:03 UTC
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
    API Key authentication for Klaviyo API.

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
    "get_accounts": [["Klaviyo-API-Key"]],
    "get_account": [["Klaviyo-API-Key"]],
    "list_campaigns": [["Klaviyo-API-Key"]],
    "get_campaign": [["Klaviyo-API-Key"]],
    "update_campaign": [["Klaviyo-API-Key"]],
    "delete_campaign": [["Klaviyo-API-Key"]],
    "get_campaign_message": [["Klaviyo-API-Key"]],
    "update_campaign_message": [["Klaviyo-API-Key"]],
    "get_campaign_send_job": [["Klaviyo-API-Key"]],
    "update_campaign_send_job": [["Klaviyo-API-Key"]],
    "get_campaign_recipient_estimation_job": [["Klaviyo-API-Key"]],
    "get_campaign_recipient_estimation": [["Klaviyo-API-Key"]],
    "clone_campaign": [["Klaviyo-API-Key"]],
    "assign_template_to_campaign_message": [["Klaviyo-API-Key"]],
    "send_campaign": [["Klaviyo-API-Key"]],
    "trigger_campaign_recipient_estimation": [["Klaviyo-API-Key"]],
    "get_campaign_for_campaign_message": [["Klaviyo-API-Key"]],
    "get_campaign_id_for_campaign_message": [["Klaviyo-API-Key"]],
    "get_template_for_campaign_message": [["Klaviyo-API-Key"]],
    "get_template_id_for_campaign_message": [["Klaviyo-API-Key"]],
    "get_image_for_campaign_message": [["Klaviyo-API-Key"]],
    "get_image_id_for_campaign_message": [["Klaviyo-API-Key"]],
    "update_image_for_campaign_message": [["Klaviyo-API-Key"]],
    "list_tags_for_campaign": [["Klaviyo-API-Key"]],
    "list_tag_ids_for_campaign": [["Klaviyo-API-Key"]],
    "list_messages_for_campaign": [["Klaviyo-API-Key"]],
    "list_message_ids_for_campaign": [["Klaviyo-API-Key"]],
    "list_catalog_items": [["Klaviyo-API-Key"]],
    "create_catalog_item": [["Klaviyo-API-Key"]],
    "get_catalog_item": [["Klaviyo-API-Key"]],
    "update_catalog_item": [["Klaviyo-API-Key"]],
    "delete_catalog_item": [["Klaviyo-API-Key"]],
    "list_catalog_variants": [["Klaviyo-API-Key"]],
    "create_catalog_variant": [["Klaviyo-API-Key"]],
    "get_catalog_variant": [["Klaviyo-API-Key"]],
    "update_catalog_variant": [["Klaviyo-API-Key"]],
    "delete_catalog_variant": [["Klaviyo-API-Key"]],
    "list_catalog_categories": [["Klaviyo-API-Key"]],
    "create_catalog_category": [["Klaviyo-API-Key"]],
    "get_catalog_category": [["Klaviyo-API-Key"]],
    "update_catalog_category": [["Klaviyo-API-Key"]],
    "delete_catalog_category": [["Klaviyo-API-Key"]],
    "list_bulk_create_catalog_items_jobs": [["Klaviyo-API-Key"]],
    "create_catalog_items_bulk_job": [["Klaviyo-API-Key"]],
    "get_bulk_create_catalog_items_job": [["Klaviyo-API-Key"]],
    "list_catalog_item_bulk_update_jobs": [["Klaviyo-API-Key"]],
    "create_catalog_item_bulk_update_job": [["Klaviyo-API-Key"]],
    "get_bulk_update_catalog_items_job": [["Klaviyo-API-Key"]],
    "list_bulk_delete_catalog_items_jobs": [["Klaviyo-API-Key"]],
    "create_catalog_item_bulk_delete_job": [["Klaviyo-API-Key"]],
    "get_bulk_delete_catalog_items_job": [["Klaviyo-API-Key"]],
    "list_bulk_create_variants_jobs": [["Klaviyo-API-Key"]],
    "create_catalog_variants_bulk": [["Klaviyo-API-Key"]],
    "get_bulk_create_variants_job": [["Klaviyo-API-Key"]],
    "list_bulk_update_variants_jobs": [["Klaviyo-API-Key"]],
    "create_catalog_variant_bulk_update_job": [["Klaviyo-API-Key"]],
    "get_bulk_update_variants_job": [["Klaviyo-API-Key"]],
    "list_bulk_delete_variants_jobs": [["Klaviyo-API-Key"]],
    "create_catalog_variant_bulk_delete_job": [["Klaviyo-API-Key"]],
    "get_bulk_delete_variants_job": [["Klaviyo-API-Key"]],
    "list_bulk_create_categories_jobs": [["Klaviyo-API-Key"]],
    "create_catalog_categories_bulk_job": [["Klaviyo-API-Key"]],
    "get_bulk_create_categories_job": [["Klaviyo-API-Key"]],
    "list_bulk_update_categories_jobs": [["Klaviyo-API-Key"]],
    "create_catalog_category_bulk_update_job": [["Klaviyo-API-Key"]],
    "get_bulk_update_categories_job": [["Klaviyo-API-Key"]],
    "list_bulk_delete_categories_jobs": [["Klaviyo-API-Key"]],
    "create_catalog_category_bulk_delete_job": [["Klaviyo-API-Key"]],
    "get_bulk_delete_categories_job": [["Klaviyo-API-Key"]],
    "create_back_in_stock_subscription": [["Klaviyo-API-Key"]],
    "list_items_for_catalog_category": [["Klaviyo-API-Key"]],
    "list_item_ids_for_catalog_category": [["Klaviyo-API-Key"]],
    "add_items_to_catalog_category": [["Klaviyo-API-Key"]],
    "update_items_for_catalog_category": [["Klaviyo-API-Key"]],
    "remove_items_from_catalog_category": [["Klaviyo-API-Key"]],
    "list_variants_for_catalog_item": [["Klaviyo-API-Key"]],
    "list_variant_ids_for_catalog_item": [["Klaviyo-API-Key"]],
    "list_categories_for_catalog_item": [["Klaviyo-API-Key"]],
    "list_category_ids_for_catalog_item": [["Klaviyo-API-Key"]],
    "add_categories_to_catalog_item": [["Klaviyo-API-Key"]],
    "update_categories_for_catalog_item": [["Klaviyo-API-Key"]],
    "remove_categories_from_catalog_item": [["Klaviyo-API-Key"]],
    "list_coupons": [["Klaviyo-API-Key"]],
    "create_coupon": [["Klaviyo-API-Key"]],
    "get_coupon": [["Klaviyo-API-Key"]],
    "update_coupon": [["Klaviyo-API-Key"]],
    "delete_coupon": [["Klaviyo-API-Key"]],
    "list_coupon_codes": [["Klaviyo-API-Key"]],
    "create_coupon_code": [["Klaviyo-API-Key"]],
    "get_coupon_code": [["Klaviyo-API-Key"]],
    "update_coupon_code": [["Klaviyo-API-Key"]],
    "delete_coupon_code": [["Klaviyo-API-Key"]],
    "list_coupon_code_bulk_create_jobs": [["Klaviyo-API-Key"]],
    "create_coupon_code_bulk_job": [["Klaviyo-API-Key"]],
    "get_coupon_code_bulk_create_job": [["Klaviyo-API-Key"]],
    "get_coupon_for_coupon_code": [["Klaviyo-API-Key"]],
    "get_coupon_relationship_for_coupon_code": [["Klaviyo-API-Key"]],
    "list_coupon_codes_for_coupon": [["Klaviyo-API-Key"]],
    "list_coupon_code_ids_for_coupon": [["Klaviyo-API-Key"]],
    "list_data_sources": [["Klaviyo-API-Key"]],
    "create_data_source": [["Klaviyo-API-Key"]],
    "get_data_source": [["Klaviyo-API-Key"]],
    "delete_data_source": [["Klaviyo-API-Key"]],
    "create_data_source_records_bulk": [["Klaviyo-API-Key"]],
    "create_data_source_record": [["Klaviyo-API-Key"]],
    "create_profile_deletion_job": [["Klaviyo-API-Key"]],
    "list_events": [["Klaviyo-API-Key"]],
    "create_event": [["Klaviyo-API-Key"]],
    "get_event": [["Klaviyo-API-Key"]],
    "create_events_bulk": [["Klaviyo-API-Key"]],
    "get_metric_for_event": [["Klaviyo-API-Key"]],
    "list_metrics_for_event": [["Klaviyo-API-Key"]],
    "get_profile_for_event": [["Klaviyo-API-Key"]],
    "get_profile_id_for_event": [["Klaviyo-API-Key"]],
    "list_flows": [["Klaviyo-API-Key"]],
    "get_flow": [["Klaviyo-API-Key"]],
    "update_flow_status": [["Klaviyo-API-Key"]],
    "delete_flow": [["Klaviyo-API-Key"]],
    "get_flow_action": [["Klaviyo-API-Key"]],
    "get_flow_message": [["Klaviyo-API-Key"]],
    "list_actions_for_flow": [["Klaviyo-API-Key"]],
    "list_action_ids_for_flow": [["Klaviyo-API-Key"]],
    "get_tags_for_flow": [["Klaviyo-API-Key"]],
    "list_tag_ids_for_flow": [["Klaviyo-API-Key"]],
    "get_flow_for_flow_action": [["Klaviyo-API-Key"]],
    "get_flow_relationship_for_flow_action": [["Klaviyo-API-Key"]],
    "list_flow_action_messages": [["Klaviyo-API-Key"]],
    "list_message_ids_for_flow_action": [["Klaviyo-API-Key"]],
    "get_flow_action_for_message": [["Klaviyo-API-Key"]],
    "get_flow_action_for_flow_message": [["Klaviyo-API-Key"]],
    "get_template_for_flow_message": [["Klaviyo-API-Key"]],
    "get_template_id_for_flow_message": [["Klaviyo-API-Key"]],
    "list_forms": [["Klaviyo-API-Key"]],
    "create_form": [["Klaviyo-API-Key"]],
    "get_form": [["Klaviyo-API-Key"]],
    "delete_form": [["Klaviyo-API-Key"]],
    "get_form_version": [["Klaviyo-API-Key"]],
    "list_versions_for_form": [["Klaviyo-API-Key"]],
    "list_version_ids_for_form": [["Klaviyo-API-Key"]],
    "get_form_for_form_version": [["Klaviyo-API-Key"]],
    "get_form_id_for_form_version": [["Klaviyo-API-Key"]],
    "list_images": [["Klaviyo-API-Key"]],
    "import_image_from_url": [["Klaviyo-API-Key"]],
    "get_image": [["Klaviyo-API-Key"]],
    "update_image": [["Klaviyo-API-Key"]],
    "create_image_from_file": [["Klaviyo-API-Key"]],
    "list_lists": [["Klaviyo-API-Key"]],
    "create_list": [["Klaviyo-API-Key"]],
    "get_list": [["Klaviyo-API-Key"]],
    "update_list": [["Klaviyo-API-Key"]],
    "delete_list": [["Klaviyo-API-Key"]],
    "list_tags_for_list": [["Klaviyo-API-Key"]],
    "list_tag_ids_for_list": [["Klaviyo-API-Key"]],
    "list_profiles_for_list": [["Klaviyo-API-Key"]],
    "list_profile_ids_for_list": [["Klaviyo-API-Key"]],
    "add_profiles_to_list": [["Klaviyo-API-Key"]],
    "remove_profiles_from_list": [["Klaviyo-API-Key"]],
    "list_flows_triggered_by_list": [["Klaviyo-API-Key"]],
    "list_flow_trigger_ids_for_list": [["Klaviyo-API-Key"]],
    "list_metrics": [["Klaviyo-API-Key"]],
    "get_metric": [["Klaviyo-API-Key"]],
    "get_metric_property": [["Klaviyo-API-Key"]],
    "list_custom_metrics": [["Klaviyo-API-Key"]],
    "create_custom_metric": [["Klaviyo-API-Key"]],
    "get_custom_metric": [["Klaviyo-API-Key"]],
    "update_custom_metric": [["Klaviyo-API-Key"]],
    "delete_custom_metric": [["Klaviyo-API-Key"]],
    "list_mapped_metrics": [["Klaviyo-API-Key"]],
    "get_mapped_metric": [["Klaviyo-API-Key"]],
    "update_mapped_metric": [["Klaviyo-API-Key"]],
    "query_metric_aggregates": [["Klaviyo-API-Key"]],
    "list_flows_triggered_by_metric": [["Klaviyo-API-Key"]],
    "list_flow_ids_triggered_by_metric": [["Klaviyo-API-Key"]],
    "get_metric_properties": [["Klaviyo-API-Key"]],
    "list_property_ids_for_metric": [["Klaviyo-API-Key"]],
    "get_metric_for_metric_property": [["Klaviyo-API-Key"]],
    "get_metric_id_for_metric_property": [["Klaviyo-API-Key"]],
    "get_metrics_for_custom_metric": [["Klaviyo-API-Key"]],
    "list_metrics_for_custom_metric": [["Klaviyo-API-Key"]],
    "get_metric_for_mapped_metric": [["Klaviyo-API-Key"]],
    "get_metric_id_for_mapped_metric": [["Klaviyo-API-Key"]],
    "get_custom_metric_for_mapped_metric": [["Klaviyo-API-Key"]],
    "get_custom_metric_id_for_mapped_metric": [["Klaviyo-API-Key"]],
    "list_profiles": [["Klaviyo-API-Key"]],
    "create_profile": [["Klaviyo-API-Key"]],
    "get_profile": [["Klaviyo-API-Key"]],
    "update_profile": [["Klaviyo-API-Key"]],
    "list_bulk_import_profiles_jobs": [["Klaviyo-API-Key"]],
    "create_profile_bulk_import_job": [["Klaviyo-API-Key"]],
    "get_bulk_import_profiles_job": [["Klaviyo-API-Key"]],
    "list_bulk_suppress_profiles_jobs": [["Klaviyo-API-Key"]],
    "create_profile_suppression_bulk_job": [["Klaviyo-API-Key"]],
    "get_bulk_suppress_profiles_job": [["Klaviyo-API-Key"]],
    "list_bulk_unsuppress_profiles_jobs": [["Klaviyo-API-Key"]],
    "remove_profile_suppressions_bulk": [["Klaviyo-API-Key"]],
    "get_bulk_unsuppress_profiles_job": [["Klaviyo-API-Key"]],
    "list_push_tokens": [["Klaviyo-API-Key"]],
    "create_or_update_push_token": [["Klaviyo-API-Key"]],
    "get_push_token": [["Klaviyo-API-Key"]],
    "delete_push_token": [["Klaviyo-API-Key"]],
    "create_or_update_profile": [["Klaviyo-API-Key"]],
    "merge_profiles": [["Klaviyo-API-Key"]],
    "subscribe_profiles_bulk": [["Klaviyo-API-Key"]],
    "unsubscribe_profiles_bulk": [["Klaviyo-API-Key"]],
    "list_push_tokens_for_profile": [["Klaviyo-API-Key"]],
    "list_push_token_ids_for_profile": [["Klaviyo-API-Key"]],
    "list_lists_for_profile": [["Klaviyo-API-Key"]],
    "get_lists_for_profile_relationship": [["Klaviyo-API-Key"]],
    "get_segments_for_profile": [["Klaviyo-API-Key"]],
    "list_segment_ids_for_profile": [["Klaviyo-API-Key"]],
    "get_lists_for_bulk_import_profiles_job": [["Klaviyo-API-Key"]],
    "get_list_ids_for_bulk_import_profiles_job": [["Klaviyo-API-Key"]],
    "list_profiles_for_bulk_import_job": [["Klaviyo-API-Key"]],
    "list_profile_ids_for_bulk_import_job": [["Klaviyo-API-Key"]],
    "list_import_errors_for_bulk_import_profiles_job": [["Klaviyo-API-Key"]],
    "get_profile_for_push_token": [["Klaviyo-API-Key"]],
    "get_profile_id_for_push_token": [["Klaviyo-API-Key"]],
    "query_campaign_values_report": [["Klaviyo-API-Key"]],
    "query_flow_values_report": [["Klaviyo-API-Key"]],
    "get_flow_series_analytics": [["Klaviyo-API-Key"]],
    "query_form_values_report": [["Klaviyo-API-Key"]],
    "get_form_series_analytics": [["Klaviyo-API-Key"]],
    "get_segment_values_report": [["Klaviyo-API-Key"]],
    "get_segment_series_report": [["Klaviyo-API-Key"]],
    "list_reviews": [["Klaviyo-API-Key"]],
    "get_review": [["Klaviyo-API-Key"]],
    "update_review": [["Klaviyo-API-Key"]],
    "list_segments": [["Klaviyo-API-Key"]],
    "create_segment": [["Klaviyo-API-Key"]],
    "get_segment": [["Klaviyo-API-Key"]],
    "update_segment": [["Klaviyo-API-Key"]],
    "delete_segment": [["Klaviyo-API-Key"]],
    "list_tags_for_segment": [["Klaviyo-API-Key"]],
    "list_tag_ids_for_segment": [["Klaviyo-API-Key"]],
    "list_profiles_for_segment": [["Klaviyo-API-Key"]],
    "list_profile_ids_for_segment": [["Klaviyo-API-Key"]],
    "list_flows_triggered_by_segment": [["Klaviyo-API-Key"]],
    "list_flow_ids_triggered_by_segment": [["Klaviyo-API-Key"]],
    "list_tags": [["Klaviyo-API-Key"]],
    "create_tag": [["Klaviyo-API-Key"]],
    "get_tag": [["Klaviyo-API-Key"]],
    "update_tag": [["Klaviyo-API-Key"]],
    "delete_tag": [["Klaviyo-API-Key"]],
    "list_tag_groups": [["Klaviyo-API-Key"]],
    "create_tag_group": [["Klaviyo-API-Key"]],
    "get_tag_group": [["Klaviyo-API-Key"]],
    "update_tag_group": [["Klaviyo-API-Key"]],
    "delete_tag_group": [["Klaviyo-API-Key"]],
    "list_flows_for_tag": [["Klaviyo-API-Key"]],
    "add_flows_to_tag": [["Klaviyo-API-Key"]],
    "remove_tag_from_flows": [["Klaviyo-API-Key"]],
    "list_campaign_ids_for_tag": [["Klaviyo-API-Key"]],
    "add_campaigns_to_tag": [["Klaviyo-API-Key"]],
    "remove_tag_from_campaigns": [["Klaviyo-API-Key"]],
    "list_lists_for_tag": [["Klaviyo-API-Key"]],
    "associate_lists_with_tag": [["Klaviyo-API-Key"]],
    "remove_tag_from_lists": [["Klaviyo-API-Key"]],
    "list_segment_ids_for_tag": [["Klaviyo-API-Key"]],
    "add_segments_to_tag": [["Klaviyo-API-Key"]],
    "remove_tag_from_segments": [["Klaviyo-API-Key"]],
    "get_tag_group_for_tag": [["Klaviyo-API-Key"]],
    "get_tag_group_id_for_tag": [["Klaviyo-API-Key"]],
    "list_tags_for_tag_group": [["Klaviyo-API-Key"]],
    "list_tag_ids_for_tag_group": [["Klaviyo-API-Key"]],
    "list_templates": [["Klaviyo-API-Key"]],
    "create_template": [["Klaviyo-API-Key"]],
    "get_template": [["Klaviyo-API-Key"]],
    "update_template": [["Klaviyo-API-Key"]],
    "delete_template": [["Klaviyo-API-Key"]],
    "list_universal_content": [["Klaviyo-API-Key"]],
    "create_universal_content": [["Klaviyo-API-Key"]],
    "get_universal_content": [["Klaviyo-API-Key"]],
    "update_template_universal_content": [["Klaviyo-API-Key"]],
    "delete_universal_content": [["Klaviyo-API-Key"]],
    "render_template": [["Klaviyo-API-Key"]],
    "create_template_clone": [["Klaviyo-API-Key"]],
    "get_tracking_settings": [["Klaviyo-API-Key"]],
    "get_tracking_setting": [["Klaviyo-API-Key"]],
    "list_web_feeds": [["Klaviyo-API-Key"]],
    "create_web_feed": [["Klaviyo-API-Key"]],
    "get_web_feed": [["Klaviyo-API-Key"]],
    "update_web_feed": [["Klaviyo-API-Key"]],
    "delete_web_feed": [["Klaviyo-API-Key"]],
    "list_webhooks": [["Klaviyo-API-Key"]],
    "get_webhook": [["Klaviyo-API-Key"]],
    "update_webhook": [["Klaviyo-API-Key"]],
    "delete_webhook": [["Klaviyo-API-Key"]],
    "list_webhook_topics": [["Klaviyo-API-Key"]],
    "get_webhook_topic": [["Klaviyo-API-Key"]],
    "list_client_review_values_reports": [],
    "list_client_reviews": [],
    "create_client_review": [],
    "create_client_subscription": [],
    "create_or_update_client_profile": [],
    "subscribe_profile_to_back_in_stock_notifications": []
}

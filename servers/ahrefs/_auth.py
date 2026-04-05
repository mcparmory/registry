"""
Authentication module for Ahrefs API MCP server.

Generated: 2026-04-05 19:42:41 UTC
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
    Bearer token authentication for Ahrefs API.

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
    "get_domain_rating": [["bearerAuth"]],
    "get_backlinks_stats": [["bearerAuth"]],
    "list_outlinks_stats": [["bearerAuth"]],
    "get_domain_metrics": [["bearerAuth"]],
    "get_refdomains_history": [["bearerAuth"]],
    "get_domain_rating_history": [["bearerAuth"]],
    "get_url_rating_history": [["bearerAuth"]],
    "list_page_history": [["bearerAuth"]],
    "get_domain_metrics_history": [["bearerAuth"]],
    "list_keyword_history": [["bearerAuth"]],
    "list_country_metrics": [["bearerAuth"]],
    "list_pages_by_traffic": [["bearerAuth"]],
    "get_search_volume_history": [["bearerAuth"]],
    "list_backlinks": [["bearerAuth"]],
    "list_broken_backlinks": [["bearerAuth"]],
    "list_refdomains": [["bearerAuth"]],
    "list_anchor_text": [["bearerAuth"]],
    "list_organic_keywords": [["bearerAuth"]],
    "list_organic_competitors": [["bearerAuth"]],
    "list_top_pages": [["bearerAuth"]],
    "list_paid_pages": [["bearerAuth"]],
    "list_pages_by_backlinks": [["bearerAuth"]],
    "list_pages_by_internal_links": [["bearerAuth"]],
    "list_linked_domains": [["bearerAuth"]],
    "list_external_anchors": [["bearerAuth"]],
    "list_internal_anchors": [["bearerAuth"]],
    "get_keyword_metrics": [["bearerAuth"]],
    "get_keyword_volume_history": [["bearerAuth"]],
    "get_keyword_volume_by_country": [["bearerAuth"]],
    "search_matching_keywords": [["bearerAuth"]],
    "list_related_keywords": [["bearerAuth"]],
    "search_keyword_suggestions": [["bearerAuth"]],
    "list_audit_projects": [["bearerAuth"]],
    "list_audit_issues": [["bearerAuth"]],
    "get_page_content": [["bearerAuth"]],
    "list_audit_pages": [["bearerAuth"]],
    "get_rank_tracker_overview": [["bearerAuth"]],
    "get_serp_overview": [["bearerAuth"]],
    "list_competitor_rankings": [["bearerAuth"]],
    "list_competitor_pages": [["bearerAuth"]],
    "list_competitor_stats": [["bearerAuth"]],
    "get_serp_overview_keyword": [["bearerAuth"]],
    "analyze_targets_batch": [["bearerAuth"]],
    "get_subscription_limits_and_usage": [["bearerAuth"]],
    "list_projects": [["bearerAuth"]],
    "create_project": [["bearerAuth"]],
    "update_project_access": [["bearerAuth"]],
    "list_project_keywords": [["bearerAuth"]],
    "add_keywords": [["bearerAuth"]],
    "delete_keywords": [["bearerAuth"]],
    "list_project_competitors": [["bearerAuth"]],
    "add_competitors": [["bearerAuth"]],
    "delete_competitors": [["bearerAuth"]],
    "list_locations": [["bearerAuth"]],
    "list_keyword_list_keywords": [["bearerAuth"]],
    "add_keywords_to_list": [["bearerAuth"]],
    "delete_keyword_list_keywords": [["bearerAuth"]],
    "list_brand_radar_prompts": [["bearerAuth"]],
    "create_brand_radar_prompt": [["bearerAuth"]],
    "delete_brand_radar_prompts": [["bearerAuth"]],
    "list_brand_radar_reports": [["bearerAuth"]],
    "create_brand_radar_report": [["bearerAuth"]],
    "update_brand_radar_report": [["bearerAuth"]],
    "list_ai_responses": [["bearerAuth"]],
    "list_cited_pages": [["bearerAuth"]],
    "list_cited_domains": [["bearerAuth"]],
    "list_brand_radar_impression_overviews": [["bearerAuth"]],
    "list_brand_mentions_overview": [["bearerAuth"]],
    "get_share_of_voice_overview": [["bearerAuth"]],
    "list_brand_mention_impressions_history": [["bearerAuth"]],
    "list_brand_mention_history": [["bearerAuth"]],
    "list_brand_sov_history": [["bearerAuth"]],
    "list_web_analytics_stats": [["bearerAuth"]],
    "get_web_analytics_chart": [["bearerAuth"]],
    "list_source_channels": [["bearerAuth"]],
    "get_source_channels_chart": [["bearerAuth"]],
    "list_traffic_sources": [["bearerAuth"]],
    "get_traffic_sources_chart": [["bearerAuth"]],
    "list_referrers": [["bearerAuth"]],
    "get_referrers_chart": [["bearerAuth"]],
    "list_utm_parameters": [["bearerAuth"]],
    "get_utm_params_chart": [["bearerAuth"]],
    "list_entry_pages": [["bearerAuth"]],
    "get_entry_pages_chart": [["bearerAuth"]],
    "list_exit_pages": [["bearerAuth"]],
    "get_exit_pages_chart": [["bearerAuth"]],
    "list_top_pages_by_pageviews": [["bearerAuth"]],
    "get_top_pages_chart": [["bearerAuth"]],
    "list_web_analytics_by_city": [["bearerAuth"]],
    "get_web_analytics_cities_chart": [["bearerAuth"]],
    "list_continent_analytics": [["bearerAuth"]],
    "get_continents_chart": [["bearerAuth"]],
    "list_web_analytics_by_country": [["bearerAuth"]],
    "get_countries_chart": [["bearerAuth"]],
    "list_language_analytics": [["bearerAuth"]],
    "get_language_analytics_chart": [["bearerAuth"]],
    "list_browser_analytics": [["bearerAuth"]],
    "get_browser_chart": [["bearerAuth"]],
    "list_browser_versions": [["bearerAuth"]],
    "get_browser_versions_chart": [["bearerAuth"]],
    "list_device_analytics": [["bearerAuth"]],
    "get_devices_chart": [["bearerAuth"]],
    "list_operating_systems_analytics": [["bearerAuth"]],
    "get_operating_systems_chart": [["bearerAuth"]],
    "list_operating_system_versions": [["bearerAuth"]],
    "get_operating_system_versions_chart": [["bearerAuth"]],
    "get_search_performance_history": [["bearerAuth"]],
    "list_keyword_position_history": [["bearerAuth"]],
    "list_page_history_gsc": [["bearerAuth"]],
    "list_device_performance": [["bearerAuth"]],
    "list_gsc_metrics_by_country": [["bearerAuth"]],
    "list_ctr_by_position": [["bearerAuth"]],
    "list_search_performance_by_position": [["bearerAuth"]],
    "list_keyword_history_gsc": [["bearerAuth"]],
    "list_gsc_keywords": [["bearerAuth"]],
    "get_page_history": [["bearerAuth"]],
    "list_gsc_pages": [["bearerAuth"]],
    "list_anonymous_queries": [["bearerAuth"]],
    "list_crawler_ips": [["bearerAuth"]],
    "list_crawler_ip_ranges": [["bearerAuth"]]
}

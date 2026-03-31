"""
Authentication module for Firecrawl API MCP server.

Generated: 2026-03-31 17:20:10 UTC
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
    "BearerTokenAuth",
    "OPERATION_AUTH_MAP",
]

# ============================================================================
# Authentication Classes
# ============================================================================

class BearerTokenAuth:
    """
    Bearer token authentication for Firecrawl API.

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
    "scrape_and_extract_webpage": [["bearerAuth"]],
    "scrape_and_extract_urls": [["bearerAuth"]],
    "get_batch_scrape_status": [["bearerAuth"]],
    "cancel_batch_scrape": [["bearerAuth"]],
    "list_batch_scrape_errors": [["bearerAuth"]],
    "get_crawl_status": [["bearerAuth"]],
    "cancel_crawl": [["bearerAuth"]],
    "list_crawl_errors": [["bearerAuth"]],
    "crawl_urls": [["bearerAuth"]],
    "crawl_urls_map": [["bearerAuth"]],
    "extract_structured_data": [["bearerAuth"]],
    "get_extraction_status": [["bearerAuth"]],
    "list_active_crawls": [["bearerAuth"]],
    "initiate_deep_research": [["bearerAuth"]],
    "get_deep_research_status": [["bearerAuth"]],
    "get_team_credit_usage": [["bearerAuth"]],
    "list_credit_usage_history": [["bearerAuth"]],
    "get_token_usage": [["bearerAuth"]],
    "list_token_usage_history": [["bearerAuth"]],
    "get_queue_status": [["bearerAuth"]],
    "search_and_scrape_results": [["bearerAuth"]],
    "generate_llms_txt": [["bearerAuth"]],
    "get_llms_txt_generation_status": [["bearerAuth"]]
}

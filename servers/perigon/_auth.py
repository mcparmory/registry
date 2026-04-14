"""
Authentication module for Perigon API MCP server.

Generated: 2026-04-14 18:30:19 UTC
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
    Bearer token authentication for Perigon API.

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
    "search_articles": [["apiKeyAuth"]],
    "search_companies": [["apiKeyAuth"]],
    "search_journalists": [["apiKeyAuth"]],
    "get_journalist": [["apiKeyAuth"]],
    "search_people": [["apiKeyAuth"]],
    "search_media_sources": [["apiKeyAuth"]],
    "search_stories": [["apiKeyAuth"]],
    "list_story_history": [["apiKeyAuth"]],
    "get_story_counts_by_time_interval": [["apiKeyAuth"]],
    "search_and_summarize_articles": [["apiKeyAuth"]],
    "search_topics": [["apiKeyAuth"]],
    "search_news_articles": [["apiKeyAuth"]],
    "search_wikipedia": [["apiKeyAuth"]],
    "search_wikipedia_pages": [["apiKeyAuth"]]
}

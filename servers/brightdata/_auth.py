"""
Authentication module for Bright Data MCP server.

Generated: 2026-05-11 23:11:12 UTC
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
    Bearer token authentication for Bright Data API.

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
    "list_cities": [["bearerAuth"]],
    "list_countries_by_zone": [["bearerAuth"]],
    "get_customer_balance": [["bearerAuth"]],
    "get_bandwidth_stats": [["bearerAuth"]],
    "get_zone_info": [["bearerAuth"]],
    "create_zone": [["bearerAuth"]],
    "delete_zone": [["bearerAuth"]],
    "list_zone_blacklisted_ips": [["bearerAuth"]],
    "add_ips_to_zone_denylist": [["bearerAuth"]],
    "delete_blacklist_entry": [["bearerAuth"]],
    "get_zone_bandwidth_stats": [["bearerAuth"]],
    "set_zone_status": [["bearerAuth"]],
    "count_available_ips": [["bearerAuth"]],
    "get_zone_cost": [["bearerAuth"]],
    "add_zone_domain_permission": [["bearerAuth"]],
    "list_active_zones": [["bearerAuth"]],
    "list_zones": [["bearerAuth"]],
    "list_zone_ips": [["bearerAuth"]],
    "add_zone_static_ips": [["bearerAuth"]],
    "remove_zone_ips": [["bearerAuth"]],
    "migrate_zone_ips": [["bearerAuth"]],
    "refresh_zone_ips": [["bearerAuth"]],
    "list_unavailable_zone_ips": [["bearerAuth"]],
    "list_zone_passwords": [["bearerAuth"]],
    "list_proxies_pending_replacement": [["bearerAuth"]],
    "list_zone_recent_ips": [["bearerAuth"]],
    "list_zone_route_ips": [["bearerAuth"]],
    "list_zone_dedicated_ips": [["bearerAuth"]],
    "list_static_cities": [["bearerAuth"]],
    "get_zone_status": [["bearerAuth"]],
    "toggle_zone_failover": [["bearerAuth"]],
    "remove_zone_vips": [["bearerAuth"]],
    "list_zone_whitelisted_ips": [["bearerAuth"]],
    "add_zone_whitelist_ip": [["bearerAuth"]],
    "delete_whitelist_ip": [["bearerAuth"]]
}

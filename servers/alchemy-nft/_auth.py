"""
Authentication module for Alchemy NFT MCP server.

Generated: 2026-04-23 20:56:56 UTC
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
    API Key authentication for 🎨 NFT API.

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
    "list_nfts_by_owner": [["ApiKeyAuth"]],
    "list_nfts_for_contract": [["ApiKeyAuth"]],
    "list_nfts_for_collection": [["ApiKeyAuth"]],
    "get_nft_metadata": [["ApiKeyAuth"]],
    "batch_retrieve_nft_metadata": [["ApiKeyAuth"]],
    "get_nft_contract_metadata": [["ApiKeyAuth"]],
    "get_collection_metadata": [["ApiKeyAuth"]],
    "batch_get_contract_metadata": [["ApiKeyAuth"]],
    "get_nft_owners": [["ApiKeyAuth"]],
    "list_nft_contract_owners": [["ApiKeyAuth"]],
    "list_spam_contracts": [["ApiKeyAuth"]],
    "check_spam_contract": [["ApiKeyAuth"]],
    "check_nft_airdrop": [["ApiKeyAuth"]],
    "get_nft_collection_attribute_summary": [["ApiKeyAuth"]],
    "get_nft_collection_floor_prices": [["ApiKeyAuth"]],
    "search_contract_metadata": [["ApiKeyAuth"]],
    "check_nft_holder": [["ApiKeyAuth"]],
    "calculate_nft_attribute_rarity": [["ApiKeyAuth"]],
    "list_nft_sales": [["ApiKeyAuth"]],
    "list_nft_contracts_by_owner": [["ApiKeyAuth"]],
    "list_nft_collections_by_owner": [["ApiKeyAuth"]],
    "report_spam_address": [["ApiKeyAuth"]],
    "refresh_nft_metadata": [["ApiKeyAuth"]],
    "list_nfts": [["ApiKeyAuth"]],
    "get_token_owners": [["ApiKeyAuth"]],
    "list_nft_collection_owners": [["ApiKeyAuth"]],
    "check_token_airdrop": [["ApiKeyAuth"]],
    "check_wallet_nft_collection_ownership": [["ApiKeyAuth"]]
}

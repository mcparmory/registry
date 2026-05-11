"""
Authentication module for BuiltWith MCP server.

Generated: 2026-05-11 23:13:29 UTC
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
    API Key authentication for BuiltWith API.

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
    "detect_technologies": [["apiKeyQuery"]],
    "get_domain_technologies": [["apiKeyQuery"]],
    "get_domain_technologies_csv": [["apiKeyQuery"]],
    "bulk_lookup_domains": [["apiKeyQuery"]],
    "get_bulk_domain_job_status": [["apiKeyQuery"]],
    "retrieve_bulk_domain_job_result": [["apiKeyQuery"]],
    "get_domain_technology_summary": [["apiKeyQuery"]],
    "get_domain_technology_summary_xml": [["apiKeyQuery"]],
    "list_website_relationships": [["apiKeyQuery"]],
    "list_website_relationships_xml": [["apiKeyQuery"]],
    "list_website_relationships_csv": [["apiKeyQuery"]],
    "list_website_relationships_tsv": [["apiKeyQuery"]],
    "list_websites_by_technology": [["apiKeyQuery"]],
    "list_websites_by_technology_xml": [["apiKeyQuery"]],
    "lookup_company_domains": [["apiKeyQuery"]],
    "resolve_company_domains": [["apiKeyQuery"]],
    "list_domains_by_attribute": [["apiKeyQuery"]],
    "list_domains_by_attribute_xml": [["apiKeyQuery"]],
    "get_technology_recommendations": [["apiKeyQuery"]],
    "get_technology_recommendations_xml": [["apiKeyQuery"]],
    "get_domain_redirects": [["apiKeyQuery"]],
    "get_domain_redirects_xml": [["apiKeyQuery"]],
    "list_domain_keywords": [["apiKeyQuery"]],
    "extract_domain_keywords": [["apiKeyQuery"]],
    "search_websites_by_keyword": [["apiKeyQuery"]],
    "search_websites_by_keyword_csv": [["apiKeyQuery"]],
    "search_technologies": [["apiKeyQuery"]],
    "search_technologies_xml": [["apiKeyQuery"]],
    "search_technologies_csv": [["apiKeyQuery"]],
    "get_technology_trends": [["apiKeyQuery"]],
    "get_technology_trends_xml": [["apiKeyQuery"]],
    "search_product_listings": [["apiKeyQuery"]],
    "assess_domain_trust": [["apiKeyQuery"]],
    "assess_domain_trust_xml": [["apiKeyQuery"]]
}

"""
Builtwith Api MCP Server - Pydantic Models

Generated: 2026-04-09 17:16:41 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "GetV22ApiCsvRequest",
    "GetV22ApiJsonRequest",
    "GetV22ApiXmlRequest",
    "GetV22Ctu3ApiJsonRequest",
    "GetV22Ctu3ApiXmlRequest",
    "GetV22DomainBulkJobIdRequest",
    "GetV22DomainBulkJobIdResultRequest",
    "GetV22Free1ApiJsonRequest",
    "GetV22Free1ApiXmlRequest",
    "GetV22Kw2ApiJsonRequest",
    "GetV22Kw2ApiXmlRequest",
    "GetV22Kws1ApiCsvRequest",
    "GetV22Kws1ApiJsonRequest",
    "GetV22Lists12ApiJsonRequest",
    "GetV22Lists12ApiXmlRequest",
    "GetV22Productv1ApiJsonRequest",
    "GetV22Rec1ApiJsonRequest",
    "GetV22Rec1ApiXmlRequest",
    "GetV22Redirect1ApiJsonRequest",
    "GetV22Redirect1ApiXmlRequest",
    "GetV22Rv4ApiCsvRequest",
    "GetV22Rv4ApiJsonRequest",
    "GetV22Rv4ApiTsvRequest",
    "GetV22Rv4ApiXmlRequest",
    "GetV22Tag1ApiJsonRequest",
    "GetV22Tag1ApiXmlRequest",
    "GetV22TrendsV6ApiJsonRequest",
    "GetV22TrendsV6ApiXmlRequest",
    "GetV22Trustv1ApiJsonRequest",
    "GetV22Trustv1ApiXmlRequest",
    "GetV22VectorV1ApiCsvRequest",
    "GetV22VectorV1ApiJsonRequest",
    "GetV22VectorV1ApiXmlRequest",
    "PostV22DomainBulkRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: detect_technologies
class GetV22ApiJsonRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="Single domain or comma-separated list of up to 16 domains to analyze (e.g., example.com or example.com,other.com,another.com).")
    liveonly: Literal["yes"] | None = Field(default=None, validation_alias="LIVEONLY", serialization_alias="LIVEONLY", description="Filter results to only include technologies currently active on the domain.")
    trust: Literal["yes"] | None = Field(default=None, validation_alias="TRUST", serialization_alias="TRUST", description="Enrich results with additional trust and security data from the Trust API (consumes extra API credits).")
    nometa: Literal["yes"] | None = Field(default=None, validation_alias="NOMETA", serialization_alias="NOMETA", description="Exclude metadata such as business addresses and contact names to reduce response size and improve performance.")
    nopii: Literal["yes"] | None = Field(default=None, validation_alias="NOPII", serialization_alias="NOPII", description="Remove personally identifiable information including people names and email addresses (EU and California PII automatically redacted regardless).")
    fdrange: str | None = Field(default=None, validation_alias="FDRANGE", serialization_alias="FDRANGE", description="Filter technologies by first detection date range using ISO 8601 format (start_date|end_date, e.g., 2022-01-01|2023-01-01).")
    ldrange: str | None = Field(default=None, validation_alias="LDRANGE", serialization_alias="LDRANGE", description="Filter technologies by last detection date range using ISO 8601 format (start_date|end_date, e.g., 2022-01-01|2023-01-01).")
    noattr: Literal["yes"] | None = Field(default=None, validation_alias="NOATTR", serialization_alias="NOATTR", description="Exclude technology attributes data to reduce response size and improve performance.")
class GetV22ApiJsonRequest(StrictModel):
    """Detect and retrieve technology stack information for one or more websites. Returns comprehensive details about installed technologies, metadata, and detection attributes in JSON format."""
    query: GetV22ApiJsonRequestQuery

# Operation: get_domain_technologies
class GetV22ApiXmlRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="A single root domain or comma-separated list of up to 16 domains to analyze for technology detection.")
    liveonly: Literal["yes"] | None = Field(default=None, validation_alias="LIVEONLY", serialization_alias="LIVEONLY", description="When enabled, returns only technologies currently active on the domain, filtering out historical or inactive detections.")
    trust: Literal["yes"] | None = Field(default=None, validation_alias="TRUST", serialization_alias="TRUST", description="When enabled, includes additional Trust API data alongside technology information for enhanced security and reputation insights.")
    nometa: Literal["yes"] | None = Field(default=None, validation_alias="NOMETA", serialization_alias="NOMETA", description="When enabled, excludes metadata from the response to reduce payload size and improve response performance.")
    nopii: Literal["yes"] | None = Field(default=None, validation_alias="NOPII", serialization_alias="NOPII", description="When enabled, removes personally identifiable information such as people names and email addresses from the results.")
    fdrange: str | None = Field(default=None, validation_alias="FDRANGE", serialization_alias="FDRANGE", description="Filters technologies to include only those first detected within a specified date range. Use ISO 8601 format for date specification.")
    ldrange: str | None = Field(default=None, validation_alias="LDRANGE", serialization_alias="LDRANGE", description="Filters technologies to include only those last detected within a specified date range. Use ISO 8601 format for date specification.")
    noattr: Literal["yes"] | None = Field(default=None, validation_alias="NOATTR", serialization_alias="NOATTR", description="When enabled, excludes technology attributes from the response to reduce payload size and improve response performance.")
class GetV22ApiXmlRequest(StrictModel):
    """Retrieve detected technologies and metadata for one or more domains in XML format. Supports filtering by detection dates, trust data inclusion, and optional data exclusion for performance optimization."""
    query: GetV22ApiXmlRequestQuery

# Operation: get_domain_technologies_csv
class GetV22ApiCsvRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="A single root domain or comma-separated list of up to 16 domains to analyze for technology detection.")
    liveonly: Literal["yes"] | None = Field(default=None, validation_alias="LIVEONLY", serialization_alias="LIVEONLY", description="When set to 'yes', returns only technologies currently active on the domain, excluding deprecated or historical detections.")
    nometa: Literal["yes"] | None = Field(default=None, validation_alias="NOMETA", serialization_alias="NOMETA", description="When set to 'yes', excludes metadata fields from the response to reduce payload size.")
    nopii: Literal["yes"] | None = Field(default=None, validation_alias="NOPII", serialization_alias="NOPII", description="When set to 'yes', removes personally identifiable information such as people names and email addresses from the results.")
    noattr: Literal["yes"] | None = Field(default=None, validation_alias="NOATTR", serialization_alias="NOATTR", description="When set to 'yes', excludes attribute data from the response to reduce payload size.")
class GetV22ApiCsvRequest(StrictModel):
    """Retrieve technology stack information for one or more websites in CSV format. Supports batch lookups of up to 16 domains with optional filtering and data reduction."""
    query: GetV22ApiCsvRequestQuery

# Operation: bulk_lookup_domains
class PostV22DomainBulkRequestBodyOptions(StrictModel):
    no_meta: bool | None = Field(default=None, validation_alias="noMeta", serialization_alias="noMeta", description="Exclude metadata from the response to reduce payload size and improve performance.")
    no_pii: bool | None = Field(default=None, validation_alias="noPii", serialization_alias="noPii", description="Strip personally identifiable information from results to ensure privacy compliance.")
    live_only: bool | None = Field(default=None, validation_alias="liveOnly", serialization_alias="liveOnly", description="Return only technologies that are currently active or deployed on the domains, filtering out historical or inactive detections.")
class PostV22DomainBulkRequestBody(StrictModel):
    lookups: list[str] = Field(default=..., description="Array of root domains to analyze. Each item should be a valid domain name. Order is preserved in results.")
    options: PostV22DomainBulkRequestBodyOptions | None = None
class PostV22DomainBulkRequest(StrictModel):
    """Submit multiple root domains for technology stack analysis. Small batches return results immediately, while large batches are processed asynchronously and return a job ID for tracking."""
    body: PostV22DomainBulkRequestBody

# Operation: get_bulk_domain_job_status
class GetV22DomainBulkJobIdRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk job, provided as a UUID.", json_schema_extra={'format': 'uuid'})
class GetV22DomainBulkJobIdRequest(StrictModel):
    """Retrieve the current status and results of a bulk domain lookup job. Use this to check progress and retrieve completed domain information."""
    path: GetV22DomainBulkJobIdRequestPath

# Operation: retrieve_bulk_domain_job_result
class GetV22DomainBulkJobIdResultRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk job, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetV22DomainBulkJobIdResultRequest(StrictModel):
    """Retrieve the results of a completed bulk domain lookup job. Note that results are automatically deleted after the first access, so this is a one-time download operation."""
    path: GetV22DomainBulkJobIdResultRequestPath

# Operation: get_domain_technology_summary
class GetV22Free1ApiJsonRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="The domain to analyze. Provide only the root domain (e.g., hotelscombined.com); subdomains will automatically resolve to their root domain.")
class GetV22Free1ApiJsonRequest(StrictModel):
    """Retrieve technology stack metadata for a domain, including last updated timestamp and counts of active and inactive technologies organized by group and category."""
    query: GetV22Free1ApiJsonRequestQuery

# Operation: get_domain_technology_summary_xml
class GetV22Free1ApiXmlRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="The domain to analyze. Only root domain results are returned; subdomains are automatically resolved to their root domain.")
class GetV22Free1ApiXmlRequest(StrictModel):
    """Retrieve technology group and category metadata for a domain, including last updated timestamp and counts of active and inactive technologies."""
    query: GetV22Free1ApiXmlRequestQuery

# Operation: list_website_relationships
class GetV22Rv4ApiJsonRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="One or more domains to analyze for relationships. Accepts individual domains, subdomains, or up to 16 domains as comma-separated values for batch lookups.")
    ip: Literal["yes"] | None = Field(default=None, validation_alias="IP", serialization_alias="IP", description="Optional flag to include website IP address data in the results, which significantly expands the relationship data returned.")
class GetV22Rv4ApiJsonRequest(StrictModel):
    """Retrieve the network of relationships between websites, showing which sites are linked together. Results are returned in JSON format and consume 1 API credit per 500 relationships."""
    query: GetV22Rv4ApiJsonRequestQuery

# Operation: list_website_relationships_xml
class GetV22Rv4ApiXmlRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="One or more domains to analyze for relationships. Accepts individual domains, subdomains, or up to 16 domains as comma-separated values for batch lookups.")
    ip: Literal["yes"] | None = Field(default=None, validation_alias="IP", serialization_alias="IP", description="Optional flag to include IP address data for the websites in the response.")
class GetV22Rv4ApiXmlRequest(StrictModel):
    """Retrieve relationships between websites showing which sites are linked together in XML format. Each request consumes 1 API credit per 500 relationships returned."""
    query: GetV22Rv4ApiXmlRequestQuery

# Operation: list_website_relationships_csv
class GetV22Rv4ApiCsvRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="The domain name to lookup and analyze for relationships. Specify a single domain (e.g., builtwith.com) to retrieve all linked websites.")
    ip: Literal["yes"] | None = Field(default=None, validation_alias="IP", serialization_alias="IP", description="Optional flag to include IP address data for the websites in the results. Set to 'yes' to enable IP data retrieval.")
class GetV22Rv4ApiCsvRequest(StrictModel):
    """Retrieve relationships between websites showing which sites are linked together in CSV format. Each request consumes 1 API credit per 500 relationships returned."""
    query: GetV22Rv4ApiCsvRequestQuery

# Operation: list_website_relationships_tsv
class GetV22Rv4ApiTsvRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="The domain or domains to analyze for relationship data. Specify one or more domains to discover their linking relationships with other websites.")
    ip: Literal["yes"] | None = Field(default=None, validation_alias="IP", serialization_alias="IP", description="Optional flag to include IP address information for the websites in the results. Set to 'yes' to retrieve IP data alongside relationship data.")
class GetV22Rv4ApiTsvRequest(StrictModel):
    """Retrieve relationships between websites showing which sites link to each other in TSV format. Each API credit covers up to 500 relationships."""
    query: GetV22Rv4ApiTsvRequestQuery

# Operation: list_websites_by_technology
class GetV22Lists12ApiJsonRequestQuery(StrictModel):
    tech: str = Field(default=..., validation_alias="TECH", serialization_alias="TECH", description="The name of the web technology to search for, with spaces replaced by dashes (e.g., 'Shopify' becomes 'Shopify'). This is the core search parameter.")
    meta: Literal["yes"] | None = Field(default=None, validation_alias="META", serialization_alias="META", description="Include enriched metadata with results such as company names, titles, social media links, addresses, email addresses, phone numbers, and traffic rankings.")
    country: str | None = Field(default=None, validation_alias="COUNTRY", serialization_alias="COUNTRY", description="Filter results to websites with specific country domains and/or country addresses. Specify one or more countries using ISO 3166-1 alpha-2 format (e.g., 'br' for Brazil), separated by commas for multiple countries. Use 'UK' instead of 'GB' for the United Kingdom.")
class GetV22Lists12ApiJsonRequest(StrictModel):
    """Retrieve a list of websites currently using a specified web technology. Optionally filter by country and include detailed metadata such as company names, contact information, and traffic rankings."""
    query: GetV22Lists12ApiJsonRequestQuery

# Operation: list_websites_by_technology_xml
class GetV22Lists12ApiXmlRequestQuery(StrictModel):
    tech: str = Field(default=..., validation_alias="TECH", serialization_alias="TECH", description="The name of the web technology to search for. Replace spaces with dashes in the technology name (e.g., 'Magento' or 'Google-Analytics').")
    meta: Literal["yes"] | None = Field(default=None, validation_alias="META", serialization_alias="META", description="Include detailed metadata with results such as company names, titles, social media links, addresses, email addresses, phone numbers, and traffic rankings.")
    country: str | None = Field(default=None, validation_alias="COUNTRY", serialization_alias="COUNTRY", description="Filter results by country using ISO 3166-1 alpha-2 country codes (e.g., 'br' for Brazil, 'uk' for United Kingdom). Specify multiple countries as comma-separated values (e.g., 'au,nz').")
class GetV22Lists12ApiXmlRequest(StrictModel):
    """Retrieve a list of websites currently using a specified web technology. Optionally filter by country and include detailed metadata such as company names, contact information, and traffic rankings."""
    query: GetV22Lists12ApiXmlRequestQuery

# Operation: lookup_company_domains
class GetV22Ctu3ApiJsonRequestQuery(StrictModel):
    company: str = Field(default=..., validation_alias="COMPANY", serialization_alias="COMPANY", description="One or more company names to look up, provided as a single name or as a comma-separated list of names (URL encoded).")
class GetV22Ctu3ApiJsonRequest(StrictModel):
    """Retrieve domain names and websites associated with one or more company names, ordered by relevance to help identify official web presences."""
    query: GetV22Ctu3ApiJsonRequestQuery

# Operation: resolve_company_domains
class GetV22Ctu3ApiXmlRequestQuery(StrictModel):
    company: str = Field(default=..., validation_alias="COMPANY", serialization_alias="COMPANY", description="A single company name or comma-separated list of company names to look up. Each company name should be URL encoded if containing special characters.")
class GetV22Ctu3ApiXmlRequest(StrictModel):
    """Resolve domain names and websites for one or more company names. Supply a single company name or a comma-separated list of company names to retrieve associated domain information in XML format."""
    query: GetV22Ctu3ApiXmlRequestQuery

# Operation: list_domains_by_attribute
class GetV22Tag1ApiJsonRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="The attribute to search for, specified in ATTRIBUTE-TYPE-CODE format (e.g., IP-98.158.194.127 or CA-PUB-1894893914772263). You can provide up to 16 comma-separated values to lookup multiple attributes in a single request.")
    types: bool | None = Field(default=None, validation_alias="TYPES", serialization_alias="TYPES", description="Set to true to retrieve the list of available attribute types that can be used in lookups instead of searching for domains.")
class GetV22Tag1ApiJsonRequest(StrictModel):
    """Retrieve a list of domains that share a common attribute such as an IP address, Google Analytics tag, or other identifier. Optionally retrieve available attribute types for lookup."""
    query: GetV22Tag1ApiJsonRequestQuery

# Operation: list_domains_by_attribute_xml
class GetV22Tag1ApiXmlRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="The attribute to search for, specified in ATTRIBUTE-TYPE-CODE format (e.g., IP-98.158.194.127 for IP addresses or CA-PUB-1894893914772263 for Google Analytics tags). You can provide up to 16 comma-separated values to search for multiple attributes at once.")
    types: bool | None = Field(default=None, validation_alias="TYPES", serialization_alias="TYPES", description="Set to true to retrieve the list of available attribute types that can be used for lookups instead of searching for domains.")
class GetV22Tag1ApiXmlRequest(StrictModel):
    """Retrieve a list of domains that share a specific attribute such as an IP address, Google Analytics tag, or other identifier in XML format."""
    query: GetV22Tag1ApiXmlRequestQuery

# Operation: get_technology_recommendations
class GetV22Rec1ApiJsonRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="One or more root domains to analyze, provided as a single domain or comma-separated list of up to 16 domains. Only alphanumeric characters, dots, hyphens, and commas are allowed.", pattern='^[a-zA-Z0-9.,-]+$')
class GetV22Rec1ApiJsonRequest(StrictModel):
    """Retrieve technology recommendations for websites based on analysis of similar technology profiles. Accepts one or more domains to identify recommended technologies used by comparable sites."""
    query: GetV22Rec1ApiJsonRequestQuery

# Operation: get_technology_recommendations_xml
class GetV22Rec1ApiXmlRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="One or more root domains to analyze, provided as a single domain or comma-separated list of up to 16 domains. Only alphanumeric characters, dots, hyphens, and commas are allowed.", pattern='^[a-zA-Z0-9.,-]+$')
class GetV22Rec1ApiXmlRequest(StrictModel):
    """Retrieve technology stack recommendations for websites based on analysis of similar technology profiles. Returns results in XML format."""
    query: GetV22Rec1ApiXmlRequestQuery

# Operation: get_domain_redirects
class GetV22Redirect1ApiJsonRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="The root domain to look up (e.g., hotelscombined.com). Only root domains are supported; internal pages and subdomains are not valid.")
class GetV22Redirect1ApiJsonRequest(StrictModel):
    """Retrieve live and historical redirect information for a domain, including both inbound and outbound redirects in JSON format."""
    query: GetV22Redirect1ApiJsonRequestQuery

# Operation: get_domain_redirects_xml
class GetV22Redirect1ApiXmlRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="The root domain to look up redirects for. Only root domains are supported (e.g., builtwith.com); internal pages and subdomains are not accepted.")
class GetV22Redirect1ApiXmlRequest(StrictModel):
    """Retrieve live and historical redirect information for a domain in XML format. Returns both inbound and outbound redirects that point to or from the specified domain."""
    query: GetV22Redirect1ApiXmlRequestQuery

# Operation: list_domain_keywords
class GetV22Kw2ApiJsonRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="One or more root domains to analyze (e.g., cnn.com). Use comma-separated values to look up multiple domains at once, up to 16 domains maximum. Only root domains are supported; subdomains and internal page URLs will not work.")
class GetV22Kw2ApiJsonRequest(StrictModel):
    """Retrieve keywords found on one or more domains. Useful for understanding the primary topics and content focus of websites."""
    query: GetV22Kw2ApiJsonRequestQuery

# Operation: extract_domain_keywords
class GetV22Kw2ApiXmlRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="One or more root domains to analyze for keywords. Provide a single domain (e.g., hotelscombined.com) or multiple domains in comma-separated format for batch lookup of up to 16 domains. Subdomains and internal page URLs are not supported.")
class GetV22Kw2ApiXmlRequest(StrictModel):
    """Extract keywords found on one or more domains and return the results in XML format. Useful for SEO analysis and understanding domain content focus."""
    query: GetV22Kw2ApiXmlRequestQuery

# Operation: search_websites_by_keyword
class GetV22Kws1ApiJsonRequestQuery(StrictModel):
    keyword: str = Field(default=..., validation_alias="KEYWORD", serialization_alias="KEYWORD", description="The keyword to search for. Must be at least 4 letters long, contain only alphabetical characters, and cannot be a common stop word (e.g., 'the', 'and').", min_length=4)
    limit: int | None = Field(default=None, validation_alias="LIMIT", serialization_alias="LIMIT", description="Number of results to return, ranging from 16 to 1000 domains. Defaults to 100 results if not specified.", ge=16, le=1000)
class GetV22Kws1ApiJsonRequest(StrictModel):
    """Search for websites containing specific keywords. Returns a list of domain names that match your search criteria, useful for market research, competitor analysis, or finding relevant web properties."""
    query: GetV22Kws1ApiJsonRequestQuery

# Operation: search_websites_by_keyword_csv
class GetV22Kws1ApiCsvRequestQuery(StrictModel):
    keyword: str = Field(default=..., validation_alias="KEYWORD", serialization_alias="KEYWORD", description="The keyword to search for. Must be at least 4 characters long, contain only alphabetical characters, and cannot be a common stop word.", min_length=4)
    limit: int | None = Field(default=None, validation_alias="LIMIT", serialization_alias="LIMIT", description="The number of results to return, ranging from 16 to 1000 results. Defaults to 100 if not specified.", ge=16, le=1000)
class GetV22Kws1ApiCsvRequest(StrictModel):
    """Search for websites containing a specific keyword and retrieve results in CSV format. Useful for finding web properties associated with particular topics or terms."""
    query: GetV22Kws1ApiCsvRequestQuery

# Operation: search_technologies
class GetV22VectorV1ApiJsonRequestQuery(StrictModel):
    query: str = Field(default=..., validation_alias="QUERY", serialization_alias="QUERY", description="The search query describing the technologies or categories you want to find (e.g., 'react framework'). Use natural language to describe what you're looking for.")
    limit: int | None = Field(default=None, validation_alias="LIMIT", serialization_alias="LIMIT", description="Maximum number of results to return in the response. Must be between 1 and 100 results; defaults to 10 if not specified.", ge=1, le=100)
class GetV22VectorV1ApiJsonRequest(StrictModel):
    """Search for technologies and categories using natural language queries powered by vector similarity matching. Discover relevant tools and categories by describing what you're looking for."""
    query: GetV22VectorV1ApiJsonRequestQuery

# Operation: search_technologies_xml
class GetV22VectorV1ApiXmlRequestQuery(StrictModel):
    query: str = Field(default=..., validation_alias="QUERY", serialization_alias="QUERY", description="The search query describing the technology or category you want to find (e.g., 'google analytics', 'web tracking', 'analytics platform')")
    limit: int | None = Field(default=None, validation_alias="LIMIT", serialization_alias="LIMIT", description="Maximum number of results to return, between 1 and 100 (defaults to 10 if not specified)", ge=1, le=100)
class GetV22VectorV1ApiXmlRequest(StrictModel):
    """Search for technologies and categories using natural language queries powered by vector similarity matching. Describe what you're looking for to discover relevant technologies and their categories."""
    query: GetV22VectorV1ApiXmlRequestQuery

# Operation: search_technologies_csv
class GetV22VectorV1ApiCsvRequestQuery(StrictModel):
    query: str = Field(default=..., validation_alias="QUERY", serialization_alias="QUERY", description="The search query describing the technologies or categories you want to find (e.g., 'ecommerce platform'). Use natural language to describe what you're looking for.")
    limit: int | None = Field(default=None, validation_alias="LIMIT", serialization_alias="LIMIT", description="Maximum number of results to return in the response. Must be between 1 and 100 results; defaults to 10 if not specified.", ge=1, le=100)
class GetV22VectorV1ApiCsvRequest(StrictModel):
    """Search for technologies and categories using natural language queries powered by vector similarity matching. Returns matching results in CSV format for easy integration and analysis."""
    query: GetV22VectorV1ApiCsvRequestQuery

# Operation: get_technology_trends
class GetV22TrendsV6ApiJsonRequestQuery(StrictModel):
    tech: str = Field(default=..., validation_alias="TECH", serialization_alias="TECH", description="The name of the technology to retrieve trends for. Use hyphens (-) instead of spaces in multi-word technology names (e.g., 'Magento').")
    date: str | None = Field(default=None, validation_alias="DATE", serialization_alias="DATE", description="Optional date to retrieve historical trend totals. When provided, returns the trend data closest to the specified date in ISO 8601 format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class GetV22TrendsV6ApiJsonRequest(StrictModel):
    """Retrieve technology trend data in JSON format for a specified technology, optionally filtered to a specific date."""
    query: GetV22TrendsV6ApiJsonRequestQuery

# Operation: get_technology_trends_xml
class GetV22TrendsV6ApiXmlRequestQuery(StrictModel):
    tech: str = Field(default=..., validation_alias="TECH", serialization_alias="TECH", description="The name of the technology to retrieve trends for. Use hyphens to replace spaces in multi-word technology names (e.g., 'Shopify' or 'Node-js').")
    date: str | None = Field(default=None, validation_alias="DATE", serialization_alias="DATE", description="Optional date to retrieve historical trend data. When provided, returns trend totals closest to the specified date in ISO 8601 format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class GetV22TrendsV6ApiXmlRequest(StrictModel):
    """Retrieve technology trend data in XML format for a specified technology, optionally filtered to a specific date."""
    query: GetV22TrendsV6ApiXmlRequestQuery

# Operation: search_product_listings
class GetV22Productv1ApiJsonRequestQuery(StrictModel):
    query: str = Field(default=..., validation_alias="QUERY", serialization_alias="QUERY", description="Search query for products or specific domains. Use 'dom:domain.com' format to find all products available at a particular website, or enter a product name or description to search across all shops.")
    limit: int | None = Field(default=None, validation_alias="LIMIT", serialization_alias="LIMIT", description="Maximum number of shops to return in the results, ranging from 1 to 500. Defaults to 50 shops per request.", ge=1, le=500)
    page: int | None = Field(default=None, validation_alias="PAGE", serialization_alias="PAGE", description="Zero-indexed page number for pagination through results. Use 0 for the first page, 1 for the second, and so on. Defaults to the first page.", ge=0)
class GetV22Productv1ApiJsonRequest(StrictModel):
    """Search for eCommerce products across the internet and discover which shops are selling them. Results are organized by domain/shop and support pagination for browsing large result sets."""
    query: GetV22Productv1ApiJsonRequestQuery

# Operation: assess_domain_trust
class GetV22Trustv1ApiJsonRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="The domain, subdomain, or specific page URL to evaluate for trustworthiness. Supports both root domains and internal page paths.")
    live: Literal["yes", "no"] | None = Field(default=None, validation_alias="LIVE", serialization_alias="LIVE", description="Enable real-time website verification for more accurate results. Live lookups take longer to complete but are required when the initial assessment indicates the site needs further investigation.")
    words: str | None = Field(default=None, validation_alias="WORDS", serialization_alias="WORDS", description="Optional keywords to cross-reference against website content and metadata, provided as a comma-separated list. Helps identify relevance and potential keyword stuffing or mismatch indicators.")
class GetV22Trustv1ApiJsonRequest(StrictModel):
    """Evaluate the trustworthiness of a website to support fraud detection and risk assessment. Analyzes trust signals including technology investment, domain history, relationships, response patterns, and keyword relevance."""
    query: GetV22Trustv1ApiJsonRequestQuery

# Operation: assess_domain_trust_xml
class GetV22Trustv1ApiXmlRequestQuery(StrictModel):
    lookup: str = Field(default=..., validation_alias="LOOKUP", serialization_alias="LOOKUP", description="The domain, subdomain, or internal page URL to evaluate. Supports subdomains and internal pages when using the live lookup feature.")
    live: Literal["yes", "no"] | None = Field(default=None, validation_alias="LIVE", serialization_alias="LIVE", description="Enable live website lookup for real-time verification. Live lookups take longer to complete but are required when the initial assessment returns a 'needLive' status to determine if the website is genuinely suspect.")
    words: str | None = Field(default=None, validation_alias="WORDS", serialization_alias="WORDS", description="Optional keywords to match against the website content and metadata. Provide as a comma-separated list to help identify relevant trust signals.")
class GetV22Trustv1ApiXmlRequest(StrictModel):
    """Evaluate the trustworthiness of a website for fraud detection purposes. Returns trust status and analysis based on technology spend, time, relationships, response, keywords, and other attributes in XML format."""
    query: GetV22Trustv1ApiXmlRequestQuery

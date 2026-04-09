"""
Google Search Console Api MCP Server - Pydantic Models

Generated: 2026-04-09 17:24:12 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "SearchconsoleUrlInspectionIndexInspectRequest",
    "SearchconsoleUrlTestingToolsMobileFriendlyTestRunRequest",
    "WebmastersSearchanalyticsQueryRequest",
    "WebmastersSitemapsDeleteRequest",
    "WebmastersSitemapsGetRequest",
    "WebmastersSitemapsListRequest",
    "WebmastersSitemapsSubmitRequest",
    "WebmastersSitesAddRequest",
    "WebmastersSitesDeleteRequest",
    "WebmastersSitesGetRequest",
    "ApiDimensionFilterGroup",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: query_search_analytics
class WebmastersSearchanalyticsQueryRequestPath(StrictModel):
    site_url: str = Field(default=..., validation_alias="siteUrl", serialization_alias="siteUrl", description="The site URL to query, including protocol (e.g., http://www.example.com/ or https://example.com). Must match a verified property in Search Console.")
class WebmastersSearchanalyticsQueryRequestBody(StrictModel):
    aggregation_type: Literal["AUTO", "BY_PROPERTY", "BY_PAGE", "BY_NEWS_SHOWCASE_PANEL"] | None = Field(default=None, validation_alias="aggregationType", serialization_alias="aggregationType", description="How to aggregate the returned data: AUTO (default, required if filtering/grouping by page), BY_PROPERTY (aggregate all data for the same property), BY_PAGE (aggregate by canonical URI), or BY_NEWS_SHOWCASE_PANEL. Cannot use BY_PROPERTY if grouping or filtering by page.")
    data_state: Literal["DATA_STATE_UNSPECIFIED", "FINAL", "ALL", "HOURLY_ALL"] | None = Field(default=None, validation_alias="dataState", serialization_alias="dataState", description="Which data state to retrieve: FINAL (complete data only), ALL (complete and partial data), or HOURLY_ALL (includes hourly data). Defaults to FINAL if not specified.")
    dimension_filter_groups: list[ApiDimensionFilterGroup] | None = Field(default=None, validation_alias="dimensionFilterGroups", serialization_alias="dimensionFilterGroups", description="Zero or more filter groups to narrow results by dimension values (e.g., query contains 'buy', country equals 'USA'). Filters are applied without requiring those dimensions to be in the grouping.")
    dimensions: list[Literal["DATE", "QUERY", "PAGE", "COUNTRY", "DEVICE", "SEARCH_APPEARANCE", "HOUR"]] | None = Field(default=None, description="Zero or more dimensions to group results by (e.g., query, page, country, device). Results are grouped in the order specified. At least one dimension is typically needed for meaningful results.")
    end_date: str | None = Field(default=None, validation_alias="endDate", serialization_alias="endDate", description="End date for the query range in YYYY-MM-DD format (PST/UTC-8). Must be greater than or equal to the start date and is included in the range.")
    row_limit: int | None = Field(default=None, validation_alias="rowLimit", serialization_alias="rowLimit", description="Maximum number of rows to return in the response. Must be between 1 and 25,000 inclusive. Defaults to 1,000 if not specified.", json_schema_extra={'format': 'int32'})
    search_type: Literal["WEB", "IMAGE", "VIDEO", "NEWS", "DISCOVER", "GOOGLE_NEWS"] | None = Field(default=None, validation_alias="searchType", serialization_alias="searchType", description="Filter results to a specific search type: WEB (default), IMAGE, VIDEO, NEWS, DISCOVER, or GOOGLE_NEWS.")
    start_date: str | None = Field(default=None, validation_alias="startDate", serialization_alias="startDate", description="Start date for the query range in YYYY-MM-DD format (PST/UTC-8). Must be less than or equal to the end date and is included in the range.")
    start_row: int | None = Field(default=None, validation_alias="startRow", serialization_alias="startRow", description="Zero-based index of the first row to return, used for pagination. Must be a non-negative integer. Defaults to 0 if not specified.", json_schema_extra={'format': 'int32'})
class WebmastersSearchanalyticsQueryRequest(StrictModel):
    """Query Google Search Console analytics data with custom filters and grouping. Returns aggregated performance metrics (clicks, impressions, CTR, position) for your specified dimensions and date range."""
    path: WebmastersSearchanalyticsQueryRequestPath
    body: WebmastersSearchanalyticsQueryRequestBody | None = None

# Operation: get_sitemap
class WebmastersSitemapsGetRequestPath(StrictModel):
    site_url: str = Field(default=..., validation_alias="siteUrl", serialization_alias="siteUrl", description="The website's URL including the protocol (http or https). Must be a valid, fully-qualified URL such as http://www.example.com/.")
    feedpath: str = Field(default=..., description="The complete URL path to the sitemap file. Must be a valid, fully-qualified URL such as http://www.example.com/sitemap.xml.")
class WebmastersSitemapsGetRequest(StrictModel):
    """Retrieves detailed information about a specific sitemap for a website, including its status and metadata."""
    path: WebmastersSitemapsGetRequestPath

# Operation: submit_sitemap
class WebmastersSitemapsSubmitRequestPath(StrictModel):
    site_url: str = Field(default=..., validation_alias="siteUrl", serialization_alias="siteUrl", description="The site's URL including the protocol (http or https). Must be a valid, fully-qualified URL with trailing slash (e.g., http://www.example.com/).")
    feedpath: str = Field(default=..., description="The complete URL path to the sitemap file. Must be a valid, fully-qualified URL pointing to the actual sitemap resource (e.g., http://www.example.com/sitemap.xml).")
class WebmastersSitemapsSubmitRequest(StrictModel):
    """Submits a sitemap to Google Search Console for a specified site. This enables Google to discover and index the URLs listed in your sitemap."""
    path: WebmastersSitemapsSubmitRequestPath

# Operation: delete_sitemap
class WebmastersSitemapsDeleteRequestPath(StrictModel):
    site_url: str = Field(default=..., validation_alias="siteUrl", serialization_alias="siteUrl", description="The site's URL including the protocol (e.g., http://www.example.com/ or https://www.example.com/). This identifies which site the sitemap belongs to.")
    feedpath: str = Field(default=..., description="The complete URL of the sitemap file to delete (e.g., http://www.example.com/sitemap.xml). This must be the exact sitemap URL you want to remove from the report.")
class WebmastersSitemapsDeleteRequest(StrictModel):
    """Removes a sitemap from the Sitemaps report. Note that this action does not prevent Google from crawling the sitemap or previously indexed URLs from that sitemap."""
    path: WebmastersSitemapsDeleteRequestPath

# Operation: list_sitemaps
class WebmastersSitemapsListRequestPath(StrictModel):
    site_url: str = Field(default=..., validation_alias="siteUrl", serialization_alias="siteUrl", description="The website's URL including the protocol (http:// or https://). For example: http://www.example.com/ or https://example.com/. This identifies which site's sitemaps to retrieve.")
class WebmastersSitemapsListRequestQuery(StrictModel):
    sitemap_index: str | None = Field(default=None, validation_alias="sitemapIndex", serialization_alias="sitemapIndex", description="Optional URL pointing to a sitemap index file that aggregates multiple sitemaps. When provided, returns only the sitemaps referenced within that index file rather than all submitted sitemaps.")
class WebmastersSitemapsListRequest(StrictModel):
    """Retrieves all sitemaps submitted for a website or included in a sitemap index file. Use this to view the complete list of sitemaps Google has discovered for your site."""
    path: WebmastersSitemapsListRequestPath
    query: WebmastersSitemapsListRequestQuery | None = None

# Operation: get_site
class WebmastersSitesGetRequestPath(StrictModel):
    site_url: str = Field(default=..., validation_alias="siteUrl", serialization_alias="siteUrl", description="The site URL or domain property identifier as it appears in Search Console. Use the full URL format (e.g., http://www.example.com/) for URL-prefix properties or the domain format (e.g., sc-domain:example.com) for domain properties.")
class WebmastersSitesGetRequest(StrictModel):
    """Retrieves detailed information about a specific site property registered in Google Search Console, including its configuration and metadata."""
    path: WebmastersSitesGetRequestPath

# Operation: add_site
class WebmastersSitesAddRequestPath(StrictModel):
    site_url: str = Field(default=..., validation_alias="siteUrl", serialization_alias="siteUrl", description="The complete URL of the website to add to Search Console (e.g., domain, subdomain, or URL prefix).")
class WebmastersSitesAddRequest(StrictModel):
    """Adds a website to your Search Console account, enabling you to monitor and manage its search performance."""
    path: WebmastersSitesAddRequestPath

# Operation: delete_site
class WebmastersSitesDeleteRequestPath(StrictModel):
    site_url: str = Field(default=..., validation_alias="siteUrl", serialization_alias="siteUrl", description="The site URL or domain property identifier as it appears in Search Console. Use the full URL format (e.g., http://www.example.com/) for URL-prefix properties or the domain format (e.g., sc-domain:example.com) for domain properties.")
class WebmastersSitesDeleteRequest(StrictModel):
    """Removes a website property from your Search Console account, preventing further monitoring and analysis of that site."""
    path: WebmastersSitesDeleteRequestPath

# Operation: inspect_url_index_status
class SearchconsoleUrlInspectionIndexInspectRequestBody(StrictModel):
    inspection_url: str | None = Field(default=None, validation_alias="inspectionUrl", serialization_alias="inspectionUrl", description="The URL to inspect for indexing status. Must be a valid URL that belongs to the property specified in siteUrl.")
    language_code: str | None = Field(default=None, validation_alias="languageCode", serialization_alias="languageCode", description="The language for translated issue messages in IETF BCP-47 format (e.g., en-US, de-CH). Defaults to English (US) if not specified.")
    site_url: str | None = Field(default=None, validation_alias="siteUrl", serialization_alias="siteUrl", description="The Search Console property URL in either URL-prefix format (e.g., http://www.example.com/) or domain property format (e.g., sc-domain:example.com). The inspectionUrl must belong to this property.")
class SearchconsoleUrlInspectionIndexInspectRequest(StrictModel):
    """Inspect the indexing status of a specific URL within a Search Console property. Returns detailed information about whether the URL is indexed and any associated issues."""
    body: SearchconsoleUrlInspectionIndexInspectRequestBody | None = None

# Operation: test_mobile_friendly
class SearchconsoleUrlTestingToolsMobileFriendlyTestRunRequestBody(StrictModel):
    request_screenshot: bool | None = Field(default=None, validation_alias="requestScreenshot", serialization_alias="requestScreenshot", description="Whether to include a screenshot of the URL as rendered on a mobile device in the test results.")
    url: str | None = Field(default=None, description="The complete URL to test for mobile-friendliness, including the protocol (http or https).")
class SearchconsoleUrlTestingToolsMobileFriendlyTestRunRequest(StrictModel):
    """Tests whether a given URL is mobile-friendly by analyzing its mobile rendering and usability. Optionally returns a screenshot of the mobile view."""
    body: SearchconsoleUrlTestingToolsMobileFriendlyTestRunRequestBody | None = None

# ============================================================================
# Component Models
# ============================================================================

class ApiDimensionFilter(PermissiveModel):
    """A filter test to be applied to each row in the data set, where a match can return the row. Filters are string comparisons, and values and dimension names are not case-sensitive. Individual filters are either AND'ed or OR'ed within their parent filter group, according to the group's group type. You do not need to group by a specified dimension to filter against it."""
    dimension: Literal["QUERY", "PAGE", "COUNTRY", "DEVICE", "SEARCH_APPEARANCE"] | None = None
    expression: str | None = None
    operator: Literal["EQUALS", "NOT_EQUALS", "CONTAINS", "NOT_CONTAINS", "INCLUDING_REGEX", "EXCLUDING_REGEX"] | None = None

class ApiDimensionFilterGroup(PermissiveModel):
    """A set of dimension value filters to test against each row. Only rows that pass all filter groups will be returned. All results within a filter group are either AND'ed or OR'ed together, depending on the group type selected. All filter groups are AND'ed together."""
    filters: list[ApiDimensionFilter] | None = None
    group_type: Literal["AND"] | None = Field(None, validation_alias="groupType", serialization_alias="groupType")


# Rebuild models to resolve forward references (required for circular refs)
ApiDimensionFilter.model_rebuild()
ApiDimensionFilterGroup.model_rebuild()

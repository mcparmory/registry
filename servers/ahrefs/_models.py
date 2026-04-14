"""
Ahrefs Api MCP Server - Pydantic Models

Generated: 2026-04-14 18:13:08 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "GetV3BrandRadarAiResponsesRequest",
    "GetV3BrandRadarCitedDomainsRequest",
    "GetV3BrandRadarCitedPagesRequest",
    "GetV3BrandRadarImpressionsHistoryRequest",
    "GetV3BrandRadarImpressionsOverviewRequest",
    "GetV3BrandRadarMentionsHistoryRequest",
    "GetV3BrandRadarMentionsOverviewRequest",
    "GetV3BrandRadarSovHistoryRequest",
    "GetV3BrandRadarSovOverviewRequest",
    "GetV3GscAnonymousQueriesRequest",
    "GetV3GscCtrByPositionRequest",
    "GetV3GscKeywordHistoryRequest",
    "GetV3GscKeywordsRequest",
    "GetV3GscMetricsByCountryRequest",
    "GetV3GscPageHistoryRequest",
    "GetV3GscPagesHistoryRequest",
    "GetV3GscPagesRequest",
    "GetV3GscPerformanceByDeviceRequest",
    "GetV3GscPerformanceByPositionRequest",
    "GetV3GscPerformanceHistoryRequest",
    "GetV3GscPositionsHistoryRequest",
    "GetV3KeywordsExplorerMatchingTermsRequest",
    "GetV3KeywordsExplorerOverviewRequest",
    "GetV3KeywordsExplorerRelatedTermsRequest",
    "GetV3KeywordsExplorerSearchSuggestionsRequest",
    "GetV3KeywordsExplorerVolumeByCountryRequest",
    "GetV3KeywordsExplorerVolumeHistoryRequest",
    "GetV3ManagementBrandRadarPromptsRequest",
    "GetV3ManagementKeywordListKeywordsRequest",
    "GetV3ManagementLocationsRequest",
    "GetV3ManagementProjectCompetitorsRequest",
    "GetV3ManagementProjectKeywordsRequest",
    "GetV3ManagementProjectsRequest",
    "GetV3RankTrackerCompetitorsOverviewRequest",
    "GetV3RankTrackerCompetitorsPagesRequest",
    "GetV3RankTrackerCompetitorsStatsRequest",
    "GetV3RankTrackerOverviewRequest",
    "GetV3RankTrackerSerpOverviewRequest",
    "GetV3SerpOverviewRequest",
    "GetV3SiteAuditIssuesRequest",
    "GetV3SiteAuditPageContentRequest",
    "GetV3SiteAuditPageExplorerRequest",
    "GetV3SiteAuditProjectsRequest",
    "GetV3SiteExplorerAllBacklinksRequest",
    "GetV3SiteExplorerAnchorsRequest",
    "GetV3SiteExplorerBacklinksStatsRequest",
    "GetV3SiteExplorerBrokenBacklinksRequest",
    "GetV3SiteExplorerDomainRatingHistoryRequest",
    "GetV3SiteExplorerDomainRatingRequest",
    "GetV3SiteExplorerKeywordsHistoryRequest",
    "GetV3SiteExplorerLinkedAnchorsExternalRequest",
    "GetV3SiteExplorerLinkedAnchorsInternalRequest",
    "GetV3SiteExplorerLinkeddomainsRequest",
    "GetV3SiteExplorerMetricsByCountryRequest",
    "GetV3SiteExplorerMetricsHistoryRequest",
    "GetV3SiteExplorerMetricsRequest",
    "GetV3SiteExplorerOrganicCompetitorsRequest",
    "GetV3SiteExplorerOrganicKeywordsRequest",
    "GetV3SiteExplorerOutlinksStatsRequest",
    "GetV3SiteExplorerPagesByBacklinksRequest",
    "GetV3SiteExplorerPagesByInternalLinksRequest",
    "GetV3SiteExplorerPagesByTrafficRequest",
    "GetV3SiteExplorerPagesHistoryRequest",
    "GetV3SiteExplorerPaidPagesRequest",
    "GetV3SiteExplorerRefdomainsHistoryRequest",
    "GetV3SiteExplorerRefdomainsRequest",
    "GetV3SiteExplorerTopPagesRequest",
    "GetV3SiteExplorerTotalSearchVolumeHistoryRequest",
    "GetV3SiteExplorerUrlRatingHistoryRequest",
    "GetV3WebAnalyticsBrowsersChartRequest",
    "GetV3WebAnalyticsBrowsersRequest",
    "GetV3WebAnalyticsBrowserVersionsChartRequest",
    "GetV3WebAnalyticsBrowserVersionsRequest",
    "GetV3WebAnalyticsChartRequest",
    "GetV3WebAnalyticsCitiesChartRequest",
    "GetV3WebAnalyticsCitiesRequest",
    "GetV3WebAnalyticsContinentsChartRequest",
    "GetV3WebAnalyticsContinentsRequest",
    "GetV3WebAnalyticsCountriesChartRequest",
    "GetV3WebAnalyticsCountriesRequest",
    "GetV3WebAnalyticsDevicesChartRequest",
    "GetV3WebAnalyticsDevicesRequest",
    "GetV3WebAnalyticsEntryPagesChartRequest",
    "GetV3WebAnalyticsEntryPagesRequest",
    "GetV3WebAnalyticsExitPagesChartRequest",
    "GetV3WebAnalyticsExitPagesRequest",
    "GetV3WebAnalyticsLanguagesChartRequest",
    "GetV3WebAnalyticsLanguagesRequest",
    "GetV3WebAnalyticsOperatingSystemsChartRequest",
    "GetV3WebAnalyticsOperatingSystemsRequest",
    "GetV3WebAnalyticsOperatingSystemsVersionsChartRequest",
    "GetV3WebAnalyticsOperatingSystemsVersionsRequest",
    "GetV3WebAnalyticsReferrersChartRequest",
    "GetV3WebAnalyticsReferrersRequest",
    "GetV3WebAnalyticsSourceChannelsChartRequest",
    "GetV3WebAnalyticsSourceChannelsRequest",
    "GetV3WebAnalyticsSourcesChartRequest",
    "GetV3WebAnalyticsSourcesRequest",
    "GetV3WebAnalyticsStatsRequest",
    "GetV3WebAnalyticsTopPagesChartRequest",
    "GetV3WebAnalyticsTopPagesRequest",
    "GetV3WebAnalyticsUtmParamsChartRequest",
    "GetV3WebAnalyticsUtmParamsRequest",
    "PatchV3ManagementBrandRadarReportsRequest",
    "PatchV3ManagementUpdateProjectRequest",
    "PostV3BatchAnalysisRequest",
    "PostV3ManagementBrandRadarPromptsRequest",
    "PostV3ManagementBrandRadarReportsRequest",
    "PostV3ManagementProjectCompetitorsDeleteRequest",
    "PostV3ManagementProjectCompetitorsRequest",
    "PostV3ManagementProjectsRequest",
    "PutV3ManagementBrandRadarPromptsDeleteRequest",
    "PutV3ManagementKeywordListKeywordsDeleteRequest",
    "PutV3ManagementKeywordListKeywordsRequest",
    "PutV3ManagementProjectKeywordsDeleteRequest",
    "PutV3ManagementProjectKeywordsRequest",
    "PatchV3ManagementBrandRadarReportsBodyPromptsFrequencyItem",
    "PostV3BatchAnalysisBodyTargetsItem",
    "PostV3ManagementProjectCompetitorsBodyCompetitorsItem",
    "PostV3ManagementProjectCompetitorsDeleteBodyCompetitorsItem",
    "PutV3ManagementProjectKeywordsBodyKeywordsItem",
    "PutV3ManagementProjectKeywordsBodyLocationsItem",
    "PutV3ManagementProjectKeywordsDeleteBodyKeywordsItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_domain_rating
class GetV3SiteExplorerDomainRatingRequestQuery(StrictModel):
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="The protocol scheme to include in the analysis. Choose 'http' for HTTP only, 'https' for HTTPS only, or 'both' to analyze both protocols together. Defaults to 'both' if not specified.")
    target: str = Field(default=..., description="The domain or URL to analyze. This is the primary target for which you want to retrieve the domain rating.")
    date: str = Field(default=..., description="The date for which to retrieve metrics, specified in YYYY-MM-DD format (e.g., 2024-01-15).", json_schema_extra={'format': 'date'})
class GetV3SiteExplorerDomainRatingRequest(StrictModel):
    """Retrieve the domain rating for a target domain or URL on a specific date. Domain rating is a metric that indicates the authority and trustworthiness of a domain."""
    query: GetV3SiteExplorerDomainRatingRequestQuery

# Operation: get_backlinks_stats
class GetV3SiteExplorerBacklinksStatsRequestQuery(StrictModel):
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="The protocol to include in the search results: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both protocols if not specified.")
    target: str = Field(default=..., description="The domain or URL to analyze for backlink statistics. This is the target you want to get data for.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The scope of the search relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains if not specified.")
    date: str = Field(default=..., description="The date for which to retrieve backlink metrics, specified in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
class GetV3SiteExplorerBacklinksStatsRequest(StrictModel):
    """Retrieve backlink statistics for a target domain or URL on a specific date. Returns metrics about incoming links based on your specified scope and protocol."""
    query: GetV3SiteExplorerBacklinksStatsRequestQuery

# Operation: list_outlinks_stats
class GetV3SiteExplorerOutlinksStatsRequestQuery(StrictModel):
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="The protocol to filter by: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both protocols if not specified.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The scope of the search relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to all subdomains if not specified.")
    target: str = Field(default=..., description="The domain or URL to analyze for outlink statistics.")
class GetV3SiteExplorerOutlinksStatsRequest(StrictModel):
    """Retrieve outlink statistics for a target domain or URL. This beta endpoint provides insights into outbound links, though data may not perfectly match the Ahrefs UI and accuracy improvements are ongoing."""
    query: GetV3SiteExplorerOutlinksStatsRequestQuery

# Operation: get_domain_metrics
class GetV3SiteExplorerMetricsRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze. Can be a full domain (example.com) or a specific URL path.")
    date: str = Field(default=..., description="The date for which to retrieve metrics, specified in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="Determines how search volume is calculated: use 'monthly' for monthly averages or 'average' for overall average. This affects volume, traffic, and traffic value calculations. Defaults to 'monthly'.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="The protocol scheme to include in the analysis: 'http', 'https', or 'both' to include both protocols. Defaults to 'both'.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The scope of analysis relative to your target: 'exact' for the exact URL, 'prefix' for URL prefix matching, 'domain' for the entire domain, or 'subdomains' to include all subdomains. Defaults to 'subdomains'.")
class GetV3SiteExplorerMetricsRequest(StrictModel):
    """Retrieve comprehensive SEO metrics for a domain or URL, including keyword rankings, traffic estimates, and search volume data for a specified date."""
    query: GetV3SiteExplorerMetricsRequestQuery

# Operation: get_refdomains_history
class GetV3SiteExplorerRefdomainsHistoryRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze for referring domain history.")
    date_from: str = Field(default=..., description="The start date for the historical analysis period, specified in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="The end date for the historical analysis period, specified in YYYY-MM-DD format. If omitted, defaults to the current date.", json_schema_extra={'format': 'date'})
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="The time interval for grouping historical data points. Choose from daily, weekly, or monthly aggregation; defaults to monthly.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="The protocol scope to include in the analysis: both HTTP and HTTPS, HTTP only, or HTTPS only; defaults to both.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The search scope relative to your target: exact domain match, prefix match, entire domain, or all subdomains; defaults to subdomains.")
class GetV3SiteExplorerRefdomainsHistoryRequest(StrictModel):
    """Retrieve historical data on referring domains for a target domain or URL over a specified time period, with flexible grouping and protocol filtering options."""
    query: GetV3SiteExplorerRefdomainsHistoryRequestQuery

# Operation: get_domain_rating_history
class GetV3SiteExplorerDomainRatingHistoryRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze. Can be a full domain (e.g., example.com) or a specific URL path.")
    date_from: str = Field(default=..., description="The start date for the historical data range in YYYY-MM-DD format (e.g., 2024-01-01).", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="The end date for the historical data range in YYYY-MM-DD format (e.g., 2024-12-31). If not provided, defaults to today's date.", json_schema_extra={'format': 'date'})
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="How to group the historical data by time interval: daily, weekly, or monthly. Defaults to monthly grouping if not specified.")
class GetV3SiteExplorerDomainRatingHistoryRequest(StrictModel):
    """Retrieve historical Domain Rating data for a domain or URL over a specified time period, grouped by your chosen time interval."""
    query: GetV3SiteExplorerDomainRatingHistoryRequestQuery

# Operation: get_url_rating_history
class GetV3SiteExplorerUrlRatingHistoryRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze. Can be a full domain (e.g., example.com) or a specific URL path.")
    date_from: str = Field(default=..., description="The start date for the historical data retrieval in YYYY-MM-DD format (e.g., 2024-01-01).", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="The end date for the historical data retrieval in YYYY-MM-DD format (e.g., 2024-12-31). If omitted, defaults to the current date.", json_schema_extra={'format': 'date'})
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="The time interval for grouping historical data points. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified.")
class GetV3SiteExplorerUrlRatingHistoryRequest(StrictModel):
    """Retrieve the historical URL Rating progression for a target domain or URL over a specified date range, with flexible time-based grouping options."""
    query: GetV3SiteExplorerUrlRatingHistoryRequestQuery

# Operation: list_page_history
class GetV3SiteExplorerPagesHistoryRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze. This is the primary search target for retrieving page history data.")
    date_from: str = Field(default=..., description="The start date for the historical period in YYYY-MM-DD format (e.g., 2024-01-15). This marks the beginning of the data range to retrieve.", json_schema_extra={'format': 'date'})
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The scope of the search relative to your target: 'exact' matches the target precisely, 'prefix' matches URLs starting with the target, 'domain' searches the entire domain, or 'subdomains' includes all subdomains. Defaults to 'subdomains'.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="The protocol to include in results: 'http', 'https', or 'both' for both protocols. Defaults to 'both'.")
    date_to: str | None = Field(default=None, description="The end date for the historical period in YYYY-MM-DD format (e.g., 2024-12-31). If omitted, defaults to the current date.", json_schema_extra={'format': 'date'})
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="The time interval for grouping historical data: 'daily' for day-by-day data, 'weekly' for week-by-week aggregation, or 'monthly' for month-by-month aggregation. Defaults to 'monthly'.")
    page_positions: Literal["top10", "top100"] | None = Field(default=None, description="Filter results by ranking position: 'top10' returns only pages ranking in the top 10 positions, or 'top100' returns all pages ranking in the top 100. Defaults to 'top100'.")
class GetV3SiteExplorerPagesHistoryRequest(StrictModel):
    """Retrieve historical ranking data for pages from a target domain or URL over a specified time period. Results can be grouped by daily, weekly, or monthly intervals and filtered by search scope and ranking position."""
    query: GetV3SiteExplorerPagesHistoryRequestQuery

# Operation: get_domain_metrics_history
class GetV3SiteExplorerMetricsHistoryRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze. Can be a full domain, subdomain, or specific URL path depending on the mode parameter.")
    date_from: str = Field(default=..., description="The start date for the historical data range in YYYY-MM-DD format (e.g., 2024-01-01).", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="The end date for the historical data range in YYYY-MM-DD format (e.g., 2024-12-31). If omitted, defaults to the current date.", json_schema_extra={'format': 'date'})
    select: str | None = Field(default=None, description="Comma-separated list of specific metrics to include in the response (e.g., date, org_cost, org_traffic). If not specified, returns date, org_cost, org_traffic, paid_cost, and paid_traffic by default.")
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="Determines how search volume is calculated: monthly totals or average values. Affects volume, traffic, and traffic value metrics. Defaults to monthly.")
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="The time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly for broader trends.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Filter results by protocol: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The scope of analysis relative to the target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains.")
class GetV3SiteExplorerMetricsHistoryRequest(StrictModel):
    """Retrieve historical performance metrics for a domain or URL over a specified date range, with options to customize time intervals, volume calculations, and protocol scope."""
    query: GetV3SiteExplorerMetricsHistoryRequestQuery

# Operation: list_keyword_history
class GetV3SiteExplorerKeywordsHistoryRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze for keyword history.")
    date_from: str = Field(default=..., description="The start date for the historical period in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="The end date for the historical period in YYYY-MM-DD format. If omitted, defaults to the current date.", json_schema_extra={'format': 'date'})
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The search scope relative to your target: exact URL match, URL prefix, entire domain, or all subdomains. Defaults to subdomains.")
    select: str | None = Field(default=None, description="A comma-separated list of data columns to include in the response. Defaults to date, top 3 keywords, top 4-10 keywords, and top 11+ keywords.")
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="The time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Filter results by protocol: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both.")
class GetV3SiteExplorerKeywordsHistoryRequest(StrictModel):
    """Retrieve the historical ranking data for keywords associated with a target domain or URL across a specified date range, with options to group results by time interval and filter by protocol."""
    query: GetV3SiteExplorerKeywordsHistoryRequestQuery

# Operation: list_country_metrics
class GetV3SiteExplorerMetricsByCountryRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze. Can be a full domain (example.com) or a specific URL path depending on the mode parameter.")
    date: str = Field(default=..., description="The date for which to retrieve metrics, specified in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    select: str | None = Field(default=None, description="A comma-separated list of specific metrics to include in the response. If not specified, defaults to paid_cost, paid_keywords, org_cost, paid_pages, org_keywords_1_3, org_keywords, org_traffic, paid_traffic, and country.")
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="Determines how search volume is calculated: either as a monthly total or as an average. This affects volume, traffic, and traffic value metrics. Defaults to monthly.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="The protocol to include in the analysis: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The scope of analysis based on your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains.")
class GetV3SiteExplorerMetricsByCountryRequest(StrictModel):
    """Retrieve performance metrics broken down by country for a target domain or URL on a specific date. Useful for analyzing geographic traffic distribution and keyword performance across regions."""
    query: GetV3SiteExplorerMetricsByCountryRequestQuery

# Operation: list_pages_by_traffic
class GetV3SiteExplorerPagesByTrafficRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze for traffic data.")
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="Calculate search volume based on monthly totals or average values. Defaults to monthly calculation, which also affects traffic and traffic value metrics.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Filter results by protocol type: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both protocols.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Define the search scope relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains.")
class GetV3SiteExplorerPagesByTrafficRequest(StrictModel):
    """Retrieve pages grouped by traffic volume ranges for a domain or URL. Useful for identifying high-traffic pages and traffic distribution patterns across your site."""
    query: GetV3SiteExplorerPagesByTrafficRequestQuery

# Operation: get_search_volume_history
class GetV3SiteExplorerTotalSearchVolumeHistoryRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze. Can be a full domain, subdomain, or specific URL path depending on the mode selected.")
    date_from: str = Field(default=..., description="The start date for the historical data range in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="The end date for the historical data range in YYYY-MM-DD format. If not provided, defaults to the current date.", json_schema_extra={'format': 'date'})
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The scope of analysis relative to your target: exact URL match, URL prefix, entire domain, or all subdomains. Defaults to analyzing all subdomains.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Whether to include both HTTP and HTTPS protocols, or filter to a specific protocol. Defaults to both.")
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="How search volume is calculated: monthly totals or average per month. This affects reported volume, traffic, and traffic value metrics. Defaults to monthly totals.")
    top_positions: Literal["top_10", "top_100"] | None = Field(default=None, description="The number of top organic search positions to include in volume calculations: top 10 or top 100 results. Defaults to top 10.")
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="The time interval for grouping historical data: daily, weekly, or monthly snapshots. Defaults to monthly grouping.")
class GetV3SiteExplorerTotalSearchVolumeHistoryRequest(StrictModel):
    """Retrieve historical search volume data for a domain or URL over a specified time period. Use this to analyze organic search trends and traffic patterns."""
    query: GetV3SiteExplorerTotalSearchVolumeHistoryRequestQuery

# Operation: list_backlinks
class GetV3SiteExplorerAllBacklinksRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze for backlinks.")
    select: str = Field(default=..., description="Comma-separated list of data columns to include in the response. Refer to the response schema for valid column identifiers.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Search scope relative to the target: exact URL match, URL prefix, entire domain, or all subdomains. Defaults to subdomains.")
    aggregation: Literal["similar_links", "1_per_domain", "all"] | None = Field(default=None, description="How to group backlinks in results: similar links (deduplicated), one per domain, or all individual links. Defaults to similar links.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Filter results by protocol: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both.")
    history: str | None = Field(default=None, description="Time frame for backlink data: live (current only), since a specific date in YYYY-MM-DD format, or all historical data. Defaults to all time.")
    order_by: str | None = Field(default=None, description="Column identifier to sort results by. Refer to the response schema for valid options; link_group_count is not supported for sorting.")
    where: str | None = Field(default=None, description="Filter expression to narrow results based on column values. Refer to the response schema for recognized column identifiers.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 1000.")
class GetV3SiteExplorerAllBacklinksRequest(StrictModel):
    """Retrieve all backlinks pointing to a target domain or URL, including detailed backlink profile metrics and historical data. Results can be aggregated, filtered, and sorted to analyze link quality and sources."""
    query: GetV3SiteExplorerAllBacklinksRequestQuery

# Operation: list_broken_backlinks
class GetV3SiteExplorerBrokenBacklinksRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 1000 results.")
    order_by: str | None = Field(default=None, description="Column name to sort results by. Refer to the response schema for valid column identifiers; note that http_code_target, last_visited_target, and link_group_count cannot be used for sorting.")
    where: str | None = Field(default=None, description="Filter expression to narrow results. Use column identifiers from the response schema to construct conditions (column identifiers differ from those used in the select parameter).")
    select: str = Field(default=..., description="Comma-separated list of column names to include in the response. See the response schema for all available column identifiers.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Protocol to search within: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to searching both protocols.")
    target: str = Field(default=..., description="The target of your search: either a domain name or a specific URL.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Scope of the search relative to your target. Use 'exact' for the precise URL, 'prefix' for URLs starting with the target, 'domain' for the exact domain, or 'subdomains' to include all subdomains. Defaults to subdomains.")
    aggregation: Literal["similar_links", "1_per_domain", "all"] | None = Field(default=None, description="Grouping strategy for backlinks: 'similar_links' groups by similarity, '1_per_domain' returns one backlink per referring domain, or 'all' returns every backlink. Defaults to similar_links.")
class GetV3SiteExplorerBrokenBacklinksRequest(StrictModel):
    """Retrieve broken backlinks pointing to a target domain or URL. Returns backlinks that result in HTTP errors, with options to filter, sort, and aggregate results by domain or similarity."""
    query: GetV3SiteExplorerBrokenBacklinksRequestQuery

# Operation: list_refdomains
class GetV3SiteExplorerRefdomainsRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze for referring domains.")
    select: str = Field(default=..., description="Comma-separated list of data columns to include in the response. Refer to the response schema for valid column identifiers.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Search scope relative to the target: exact URL match, URL prefix, entire domain, or all subdomains. Defaults to subdomains.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Filter results by protocol type: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 1000.")
    order_by: str | None = Field(default=None, description="Column identifier to sort results by. Refer to the response schema for valid column identifiers.")
    where: str | None = Field(default=None, description="Filter expression to narrow results based on column values. Refer to the response schema for recognized column identifiers.")
    history: str | None = Field(default=None, description="Time frame for historical backlink data: 'live' for current data only, 'since:<date>' for data since a specific date in YYYY-MM-DD format, or 'all_time' for complete history. Defaults to all_time.")
class GetV3SiteExplorerRefdomainsRequest(StrictModel):
    """Retrieve referring domains data for a target domain or URL, with filtering and sorting capabilities to analyze backlink sources."""
    query: GetV3SiteExplorerRefdomainsRequestQuery

# Operation: list_anchor_text
class GetV3SiteExplorerAnchorsRequestQuery(StrictModel):
    target: str = Field(default=..., description="The target domain or URL to analyze for incoming anchor text. Can be a full domain or specific URL path.")
    select: str = Field(default=..., description="Comma-separated list of data columns to include in the response. Refer to the response schema for valid column identifiers.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Search scope relative to your target: 'exact' for the precise URL, 'prefix' for URLs starting with your target, 'domain' for the entire domain, or 'subdomains' to include all subdomains. Defaults to subdomains.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Filter results by protocol type: 'http', 'https', or 'both' to include all protocols. Defaults to both.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in a single response. Defaults to 1000.")
    order_by: str | None = Field(default=None, description="Column identifier to sort results by. Refer to the response schema for valid column identifiers.")
    where: str | None = Field(default=None, description="Filter expression to narrow results based on specific column values. Supports the column identifiers documented in the response schema.")
    history: str | None = Field(default=None, description="Time frame for historical data: 'live' for current data only, 'since:YYYY-MM-DD' to include data from a specific date forward, or 'all_time' for complete historical records. Defaults to all_time.")
class GetV3SiteExplorerAnchorsRequest(StrictModel):
    """Retrieve anchor text (clickable words in hyperlinks) that point to a target domain or URL. Use this to analyze inbound link text and understand how external sites reference your target."""
    query: GetV3SiteExplorerAnchorsRequestQuery

# Operation: list_organic_keywords
class GetV3SiteExplorerOrganicKeywordsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response; defaults to 1000 if not specified.")
    order_by: str | None = Field(default=None, description="Column name to sort results by; refer to the response schema for valid column identifiers.")
    where: str | None = Field(default=None, description="Filter expression to narrow results; use column identifiers recognized by the API (note: these differ from select parameter identifiers).")
    select: str = Field(default=..., description="Comma-separated list of column names to include in the response; refer to the response schema for valid identifiers.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Protocol scheme to target: both HTTP and HTTPS, HTTP only, or HTTPS only; defaults to both.")
    target: str = Field(default=..., description="The domain or URL to analyze for organic keywords.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Search scope relative to the target: exact URL match, URL prefix match, entire domain, or domain with subdomains; defaults to subdomains.")
    date: str = Field(default=..., description="Date for which to report metrics, formatted as YYYY-MM-DD.", json_schema_extra={'format': 'date'})
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="Method for calculating search volume: monthly totals or average across the period; defaults to monthly.")
class GetV3SiteExplorerOrganicKeywordsRequest(StrictModel):
    """Retrieve organic keywords that drive traffic to a target domain or URL, with metrics for a specified date. Results can be filtered, sorted, and customized to show specific data columns."""
    query: GetV3SiteExplorerOrganicKeywordsRequestQuery

# Operation: list_organic_competitors
class GetV3SiteExplorerOrganicCompetitorsRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze for competitors. Can be a full domain (example.com) or specific URL path.")
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(default=..., description="Two-letter country code (ISO 3166-1 alpha-2 format) specifying the geographic market for competitor analysis.")
    date: str = Field(default=..., description="Report date in YYYY-MM-DD format. Metrics will be calculated for this specific date.", json_schema_extra={'format': 'date'})
    select: str = Field(default=..., description="Comma-separated list of data columns to include in results. Valid identifiers correspond to the response schema fields.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Search scope relative to the target: exact URL match, URL prefix, entire domain, or all subdomains. Defaults to subdomains.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="HTTP protocol filter: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both.")
    limit: int | None = Field(default=None, description="Maximum number of competitor results to return. Defaults to 1000.")
    offset: int | None = Field(default=None, description="Number of results to skip for pagination. Use with limit to retrieve subsequent result pages.")
    order_by: str | None = Field(default=None, description="Column identifier to sort results by. Must correspond to a valid response schema field.")
    where: str | None = Field(default=None, description="Filter expression to narrow results. Supports column identifiers from the response schema (different set than select parameter).")
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="Search volume calculation method: monthly totals or average across the period. Affects volume, traffic, and traffic value metrics. Defaults to monthly.")
class GetV3SiteExplorerOrganicCompetitorsRequest(StrictModel):
    """Identify organic search competitors for a target domain or URL by analyzing shared keyword rankings in a specific country and date."""
    query: GetV3SiteExplorerOrganicCompetitorsRequestQuery

# Operation: list_top_pages
class GetV3SiteExplorerTopPagesRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze. Can be a full domain, subdomain, or specific URL path depending on the mode selected.")
    date: str = Field(default=..., description="The date for which to retrieve metrics, specified in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    select: str = Field(default=..., description="A comma-separated list of metric columns to include in the response. Refer to the response schema for valid column identifiers.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The scope of analysis relative to your target. Use 'exact' for the precise URL, 'prefix' for URL path matching, 'domain' for the entire domain, or 'subdomains' to include all subdomains. Defaults to subdomains.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Filter results by protocol type: 'http', 'https', or 'both' to include all protocols. Defaults to both.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 1000.")
    order_by: str | None = Field(default=None, description="Column identifier to sort results by. Refer to the response schema for valid column identifiers.")
    where: str | None = Field(default=None, description="Filter expression to narrow results based on column values. Refer to the response schema for recognized column identifiers and filtering syntax.")
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="Calculation method for search volume metrics: 'monthly' for current month data or 'average' for historical average. Affects volume, traffic, and traffic value calculations. Defaults to monthly.")
class GetV3SiteExplorerTopPagesRequest(StrictModel):
    """Retrieve the top-performing pages for a domain or URL, including organic search metrics such as traffic and rankings for a specified date."""
    query: GetV3SiteExplorerTopPagesRequestQuery

# Operation: list_paid_pages
class GetV3SiteExplorerPaidPagesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response, up to 1000 by default.")
    order_by: str | None = Field(default=None, description="Column name to sort results by. Refer to the response schema for valid column identifiers.")
    where: str | None = Field(default=None, description="Filter expression to narrow results. Use column identifiers from the response schema to construct conditions.")
    select: str = Field(default=..., description="Comma-separated list of column names to include in the response. Refer to the response schema for valid column identifiers.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Protocol to search within: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both.")
    target: str = Field(default=..., description="The domain or URL to analyze for paid pages.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Search scope relative to the target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to all subdomains.")
    date: str = Field(default=..., description="The date for which to report metrics, specified in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="Calculation method for search volume metrics: monthly totals or average over time. Defaults to monthly and affects volume, traffic, and traffic value columns.")
class GetV3SiteExplorerPaidPagesRequest(StrictModel):
    """Retrieve paid search pages for a target domain or URL, showing which pages are generating paid search traffic on a specified date."""
    query: GetV3SiteExplorerPaidPagesRequestQuery

# Operation: list_pages_by_backlinks
class GetV3SiteExplorerPagesByBacklinksRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 1000 results if not specified.")
    order_by: str | None = Field(default=None, description="Column name to sort results by in ascending or descending order. Refer to the response schema for valid column names; note that certain columns like http_code_target, languages_target, last_visited_target, powered_by_target, target_redirect, title_target, url_rating_target, and url_rating_target are not sortable.")
    select: str = Field(default=..., description="Comma-separated list of column names to include in the response. Consult the response schema to see all available columns you can request.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Protocol scheme to filter results by: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both if not specified.")
    target: str = Field(default=..., description="The domain or URL to analyze. This is the target for which you want to find pages ranked by backlinks.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Search scope relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to all subdomains if not specified.")
    history: str | None = Field(default=None, description="Time frame for including historical backlink data: live data only, backlinks since a specific date (format: YYYY-MM-DD), or complete historical data. Defaults to all_time if not specified.")
    where: str | None = Field(default=None, description="The filter expression. The following column identifiers are recognized (this differs from the identifiers recognized by the select parameter).")
class GetV3SiteExplorerPagesByBacklinksRequest(StrictModel):
    """Retrieve the best performing pages for a target domain or URL ranked by backlink count. Use this to identify which pages attract the most external links and understand your site's link profile."""
    query: GetV3SiteExplorerPagesByBacklinksRequestQuery

# Operation: list_pages_by_internal_links
class GetV3SiteExplorerPagesByInternalLinksRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze. Can be a full domain (example.com) or a specific URL path depending on the mode parameter.")
    select: str = Field(default=..., description="Comma-separated list of data columns to include in the response. Refer to the response schema for valid column identifiers.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Defines the search scope relative to your target. Use 'exact' for the precise URL, 'prefix' for URL path matching, 'domain' for the root domain only, or 'subdomains' to include all subdomains. Defaults to subdomains.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Filter results by protocol type. Choose 'http', 'https', or 'both' to include all protocols. Defaults to both.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 1000.")
    order_by: str | None = Field(default=None, description="Column identifier to sort results by. See the response schema for valid options. Note that certain columns like http_code_target, languages_target, last_visited_target, powered_by_target, target_redirect, title_target, url_rating_target, and target_redirect are not supported for sorting.")
    where: str | None = Field(default=None, description="Filter expression to narrow results. Accepts column identifiers recognized by the API's filter syntax (note: these may differ from the select parameter's column identifiers).")
class GetV3SiteExplorerPagesByInternalLinksRequest(StrictModel):
    """Retrieve the best-performing pages for a target domain or URL ranked by the number of internal links pointing to them. Use this to identify which pages are most linked internally and understand your site's link structure."""
    query: GetV3SiteExplorerPagesByInternalLinksRequestQuery

# Operation: list_linked_domains
class GetV3SiteExplorerLinkeddomainsRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze for incoming links. This is the target whose linked domains you want to discover.")
    select: str = Field(default=..., description="Comma-separated list of data columns to include in results. Refer to the response schema for valid column identifiers.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Defines the search scope relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Filter results by protocol type: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 1000.")
    order_by: str | None = Field(default=None, description="Column identifier to sort results by. Refer to the response schema for valid column identifiers.")
    where: str | None = Field(default=None, description="Filter expression to narrow results. Supports column identifiers recognized by the API (note: these may differ from the select parameter identifiers).")
class GetV3SiteExplorerLinkeddomainsRequest(StrictModel):
    """Retrieve domains that link to your target domain or URL, with customizable filtering, sorting, and column selection for link analysis."""
    query: GetV3SiteExplorerLinkeddomainsRequestQuery

# Operation: list_external_anchors
class GetV3SiteExplorerLinkedAnchorsExternalRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze for outgoing external anchors.")
    select: str = Field(default=..., description="Comma-separated list of column identifiers to include in the response. See response schema for valid column names.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The scope of the search relative to your target: exact URL match, URL prefix match, entire domain, or all subdomains. Defaults to subdomains.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Filter results by protocol type: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 1000.")
    order_by: str | None = Field(default=None, description="Column identifier to sort results by. See response schema for valid column names.")
    where: str | None = Field(default=None, description="Filter expression to narrow results. Supports column identifiers recognized by the API (note: different set than the select parameter).")
class GetV3SiteExplorerLinkedAnchorsExternalRequest(StrictModel):
    """Retrieve outgoing external anchor links from a target domain or URL. Results can be filtered by search scope, protocol, and custom expressions, with configurable sorting and pagination."""
    query: GetV3SiteExplorerLinkedAnchorsExternalRequestQuery

# Operation: list_internal_anchors
class GetV3SiteExplorerLinkedAnchorsInternalRequestQuery(StrictModel):
    target: str = Field(default=..., description="The domain or URL to analyze for outgoing internal anchors.")
    select: str = Field(default=..., description="Comma-separated list of columns to include in the response. See response schema for valid column identifiers.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="The scope of the search relative to your target: exact URL match, URL prefix match, entire domain, or subdomains. Defaults to subdomains.")
    protocol: Literal["both", "http", "https"] | None = Field(default=None, description="Filter results by protocol type: both HTTP and HTTPS, HTTP only, or HTTPS only. Defaults to both.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 1000.")
    order_by: str | None = Field(default=None, description="Column identifier to sort results by. See response schema for valid column identifiers.")
    where: str | None = Field(default=None, description="Filter expression to narrow results. Supports the column identifiers listed in the response schema (note: different identifiers than the select parameter).")
class GetV3SiteExplorerLinkedAnchorsInternalRequest(StrictModel):
    """Retrieve outgoing internal anchor links from a target domain or URL. Results can be filtered, ordered, and scoped by search mode and protocol."""
    query: GetV3SiteExplorerLinkedAnchorsInternalRequestQuery

# Operation: get_keyword_metrics
class GetV3KeywordsExplorerOverviewRequestQuery(StrictModel):
    select: str = Field(default=..., description="Comma-separated list of data columns to include in the response. Refer to the response schema for valid column identifiers.")
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(default=..., description="Two-letter ISO 3166-1 country code (e.g., 'us', 'gb', 'de') specifying the target market for keyword data.")
    target: str | None = Field(default=None, description="Optional domain or URL to analyze keyword rankings for. Use with target_mode to define the scope of analysis.")
    target_mode: Literal["exact", "prefix", "domain", "subdomains"] | None = Field(default=None, description="Scope of the target URL analysis: 'exact' for the exact URL, 'prefix' for URL path prefix, 'domain' for the entire domain, or 'subdomains' for all subdomains.")
    target_position: Literal["in_top10", "in_top100"] | None = Field(default=None, description="Filter keywords by the ranking position of the specified target: 'in_top10' for top 10 rankings or 'in_top100' for top 100 rankings.")
    volume_monthly_date_from: str | None = Field(default=None, description="Start date in YYYY-MM-DD format for retrieving historical monthly search volume data. Required only when requesting volume_monthly_history.", json_schema_extra={'format': 'date'})
    volume_monthly_date_to: str | None = Field(default=None, description="End date in YYYY-MM-DD format for retrieving historical monthly search volume data. Required only when requesting volume_monthly_history.", json_schema_extra={'format': 'date'})
    where: str | None = Field(default=None, description="Filter expression to narrow results based on keyword metrics and attributes. Refer to the response schema for supported column identifiers.")
    order_by: str | None = Field(default=None, description="Column identifier to sort results by. Refer to the response schema for valid options; note that volume_monthly is not supported for sorting on this endpoint.")
    limit: int | None = Field(default=None, description="Maximum number of results to return. Defaults to 1000 if not specified.")
    search_engine: Literal["google"] | None = Field(default=None, description="Deprecated parameter. Only 'google' is supported; included for backward compatibility.")
class GetV3KeywordsExplorerOverviewRequest(StrictModel):
    """Retrieve keyword performance metrics and search data for specified keywords in a target country, with optional filtering by domain/URL ranking position and historical volume trends."""
    query: GetV3KeywordsExplorerOverviewRequestQuery

# Operation: get_keyword_volume_history
class GetV3KeywordsExplorerVolumeHistoryRequestQuery(StrictModel):
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(default=..., description="The target country for volume data, specified as a two-letter ISO 3166-1 alpha-2 country code (e.g., 'us' for United States, 'gb' for United Kingdom).")
    keyword: str = Field(default=..., description="The keyword term to retrieve volume history for.")
    date_from: str | None = Field(default=None, description="The start date for the historical period in YYYY-MM-DD format. If omitted, defaults to the earliest available data.", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="The end date for the historical period in YYYY-MM-DD format. If omitted, defaults to the most recent available data.", json_schema_extra={'format': 'date'})
class GetV3KeywordsExplorerVolumeHistoryRequest(StrictModel):
    """Retrieve historical search volume data for a keyword across a specified date range in a given country. Use this to analyze keyword popularity trends over time."""
    query: GetV3KeywordsExplorerVolumeHistoryRequestQuery

# Operation: get_keyword_volume_by_country
class GetV3KeywordsExplorerVolumeByCountryRequestQuery(StrictModel):
    keyword: str = Field(default=..., description="The keyword to analyze. Provide the exact search term you want to get volume data for.")
    limit: int | None = Field(default=None, description="Maximum number of countries to return in the results. Omit to get all available data.")
    search_engine: Literal["google"] | None = Field(default=None, description="Search engine to query (currently only Google is supported). This parameter is deprecated as of August 5, 2024.")
class GetV3KeywordsExplorerVolumeByCountryRequest(StrictModel):
    """Retrieve search volume metrics for a keyword broken down by country. Use this to understand geographic demand patterns and identify high-opportunity markets for your target keyword."""
    query: GetV3KeywordsExplorerVolumeByCountryRequestQuery

# Operation: search_matching_keywords
class GetV3KeywordsExplorerMatchingTermsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 1000 results if not specified.")
    order_by: str | None = Field(default=None, description="Column name to sort results by in ascending order. Refer to the response schema for valid column names; monthly search volume is not supported for sorting on this endpoint.")
    where: str | None = Field(default=None, description="Filter expression to narrow results based on keyword metrics and attributes. Use column identifiers from the response schema to construct filter conditions.")
    select: str = Field(default=..., description="Comma-separated list of data columns to include in the response. Specify which metrics and attributes you want returned for each matching keyword.")
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(default=..., description="Two-letter ISO country code (e.g., 'us', 'gb', 'de') that determines the geographic market for keyword data and search volume metrics.")
    search_engine: Literal["google"] | None = Field(default=None, description="Deprecated parameter. Only 'google' is supported; included for backward compatibility.")
    match_mode: Literal["terms", "phrase"] | None = Field(default=None, description="Search matching mode: 'terms' finds keywords containing your search words in any order, while 'phrase' requires exact word order. Defaults to 'terms' mode.")
    terms: Literal["all", "questions"] | None = Field(default=None, description="Filter results to include all keyword ideas or only those phrased as questions. Defaults to returning all keyword ideas.")
class GetV3KeywordsExplorerMatchingTermsRequest(StrictModel):
    """Find keyword variations and related search terms with performance metrics for a specific country. Returns matching keywords based on search mode (exact phrase or term-based) with optional filtering and sorting capabilities."""
    query: GetV3KeywordsExplorerMatchingTermsRequestQuery

# Operation: list_related_keywords
class GetV3KeywordsExplorerRelatedTermsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 1000 results if not specified.")
    order_by: str | None = Field(default=None, description="Column name to sort results by. Refer to the response schema for valid column identifiers; note that monthly search volume is not available as a sort option for this endpoint.")
    where: str | None = Field(default=None, description="Filter expression to narrow results. Use column identifiers from the response schema to create conditions (note: different identifiers than those used in the select parameter).")
    select: str = Field(default=..., description="Comma-separated list of data columns to include in the response. Required parameter that determines which metrics and attributes are returned.")
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(default=..., description="Two-letter ISO country code (e.g., 'us', 'gb', 'de') specifying the geographic market for keyword data. Required parameter.")
    view_for: Literal["top_10", "top_100"] | None = Field(default=None, description="Scope of analysis: analyze keywords from the top 10 or top 100 ranking pages. Defaults to top 10 if not specified.")
    terms: Literal["also_rank_for", "also_talk_about", "all"] | None = Field(default=None, description="Type of related keywords to retrieve: keywords the top pages also rank for, topics they mention, or both combined. Defaults to all types if not specified.")
class GetV3KeywordsExplorerRelatedTermsRequest(StrictModel):
    """Discover related keywords that top-ranking pages rank for or mention, including keywords they also target and topics they discuss. Use this to identify keyword opportunities and content gaps around your target search terms."""
    query: GetV3KeywordsExplorerRelatedTermsRequestQuery

# Operation: search_keyword_suggestions
class GetV3KeywordsExplorerSearchSuggestionsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of suggestions to return in the response. Defaults to 1000 results if not specified.")
    order_by: str | None = Field(default=None, description="Column name to sort results by. Refer to the response schema for valid column identifiers; note that monthly search volume is not available as a sort option for this endpoint.")
    where: str | None = Field(default=None, description="Filter expression to narrow results. Use column identifiers from the response schema to create conditions (different identifiers than those used in the select parameter).")
    select: str = Field(default=..., description="Comma-separated list of data columns to include in the response. Required parameter that determines which fields are returned for each suggestion.")
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(default=..., description="Two-letter ISO 3166-1 country code specifying the geographic market for keyword suggestions. Required parameter that determines regional search data.")
    search_engine: Literal["google"] | None = Field(default=None, description="Search engine source for suggestions. Currently supports Google only; this parameter is deprecated as of August 5, 2024.")
class GetV3KeywordsExplorerSearchSuggestionsRequest(StrictModel):
    """Retrieve keyword search suggestions for a specified country. Returns relevant keyword variations and related search terms to help identify search opportunities in your target market."""
    query: GetV3KeywordsExplorerSearchSuggestionsRequestQuery

# Operation: list_audit_projects
class GetV3SiteAuditProjectsRequestQuery(StrictModel):
    project_url: str | None = Field(default=None, description="Filter results to projects matching this target URL. The comparison ignores protocol differences and trailing slashes for flexible matching.")
    project_name: str | None = Field(default=None, description="Filter results to projects matching this name.")
    date: str | None = Field(default=None, description="Retrieve metrics from a specific crawl date and time in ISO 8601 format (YYYY-MM-DDThh:mm:ss UTC). If omitted, returns data from the most recent available crawl. For scheduled crawls, returns the latest crawl completed before this timestamp; for Always-on audits, returns data as of the specified moment. The time component defaults to 00:00:00 if not provided.", json_schema_extra={'format': 'date-time'})
class GetV3SiteAuditProjectsRequest(StrictModel):
    """Retrieve health scores and performance metrics for Site Audit projects. Returns data from the most recent crawl by default, or from a specified crawl date if provided."""
    query: GetV3SiteAuditProjectsRequestQuery | None = None

# Operation: list_audit_issues
class GetV3SiteAuditIssuesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project, found in the URL of your Site Audit project dashboard (https://app.ahrefs.com/site-audit/#project_id#).")
    date: str | None = Field(default=None, description="Optional timestamp in ISO 8601 format (YYYY-MM-DDThh:mm:ss UTC) to retrieve issues from a specific crawl. Defaults to the most recent crawl if not provided. For scheduled crawls, returns data from the latest crawl completed before this timestamp; for Always-on audits, returns data as of the specified date and time. If only the date is provided without time, it defaults to 00:00:00 UTC.", json_schema_extra={'format': 'date-time'})
class GetV3SiteAuditIssuesRequest(StrictModel):
    """Retrieve site audit issues for a specific project. This operation costs 50 API units per request and returns issues from either a specified crawl date or the most recent available crawl."""
    query: GetV3SiteAuditIssuesRequestQuery

# Operation: get_page_content
class GetV3SiteAuditPageContentRequestQuery(StrictModel):
    select: str = Field(default=..., description="Comma-separated list of column identifiers to include in the response. Refer to the response schema for valid column names.")
    date: str | None = Field(default=None, description="Optional crawl date in ISO 8601 format (YYYY-MM-DDThh:mm:ss UTC). Defaults to the most recent crawl if omitted. For scheduled crawls, returns data from the latest crawl completed before this timestamp; for Always-on audits, returns data as of the specified date and time. If only the date is provided, the time defaults to 00:00:00 UTC.", json_schema_extra={'format': 'date-time'})
    target_url: str = Field(default=..., description="The full URL of the page to retrieve content for.")
    project_id: int = Field(default=..., description="The unique identifier of the Site Audit project. Only projects with verified ownership are supported. You can find this ID in your Site Audit project URL on Ahrefs.")
class GetV3SiteAuditPageContentRequest(StrictModel):
    """Retrieve page content and metadata from a Site Audit project for a specific URL. This operation consumes 50 API units per request."""
    query: GetV3SiteAuditPageContentRequestQuery

# Operation: list_audit_pages
class GetV3SiteAuditPageExplorerRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project. Only projects with verified ownership are supported. You can find this in your Site Audit project URL on Ahrefs.")
    date: str | None = Field(default=None, description="The crawl date to retrieve metrics from in ISO 8601 format (YYYY-MM-DDThh:mm:ss UTC). Defaults to the most recent crawl if omitted. For scheduled crawls, returns data from the latest crawl before this timestamp; for Always-on audits, returns data as of the specified date. If time is omitted, defaults to 00:00:00 UTC.", json_schema_extra={'format': 'date-time'})
    select: str | None = Field(default=None, description="A comma-separated list of columns to include in the response. Defaults to a comprehensive set including page rating, URL, HTTP status, content type, title, meta description, heading, traffic, canonical status, redirect information, link counts, Core Web Vitals categories, and schema validation data.")
    order_by: str | None = Field(default=None, description="The column name to sort results by. Must be one of the valid columns available in the response schema.")
    limit: int | None = Field(default=None, description="The maximum number of results to return. Defaults to 1000 results per request.")
    filter_mode: Literal["added", "new", "removed", "missing", "no_change"] | None = Field(default=None, description="Filter pages by their status relative to the previous crawl. Use 'added' for new matches, 'new' for newly crawled pages, 'removed' for pages no longer matching filters, 'missing' for uncrawled pages that previously matched, or 'no_change' for pages matching in both crawls. If omitted, returns all matching pages.")
    issue_id: str | None = Field(default=None, description="The unique identifier of a specific issue to filter by. When specified, only pages affected by this issue are returned. Retrieve issue IDs from the site-audit/issues endpoint.")
    where: str | None = Field(default=None, description="The filter expression. The following column identifiers are recognized (this differs from the identifiers recognized by the select parameter).")
class GetV3SiteAuditPageExplorerRequest(StrictModel):
    """Retrieve page-level metrics and SEO data from a Site Audit crawl. This endpoint costs 50 API units per request and supports filtering, sorting, and comparison against previous crawls."""
    query: GetV3SiteAuditPageExplorerRequestQuery

# Operation: get_rank_tracker_overview
class GetV3RankTrackerOverviewRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the Rank Tracker project, found in the project URL on Ahrefs.")
    date: str = Field(default=..., description="The date for which to report metrics, specified in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    device: Literal["desktop", "mobile"] = Field(default=..., description="The device type for ranking data: either desktop or mobile.")
    select: str = Field(default=..., description="A comma-separated list of metric columns to include in the response. Refer to the response schema for valid column identifiers.")
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="The search volume calculation method: monthly (default) calculates based on monthly data, while average uses historical averages. This affects volume, traffic, and traffic value metrics.")
    order_by: str | None = Field(default=None, description="A column identifier to sort results by. Refer to the response schema for valid column identifiers.")
    limit: int | None = Field(default=None, description="The maximum number of results to return. Defaults to 1000 if not specified.")
    where: str | None = Field(default=None, description="A filter expression to narrow results by specific criteria. Refer to the response schema for recognized column identifiers and filter syntax.")
class GetV3RankTrackerOverviewRequest(StrictModel):
    """Retrieve overview metrics for all tracked keywords in a Rank Tracker project on a specific date, with support for filtering, sorting, and device-specific rankings."""
    query: GetV3RankTrackerOverviewRequestQuery

# Operation: get_serp_overview
class GetV3RankTrackerSerpOverviewRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of your Rank Tracker project, found in the project URL on Ahrefs.")
    keyword: str = Field(default=..., description="The keyword to retrieve SERP data for.")
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(default=..., description="The target country specified as a two-letter ISO 3166-1 alpha-2 code (e.g., 'us', 'gb', 'de').")
    device: Literal["desktop", "mobile"] = Field(default=..., description="The device type for ranking data: either 'desktop' or 'mobile'.")
    language_code: str | None = Field(default=None, description="Optional language code for the tracked keyword. Use the management/project-keywords endpoint to find the correct language code for your keyword.")
    location_id: int | None = Field(default=None, description="Optional location ID for the tracked keyword. Use the management/project-keywords endpoint to find the correct location ID for your keyword.")
    date: str | None = Field(default=None, description="Optional timestamp to retrieve historical SERP data in ISO 8601 format (YYYY-MM-DDThh:mm:ss). If omitted, returns the most recent available data.", json_schema_extra={'format': 'date-time'})
    top_positions: int | None = Field(default=None, description="Optional limit on the number of top organic positions to return. If not specified, all available positions are included.")
class GetV3RankTrackerSerpOverviewRequest(StrictModel):
    """Retrieve the current SERP overview for a tracked keyword, including top organic positions and ranking data. This endpoint is free and does not consume API units."""
    query: GetV3RankTrackerSerpOverviewRequestQuery

# Operation: list_competitor_rankings
class GetV3RankTrackerCompetitorsOverviewRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of your Rank Tracker project, found in the project URL within Ahrefs.")
    date: str = Field(default=..., description="The date for which to retrieve ranking metrics, specified in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    device: Literal["desktop", "mobile"] = Field(default=..., description="The device type to report rankings for: either desktop or mobile.")
    select: str = Field(default=..., description="A comma-separated list of column identifiers to include in the response. Refer to the response schema for valid column names.")
    limit: int | None = Field(default=None, description="The maximum number of results to return in the response. Defaults to 1000 if not specified.")
    order_by: str | None = Field(default=None, description="The column identifier to sort results by. Refer to the response schema for valid column names.")
    where: str | None = Field(default=None, description="A filter expression to narrow results. Supports filtering by recognized column identifiers (which may differ from those used in the select parameter).")
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="The method for calculating search volume metrics: monthly (default) or average. This affects volume, traffic, and traffic value calculations.")
class GetV3RankTrackerCompetitorsOverviewRequest(StrictModel):
    """Retrieve an overview of competitor rankings for your tracked keywords on a specific date. This endpoint is free and does not consume API units."""
    query: GetV3RankTrackerCompetitorsOverviewRequestQuery

# Operation: list_competitor_pages
class GetV3RankTrackerCompetitorsPagesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of your Rank Tracker project, found in the project URL on Ahrefs.")
    date: str = Field(default=..., description="The date for which to retrieve metrics, specified in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    device: Literal["desktop", "mobile"] = Field(default=..., description="The device type to report rankings for: either desktop or mobile.")
    select: str = Field(default=..., description="A comma-separated list of column identifiers to include in the response. Refer to the response schema for valid column names.")
    limit: int | None = Field(default=None, description="The maximum number of results to return. Defaults to 1000 if not specified.")
    order_by: str | None = Field(default=None, description="A column identifier to sort results by. Refer to the response schema for valid column names.")
    where: str | None = Field(default=None, description="A filter expression to narrow results. Supports column identifiers recognized by the API (which may differ from select parameter identifiers).")
    target_and_tracked_competitors_only: bool | None = Field(default=None, description="When enabled, restricts results to only target and tracked competitors. Defaults to false.")
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="The method for calculating search volume: monthly (default) or average. This affects volume, traffic, and traffic value metrics.")
class GetV3RankTrackerCompetitorsPagesRequest(StrictModel):
    """Retrieve competitor pages data for a Rank Tracker project on a specific date, filtered by device type and customizable metrics."""
    query: GetV3RankTrackerCompetitorsPagesRequestQuery

# Operation: list_competitor_stats
class GetV3RankTrackerCompetitorsStatsRequestQuery(StrictModel):
    select: str = Field(default=..., description="Comma-separated list of metric columns to include in the response. Refer to the response schema for available column identifiers.")
    date: str = Field(default=..., description="The date for which to retrieve metrics, formatted as YYYY-MM-DD.", json_schema_extra={'format': 'date'})
    device: Literal["desktop", "mobile"] = Field(default=..., description="The device type to report rankings for: either desktop or mobile.")
    project_id: int = Field(default=..., description="The unique identifier of your Rank Tracker project, found in the project URL within Ahrefs.")
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="The method for calculating search volume metrics: monthly (default) for monthly averages or average for overall average volume. This affects volume, traffic, and traffic value calculations.")
class GetV3RankTrackerCompetitorsStatsRequest(StrictModel):
    """Retrieve competitor performance metrics for tracked keywords on a specified date and device type. Use this to analyze how competitors rank for your target keywords and monitor their search visibility."""
    query: GetV3RankTrackerCompetitorsStatsRequestQuery

# Operation: get_serp_overview_keyword
class GetV3SerpOverviewRequestQuery(StrictModel):
    select: str = Field(default=..., description="Comma-separated list of data columns to include in the response. Refer to the response schema documentation for valid column identifiers.")
    top_positions: int | None = Field(default=None, description="Maximum number of top organic search results to return. If omitted, all available positions are included.")
    date: str | None = Field(default=None, description="Specific date and time for which to retrieve SERP data in ISO 8601 format (YYYY-MM-DDThh:mm:ss). If not provided, the most recent available data is returned.", json_schema_extra={'format': 'date-time'})
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(default=..., description="Two-letter ISO 3166-1 country code (e.g., 'us', 'gb', 'de') indicating the search market for the SERP data.")
    keyword: str = Field(default=..., description="The search keyword to retrieve SERP overview data for.")
class GetV3SerpOverviewRequest(StrictModel):
    """Retrieve SERP (Search Engine Results Page) overview data for a keyword in a specified country, including top organic positions and customizable metrics."""
    query: GetV3SerpOverviewRequestQuery

# Operation: analyze_targets_batch
class PostV3BatchAnalysisRequestBody(StrictModel):
    select: list[str] = Field(default=..., description="Specify which SEO metrics to include in the response (e.g., url, ahrefs_rank). Refer to the response schema for all available column identifiers.")
    order_by: str | None = Field(default=None, description="Sort results by a specific SEO metric column. Refer to the response schema for valid column identifiers.")
    volume_mode: Literal["monthly", "average"] | None = Field(default=None, description="Choose how search volume is calculated: monthly (current month data) or average (historical average). This affects volume, traffic, and traffic value metrics.")
    targets: list[PostV3BatchAnalysisBodyTargetsItem] = Field(default=..., description="Provide a list of targets (domains, URLs, or keywords) to analyze. Each target will be evaluated for the selected metrics.")
class PostV3BatchAnalysisRequest(StrictModel):
    """Perform batch SEO analysis on multiple targets to retrieve comprehensive metrics including backlinks, keywords, traffic, and ranking data. Customize which metrics to return and how results are ordered."""
    body: PostV3BatchAnalysisRequestBody

# Operation: list_projects
class GetV3ManagementProjectsRequestQuery(StrictModel):
    owned_by: str | None = Field(default=None, description="Filter projects by the email address of the project owner.")
    access: Literal["private", "shared"] | None = Field(default=None, description="Filter projects by access type: either private (accessible only to you) or shared (accessible to others).")
    has_keywords: bool | None = Field(default=None, description="Filter to only include projects that have Rank Tracker keywords configured.")
class GetV3ManagementProjectsRequest(StrictModel):
    """Retrieve your projects with optional filtering by owner, access type, and keyword tracking status. This operation is free and does not consume any API units."""
    query: GetV3ManagementProjectsRequestQuery | None = None

# Operation: create_project
class PostV3ManagementProjectsRequestBody(StrictModel):
    owned_by: str | None = Field(default=None, description="The email address of the user who will own this project. If not specified, ownership defaults to the workspace owner.")
    access: Literal["private", "shared"] | None = Field(default=None, description="The access control level for this project, either private (restricted to owner) or shared (accessible to workspace members).")
    protocol: Literal["both", "http", "https"] = Field(default=..., description="The protocol(s) to monitor for the target: http only, https only, or both protocols.")
    url: str = Field(default=..., description="The URL of the target resource or service that this project will monitor or manage.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] = Field(default=..., description="The scope matching strategy for the target URL: exact (precise URL match), prefix (URL and all subpaths), domain (entire domain), or subdomains (domain and all subdomains).")
    project_name: str = Field(default=..., description="A descriptive name for this project to identify it within the workspace.")
class PostV3ManagementProjectsRequest(StrictModel):
    """Create a new project by specifying a target URL, protocol, and matching scope. The project will be assigned to the specified owner or the workspace owner by default."""
    body: PostV3ManagementProjectsRequestBody

# Operation: update_project_access
class PatchV3ManagementUpdateProjectRequestBody(StrictModel):
    access: Literal["private", "shared"] = Field(default=..., description="The new access level for the project. Must be either 'private' to restrict access to the project owner, or 'shared' to allow others to access it.")
    project_id: int = Field(default=..., description="The unique identifier of the project to update. You can find this ID in the URL of your Rank Tracker project dashboard in Ahrefs (the numeric value in the project URL).")
class PatchV3ManagementUpdateProjectRequest(StrictModel):
    """Update the access setting for a project to control whether it is private or shared. This operation is free and does not consume any API units."""
    body: PatchV3ManagementUpdateProjectRequestBody

# Operation: list_project_keywords
class GetV3ManagementProjectKeywordsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project, found in the URL of your Rank Tracker project dashboard (the numeric ID in the project URL).")
class GetV3ManagementProjectKeywordsRequest(StrictModel):
    """Retrieve all keywords tracked for a specific project in Rank Tracker. This operation is free and does not consume any API units."""
    query: GetV3ManagementProjectKeywordsRequestQuery

# Operation: add_keywords
class PutV3ManagementProjectKeywordsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project you want to add keywords to. You can find this ID in the URL of your Rank Tracker project dashboard.")
class PutV3ManagementProjectKeywordsRequestBody(StrictModel):
    locations: list[PutV3ManagementProjectKeywordsBodyLocationsItem] = Field(default=..., description="A list of locations where the keywords should be tracked. Use the Locations and languages endpoint to retrieve valid country codes, language codes, and location IDs for your target regions.")
    keywords: list[PutV3ManagementProjectKeywordsBodyKeywordsItem] = Field(default=..., description="A list of keywords to add to the project. Each keyword will be assigned to all specified locations.")
class PutV3ManagementProjectKeywordsRequest(StrictModel):
    """Add keywords to a project and assign them to specific locations for tracking. This operation allows you to expand your keyword monitoring across different geographic regions."""
    query: PutV3ManagementProjectKeywordsRequestQuery
    body: PutV3ManagementProjectKeywordsRequestBody

# Operation: delete_keywords
class PutV3ManagementProjectKeywordsDeleteRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the Rank Tracker project, found in the project URL within Ahrefs.")
class PutV3ManagementProjectKeywordsDeleteRequestBody(StrictModel):
    keywords: list[PutV3ManagementProjectKeywordsDeleteBodyKeywordsItem] = Field(default=..., description="An array of keywords to remove from the project. Each keyword should be specified as a string value.")
class PutV3ManagementProjectKeywordsDeleteRequest(StrictModel):
    """Remove one or more keywords from a Rank Tracker project. This operation is free and does not consume API units."""
    query: PutV3ManagementProjectKeywordsDeleteRequestQuery
    body: PutV3ManagementProjectKeywordsDeleteRequestBody

# Operation: list_project_competitors
class GetV3ManagementProjectCompetitorsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project, found in the URL of your Rank Tracker project dashboard (the numeric ID in the project overview URL).")
class GetV3ManagementProjectCompetitorsRequest(StrictModel):
    """Retrieve the list of competitors tracked for a specific project. This operation is free and does not consume any API units."""
    query: GetV3ManagementProjectCompetitorsRequestQuery

# Operation: add_competitors
class PostV3ManagementProjectCompetitorsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the Rank Tracker project. You can find this ID in the URL of your project dashboard (https://app.ahrefs.com/rank-tracker/overview/#project_id#).")
class PostV3ManagementProjectCompetitorsRequestBody(StrictModel):
    competitors: list[PostV3ManagementProjectCompetitorsBodyCompetitorsItem] = Field(default=..., description="An array of competitor entries to add to the project. Each item represents a competitor domain or website to track.")
class PostV3ManagementProjectCompetitorsRequest(StrictModel):
    """Add competitors to a Rank Tracker project for monitoring and comparison. This operation is free and does not consume API units."""
    query: PostV3ManagementProjectCompetitorsRequestQuery
    body: PostV3ManagementProjectCompetitorsRequestBody

# Operation: delete_competitors
class PostV3ManagementProjectCompetitorsDeleteRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the Rank Tracker project, found in the project URL within Ahrefs (e.g., https://app.ahrefs.com/rank-tracker/overview/#project_id#).")
class PostV3ManagementProjectCompetitorsDeleteRequestBody(StrictModel):
    competitors: list[PostV3ManagementProjectCompetitorsDeleteBodyCompetitorsItem] = Field(default=..., description="An array of competitor identifiers to remove from the project. Each item should be a competitor ID.")
class PostV3ManagementProjectCompetitorsDeleteRequest(StrictModel):
    """Remove competitors from a Rank Tracker project. This operation is free and does not consume any API units."""
    query: PostV3ManagementProjectCompetitorsDeleteRequestQuery
    body: PostV3ManagementProjectCompetitorsDeleteRequestBody

# Operation: list_locations
class GetV3ManagementLocationsRequestQuery(StrictModel):
    country_code: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(default=..., description="The two-letter ISO 3166-1 alpha-2 country code identifying the country for which to retrieve location and language information.")
    us_state: Literal["al", "ak", "az", "ar", "ca", "co", "ct", "de", "dc", "fl", "ga", "hi", "id", "il", "in", "ia", "ks", "ky", "la", "me", "md", "ma", "mi", "mn", "ms", "mo", "mt", "ne", "nv", "nh", "nj", "nm", "ny", "nc", "nd", "oh", "ok", "or", "pa", "ri", "sc", "sd", "tn", "tx", "ut", "va", "wa", "wv", "wi", "wy"] | None = Field(default=None, description="The two-letter ISO 3166-2:US state code. Required only when country_code is set to 'us' to retrieve state-specific location and language data.")
class GetV3ManagementLocationsRequest(StrictModel):
    """Retrieve available locations and supported languages for a specified country. This is a free operation that does not consume API units."""
    query: GetV3ManagementLocationsRequestQuery

# Operation: list_keyword_list_keywords
class GetV3ManagementKeywordListKeywordsRequestQuery(StrictModel):
    keyword_list_id: int = Field(default=..., description="The unique identifier of the keyword list from which to retrieve keywords.")
class GetV3ManagementKeywordListKeywordsRequest(StrictModel):
    """Retrieve all keywords from a specified keyword list. This operation is free and does not consume any API units."""
    query: GetV3ManagementKeywordListKeywordsRequestQuery

# Operation: add_keywords_to_list
class PutV3ManagementKeywordListKeywordsRequestQuery(StrictModel):
    keyword_list_id: int = Field(default=..., description="The unique identifier of the keyword list to update. Must reference an existing keyword list.")
class PutV3ManagementKeywordListKeywordsRequestBody(StrictModel):
    keywords: list[str] = Field(default=..., description="An array of keywords to add to the list. Each keyword is a string value; order is preserved as provided.")
class PutV3ManagementKeywordListKeywordsRequest(StrictModel):
    """Add one or more keywords to an existing keyword list. The keywords will be appended to the list's current contents."""
    query: PutV3ManagementKeywordListKeywordsRequestQuery
    body: PutV3ManagementKeywordListKeywordsRequestBody

# Operation: delete_keyword_list_keywords
class PutV3ManagementKeywordListKeywordsDeleteRequestQuery(StrictModel):
    keyword_list_id: int = Field(default=..., description="The unique identifier of the keyword list from which keywords will be removed.")
class PutV3ManagementKeywordListKeywordsDeleteRequestBody(StrictModel):
    keywords: list[str] = Field(default=..., description="An array of keywords to delete from the specified keyword list. Each keyword in the array will be removed from the list.")
class PutV3ManagementKeywordListKeywordsDeleteRequest(StrictModel):
    """Remove one or more keywords from an existing keyword list. Specify the keyword list by its ID and provide the keywords to be deleted."""
    query: PutV3ManagementKeywordListKeywordsDeleteRequestQuery
    body: PutV3ManagementKeywordListKeywordsDeleteRequestBody

# Operation: list_brand_radar_prompts
class GetV3ManagementBrandRadarPromptsRequestQuery(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the Brand Radar report. You can find this ID in the URL of your Brand Radar report within Ahrefs (the #report_id# segment in https://app.ahrefs.com/brand-radar/reports/#report_id#/...).")
class GetV3ManagementBrandRadarPromptsRequest(StrictModel):
    """Retrieve the Brand Radar prompts associated with a specific report. This operation is free and does not consume any API units."""
    query: GetV3ManagementBrandRadarPromptsRequestQuery

# Operation: create_brand_radar_prompt
class PostV3ManagementBrandRadarPromptsRequestQuery(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the Brand Radar report where prompts will be applied. You can find this ID in the URL of your Brand Radar report in Ahrefs.")
class PostV3ManagementBrandRadarPromptsRequestBody(StrictModel):
    countries: list[str] = Field(default=..., description="A list of two-letter country codes in ISO 3166-1 alpha-2 format specifying the geographic regions for the prompts.")
    prompts: list[str] = Field(default=..., description="A list of custom prompts to apply to the report. Each prompt must be valid UTF-8 text and not exceed 400 characters in length.")
class PostV3ManagementBrandRadarPromptsRequest(StrictModel):
    """Create custom prompts for Brand Radar reports to customize monitoring and analysis. This operation is free and does not consume API units."""
    query: PostV3ManagementBrandRadarPromptsRequestQuery
    body: PostV3ManagementBrandRadarPromptsRequestBody

# Operation: delete_brand_radar_prompts
class PutV3ManagementBrandRadarPromptsDeleteRequestQuery(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the Brand Radar report from which to delete prompts. You can find this ID in the URL of your Brand Radar report in Ahrefs.")
class PutV3ManagementBrandRadarPromptsDeleteRequestBody(StrictModel):
    countries: list[str] | None = Field(default=None, description="Optional list of two-letter country codes (ISO 3166-1 alpha-2 format) to scope the prompt deletion to specific countries.")
    prompts: list[str] = Field(default=..., description="List of custom prompts to delete. Each prompt must be valid UTF-8 encoded text and not exceed 400 characters in length.")
class PutV3ManagementBrandRadarPromptsDeleteRequest(StrictModel):
    """Remove custom prompts from a Brand Radar report. This operation is free and does not consume API units."""
    query: PutV3ManagementBrandRadarPromptsDeleteRequestQuery
    body: PutV3ManagementBrandRadarPromptsDeleteRequestBody

# Operation: create_brand_radar_report
class PostV3ManagementBrandRadarReportsRequestBody(StrictModel):
    data_source: Literal["chatgpt", "gemini", "perplexity", "copilot"] = Field(default=..., description="The AI data source to monitor for brand mentions. Choose from ChatGPT, Gemini, Perplexity, or Copilot.")
    frequency: Literal["daily", "weekly", "monthly", "off"] = Field(default=..., description="The update frequency for the report. Select daily for real-time monitoring, weekly for periodic summaries, monthly for long-term trends, or off to disable the report.")
    name: str | None = Field(default=None, description="A custom name for the report to help identify it in your dashboard.")
class PostV3ManagementBrandRadarReportsRequest(StrictModel):
    """Create a brand radar report that monitors brand mentions across AI-powered data sources. This operation is free and does not consume API units."""
    body: PostV3ManagementBrandRadarReportsRequestBody

# Operation: update_brand_radar_report
class PatchV3ManagementBrandRadarReportsRequestBody(StrictModel):
    prompts_frequency: list[PatchV3ManagementBrandRadarReportsBodyPromptsFrequencyItem] = Field(default=..., description="The frequency at which the report should generate prompts. Specify as an array of frequency values.")
    report_id: str = Field(default=..., description="The unique identifier of the Brand Radar report to update. You can find this ID in the URL of your report in Ahrefs at https://app.ahrefs.com/brand-radar/reports/#report_id#/...")
class PatchV3ManagementBrandRadarReportsRequest(StrictModel):
    """Update the configuration of a Brand Radar report, including its monitoring frequency. This operation is free and does not consume API units."""
    body: PatchV3ManagementBrandRadarReportsRequestBody

# Operation: list_ai_responses
class GetV3BrandRadarAiResponsesRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter expression to narrow results using recognized column identifiers. Refer to the response schema for valid column names to use in filter conditions.")
    select: str = Field(default=..., description="Comma-separated list of columns to include in the response. Required to specify which data fields you want returned.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 1000 if not specified.")
    date: str | None = Field(default=None, description="Specific date to search for, formatted as YYYY-MM-DD.", json_schema_extra={'format': 'date'})
    order_by: Literal["relevance", "volume"] | None = Field(default=None, description="Column to sort results by. Choose between relevance (default) or volume-based ordering.")
    report_id: str | None = Field(default=None, description="ID of a saved report to use as the base configuration. When provided, brand, competitors, market, and country settings are inherited from the report, though country and filters can be overridden.")
    prompts: Literal["ahrefs", "custom"] | None = Field(default=None, description="Type of prompts to use for generating responses. Choose Ahrefs prompts (standard pricing), custom prompts (free, requires report_id), or both (default). Custom prompts require a report_id to be provided.")
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(default=..., description="Comma-separated list of chatbot models to query. Choose from Google AI Overviews, Google AI Mode, ChatGPT, Gemini, Perplexity, or Copilot. Note: Google models cannot be combined with each other or with non-Google models.")
class GetV3BrandRadarAiResponsesRequest(StrictModel):
    """Retrieve AI-generated responses from multiple chatbot models for brand-related queries. API unit consumption depends on prompt type: custom prompts are free, while Ahrefs prompts follow standard pricing."""
    query: GetV3BrandRadarAiResponsesRequestQuery

# Operation: list_cited_pages
class GetV3BrandRadarCitedPagesRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter expression to narrow results by specific column criteria. Refer to the response schema for valid column identifiers supported by this filter.")
    select: str = Field(default=..., description="Comma-separated list of columns to include in the response. Required to specify which data fields you want returned.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 1000 if not specified.")
    date: str | None = Field(default=None, description="Specific date to search for in YYYY-MM-DD format. If omitted, returns results across all available dates.", json_schema_extra={'format': 'date'})
    report_id: str | None = Field(default=None, description="ID of a saved Brand Radar report to use as the configuration source. When provided, brand, competitors, market, and country settings are inherited from the report. You can find this ID in your Ahrefs Brand Radar report URL. Country and filter parameters will override report settings if also provided.")
    prompts: Literal["ahrefs", "custom"] | None = Field(default=None, description="Type of prompts to apply: 'ahrefs' for Ahrefs-generated prompts, 'custom' for your own prompts (requires report_id), or omit to use both types.")
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(default=..., description="Comma-separated list of chatbot models to query. Choose from Google AI Overviews, Google AI Mode, ChatGPT, Gemini, Perplexity, or Copilot. Note: Google models cannot be combined with each other or with non-Google models in a single request.")
class GetV3BrandRadarCitedPagesRequest(StrictModel):
    """Retrieve pages that cite your brand across specified chatbot models and AI overviews. API unit consumption depends on the prompts parameter: custom prompt data requests are free, while requests including Ahrefs prompt data incur standard API unit charges."""
    query: GetV3BrandRadarCitedPagesRequestQuery

# Operation: list_cited_domains
class GetV3BrandRadarCitedDomainsRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter expression to narrow results using recognized column identifiers. Refer to the response schema for valid column names to use in filter conditions.")
    select: str = Field(default=..., description="Comma-separated list of column identifiers to include in the response. Required to specify which data fields you want returned.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 1000 if not specified.")
    date: str | None = Field(default=None, description="Specific date to retrieve data for, formatted as YYYY-MM-DD.", json_schema_extra={'format': 'date'})
    report_id: str | None = Field(default=None, description="ID of a saved Brand Radar report to use as the configuration source. When provided, brand, competitors, market, and country settings are inherited from the report. You can find this ID in the URL of your Brand Radar report in Ahrefs. Country and filter parameters can override report settings if provided.")
    prompts: Literal["ahrefs", "custom"] | None = Field(default=None, description="Type of prompts to use for analysis. Choose 'ahrefs' for Ahrefs-generated prompts, 'custom' for your own prompts (requires report_id), or omit to use both types.")
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(default=..., description="Comma-separated list of chatbot models and AI sources to query. Choose from Google AI Overviews, Google AI Mode, ChatGPT, Gemini, Perplexity, or Copilot. Note: Google models cannot be combined with each other or with non-Google models in a single request.")
class GetV3BrandRadarCitedDomainsRequest(StrictModel):
    """Retrieve domains cited in AI visibility data from chatbot models and search engines. API unit consumption depends on the prompts parameter: requests using only custom prompts are free, while requests including Ahrefs prompts follow standard pricing."""
    query: GetV3BrandRadarCitedDomainsRequestQuery

# Operation: list_brand_radar_impression_overviews
class GetV3BrandRadarImpressionsOverviewRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter expression to narrow results using recognized column identifiers. Refer to the response schema for valid column names to use in filter conditions.")
    select: str = Field(default=..., description="Comma-separated list of columns to include in the response. Required parameter that determines which data fields are returned.")
    report_id: str | None = Field(default=None, description="ID of an existing Brand Radar report to use as a configuration source. When provided, brand, competitors, market, and country settings are inherited from the report. Can be found in the URL of your Brand Radar report in Ahrefs. Country and filter parameters will override report settings if also provided.")
    prompts: Literal["ahrefs", "custom"] | None = Field(default=None, description="Type of prompts to use for data retrieval: 'ahrefs' for Ahrefs-generated prompts, 'custom' for user-defined prompts, or omit to use both types. Custom prompts require a report_id to be specified.")
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(default=..., description="Comma-separated list of chatbot models to query. Choose from: google_ai_overviews, google_ai_mode, chatgpt, gemini, perplexity, or copilot. Note: Google models cannot be combined with each other or with non-Google models in a single request.")
class GetV3BrandRadarImpressionsOverviewRequest(StrictModel):
    """Retrieve impressions overview data for Brand Radar across specified chatbot models and data sources. API unit consumption depends on prompt type: custom prompts are free, while Ahrefs prompts follow standard pricing."""
    query: GetV3BrandRadarImpressionsOverviewRequestQuery

# Operation: list_brand_mentions_overview
class GetV3BrandRadarMentionsOverviewRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter expression to narrow results using recognized column identifiers. Use this to apply conditions on the mentions data.")
    select: str = Field(default=..., description="Comma-separated list of column identifiers to include in the response. Required to specify which data fields to return.")
    report_id: str | None = Field(default=None, description="The Brand Radar report ID to use as a template. When provided, brand, competitors, market, and country settings are inherited from the report. You can find this ID in your Brand Radar report URL. Country or filter parameters will override report settings if also provided.")
    prompts: Literal["ahrefs", "custom"] | None = Field(default=None, description="Type of prompts to apply to the data. Choose 'ahrefs' for Ahrefs-generated prompts, 'custom' for your own prompts (requires a report_id), or omit to use both types.")
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(default=..., description="Comma-separated list of AI chatbot models to query. Choose from Google AI Overviews, Google AI Mode, ChatGPT, Gemini, Perplexity, or Copilot. Note: Google models cannot be combined with each other or with non-Google models.")
class GetV3BrandRadarMentionsOverviewRequest(StrictModel):
    """Retrieve an overview of brand mentions data across specified data sources. API unit consumption depends on prompt type: custom prompts only are free, while Ahrefs prompts follow standard pricing."""
    query: GetV3BrandRadarMentionsOverviewRequestQuery

# Operation: get_share_of_voice_overview
class GetV3BrandRadarSovOverviewRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter expression to narrow results using recognized column identifiers specific to this endpoint.")
    report_id: str | None = Field(default=None, description="The Brand Radar report ID to use as a base configuration. When provided, brand, competitors, market, and country settings are inherited from the report, though country and filter parameters can override report settings if explicitly provided.")
    prompts: Literal["ahrefs", "custom"] | None = Field(default=None, description="Specify which prompt types to include: 'ahrefs' for Ahrefs-generated prompts, 'custom' for custom prompts (requires report_id), or omit to use both types.")
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(default=..., description="Comma-separated list of chatbot models to query. Google models (google_ai_overviews and google_ai_mode) cannot be combined with each other or with non-Google models. Required parameter.")
class GetV3BrandRadarSovOverviewRequest(StrictModel):
    """Retrieve Share of Voice data for brands across specified data sources. API unit consumption depends on prompt type: custom prompts only are free, while Ahrefs prompts follow standard pricing."""
    query: GetV3BrandRadarSovOverviewRequestQuery

# Operation: list_brand_mention_impressions_history
class GetV3BrandRadarImpressionsHistoryRequestQuery(StrictModel):
    brand: str = Field(default=..., description="The brand name to track for mentions and impressions.")
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(default=..., description="One or more AI chatbot platforms to query, provided as a comma-separated list. Google models (google_ai_overviews, google_ai_mode) cannot be combined with each other or with non-Google platforms (chatgpt, gemini, perplexity, copilot).")
    date_from: str = Field(default=..., description="The start date for the historical period, formatted as YYYY-MM-DD.", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="The end date for the historical period, formatted as YYYY-MM-DD. If omitted, defaults to the current date.", json_schema_extra={'format': 'date'})
    report_id: str | None = Field(default=None, description="The ID of a saved report to use as a template. When provided, market, country, and filter settings are inherited from the report, though country and filters can be overridden with explicit parameters.")
    prompts: Literal["ahrefs", "custom"] | None = Field(default=None, description="The type of prompts to include in results: 'ahrefs' for Ahrefs-generated prompts, 'custom' for user-defined prompts (requires report_id), or omit to include both types.")
    where: str | None = Field(default=None, description="A filter expression to narrow results. Supports recognized column identifiers for advanced filtering.")
class GetV3BrandRadarImpressionsHistoryRequest(StrictModel):
    """Retrieve historical impression data for brand mentions across AI chatbot platforms. API consumption varies based on prompt type: custom prompts are free, while Ahrefs prompts follow standard pricing."""
    query: GetV3BrandRadarImpressionsHistoryRequestQuery

# Operation: list_brand_mention_history
class GetV3BrandRadarMentionsHistoryRequestQuery(StrictModel):
    brand: str = Field(default=..., description="The brand name to retrieve mention history for.")
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(default=..., description="One or more chatbot models to query, provided as a comma-separated list. Google models (google_ai_overviews, google_ai_mode) cannot be combined with each other or with non-Google models (chatgpt, gemini, perplexity, copilot).")
    date_from: str = Field(default=..., description="The start date for the historical period in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="The end date for the historical period in YYYY-MM-DD format (inclusive). If omitted, defaults to the current date.", json_schema_extra={'format': 'date'})
    prompts: Literal["ahrefs", "custom"] | None = Field(default=None, description="Filter results to a specific prompt type: 'ahrefs' for Ahrefs-generated prompts or 'custom' for user-defined prompts. If not specified, both types are included. Custom prompts require a report_id.")
    report_id: str | None = Field(default=None, description="The Brand Radar report ID to use as a configuration source. When provided, market, country, and filter settings are inherited from the report, though country and filters parameters can override report settings. Find the report ID in your Ahrefs Brand Radar report URL.")
    where: str | None = Field(default=None, description="A filter expression to narrow results by specific columns. Refer to API documentation for recognized column identifiers.")
class GetV3BrandRadarMentionsHistoryRequest(StrictModel):
    """Retrieve historical mention data for a brand across specified AI chatbot models and date range. API consumption varies based on prompt type: custom prompts are free, while Ahrefs prompts follow standard pricing."""
    query: GetV3BrandRadarMentionsHistoryRequestQuery

# Operation: list_brand_sov_history
class GetV3BrandRadarSovHistoryRequestQuery(StrictModel):
    date_from: str = Field(default=..., description="Start date for the historical period in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="End date for the historical period in YYYY-MM-DD format. If omitted, defaults to the current date.", json_schema_extra={'format': 'date'})
    data_source: Literal["google_ai_overviews", "google_ai_mode", "chatgpt", "gemini", "perplexity", "copilot"] = Field(default=..., description="Comma-separated list of chatbot models to analyze (google_ai_overviews, google_ai_mode, chatgpt, gemini, perplexity, or copilot). Google models cannot be combined with each other or with non-Google models.")
    where: str | None = Field(default=None, description="Optional filter expression to narrow results based on specific column identifiers.")
    report_id: str | None = Field(default=None, description="ID of an existing Brand Radar report to use as a template. When provided, brand, competitors, market, and country settings are inherited from the report, though country and filters parameters can override report settings.")
    prompts: Literal["ahrefs", "custom"] | None = Field(default=None, description="Type of prompts to include in results: 'ahrefs' for Ahrefs-generated prompts, 'custom' for user-defined prompts (requires report_id), or omit to include both types.")
class GetV3BrandRadarSovHistoryRequest(StrictModel):
    """Retrieve historical Share of Voice data for brands across specified chatbot models and date ranges. API unit consumption depends on prompt type: custom prompts only are free, while Ahrefs prompts follow standard pricing."""
    query: GetV3BrandRadarSovHistoryRequestQuery

# Operation: list_web_analytics_stats
class GetV3WebAnalyticsStatsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve analytics statistics.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the analytics query, specified in ISO 8601 format. If omitted, defaults to the earliest available data.")
    to: str | None = Field(default=None, description="End of the date range for the analytics query, specified in ISO 8601 format. If omitted, defaults to the current date.")
    where: str | None = Field(default=None, description="Filter expression to narrow results by dimensions and metrics. Use standard filter syntax to specify conditions on available dimensions and metrics.")
    order_by: str | None = Field(default=None, description="Sort results by a metric in ascending or descending order, specified as metric_name:asc or metric_name:desc.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Useful for pagination and controlling response size.")
class GetV3WebAnalyticsStatsRequest(StrictModel):
    """Retrieve aggregated web analytics statistics for a project, with optional filtering, sorting, and date range constraints."""
    query: GetV3WebAnalyticsStatsRequestQuery

# Operation: get_web_analytics_chart
class GetV3WebAnalyticsChartRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose analytics data you want to retrieve.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval for aggregating data points. Choose from hourly, daily, weekly, or monthly granularity depending on the level of detail needed.")
    where: str | None = Field(default=None, description="Optional filter expression to narrow results by specific dimensions and metrics. Use standard filter syntax to refine the data returned.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Optional start datetime for the query range. Specify in ISO 8601 format to define when the data collection period begins.")
    to: str | None = Field(default=None, description="Optional end datetime for the query range. Specify in ISO 8601 format to define when the data collection period ends.")
class GetV3WebAnalyticsChartRequest(StrictModel):
    """Retrieve time-series chart data for web analytics metrics with configurable time granularity. Use this to visualize analytics trends across different time periods."""
    query: GetV3WebAnalyticsChartRequestQuery

# Operation: list_source_channels
class GetV3WebAnalyticsSourceChannelsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose source channel analytics you want to retrieve.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response.")
    order_by: str | None = Field(default=None, description="Sort results by a metric in ascending or descending order. Supported metrics include visitors, session_bounce_rate, and avg_session_duration_sec.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference dimensions and metrics to narrow down the data returned.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format.")
    to: str | None = Field(default=None, description="End of the date range for the analytics query in ISO 8601 datetime format.")
class GetV3WebAnalyticsSourceChannelsRequest(StrictModel):
    """Retrieve web analytics data grouped by source channels, including visitor counts, bounce rates, and session duration metrics. This endpoint is free and does not consume API units."""
    query: GetV3WebAnalyticsSourceChannelsRequestQuery

# Operation: get_source_channels_chart
class GetV3WebAnalyticsSourceChannelsChartRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose analytics data should be retrieved.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval for aggregating data points in the chart. Choose from hourly, daily, weekly, or monthly granularity.")
    source_channels_to_chart: str | None = Field(default=None, description="Comma-separated list of source channels to include in the chart. If not specified, defaults to the top 5 channels by visitor count.")
    where: str | None = Field(default=None, description="Filter expression to narrow results by dimensions and metrics. Use standard filter syntax to refine the dataset.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the data query range. Use ISO 8601 format to define the beginning of the analysis period.")
    to: str | None = Field(default=None, description="End datetime for the data query range. Use ISO 8601 format to define the end of the analysis period.")
class GetV3WebAnalyticsSourceChannelsChartRequest(StrictModel):
    """Retrieve source channels chart data with visitor analytics and session metrics, aggregated at the specified time granularity."""
    query: GetV3WebAnalyticsSourceChannelsChartRequestQuery

# Operation: list_traffic_sources
class GetV3WebAnalyticsSourcesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project to retrieve traffic sources for.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response.")
    order_by: str | None = Field(default=None, description="Sort results by a specific metric in ascending or descending order using the format metric:asc or metric:desc.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference available dimensions and metrics to narrow down the data.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the query in ISO 8601 datetime format.")
    to: str | None = Field(default=None, description="End of the date range for the query in ISO 8601 datetime format.")
class GetV3WebAnalyticsSourcesRequest(StrictModel):
    """Retrieve traffic sources data for a project, showing where visitors are coming from. Results can be filtered by date range and custom criteria, with optional sorting and pagination."""
    query: GetV3WebAnalyticsSourcesRequestQuery

# Operation: get_traffic_sources_chart
class GetV3WebAnalyticsSourcesChartRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose traffic sources you want to analyze.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval for grouping data points in the chart. Choose from hourly, daily, weekly, or monthly granularity.")
    sources_to_chart: str | None = Field(default=None, description="Comma-separated list of traffic sources to include in the chart. If not specified, the top 5 sources by visitor count are displayed by default.")
    where: str | None = Field(default=None, description="Optional filter expression to narrow results by dimensions and metrics relevant to your traffic sources data.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the data query range in ISO 8601 format. If omitted, data retrieval begins from the earliest available records.")
    to: str | None = Field(default=None, description="End datetime for the data query range in ISO 8601 format. If omitted, data retrieval extends to the most recent available records.")
class GetV3WebAnalyticsSourcesChartRequest(StrictModel):
    """Retrieve traffic sources chart data with visitor metrics aggregated by your specified time granularity (hourly, daily, weekly, or monthly). This endpoint is free to use and does not consume API units."""
    query: GetV3WebAnalyticsSourcesChartRequestQuery

# Operation: list_referrers
class GetV3WebAnalyticsReferrersRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve referrer analytics.")
    limit: int | None = Field(default=None, description="Maximum number of referrer records to return in the response.")
    order_by: str | None = Field(default=None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`.")
    where: str | None = Field(default=None, description="Filter results using a filter expression that can reference available dimensions and metrics to narrow down referrer data.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format.")
    to: str | None = Field(default=None, description="End of the date range for the analytics query in ISO 8601 datetime format.")
class GetV3WebAnalyticsReferrersRequest(StrictModel):
    """Retrieve referrer traffic sources and their associated metrics for a project, with optional filtering, sorting, and date range selection."""
    query: GetV3WebAnalyticsReferrersRequestQuery

# Operation: get_referrers_chart
class GetV3WebAnalyticsReferrersChartRequestQuery(StrictModel):
    source_referers_to_chart: str | None = Field(default=None, description="Comma-separated list of referrer values to include in the chart. If not specified, defaults to the top 5 referrers by visitor count.")
    where: str | None = Field(default=None, description="Filter expression to narrow results by dimensions and metrics. Use standard filter syntax to refine the data returned.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="Time granularity for data points in the chart. Choose from hourly, daily, weekly, or monthly intervals.")
    to: str | None = Field(default=None, description="End datetime for the data query range. Use ISO 8601 format for the timestamp.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the data query range. Use ISO 8601 format for the timestamp.")
    project_id: int = Field(default=..., description="The unique identifier for the project whose referrers data should be retrieved.")
class GetV3WebAnalyticsReferrersChartRequest(StrictModel):
    """Retrieve referrers chart data for web analytics, showing traffic sources over a specified time period with configurable granularity and filtering options."""
    query: GetV3WebAnalyticsReferrersChartRequestQuery

# Operation: list_utm_parameters
class GetV3WebAnalyticsUtmParamsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response.")
    order_by: str | None = Field(default=None, description="Sort results by a metric in ascending or descending order using the format metric:asc or metric:desc.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference available dimensions and metrics.")
    to: str | None = Field(default=None, description="End datetime for the data query range in ISO 8601 format.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the data query range in ISO 8601 format.")
    utm_param: Literal["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"] = Field(default=..., description="The UTM parameter to use as the grouping dimension. Choose from: utm_source, utm_medium, utm_campaign, utm_term, or utm_content.")
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve UTM parameter analytics.")
class GetV3WebAnalyticsUtmParamsRequest(StrictModel):
    """Retrieve UTM parameter data for web analytics, grouped by a specified UTM dimension (source, medium, campaign, term, or content) with optional filtering and time range selection."""
    query: GetV3WebAnalyticsUtmParamsRequestQuery

# Operation: get_utm_params_chart
class GetV3WebAnalyticsUtmParamsChartRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose analytics data you want to retrieve.")
    utm_param: Literal["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"] = Field(default=..., description="The UTM parameter to use as the primary dimension for the chart. Choose from: utm_source, utm_medium, utm_campaign, utm_term, or utm_content.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval for data aggregation in the chart. Choose from: hourly, daily, weekly, or monthly granularity.")
    utm_params_to_chart: str | None = Field(default=None, description="Optional comma-separated list of specific UTM parameter values to include in the chart. If omitted, the top 5 values by visitor count are displayed by default.")
    where: str | None = Field(default=None, description="Optional filter expression to refine the data. You can reference available dimensions and metrics to narrow results based on specific criteria.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Optional start datetime for the data query range. Use ISO 8601 format to define when the analytics period begins.")
    to: str | None = Field(default=None, description="Optional end datetime for the data query range. Use ISO 8601 format to define when the analytics period ends.")
class GetV3WebAnalyticsUtmParamsChartRequest(StrictModel):
    """Retrieve UTM parameters chart data for web analytics, visualizing traffic patterns across a specified UTM dimension over time. Use this to analyze campaign performance, traffic sources, or other UTM-tracked metrics."""
    query: GetV3WebAnalyticsUtmParamsChartRequestQuery

# Operation: list_entry_pages
class GetV3WebAnalyticsEntryPagesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose entry pages data should be retrieved.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Useful for pagination and controlling response size.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for analytics data in ISO 8601 format. Only data from this datetime onward will be included.")
    to: str | None = Field(default=None, description="End of the date range for analytics data in ISO 8601 format. Only data up to this datetime will be included.")
    order_by: str | None = Field(default=None, description="Order by metric, as `metric:desc` or `metric:asc`. The following metrics are supported: entry_page, visitors, entries, avg_session_duration_sec")
    where: str | None = Field(default=None, description="Filter expression. Can mention dimensions and metrics.")
class GetV3WebAnalyticsEntryPagesRequest(StrictModel):
    """Retrieve entry pages analytics data for a project, showing which pages users first land on. Supports filtering by date range and result limits."""
    query: GetV3WebAnalyticsEntryPagesRequestQuery

# Operation: get_entry_pages_chart
class GetV3WebAnalyticsEntryPagesChartRequestQuery(StrictModel):
    entry_pages_to_chart: str | None = Field(default=None, description="Specify which entry page metrics to display on the chart as a comma-separated list. Defaults to the top 5 pages by visitor count if not provided.")
    where: str | None = Field(default=None, description="Apply filters to the data using dimension and metric expressions to narrow results to specific criteria.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="Set the time interval for data points on the chart: hourly, daily, weekly, or monthly granularity.")
    to: str | None = Field(default=None, description="End datetime for the data query range in ISO 8601 format.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the data query range in ISO 8601 format.")
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve entry pages chart data.")
class GetV3WebAnalyticsEntryPagesChartRequest(StrictModel):
    """Retrieve entry pages chart data for a project, showing visitor traffic patterns across specified time periods. This endpoint is free and does not consume API units."""
    query: GetV3WebAnalyticsEntryPagesChartRequestQuery

# Operation: list_exit_pages
class GetV3WebAnalyticsExitPagesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project to retrieve exit pages data for.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response.")
    order_by: str | None = Field(default=None, description="Sort results by a metric in ascending or descending order using the format `metric:asc` or `metric:desc`.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference available dimensions and metrics to narrow down the data.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the query in ISO 8601 datetime format.")
    to: str | None = Field(default=None, description="End of the date range for the query in ISO 8601 datetime format.")
class GetV3WebAnalyticsExitPagesRequest(StrictModel):
    """Retrieve exit pages analytics data for a project, showing which pages users exit from most frequently. Supports filtering, sorting, and date range specification."""
    query: GetV3WebAnalyticsExitPagesRequestQuery

# Operation: get_exit_pages_chart
class GetV3WebAnalyticsExitPagesChartRequestQuery(StrictModel):
    exit_pages_to_chart: str | None = Field(default=None, description="Specify which exit page metrics to display on the chart as a comma-separated list. If not provided, defaults to the top 5 pages by visitor count.")
    where: str | None = Field(default=None, description="Filter the data using expressions that reference available dimensions and metrics to narrow results.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="Time granularity for aggregating chart data points. Choose from hourly, daily, weekly, or monthly intervals.")
    to: str | None = Field(default=None, description="End datetime for the data query range. Use ISO 8601 format.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the data query range. Use ISO 8601 format.")
    project_id: int = Field(default=..., description="The unique identifier of the project to retrieve exit pages data for.")
class GetV3WebAnalyticsExitPagesChartRequest(StrictModel):
    """Retrieve exit pages chart data for a project, showing which pages visitors exit from. Supports filtering, time-based aggregation, and customizable metrics selection."""
    query: GetV3WebAnalyticsExitPagesChartRequestQuery

# Operation: list_top_pages_by_pageviews
class GetV3WebAnalyticsTopPagesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose page analytics you want to retrieve.")
    limit: int | None = Field(default=None, description="Maximum number of top pages to return in the results. Defaults to a system-defined limit if not specified.")
    order_by: str | None = Field(default=None, description="Sort results by a specific metric in ascending or descending order. Supported metrics include pageviews, visitors, session_bounce_rate, and avg_page_visit_duration_sec. Use the format metric:asc or metric:desc.")
    where: str | None = Field(default=None, description="Apply filters to narrow results by dimensions and metrics. Specify filter conditions to focus on specific pages or traffic characteristics.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the analytics query. Specify as an ISO 8601 formatted datetime.")
    to: str | None = Field(default=None, description="End of the date range for the analytics query. Specify as an ISO 8601 formatted datetime.")
class GetV3WebAnalyticsTopPagesRequest(StrictModel):
    """Retrieve the top-performing pages for a project ranked by pageviews and other engagement metrics. Use filtering and date range parameters to analyze specific traffic patterns and time periods."""
    query: GetV3WebAnalyticsTopPagesRequestQuery

# Operation: get_top_pages_chart
class GetV3WebAnalyticsTopPagesChartRequestQuery(StrictModel):
    pages_to_chart: str | None = Field(default=None, description="Comma-separated list of values to display on the chart. If not specified, defaults to the top 5 pages by visitor count.")
    where: str | None = Field(default=None, description="Filter expression to narrow results by dimensions and metrics (e.g., country, device type, traffic source).")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="Time granularity for data aggregation: hourly, daily, weekly, or monthly.")
    to: str | None = Field(default=None, description="End datetime for the data query range in ISO 8601 format.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the data query range in ISO 8601 format.")
    project_id: int = Field(default=..., description="The numeric identifier of the project to retrieve analytics for.")
class GetV3WebAnalyticsTopPagesChartRequest(StrictModel):
    """Retrieve a chart of your top-performing pages with visitor metrics and engagement statistics, aggregated at your specified time granularity."""
    query: GetV3WebAnalyticsTopPagesChartRequestQuery

# Operation: list_web_analytics_by_city
class GetV3WebAnalyticsCitiesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve city-level analytics data.")
    limit: int | None = Field(default=None, description="Maximum number of city results to return in the response. If not specified, a default limit applies.")
    order_by: str | None = Field(default=None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference available dimensions and metrics. Allows narrowing data to specific criteria.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format. Data returned will be from this point forward.")
    to: str | None = Field(default=None, description="End of the date range for the analytics query in ISO 8601 datetime format. Data returned will be up to this point.")
class GetV3WebAnalyticsCitiesRequest(StrictModel):
    """Retrieve web analytics metrics aggregated by city for a specified project. This endpoint is free to use and does not consume API units."""
    query: GetV3WebAnalyticsCitiesRequestQuery

# Operation: get_web_analytics_cities_chart
class GetV3WebAnalyticsCitiesChartRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose analytics data you want to retrieve.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval for data aggregation. Choose from hourly, daily, weekly, or monthly granularity to control the resolution of your chart data points.")
    cities_to_chart: str | None = Field(default=None, description="Comma-separated list of specific cities to include in the chart. If not specified, the top 5 cities by visitor count are displayed by default.")
    where: str | None = Field(default=None, description="Optional filter expression to narrow results based on dimensions and metrics. Use this to segment data by specific criteria.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="The start datetime for the data query range. Use ISO 8601 format to specify when the analytics period begins.")
    to: str | None = Field(default=None, description="The end datetime for the data query range. Use ISO 8601 format to specify when the analytics period ends.")
class GetV3WebAnalyticsCitiesChartRequest(StrictModel):
    """Retrieve cities chart data for web analytics showing visitor distribution across geographic locations. This endpoint is free to use and does not consume API units."""
    query: GetV3WebAnalyticsCitiesChartRequestQuery

# Operation: list_continent_analytics
class GetV3WebAnalyticsContinentsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose analytics data you want to retrieve.")
    limit: int | None = Field(default=None, description="Maximum number of continent records to return in the response.")
    order_by: str | None = Field(default=None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference available dimensions and metrics to narrow down the data returned.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format.")
    to: str | None = Field(default=None, description="End of the date range for the analytics query in ISO 8601 datetime format.")
class GetV3WebAnalyticsContinentsRequest(StrictModel):
    """Retrieve web analytics metrics aggregated by continent for a specified project and time period. This endpoint is free to use and does not consume API units."""
    query: GetV3WebAnalyticsContinentsRequestQuery

# Operation: get_continents_chart
class GetV3WebAnalyticsContinentsChartRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose analytics data you want to retrieve.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval for data aggregation. Choose from hourly, daily, weekly, or monthly granularity.")
    continents_to_chart: str | None = Field(default=None, description="Comma-separated list of continents to include in the chart. If not specified, the top 5 continents by visitor count are displayed by default.")
    where: str | None = Field(default=None, description="Filter expression to narrow results based on dimensions and metrics. Use standard filter syntax to refine the data.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the query in ISO 8601 format. Data will be included from this datetime onwards.")
    to: str | None = Field(default=None, description="End of the date range for the query in ISO 8601 format. Data will be included up to this datetime.")
class GetV3WebAnalyticsContinentsChartRequest(StrictModel):
    """Retrieve web analytics chart data aggregated by continent. This endpoint is free to use and does not consume API units."""
    query: GetV3WebAnalyticsContinentsChartRequestQuery

# Operation: list_web_analytics_by_country
class GetV3WebAnalyticsCountriesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of country records to return in the response. Use this to paginate through large result sets.")
    order_by: str | None = Field(default=None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference available dimensions and metrics. Enables targeted analysis of specific geographic or performance segments.")
    to: str | None = Field(default=None, description="End datetime for the analytics query range in ISO 8601 format. Data will be included up to this point in time.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the analytics query range in ISO 8601 format. Data will be included from this point forward.")
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve country-level web analytics data.")
class GetV3WebAnalyticsCountriesRequest(StrictModel):
    """Retrieve web analytics metrics aggregated by country for a specified project and time period. Results can be filtered, sorted, and paginated to analyze geographic performance data."""
    query: GetV3WebAnalyticsCountriesRequestQuery

# Operation: get_countries_chart
class GetV3WebAnalyticsCountriesChartRequestQuery(StrictModel):
    countries_to_chart: str | None = Field(default=None, description="Comma-separated list of countries to include in the chart. If not specified, defaults to the top 5 countries by visitor count.")
    where: str | None = Field(default=None, description="Filter expression to narrow results by dimensions and metrics (e.g., visitor count thresholds, traffic source).")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="Time granularity for data points: hourly, daily, weekly, or monthly aggregation.")
    to: str | None = Field(default=None, description="End datetime for the query range in ISO 8601 format. If omitted, defaults to the current time.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the query range in ISO 8601 format. If omitted, defaults to a standard lookback period.")
    project_id: int = Field(default=..., description="The numeric identifier of the project to retrieve analytics for.")
class GetV3WebAnalyticsCountriesChartRequest(StrictModel):
    """Retrieve web analytics chart data aggregated by country with configurable time granularity and filtering. This endpoint is free and does not consume API units."""
    query: GetV3WebAnalyticsCountriesChartRequestQuery

# Operation: list_language_analytics
class GetV3WebAnalyticsLanguagesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve language analytics data.")
    limit: int | None = Field(default=None, description="Maximum number of language records to return in the response. Useful for pagination or limiting result set size.")
    order_by: str | None = Field(default=None, description="Sort results by a specific metric in ascending or descending order using the format metric:asc or metric:desc.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference available dimensions and metrics to narrow down the dataset.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format. Data returned will be from this point forward.")
    to: str | None = Field(default=None, description="End of the date range for the analytics query in ISO 8601 datetime format. Data returned will be up to this point.")
class GetV3WebAnalyticsLanguagesRequest(StrictModel):
    """Retrieve browser language statistics for a project, showing how visitors are distributed across different language preferences. This endpoint is free to use and does not consume API units."""
    query: GetV3WebAnalyticsLanguagesRequestQuery

# Operation: get_language_analytics_chart
class GetV3WebAnalyticsLanguagesChartRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose language analytics data should be retrieved.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval for aggregating data points in the chart. Choose from hourly, daily, weekly, or monthly granularity.")
    browser_language_to_chart: str | None = Field(default=None, description="Comma-separated list of browser languages to include in the chart. If not specified, the top 5 languages by visitor count are displayed by default.")
    where: str | None = Field(default=None, description="Optional filter expression to narrow results based on dimensions and metrics available in the analytics dataset.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the analytics query range in ISO 8601 format. If omitted, defaults to an appropriate historical starting point.")
    to: str | None = Field(default=None, description="End datetime for the analytics query range in ISO 8601 format. If omitted, defaults to the current time.")
class GetV3WebAnalyticsLanguagesChartRequest(StrictModel):
    """Retrieve browser language distribution data for web analytics with support for time-series charting across different granularities. This endpoint is free to use and does not consume API units."""
    query: GetV3WebAnalyticsLanguagesChartRequestQuery

# Operation: list_browser_analytics
class GetV3WebAnalyticsBrowsersRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve browser analytics data.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response.")
    order_by: str | None = Field(default=None, description="Sort results by a specific metric in ascending or descending order. Supported metrics include browser name, visitor count, session bounce rate, and average session duration in seconds.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference dimensions (such as browser) and metrics (such as visitors or bounce rate).")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format.", json_schema_extra={'format': 'date-time'})
    to: str | None = Field(default=None, description="End of the date range for the analytics query in ISO 8601 datetime format.", json_schema_extra={'format': 'date-time'})
class GetV3WebAnalyticsBrowsersRequest(StrictModel):
    """Retrieve browser analytics data for a project, including visitor counts, bounce rates, and session duration metrics. This endpoint is free and does not consume API units."""
    query: GetV3WebAnalyticsBrowsersRequestQuery

# Operation: get_browser_chart
class GetV3WebAnalyticsBrowsersChartRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve browser analytics data.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="The time interval for aggregating data points in the chart. Choose from hourly, daily, weekly, or monthly granularity.")
    browser_to_chart: str | None = Field(default=None, description="Comma-separated list of browsers to include in the chart. If not specified, the top 5 browsers by visitor count are displayed by default.")
    where: str | None = Field(default=None, description="Filter expression to narrow results based on dimensions and metrics. Use this to segment data by specific criteria.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the data query range. Use ISO 8601 format to define when the analytics period begins.")
    to: str | None = Field(default=None, description="End datetime for the data query range. Use ISO 8601 format to define when the analytics period ends.")
class GetV3WebAnalyticsBrowsersChartRequest(StrictModel):
    """Retrieve browser usage chart data for a project, showing visitor distribution across different browsers over a specified time period with configurable granularity."""
    query: GetV3WebAnalyticsBrowsersChartRequestQuery

# Operation: list_browser_versions
class GetV3WebAnalyticsBrowserVersionsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose browser version data you want to retrieve.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. If not specified, a default limit applies.")
    order_by: str | None = Field(default=None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference available dimensions and metrics. Allows you to narrow down the data returned.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the query in ISO 8601 datetime format. Data returned will be from this point forward.")
    to: str | None = Field(default=None, description="End of the date range for the query in ISO 8601 datetime format. Data returned will be up to this point.")
class GetV3WebAnalyticsBrowserVersionsRequest(StrictModel):
    """Retrieve browser version statistics and metrics for web analytics. This endpoint is free to use and does not consume API units."""
    query: GetV3WebAnalyticsBrowserVersionsRequestQuery

# Operation: get_browser_versions_chart
class GetV3WebAnalyticsBrowserVersionsChartRequestQuery(StrictModel):
    browser_version_to_chart: str | None = Field(default=None, description="Comma-separated list of browser versions to include in the chart. If not specified, defaults to the top 5 browser versions by visitor count.")
    where: str | None = Field(default=None, description="Filter expression to narrow results by dimensions and metrics (e.g., country, device type, traffic source).")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="Time interval for chart data points. Choose from hourly, daily, weekly, or monthly granularity.")
    to: str | None = Field(default=None, description="End date and time for the data query in ISO 8601 format. If omitted, defaults to the current time.", json_schema_extra={'format': 'date-time'})
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start date and time for the data query in ISO 8601 format. If omitted, defaults to a standard lookback period.", json_schema_extra={'format': 'date-time'})
    project_id: int = Field(default=..., description="The unique identifier of the project to retrieve analytics data for.")
class GetV3WebAnalyticsBrowserVersionsChartRequest(StrictModel):
    """Retrieve a chart of browser version performance metrics including visitor counts and session statistics over a specified time period."""
    query: GetV3WebAnalyticsBrowserVersionsChartRequestQuery

# Operation: list_device_analytics
class GetV3WebAnalyticsDevicesRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve device analytics.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response.")
    order_by: str | None = Field(default=None, description="Sort results by a specific metric in ascending or descending order using the format `metric:asc` or `metric:desc`.")
    where: str | None = Field(default=None, description="Filter results using a filter expression that can reference available dimensions and metrics to narrow the dataset.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the time range for the query in ISO 8601 datetime format (inclusive).")
    to: str | None = Field(default=None, description="End of the time range for the query in ISO 8601 datetime format (inclusive).")
class GetV3WebAnalyticsDevicesRequest(StrictModel):
    """Retrieve device analytics data for a project, including metrics such as user counts, sessions, and engagement by device type. Results can be filtered, sorted, and scoped to a specific time range."""
    query: GetV3WebAnalyticsDevicesRequestQuery

# Operation: get_devices_chart
class GetV3WebAnalyticsDevicesChartRequestQuery(StrictModel):
    devices_to_chart: str | None = Field(default=None, description="Comma-separated list of device values to include in the chart. If not specified, defaults to the top 5 devices by visitor count.")
    where: str | None = Field(default=None, description="Filter expression to narrow results by dimensions and metrics (e.g., country, device type, visitor segment).")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="Time granularity for data aggregation. Choose from hourly, daily, weekly, or monthly intervals.")
    to: str | None = Field(default=None, description="End datetime for the data query range. Use ISO 8601 format.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the data query range. Use ISO 8601 format.")
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve device analytics.")
class GetV3WebAnalyticsDevicesChartRequest(StrictModel):
    """Retrieve device analytics chart data showing visitor distribution across different devices over a specified time period. This endpoint is free and does not consume API units."""
    query: GetV3WebAnalyticsDevicesChartRequestQuery

# Operation: list_operating_systems_analytics
class GetV3WebAnalyticsOperatingSystemsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier for the project whose operating system analytics you want to retrieve.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Useful for pagination and controlling response size.")
    order_by: str | None = Field(default=None, description="Sort results by a specific metric in ascending or descending order. Available metrics include visitors, session_bounce_rate, and avg_session_duration_sec.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference dimensions and metrics. Allows you to narrow down data based on specific criteria.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the analytics query in ISO 8601 datetime format. Data returned will include this date and time onward.")
    to: str | None = Field(default=None, description="End of the date range for the analytics query in ISO 8601 datetime format. Data returned will include results up to this date and time.")
class GetV3WebAnalyticsOperatingSystemsRequest(StrictModel):
    """Retrieve analytics data for operating systems across your project. This endpoint provides insights into visitor behavior by operating system and is available at no cost."""
    query: GetV3WebAnalyticsOperatingSystemsRequestQuery

# Operation: get_operating_systems_chart
class GetV3WebAnalyticsOperatingSystemsChartRequestQuery(StrictModel):
    os_to_chart: str | None = Field(default=None, description="Specify which operating systems to include in the chart as a comma-separated list. If not provided, defaults to the top 5 operating systems by visitor count.")
    where: str | None = Field(default=None, description="Filter the data using expressions that reference available dimensions and metrics to narrow results to specific criteria.")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="Time granularity for data points in the chart. Choose from hourly, daily, weekly, or monthly intervals.")
    to: str | None = Field(default=None, description="End datetime for the data query range. Use ISO 8601 format.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the data query range. Use ISO 8601 format.")
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve operating systems chart data.")
class GetV3WebAnalyticsOperatingSystemsChartRequest(StrictModel):
    """Retrieve operating systems chart data for web analytics across a specified time period and granularity. This endpoint is free to use and does not consume API units."""
    query: GetV3WebAnalyticsOperatingSystemsChartRequestQuery

# Operation: list_operating_system_versions
class GetV3WebAnalyticsOperatingSystemsVersionsRequestQuery(StrictModel):
    project_id: int = Field(default=..., description="The unique identifier of the project for which to retrieve operating system versions data.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response.")
    order_by: str | None = Field(default=None, description="Sort results by a metric in ascending or descending order using the format metric:asc or metric:desc.")
    where: str | None = Field(default=None, description="Filter results using expressions that reference available dimensions and metrics to narrow the dataset.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start of the date range for the query in ISO 8601 datetime format.")
    to: str | None = Field(default=None, description="End of the date range for the query in ISO 8601 datetime format.")
class GetV3WebAnalyticsOperatingSystemsVersionsRequest(StrictModel):
    """Retrieve operating system versions analytics data for a specified project, with optional filtering, sorting, and date range selection."""
    query: GetV3WebAnalyticsOperatingSystemsVersionsRequestQuery

# Operation: get_operating_system_versions_chart
class GetV3WebAnalyticsOperatingSystemsVersionsChartRequestQuery(StrictModel):
    os_versions_to_chart: str | None = Field(default=None, description="Comma-separated list of operating system versions to include in the chart. If not specified, defaults to the top 5 versions by visitor count.")
    where: str | None = Field(default=None, description="Filter expression to narrow results by dimensions and metrics (e.g., country, device type, engagement thresholds).")
    granularity: Literal["hourly", "daily", "weekly", "monthly"] = Field(default=..., description="Time interval for aggregating data points in the chart. Choose from hourly, daily, weekly, or monthly granularity.")
    to: str | None = Field(default=None, description="End datetime for the data query range in ISO 8601 format.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="Start datetime for the data query range in ISO 8601 format.")
    project_id: int = Field(default=..., description="Unique identifier of the project to retrieve analytics data for.")
class GetV3WebAnalyticsOperatingSystemsVersionsChartRequest(StrictModel):
    """Retrieve a time-series chart of visitor counts and engagement metrics broken down by operating system versions. Data can be filtered, aggregated at different time intervals, and limited to specific OS versions."""
    query: GetV3WebAnalyticsOperatingSystemsVersionsChartRequestQuery

# Operation: get_search_performance_history
class GetV3GscPerformanceHistoryRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter results by specific fields using supported filter expressions to narrow down the performance data returned.")
    device: Literal["desktop", "mobile", "tablet"] | None = Field(default=None, description="Limit results to a specific device type: desktop, mobile, or tablet.")
    search_type: Literal["web", "image", "video", "news"] | None = Field(default=None, description="Specify the search result category to analyze: web, image, video, or news. Defaults to web search results.")
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="Choose the time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly grouping.")
    date_to: str | None = Field(default=None, description="The end date for the historical period in YYYY-MM-DD format. If not specified, defaults to the current date.", json_schema_extra={'format': 'date'})
    date_from: str = Field(default=..., description="The start date for the historical period in YYYY-MM-DD format. Required to define the beginning of the data range.", json_schema_extra={'format': 'date'})
class GetV3GscPerformanceHistoryRequest(StrictModel):
    """Retrieve Google Search Console performance metrics over a specified historical period, with options to filter by device type, search category, and time interval grouping."""
    query: GetV3GscPerformanceHistoryRequestQuery

# Operation: list_keyword_position_history
class GetV3GscPositionsHistoryRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter conditions to narrow results by specific criteria such as keywords, URLs, or other query parameters.")
    device: Literal["desktop", "mobile", "tablet"] | None = Field(default=None, description="Limit results to a specific device type: desktop, mobile, or tablet.")
    search_type: Literal["web", "image", "video", "news"] | None = Field(default=None, description="Specify the type of search results to analyze: web, image, video, or news. Defaults to web search results.")
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="Set the time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly aggregation.")
    date_to: str | None = Field(default=None, description="The end date for the historical period in YYYY-MM-DD format. If not specified, defaults to the current date.", json_schema_extra={'format': 'date'})
    date_from: str = Field(default=..., description="The start date for the historical period in YYYY-MM-DD format. Required to define the beginning of your analysis window.", json_schema_extra={'format': 'date'})
class GetV3GscPositionsHistoryRequest(StrictModel):
    """Retrieve historical keyword position data for a project, aggregated into position ranges over a specified time period. Use this to analyze ranking trends and performance across different time intervals."""
    query: GetV3GscPositionsHistoryRequestQuery

# Operation: list_page_history_gsc
class GetV3GscPagesHistoryRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter results by supported fields using query syntax to narrow down the page history data returned.")
    device: Literal["desktop", "mobile", "tablet"] | None = Field(default=None, description="Limit results to a specific device type: desktop, mobile, or tablet.")
    search_type: Literal["web", "image", "video", "news"] | None = Field(default=None, description="Specify the search result category to analyze: web, image, video, or news. Defaults to web search results.")
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="Set the time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly grouping.")
    date_to: str | None = Field(default=None, description="The end date for the historical period in YYYY-MM-DD format. If not specified, defaults to the current date.", json_schema_extra={'format': 'date'})
    date_from: str = Field(default=..., description="The start date for the historical period in YYYY-MM-DD format. Required to define the beginning of the data range.", json_schema_extra={'format': 'date'})
class GetV3GscPagesHistoryRequest(StrictModel):
    """Retrieve historical page performance metrics from Google Search Console, including impressions, clicks, and rankings over a specified time period."""
    query: GetV3GscPagesHistoryRequestQuery

# Operation: list_device_performance
class GetV3GscPerformanceByDeviceRequestQuery(StrictModel):
    date_from: str = Field(default=..., description="Start date for the performance data in YYYY-MM-DD format (e.g., 2024-01-01). This is the beginning of the historical period to analyze.", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="End date for the performance data in YYYY-MM-DD format (e.g., 2024-01-31). If not provided, defaults to the current date. Must be on or after the start date.", json_schema_extra={'format': 'date'})
    search_type: Literal["web", "image", "video", "news"] | None = Field(default=None, description="Filter results to a specific search type: web search, image search, video search, or news search. Defaults to web search if not specified.")
    where: str | None = Field(default=None, description="Optional filter expression to narrow results by supported fields (e.g., country, device, query). Use this to segment performance data further.")
class GetV3GscPerformanceByDeviceRequest(StrictModel):
    """Retrieve Google Search Console performance metrics aggregated by device type (desktop, mobile, tablet) for a specified date range."""
    query: GetV3GscPerformanceByDeviceRequestQuery

# Operation: list_gsc_metrics_by_country
class GetV3GscMetricsByCountryRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter results using supported field conditions to narrow down the metrics returned.")
    device: Literal["desktop", "mobile", "tablet"] | None = Field(default=None, description="Filter metrics by device type: desktop, mobile, or tablet.")
    search_type: Literal["web", "image", "video", "news"] | None = Field(default=None, description="Specify the type of search results to include in metrics: web, image, video, or news. Defaults to web search.")
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="Set the time interval for grouping historical data: daily, weekly, or monthly. Defaults to monthly aggregation.")
    date_to: str | None = Field(default=None, description="The end date for the metrics period in YYYY-MM-DD format. If not specified, defaults to the current date.", json_schema_extra={'format': 'date'})
    date_from: str = Field(default=..., description="The start date for the metrics period in YYYY-MM-DD format. Required to define the historical data range.", json_schema_extra={'format': 'date'})
class GetV3GscMetricsByCountryRequest(StrictModel):
    """Retrieve Google Search Console metrics aggregated by country for a specified date range. This endpoint is free to use and does not consume API units."""
    query: GetV3GscMetricsByCountryRequestQuery

# Operation: list_ctr_by_position
class GetV3GscCtrByPositionRequestQuery(StrictModel):
    date_from: str = Field(default=..., description="Start date for the historical period in YYYY-MM-DD format (required).", json_schema_extra={'format': 'date'})
    date_to: str | None = Field(default=None, description="End date for the historical period in YYYY-MM-DD format. If omitted, defaults to the start date.", json_schema_extra={'format': 'date'})
    device: Literal["desktop", "mobile", "tablet"] | None = Field(default=None, description="Filter results by device type: desktop, mobile, or tablet. If omitted, returns metrics across all device types.")
class GetV3GscCtrByPositionRequest(StrictModel):
    """Retrieve click-through rate (CTR) metrics aggregated by search position for a specified date range. This endpoint is free to use and does not consume API units."""
    query: GetV3GscCtrByPositionRequestQuery

# Operation: list_search_performance_by_position
class GetV3GscPerformanceByPositionRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter results using supported field conditions to narrow down the performance data returned.")
    device: Literal["desktop", "mobile", "tablet"] | None = Field(default=None, description="Filter results by device type: desktop, mobile, or tablet.")
    search_type: Literal["web", "image", "video", "news"] | None = Field(default=None, description="Specify the type of search results to analyze: web, image, video, or news. Defaults to web search results.")
    date_to: str | None = Field(default=None, description="The end date for the historical period you want to analyze, specified in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    date_from: str = Field(default=..., description="The start date for the historical period you want to analyze, specified in YYYY-MM-DD format. This parameter is required.", json_schema_extra={'format': 'date'})
class GetV3GscPerformanceByPositionRequest(StrictModel):
    """Retrieve search performance metrics aggregated by search result position. This endpoint provides free access to performance data without consuming API units."""
    query: GetV3GscPerformanceByPositionRequestQuery

# Operation: list_keyword_history_gsc
class GetV3GscKeywordHistoryRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter results by supported fields using query syntax to narrow down keyword history data.")
    device: Literal["desktop", "mobile", "tablet"] | None = Field(default=None, description="Filter results by device type: desktop, mobile, or tablet.")
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="Group historical data by time interval: daily, weekly, or monthly. Defaults to monthly grouping.")
    date_to: str | None = Field(default=None, description="End date for the historical period in YYYY-MM-DD format (inclusive).", json_schema_extra={'format': 'date'})
    date_from: str = Field(default=..., description="Start date for the historical period in YYYY-MM-DD format (inclusive). Required to define the date range for keyword history retrieval.", json_schema_extra={'format': 'date'})
class GetV3GscKeywordHistoryRequest(StrictModel):
    """Retrieve historical Google Search Console keyword performance data with optional filtering by device type, country, and date range. Data can be grouped by daily, weekly, or monthly intervals."""
    query: GetV3GscKeywordHistoryRequestQuery

# Operation: list_gsc_keywords
class GetV3GscKeywordsRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter keywords using a filter expression to narrow results by specific criteria.")
    limit: int | None = Field(default=None, description="Maximum number of keyword results to return in the response. Defaults to 1000 if not specified.")
    device: Literal["desktop", "mobile", "tablet"] | None = Field(default=None, description="Filter results by device type: desktop, mobile, or tablet.")
    search_type: Literal["web", "image", "video", "news"] | None = Field(default=None, description="Type of search results to include: web, image, video, or news. Defaults to web if not specified.")
    date_to: str | None = Field(default=None, description="End date for the historical data range in YYYY-MM-DD format. If not provided, defaults to the current date.", json_schema_extra={'format': 'date'})
    date_from: str = Field(default=..., description="Start date for the historical data range in YYYY-MM-DD format. Required to define the beginning of the analysis period.", json_schema_extra={'format': 'date'})
class GetV3GscKeywordsRequest(StrictModel):
    """Retrieve keywords from Google Search Console data for a specified date range. This operation is free and does not consume API units."""
    query: GetV3GscKeywordsRequestQuery

# Operation: get_page_history
class GetV3GscPageHistoryRequestQuery(StrictModel):
    pages: str | None = Field(default=None, description="Comma-separated list of page URLs to retrieve history data for. If not specified, data for all pages is included.")
    device: Literal["desktop", "mobile", "tablet"] | None = Field(default=None, description="Filter results by device type: desktop, mobile, or tablet. If not specified, data for all device types is included.")
    history_grouping: Literal["daily", "weekly", "monthly"] | None = Field(default=None, description="Time interval for grouping historical data points. Choose from daily, weekly, or monthly granularity. Defaults to monthly if not specified.")
    date_to: str | None = Field(default=None, description="End date for the historical period in YYYY-MM-DD format. If not specified, defaults to the current date.", json_schema_extra={'format': 'date'})
    date_from: str = Field(default=..., description="Start date for the historical period in YYYY-MM-DD format. Required to define the beginning of the data range.", json_schema_extra={'format': 'date'})
class GetV3GscPageHistoryRequest(StrictModel):
    """Retrieve historical performance data for specified pages from Google Search Console, including metrics like clicks, impressions, and average position over a configurable time period."""
    query: GetV3GscPageHistoryRequestQuery

# Operation: list_gsc_pages
class GetV3GscPagesRequestQuery(StrictModel):
    where: str | None = Field(default=None, description="Filter pages by supported field criteria using query syntax to narrow results to specific pages or patterns.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response; defaults to 1000 if not specified.")
    device: Literal["desktop", "mobile", "tablet"] | None = Field(default=None, description="Filter results by device type: desktop, mobile, or tablet.")
    search_type: Literal["web", "image", "video", "news"] | None = Field(default=None, description="Type of search results to include in the data; defaults to web search and supports web, image, video, and news results.")
    date_to: str | None = Field(default=None, description="End date for the historical data range in YYYY-MM-DD format; if omitted, defaults to the current date.", json_schema_extra={'format': 'date'})
    date_from: str = Field(default=..., description="Start date for the historical data range in YYYY-MM-DD format; required to define the beginning of the analysis period.", json_schema_extra={'format': 'date'})
class GetV3GscPagesRequest(StrictModel):
    """Retrieve page performance metrics from Google Search Console, including impressions, clicks, and rankings for specified date ranges and filters."""
    query: GetV3GscPagesRequestQuery

# Operation: list_anonymous_queries
class GetV3GscAnonymousQueriesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response. Defaults to 1000 if not specified.")
    order_by: str | None = Field(default=None, description="Column name to sort results by. Refer to the response schema for valid column identifiers available for ordering.")
    where: str | None = Field(default=None, description="Filter expression to narrow results. Supports filtering by keyword (string) and url (string) columns using standard filter syntax.")
    select: str = Field(default=..., description="Comma-separated list of column names to include in the response. Refer to the response schema for valid column identifiers.")
    country: Literal["ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bn", "bo", "br", "bs", "bt", "bw", "by", "bz", "ca", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "es", "et", "fi", "fj", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gt", "gu", "gy", "hk", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "iq", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "kn", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mk", "ml", "mm", "mn", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pn", "pr", "ps", "pt", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "se", "sg", "sh", "si", "sk", "sl", "sm", "sn", "so", "sr", "st", "sv", "td", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tw", "tz", "ua", "ug", "us", "uy", "uz", "vc", "ve", "vg", "vi", "vn", "vu", "ws", "ye", "yt", "za", "zm", "zw"] = Field(default=..., description="Two-letter country code in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de') to scope results to a specific country.")
    date_from: str = Field(default=..., description="Start date for the historical data range in YYYY-MM-DD format. Results will include data from this date onward.", json_schema_extra={'format': 'date'})
    project_id: int = Field(default=..., description="Unique identifier of the project for which to retrieve anonymous queries.")
class GetV3GscAnonymousQueriesRequest(StrictModel):
    """Retrieve anonymous search queries for a specific project and country. Returns query data filtered by date range with customizable columns, sorting, and filtering options."""
    query: GetV3GscAnonymousQueriesRequestQuery

# ============================================================================
# Component Models
# ============================================================================

class PatchV3ManagementBrandRadarReportsBodyPromptsFrequencyItem(PermissiveModel):
    data_source: Literal["chatgpt", "gemini", "perplexity", "copilot"] = Field(..., description="The data source to use.")
    frequency: Literal["daily", "weekly", "monthly", "off"] = Field(..., description="The update interval to use.")

class PostV3BatchAnalysisBodyTargetsItem(PermissiveModel):
    url: str = Field(..., description="The URL of the analyzed target.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] = Field(..., description="The target mode used for the analysis.")
    protocol: Literal["both", "http", "https"] = Field(..., description="The protocol of the target.")

class PostV3ManagementProjectCompetitorsBodyCompetitorsItem(PermissiveModel):
    url: str = Field(..., description="The URL of the project's target.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] = Field(..., description="The scope of the target. Possible values: exact, prefix, domain, subdomains.")

class PostV3ManagementProjectCompetitorsDeleteBodyCompetitorsItem(PermissiveModel):
    url: str = Field(..., description="The URL of the project's target.")
    mode: Literal["exact", "prefix", "domain", "subdomains"] = Field(..., description="The scope of the target. Possible values: exact, prefix, domain, subdomains.")

class PutV3ManagementProjectKeywordsBodyKeywordsItem(PermissiveModel):
    keyword: str = Field(..., description="The keyword to add")
    tags: list[str] | None = Field(None, description="A list of tags to assign to a given keyword")

class PutV3ManagementProjectKeywordsBodyLocationsItem(PermissiveModel):
    country: str = Field(..., description="The country code")
    language: str | None = Field(None, description="The language code")
    location_id: int | None = Field(None, description="The location ID")

class PutV3ManagementProjectKeywordsDeleteBodyKeywordsItem(PermissiveModel):
    keyword: str = Field(..., description="The keyword to delete.")
    country: str | None = Field(None, description="The country code.")
    language: str | None = Field(None, description="The language code.")
    location_id: int | None = Field(None, description="The location ID.")


# Rebuild models to resolve forward references (required for circular refs)
PatchV3ManagementBrandRadarReportsBodyPromptsFrequencyItem.model_rebuild()
PostV3BatchAnalysisBodyTargetsItem.model_rebuild()
PostV3ManagementProjectCompetitorsBodyCompetitorsItem.model_rebuild()
PostV3ManagementProjectCompetitorsDeleteBodyCompetitorsItem.model_rebuild()
PutV3ManagementProjectKeywordsBodyKeywordsItem.model_rebuild()
PutV3ManagementProjectKeywordsBodyLocationsItem.model_rebuild()
PutV3ManagementProjectKeywordsDeleteBodyKeywordsItem.model_rebuild()

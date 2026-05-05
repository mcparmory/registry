"""
Perigon Api MCP Server - Pydantic Models

Generated: 2026-05-05 15:51:05 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "GetJournalistByIdRequest",
    "GetStoryCountsRequest",
    "GetStoryHistoryRequest",
    "SearchArticlesRequest",
    "SearchCompaniesRequest",
    "SearchJournalistsRequest",
    "SearchPeopleRequest",
    "SearchSourcesRequest",
    "SearchStoriesRequest",
    "SearchSummarizerRequest",
    "SearchTopicsRequest",
    "SearchWikipediaRequest",
    "VectorSearchArticlesRequest",
    "VectorSearchWikipediaRequest",
    "VectorSearchArticlesBodyFilter",
    "VectorSearchWikipediaBodyFilter",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: search_articles
class SearchArticlesRequestQuery(StrictModel):
    title: str | None = Field(default=None, description="Search within article headlines and titles. Supports Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern variations.")
    desc: str | None = Field(default=None, description="Search within article description fields. Supports Boolean expressions, exact phrase matching with quotes, and wildcards for flexible pattern matching.")
    content: str | None = Field(default=None, description="Search within the full article body content. Supports Boolean logic, exact phrase matching with quotes, and wildcards for comprehensive content searching.")
    summary: str | None = Field(default=None, description="Search within article summary fields. Supports Boolean expressions, exact phrase matching with quotes, and wildcards for flexible pattern matching.")
    url: str | None = Field(default=None, description="Search query on the URL field. Useful for filtering articles from specific website sections or domains (e.g., source=cnn.com&url=travel).")
    article_id: list[str] | None = Field(default=None, validation_alias="articleId", serialization_alias="articleId", description="Retrieve specific articles by their unique identifiers. Provide one or more article IDs to return a targeted collection.")
    cluster_id: list[str] | None = Field(default=None, validation_alias="clusterId", serialization_alias="clusterId", description="Filter results to articles within a specific related content cluster. Returns articles grouped together as part of Perigon Stories based on topic relevance.")
    sort_by: Literal["relevance", "date", "reverseDate", "reverseAddDate", "addDate", "pubDate", "refreshDate"] | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="Determines result ordering. Choose from relevance (default), date/pubDate (newest first), reverseDate (oldest first), addDate (newest ingestion first), reverseAddDate (oldest ingestion first), or refreshDate (most recently updated first).")
    page: int | None = Field(default=None, description="The page number of results to retrieve in paginated responses. Starts at 0 and supports up to page 10000.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(default=None, description="Number of articles to return per page. Accepts values from 0 to 1000.", json_schema_extra={'format': 'int32'})
    add_date_from: str | None = Field(default=None, validation_alias="addDateFrom", serialization_alias="addDateFrom", description="Filter for articles added to Perigon's system after this date. Accepts ISO 8601 format (e.g., 2022-02-01T00:00:00) or simple date format (yyyy-mm-dd).", json_schema_extra={'format': 'date-time'})
    add_date_to: str | None = Field(default=None, validation_alias="addDateTo", serialization_alias="addDateTo", description="Filter for articles added to Perigon's system before this date. Accepts ISO 8601 format (e.g., 2022-02-01T23:59:59) or simple date format (yyyy-mm-dd).", json_schema_extra={'format': 'date-time'})
    refresh_date_from: str | None = Field(default=None, validation_alias="refreshDateFrom", serialization_alias="refreshDateFrom", description="Filter for articles refreshed or updated in Perigon's system after this date. May differ from addDateFrom for updated content. Accepts ISO 8601 or simple date format.", json_schema_extra={'format': 'date-time'})
    refresh_date_to: str | None = Field(default=None, validation_alias="refreshDateTo", serialization_alias="refreshDateTo", description="Filter for articles refreshed or updated in Perigon's system before this date. May differ from addDateTo for updated content. Accepts ISO 8601 or simple date format.", json_schema_extra={'format': 'date-time'})
    medium: list[str] | None = Field(default=None, description="Filter by content medium type. Choose Article for written content or Video for video-based stories. Multiple values create an OR filter.")
    source: list[str] | None = Field(default=None, description="Filter by specific publisher domains or subdomains. Supports wildcards (* and ?) for pattern matching (e.g., *.cnn.com). Multiple values create an OR filter.")
    source_group: list[str] | None = Field(default=None, validation_alias="sourceGroup", serialization_alias="sourceGroup", description="Filter using Perigon's curated publisher bundles (e.g., top100, top25crypto). Multiple values create an OR filter to include articles from any specified bundle.")
    exclude_source_group: list[str] | None = Field(default=None, validation_alias="excludeSourceGroup", serialization_alias="excludeSourceGroup", description="Exclude articles from specified Perigon source groups. Multiple values create an AND-exclude filter, removing content from publishers in any specified bundle.")
    exclude_source: list[str] | None = Field(default=None, validation_alias="excludeSource", serialization_alias="excludeSource", description="Exclude articles from specific publisher domains or subdomains. Supports wildcards (* and ?) for pattern matching. Multiple values create an AND-exclude filter.")
    watchlist: list[str] | None = Field(default=None, description="Filter articles using watchlists of people and companies. Multiple values create an OR filter to include articles mentioning any entity from specified watchlists.")
    exclude_watchlist: list[str] | None = Field(default=None, validation_alias="excludeWatchlist", serialization_alias="excludeWatchlist", description="Exclude articles mentioning entities from specified watchlists. Multiple values create an AND-exclude filter, removing content about any entity in the specified watchlists.")
    paywall: bool | None = Field(default=None, description="Filter by paywall status. Set to true to show only paywalled sources, or false to show only free sources.")
    author: list[str] | None = Field(default=None, description="Filter articles by specific author names using exact matching. Multiple values create an OR filter to find articles by any specified author.")
    exclude_author: list[str] | None = Field(default=None, validation_alias="excludeAuthor", serialization_alias="excludeAuthor", description="Exclude articles written by specific authors. Any article with an author name matching an entry will be omitted. Multiple values create an AND-exclude filter.")
    journalist_id: list[str] | None = Field(default=None, validation_alias="journalistId", serialization_alias="journalistId", description="Filter by unique journalist identifiers (available via the Journalist API or matchedAuthors field). Multiple values create an OR filter.")
    exclude_journalist_id: list[str] | None = Field(default=None, validation_alias="excludeJournalistId", serialization_alias="excludeJournalistId", description="Exclude articles written by specific journalists identified by their unique IDs. Multiple values create an AND-exclude filter.")
    language: list[str] | None = Field(default=None, description="Filter articles by language using ISO 639 two-letter codes (e.g., en, es, fr). Multiple values create an OR filter.")
    exclude_language: list[str] | None = Field(default=None, validation_alias="excludeLanguage", serialization_alias="excludeLanguage", description="Exclude articles in specific languages using ISO 639 two-letter codes. Multiple values create an AND-exclude filter.")
    search_translation: bool | None = Field(default=None, validation_alias="searchTranslation", serialization_alias="searchTranslation", description="Expand search to include translated content fields for non-English articles. When enabled, searches translated title, description, and content fields.")
    label: list[str] | None = Field(default=None, description="Filter articles by editorial labels such as Opinion, Paid-news, Non-news, Fact Check, or Press Release. Multiple values create an OR filter.")
    exclude_label: list[str] | None = Field(default=None, validation_alias="excludeLabel", serialization_alias="excludeLabel", description="Exclude articles with specific editorial labels. Multiple values create an AND-exclude filter, removing all content with any specified label.")
    category: list[str] | None = Field(default=None, description="Filter by general article categories (e.g., Tech, Politics). Use 'none' to search uncategorized articles. Multiple values create an OR filter.")
    exclude_category: list[str] | None = Field(default=None, validation_alias="excludeCategory", serialization_alias="excludeCategory", description="Exclude articles with specific categories. Multiple values create an AND-exclude filter, removing all content with any specified category.")
    topic: list[str] | None = Field(default=None, description="Filter by specific topics (e.g., Markets, Crime, Cryptocurrency, College Sports). Topics are more granular than categories and articles can have multiple topics. Multiple values create an OR filter.")
    exclude_topic: list[str] | None = Field(default=None, validation_alias="excludeTopic", serialization_alias="excludeTopic", description="Exclude articles with specific topics. Multiple values create an AND-exclude filter, removing all content with any specified topic.")
    link_to: str | None = Field(default=None, validation_alias="linkTo", serialization_alias="linkTo", description="Returns only articles that contain links to the specified URL pattern. Matches against the links field in article responses.")
    show_reprints: bool | None = Field(default=None, validation_alias="showReprints", serialization_alias="showReprints", description="Controls whether to include reprinted content in results. When true (default), shows syndicated articles from wire services like AP or Reuters that appear on multiple sites.")
    reprint_group_id: str | None = Field(default=None, validation_alias="reprintGroupId", serialization_alias="reprintGroupId", description="Returns all articles in a specific reprint group, including the original article and all known reprints. Use to see all versions of the same content.")
    city: list[str] | None = Field(default=None, description="Filter articles where a specified city plays a central role in the content, beyond mere mentions. Multiple values create an OR filter.")
    exclude_city: list[str] | None = Field(default=None, validation_alias="excludeCity", serialization_alias="excludeCity", description="Exclude articles associated with specified cities. Articles tagged with any specified city will be filtered out.")
    state: list[str] | None = Field(default=None, description="Filter articles where a specified state plays a central role in the content, beyond mere mentions. Multiple values create an OR filter.")
    exclude_state: list[str] | None = Field(default=None, validation_alias="excludeState", serialization_alias="excludeState", description="Exclude articles associated with specified states. Articles tagged with any specified state will be filtered out.")
    county: list[str] | None = Field(default=None, description="Filter articles by specific counties. Only articles tagged with one of these counties will be included.")
    exclude_county: list[str] | None = Field(default=None, validation_alias="excludeCounty", serialization_alias="excludeCounty", description="Exclude articles from specific counties or administrative divisions. County names should match the format used in article metadata (e.g., 'Los Angeles County', 'Cook County').")
    country: list[str] | None = Field(default=None, description="Filter articles by country code. Multiple values create an OR filter.")
    location: list[str] | None = Field(default=None, description="Return articles with specified location attributes. Location format uses ':' between key and value, and '::' between attributes (e.g., 'city:New York::state:NY').")
    lat: float | None = Field(default=None, description="Latitude of the center point for geographic search. Must be between -90 and 90 degrees.", ge=-90, le=90, json_schema_extra={'format': 'double'})
    lon: float | None = Field(default=None, description="Longitude of the center point for geographic search. Must be between -180 and 180 degrees.", ge=-180, le=180, json_schema_extra={'format': 'double'})
    max_distance: float | None = Field(default=None, validation_alias="maxDistance", serialization_alias="maxDistance", description="Maximum distance in kilometers from the center point for geographic search. Must be between 1 and 300 km.", ge=1, le=300, json_schema_extra={'format': 'double'})
    source_city: list[str] | None = Field(default=None, validation_alias="sourceCity", serialization_alias="sourceCity", description="Find articles published by sources located within specified cities.")
    exclude_source_city: list[str] | None = Field(default=None, validation_alias="excludeSourceCity", serialization_alias="excludeSourceCity", description="Exclude articles published by sources located within specified cities.")
    source_county: list[str] | None = Field(default=None, validation_alias="sourceCounty", serialization_alias="sourceCounty", description="Find articles published by sources located within specified counties.")
    exclude_source_county: list[str] | None = Field(default=None, validation_alias="excludeSourceCounty", serialization_alias="excludeSourceCounty", description="Exclude articles published by sources located within specified counties.")
    source_country: list[str] | None = Field(default=None, validation_alias="sourceCountry", serialization_alias="sourceCountry", description="Find articles published by sources located within specified countries. Use 2-character country codes (e.g., us, gb).")
    exclude_source_country: list[str] | None = Field(default=None, validation_alias="excludeSourceCountry", serialization_alias="excludeSourceCountry", description="Exclude articles published by sources located within specified countries. Use 2-character country codes (e.g., us, gb).")
    source_state: list[str] | None = Field(default=None, validation_alias="sourceState", serialization_alias="sourceState", description="Find articles published by sources located within specified states.")
    exclude_source_state: list[str] | None = Field(default=None, validation_alias="excludeSourceState", serialization_alias="excludeSourceState", description="Exclude articles published by sources located within specified states.")
    person_wikidata_id: list[str] | None = Field(default=None, validation_alias="personWikidataId", serialization_alias="personWikidataId", description="Filter articles by Wikidata IDs of mentioned people. Refer to the /people endpoint for available tracked individuals. Multiple values create an OR filter.")
    exclude_person_wikidata_id: list[str] | None = Field(default=None, validation_alias="excludePersonWikidataId", serialization_alias="excludePersonWikidataId", description="Exclude articles mentioning people with specific Wikidata IDs. Uses precise identifiers to avoid name ambiguity. Multiple values create an AND-exclude filter.")
    exclude_person_name: list[str] | None = Field(default=None, validation_alias="excludePersonName", serialization_alias="excludePersonName", description="Exclude articles mentioning specific people by name. Multiple values create an AND-exclude filter.")
    company_id: list[str] | None = Field(default=None, validation_alias="companyId", serialization_alias="companyId", description="Filter articles by company identifiers. Refer to the /companies endpoint for available tracked companies. Multiple values create an OR filter.")
    exclude_company_id: list[str] | None = Field(default=None, validation_alias="excludeCompanyId", serialization_alias="excludeCompanyId", description="Exclude articles mentioning companies with specific identifiers. Multiple values create an AND-exclude filter.")
    company_domain: list[str] | None = Field(default=None, validation_alias="companyDomain", serialization_alias="companyDomain", description="Filter articles by company domains (e.g., apple.com). Consult the /companies endpoint for available company entities. Multiple values create an OR filter.")
    exclude_company_domain: list[str] | None = Field(default=None, validation_alias="excludeCompanyDomain", serialization_alias="excludeCompanyDomain", description="Exclude articles related to companies with specific domains. Multiple values create an AND-exclude filter.")
    company_symbol: list[str] | None = Field(default=None, validation_alias="companySymbol", serialization_alias="companySymbol", description="Filter articles by company stock symbols (ticker symbols). Consult the /companies endpoint for available symbols. Multiple values create an OR filter.")
    exclude_company_symbol: list[str] | None = Field(default=None, validation_alias="excludeCompanySymbol", serialization_alias="excludeCompanySymbol", description="Exclude articles related to companies with specific stock symbols. Multiple values create an AND-exclude filter.")
    positive_sentiment_from: float | None = Field(default=None, validation_alias="positiveSentimentFrom", serialization_alias="positiveSentimentFrom", description="Filter articles with positive sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger positive tone.", json_schema_extra={'format': 'float'})
    positive_sentiment_to: float | None = Field(default=None, validation_alias="positiveSentimentTo", serialization_alias="positiveSentimentTo", description="Filter articles with positive sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger positive tone.", json_schema_extra={'format': 'float'})
    neutral_sentiment_from: float | None = Field(default=None, validation_alias="neutralSentimentFrom", serialization_alias="neutralSentimentFrom", description="Filter articles with neutral sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger neutral tone.", json_schema_extra={'format': 'float'})
    neutral_sentiment_to: float | None = Field(default=None, validation_alias="neutralSentimentTo", serialization_alias="neutralSentimentTo", description="Filter articles with neutral sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger neutral tone.", json_schema_extra={'format': 'float'})
    negative_sentiment_from: float | None = Field(default=None, validation_alias="negativeSentimentFrom", serialization_alias="negativeSentimentFrom", description="Filter articles with negative sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger negative tone.", json_schema_extra={'format': 'float'})
    negative_sentiment_to: float | None = Field(default=None, validation_alias="negativeSentimentTo", serialization_alias="negativeSentimentTo", description="Filter articles with negative sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger negative tone.", json_schema_extra={'format': 'float'})
    taxonomy: list[str] | None = Field(default=None, description="Filter by Google Content Categories using full category names (e.g., /Finance/Banking/Other, /Finance/Investing/Funds). Refer to Google's category list for complete options. Multiple values create an OR filter.")
    prefix_taxonomy: str | None = Field(default=None, validation_alias="prefixTaxonomy", serialization_alias="prefixTaxonomy", description="Filter by Google Content Categories using category prefix only (e.g., /Finance). Matches all categories starting with the specified prefix.")
class SearchArticlesRequest(StrictModel):
    """Search and filter news articles across Perigon's database using flexible query parameters. Returns paginated results with support for text search, date ranges, geographic filters, entity mentions, sentiment analysis, and content categorization."""
    query: SearchArticlesRequestQuery | None = None

# Operation: search_companies
class SearchCompaniesRequestQuery(StrictModel):
    id_: list[str] | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Filter results to companies with specific unique identifiers. Accepts multiple IDs as an OR filter (returns companies matching any ID in the list).")
    symbol: list[str] | None = Field(default=None, description="Filter results to companies with specific stock ticker symbols (e.g., AAPL, MSFT). Accepts multiple symbols as an OR filter.")
    domain: list[str] | None = Field(default=None, description="Filter results to companies with specific domain names or websites (e.g., apple.com, microsoft.com). Accepts multiple domains as an OR filter.")
    country: list[str] | None = Field(default=None, description="Filter results to companies headquartered in specific countries. Accepts multiple countries as an OR filter.")
    exchange: list[str] | None = Field(default=None, description="Filter results to companies listed on specific stock exchanges (e.g., NASDAQ, NYSE). Accepts multiple exchanges as an OR filter.")
    num_employees_from: int | None = Field(default=None, validation_alias="numEmployeesFrom", serialization_alias="numEmployeesFrom", description="Filter for companies with at least this minimum number of employees. Must be a positive integer.", json_schema_extra={'format': 'int32'})
    num_employees_to: int | None = Field(default=None, validation_alias="numEmployeesTo", serialization_alias="numEmployeesTo", description="Filter for companies with no more than this maximum number of employees. Must be a positive integer.", json_schema_extra={'format': 'int32'})
    ipo_from: str | None = Field(default=None, validation_alias="ipoFrom", serialization_alias="ipoFrom", description="Filter for companies that went public on or after this date. Accepts ISO 8601 format (e.g., 2023-01-01T00:00:00) or yyyy-mm-dd format.", json_schema_extra={'format': 'date-time'})
    ipo_to: str | None = Field(default=None, validation_alias="ipoTo", serialization_alias="ipoTo", description="Filter for companies that went public on or before this date. Accepts ISO 8601 format (e.g., 2023-12-31T23:59:59) or yyyy-mm-dd format.", json_schema_extra={'format': 'date-time'})
    name: str | None = Field(default=None, description="Search within company names using Boolean operators (AND, OR, NOT), exact phrases with quotes, and wildcards (* for multiple characters, ? for single character).")
    industry: str | None = Field(default=None, description="Filter by company industry classifications using Boolean operators (AND, OR, NOT), exact phrases with quotes, and wildcards (* for multiple characters, ? for single character).")
    sector: str | None = Field(default=None, description="Filter by company sector classifications using Boolean operators (AND, OR, NOT), exact phrases with quotes, and wildcards (* for multiple characters, ? for single character).")
    size: int | None = Field(default=None, description="Number of companies to return per page. Must be between 1 and 100 inclusive.", json_schema_extra={'format': 'int32'})
    page: int | None = Field(default=None, description="Zero-indexed page number to retrieve from the paginated results. Must be 0 or greater.", json_schema_extra={'format': 'int32'})
class SearchCompaniesRequest(StrictModel):
    """Search and filter companies tracked by Perigon using multiple criteria including name, domain, ticker symbol, industry, sector, and company metadata. Supports Boolean search logic for flexible querying across company attributes."""
    query: SearchCompaniesRequestQuery | None = None

# Operation: search_journalists
class SearchJournalistsRequestQuery(StrictModel):
    id_: list[str] | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Filter by one or more journalist IDs. Matches any journalist whose ID is in the provided list (OR operation).")
    name: str | None = Field(default=None, description="Search journalist names using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (* and ?) for pattern matching.")
    twitter: str | None = Field(default=None, description="Filter by exact Twitter handle (without the @ symbol).")
    size: int | None = Field(default=None, description="Number of results to return per page. Must be between 0 and 1,000.", json_schema_extra={'format': 'int32'})
    page: int | None = Field(default=None, description="Zero-indexed page number for pagination. Use 0 for the first page.", json_schema_extra={'format': 'int32'})
    source: list[str] | None = Field(default=None, description="Filter by publisher domains where journalists write. Supports wildcards (* and ?) for pattern matching (e.g., *.cnn.com). Matches any domain in the list (OR operation).")
    topic: list[str] | None = Field(default=None, description="Filter by specific topics journalists cover (e.g., 'Economy', 'Real Estate', 'Cryptocurrency'). Matches any topic in the list (OR operation).")
    category: list[str] | None = Field(default=None, description="Filter by general content categories journalists cover (e.g., 'Tech', 'Politics'). Matches any category in the list (OR operation).")
    label: list[str] | None = Field(default=None, description="Filter by article labels most commonly associated with journalists' work (e.g., 'Opinion', 'Pop Culture'). Matches any label in the list (OR operation).")
    country: list[str] | None = Field(default=None, description="Filter by countries journalists commonly cover. Use ISO 3166-1 alpha-2 country codes in lowercase (e.g., us, gb, jp). Matches any country in the list (OR operation).")
    updated_at_from: str | None = Field(default=None, validation_alias="updatedAtFrom", serialization_alias="updatedAtFrom", description="Filter for journalist profiles updated on or after this date. Accepts ISO 8601 format (e.g., 2023-03-01T00:00:00) or yyyy-mm-dd format.", json_schema_extra={'format': 'date-time'})
    updated_at_to: str | None = Field(default=None, validation_alias="updatedAtTo", serialization_alias="updatedAtTo", description="Filter for journalist profiles updated on or before this date. Accepts ISO 8601 format (e.g., 2023-03-01T23:59:59) or yyyy-mm-dd format.", json_schema_extra={'format': 'date-time'})
class SearchJournalistsRequest(StrictModel):
    """Search and filter journalists from a global database of over 230,000 profiles. Use multiple filter criteria to find journalists by name, coverage topics, publication sources, and other attributes."""
    query: SearchJournalistsRequestQuery | None = None

# Operation: get_journalist
class GetJournalistByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the journalist. This ID is provided in article response objects and is used to fetch the journalist's full profile.")
class GetJournalistByIdRequest(StrictModel):
    """Retrieve detailed information about a specific journalist using their unique identifier. Use this to access journalist profiles and biographical details referenced in article responses."""
    path: GetJournalistByIdRequestPath

# Operation: search_people
class SearchPeopleRequestQuery(StrictModel):
    name: str | None = Field(default=None, description="Search by person's full or partial name using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (* for multiple characters, ? for single character) for flexible name-based lookups.")
    wikidata_id: list[str] | None = Field(default=None, validation_alias="wikidataId", serialization_alias="wikidataId", description="Filter results by one or more Wikidata entity IDs (e.g., Q7747, Q937) to precisely identify specific individuals and eliminate name ambiguity. Multiple IDs are combined with OR logic.")
    occupation_label: str | None = Field(default=None, validation_alias="occupationLabel", serialization_alias="occupationLabel", description="Search by occupation or profession (e.g., politician, actor, CEO, athlete) using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (* and ?) for flexible occupation-based filtering.")
    page: int | None = Field(default=None, description="Specify which page of results to retrieve in the paginated response, starting from page 0. Use with size parameter to navigate through large result sets.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(default=None, description="Set the number of people to return per page, between 1 and 100 results. Combine with page parameter to control pagination through results.", json_schema_extra={'format': 'int32'})
class SearchPeopleRequest(StrictModel):
    """Search and retrieve detailed information on known persons from Perigon's database of over 650,000 people worldwide. Results include Wikidata identifiers for cross-referencing additional biographical data."""
    query: SearchPeopleRequestQuery | None = None

# Operation: search_media_sources
class SearchSourcesRequestQuery(StrictModel):
    domain: list[str] | None = Field(default=None, description="Filter by publisher domain or subdomain using wildcard patterns (* for any characters, ? for single character). Supports multiple domains with OR logic (e.g., *.cnn.com, us?.nytimes.com).")
    name: str | None = Field(default=None, description="Search source names using Boolean operators (AND, OR, NOT), quoted exact phrases, and wildcards (* and ?) for flexible matching.")
    source_group: str | None = Field(default=None, validation_alias="sourceGroup", serialization_alias="sourceGroup", description="Filter by predefined publisher bundles or collections (e.g., top100, top50tech). Returns all sources within the specified group.")
    sort_by: Literal["createdAt", "updatedAt", "relevance", "count", "totalCount"] | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="Sort results by relevance to your query (default), overall traffic rank, monthly visitor count, or publication frequency. Choose the metric most relevant to your use case.")
    page: int | None = Field(default=None, description="Retrieve a specific page of results (0-indexed). Use with size parameter for pagination through large result sets.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(default=None, description="Number of sources per page (1-100). Adjust based on your needs; larger values reduce pagination requests but increase response size.", json_schema_extra={'format': 'int32'})
    country: list[str] | None = Field(default=None, description="Filter sources by countries they frequently cover in reporting. Use ISO 3166-1 alpha-2 country codes (lowercase, e.g., us, gb, jp). Multiple values use OR logic.")
    source_country: list[str] | None = Field(default=None, validation_alias="sourceCountry", serialization_alias="sourceCountry", description="Filter for local publications based in specific countries. Use ISO 3166-1 alpha-2 country codes (lowercase). Multiple values use OR logic.")
    source_state: list[str] | None = Field(default=None, validation_alias="sourceState", serialization_alias="sourceState", description="Filter for local publications based in specific states or regions. Use standard two-letter state codes (lowercase, e.g., ca, ny, tx). Multiple values use OR logic.")
    source_county: list[str] | None = Field(default=None, validation_alias="sourceCounty", serialization_alias="sourceCounty", description="Filter for local publications based in specific counties. Multiple values use OR logic.")
    source_city: list[str] | None = Field(default=None, validation_alias="sourceCity", serialization_alias="sourceCity", description="Filter for local publications based in specific cities. Multiple values use OR logic.")
    category: list[str] | None = Field(default=None, description="Filter sources by primary content categories (e.g., Politics, Tech, Sports, Business, Finance). Returns sources that frequently cover these topics. Multiple values use OR logic.")
    topic: list[str] | None = Field(default=None, description="Filter sources by frequently covered topics (e.g., Markets, Cryptocurrency, Climate Change). Returns sources where the topic ranks in their top 10 coverage areas. Multiple values use OR logic.")
    label: list[str] | None = Field(default=None, description="Filter sources by content label patterns (e.g., Opinion, Paid-news, Non-news). Returns sources where the label commonly appears in published content. Multiple values use OR logic.")
    paywall: bool | None = Field(default=None, description="Filter by paywall status: true for sources with paywalls, false for sources without paywalls.")
    show_subdomains: bool | None = Field(default=None, validation_alias="showSubdomains", serialization_alias="showSubdomains", description="Control subdomain handling in results. When true (default), subdomains appear as separate sources. When false, results consolidate to parent domains only.")
class SearchSourcesRequest(StrictModel):
    """Search and filter from 200,000+ media sources to find publishers matching your criteria. Results include detailed source information with flexible filtering by domain, geography, content focus, and publication characteristics."""
    query: SearchSourcesRequestQuery | None = None

# Operation: search_stories
class SearchStoriesRequestQuery(StrictModel):
    name: str | None = Field(default=None, description="Search story names using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern variations.")
    cluster_id: list[str] | None = Field(default=None, validation_alias="clusterId", serialization_alias="clusterId", description="Filter results to specific stories by their unique cluster identifiers. Multiple values return stories matching any of the specified IDs (OR logic).")
    exclude_cluster_id: list[str] | None = Field(default=None, validation_alias="excludeClusterId", serialization_alias="excludeClusterId", description="Exclude specific stories from results by their unique cluster identifiers. Multiple values exclude stories matching any of the specified IDs.")
    sort_by: Literal["createdAt", "updatedAt", "relevance", "count", "totalCount"] | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="Sort results by story creation date (default), last update time (best for tracking developing events), relevance to query, unique article count, or total article count including reprints.")
    page: int | None = Field(default=None, description="Retrieve a specific page of paginated results, starting from page 0. Maximum page value is 10,000.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(default=None, description="Number of stories to return per page. Must be between 0 and 100.", json_schema_extra={'format': 'int32'})
    updated_from: str | None = Field(default=None, validation_alias="updatedFrom", serialization_alias="updatedFrom", description="Return only stories that received new articles on or after this date (ISO 8601 format). Useful for tracking recently developing events.", json_schema_extra={'format': 'date-time'})
    updated_to: str | None = Field(default=None, validation_alias="updatedTo", serialization_alias="updatedTo", description="Return only stories that received new articles on or before this date (ISO 8601 format). Useful for tracking recently developing events.", json_schema_extra={'format': 'date-time'})
    topic: list[str] | None = Field(default=None, description="Filter stories by granular topics (e.g., Markets, Crime, Cryptocurrency, College Sports). Stories can match multiple topics. Multiple values return stories matching any topic (OR logic).")
    category: list[str] | None = Field(default=None, description="Filter stories by broad content categories (e.g., Politics, Tech, Sports, Business, Finance). Use 'none' to find uncategorized stories. Multiple values return stories matching any category (OR logic).")
    taxonomy: list[str] | None = Field(default=None, description="Filter stories by Google Content Categories using full hierarchical paths (e.g., /Finance/Banking/Other). Multiple values return stories matching any taxonomy path (OR logic).")
    source: list[str] | None = Field(default=None, description="Filter stories containing articles from specific publisher domains or subdomains. Supports wildcard patterns (* and ?) for flexible matching. A story matches if it contains at least one article from any specified source. Multiple values use OR logic.")
    source_group: list[str] | None = Field(default=None, validation_alias="sourceGroup", serialization_alias="sourceGroup", description="Filter stories containing articles from publishers in Perigon's curated source bundles (e.g., top100, top25crypto). A story matches if it contains at least one article from any publisher in the specified bundles. Multiple values use OR logic.")
    min_unique_sources: int | None = Field(default=None, validation_alias="minUniqueSources", serialization_alias="minUniqueSources", description="Return only stories covered by at least this many unique sources. Higher values identify more significant stories with broader coverage. Minimum value is 1; defaults to 3.", json_schema_extra={'format': 'int32'})
    person_wikidata_id: list[str] | None = Field(default=None, validation_alias="personWikidataId", serialization_alias="personWikidataId", description="Filter stories by Wikidata IDs of prominently mentioned people. Returns stories where these individuals appear as key entities. Multiple values use OR logic.")
    company_id: list[str] | None = Field(default=None, validation_alias="companyId", serialization_alias="companyId", description="Filter stories by company identifiers of prominently mentioned companies. Returns stories where these companies appear as key entities. Multiple values use OR logic.")
    company_domain: list[str] | None = Field(default=None, validation_alias="companyDomain", serialization_alias="companyDomain", description="Filter stories by domains of prominently mentioned companies (e.g., apple.com). Returns stories where companies with these domains appear as key entities. Multiple values use OR logic.")
    company_symbol: list[str] | None = Field(default=None, validation_alias="companySymbol", serialization_alias="companySymbol", description="Filter stories by stock symbols of prominently mentioned companies. Returns stories where companies with these symbols appear as key entities. Multiple values use OR logic.")
    country: list[str] | None = Field(default=None, description="Filter stories by country code. Multiple values return stories matching any country (OR logic).")
    state: list[str] | None = Field(default=None, description="Filter local news by state. When applied, only local news from specified states is returned; non-local news is excluded. Multiple values use OR logic.")
    city: list[str] | None = Field(default=None, description="Filter local news by city. When applied, only local news from specified cities is returned; non-local news is excluded. Multiple values use OR logic.")
    min_cluster_size: int | None = Field(default=None, validation_alias="minClusterSize", serialization_alias="minClusterSize", description="Return only stories with at least this many unique articles. Minimum value is 1.", json_schema_extra={'format': 'int32'})
    max_cluster_size: int | None = Field(default=None, validation_alias="maxClusterSize", serialization_alias="maxClusterSize", description="Return only stories with at most this many unique articles.", json_schema_extra={'format': 'int32'})
    name_exists: bool | None = Field(default=None, validation_alias="nameExists", serialization_alias="nameExists", description="Return only stories that have been assigned names. Stories receive names after accumulating at least 5 unique articles. Defaults to true.")
    positive_sentiment_from: float | None = Field(default=None, validation_alias="positiveSentimentFrom", serialization_alias="positiveSentimentFrom", description="Filter stories with aggregate positive sentiment score at or above this threshold. Scores range from 0 to 1, with higher values indicating stronger positive tone.", json_schema_extra={'format': 'float'})
    positive_sentiment_to: float | None = Field(default=None, validation_alias="positiveSentimentTo", serialization_alias="positiveSentimentTo", description="Filter stories with aggregate positive sentiment score at or below this threshold. Scores range from 0 to 1, with higher values indicating stronger positive tone.", json_schema_extra={'format': 'float'})
    neutral_sentiment_from: float | None = Field(default=None, validation_alias="neutralSentimentFrom", serialization_alias="neutralSentimentFrom", description="Filter stories with aggregate neutral sentiment score at or above this threshold. Scores range from 0 to 1, with higher values indicating stronger neutral tone.", json_schema_extra={'format': 'float'})
    neutral_sentiment_to: float | None = Field(default=None, validation_alias="neutralSentimentTo", serialization_alias="neutralSentimentTo", description="Filter stories with aggregate neutral sentiment score at or below this threshold. Scores range from 0 to 1, with higher values indicating stronger neutral tone.", json_schema_extra={'format': 'float'})
    negative_sentiment_from: float | None = Field(default=None, validation_alias="negativeSentimentFrom", serialization_alias="negativeSentimentFrom", description="Filter stories with aggregate negative sentiment score at or above this threshold. Scores range from 0 to 1, with higher values indicating stronger negative tone.", json_schema_extra={'format': 'float'})
    negative_sentiment_to: float | None = Field(default=None, validation_alias="negativeSentimentTo", serialization_alias="negativeSentimentTo", description="Filter stories with aggregate negative sentiment score at or below this threshold. Scores range from 0 to 1, with higher values indicating stronger negative tone.", json_schema_extra={'format': 'float'})
class SearchStoriesRequest(StrictModel):
    """Search and filter news story clusters to track evolving narratives, monitor sentiment trends, and identify coverage patterns across global publishers. Returns structured story metadata including summaries, key entities, sentiment scores, and article counts."""
    query: SearchStoriesRequestQuery | None = None

# Operation: list_story_history
class GetStoryHistoryRequestQuery(StrictModel):
    cluster_id: list[str] | None = Field(default=None, validation_alias="clusterId", serialization_alias="clusterId", description="Filter results to specific clusters by providing one or more cluster IDs. Only stories within the specified clusters will be returned.")
    sort_by: Literal["createdAt", "triggeredAt"] | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="Sort results by creation date or the date the story was last refreshed/triggered. Defaults to creation date if not specified.")
    page: int | None = Field(default=None, description="Zero-based page number for pagination, ranging from 0 to 10000. Use this to navigate through large result sets.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(default=None, description="Number of story results to return per page, ranging from 0 to 100. Larger values reduce the number of requests needed but increase response size.", json_schema_extra={'format': 'int32'})
    changelog_exists: bool | None = Field(default=None, validation_alias="changelogExists", serialization_alias="changelogExists", description="Filter to include only clusters that have a changelog (true) or exclude clusters with changelogs (false). Omit to return all clusters regardless of changelog status.")
class GetStoryHistoryRequest(StrictModel):
    """Retrieve a paginated list of story history records with optional filtering by cluster, sorting, and changelog status. Use this to track story creation and refresh events across your clusters."""
    query: GetStoryHistoryRequestQuery | None = None

# Operation: get_story_counts_by_time_interval
class GetStoryCountsRequestQuery(StrictModel):
    name: str | None = Field(default=None, description="Search for stories by name using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcard patterns (* and ?) for flexible name matching.")
    cluster_id: list[str] | None = Field(default=None, validation_alias="clusterId", serialization_alias="clusterId", description="Filter results to include only stories with specific cluster IDs. Multiple IDs are combined with OR logic, returning stories matching any of the provided identifiers.")
    exclude_cluster_id: list[str] | None = Field(default=None, validation_alias="excludeClusterId", serialization_alias="excludeClusterId", description="Exclude stories by their cluster IDs. Multiple IDs are combined with OR logic, filtering out stories matching any of the provided identifiers.")
    sort_by: Literal["createdAt", "updatedAt", "relevance", "count", "totalCount"] | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="Sort results by story creation date (default), last update date (best for tracking developing stories), relevance to query, unique article count, or total article count including reprints.")
    page: int | None = Field(default=None, description="Specify which page of results to retrieve in the paginated response, starting from page 0. Maximum page number is 10,000.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(default=None, description="Set the number of results per page. Must be between 0 and 100 results per page.", json_schema_extra={'format': 'int32'})
    updated_from: str | None = Field(default=None, validation_alias="updatedFrom", serialization_alias="updatedFrom", description="Filter for stories that received new articles on or after this date (ISO 8601 format). Useful for tracking recently developing news events.", json_schema_extra={'format': 'date-time'})
    updated_to: str | None = Field(default=None, validation_alias="updatedTo", serialization_alias="updatedTo", description="Filter for stories that received new articles on or before this date (ISO 8601 format). Useful for tracking recently developing news events.", json_schema_extra={'format': 'date-time'})
    topic: list[str] | None = Field(default=None, description="Filter stories by specific topics (e.g., Markets, Crime, Cryptocurrency, College Sports). Multiple topics are combined with OR logic. Consult the /topics endpoint for available options.")
    category: list[str] | None = Field(default=None, description="Filter stories by broad content categories (e.g., Politics, Tech, Sports, Business, Finance). Use 'none' to find uncategorized stories. Multiple categories are combined with OR logic.")
    taxonomy: list[str] | None = Field(default=None, description="Filter stories by Google Content Categories using full hierarchical paths (e.g., /Finance/Banking/Other). Multiple paths are combined with OR logic.")
    source: list[str] | None = Field(default=None, description="Filter stories containing articles from specific publisher domains or subdomains. Supports wildcard patterns (* and ?) for flexible matching. A story matches if it contains at least one article from any specified source. Multiple sources are combined with OR logic.")
    source_group: list[str] | None = Field(default=None, validation_alias="sourceGroup", serialization_alias="sourceGroup", description="Filter stories containing articles from publishers in Perigon's curated source bundles (e.g., top100, top25crypto). A story matches if it contains at least one article from any publisher in the specified bundles. Multiple bundles are combined with OR logic.")
    min_unique_sources: int | None = Field(default=None, validation_alias="minUniqueSources", serialization_alias="minUniqueSources", description="Require stories to be covered by a minimum number of unique sources. Higher values return more significant stories with broader coverage. Minimum value is 1; defaults to 3.", json_schema_extra={'format': 'int32'})
    person_wikidata_id: list[str] | None = Field(default=None, validation_alias="personWikidataId", serialization_alias="personWikidataId", description="Filter stories by Wikidata IDs of prominently mentioned people. Multiple IDs are combined with OR logic. Refer to the /people endpoint for available individuals.")
    company_id: list[str] | None = Field(default=None, validation_alias="companyId", serialization_alias="companyId", description="Filter stories by company identifiers of prominently mentioned companies. Multiple IDs are combined with OR logic. Refer to the /companies endpoint for available companies.")
    company_domain: list[str] | None = Field(default=None, validation_alias="companyDomain", serialization_alias="companyDomain", description="Filter stories by domains of prominently mentioned companies (e.g., apple.com). Multiple domains are combined with OR logic. Refer to the /companies endpoint for available options.")
    company_symbol: list[str] | None = Field(default=None, validation_alias="companySymbol", serialization_alias="companySymbol", description="Filter stories by stock symbols of prominently mentioned companies. Multiple symbols are combined with OR logic. Refer to the /companies endpoint for available symbols.")
    country: list[str] | None = Field(default=None, description="Filter stories by country using ISO country codes. Multiple countries are combined with OR logic.")
    state: list[str] | None = Field(default=None, description="Filter local news by state. When applied, only local news from specified states is returned; non-local news is excluded. Multiple states are combined with OR logic.")
    city: list[str] | None = Field(default=None, description="Filter local news by city. When applied, only local news from specified cities is returned; non-local news is excluded. Multiple cities are combined with OR logic.")
    min_cluster_size: int | None = Field(default=None, validation_alias="minClusterSize", serialization_alias="minClusterSize", description="Filter stories by minimum cluster size based on unique article count. Minimum value is 1.", json_schema_extra={'format': 'int32'})
    max_cluster_size: int | None = Field(default=None, validation_alias="maxClusterSize", serialization_alias="maxClusterSize", description="Filter stories by maximum cluster size based on unique article count.", json_schema_extra={'format': 'int32'})
    name_exists: bool | None = Field(default=None, validation_alias="nameExists", serialization_alias="nameExists", description="Include only stories that have been assigned names. Stories receive names after accumulating at least 5 unique articles. Defaults to true.")
    positive_sentiment_from: float | None = Field(default=None, validation_alias="positiveSentimentFrom", serialization_alias="positiveSentimentFrom", description="Filter stories with aggregate positive sentiment score at or above the specified threshold. Scores range from 0 to 1, with higher values indicating stronger positive tone.", json_schema_extra={'format': 'float'})
    positive_sentiment_to: float | None = Field(default=None, validation_alias="positiveSentimentTo", serialization_alias="positiveSentimentTo", description="Filter stories with aggregate positive sentiment score at or below the specified threshold. Scores range from 0 to 1, with higher values indicating stronger positive tone.", json_schema_extra={'format': 'float'})
    neutral_sentiment_from: float | None = Field(default=None, validation_alias="neutralSentimentFrom", serialization_alias="neutralSentimentFrom", description="Filter stories with aggregate neutral sentiment score at or above the specified threshold. Scores range from 0 to 1, with higher values indicating stronger neutral tone.", json_schema_extra={'format': 'float'})
    neutral_sentiment_to: float | None = Field(default=None, validation_alias="neutralSentimentTo", serialization_alias="neutralSentimentTo", description="Filter stories with aggregate neutral sentiment score at or below the specified threshold. Scores range from 0 to 1, with higher values indicating stronger neutral tone.", json_schema_extra={'format': 'float'})
    negative_sentiment_from: float | None = Field(default=None, validation_alias="negativeSentimentFrom", serialization_alias="negativeSentimentFrom", description="Filter stories with aggregate negative sentiment score at or above the specified threshold. Scores range from 0 to 1, with higher values indicating stronger negative tone.", json_schema_extra={'format': 'float'})
    negative_sentiment_to: float | None = Field(default=None, validation_alias="negativeSentimentTo", serialization_alias="negativeSentimentTo", description="Filter stories with aggregate negative sentiment score at or below the specified threshold. Scores range from 0 to 1, with higher values indicating stronger negative tone.", json_schema_extra={'format': 'float'})
    split_by: Literal["hour", "day", "week", "month", "none"] = Field(default=..., validation_alias="splitBy", serialization_alias="splitBy", description="Required. Specify the time interval for grouping story count statistics: HOUR (hourly breakdown), DAY (daily breakdown), WEEK (weekly breakdown), MONTH (monthly breakdown), or NONE (no time-based grouping).")
class GetStoryCountsRequest(StrictModel):
    """Retrieve aggregated story count statistics grouped by specified time intervals (hour, day, week, or month). Supports comprehensive filtering by story attributes, entities, sentiment, and geographic location to analyze news trends and story evolution over time."""
    query: GetStoryCountsRequestQuery

# Operation: search_and_summarize_articles
class SearchSummarizerRequestQuery(StrictModel):
    title: str | None = Field(default=None, description="Search article titles using Boolean operators (AND, OR, NOT), exact phrases with quotes, and wildcards for pattern matching.")
    desc: str | None = Field(default=None, description="Search article descriptions using Boolean expressions, exact phrase matching with quotes, and wildcards for flexible pattern matching.")
    content: str | None = Field(default=None, description="Search full article body content using Boolean logic, exact phrase matching with quotes, and wildcards for comprehensive searching.")
    summary: str | None = Field(default=None, description="Search article summary fields using Boolean expressions, exact phrase matching with quotes, and wildcards for flexible pattern matching.")
    url: str | None = Field(default=None, description="Search by URL patterns to filter articles from specific website sections or domains.")
    article_id: list[str] | None = Field(default=None, validation_alias="articleId", serialization_alias="articleId", description="Retrieve specific articles by their unique identifiers. Provide one or more article IDs to return a targeted collection.")
    cluster_id: list[str] | None = Field(default=None, validation_alias="clusterId", serialization_alias="clusterId", description="Filter results to articles within a specific related content cluster. Returns articles grouped by topic relevance as Perigon Stories.")
    sort_by: Literal["relevance", "date", "reverseDate", "reverseAddDate", "addDate", "pubDate", "refreshDate"] | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="Determine article sort order: relevance (default), date/pubDate (newest first), reverseDate (oldest first), addDate (newest ingestion first), reverseAddDate (oldest ingestion first), or refreshDate (most recently updated first).")
    page: int | None = Field(default=None, description="Specify which page of results to retrieve, starting from page 0. Supports up to 10,000 pages.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(default=None, description="Number of articles to return per page. Range: 0–1,000 articles.", json_schema_extra={'format': 'int32'})
    add_date_from: str | None = Field(default=None, validation_alias="addDateFrom", serialization_alias="addDateFrom", description="Filter for articles added to the system after this date. Accepts ISO 8601 format (e.g., 2022-02-01T00:00:00) or yyyy-mm-dd format.", json_schema_extra={'format': 'date-time'})
    add_date_to: str | None = Field(default=None, validation_alias="addDateTo", serialization_alias="addDateTo", description="Filter for articles added to the system before this date. Accepts ISO 8601 format (e.g., 2022-02-01T23:59:59) or yyyy-mm-dd format.", json_schema_extra={'format': 'date-time'})
    refresh_date_from: str | None = Field(default=None, validation_alias="refreshDateFrom", serialization_alias="refreshDateFrom", description="Filter for articles refreshed or updated in the system after this date. Accepts ISO 8601 format (e.g., 2022-02-01T00:00:00) or yyyy-mm-dd format.", json_schema_extra={'format': 'date-time'})
    refresh_date_to: str | None = Field(default=None, validation_alias="refreshDateTo", serialization_alias="refreshDateTo", description="Filter for articles refreshed or updated in the system before this date. Accepts ISO 8601 format (e.g., 2022-02-01T23:59:59) or yyyy-mm-dd format.", json_schema_extra={'format': 'date-time'})
    medium: list[str] | None = Field(default=None, description="Filter by content medium: Article (written content) or Video (video-based stories). Multiple values create an OR filter.")
    source: list[str] | None = Field(default=None, description="Filter by specific publisher domains or subdomains. Supports wildcards (* and ?) for pattern matching. Multiple values create an OR filter.")
    source_group: list[str] | None = Field(default=None, validation_alias="sourceGroup", serialization_alias="sourceGroup", description="Filter using Perigon's curated publisher bundles (e.g., top100, top25crypto). Multiple values create an OR filter.")
    exclude_source_group: list[str] | None = Field(default=None, validation_alias="excludeSourceGroup", serialization_alias="excludeSourceGroup", description="Exclude articles from specified Perigon source groups. Multiple values create an AND-exclude filter, removing content from any matching bundle.")
    exclude_source: list[str] | None = Field(default=None, validation_alias="excludeSource", serialization_alias="excludeSource", description="Exclude articles from specific publisher domains or subdomains. Supports wildcards (* and ?) for pattern matching. Multiple values create an AND-exclude filter.")
    watchlist: list[str] | None = Field(default=None, description="Filter articles using watchlists of people and companies. Multiple values create an OR filter to include articles mentioning any entity from specified watchlists.")
    exclude_watchlist: list[str] | None = Field(default=None, validation_alias="excludeWatchlist", serialization_alias="excludeWatchlist", description="Exclude articles mentioning entities from specified watchlists. Multiple values create an AND-exclude filter, removing content about any matching entity.")
    paywall: bool | None = Field(default=None, description="Filter by paywall status: true for sources with paywalls, false for sources without paywalls.")
    author: list[str] | None = Field(default=None, description="Filter articles by specific author names using exact matching. Multiple values create an OR filter to find articles by any specified author.")
    exclude_author: list[str] | None = Field(default=None, validation_alias="excludeAuthor", serialization_alias="excludeAuthor", description="Exclude articles written by specific authors using exact name matching. Multiple values create an AND-exclude filter.")
    journalist_id: list[str] | None = Field(default=None, validation_alias="journalistId", serialization_alias="journalistId", description="Filter articles by unique journalist identifiers (available via the Journalist API or matchedAuthors field). Multiple values create an OR filter.")
    exclude_journalist_id: list[str] | None = Field(default=None, validation_alias="excludeJournalistId", serialization_alias="excludeJournalistId", description="Exclude articles written by specific journalists identified by their unique IDs. Multiple values create an AND-exclude filter.")
    language: list[str] | None = Field(default=None, description="Filter articles by language using ISO 639 two-letter codes (e.g., en, es, fr). Multiple values create an OR filter.")
    exclude_language: list[str] | None = Field(default=None, validation_alias="excludeLanguage", serialization_alias="excludeLanguage", description="Exclude articles in specific languages using ISO 639 two-letter codes. Multiple values create an AND-exclude filter.")
    search_translation: bool | None = Field(default=None, validation_alias="searchTranslation", serialization_alias="searchTranslation", description="When true, expands search to include translated title, description, and content fields for non-English articles.")
    label: list[str] | None = Field(default=None, description="Filter articles by editorial labels such as Opinion, Paid-news, Non-news, Fact Check, or Press Release. Multiple values create an OR filter.")
    exclude_label: list[str] | None = Field(default=None, validation_alias="excludeLabel", serialization_alias="excludeLabel", description="Exclude articles with specific editorial labels. Multiple values create an AND-exclude filter.")
    category: list[str] | None = Field(default=None, description="Filter by general article categories (e.g., Tech, Politics). Use 'none' to search uncategorized articles. Multiple values create an OR filter.")
    exclude_category: list[str] | None = Field(default=None, validation_alias="excludeCategory", serialization_alias="excludeCategory", description="Exclude articles with specific categories. Multiple values create an AND-exclude filter.")
    topic: list[str] | None = Field(default=None, description="Filter by specific topics (e.g., Markets, Crime, Cryptocurrency, College Sports). Topics are more granular than categories. Multiple values create an OR filter. Consult the /topics endpoint for available topics.")
    exclude_topic: list[str] | None = Field(default=None, validation_alias="excludeTopic", serialization_alias="excludeTopic", description="Exclude articles with specific topics. Multiple values create an AND-exclude filter.")
    link_to: str | None = Field(default=None, validation_alias="linkTo", serialization_alias="linkTo", description="Return only articles containing links to the specified URL pattern.")
    show_reprints: bool | None = Field(default=None, validation_alias="showReprints", serialization_alias="showReprints", description="When true (default), includes reprinted content from wire services like AP or Reuters that appear on multiple sites.")
    reprint_group_id: str | None = Field(default=None, validation_alias="reprintGroupId", serialization_alias="reprintGroupId", description="Return all articles in a specific reprint group, including the original article and all known reprints.")
    city: list[str] | None = Field(default=None, description="Filter articles where a specified city plays a central role in the content. Multiple values create an OR filter.")
    exclude_city: list[str] | None = Field(default=None, validation_alias="excludeCity", serialization_alias="excludeCity", description="Exclude articles associated with specified cities. Multiple values create an AND-exclude filter.")
    state: list[str] | None = Field(default=None, description="Filter articles where a specified state plays a central role in the content. Multiple values create an OR filter.")
    exclude_state: list[str] | None = Field(default=None, validation_alias="excludeState", serialization_alias="excludeState", description="Exclude articles associated with specified states. Multiple values create an AND-exclude filter.")
    county: list[str] | None = Field(default=None, description="Filter articles by county. Only articles tagged with one of these counties will be included. Multiple values create an OR filter.")
    exclude_county: list[str] | None = Field(default=None, validation_alias="excludeCounty", serialization_alias="excludeCounty", description="Exclude articles from specific counties or administrative divisions. County names should match the format used in article metadata (e.g., 'Los Angeles County', 'Cook County'). Multiple values create an AND-exclude filter.")
    country: list[str] | None = Field(default=None, description="Filter articles by country code. Multiple values create an OR filter.")
    location: list[str] | None = Field(default=None, description="Return articles with specified location attributes. Format: 'city:New York::state:NY' with ':' between key and value, '::' between attributes.")
    lat: float | None = Field(default=None, description="Latitude of the center point for geographic search. Range: -90 to 90 degrees.", ge=-90, le=90, json_schema_extra={'format': 'double'})
    lon: float | None = Field(default=None, description="Longitude of the center point for geographic search. Range: -180 to 180 degrees.", ge=-180, le=180, json_schema_extra={'format': 'double'})
    max_distance: float | None = Field(default=None, validation_alias="maxDistance", serialization_alias="maxDistance", description="Maximum distance in kilometers from the center point for geographic search. Range: 1–300 km.", ge=1, le=300, json_schema_extra={'format': 'double'})
    source_city: list[str] | None = Field(default=None, validation_alias="sourceCity", serialization_alias="sourceCity", description="Filter articles published by sources located within specified cities. Multiple values create an OR filter.")
    exclude_source_city: list[str] | None = Field(default=None, validation_alias="excludeSourceCity", serialization_alias="excludeSourceCity", description="Exclude articles published by sources located within specified cities. Multiple values create an AND-exclude filter.")
    source_county: list[str] | None = Field(default=None, validation_alias="sourceCounty", serialization_alias="sourceCounty", description="Filter articles published by sources located within specified counties. Multiple values create an OR filter.")
    exclude_source_county: list[str] | None = Field(default=None, validation_alias="excludeSourceCounty", serialization_alias="excludeSourceCounty", description="Exclude articles published by sources located within specified counties. Multiple values create an AND-exclude filter.")
    source_country: list[str] | None = Field(default=None, validation_alias="sourceCountry", serialization_alias="sourceCountry", description="Filter articles published by sources located within specified countries. Use 2-character country codes (e.g., us, gb). Multiple values create an OR filter.")
    exclude_source_country: list[str] | None = Field(default=None, validation_alias="excludeSourceCountry", serialization_alias="excludeSourceCountry", description="Exclude articles published by sources located within specified countries. Use 2-character country codes (e.g., us, gb). Multiple values create an AND-exclude filter.")
    source_state: list[str] | None = Field(default=None, validation_alias="sourceState", serialization_alias="sourceState", description="Filter articles published by sources located within specified states. Multiple values create an OR filter.")
    exclude_source_state: list[str] | None = Field(default=None, validation_alias="excludeSourceState", serialization_alias="excludeSourceState", description="Exclude articles published by sources located within specified states. Multiple values create an AND-exclude filter.")
    person_wikidata_id: list[str] | None = Field(default=None, validation_alias="personWikidataId", serialization_alias="personWikidataId", description="Filter articles by Wikidata IDs of mentioned people. Refer to the /people endpoint for tracked individuals. Multiple values create an OR filter.")
    exclude_person_wikidata_id: list[str] | None = Field(default=None, validation_alias="excludePersonWikidataId", serialization_alias="excludePersonWikidataId", description="Exclude articles mentioning people with specific Wikidata IDs. Multiple values create an AND-exclude filter.")
    exclude_person_name: list[str] | None = Field(default=None, validation_alias="excludePersonName", serialization_alias="excludePersonName", description="Exclude articles mentioning specific people by name. Multiple values create an AND-exclude filter.")
    company_id: list[str] | None = Field(default=None, validation_alias="companyId", serialization_alias="companyId", description="Filter articles by company identifiers. Refer to the /companies endpoint for tracked companies. Multiple values create an OR filter.")
    exclude_company_id: list[str] | None = Field(default=None, validation_alias="excludeCompanyId", serialization_alias="excludeCompanyId", description="Exclude articles mentioning companies with specific identifiers. Multiple values create an AND-exclude filter.")
    company_domain: list[str] | None = Field(default=None, validation_alias="companyDomain", serialization_alias="companyDomain", description="Filter articles by company domains (e.g., apple.com). Consult the /companies endpoint for available entities. Multiple values create an OR filter.")
    exclude_company_domain: list[str] | None = Field(default=None, validation_alias="excludeCompanyDomain", serialization_alias="excludeCompanyDomain", description="Exclude articles related to companies with specific domains. Multiple values create an AND-exclude filter.")
    company_symbol: list[str] | None = Field(default=None, validation_alias="companySymbol", serialization_alias="companySymbol", description="Filter articles by company stock symbols (ticker symbols). Consult the /companies endpoint for available symbols. Multiple values create an OR filter.")
    exclude_company_symbol: list[str] | None = Field(default=None, validation_alias="excludeCompanySymbol", serialization_alias="excludeCompanySymbol", description="Exclude articles related to companies with specific stock symbols. Multiple values create an AND-exclude filter.")
    positive_sentiment_from: float | None = Field(default=None, validation_alias="positiveSentimentFrom", serialization_alias="positiveSentimentFrom", description="Filter articles with positive sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger positive tone.", json_schema_extra={'format': 'float'})
    positive_sentiment_to: float | None = Field(default=None, validation_alias="positiveSentimentTo", serialization_alias="positiveSentimentTo", description="Filter articles with positive sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger positive tone.", json_schema_extra={'format': 'float'})
    neutral_sentiment_from: float | None = Field(default=None, validation_alias="neutralSentimentFrom", serialization_alias="neutralSentimentFrom", description="Filter articles with neutral sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger neutral tone.", json_schema_extra={'format': 'float'})
    neutral_sentiment_to: float | None = Field(default=None, validation_alias="neutralSentimentTo", serialization_alias="neutralSentimentTo", description="Filter articles with neutral sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger neutral tone.", json_schema_extra={'format': 'float'})
    negative_sentiment_from: float | None = Field(default=None, validation_alias="negativeSentimentFrom", serialization_alias="negativeSentimentFrom", description="Filter articles with negative sentiment score greater than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger negative tone.", json_schema_extra={'format': 'float'})
    negative_sentiment_to: float | None = Field(default=None, validation_alias="negativeSentimentTo", serialization_alias="negativeSentimentTo", description="Filter articles with negative sentiment score less than or equal to the specified value. Scores range from 0 to 1, with higher values indicating stronger negative tone.", json_schema_extra={'format': 'float'})
    taxonomy: list[str] | None = Field(default=None, description="Filter by Google Content Categories using full category names (e.g., /Finance/Banking/Other, /Finance/Investing/Funds). Refer to the Google Content Categories documentation for the complete list. Multiple values create an OR filter.")
    prefix_taxonomy: str | None = Field(default=None, validation_alias="prefixTaxonomy", serialization_alias="prefixTaxonomy", description="Filter by Google Content Categories using category prefix only (e.g., /Finance). Matches all categories starting with the specified prefix.")
class SearchSummarizerRequestBody(StrictModel):
    prompt: str | None = Field(default=None, description="Custom instructions guiding how the summary should be written. Maximum 2,048 characters. Defaults to a casual, natural tone synthesis in one paragraph (no more than 125 words).")
    max_article_count: int | None = Field(default=None, validation_alias="maxArticleCount", serialization_alias="maxArticleCount", description="Maximum number of articles to factor into the summary. Range: 1–100 articles. Default: 10.", json_schema_extra={'format': 'int32'})
    returned_article_count: int | None = Field(default=None, validation_alias="returnedArticleCount", serialization_alias="returnedArticleCount", description="Maximum number of articles to return in the response. Can be less than maxArticleCount. Range: 1–100 articles. Default: 10.", json_schema_extra={'format': 'int32'})
    summarize_fields: list[Literal["TITLE", "CONTENT", "SUMMARY"]] | None = Field(default=None, validation_alias="summarizeFields", serialization_alias="summarizeFields", description="Which article fields to include when generating the summary. Choose up to three values from: TITLE, CONTENT, SUMMARY. Default: all three.")
    method: Literal["ARTICLES", "CLUSTERS"] | None = Field(default=None, description="Method for selecting articles: ARTICLES (include all matches) or CLUSTERS (one article per cluster). Default: ARTICLES.")
    model: Literal["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "llama-3.3-70b-versatile", "openai/gpt-oss-120b"] | None = Field(default=None, description="Underlying LLM model for generation. Options: gpt-4o, gpt-4o-mini, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, llama-3.3-70b-versatile, openai/gpt-oss-120b. Default: gpt-4.1.")
    temperature: float | None = Field(default=None, description="Sampling temperature for the LLM controlling randomness. Range: 0.0 (deterministic) to 2.0 (very creative). Default: 0.7.", ge=0, le=2, json_schema_extra={'format': 'double'})
    top_p: float | None = Field(default=None, validation_alias="topP", serialization_alias="topP", description="Nucleus sampling (top-p) parameter for the LLM controlling diversity. Range: 0.0 to 1.0. Default: 1.0.", ge=0, le=1, json_schema_extra={'format': 'double'})
    max_tokens: int | None = Field(default=None, validation_alias="maxTokens", serialization_alias="maxTokens", description="Maximum number of tokens to generate in the summary. Default: 2,048 tokens.", json_schema_extra={'format': 'int32'})
class SearchSummarizerRequest(StrictModel):
    """Generate a single, concise summary synthesizing insights from articles matching your search filters and criteria. Use custom prompts to guide which themes and findings to highlight in the summary."""
    query: SearchSummarizerRequestQuery | None = None
    body: SearchSummarizerRequestBody | None = None

# Operation: search_topics
class SearchTopicsRequestQuery(StrictModel):
    name: str | None = Field(default=None, description="Filter topics by exact name match or partial text search. Supports partial matching but does not accept wildcard patterns.")
    category: str | None = Field(default=None, description="Filter results to a specific broad category such as Politics, Tech, Sports, Business, Finance, or Entertainment.")
    subcategory: str | None = Field(default=None, description="Narrow results to a specific subcategory within the selected category for more granular topic classification.")
    page: int | None = Field(default=None, description="Specify which page of results to retrieve in the paginated response. Page numbering starts at 0.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(default=None, description="Set the maximum number of topics to return per page. Must be a non-negative integer.", json_schema_extra={'format': 'int32'})
class SearchTopicsRequest(StrictModel):
    """Search and browse all available topics in the Perigon database, with filtering by name, category, and subcategory. Results are paginated for efficient data retrieval."""
    query: SearchTopicsRequestQuery | None = None

# Operation: search_news_articles
class VectorSearchArticlesRequestBody(StrictModel):
    prompt: str = Field(default=..., description="Natural language query describing what you want to find in news articles. Accepts up to 1024 characters.", min_length=0, max_length=1024)
    filter_: VectorSearchArticlesBodyFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter criteria to narrow search results (specific filter structure not documented).")
    pub_date_from: str | None = Field(default=None, validation_alias="pubDateFrom", serialization_alias="pubDateFrom", description="Earliest publication date to include in results. Accepts ISO 8601 format (e.g., 2024-01-01T00:00:00Z) or simple date format (yyyy-mm-dd). Defaults to articles from the last 30 days if not specified.", json_schema_extra={'format': 'date-time'})
    pub_date_to: str | None = Field(default=None, validation_alias="pubDateTo", serialization_alias="pubDateTo", description="Latest publication date to include in results. Accepts ISO 8601 format (e.g., 2024-12-31T23:59:59Z) or simple date format (yyyy-mm-dd).", json_schema_extra={'format': 'date-time'})
    show_reprints: bool | None = Field(default=None, validation_alias="showReprints", serialization_alias="showReprints", description="Include or exclude reprinted articles (wire service content from sources like AP or Reuters that appear across multiple outlets). Defaults to including reprints.")
    size: int | None = Field(default=None, description="Number of results to return per page. Must be between 1 and 100 articles. Defaults to 10.", json_schema_extra={'format': 'int32'})
    page: int | None = Field(default=None, description="Page number to retrieve for paginated results. Must be between 0 and 10000. Defaults to the first page (0).", json_schema_extra={'format': 'int32'})
class VectorSearchArticlesRequest(StrictModel):
    """Search news articles from the past 6 months using natural language queries with semantic relevance matching. Returns a ranked list of articles most closely aligned with your search intent, with optional filtering by publication date and content type."""
    body: VectorSearchArticlesRequestBody

# Operation: search_wikipedia
class VectorSearchWikipediaRequestBody(StrictModel):
    prompt: str = Field(default=..., description="Natural language query describing what you want to find. Supports up to 1024 characters.", min_length=0, max_length=1024)
    filter_: VectorSearchWikipediaBodyFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter to narrow search results by specific criteria.")
    size: int | None = Field(default=None, description="Number of results to return per page, between 1 and 100 items. Defaults to 10.", json_schema_extra={'format': 'int32'})
    page: int | None = Field(default=None, description="Page number for pagination, starting from 0 up to 10000. Defaults to 0 for the first page.", json_schema_extra={'format': 'int32'})
class VectorSearchWikipediaRequest(StrictModel):
    """Search Wikipedia using natural language queries to find page sections ranked by semantic relevance to your search intent."""
    body: VectorSearchWikipediaRequestBody

# Operation: search_wikipedia_pages
class SearchWikipediaRequestQuery(StrictModel):
    title: str | None = Field(default=None, description="Search within page titles using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern matching.")
    summary: str | None = Field(default=None, description="Search within page summaries using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern matching.")
    text: str | None = Field(default=None, description="Search across all page content and sections using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern matching.")
    reference: str | None = Field(default=None, description="Search across page references and citations using Boolean operators (AND, OR, NOT), exact phrase matching with quotes, and wildcards (*) for pattern matching.")
    id_: list[str] | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Retrieve specific pages by their unique Perigon identifiers. Provide one or more IDs as an array to return a targeted collection of pages.")
    wiki_namespace: list[int] | None = Field(default=None, validation_alias="wikiNamespace", serialization_alias="wikiNamespace", description="Filter pages by wiki namespace. Currently only the main namespace (0) is supported.")
    wikidata_id: list[str] | None = Field(default=None, validation_alias="wikidataId", serialization_alias="wikidataId", description="Retrieve pages by their corresponding Wikidata entity identifiers. Provide one or more Wikidata IDs as an array.")
    wikidata_instance_of_id: list[str] | None = Field(default=None, validation_alias="wikidataInstanceOfId", serialization_alias="wikidataInstanceOfId", description="Retrieve pages whose Wikidata entities are instances of the specified Wikidata IDs. Provide one or more IDs as an array.")
    wikidata_instance_of_label: list[str] | None = Field(default=None, validation_alias="wikidataInstanceOfLabel", serialization_alias="wikidataInstanceOfLabel", description="Retrieve pages whose Wikidata entities are instances of the specified labels. Provide one or more Wikidata entity labels as an array.")
    category: list[str] | None = Field(default=None, description="Filter pages by Wikipedia categories. Provide one or more category names as an array.")
    section_id: list[str] | None = Field(default=None, validation_alias="sectionId", serialization_alias="sectionId", description="Retrieve pages containing specific section identifiers. Each section ID is unique within the Wikipedia dataset; provide one or more as an array.")
    with_pageviews: bool | None = Field(default=None, validation_alias="withPageviews", serialization_alias="withPageviews", description="When enabled, return only pages that have viewership statistics available. Defaults to false, which returns all matching pages regardless of viewership data.")
    page: int | None = Field(default=None, description="Specify which page of results to retrieve in the paginated response, starting from 0. Maximum page number is 10000.", json_schema_extra={'format': 'int32'})
    size: int | None = Field(default=None, description="Set the number of articles to return per page in the paginated response. Maximum is 1000 results per page.", json_schema_extra={'format': 'int32'})
    sort_by: Literal["relevance", "revisionTsDesc", "revisionTsAsc", "pageViewsDesc", "pageViewsAsc", "scrapedAtDesc", "scrapedAtAsc"] | None = Field(default=None, validation_alias="sortBy", serialization_alias="sortBy", description="Sort results by relevance (default), revision timestamp (ascending or descending for recently edited), page views (ascending or descending for viewership), or scrape timestamp (ascending or descending for recently updated).")
class SearchWikipediaRequest(StrictModel):
    """Search and retrieve Wikipedia pages from the Perigon API using flexible filtering criteria across titles, summaries, content, and references. Results are returned as paginated collections that can be sorted by relevance, recency, or viewership."""
    query: SearchWikipediaRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class CategoryHolder(PermissiveModel):
    name: str | None = None

class CategoryWithScoreHolder(PermissiveModel):
    name: str | None = None
    score: float | None = Field(None, json_schema_extra={'format': 'double'})

class CompanyCount(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    domains: list[str] | None = None
    symbols: list[str] | None = None
    count: int | None = Field(None, json_schema_extra={'format': 'int32'})

class CompanyHolder(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    domains: list[str] | None = None
    symbols: list[str] | None = None

class Coordinate(PermissiveModel):
    lat: float | None = Field(None, json_schema_extra={'format': 'double'})
    lon: float | None = Field(None, json_schema_extra={'format': 'double'})

class CoordinateFilter(PermissiveModel):
    """Filter articles from publishers based at specific geographic locations. Uses latitude, longitude, and radius parameters to define a circular search area for publisher locations."""
    lat: float | None = Field(None, json_schema_extra={'format': 'float'})
    lon: float | None = Field(None, json_schema_extra={'format': 'float'})
    radius: float | None = Field(None, json_schema_extra={'format': 'float'})

class EntityHolder(PermissiveModel):
    data: str | None = None
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")
    mentions: int | None = Field(None, json_schema_extra={'format': 'int32'})

class EventTypeHolder(PermissiveModel):
    name: str | None = None
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")

class IdNameHolder(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None

class KeyPoint(PermissiveModel):
    point: str | None = None
    references: list[str] | None = None

class KeywordHolder(PermissiveModel):
    name: str | None = None
    weight: float | None = Field(None, json_schema_extra={'format': 'float'})

class LabelHolder(PermissiveModel):
    name: str | None = None

class LocationCount(PermissiveModel):
    country: str | None = None
    state: str | None = None
    county: str | None = None
    city: str | None = None
    area: str | None = None
    count: int | None = Field(None, json_schema_extra={'format': 'int32'})

class LocationHolder(PermissiveModel):
    country: str | None = None
    state: str | None = None
    county: str | None = None
    city: str | None = None
    area: str | None = None

class NameCount(PermissiveModel):
    name: str | None = None
    count: int | None = Field(None, json_schema_extra={'format': 'int64'})

class Journalist(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    name: str | None = None
    full_name: str | None = Field(None, validation_alias="fullName", serialization_alias="fullName")
    headline: str | None = None
    description: str | None = None
    title: str | None = None
    locations: list[LocationHolder] | None = None
    updated_at: str | None = Field(None, validation_alias="updatedAt", serialization_alias="updatedAt")
    top_topics: list[NameCount] | None = Field(None, validation_alias="topTopics", serialization_alias="topTopics")
    top_sources: list[NameCount] | None = Field(None, validation_alias="topSources", serialization_alias="topSources")
    top_categories: list[NameCount] | None = Field(None, validation_alias="topCategories", serialization_alias="topCategories")
    top_labels: list[NameCount] | None = Field(None, validation_alias="topLabels", serialization_alias="topLabels")
    top_countries: list[NameCount] | None = Field(None, validation_alias="topCountries", serialization_alias="topCountries")
    avg_monthly_posts: int | None = Field(None, validation_alias="avgMonthlyPosts", serialization_alias="avgMonthlyPosts", json_schema_extra={'format': 'int32'})
    twitter_handle: str | None = Field(None, validation_alias="twitterHandle", serialization_alias="twitterHandle")
    twitter_bio: str | None = Field(None, validation_alias="twitterBio", serialization_alias="twitterBio")
    image_url: str | None = Field(None, validation_alias="imageUrl", serialization_alias="imageUrl")
    linkedin_url: str | None = Field(None, validation_alias="linkedinUrl", serialization_alias="linkedinUrl")
    linkedin_connections: int | None = Field(None, validation_alias="linkedinConnections", serialization_alias="linkedinConnections", json_schema_extra={'format': 'int32'})
    linkedin_followers: int | None = Field(None, validation_alias="linkedinFollowers", serialization_alias="linkedinFollowers", json_schema_extra={'format': 'int32'})
    facebook_url: str | None = Field(None, validation_alias="facebookUrl", serialization_alias="facebookUrl")
    instagram_url: str | None = Field(None, validation_alias="instagramUrl", serialization_alias="instagramUrl")
    website_url: str | None = Field(None, validation_alias="websiteUrl", serialization_alias="websiteUrl")
    blog_url: str | None = Field(None, validation_alias="blogUrl", serialization_alias="blogUrl")
    tumblr_url: str | None = Field(None, validation_alias="tumblrUrl", serialization_alias="tumblrUrl")
    youtube_url: str | None = Field(None, validation_alias="youtubeUrl", serialization_alias="youtubeUrl")

class PersonCount(PermissiveModel):
    wikidata_id: str | None = Field(None, validation_alias="wikidataId", serialization_alias="wikidataId")
    name: str | None = None
    count: int | None = Field(None, json_schema_extra={'format': 'int32'})

class PersonHolder(PermissiveModel):
    wikidata_id: str | None = Field(None, validation_alias="wikidataId", serialization_alias="wikidataId")
    name: str | None = None

class Place(PermissiveModel):
    osm_id: str | None = Field(None, validation_alias="osmId", serialization_alias="osmId")
    road: str | None = None
    quarter: str | None = None
    suburb: str | None = None
    city: str | None = None
    town: str | None = None
    county: str | None = None
    state_district: str | None = Field(None, validation_alias="stateDistrict", serialization_alias="stateDistrict")
    state: str | None = None
    postcode: str | None = None
    country: str | None = None
    country_code: str | None = Field(None, validation_alias="countryCode", serialization_alias="countryCode")
    amenity: str | None = None
    neighbourhood: str | None = None
    coordinates: Coordinate | None = None

class Question(PermissiveModel):
    question: str | None = None
    answer: str | None = None
    references: list[str] | None = None

class RecordStatHolder(PermissiveModel):
    name: str | None = None
    count: int | None = Field(None, json_schema_extra={'format': 'int32'})

class SentimentHolder(PermissiveModel):
    positive: float | None = Field(None, json_schema_extra={'format': 'float'})
    negative: float | None = Field(None, json_schema_extra={'format': 'float'})
    neutral: float | None = Field(None, json_schema_extra={'format': 'float'})

class SourceLocation(PermissiveModel):
    country: str | None = None
    state: str | None = None
    county: str | None = None
    city: str | None = None
    coordinates: Coordinate | None = None

class SourceHolder(PermissiveModel):
    domain: str | None = None
    paywall: bool | None = None
    location: SourceLocation | None = None

class TopicHolder(PermissiveModel):
    name: str | None = None

class VectorData(PermissiveModel):
    data: list[float] | None = None
    version: int | None = Field(None, json_schema_extra={'format': 'int32'})

class VectorSearchArticlesBodyFilterCoordinates(PermissiveModel):
    lat: float | None = Field(None, json_schema_extra={'format': 'float'})
    lon: float | None = Field(None, json_schema_extra={'format': 'float'})
    radius: float | None = Field(None, json_schema_extra={'format': 'float'})

class VectorSearchArticlesBodyFilterSourceCoordinates(PermissiveModel):
    lat: float | None = Field(None, json_schema_extra={'format': 'float'})
    lon: float | None = Field(None, json_schema_extra={'format': 'float'})
    radius: float | None = Field(None, json_schema_extra={'format': 'float'})

class Article(PermissiveModel):
    url: str | None = None
    authors_byline: str | None = Field(None, validation_alias="authorsByline", serialization_alias="authorsByline")
    article_id: str | None = Field(None, validation_alias="articleId", serialization_alias="articleId")
    cluster_id: str | None = Field(None, validation_alias="clusterId", serialization_alias="clusterId")
    source: SourceHolder | None = None
    image_url: str | None = Field(None, validation_alias="imageUrl", serialization_alias="imageUrl")
    country: str | None = None
    language: str | None = None
    pub_date: str | None = Field(None, validation_alias="pubDate", serialization_alias="pubDate")
    add_date: str | None = Field(None, validation_alias="addDate", serialization_alias="addDate")
    refresh_date: str | None = Field(None, validation_alias="refreshDate", serialization_alias="refreshDate")
    score: float | None = Field(None, json_schema_extra={'format': 'float'})
    title: str | None = None
    description: str | None = None
    content: str | None = None
    en_content_word_count: int | None = Field(None, validation_alias="enContentWordCount", serialization_alias="enContentWordCount", json_schema_extra={'format': 'int32'})
    medium: str | None = None
    links: list[str] | None = None
    labels: list[LabelHolder] | None = None
    event_types: list[EventTypeHolder] | None = Field(None, validation_alias="eventTypes", serialization_alias="eventTypes")
    matched_authors: list[IdNameHolder] | None = Field(None, validation_alias="matchedAuthors", serialization_alias="matchedAuthors")
    claim: str | None = None
    verdict: str | None = None
    keywords: list[KeywordHolder] | None = None
    topics: list[TopicHolder] | None = None
    categories: list[CategoryHolder] | None = None
    taxonomies: list[CategoryWithScoreHolder] | None = None
    entities: list[EntityHolder] | None = None
    companies: list[CompanyHolder] | None = None
    sentiment: SentimentHolder | None = None
    summary: str | None = None
    short_summary: str | None = Field(None, validation_alias="shortSummary", serialization_alias="shortSummary")
    translation: str | None = None
    translated_title: str | None = Field(None, validation_alias="translatedTitle", serialization_alias="translatedTitle")
    translated_description: str | None = Field(None, validation_alias="translatedDescription", serialization_alias="translatedDescription")
    translated_summary: str | None = Field(None, validation_alias="translatedSummary", serialization_alias="translatedSummary")
    locations: list[LocationHolder] | None = None
    reprint: bool | None = None
    reprint_group_id: str | None = Field(None, validation_alias="reprintGroupId", serialization_alias="reprintGroupId")
    places: list[Place] | None = None
    people: list[PersonHolder] | None = None
    cluster: NewsCluster | None = None
    journalists: list[Journalist] | None = None
    highlights: dict[str, list[str]] | None = None
    vectors: list[VectorData] | None = None

class ArticleSearchFilter(PermissiveModel):
    """Complex filter structure for article searches that supports nested logical operations (AND, OR, NOT) and multiple filtering criteria."""
    article_id: list[str] | None = Field(None, validation_alias="articleId", serialization_alias="articleId", description="Filter by specific article identifiers. Accepts either a single ID or an array of IDs. Returns only articles matching these IDs.")
    cluster_id: list[str] | None = Field(None, validation_alias="clusterId", serialization_alias="clusterId", description="Filter by specific story identifiers. Accepts either a single ID or an array of IDs. Returns only articles belonging to these stories.")
    source: list[str] | None = Field(None, description="Filter articles by specific publisher domains or subdomains. Accepts either a single domain or an array of domains. Multiple values create an OR filter.")
    exclude_source: list[str] | None = Field(None, validation_alias="excludeSource", serialization_alias="excludeSource", description="Exclude articles from specific publisher domains or subdomains. Accepts either a single domain or an array of domains. Multiple values create an AND-exclude filter.")
    source_group: list[str] | None = Field(None, validation_alias="sourceGroup", serialization_alias="sourceGroup", description="Filter articles using Perigon's curated publisher bundles (e.g., top100, top25tech). Accepts either a single source group or an array. Multiple values create an OR filter to include articles from any of the specified bundles.")
    language: list[str] | None = Field(None, description="Filter articles by their language using ISO-639 two-letter codes in lowercase (e.g., en, es, fr). Accepts either a single language code or an array. Multiple values create an OR filter.")
    exclude_language: list[str] | None = Field(None, validation_alias="excludeLanguage", serialization_alias="excludeLanguage", description="Exclude articles in specific languages using ISO-639 two-letter codes in lowercase. Accepts either a single language code or an array. Multiple values create an AND-exclude filter.")
    label: list[str] | None = Field(None, description="Filter articles by editorial labels such as Opinion, Paid-news, Non-news, Fact Check, or Press Release. View our docs for an exhaustive list of labels. Accepts either a single label or an array. Multiple values create an OR filter.")
    exclude_label: list[str] | None = Field(None, validation_alias="excludeLabel", serialization_alias="excludeLabel", description="Exclude articles with specific editorial labels. Accepts either a single label or an array. Multiple values create an AND-exclude filter, removing all content with any of these labels.")
    taxonomy: list[str] | None = Field(None, description="Filter by Google Content Categories. Must pass the full hierarchical path of the category. Accepts either a single path or an array. Example: taxonomy=/Finance/Banking/Other,/Finance/Investing/Funds. Multiple values create an OR filter.")
    category: list[str] | None = Field(None, description="Filter by broad content categories such as Politics, Tech, Sports, Business, or Finance. Accepts either a single category or an array. Use none to find uncategorized articles. Multiple values create an OR filter.")
    topic: list[str] | None = Field(None, description="Filter by specific topics such as Markets, Crime, Cryptocurrency, or College Sports. Accepts either a single topic or an array. Topics are more granular than categories, and articles can have multiple topics. Multiple values create an OR filter.")
    exclude_topic: list[str] | None = Field(None, validation_alias="excludeTopic", serialization_alias="excludeTopic", description="Exclude articles with specific topics. Accepts either a single topic or an array. Multiple values create an AND-exclude filter, removing all content with any of these topics.")
    country: list[str] | None = Field(None, description="Filter articles by countries they mention using two-letter country codes in lowercase (e.g., us, gb, jp). Accepts either a single country code or an array. Multiple values create an OR filter. See documentation for supported country codes.")
    exclude_country: list[str] | None = Field(None, validation_alias="excludeCountry", serialization_alias="excludeCountry", description="Exclude articles from specific countries using two-letter country codes in lowercase. Accepts either a single country code or an array. Multiple values create an AND-exclude filter. See documentation for supported country codes.")
    locations_country: list[str] | None = Field(None, validation_alias="locationsCountry", serialization_alias="locationsCountry", description="Filter articles where specified countries play a central role in the content, not just mentioned. Uses two-letter country codes in lowercase. Accepts either a single country code or an array. Multiple values create an OR filter. See documentation for supported country codes.")
    exclude_locations_country: list[str] | None = Field(None, validation_alias="excludeLocationsCountry", serialization_alias="excludeLocationsCountry", description="Exclude articles where specified countries play a central role in the content. Accepts either a single country code or an array. Multiple values create an AND-exclude filter, removing articles focused on any of these countries. See documentation for supported country codes.")
    state: list[str] | None = Field(None, description="Filter articles where specified states play a central role in the content. Accepts either a single state code or an array. Multiple values create an OR filter. Uses two-letter state codes in lowercase. See documentation for supported state codes.")
    exclude_state: list[str] | None = Field(None, validation_alias="excludeState", serialization_alias="excludeState", description="Exclude articles where specified states play a central role. Accepts either a single state code or an array. Multiple values create an AND-exclude filter, removing articles focused on any of these states. See documentation for supported state codes.")
    county: list[str] | None = Field(None, description="Filter articles that mention or are related to specific counties. Accepts either a single county name or an array. Multiple values create an OR filter. County names typically include the word 'County' (e.g., Los Angeles County).")
    exclude_county: list[str] | None = Field(None, validation_alias="excludeCounty", serialization_alias="excludeCounty", description="Exclude articles that mention or are related to specific counties. Accepts either a single county name or an array. Multiple values create an AND-exclude filter. County names should match the format in article metadata (e.g., Los Angeles County, Cook County).")
    city: list[str] | None = Field(None, description="Filter articles that mention or are related to specific cities. Accepts either a single city name or an array. Multiple values create an OR filter.")
    exclude_city: list[str] | None = Field(None, validation_alias="excludeCity", serialization_alias="excludeCity", description="Exclude articles that mention or are related to specific cities. Accepts either a single city name or an array. Multiple values create an AND-exclude filter.")
    source_country: list[str] | None = Field(None, validation_alias="sourceCountry", serialization_alias="sourceCountry", description="Filter for articles from publishers based in specific countries. Accepts either a single country code or an array. Uses two-letter country codes in lowercase (e.g., us, gb). See documentation for supported country codes.")
    source_state: list[str] | None = Field(None, validation_alias="sourceState", serialization_alias="sourceState", description="Filter for articles from publishers based in specific states or regions. Accepts either a single state code or an array. Uses two-letter state codes in lowercase. See documentation for supported state codes.")
    source_county: list[str] | None = Field(None, validation_alias="sourceCounty", serialization_alias="sourceCounty", description="Filter for articles from publishers based in specific counties. Accepts either a single county name or an array. Multiple values create an OR filter.")
    source_city: list[str] | None = Field(None, validation_alias="sourceCity", serialization_alias="sourceCity", description="Filter for articles from publishers based in specific cities. Accepts either a single city name or an array. Multiple values create an OR filter.")
    coordinates: CoordinateFilter | None = None
    source_coordinates: CoordinateFilter | None = Field(None, validation_alias="sourceCoordinates", serialization_alias="sourceCoordinates")
    company_id: list[str] | None = Field(None, validation_alias="companyId", serialization_alias="companyId", description="Filter articles by company identifiers. Accepts either a single ID or an array. Multiple values create an OR filter. For a complete list of tracked companies and their IDs, refer to the /companies endpoint.")
    exclude_company_id: list[str] | None = Field(None, validation_alias="excludeCompanyId", serialization_alias="excludeCompanyId", description="Exclude articles mentioning companies with specific identifiers. Accepts either a single ID or an array. Multiple values create an AND-exclude filter. For a complete list of tracked companies and their IDs, refer to the /companies endpoint.")
    company_domain: list[str] | None = Field(None, validation_alias="companyDomain", serialization_alias="companyDomain", description="Filter articles by company domains (e.g., apple.com). Accepts either a single domain or an array. Multiple values create an OR filter. For a complete list of tracked companies and their domains, refer to the /companies endpoint.")
    exclude_company_domain: list[str] | None = Field(None, validation_alias="excludeCompanyDomain", serialization_alias="excludeCompanyDomain", description="Exclude articles related to companies with specific domains. Accepts either a single domain or an array. Multiple values create an AND-exclude filter. For a complete list of tracked companies and their domains, refer to the /companies endpoint.")
    company_symbol: list[str] | None = Field(None, validation_alias="companySymbol", serialization_alias="companySymbol", description="Filter articles by company stock symbols (e.g., AAPL, MSFT). Accepts either a single symbol or an array. Multiple values create an OR filter. For a complete list of tracked companies and their symbols, refer to the /companies endpoint.")
    exclude_company_symbol: list[str] | None = Field(None, validation_alias="excludeCompanySymbol", serialization_alias="excludeCompanySymbol", description="Exclude articles related to companies with specific stock symbols. Accepts either a single symbol or an array. Multiple values create an AND-exclude filter. For a complete list of tracked companies and their symbols, refer to the /companies endpoint.")
    company_name: list[str] | None = Field(None, validation_alias="companyName", serialization_alias="companyName", description="Filter articles by company name mentions. Accepts either a single name or an array. Performs exact matching on company names. Multiple values create an OR filter. For a complete list of tracked companies and their names, refer to the /companies endpoint.")
    person_wikidata_id: list[str] | None = Field(None, validation_alias="personWikidataId", serialization_alias="personWikidataId", description="Filter articles by Wikidata IDs of mentioned people. Accepts either a single ID or an array. Multiple values create an OR filter. For a complete list of tracked individuals and their Wikidata IDs, refer to the /people endpoint.")
    exclude_person_wikidata_id: list[str] | None = Field(None, validation_alias="excludePersonWikidataId", serialization_alias="excludePersonWikidataId", description="Exclude articles mentioning people with specific Wikidata IDs. Accepts either a single ID or an array. Multiple values create an AND-exclude filter. For a complete list of tracked individuals and their Wikidata IDs, refer to the /people endpoint.")
    person_name: list[str] | None = Field(None, validation_alias="personName", serialization_alias="personName", description="Filter articles by exact person name matches. Accepts either a single name or an array. Does not support Boolean operators or wildcards. Multiple values create an OR filter. For a complete list of tracked individuals and their names, refer to the /people endpoint.")
    exclude_person_name: list[str] | None = Field(None, validation_alias="excludePersonName", serialization_alias="excludePersonName", description="Exclude articles mentioning specific people by name. Accepts either a single name or an array. Multiple values create an AND-exclude filter. For a complete list of tracked individuals and their names, refer to the /people endpoint.")
    and_: list[ArticleSearchFilter] | None = Field(None, validation_alias="AND", serialization_alias="AND", description="Adds additional AND filter objects. These objects must be of the same type as the original filter object and will be combined with the existing filter using the AND logical operator.")
    or_: list[ArticleSearchFilter] | None = Field(None, validation_alias="OR", serialization_alias="OR", description="Adds additional OR filter objects. These objects must be of the same type as the original filter object and will be combined with the existing filter using the OR logical operator.")
    not_: list[ArticleSearchFilter] | None = Field(None, validation_alias="NOT", serialization_alias="NOT", description="A filter object for logical NOT operations")

class NewsCluster(PermissiveModel):
    created_at: str | None = Field(None, validation_alias="createdAt", serialization_alias="createdAt")
    updated_at: str | None = Field(None, validation_alias="updatedAt", serialization_alias="updatedAt")
    initialized_at: str | None = Field(None, validation_alias="initializedAt", serialization_alias="initializedAt")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    duplicate_of: str | None = Field(None, validation_alias="duplicateOf", serialization_alias="duplicateOf")
    slug: str | None = None
    name: str | None = None
    summary: str | None = None
    short_summary: str | None = Field(None, validation_alias="shortSummary", serialization_alias="shortSummary")
    summary_references: list[str] | None = Field(None, validation_alias="summaryReferences", serialization_alias="summaryReferences")
    image_source: SourceHolder | None = Field(None, validation_alias="imageSource", serialization_alias="imageSource")
    image_url: str | None = Field(None, validation_alias="imageUrl", serialization_alias="imageUrl")
    key_points: list[KeyPoint] | None = Field(None, validation_alias="keyPoints", serialization_alias="keyPoints")
    questions: list[Question] | None = None
    unique_sources: list[str] | None = Field(None, validation_alias="uniqueSources", serialization_alias="uniqueSources")
    selected_articles: list[Article] | None = Field(None, validation_alias="selectedArticles", serialization_alias="selectedArticles")
    sentiment: SentimentHolder | None = None
    unique_count: int | None = Field(None, validation_alias="uniqueCount", serialization_alias="uniqueCount", json_schema_extra={'format': 'int32'})
    reprint_count: int | None = Field(None, validation_alias="reprintCount", serialization_alias="reprintCount", json_schema_extra={'format': 'int32'})
    total_count: int | None = Field(None, validation_alias="totalCount", serialization_alias="totalCount", json_schema_extra={'format': 'int32'})
    countries: list[RecordStatHolder] | None = None
    top_countries: list[str] | None = Field(None, validation_alias="topCountries", serialization_alias="topCountries")
    topics: list[RecordStatHolder] | None = None
    top_topics: list[TopicHolder] | None = Field(None, validation_alias="topTopics", serialization_alias="topTopics")
    categories: list[RecordStatHolder] | None = None
    top_categories: list[CategoryHolder] | None = Field(None, validation_alias="topCategories", serialization_alias="topCategories")
    taxonomies: list[RecordStatHolder] | None = None
    top_taxonomies: list[CategoryHolder] | None = Field(None, validation_alias="topTaxonomies", serialization_alias="topTaxonomies")
    people: list[PersonCount] | None = None
    top_people: list[PersonHolder] | None = Field(None, validation_alias="topPeople", serialization_alias="topPeople")
    companies: list[CompanyCount] | None = None
    top_companies: list[CompanyHolder] | None = Field(None, validation_alias="topCompanies", serialization_alias="topCompanies")
    locations: list[LocationCount] | None = None
    top_locations: list[LocationHolder] | None = Field(None, validation_alias="topLocations", serialization_alias="topLocations")
    highlights: dict[str, list[str]] | None = None

class VectorSearchArticlesBodyFilter(PermissiveModel):
    article_id: list[str] | None = Field(None, validation_alias="articleId", serialization_alias="articleId", description="Filter by specific article identifiers. Accepts either a single ID or an array of IDs. Returns only articles matching these IDs.")
    cluster_id: list[str] | None = Field(None, validation_alias="clusterId", serialization_alias="clusterId", description="Filter by specific story identifiers. Accepts either a single ID or an array of IDs. Returns only articles belonging to these stories.")
    source: list[str] | None = Field(None, description="Filter articles by specific publisher domains or subdomains. Accepts either a single domain or an array of domains. Multiple values create an OR filter.")
    exclude_source: list[str] | None = Field(None, validation_alias="excludeSource", serialization_alias="excludeSource", description="Exclude articles from specific publisher domains or subdomains. Accepts either a single domain or an array of domains. Multiple values create an AND-exclude filter.")
    source_group: list[str] | None = Field(None, validation_alias="sourceGroup", serialization_alias="sourceGroup", description="Filter articles using Perigon's curated publisher bundles (e.g., top100, top25tech). Accepts either a single source group or an array. Multiple values create an OR filter to include articles from any of the specified bundles.")
    language: list[str] | None = Field(None, description="Filter articles by their language using ISO-639 two-letter codes in lowercase (e.g., en, es, fr). Accepts either a single language code or an array. Multiple values create an OR filter.")
    exclude_language: list[str] | None = Field(None, validation_alias="excludeLanguage", serialization_alias="excludeLanguage", description="Exclude articles in specific languages using ISO-639 two-letter codes in lowercase. Accepts either a single language code or an array. Multiple values create an AND-exclude filter.")
    label: list[str] | None = Field(None, description="Filter articles by editorial labels such as Opinion, Paid-news, Non-news, Fact Check, or Press Release. View our docs for an exhaustive list of labels. Accepts either a single label or an array. Multiple values create an OR filter.")
    exclude_label: list[str] | None = Field(None, validation_alias="excludeLabel", serialization_alias="excludeLabel", description="Exclude articles with specific editorial labels. Accepts either a single label or an array. Multiple values create an AND-exclude filter, removing all content with any of these labels.")
    taxonomy: list[str] | None = Field(None, description="Filter by Google Content Categories. Must pass the full hierarchical path of the category. Accepts either a single path or an array. Example: taxonomy=/Finance/Banking/Other,/Finance/Investing/Funds. Multiple values create an OR filter.")
    category: list[str] | None = Field(None, description="Filter by broad content categories such as Politics, Tech, Sports, Business, or Finance. Accepts either a single category or an array. Use none to find uncategorized articles. Multiple values create an OR filter.")
    topic: list[str] | None = Field(None, description="Filter by specific topics such as Markets, Crime, Cryptocurrency, or College Sports. Accepts either a single topic or an array. Topics are more granular than categories, and articles can have multiple topics. Multiple values create an OR filter.")
    exclude_topic: list[str] | None = Field(None, validation_alias="excludeTopic", serialization_alias="excludeTopic", description="Exclude articles with specific topics. Accepts either a single topic or an array. Multiple values create an AND-exclude filter, removing all content with any of these topics.")
    country: list[str] | None = Field(None, description="Filter articles by countries they mention using two-letter country codes in lowercase (e.g., us, gb, jp). Accepts either a single country code or an array. Multiple values create an OR filter. See documentation for supported country codes.")
    exclude_country: list[str] | None = Field(None, validation_alias="excludeCountry", serialization_alias="excludeCountry", description="Exclude articles from specific countries using two-letter country codes in lowercase. Accepts either a single country code or an array. Multiple values create an AND-exclude filter. See documentation for supported country codes.")
    locations_country: list[str] | None = Field(None, validation_alias="locationsCountry", serialization_alias="locationsCountry", description="Filter articles where specified countries play a central role in the content, not just mentioned. Uses two-letter country codes in lowercase. Accepts either a single country code or an array. Multiple values create an OR filter. See documentation for supported country codes.")
    exclude_locations_country: list[str] | None = Field(None, validation_alias="excludeLocationsCountry", serialization_alias="excludeLocationsCountry", description="Exclude articles where specified countries play a central role in the content. Accepts either a single country code or an array. Multiple values create an AND-exclude filter, removing articles focused on any of these countries. See documentation for supported country codes.")
    state: list[str] | None = Field(None, description="Filter articles where specified states play a central role in the content. Accepts either a single state code or an array. Multiple values create an OR filter. Uses two-letter state codes in lowercase. See documentation for supported state codes.")
    exclude_state: list[str] | None = Field(None, validation_alias="excludeState", serialization_alias="excludeState", description="Exclude articles where specified states play a central role. Accepts either a single state code or an array. Multiple values create an AND-exclude filter, removing articles focused on any of these states. See documentation for supported state codes.")
    county: list[str] | None = Field(None, description="Filter articles that mention or are related to specific counties. Accepts either a single county name or an array. Multiple values create an OR filter. County names typically include the word 'County' (e.g., Los Angeles County).")
    exclude_county: list[str] | None = Field(None, validation_alias="excludeCounty", serialization_alias="excludeCounty", description="Exclude articles that mention or are related to specific counties. Accepts either a single county name or an array. Multiple values create an AND-exclude filter. County names should match the format in article metadata (e.g., Los Angeles County, Cook County).")
    city: list[str] | None = Field(None, description="Filter articles that mention or are related to specific cities. Accepts either a single city name or an array. Multiple values create an OR filter.")
    exclude_city: list[str] | None = Field(None, validation_alias="excludeCity", serialization_alias="excludeCity", description="Exclude articles that mention or are related to specific cities. Accepts either a single city name or an array. Multiple values create an AND-exclude filter.")
    source_country: list[str] | None = Field(None, validation_alias="sourceCountry", serialization_alias="sourceCountry", description="Filter for articles from publishers based in specific countries. Accepts either a single country code or an array. Uses two-letter country codes in lowercase (e.g., us, gb). See documentation for supported country codes.")
    source_state: list[str] | None = Field(None, validation_alias="sourceState", serialization_alias="sourceState", description="Filter for articles from publishers based in specific states or regions. Accepts either a single state code or an array. Uses two-letter state codes in lowercase. See documentation for supported state codes.")
    source_county: list[str] | None = Field(None, validation_alias="sourceCounty", serialization_alias="sourceCounty", description="Filter for articles from publishers based in specific counties. Accepts either a single county name or an array. Multiple values create an OR filter.")
    source_city: list[str] | None = Field(None, validation_alias="sourceCity", serialization_alias="sourceCity", description="Filter for articles from publishers based in specific cities. Accepts either a single city name or an array. Multiple values create an OR filter.")
    coordinates: VectorSearchArticlesBodyFilterCoordinates | None = None
    source_coordinates: VectorSearchArticlesBodyFilterSourceCoordinates | None = Field(None, validation_alias="sourceCoordinates", serialization_alias="sourceCoordinates")
    company_id: list[str] | None = Field(None, validation_alias="companyId", serialization_alias="companyId", description="Filter articles by company identifiers. Accepts either a single ID or an array. Multiple values create an OR filter. For a complete list of tracked companies and their IDs, refer to the /companies endpoint.")
    exclude_company_id: list[str] | None = Field(None, validation_alias="excludeCompanyId", serialization_alias="excludeCompanyId", description="Exclude articles mentioning companies with specific identifiers. Accepts either a single ID or an array. Multiple values create an AND-exclude filter. For a complete list of tracked companies and their IDs, refer to the /companies endpoint.")
    company_domain: list[str] | None = Field(None, validation_alias="companyDomain", serialization_alias="companyDomain", description="Filter articles by company domains (e.g., apple.com). Accepts either a single domain or an array. Multiple values create an OR filter. For a complete list of tracked companies and their domains, refer to the /companies endpoint.")
    exclude_company_domain: list[str] | None = Field(None, validation_alias="excludeCompanyDomain", serialization_alias="excludeCompanyDomain", description="Exclude articles related to companies with specific domains. Accepts either a single domain or an array. Multiple values create an AND-exclude filter. For a complete list of tracked companies and their domains, refer to the /companies endpoint.")
    company_symbol: list[str] | None = Field(None, validation_alias="companySymbol", serialization_alias="companySymbol", description="Filter articles by company stock symbols (e.g., AAPL, MSFT). Accepts either a single symbol or an array. Multiple values create an OR filter. For a complete list of tracked companies and their symbols, refer to the /companies endpoint.")
    exclude_company_symbol: list[str] | None = Field(None, validation_alias="excludeCompanySymbol", serialization_alias="excludeCompanySymbol", description="Exclude articles related to companies with specific stock symbols. Accepts either a single symbol or an array. Multiple values create an AND-exclude filter. For a complete list of tracked companies and their symbols, refer to the /companies endpoint.")
    company_name: list[str] | None = Field(None, validation_alias="companyName", serialization_alias="companyName", description="Filter articles by company name mentions. Accepts either a single name or an array. Performs exact matching on company names. Multiple values create an OR filter. For a complete list of tracked companies and their names, refer to the /companies endpoint.")
    person_wikidata_id: list[str] | None = Field(None, validation_alias="personWikidataId", serialization_alias="personWikidataId", description="Filter articles by Wikidata IDs of mentioned people. Accepts either a single ID or an array. Multiple values create an OR filter. For a complete list of tracked individuals and their Wikidata IDs, refer to the /people endpoint.")
    exclude_person_wikidata_id: list[str] | None = Field(None, validation_alias="excludePersonWikidataId", serialization_alias="excludePersonWikidataId", description="Exclude articles mentioning people with specific Wikidata IDs. Accepts either a single ID or an array. Multiple values create an AND-exclude filter. For a complete list of tracked individuals and their Wikidata IDs, refer to the /people endpoint.")
    person_name: list[str] | None = Field(None, validation_alias="personName", serialization_alias="personName", description="Filter articles by exact person name matches. Accepts either a single name or an array. Does not support Boolean operators or wildcards. Multiple values create an OR filter. For a complete list of tracked individuals and their names, refer to the /people endpoint.")
    exclude_person_name: list[str] | None = Field(None, validation_alias="excludePersonName", serialization_alias="excludePersonName", description="Exclude articles mentioning specific people by name. Accepts either a single name or an array. Multiple values create an AND-exclude filter. For a complete list of tracked individuals and their names, refer to the /people endpoint.")
    and_: list[ArticleSearchFilter] | None = Field(None, validation_alias="AND", serialization_alias="AND", description="Adds additional AND filter objects. These objects must be of the same type as the original filter object and will be combined with the existing filter using the AND logical operator.")
    or_: list[ArticleSearchFilter] | None = Field(None, validation_alias="OR", serialization_alias="OR", description="Adds additional OR filter objects. These objects must be of the same type as the original filter object and will be combined with the existing filter using the OR logical operator.")
    not_: list[ArticleSearchFilter] | None = Field(None, validation_alias="NOT", serialization_alias="NOT", description="A filter object for logical NOT operations")

class VectorSearchWikipediaBodyFilter(PermissiveModel):
    page_id: list[str] | None = Field(None, validation_alias="pageId", serialization_alias="pageId", description="Filter by specific Perigon page identifiers. Accepts either a single ID or an array of IDs. Returns only pages matching these IDs.")
    section_id: list[str] | None = Field(None, validation_alias="sectionId", serialization_alias="sectionId", description="Filter by specific section identifiers. Accepts either a single ID or an array of IDs. Returns only pages containing these sections.")
    wiki_page_id: list[int] | None = Field(None, validation_alias="wikiPageId", serialization_alias="wikiPageId", description="Filter by specific Wikipedia page identifiers. Accepts either a single ID or an array of IDs. Returns only pages matching these IDs.")
    wiki_revision_id: list[int] | None = Field(None, validation_alias="wikiRevisionId", serialization_alias="wikiRevisionId", description="Filter by specific Perigon page revision identifiers. Accepts either a single ID or an array of IDs. Returns only pages matching these IDs.")
    wiki_code: list[str] | None = Field(None, validation_alias="wikiCode", serialization_alias="wikiCode", description="Filter by specific Wikipedia project codes. Returns only pages matching these projects.")
    wiki_namespace: list[int] | None = Field(None, validation_alias="wikiNamespace", serialization_alias="wikiNamespace", description="Filter by specific Wikipedia namespaces. Returns only pages matching these namespaces.")
    wikidata_id: list[str] | None = Field(None, validation_alias="wikidataId", serialization_alias="wikidataId", description="Filter by specific Wikidata entity IDs. Returns only pages whose Wikidata entities match those ids.")
    wikidata_instance_of_id: list[str] | None = Field(None, validation_alias="wikidataInstanceOfId", serialization_alias="wikidataInstanceOfId", description="Filter by specific Wikidata entity IDs. Returns only pages whose Wikidata entities are instances of provided ids.")
    wikidata_instance_of_label: list[str] | None = Field(None, validation_alias="wikidataInstanceOfLabel", serialization_alias="wikidataInstanceOfLabel", description="Filter by specific Wikidata entity labels. Returns only pages whose Wikidata entities are instances of these labels.")
    and_: list[WikipediaSearchFilter] | None = Field(None, validation_alias="AND", serialization_alias="AND", description="Adds additional AND filter objects. These objects must be of the same type as the original filter object and will be combined with the existing filter using the AND logical operator.")
    or_: list[WikipediaSearchFilter] | None = Field(None, validation_alias="OR", serialization_alias="OR", description="Adds additional OR filter objects. These objects must be of the same type as the original filter object and will be combined with the existing filter using the OR logical operator.")
    not_: list[WikipediaSearchFilter] | None = Field(None, validation_alias="NOT", serialization_alias="NOT", description="A filter object for logical NOT operations")

class WikipediaSearchFilter(PermissiveModel):
    """Complex filter structure for Wikipedia page searches that supports nested logical operations (AND, OR, NOT) and multiple filtering criteria."""
    page_id: list[str] | None = Field(None, validation_alias="pageId", serialization_alias="pageId", description="Filter by specific Perigon page identifiers. Accepts either a single ID or an array of IDs. Returns only pages matching these IDs.")
    section_id: list[str] | None = Field(None, validation_alias="sectionId", serialization_alias="sectionId", description="Filter by specific section identifiers. Accepts either a single ID or an array of IDs. Returns only pages containing these sections.")
    wiki_page_id: list[int] | None = Field(None, validation_alias="wikiPageId", serialization_alias="wikiPageId", description="Filter by specific Wikipedia page identifiers. Accepts either a single ID or an array of IDs. Returns only pages matching these IDs.")
    wiki_revision_id: list[int] | None = Field(None, validation_alias="wikiRevisionId", serialization_alias="wikiRevisionId", description="Filter by specific Perigon page revision identifiers. Accepts either a single ID or an array of IDs. Returns only pages matching these IDs.")
    wiki_code: list[str] | None = Field(None, validation_alias="wikiCode", serialization_alias="wikiCode", description="Filter by specific Wikipedia project codes. Returns only pages matching these projects.")
    wiki_namespace: list[int] | None = Field(None, validation_alias="wikiNamespace", serialization_alias="wikiNamespace", description="Filter by specific Wikipedia namespaces. Returns only pages matching these namespaces.")
    wikidata_id: list[str] | None = Field(None, validation_alias="wikidataId", serialization_alias="wikidataId", description="Filter by specific Wikidata entity IDs. Returns only pages whose Wikidata entities match those ids.")
    wikidata_instance_of_id: list[str] | None = Field(None, validation_alias="wikidataInstanceOfId", serialization_alias="wikidataInstanceOfId", description="Filter by specific Wikidata entity IDs. Returns only pages whose Wikidata entities are instances of provided ids.")
    wikidata_instance_of_label: list[str] | None = Field(None, validation_alias="wikidataInstanceOfLabel", serialization_alias="wikidataInstanceOfLabel", description="Filter by specific Wikidata entity labels. Returns only pages whose Wikidata entities are instances of these labels.")
    and_: list[WikipediaSearchFilter] | None = Field(None, validation_alias="AND", serialization_alias="AND", description="Adds additional AND filter objects. These objects must be of the same type as the original filter object and will be combined with the existing filter using the AND logical operator.")
    or_: list[WikipediaSearchFilter] | None = Field(None, validation_alias="OR", serialization_alias="OR", description="Adds additional OR filter objects. These objects must be of the same type as the original filter object and will be combined with the existing filter using the OR logical operator.")
    not_: list[WikipediaSearchFilter] | None = Field(None, validation_alias="NOT", serialization_alias="NOT", description="A filter object for logical NOT operations")


# Rebuild models to resolve forward references (required for circular refs)
Article.model_rebuild()
ArticleSearchFilter.model_rebuild()
CategoryHolder.model_rebuild()
CategoryWithScoreHolder.model_rebuild()
CompanyCount.model_rebuild()
CompanyHolder.model_rebuild()
Coordinate.model_rebuild()
CoordinateFilter.model_rebuild()
EntityHolder.model_rebuild()
EventTypeHolder.model_rebuild()
IdNameHolder.model_rebuild()
Journalist.model_rebuild()
KeyPoint.model_rebuild()
KeywordHolder.model_rebuild()
LabelHolder.model_rebuild()
LocationCount.model_rebuild()
LocationHolder.model_rebuild()
NameCount.model_rebuild()
NewsCluster.model_rebuild()
PersonCount.model_rebuild()
PersonHolder.model_rebuild()
Place.model_rebuild()
Question.model_rebuild()
RecordStatHolder.model_rebuild()
SentimentHolder.model_rebuild()
SourceHolder.model_rebuild()
SourceLocation.model_rebuild()
TopicHolder.model_rebuild()
VectorData.model_rebuild()
VectorSearchArticlesBodyFilter.model_rebuild()
VectorSearchArticlesBodyFilterCoordinates.model_rebuild()
VectorSearchArticlesBodyFilterSourceCoordinates.model_rebuild()
VectorSearchWikipediaBodyFilter.model_rebuild()
WikipediaSearchFilter.model_rebuild()

"""
Algolia Search MCP Server - Pydantic Models

Generated: 2026-05-05 14:09:00 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "CustomPostRequest",
    "GetRecommendationsRequest",
    "SearchRequest",
    "BoughtTogetherQuery",
    "LookingSimilarQuery",
    "RelatedQuery",
    "SearchForFacets",
    "SearchForHits",
    "TrendingFacetsQuery",
    "TrendingItemsQuery",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: send_custom_post_request
class CustomPostRequestPath(StrictModel):
    path: str = Field(default=..., description="The relative path of the Algolia REST API endpoint to target, starting after the base URL.")
class CustomPostRequestQuery(StrictModel):
    parameters: dict[str, Any] | None = Field(default=None, description="Optional key-value pairs to include as URL query parameters with the request.")
class CustomPostRequestBody(StrictModel):
    """Parameters to send with the custom request."""
    body: dict[str, Any] | None = Field(default=None, description="Optional JSON object to send as the POST request body payload.")
class CustomPostRequest(StrictModel):
    """Send a custom POST request directly to any Algolia REST API endpoint. Useful for accessing new or undocumented features not yet covered by dedicated methods."""
    path: CustomPostRequestPath
    query: CustomPostRequestQuery | None = None
    body: CustomPostRequestBody | None = None

# Operation: search_multiple_indices
class SearchRequestBody(StrictModel):
    """Muli-search request body. Results are returned in the same order as the requests."""
    requests: list[SearchForHits | SearchForFacets] = Field(default=..., description="List of search requests to execute, where each item specifies the target index, query, and any search parameters. Order determines execution sequence when using the stopIfEnoughMatches strategy.")
    strategy: Literal["none", "stopIfEnoughMatches"] | None = Field(default=None, description="Controls how multiple queries are executed: run all queries regardless of results (none), or stop early once any query returns at least hitsPerPage results (stopIfEnoughMatches).")
class SearchRequest(StrictModel):
    """Executes multiple search queries across one or more indices in a single request, useful for querying different indices simultaneously or applying varied filters to the same index."""
    body: SearchRequestBody

# Operation: get_recommendations
class GetRecommendationsRequestBody(StrictModel):
    requests: list[BoughtTogetherQuery | RelatedQuery | TrendingItemsQuery | TrendingFacetsQuery | LookingSimilarQuery] = Field(default=..., description="List of recommendation requests to execute, each specifying the target index, AI model, and model-specific parameters. Multiple requests can be batched together; order of items determines order of results returned.")
class GetRecommendationsRequest(StrictModel):
    """Retrieves AI-powered recommendations (e.g., related products, frequently bought together) from Algolia's recommendation models. Supports multiple concurrent recommendation requests in a single call."""
    body: GetRecommendationsRequestBody

# ============================================================================
# Component Models
# ============================================================================

class AnalyticsTags(RootModel[list[str]]):
    pass

class AroundPrecisionFromValueItem(PermissiveModel):
    """Range object with lower and upper values in meters to define custom ranges."""
    from_: int | None = Field(None, validation_alias="from", serialization_alias="from", description="Lower boundary of a range in meters. The Geo ranking criterion considers all records within the range to be equal.")
    value: int | None = Field(None, description="Upper boundary of a range in meters. The Geo ranking criterion considers all records within the range to be equal.")

class AroundPrecisionFromValue(RootModel[list[AroundPrecisionFromValueItem]]):
    pass

class AroundPrecision(PermissiveModel):
    """Precision of a coordinate-based search in meters to group results with similar distances.

The Geo ranking criterion considers all matches within the same range of distances to be equal.
"""
    around_precision: int | AroundPrecisionFromValue

class AttributesToHighlight(RootModel[list[str]]):
    pass

class AttributesToRetrieve(RootModel[list[str]]):
    pass

class AttributesToSnippet(RootModel[list[str]]):
    pass

class BannerImageUrl(StrictModel):
    """URL for an image to show inside a banner."""
    url: str | None = None

class BannerImage(StrictModel):
    """Image to show inside a banner."""
    urls: list[BannerImageUrl] | None = None
    title: str | None = None

class BannerLink(StrictModel):
    """Link for a banner defined in the Merchandising Studio."""
    url: str | None = None

class Banner(StrictModel):
    """Banner with image and link to redirect users."""
    image: BannerImage | None = None
    link: BannerLink | None = None

class Banners(RootModel[list[Banner]]):
    pass

class DisableExactOnAttributes(RootModel[list[str]]):
    pass

class DisableTypoToleranceOnAttributes(RootModel[list[str]]):
    pass

class FacetFilters(PermissiveModel):
    """Filter the search by facet values, so that only records with the same facet values are retrieved.

**Prefer using the `filters` parameter, which supports all filter types and combinations with boolean operators.**

- `[filter1, filter2]` is interpreted as `filter1 AND filter2`.
- `[[filter1, filter2], filter3]` is interpreted as `filter1 OR filter2 AND filter3`.
- `facet:-value` is interpreted as `NOT facet:value`.

While it's best to avoid attributes that start with a `-`, you can still filter them by escaping with a backslash:
`facet:\\-value`.
"""
    facet_filters: list[FacetFilters] | str

class Facets(RootModel[list[str]]):
    pass

class Hide(RootModel[list[str]]):
    pass

class IndexSettingsAdvancedSyntaxFeatures(RootModel[list[Literal["exactPhrase", "excludeWords"]]]):
    pass

class IndexSettingsAlternativesAsExact(RootModel[list[Literal["ignorePlurals", "singleWordSynonym", "multiWordsSynonym", "ignoreConjugations"]]]):
    pass

class InsideBoundingBoxArray(RootModel[list[list[float]]]):
    pass

class InsideBoundingBox(PermissiveModel):
    inside_bounding_box: str | InsideBoundingBoxArray

class InsidePolygon(RootModel[list[list[float]]]):
    pass

class NaturalLanguages(RootModel[list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]]]):
    pass

class NumericFilters(PermissiveModel):
    """Filter by numeric facets.

**Prefer using the `filters` parameter, which supports all filter types and combinations with boolean operators.**

You can use numeric comparison operators: `<`, `<=`, `=`, `!=`, `>`, `>=`.
Comparisons are precise up to 3 decimals.
You can also provide ranges: `facet:<lower> TO <upper>`. The range includes the lower and upper boundaries.
The same combination rules apply as for `facetFilters`.
"""
    numeric_filters: list[NumericFilters] | str

class OptionalFilters(PermissiveModel):
    """Filters to promote or demote records in the search results.

Optional filters work like facet filters, but they don't exclude records from the search results.
Records that match the optional filter rank before records that don't match.
If you're using a negative filter `facet:-value`, matching records rank after records that don't match.

- Optional filters are applied _after_ sort-by attributes.
- Optional filters are applied _before_ custom ranking attributes (in the default [ranking](https://www.algolia.com/doc/guides/managing-results/relevance-overview/in-depth/ranking-criteria)).
- Optional filters don't work with numeric attributes.
- On virtual replicas, optional filters are applied _after_ the replica's [relevant sort](https://www.algolia.com/doc/guides/managing-results/refine-results/sorting/in-depth/relevant-sort).
"""
    optional_filters: list[OptionalFilters] | str

class OptionalWordsArray(RootModel[list[str]]):
    pass

class OptionalWords(PermissiveModel):
    """Words that should be considered optional when found in the query.

By default, records must match all words in the search query to be included in the search results.
Adding optional words can increase the number of search results by running an additional search query that doesn't include the optional words.
For example, if the search query is "action video" and "video" is optional,
the search engine runs two queries: one for "action video" and one for "action".
Records that match all words are ranked higher.

For a search query with 4 or more words **and** all its words are optional,
the number of matched words required for a record to be included in the search results increases for every 1,000 records:

- If `optionalWords` has fewer than 10 words, the required number of matched words increases by 1:
  results 1 to 1,000 require 1 matched word; results 1,001 to 2,000 need 2 matched words.
- If `optionalWords` has 10 or more words, the required number of matched words increases by the number of optional words divided by 5 (rounded down).
  Example: with 18 optional words, results 1 to 1,000 require 1 matched word; results 1,001 to 2,000 need 4 matched words.

For more information, see [Optional words](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/empty-or-insufficient-results/#creating-a-list-of-optional-words).
"""
    optional_words: str | OptionalWordsArray

class Order(RootModel[list[str]]):
    pass

class IndexSettingsFacets(StrictModel):
    """Order of facet names."""
    order: Order | None = None

class QueryLanguages(RootModel[list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]]]):
    pass

class Ranking(RootModel[list[str]]):
    pass

class ReRankingApplyFilter(PermissiveModel):
    """Restrict [Dynamic Re-Ranking](https://www.algolia.com/doc/guides/algolia-ai/re-ranking) to records that match these filters.
"""
    re_ranking_apply_filter: list[ReRankingApplyFilter] | str

class RedirectUrl(StrictModel):
    """The redirect rule container."""
    url: str | None = None

class ResponseFields(RootModel[list[str]]):
    pass

class RestrictSearchableAttributes(RootModel[list[str]]):
    pass

class RuleContexts(RootModel[list[str]]):
    pass

class SearchForFacetsOptions(PermissiveModel):
    facet: str = Field(..., description="Facet name.")
    index_name: str = Field(..., validation_alias="indexName", serialization_alias="indexName")
    facet_query: str | None = Field(None, validation_alias="facetQuery", serialization_alias="facetQuery")
    max_facet_hits: int | None = Field(None, validation_alias="maxFacetHits", serialization_alias="maxFacetHits")
    type_: Literal["facet"] = Field(..., validation_alias="type", serialization_alias="type")

class SearchForHitsOptions(PermissiveModel):
    index_name: str = Field(..., validation_alias="indexName", serialization_alias="indexName")
    type_: Literal["default"] | None = Field(None, validation_alias="type", serialization_alias="type")

class SearchParamsQuery(StrictModel):
    query: str | None = None

class SearchParamsString(StrictModel):
    """Search parameters as query string."""
    params: str | None = None

class SemanticSearch(PermissiveModel):
    """Settings for the semantic search part of NeuralSearch.
Only used when `mode` is `neuralSearch`.
"""
    event_sources: list[str] | None = Field(None, validation_alias="eventSources", serialization_alias="eventSources", description="Indices from which to collect click and conversion events.\n\nIf null, the current index and all its replicas are used.\n")

class TagFilters(PermissiveModel):
    """Filter the search by values of the special `_tags` attribute.

**Prefer using the `filters` parameter, which supports all filter types and combinations with boolean operators.**

Different from regular facets, `_tags` can only be used for filtering (including or excluding records).
You won't get a facet count.
The same combination and escaping rules apply as for `facetFilters`.
"""
    tag_filters: list[TagFilters] | str

class BaseRecommendSearchParams(StrictModel):
    similar_query: str | None = Field(None, validation_alias="similarQuery", serialization_alias="similarQuery")
    filters: str | None = None
    facet_filters: FacetFilters | None = Field(None, validation_alias="facetFilters", serialization_alias="facetFilters")
    optional_filters: OptionalFilters | None = Field(None, validation_alias="optionalFilters", serialization_alias="optionalFilters")
    numeric_filters: NumericFilters | None = Field(None, validation_alias="numericFilters", serialization_alias="numericFilters")
    tag_filters: TagFilters | None = Field(None, validation_alias="tagFilters", serialization_alias="tagFilters")
    sum_or_filters_scores: bool | None = Field(None, validation_alias="sumOrFiltersScores", serialization_alias="sumOrFiltersScores")
    restrict_searchable_attributes: RestrictSearchableAttributes | None = Field(None, validation_alias="restrictSearchableAttributes", serialization_alias="restrictSearchableAttributes")
    facets: Facets | None = None
    faceting_after_distinct: bool | None = Field(None, validation_alias="facetingAfterDistinct", serialization_alias="facetingAfterDistinct")
    around_lat_lng: str | None = Field(None, validation_alias="aroundLatLng", serialization_alias="aroundLatLng")
    around_lat_lng_via_ip: bool | None = Field(None, validation_alias="aroundLatLngViaIP", serialization_alias="aroundLatLngViaIP")
    around_radius: int | Literal["all"] | None = Field(None, validation_alias="aroundRadius", serialization_alias="aroundRadius")
    around_precision: AroundPrecision | None = Field(None, validation_alias="aroundPrecision", serialization_alias="aroundPrecision")
    minimum_around_radius: int | None = Field(None, validation_alias="minimumAroundRadius", serialization_alias="minimumAroundRadius")
    inside_bounding_box: InsideBoundingBox | None = Field(None, validation_alias="insideBoundingBox", serialization_alias="insideBoundingBox")
    inside_polygon: InsidePolygon | None = Field(None, validation_alias="insidePolygon", serialization_alias="insidePolygon")
    natural_languages: NaturalLanguages | None = Field(None, validation_alias="naturalLanguages", serialization_alias="naturalLanguages")
    rule_contexts: RuleContexts | None = Field(None, validation_alias="ruleContexts", serialization_alias="ruleContexts")
    personalization_impact: int | None = Field(None, validation_alias="personalizationImpact", serialization_alias="personalizationImpact")
    user_token: str | None = Field(None, validation_alias="userToken", serialization_alias="userToken")
    get_ranking_info: bool | None = Field(None, validation_alias="getRankingInfo", serialization_alias="getRankingInfo")
    synonyms: bool | None = None
    click_analytics: bool | None = Field(None, validation_alias="clickAnalytics", serialization_alias="clickAnalytics")
    analytics: bool | None = None
    analytics_tags: AnalyticsTags | None = Field(None, validation_alias="analyticsTags", serialization_alias="analyticsTags")
    percentile_computation: bool | None = Field(None, validation_alias="percentileComputation", serialization_alias="percentileComputation")
    enable_ab_test: bool | None = Field(None, validation_alias="enableABTest", serialization_alias="enableABTest")

class BaseSearchParamsWithoutQuery(StrictModel):
    similar_query: str | None = Field(None, validation_alias="similarQuery", serialization_alias="similarQuery")
    filters: str | None = None
    facet_filters: FacetFilters | None = Field(None, validation_alias="facetFilters", serialization_alias="facetFilters")
    optional_filters: OptionalFilters | None = Field(None, validation_alias="optionalFilters", serialization_alias="optionalFilters")
    numeric_filters: NumericFilters | None = Field(None, validation_alias="numericFilters", serialization_alias="numericFilters")
    tag_filters: TagFilters | None = Field(None, validation_alias="tagFilters", serialization_alias="tagFilters")
    sum_or_filters_scores: bool | None = Field(None, validation_alias="sumOrFiltersScores", serialization_alias="sumOrFiltersScores")
    restrict_searchable_attributes: RestrictSearchableAttributes | None = Field(None, validation_alias="restrictSearchableAttributes", serialization_alias="restrictSearchableAttributes")
    facets: list[str] | None = Field([], description="Facets for which to retrieve facet values that match the search criteria and the number of matching facet values\nTo retrieve all facets, use the wildcard character `*`.\nFor more information, see [facets](https://www.algolia.com/doc/guides/managing-results/refine-results/faceting/#contextual-facet-values-and-counts).\n")
    faceting_after_distinct: bool | None = Field(None, validation_alias="facetingAfterDistinct", serialization_alias="facetingAfterDistinct")
    page: int | None = None
    offset: int | None = Field(None, description="Position of the first hit to retrieve.")
    length: int | None = None
    around_lat_lng: str | None = Field(None, validation_alias="aroundLatLng", serialization_alias="aroundLatLng")
    around_lat_lng_via_ip: bool | None = Field(None, validation_alias="aroundLatLngViaIP", serialization_alias="aroundLatLngViaIP")
    around_radius: int | Literal["all"] | None = Field(None, validation_alias="aroundRadius", serialization_alias="aroundRadius")
    around_precision: AroundPrecision | None = Field(None, validation_alias="aroundPrecision", serialization_alias="aroundPrecision")
    minimum_around_radius: int | None = Field(None, validation_alias="minimumAroundRadius", serialization_alias="minimumAroundRadius")
    inside_bounding_box: InsideBoundingBox | None = Field(None, validation_alias="insideBoundingBox", serialization_alias="insideBoundingBox")
    inside_polygon: InsidePolygon | None = Field(None, validation_alias="insidePolygon", serialization_alias="insidePolygon")
    natural_languages: NaturalLanguages | None = Field(None, validation_alias="naturalLanguages", serialization_alias="naturalLanguages")
    rule_contexts: RuleContexts | None = Field(None, validation_alias="ruleContexts", serialization_alias="ruleContexts")
    personalization_impact: int | None = Field(None, validation_alias="personalizationImpact", serialization_alias="personalizationImpact")
    user_token: str | None = Field(None, validation_alias="userToken", serialization_alias="userToken")
    get_ranking_info: bool | None = Field(None, validation_alias="getRankingInfo", serialization_alias="getRankingInfo")
    synonyms: bool | None = None
    click_analytics: bool | None = Field(None, validation_alias="clickAnalytics", serialization_alias="clickAnalytics")
    analytics: bool | None = None
    analytics_tags: AnalyticsTags | None = Field(None, validation_alias="analyticsTags", serialization_alias="analyticsTags")
    percentile_computation: bool | None = Field(None, validation_alias="percentileComputation", serialization_alias="percentileComputation")
    enable_ab_test: bool | None = Field(None, validation_alias="enableABTest", serialization_alias="enableABTest")

class BaseSearchParams(PermissiveModel):
    query: str | None = None
    similar_query: str | None = Field(None, validation_alias="similarQuery", serialization_alias="similarQuery")
    filters: str | None = None
    facet_filters: FacetFilters | None = Field(None, validation_alias="facetFilters", serialization_alias="facetFilters")
    optional_filters: OptionalFilters | None = Field(None, validation_alias="optionalFilters", serialization_alias="optionalFilters")
    numeric_filters: NumericFilters | None = Field(None, validation_alias="numericFilters", serialization_alias="numericFilters")
    tag_filters: TagFilters | None = Field(None, validation_alias="tagFilters", serialization_alias="tagFilters")
    sum_or_filters_scores: bool | None = Field(None, validation_alias="sumOrFiltersScores", serialization_alias="sumOrFiltersScores")
    restrict_searchable_attributes: RestrictSearchableAttributes | None = Field(None, validation_alias="restrictSearchableAttributes", serialization_alias="restrictSearchableAttributes")
    facets: list[str] | None = Field([], description="Facets for which to retrieve facet values that match the search criteria and the number of matching facet values\nTo retrieve all facets, use the wildcard character `*`.\nFor more information, see [facets](https://www.algolia.com/doc/guides/managing-results/refine-results/faceting/#contextual-facet-values-and-counts).\n")
    faceting_after_distinct: bool | None = Field(None, validation_alias="facetingAfterDistinct", serialization_alias="facetingAfterDistinct")
    page: int | None = None
    offset: int | None = Field(None, description="Position of the first hit to retrieve.")
    length: int | None = None
    around_lat_lng: str | None = Field(None, validation_alias="aroundLatLng", serialization_alias="aroundLatLng")
    around_lat_lng_via_ip: bool | None = Field(None, validation_alias="aroundLatLngViaIP", serialization_alias="aroundLatLngViaIP")
    around_radius: int | Literal["all"] | None = Field(None, validation_alias="aroundRadius", serialization_alias="aroundRadius")
    around_precision: AroundPrecision | None = Field(None, validation_alias="aroundPrecision", serialization_alias="aroundPrecision")
    minimum_around_radius: int | None = Field(None, validation_alias="minimumAroundRadius", serialization_alias="minimumAroundRadius")
    inside_bounding_box: InsideBoundingBox | None = Field(None, validation_alias="insideBoundingBox", serialization_alias="insideBoundingBox")
    inside_polygon: InsidePolygon | None = Field(None, validation_alias="insidePolygon", serialization_alias="insidePolygon")
    natural_languages: NaturalLanguages | None = Field(None, validation_alias="naturalLanguages", serialization_alias="naturalLanguages")
    rule_contexts: RuleContexts | None = Field(None, validation_alias="ruleContexts", serialization_alias="ruleContexts")
    personalization_impact: int | None = Field(None, validation_alias="personalizationImpact", serialization_alias="personalizationImpact")
    user_token: str | None = Field(None, validation_alias="userToken", serialization_alias="userToken")
    get_ranking_info: bool | None = Field(None, validation_alias="getRankingInfo", serialization_alias="getRankingInfo")
    synonyms: bool | None = None
    click_analytics: bool | None = Field(None, validation_alias="clickAnalytics", serialization_alias="clickAnalytics")
    analytics: bool | None = None
    analytics_tags: AnalyticsTags | None = Field(None, validation_alias="analyticsTags", serialization_alias="analyticsTags")
    percentile_computation: bool | None = Field(None, validation_alias="percentileComputation", serialization_alias="percentileComputation")
    enable_ab_test: bool | None = Field(None, validation_alias="enableABTest", serialization_alias="enableABTest")

class TrendingFacets(StrictModel):
    index_name: str = Field(..., validation_alias="indexName", serialization_alias="indexName")
    threshold: float = Field(..., description="Minimum score a recommendation must have to be included in the response.", ge=0, le=100, json_schema_extra={'format': 'double'})
    max_recommendations: int | None = Field(30, validation_alias="maxRecommendations", serialization_alias="maxRecommendations", description="Maximum number of recommendations to retrieve.\nBy default, all recommendations are returned and no fallback request is made.\nDepending on the available recommendations and the other request parameters,\nthe actual number of recommendations may be lower than this value.\n", ge=1, le=30)
    facet_name: str = Field(..., validation_alias="facetName", serialization_alias="facetName", description="Facet attribute for which to retrieve trending facet values.")
    model: Literal["trending-facets"]

class TrendingFacetsQuery(PermissiveModel):
    index_name: str = Field(..., validation_alias="indexName", serialization_alias="indexName")
    threshold: float = Field(..., description="Minimum score a recommendation must have to be included in the response.", ge=0, le=100, json_schema_extra={'format': 'double'})
    max_recommendations: int | None = Field(30, validation_alias="maxRecommendations", serialization_alias="maxRecommendations", description="Maximum number of recommendations to retrieve.\nBy default, all recommendations are returned and no fallback request is made.\nDepending on the available recommendations and the other request parameters,\nthe actual number of recommendations may be lower than this value.\n", ge=1, le=30)
    facet_name: str = Field(..., validation_alias="facetName", serialization_alias="facetName", description="Facet attribute for which to retrieve trending facet values.")
    model: Literal["trending-facets"]

class UserData(PermissiveModel):
    """An object with custom data.

You can store up to 32kB as custom data.
"""
    pass

class BaseIndexSettings(StrictModel):
    attributes_for_faceting: list[str] | None = Field([], validation_alias="attributesForFaceting", serialization_alias="attributesForFaceting", description="Attributes used for [faceting](https://www.algolia.com/doc/guides/managing-results/refine-results/faceting).\n\nFacets are attributes that let you categorize search results.\nThey can be used for filtering search results.\nBy default, no attribute is used for faceting.\nAttribute names are case-sensitive.\n\n**Modifiers**\n\n- `filterOnly(\"ATTRIBUTE\")`.\n  Allows the attribute to be used as a filter but doesn't evaluate the facet values.\n\n- `searchable(\"ATTRIBUTE\")`.\n  Allows searching for facet values.\n\n- `afterDistinct(\"ATTRIBUTE\")`.\n  Evaluates the facet count _after_ deduplication with `distinct`.\n  This ensures accurate facet counts.\n  You can apply this modifier to searchable facets: `afterDistinct(searchable(ATTRIBUTE))`.\n")
    replicas: list[str] | None = Field([], description="Creates [replica indices](https://www.algolia.com/doc/guides/managing-results/refine-results/sorting/in-depth/replicas).\n\nReplicas are copies of a primary index with the same records but different settings, synonyms, or rules.\nIf you want to offer a different ranking or sorting of your search results, you'll use replica indices.\nAll index operations on a primary index are automatically forwarded to its replicas.\nTo add a replica index, you must provide the complete set of replicas to this parameter.\nIf you omit a replica from this list, the replica turns into a regular, standalone index that will no longer be synced with the primary index.\n\n**Modifier**\n\n- `virtual(\"REPLICA\")`.\n  Create a virtual replica,\n  Virtual replicas don't increase the number of records and are optimized for [Relevant sorting](https://www.algolia.com/doc/guides/managing-results/refine-results/sorting/in-depth/relevant-sort).\n")
    pagination_limited_to: int | None = Field(1000, validation_alias="paginationLimitedTo", serialization_alias="paginationLimitedTo", description="Maximum number of search results that can be obtained through pagination.\n\nHigher pagination limits might slow down your search.\nFor pagination limits above 1,000, the sorting of results beyond the 1,000th hit can't be guaranteed.\n", le=20000)
    unretrievable_attributes: list[str] | None = Field([], validation_alias="unretrievableAttributes", serialization_alias="unretrievableAttributes", description="Attributes that can't be retrieved at query time.\n\nThis can be useful if you want to use an attribute for ranking or to [restrict access](https://www.algolia.com/doc/guides/security/api-keys/how-to/user-restricted-access-to-data),\nbut don't want to include it in the search results.\nAttribute names are case-sensitive.\n")
    disable_typo_tolerance_on_words: list[str] | None = Field([], validation_alias="disableTypoToleranceOnWords", serialization_alias="disableTypoToleranceOnWords", description="Creates a list of [words which require exact matches](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/typo-tolerance/in-depth/configuring-typo-tolerance/#turn-off-typo-tolerance-for-certain-words).\nThis also turns off [word splitting and concatenation](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/in-depth/splitting-and-concatenation) for the specified words.\n")
    attributes_to_transliterate: list[str] | None = Field(None, validation_alias="attributesToTransliterate", serialization_alias="attributesToTransliterate", description="Attributes, for which you want to support [Japanese transliteration](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/in-depth/language-specific-configurations/#japanese-transliteration-and-type-ahead).\n\nTransliteration supports searching in any of the Japanese writing systems.\nTo support transliteration, you must set the indexing language to Japanese.\nAttribute names are case-sensitive.\n")
    camel_case_attributes: list[str] | None = Field([], validation_alias="camelCaseAttributes", serialization_alias="camelCaseAttributes", description="Attributes for which to split [camel case](https://wikipedia.org/wiki/Camel_case) words.\nAttribute names are case-sensitive.\n")
    decompounded_attributes: dict[str, Any] | None = Field({}, validation_alias="decompoundedAttributes", serialization_alias="decompoundedAttributes", description="Searchable attributes to which Algolia should apply [word segmentation](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/how-to/customize-segmentation) (decompounding).\nAttribute names are case-sensitive.\n\nCompound words are formed by combining two or more individual words,\nand are particularly prevalent in Germanic languages—for example, \"firefighter\".\nWith decompounding, the individual components are indexed separately.\n\nYou can specify different lists for different languages.\nDecompounding is supported for these languages:\nDutch (`nl`), German (`de`), Finnish (`fi`), Danish (`da`), Swedish (`sv`), and Norwegian (`no`).\nDecompounding doesn't work for words with [non-spacing mark Unicode characters](https://www.charactercodes.net/category/non-spacing_mark).\nFor example, `Gartenstühle` won't be decompounded if the `ü` consists of `u` (U+0075) and `◌̈` (U+0308).\n")
    index_languages: list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]] | None = Field(None, validation_alias="indexLanguages", serialization_alias="indexLanguages", description="Languages for language-specific processing steps, such as word detection and dictionary settings.\n\n**Always specify an indexing language.**\nIf you don't specify an indexing language, the search engine uses all [supported languages](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/in-depth/supported-languages),\nor the languages you specified with the `ignorePlurals` or `removeStopWords` parameters.\nThis can lead to unexpected search results.\nFor more information, see [Language-specific configuration](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/in-depth/language-specific-configurations).\n")
    disable_prefix_on_attributes: list[str] | None = Field([], validation_alias="disablePrefixOnAttributes", serialization_alias="disablePrefixOnAttributes", description="Searchable attributes for which you want to turn off [prefix matching](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/override-search-engine-defaults/#adjusting-prefix-search).\nAttribute names are case-sensitive.\n")
    allow_compression_of_integer_array: bool | None = Field(False, validation_alias="allowCompressionOfIntegerArray", serialization_alias="allowCompressionOfIntegerArray", description="Whether arrays with exclusively non-negative integers should be compressed for better performance.\nIf true, the compressed arrays may be reordered.\n")
    numeric_attributes_for_filtering: list[str] | None = Field([], validation_alias="numericAttributesForFiltering", serialization_alias="numericAttributesForFiltering", description="Numeric attributes that can be used as [numerical filters](https://www.algolia.com/doc/guides/managing-results/rules/detecting-intent/how-to/applying-a-custom-filter-for-a-specific-query/#numerical-filters).\nAttribute names are case-sensitive.\n\nBy default, all numeric attributes are available as numerical filters.\nFor faster indexing, reduce the number of numeric attributes.\n\nTo turn off filtering for all numeric attributes, specify an attribute that doesn't exist in your index, such as `NO_NUMERIC_FILTERING`.\n\n**Modifier**\n\n- `equalOnly(\"ATTRIBUTE\")`.\n  Support only filtering based on equality comparisons `=` and `!=`.\n")
    separators_to_index: str | None = Field('', validation_alias="separatorsToIndex", serialization_alias="separatorsToIndex", description="Control which non-alphanumeric characters are indexed.\n\nBy default, Algolia ignores [non-alphanumeric characters](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/typo-tolerance/how-to/how-to-search-in-hyphenated-attributes/#handling-non-alphanumeric-characters) like hyphen (`-`), plus (`+`), and parentheses (`(`,`)`).\nTo include such characters, define them with `separatorsToIndex`.\n\nSeparators are all non-letter characters except spaces and currency characters, such as $€£¥.\n\nWith `separatorsToIndex`, Algolia treats separator characters as separate words.\nFor example, in a search for \"Disney+\", Algolia considers \"Disney\" and \"+\" as two separate words.\n")
    searchable_attributes: list[str] | None = Field([], validation_alias="searchableAttributes", serialization_alias="searchableAttributes", description="Attributes used for searching. Attribute names are case-sensitive.\n\nBy default, all attributes are searchable and the [Attribute](https://www.algolia.com/doc/guides/managing-results/relevance-overview/in-depth/ranking-criteria/#attribute) ranking criterion is turned off.\nWith a non-empty list, Algolia only returns results with matches in the selected attributes.\nIn addition, the Attribute ranking criterion is turned on: matches in attributes that are higher in the list of `searchableAttributes` rank first.\nTo make matches in two attributes rank equally, include them in a comma-separated string, such as `\"title,alternate_title\"`.\nAttributes with the same priority are always unordered.\n\nFor more information, see [Searchable attributes](https://www.algolia.com/doc/guides/sending-and-managing-data/prepare-your-data/how-to/setting-searchable-attributes).\n\n**Modifier**\n\n- `unordered(\"ATTRIBUTE\")`.\n  Ignore the position of a match within the attribute.\n\nWithout a modifier, matches at the beginn...")
    user_data: UserData | None = Field(None, validation_alias="userData", serialization_alias="userData")
    custom_normalization: dict[str, dict[str, str]] | None = Field(None, validation_alias="customNormalization", serialization_alias="customNormalization", description="Characters and their normalized replacements.\nThis overrides Algolia's default [normalization](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/in-depth/normalization).\n")
    attribute_for_distinct: str | None = Field(None, validation_alias="attributeForDistinct", serialization_alias="attributeForDistinct", description="Attribute that should be used to establish groups of results.\nAttribute names are case-sensitive.\n\nAll records with the same value for this attribute are considered a group.\nYou can combine `attributeForDistinct` with the `distinct` search parameter to control\nhow many items per group are included in the search results.\n\nIf you want to use the same attribute also for faceting, use the `afterDistinct` modifier of the `attributesForFaceting` setting.\nThis applies faceting _after_ deduplication, which will result in accurate facet counts.\n")
    max_facet_hits: int | None = Field(None, validation_alias="maxFacetHits", serialization_alias="maxFacetHits")
    keep_diacritics_on_characters: str | None = Field('', validation_alias="keepDiacriticsOnCharacters", serialization_alias="keepDiacriticsOnCharacters", description="Characters for which diacritics should be preserved.\n\nBy default, Algolia removes diacritics from letters.\nFor example, `é` becomes `e`. If this causes issues in your search,\nyou can specify characters that should keep their diacritics.\n")
    custom_ranking: list[str] | None = Field([], validation_alias="customRanking", serialization_alias="customRanking", description="Attributes to use as [custom ranking](https://www.algolia.com/doc/guides/managing-results/must-do/custom-ranking).\nAttribute names are case-sensitive.\n\nThe custom ranking attributes decide which items are shown first if the other ranking criteria are equal.\n\nRecords with missing values for your selected custom ranking attributes are always sorted last.\nBoolean attributes are sorted based on their alphabetical order.\n\n**Modifiers**\n\n- `asc(\"ATTRIBUTE\")`.\n  Sort the index by the values of an attribute, in ascending order.\n\n- `desc(\"ATTRIBUTE\")`.\n  Sort the index by the values of an attribute, in descending order.\n\nIf you use two or more custom ranking attributes,\n[reduce the precision](https://www.algolia.com/doc/guides/managing-results/must-do/custom-ranking/how-to/controlling-custom-ranking-metrics-precision) of your first attributes,\nor the other attributes will never be applied.\n")

class Value(StrictModel):
    order: Order | None = None
    sort_remaining_by: Literal["count", "alpha", "hidden"] | None = Field(None, validation_alias="sortRemainingBy", serialization_alias="sortRemainingBy")
    hide: Hide | None = None

class Values(RootModel[dict[str, Value]]):
    pass

class FacetOrdering(StrictModel):
    """Order of facet names and facet values in your UI."""
    facets: IndexSettingsFacets | None = None
    values: Values | None = None

class Widgets(StrictModel):
    """Widgets returned from any rules that are applied to the current search."""
    banners: Banners | None = None

class RenderingContent(StrictModel):
    """Extra data that can be used in the search UI.

You can use this to control aspects of your search UI, such as the order of facet names and values
without changing your frontend code.
"""
    facet_ordering: FacetOrdering | None = Field(None, validation_alias="facetOrdering", serialization_alias="facetOrdering")
    redirect: RedirectUrl | None = None
    widgets: Widgets | None = None

class BaseRecommendIndexSettings(StrictModel):
    attributes_to_retrieve: AttributesToRetrieve | None = Field(None, validation_alias="attributesToRetrieve", serialization_alias="attributesToRetrieve")
    ranking: Ranking | None = None
    relevancy_strictness: int | None = Field(None, validation_alias="relevancyStrictness", serialization_alias="relevancyStrictness")
    attributes_to_highlight: AttributesToHighlight | None = Field(None, validation_alias="attributesToHighlight", serialization_alias="attributesToHighlight")
    attributes_to_snippet: AttributesToSnippet | None = Field(None, validation_alias="attributesToSnippet", serialization_alias="attributesToSnippet")
    highlight_pre_tag: str | None = Field(None, validation_alias="highlightPreTag", serialization_alias="highlightPreTag")
    highlight_post_tag: str | None = Field(None, validation_alias="highlightPostTag", serialization_alias="highlightPostTag")
    snippet_ellipsis_text: str | None = Field(None, validation_alias="snippetEllipsisText", serialization_alias="snippetEllipsisText")
    restrict_highlight_and_snippet_arrays: bool | None = Field(None, validation_alias="restrictHighlightAndSnippetArrays", serialization_alias="restrictHighlightAndSnippetArrays")
    min_word_sizefor1_typo: int | None = Field(None, validation_alias="minWordSizefor1Typo", serialization_alias="minWordSizefor1Typo")
    min_word_sizefor2_typos: int | None = Field(None, validation_alias="minWordSizefor2Typos", serialization_alias="minWordSizefor2Typos")
    typo_tolerance: bool | Literal["min", "strict", "true", "false"] | None = Field(None, validation_alias="typoTolerance", serialization_alias="typoTolerance")
    allow_typos_on_numeric_tokens: bool | None = Field(None, validation_alias="allowTyposOnNumericTokens", serialization_alias="allowTyposOnNumericTokens")
    disable_typo_tolerance_on_attributes: DisableTypoToleranceOnAttributes | None = Field(None, validation_alias="disableTypoToleranceOnAttributes", serialization_alias="disableTypoToleranceOnAttributes")
    ignore_plurals: list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]] | Literal["true", "false"] | bool | None = Field(None, validation_alias="ignorePlurals", serialization_alias="ignorePlurals")
    remove_stop_words: list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]] | bool | None = Field(None, validation_alias="removeStopWords", serialization_alias="removeStopWords")
    query_languages: QueryLanguages | None = Field(None, validation_alias="queryLanguages", serialization_alias="queryLanguages")
    decompound_query: bool | None = Field(None, validation_alias="decompoundQuery", serialization_alias="decompoundQuery")
    enable_rules: bool | None = Field(None, validation_alias="enableRules", serialization_alias="enableRules")
    enable_personalization: bool | None = Field(None, validation_alias="enablePersonalization", serialization_alias="enablePersonalization")
    query_type: Literal["prefixLast", "prefixAll", "prefixNone"] | None = Field(None, validation_alias="queryType", serialization_alias="queryType")
    remove_words_if_no_results: Literal["none", "lastWords", "firstWords", "allOptional"] | None = Field(None, validation_alias="removeWordsIfNoResults", serialization_alias="removeWordsIfNoResults")
    advanced_syntax: bool | None = Field(None, validation_alias="advancedSyntax", serialization_alias="advancedSyntax")
    optional_words: OptionalWords | None = Field(None, validation_alias="optionalWords", serialization_alias="optionalWords")
    disable_exact_on_attributes: DisableExactOnAttributes | None = Field(None, validation_alias="disableExactOnAttributes", serialization_alias="disableExactOnAttributes")
    exact_on_single_word_query: Literal["attribute", "none", "word"] | None = Field(None, validation_alias="exactOnSingleWordQuery", serialization_alias="exactOnSingleWordQuery")
    alternatives_as_exact: IndexSettingsAlternativesAsExact | None = Field(None, validation_alias="alternativesAsExact", serialization_alias="alternativesAsExact")
    advanced_syntax_features: IndexSettingsAdvancedSyntaxFeatures | None = Field(None, validation_alias="advancedSyntaxFeatures", serialization_alias="advancedSyntaxFeatures")
    distinct: bool | int | None = None
    replace_synonyms_in_highlight: bool | None = Field(None, validation_alias="replaceSynonymsInHighlight", serialization_alias="replaceSynonymsInHighlight")
    min_proximity: int | None = Field(None, validation_alias="minProximity", serialization_alias="minProximity")
    response_fields: ResponseFields | None = Field(None, validation_alias="responseFields", serialization_alias="responseFields")
    max_values_per_facet: int | None = Field(None, validation_alias="maxValuesPerFacet", serialization_alias="maxValuesPerFacet")
    sort_facet_values_by: str | None = Field(None, validation_alias="sortFacetValuesBy", serialization_alias="sortFacetValuesBy")
    attribute_criteria_computed_by_min_proximity: bool | None = Field(None, validation_alias="attributeCriteriaComputedByMinProximity", serialization_alias="attributeCriteriaComputedByMinProximity")
    rendering_content: RenderingContent | None = Field(None, validation_alias="renderingContent", serialization_alias="renderingContent")
    enable_re_ranking: bool | None = Field(None, validation_alias="enableReRanking", serialization_alias="enableReRanking")
    re_ranking_apply_filter: ReRankingApplyFilter | None = Field(None, validation_alias="reRankingApplyFilter", serialization_alias="reRankingApplyFilter")

class IndexSettingsAsSearchParams(StrictModel):
    attributes_to_retrieve: AttributesToRetrieve | None = Field(None, validation_alias="attributesToRetrieve", serialization_alias="attributesToRetrieve")
    ranking: list[str] | None = Field(['typo', 'geo', 'words', 'filters', 'proximity', 'attribute', 'exact', 'custom'], description="Determines the order in which Algolia returns your results.\n\nBy default, each entry corresponds to a [ranking criteria](https://www.algolia.com/doc/guides/managing-results/relevance-overview/in-depth/ranking-criteria).\nThe tie-breaking algorithm sequentially applies each criterion in the order they're specified.\nIf you configure a replica index for [sorting by an attribute](https://www.algolia.com/doc/guides/managing-results/refine-results/sorting/how-to/sort-by-attribute),\nyou put the sorting attribute at the top of the list.\n\n**Modifiers**\n\n- `asc(\"ATTRIBUTE\")`.\n  Sort the index by the values of an attribute, in ascending order.\n- `desc(\"ATTRIBUTE\")`.\n  Sort the index by the values of an attribute, in descending order.\n\nBefore you modify the default setting,\ntest your changes in the dashboard,\nand by [A/B testing](https://www.algolia.com/doc/guides/ab-testing/what-is-ab-testing).\n")
    relevancy_strictness: int | None = Field(None, validation_alias="relevancyStrictness", serialization_alias="relevancyStrictness")
    attributes_to_highlight: AttributesToHighlight | None = Field(None, validation_alias="attributesToHighlight", serialization_alias="attributesToHighlight")
    attributes_to_snippet: AttributesToSnippet | None = Field(None, validation_alias="attributesToSnippet", serialization_alias="attributesToSnippet")
    highlight_pre_tag: str | None = Field(None, validation_alias="highlightPreTag", serialization_alias="highlightPreTag")
    highlight_post_tag: str | None = Field(None, validation_alias="highlightPostTag", serialization_alias="highlightPostTag")
    snippet_ellipsis_text: str | None = Field(None, validation_alias="snippetEllipsisText", serialization_alias="snippetEllipsisText")
    restrict_highlight_and_snippet_arrays: bool | None = Field(None, validation_alias="restrictHighlightAndSnippetArrays", serialization_alias="restrictHighlightAndSnippetArrays")
    hits_per_page: int | None = Field(None, validation_alias="hitsPerPage", serialization_alias="hitsPerPage")
    min_word_sizefor1_typo: int | None = Field(None, validation_alias="minWordSizefor1Typo", serialization_alias="minWordSizefor1Typo")
    min_word_sizefor2_typos: int | None = Field(None, validation_alias="minWordSizefor2Typos", serialization_alias="minWordSizefor2Typos")
    typo_tolerance: bool | Literal["min", "strict", "true", "false"] | None = Field(None, validation_alias="typoTolerance", serialization_alias="typoTolerance")
    allow_typos_on_numeric_tokens: bool | None = Field(None, validation_alias="allowTyposOnNumericTokens", serialization_alias="allowTyposOnNumericTokens")
    disable_typo_tolerance_on_attributes: DisableTypoToleranceOnAttributes | None = Field(None, validation_alias="disableTypoToleranceOnAttributes", serialization_alias="disableTypoToleranceOnAttributes")
    ignore_plurals: list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]] | Literal["true", "false"] | bool | None = Field(None, validation_alias="ignorePlurals", serialization_alias="ignorePlurals")
    remove_stop_words: list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]] | bool | None = Field(None, validation_alias="removeStopWords", serialization_alias="removeStopWords")
    query_languages: QueryLanguages | None = Field(None, validation_alias="queryLanguages", serialization_alias="queryLanguages")
    decompound_query: bool | None = Field(None, validation_alias="decompoundQuery", serialization_alias="decompoundQuery")
    enable_rules: bool | None = Field(None, validation_alias="enableRules", serialization_alias="enableRules")
    enable_personalization: bool | None = Field(None, validation_alias="enablePersonalization", serialization_alias="enablePersonalization")
    query_type: Literal["prefixLast", "prefixAll", "prefixNone"] | None = Field(None, validation_alias="queryType", serialization_alias="queryType")
    remove_words_if_no_results: Literal["none", "lastWords", "firstWords", "allOptional"] | None = Field(None, validation_alias="removeWordsIfNoResults", serialization_alias="removeWordsIfNoResults")
    mode: Literal["neuralSearch", "keywordSearch"] | None = None
    semantic_search: SemanticSearch | None = Field(None, validation_alias="semanticSearch", serialization_alias="semanticSearch")
    advanced_syntax: bool | None = Field(None, validation_alias="advancedSyntax", serialization_alias="advancedSyntax")
    optional_words: OptionalWords | None = Field(None, validation_alias="optionalWords", serialization_alias="optionalWords")
    disable_exact_on_attributes: DisableExactOnAttributes | None = Field(None, validation_alias="disableExactOnAttributes", serialization_alias="disableExactOnAttributes")
    exact_on_single_word_query: Literal["attribute", "none", "word"] | None = Field(None, validation_alias="exactOnSingleWordQuery", serialization_alias="exactOnSingleWordQuery")
    alternatives_as_exact: IndexSettingsAlternativesAsExact | None = Field(None, validation_alias="alternativesAsExact", serialization_alias="alternativesAsExact")
    advanced_syntax_features: IndexSettingsAdvancedSyntaxFeatures | None = Field(None, validation_alias="advancedSyntaxFeatures", serialization_alias="advancedSyntaxFeatures")
    distinct: bool | int | None = None
    replace_synonyms_in_highlight: bool | None = Field(None, validation_alias="replaceSynonymsInHighlight", serialization_alias="replaceSynonymsInHighlight")
    min_proximity: int | None = Field(None, validation_alias="minProximity", serialization_alias="minProximity")
    response_fields: ResponseFields | None = Field(None, validation_alias="responseFields", serialization_alias="responseFields")
    max_values_per_facet: int | None = Field(None, validation_alias="maxValuesPerFacet", serialization_alias="maxValuesPerFacet")
    sort_facet_values_by: str | None = Field(None, validation_alias="sortFacetValuesBy", serialization_alias="sortFacetValuesBy")
    attribute_criteria_computed_by_min_proximity: bool | None = Field(None, validation_alias="attributeCriteriaComputedByMinProximity", serialization_alias="attributeCriteriaComputedByMinProximity")
    rendering_content: RenderingContent | None = Field(None, validation_alias="renderingContent", serialization_alias="renderingContent")
    enable_re_ranking: bool | None = Field(None, validation_alias="enableReRanking", serialization_alias="enableReRanking")
    re_ranking_apply_filter: ReRankingApplyFilter | None = Field(None, validation_alias="reRankingApplyFilter", serialization_alias="reRankingApplyFilter")

class RecommendIndexSettings(PermissiveModel):
    """Index settings."""
    attributes_for_faceting: list[str] | None = Field([], validation_alias="attributesForFaceting", serialization_alias="attributesForFaceting", description="Attributes used for [faceting](https://www.algolia.com/doc/guides/managing-results/refine-results/faceting).\n\nFacets are attributes that let you categorize search results.\nThey can be used for filtering search results.\nBy default, no attribute is used for faceting.\nAttribute names are case-sensitive.\n\n**Modifiers**\n\n- `filterOnly(\"ATTRIBUTE\")`.\n  Allows the attribute to be used as a filter but doesn't evaluate the facet values.\n\n- `searchable(\"ATTRIBUTE\")`.\n  Allows searching for facet values.\n\n- `afterDistinct(\"ATTRIBUTE\")`.\n  Evaluates the facet count _after_ deduplication with `distinct`.\n  This ensures accurate facet counts.\n  You can apply this modifier to searchable facets: `afterDistinct(searchable(ATTRIBUTE))`.\n")
    replicas: list[str] | None = Field([], description="Creates [replica indices](https://www.algolia.com/doc/guides/managing-results/refine-results/sorting/in-depth/replicas).\n\nReplicas are copies of a primary index with the same records but different settings, synonyms, or rules.\nIf you want to offer a different ranking or sorting of your search results, you'll use replica indices.\nAll index operations on a primary index are automatically forwarded to its replicas.\nTo add a replica index, you must provide the complete set of replicas to this parameter.\nIf you omit a replica from this list, the replica turns into a regular, standalone index that will no longer be synced with the primary index.\n\n**Modifier**\n\n- `virtual(\"REPLICA\")`.\n  Create a virtual replica,\n  Virtual replicas don't increase the number of records and are optimized for [Relevant sorting](https://www.algolia.com/doc/guides/managing-results/refine-results/sorting/in-depth/relevant-sort).\n")
    pagination_limited_to: int | None = Field(1000, validation_alias="paginationLimitedTo", serialization_alias="paginationLimitedTo", description="Maximum number of search results that can be obtained through pagination.\n\nHigher pagination limits might slow down your search.\nFor pagination limits above 1,000, the sorting of results beyond the 1,000th hit can't be guaranteed.\n", le=20000)
    unretrievable_attributes: list[str] | None = Field([], validation_alias="unretrievableAttributes", serialization_alias="unretrievableAttributes", description="Attributes that can't be retrieved at query time.\n\nThis can be useful if you want to use an attribute for ranking or to [restrict access](https://www.algolia.com/doc/guides/security/api-keys/how-to/user-restricted-access-to-data),\nbut don't want to include it in the search results.\nAttribute names are case-sensitive.\n")
    disable_typo_tolerance_on_words: list[str] | None = Field([], validation_alias="disableTypoToleranceOnWords", serialization_alias="disableTypoToleranceOnWords", description="Creates a list of [words which require exact matches](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/typo-tolerance/in-depth/configuring-typo-tolerance/#turn-off-typo-tolerance-for-certain-words).\nThis also turns off [word splitting and concatenation](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/in-depth/splitting-and-concatenation) for the specified words.\n")
    attributes_to_transliterate: list[str] | None = Field(None, validation_alias="attributesToTransliterate", serialization_alias="attributesToTransliterate", description="Attributes, for which you want to support [Japanese transliteration](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/in-depth/language-specific-configurations/#japanese-transliteration-and-type-ahead).\n\nTransliteration supports searching in any of the Japanese writing systems.\nTo support transliteration, you must set the indexing language to Japanese.\nAttribute names are case-sensitive.\n")
    camel_case_attributes: list[str] | None = Field([], validation_alias="camelCaseAttributes", serialization_alias="camelCaseAttributes", description="Attributes for which to split [camel case](https://wikipedia.org/wiki/Camel_case) words.\nAttribute names are case-sensitive.\n")
    decompounded_attributes: dict[str, Any] | None = Field({}, validation_alias="decompoundedAttributes", serialization_alias="decompoundedAttributes", description="Searchable attributes to which Algolia should apply [word segmentation](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/how-to/customize-segmentation) (decompounding).\nAttribute names are case-sensitive.\n\nCompound words are formed by combining two or more individual words,\nand are particularly prevalent in Germanic languages—for example, \"firefighter\".\nWith decompounding, the individual components are indexed separately.\n\nYou can specify different lists for different languages.\nDecompounding is supported for these languages:\nDutch (`nl`), German (`de`), Finnish (`fi`), Danish (`da`), Swedish (`sv`), and Norwegian (`no`).\nDecompounding doesn't work for words with [non-spacing mark Unicode characters](https://www.charactercodes.net/category/non-spacing_mark).\nFor example, `Gartenstühle` won't be decompounded if the `ü` consists of `u` (U+0075) and `◌̈` (U+0308).\n")
    index_languages: list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]] | None = Field(None, validation_alias="indexLanguages", serialization_alias="indexLanguages", description="Languages for language-specific processing steps, such as word detection and dictionary settings.\n\n**Always specify an indexing language.**\nIf you don't specify an indexing language, the search engine uses all [supported languages](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/in-depth/supported-languages),\nor the languages you specified with the `ignorePlurals` or `removeStopWords` parameters.\nThis can lead to unexpected search results.\nFor more information, see [Language-specific configuration](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/in-depth/language-specific-configurations).\n")
    disable_prefix_on_attributes: list[str] | None = Field([], validation_alias="disablePrefixOnAttributes", serialization_alias="disablePrefixOnAttributes", description="Searchable attributes for which you want to turn off [prefix matching](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/override-search-engine-defaults/#adjusting-prefix-search).\nAttribute names are case-sensitive.\n")
    allow_compression_of_integer_array: bool | None = Field(False, validation_alias="allowCompressionOfIntegerArray", serialization_alias="allowCompressionOfIntegerArray", description="Whether arrays with exclusively non-negative integers should be compressed for better performance.\nIf true, the compressed arrays may be reordered.\n")
    numeric_attributes_for_filtering: list[str] | None = Field([], validation_alias="numericAttributesForFiltering", serialization_alias="numericAttributesForFiltering", description="Numeric attributes that can be used as [numerical filters](https://www.algolia.com/doc/guides/managing-results/rules/detecting-intent/how-to/applying-a-custom-filter-for-a-specific-query/#numerical-filters).\nAttribute names are case-sensitive.\n\nBy default, all numeric attributes are available as numerical filters.\nFor faster indexing, reduce the number of numeric attributes.\n\nTo turn off filtering for all numeric attributes, specify an attribute that doesn't exist in your index, such as `NO_NUMERIC_FILTERING`.\n\n**Modifier**\n\n- `equalOnly(\"ATTRIBUTE\")`.\n  Support only filtering based on equality comparisons `=` and `!=`.\n")
    separators_to_index: str | None = Field('', validation_alias="separatorsToIndex", serialization_alias="separatorsToIndex", description="Control which non-alphanumeric characters are indexed.\n\nBy default, Algolia ignores [non-alphanumeric characters](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/typo-tolerance/how-to/how-to-search-in-hyphenated-attributes/#handling-non-alphanumeric-characters) like hyphen (`-`), plus (`+`), and parentheses (`(`,`)`).\nTo include such characters, define them with `separatorsToIndex`.\n\nSeparators are all non-letter characters except spaces and currency characters, such as $€£¥.\n\nWith `separatorsToIndex`, Algolia treats separator characters as separate words.\nFor example, in a search for \"Disney+\", Algolia considers \"Disney\" and \"+\" as two separate words.\n")
    searchable_attributes: list[str] | None = Field([], validation_alias="searchableAttributes", serialization_alias="searchableAttributes", description="Attributes used for searching. Attribute names are case-sensitive.\n\nBy default, all attributes are searchable and the [Attribute](https://www.algolia.com/doc/guides/managing-results/relevance-overview/in-depth/ranking-criteria/#attribute) ranking criterion is turned off.\nWith a non-empty list, Algolia only returns results with matches in the selected attributes.\nIn addition, the Attribute ranking criterion is turned on: matches in attributes that are higher in the list of `searchableAttributes` rank first.\nTo make matches in two attributes rank equally, include them in a comma-separated string, such as `\"title,alternate_title\"`.\nAttributes with the same priority are always unordered.\n\nFor more information, see [Searchable attributes](https://www.algolia.com/doc/guides/sending-and-managing-data/prepare-your-data/how-to/setting-searchable-attributes).\n\n**Modifier**\n\n- `unordered(\"ATTRIBUTE\")`.\n  Ignore the position of a match within the attribute.\n\nWithout a modifier, matches at the beginn...")
    user_data: UserData | None = Field(None, validation_alias="userData", serialization_alias="userData")
    custom_normalization: dict[str, dict[str, str]] | None = Field(None, validation_alias="customNormalization", serialization_alias="customNormalization", description="Characters and their normalized replacements.\nThis overrides Algolia's default [normalization](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/handling-natural-languages-nlp/in-depth/normalization).\n")
    attribute_for_distinct: str | None = Field(None, validation_alias="attributeForDistinct", serialization_alias="attributeForDistinct", description="Attribute that should be used to establish groups of results.\nAttribute names are case-sensitive.\n\nAll records with the same value for this attribute are considered a group.\nYou can combine `attributeForDistinct` with the `distinct` search parameter to control\nhow many items per group are included in the search results.\n\nIf you want to use the same attribute also for faceting, use the `afterDistinct` modifier of the `attributesForFaceting` setting.\nThis applies faceting _after_ deduplication, which will result in accurate facet counts.\n")
    max_facet_hits: int | None = Field(None, validation_alias="maxFacetHits", serialization_alias="maxFacetHits")
    keep_diacritics_on_characters: str | None = Field('', validation_alias="keepDiacriticsOnCharacters", serialization_alias="keepDiacriticsOnCharacters", description="Characters for which diacritics should be preserved.\n\nBy default, Algolia removes diacritics from letters.\nFor example, `é` becomes `e`. If this causes issues in your search,\nyou can specify characters that should keep their diacritics.\n")
    custom_ranking: list[str] | None = Field([], validation_alias="customRanking", serialization_alias="customRanking", description="Attributes to use as [custom ranking](https://www.algolia.com/doc/guides/managing-results/must-do/custom-ranking).\nAttribute names are case-sensitive.\n\nThe custom ranking attributes decide which items are shown first if the other ranking criteria are equal.\n\nRecords with missing values for your selected custom ranking attributes are always sorted last.\nBoolean attributes are sorted based on their alphabetical order.\n\n**Modifiers**\n\n- `asc(\"ATTRIBUTE\")`.\n  Sort the index by the values of an attribute, in ascending order.\n\n- `desc(\"ATTRIBUTE\")`.\n  Sort the index by the values of an attribute, in descending order.\n\nIf you use two or more custom ranking attributes,\n[reduce the precision](https://www.algolia.com/doc/guides/managing-results/must-do/custom-ranking/how-to/controlling-custom-ranking-metrics-precision) of your first attributes,\nor the other attributes will never be applied.\n")
    attributes_to_retrieve: AttributesToRetrieve | None = Field(None, validation_alias="attributesToRetrieve", serialization_alias="attributesToRetrieve")
    ranking: Ranking | None = None
    relevancy_strictness: int | None = Field(None, validation_alias="relevancyStrictness", serialization_alias="relevancyStrictness")
    attributes_to_highlight: AttributesToHighlight | None = Field(None, validation_alias="attributesToHighlight", serialization_alias="attributesToHighlight")
    attributes_to_snippet: AttributesToSnippet | None = Field(None, validation_alias="attributesToSnippet", serialization_alias="attributesToSnippet")
    highlight_pre_tag: str | None = Field(None, validation_alias="highlightPreTag", serialization_alias="highlightPreTag")
    highlight_post_tag: str | None = Field(None, validation_alias="highlightPostTag", serialization_alias="highlightPostTag")
    snippet_ellipsis_text: str | None = Field(None, validation_alias="snippetEllipsisText", serialization_alias="snippetEllipsisText")
    restrict_highlight_and_snippet_arrays: bool | None = Field(None, validation_alias="restrictHighlightAndSnippetArrays", serialization_alias="restrictHighlightAndSnippetArrays")
    min_word_sizefor1_typo: int | None = Field(None, validation_alias="minWordSizefor1Typo", serialization_alias="minWordSizefor1Typo")
    min_word_sizefor2_typos: int | None = Field(None, validation_alias="minWordSizefor2Typos", serialization_alias="minWordSizefor2Typos")
    typo_tolerance: bool | Literal["min", "strict", "true", "false"] | None = Field(None, validation_alias="typoTolerance", serialization_alias="typoTolerance")
    allow_typos_on_numeric_tokens: bool | None = Field(None, validation_alias="allowTyposOnNumericTokens", serialization_alias="allowTyposOnNumericTokens")
    disable_typo_tolerance_on_attributes: DisableTypoToleranceOnAttributes | None = Field(None, validation_alias="disableTypoToleranceOnAttributes", serialization_alias="disableTypoToleranceOnAttributes")
    ignore_plurals: list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]] | Literal["true", "false"] | bool | None = Field(None, validation_alias="ignorePlurals", serialization_alias="ignorePlurals")
    remove_stop_words: list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]] | bool | None = Field(None, validation_alias="removeStopWords", serialization_alias="removeStopWords")
    query_languages: QueryLanguages | None = Field(None, validation_alias="queryLanguages", serialization_alias="queryLanguages")
    decompound_query: bool | None = Field(None, validation_alias="decompoundQuery", serialization_alias="decompoundQuery")
    enable_rules: bool | None = Field(None, validation_alias="enableRules", serialization_alias="enableRules")
    enable_personalization: bool | None = Field(None, validation_alias="enablePersonalization", serialization_alias="enablePersonalization")
    query_type: Literal["prefixLast", "prefixAll", "prefixNone"] | None = Field(None, validation_alias="queryType", serialization_alias="queryType")
    remove_words_if_no_results: Literal["none", "lastWords", "firstWords", "allOptional"] | None = Field(None, validation_alias="removeWordsIfNoResults", serialization_alias="removeWordsIfNoResults")
    advanced_syntax: bool | None = Field(None, validation_alias="advancedSyntax", serialization_alias="advancedSyntax")
    optional_words: OptionalWords | None = Field(None, validation_alias="optionalWords", serialization_alias="optionalWords")
    disable_exact_on_attributes: DisableExactOnAttributes | None = Field(None, validation_alias="disableExactOnAttributes", serialization_alias="disableExactOnAttributes")
    exact_on_single_word_query: Literal["attribute", "none", "word"] | None = Field(None, validation_alias="exactOnSingleWordQuery", serialization_alias="exactOnSingleWordQuery")
    alternatives_as_exact: IndexSettingsAlternativesAsExact | None = Field(None, validation_alias="alternativesAsExact", serialization_alias="alternativesAsExact")
    advanced_syntax_features: IndexSettingsAdvancedSyntaxFeatures | None = Field(None, validation_alias="advancedSyntaxFeatures", serialization_alias="advancedSyntaxFeatures")
    distinct: bool | int | None = None
    replace_synonyms_in_highlight: bool | None = Field(None, validation_alias="replaceSynonymsInHighlight", serialization_alias="replaceSynonymsInHighlight")
    min_proximity: int | None = Field(None, validation_alias="minProximity", serialization_alias="minProximity")
    response_fields: ResponseFields | None = Field(None, validation_alias="responseFields", serialization_alias="responseFields")
    max_values_per_facet: int | None = Field(None, validation_alias="maxValuesPerFacet", serialization_alias="maxValuesPerFacet")
    sort_facet_values_by: str | None = Field(None, validation_alias="sortFacetValuesBy", serialization_alias="sortFacetValuesBy")
    attribute_criteria_computed_by_min_proximity: bool | None = Field(None, validation_alias="attributeCriteriaComputedByMinProximity", serialization_alias="attributeCriteriaComputedByMinProximity")
    rendering_content: RenderingContent | None = Field(None, validation_alias="renderingContent", serialization_alias="renderingContent")
    enable_re_ranking: bool | None = Field(None, validation_alias="enableReRanking", serialization_alias="enableReRanking")
    re_ranking_apply_filter: ReRankingApplyFilter | None = Field(None, validation_alias="reRankingApplyFilter", serialization_alias="reRankingApplyFilter")

class RecommendSearchParams(PermissiveModel):
    """Search parameters for filtering the recommendations."""
    similar_query: str | None = Field(None, validation_alias="similarQuery", serialization_alias="similarQuery")
    filters: str | None = None
    facet_filters: FacetFilters | None = Field(None, validation_alias="facetFilters", serialization_alias="facetFilters")
    optional_filters: OptionalFilters | None = Field(None, validation_alias="optionalFilters", serialization_alias="optionalFilters")
    numeric_filters: NumericFilters | None = Field(None, validation_alias="numericFilters", serialization_alias="numericFilters")
    tag_filters: TagFilters | None = Field(None, validation_alias="tagFilters", serialization_alias="tagFilters")
    sum_or_filters_scores: bool | None = Field(None, validation_alias="sumOrFiltersScores", serialization_alias="sumOrFiltersScores")
    restrict_searchable_attributes: RestrictSearchableAttributes | None = Field(None, validation_alias="restrictSearchableAttributes", serialization_alias="restrictSearchableAttributes")
    facets: Facets | None = None
    faceting_after_distinct: bool | None = Field(None, validation_alias="facetingAfterDistinct", serialization_alias="facetingAfterDistinct")
    around_lat_lng: str | None = Field(None, validation_alias="aroundLatLng", serialization_alias="aroundLatLng")
    around_lat_lng_via_ip: bool | None = Field(None, validation_alias="aroundLatLngViaIP", serialization_alias="aroundLatLngViaIP")
    around_radius: int | Literal["all"] | None = Field(None, validation_alias="aroundRadius", serialization_alias="aroundRadius")
    around_precision: AroundPrecision | None = Field(None, validation_alias="aroundPrecision", serialization_alias="aroundPrecision")
    minimum_around_radius: int | None = Field(None, validation_alias="minimumAroundRadius", serialization_alias="minimumAroundRadius")
    inside_bounding_box: InsideBoundingBox | None = Field(None, validation_alias="insideBoundingBox", serialization_alias="insideBoundingBox")
    inside_polygon: InsidePolygon | None = Field(None, validation_alias="insidePolygon", serialization_alias="insidePolygon")
    natural_languages: NaturalLanguages | None = Field(None, validation_alias="naturalLanguages", serialization_alias="naturalLanguages")
    rule_contexts: RuleContexts | None = Field(None, validation_alias="ruleContexts", serialization_alias="ruleContexts")
    personalization_impact: int | None = Field(None, validation_alias="personalizationImpact", serialization_alias="personalizationImpact")
    user_token: str | None = Field(None, validation_alias="userToken", serialization_alias="userToken")
    get_ranking_info: bool | None = Field(None, validation_alias="getRankingInfo", serialization_alias="getRankingInfo")
    synonyms: bool | None = None
    click_analytics: bool | None = Field(None, validation_alias="clickAnalytics", serialization_alias="clickAnalytics")
    analytics: bool | None = None
    analytics_tags: AnalyticsTags | None = Field(None, validation_alias="analyticsTags", serialization_alias="analyticsTags")
    percentile_computation: bool | None = Field(None, validation_alias="percentileComputation", serialization_alias="percentileComputation")
    enable_ab_test: bool | None = Field(None, validation_alias="enableABTest", serialization_alias="enableABTest")
    query: str | None = None

class BaseRecommendRequest(StrictModel):
    index_name: str = Field(..., validation_alias="indexName", serialization_alias="indexName")
    threshold: float = Field(..., description="Minimum score a recommendation must have to be included in the response.", ge=0, le=100, json_schema_extra={'format': 'double'})
    max_recommendations: int | None = Field(30, validation_alias="maxRecommendations", serialization_alias="maxRecommendations", description="Maximum number of recommendations to retrieve.\nBy default, all recommendations are returned and no fallback request is made.\nDepending on the available recommendations and the other request parameters,\nthe actual number of recommendations may be lower than this value.\n", ge=1, le=30)
    query_parameters: RecommendSearchParams | None = Field(None, validation_alias="queryParameters", serialization_alias="queryParameters")

class FallbackParams(PermissiveModel):
    pass

class FrequentlyBoughtTogether(PermissiveModel):
    model: Literal["bought-together"]
    object_id: str = Field(..., validation_alias="objectID", serialization_alias="objectID")
    fallback_parameters: FallbackParams | None = Field(None, validation_alias="fallbackParameters", serialization_alias="fallbackParameters")

class BoughtTogetherQuery(PermissiveModel):
    index_name: str = Field(..., validation_alias="indexName", serialization_alias="indexName")
    threshold: float = Field(..., description="Minimum score a recommendation must have to be included in the response.", ge=0, le=100, json_schema_extra={'format': 'double'})
    max_recommendations: int | None = Field(30, validation_alias="maxRecommendations", serialization_alias="maxRecommendations", description="Maximum number of recommendations to retrieve.\nBy default, all recommendations are returned and no fallback request is made.\nDepending on the available recommendations and the other request parameters,\nthe actual number of recommendations may be lower than this value.\n", ge=1, le=30)
    query_parameters: RecommendSearchParams | None = Field(None, validation_alias="queryParameters", serialization_alias="queryParameters")
    model: Literal["bought-together"]
    object_id: str = Field(..., validation_alias="objectID", serialization_alias="objectID")
    fallback_parameters: FallbackParams | None = Field(None, validation_alias="fallbackParameters", serialization_alias="fallbackParameters")

class LookingSimilar(PermissiveModel):
    model: Literal["looking-similar"]
    object_id: str = Field(..., validation_alias="objectID", serialization_alias="objectID")
    fallback_parameters: FallbackParams | None = Field(None, validation_alias="fallbackParameters", serialization_alias="fallbackParameters")

class LookingSimilarQuery(PermissiveModel):
    index_name: str = Field(..., validation_alias="indexName", serialization_alias="indexName")
    threshold: float = Field(..., description="Minimum score a recommendation must have to be included in the response.", ge=0, le=100, json_schema_extra={'format': 'double'})
    max_recommendations: int | None = Field(30, validation_alias="maxRecommendations", serialization_alias="maxRecommendations", description="Maximum number of recommendations to retrieve.\nBy default, all recommendations are returned and no fallback request is made.\nDepending on the available recommendations and the other request parameters,\nthe actual number of recommendations may be lower than this value.\n", ge=1, le=30)
    query_parameters: RecommendSearchParams | None = Field(None, validation_alias="queryParameters", serialization_alias="queryParameters")
    model: Literal["looking-similar"]
    object_id: str = Field(..., validation_alias="objectID", serialization_alias="objectID")
    fallback_parameters: FallbackParams | None = Field(None, validation_alias="fallbackParameters", serialization_alias="fallbackParameters")

class RelatedProducts(PermissiveModel):
    model: Literal["related-products"]
    object_id: str = Field(..., validation_alias="objectID", serialization_alias="objectID")
    fallback_parameters: FallbackParams | None = Field(None, validation_alias="fallbackParameters", serialization_alias="fallbackParameters")

class RelatedQuery(PermissiveModel):
    index_name: str = Field(..., validation_alias="indexName", serialization_alias="indexName")
    threshold: float = Field(..., description="Minimum score a recommendation must have to be included in the response.", ge=0, le=100, json_schema_extra={'format': 'double'})
    max_recommendations: int | None = Field(30, validation_alias="maxRecommendations", serialization_alias="maxRecommendations", description="Maximum number of recommendations to retrieve.\nBy default, all recommendations are returned and no fallback request is made.\nDepending on the available recommendations and the other request parameters,\nthe actual number of recommendations may be lower than this value.\n", ge=1, le=30)
    query_parameters: RecommendSearchParams | None = Field(None, validation_alias="queryParameters", serialization_alias="queryParameters")
    model: Literal["related-products"]
    object_id: str = Field(..., validation_alias="objectID", serialization_alias="objectID")
    fallback_parameters: FallbackParams | None = Field(None, validation_alias="fallbackParameters", serialization_alias="fallbackParameters")

class SearchParamsObject(PermissiveModel):
    """Each parameter value, including the `query` must not be larger than 512 bytes."""
    attributes_to_retrieve: AttributesToRetrieve | None = Field(None, validation_alias="attributesToRetrieve", serialization_alias="attributesToRetrieve")
    ranking: list[str] | None = Field(['typo', 'geo', 'words', 'filters', 'proximity', 'attribute', 'exact', 'custom'], description="Determines the order in which Algolia returns your results.\n\nBy default, each entry corresponds to a [ranking criteria](https://www.algolia.com/doc/guides/managing-results/relevance-overview/in-depth/ranking-criteria).\nThe tie-breaking algorithm sequentially applies each criterion in the order they're specified.\nIf you configure a replica index for [sorting by an attribute](https://www.algolia.com/doc/guides/managing-results/refine-results/sorting/how-to/sort-by-attribute),\nyou put the sorting attribute at the top of the list.\n\n**Modifiers**\n\n- `asc(\"ATTRIBUTE\")`.\n  Sort the index by the values of an attribute, in ascending order.\n- `desc(\"ATTRIBUTE\")`.\n  Sort the index by the values of an attribute, in descending order.\n\nBefore you modify the default setting,\ntest your changes in the dashboard,\nand by [A/B testing](https://www.algolia.com/doc/guides/ab-testing/what-is-ab-testing).\n")
    relevancy_strictness: int | None = Field(None, validation_alias="relevancyStrictness", serialization_alias="relevancyStrictness")
    attributes_to_highlight: AttributesToHighlight | None = Field(None, validation_alias="attributesToHighlight", serialization_alias="attributesToHighlight")
    attributes_to_snippet: AttributesToSnippet | None = Field(None, validation_alias="attributesToSnippet", serialization_alias="attributesToSnippet")
    highlight_pre_tag: str | None = Field(None, validation_alias="highlightPreTag", serialization_alias="highlightPreTag")
    highlight_post_tag: str | None = Field(None, validation_alias="highlightPostTag", serialization_alias="highlightPostTag")
    snippet_ellipsis_text: str | None = Field(None, validation_alias="snippetEllipsisText", serialization_alias="snippetEllipsisText")
    restrict_highlight_and_snippet_arrays: bool | None = Field(None, validation_alias="restrictHighlightAndSnippetArrays", serialization_alias="restrictHighlightAndSnippetArrays")
    hits_per_page: int | None = Field(None, validation_alias="hitsPerPage", serialization_alias="hitsPerPage")
    min_word_sizefor1_typo: int | None = Field(None, validation_alias="minWordSizefor1Typo", serialization_alias="minWordSizefor1Typo")
    min_word_sizefor2_typos: int | None = Field(None, validation_alias="minWordSizefor2Typos", serialization_alias="minWordSizefor2Typos")
    typo_tolerance: bool | Literal["min", "strict", "true", "false"] | None = Field(None, validation_alias="typoTolerance", serialization_alias="typoTolerance")
    allow_typos_on_numeric_tokens: bool | None = Field(None, validation_alias="allowTyposOnNumericTokens", serialization_alias="allowTyposOnNumericTokens")
    disable_typo_tolerance_on_attributes: DisableTypoToleranceOnAttributes | None = Field(None, validation_alias="disableTypoToleranceOnAttributes", serialization_alias="disableTypoToleranceOnAttributes")
    ignore_plurals: list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]] | Literal["true", "false"] | bool | None = Field(None, validation_alias="ignorePlurals", serialization_alias="ignorePlurals")
    remove_stop_words: list[Literal["af", "ar", "az", "bg", "bn", "ca", "cs", "cy", "da", "de", "el", "en", "eo", "es", "et", "eu", "fa", "fi", "fo", "fr", "ga", "gl", "he", "hi", "hu", "hy", "id", "is", "it", "ja", "ka", "kk", "ko", "ku", "ky", "lt", "lv", "mi", "mn", "mr", "ms", "mt", "nb", "nl", "no", "ns", "pl", "ps", "pt", "pt-br", "qu", "ro", "ru", "sk", "sq", "sv", "sw", "ta", "te", "th", "tl", "tn", "tr", "tt", "uk", "ur", "uz", "zh"]] | bool | None = Field(None, validation_alias="removeStopWords", serialization_alias="removeStopWords")
    query_languages: QueryLanguages | None = Field(None, validation_alias="queryLanguages", serialization_alias="queryLanguages")
    decompound_query: bool | None = Field(None, validation_alias="decompoundQuery", serialization_alias="decompoundQuery")
    enable_rules: bool | None = Field(None, validation_alias="enableRules", serialization_alias="enableRules")
    enable_personalization: bool | None = Field(None, validation_alias="enablePersonalization", serialization_alias="enablePersonalization")
    query_type: Literal["prefixLast", "prefixAll", "prefixNone"] | None = Field(None, validation_alias="queryType", serialization_alias="queryType")
    remove_words_if_no_results: Literal["none", "lastWords", "firstWords", "allOptional"] | None = Field(None, validation_alias="removeWordsIfNoResults", serialization_alias="removeWordsIfNoResults")
    mode: Literal["neuralSearch", "keywordSearch"] | None = None
    semantic_search: SemanticSearch | None = Field(None, validation_alias="semanticSearch", serialization_alias="semanticSearch")
    advanced_syntax: bool | None = Field(None, validation_alias="advancedSyntax", serialization_alias="advancedSyntax")
    optional_words: OptionalWords | None = Field(None, validation_alias="optionalWords", serialization_alias="optionalWords")
    disable_exact_on_attributes: DisableExactOnAttributes | None = Field(None, validation_alias="disableExactOnAttributes", serialization_alias="disableExactOnAttributes")
    exact_on_single_word_query: Literal["attribute", "none", "word"] | None = Field(None, validation_alias="exactOnSingleWordQuery", serialization_alias="exactOnSingleWordQuery")
    alternatives_as_exact: IndexSettingsAlternativesAsExact | None = Field(None, validation_alias="alternativesAsExact", serialization_alias="alternativesAsExact")
    advanced_syntax_features: IndexSettingsAdvancedSyntaxFeatures | None = Field(None, validation_alias="advancedSyntaxFeatures", serialization_alias="advancedSyntaxFeatures")
    distinct: bool | int | None = None
    replace_synonyms_in_highlight: bool | None = Field(None, validation_alias="replaceSynonymsInHighlight", serialization_alias="replaceSynonymsInHighlight")
    min_proximity: int | None = Field(None, validation_alias="minProximity", serialization_alias="minProximity")
    response_fields: ResponseFields | None = Field(None, validation_alias="responseFields", serialization_alias="responseFields")
    max_values_per_facet: int | None = Field(None, validation_alias="maxValuesPerFacet", serialization_alias="maxValuesPerFacet")
    sort_facet_values_by: str | None = Field(None, validation_alias="sortFacetValuesBy", serialization_alias="sortFacetValuesBy")
    attribute_criteria_computed_by_min_proximity: bool | None = Field(None, validation_alias="attributeCriteriaComputedByMinProximity", serialization_alias="attributeCriteriaComputedByMinProximity")
    rendering_content: RenderingContent | None = Field(None, validation_alias="renderingContent", serialization_alias="renderingContent")
    enable_re_ranking: bool | None = Field(None, validation_alias="enableReRanking", serialization_alias="enableReRanking")
    re_ranking_apply_filter: ReRankingApplyFilter | None = Field(None, validation_alias="reRankingApplyFilter", serialization_alias="reRankingApplyFilter")

class SearchParams(PermissiveModel):
    search_params: SearchParamsString | SearchParamsObject

class SearchForFacets(PermissiveModel):
    facet: str = Field(..., description="Facet name.")
    index_name: str = Field(..., validation_alias="indexName", serialization_alias="indexName")
    facet_query: str | None = Field(None, validation_alias="facetQuery", serialization_alias="facetQuery")
    max_facet_hits: int | None = Field(None, validation_alias="maxFacetHits", serialization_alias="maxFacetHits")
    type_: Literal["facet"] = Field(..., validation_alias="type", serialization_alias="type")

class SearchForHits(PermissiveModel):
    index_name: str = Field(..., validation_alias="indexName", serialization_alias="indexName")
    type_: Literal["default"] | None = Field(None, validation_alias="type", serialization_alias="type")

class TrendingItems(PermissiveModel):
    facet_name: str | None = Field(None, validation_alias="facetName", serialization_alias="facetName")
    facet_value: str | None = Field(None, validation_alias="facetValue", serialization_alias="facetValue")
    model: Literal["trending-items"]
    fallback_parameters: FallbackParams | None = Field(None, validation_alias="fallbackParameters", serialization_alias="fallbackParameters")

class TrendingItemsQuery(PermissiveModel):
    index_name: str = Field(..., validation_alias="indexName", serialization_alias="indexName")
    threshold: float = Field(..., description="Minimum score a recommendation must have to be included in the response.", ge=0, le=100, json_schema_extra={'format': 'double'})
    max_recommendations: int | None = Field(30, validation_alias="maxRecommendations", serialization_alias="maxRecommendations", description="Maximum number of recommendations to retrieve.\nBy default, all recommendations are returned and no fallback request is made.\nDepending on the available recommendations and the other request parameters,\nthe actual number of recommendations may be lower than this value.\n", ge=1, le=30)
    query_parameters: RecommendSearchParams | None = Field(None, validation_alias="queryParameters", serialization_alias="queryParameters")
    facet_name: str | None = Field(None, validation_alias="facetName", serialization_alias="facetName")
    facet_value: str | None = Field(None, validation_alias="facetValue", serialization_alias="facetValue")
    model: Literal["trending-items"]
    fallback_parameters: FallbackParams | None = Field(None, validation_alias="fallbackParameters", serialization_alias="fallbackParameters")


# Rebuild models to resolve forward references (required for circular refs)
AnalyticsTags.model_rebuild()
AroundPrecision.model_rebuild()
AroundPrecisionFromValue.model_rebuild()
AroundPrecisionFromValueItem.model_rebuild()
AttributesToHighlight.model_rebuild()
AttributesToRetrieve.model_rebuild()
AttributesToSnippet.model_rebuild()
Banner.model_rebuild()
BannerImage.model_rebuild()
BannerImageUrl.model_rebuild()
BannerLink.model_rebuild()
Banners.model_rebuild()
BaseIndexSettings.model_rebuild()
BaseRecommendIndexSettings.model_rebuild()
BaseRecommendRequest.model_rebuild()
BaseRecommendSearchParams.model_rebuild()
BaseSearchParams.model_rebuild()
BaseSearchParamsWithoutQuery.model_rebuild()
BoughtTogetherQuery.model_rebuild()
DisableExactOnAttributes.model_rebuild()
DisableTypoToleranceOnAttributes.model_rebuild()
FacetFilters.model_rebuild()
FacetOrdering.model_rebuild()
Facets.model_rebuild()
FallbackParams.model_rebuild()
FrequentlyBoughtTogether.model_rebuild()
Hide.model_rebuild()
IndexSettingsAdvancedSyntaxFeatures.model_rebuild()
IndexSettingsAlternativesAsExact.model_rebuild()
IndexSettingsAsSearchParams.model_rebuild()
IndexSettingsFacets.model_rebuild()
InsideBoundingBox.model_rebuild()
InsideBoundingBoxArray.model_rebuild()
InsidePolygon.model_rebuild()
LookingSimilar.model_rebuild()
LookingSimilarQuery.model_rebuild()
NaturalLanguages.model_rebuild()
NumericFilters.model_rebuild()
OptionalFilters.model_rebuild()
OptionalWords.model_rebuild()
OptionalWordsArray.model_rebuild()
Order.model_rebuild()
QueryLanguages.model_rebuild()
Ranking.model_rebuild()
RecommendIndexSettings.model_rebuild()
RecommendSearchParams.model_rebuild()
RedirectUrl.model_rebuild()
RelatedProducts.model_rebuild()
RelatedQuery.model_rebuild()
RenderingContent.model_rebuild()
ReRankingApplyFilter.model_rebuild()
ResponseFields.model_rebuild()
RestrictSearchableAttributes.model_rebuild()
RuleContexts.model_rebuild()
SearchForFacets.model_rebuild()
SearchForFacetsOptions.model_rebuild()
SearchForHits.model_rebuild()
SearchForHitsOptions.model_rebuild()
SearchParams.model_rebuild()
SearchParamsObject.model_rebuild()
SearchParamsQuery.model_rebuild()
SearchParamsString.model_rebuild()
SemanticSearch.model_rebuild()
TagFilters.model_rebuild()
TrendingFacets.model_rebuild()
TrendingFacetsQuery.model_rebuild()
TrendingItems.model_rebuild()
TrendingItemsQuery.model_rebuild()
UserData.model_rebuild()
Value.model_rebuild()
Values.model_rebuild()
Widgets.model_rebuild()

"""
Shopify Admin MCP Server - Pydantic Models

Generated: 2026-05-12 12:49:30 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "CreateCustomersParamCustomerIdAccountActivationUrlRequest",
    "CreateCustomersParamCustomerIdAddressesRequest",
    "CreateCustomersParamCustomerIdSendInviteRequest",
    "CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest",
    "CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest",
    "CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest",
    "CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest",
    "CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest",
    "CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest",
    "CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest",
    "CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest",
    "CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequest",
    "CreateFulfillmentsParamFulfillmentIdCancelRequest",
    "CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest",
    "CreateGiftCardsParamGiftCardIdDisableRequest",
    "CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequest",
    "CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest",
    "CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest",
    "CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequest",
    "CreateOrdersParamOrderIdFulfillmentsRequest",
    "CreateOrdersParamOrderIdRefundsCalculateRequest",
    "CreateOrdersParamOrderIdRefundsRequest",
    "CreateOrdersParamOrderIdRisksRequest",
    "CreatePriceRulesParamPriceRuleIdBatchRequest",
    "CreatePriceRulesParamPriceRuleIdDiscountCodesRequest",
    "CreateProductsParamProductIdImagesRequest",
    "CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest",
    "DeleteBlogsParamBlogIdArticlesParamArticleIdRequest",
    "DeleteCarrierServicesParamCarrierServiceIdRequest",
    "DeleteCollectsParamCollectIdRequest",
    "DeleteCountriesParamCountryIdRequest",
    "DeleteCustomCollectionsParamCustomCollectionIdRequest",
    "DeleteCustomerSavedSearchesParamCustomerSavedSearchIdRequest",
    "DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "DeleteCustomersParamCustomerIdRequest",
    "DeleteFulfillmentServicesParamFulfillmentServiceIdRequest",
    "DeleteInventoryLevelsRequest",
    "DeleteMetafieldsParamMetafieldIdRequest",
    "DeleteOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequest",
    "DeleteOrdersParamOrderIdRisksParamRiskIdRequest",
    "DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "DeleteProductsParamProductIdImagesParamImageIdRequest",
    "DeleteProductsParamProductIdRequest",
    "DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest",
    "DeleteRedirectsParamRedirectIdRequest",
    "DeleteScriptTagsParamScriptTagIdRequest",
    "DeleteSmartCollectionsParamSmartCollectionIdRequest",
    "DeleteThemesParamThemeIdAssetsRequest",
    "DeleteThemesParamThemeIdRequest",
    "DeleteWebhooksParamWebhookIdRequest",
    "GetApplicationChargesParamApplicationChargeIdRequest",
    "GetApplicationChargesRequest",
    "GetApplicationCreditsParamApplicationCreditIdRequest",
    "GetApplicationCreditsRequest",
    "GetArticlesTagsRequest",
    "GetBlogsParamBlogIdArticlesCountRequest",
    "GetBlogsParamBlogIdArticlesParamArticleIdRequest",
    "GetBlogsParamBlogIdArticlesRequest",
    "GetCarrierServicesParamCarrierServiceIdRequest",
    "GetCheckoutsCountRequest",
    "GetCollectionsParamCollectionIdProductsRequest",
    "GetCollectionsParamCollectionIdRequest",
    "GetCollectsCountRequest",
    "GetCollectsParamCollectIdRequest",
    "GetCollectsRequest",
    "GetCountriesParamCountryIdProvincesCountRequest",
    "GetCountriesParamCountryIdProvincesParamProvinceIdRequest",
    "GetCountriesParamCountryIdProvincesRequest",
    "GetCountriesParamCountryIdRequest",
    "GetCountriesRequest",
    "GetCustomCollectionsCountRequest",
    "GetCustomCollectionsParamCustomCollectionIdRequest",
    "GetCustomCollectionsRequest",
    "GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequest",
    "GetCustomerSavedSearchesParamCustomerSavedSearchIdRequest",
    "GetCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "GetCustomersParamCustomerIdAddressesRequest",
    "GetCustomersParamCustomerIdOrdersRequest",
    "GetCustomersParamCustomerIdRequest",
    "GetCustomersRequest",
    "GetCustomersSearchRequest",
    "GetDiscountCodesLookupRequest",
    "GetEventsParamEventIdRequest",
    "GetEventsRequest",
    "GetFulfillmentOrdersParamFulfillmentOrderIdFulfillmentsRequest",
    "GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest",
    "GetFulfillmentOrdersParamFulfillmentOrderIdRequest",
    "GetFulfillmentServicesParamFulfillmentServiceIdRequest",
    "GetFulfillmentServicesRequest",
    "GetGiftCardsCountRequest",
    "GetGiftCardsParamGiftCardIdRequest",
    "GetGiftCardsRequest",
    "GetGiftCardsSearchRequest",
    "GetInventoryItemsParamInventoryItemIdRequest",
    "GetInventoryItemsRequest",
    "GetInventoryLevelsRequest",
    "GetLocationsParamLocationIdInventoryLevelsRequest",
    "GetLocationsParamLocationIdRequest",
    "GetMetafieldsParamMetafieldIdRequest",
    "GetMetafieldsRequest",
    "GetOrdersParamOrderIdFulfillmentOrdersRequest",
    "GetOrdersParamOrderIdFulfillmentsCountRequest",
    "GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequest",
    "GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest",
    "GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "GetOrdersParamOrderIdFulfillmentsRequest",
    "GetOrdersParamOrderIdRefundsParamRefundIdRequest",
    "GetOrdersParamOrderIdRefundsRequest",
    "GetOrdersParamOrderIdRisksParamRiskIdRequest",
    "GetOrdersParamOrderIdRisksRequest",
    "GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest",
    "GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest",
    "GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "GetPriceRulesParamPriceRuleIdDiscountCodesRequest",
    "GetProductsCountRequest",
    "GetProductsParamProductIdImagesCountRequest",
    "GetProductsParamProductIdImagesParamImageIdRequest",
    "GetProductsParamProductIdImagesRequest",
    "GetProductsParamProductIdRequest",
    "GetProductsRequest",
    "GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequest",
    "GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest",
    "GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest",
    "GetRecurringApplicationChargesRequest",
    "GetRedirectsCountRequest",
    "GetRedirectsParamRedirectIdRequest",
    "GetRedirectsRequest",
    "GetScriptTagsParamScriptTagIdRequest",
    "GetScriptTagsRequest",
    "GetShippingZonesRequest",
    "GetShopifyPaymentsPayoutsParamPayoutIdRequest",
    "GetShopifyPaymentsPayoutsRequest",
    "GetShopRequest",
    "GetSmartCollectionsCountRequest",
    "GetSmartCollectionsParamSmartCollectionIdRequest",
    "GetSmartCollectionsRequest",
    "GetTenderTransactionsRequest",
    "GetThemesParamThemeIdAssetsRequest",
    "GetThemesParamThemeIdRequest",
    "GetThemesRequest",
    "GetWebhooksCountRequest",
    "GetWebhooksParamWebhookIdRequest",
    "GetWebhooksRequest",
    "UpdateBlogsParamBlogIdArticlesParamArticleIdRequest",
    "UpdateCarrierServicesParamCarrierServiceIdRequest",
    "UpdateCustomCollectionsParamCustomCollectionIdRequest",
    "UpdateCustomerSavedSearchesParamCustomerSavedSearchIdRequest",
    "UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest",
    "UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "UpdateCustomersParamCustomerIdAddressesSetRequest",
    "UpdateCustomersParamCustomerIdRequest",
    "UpdateFulfillmentServicesParamFulfillmentServiceIdRequest",
    "UpdateGiftCardsParamGiftCardIdRequest",
    "UpdateInventoryItemsParamInventoryItemIdRequest",
    "UpdateMetafieldsParamMetafieldIdRequest",
    "UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "UpdateOrdersParamOrderIdRisksParamRiskIdRequest",
    "UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "UpdateProductsParamProductIdImagesParamImageIdRequest",
    "UpdateProductsParamProductIdRequest",
    "UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest",
    "UpdateRedirectsParamRedirectIdRequest",
    "UpdateScriptTagsParamScriptTagIdRequest",
    "UpdateSmartCollectionsParamSmartCollectionIdOrderRequest",
    "UpdateSmartCollectionsParamSmartCollectionIdRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_application_charges
class GetApplicationChargesRequestQuery(StrictModel):
    since_id: Any | None = Field(default=None, description="Restrict results to charges after the specified ID. Use this for cursor-based pagination to fetch subsequent pages of results.")
    fields: Any | None = Field(default=None, description="A comma-separated list of specific fields to include in the response. Omit to receive all available fields for each charge.")
class GetApplicationChargesRequest(StrictModel):
    """Retrieves a paginated list of application charges for the store. Use this to view all charges or filter results by cursor position."""
    query: GetApplicationChargesRequestQuery | None = None

# Operation: get_application_charge
class GetApplicationChargesParamApplicationChargeIdRequestPath(StrictModel):
    application_charge_id: str = Field(default=..., description="The unique identifier of the application charge to retrieve.")
class GetApplicationChargesParamApplicationChargeIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="A comma-separated list of specific fields to include in the response. If omitted, all fields are returned.")
class GetApplicationChargesParamApplicationChargeIdRequest(StrictModel):
    """Retrieves the details of a specific application charge by its ID, including status, price, and billing information."""
    path: GetApplicationChargesParamApplicationChargeIdRequestPath
    query: GetApplicationChargesParamApplicationChargeIdRequestQuery | None = None

# Operation: list_application_credits
class GetApplicationCreditsRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="A comma-separated list of field names to include in the response. Omit this parameter to return all available fields.")
class GetApplicationCreditsRequest(StrictModel):
    """Retrieves all application credits for the store. Use this to view credit transactions and their details."""
    query: GetApplicationCreditsRequestQuery | None = None

# Operation: get_application_credit
class GetApplicationCreditsParamApplicationCreditIdRequestPath(StrictModel):
    application_credit_id: str = Field(default=..., description="The unique identifier of the application credit to retrieve.")
class GetApplicationCreditsParamApplicationCreditIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="A comma-separated list of specific fields to include in the response. Omit to return all available fields.")
class GetApplicationCreditsParamApplicationCreditIdRequest(StrictModel):
    """Retrieves the details of a single application credit by its ID. Use this to fetch information about a specific credit issued to an app."""
    path: GetApplicationCreditsParamApplicationCreditIdRequestPath
    query: GetApplicationCreditsParamApplicationCreditIdRequestQuery | None = None

# Operation: list_article_tags
class GetArticlesTagsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of tags to return in the response. Limits the size of the result set.")
    popular: Any | None = Field(default=None, description="When included, orders results by tag popularity in descending order (most popular first). Omit this parameter to retrieve tags in default order.")
class GetArticlesTagsRequest(StrictModel):
    """Retrieves all tags used across articles in the online store. Results can be optionally ordered by popularity to surface the most frequently used tags."""
    query: GetArticlesTagsRequestQuery | None = None

# Operation: list_blog_articles
class GetBlogsParamBlogIdArticlesRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog from which to retrieve articles.")
class GetBlogsParamBlogIdArticlesRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of articles to return per request, between 1 and 250 (defaults to 50).")
    since_id: Any | None = Field(default=None, description="Return only articles with an ID greater than this value, useful for pagination and filtering out previously retrieved results.")
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: published (live articles only), unpublished (draft articles only), or any (all articles regardless of status). Defaults to any.")
    handle: Any | None = Field(default=None, description="Return only the article with this specific URL-friendly handle.")
    tag: Any | None = Field(default=None, description="Return only articles tagged with this specific tag.")
    author: Any | None = Field(default=None, description="Return only articles written by this specific author.")
    fields: Any | None = Field(default=None, description="Limit the response to only these fields, specified as a comma-separated list of field names. Reduces payload size when only certain article properties are needed.")
class GetBlogsParamBlogIdArticlesRequest(StrictModel):
    """Retrieves a paginated list of articles from a specific blog. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    path: GetBlogsParamBlogIdArticlesRequestPath
    query: GetBlogsParamBlogIdArticlesRequestQuery | None = None

# Operation: count_articles_in_blog
class GetBlogsParamBlogIdArticlesCountRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog for which to count articles.")
class GetBlogsParamBlogIdArticlesCountRequestQuery(StrictModel):
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: use 'published' to count only published articles, 'unpublished' to count only unpublished articles, or 'any' to count all articles regardless of status. Defaults to 'any' if not specified.")
class GetBlogsParamBlogIdArticlesCountRequest(StrictModel):
    """Retrieves the total count of articles in a specific blog, with optional filtering by publication status."""
    path: GetBlogsParamBlogIdArticlesCountRequestPath
    query: GetBlogsParamBlogIdArticlesCountRequestQuery | None = None

# Operation: get_article
class GetBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article.")
    article_id: str = Field(default=..., description="The unique identifier of the article to retrieve.")
class GetBlogsParamBlogIdArticlesParamArticleIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. If omitted, all fields are returned.")
class GetBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Retrieves a single article from a blog by its ID. Returns the full article object unless specific fields are requested."""
    path: GetBlogsParamBlogIdArticlesParamArticleIdRequestPath
    query: GetBlogsParamBlogIdArticlesParamArticleIdRequestQuery | None = None

# Operation: update_article
class UpdateBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article to update.")
    article_id: str = Field(default=..., description="The unique identifier of the article to update.")
class UpdateBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Updates an existing article within a blog. Modify article content, metadata, and publishing settings by providing the blog and article identifiers."""
    path: UpdateBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: delete_article
class DeleteBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article to delete.")
    article_id: str = Field(default=..., description="The unique identifier of the article to delete.")
class DeleteBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Permanently deletes an article from a blog. This action cannot be undone."""
    path: DeleteBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: get_carrier_service
class GetCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to retrieve.")
class GetCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Retrieves the details of a single carrier service by its unique identifier. Use this to fetch configuration and capabilities for a specific shipping carrier integration."""
    path: GetCarrierServicesParamCarrierServiceIdRequestPath

# Operation: update_carrier_service
class UpdateCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to update.")
class UpdateCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Updates an existing carrier service configuration. Only the application that originally created the carrier service can modify it."""
    path: UpdateCarrierServicesParamCarrierServiceIdRequestPath

# Operation: delete_carrier_service
class DeleteCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to delete.")
class DeleteCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Permanently deletes a carrier service from the store. This removes the shipping method and all associated configurations."""
    path: DeleteCarrierServicesParamCarrierServiceIdRequestPath

# Operation: get_checkouts_count
class GetCheckoutsCountRequestQuery(StrictModel):
    since_id: Any | None = Field(default=None, description="Restrict the count to checkouts created after the specified checkout ID, useful for pagination or incremental syncing.")
    status: Any | None = Field(default=None, description="Filter checkouts by status: 'open' counts only active abandoned checkouts (default), while 'closed' counts only completed or cancelled abandoned checkouts.")
class GetCheckoutsCountRequest(StrictModel):
    """Retrieves the count of abandoned checkouts from the past 90 days, optionally filtered by status or since a specific checkpoint ID."""
    query: GetCheckoutsCountRequestQuery | None = None

# Operation: get_collection
class GetCollectionsParamCollectionIdRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection to retrieve.")
class GetCollectionsParamCollectionIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size.")
class GetCollectionsParamCollectionIdRequest(StrictModel):
    """Retrieves a single collection by its ID. Use this to fetch detailed information about a specific collection, including its products, metadata, and configuration."""
    path: GetCollectionsParamCollectionIdRequestPath
    query: GetCollectionsParamCollectionIdRequestQuery | None = None

# Operation: list_collection_products
class GetCollectionsParamCollectionIdProductsRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection whose products you want to retrieve.")
class GetCollectionsParamCollectionIdProductsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of products to return per request, ranging from 1 to 250 products. Defaults to 50 if not specified.")
class GetCollectionsParamCollectionIdProductsRequest(StrictModel):
    """Retrieve products belonging to a specific collection, sorted according to the collection's configured sort order. Results are paginated using link-based navigation provided in response headers."""
    path: GetCollectionsParamCollectionIdProductsRequestPath
    query: GetCollectionsParamCollectionIdProductsRequestQuery | None = None

# Operation: list_collects
class GetCollectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 if not specified.")
    since_id: Any | None = Field(default=None, description="Restrict results to collects created after the specified collect ID, useful for incremental syncing.")
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. Omit to return all fields.")
class GetCollectsRequest(StrictModel):
    """Retrieves a paginated list of collects (product-to-collection associations). Results are paginated using cursor-based links provided in response headers; use the link relations to navigate pages rather than the page parameter."""
    query: GetCollectsRequestQuery | None = None

# Operation: get_collects_count
class GetCollectsCountRequestQuery(StrictModel):
    collection_id: int | None = Field(default=None, description="Filter the count to only include collects within a specific collection. When omitted, returns the total count of all collects.")
class GetCollectsCountRequest(StrictModel):
    """Retrieves the total count of collects, optionally filtered by a specific collection. Use this to determine how many products are associated with a collection or to get the total number of collects across all collections."""
    query: GetCollectsCountRequestQuery | None = None

# Operation: get_collect
class GetCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect to retrieve.")
class GetCollectsParamCollectIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size.")
class GetCollectsParamCollectIdRequest(StrictModel):
    """Retrieves a specific product collection by its ID. Use this to fetch detailed information about a single collect resource."""
    path: GetCollectsParamCollectIdRequestPath
    query: GetCollectsParamCollectIdRequestQuery | None = None

# Operation: remove_product_from_collection
class DeleteCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect relationship to remove. This ID represents the link between a product and a collection.")
class DeleteCollectsParamCollectIdRequest(StrictModel):
    """Removes a product from a collection by deleting the collect relationship. This operation unlinks a product from a specific collection without affecting the product or collection itself."""
    path: DeleteCollectsParamCollectIdRequestPath

# Operation: list_countries
class GetCountriesRequestQuery(StrictModel):
    since_id: Any | None = Field(default=None, description="Restrict results to countries after the specified country ID, useful for pagination or resuming from a previous request.")
    fields: Any | None = Field(default=None, description="Limit the response to specific fields by providing a comma-separated list of field names, reducing payload size when only certain data is needed.")
class GetCountriesRequest(StrictModel):
    """Retrieves a list of all countries available in the Shopify store, optionally filtered and with customizable field selection."""
    query: GetCountriesRequestQuery | None = None

# Operation: get_country
class GetCountriesParamCountryIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country to retrieve.")
class GetCountriesParamCountryIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of specific fields to include in the response. If omitted, all fields are returned.")
class GetCountriesParamCountryIdRequest(StrictModel):
    """Retrieves detailed information about a specific country, including its provinces, tax rates, and other regional properties."""
    path: GetCountriesParamCountryIdRequestPath
    query: GetCountriesParamCountryIdRequestQuery | None = None

# Operation: delete_country
class DeleteCountriesParamCountryIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country to delete.")
class DeleteCountriesParamCountryIdRequest(StrictModel):
    """Permanently deletes a country from the store's shipping configuration. This action cannot be undone."""
    path: DeleteCountriesParamCountryIdRequestPath

# Operation: list_provinces_for_country
class GetCountriesParamCountryIdProvincesRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve provinces.")
class GetCountriesParamCountryIdProvincesRequestQuery(StrictModel):
    since_id: Any | None = Field(default=None, description="Restrict results to provinces after the specified ID, useful for pagination or fetching only recently added provinces.")
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. Omit to return all available fields.")
class GetCountriesParamCountryIdProvincesRequest(StrictModel):
    """Retrieves a list of provinces or states for a specified country. Use this to populate location selectors or display regional subdivisions."""
    path: GetCountriesParamCountryIdProvincesRequestPath
    query: GetCountriesParamCountryIdProvincesRequestQuery | None = None

# Operation: get_province_count_for_country
class GetCountriesParamCountryIdProvincesCountRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve the province count.")
class GetCountriesParamCountryIdProvincesCountRequest(StrictModel):
    """Retrieves the total count of provinces or states for a specified country. Useful for understanding administrative divisions available in a country."""
    path: GetCountriesParamCountryIdProvincesCountRequestPath

# Operation: get_province
class GetCountriesParamCountryIdProvincesParamProvinceIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country. Required to scope the province lookup to the correct country.")
    province_id: str = Field(default=..., description="The unique identifier of the province within the specified country. Required to retrieve the specific province details.")
class GetCountriesParamCountryIdProvincesParamProvinceIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields will be returned, allowing you to optimize response payload size.")
class GetCountriesParamCountryIdProvincesParamProvinceIdRequest(StrictModel):
    """Retrieves detailed information about a specific province within a country. Use this to fetch province data such as name, code, and tax information for a given country."""
    path: GetCountriesParamCountryIdProvincesParamProvinceIdRequestPath
    query: GetCountriesParamCountryIdProvincesParamProvinceIdRequestQuery | None = None

# Operation: list_custom_collections
class GetCustomCollectionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 if not specified.")
    ids: Any | None = Field(default=None, description="Filter results to only include collections with IDs matching this comma-separated list.")
    since_id: Any | None = Field(default=None, description="Return only collections with IDs greater than this value, useful for cursor-based pagination when combined with limit.")
    title: Any | None = Field(default=None, description="Filter results to collections matching this exact title.")
    product_id: Any | None = Field(default=None, description="Filter results to only collections that contain the product with this ID.")
    handle: Any | None = Field(default=None, description="Filter results to collections matching this handle (the URL-friendly identifier).")
    published_status: Any | None = Field(default=None, description="Filter by publication status: 'published' for published collections only, 'unpublished' for unpublished only, or 'any' for all statuses. Defaults to 'any'.")
    fields: Any | None = Field(default=None, description="Limit the response to only these fields, specified as a comma-separated list of field names. Reduces payload size when you only need specific data.")
class GetCustomCollectionsRequest(StrictModel):
    """Retrieves a list of custom collections from your store, with support for filtering, sorting, and field selection. Results are paginated using cursor-based links provided in response headers."""
    query: GetCustomCollectionsRequestQuery | None = None

# Operation: count_custom_collections
class GetCustomCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter the count to include only custom collections with this exact title.")
    product_id: Any | None = Field(default=None, description="Filter the count to include only custom collections that contain this specific product.")
    published_status: Any | None = Field(default=None, description="Filter the count by publication status: 'published' for published collections only, 'unpublished' for unpublished collections only, or 'any' for all collections regardless of status. Defaults to 'any'.")
class GetCustomCollectionsCountRequest(StrictModel):
    """Retrieves the total count of custom collections, optionally filtered by title, product inclusion, or published status."""
    query: GetCustomCollectionsCountRequestQuery | None = None

# Operation: get_custom_collection
class GetCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to retrieve.")
class GetCustomCollectionsParamCustomCollectionIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size.")
class GetCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Retrieves a single custom collection by its ID. Use this to fetch detailed information about a specific custom collection in your store."""
    path: GetCustomCollectionsParamCustomCollectionIdRequestPath
    query: GetCustomCollectionsParamCustomCollectionIdRequestQuery | None = None

# Operation: update_custom_collection
class UpdateCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to update.")
class UpdateCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Updates the properties of an existing custom collection, such as title, description, image, or sort order of products."""
    path: UpdateCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: delete_custom_collection
class DeleteCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to delete.")
class DeleteCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Permanently deletes a custom collection from the store. This action cannot be undone."""
    path: DeleteCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: get_customer_saved_search
class GetCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath(StrictModel):
    customer_saved_search_id: str = Field(default=..., description="The unique identifier of the customer saved search to retrieve.")
class GetCustomerSavedSearchesParamCustomerSavedSearchIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size.")
class GetCustomerSavedSearchesParamCustomerSavedSearchIdRequest(StrictModel):
    """Retrieves a single customer saved search by its ID. Use this to fetch detailed information about a specific saved search that a customer has created."""
    path: GetCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath
    query: GetCustomerSavedSearchesParamCustomerSavedSearchIdRequestQuery | None = None

# Operation: update_customer_saved_search
class UpdateCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath(StrictModel):
    customer_saved_search_id: str = Field(default=..., description="The unique identifier of the customer saved search to update. This ID is returned when the saved search is created and is required to target the correct search for modification.")
class UpdateCustomerSavedSearchesParamCustomerSavedSearchIdRequest(StrictModel):
    """Updates an existing customer saved search with new criteria or settings. This allows modification of a previously created saved search that customers can use to filter and organize customer data."""
    path: UpdateCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath

# Operation: delete_customer_saved_search
class DeleteCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath(StrictModel):
    customer_saved_search_id: str = Field(default=..., description="The unique identifier of the customer saved search to delete.")
class DeleteCustomerSavedSearchesParamCustomerSavedSearchIdRequest(StrictModel):
    """Permanently deletes a customer saved search by its ID. This action cannot be undone."""
    path: DeleteCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath

# Operation: list_customers_for_saved_search
class GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestPath(StrictModel):
    customer_saved_search_id: str = Field(default=..., description="The unique identifier of the customer saved search whose matching customers you want to retrieve.")
class GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="Specifies the field and sort direction for ordering results. Defaults to sorting by last order date in descending order.")
    limit: Any | None = Field(default=None, description="The maximum number of customer records to return per request, ranging from 1 to 250. Defaults to 50 results.")
    fields: Any | None = Field(default=None, description="Comma-separated list of customer field names to include in the response. Omit to return all available fields.")
class GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequest(StrictModel):
    """Retrieves all customers matching the criteria defined in a customer saved search. Use this to fetch customer lists based on pre-configured search filters."""
    path: GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestPath
    query: GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestQuery | None = None

# Operation: list_customers
class GetCustomersRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only customers with IDs matching this comma-separated list of customer identifiers.")
    since_id: Any | None = Field(default=None, description="Return only customers with IDs greater than this value, useful for cursor-based pagination when link headers are unavailable.")
    limit: Any | None = Field(default=None, description="Maximum number of customers to return per request; defaults to 50 and cannot exceed 250.")
    fields: Any | None = Field(default=None, description="Restrict the response to only these fields, specified as a comma-separated list of field names; omit to receive all available fields.")
class GetCustomersRequest(StrictModel):
    """Retrieves a paginated list of customers from the store. Results are paginated using cursor-based links provided in response headers; use the link relations to navigate pages rather than the page parameter."""
    query: GetCustomersRequestQuery | None = None

# Operation: search_customers
class GetCustomersSearchRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="Specify the field and direction to sort results. Use format: field_name ASC or field_name DESC. Defaults to sorting by last order date in descending order.")
    query: Any | None = Field(default=None, description="Text query to search across customer data fields such as name, email, phone, and address information.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request. Must be between 1 and 250. Defaults to 50 results.")
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. If omitted, all fields are returned.")
class GetCustomersSearchRequest(StrictModel):
    """Search for customers in the shop by query text, with support for sorting and field filtering. Results are paginated using cursor-based links provided in response headers."""
    query: GetCustomersSearchRequestQuery | None = None

# Operation: get_customer
class GetCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to retrieve.")
class GetCustomersParamCustomerIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of specific fields to return in the response. Omit to retrieve all available customer fields.")
class GetCustomersParamCustomerIdRequest(StrictModel):
    """Retrieves a single customer by ID from the Shopify store. Use this to fetch detailed customer information including contact details, addresses, and order history."""
    path: GetCustomersParamCustomerIdRequestPath
    query: GetCustomersParamCustomerIdRequestQuery | None = None

# Operation: update_customer
class UpdateCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to update. This ID is required to specify which customer record should be modified.")
class UpdateCustomersParamCustomerIdRequest(StrictModel):
    """Updates an existing customer's information in Shopify. Modify customer details such as name, email, phone, and other profile attributes."""
    path: UpdateCustomersParamCustomerIdRequestPath

# Operation: delete_customer
class DeleteCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to delete.")
class DeleteCustomersParamCustomerIdRequest(StrictModel):
    """Permanently deletes a customer from the store. The deletion will fail if the customer has any existing orders."""
    path: DeleteCustomersParamCustomerIdRequestPath

# Operation: generate_customer_account_activation_url
class CreateCustomersParamCustomerIdAccountActivationUrlRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer for whom to generate the activation URL.")
class CreateCustomersParamCustomerIdAccountActivationUrlRequest(StrictModel):
    """Generate a one-time account activation URL for a customer whose account is not yet enabled. The URL expires after 30 days; generating a new URL invalidates any previously generated URLs."""
    path: CreateCustomersParamCustomerIdAccountActivationUrlRequestPath

# Operation: list_customer_addresses
class GetCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses you want to retrieve.")
class GetCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Retrieves all addresses associated with a specific customer. Results are paginated using link-based navigation provided in response headers."""
    path: GetCustomersParamCustomerIdAddressesRequestPath

# Operation: add_address_for_customer
class CreateCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to whom the address will be added.")
class CreateCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Adds a new address to a customer's address book. The address will be associated with the specified customer and can be used for shipping or billing purposes."""
    path: CreateCustomersParamCustomerIdAddressesRequestPath

# Operation: update_customer_addresses
class UpdateCustomersParamCustomerIdAddressesSetRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses will be modified.")
class UpdateCustomersParamCustomerIdAddressesSetRequestQuery(StrictModel):
    address_ids: int | None = Field(default=None, validation_alias="address_ids[]", serialization_alias="address_ids[]", description="Array of address IDs to include in the bulk operation. The order may be significant depending on the operation type.")
    operation: str | None = Field(default=None, description="The type of bulk operation to perform on the specified addresses (e.g., set as default, delete, or activate).")
class UpdateCustomersParamCustomerIdAddressesSetRequest(StrictModel):
    """Perform bulk operations on multiple addresses for a specific customer, such as setting a default address or removing addresses in batch."""
    path: UpdateCustomersParamCustomerIdAddressesSetRequestPath
    query: UpdateCustomersParamCustomerIdAddressesSetRequestQuery | None = None

# Operation: get_customer_address
class GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who owns the address.")
    address_id: str = Field(default=..., description="The unique identifier of the address to retrieve.")
class GetCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Retrieves the details of a specific address associated with a customer account."""
    path: GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: update_customer_address
class UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being updated.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to update for the customer.")
class UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Updates an existing address for a customer. Provide the customer ID and address ID to modify the address details."""
    path: UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: delete_customer_address
class DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being removed.")
    address_id: str = Field(default=..., description="The unique identifier of the address to be deleted from the customer's address list.")
class DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Removes a specific address from a customer's address list. This operation permanently deletes the address record associated with the given customer."""
    path: DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: set_customer_default_address
class UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose default address is being updated.")
    address_id: str = Field(default=..., description="The unique identifier of the address to set as the customer's default address.")
class UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest(StrictModel):
    """Designates a specific address as the default address for a customer. This address will be used as the primary contact address for the customer account."""
    path: UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath

# Operation: list_customer_orders
class GetCustomersParamCustomerIdOrdersRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose orders should be retrieved.")
class GetCustomersParamCustomerIdOrdersRequest(StrictModel):
    """Retrieves all orders for a specific customer. Supports standard order resource query parameters for filtering, sorting, and pagination."""
    path: GetCustomersParamCustomerIdOrdersRequestPath

# Operation: send_customer_invite
class CreateCustomersParamCustomerIdSendInviteRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who will receive the invitation.")
class CreateCustomersParamCustomerIdSendInviteRequest(StrictModel):
    """Sends an account invitation email to a customer, allowing them to create or access their account."""
    path: CreateCustomersParamCustomerIdSendInviteRequestPath

# Operation: lookup_discount_code
class GetDiscountCodesLookupRequestQuery(StrictModel):
    code: str | None = Field(default=None, description="The discount code string to look up. Used to find and return the resource location of the matching discount code.")
class GetDiscountCodesLookupRequest(StrictModel):
    """Retrieves the location of a discount code by its code value. The discount code's location is returned in the HTTP location header rather than in the response body."""
    query: GetDiscountCodesLookupRequestQuery | None = None

# Operation: list_events
class GetEventsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of events to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
    since_id: Any | None = Field(default=None, description="Return only events that occurred after the specified event ID, useful for incremental syncing.")
    filter_: Any | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter events by a specific criteria or resource type to narrow results.")
    verb: Any | None = Field(default=None, description="Filter events by action type (e.g., create, update, delete) to show only events of a certain kind.")
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response; omit to return all fields.")
class GetEventsRequest(StrictModel):
    """Retrieves a paginated list of events from the store. Results are paginated using cursor-based links provided in response headers; use the link relations to navigate pages rather than the page parameter."""
    query: GetEventsRequestQuery | None = None

# Operation: get_event
class GetEventsParamEventIdRequestPath(StrictModel):
    event_id: str = Field(default=..., description="The unique identifier of the event to retrieve.")
class GetEventsParamEventIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields will be returned, reducing payload size.")
class GetEventsParamEventIdRequest(StrictModel):
    """Retrieves a single event by its ID from the Shopify admin. Use this to fetch detailed information about a specific event that occurred in your store."""
    path: GetEventsParamEventIdRequestPath
    query: GetEventsParamEventIdRequestQuery | None = None

# Operation: get_fulfillment_order
class GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to retrieve.")
class GetFulfillmentOrdersParamFulfillmentOrderIdRequest(StrictModel):
    """Retrieves the details of a specific fulfillment order by its ID, including order status, line items, and fulfillment tracking information."""
    path: GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath

# Operation: cancel_fulfillment_order
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel. This ID references a specific fulfillment order within your store.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest(StrictModel):
    """Cancels a fulfillment order, marking it as no longer needed for processing. This operation prevents further fulfillment actions on the specified order."""
    path: CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath

# Operation: send_fulfillment_order_cancellation_request
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel. This ID references a specific fulfillment order within your Shopify store.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for the cancellation request. This message is typically sent to the fulfillment service to provide context for the cancellation.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest(StrictModel):
    """Sends a cancellation request to the fulfillment service for a specific fulfillment order. This notifies the fulfillment provider that the order should be cancelled if not yet fulfilled."""
    path: CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath
    query: CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery | None = None

# Operation: accept_fulfillment_order_cancellation_request
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the cancellation request is being accepted.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for accepting the cancellation request.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest(StrictModel):
    """Accepts a cancellation request for a fulfillment order, notifying the fulfillment service that the cancellation has been approved. Optionally include a reason for accepting the request."""
    path: CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath
    query: CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_order_cancellation_request
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the cancellation request should be rejected.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining why the cancellation request is being rejected. This reason will be communicated to the fulfillment service.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest(StrictModel):
    """Rejects a cancellation request that was sent to a fulfillment service for a specific fulfillment order. Use this when you need to decline a cancellation and optionally provide a reason to the fulfillment service."""
    path: CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath
    query: CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery | None = None

# Operation: close_fulfillment_order
class CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to close.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional reason or note explaining why the fulfillment order is being marked as incomplete.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest(StrictModel):
    """Marks an in-progress fulfillment order as incomplete, indicating the fulfillment service cannot ship remaining items and is closing the order."""
    path: CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath
    query: CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery | None = None

# Operation: send_fulfillment_request
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to request fulfillment for.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message to include with the fulfillment request, typically for communicating special instructions or notes to the fulfillment service.")
    fulfillment_order_line_items: Any | None = Field(default=None, description="An optional list of specific line items from the fulfillment order to request for fulfillment. If omitted, all unfulfilled line items in the order are included in the request.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest(StrictModel):
    """Sends a fulfillment request to the fulfillment service for a specific fulfillment order, optionally targeting specific line items or including a message for the fulfillment provider."""
    path: CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath
    query: CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery | None = None

# Operation: accept_fulfillment_request
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request is being accepted.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for accepting the fulfillment request.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest(StrictModel):
    """Accepts a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, optionally providing a reason for acceptance."""
    path: CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath
    query: CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_request
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request should be rejected.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for rejecting the fulfillment request.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest(StrictModel):
    """Rejects a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, optionally providing a reason for the rejection."""
    path: CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath
    query: CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery | None = None

# Operation: list_fulfillments_for_order
class GetFulfillmentOrdersParamFulfillmentOrderIdFulfillmentsRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order. This ID is required to retrieve its associated fulfillments.")
class GetFulfillmentOrdersParamFulfillmentOrderIdFulfillmentsRequest(StrictModel):
    """Retrieves all fulfillments associated with a specific fulfillment order. Use this to view fulfillment details and status for a given order."""
    path: GetFulfillmentOrdersParamFulfillmentOrderIdFulfillmentsRequestPath

# Operation: list_locations_for_fulfillment_order_move
class GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to retrieve available move destinations.")
class GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest(StrictModel):
    """Retrieves a list of locations where a fulfillment order can be moved to. Results are sorted alphabetically by location name in ascending order."""
    path: GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath

# Operation: move_fulfillment_order
class CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to be moved.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequestQuery(StrictModel):
    new_location_id: Any | None = Field(default=None, description="The unique identifier of the destination location where the fulfillment order will be transferred. Must be a merchant-managed location.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequest(StrictModel):
    """Relocates a fulfillment order to a different merchant-managed location, enabling inventory redistribution across fulfillment centers."""
    path: CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequestPath
    query: CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequestQuery | None = None

# Operation: list_fulfillment_services
class GetFulfillmentServicesRequestQuery(StrictModel):
    scope: Any | None = Field(default=None, description="Filter scope for returned fulfillment providers. Use 'current_client' (default) to return only providers created by this app, or 'all' to return every fulfillment provider in the store.")
class GetFulfillmentServicesRequest(StrictModel):
    """Retrieve a list of fulfillment service providers. By default, returns only fulfillment providers created by the requesting app, or optionally all available providers in the store."""
    query: GetFulfillmentServicesRequestQuery | None = None

# Operation: get_fulfillment_service
class GetFulfillmentServicesParamFulfillmentServiceIdRequestPath(StrictModel):
    fulfillment_service_id: str = Field(default=..., description="The unique identifier of the fulfillment service to retrieve. This ID is assigned by Shopify when the service is created or integrated.")
class GetFulfillmentServicesParamFulfillmentServiceIdRequest(StrictModel):
    """Retrieve detailed information about a specific fulfillment service by its ID. Use this to fetch configuration, capabilities, and status of a fulfillment service integrated with your Shopify store."""
    path: GetFulfillmentServicesParamFulfillmentServiceIdRequestPath

# Operation: update_fulfillment_service
class UpdateFulfillmentServicesParamFulfillmentServiceIdRequestPath(StrictModel):
    fulfillment_service_id: str = Field(default=..., description="The unique identifier of the fulfillment service to update.")
class UpdateFulfillmentServicesParamFulfillmentServiceIdRequest(StrictModel):
    """Update the configuration and settings of an existing fulfillment service, such as its name, callback URLs, or tracking capabilities."""
    path: UpdateFulfillmentServicesParamFulfillmentServiceIdRequestPath

# Operation: delete_fulfillment_service
class DeleteFulfillmentServicesParamFulfillmentServiceIdRequestPath(StrictModel):
    fulfillment_service_id: str = Field(default=..., description="The unique identifier of the fulfillment service to delete.")
class DeleteFulfillmentServicesParamFulfillmentServiceIdRequest(StrictModel):
    """Permanently delete a fulfillment service by its ID. This removes the fulfillment service from your Shopify store."""
    path: DeleteFulfillmentServicesParamFulfillmentServiceIdRequestPath

# Operation: cancel_fulfillment
class CreateFulfillmentsParamFulfillmentIdCancelRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to cancel. This ID references a specific fulfillment record that must exist and be in a cancellable state.")
class CreateFulfillmentsParamFulfillmentIdCancelRequest(StrictModel):
    """Cancels an existing fulfillment, preventing further processing or shipment of the associated items."""
    path: CreateFulfillmentsParamFulfillmentIdCancelRequestPath

# Operation: update_fulfillment_tracking
class CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment whose tracking information should be updated.")
class CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest(StrictModel):
    """Updates the tracking information for a fulfillment, allowing you to modify shipment tracking details after the fulfillment has been created."""
    path: CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath

# Operation: list_gift_cards
class GetGiftCardsRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter results to gift cards with a specific status: enabled to show only active gift cards, or disabled to show only inactive gift cards.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250 (defaults to 50).")
    since_id: Any | None = Field(default=None, description="Cursor-based pagination parameter: retrieve only gift cards with IDs after the specified ID to continue from a previous result set.")
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response; omit to return all fields.")
class GetGiftCardsRequest(StrictModel):
    """Retrieves a paginated list of gift cards from the store, optionally filtered by status. Results are paginated using cursor-based links provided in response headers."""
    query: GetGiftCardsRequestQuery | None = None

# Operation: get_gift_cards_count
class GetGiftCardsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count to only include gift cards with a specific status: enabled for active gift cards, or disabled for inactive gift cards. Omit to count all gift cards regardless of status.")
class GetGiftCardsCountRequest(StrictModel):
    """Retrieves the total count of gift cards in the store, optionally filtered by status (enabled or disabled)."""
    query: GetGiftCardsCountRequestQuery | None = None

# Operation: search_gift_cards
class GetGiftCardsSearchRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="The field and direction to sort results by. Specify a field name followed by ASC or DESC (for example: balance DESC or created_at ASC). Defaults to sorting by disabled_at in descending order.")
    query: Any | None = Field(default=None, description="The search query text to match against indexed gift card fields including created_at, updated_at, disabled_at, balance, initial_value, amount_spent, email, and last_characters.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 results.")
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. Omit to return all fields.")
class GetGiftCardsSearchRequest(StrictModel):
    """Search for gift cards using indexed fields like balance, email, or creation date. Results are paginated and can be filtered, sorted, and limited to specific fields."""
    query: GetGiftCardsSearchRequestQuery | None = None

# Operation: get_gift_card
class GetGiftCardsParamGiftCardIdRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to retrieve.")
class GetGiftCardsParamGiftCardIdRequest(StrictModel):
    """Retrieves the details of a single gift card by its unique identifier. Use this to fetch gift card information such as balance, status, and creation date."""
    path: GetGiftCardsParamGiftCardIdRequestPath

# Operation: update_gift_card
class UpdateGiftCardsParamGiftCardIdRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to update.")
class UpdateGiftCardsParamGiftCardIdRequest(StrictModel):
    """Updates an existing gift card's expiry date, note, and template suffix. The gift card's balance cannot be modified through the API."""
    path: UpdateGiftCardsParamGiftCardIdRequestPath

# Operation: disable_gift_card
class CreateGiftCardsParamGiftCardIdDisableRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to disable.")
class CreateGiftCardsParamGiftCardIdDisableRequest(StrictModel):
    """Permanently disables a gift card, preventing further use. This action cannot be reversed."""
    path: CreateGiftCardsParamGiftCardIdDisableRequestPath

# Operation: list_inventory_items
class GetInventoryItemsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250 items. Defaults to 50 if not specified.")
    ids: str | None = Field(default=None, description="Filter results to specific inventory items by their numeric IDs. Provide one or more comma-separated integer IDs.")
class GetInventoryItemsRequest(StrictModel):
    """Retrieves a paginated list of inventory items. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: GetInventoryItemsRequestQuery | None = None

# Operation: get_inventory_item
class GetInventoryItemsParamInventoryItemIdRequestPath(StrictModel):
    inventory_item_id: str = Field(default=..., description="The unique identifier of the inventory item to retrieve.")
class GetInventoryItemsParamInventoryItemIdRequest(StrictModel):
    """Retrieves a single inventory item by its unique identifier. Use this to fetch detailed inventory information for a specific product variant."""
    path: GetInventoryItemsParamInventoryItemIdRequestPath

# Operation: update_inventory_item
class UpdateInventoryItemsParamInventoryItemIdRequestPath(StrictModel):
    inventory_item_id: str = Field(default=..., description="The unique identifier of the inventory item to update. This ID is assigned by Shopify when the inventory item is created.")
class UpdateInventoryItemsParamInventoryItemIdRequest(StrictModel):
    """Updates an existing inventory item in your store's inventory system. Use this to modify properties like SKU, tracked status, or other inventory attributes for a specific item."""
    path: UpdateInventoryItemsParamInventoryItemIdRequestPath

# Operation: list_inventory_levels
class GetInventoryLevelsRequestQuery(StrictModel):
    inventory_item_ids: Any | None = Field(default=None, description="Comma-separated list of inventory item IDs to filter results. Maximum of 50 IDs per request.")
    location_ids: Any | None = Field(default=None, description="Comma-separated list of location IDs to filter results. Maximum of 50 IDs per request. Use the Location resource to find location IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
class GetInventoryLevelsRequest(StrictModel):
    """Retrieves inventory levels across locations and inventory items. You must filter by at least one inventory item ID or location ID to retrieve results."""
    query: GetInventoryLevelsRequestQuery | None = None

# Operation: delete_inventory_level
class DeleteInventoryLevelsRequestQuery(StrictModel):
    inventory_item_id: int | None = Field(default=None, description="The unique identifier of the inventory item whose level should be deleted.")
    location_id: int | None = Field(default=None, description="The unique identifier of the location where the inventory level should be removed.")
class DeleteInventoryLevelsRequest(StrictModel):
    """Removes an inventory level for a specific inventory item at a location. This disconnects the item from that location; note that every inventory item must retain at least one inventory level, so connect the item to another location before deleting its last level."""
    query: DeleteInventoryLevelsRequestQuery | None = None

# Operation: get_location
class GetLocationsParamLocationIdRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location to retrieve. This ID is assigned by Shopify and is required to fetch the specific location's details.")
class GetLocationsParamLocationIdRequest(StrictModel):
    """Retrieves detailed information about a specific inventory location by its ID. Use this to fetch location details such as address, fulfillment capabilities, and operational status."""
    path: GetLocationsParamLocationIdRequestPath

# Operation: list_inventory_levels_for_location
class GetLocationsParamLocationIdInventoryLevelsRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location for which to retrieve inventory levels.")
class GetLocationsParamLocationIdInventoryLevelsRequest(StrictModel):
    """Retrieves a paginated list of inventory levels for a specific location. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""
    path: GetLocationsParamLocationIdInventoryLevelsRequestPath

# Operation: list_metafields_for_product_image
class GetMetafieldsRequestQuery(StrictModel):
    metafield_owner_id: int | None = Field(default=None, validation_alias="metafield[owner_id]", serialization_alias="metafield[owner_id]", description="The unique identifier of the Product Image resource that owns the metafields. Required when filtering metafields by a specific image.")
    metafield_owner_resource: str | None = Field(default=None, validation_alias="metafield[owner_resource]", serialization_alias="metafield[owner_resource]", description="The resource type that owns the metafields. Should be set to 'product_image' to retrieve metafields for Product Image resources.")
class GetMetafieldsRequest(StrictModel):
    """Retrieves metafields associated with a specific Product Image resource. Use owner_id and owner_resource to filter metafields for a particular image."""
    query: GetMetafieldsRequestQuery | None = None

# Operation: get_metafield
class GetMetafieldsParamMetafieldIdRequestPath(StrictModel):
    metafield_id: str = Field(default=..., description="The unique identifier of the metafield to retrieve.")
class GetMetafieldsParamMetafieldIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Optionally limit the response to specific fields by providing a comma-separated list of field names. Reduces payload size when only certain metafield properties are needed.")
class GetMetafieldsParamMetafieldIdRequest(StrictModel):
    """Retrieves a single metafield by its ID. Use this to fetch detailed information about a specific metafield attached to a resource."""
    path: GetMetafieldsParamMetafieldIdRequestPath
    query: GetMetafieldsParamMetafieldIdRequestQuery | None = None

# Operation: update_metafield
class UpdateMetafieldsParamMetafieldIdRequestPath(StrictModel):
    metafield_id: str = Field(default=..., description="The unique identifier of the metafield to update. This ID is returned when a metafield is created and is required to target the specific metafield for modification.")
class UpdateMetafieldsParamMetafieldIdRequest(StrictModel):
    """Updates an existing metafield by ID. Modify metafield properties such as namespace, key, value, and type."""
    path: UpdateMetafieldsParamMetafieldIdRequestPath

# Operation: delete_metafield
class DeleteMetafieldsParamMetafieldIdRequestPath(StrictModel):
    metafield_id: str = Field(default=..., description="The unique identifier of the metafield to delete.")
class DeleteMetafieldsParamMetafieldIdRequest(StrictModel):
    """Permanently deletes a metafield by its ID. This action cannot be undone."""
    path: DeleteMetafieldsParamMetafieldIdRequestPath

# Operation: list_fulfillment_orders
class GetOrdersParamOrderIdFulfillmentOrdersRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve fulfillment orders.")
class GetOrdersParamOrderIdFulfillmentOrdersRequest(StrictModel):
    """Retrieves all fulfillment orders associated with a specific order, including their current status and fulfillment details."""
    path: GetOrdersParamOrderIdFulfillmentOrdersRequestPath

# Operation: list_order_fulfillments
class GetOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve fulfillments.")
class GetOrdersParamOrderIdFulfillmentsRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="A comma-separated list of specific fields to include in the response. Omit to return all fields.")
    limit: Any | None = Field(default=None, description="Maximum number of fulfillments to return per request. Defaults to 50; maximum allowed is 250.")
    since_id: Any | None = Field(default=None, description="Restrict results to fulfillments created after the specified fulfillment ID, useful for pagination when combined with link headers.")
class GetOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Retrieves all fulfillments associated with a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    path: GetOrdersParamOrderIdFulfillmentsRequestPath
    query: GetOrdersParamOrderIdFulfillmentsRequestQuery | None = None

# Operation: create_fulfillment_for_order
class CreateOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the fulfillment. Required to specify which order's line items should be fulfilled.")
class CreateOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Create a fulfillment for specified line items in an order. The fulfillment status depends on the fulfillment service type: manual/custom services set status immediately, while external services queue the fulfillment with pending status until processed. All line items in a fulfillment must use the same fulfillment service, and refunded orders or line items cannot be fulfilled."""
    path: CreateOrdersParamOrderIdFulfillmentsRequestPath

# Operation: get_fulfillment_count
class GetOrdersParamOrderIdFulfillmentsCountRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve the fulfillment count.")
class GetOrdersParamOrderIdFulfillmentsCountRequest(StrictModel):
    """Retrieves the total count of fulfillments associated with a specific order. Useful for understanding fulfillment status and logistics tracking without fetching full fulfillment details."""
    path: GetOrdersParamOrderIdFulfillmentsCountRequestPath

# Operation: get_fulfillment
class GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to retrieve.")
class GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of specific fields to include in the response. If omitted, all fields are returned.")
class GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Retrieve detailed information about a specific fulfillment for an order, including tracking and line item fulfillment status."""
    path: GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath
    query: GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestQuery | None = None

# Operation: update_fulfillment
class UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to update.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to update.")
class UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Update fulfillment details for a specific order, such as tracking information, status, or line items included in the shipment."""
    path: UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: cancel_fulfillment_order_2
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to cancel.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to cancel within the specified order.")
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequest(StrictModel):
    """Cancel an active fulfillment for a specific order. This operation marks the fulfillment as cancelled and may trigger related notifications depending on the fulfillment state."""
    path: CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequestPath

# Operation: complete_fulfillment
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to be completed.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to mark as complete.")
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest(StrictModel):
    """Mark a fulfillment as complete, indicating that all items in the fulfillment have been shipped and are on their way to the customer."""
    path: CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath

# Operation: list_fulfillment_events
class GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment within the specified order.")
class GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest(StrictModel):
    """Retrieves all events associated with a specific fulfillment for an order, including status updates and tracking information."""
    path: GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath

# Operation: create_fulfillment_event
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment for which to create the event.")
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest(StrictModel):
    """Creates a fulfillment event for a specific fulfillment within an order. Fulfillment events track status changes and milestones in the fulfillment lifecycle."""
    path: CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath

# Operation: get_fulfillment_event
class GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment event.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment within the order.")
    event_id: str = Field(default=..., description="The unique identifier of the specific fulfillment event to retrieve.")
class GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequest(StrictModel):
    """Retrieves a specific fulfillment event for a given order and fulfillment. Use this to fetch details about a particular event in the fulfillment lifecycle, such as tracking updates or status changes."""
    path: GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequestPath

# Operation: delete_fulfillment_event
class DeleteOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment event to delete.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment within the order that contains the event to delete.")
    event_id: str = Field(default=..., description="The unique identifier of the fulfillment event to delete.")
class DeleteOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequest(StrictModel):
    """Deletes a specific fulfillment event from an order's fulfillment. This removes the event record associated with the fulfillment tracking."""
    path: DeleteOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequestPath

# Operation: open_fulfillment
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to be opened.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to mark as open.")
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequest(StrictModel):
    """Mark a fulfillment as open, allowing it to receive additional items or changes. This transitions the fulfillment to an open state for the specified order."""
    path: CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequestPath

# Operation: list_order_refunds
class GetOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve refunds.")
class GetOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of refunds to return per request, between 1 and 250 (defaults to 50).")
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. Omit to return all fields.")
    in_shop_currency: Any | None = Field(default=None, description="When true, displays monetary amounts in the shop's currency for the underlying transaction (defaults to false).")
class GetOrdersParamOrderIdRefundsRequest(StrictModel):
    """Retrieves a list of refunds for a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    path: GetOrdersParamOrderIdRefundsRequestPath
    query: GetOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: create_order_refund
class CreateOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create a refund.")
class CreateOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    notify: Any | None = Field(default=None, description="Whether to send a refund notification email to the customer.")
    note: Any | None = Field(default=None, description="An optional note to attach to the refund for internal reference.")
    discrepancy_reason: Any | None = Field(default=None, description="An optional reason explaining any discrepancy between calculated and actual refund amounts. Valid values are: restock, damage, customer, or other.")
    shipping: Any | None = Field(default=None, description="Specifies how much shipping to refund. Provide either full_refund (boolean) to refund all remaining shipping, or amount (decimal) to refund a specific shipping amount. The amount takes precedence if both are provided.")
    refund_line_items: Any | None = Field(default=None, description="A list of line items to refund, each specifying the line_item_id, quantity to refund, restock_type (no_restock, cancel, or return), and location_id (required for cancel or return restock types). The location_id determines where restocked items are added back to inventory.")
    transactions: Any | None = Field(default=None, description="A list of transactions to process as refunds. These should be obtained from the calculate endpoint to ensure accuracy.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required for multi-currency orders when an amount property is provided.")
class CreateOrdersParamOrderIdRefundsRequest(StrictModel):
    """Creates a refund for an order. Use the calculate endpoint first to determine the correct transactions to submit. For multi-currency orders, the currency property is required whenever an amount is specified."""
    path: CreateOrdersParamOrderIdRefundsRequestPath
    query: CreateOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: calculate_order_refund
class CreateOrdersParamOrderIdRefundsCalculateRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to calculate the refund.")
class CreateOrdersParamOrderIdRefundsCalculateRequestQuery(StrictModel):
    shipping: Any | None = Field(default=None, description="Shipping refund configuration. Specify either full_refund to refund all remaining shipping costs, or amount to refund a specific shipping amount. The amount property takes precedence over full_refund if both are provided. Required for multi-currency orders when amount is specified.")
    refund_line_items: Any | None = Field(default=None, description="A list of line items to refund, each specifying the line item ID, quantity to refund, and how the refund affects inventory (no_restock, cancel, or return). Optionally specify the location_id where items should be restocked; if not provided, the system will suggest a suitable location for return or cancel operations. Use already_stocked to indicate whether the item is already in stock at the location.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund amount. Required whenever a shipping amount is specified for multi-currency orders.")
class CreateOrdersParamOrderIdRefundsCalculateRequest(StrictModel):
    """Calculates refund transactions for an order based on specified line items, quantities, restock instructions, and shipping costs. Use this endpoint to generate accurate refund details before creating the actual refund. The response includes suggested refund transactions that must be converted to actual refunds when submitting the refund creation request."""
    path: CreateOrdersParamOrderIdRefundsCalculateRequestPath
    query: CreateOrdersParamOrderIdRefundsCalculateRequestQuery | None = None

# Operation: get_refund
class GetOrdersParamOrderIdRefundsParamRefundIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the refund.")
    refund_id: str = Field(default=..., description="The unique identifier of the refund to retrieve.")
class GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size.")
    in_shop_currency: Any | None = Field(default=None, description="When enabled, monetary amounts in the response are displayed in the shop's currency rather than the transaction currency. Defaults to false.")
class GetOrdersParamOrderIdRefundsParamRefundIdRequest(StrictModel):
    """Retrieves the details of a specific refund associated with an order. Use this to view refund information including amounts, line items, and status."""
    path: GetOrdersParamOrderIdRefundsParamRefundIdRequestPath
    query: GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery | None = None

# Operation: list_order_risks
class GetOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve risk assessments.")
class GetOrdersParamOrderIdRisksRequest(StrictModel):
    """Retrieves all fraud and risk assessments associated with a specific order. Use this to review potential risks flagged by Shopify's risk analysis system for an order."""
    path: GetOrdersParamOrderIdRisksRequestPath

# Operation: create_order_risk
class CreateOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which the risk is being created.")
class CreateOrdersParamOrderIdRisksRequest(StrictModel):
    """Creates a risk assessment record for an order, allowing merchants to flag potential issues or concerns associated with the order."""
    path: CreateOrdersParamOrderIdRisksRequestPath

# Operation: get_order_risk
class GetOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk assessment.")
    risk_id: str = Field(default=..., description="The unique identifier of the specific risk assessment to retrieve.")
class GetOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Retrieves a single risk assessment associated with an order. Use this to fetch detailed information about a specific fraud or security risk flagged on an order."""
    path: GetOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: update_order_risk
class UpdateOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to be updated.")
    risk_id: str = Field(default=..., description="The unique identifier of the order risk to be updated.")
class UpdateOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Updates an existing order risk for a specific order. Note that you cannot modify an order risk that was created by another application."""
    path: UpdateOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: delete_order_risk
class DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to delete.")
    risk_id: str = Field(default=..., description="The unique identifier of the risk assessment to delete.")
class DeleteOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Deletes a fraud risk assessment associated with an order. Note that you can only delete risks created by your application; risks created by other applications cannot be removed."""
    path: DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: create_discount_codes_batch
class CreatePriceRulesParamPriceRuleIdBatchRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which discount codes will be created.")
class CreatePriceRulesParamPriceRuleIdBatchRequest(StrictModel):
    """Asynchronously create up to 100 discount codes for a price rule in a single batch job. Returns a discount code creation job object that can be monitored for completion status, import counts, and validation errors."""
    path: CreatePriceRulesParamPriceRuleIdBatchRequestPath

# Operation: get_discount_code_batch
class GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch job.")
    batch_id: str = Field(default=..., description="The unique identifier of the batch job to retrieve status and results for.")
class GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest(StrictModel):
    """Retrieves the status and details of a discount code creation job batch for a specific price rule."""
    path: GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath

# Operation: list_discount_codes_for_batch
class GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code batch job.")
    batch_id: str = Field(default=..., description="The unique identifier of the batch job for which to retrieve discount codes.")
class GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest(StrictModel):
    """Retrieves all discount codes generated from a specific batch job within a price rule. Results include successfully created codes (with populated id) and codes that failed during creation (with populated errors)."""
    path: GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath

# Operation: list_discount_codes_for_price_rule
class GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which to retrieve associated discount codes.")
class GetPriceRulesParamPriceRuleIdDiscountCodesRequest(StrictModel):
    """Retrieve all discount codes associated with a specific price rule. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""
    path: GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath

# Operation: create_discount_code
class CreatePriceRulesParamPriceRuleIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule to which this discount code will be associated. This price rule must already exist.")
class CreatePriceRulesParamPriceRuleIdDiscountCodesRequest(StrictModel):
    """Creates a new discount code associated with a specific price rule. The discount code can be used by customers to apply the price rule's discounts during checkout."""
    path: CreatePriceRulesParamPriceRuleIdDiscountCodesRequestPath

# Operation: get_discount_code
class GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to retrieve.")
class GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Retrieves a single discount code associated with a specific price rule. Use this to fetch detailed information about a discount code by its ID."""
    path: GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: update_discount_code
class UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code being updated.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to update.")
class UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Updates an existing discount code associated with a price rule. Modify discount code properties such as code value, usage limits, and other configurations."""
    path: UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: delete_discount_code
class DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code to be deleted.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to be deleted.")
class DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Permanently deletes a specific discount code associated with a price rule. This action cannot be undone."""
    path: DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: list_products
class GetProductsRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only products with IDs in this comma-separated list.")
    limit: Any | None = Field(default=None, description="Maximum number of products to return per page; defaults to 50 and cannot exceed 250.")
    since_id: Any | None = Field(default=None, description="Return only products with IDs greater than this value, useful for cursor-based pagination.")
    title: Any | None = Field(default=None, description="Filter results to products matching this title exactly or partially.")
    vendor: Any | None = Field(default=None, description="Filter results to products from this vendor.")
    handle: Any | None = Field(default=None, description="Filter results to products with this handle (URL-friendly identifier).")
    product_type: Any | None = Field(default=None, description="Filter results to products of this type.")
    status: Any | None = Field(default=None, description="Filter results by product status: active (default), archived, or draft.")
    collection_id: Any | None = Field(default=None, description="Filter results to products in this collection by collection ID.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: published, unpublished, or any (default).")
    fields: Any | None = Field(default=None, description="Return only specified fields as a comma-separated list; omit to return all fields.")
    presentment_currencies: Any | None = Field(default=None, description="Return presentment prices in only these currencies, specified as a comma-separated list of ISO 4217 currency codes.")
class GetProductsRequest(StrictModel):
    """Retrieves a paginated list of products from the store, with support for filtering by various attributes and controlling which fields are returned. Results are paginated using link headers rather than page parameters."""
    query: GetProductsRequestQuery | None = None

# Operation: get_products_count
class GetProductsCountRequestQuery(StrictModel):
    vendor: Any | None = Field(default=None, description="Filter the count to include only products from a specific vendor.")
    product_type: Any | None = Field(default=None, description="Filter the count to include only products of a specific product type.")
    collection_id: Any | None = Field(default=None, description="Filter the count to include only products belonging to a specific collection.")
    published_status: Any | None = Field(default=None, description="Filter the count by product publication status: 'published' for published products only, 'unpublished' for unpublished products only, or 'any' to include all products regardless of status (default: any).")
class GetProductsCountRequest(StrictModel):
    """Retrieves the total count of products in the store, with optional filtering by vendor, product type, collection, or published status."""
    query: GetProductsCountRequestQuery | None = None

# Operation: get_product
class GetProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to retrieve.")
class GetProductsParamProductIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="A comma-separated list of specific fields to include in the response. Omit to return all available product fields.")
class GetProductsParamProductIdRequest(StrictModel):
    """Retrieves a single product by its ID from the Shopify store. Use this to fetch detailed product information including variants, images, and metadata."""
    path: GetProductsParamProductIdRequestPath
    query: GetProductsParamProductIdRequestQuery | None = None

# Operation: update_product
class UpdateProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to update.")
class UpdateProductsParamProductIdRequest(StrictModel):
    """Updates a product's details, variants, images, and SEO metadata. Use metafields_global_title_tag and metafields_global_description_tag to manage SEO title and description tags."""
    path: UpdateProductsParamProductIdRequestPath

# Operation: delete_product
class DeleteProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to delete. This is a required string value that identifies which product should be removed.")
class DeleteProductsParamProductIdRequest(StrictModel):
    """Permanently deletes a product from the store. This action cannot be undone and will remove the product and all associated data."""
    path: DeleteProductsParamProductIdRequestPath

# Operation: list_product_images
class GetProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product whose images you want to retrieve.")
class GetProductsParamProductIdImagesRequestQuery(StrictModel):
    since_id: Any | None = Field(default=None, description="Filter results to return only images created after the specified image ID. Useful for pagination when combined with limit parameters.")
    fields: Any | None = Field(default=None, description="Comma-separated list of specific fields to include in the response. Omit to return all available fields for each image.")
class GetProductsParamProductIdImagesRequest(StrictModel):
    """Retrieve all images associated with a specific product. Images are returned in the order they appear in the product's image gallery."""
    path: GetProductsParamProductIdImagesRequestPath
    query: GetProductsParamProductIdImagesRequestQuery | None = None

# Operation: create_product_image
class CreateProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to which the image will be attached. This product must exist in the store.")
class CreateProductsParamProductIdImagesRequest(StrictModel):
    """Upload and attach a new image to a product. The image will be associated with the specified product and can be used for product display across storefronts."""
    path: CreateProductsParamProductIdImagesRequestPath

# Operation: count_product_images
class GetProductsParamProductIdImagesCountRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product for which to count images.")
class GetProductsParamProductIdImagesCountRequestQuery(StrictModel):
    since_id: Any | None = Field(default=None, description="Optional filter to count only images with an ID greater than this value, useful for pagination or incremental updates.")
class GetProductsParamProductIdImagesCountRequest(StrictModel):
    """Retrieve the total count of images associated with a specific product. Optionally filter to count only images added after a specified image ID."""
    path: GetProductsParamProductIdImagesCountRequestPath
    query: GetProductsParamProductIdImagesCountRequestQuery | None = None

# Operation: get_product_image
class GetProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product that contains the image.")
    image_id: str = Field(default=..., description="The unique identifier of the image to retrieve.")
class GetProductsParamProductIdImagesParamImageIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of specific fields to include in the response. If omitted, all fields are returned.")
class GetProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Retrieve a single product image by its ID. Returns detailed metadata for the specified image associated with a product."""
    path: GetProductsParamProductIdImagesParamImageIdRequestPath
    query: GetProductsParamProductIdImagesParamImageIdRequestQuery | None = None

# Operation: update_product_image
class UpdateProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product that contains the image to be updated.")
    image_id: str = Field(default=..., description="The unique identifier of the image within the product to be updated.")
class UpdateProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Update metadata and properties of an existing product image, such as alt text, position, or other image attributes."""
    path: UpdateProductsParamProductIdImagesParamImageIdRequestPath

# Operation: delete_product_image
class DeleteProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product containing the image to delete.")
    image_id: str = Field(default=..., description="The unique identifier of the image to delete from the product.")
class DeleteProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Delete a specific image from a product. This removes the image association and makes it unavailable for the product."""
    path: DeleteProductsParamProductIdImagesParamImageIdRequestPath

# Operation: list_recurring_application_charges
class GetRecurringApplicationChargesRequestQuery(StrictModel):
    since_id: Any | None = Field(default=None, description="Filter results to return only charges created after the specified charge ID, useful for pagination or retrieving newly created charges.")
    fields: Any | None = Field(default=None, description="Comma-separated list of specific fields to include in the response. Omit to receive all available fields for each charge.")
class GetRecurringApplicationChargesRequest(StrictModel):
    """Retrieves a list of all recurring application charges for the store. Use this to view subscription-based charges associated with your app."""
    query: GetRecurringApplicationChargesRequestQuery | None = None

# Operation: get_recurring_application_charge
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to retrieve.")
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="A comma-separated list of specific fields to include in the response. Omit to return all available fields.")
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(StrictModel):
    """Retrieves the details of a single recurring application charge by its ID. Use this to fetch current status, pricing, and other metadata for a specific recurring charge."""
    path: GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath
    query: GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestQuery | None = None

# Operation: delete_recurring_application_charge
class DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to cancel. This ID is returned when the charge is created.")
class DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(StrictModel):
    """Cancels an active recurring application charge for the store. This operation permanently removes the charge and stops any future billing cycles associated with it."""
    path: DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath

# Operation: update_recurring_application_charge_capped_amount
class UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to update. This must be an active charge.")
class UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery(StrictModel):
    recurring_application_charge_capped_amount: int | None = Field(default=None, validation_alias="recurring_application_charge[capped_amount]", serialization_alias="recurring_application_charge[capped_amount]", description="The new maximum billing cap amount for the recurring charge, specified as a monetary value in the store's currency.")
class UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest(StrictModel):
    """Updates the capped amount of an active recurring application charge. This allows you to modify the maximum billing cap for an existing charge without canceling and recreating it."""
    path: UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath
    query: UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery | None = None

# Operation: list_usage_charges_for_recurring_application_charge
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge for which to retrieve usage charges.")
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="A comma-separated list of specific fields to include in the response. Omit to return all available fields.")
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Retrieves all usage charges associated with a specific recurring application charge. Usage charges represent variable fees billed on top of a recurring application charge."""
    path: GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath
    query: GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestQuery | None = None

# Operation: create_usage_charge_for_recurring_application_charge
class CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to which this usage charge will be applied.")
class CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Creates a usage charge against an existing recurring application charge. Usage charges allow you to bill merchants for variable consumption on top of their recurring subscription."""
    path: CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath

# Operation: get_usage_charge
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge that contains the usage charge.")
    usage_charge_id: str = Field(default=..., description="The unique identifier of the usage charge to retrieve.")
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="A comma-separated list of specific fields to include in the response. Omit to return all available fields.")
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest(StrictModel):
    """Retrieves a single usage charge associated with a recurring application charge. Use this to fetch details about a specific metered billing charge."""
    path: GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath
    query: GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestQuery | None = None

# Operation: list_redirects
class GetRedirectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of redirects to return per request. Defaults to 50 and cannot exceed 250.")
    since_id: Any | None = Field(default=None, description="Filter results to return only redirects with IDs greater than this value, useful for cursor-based pagination.")
    path: Any | None = Field(default=None, description="Filter results to show only redirects matching the specified source path.")
    target: Any | None = Field(default=None, description="Filter results to show only redirects pointing to the specified target URL.")
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. Omit to return all fields.")
class GetRedirectsRequest(StrictModel):
    """Retrieves a list of URL redirects configured in the store. Results are paginated using cursor-based links provided in response headers."""
    query: GetRedirectsRequestQuery | None = None

# Operation: get_redirects_count
class GetRedirectsCountRequestQuery(StrictModel):
    path: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific path value.")
    target: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific target URL.")
class GetRedirectsCountRequest(StrictModel):
    """Retrieves the total count of URL redirects in the store, with optional filtering by path or target URL."""
    query: GetRedirectsCountRequestQuery | None = None

# Operation: get_redirect
class GetRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to retrieve.")
class GetRedirectsParamRedirectIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, allowing you to optimize response payload size.")
class GetRedirectsParamRedirectIdRequest(StrictModel):
    """Retrieves a single redirect by its ID. Use this to fetch detailed information about a specific URL redirect configured in the online store."""
    path: GetRedirectsParamRedirectIdRequestPath
    query: GetRedirectsParamRedirectIdRequestQuery | None = None

# Operation: update_redirect
class UpdateRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to update. This ID is required to locate and modify the specific redirect rule.")
class UpdateRedirectsParamRedirectIdRequest(StrictModel):
    """Updates an existing redirect configuration in the online store. Modify redirect rules by specifying the redirect ID and providing updated redirect details."""
    path: UpdateRedirectsParamRedirectIdRequestPath

# Operation: delete_redirect
class DeleteRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to delete.")
class DeleteRedirectsParamRedirectIdRequest(StrictModel):
    """Permanently deletes a redirect from the online store. Once deleted, the redirect cannot be recovered."""
    path: DeleteRedirectsParamRedirectIdRequestPath

# Operation: list_script_tags
class GetScriptTagsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
    since_id: Any | None = Field(default=None, description="Filters results to return only script tags created after the specified tag ID, useful for incremental syncing.")
    fields: Any | None = Field(default=None, description="Comma-separated list of specific fields to include in the response. Omit to return all available fields.")
class GetScriptTagsRequest(StrictModel):
    """Retrieves a paginated list of all script tags in the store. Results are paginated using cursor-based links provided in the response header."""
    query: GetScriptTagsRequestQuery | None = None

# Operation: get_script_tag
class GetScriptTagsParamScriptTagIdRequestPath(StrictModel):
    script_tag_id: str = Field(default=..., description="The unique identifier of the script tag to retrieve.")
class GetScriptTagsParamScriptTagIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="A comma-separated list of specific fields to include in the response. Omit to return all available fields.")
class GetScriptTagsParamScriptTagIdRequest(StrictModel):
    """Retrieves a single script tag by its ID from the online store. Use this to fetch detailed information about a specific script tag resource."""
    path: GetScriptTagsParamScriptTagIdRequestPath
    query: GetScriptTagsParamScriptTagIdRequestQuery | None = None

# Operation: update_script_tag
class UpdateScriptTagsParamScriptTagIdRequestPath(StrictModel):
    script_tag_id: str = Field(default=..., description="The unique identifier of the script tag to update. This ID is returned when the script tag is created and is required to target the correct script tag for modification.")
class UpdateScriptTagsParamScriptTagIdRequest(StrictModel):
    """Updates an existing script tag in the online store. Modify script tag properties such as source URL, event triggers, or display scope."""
    path: UpdateScriptTagsParamScriptTagIdRequestPath

# Operation: delete_script_tag
class DeleteScriptTagsParamScriptTagIdRequestPath(StrictModel):
    script_tag_id: str = Field(default=..., description="The unique identifier of the script tag to delete.")
class DeleteScriptTagsParamScriptTagIdRequest(StrictModel):
    """Permanently deletes a script tag from the store. This removes the associated script injection from the online store."""
    path: DeleteScriptTagsParamScriptTagIdRequestPath

# Operation: list_shipping_zones
class GetShippingZonesRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of specific fields to include in the response. If omitted, all fields are returned.")
class GetShippingZonesRequest(StrictModel):
    """Retrieve all shipping zones configured for the store. Shipping zones define geographic areas and their associated shipping rates and methods."""
    query: GetShippingZonesRequestQuery | None = None

# Operation: get_shop
class GetShopRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="A comma-separated list of specific fields to include in the response. When omitted, all available fields are returned. Use this to optimize response payload by requesting only the fields your application needs.")
class GetShopRequest(StrictModel):
    """Retrieves the shop's configuration and store properties. Use this to access fundamental shop information such as name, currency, timezone, and other store-level settings."""
    query: GetShopRequestQuery | None = None

# Operation: list_shopify_payments_payouts
class GetShopifyPaymentsPayoutsRequestQuery(StrictModel):
    since_id: Any | None = Field(default=None, description="Filter results to payouts made after the specified payout ID, useful for fetching payouts created since a known reference point.")
    date_min: Any | None = Field(default=None, description="Filter results to payouts made on or after the specified date (inclusive). Use ISO 8601 format.")
    date_max: Any | None = Field(default=None, description="Filter results to payouts made on or before the specified date (inclusive). Use ISO 8601 format.")
    status: Any | None = Field(default=None, description="Filter results to payouts with a specific status (e.g., pending, paid, failed, cancelled).")
class GetShopifyPaymentsPayoutsRequest(StrictModel):
    """Retrieves a list of all payouts ordered by most recent first. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""
    query: GetShopifyPaymentsPayoutsRequestQuery | None = None

# Operation: get_payout
class GetShopifyPaymentsPayoutsParamPayoutIdRequestPath(StrictModel):
    payout_id: str = Field(default=..., description="The unique identifier of the payout to retrieve.")
class GetShopifyPaymentsPayoutsParamPayoutIdRequest(StrictModel):
    """Retrieves the details of a single Shopify Payments payout by its unique identifier."""
    path: GetShopifyPaymentsPayoutsParamPayoutIdRequestPath

# Operation: list_smart_collections
class GetSmartCollectionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of smart collections to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
    ids: Any | None = Field(default=None, description="Filter results to only smart collections with the specified IDs. Provide as a comma-separated list of numeric IDs.")
    since_id: Any | None = Field(default=None, description="Return only smart collections with an ID greater than this value. Useful for pagination when not using link headers.")
    title: Any | None = Field(default=None, description="Filter results to smart collections matching the exact title.")
    product_id: Any | None = Field(default=None, description="Filter results to only smart collections that contain the specified product ID.")
    handle: Any | None = Field(default=None, description="Filter results by the smart collection's URL-friendly handle.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status. Use 'published' for published collections only, 'unpublished' for unpublished only, or 'any' to include all collections regardless of status. Defaults to 'any'.")
    fields: Any | None = Field(default=None, description="Limit the response to only specified fields. Provide as a comma-separated list of field names to reduce payload size.")
class GetSmartCollectionsRequest(StrictModel):
    """Retrieves a paginated list of smart collections from your store. Results are paginated using link headers in the response; use the provided links to navigate between pages."""
    query: GetSmartCollectionsRequestQuery | None = None

# Operation: count_smart_collections
class GetSmartCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter to smart collections with an exact matching title.")
    product_id: Any | None = Field(default=None, description="Filter to smart collections that contain the specified product ID.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for live collections, 'unpublished' for draft collections, or 'any' to include all collections regardless of status. Defaults to 'any'.")
class GetSmartCollectionsCountRequest(StrictModel):
    """Retrieves the total count of smart collections, optionally filtered by title, product inclusion, or published status."""
    query: GetSmartCollectionsCountRequestQuery | None = None

# Operation: get_smart_collection
class GetSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to retrieve.")
class GetSmartCollectionsParamSmartCollectionIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size.")
class GetSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Retrieves a single smart collection by ID. Use this to fetch detailed information about a specific smart collection, including its rules, products, and metadata."""
    path: GetSmartCollectionsParamSmartCollectionIdRequestPath
    query: GetSmartCollectionsParamSmartCollectionIdRequestQuery | None = None

# Operation: update_smart_collection
class UpdateSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to update.")
class UpdateSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Updates an existing smart collection by ID. Modify collection properties such as title, rules, sorting, and visibility settings."""
    path: UpdateSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: delete_smart_collection
class DeleteSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to delete.")
class DeleteSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Permanently removes a smart collection from the store. This action cannot be undone."""
    path: DeleteSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: update_smart_collection_order
class UpdateSmartCollectionsParamSmartCollectionIdOrderRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to update.")
class UpdateSmartCollectionsParamSmartCollectionIdOrderRequestQuery(StrictModel):
    products: Any | None = Field(default=None, description="An ordered array of product IDs to pin at the top of the collection. Pass an empty array to clear any previously pinned products and return to automatic sorting.")
    sort_order: Any | None = Field(default=None, description="The automatic sorting method to apply to the collection (e.g., alphabetical, price, newest). If not specified, the current sort order is preserved.")
class UpdateSmartCollectionsParamSmartCollectionIdOrderRequest(StrictModel):
    """Updates the sorting configuration for products in a smart collection, allowing you to manually order specific products at the top or apply an automatic sort order."""
    path: UpdateSmartCollectionsParamSmartCollectionIdOrderRequestPath
    query: UpdateSmartCollectionsParamSmartCollectionIdOrderRequestQuery | None = None

# Operation: list_tender_transactions
class GetTenderTransactionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 if not specified.")
    since_id: Any | None = Field(default=None, description="Retrieve only transactions with an ID greater than this value, useful for resuming pagination or fetching incremental updates.")
    processed_at_min: Any | None = Field(default=None, description="Filter to show only transactions processed on or after this date (ISO 8601 format).")
    processed_at_max: Any | None = Field(default=None, description="Filter to show only transactions processed on or before this date (ISO 8601 format).")
    order: Any | None = Field(default=None, description="Sort results by processed_at timestamp in either ascending or descending order.")
class GetTenderTransactionsRequest(StrictModel):
    """Retrieves a paginated list of tender transactions. Results are paginated using link headers in the response; use the provided links to navigate through pages rather than manual offset calculations."""
    query: GetTenderTransactionsRequestQuery | None = None

# Operation: list_themes
class GetThemesRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of specific theme fields to return in the response. Omit to retrieve all available fields for each theme.")
class GetThemesRequest(StrictModel):
    """Retrieves a list of all themes available in the Shopify store. Use this to discover theme IDs and metadata for further operations."""
    query: GetThemesRequestQuery | None = None

# Operation: get_theme
class GetThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to retrieve.")
class GetThemesParamThemeIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of field names to include in the response. When specified, only the listed fields are returned, reducing payload size.")
class GetThemesParamThemeIdRequest(StrictModel):
    """Retrieves a single theme by its ID from the Shopify online store."""
    path: GetThemesParamThemeIdRequestPath
    query: GetThemesParamThemeIdRequestQuery | None = None

# Operation: delete_theme
class DeleteThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to delete, returned as a string by the Shopify API.")
class DeleteThemesParamThemeIdRequest(StrictModel):
    """Permanently deletes a theme from the store. The theme must not be the currently active theme."""
    path: DeleteThemesParamThemeIdRequestPath

# Operation: get_theme_asset
class GetThemesParamThemeIdAssetsRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme containing the asset.")
class GetThemesParamThemeIdAssetsRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of specific fields to include in the response. If omitted, all asset fields are returned.")
    asset_key: str | None = Field(default=None, validation_alias="asset[key]", serialization_alias="asset[key]", description="The key path of the asset to retrieve, such as templates/index.liquid or config/settings_data.json. This parameter is required to fetch a specific asset.")
class GetThemesParamThemeIdAssetsRequest(StrictModel):
    """Retrieves a single asset file from a theme by its key. Use the asset[key] parameter to specify which asset to retrieve, such as templates/index.liquid or other theme files."""
    path: GetThemesParamThemeIdAssetsRequestPath
    query: GetThemesParamThemeIdAssetsRequestQuery | None = None

# Operation: delete_theme_asset
class DeleteThemesParamThemeIdAssetsRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme from which the asset will be deleted.")
class DeleteThemesParamThemeIdAssetsRequestQuery(StrictModel):
    asset_key: str | None = Field(default=None, validation_alias="asset[key]", serialization_alias="asset[key]", description="The key (file path) of the asset to delete from the theme. This identifies which specific asset file to remove.")
class DeleteThemesParamThemeIdAssetsRequest(StrictModel):
    """Removes a specific asset file from a theme. The asset is identified by its key within the theme."""
    path: DeleteThemesParamThemeIdAssetsRequestPath
    query: DeleteThemesParamThemeIdAssetsRequestQuery | None = None

# Operation: list_webhooks
class GetWebhooksRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter webhooks by the URI endpoint where they send POST requests.")
    fields: Any | None = Field(default=None, description="Comma-separated list of specific properties to return for each webhook. Omit to receive all properties.")
    limit: Any | None = Field(default=None, description="Maximum number of webhooks to return per request. Defaults to 50; maximum allowed is 250.")
    since_id: Any | None = Field(default=None, description="Return only webhooks with an ID greater than this value. Use for pagination when combined with limit.")
    topic: Any | None = Field(default=None, description="Filter webhooks by topic (e.g., orders/create, products/update). Refer to webhook topic documentation for valid values.")
class GetWebhooksRequest(StrictModel):
    """Retrieves a list of webhook subscriptions configured for your store. Results are paginated using link headers in the response."""
    query: GetWebhooksRequestQuery | None = None

# Operation: get_webhooks_count
class GetWebhooksCountRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter the count to only include webhook subscriptions that send POST requests to this specific URI.")
    topic: Any | None = Field(default=None, description="Filter the count to only include webhook subscriptions for a specific event topic (e.g., orders/create, products/update). Refer to Shopify's webhook topic documentation for valid values.")
class GetWebhooksCountRequest(StrictModel):
    """Retrieves the total count of webhook subscriptions configured for your Shopify store, with optional filtering by destination address or event topic."""
    query: GetWebhooksCountRequestQuery | None = None

# Operation: get_webhook
class GetWebhooksParamWebhookIdRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook subscription to retrieve.")
class GetWebhooksParamWebhookIdRequestQuery(StrictModel):
    fields: Any | None = Field(default=None, description="Comma-separated list of specific webhook properties to return in the response. When omitted, all properties are returned.")
class GetWebhooksParamWebhookIdRequest(StrictModel):
    """Retrieves the details of a single webhook subscription by its ID, including its configuration and event subscriptions."""
    path: GetWebhooksParamWebhookIdRequestPath
    query: GetWebhooksParamWebhookIdRequestQuery | None = None

# Operation: delete_webhook
class DeleteWebhooksParamWebhookIdRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook subscription to delete.")
class DeleteWebhooksParamWebhookIdRequest(StrictModel):
    """Permanently delete a webhook subscription by its ID. Once deleted, the webhook will no longer receive event notifications."""
    path: DeleteWebhooksParamWebhookIdRequestPath

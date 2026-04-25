"""
Shopify Admin MCP Server - Pydantic Models

Generated: 2026-04-25 19:22:51 UTC
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
    "CreateReportsRequest",
    "DeleteBlogsParamBlogIdArticlesParamArticleIdRequest",
    "DeleteCarrierServicesParamCarrierServiceIdRequest",
    "DeleteCollectionListingsParamCollectionListingIdRequest",
    "DeleteCollectsParamCollectIdRequest",
    "DeleteCountriesParamCountryIdRequest",
    "DeleteCustomCollectionsParamCustomCollectionIdRequest",
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
    "DeleteReportsParamReportIdRequest",
    "DeleteScriptTagsParamScriptTagIdRequest",
    "DeleteSmartCollectionsParamSmartCollectionIdRequest",
    "DeleteStorefrontAccessTokensParamStorefrontAccessTokenIdRequest",
    "DeleteThemesParamThemeIdAssetsRequest",
    "DeleteThemesParamThemeIdRequest",
    "Deprecated202001CreateCommentsParamCommentIdApproveRequest",
    "Deprecated202001CreateCommentsParamCommentIdNotSpamRequest",
    "Deprecated202001CreateCommentsParamCommentIdRestoreRequest",
    "Deprecated202001CreateCommentsParamCommentIdSpamRequest",
    "Deprecated202001CreateCustomersParamCustomerIdAccountActivationUrlRequest",
    "Deprecated202001CreateCustomersParamCustomerIdAddressesRequest",
    "Deprecated202001CreateCustomersParamCustomerIdSendInviteRequest",
    "Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest",
    "Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest",
    "Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest",
    "Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest",
    "Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest",
    "Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest",
    "Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest",
    "Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest",
    "Deprecated202001CreateFulfillmentsParamFulfillmentIdCancelRequest",
    "Deprecated202001CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest",
    "Deprecated202001CreateGiftCardsParamGiftCardIdDisableRequest",
    "Deprecated202001CreateOrdersParamOrderIdCancelRequest",
    "Deprecated202001CreateOrdersParamOrderIdCloseRequest",
    "Deprecated202001CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest",
    "Deprecated202001CreateOrdersParamOrderIdFulfillmentsRequest",
    "Deprecated202001CreateOrdersParamOrderIdOpenRequest",
    "Deprecated202001CreateOrdersParamOrderIdRefundsCalculateRequest",
    "Deprecated202001CreateOrdersParamOrderIdRefundsRequest",
    "Deprecated202001CreateOrdersParamOrderIdRisksRequest",
    "Deprecated202001CreatePriceRulesParamPriceRuleIdBatchRequest",
    "Deprecated202001CreateProductsParamProductIdImagesRequest",
    "Deprecated202001CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest",
    "Deprecated202001CreateReportsRequest",
    "Deprecated202001DeleteBlogsParamBlogIdArticlesParamArticleIdRequest",
    "Deprecated202001DeleteBlogsParamBlogIdRequest",
    "Deprecated202001DeleteCarrierServicesParamCarrierServiceIdRequest",
    "Deprecated202001DeleteCollectionListingsParamCollectionListingIdRequest",
    "Deprecated202001DeleteCollectsParamCollectIdRequest",
    "Deprecated202001DeleteCountriesParamCountryIdRequest",
    "Deprecated202001DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202001DeleteCustomersParamCustomerIdRequest",
    "Deprecated202001DeleteFulfillmentServicesParamFulfillmentServiceIdRequest",
    "Deprecated202001DeleteInventoryLevelsRequest",
    "Deprecated202001DeleteOrdersParamOrderIdRequest",
    "Deprecated202001DeleteOrdersParamOrderIdRisksParamRiskIdRequest",
    "Deprecated202001DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "Deprecated202001DeleteProductListingsParamProductListingIdRequest",
    "Deprecated202001DeleteProductsParamProductIdImagesParamImageIdRequest",
    "Deprecated202001DeleteProductsParamProductIdRequest",
    "Deprecated202001DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest",
    "Deprecated202001DeleteRedirectsParamRedirectIdRequest",
    "Deprecated202001DeleteReportsParamReportIdRequest",
    "Deprecated202001DeleteSmartCollectionsParamSmartCollectionIdRequest",
    "Deprecated202001DeleteThemesParamThemeIdAssetsRequest",
    "Deprecated202001DeleteThemesParamThemeIdRequest",
    "Deprecated202001GetApplicationChargesParamApplicationChargeIdRequest",
    "Deprecated202001GetAssignedFulfillmentOrdersRequest",
    "Deprecated202001GetBlogsParamBlogIdArticlesCountRequest",
    "Deprecated202001GetBlogsParamBlogIdArticlesParamArticleIdRequest",
    "Deprecated202001GetBlogsParamBlogIdArticlesRequest",
    "Deprecated202001GetBlogsParamBlogIdRequest",
    "Deprecated202001GetCheckoutsCountRequest",
    "Deprecated202001GetCheckoutsParamTokenShippingRatesRequest",
    "Deprecated202001GetCollectionListingsParamCollectionListingIdProductIdsRequest",
    "Deprecated202001GetCollectionsParamCollectionIdProductsRequest",
    "Deprecated202001GetCollectionsParamCollectionIdRequest",
    "Deprecated202001GetCollectsCountRequest",
    "Deprecated202001GetCollectsParamCollectIdRequest",
    "Deprecated202001GetCollectsRequest",
    "Deprecated202001GetCountriesParamCountryIdProvincesCountRequest",
    "Deprecated202001GetCountriesParamCountryIdProvincesRequest",
    "Deprecated202001GetCountriesParamCountryIdRequest",
    "Deprecated202001GetCustomCollectionsCountRequest",
    "Deprecated202001GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequest",
    "Deprecated202001GetCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202001GetCustomersParamCustomerIdAddressesRequest",
    "Deprecated202001GetCustomersParamCustomerIdOrdersRequest",
    "Deprecated202001GetCustomersParamCustomerIdRequest",
    "Deprecated202001GetCustomersRequest",
    "Deprecated202001GetEventsParamEventIdRequest",
    "Deprecated202001GetEventsRequest",
    "Deprecated202001GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest",
    "Deprecated202001GetFulfillmentOrdersParamFulfillmentOrderIdRequest",
    "Deprecated202001GetGiftCardsCountRequest",
    "Deprecated202001GetGiftCardsRequest",
    "Deprecated202001GetGiftCardsSearchRequest",
    "Deprecated202001GetInventoryItemsRequest",
    "Deprecated202001GetInventoryLevelsRequest",
    "Deprecated202001GetLocationsParamLocationIdInventoryLevelsRequest",
    "Deprecated202001GetLocationsParamLocationIdRequest",
    "Deprecated202001GetOrdersCountRequest",
    "Deprecated202001GetOrdersParamOrderIdFulfillmentOrdersRequest",
    "Deprecated202001GetOrdersParamOrderIdFulfillmentsCountRequest",
    "Deprecated202001GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest",
    "Deprecated202001GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "Deprecated202001GetOrdersParamOrderIdFulfillmentsRequest",
    "Deprecated202001GetOrdersParamOrderIdRefundsParamRefundIdRequest",
    "Deprecated202001GetOrdersParamOrderIdRefundsRequest",
    "Deprecated202001GetOrdersParamOrderIdRequest",
    "Deprecated202001GetOrdersParamOrderIdRisksParamRiskIdRequest",
    "Deprecated202001GetOrdersParamOrderIdRisksRequest",
    "Deprecated202001GetOrdersRequest",
    "Deprecated202001GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest",
    "Deprecated202001GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest",
    "Deprecated202001GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "Deprecated202001GetPriceRulesParamPriceRuleIdDiscountCodesRequest",
    "Deprecated202001GetProductsCountRequest",
    "Deprecated202001GetProductsParamProductIdImagesCountRequest",
    "Deprecated202001GetProductsParamProductIdImagesRequest",
    "Deprecated202001GetProductsParamProductIdRequest",
    "Deprecated202001GetProductsRequest",
    "Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequest",
    "Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest",
    "Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest",
    "Deprecated202001GetRedirectsCountRequest",
    "Deprecated202001GetRedirectsParamRedirectIdRequest",
    "Deprecated202001GetRedirectsRequest",
    "Deprecated202001GetReportsParamReportIdRequest",
    "Deprecated202001GetShopifyPaymentsBalanceTransactionsRequest",
    "Deprecated202001GetShopifyPaymentsDisputesRequest",
    "Deprecated202001GetShopifyPaymentsPayoutsParamPayoutIdRequest",
    "Deprecated202001GetShopifyPaymentsPayoutsRequest",
    "Deprecated202001GetSmartCollectionsCountRequest",
    "Deprecated202001GetSmartCollectionsRequest",
    "Deprecated202001GetTenderTransactionsRequest",
    "Deprecated202001GetThemesParamThemeIdRequest",
    "Deprecated202001GetWebhooksCountRequest",
    "Deprecated202001GetWebhooksRequest",
    "Deprecated202001UpdateCarrierServicesParamCarrierServiceIdRequest",
    "Deprecated202001UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest",
    "Deprecated202001UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202001UpdateCustomersParamCustomerIdAddressesSetRequest",
    "Deprecated202001UpdateCustomersParamCustomerIdRequest",
    "Deprecated202001UpdateGiftCardsParamGiftCardIdRequest",
    "Deprecated202001UpdateInventoryItemsParamInventoryItemIdRequest",
    "Deprecated202001UpdateMetafieldsParamMetafieldIdRequest",
    "Deprecated202001UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "Deprecated202001UpdateOrdersParamOrderIdRequest",
    "Deprecated202001UpdateOrdersParamOrderIdRisksParamRiskIdRequest",
    "Deprecated202001UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "Deprecated202001UpdateProductListingsParamProductListingIdRequest",
    "Deprecated202001UpdateProductsParamProductIdImagesParamImageIdRequest",
    "Deprecated202001UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest",
    "Deprecated202001UpdateRedirectsParamRedirectIdRequest",
    "Deprecated202001UpdateSmartCollectionsParamSmartCollectionIdRequest",
    "Deprecated202001UpdateThemesParamThemeIdRequest",
    "Deprecated202004CreateBlogsParamBlogIdArticlesRequest",
    "Deprecated202004CreateCustomersParamCustomerIdAccountActivationUrlRequest",
    "Deprecated202004CreateCustomersParamCustomerIdAddressesRequest",
    "Deprecated202004CreateCustomersParamCustomerIdSendInviteRequest",
    "Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest",
    "Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest",
    "Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest",
    "Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest",
    "Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest",
    "Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest",
    "Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest",
    "Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest",
    "Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequest",
    "Deprecated202004CreateFulfillmentsParamFulfillmentIdCancelRequest",
    "Deprecated202004CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest",
    "Deprecated202004CreateGiftCardsParamGiftCardIdDisableRequest",
    "Deprecated202004CreateOrdersParamOrderIdCancelRequest",
    "Deprecated202004CreateOrdersParamOrderIdCloseRequest",
    "Deprecated202004CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest",
    "Deprecated202004CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequest",
    "Deprecated202004CreateOrdersParamOrderIdFulfillmentsRequest",
    "Deprecated202004CreateOrdersParamOrderIdOpenRequest",
    "Deprecated202004CreateOrdersParamOrderIdRefundsCalculateRequest",
    "Deprecated202004CreateOrdersParamOrderIdRefundsRequest",
    "Deprecated202004CreateOrdersParamOrderIdRisksRequest",
    "Deprecated202004CreatePriceRulesParamPriceRuleIdBatchRequest",
    "Deprecated202004CreateProductsParamProductIdImagesRequest",
    "Deprecated202004CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest",
    "Deprecated202004CreateReportsRequest",
    "Deprecated202004DeleteBlogsParamBlogIdArticlesParamArticleIdRequest",
    "Deprecated202004DeleteCarrierServicesParamCarrierServiceIdRequest",
    "Deprecated202004DeleteCollectionListingsParamCollectionListingIdRequest",
    "Deprecated202004DeleteCollectsParamCollectIdRequest",
    "Deprecated202004DeleteCountriesParamCountryIdRequest",
    "Deprecated202004DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202004DeleteCustomersParamCustomerIdRequest",
    "Deprecated202004DeleteFulfillmentServicesParamFulfillmentServiceIdRequest",
    "Deprecated202004DeleteInventoryLevelsRequest",
    "Deprecated202004DeleteOrdersParamOrderIdRequest",
    "Deprecated202004DeleteOrdersParamOrderIdRisksParamRiskIdRequest",
    "Deprecated202004DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "Deprecated202004DeleteProductListingsParamProductListingIdRequest",
    "Deprecated202004DeleteProductsParamProductIdImagesParamImageIdRequest",
    "Deprecated202004DeleteProductsParamProductIdRequest",
    "Deprecated202004DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest",
    "Deprecated202004DeleteRedirectsParamRedirectIdRequest",
    "Deprecated202004DeleteReportsParamReportIdRequest",
    "Deprecated202004DeleteSmartCollectionsParamSmartCollectionIdRequest",
    "Deprecated202004DeleteThemesParamThemeIdAssetsRequest",
    "Deprecated202004DeleteThemesParamThemeIdRequest",
    "Deprecated202004GetApplicationChargesParamApplicationChargeIdRequest",
    "Deprecated202004GetBlogsParamBlogIdArticlesCountRequest",
    "Deprecated202004GetBlogsParamBlogIdArticlesParamArticleIdRequest",
    "Deprecated202004GetBlogsParamBlogIdArticlesRequest",
    "Deprecated202004GetCheckoutsCountRequest",
    "Deprecated202004GetCheckoutsParamTokenShippingRatesRequest",
    "Deprecated202004GetCollectionsParamCollectionIdProductsRequest",
    "Deprecated202004GetCollectionsParamCollectionIdRequest",
    "Deprecated202004GetCollectsCountRequest",
    "Deprecated202004GetCollectsParamCollectIdRequest",
    "Deprecated202004GetCollectsRequest",
    "Deprecated202004GetCountriesParamCountryIdProvincesCountRequest",
    "Deprecated202004GetCountriesParamCountryIdProvincesRequest",
    "Deprecated202004GetCustomCollectionsCountRequest",
    "Deprecated202004GetCustomCollectionsRequest",
    "Deprecated202004GetCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202004GetCustomersParamCustomerIdAddressesRequest",
    "Deprecated202004GetCustomersParamCustomerIdOrdersRequest",
    "Deprecated202004GetCustomersParamCustomerIdRequest",
    "Deprecated202004GetCustomersRequest",
    "Deprecated202004GetCustomersSearchRequest",
    "Deprecated202004GetEventsParamEventIdRequest",
    "Deprecated202004GetEventsRequest",
    "Deprecated202004GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest",
    "Deprecated202004GetFulfillmentOrdersParamFulfillmentOrderIdRequest",
    "Deprecated202004GetGiftCardsCountRequest",
    "Deprecated202004GetGiftCardsRequest",
    "Deprecated202004GetGiftCardsSearchRequest",
    "Deprecated202004GetInventoryItemsRequest",
    "Deprecated202004GetInventoryLevelsRequest",
    "Deprecated202004GetLocationsParamLocationIdInventoryLevelsRequest",
    "Deprecated202004GetLocationsParamLocationIdRequest",
    "Deprecated202004GetOrdersCountRequest",
    "Deprecated202004GetOrdersParamOrderIdFulfillmentOrdersRequest",
    "Deprecated202004GetOrdersParamOrderIdFulfillmentsCountRequest",
    "Deprecated202004GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest",
    "Deprecated202004GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "Deprecated202004GetOrdersParamOrderIdFulfillmentsRequest",
    "Deprecated202004GetOrdersParamOrderIdRefundsParamRefundIdRequest",
    "Deprecated202004GetOrdersParamOrderIdRefundsRequest",
    "Deprecated202004GetOrdersParamOrderIdRequest",
    "Deprecated202004GetOrdersParamOrderIdRisksParamRiskIdRequest",
    "Deprecated202004GetOrdersParamOrderIdRisksRequest",
    "Deprecated202004GetOrdersRequest",
    "Deprecated202004GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest",
    "Deprecated202004GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest",
    "Deprecated202004GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "Deprecated202004GetPriceRulesParamPriceRuleIdDiscountCodesRequest",
    "Deprecated202004GetProductsCountRequest",
    "Deprecated202004GetProductsParamProductIdImagesCountRequest",
    "Deprecated202004GetProductsParamProductIdImagesRequest",
    "Deprecated202004GetProductsParamProductIdRequest",
    "Deprecated202004GetProductsRequest",
    "Deprecated202004GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequest",
    "Deprecated202004GetRedirectsCountRequest",
    "Deprecated202004GetRedirectsParamRedirectIdRequest",
    "Deprecated202004GetRedirectsRequest",
    "Deprecated202004GetReportsParamReportIdRequest",
    "Deprecated202004GetShopifyPaymentsDisputesRequest",
    "Deprecated202004GetShopifyPaymentsPayoutsParamPayoutIdRequest",
    "Deprecated202004GetShopifyPaymentsPayoutsRequest",
    "Deprecated202004GetSmartCollectionsCountRequest",
    "Deprecated202004GetSmartCollectionsRequest",
    "Deprecated202004GetThemesParamThemeIdRequest",
    "Deprecated202004GetWebhooksCountRequest",
    "Deprecated202004GetWebhooksRequest",
    "Deprecated202004UpdateBlogsParamBlogIdArticlesParamArticleIdRequest",
    "Deprecated202004UpdateCarrierServicesParamCarrierServiceIdRequest",
    "Deprecated202004UpdateCountriesParamCountryIdProvincesParamProvinceIdRequest",
    "Deprecated202004UpdateCountriesParamCountryIdRequest",
    "Deprecated202004UpdateCustomCollectionsParamCustomCollectionIdRequest",
    "Deprecated202004UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest",
    "Deprecated202004UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202004UpdateCustomersParamCustomerIdAddressesSetRequest",
    "Deprecated202004UpdateCustomersParamCustomerIdRequest",
    "Deprecated202004UpdateGiftCardsParamGiftCardIdRequest",
    "Deprecated202004UpdateInventoryItemsParamInventoryItemIdRequest",
    "Deprecated202004UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "Deprecated202004UpdateOrdersParamOrderIdRequest",
    "Deprecated202004UpdateOrdersParamOrderIdRisksParamRiskIdRequest",
    "Deprecated202004UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "Deprecated202004UpdateProductsParamProductIdImagesParamImageIdRequest",
    "Deprecated202004UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest",
    "Deprecated202004UpdateRedirectsParamRedirectIdRequest",
    "Deprecated202004UpdateSmartCollectionsParamSmartCollectionIdRequest",
    "Deprecated202004UpdateThemesParamThemeIdRequest",
    "Deprecated202007CreateBlogsParamBlogIdArticlesRequest",
    "Deprecated202007CreateCustomersParamCustomerIdAccountActivationUrlRequest",
    "Deprecated202007CreateCustomersParamCustomerIdAddressesRequest",
    "Deprecated202007CreateCustomersParamCustomerIdSendInviteRequest",
    "Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest",
    "Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest",
    "Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest",
    "Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest",
    "Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest",
    "Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest",
    "Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest",
    "Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest",
    "Deprecated202007CreateFulfillmentsParamFulfillmentIdCancelRequest",
    "Deprecated202007CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest",
    "Deprecated202007CreateGiftCardsParamGiftCardIdDisableRequest",
    "Deprecated202007CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest",
    "Deprecated202007CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequest",
    "Deprecated202007CreateOrdersParamOrderIdFulfillmentsRequest",
    "Deprecated202007CreateOrdersParamOrderIdRefundsCalculateRequest",
    "Deprecated202007CreateOrdersParamOrderIdRefundsRequest",
    "Deprecated202007CreateOrdersParamOrderIdRisksRequest",
    "Deprecated202007CreatePriceRulesParamPriceRuleIdBatchRequest",
    "Deprecated202007CreatePriceRulesParamPriceRuleIdDiscountCodesRequest",
    "Deprecated202007CreateProductsParamProductIdImagesRequest",
    "Deprecated202007CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest",
    "Deprecated202007CreateReportsRequest",
    "Deprecated202007DeleteBlogsParamBlogIdArticlesParamArticleIdRequest",
    "Deprecated202007DeleteCollectionListingsParamCollectionListingIdRequest",
    "Deprecated202007DeleteCollectsParamCollectIdRequest",
    "Deprecated202007DeleteCountriesParamCountryIdRequest",
    "Deprecated202007DeleteCustomCollectionsParamCustomCollectionIdRequest",
    "Deprecated202007DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202007DeleteCustomersParamCustomerIdRequest",
    "Deprecated202007DeleteInventoryLevelsRequest",
    "Deprecated202007DeleteOrdersParamOrderIdRisksParamRiskIdRequest",
    "Deprecated202007DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "Deprecated202007DeleteProductListingsParamProductListingIdRequest",
    "Deprecated202007DeleteProductsParamProductIdImagesParamImageIdRequest",
    "Deprecated202007DeleteProductsParamProductIdRequest",
    "Deprecated202007DeleteRedirectsParamRedirectIdRequest",
    "Deprecated202007DeleteReportsParamReportIdRequest",
    "Deprecated202007DeleteSmartCollectionsParamSmartCollectionIdRequest",
    "Deprecated202007DeleteThemesParamThemeIdAssetsRequest",
    "Deprecated202007DeleteThemesParamThemeIdRequest",
    "Deprecated202007GetApplicationChargesParamApplicationChargeIdRequest",
    "Deprecated202007GetBlogsParamBlogIdArticlesCountRequest",
    "Deprecated202007GetBlogsParamBlogIdArticlesParamArticleIdRequest",
    "Deprecated202007GetBlogsParamBlogIdArticlesRequest",
    "Deprecated202007GetCheckoutsCountRequest",
    "Deprecated202007GetCheckoutsParamTokenShippingRatesRequest",
    "Deprecated202007GetCollectionListingsParamCollectionListingIdProductIdsRequest",
    "Deprecated202007GetCollectionsParamCollectionIdProductsRequest",
    "Deprecated202007GetCollectionsParamCollectionIdRequest",
    "Deprecated202007GetCollectsCountRequest",
    "Deprecated202007GetCollectsParamCollectIdRequest",
    "Deprecated202007GetCollectsRequest",
    "Deprecated202007GetCountriesParamCountryIdProvincesCountRequest",
    "Deprecated202007GetCountriesParamCountryIdProvincesRequest",
    "Deprecated202007GetCustomCollectionsCountRequest",
    "Deprecated202007GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequest",
    "Deprecated202007GetCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202007GetCustomersParamCustomerIdAddressesRequest",
    "Deprecated202007GetCustomersParamCustomerIdOrdersRequest",
    "Deprecated202007GetCustomersParamCustomerIdRequest",
    "Deprecated202007GetCustomersRequest",
    "Deprecated202007GetDiscountCodesLookupRequest",
    "Deprecated202007GetEventsParamEventIdRequest",
    "Deprecated202007GetEventsRequest",
    "Deprecated202007GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest",
    "Deprecated202007GetFulfillmentOrdersParamFulfillmentOrderIdRequest",
    "Deprecated202007GetGiftCardsCountRequest",
    "Deprecated202007GetGiftCardsRequest",
    "Deprecated202007GetGiftCardsSearchRequest",
    "Deprecated202007GetInventoryItemsParamInventoryItemIdRequest",
    "Deprecated202007GetInventoryItemsRequest",
    "Deprecated202007GetInventoryLevelsRequest",
    "Deprecated202007GetLocationsParamLocationIdInventoryLevelsRequest",
    "Deprecated202007GetLocationsParamLocationIdRequest",
    "Deprecated202007GetOrdersParamOrderIdFulfillmentOrdersRequest",
    "Deprecated202007GetOrdersParamOrderIdFulfillmentsCountRequest",
    "Deprecated202007GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest",
    "Deprecated202007GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "Deprecated202007GetOrdersParamOrderIdFulfillmentsRequest",
    "Deprecated202007GetOrdersParamOrderIdRefundsParamRefundIdRequest",
    "Deprecated202007GetOrdersParamOrderIdRefundsRequest",
    "Deprecated202007GetOrdersParamOrderIdRisksRequest",
    "Deprecated202007GetOrdersRequest",
    "Deprecated202007GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest",
    "Deprecated202007GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest",
    "Deprecated202007GetPriceRulesParamPriceRuleIdDiscountCodesRequest",
    "Deprecated202007GetProductsCountRequest",
    "Deprecated202007GetProductsParamProductIdImagesCountRequest",
    "Deprecated202007GetProductsParamProductIdImagesParamImageIdRequest",
    "Deprecated202007GetProductsParamProductIdImagesRequest",
    "Deprecated202007GetProductsParamProductIdRequest",
    "Deprecated202007GetProductsRequest",
    "Deprecated202007GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest",
    "Deprecated202007GetRedirectsCountRequest",
    "Deprecated202007GetRedirectsParamRedirectIdRequest",
    "Deprecated202007GetRedirectsRequest",
    "Deprecated202007GetReportsParamReportIdRequest",
    "Deprecated202007GetShopifyPaymentsPayoutsParamPayoutIdRequest",
    "Deprecated202007GetShopifyPaymentsPayoutsRequest",
    "Deprecated202007GetSmartCollectionsCountRequest",
    "Deprecated202007GetSmartCollectionsParamSmartCollectionIdRequest",
    "Deprecated202007GetSmartCollectionsRequest",
    "Deprecated202007GetTenderTransactionsRequest",
    "Deprecated202007GetThemesParamThemeIdAssetsRequest",
    "Deprecated202007GetThemesParamThemeIdRequest",
    "Deprecated202007GetWebhooksCountRequest",
    "Deprecated202007GetWebhooksRequest",
    "Deprecated202007UpdateCarrierServicesParamCarrierServiceIdRequest",
    "Deprecated202007UpdateCountriesParamCountryIdProvincesParamProvinceIdRequest",
    "Deprecated202007UpdateCountriesParamCountryIdRequest",
    "Deprecated202007UpdateCustomCollectionsParamCustomCollectionIdRequest",
    "Deprecated202007UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest",
    "Deprecated202007UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202007UpdateCustomersParamCustomerIdAddressesSetRequest",
    "Deprecated202007UpdateCustomersParamCustomerIdRequest",
    "Deprecated202007UpdateGiftCardsParamGiftCardIdRequest",
    "Deprecated202007UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "Deprecated202007UpdateOrdersParamOrderIdRisksParamRiskIdRequest",
    "Deprecated202007UpdateProductListingsParamProductListingIdRequest",
    "Deprecated202007UpdateProductsParamProductIdImagesParamImageIdRequest",
    "Deprecated202007UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest",
    "Deprecated202007UpdateRedirectsParamRedirectIdRequest",
    "Deprecated202007UpdateSmartCollectionsParamSmartCollectionIdRequest",
    "Deprecated202007UpdateThemesParamThemeIdRequest",
    "Deprecated202101CreateBlogsParamBlogIdArticlesRequest",
    "Deprecated202101CreateCheckoutsParamTokenCompleteRequest",
    "Deprecated202101CreateCustomersParamCustomerIdAccountActivationUrlRequest",
    "Deprecated202101CreateCustomersParamCustomerIdAddressesRequest",
    "Deprecated202101CreateCustomersParamCustomerIdSendInviteRequest",
    "Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest",
    "Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest",
    "Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest",
    "Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest",
    "Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest",
    "Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest",
    "Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest",
    "Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest",
    "Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdOpenRequest",
    "Deprecated202101CreateFulfillmentsParamFulfillmentIdCancelRequest",
    "Deprecated202101CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest",
    "Deprecated202101CreateGiftCardsParamGiftCardIdDisableRequest",
    "Deprecated202101CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequest",
    "Deprecated202101CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest",
    "Deprecated202101CreateOrdersParamOrderIdFulfillmentsRequest",
    "Deprecated202101CreateOrdersParamOrderIdRefundsCalculateRequest",
    "Deprecated202101CreateOrdersParamOrderIdRefundsRequest",
    "Deprecated202101CreateOrdersParamOrderIdRisksRequest",
    "Deprecated202101CreatePriceRulesParamPriceRuleIdBatchRequest",
    "Deprecated202101CreateProductsParamProductIdImagesRequest",
    "Deprecated202101CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest",
    "Deprecated202101CreateReportsRequest",
    "Deprecated202101DeleteBlogsParamBlogIdArticlesParamArticleIdRequest",
    "Deprecated202101DeleteCarrierServicesParamCarrierServiceIdRequest",
    "Deprecated202101DeleteCollectionListingsParamCollectionListingIdRequest",
    "Deprecated202101DeleteCollectsParamCollectIdRequest",
    "Deprecated202101DeleteCountriesParamCountryIdRequest",
    "Deprecated202101DeleteCustomCollectionsParamCustomCollectionIdRequest",
    "Deprecated202101DeleteCustomerSavedSearchesParamCustomerSavedSearchIdRequest",
    "Deprecated202101DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202101DeleteCustomersParamCustomerIdRequest",
    "Deprecated202101DeleteInventoryLevelsRequest",
    "Deprecated202101DeleteOrdersParamOrderIdRisksParamRiskIdRequest",
    "Deprecated202101DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "Deprecated202101DeleteProductsParamProductIdImagesParamImageIdRequest",
    "Deprecated202101DeleteProductsParamProductIdRequest",
    "Deprecated202101DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest",
    "Deprecated202101DeleteRedirectsParamRedirectIdRequest",
    "Deprecated202101DeleteReportsParamReportIdRequest",
    "Deprecated202101DeleteSmartCollectionsParamSmartCollectionIdRequest",
    "Deprecated202101DeleteThemesParamThemeIdAssetsRequest",
    "Deprecated202101DeleteThemesParamThemeIdRequest",
    "Deprecated202101GetApplicationChargesParamApplicationChargeIdRequest",
    "Deprecated202101GetBlogsParamBlogIdArticlesCountRequest",
    "Deprecated202101GetBlogsParamBlogIdArticlesParamArticleIdRequest",
    "Deprecated202101GetBlogsParamBlogIdArticlesRequest",
    "Deprecated202101GetCheckoutsCountRequest",
    "Deprecated202101GetCheckoutsParamTokenShippingRatesRequest",
    "Deprecated202101GetCollectionListingsParamCollectionListingIdProductIdsRequest",
    "Deprecated202101GetCollectionsParamCollectionIdProductsRequest",
    "Deprecated202101GetCollectionsParamCollectionIdRequest",
    "Deprecated202101GetCollectsCountRequest",
    "Deprecated202101GetCollectsParamCollectIdRequest",
    "Deprecated202101GetCollectsRequest",
    "Deprecated202101GetCountriesParamCountryIdProvincesCountRequest",
    "Deprecated202101GetCountriesParamCountryIdProvincesRequest",
    "Deprecated202101GetCustomCollectionsCountRequest",
    "Deprecated202101GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequest",
    "Deprecated202101GetCustomerSavedSearchesParamCustomerSavedSearchIdRequest",
    "Deprecated202101GetCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202101GetCustomersParamCustomerIdAddressesRequest",
    "Deprecated202101GetCustomersParamCustomerIdOrdersRequest",
    "Deprecated202101GetCustomersParamCustomerIdRequest",
    "Deprecated202101GetCustomersRequest",
    "Deprecated202101GetCustomersSearchRequest",
    "Deprecated202101GetEventsParamEventIdRequest",
    "Deprecated202101GetEventsRequest",
    "Deprecated202101GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest",
    "Deprecated202101GetFulfillmentOrdersParamFulfillmentOrderIdRequest",
    "Deprecated202101GetGiftCardsCountRequest",
    "Deprecated202101GetGiftCardsRequest",
    "Deprecated202101GetGiftCardsSearchRequest",
    "Deprecated202101GetInventoryItemsRequest",
    "Deprecated202101GetInventoryLevelsRequest",
    "Deprecated202101GetLocationsParamLocationIdInventoryLevelsRequest",
    "Deprecated202101GetLocationsParamLocationIdRequest",
    "Deprecated202101GetOrdersParamOrderIdFulfillmentOrdersRequest",
    "Deprecated202101GetOrdersParamOrderIdFulfillmentsCountRequest",
    "Deprecated202101GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest",
    "Deprecated202101GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "Deprecated202101GetOrdersParamOrderIdFulfillmentsRequest",
    "Deprecated202101GetOrdersParamOrderIdRefundsParamRefundIdRequest",
    "Deprecated202101GetOrdersParamOrderIdRefundsRequest",
    "Deprecated202101GetOrdersParamOrderIdRisksParamRiskIdRequest",
    "Deprecated202101GetOrdersParamOrderIdRisksRequest",
    "Deprecated202101GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest",
    "Deprecated202101GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest",
    "Deprecated202101GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "Deprecated202101GetPriceRulesParamPriceRuleIdDiscountCodesRequest",
    "Deprecated202101GetProductsCountRequest",
    "Deprecated202101GetProductsParamProductIdImagesCountRequest",
    "Deprecated202101GetProductsParamProductIdImagesRequest",
    "Deprecated202101GetProductsParamProductIdRequest",
    "Deprecated202101GetProductsRequest",
    "Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequest",
    "Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest",
    "Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest",
    "Deprecated202101GetRedirectsCountRequest",
    "Deprecated202101GetRedirectsParamRedirectIdRequest",
    "Deprecated202101GetRedirectsRequest",
    "Deprecated202101GetReportsParamReportIdRequest",
    "Deprecated202101GetShopifyPaymentsPayoutsParamPayoutIdRequest",
    "Deprecated202101GetShopifyPaymentsPayoutsRequest",
    "Deprecated202101GetSmartCollectionsCountRequest",
    "Deprecated202101GetSmartCollectionsRequest",
    "Deprecated202101GetTenderTransactionsRequest",
    "Deprecated202101GetThemesParamThemeIdRequest",
    "Deprecated202101GetWebhooksCountRequest",
    "Deprecated202101GetWebhooksRequest",
    "Deprecated202101UpdateBlogsParamBlogIdArticlesParamArticleIdRequest",
    "Deprecated202101UpdateCarrierServicesParamCarrierServiceIdRequest",
    "Deprecated202101UpdateCustomCollectionsParamCustomCollectionIdRequest",
    "Deprecated202101UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest",
    "Deprecated202101UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "Deprecated202101UpdateCustomersParamCustomerIdAddressesSetRequest",
    "Deprecated202101UpdateCustomersParamCustomerIdRequest",
    "Deprecated202101UpdateGiftCardsParamGiftCardIdRequest",
    "Deprecated202101UpdateInventoryItemsParamInventoryItemIdRequest",
    "Deprecated202101UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "Deprecated202101UpdateOrdersParamOrderIdRisksParamRiskIdRequest",
    "Deprecated202101UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "Deprecated202101UpdateProductsParamProductIdImagesParamImageIdRequest",
    "Deprecated202101UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest",
    "Deprecated202101UpdateRedirectsParamRedirectIdRequest",
    "Deprecated202101UpdateReportsParamReportIdRequest",
    "DeprecatedUnstableCreateCustomersParamCustomerIdAccountActivationUrlRequest",
    "DeprecatedUnstableCreateCustomersParamCustomerIdSendInviteRequest",
    "DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest",
    "DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest",
    "DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest",
    "DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest",
    "DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest",
    "DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest",
    "DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest",
    "DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest",
    "DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdOpenRequest",
    "DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdRescheduleRequest",
    "DeprecatedUnstableCreateFulfillmentsParamFulfillmentIdCancelRequest",
    "DeprecatedUnstableCreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest",
    "DeprecatedUnstableCreateGiftCardsParamGiftCardIdDisableRequest",
    "DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequest",
    "DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest",
    "DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest",
    "DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequest",
    "DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsRequest",
    "DeprecatedUnstableCreateOrdersParamOrderIdRefundsCalculateRequest",
    "DeprecatedUnstableCreateOrdersParamOrderIdRefundsRequest",
    "DeprecatedUnstableCreateOrdersParamOrderIdRisksRequest",
    "DeprecatedUnstableCreatePriceRulesParamPriceRuleIdBatchRequest",
    "DeprecatedUnstableCreateProductsParamProductIdImagesRequest",
    "DeprecatedUnstableCreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest",
    "DeprecatedUnstableDeleteCollectsParamCollectIdRequest",
    "DeprecatedUnstableDeleteCustomCollectionsParamCustomCollectionIdRequest",
    "DeprecatedUnstableDeleteCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "DeprecatedUnstableDeleteCustomersParamCustomerIdRequest",
    "DeprecatedUnstableDeleteInventoryLevelsRequest",
    "DeprecatedUnstableDeleteOrdersParamOrderIdRisksParamRiskIdRequest",
    "DeprecatedUnstableDeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "DeprecatedUnstableDeleteProductsParamProductIdImagesParamImageIdRequest",
    "DeprecatedUnstableDeleteProductsParamProductIdRequest",
    "DeprecatedUnstableDeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest",
    "DeprecatedUnstableDeleteRedirectsParamRedirectIdRequest",
    "DeprecatedUnstableDeleteReportsParamReportIdRequest",
    "DeprecatedUnstableDeleteSmartCollectionsParamSmartCollectionIdRequest",
    "DeprecatedUnstableDeleteStorefrontAccessTokensParamStorefrontAccessTokenIdRequest",
    "DeprecatedUnstableDeleteThemesParamThemeIdAssetsRequest",
    "DeprecatedUnstableDeleteThemesParamThemeIdRequest",
    "DeprecatedUnstableDeleteWebhooksParamWebhookIdRequest",
    "DeprecatedUnstableGetApplicationChargesParamApplicationChargeIdRequest",
    "DeprecatedUnstableGetApplicationCreditsParamApplicationCreditIdRequest",
    "DeprecatedUnstableGetArticlesTagsRequest",
    "DeprecatedUnstableGetBlogsParamBlogIdArticlesCountRequest",
    "DeprecatedUnstableGetBlogsParamBlogIdArticlesRequest",
    "DeprecatedUnstableGetCheckoutsCountRequest",
    "DeprecatedUnstableGetCollectionsParamCollectionIdProductsRequest",
    "DeprecatedUnstableGetCollectionsParamCollectionIdRequest",
    "DeprecatedUnstableGetCollectsCountRequest",
    "DeprecatedUnstableGetCollectsParamCollectIdRequest",
    "DeprecatedUnstableGetCollectsRequest",
    "DeprecatedUnstableGetCustomCollectionsCountRequest",
    "DeprecatedUnstableGetCustomCollectionsParamCustomCollectionIdRequest",
    "DeprecatedUnstableGetCustomCollectionsRequest",
    "DeprecatedUnstableGetCustomersParamCustomerIdAddressesParamAddressIdRequest",
    "DeprecatedUnstableGetCustomersParamCustomerIdAddressesRequest",
    "DeprecatedUnstableGetCustomersParamCustomerIdOrdersRequest",
    "DeprecatedUnstableGetCustomersParamCustomerIdRequest",
    "DeprecatedUnstableGetCustomersRequest",
    "DeprecatedUnstableGetCustomersSearchRequest",
    "DeprecatedUnstableGetEventsRequest",
    "DeprecatedUnstableGetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest",
    "DeprecatedUnstableGetFulfillmentOrdersParamFulfillmentOrderIdRequest",
    "DeprecatedUnstableGetGiftCardsCountRequest",
    "DeprecatedUnstableGetGiftCardsParamGiftCardIdRequest",
    "DeprecatedUnstableGetInventoryItemsParamInventoryItemIdRequest",
    "DeprecatedUnstableGetInventoryItemsRequest",
    "DeprecatedUnstableGetInventoryLevelsRequest",
    "DeprecatedUnstableGetLocationsParamLocationIdInventoryLevelsRequest",
    "DeprecatedUnstableGetLocationsParamLocationIdRequest",
    "DeprecatedUnstableGetMetafieldsParamMetafieldIdRequest",
    "DeprecatedUnstableGetOrdersParamOrderIdFulfillmentOrdersRequest",
    "DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsCountRequest",
    "DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsRequest",
    "DeprecatedUnstableGetOrdersParamOrderIdRefundsParamRefundIdRequest",
    "DeprecatedUnstableGetOrdersParamOrderIdRefundsRequest",
    "DeprecatedUnstableGetOrdersParamOrderIdRisksParamRiskIdRequest",
    "DeprecatedUnstableGetOrdersParamOrderIdRisksRequest",
    "DeprecatedUnstableGetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest",
    "DeprecatedUnstableGetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest",
    "DeprecatedUnstableGetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "DeprecatedUnstableGetPriceRulesParamPriceRuleIdDiscountCodesRequest",
    "DeprecatedUnstableGetProductsParamProductIdImagesCountRequest",
    "DeprecatedUnstableGetProductsParamProductIdImagesRequest",
    "DeprecatedUnstableGetProductsParamProductIdRequest",
    "DeprecatedUnstableGetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest",
    "DeprecatedUnstableGetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest",
    "DeprecatedUnstableGetRedirectsCountRequest",
    "DeprecatedUnstableGetRedirectsParamRedirectIdRequest",
    "DeprecatedUnstableGetRedirectsRequest",
    "DeprecatedUnstableGetReportsRequest",
    "DeprecatedUnstableGetScriptTagsRequest",
    "DeprecatedUnstableGetShopifyPaymentsPayoutsParamPayoutIdRequest",
    "DeprecatedUnstableGetShopifyPaymentsPayoutsRequest",
    "DeprecatedUnstableGetSmartCollectionsCountRequest",
    "DeprecatedUnstableGetSmartCollectionsParamSmartCollectionIdRequest",
    "DeprecatedUnstableGetSmartCollectionsRequest",
    "DeprecatedUnstableGetTenderTransactionsRequest",
    "DeprecatedUnstableGetThemesParamThemeIdRequest",
    "DeprecatedUnstableGetUsersParamUserIdRequest",
    "DeprecatedUnstableGetUsersRequest",
    "DeprecatedUnstableGetWebhooksCountRequest",
    "DeprecatedUnstableGetWebhooksParamWebhookIdRequest",
    "DeprecatedUnstableUpdateBlogsParamBlogIdArticlesParamArticleIdRequest",
    "DeprecatedUnstableUpdateCarrierServicesParamCarrierServiceIdRequest",
    "DeprecatedUnstableUpdateCustomCollectionsParamCustomCollectionIdRequest",
    "DeprecatedUnstableUpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest",
    "DeprecatedUnstableUpdateCustomersParamCustomerIdAddressesSetRequest",
    "DeprecatedUnstableUpdateCustomersParamCustomerIdRequest",
    "DeprecatedUnstableUpdateGiftCardsParamGiftCardIdRequest",
    "DeprecatedUnstableUpdateMetafieldsParamMetafieldIdRequest",
    "DeprecatedUnstableUpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest",
    "DeprecatedUnstableUpdateOrdersParamOrderIdRisksParamRiskIdRequest",
    "DeprecatedUnstableUpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest",
    "DeprecatedUnstableUpdateProductsParamProductIdRequest",
    "DeprecatedUnstableUpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest",
    "DeprecatedUnstableUpdateRedirectsParamRedirectIdRequest",
    "DeprecatedUnstableUpdateSmartCollectionsParamSmartCollectionIdOrderRequest",
    "DeprecatedUnstableUpdateSmartCollectionsParamSmartCollectionIdRequest",
    "GetApplicationChargesParamApplicationChargeIdRequest",
    "GetApplicationCreditsParamApplicationCreditIdRequest",
    "GetArticlesTagsRequest",
    "GetAssignedFulfillmentOrdersRequest",
    "GetBlogsParamBlogIdArticlesCountRequest",
    "GetBlogsParamBlogIdArticlesParamArticleIdRequest",
    "GetBlogsParamBlogIdArticlesRequest",
    "GetCarrierServicesParamCarrierServiceIdRequest",
    "GetCheckoutsCountRequest",
    "GetCollectionListingsParamCollectionListingIdProductIdsRequest",
    "GetCollectionListingsParamCollectionListingIdRequest",
    "GetCollectionsParamCollectionIdProductsRequest",
    "GetCollectionsParamCollectionIdRequest",
    "GetCollectsCountRequest",
    "GetCollectsParamCollectIdRequest",
    "GetCollectsRequest",
    "GetCountriesParamCountryIdProvincesCountRequest",
    "GetCountriesParamCountryIdProvincesParamProvinceIdRequest",
    "GetCountriesParamCountryIdProvincesRequest",
    "GetCountriesParamCountryIdRequest",
    "GetCustomCollectionsCountRequest",
    "GetCustomCollectionsParamCustomCollectionIdRequest",
    "GetCustomCollectionsRequest",
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
    "GetRedirectsCountRequest",
    "GetRedirectsParamRedirectIdRequest",
    "GetRedirectsRequest",
    "GetReportsParamReportIdRequest",
    "GetReportsRequest",
    "GetScriptTagsParamScriptTagIdRequest",
    "GetScriptTagsRequest",
    "GetShopifyPaymentsPayoutsParamPayoutIdRequest",
    "GetShopifyPaymentsPayoutsRequest",
    "GetSmartCollectionsCountRequest",
    "GetSmartCollectionsParamSmartCollectionIdRequest",
    "GetSmartCollectionsRequest",
    "GetTenderTransactionsRequest",
    "GetThemesParamThemeIdAssetsRequest",
    "GetThemesParamThemeIdRequest",
    "GetUsersParamUserIdRequest",
    "GetWebhooksCountRequest",
    "GetWebhooksParamWebhookIdRequest",
    "GetWebhooksRequest",
    "UpdateBlogsParamBlogIdArticlesParamArticleIdRequest",
    "UpdateCarrierServicesParamCarrierServiceIdRequest",
    "UpdateCollectionListingsParamCollectionListingIdRequest",
    "UpdateCustomCollectionsParamCustomCollectionIdRequest",
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
    "UpdateReportsParamReportIdRequest",
    "UpdateScriptTagsParamScriptTagIdRequest",
    "UpdateSmartCollectionsParamSmartCollectionIdOrderRequest",
    "UpdateSmartCollectionsParamSmartCollectionIdRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_application_charge_202001
class Deprecated202001GetApplicationChargesParamApplicationChargeIdRequestPath(StrictModel):
    application_charge_id: str = Field(default=..., description="The unique identifier of the application charge to retrieve.")
class Deprecated202001GetApplicationChargesParamApplicationChargeIdRequest(StrictModel):
    """Retrieves the details of a specific application charge by its ID. Use this to fetch information about a charge created for your app."""
    path: Deprecated202001GetApplicationChargesParamApplicationChargeIdRequestPath

# Operation: list_assigned_fulfillment_orders_legacy
class Deprecated202001GetAssignedFulfillmentOrdersRequestQuery(StrictModel):
    assignment_status: Any | None = Field(default=None, description="Filter results by the fulfillment request status: use 'cancellation_requested' for orders where the merchant requested cancellation, 'fulfillment_requested' for pending fulfillment requests, or 'fulfillment_accepted' for approved requests ready for fulfillment creation.")
    location_ids: Any | None = Field(default=None, description="Restrict results to specific assigned locations by providing their location IDs as a comma-separated list or array. Omit to retrieve fulfillment orders from all assigned locations.")
class Deprecated202001GetAssignedFulfillmentOrdersRequest(StrictModel):
    """Retrieves fulfillment orders assigned to your app on the shop, optionally filtered by assignment status and location. Use this to monitor fulfillment requests, acceptances, and cancellations across your assigned locations."""
    query: Deprecated202001GetAssignedFulfillmentOrdersRequestQuery | None = None

# Operation: get_blog
class Deprecated202001GetBlogsParamBlogIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog to retrieve.")
class Deprecated202001GetBlogsParamBlogIdRequest(StrictModel):
    """Retrieve a single blog by its ID from the Shopify online store. Returns detailed information about the specified blog."""
    path: Deprecated202001GetBlogsParamBlogIdRequestPath

# Operation: delete_blog
class Deprecated202001DeleteBlogsParamBlogIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog to delete. This is a required string value that specifies which blog resource to remove.")
class Deprecated202001DeleteBlogsParamBlogIdRequest(StrictModel):
    """Permanently delete a blog from the online store. This action cannot be undone and will remove all associated blog posts and content."""
    path: Deprecated202001DeleteBlogsParamBlogIdRequestPath

# Operation: list_articles_for_blog
class Deprecated202001GetBlogsParamBlogIdArticlesRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog from which to retrieve articles.")
class Deprecated202001GetBlogsParamBlogIdArticlesRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of articles to return per request, between 1 and 250 (defaults to 50).")
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: 'published' for published articles only, 'unpublished' for unpublished articles only, or 'any' for all articles regardless of status (defaults to 'any').")
    handle: Any | None = Field(default=None, description="Retrieve a single article by its URL-friendly handle identifier.")
    tag: Any | None = Field(default=None, description="Filter articles to only those tagged with a specific tag.")
    author: Any | None = Field(default=None, description="Filter articles to only those authored by a specific author.")
class Deprecated202001GetBlogsParamBlogIdArticlesRequest(StrictModel):
    """Retrieves a paginated list of articles from a specific blog. Results are paginated using link headers in the response; use the provided links for navigation rather than the page parameter."""
    path: Deprecated202001GetBlogsParamBlogIdArticlesRequestPath
    query: Deprecated202001GetBlogsParamBlogIdArticlesRequestQuery | None = None

# Operation: get_article_count_for_blog_2020_01
class Deprecated202001GetBlogsParamBlogIdArticlesCountRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog for which to count articles.")
class Deprecated202001GetBlogsParamBlogIdArticlesCountRequestQuery(StrictModel):
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: use 'published' to count only published articles, 'unpublished' to count only unpublished articles, or 'any' to count all articles regardless of status. Defaults to 'any' if not specified.")
class Deprecated202001GetBlogsParamBlogIdArticlesCountRequest(StrictModel):
    """Retrieves the total count of articles in a specific blog, with optional filtering by publication status."""
    path: Deprecated202001GetBlogsParamBlogIdArticlesCountRequestPath
    query: Deprecated202001GetBlogsParamBlogIdArticlesCountRequestQuery | None = None

# Operation: get_article_202001
class Deprecated202001GetBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article.")
    article_id: str = Field(default=..., description="The unique identifier of the article to retrieve.")
class Deprecated202001GetBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Retrieves a single article from a blog by its ID. Use this to fetch detailed information about a specific article in the Shopify online store."""
    path: Deprecated202001GetBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: delete_article_202001
class Deprecated202001DeleteBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article to delete.")
    article_id: str = Field(default=..., description="The unique identifier of the article to delete.")
class Deprecated202001DeleteBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Permanently deletes an article from a blog. This action cannot be undone."""
    path: Deprecated202001DeleteBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: update_carrier_service_202001
class Deprecated202001UpdateCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to update.")
class Deprecated202001UpdateCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Updates an existing carrier service configuration. Only the application that originally created the carrier service can modify it."""
    path: Deprecated202001UpdateCarrierServicesParamCarrierServiceIdRequestPath

# Operation: delete_carrier_service_2020_01
class Deprecated202001DeleteCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to delete.")
class Deprecated202001DeleteCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Permanently deletes a carrier service from the store. This action cannot be undone and will remove the carrier service configuration."""
    path: Deprecated202001DeleteCarrierServicesParamCarrierServiceIdRequestPath

# Operation: get_abandoned_checkouts_count_202001
class Deprecated202001GetCheckoutsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count by checkout status. Use 'open' to count only active abandoned checkouts or 'closed' to count only completed/closed abandoned checkouts. Defaults to 'open' if not specified.")
class Deprecated202001GetCheckoutsCountRequest(StrictModel):
    """Retrieves the count of abandoned checkouts from the past 90 days, optionally filtered by checkout status."""
    query: Deprecated202001GetCheckoutsCountRequestQuery | None = None

# Operation: list_shipping_rates_for_checkout_2020_01
class Deprecated202001GetCheckoutsParamTokenShippingRatesRequestPath(StrictModel):
    token: str = Field(default=..., description="The unique identifier for the checkout. This token is used to retrieve shipping rates specific to that checkout.")
class Deprecated202001GetCheckoutsParamTokenShippingRatesRequest(StrictModel):
    """Retrieves available shipping rates for a checkout. Poll this endpoint until rates become available, then use the returned rates to display updated pricing (subtotal, tax, total) or apply a rate by updating the checkout's shipping line."""
    path: Deprecated202001GetCheckoutsParamTokenShippingRatesRequestPath

# Operation: delete_collection_listing_202001
class Deprecated202001DeleteCollectionListingsParamCollectionListingIdRequestPath(StrictModel):
    collection_listing_id: str = Field(default=..., description="The unique identifier of the collection listing to delete.")
class Deprecated202001DeleteCollectionListingsParamCollectionListingIdRequest(StrictModel):
    """Remove a collection listing to unpublish a collection from your sales channel or app."""
    path: Deprecated202001DeleteCollectionListingsParamCollectionListingIdRequestPath

# Operation: list_collection_product_ids_legacy
class Deprecated202001GetCollectionListingsParamCollectionListingIdProductIdsRequestPath(StrictModel):
    collection_listing_id: str = Field(default=..., description="The unique identifier of the collection listing whose published product IDs you want to retrieve.")
class Deprecated202001GetCollectionListingsParamCollectionListingIdProductIdsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of product IDs to return per request, ranging from 1 to 1000 (defaults to 50).")
class Deprecated202001GetCollectionListingsParamCollectionListingIdProductIdsRequest(StrictModel):
    """Retrieve the product IDs that are published to a specific collection. Results are paginated using link headers in the response."""
    path: Deprecated202001GetCollectionListingsParamCollectionListingIdProductIdsRequestPath
    query: Deprecated202001GetCollectionListingsParamCollectionListingIdProductIdsRequestQuery | None = None

# Operation: get_collection_202001
class Deprecated202001GetCollectionsParamCollectionIdRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection to retrieve.")
class Deprecated202001GetCollectionsParamCollectionIdRequest(StrictModel):
    """Retrieves the details of a single collection by its ID. Use this to fetch collection information such as name, description, and other metadata."""
    path: Deprecated202001GetCollectionsParamCollectionIdRequestPath

# Operation: list_collection_products_202001
class Deprecated202001GetCollectionsParamCollectionIdProductsRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection whose products you want to retrieve.")
class Deprecated202001GetCollectionsParamCollectionIdProductsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of products to return per request, ranging from 1 to 250 products (defaults to 50 if not specified).")
class Deprecated202001GetCollectionsParamCollectionIdProductsRequest(StrictModel):
    """Retrieve products belonging to a specific collection, sorted according to the collection's sort order. Results are paginated using link-based navigation provided in response headers."""
    path: Deprecated202001GetCollectionsParamCollectionIdProductsRequestPath
    query: Deprecated202001GetCollectionsParamCollectionIdProductsRequestQuery | None = None

# Operation: list_collects_2020_01
class Deprecated202001GetCollectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, ranging from 1 to 250 items. Defaults to 50 if not specified.")
class Deprecated202001GetCollectsRequest(StrictModel):
    """Retrieves a list of collects (product-to-collection associations). Uses cursor-based pagination via response header links; the page parameter is not supported."""
    query: Deprecated202001GetCollectsRequestQuery | None = None

# Operation: get_collects_count_202001
class Deprecated202001GetCollectsCountRequestQuery(StrictModel):
    collection_id: int | None = Field(default=None, description="Filter the count to only include collects belonging to a specific collection. If omitted, returns the total count of all collects across the store.")
class Deprecated202001GetCollectsCountRequest(StrictModel):
    """Retrieves the total count of collects, optionally filtered by a specific collection. Useful for understanding the size of a collection or the total number of product-to-collection associations in the store."""
    query: Deprecated202001GetCollectsCountRequestQuery | None = None

# Operation: get_collect_202001
class Deprecated202001GetCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect resource to retrieve.")
class Deprecated202001GetCollectsParamCollectIdRequest(StrictModel):
    """Retrieves a specific product collection by its ID from the Shopify store."""
    path: Deprecated202001GetCollectsParamCollectIdRequestPath

# Operation: remove_product_from_collection_2020_01
class Deprecated202001DeleteCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect relationship to remove. This ID represents the link between a product and a collection.")
class Deprecated202001DeleteCollectsParamCollectIdRequest(StrictModel):
    """Removes a product from a collection by deleting the collect relationship. This operation unlinks a product from a specific collection without affecting the product or collection itself."""
    path: Deprecated202001DeleteCollectsParamCollectIdRequestPath

# Operation: approve_comment
class Deprecated202001CreateCommentsParamCommentIdApproveRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to approve. This ID must correspond to an existing comment in the system.")
class Deprecated202001CreateCommentsParamCommentIdApproveRequest(StrictModel):
    """Approves a comment in the online store, making it visible to customers. This operation is used to moderate and publish pending comments."""
    path: Deprecated202001CreateCommentsParamCommentIdApproveRequestPath

# Operation: mark_comment_not_spam
class Deprecated202001CreateCommentsParamCommentIdNotSpamRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to mark as not spam.")
class Deprecated202001CreateCommentsParamCommentIdNotSpamRequest(StrictModel):
    """Marks a specific comment as not spam, removing any spam classification it may have had. This operation is used to correct false-positive spam flagging in the online store."""
    path: Deprecated202001CreateCommentsParamCommentIdNotSpamRequestPath

# Operation: restore_comment
class Deprecated202001CreateCommentsParamCommentIdRestoreRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to restore. This must be a valid comment ID that was previously removed.")
class Deprecated202001CreateCommentsParamCommentIdRestoreRequest(StrictModel):
    """Restores a previously removed comment in the online store. This operation reactivates a comment that was previously deleted or hidden."""
    path: Deprecated202001CreateCommentsParamCommentIdRestoreRequestPath

# Operation: mark_comment_as_spam
class Deprecated202001CreateCommentsParamCommentIdSpamRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to mark as spam.")
class Deprecated202001CreateCommentsParamCommentIdSpamRequest(StrictModel):
    """Marks a specific comment as spam in the online store. This action flags the comment for moderation and helps maintain comment quality."""
    path: Deprecated202001CreateCommentsParamCommentIdSpamRequestPath

# Operation: get_country_legacy
class Deprecated202001GetCountriesParamCountryIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier for the country to retrieve.")
class Deprecated202001GetCountriesParamCountryIdRequest(StrictModel):
    """Retrieves detailed information about a specific country, including its provinces and tax settings available in the Shopify store."""
    path: Deprecated202001GetCountriesParamCountryIdRequestPath

# Operation: delete_country_202001
class Deprecated202001DeleteCountriesParamCountryIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country to delete. This is a required string value that specifies which country record to remove.")
class Deprecated202001DeleteCountriesParamCountryIdRequest(StrictModel):
    """Permanently deletes a country from the store. This action cannot be undone and will remove the country from all applicable store configurations."""
    path: Deprecated202001DeleteCountriesParamCountryIdRequestPath

# Operation: list_provinces_for_country_202001
class Deprecated202001GetCountriesParamCountryIdProvincesRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve provinces. This ID must correspond to a valid country in the Shopify system.")
class Deprecated202001GetCountriesParamCountryIdProvincesRequest(StrictModel):
    """Retrieves a list of provinces or states for a specified country. Use this to populate province/state selectors in address forms or location-based workflows."""
    path: Deprecated202001GetCountriesParamCountryIdProvincesRequestPath

# Operation: get_province_count_for_country_202001
class Deprecated202001GetCountriesParamCountryIdProvincesCountRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve the province count.")
class Deprecated202001GetCountriesParamCountryIdProvincesCountRequest(StrictModel):
    """Retrieves the total count of provinces or states for a specified country. Useful for understanding administrative divisions within a country."""
    path: Deprecated202001GetCountriesParamCountryIdProvincesCountRequestPath

# Operation: count_custom_collections_2020_01
class Deprecated202001GetCustomCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter the count to include only custom collections with this exact title.")
    product_id: Any | None = Field(default=None, description="Filter the count to include only custom collections that contain this specific product.")
    published_status: Any | None = Field(default=None, description="Filter the count by publication status: 'published' for only published collections, 'unpublished' for only unpublished collections, or 'any' for all collections regardless of status. Defaults to 'any' if not specified.")
class Deprecated202001GetCustomCollectionsCountRequest(StrictModel):
    """Retrieves the total count of custom collections in the store, with optional filtering by title, product inclusion, or published status."""
    query: Deprecated202001GetCustomCollectionsCountRequestQuery | None = None

# Operation: list_customers_for_saved_search_2020_01
class Deprecated202001GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestPath(StrictModel):
    customer_saved_search_id: str = Field(default=..., description="The unique identifier of the customer saved search to retrieve customers for.")
class Deprecated202001GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="Specifies the field and direction to sort results by (e.g., 'last_order_date DESC'). Defaults to sorting by last order date in descending order.")
    limit: Any | None = Field(default=None, description="The maximum number of customer records to return per request. Defaults to 50 and cannot exceed 250.")
class Deprecated202001GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequest(StrictModel):
    """Retrieves all customers matching the criteria defined in a customer saved search. Results can be ordered and paginated."""
    path: Deprecated202001GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestPath
    query: Deprecated202001GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestQuery | None = None

# Operation: list_customers_202001
class Deprecated202001GetCustomersRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only include customers with the specified IDs. Provide as a comma-separated list of customer IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of customer records to return per request. Defaults to 50 and cannot exceed 250.")
class Deprecated202001GetCustomersRequest(StrictModel):
    """Retrieves a paginated list of customers from the store. Results are paginated using link headers in the response; use the provided links for navigation rather than the page parameter."""
    query: Deprecated202001GetCustomersRequestQuery | None = None

# Operation: get_customer_202001
class Deprecated202001GetCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to retrieve.")
class Deprecated202001GetCustomersParamCustomerIdRequest(StrictModel):
    """Retrieves a single customer by their unique identifier from the Shopify store."""
    path: Deprecated202001GetCustomersParamCustomerIdRequestPath

# Operation: update_customer_202001
class Deprecated202001UpdateCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to update. This ID is required to specify which customer record should be modified.")
class Deprecated202001UpdateCustomersParamCustomerIdRequest(StrictModel):
    """Updates an existing customer's information in Shopify. Modify customer details such as email, name, phone, and other profile attributes."""
    path: Deprecated202001UpdateCustomersParamCustomerIdRequestPath

# Operation: delete_customer_v202001
class Deprecated202001DeleteCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to delete.")
class Deprecated202001DeleteCustomersParamCustomerIdRequest(StrictModel):
    """Permanently deletes a customer from the store. Note that a customer cannot be deleted if they have any existing orders associated with their account."""
    path: Deprecated202001DeleteCustomersParamCustomerIdRequestPath

# Operation: generate_customer_account_activation_url_2020_01
class Deprecated202001CreateCustomersParamCustomerIdAccountActivationUrlRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer for whom to generate the account activation URL.")
class Deprecated202001CreateCustomersParamCustomerIdAccountActivationUrlRequest(StrictModel):
    """Generate a one-time account activation URL for a customer whose account is not yet enabled. The URL expires after 30 days; generating a new URL invalidates any previously generated URLs."""
    path: Deprecated202001CreateCustomersParamCustomerIdAccountActivationUrlRequestPath

# Operation: list_customer_addresses_202001
class Deprecated202001GetCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses you want to retrieve.")
class Deprecated202001GetCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Retrieves all addresses associated with a specific customer. Uses cursor-based pagination via response headers; the page parameter is not supported."""
    path: Deprecated202001GetCustomersParamCustomerIdAddressesRequestPath

# Operation: create_customer_address
class Deprecated202001CreateCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer for whom the address is being created.")
class Deprecated202001CreateCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Creates a new address for a customer. The address is added to the customer's address list and can be set as their default billing or shipping address."""
    path: Deprecated202001CreateCustomersParamCustomerIdAddressesRequestPath

# Operation: bulk_update_customer_addresses_202001
class Deprecated202001UpdateCustomersParamCustomerIdAddressesSetRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses will be modified.")
class Deprecated202001UpdateCustomersParamCustomerIdAddressesSetRequestQuery(StrictModel):
    address_ids: int | None = Field(default=None, validation_alias="address_ids[]", serialization_alias="address_ids[]", description="Array of address IDs to target for the bulk operation. The order may be significant depending on the operation type being performed.")
    operation: str | None = Field(default=None, description="The type of bulk operation to perform on the specified addresses (e.g., delete, set as default). Refer to API documentation for valid operation values.")
class Deprecated202001UpdateCustomersParamCustomerIdAddressesSetRequest(StrictModel):
    """Performs bulk operations on multiple customer addresses, allowing you to update, delete, or modify address records in a single request for a specific customer."""
    path: Deprecated202001UpdateCustomersParamCustomerIdAddressesSetRequestPath
    query: Deprecated202001UpdateCustomersParamCustomerIdAddressesSetRequestQuery | None = None

# Operation: get_customer_address_202001
class Deprecated202001GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who owns the address.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to retrieve.")
class Deprecated202001GetCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Retrieves the details of a specific customer address by customer ID and address ID."""
    path: Deprecated202001GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: update_customer_address_2020_01
class Deprecated202001UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being updated.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to update for the customer.")
class Deprecated202001UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Updates an existing customer address by customer ID and address ID. Use this to modify address details such as street, city, postal code, or other address information for a specific customer."""
    path: Deprecated202001UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: delete_customer_address_202001
class Deprecated202001DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being removed.")
    address_id: str = Field(default=..., description="The unique identifier of the address to be deleted from the customer's address list.")
class Deprecated202001DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Removes a specific address from a customer's address list. This operation permanently deletes the address record associated with the given customer."""
    path: Deprecated202001DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: set_customer_default_address_202001
class Deprecated202001UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose default address will be updated.")
    address_id: str = Field(default=..., description="The unique identifier of the address to set as the customer's default address.")
class Deprecated202001UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest(StrictModel):
    """Sets a specific address as the default address for a customer. This operation updates the customer's default address preference in their address book."""
    path: Deprecated202001UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath

# Operation: list_customer_orders_202001
class Deprecated202001GetCustomersParamCustomerIdOrdersRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose orders should be retrieved.")
class Deprecated202001GetCustomersParamCustomerIdOrdersRequest(StrictModel):
    """Retrieves all orders for a specific customer. Supports filtering and sorting through standard Order resource query parameters."""
    path: Deprecated202001GetCustomersParamCustomerIdOrdersRequestPath

# Operation: send_customer_invite_202001
class Deprecated202001CreateCustomersParamCustomerIdSendInviteRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who will receive the account invite.")
class Deprecated202001CreateCustomersParamCustomerIdSendInviteRequest(StrictModel):
    """Sends an account invitation email to a customer, allowing them to create or access their account on the store."""
    path: Deprecated202001CreateCustomersParamCustomerIdSendInviteRequestPath

# Operation: list_events_202001
class Deprecated202001GetEventsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of events to return per request, between 1 and 250 (defaults to 50).")
    filter_: Any | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter events by specific criteria to narrow results to matching events.")
    verb: Any | None = Field(default=None, description="Filter events by type or action verb to show only events of a certain category.")
class Deprecated202001GetEventsRequest(StrictModel):
    """Retrieves a paginated list of events from the store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: Deprecated202001GetEventsRequestQuery | None = None

# Operation: get_event_2020_01
class Deprecated202001GetEventsParamEventIdRequestPath(StrictModel):
    event_id: str = Field(default=..., description="The unique identifier of the event to retrieve.")
class Deprecated202001GetEventsParamEventIdRequest(StrictModel):
    """Retrieves a single event by its ID from the Shopify admin. Use this to fetch detailed information about a specific event that occurred in your store."""
    path: Deprecated202001GetEventsParamEventIdRequestPath

# Operation: get_fulfillment_order_202001
class Deprecated202001GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to retrieve.")
class Deprecated202001GetFulfillmentOrdersParamFulfillmentOrderIdRequest(StrictModel):
    """Retrieves the details of a specific fulfillment order by its ID. Use this to fetch current status, line items, and fulfillment information for a particular order."""
    path: Deprecated202001GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath

# Operation: cancel_fulfillment_order_2020_01
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest(StrictModel):
    """Cancels a fulfillment order, marking it as no longer needed for processing. This operation is useful when a fulfillment order must be abandoned before it's been fulfilled."""
    path: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath

# Operation: send_fulfillment_order_cancellation_request_2020_01
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel. This ID references a specific fulfillment order in the system.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for the cancellation request. This provides context to the fulfillment service about why the order is being cancelled.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest(StrictModel):
    """Sends a cancellation request to the fulfillment service for a specific fulfillment order. This notifies the fulfillment provider that the order should be cancelled if not yet fulfilled."""
    path: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath
    query: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery | None = None

# Operation: accept_fulfillment_order_cancellation_request_2020_01
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to accept the cancellation request.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for accepting the cancellation request.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest(StrictModel):
    """Accepts a cancellation request for a fulfillment order, confirming that the fulfillment service should cancel the specified order. Optionally include a reason message for the acceptance."""
    path: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath
    query: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_order_cancellation_request_2020_01
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which you are rejecting the cancellation request.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining why the cancellation request is being rejected. This reason may be communicated to the fulfillment service.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest(StrictModel):
    """Rejects a cancellation request that was sent to a fulfillment service for a specific fulfillment order. Use this to deny a cancellation and keep the fulfillment order active."""
    path: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath
    query: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery | None = None

# Operation: close_fulfillment_order_2020_01
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to close.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional reason or note explaining why the fulfillment order is being marked as incomplete.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest(StrictModel):
    """Marks an in-progress fulfillment order as incomplete, indicating the fulfillment service cannot ship remaining items and is closing the order."""
    path: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath
    query: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery | None = None

# Operation: send_fulfillment_request_202001
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to request fulfillment for.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message to include with the fulfillment request, such as special instructions or notes for the fulfillment service.")
    fulfillment_order_line_items: Any | None = Field(default=None, description="An optional array of fulfillment order line items to request for fulfillment. If omitted, all line items in the fulfillment order will be requested.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest(StrictModel):
    """Sends a fulfillment request to the fulfillment service for a specific fulfillment order, optionally specifying which line items to fulfill and including an optional message."""
    path: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath
    query: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery | None = None

# Operation: accept_fulfillment_request_2020_01
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request is being accepted.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for accepting the fulfillment request.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest(StrictModel):
    """Accepts a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, optionally providing a reason for acceptance."""
    path: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath
    query: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_request_202001
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request should be rejected.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for rejecting the fulfillment request.")
class Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest(StrictModel):
    """Rejects a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, optionally providing a reason for the rejection."""
    path: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath
    query: Deprecated202001CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery | None = None

# Operation: list_locations_for_fulfillment_order_move_2020_01
class Deprecated202001GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to retrieve available move destinations.")
class Deprecated202001GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest(StrictModel):
    """Retrieves an alphabetically sorted list of locations where a fulfillment order can be moved. Use this to determine valid destination locations before initiating a fulfillment order transfer."""
    path: Deprecated202001GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath

# Operation: delete_fulfillment_service_202001
class Deprecated202001DeleteFulfillmentServicesParamFulfillmentServiceIdRequestPath(StrictModel):
    fulfillment_service_id: str = Field(default=..., description="The unique identifier of the fulfillment service to delete. This ID is required to specify which fulfillment service should be removed.")
class Deprecated202001DeleteFulfillmentServicesParamFulfillmentServiceIdRequest(StrictModel):
    """Permanently delete a fulfillment service from your Shopify store. This operation removes the fulfillment service and its associated configuration."""
    path: Deprecated202001DeleteFulfillmentServicesParamFulfillmentServiceIdRequestPath

# Operation: cancel_fulfillment_202001
class Deprecated202001CreateFulfillmentsParamFulfillmentIdCancelRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to cancel. This ID references a specific fulfillment order that has been previously created.")
class Deprecated202001CreateFulfillmentsParamFulfillmentIdCancelRequest(StrictModel):
    """Cancels an existing fulfillment order. This operation marks the specified fulfillment as cancelled and updates its status accordingly."""
    path: Deprecated202001CreateFulfillmentsParamFulfillmentIdCancelRequestPath

# Operation: update_fulfillment_tracking_2020_01
class Deprecated202001CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment whose tracking information should be updated.")
class Deprecated202001CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest(StrictModel):
    """Updates the tracking information for a fulfillment, allowing you to modify shipment tracking details after the fulfillment has been created."""
    path: Deprecated202001CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath

# Operation: list_gift_cards_2020_01
class Deprecated202001GetGiftCardsRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter results to gift cards with a specific status: enabled to show only active gift cards, or disabled to show only inactive gift cards.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, ranging from 1 to 250 (defaults to 50).")
class Deprecated202001GetGiftCardsRequest(StrictModel):
    """Retrieves a paginated list of gift cards, optionally filtered by status. Results are paginated using link headers in the response; the page parameter is not supported."""
    query: Deprecated202001GetGiftCardsRequestQuery | None = None

# Operation: count_gift_cards
class Deprecated202001GetGiftCardsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count to only include gift cards with a specific status: enabled for active gift cards, or disabled for inactive gift cards. Omit to count all gift cards regardless of status.")
class Deprecated202001GetGiftCardsCountRequest(StrictModel):
    """Retrieves the total count of gift cards, optionally filtered by their enabled or disabled status."""
    query: Deprecated202001GetGiftCardsCountRequestQuery | None = None

# Operation: search_gift_cards_202001
class Deprecated202001GetGiftCardsSearchRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="The field and direction to sort results by. Defaults to most recently disabled gift cards first. Common sortable fields include created_at, updated_at, disabled_at, balance, initial_value, amount_spent, email, and last_characters.")
    query: Any | None = Field(default=None, description="The search query text to match against indexed gift card fields such as email, balance, initial value, amount spent, and last characters.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 results.")
class Deprecated202001GetGiftCardsSearchRequest(StrictModel):
    """Search for gift cards using indexed fields like balance, email, creation date, and more. Results are paginated using link-based navigation provided in response headers."""
    query: Deprecated202001GetGiftCardsSearchRequestQuery | None = None

# Operation: update_gift_card_202001
class Deprecated202001UpdateGiftCardsParamGiftCardIdRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to update.")
class Deprecated202001UpdateGiftCardsParamGiftCardIdRequest(StrictModel):
    """Update an existing gift card's expiry date, note, or template suffix. Note that the gift card's balance cannot be modified through the API."""
    path: Deprecated202001UpdateGiftCardsParamGiftCardIdRequestPath

# Operation: disable_gift_card_202001
class Deprecated202001CreateGiftCardsParamGiftCardIdDisableRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to disable.")
class Deprecated202001CreateGiftCardsParamGiftCardIdDisableRequest(StrictModel):
    """Permanently disables a gift card, preventing it from being used for future transactions. This action cannot be reversed."""
    path: Deprecated202001CreateGiftCardsParamGiftCardIdDisableRequestPath

# Operation: list_inventory_items_202001
class Deprecated202001GetInventoryItemsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of inventory items to return per request, between 1 and 250 items (defaults to 50).")
    ids: int | None = Field(default=None, description="Filter results to only inventory items with the specified IDs. Provide as a comma-separated list of integers.")
class Deprecated202001GetInventoryItemsRequest(StrictModel):
    """Retrieves a paginated list of inventory items. Uses cursor-based pagination via response header links; the page parameter is not supported."""
    query: Deprecated202001GetInventoryItemsRequestQuery | None = None

# Operation: update_inventory_item_legacy_202001
class Deprecated202001UpdateInventoryItemsParamInventoryItemIdRequestPath(StrictModel):
    inventory_item_id: str = Field(default=..., description="The unique identifier of the inventory item to update. This ID is required to specify which inventory item should be modified.")
class Deprecated202001UpdateInventoryItemsParamInventoryItemIdRequest(StrictModel):
    """Updates an existing inventory item in your Shopify store. Use this to modify inventory item properties such as tracked status, cost, and other attributes."""
    path: Deprecated202001UpdateInventoryItemsParamInventoryItemIdRequestPath

# Operation: list_inventory_levels_202001
class Deprecated202001GetInventoryLevelsRequestQuery(StrictModel):
    inventory_item_ids: Any | None = Field(default=None, description="Comma-separated list of inventory item IDs to filter results. Maximum of 50 IDs per request.")
    location_ids: Any | None = Field(default=None, description="Comma-separated list of location IDs to filter results. Maximum of 50 IDs per request. Use the Location resource to find location IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
class Deprecated202001GetInventoryLevelsRequest(StrictModel):
    """Retrieves inventory levels across your store's locations. You must filter by at least one inventory item ID or location ID to retrieve results."""
    query: Deprecated202001GetInventoryLevelsRequestQuery | None = None

# Operation: delete_inventory_level_202001
class Deprecated202001DeleteInventoryLevelsRequestQuery(StrictModel):
    inventory_item_id: int | None = Field(default=None, description="The unique identifier of the inventory item whose level should be deleted.")
    location_id: int | None = Field(default=None, description="The unique identifier of the location from which the inventory item should be removed.")
class Deprecated202001DeleteInventoryLevelsRequest(StrictModel):
    """Removes an inventory level for a specific inventory item at a location. This operation disconnects the inventory item from that location; note that every inventory item must maintain at least one inventory level, so you must connect the item to another location before deleting its last level."""
    query: Deprecated202001DeleteInventoryLevelsRequestQuery | None = None

# Operation: get_location_202001
class Deprecated202001GetLocationsParamLocationIdRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location to retrieve.")
class Deprecated202001GetLocationsParamLocationIdRequest(StrictModel):
    """Retrieves a single location by its ID from the Shopify inventory system. Use this to fetch detailed information about a specific store location."""
    path: Deprecated202001GetLocationsParamLocationIdRequestPath

# Operation: list_inventory_levels_for_location_202001
class Deprecated202001GetLocationsParamLocationIdInventoryLevelsRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location for which to retrieve inventory levels.")
class Deprecated202001GetLocationsParamLocationIdInventoryLevelsRequest(StrictModel):
    """Retrieves all inventory levels for a specific location. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""
    path: Deprecated202001GetLocationsParamLocationIdInventoryLevelsRequestPath

# Operation: update_metafield_legacy
class Deprecated202001UpdateMetafieldsParamMetafieldIdRequestPath(StrictModel):
    metafield_id: str = Field(default=..., description="The unique identifier of the metafield to update. This ID is returned when a metafield is created and is required to target the specific metafield for modification.")
class Deprecated202001UpdateMetafieldsParamMetafieldIdRequest(StrictModel):
    """Updates an existing metafield by its ID. Use this to modify metafield properties such as namespace, key, value, and value type."""
    path: Deprecated202001UpdateMetafieldsParamMetafieldIdRequestPath

# Operation: list_orders
class Deprecated202001GetOrdersRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only orders with the specified IDs. Provide as a comma-separated list of order IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of orders to return per page. Defaults to 50; maximum allowed is 250.")
    processed_at_min: Any | None = Field(default=None, description="Show only orders processed at or after this date. Use ISO 8601 format with timezone offset.")
    processed_at_max: Any | None = Field(default=None, description="Show only orders processed at or before this date. Use ISO 8601 format with timezone offset.")
    attribution_app_id: Any | None = Field(default=None, description="Filter orders by the app that created them. Use the app's ID, or set to 'current' to show orders created by the app making this request.")
    status: Any | None = Field(default=None, description="Filter orders by fulfillment status: open (default), closed, cancelled, or any (including archived orders).")
    financial_status: Any | None = Field(default=None, description="Filter orders by payment status: authorized, pending, paid, partially_paid, refunded, voided, partially_refunded, unpaid, or any (default).")
    fulfillment_status: Any | None = Field(default=None, description="Filter orders by shipment status: shipped (fulfilled), partial (partially shipped), unshipped (not yet shipped), unfulfilled (unshipped or partial), or any (default).")
class Deprecated202001GetOrdersRequest(StrictModel):
    """Retrieves a paginated list of orders from the store. Results are paginated using link headers in the response; use the provided links for navigation rather than the page parameter."""
    query: Deprecated202001GetOrdersRequestQuery | None = None

# Operation: get_orders_count
class Deprecated202001GetOrdersCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter orders by their fulfillment state. Defaults to 'open' if not specified. Valid values are 'open' (unfulfilled orders), 'closed' (completed orders), or 'any' (all orders regardless of state).")
    financial_status: Any | None = Field(default=None, description="Filter orders by their payment state. Defaults to 'any' if not specified. Valid values are 'authorized', 'pending', 'paid', 'refunded', 'voided', or 'any' (all payment states).")
    fulfillment_status: Any | None = Field(default=None, description="Filter orders by their shipping state. Defaults to 'any' if not specified. Valid values are 'shipped' (fully fulfilled), 'partial' (partially shipped), 'unshipped' (not yet shipped), 'unfulfilled' (not shipped or partially shipped), or 'any' (all shipping states).")
class Deprecated202001GetOrdersCountRequest(StrictModel):
    """Retrieves the count of orders filtered by status, financial status, and fulfillment status. Useful for obtaining order statistics without fetching full order details."""
    query: Deprecated202001GetOrdersCountRequestQuery | None = None

# Operation: get_order_legacy
class Deprecated202001GetOrdersParamOrderIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to retrieve.")
class Deprecated202001GetOrdersParamOrderIdRequest(StrictModel):
    """Retrieves the details of a specific order by its ID. Use this to fetch complete order information including items, customer details, and fulfillment status."""
    path: Deprecated202001GetOrdersParamOrderIdRequestPath

# Operation: update_order
class Deprecated202001UpdateOrdersParamOrderIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to update. This is a required string value that specifies which order will be modified.")
class Deprecated202001UpdateOrdersParamOrderIdRequest(StrictModel):
    """Updates an existing order in Shopify. Use this operation to modify order details such as status, customer information, or other order attributes."""
    path: Deprecated202001UpdateOrdersParamOrderIdRequestPath

# Operation: delete_order
class Deprecated202001DeleteOrdersParamOrderIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to delete. This is a required string value that identifies which order should be removed.")
class Deprecated202001DeleteOrdersParamOrderIdRequest(StrictModel):
    """Permanently deletes an order from the store. Note that orders connected to online payment gateways cannot be deleted due to payment processing requirements."""
    path: Deprecated202001DeleteOrdersParamOrderIdRequestPath

# Operation: cancel_order
class Deprecated202001CreateOrdersParamOrderIdCancelRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to cancel.")
class Deprecated202001CreateOrdersParamOrderIdCancelRequestQuery(StrictModel):
    amount: Any | None = Field(default=None, description="The monetary amount to refund. When provided, Shopify attempts to void or refund the payment based on its current status. For multi-currency orders, the currency parameter is required when this is set.")
    currency: Any | None = Field(default=None, description="The currency code for the refund amount in multi-currency orders. Required whenever the amount parameter is provided for orders with multiple currencies.")
    reason: Any | None = Field(default=None, description="The reason for cancellation. Valid options are: customer, inventory, fraud, declined, or other. Defaults to other if not specified.")
    email: Any | None = Field(default=None, description="Whether to send a cancellation notification email to the customer. Defaults to false if not specified.")
    refund: Any | None = Field(default=None, description="Refund transaction details for complex refund scenarios. Use this for advanced refund operations beyond simple amount-based refunds. See the Refund API documentation for structure details.")
class Deprecated202001CreateOrdersParamOrderIdCancelRequest(StrictModel):
    """Cancels an order and optionally processes a refund. Orders with fulfillment objects cannot be canceled. For multi-currency orders, the currency property is required whenever an amount is specified."""
    path: Deprecated202001CreateOrdersParamOrderIdCancelRequestPath
    query: Deprecated202001CreateOrdersParamOrderIdCancelRequestQuery | None = None

# Operation: close_order
class Deprecated202001CreateOrdersParamOrderIdCloseRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to close. This is the Shopify order ID.")
class Deprecated202001CreateOrdersParamOrderIdCloseRequest(StrictModel):
    """Closes an order, preventing further modifications. This operation marks the order as closed in the system."""
    path: Deprecated202001CreateOrdersParamOrderIdCloseRequestPath

# Operation: list_fulfillment_orders_for_order_2020_01
class Deprecated202001GetOrdersParamOrderIdFulfillmentOrdersRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve fulfillment orders.")
class Deprecated202001GetOrdersParamOrderIdFulfillmentOrdersRequest(StrictModel):
    """Retrieves all fulfillment orders associated with a specific order. Fulfillment orders represent the items in an order that need to be fulfilled."""
    path: Deprecated202001GetOrdersParamOrderIdFulfillmentOrdersRequestPath

# Operation: list_fulfillments_for_order
class Deprecated202001GetOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order whose fulfillments you want to retrieve.")
class Deprecated202001GetOrdersParamOrderIdFulfillmentsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of fulfillments to return per request, between 1 and 250 (defaults to 50).")
class Deprecated202001GetOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Retrieves all fulfillments associated with a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the limit parameter."""
    path: Deprecated202001GetOrdersParamOrderIdFulfillmentsRequestPath
    query: Deprecated202001GetOrdersParamOrderIdFulfillmentsRequestQuery | None = None

# Operation: create_fulfillment_for_order_legacy_202001
class Deprecated202001CreateOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the fulfillment.")
class Deprecated202001CreateOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Create a fulfillment for specified line items in an order. The fulfillment status depends on the fulfillment service type: manual/custom services set status immediately, while external services queue the fulfillment with pending status until processed."""
    path: Deprecated202001CreateOrdersParamOrderIdFulfillmentsRequestPath

# Operation: get_fulfillment_count_for_order
class Deprecated202001GetOrdersParamOrderIdFulfillmentsCountRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve the fulfillment count.")
class Deprecated202001GetOrdersParamOrderIdFulfillmentsCountRequest(StrictModel):
    """Retrieves the total count of fulfillments associated with a specific order. Useful for understanding fulfillment status and logistics tracking without fetching full fulfillment details."""
    path: Deprecated202001GetOrdersParamOrderIdFulfillmentsCountRequestPath

# Operation: get_fulfillment_202001
class Deprecated202001GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to retrieve.")
class Deprecated202001GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Retrieve detailed information about a specific fulfillment for an order. Use this to access fulfillment status, tracking information, and line item details."""
    path: Deprecated202001GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: update_fulfillment_202001
class Deprecated202001UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to update.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to update.")
class Deprecated202001UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Update fulfillment details for a specific order, such as tracking information or fulfillment status."""
    path: Deprecated202001UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: complete_fulfillment_2020_01
class Deprecated202001CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to be completed.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to mark as complete.")
class Deprecated202001CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest(StrictModel):
    """Mark a fulfillment as complete, indicating that all items in the fulfillment have been shipped and the order fulfillment process is finished."""
    path: Deprecated202001CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath

# Operation: list_fulfillment_events_202001
class Deprecated202001GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment within the specified order.")
class Deprecated202001GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest(StrictModel):
    """Retrieves all events associated with a specific fulfillment for an order. Events track status changes and milestones throughout the fulfillment lifecycle."""
    path: Deprecated202001GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath

# Operation: reopen_order
class Deprecated202001CreateOrdersParamOrderIdOpenRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to re-open. This must be a valid order ID from your Shopify store.")
class Deprecated202001CreateOrdersParamOrderIdOpenRequest(StrictModel):
    """Re-opens a previously closed order, allowing it to be modified and processed again. This operation restores a closed order to an active state."""
    path: Deprecated202001CreateOrdersParamOrderIdOpenRequestPath

# Operation: list_order_refunds_202001
class Deprecated202001GetOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve refunds.")
class Deprecated202001GetOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of refunds to return per request, between 1 and 250 (defaults to 50).")
    in_shop_currency: Any | None = Field(default=None, description="When true, displays refund amounts in the shop's currency for the underlying transaction; defaults to false.")
class Deprecated202001GetOrdersParamOrderIdRefundsRequest(StrictModel):
    """Retrieves a list of refunds for a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    path: Deprecated202001GetOrdersParamOrderIdRefundsRequestPath
    query: Deprecated202001GetOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: create_order_refund_202001
class Deprecated202001CreateOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create a refund.")
class Deprecated202001CreateOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    notify: Any | None = Field(default=None, description="Whether to send a refund notification email to the customer.")
    note: Any | None = Field(default=None, description="An optional note to attach to the refund for internal reference.")
    discrepancy_reason: Any | None = Field(default=None, description="An optional reason explaining any discrepancy between calculated and actual refund amounts. Valid values are: restock, damage, customer, or other.")
    shipping: Any | None = Field(default=None, description="Specifies shipping refund details. Use full_refund to refund all remaining shipping, or provide a specific amount to refund (which takes precedence over full_refund).")
    refund_line_items: Any | None = Field(default=None, description="A list of line items to refund, each specifying the line item ID, quantity to refund, restock type (no_restock, cancel, or return), and location ID for restocking (required for cancel and return types).")
    transactions: Any | None = Field(default=None, description="A list of transactions to process as refunds. Should be calculated using the calculate endpoint before submission.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required for multi-currency orders when an amount property is provided.")
class Deprecated202001CreateOrdersParamOrderIdRefundsRequest(StrictModel):
    """Creates a refund for an order. Use the calculate endpoint first to determine the correct transactions to submit. For multi-currency orders, the currency property is required whenever an amount is specified."""
    path: Deprecated202001CreateOrdersParamOrderIdRefundsRequestPath
    query: Deprecated202001CreateOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: calculate_order_refund_2020_01
class Deprecated202001CreateOrdersParamOrderIdRefundsCalculateRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to calculate the refund.")
class Deprecated202001CreateOrdersParamOrderIdRefundsCalculateRequestQuery(StrictModel):
    shipping: Any | None = Field(default=None, description="Shipping refund configuration. Specify either full_refund to refund all remaining shipping, or amount to refund a specific shipping cost. The amount property takes precedence over full_refund.")
    refund_line_items: Any | None = Field(default=None, description="List of line items to refund, each specifying the line item ID, quantity to refund, restock instructions (no_restock, cancel, or return), and optionally the location ID where items should be restocked. If location_id is omitted for return or cancel restocks, the endpoint will suggest an appropriate location.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required whenever a shipping amount is specified, particularly important for multi-currency orders.")
class Deprecated202001CreateOrdersParamOrderIdRefundsCalculateRequest(StrictModel):
    """Calculate refund transactions for an order based on line items and shipping costs. Use this endpoint to generate accurate refund details before creating an actual refund, including any necessary adjustments to restock instructions."""
    path: Deprecated202001CreateOrdersParamOrderIdRefundsCalculateRequestPath
    query: Deprecated202001CreateOrdersParamOrderIdRefundsCalculateRequestQuery | None = None

# Operation: get_refund_for_order
class Deprecated202001GetOrdersParamOrderIdRefundsParamRefundIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the refund.")
    refund_id: str = Field(default=..., description="The unique identifier of the refund to retrieve.")
class Deprecated202001GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery(StrictModel):
    in_shop_currency: Any | None = Field(default=None, description="When enabled, displays all monetary amounts in the shop's native currency rather than the transaction currency. Defaults to false.")
class Deprecated202001GetOrdersParamOrderIdRefundsParamRefundIdRequest(StrictModel):
    """Retrieves details for a specific refund associated with an order. Use this to view refund information including amounts, line items, and status."""
    path: Deprecated202001GetOrdersParamOrderIdRefundsParamRefundIdRequestPath
    query: Deprecated202001GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery | None = None

# Operation: list_order_risks_2020_01
class Deprecated202001GetOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve risk assessments.")
class Deprecated202001GetOrdersParamOrderIdRisksRequest(StrictModel):
    """Retrieves all fraud and risk assessments associated with a specific order. Results are paginated using link headers in the response."""
    path: Deprecated202001GetOrdersParamOrderIdRisksRequestPath

# Operation: create_order_risk_202001
class Deprecated202001CreateOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the risk record.")
class Deprecated202001CreateOrdersParamOrderIdRisksRequest(StrictModel):
    """Creates a risk assessment record for a specific order. Use this to flag potential issues or concerns associated with an order that may require review or action."""
    path: Deprecated202001CreateOrdersParamOrderIdRisksRequestPath

# Operation: get_order_risk_202001
class Deprecated202001GetOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk assessment.")
    risk_id: str = Field(default=..., description="The unique identifier of the specific risk assessment to retrieve.")
class Deprecated202001GetOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Retrieves a single risk assessment associated with a specific order. Use this to view fraud or security risk details that Shopify has flagged for an order."""
    path: Deprecated202001GetOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: update_order_risk_202001
class Deprecated202001UpdateOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to be updated.")
    risk_id: str = Field(default=..., description="The unique identifier of the order risk to be updated.")
class Deprecated202001UpdateOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Updates an existing order risk for a specific order. Note that you cannot modify an order risk that was created by another application."""
    path: Deprecated202001UpdateOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: delete_order_risk_202001
class Deprecated202001DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to be deleted.")
    risk_id: str = Field(default=..., description="The unique identifier of the risk assessment to be deleted from the order.")
class Deprecated202001DeleteOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Removes a specific risk assessment from an order. Note that you can only delete risks created by your application; risks created by other applications cannot be deleted."""
    path: Deprecated202001DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: create_discount_codes_batch_202001
class Deprecated202001CreatePriceRulesParamPriceRuleIdBatchRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which discount codes will be created.")
class Deprecated202001CreatePriceRulesParamPriceRuleIdBatchRequest(StrictModel):
    """Asynchronously creates up to 100 discount codes for a price rule in a single batch job. Returns a discount code creation job object that can be monitored for completion status, including counts of successful and failed code creations."""
    path: Deprecated202001CreatePriceRulesParamPriceRuleIdBatchRequestPath

# Operation: get_discount_code_batch_202001
class Deprecated202001GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch.")
    batch_id: str = Field(default=..., description="The unique identifier of the batch job to retrieve status and results for.")
class Deprecated202001GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest(StrictModel):
    """Retrieves the status and details of a discount code creation job batch for a specific price rule. Use this to check the progress and results of bulk discount code generation."""
    path: Deprecated202001GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath

# Operation: list_discount_codes_for_batch_202001
class Deprecated202001GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch.")
    batch_id: str = Field(default=..., description="The unique identifier of the batch job that generated the discount codes.")
class Deprecated202001GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest(StrictModel):
    """Retrieves all discount codes generated from a batch creation job for a specific price rule. Results include successfully created codes with populated IDs and codes that failed with error details."""
    path: Deprecated202001GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath

# Operation: list_discount_codes_for_price_rule_2020_01
class Deprecated202001GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which to retrieve associated discount codes.")
class Deprecated202001GetPriceRulesParamPriceRuleIdDiscountCodesRequest(StrictModel):
    """Retrieve all discount codes associated with a specific price rule. Results are paginated using link-based navigation provided in response headers."""
    path: Deprecated202001GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath

# Operation: get_discount_code_for_price_rule
class Deprecated202001GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to retrieve.")
class Deprecated202001GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Retrieves a specific discount code associated with a price rule. Use this to fetch details about an individual discount code within a price rule configuration."""
    path: Deprecated202001GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: update_discount_code_202001
class Deprecated202001UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code being updated.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to update.")
class Deprecated202001UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Updates an existing discount code associated with a price rule. Modify discount code properties such as code value, usage limits, and other settings."""
    path: Deprecated202001UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: delete_discount_code_202001
class Deprecated202001DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code to be deleted.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to be deleted.")
class Deprecated202001DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Permanently deletes a specific discount code associated with a price rule. This action cannot be undone."""
    path: Deprecated202001DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: update_product_listing
class Deprecated202001UpdateProductListingsParamProductListingIdRequestPath(StrictModel):
    product_listing_id: str = Field(default=..., description="The unique identifier of the product listing to update.")
class Deprecated202001UpdateProductListingsParamProductListingIdRequest(StrictModel):
    """Update a product listing to publish or modify a product's presence on your sales channel app."""
    path: Deprecated202001UpdateProductListingsParamProductListingIdRequestPath

# Operation: delete_product_listing
class Deprecated202001DeleteProductListingsParamProductListingIdRequestPath(StrictModel):
    product_listing_id: str = Field(default=..., description="The unique identifier of the product listing to delete.")
class Deprecated202001DeleteProductListingsParamProductListingIdRequest(StrictModel):
    """Remove a product listing to unpublish a product from your sales channel app. This operation deletes the listing relationship without affecting the product itself."""
    path: Deprecated202001DeleteProductListingsParamProductListingIdRequestPath

# Operation: list_products_2020_01
class Deprecated202001GetProductsRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only include products with IDs matching this comma-separated list of product identifiers.")
    limit: Any | None = Field(default=None, description="Maximum number of products to return per page, between 1 and 250 (defaults to 50).")
    title: Any | None = Field(default=None, description="Filter results to only include products whose title contains this text.")
    vendor: Any | None = Field(default=None, description="Filter results to only include products from this vendor.")
    handle: Any | None = Field(default=None, description="Filter results to only include products with this handle (URL-friendly identifier).")
    product_type: Any | None = Field(default=None, description="Filter results to only include products of this type.")
    status: Any | None = Field(default=None, description="Filter results by product status: active (default) shows only active products, archived shows only archived products, or draft shows only draft products.")
    collection_id: Any | None = Field(default=None, description="Filter results to only include products in this collection, specified by collection ID.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: published shows only published products, unpublished shows only unpublished products, or any (default) shows all products regardless of publication status.")
    presentment_currencies: Any | None = Field(default=None, description="Return presentment prices in only the specified currencies, provided as a comma-separated list of ISO 4217 currency codes.")
class Deprecated202001GetProductsRequest(StrictModel):
    """Retrieves a paginated list of products from the store, with support for filtering by various attributes and sorting options. Uses cursor-based pagination via response headers rather than page parameters."""
    query: Deprecated202001GetProductsRequestQuery | None = None

# Operation: get_products_count_202001
class Deprecated202001GetProductsCountRequestQuery(StrictModel):
    vendor: Any | None = Field(default=None, description="Filter the count to include only products from a specific vendor.")
    product_type: Any | None = Field(default=None, description="Filter the count to include only products of a specific product type.")
    collection_id: Any | None = Field(default=None, description="Filter the count to include only products belonging to a specific collection by its ID.")
    published_status: Any | None = Field(default=None, description="Filter products by their publication status: use 'published' for only published products, 'unpublished' for only unpublished products, or 'any' to include all products regardless of status (default is 'any').")
class Deprecated202001GetProductsCountRequest(StrictModel):
    """Retrieves the total count of products in the store, with optional filtering by vendor, product type, collection, or published status."""
    query: Deprecated202001GetProductsCountRequestQuery | None = None

# Operation: get_product_202001
class Deprecated202001GetProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to retrieve.")
class Deprecated202001GetProductsParamProductIdRequest(StrictModel):
    """Retrieves detailed information for a single product by its ID from the Shopify store."""
    path: Deprecated202001GetProductsParamProductIdRequestPath

# Operation: delete_product_202001
class Deprecated202001DeleteProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to delete. This is a numeric ID assigned by Shopify.")
class Deprecated202001DeleteProductsParamProductIdRequest(StrictModel):
    """Permanently deletes a product from the store. This action cannot be undone and will remove the product and all associated data."""
    path: Deprecated202001DeleteProductsParamProductIdRequestPath

# Operation: list_product_images_202001
class Deprecated202001GetProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product whose images you want to retrieve.")
class Deprecated202001GetProductsParamProductIdImagesRequest(StrictModel):
    """Retrieve all images associated with a specific product. Returns a collection of image resources for the given product."""
    path: Deprecated202001GetProductsParamProductIdImagesRequestPath

# Operation: create_product_image_202001
class Deprecated202001CreateProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to which the image will be added.")
class Deprecated202001CreateProductsParamProductIdImagesRequest(StrictModel):
    """Create a new image for a specific product. The image will be associated with the product and can be used to display product visuals in the storefront."""
    path: Deprecated202001CreateProductsParamProductIdImagesRequestPath

# Operation: get_product_images_count_202001
class Deprecated202001GetProductsParamProductIdImagesCountRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product for which to retrieve the image count.")
class Deprecated202001GetProductsParamProductIdImagesCountRequest(StrictModel):
    """Retrieve the total count of images associated with a specific product. Useful for determining how many product images exist without fetching the full image data."""
    path: Deprecated202001GetProductsParamProductIdImagesCountRequestPath

# Operation: update_product_image_202001
class Deprecated202001UpdateProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product that contains the image to be updated.")
    image_id: str = Field(default=..., description="The unique identifier of the specific image within the product to be updated.")
class Deprecated202001UpdateProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Update the properties of an existing product image, such as alt text, position, or other image metadata."""
    path: Deprecated202001UpdateProductsParamProductIdImagesParamImageIdRequestPath

# Operation: delete_product_image_202001
class Deprecated202001DeleteProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product that contains the image to be deleted.")
    image_id: str = Field(default=..., description="The unique identifier of the image to be deleted from the product.")
class Deprecated202001DeleteProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Delete a specific image associated with a product. This removes the image from the product's image gallery."""
    path: Deprecated202001DeleteProductsParamProductIdImagesParamImageIdRequestPath

# Operation: get_recurring_application_charge_202001
class Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to retrieve.")
class Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(StrictModel):
    """Retrieves details for a specific recurring application charge by its ID. Use this to fetch the current status, pricing, and other metadata for a recurring charge."""
    path: Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath

# Operation: delete_recurring_application_charge_2020_01
class Deprecated202001DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to cancel. This ID is returned when the charge is created.")
class Deprecated202001DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(StrictModel):
    """Cancels an active recurring application charge for the app. This prevents future billing cycles for the specified charge."""
    path: Deprecated202001DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath

# Operation: update_recurring_application_charge_capped_amount_2020_01
class Deprecated202001UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to update.")
class Deprecated202001UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery(StrictModel):
    recurring_application_charge_capped_amount: int | None = Field(default=None, validation_alias="recurring_application_charge[capped_amount]", serialization_alias="recurring_application_charge[capped_amount]", description="The new capped amount limit for the recurring charge, specified as a whole number representing the maximum billable amount.")
class Deprecated202001UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest(StrictModel):
    """Updates the capped amount limit for an active recurring application charge. This allows you to modify the maximum amount that can be charged to the merchant for this recurring billing plan."""
    path: Deprecated202001UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath
    query: Deprecated202001UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery | None = None

# Operation: list_usage_charges_for_recurring_application_charge_2020_01
class Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge for which to retrieve associated usage charges.")
class Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Retrieves all usage charges associated with a specific recurring application charge. Usage charges represent metered billing events tracked against a recurring subscription."""
    path: Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath

# Operation: create_usage_charge_for_recurring_application_charge_202001
class Deprecated202001CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge for which to create the usage charge.")
class Deprecated202001CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Creates a usage charge against an existing recurring application charge. Usage charges allow you to bill customers for variable usage on top of their recurring subscription."""
    path: Deprecated202001CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath

# Operation: get_usage_charge_for_recurring_application_charge_202001
class Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge that contains the usage charge you want to retrieve.")
    usage_charge_id: str = Field(default=..., description="The unique identifier of the specific usage charge to retrieve.")
class Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest(StrictModel):
    """Retrieves a single usage charge associated with a recurring application charge. Use this to fetch details about a specific metered billing charge."""
    path: Deprecated202001GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath

# Operation: list_redirects_202001
class Deprecated202001GetRedirectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of redirects to return per request, between 1 and 250 (defaults to 50).")
    path: Any | None = Field(default=None, description="Filter results to show only redirects with a specific source path.")
    target: Any | None = Field(default=None, description="Filter results to show only redirects pointing to a specific target URL.")
class Deprecated202001GetRedirectsRequest(StrictModel):
    """Retrieves a list of URL redirects configured in the online store. Results are paginated using link headers in the response."""
    query: Deprecated202001GetRedirectsRequestQuery | None = None

# Operation: get_redirects_count_2020_01
class Deprecated202001GetRedirectsCountRequestQuery(StrictModel):
    path: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific path value.")
    target: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific target URL.")
class Deprecated202001GetRedirectsCountRequest(StrictModel):
    """Retrieves the total count of URL redirects in the store, with optional filtering by path or target URL."""
    query: Deprecated202001GetRedirectsCountRequestQuery | None = None

# Operation: get_redirect_202001
class Deprecated202001GetRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to retrieve.")
class Deprecated202001GetRedirectsParamRedirectIdRequest(StrictModel):
    """Retrieves a single redirect by its ID from the Shopify online store. Use this to fetch details about a specific URL redirect configuration."""
    path: Deprecated202001GetRedirectsParamRedirectIdRequestPath

# Operation: update_redirect_v202001
class Deprecated202001UpdateRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to update. This ID is required to locate and modify the specific redirect.")
class Deprecated202001UpdateRedirectsParamRedirectIdRequest(StrictModel):
    """Updates an existing redirect in the online store. Modify redirect settings such as the target path or status by providing the redirect's unique identifier."""
    path: Deprecated202001UpdateRedirectsParamRedirectIdRequestPath

# Operation: delete_redirect_v202001
class Deprecated202001DeleteRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to delete.")
class Deprecated202001DeleteRedirectsParamRedirectIdRequest(StrictModel):
    """Permanently deletes a redirect from the online store. This action cannot be undone."""
    path: Deprecated202001DeleteRedirectsParamRedirectIdRequestPath

# Operation: create_report_legacy_202001
class Deprecated202001CreateReportsRequestQuery(StrictModel):
    name: Any | None = Field(default=None, description="The display name for the report. Must not exceed 255 characters.")
    shopify_ql: Any | None = Field(default=None, description="The ShopifyQL query string that defines what data the report will retrieve and analyze.")
class Deprecated202001CreateReportsRequest(StrictModel):
    """Creates a new custom report in the Shopify admin. Reports can be configured with a name and ShopifyQL query to analyze store data."""
    query: Deprecated202001CreateReportsRequestQuery | None = None

# Operation: get_report_202001
class Deprecated202001GetReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to retrieve.")
class Deprecated202001GetReportsParamReportIdRequest(StrictModel):
    """Retrieves a single report that was created by your app. Use this to fetch details about a specific report by its ID."""
    path: Deprecated202001GetReportsParamReportIdRequestPath

# Operation: delete_report_202001
class Deprecated202001DeleteReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to delete. This is a required string value that identifies which report should be removed.")
class Deprecated202001DeleteReportsParamReportIdRequest(StrictModel):
    """Permanently deletes a specific report from the Shopify admin. This action cannot be undone."""
    path: Deprecated202001DeleteReportsParamReportIdRequestPath

# Operation: list_shopify_payments_balance_transactions
class Deprecated202001GetShopifyPaymentsBalanceTransactionsRequestQuery(StrictModel):
    test: Any | None = Field(default=None, description="Filter results to include only transactions placed in test mode when set to true.")
    payout_id: Any | None = Field(default=None, description="Filter results to transactions associated with a specific payout by providing the payout ID.")
    payout_status: Any | None = Field(default=None, description="Filter results to transactions with a specific payout status (e.g., pending, paid, failed).")
class Deprecated202001GetShopifyPaymentsBalanceTransactionsRequest(StrictModel):
    """Retrieves a paginated list of Shopify Payments balance transactions ordered by processing time, with the most recent first. Use cursor-based pagination via response header links."""
    query: Deprecated202001GetShopifyPaymentsBalanceTransactionsRequestQuery | None = None

# Operation: list_shopify_payments_disputes
class Deprecated202001GetShopifyPaymentsDisputesRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter disputes by their current status (e.g., won, lost, under_review). Only disputes matching the specified status will be returned.")
    initiated_at: Any | None = Field(default=None, description="Filter disputes by their initiation date in ISO 8601 format. Only disputes initiated on the specified date will be returned.")
class Deprecated202001GetShopifyPaymentsDisputesRequest(StrictModel):
    """Retrieve all Shopify Payments disputes ordered by initiation date (most recent first). Results are paginated using link headers in the response."""
    query: Deprecated202001GetShopifyPaymentsDisputesRequestQuery | None = None

# Operation: list_shopify_payments_payouts_2020_01
class Deprecated202001GetShopifyPaymentsPayoutsRequestQuery(StrictModel):
    date_min: Any | None = Field(default=None, description="Filter payouts to include only those made on or after this date (inclusive). Specify as an ISO 8601 formatted date.")
    date_max: Any | None = Field(default=None, description="Filter payouts to include only those made on or before this date (inclusive). Specify as an ISO 8601 formatted date.")
    status: Any | None = Field(default=None, description="Filter payouts by their current status (e.g., pending, paid, failed, cancelled). Only payouts matching the specified status will be returned.")
class Deprecated202001GetShopifyPaymentsPayoutsRequest(StrictModel):
    """Retrieves a list of all payouts from Shopify Payments, ordered by payout date with the most recent first. Results are paginated using link headers in the response."""
    query: Deprecated202001GetShopifyPaymentsPayoutsRequestQuery | None = None

# Operation: get_shopify_payments_payout_2020_01
class Deprecated202001GetShopifyPaymentsPayoutsParamPayoutIdRequestPath(StrictModel):
    payout_id: str = Field(default=..., description="The unique identifier of the payout to retrieve.")
class Deprecated202001GetShopifyPaymentsPayoutsParamPayoutIdRequest(StrictModel):
    """Retrieves details for a specific Shopify Payments payout by its unique identifier."""
    path: Deprecated202001GetShopifyPaymentsPayoutsParamPayoutIdRequestPath

# Operation: list_smart_collections_202001
class Deprecated202001GetSmartCollectionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of smart collections to return per request. Must be between 1 and 250; defaults to 50.")
    ids: Any | None = Field(default=None, description="Filter results to only smart collections with the specified IDs. Provide as a comma-separated list of numeric IDs.")
    title: Any | None = Field(default=None, description="Filter results to smart collections matching the exact title.")
    product_id: Any | None = Field(default=None, description="Filter results to smart collections that contain the specified product ID.")
    handle: Any | None = Field(default=None, description="Filter results by smart collection handle (the URL-friendly identifier).")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for published collections only, 'unpublished' for unpublished only, or 'any' for all collections. Defaults to 'any'.")
class Deprecated202001GetSmartCollectionsRequest(StrictModel):
    """Retrieves a paginated list of smart collections from your store. Results are paginated using link headers in the response."""
    query: Deprecated202001GetSmartCollectionsRequestQuery | None = None

# Operation: count_smart_collections_202001
class Deprecated202001GetSmartCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter to only count smart collections with this exact title.")
    product_id: Any | None = Field(default=None, description="Filter to only count smart collections that include the specified product.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for only published collections, 'unpublished' for only unpublished collections, or 'any' to include all collections regardless of status. Defaults to 'any'.")
class Deprecated202001GetSmartCollectionsCountRequest(StrictModel):
    """Retrieves the total count of smart collections in the store, with optional filtering by title, product inclusion, or published status."""
    query: Deprecated202001GetSmartCollectionsCountRequestQuery | None = None

# Operation: update_smart_collection_202001
class Deprecated202001UpdateSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to update.")
class Deprecated202001UpdateSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Updates an existing smart collection by its ID. Use this to modify smart collection properties such as title, rules, and other configuration settings."""
    path: Deprecated202001UpdateSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: delete_smart_collection_202001
class Deprecated202001DeleteSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to delete.")
class Deprecated202001DeleteSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Permanently removes a smart collection from the store. This action cannot be undone."""
    path: Deprecated202001DeleteSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: list_tender_transactions_202001
class Deprecated202001GetTenderTransactionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250 (defaults to 50).")
    processed_at_min: Any | None = Field(default=None, description="Filter to show only tender transactions processed on or after this date (ISO 8601 format).")
    processed_at_max: Any | None = Field(default=None, description="Filter to show only tender transactions processed on or before this date (ISO 8601 format).")
    order: Any | None = Field(default=None, description="Sort results by processed_at timestamp in either ascending or descending order.")
class Deprecated202001GetTenderTransactionsRequest(StrictModel):
    """Retrieves a paginated list of tender transactions. Results are paginated using link headers in the response; use the provided links to navigate between pages."""
    query: Deprecated202001GetTenderTransactionsRequestQuery | None = None

# Operation: get_theme_202001
class Deprecated202001GetThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to retrieve.")
class Deprecated202001GetThemesParamThemeIdRequest(StrictModel):
    """Retrieves the details of a single theme by its ID from the Shopify online store."""
    path: Deprecated202001GetThemesParamThemeIdRequestPath

# Operation: update_theme_deprecated
class Deprecated202001UpdateThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to update. This is a required string value that specifies which theme will be modified.")
class Deprecated202001UpdateThemesParamThemeIdRequest(StrictModel):
    """Updates an existing theme in the Shopify online store. Modify theme settings and properties by providing the theme ID."""
    path: Deprecated202001UpdateThemesParamThemeIdRequestPath

# Operation: delete_theme_2020_01
class Deprecated202001DeleteThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to delete, returned as a string by the Shopify API.")
class Deprecated202001DeleteThemesParamThemeIdRequest(StrictModel):
    """Permanently deletes a theme from the Shopify store. The theme must not be the currently active theme."""
    path: Deprecated202001DeleteThemesParamThemeIdRequestPath

# Operation: delete_theme_asset_202001
class Deprecated202001DeleteThemesParamThemeIdAssetsRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme from which the asset will be deleted.")
class Deprecated202001DeleteThemesParamThemeIdAssetsRequestQuery(StrictModel):
    asset_key: str | None = Field(default=None, validation_alias="asset[key]", serialization_alias="asset[key]", description="The key (file path) of the asset to delete from the theme. This identifies which specific asset file to remove.")
class Deprecated202001DeleteThemesParamThemeIdAssetsRequest(StrictModel):
    """Removes a specific asset file from a Shopify theme. The asset is identified by its key within the theme."""
    path: Deprecated202001DeleteThemesParamThemeIdAssetsRequestPath
    query: Deprecated202001DeleteThemesParamThemeIdAssetsRequestQuery | None = None

# Operation: list_webhooks_legacy_202001
class Deprecated202001GetWebhooksRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter webhooks by the URI endpoint where they send POST requests.")
    limit: Any | None = Field(default=None, description="Maximum number of webhooks to return per request, between 1 and 250 (defaults to 50).")
    topic: Any | None = Field(default=None, description="Filter webhooks by topic name to show only subscriptions for specific events.")
class Deprecated202001GetWebhooksRequest(StrictModel):
    """Retrieves a list of webhook subscriptions configured for your Shopify store. Results are paginated using link headers in the response."""
    query: Deprecated202001GetWebhooksRequestQuery | None = None

# Operation: count_webhooks_202001
class Deprecated202001GetWebhooksCountRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter the webhook count to only subscriptions that deliver POST requests to this specific URI.")
    topic: Any | None = Field(default=None, description="Filter the webhook count to only subscriptions listening to this specific event topic. Refer to the webhook topic property documentation for valid topic values.")
class Deprecated202001GetWebhooksCountRequest(StrictModel):
    """Retrieves the total count of webhook subscriptions configured in the Shopify store, with optional filtering by delivery address or event topic."""
    query: Deprecated202001GetWebhooksCountRequestQuery | None = None

# Operation: get_application_charge_202004
class Deprecated202004GetApplicationChargesParamApplicationChargeIdRequestPath(StrictModel):
    application_charge_id: str = Field(default=..., description="The unique identifier of the application charge to retrieve.")
class Deprecated202004GetApplicationChargesParamApplicationChargeIdRequest(StrictModel):
    """Retrieves details for a specific application charge by its ID. Use this to fetch the current status and information of a billing charge associated with your app."""
    path: Deprecated202004GetApplicationChargesParamApplicationChargeIdRequestPath

# Operation: list_articles_for_blog_v202004
class Deprecated202004GetBlogsParamBlogIdArticlesRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog from which to retrieve articles.")
class Deprecated202004GetBlogsParamBlogIdArticlesRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of articles to return per request, between 1 and 250 (defaults to 50).")
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: 'published' for published articles only, 'unpublished' for unpublished articles only, or 'any' for all articles regardless of status (defaults to 'any').")
    handle: Any | None = Field(default=None, description="Retrieve a single article by its URL-friendly handle identifier.")
    tag: Any | None = Field(default=None, description="Filter articles to only those tagged with a specific tag.")
    author: Any | None = Field(default=None, description="Filter articles to only those written by a specific author.")
class Deprecated202004GetBlogsParamBlogIdArticlesRequest(StrictModel):
    """Retrieves a paginated list of articles from a specific blog. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    path: Deprecated202004GetBlogsParamBlogIdArticlesRequestPath
    query: Deprecated202004GetBlogsParamBlogIdArticlesRequestQuery | None = None

# Operation: create_article_for_blog_202004
class Deprecated202004CreateBlogsParamBlogIdArticlesRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog where the article will be created.")
class Deprecated202004CreateBlogsParamBlogIdArticlesRequest(StrictModel):
    """Creates a new article for a specified blog. The article will be added to the blog's collection of articles."""
    path: Deprecated202004CreateBlogsParamBlogIdArticlesRequestPath

# Operation: get_article_count_for_blog_2020_04
class Deprecated202004GetBlogsParamBlogIdArticlesCountRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog for which to count articles.")
class Deprecated202004GetBlogsParamBlogIdArticlesCountRequestQuery(StrictModel):
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: use 'published' to count only published articles, 'unpublished' to count only unpublished articles, or 'any' to count all articles regardless of status. Defaults to 'any' if not specified.")
class Deprecated202004GetBlogsParamBlogIdArticlesCountRequest(StrictModel):
    """Retrieves the total count of articles in a specific blog, with optional filtering by publication status."""
    path: Deprecated202004GetBlogsParamBlogIdArticlesCountRequestPath
    query: Deprecated202004GetBlogsParamBlogIdArticlesCountRequestQuery | None = None

# Operation: get_article_202004
class Deprecated202004GetBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article.")
    article_id: str = Field(default=..., description="The unique identifier of the article to retrieve.")
class Deprecated202004GetBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Retrieves a single article from a blog by its ID. Use this to fetch detailed information about a specific article in the Shopify online store."""
    path: Deprecated202004GetBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: update_article_202004
class Deprecated202004UpdateBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article to update.")
    article_id: str = Field(default=..., description="The unique identifier of the article to update.")
class Deprecated202004UpdateBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Updates an existing article within a blog. Modify article content, metadata, and other properties by providing the blog and article identifiers."""
    path: Deprecated202004UpdateBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: delete_article_202004
class Deprecated202004DeleteBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article to delete.")
    article_id: str = Field(default=..., description="The unique identifier of the article to delete.")
class Deprecated202004DeleteBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Permanently deletes an article from a blog. This action cannot be undone."""
    path: Deprecated202004DeleteBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: update_carrier_service_202004
class Deprecated202004UpdateCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to update.")
class Deprecated202004UpdateCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Updates an existing carrier service configuration. Only the application that originally created the carrier service can modify it."""
    path: Deprecated202004UpdateCarrierServicesParamCarrierServiceIdRequestPath

# Operation: delete_carrier_service_2020_04
class Deprecated202004DeleteCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to delete.")
class Deprecated202004DeleteCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Permanently deletes a carrier service from the store. This action cannot be undone and will remove the carrier service configuration."""
    path: Deprecated202004DeleteCarrierServicesParamCarrierServiceIdRequestPath

# Operation: get_abandoned_checkouts_count_202004
class Deprecated202004GetCheckoutsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count by checkout status. Use 'open' to count only active abandoned checkouts or 'closed' to count only completed/closed abandoned checkouts. Defaults to 'open' if not specified.")
class Deprecated202004GetCheckoutsCountRequest(StrictModel):
    """Retrieves the count of abandoned checkouts from the past 90 days, optionally filtered by checkout status."""
    query: Deprecated202004GetCheckoutsCountRequestQuery | None = None

# Operation: list_shipping_rates_for_checkout_2020_04
class Deprecated202004GetCheckoutsParamTokenShippingRatesRequestPath(StrictModel):
    token: str = Field(default=..., description="The unique identifier for the checkout. This token is used to retrieve shipping rates specific to that checkout.")
class Deprecated202004GetCheckoutsParamTokenShippingRatesRequest(StrictModel):
    """Retrieves available shipping rates for a checkout. Poll this endpoint until rates become available, then use the returned rates to display updated pricing (subtotal, tax, total) or apply a rate by updating the checkout's shipping line."""
    path: Deprecated202004GetCheckoutsParamTokenShippingRatesRequestPath

# Operation: delete_collection_listing_202004
class Deprecated202004DeleteCollectionListingsParamCollectionListingIdRequestPath(StrictModel):
    collection_listing_id: str = Field(default=..., description="The unique identifier of the collection listing to delete.")
class Deprecated202004DeleteCollectionListingsParamCollectionListingIdRequest(StrictModel):
    """Remove a collection listing to unpublish a collection from your sales channel or app."""
    path: Deprecated202004DeleteCollectionListingsParamCollectionListingIdRequestPath

# Operation: get_collection_202004
class Deprecated202004GetCollectionsParamCollectionIdRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection to retrieve.")
class Deprecated202004GetCollectionsParamCollectionIdRequest(StrictModel):
    """Retrieves the details of a single collection by its ID, including metadata such as name, description, and product associations."""
    path: Deprecated202004GetCollectionsParamCollectionIdRequestPath

# Operation: list_collection_products_202004
class Deprecated202004GetCollectionsParamCollectionIdProductsRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection whose products you want to retrieve.")
class Deprecated202004GetCollectionsParamCollectionIdProductsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of products to return per request, ranging from 1 to 250 products (defaults to 50 if not specified).")
class Deprecated202004GetCollectionsParamCollectionIdProductsRequest(StrictModel):
    """Retrieve products belonging to a specific collection, sorted according to the collection's configured sort order. Results are paginated using link-based navigation provided in response headers."""
    path: Deprecated202004GetCollectionsParamCollectionIdProductsRequestPath
    query: Deprecated202004GetCollectionsParamCollectionIdProductsRequestQuery | None = None

# Operation: list_collects_2020_04
class Deprecated202004GetCollectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, ranging from 1 to 250 items. Defaults to 50 if not specified.")
class Deprecated202004GetCollectsRequest(StrictModel):
    """Retrieves a list of collects (product-to-collection associations). Uses cursor-based pagination via response header links; the page parameter is not supported."""
    query: Deprecated202004GetCollectsRequestQuery | None = None

# Operation: get_collects_count_202004
class Deprecated202004GetCollectsCountRequestQuery(StrictModel):
    collection_id: int | None = Field(default=None, description="Filter the count to only include collects within a specific collection. When omitted, returns the count of all collects across the store.")
class Deprecated202004GetCollectsCountRequest(StrictModel):
    """Retrieves the total count of collects, optionally filtered by a specific collection. Useful for understanding the size of a collection or the total number of product-to-collection associations."""
    query: Deprecated202004GetCollectsCountRequestQuery | None = None

# Operation: get_collect_202004
class Deprecated202004GetCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect record to retrieve.")
class Deprecated202004GetCollectsParamCollectIdRequest(StrictModel):
    """Retrieves a specific product collection by its ID. Use this to fetch details about how a product is organized within a collection."""
    path: Deprecated202004GetCollectsParamCollectIdRequestPath

# Operation: remove_product_from_collection_2020_04
class Deprecated202004DeleteCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect relationship to remove. This ID represents the link between a product and a collection.")
class Deprecated202004DeleteCollectsParamCollectIdRequest(StrictModel):
    """Removes a product from a collection by deleting the collect relationship. This operation unlinks a product from a specific collection without affecting the product or collection itself."""
    path: Deprecated202004DeleteCollectsParamCollectIdRequestPath

# Operation: update_country_202004
class Deprecated202004UpdateCountriesParamCountryIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country to update.")
class Deprecated202004UpdateCountriesParamCountryIdRequest(StrictModel):
    """Updates an existing country's configuration. Note: The tax field is deprecated as of API version 2020-10 and should not be used."""
    path: Deprecated202004UpdateCountriesParamCountryIdRequestPath

# Operation: delete_country_202004
class Deprecated202004DeleteCountriesParamCountryIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country to delete. This is a required string value that specifies which country record to remove.")
class Deprecated202004DeleteCountriesParamCountryIdRequest(StrictModel):
    """Permanently deletes a country from the store's configuration. This operation removes the country and all associated settings."""
    path: Deprecated202004DeleteCountriesParamCountryIdRequestPath

# Operation: list_provinces_for_country_202004
class Deprecated202004GetCountriesParamCountryIdProvincesRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve provinces. This ID corresponds to a valid country in the Shopify system.")
class Deprecated202004GetCountriesParamCountryIdProvincesRequest(StrictModel):
    """Retrieves a list of provinces or states for a specified country. Use this to populate province/state selectors in address forms or location-based workflows."""
    path: Deprecated202004GetCountriesParamCountryIdProvincesRequestPath

# Operation: get_province_count_for_country_202004
class Deprecated202004GetCountriesParamCountryIdProvincesCountRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve the province count.")
class Deprecated202004GetCountriesParamCountryIdProvincesCountRequest(StrictModel):
    """Retrieves the total count of provinces or states for a specified country. Useful for understanding administrative divisions within a country."""
    path: Deprecated202004GetCountriesParamCountryIdProvincesCountRequestPath

# Operation: update_province_for_country_2020_04
class Deprecated202004UpdateCountriesParamCountryIdProvincesParamProvinceIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country containing the province to update.")
    province_id: str = Field(default=..., description="The unique identifier of the province to update.")
class Deprecated202004UpdateCountriesParamCountryIdProvincesParamProvinceIdRequest(StrictModel):
    """Updates an existing province for a specified country. Note: The tax field is deprecated as of API version 2020-10."""
    path: Deprecated202004UpdateCountriesParamCountryIdProvincesParamProvinceIdRequestPath

# Operation: list_custom_collections_202004
class Deprecated202004GetCustomCollectionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 if not specified.")
    ids: Any | None = Field(default=None, description="Filter results to only collections with IDs matching this comma-separated list of collection IDs.")
    title: Any | None = Field(default=None, description="Filter results to only collections with an exact title match.")
    product_id: Any | None = Field(default=None, description="Filter results to only collections that contain a specific product, identified by product ID.")
    handle: Any | None = Field(default=None, description="Filter results by the collection's URL-friendly handle identifier.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for published collections only, 'unpublished' for unpublished collections only, or 'any' for all collections regardless of status. Defaults to 'any'.")
class Deprecated202004GetCustomCollectionsRequest(StrictModel):
    """Retrieves a list of custom collections with optional filtering and pagination. Results are paginated using link headers in the response; the page parameter is not supported."""
    query: Deprecated202004GetCustomCollectionsRequestQuery | None = None

# Operation: count_custom_collections_2020_04
class Deprecated202004GetCustomCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter the count to include only custom collections with this exact title.")
    product_id: Any | None = Field(default=None, description="Filter the count to include only custom collections that contain this specific product.")
    published_status: Any | None = Field(default=None, description="Filter the count by publication status: 'published' for only published collections, 'unpublished' for only unpublished collections, or 'any' for all collections regardless of status. Defaults to 'any' if not specified.")
class Deprecated202004GetCustomCollectionsCountRequest(StrictModel):
    """Retrieves the total count of custom collections in the store, with optional filtering by title, product inclusion, or published status."""
    query: Deprecated202004GetCustomCollectionsCountRequestQuery | None = None

# Operation: update_custom_collection_202004
class Deprecated202004UpdateCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to update.")
class Deprecated202004UpdateCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Updates an existing custom collection in your Shopify store. Modify collection details such as title, description, image, and other properties."""
    path: Deprecated202004UpdateCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: list_customers_202004
class Deprecated202004GetCustomersRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only include customers with the specified IDs. Provide as a comma-separated list of customer IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of customer records to return per request. Defaults to 50 and cannot exceed 250.")
class Deprecated202004GetCustomersRequest(StrictModel):
    """Retrieves a paginated list of customers from the store. Results are paginated using link headers in the response; use the provided links for navigation rather than the page parameter."""
    query: Deprecated202004GetCustomersRequestQuery | None = None

# Operation: search_customers_202004
class Deprecated202004GetCustomersSearchRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="Specify which field to sort results by and the sort direction (ascending or descending). Defaults to sorting by last order date in descending order.")
    query: Any | None = Field(default=None, description="Text query to search across customer data fields such as name, email, phone, and address.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 results.")
class Deprecated202004GetCustomersSearchRequest(StrictModel):
    """Search for customers in the shop by query text. Results are paginated using link headers in the response."""
    query: Deprecated202004GetCustomersSearchRequestQuery | None = None

# Operation: get_customer_202004
class Deprecated202004GetCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to retrieve.")
class Deprecated202004GetCustomersParamCustomerIdRequest(StrictModel):
    """Retrieves a single customer by their unique identifier from the Shopify store."""
    path: Deprecated202004GetCustomersParamCustomerIdRequestPath

# Operation: update_customer_202004
class Deprecated202004UpdateCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to update. This ID is required to specify which customer record should be modified.")
class Deprecated202004UpdateCustomersParamCustomerIdRequest(StrictModel):
    """Updates an existing customer's information in Shopify. Modify customer details such as email, name, phone, and other profile attributes."""
    path: Deprecated202004UpdateCustomersParamCustomerIdRequestPath

# Operation: delete_customer_v202004
class Deprecated202004DeleteCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to delete.")
class Deprecated202004DeleteCustomersParamCustomerIdRequest(StrictModel):
    """Permanently deletes a customer from the store. Note that a customer cannot be deleted if they have any existing orders."""
    path: Deprecated202004DeleteCustomersParamCustomerIdRequestPath

# Operation: generate_customer_account_activation_url_2020_04
class Deprecated202004CreateCustomersParamCustomerIdAccountActivationUrlRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer for whom to generate the account activation URL.")
class Deprecated202004CreateCustomersParamCustomerIdAccountActivationUrlRequest(StrictModel):
    """Generate a one-time account activation URL for a customer whose account is not yet enabled. The URL expires after 30 days; generating a new URL invalidates any previously generated URLs."""
    path: Deprecated202004CreateCustomersParamCustomerIdAccountActivationUrlRequestPath

# Operation: list_customer_addresses_202004
class Deprecated202004GetCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses you want to retrieve.")
class Deprecated202004GetCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Retrieves all addresses associated with a specific customer. Uses cursor-based pagination via response headers; the page parameter is not supported."""
    path: Deprecated202004GetCustomersParamCustomerIdAddressesRequestPath

# Operation: create_customer_address_v202004
class Deprecated202004CreateCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer for whom the address is being created.")
class Deprecated202004CreateCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Creates a new address for a customer. The address is added to the customer's address list and can be set as their default billing or shipping address."""
    path: Deprecated202004CreateCustomersParamCustomerIdAddressesRequestPath

# Operation: bulk_update_customer_addresses_202004
class Deprecated202004UpdateCustomersParamCustomerIdAddressesSetRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses will be modified.")
class Deprecated202004UpdateCustomersParamCustomerIdAddressesSetRequestQuery(StrictModel):
    address_ids: int | None = Field(default=None, validation_alias="address_ids[]", serialization_alias="address_ids[]", description="Array of address IDs to target for the bulk operation. The order may affect processing sequence depending on the operation type.")
    operation: str | None = Field(default=None, description="The type of bulk operation to perform on the specified addresses (e.g., delete, set as default). Consult API documentation for valid operation values.")
class Deprecated202004UpdateCustomersParamCustomerIdAddressesSetRequest(StrictModel):
    """Performs bulk operations on multiple customer addresses, allowing you to update, delete, or modify address records in a single request."""
    path: Deprecated202004UpdateCustomersParamCustomerIdAddressesSetRequestPath
    query: Deprecated202004UpdateCustomersParamCustomerIdAddressesSetRequestQuery | None = None

# Operation: get_customer_address_202004
class Deprecated202004GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who owns the address.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to retrieve.")
class Deprecated202004GetCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Retrieves the details of a specific customer address by customer ID and address ID."""
    path: Deprecated202004GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: update_customer_address_2020_04
class Deprecated202004UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being updated.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to update for the customer.")
class Deprecated202004UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Updates an existing customer address by customer ID and address ID. Use this to modify address details such as street, city, postal code, or other address information for a specific customer."""
    path: Deprecated202004UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: delete_customer_address_202004
class Deprecated202004DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being removed.")
    address_id: str = Field(default=..., description="The unique identifier of the address to be deleted from the customer's address list.")
class Deprecated202004DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Removes a specific address from a customer's address list. This operation permanently deletes the address record associated with the given customer."""
    path: Deprecated202004DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: set_customer_default_address_202004
class Deprecated202004UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose default address is being updated.")
    address_id: str = Field(default=..., description="The unique identifier of the address to set as the customer's default address.")
class Deprecated202004UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest(StrictModel):
    """Sets a specific address as the default address for a customer. This updates the customer's primary address used for shipping and billing purposes."""
    path: Deprecated202004UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath

# Operation: list_customer_orders_202004
class Deprecated202004GetCustomersParamCustomerIdOrdersRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose orders should be retrieved.")
class Deprecated202004GetCustomersParamCustomerIdOrdersRequest(StrictModel):
    """Retrieves all orders for a specific customer. Supports filtering and sorting through standard Order resource query parameters."""
    path: Deprecated202004GetCustomersParamCustomerIdOrdersRequestPath

# Operation: send_customer_invite_202004
class Deprecated202004CreateCustomersParamCustomerIdSendInviteRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who will receive the account invite.")
class Deprecated202004CreateCustomersParamCustomerIdSendInviteRequest(StrictModel):
    """Sends an account invitation email to a customer, allowing them to create or access their account on the store."""
    path: Deprecated202004CreateCustomersParamCustomerIdSendInviteRequestPath

# Operation: list_events_202004
class Deprecated202004GetEventsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of events to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
    filter_: Any | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filters events to only those matching the specified criteria. Use this to narrow results to specific event types or conditions.")
    verb: Any | None = Field(default=None, description="Filters events to only those of a specific action type (e.g., create, update, delete). Narrows results to events matching the specified verb.")
class Deprecated202004GetEventsRequest(StrictModel):
    """Retrieves a paginated list of events from the store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: Deprecated202004GetEventsRequestQuery | None = None

# Operation: get_event_2020_04
class Deprecated202004GetEventsParamEventIdRequestPath(StrictModel):
    event_id: str = Field(default=..., description="The unique identifier of the event to retrieve.")
class Deprecated202004GetEventsParamEventIdRequest(StrictModel):
    """Retrieves a single event by its ID from the Shopify admin. Use this to fetch detailed information about a specific event that occurred in your store."""
    path: Deprecated202004GetEventsParamEventIdRequestPath

# Operation: get_fulfillment_order_202004
class Deprecated202004GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to retrieve.")
class Deprecated202004GetFulfillmentOrdersParamFulfillmentOrderIdRequest(StrictModel):
    """Retrieves the details of a specific fulfillment order by its ID. Use this to fetch current status, line items, and fulfillment information for a particular order."""
    path: Deprecated202004GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath

# Operation: cancel_fulfillment_order_2020_04
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest(StrictModel):
    """Cancels a fulfillment order, marking it as no longer needed for processing. This operation is used to prevent a fulfillment order from being fulfilled."""
    path: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath

# Operation: send_fulfillment_order_cancellation_request_2020_04
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for the cancellation request.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest(StrictModel):
    """Sends a cancellation request to the fulfillment service for a specific fulfillment order. This notifies the fulfillment provider that the order should be cancelled."""
    path: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath
    query: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery | None = None

# Operation: accept_fulfillment_order_cancellation_request_2020_04
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to accept the cancellation request.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for accepting the cancellation request.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest(StrictModel):
    """Accepts a cancellation request for a fulfillment order, confirming that the fulfillment service should cancel the specified order. Optionally include a reason message for the acceptance."""
    path: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath
    query: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_order_cancellation_request_2020_04
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which you are rejecting the cancellation request.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining why the cancellation request is being rejected. This reason will be communicated to the fulfillment service.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest(StrictModel):
    """Rejects a cancellation request that was sent to a fulfillment service for a specific fulfillment order. Use this when you need to decline a cancellation and optionally provide a reason to the fulfillment service."""
    path: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath
    query: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery | None = None

# Operation: close_fulfillment_order_2020_04
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to close.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional reason or note explaining why the fulfillment order is being marked as incomplete.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest(StrictModel):
    """Marks an in-progress fulfillment order as incomplete, indicating the fulfillment service cannot ship remaining items and is closing the order."""
    path: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath
    query: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery | None = None

# Operation: send_fulfillment_request_202004
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to request fulfillment for.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message to include with the fulfillment request, such as special instructions or notes for the fulfillment service.")
    fulfillment_order_line_items: Any | None = Field(default=None, description="An optional array of fulfillment order line items to request for fulfillment. If omitted, all line items in the fulfillment order will be requested.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest(StrictModel):
    """Sends a fulfillment request to the fulfillment service for a specific fulfillment order, optionally specifying which line items to fulfill and including an optional message."""
    path: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath
    query: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery | None = None

# Operation: accept_fulfillment_request_2020_04
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request is being accepted.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for accepting the fulfillment request.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest(StrictModel):
    """Accepts a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, optionally providing a reason for acceptance."""
    path: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath
    query: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_request_202004
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request should be rejected.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for rejecting the fulfillment request.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest(StrictModel):
    """Rejects a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, optionally providing a reason for the rejection."""
    path: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath
    query: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery | None = None

# Operation: list_locations_for_fulfillment_order_move_2020_04
class Deprecated202004GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to retrieve available move destinations.")
class Deprecated202004GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest(StrictModel):
    """Retrieves an alphabetically sorted list of locations where a fulfillment order can be moved. Use this to determine valid destination locations before initiating a fulfillment order transfer."""
    path: Deprecated202004GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath

# Operation: move_fulfillment_order_legacy
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to be moved.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequestQuery(StrictModel):
    new_location_id: Any | None = Field(default=None, description="The unique identifier of the destination location where the fulfillment order will be transferred. Must be a merchant-managed location.")
class Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequest(StrictModel):
    """Relocates a fulfillment order to a different merchant-managed location, enabling inventory redistribution across fulfillment centers."""
    path: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequestPath
    query: Deprecated202004CreateFulfillmentOrdersParamFulfillmentOrderIdMoveRequestQuery | None = None

# Operation: delete_fulfillment_service_202004
class Deprecated202004DeleteFulfillmentServicesParamFulfillmentServiceIdRequestPath(StrictModel):
    fulfillment_service_id: str = Field(default=..., description="The unique identifier of the fulfillment service to delete. This ID is required to specify which fulfillment service should be removed.")
class Deprecated202004DeleteFulfillmentServicesParamFulfillmentServiceIdRequest(StrictModel):
    """Permanently delete a fulfillment service from your Shopify store. This operation removes the fulfillment service and its associated configuration."""
    path: Deprecated202004DeleteFulfillmentServicesParamFulfillmentServiceIdRequestPath

# Operation: cancel_fulfillment_202004
class Deprecated202004CreateFulfillmentsParamFulfillmentIdCancelRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to cancel. This ID references a specific fulfillment order that has been previously created.")
class Deprecated202004CreateFulfillmentsParamFulfillmentIdCancelRequest(StrictModel):
    """Cancels an existing fulfillment order. This operation marks the specified fulfillment as cancelled in the system."""
    path: Deprecated202004CreateFulfillmentsParamFulfillmentIdCancelRequestPath

# Operation: update_fulfillment_tracking_2020_04
class Deprecated202004CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment whose tracking information should be updated.")
class Deprecated202004CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest(StrictModel):
    """Updates the tracking information for a fulfillment, allowing you to modify shipment tracking details after the fulfillment has been created."""
    path: Deprecated202004CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath

# Operation: list_gift_cards_2020_04
class Deprecated202004GetGiftCardsRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter results to gift cards with a specific status: enabled to show only active gift cards, or disabled to show only inactive gift cards.")
    limit: Any | None = Field(default=None, description="Maximum number of gift cards to return per request, between 1 and 250 (defaults to 50).")
class Deprecated202004GetGiftCardsRequest(StrictModel):
    """Retrieves a paginated list of gift cards, optionally filtered by status. Results are paginated using link headers in the response rather than page parameters."""
    query: Deprecated202004GetGiftCardsRequestQuery | None = None

# Operation: count_gift_cards_v202004
class Deprecated202004GetGiftCardsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count to only include gift cards with a specific status: enabled for active gift cards, or disabled for inactive gift cards. Omit to count all gift cards regardless of status.")
class Deprecated202004GetGiftCardsCountRequest(StrictModel):
    """Retrieves the total count of gift cards, optionally filtered by their enabled or disabled status."""
    query: Deprecated202004GetGiftCardsCountRequestQuery | None = None

# Operation: search_gift_cards_202004
class Deprecated202004GetGiftCardsSearchRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="The field and direction to sort results by. Defaults to most recently disabled gift cards first. Common fields include created_at, updated_at, disabled_at, balance, initial_value, amount_spent, email, and last_characters.")
    query: Any | None = Field(default=None, description="The search query text to match against indexed gift card fields such as email, balance, or last characters.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 results.")
class Deprecated202004GetGiftCardsSearchRequest(StrictModel):
    """Search for gift cards using indexed fields like balance, email, or creation date. Results are paginated and returned via link headers."""
    query: Deprecated202004GetGiftCardsSearchRequestQuery | None = None

# Operation: update_gift_card_202004
class Deprecated202004UpdateGiftCardsParamGiftCardIdRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to update.")
class Deprecated202004UpdateGiftCardsParamGiftCardIdRequest(StrictModel):
    """Update an existing gift card's expiry date, note, or template suffix. Note that the gift card's balance cannot be modified through the API."""
    path: Deprecated202004UpdateGiftCardsParamGiftCardIdRequestPath

# Operation: disable_gift_card_202004
class Deprecated202004CreateGiftCardsParamGiftCardIdDisableRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to disable.")
class Deprecated202004CreateGiftCardsParamGiftCardIdDisableRequest(StrictModel):
    """Permanently disables a gift card, preventing it from being used for future transactions. This action cannot be reversed."""
    path: Deprecated202004CreateGiftCardsParamGiftCardIdDisableRequestPath

# Operation: list_inventory_items_202004
class Deprecated202004GetInventoryItemsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of inventory items to return per request, between 1 and 250 items (defaults to 50).")
    ids: int | None = Field(default=None, description="Filter results to specific inventory items by their numeric IDs. Provide one or more comma-separated integer values.")
class Deprecated202004GetInventoryItemsRequest(StrictModel):
    """Retrieves a paginated list of inventory items. Uses cursor-based pagination via response header links; the page parameter is not supported."""
    query: Deprecated202004GetInventoryItemsRequestQuery | None = None

# Operation: update_inventory_item_legacy_202004
class Deprecated202004UpdateInventoryItemsParamInventoryItemIdRequestPath(StrictModel):
    inventory_item_id: str = Field(default=..., description="The unique identifier of the inventory item to update. This ID is required to specify which inventory item should be modified.")
class Deprecated202004UpdateInventoryItemsParamInventoryItemIdRequest(StrictModel):
    """Updates an existing inventory item in your store's inventory system. Use this to modify inventory item properties such as tracked status, cost, and other item-level settings."""
    path: Deprecated202004UpdateInventoryItemsParamInventoryItemIdRequestPath

# Operation: list_inventory_levels_202004
class Deprecated202004GetInventoryLevelsRequestQuery(StrictModel):
    inventory_item_ids: Any | None = Field(default=None, description="Comma-separated list of inventory item IDs to filter results. Maximum of 50 IDs per request.")
    location_ids: Any | None = Field(default=None, description="Comma-separated list of location IDs to filter results. Maximum of 50 IDs per request. Use the Location resource to find location IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request. Defaults to 50 if not specified, with a maximum of 250.")
class Deprecated202004GetInventoryLevelsRequest(StrictModel):
    """Retrieves inventory levels across locations and inventory items. You must filter by at least one inventory item ID or location ID to retrieve results."""
    query: Deprecated202004GetInventoryLevelsRequestQuery | None = None

# Operation: delete_inventory_level_202004
class Deprecated202004DeleteInventoryLevelsRequestQuery(StrictModel):
    inventory_item_id: int | None = Field(default=None, description="The unique identifier of the inventory item whose level should be deleted.")
    location_id: int | None = Field(default=None, description="The unique identifier of the location from which the inventory item should be removed.")
class Deprecated202004DeleteInventoryLevelsRequest(StrictModel):
    """Removes an inventory level for a specific inventory item at a location. This operation disconnects the inventory item from that location; note that every inventory item must maintain at least one inventory level, so you must connect the item to another location before deleting its last level."""
    query: Deprecated202004DeleteInventoryLevelsRequestQuery | None = None

# Operation: get_location_202004
class Deprecated202004GetLocationsParamLocationIdRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location to retrieve.")
class Deprecated202004GetLocationsParamLocationIdRequest(StrictModel):
    """Retrieves a single location by its ID from the Shopify inventory system. Use this to fetch detailed information about a specific store location."""
    path: Deprecated202004GetLocationsParamLocationIdRequestPath

# Operation: list_inventory_levels_for_location_202004
class Deprecated202004GetLocationsParamLocationIdInventoryLevelsRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location for which to retrieve inventory levels.")
class Deprecated202004GetLocationsParamLocationIdInventoryLevelsRequest(StrictModel):
    """Retrieves all inventory levels for a specific location. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""
    path: Deprecated202004GetLocationsParamLocationIdInventoryLevelsRequestPath

# Operation: list_orders_v202004
class Deprecated202004GetOrdersRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only orders with the specified IDs, provided as a comma-separated list.")
    limit: Any | None = Field(default=None, description="Maximum number of orders to return per page, between 1 and 250 (defaults to 50).")
    processed_at_min: Any | None = Field(default=None, description="Show only orders processed at or after this date, specified in ISO 8601 format with timezone.")
    processed_at_max: Any | None = Field(default=None, description="Show only orders processed at or before this date, specified in ISO 8601 format with timezone.")
    attribution_app_id: Any | None = Field(default=None, description="Filter orders by the app that created them, specified by app ID. Use 'current' to show orders for the app making the request.")
    status: Any | None = Field(default=None, description="Filter orders by their fulfillment state: open (default), closed, cancelled, or any (including archived orders).")
    financial_status: Any | None = Field(default=None, description="Filter orders by their payment state: any (default), authorized, pending, paid, partially_paid, refunded, voided, partially_refunded, or unpaid (authorized and partially paid combined).")
    fulfillment_status: Any | None = Field(default=None, description="Filter orders by their shipment state: any (default), shipped (fully fulfilled), partial (partially shipped), unshipped (not yet shipped), or unfulfilled (unshipped or partially shipped combined).")
class Deprecated202004GetOrdersRequest(StrictModel):
    """Retrieves a paginated list of orders with filtering options by status, financial state, fulfillment state, and other criteria. Results are paginated using link headers in the response."""
    query: Deprecated202004GetOrdersRequestQuery | None = None

# Operation: get_orders_count_202004
class Deprecated202004GetOrdersCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter orders by their fulfillment state. Defaults to 'open' if not specified. Use 'open' for unfulfilled orders, 'closed' for completed orders, or 'any' to count all orders regardless of status.")
    financial_status: Any | None = Field(default=None, description="Filter orders by their payment state. Defaults to 'any' if not specified. Valid states include 'authorized', 'pending', 'paid', 'refunded', 'voided', or 'any' to include all payment statuses.")
    fulfillment_status: Any | None = Field(default=None, description="Filter orders by their shipment state. Defaults to 'any' if not specified. Use 'shipped' for fully delivered orders, 'partial' for partially shipped, 'unshipped' for orders not yet sent, 'unfulfilled' for orders with no or partial shipments, or 'any' for all fulfillment states.")
class Deprecated202004GetOrdersCountRequest(StrictModel):
    """Retrieves the count of orders filtered by status, financial status, and fulfillment status. Useful for obtaining order statistics without fetching full order details."""
    query: Deprecated202004GetOrdersCountRequestQuery | None = None

# Operation: get_order
class Deprecated202004GetOrdersParamOrderIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to retrieve.")
class Deprecated202004GetOrdersParamOrderIdRequest(StrictModel):
    """Retrieves the details of a specific order by its ID. Use this to fetch complete order information including items, customer details, and fulfillment status."""
    path: Deprecated202004GetOrdersParamOrderIdRequestPath

# Operation: update_order_v2020_04
class Deprecated202004UpdateOrdersParamOrderIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to update. This is a required string value that specifies which order will be modified.")
class Deprecated202004UpdateOrdersParamOrderIdRequest(StrictModel):
    """Updates an existing order in Shopify. Use this operation to modify order details such as status, customer information, or other order attributes."""
    path: Deprecated202004UpdateOrdersParamOrderIdRequestPath

# Operation: delete_order_v2
class Deprecated202004DeleteOrdersParamOrderIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to delete. This is a required numeric ID that identifies which order should be removed.")
class Deprecated202004DeleteOrdersParamOrderIdRequest(StrictModel):
    """Permanently deletes an order from the store. Note that orders connected to online payment gateways cannot be deleted due to payment processing requirements."""
    path: Deprecated202004DeleteOrdersParamOrderIdRequestPath

# Operation: cancel_order_v2
class Deprecated202004CreateOrdersParamOrderIdCancelRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to cancel.")
class Deprecated202004CreateOrdersParamOrderIdCancelRequestQuery(StrictModel):
    amount: Any | None = Field(default=None, description="The monetary amount to refund. When provided, Shopify attempts to void or refund the payment based on its current status. For manual gateway transactions, refunds are recorded in Shopify but the customer must be refunded separately.")
    currency: Any | None = Field(default=None, description="The currency code for the refund amount. Required for orders with multiple currencies whenever the amount parameter is provided.")
    reason: Any | None = Field(default=None, description="The reason for cancellation. Valid options are: customer, inventory, fraud, declined, or other. Defaults to other if not specified.")
    email: Any | None = Field(default=None, description="Whether to send a cancellation notification email to the customer. Defaults to false if not specified.")
    refund: Any | None = Field(default=None, description="Refund transaction details for complex refund scenarios. Use this for advanced refund operations beyond simple amount-based refunds. See the Refund API documentation for structure details.")
class Deprecated202004CreateOrdersParamOrderIdCancelRequest(StrictModel):
    """Cancels an order and optionally processes a refund. Orders with fulfillment objects cannot be canceled. For multi-currency orders, the currency property is required whenever an amount is specified."""
    path: Deprecated202004CreateOrdersParamOrderIdCancelRequestPath
    query: Deprecated202004CreateOrdersParamOrderIdCancelRequestQuery | None = None

# Operation: close_order_v2
class Deprecated202004CreateOrdersParamOrderIdCloseRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to close.")
class Deprecated202004CreateOrdersParamOrderIdCloseRequest(StrictModel):
    """Closes an order, preventing further modifications. This operation marks the order as closed in the system."""
    path: Deprecated202004CreateOrdersParamOrderIdCloseRequestPath

# Operation: list_fulfillment_orders_for_order_2020_04
class Deprecated202004GetOrdersParamOrderIdFulfillmentOrdersRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve fulfillment orders.")
class Deprecated202004GetOrdersParamOrderIdFulfillmentOrdersRequest(StrictModel):
    """Retrieves all fulfillment orders associated with a specific order. Fulfillment orders represent the items in an order that need to be fulfilled."""
    path: Deprecated202004GetOrdersParamOrderIdFulfillmentOrdersRequestPath

# Operation: list_fulfillments_for_order_v202004
class Deprecated202004GetOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve fulfillments.")
class Deprecated202004GetOrdersParamOrderIdFulfillmentsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of fulfillments to return per request, between 1 and 250 (defaults to 50).")
class Deprecated202004GetOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Retrieves all fulfillments associated with a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the limit parameter."""
    path: Deprecated202004GetOrdersParamOrderIdFulfillmentsRequestPath
    query: Deprecated202004GetOrdersParamOrderIdFulfillmentsRequestQuery | None = None

# Operation: create_fulfillment_for_order_legacy_202004
class Deprecated202004CreateOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the fulfillment. Required to route the request to the correct order.")
class Deprecated202004CreateOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Create a fulfillment for specified line items in an order. The fulfillment status depends on the fulfillment service type: manual/custom services set status immediately, while external services queue the fulfillment with pending status until processed. If no line items are specified, all unfulfilled and partially fulfilled items are fulfilled."""
    path: Deprecated202004CreateOrdersParamOrderIdFulfillmentsRequestPath

# Operation: get_fulfillment_count_for_order_2020_04
class Deprecated202004GetOrdersParamOrderIdFulfillmentsCountRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve the fulfillment count.")
class Deprecated202004GetOrdersParamOrderIdFulfillmentsCountRequest(StrictModel):
    """Retrieves the total count of fulfillments associated with a specific order. Useful for understanding fulfillment status and logistics tracking without fetching full fulfillment details."""
    path: Deprecated202004GetOrdersParamOrderIdFulfillmentsCountRequestPath

# Operation: get_fulfillment_202004
class Deprecated202004GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to retrieve.")
class Deprecated202004GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Retrieve detailed information about a specific fulfillment for an order. This operation returns fulfillment status, tracking information, and line items included in the shipment."""
    path: Deprecated202004GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: update_fulfillment_202004
class Deprecated202004UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to update.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to update.")
class Deprecated202004UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Update fulfillment details for a specific order, such as tracking information or fulfillment status."""
    path: Deprecated202004UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: complete_fulfillment_2020_04
class Deprecated202004CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to be completed.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to mark as complete.")
class Deprecated202004CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest(StrictModel):
    """Mark a fulfillment as complete, indicating that all items in the fulfillment have been shipped and the order fulfillment process is finished."""
    path: Deprecated202004CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath

# Operation: list_fulfillment_events_202004
class Deprecated202004GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment within the specified order.")
class Deprecated202004GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest(StrictModel):
    """Retrieves all events associated with a specific fulfillment for an order. Events track status changes and milestones throughout the fulfillment lifecycle."""
    path: Deprecated202004GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath

# Operation: open_fulfillment_202004
class Deprecated202004CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to be opened.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to mark as open.")
class Deprecated202004CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequest(StrictModel):
    """Mark a fulfillment as open, allowing it to receive additional items or changes. This operation transitions a fulfillment from a closed state back to an open state."""
    path: Deprecated202004CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequestPath

# Operation: reopen_order_202004
class Deprecated202004CreateOrdersParamOrderIdOpenRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order to re-open. This must be a valid order ID from your Shopify store.")
class Deprecated202004CreateOrdersParamOrderIdOpenRequest(StrictModel):
    """Re-opens a previously closed order, allowing it to be modified and processed again. This operation restores a closed order to an active state."""
    path: Deprecated202004CreateOrdersParamOrderIdOpenRequestPath

# Operation: list_order_refunds_202004
class Deprecated202004GetOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve refunds.")
class Deprecated202004GetOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of refunds to return per request, between 1 and 250 (defaults to 50).")
    in_shop_currency: Any | None = Field(default=None, description="When true, displays refund amounts in the shop's currency for the underlying transaction; defaults to false.")
class Deprecated202004GetOrdersParamOrderIdRefundsRequest(StrictModel):
    """Retrieves a list of refunds for a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    path: Deprecated202004GetOrdersParamOrderIdRefundsRequestPath
    query: Deprecated202004GetOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: create_order_refund_202004
class Deprecated202004CreateOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create a refund.")
class Deprecated202004CreateOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    notify: Any | None = Field(default=None, description="Whether to send a refund notification email to the customer.")
    note: Any | None = Field(default=None, description="An optional note to attach to the refund for internal reference.")
    discrepancy_reason: Any | None = Field(default=None, description="An optional reason explaining any discrepancy between calculated and actual refund amounts. Valid values are: restock, damage, customer, or other.")
    shipping: Any | None = Field(default=None, description="Shipping refund details. Specify either full_refund to refund all remaining shipping, or amount to refund a specific shipping amount (takes precedence over full_refund).")
    refund_line_items: Any | None = Field(default=None, description="A list of line items to refund, each with the line item ID, quantity to refund, restock type (no_restock, cancel, or return), and location ID for restocking (required for cancel and return types).")
    transactions: Any | None = Field(default=None, description="A list of transactions to process as refunds. Should be obtained from the calculate endpoint for accuracy.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required for multi-currency orders when an amount property is provided.")
class Deprecated202004CreateOrdersParamOrderIdRefundsRequest(StrictModel):
    """Creates a refund for an order. Use the calculate endpoint first to determine the correct transactions to submit. For multi-currency orders, the currency property is required whenever an amount is specified."""
    path: Deprecated202004CreateOrdersParamOrderIdRefundsRequestPath
    query: Deprecated202004CreateOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: calculate_order_refund_2020_04
class Deprecated202004CreateOrdersParamOrderIdRefundsCalculateRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to calculate the refund.")
class Deprecated202004CreateOrdersParamOrderIdRefundsCalculateRequestQuery(StrictModel):
    shipping: Any | None = Field(default=None, description="Shipping refund configuration. Specify either full_refund to refund all remaining shipping costs, or amount to refund a specific shipping amount (takes precedence over full_refund). Required if providing a shipping amount for multi-currency orders.")
    refund_line_items: Any | None = Field(default=None, description="List of line items to refund, each specifying the line item ID, quantity to refund, and restock instructions. Restock type determines inventory impact: no_restock (no inventory change), cancel (items not yet fulfilled, reduces fulfillable units), or return (items already delivered, no change to fulfillable units). Optionally specify location_id for restocking; if omitted for cancel/return types, the endpoint will suggest a suitable location.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required for multi-currency orders whenever a shipping amount is specified.")
class Deprecated202004CreateOrdersParamOrderIdRefundsCalculateRequest(StrictModel):
    """Calculates refund transactions for an order based on specified line items, quantities, restock instructions, and shipping costs. Use this endpoint to generate accurate refund details before creating an actual refund; the response provides suggested transactions that must be converted to actual refunds."""
    path: Deprecated202004CreateOrdersParamOrderIdRefundsCalculateRequestPath
    query: Deprecated202004CreateOrdersParamOrderIdRefundsCalculateRequestQuery | None = None

# Operation: get_refund_for_order_202004
class Deprecated202004GetOrdersParamOrderIdRefundsParamRefundIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the refund.")
    refund_id: str = Field(default=..., description="The unique identifier of the refund to retrieve.")
class Deprecated202004GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery(StrictModel):
    in_shop_currency: Any | None = Field(default=None, description="When enabled, displays all monetary amounts in the shop's native currency rather than the transaction currency. Defaults to false.")
class Deprecated202004GetOrdersParamOrderIdRefundsParamRefundIdRequest(StrictModel):
    """Retrieves the details of a specific refund associated with an order. Use this to view refund information including amounts, line items, and status."""
    path: Deprecated202004GetOrdersParamOrderIdRefundsParamRefundIdRequestPath
    query: Deprecated202004GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery | None = None

# Operation: list_order_risks_2020_04
class Deprecated202004GetOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve associated risks.")
class Deprecated202004GetOrdersParamOrderIdRisksRequest(StrictModel):
    """Retrieves all fraud and risk assessments associated with a specific order. This endpoint uses cursor-based pagination via response headers rather than page parameters."""
    path: Deprecated202004GetOrdersParamOrderIdRisksRequestPath

# Operation: create_order_risk_202004
class Deprecated202004CreateOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the risk record.")
class Deprecated202004CreateOrdersParamOrderIdRisksRequest(StrictModel):
    """Creates a risk assessment record for a specific order. Use this to flag potential issues or concerns associated with an order that may require review or action."""
    path: Deprecated202004CreateOrdersParamOrderIdRisksRequestPath

# Operation: get_order_risk_202004
class Deprecated202004GetOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk assessment.")
    risk_id: str = Field(default=..., description="The unique identifier of the specific risk assessment to retrieve.")
class Deprecated202004GetOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Retrieves a specific risk assessment associated with an order. Use this to fetch details about a fraud or security risk that has been flagged for a particular order."""
    path: Deprecated202004GetOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: update_order_risk_202004
class Deprecated202004UpdateOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to be updated.")
    risk_id: str = Field(default=..., description="The unique identifier of the order risk to be updated.")
class Deprecated202004UpdateOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Updates an existing order risk for a specific order. Note that you cannot modify an order risk that was created by another application."""
    path: Deprecated202004UpdateOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: delete_order_risk_202004
class Deprecated202004DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to be deleted.")
    risk_id: str = Field(default=..., description="The unique identifier of the order risk to be deleted.")
class Deprecated202004DeleteOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Deletes a specific order risk associated with an order. Note that you cannot delete an order risk that was created by another application."""
    path: Deprecated202004DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: create_discount_codes_batch_202004
class Deprecated202004CreatePriceRulesParamPriceRuleIdBatchRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which discount codes will be created.")
class Deprecated202004CreatePriceRulesParamPriceRuleIdBatchRequest(StrictModel):
    """Asynchronously creates up to 100 discount codes for a price rule in a single batch job. Returns a discount code creation job object that can be monitored for completion status, including counts of successful and failed code creations."""
    path: Deprecated202004CreatePriceRulesParamPriceRuleIdBatchRequestPath

# Operation: get_discount_code_batch_202004
class Deprecated202004GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch.")
    batch_id: str = Field(default=..., description="The unique identifier of the specific batch job to retrieve status and results for.")
class Deprecated202004GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest(StrictModel):
    """Retrieves the status and details of a discount code creation job batch for a specific price rule. Use this to check the progress and results of bulk discount code generation."""
    path: Deprecated202004GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath

# Operation: list_discount_codes_for_batch_202004
class Deprecated202004GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch.")
    batch_id: str = Field(default=..., description="The unique identifier of the discount code creation batch job to retrieve codes from.")
class Deprecated202004GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest(StrictModel):
    """Retrieves all discount codes generated from a specific discount code creation batch job. Results include successfully created codes with populated IDs and codes that failed with error details."""
    path: Deprecated202004GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath

# Operation: list_discount_codes_for_price_rule_2020_04
class Deprecated202004GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which to retrieve associated discount codes.")
class Deprecated202004GetPriceRulesParamPriceRuleIdDiscountCodesRequest(StrictModel):
    """Retrieve all discount codes associated with a specific price rule. Results are paginated using link-based navigation provided in response headers."""
    path: Deprecated202004GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath

# Operation: get_discount_code_for_price_rule_v2
class Deprecated202004GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to retrieve.")
class Deprecated202004GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Retrieves a specific discount code associated with a price rule. Use this to fetch details about an individual discount code within a price rule configuration."""
    path: Deprecated202004GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: update_discount_code_202004
class Deprecated202004UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code being updated.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to update.")
class Deprecated202004UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Updates an existing discount code associated with a price rule. Modify discount code properties such as code value, usage limits, and other settings."""
    path: Deprecated202004UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: delete_discount_code_202004
class Deprecated202004DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code to be deleted.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to be deleted.")
class Deprecated202004DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Permanently deletes a specific discount code associated with a price rule. This action cannot be undone."""
    path: Deprecated202004DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: delete_product_listing_v2020_04
class Deprecated202004DeleteProductListingsParamProductListingIdRequestPath(StrictModel):
    product_listing_id: str = Field(default=..., description="The unique identifier of the product listing to delete. This ID represents the specific product-to-channel relationship being removed.")
class Deprecated202004DeleteProductListingsParamProductListingIdRequest(StrictModel):
    """Remove a product listing to unpublish a product from your sales channel app. This operation deletes the listing relationship without affecting the product itself."""
    path: Deprecated202004DeleteProductListingsParamProductListingIdRequestPath

# Operation: list_products_2020_04
class Deprecated202004GetProductsRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only include products with IDs matching this comma-separated list of product identifiers.")
    limit: Any | None = Field(default=None, description="Maximum number of products to return per page, between 1 and 250 (defaults to 50).")
    title: Any | None = Field(default=None, description="Filter results to only include products whose title contains this text.")
    vendor: Any | None = Field(default=None, description="Filter results to only include products from this vendor.")
    handle: Any | None = Field(default=None, description="Filter results to only include products with this handle (URL-friendly identifier).")
    product_type: Any | None = Field(default=None, description="Filter results to only include products of this type.")
    status: Any | None = Field(default=None, description="Filter results by product status: active (default), archived, or draft.")
    collection_id: Any | None = Field(default=None, description="Filter results to only include products assigned to this collection ID.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: published, unpublished, or any (default shows all).")
    presentment_currencies: Any | None = Field(default=None, description="Return presentment prices in only these currencies, specified as a comma-separated list of ISO 4217 currency codes.")
class Deprecated202004GetProductsRequest(StrictModel):
    """Retrieves a paginated list of products from the store, with support for filtering by various attributes and sorting options. Uses cursor-based pagination via response headers rather than page parameters."""
    query: Deprecated202004GetProductsRequestQuery | None = None

# Operation: get_products_count_202004
class Deprecated202004GetProductsCountRequestQuery(StrictModel):
    vendor: Any | None = Field(default=None, description="Filter the count to include only products from a specific vendor.")
    product_type: Any | None = Field(default=None, description="Filter the count to include only products of a specific product type.")
    collection_id: Any | None = Field(default=None, description="Filter the count to include only products belonging to a specific collection by its ID.")
    published_status: Any | None = Field(default=None, description="Filter products by their publication status: use 'published' for only published products, 'unpublished' for only unpublished products, or 'any' to include all products regardless of status (default is 'any').")
class Deprecated202004GetProductsCountRequest(StrictModel):
    """Retrieves the total count of products in the store, with optional filtering by vendor, product type, collection, or published status."""
    query: Deprecated202004GetProductsCountRequestQuery | None = None

# Operation: get_product_202004
class Deprecated202004GetProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to retrieve.")
class Deprecated202004GetProductsParamProductIdRequest(StrictModel):
    """Retrieves detailed information for a single product by its ID from the Shopify store."""
    path: Deprecated202004GetProductsParamProductIdRequestPath

# Operation: delete_product_202004
class Deprecated202004DeleteProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to delete. This is a numeric ID assigned by Shopify.")
class Deprecated202004DeleteProductsParamProductIdRequest(StrictModel):
    """Permanently deletes a product from the store. This action cannot be undone and will remove the product and all associated data."""
    path: Deprecated202004DeleteProductsParamProductIdRequestPath

# Operation: list_product_images_202004
class Deprecated202004GetProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product whose images you want to retrieve.")
class Deprecated202004GetProductsParamProductIdImagesRequest(StrictModel):
    """Retrieve all images associated with a specific product. Returns a collection of image resources for the given product."""
    path: Deprecated202004GetProductsParamProductIdImagesRequestPath

# Operation: create_product_image_202004
class Deprecated202004CreateProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to which the image will be added.")
class Deprecated202004CreateProductsParamProductIdImagesRequest(StrictModel):
    """Create a new image for a specific product. The image will be associated with the product and can be used to display product visuals in the storefront."""
    path: Deprecated202004CreateProductsParamProductIdImagesRequestPath

# Operation: get_product_images_count_202004
class Deprecated202004GetProductsParamProductIdImagesCountRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product for which to retrieve the image count.")
class Deprecated202004GetProductsParamProductIdImagesCountRequest(StrictModel):
    """Retrieve the total count of images associated with a specific product. Useful for determining how many product images exist without fetching the full image data."""
    path: Deprecated202004GetProductsParamProductIdImagesCountRequestPath

# Operation: update_product_image_202004
class Deprecated202004UpdateProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product that contains the image to be updated.")
    image_id: str = Field(default=..., description="The unique identifier of the image within the product to be updated.")
class Deprecated202004UpdateProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Update the properties of an existing product image, such as alt text, position, or other image metadata."""
    path: Deprecated202004UpdateProductsParamProductIdImagesParamImageIdRequestPath

# Operation: delete_product_image_202004
class Deprecated202004DeleteProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product containing the image to delete.")
    image_id: str = Field(default=..., description="The unique identifier of the image to delete from the product.")
class Deprecated202004DeleteProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Delete a specific image associated with a product. This removes the image from the product's image gallery."""
    path: Deprecated202004DeleteProductsParamProductIdImagesParamImageIdRequestPath

# Operation: get_recurring_application_charge_202004
class Deprecated202004GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to retrieve.")
class Deprecated202004GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(StrictModel):
    """Retrieves the details of a single recurring application charge by its ID. Use this to check the status, terms, and billing information for a specific recurring charge."""
    path: Deprecated202004GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath

# Operation: delete_recurring_application_charge_2020_04
class Deprecated202004DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to cancel. This ID is returned when the charge is created.")
class Deprecated202004DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(StrictModel):
    """Cancels an active recurring application charge for the app. This prevents future billing cycles for the specified charge."""
    path: Deprecated202004DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath

# Operation: update_recurring_application_charge_capped_amount_2020_04
class Deprecated202004UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to update.")
class Deprecated202004UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery(StrictModel):
    recurring_application_charge_capped_amount: int | None = Field(default=None, validation_alias="recurring_application_charge[capped_amount]", serialization_alias="recurring_application_charge[capped_amount]", description="The new capped amount limit for the recurring charge, specified as a whole number representing the maximum billable amount.")
class Deprecated202004UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest(StrictModel):
    """Updates the capped amount limit for an active recurring application charge. This allows you to modify the maximum amount that can be charged to the merchant during the billing cycle."""
    path: Deprecated202004UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath
    query: Deprecated202004UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery | None = None

# Operation: create_usage_charge_for_recurring_application_charge_202004
class Deprecated202004CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge for which to create the usage charge.")
class Deprecated202004CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Creates a usage charge against an existing recurring application charge. Usage charges allow you to bill merchants for variable usage on top of their recurring subscription."""
    path: Deprecated202004CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath

# Operation: list_redirects_202004
class Deprecated202004GetRedirectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of redirects to return per request, between 1 and 250 (defaults to 50).")
    path: Any | None = Field(default=None, description="Filter results to show only redirects with a specific source path.")
    target: Any | None = Field(default=None, description="Filter results to show only redirects pointing to a specific target URL.")
class Deprecated202004GetRedirectsRequest(StrictModel):
    """Retrieves a list of URL redirects configured in the online store. Results are paginated using link headers in the response."""
    query: Deprecated202004GetRedirectsRequestQuery | None = None

# Operation: get_redirects_count_2020_04
class Deprecated202004GetRedirectsCountRequestQuery(StrictModel):
    path: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific path value.")
    target: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific target URL.")
class Deprecated202004GetRedirectsCountRequest(StrictModel):
    """Retrieves the total count of URL redirects in the store, with optional filtering by path or target URL."""
    query: Deprecated202004GetRedirectsCountRequestQuery | None = None

# Operation: get_redirect_202004
class Deprecated202004GetRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to retrieve.")
class Deprecated202004GetRedirectsParamRedirectIdRequest(StrictModel):
    """Retrieves a single redirect by its ID from the Shopify online store. Use this to fetch details about a specific URL redirect configuration."""
    path: Deprecated202004GetRedirectsParamRedirectIdRequestPath

# Operation: update_redirect_v202004
class Deprecated202004UpdateRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to update.")
class Deprecated202004UpdateRedirectsParamRedirectIdRequest(StrictModel):
    """Updates an existing redirect in the online store. Modify redirect settings such as the target path or status for a specific redirect by its ID."""
    path: Deprecated202004UpdateRedirectsParamRedirectIdRequestPath

# Operation: delete_redirect_v202004
class Deprecated202004DeleteRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to delete.")
class Deprecated202004DeleteRedirectsParamRedirectIdRequest(StrictModel):
    """Permanently deletes a redirect from the online store. This action cannot be undone."""
    path: Deprecated202004DeleteRedirectsParamRedirectIdRequestPath

# Operation: create_report_legacy_202004
class Deprecated202004CreateReportsRequestQuery(StrictModel):
    name: Any | None = Field(default=None, description="The display name for the report. Must be 255 characters or fewer.")
    shopify_ql: Any | None = Field(default=None, description="The ShopifyQL query string that defines what data the report will retrieve and analyze.")
class Deprecated202004CreateReportsRequest(StrictModel):
    """Creates a new custom report in the Shopify admin. Reports use ShopifyQL queries to analyze store data and can be referenced by name for future access."""
    query: Deprecated202004CreateReportsRequestQuery | None = None

# Operation: get_report_202004
class Deprecated202004GetReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to retrieve.")
class Deprecated202004GetReportsParamReportIdRequest(StrictModel):
    """Retrieves a single report that was created by your app. Use this to fetch details about a specific report by its ID."""
    path: Deprecated202004GetReportsParamReportIdRequestPath

# Operation: delete_report_202004
class Deprecated202004DeleteReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to delete. This ID must correspond to an existing report in your Shopify store.")
class Deprecated202004DeleteReportsParamReportIdRequest(StrictModel):
    """Permanently deletes a specific report from the Shopify admin. This action cannot be undone."""
    path: Deprecated202004DeleteReportsParamReportIdRequestPath

# Operation: list_shopify_payments_disputes_legacy
class Deprecated202004GetShopifyPaymentsDisputesRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter disputes by their current status (e.g., won, lost, under_review). Only disputes matching the specified status will be returned.")
    initiated_at: Any | None = Field(default=None, description="Filter disputes by their initiation date in ISO 8601 format. Only disputes initiated on the specified date will be returned.")
class Deprecated202004GetShopifyPaymentsDisputesRequest(StrictModel):
    """Retrieve all Shopify Payments disputes ordered by initiation date (most recent first). Results are paginated using link headers in the response."""
    query: Deprecated202004GetShopifyPaymentsDisputesRequestQuery | None = None

# Operation: list_shopify_payments_payouts_2020_04
class Deprecated202004GetShopifyPaymentsPayoutsRequestQuery(StrictModel):
    date_min: Any | None = Field(default=None, description="Filter payouts to include only those made on or after the specified date (inclusive). Use ISO 8601 format.")
    date_max: Any | None = Field(default=None, description="Filter payouts to include only those made on or before the specified date (inclusive). Use ISO 8601 format.")
    status: Any | None = Field(default=None, description="Filter payouts by their status (e.g., pending, completed, failed, cancelled). Only payouts matching the specified status will be returned.")
class Deprecated202004GetShopifyPaymentsPayoutsRequest(StrictModel):
    """Retrieves a list of all payouts from Shopify Payments, ordered by payout date with the most recent first. Results are paginated using link headers in the response."""
    query: Deprecated202004GetShopifyPaymentsPayoutsRequestQuery | None = None

# Operation: get_shopify_payments_payout_2020_04
class Deprecated202004GetShopifyPaymentsPayoutsParamPayoutIdRequestPath(StrictModel):
    payout_id: str = Field(default=..., description="The unique identifier of the payout to retrieve.")
class Deprecated202004GetShopifyPaymentsPayoutsParamPayoutIdRequest(StrictModel):
    """Retrieves details for a specific Shopify Payments payout by its unique identifier."""
    path: Deprecated202004GetShopifyPaymentsPayoutsParamPayoutIdRequestPath

# Operation: list_smart_collections_202004
class Deprecated202004GetSmartCollectionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of smart collections to return per request. Defaults to 50 and cannot exceed 250.")
    ids: Any | None = Field(default=None, description="Filter results to only smart collections with the specified IDs. Provide as a comma-separated list of numeric IDs.")
    title: Any | None = Field(default=None, description="Filter results to smart collections matching the exact title.")
    product_id: Any | None = Field(default=None, description="Filter results to only smart collections that contain the specified product ID.")
    handle: Any | None = Field(default=None, description="Filter results by the smart collection's URL handle.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for published collections only, 'unpublished' for unpublished collections only, or 'any' for all collections. Defaults to 'any'.")
class Deprecated202004GetSmartCollectionsRequest(StrictModel):
    """Retrieves a paginated list of smart collections from your store. Results are paginated using link headers in the response."""
    query: Deprecated202004GetSmartCollectionsRequestQuery | None = None

# Operation: count_smart_collections_202004
class Deprecated202004GetSmartCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter to smart collections with an exact matching title.")
    product_id: Any | None = Field(default=None, description="Filter to smart collections that contain the specified product ID.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for live collections, 'unpublished' for draft collections, or 'any' to include all collections regardless of status. Defaults to 'any'.")
class Deprecated202004GetSmartCollectionsCountRequest(StrictModel):
    """Retrieves the total count of smart collections in the store, with optional filtering by title, product inclusion, or published status."""
    query: Deprecated202004GetSmartCollectionsCountRequestQuery | None = None

# Operation: update_smart_collection_202004
class Deprecated202004UpdateSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to update. This ID is required to target the specific smart collection for modification.")
class Deprecated202004UpdateSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Updates an existing smart collection by its ID. Use this to modify smart collection properties such as title, rules, and other configuration settings."""
    path: Deprecated202004UpdateSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: delete_smart_collection_202004
class Deprecated202004DeleteSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to delete.")
class Deprecated202004DeleteSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Permanently removes a smart collection from the store. This action cannot be undone."""
    path: Deprecated202004DeleteSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: get_theme_202004
class Deprecated202004GetThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to retrieve.")
class Deprecated202004GetThemesParamThemeIdRequest(StrictModel):
    """Retrieves a single theme by its ID from the Shopify online store."""
    path: Deprecated202004GetThemesParamThemeIdRequestPath

# Operation: update_theme_archived
class Deprecated202004UpdateThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to update. This ID is returned when a theme is created and is required to target the specific theme for modification.")
class Deprecated202004UpdateThemesParamThemeIdRequest(StrictModel):
    """Updates the configuration and settings of an existing theme in the Shopify store. Use this to modify theme properties after creation."""
    path: Deprecated202004UpdateThemesParamThemeIdRequestPath

# Operation: delete_theme_2020_04
class Deprecated202004DeleteThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to delete.")
class Deprecated202004DeleteThemesParamThemeIdRequest(StrictModel):
    """Permanently deletes a theme from the Shopify store. This action cannot be undone."""
    path: Deprecated202004DeleteThemesParamThemeIdRequestPath

# Operation: delete_theme_asset_202004
class Deprecated202004DeleteThemesParamThemeIdAssetsRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme from which the asset will be deleted.")
class Deprecated202004DeleteThemesParamThemeIdAssetsRequestQuery(StrictModel):
    asset_key: str | None = Field(default=None, validation_alias="asset[key]", serialization_alias="asset[key]", description="The key (file path) of the asset to delete from the theme. This identifies which specific asset file to remove.")
class Deprecated202004DeleteThemesParamThemeIdAssetsRequest(StrictModel):
    """Removes a specific asset file from a Shopify theme. The asset is identified by its key within the theme."""
    path: Deprecated202004DeleteThemesParamThemeIdAssetsRequestPath
    query: Deprecated202004DeleteThemesParamThemeIdAssetsRequestQuery | None = None

# Operation: list_webhooks_legacy_202004
class Deprecated202004GetWebhooksRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter webhooks by the URI endpoint that receives POST requests. Only webhooks sending to this address will be returned.")
    limit: Any | None = Field(default=None, description="Maximum number of webhooks to return per request, between 1 and 250. Defaults to 50 if not specified.")
    topic: Any | None = Field(default=None, description="Filter webhooks by topic to show only subscriptions for specific events. Refer to the Shopify webhook topics documentation for valid values.")
class Deprecated202004GetWebhooksRequest(StrictModel):
    """Retrieves a list of webhook subscriptions configured for your Shopify store. Results are paginated using link headers in the response."""
    query: Deprecated202004GetWebhooksRequestQuery | None = None

# Operation: count_webhooks_202004
class Deprecated202004GetWebhooksCountRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter results to webhook subscriptions that deliver POST requests to this specific URI.")
    topic: Any | None = Field(default=None, description="Filter results to webhook subscriptions listening to a specific event topic. Refer to the webhook topic documentation for valid topic values.")
class Deprecated202004GetWebhooksCountRequest(StrictModel):
    """Retrieves the total count of webhook subscriptions configured in the Shopify store, with optional filtering by delivery address or event topic."""
    query: Deprecated202004GetWebhooksCountRequestQuery | None = None

# Operation: get_application_charge_202007
class Deprecated202007GetApplicationChargesParamApplicationChargeIdRequestPath(StrictModel):
    application_charge_id: str = Field(default=..., description="The unique identifier of the application charge to retrieve.")
class Deprecated202007GetApplicationChargesParamApplicationChargeIdRequest(StrictModel):
    """Retrieves the details of a specific application charge by its ID. Use this to fetch information about a charge created for your app."""
    path: Deprecated202007GetApplicationChargesParamApplicationChargeIdRequestPath

# Operation: list_articles_for_blog_v202007
class Deprecated202007GetBlogsParamBlogIdArticlesRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog from which to retrieve articles.")
class Deprecated202007GetBlogsParamBlogIdArticlesRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of articles to return per request, between 1 and 250 (defaults to 50).")
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: 'published' for published articles only, 'unpublished' for unpublished articles only, or 'any' for all articles regardless of status (defaults to 'any').")
    handle: Any | None = Field(default=None, description="Retrieve a single article by its URL-friendly handle identifier.")
    tag: Any | None = Field(default=None, description="Filter articles to only those tagged with a specific tag.")
    author: Any | None = Field(default=None, description="Filter articles to only those written by a specific author.")
class Deprecated202007GetBlogsParamBlogIdArticlesRequest(StrictModel):
    """Retrieves a paginated list of articles from a specific blog. Results are paginated using link headers in the response; use the provided links for navigation rather than the page parameter."""
    path: Deprecated202007GetBlogsParamBlogIdArticlesRequestPath
    query: Deprecated202007GetBlogsParamBlogIdArticlesRequestQuery | None = None

# Operation: create_article_for_blog_202007
class Deprecated202007CreateBlogsParamBlogIdArticlesRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog where the article will be created.")
class Deprecated202007CreateBlogsParamBlogIdArticlesRequest(StrictModel):
    """Creates a new article for a specified blog. The article will be added to the blog's collection of articles."""
    path: Deprecated202007CreateBlogsParamBlogIdArticlesRequestPath

# Operation: count_articles_in_blog_legacy
class Deprecated202007GetBlogsParamBlogIdArticlesCountRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog for which to count articles.")
class Deprecated202007GetBlogsParamBlogIdArticlesCountRequestQuery(StrictModel):
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: use 'published' to count only published articles, 'unpublished' to count only unpublished articles, or 'any' to count all articles regardless of status. Defaults to 'any' if not specified.")
class Deprecated202007GetBlogsParamBlogIdArticlesCountRequest(StrictModel):
    """Retrieves the total count of articles in a specific blog, with optional filtering by publication status."""
    path: Deprecated202007GetBlogsParamBlogIdArticlesCountRequestPath
    query: Deprecated202007GetBlogsParamBlogIdArticlesCountRequestQuery | None = None

# Operation: get_article_202007
class Deprecated202007GetBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article.")
    article_id: str = Field(default=..., description="The unique identifier of the article to retrieve.")
class Deprecated202007GetBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Retrieves a single article from a blog by its ID. Use this to fetch detailed information about a specific article including its content, metadata, and publishing status."""
    path: Deprecated202007GetBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: delete_article_202007
class Deprecated202007DeleteBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article to delete.")
    article_id: str = Field(default=..., description="The unique identifier of the article to delete.")
class Deprecated202007DeleteBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Permanently deletes an article from a blog. This action cannot be undone."""
    path: Deprecated202007DeleteBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: update_carrier_service_202007
class Deprecated202007UpdateCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to update.")
class Deprecated202007UpdateCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Updates an existing carrier service. Only the app that originally created the carrier service can modify it."""
    path: Deprecated202007UpdateCarrierServicesParamCarrierServiceIdRequestPath

# Operation: get_abandoned_checkouts_count_202007
class Deprecated202007GetCheckoutsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count by checkout status. Use 'open' to count only active abandoned checkouts or 'closed' to count only completed/closed abandoned checkouts. Defaults to 'open' if not specified.")
class Deprecated202007GetCheckoutsCountRequest(StrictModel):
    """Retrieves the count of abandoned checkouts from the past 90 days, optionally filtered by checkout status."""
    query: Deprecated202007GetCheckoutsCountRequestQuery | None = None

# Operation: list_shipping_rates_for_checkout_2020_07
class Deprecated202007GetCheckoutsParamTokenShippingRatesRequestPath(StrictModel):
    token: str = Field(default=..., description="The unique identifier for the checkout. This token is used to retrieve shipping rates specific to that checkout.")
class Deprecated202007GetCheckoutsParamTokenShippingRatesRequest(StrictModel):
    """Retrieves available shipping rates for a checkout. Poll this endpoint until rates become available, then use the returned rates to display updated pricing (subtotal, tax, total) or apply a rate by updating the checkout's shipping line."""
    path: Deprecated202007GetCheckoutsParamTokenShippingRatesRequestPath

# Operation: delete_collection_listing_202007
class Deprecated202007DeleteCollectionListingsParamCollectionListingIdRequestPath(StrictModel):
    collection_listing_id: str = Field(default=..., description="The unique identifier of the collection listing to delete.")
class Deprecated202007DeleteCollectionListingsParamCollectionListingIdRequest(StrictModel):
    """Remove a collection listing to unpublish a collection from your sales channel or app."""
    path: Deprecated202007DeleteCollectionListingsParamCollectionListingIdRequestPath

# Operation: list_product_ids_for_collection_listing
class Deprecated202007GetCollectionListingsParamCollectionListingIdProductIdsRequestPath(StrictModel):
    collection_listing_id: str = Field(default=..., description="The unique identifier for the collection listing whose published product IDs you want to retrieve.")
class Deprecated202007GetCollectionListingsParamCollectionListingIdProductIdsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of product IDs to return per request, ranging from 1 to 1000 (defaults to 50).")
class Deprecated202007GetCollectionListingsParamCollectionListingIdProductIdsRequest(StrictModel):
    """Retrieve the product IDs that are published to a specific collection listing. Results are paginated using link headers in the response."""
    path: Deprecated202007GetCollectionListingsParamCollectionListingIdProductIdsRequestPath
    query: Deprecated202007GetCollectionListingsParamCollectionListingIdProductIdsRequestQuery | None = None

# Operation: get_collection_202007
class Deprecated202007GetCollectionsParamCollectionIdRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection to retrieve.")
class Deprecated202007GetCollectionsParamCollectionIdRequest(StrictModel):
    """Retrieves the details of a single collection by its ID, including metadata such as name, description, and product associations."""
    path: Deprecated202007GetCollectionsParamCollectionIdRequestPath

# Operation: list_collection_products_202007
class Deprecated202007GetCollectionsParamCollectionIdProductsRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection whose products you want to retrieve.")
class Deprecated202007GetCollectionsParamCollectionIdProductsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of products to return per request, ranging from 1 to 250 products (defaults to 50 if not specified).")
class Deprecated202007GetCollectionsParamCollectionIdProductsRequest(StrictModel):
    """Retrieve products belonging to a specific collection, sorted according to the collection's configured sort order. Results are paginated using link-based navigation provided in response headers."""
    path: Deprecated202007GetCollectionsParamCollectionIdProductsRequestPath
    query: Deprecated202007GetCollectionsParamCollectionIdProductsRequestQuery | None = None

# Operation: list_collects_2020_07
class Deprecated202007GetCollectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, ranging from 1 to 250 items (defaults to 50).")
class Deprecated202007GetCollectsRequest(StrictModel):
    """Retrieves a list of collects (product-to-collection associations). Uses cursor-based pagination via response header links; the page parameter is not supported."""
    query: Deprecated202007GetCollectsRequestQuery | None = None

# Operation: get_collects_count_202007
class Deprecated202007GetCollectsCountRequestQuery(StrictModel):
    collection_id: int | None = Field(default=None, description="Filter the count to only include collects belonging to a specific collection. If omitted, returns the total count of all collects across the store.")
class Deprecated202007GetCollectsCountRequest(StrictModel):
    """Retrieves the total count of collects, optionally filtered by a specific collection. Useful for understanding the size of a collection or the total number of product-to-collection associations in the store."""
    query: Deprecated202007GetCollectsCountRequestQuery | None = None

# Operation: get_collect_202007
class Deprecated202007GetCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect resource to retrieve.")
class Deprecated202007GetCollectsParamCollectIdRequest(StrictModel):
    """Retrieves a specific product collection by its ID. Use this to fetch details about how a product is organized within a collection."""
    path: Deprecated202007GetCollectsParamCollectIdRequestPath

# Operation: remove_product_from_collection_2020_07
class Deprecated202007DeleteCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect relationship to remove. This ID represents the link between a product and a collection.")
class Deprecated202007DeleteCollectsParamCollectIdRequest(StrictModel):
    """Removes a product from a collection by deleting the collect relationship. This operation unlinks a product from a specific collection without affecting the product or collection itself."""
    path: Deprecated202007DeleteCollectsParamCollectIdRequestPath

# Operation: update_country_202007
class Deprecated202007UpdateCountriesParamCountryIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country to update.")
class Deprecated202007UpdateCountriesParamCountryIdRequest(StrictModel):
    """Updates an existing country's configuration. Note: The tax field is deprecated as of API version 2020-10 and should not be used."""
    path: Deprecated202007UpdateCountriesParamCountryIdRequestPath

# Operation: delete_country_202007
class Deprecated202007DeleteCountriesParamCountryIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country to delete. This is a required string value that specifies which country record to remove.")
class Deprecated202007DeleteCountriesParamCountryIdRequest(StrictModel):
    """Permanently deletes a country from the store's configuration. This operation removes the country and all associated settings."""
    path: Deprecated202007DeleteCountriesParamCountryIdRequestPath

# Operation: list_provinces_for_country_202007
class Deprecated202007GetCountriesParamCountryIdProvincesRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve provinces. This ID must correspond to a valid country in the Shopify system.")
class Deprecated202007GetCountriesParamCountryIdProvincesRequest(StrictModel):
    """Retrieves a list of provinces or states for a specified country. Use this to populate province/state selectors or validate province data for a given country."""
    path: Deprecated202007GetCountriesParamCountryIdProvincesRequestPath

# Operation: get_province_count_for_country_202007
class Deprecated202007GetCountriesParamCountryIdProvincesCountRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve the province count.")
class Deprecated202007GetCountriesParamCountryIdProvincesCountRequest(StrictModel):
    """Retrieves the total count of provinces or states for a specified country. Useful for understanding administrative divisions within a country."""
    path: Deprecated202007GetCountriesParamCountryIdProvincesCountRequestPath

# Operation: update_province_for_country_2020_07
class Deprecated202007UpdateCountriesParamCountryIdProvincesParamProvinceIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country containing the province to update.")
    province_id: str = Field(default=..., description="The unique identifier of the province to update.")
class Deprecated202007UpdateCountriesParamCountryIdProvincesParamProvinceIdRequest(StrictModel):
    """Updates an existing province for a specified country. Note: The tax field is deprecated as of API version 2020-10."""
    path: Deprecated202007UpdateCountriesParamCountryIdProvincesParamProvinceIdRequestPath

# Operation: count_custom_collections_2020_07
class Deprecated202007GetCustomCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter the count to include only custom collections with this exact title.")
    product_id: Any | None = Field(default=None, description="Filter the count to include only custom collections that contain this specific product.")
    published_status: Any | None = Field(default=None, description="Filter the count by publication status: 'published' for only published collections, 'unpublished' for only unpublished collections, or 'any' for all collections regardless of status. Defaults to 'any' if not specified.")
class Deprecated202007GetCustomCollectionsCountRequest(StrictModel):
    """Retrieves the total count of custom collections in the store, with optional filtering by title, product inclusion, or published status."""
    query: Deprecated202007GetCustomCollectionsCountRequestQuery | None = None

# Operation: update_custom_collection_202007
class Deprecated202007UpdateCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to update. This ID is required to specify which collection should be modified.")
class Deprecated202007UpdateCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Updates an existing custom collection in your Shopify store. Modify collection details such as title, description, image, and other properties by providing the collection ID."""
    path: Deprecated202007UpdateCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: delete_custom_collection_legacy_202007
class Deprecated202007DeleteCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to delete.")
class Deprecated202007DeleteCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Permanently deletes a custom collection from the store. This action cannot be undone."""
    path: Deprecated202007DeleteCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: list_customers_for_saved_search_2020_07
class Deprecated202007GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestPath(StrictModel):
    customer_saved_search_id: str = Field(default=..., description="The unique identifier of the customer saved search to retrieve customers for.")
class Deprecated202007GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="Specifies the field and direction to sort results by (e.g., ascending or descending order). Defaults to sorting by last order date in descending order.")
    limit: Any | None = Field(default=None, description="The maximum number of customer records to return per request. Defaults to 50 and cannot exceed 250.")
class Deprecated202007GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequest(StrictModel):
    """Retrieves all customers matching the criteria defined in a customer saved search. Results can be ordered and paginated."""
    path: Deprecated202007GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestPath
    query: Deprecated202007GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestQuery | None = None

# Operation: list_customers_202007
class Deprecated202007GetCustomersRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only include customers with the specified IDs. Provide as a comma-separated list of customer ID values.")
    limit: Any | None = Field(default=None, description="Maximum number of customer records to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
class Deprecated202007GetCustomersRequest(StrictModel):
    """Retrieves a paginated list of customers from the store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: Deprecated202007GetCustomersRequestQuery | None = None

# Operation: get_customer_202007
class Deprecated202007GetCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to retrieve.")
class Deprecated202007GetCustomersParamCustomerIdRequest(StrictModel):
    """Retrieves detailed information for a single customer by their unique identifier."""
    path: Deprecated202007GetCustomersParamCustomerIdRequestPath

# Operation: update_customer_202007
class Deprecated202007UpdateCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to update. This ID is required to specify which customer record should be modified.")
class Deprecated202007UpdateCustomersParamCustomerIdRequest(StrictModel):
    """Updates an existing customer's information in Shopify. Modify customer details such as email, name, phone, and other profile attributes."""
    path: Deprecated202007UpdateCustomersParamCustomerIdRequestPath

# Operation: delete_customer_v202007
class Deprecated202007DeleteCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to delete.")
class Deprecated202007DeleteCustomersParamCustomerIdRequest(StrictModel):
    """Permanently deletes a customer from the store. Note that a customer cannot be deleted if they have any existing orders."""
    path: Deprecated202007DeleteCustomersParamCustomerIdRequestPath

# Operation: generate_customer_account_activation_url_2020_07
class Deprecated202007CreateCustomersParamCustomerIdAccountActivationUrlRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer for whom to generate the account activation URL.")
class Deprecated202007CreateCustomersParamCustomerIdAccountActivationUrlRequest(StrictModel):
    """Generate a one-time account activation URL for a customer whose account is not yet enabled. The URL expires after 30 days; generating a new URL invalidates any previously generated URLs."""
    path: Deprecated202007CreateCustomersParamCustomerIdAccountActivationUrlRequestPath

# Operation: list_customer_addresses_202007
class Deprecated202007GetCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses you want to retrieve.")
class Deprecated202007GetCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Retrieves all addresses associated with a specific customer. Uses cursor-based pagination via response headers; the page parameter is not supported."""
    path: Deprecated202007GetCustomersParamCustomerIdAddressesRequestPath

# Operation: create_customer_address_v202007
class Deprecated202007CreateCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer for whom the address is being created.")
class Deprecated202007CreateCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Creates a new address for a customer. The address is added to the customer's address list and can be set as their default billing or shipping address."""
    path: Deprecated202007CreateCustomersParamCustomerIdAddressesRequestPath

# Operation: bulk_update_customer_addresses_202007
class Deprecated202007UpdateCustomersParamCustomerIdAddressesSetRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses will be modified.")
class Deprecated202007UpdateCustomersParamCustomerIdAddressesSetRequestQuery(StrictModel):
    address_ids: int | None = Field(default=None, validation_alias="address_ids[]", serialization_alias="address_ids[]", description="Array of address IDs to target for the bulk operation. The order may be significant depending on the operation type.")
    operation: str | None = Field(default=None, description="The type of bulk operation to perform on the specified addresses (e.g., delete, set as default). Refer to API documentation for valid operation values.")
class Deprecated202007UpdateCustomersParamCustomerIdAddressesSetRequest(StrictModel):
    """Performs bulk operations on multiple customer addresses, allowing you to update, delete, or modify address records in a single request."""
    path: Deprecated202007UpdateCustomersParamCustomerIdAddressesSetRequestPath
    query: Deprecated202007UpdateCustomersParamCustomerIdAddressesSetRequestQuery | None = None

# Operation: get_customer_address_202007
class Deprecated202007GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who owns the address.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to retrieve.")
class Deprecated202007GetCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Retrieves the details of a specific customer address by customer ID and address ID."""
    path: Deprecated202007GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: update_customer_address_2020_07
class Deprecated202007UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being updated.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to update for the customer.")
class Deprecated202007UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Updates an existing customer address by customer ID and address ID. Use this to modify address details such as street, city, postal code, or other address information for a specific customer."""
    path: Deprecated202007UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: delete_customer_address_202007
class Deprecated202007DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being removed.")
    address_id: str = Field(default=..., description="The unique identifier of the address to be deleted from the customer's address list.")
class Deprecated202007DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Removes a specific address from a customer's address list. This operation permanently deletes the address record associated with the given customer."""
    path: Deprecated202007DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: set_customer_default_address_202007
class Deprecated202007UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose default address is being updated.")
    address_id: str = Field(default=..., description="The unique identifier of the address to set as the customer's default address.")
class Deprecated202007UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest(StrictModel):
    """Sets a specific address as the default address for a customer. This updates the customer's primary address used for shipping and billing purposes."""
    path: Deprecated202007UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath

# Operation: list_customer_orders_202007
class Deprecated202007GetCustomersParamCustomerIdOrdersRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose orders should be retrieved.")
class Deprecated202007GetCustomersParamCustomerIdOrdersRequest(StrictModel):
    """Retrieves all orders for a specific customer. Supports standard Order resource query parameters for filtering, sorting, and pagination."""
    path: Deprecated202007GetCustomersParamCustomerIdOrdersRequestPath

# Operation: send_customer_invite_202007
class Deprecated202007CreateCustomersParamCustomerIdSendInviteRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who will receive the account invite.")
class Deprecated202007CreateCustomersParamCustomerIdSendInviteRequest(StrictModel):
    """Sends an account invitation email to a customer, allowing them to create or access their account on the store."""
    path: Deprecated202007CreateCustomersParamCustomerIdSendInviteRequestPath

# Operation: get_discount_code_location
class Deprecated202007GetDiscountCodesLookupRequestQuery(StrictModel):
    code: str | None = Field(default=None, description="The discount code to look up (e.g. 'SUMMER20')")
class Deprecated202007GetDiscountCodesLookupRequest(StrictModel):
    """Retrieves the location URI of a discount code. The discount code's location is returned in the HTTP Location header rather than in the response body, allowing you to fetch the full discount code resource from the returned URI."""
    query: Deprecated202007GetDiscountCodesLookupRequestQuery | None = None

# Operation: list_events_202007
class Deprecated202007GetEventsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of events to return per request. Defaults to 50 if not specified; cannot exceed 250.")
    filter_: Any | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filters events to show only those matching the specified criteria. Use this to narrow results to relevant event types or resources.")
    verb: Any | None = Field(default=None, description="Filters events to show only those of a specific action type (e.g., create, update, delete). Useful for tracking particular kinds of changes.")
class Deprecated202007GetEventsRequest(StrictModel):
    """Retrieves a paginated list of events from the store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: Deprecated202007GetEventsRequestQuery | None = None

# Operation: get_event_2020_07
class Deprecated202007GetEventsParamEventIdRequestPath(StrictModel):
    event_id: str = Field(default=..., description="The unique identifier of the event to retrieve.")
class Deprecated202007GetEventsParamEventIdRequest(StrictModel):
    """Retrieves a single event by its ID from the Shopify admin. Use this to fetch detailed information about a specific event that occurred in your store."""
    path: Deprecated202007GetEventsParamEventIdRequestPath

# Operation: get_fulfillment_order_202007
class Deprecated202007GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to retrieve.")
class Deprecated202007GetFulfillmentOrdersParamFulfillmentOrderIdRequest(StrictModel):
    """Retrieves the details of a specific fulfillment order by its ID. Use this to fetch current status, line items, and fulfillment information for a particular order."""
    path: Deprecated202007GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath

# Operation: cancel_fulfillment_order_2020_07
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest(StrictModel):
    """Cancels a fulfillment order, marking it as no longer needed for processing. This operation is used to prevent a fulfillment order from being fulfilled."""
    path: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath

# Operation: send_fulfillment_order_cancellation_request_2020_07
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel. This ID references a specific fulfillment order in the system.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for the cancellation request. This provides context to the fulfillment service about why the cancellation is being requested.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest(StrictModel):
    """Sends a cancellation request to the fulfillment service for a specific fulfillment order. This notifies the fulfillment provider to stop processing or cancel an already-in-progress fulfillment."""
    path: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath
    query: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery | None = None

# Operation: accept_fulfillment_order_cancellation_request_2020_07
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to accept the cancellation request.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for accepting the cancellation request.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest(StrictModel):
    """Accepts a cancellation request for a fulfillment order, confirming that the fulfillment service should cancel the specified order. Optionally include a reason message for the acceptance."""
    path: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath
    query: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_order_cancellation_request_2020_07
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which you are rejecting the cancellation request.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining why the cancellation request is being rejected. This reason will be communicated to the fulfillment service.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest(StrictModel):
    """Rejects a cancellation request that was sent to a fulfillment service for a specific fulfillment order. Use this when you need to decline a cancellation and optionally provide a reason to the fulfillment service."""
    path: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath
    query: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery | None = None

# Operation: close_fulfillment_order_2020_07
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to close.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional reason or note explaining why the fulfillment order is being marked as incomplete.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest(StrictModel):
    """Marks an in-progress fulfillment order as incomplete, indicating the fulfillment service cannot ship remaining items and is closing the order."""
    path: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath
    query: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery | None = None

# Operation: send_fulfillment_request_202007
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to request fulfillment for.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message to include with the fulfillment request, such as special instructions or notes for the fulfillment service.")
    fulfillment_order_line_items: Any | None = Field(default=None, description="An optional array of fulfillment order line items to request for fulfillment. If omitted, all line items in the fulfillment order will be requested.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest(StrictModel):
    """Sends a fulfillment request to the fulfillment service for a specific fulfillment order, optionally specifying which line items to fulfill and including an optional message."""
    path: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath
    query: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery | None = None

# Operation: accept_fulfillment_request_2020_07
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request is being accepted.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message providing context or reasoning for accepting the fulfillment request.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest(StrictModel):
    """Accepts a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, confirming that the fulfillment service will proceed with fulfilling the order."""
    path: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath
    query: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_request_202007
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request should be rejected.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for rejecting the fulfillment request.")
class Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest(StrictModel):
    """Rejects a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, optionally providing a reason for the rejection."""
    path: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath
    query: Deprecated202007CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery | None = None

# Operation: list_locations_for_fulfillment_order_move_2020_07
class Deprecated202007GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to retrieve available move destinations.")
class Deprecated202007GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest(StrictModel):
    """Retrieves all locations where a fulfillment order can be moved to. The results are sorted alphabetically by location name in ascending order."""
    path: Deprecated202007GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath

# Operation: cancel_fulfillment_202007
class Deprecated202007CreateFulfillmentsParamFulfillmentIdCancelRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to cancel. This ID references a specific fulfillment order that has been previously created.")
class Deprecated202007CreateFulfillmentsParamFulfillmentIdCancelRequest(StrictModel):
    """Cancels an existing fulfillment order. This operation marks the specified fulfillment as cancelled and updates its status accordingly."""
    path: Deprecated202007CreateFulfillmentsParamFulfillmentIdCancelRequestPath

# Operation: update_fulfillment_tracking_2020_07
class Deprecated202007CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment whose tracking information should be updated.")
class Deprecated202007CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest(StrictModel):
    """Updates tracking information for a specific fulfillment, allowing you to modify shipment tracking details after the fulfillment has been created."""
    path: Deprecated202007CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath

# Operation: list_gift_cards_2020_07
class Deprecated202007GetGiftCardsRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter results to gift cards with a specific status: enabled to show only active gift cards, or disabled to show only inactive gift cards. Omit to retrieve all gift cards regardless of status.")
    limit: Any | None = Field(default=None, description="Maximum number of gift cards to return per request, between 1 and 250 (defaults to 50 if not specified).")
class Deprecated202007GetGiftCardsRequest(StrictModel):
    """Retrieves a paginated list of gift cards, optionally filtered by status. Results are paginated using cursor-based links provided in the response header rather than page parameters."""
    query: Deprecated202007GetGiftCardsRequestQuery | None = None

# Operation: count_gift_cards_v202007
class Deprecated202007GetGiftCardsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count to only include gift cards with a specific status: enabled for active gift cards, or disabled for inactive gift cards. Omit to count all gift cards regardless of status.")
class Deprecated202007GetGiftCardsCountRequest(StrictModel):
    """Retrieves the total count of gift cards, optionally filtered by their enabled or disabled status."""
    query: Deprecated202007GetGiftCardsCountRequestQuery | None = None

# Operation: search_gift_cards_202007
class Deprecated202007GetGiftCardsSearchRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="The field and sort direction for ordering results. Defaults to most recently disabled gift cards first.")
    query: Any | None = Field(default=None, description="The search query text to match against indexed gift card fields including created_at, updated_at, disabled_at, balance, initial_value, amount_spent, email, and last_characters.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50.")
class Deprecated202007GetGiftCardsSearchRequest(StrictModel):
    """Search for gift cards using indexed fields like balance, email, or creation date. Results are paginated and returned via link headers."""
    query: Deprecated202007GetGiftCardsSearchRequestQuery | None = None

# Operation: update_gift_card_202007
class Deprecated202007UpdateGiftCardsParamGiftCardIdRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to update.")
class Deprecated202007UpdateGiftCardsParamGiftCardIdRequest(StrictModel):
    """Update an existing gift card's expiry date, note, and template suffix. Note that the gift card's balance cannot be modified through the API."""
    path: Deprecated202007UpdateGiftCardsParamGiftCardIdRequestPath

# Operation: disable_gift_card_202007
class Deprecated202007CreateGiftCardsParamGiftCardIdDisableRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to disable.")
class Deprecated202007CreateGiftCardsParamGiftCardIdDisableRequest(StrictModel):
    """Permanently disables a gift card, preventing it from being used for future transactions. This action cannot be reversed."""
    path: Deprecated202007CreateGiftCardsParamGiftCardIdDisableRequestPath

# Operation: list_inventory_items_202007
class Deprecated202007GetInventoryItemsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of inventory items to return per request. Defaults to 50 items; maximum allowed is 250 items.")
    ids: int | None = Field(default=None, description="Filter results to only inventory items with the specified IDs. Provide one or more integer IDs to narrow the results.")
class Deprecated202007GetInventoryItemsRequest(StrictModel):
    """Retrieves a paginated list of inventory items. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: Deprecated202007GetInventoryItemsRequestQuery | None = None

# Operation: get_inventory_item_legacy
class Deprecated202007GetInventoryItemsParamInventoryItemIdRequestPath(StrictModel):
    inventory_item_id: str = Field(default=..., description="The unique identifier of the inventory item to retrieve.")
class Deprecated202007GetInventoryItemsParamInventoryItemIdRequest(StrictModel):
    """Retrieves a single inventory item by its unique identifier. Use this to fetch detailed information about a specific inventory item in your Shopify store."""
    path: Deprecated202007GetInventoryItemsParamInventoryItemIdRequestPath

# Operation: list_inventory_levels_202007
class Deprecated202007GetInventoryLevelsRequestQuery(StrictModel):
    inventory_item_ids: Any | None = Field(default=None, description="Comma-separated list of inventory item IDs to filter results. Maximum of 50 IDs per request.")
    location_ids: Any | None = Field(default=None, description="Comma-separated list of location IDs to filter results. Maximum of 50 IDs per request. Use the Location resource to find location IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request. Defaults to 50 if not specified; cannot exceed 250.")
class Deprecated202007GetInventoryLevelsRequest(StrictModel):
    """Retrieves inventory levels across locations and inventory items. You must filter by at least one inventory item ID or location ID to retrieve results."""
    query: Deprecated202007GetInventoryLevelsRequestQuery | None = None

# Operation: delete_inventory_level_202007
class Deprecated202007DeleteInventoryLevelsRequestQuery(StrictModel):
    inventory_item_id: int | None = Field(default=None, description="The unique identifier of the inventory item whose level should be deleted.")
    location_id: int | None = Field(default=None, description="The unique identifier of the location from which the inventory item should be removed.")
class Deprecated202007DeleteInventoryLevelsRequest(StrictModel):
    """Removes an inventory level for a specific inventory item at a location. This operation disconnects the inventory item from that location; note that every inventory item must maintain at least one inventory level, so you must connect the item to another location before deleting its last level."""
    query: Deprecated202007DeleteInventoryLevelsRequestQuery | None = None

# Operation: get_location_202007
class Deprecated202007GetLocationsParamLocationIdRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location to retrieve.")
class Deprecated202007GetLocationsParamLocationIdRequest(StrictModel):
    """Retrieves a single location by its ID from the Shopify inventory system. Use this to fetch detailed information about a specific location."""
    path: Deprecated202007GetLocationsParamLocationIdRequestPath

# Operation: list_inventory_levels_for_location_202007
class Deprecated202007GetLocationsParamLocationIdInventoryLevelsRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location for which to retrieve inventory levels.")
class Deprecated202007GetLocationsParamLocationIdInventoryLevelsRequest(StrictModel):
    """Retrieves all inventory levels for a specific location. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""
    path: Deprecated202007GetLocationsParamLocationIdInventoryLevelsRequestPath

# Operation: list_orders_v202007
class Deprecated202007GetOrdersRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only orders with the specified IDs, provided as a comma-separated list.")
    limit: Any | None = Field(default=None, description="Maximum number of orders to return per page, between 1 and 250 (defaults to 50).")
    processed_at_min: Any | None = Field(default=None, description="Show only orders processed at or after this date, specified in ISO 8601 format with timezone.")
    processed_at_max: Any | None = Field(default=None, description="Show only orders processed at or before this date, specified in ISO 8601 format with timezone.")
    attribution_app_id: Any | None = Field(default=None, description="Filter orders by the app that created them, using the app's ID or 'current' for the requesting app.")
    status: Any | None = Field(default=None, description="Filter orders by their fulfillment state: open (default), closed, cancelled, or any (including archived orders).")
    financial_status: Any | None = Field(default=None, description="Filter orders by their payment state: authorized, pending, paid, partially_paid, refunded, voided, partially_refunded, unpaid, or any (defaults to any).")
    fulfillment_status: Any | None = Field(default=None, description="Filter orders by their shipment state: shipped (fulfilled), partial, unshipped (null), unfulfilled (null or partial), or any (defaults to any).")
class Deprecated202007GetOrdersRequest(StrictModel):
    """Retrieves a paginated list of orders with filtering options by status, financial state, fulfillment state, and other criteria. Results are paginated using link headers in the response."""
    query: Deprecated202007GetOrdersRequestQuery | None = None

# Operation: list_fulfillment_orders_for_order_2020_07
class Deprecated202007GetOrdersParamOrderIdFulfillmentOrdersRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve fulfillment orders.")
class Deprecated202007GetOrdersParamOrderIdFulfillmentOrdersRequest(StrictModel):
    """Retrieves all fulfillment orders associated with a specific order. Fulfillment orders represent the items in an order that need to be fulfilled."""
    path: Deprecated202007GetOrdersParamOrderIdFulfillmentOrdersRequestPath

# Operation: list_fulfillments_for_order_v202007
class Deprecated202007GetOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order whose fulfillments you want to retrieve.")
class Deprecated202007GetOrdersParamOrderIdFulfillmentsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of fulfillments to return per request, between 1 and 250 (defaults to 50).")
class Deprecated202007GetOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Retrieves all fulfillments associated with a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the limit parameter."""
    path: Deprecated202007GetOrdersParamOrderIdFulfillmentsRequestPath
    query: Deprecated202007GetOrdersParamOrderIdFulfillmentsRequestQuery | None = None

# Operation: create_fulfillment_for_order_legacy_202007
class Deprecated202007CreateOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the fulfillment.")
class Deprecated202007CreateOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Create a fulfillment for specified line items in an order. The fulfillment status depends on the fulfillment service type: manual/custom services set status immediately, while external services queue the fulfillment with pending status until processed."""
    path: Deprecated202007CreateOrdersParamOrderIdFulfillmentsRequestPath

# Operation: get_fulfillment_count_for_order_2020_07
class Deprecated202007GetOrdersParamOrderIdFulfillmentsCountRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve the fulfillment count.")
class Deprecated202007GetOrdersParamOrderIdFulfillmentsCountRequest(StrictModel):
    """Retrieves the total count of fulfillments associated with a specific order. Useful for understanding fulfillment status and logistics tracking without fetching full fulfillment details."""
    path: Deprecated202007GetOrdersParamOrderIdFulfillmentsCountRequestPath

# Operation: get_fulfillment_202007
class Deprecated202007GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to retrieve.")
class Deprecated202007GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Retrieve detailed information about a specific fulfillment for an order. Use this to access fulfillment status, tracking information, and line item details."""
    path: Deprecated202007GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: update_fulfillment_202007
class Deprecated202007UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to update.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to update.")
class Deprecated202007UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Update fulfillment details for a specific order, such as tracking information or fulfillment status."""
    path: Deprecated202007UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: complete_fulfillment_2020_07
class Deprecated202007CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to be completed.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment within the order that should be marked as complete.")
class Deprecated202007CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest(StrictModel):
    """Mark a fulfillment as complete, indicating that all items in the fulfillment have been shipped or delivered to the customer."""
    path: Deprecated202007CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath

# Operation: list_fulfillment_events_202007
class Deprecated202007GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment within the specified order.")
class Deprecated202007GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest(StrictModel):
    """Retrieves all events associated with a specific fulfillment for an order, including status updates and tracking information."""
    path: Deprecated202007GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath

# Operation: open_fulfillment_202007
class Deprecated202007CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to be opened.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to mark as open.")
class Deprecated202007CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequest(StrictModel):
    """Mark a fulfillment as open, allowing it to receive additional items or changes. This operation transitions a fulfillment from a closed state back to an open state."""
    path: Deprecated202007CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequestPath

# Operation: list_order_refunds_202007
class Deprecated202007GetOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve refunds.")
class Deprecated202007GetOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of refunds to return per request, between 1 and 250 (defaults to 50).")
    in_shop_currency: Any | None = Field(default=None, description="When true, displays refund amounts in the shop's currency for the underlying transaction; defaults to false.")
class Deprecated202007GetOrdersParamOrderIdRefundsRequest(StrictModel):
    """Retrieves a list of refunds for a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    path: Deprecated202007GetOrdersParamOrderIdRefundsRequestPath
    query: Deprecated202007GetOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: create_order_refund_202007
class Deprecated202007CreateOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create a refund.")
class Deprecated202007CreateOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    notify: Any | None = Field(default=None, description="Whether to send a refund notification email to the customer.")
    note: Any | None = Field(default=None, description="An optional note to attach to the refund for internal reference.")
    discrepancy_reason: Any | None = Field(default=None, description="An optional reason explaining any discrepancy between calculated and actual refund amounts. Valid values are: restock, damage, customer, or other.")
    shipping: Any | None = Field(default=None, description="Shipping refund details. Specify either full_refund to refund all remaining shipping, or amount to refund a specific shipping amount (takes precedence over full_refund).")
    refund_line_items: Any | None = Field(default=None, description="A list of line items to refund, each with the line item ID, quantity to refund, restock type (no_restock, cancel, or return), and location ID for restocking (required for cancel and return types).")
    transactions: Any | None = Field(default=None, description="A list of transactions to process as refunds. Should be obtained from the calculate endpoint for accuracy.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required for multi-currency orders when an amount property is provided.")
class Deprecated202007CreateOrdersParamOrderIdRefundsRequest(StrictModel):
    """Creates a refund for an order. Use the calculate endpoint first to determine the correct transactions to submit. For multi-currency orders, the currency property is required whenever an amount is specified."""
    path: Deprecated202007CreateOrdersParamOrderIdRefundsRequestPath
    query: Deprecated202007CreateOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: calculate_order_refund_2020_07
class Deprecated202007CreateOrdersParamOrderIdRefundsCalculateRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to calculate the refund.")
class Deprecated202007CreateOrdersParamOrderIdRefundsCalculateRequestQuery(StrictModel):
    shipping: Any | None = Field(default=None, description="Shipping refund configuration. Specify either full_refund to refund all remaining shipping, or amount to refund a specific shipping cost. The amount property takes precedence over full_refund.")
    refund_line_items: Any | None = Field(default=None, description="List of line items to refund, each specifying the line item ID, quantity to refund, restock instructions (no_restock, cancel, or return), and optionally the location ID where items should be restocked. If location_id is omitted for return or cancel restocks, the endpoint will suggest an appropriate location.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required whenever a shipping amount is specified, particularly important for multi-currency orders.")
class Deprecated202007CreateOrdersParamOrderIdRefundsCalculateRequest(StrictModel):
    """Calculate refund transactions for an order based on line items and shipping costs. Use this endpoint to generate accurate refund details before creating an actual refund, including any necessary adjustments to restock instructions."""
    path: Deprecated202007CreateOrdersParamOrderIdRefundsCalculateRequestPath
    query: Deprecated202007CreateOrdersParamOrderIdRefundsCalculateRequestQuery | None = None

# Operation: get_refund_legacy
class Deprecated202007GetOrdersParamOrderIdRefundsParamRefundIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the refund.")
    refund_id: str = Field(default=..., description="The unique identifier of the refund to retrieve.")
class Deprecated202007GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery(StrictModel):
    in_shop_currency: Any | None = Field(default=None, description="When enabled, displays all monetary amounts in the shop's currency rather than the transaction currency. Defaults to false.")
class Deprecated202007GetOrdersParamOrderIdRefundsParamRefundIdRequest(StrictModel):
    """Retrieves the details of a specific refund for an order. Use this to view refund information including amounts, line items, and status."""
    path: Deprecated202007GetOrdersParamOrderIdRefundsParamRefundIdRequestPath
    query: Deprecated202007GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery | None = None

# Operation: list_order_risks_2020_07
class Deprecated202007GetOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve associated risks.")
class Deprecated202007GetOrdersParamOrderIdRisksRequest(StrictModel):
    """Retrieves all fraud and risk assessments associated with a specific order. This endpoint uses cursor-based pagination via response headers rather than page parameters."""
    path: Deprecated202007GetOrdersParamOrderIdRisksRequestPath

# Operation: create_order_risk_202007
class Deprecated202007CreateOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the risk record.")
class Deprecated202007CreateOrdersParamOrderIdRisksRequest(StrictModel):
    """Creates a risk assessment record for a specific order. Use this to flag potential issues or concerns associated with an order that may require review or action."""
    path: Deprecated202007CreateOrdersParamOrderIdRisksRequestPath

# Operation: update_order_risk_202007
class Deprecated202007UpdateOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to be updated.")
    risk_id: str = Field(default=..., description="The unique identifier of the order risk to be updated.")
class Deprecated202007UpdateOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Updates an existing order risk for a specific order. Note that you cannot modify an order risk that was created by another application."""
    path: Deprecated202007UpdateOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: delete_order_risk_202007
class Deprecated202007DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to delete.")
    risk_id: str = Field(default=..., description="The unique identifier of the risk assessment to delete.")
class Deprecated202007DeleteOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Removes a fraud risk assessment from an order. Note that you can only delete risks created by your application; risks created by other applications cannot be deleted."""
    path: Deprecated202007DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: create_discount_codes_batch_202007
class Deprecated202007CreatePriceRulesParamPriceRuleIdBatchRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which discount codes will be created.")
class Deprecated202007CreatePriceRulesParamPriceRuleIdBatchRequest(StrictModel):
    """Asynchronously creates up to 100 discount codes for a price rule in a single batch job. Returns a discount code creation job object that can be monitored for completion status, including counts of successful and failed code creations."""
    path: Deprecated202007CreatePriceRulesParamPriceRuleIdBatchRequestPath

# Operation: get_discount_code_batch_202007
class Deprecated202007GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch job.")
    batch_id: str = Field(default=..., description="The unique identifier of the specific batch job for discount code creation.")
class Deprecated202007GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest(StrictModel):
    """Retrieves the status and details of a discount code creation job batch for a specific price rule. Use this to check the progress and results of bulk discount code generation."""
    path: Deprecated202007GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath

# Operation: list_discount_codes_for_batch_202007
class Deprecated202007GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch.")
    batch_id: str = Field(default=..., description="The unique identifier of the batch job containing the discount codes to retrieve.")
class Deprecated202007GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest(StrictModel):
    """Retrieves all discount codes generated from a specific batch creation job for a price rule. Results include successfully created codes with populated IDs and codes that failed with error details."""
    path: Deprecated202007GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath

# Operation: list_discount_codes_for_price_rule_2020_07
class Deprecated202007GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which to retrieve associated discount codes.")
class Deprecated202007GetPriceRulesParamPriceRuleIdDiscountCodesRequest(StrictModel):
    """Retrieve all discount codes associated with a specific price rule. Results are paginated using link-based navigation provided in response headers."""
    path: Deprecated202007GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath

# Operation: create_discount_code_for_price_rule_deprecated
class Deprecated202007CreatePriceRulesParamPriceRuleIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule to which this discount code will be associated.")
class Deprecated202007CreatePriceRulesParamPriceRuleIdDiscountCodesRequest(StrictModel):
    """Creates a new discount code associated with a specific price rule. The discount code can be used by customers to apply the price rule's discounts during checkout."""
    path: Deprecated202007CreatePriceRulesParamPriceRuleIdDiscountCodesRequestPath

# Operation: delete_discount_code_202007
class Deprecated202007DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code to be deleted.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to be deleted.")
class Deprecated202007DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Permanently deletes a specific discount code associated with a price rule. This action cannot be undone."""
    path: Deprecated202007DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: update_product_listing_v202007
class Deprecated202007UpdateProductListingsParamProductListingIdRequestPath(StrictModel):
    product_listing_id: str = Field(default=..., description="The unique identifier of the product listing to update.")
class Deprecated202007UpdateProductListingsParamProductListingIdRequest(StrictModel):
    """Update a product listing to publish or modify a product's presence on your sales channel app."""
    path: Deprecated202007UpdateProductListingsParamProductListingIdRequestPath

# Operation: delete_product_listing_v2020_07
class Deprecated202007DeleteProductListingsParamProductListingIdRequestPath(StrictModel):
    product_listing_id: str = Field(default=..., description="The unique identifier of the product listing to delete. This ID represents the specific product-to-channel relationship you want to remove.")
class Deprecated202007DeleteProductListingsParamProductListingIdRequest(StrictModel):
    """Remove a product listing to unpublish a product from your sales channel app. This operation deletes the listing relationship without affecting the underlying product."""
    path: Deprecated202007DeleteProductListingsParamProductListingIdRequestPath

# Operation: list_products_2020_07
class Deprecated202007GetProductsRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only include products with IDs matching this comma-separated list of product identifiers.")
    limit: Any | None = Field(default=None, description="Maximum number of products to return per page, between 1 and 250 (defaults to 50).")
    title: Any | None = Field(default=None, description="Filter results to only include products whose title matches this value.")
    vendor: Any | None = Field(default=None, description="Filter results to only include products from this vendor.")
    handle: Any | None = Field(default=None, description="Filter results to only include products with this handle (URL-friendly identifier).")
    product_type: Any | None = Field(default=None, description="Filter results to only include products of this type.")
    status: Any | None = Field(default=None, description="Filter results by product status: active (default), archived, or draft.")
    collection_id: Any | None = Field(default=None, description="Filter results to only include products belonging to this collection ID.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: published, unpublished, or any (default shows all).")
    presentment_currencies: Any | None = Field(default=None, description="Return prices in only these currencies, specified as a comma-separated list of ISO 4217 currency codes.")
class Deprecated202007GetProductsRequest(StrictModel):
    """Retrieves a paginated list of products from the store, with support for filtering by various attributes and sorting options. Uses cursor-based pagination via response headers rather than page parameters."""
    query: Deprecated202007GetProductsRequestQuery | None = None

# Operation: get_products_count_202007
class Deprecated202007GetProductsCountRequestQuery(StrictModel):
    vendor: Any | None = Field(default=None, description="Filter the count to include only products from a specific vendor.")
    product_type: Any | None = Field(default=None, description="Filter the count to include only products of a specific product type.")
    collection_id: Any | None = Field(default=None, description="Filter the count to include only products belonging to a specific collection by its ID.")
    published_status: Any | None = Field(default=None, description="Filter products by their publication status: use 'published' for only published products, 'unpublished' for only unpublished products, or 'any' to include all products regardless of status (default is 'any').")
class Deprecated202007GetProductsCountRequest(StrictModel):
    """Retrieves the total count of products in the store, with optional filtering by vendor, product type, collection, or published status."""
    query: Deprecated202007GetProductsCountRequestQuery | None = None

# Operation: get_product_202007
class Deprecated202007GetProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to retrieve.")
class Deprecated202007GetProductsParamProductIdRequest(StrictModel):
    """Retrieves detailed information for a single product by its ID from the Shopify store."""
    path: Deprecated202007GetProductsParamProductIdRequestPath

# Operation: delete_product_202007
class Deprecated202007DeleteProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to delete. This is a numeric ID assigned by Shopify.")
class Deprecated202007DeleteProductsParamProductIdRequest(StrictModel):
    """Permanently deletes a product from the store. This action cannot be undone and will remove the product and all associated data."""
    path: Deprecated202007DeleteProductsParamProductIdRequestPath

# Operation: list_product_images_202007
class Deprecated202007GetProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product whose images you want to retrieve.")
class Deprecated202007GetProductsParamProductIdImagesRequest(StrictModel):
    """Retrieve all images associated with a specific product. Returns a collection of image resources for the given product."""
    path: Deprecated202007GetProductsParamProductIdImagesRequestPath

# Operation: create_product_image_202007
class Deprecated202007CreateProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to which the image will be added.")
class Deprecated202007CreateProductsParamProductIdImagesRequest(StrictModel):
    """Create a new image for a specific product. The image will be associated with the product and can be used to display product visuals in the storefront."""
    path: Deprecated202007CreateProductsParamProductIdImagesRequestPath

# Operation: get_product_images_count_202007
class Deprecated202007GetProductsParamProductIdImagesCountRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product for which to retrieve the image count.")
class Deprecated202007GetProductsParamProductIdImagesCountRequest(StrictModel):
    """Retrieve the total count of images associated with a specific product. Useful for determining how many product images exist without fetching the full image data."""
    path: Deprecated202007GetProductsParamProductIdImagesCountRequestPath

# Operation: get_product_image_legacy
class Deprecated202007GetProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product that contains the image.")
    image_id: str = Field(default=..., description="The unique identifier of the specific image to retrieve.")
class Deprecated202007GetProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Retrieve a specific product image by its ID. Returns detailed metadata for the requested image associated with a product."""
    path: Deprecated202007GetProductsParamProductIdImagesParamImageIdRequestPath

# Operation: update_product_image_202007
class Deprecated202007UpdateProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product that contains the image to be updated.")
    image_id: str = Field(default=..., description="The unique identifier of the image within the product to be updated.")
class Deprecated202007UpdateProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Update the properties of an existing product image, such as alt text, position, or other image metadata."""
    path: Deprecated202007UpdateProductsParamProductIdImagesParamImageIdRequestPath

# Operation: delete_product_image_202007
class Deprecated202007DeleteProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product that contains the image to be deleted.")
    image_id: str = Field(default=..., description="The unique identifier of the image to be deleted from the product.")
class Deprecated202007DeleteProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Delete a specific image associated with a product. This removes the image from the product's image gallery."""
    path: Deprecated202007DeleteProductsParamProductIdImagesParamImageIdRequestPath

# Operation: update_recurring_application_charge_capped_amount_2020_07
class Deprecated202007UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to update.")
class Deprecated202007UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery(StrictModel):
    recurring_application_charge_capped_amount: int | None = Field(default=None, validation_alias="recurring_application_charge[capped_amount]", serialization_alias="recurring_application_charge[capped_amount]", description="The new capped amount limit for the recurring charge, specified as a whole number representing the maximum billable amount.")
class Deprecated202007UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest(StrictModel):
    """Updates the capped amount limit for an active recurring application charge. This allows you to modify the maximum amount that can be charged to the merchant for this recurring billing plan."""
    path: Deprecated202007UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath
    query: Deprecated202007UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery | None = None

# Operation: create_usage_charge_for_recurring_application_charge_202007
class Deprecated202007CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge for which to create the usage charge.")
class Deprecated202007CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Creates a usage charge against an existing recurring application charge. Usage charges allow you to bill merchants for variable usage on top of their recurring subscription."""
    path: Deprecated202007CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath

# Operation: get_usage_charge_for_recurring_application_charge_202007
class Deprecated202007GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge that contains the usage charge you want to retrieve.")
    usage_charge_id: str = Field(default=..., description="The unique identifier of the specific usage charge to retrieve.")
class Deprecated202007GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest(StrictModel):
    """Retrieves a single usage charge associated with a recurring application charge. Use this to fetch details about a specific metered billing charge."""
    path: Deprecated202007GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath

# Operation: list_redirects_202007
class Deprecated202007GetRedirectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of redirects to return per request, between 1 and 250 (defaults to 50).")
    path: Any | None = Field(default=None, description="Filter results to show only redirects with a specific source path.")
    target: Any | None = Field(default=None, description="Filter results to show only redirects pointing to a specific target URL.")
class Deprecated202007GetRedirectsRequest(StrictModel):
    """Retrieves a list of URL redirects configured in the online store. Results are paginated using link headers in the response rather than page parameters."""
    query: Deprecated202007GetRedirectsRequestQuery | None = None

# Operation: get_redirects_count_2020_07
class Deprecated202007GetRedirectsCountRequestQuery(StrictModel):
    path: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific path value.")
    target: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific target URL.")
class Deprecated202007GetRedirectsCountRequest(StrictModel):
    """Retrieves the total count of URL redirects in the store, with optional filtering by path or target URL."""
    query: Deprecated202007GetRedirectsCountRequestQuery | None = None

# Operation: get_redirect_202007
class Deprecated202007GetRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to retrieve.")
class Deprecated202007GetRedirectsParamRedirectIdRequest(StrictModel):
    """Retrieves a single redirect by its ID from the Shopify online store. Use this to fetch details about a specific URL redirect configuration."""
    path: Deprecated202007GetRedirectsParamRedirectIdRequestPath

# Operation: update_redirect_v202007
class Deprecated202007UpdateRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to update. This ID is required to locate and modify the specific redirect.")
class Deprecated202007UpdateRedirectsParamRedirectIdRequest(StrictModel):
    """Updates an existing redirect in the online store. Modify redirect settings such as the target path or status by providing the redirect's unique identifier."""
    path: Deprecated202007UpdateRedirectsParamRedirectIdRequestPath

# Operation: delete_redirect_v202007
class Deprecated202007DeleteRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to delete.")
class Deprecated202007DeleteRedirectsParamRedirectIdRequest(StrictModel):
    """Permanently deletes a redirect from the online store. This action cannot be undone."""
    path: Deprecated202007DeleteRedirectsParamRedirectIdRequestPath

# Operation: create_report_legacy_202007
class Deprecated202007CreateReportsRequestQuery(StrictModel):
    name: Any | None = Field(default=None, description="The display name for the report. Must be 255 characters or fewer.")
    shopify_ql: Any | None = Field(default=None, description="The ShopifyQL query string that defines what data the report will retrieve and analyze.")
class Deprecated202007CreateReportsRequest(StrictModel):
    """Creates a new custom report in the Shopify admin. Reports use ShopifyQL queries to analyze store data and can be referenced by name for future access."""
    query: Deprecated202007CreateReportsRequestQuery | None = None

# Operation: get_report_202007
class Deprecated202007GetReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to retrieve.")
class Deprecated202007GetReportsParamReportIdRequest(StrictModel):
    """Retrieves a single report that was created by your app. Use this to fetch details about a specific report by its ID."""
    path: Deprecated202007GetReportsParamReportIdRequestPath

# Operation: delete_report_202007
class Deprecated202007DeleteReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to delete. This is a required string value that identifies which report should be removed.")
class Deprecated202007DeleteReportsParamReportIdRequest(StrictModel):
    """Permanently deletes a specific report from the Shopify admin. This action cannot be undone."""
    path: Deprecated202007DeleteReportsParamReportIdRequestPath

# Operation: list_payouts
class Deprecated202007GetShopifyPaymentsPayoutsRequestQuery(StrictModel):
    date_min: Any | None = Field(default=None, description="Filter payouts to include only those made on or after the specified date (inclusive).")
    date_max: Any | None = Field(default=None, description="Filter payouts to include only those made on or before the specified date (inclusive).")
    status: Any | None = Field(default=None, description="Filter payouts by their status (e.g., pending, completed, failed, cancelled).")
class Deprecated202007GetShopifyPaymentsPayoutsRequest(StrictModel):
    """Retrieves a list of all payouts ordered by payout date, with the most recent first. Results are paginated using link headers in the response."""
    query: Deprecated202007GetShopifyPaymentsPayoutsRequestQuery | None = None

# Operation: get_shopify_payments_payout_2020_07
class Deprecated202007GetShopifyPaymentsPayoutsParamPayoutIdRequestPath(StrictModel):
    payout_id: str = Field(default=..., description="The unique identifier of the payout to retrieve.")
class Deprecated202007GetShopifyPaymentsPayoutsParamPayoutIdRequest(StrictModel):
    """Retrieves details for a specific Shopify Payments payout by its unique identifier."""
    path: Deprecated202007GetShopifyPaymentsPayoutsParamPayoutIdRequestPath

# Operation: list_smart_collections_202007
class Deprecated202007GetSmartCollectionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of smart collections to return per request. Defaults to 50 and cannot exceed 250.")
    ids: Any | None = Field(default=None, description="Filter results to only smart collections with the specified IDs. Provide as a comma-separated list of numeric IDs.")
    title: Any | None = Field(default=None, description="Filter results to smart collections matching the exact title.")
    product_id: Any | None = Field(default=None, description="Filter results to only smart collections that contain the specified product ID.")
    handle: Any | None = Field(default=None, description="Filter results by the smart collection's URL-friendly handle.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for published collections only, 'unpublished' for unpublished collections only, or 'any' for all collections. Defaults to 'any'.")
class Deprecated202007GetSmartCollectionsRequest(StrictModel):
    """Retrieves a paginated list of smart collections from your store. Results are paginated using link headers in the response."""
    query: Deprecated202007GetSmartCollectionsRequestQuery | None = None

# Operation: count_smart_collections_202007
class Deprecated202007GetSmartCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter to only count smart collections with this exact title.")
    product_id: Any | None = Field(default=None, description="Filter to only count smart collections that include the specified product.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for only published collections, 'unpublished' for only unpublished collections, or 'any' to include all collections regardless of status. Defaults to 'any'.")
class Deprecated202007GetSmartCollectionsCountRequest(StrictModel):
    """Retrieves the total count of smart collections in the store, with optional filtering by title, product inclusion, or published status."""
    query: Deprecated202007GetSmartCollectionsCountRequestQuery | None = None

# Operation: get_smart_collection_legacy
class Deprecated202007GetSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to retrieve.")
class Deprecated202007GetSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Retrieves a single smart collection by its ID. Smart collections are dynamically generated product collections based on defined rules."""
    path: Deprecated202007GetSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: update_smart_collection_202007
class Deprecated202007UpdateSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to update. This ID is required to target the specific smart collection for modification.")
class Deprecated202007UpdateSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Updates an existing smart collection by its ID. Use this to modify smart collection properties such as title, rules, and other configuration settings."""
    path: Deprecated202007UpdateSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: delete_smart_collection_202007
class Deprecated202007DeleteSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to delete.")
class Deprecated202007DeleteSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Permanently removes a smart collection from the store. This action cannot be undone."""
    path: Deprecated202007DeleteSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: list_tender_transactions_202007
class Deprecated202007GetTenderTransactionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250 (defaults to 50).")
    processed_at_min: Any | None = Field(default=None, description="Filter to show only tender transactions processed on or after this date (ISO 8601 format).")
    processed_at_max: Any | None = Field(default=None, description="Filter to show only tender transactions processed on or before this date (ISO 8601 format).")
    order: Any | None = Field(default=None, description="Sort results by processed_at timestamp in either ascending or descending order.")
class Deprecated202007GetTenderTransactionsRequest(StrictModel):
    """Retrieves a paginated list of tender transactions. Results are paginated using link headers in the response; use the provided links to navigate between pages."""
    query: Deprecated202007GetTenderTransactionsRequestQuery | None = None

# Operation: get_theme_202007
class Deprecated202007GetThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to retrieve.")
class Deprecated202007GetThemesParamThemeIdRequest(StrictModel):
    """Retrieves a single theme by its ID from the Shopify online store."""
    path: Deprecated202007GetThemesParamThemeIdRequestPath

# Operation: update_theme_legacy
class Deprecated202007UpdateThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to update. This ID is returned when a theme is created and is required to target the specific theme for modification.")
class Deprecated202007UpdateThemesParamThemeIdRequest(StrictModel):
    """Updates the configuration and settings of an existing theme in the Shopify store. Use this to modify theme properties after creation."""
    path: Deprecated202007UpdateThemesParamThemeIdRequestPath

# Operation: delete_theme_2020_07
class Deprecated202007DeleteThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to delete, returned as a string by the Shopify API.")
class Deprecated202007DeleteThemesParamThemeIdRequest(StrictModel):
    """Permanently deletes a theme from the Shopify store. The theme must not be the currently active theme."""
    path: Deprecated202007DeleteThemesParamThemeIdRequestPath

# Operation: get_theme_asset_deprecated
class Deprecated202007GetThemesParamThemeIdAssetsRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme containing the asset to retrieve.")
class Deprecated202007GetThemesParamThemeIdAssetsRequestQuery(StrictModel):
    asset_key: str | None = Field(default=None, validation_alias="asset[key]", serialization_alias="asset[key]", description="The key path of the asset file to retrieve (e.g., templates/index.liquid). This parameter is required to specify which asset to fetch from the theme.")
class Deprecated202007GetThemesParamThemeIdAssetsRequest(StrictModel):
    """Retrieves a single asset file from a theme by its key identifier. The asset key must be provided as a query parameter to specify which theme asset to retrieve."""
    path: Deprecated202007GetThemesParamThemeIdAssetsRequestPath
    query: Deprecated202007GetThemesParamThemeIdAssetsRequestQuery | None = None

# Operation: delete_theme_asset_202007
class Deprecated202007DeleteThemesParamThemeIdAssetsRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme from which the asset will be deleted.")
class Deprecated202007DeleteThemesParamThemeIdAssetsRequestQuery(StrictModel):
    asset_key: str | None = Field(default=None, validation_alias="asset[key]", serialization_alias="asset[key]", description="The key (file path) of the asset to delete from the theme. This identifies which specific asset file to remove.")
class Deprecated202007DeleteThemesParamThemeIdAssetsRequest(StrictModel):
    """Removes a specific asset file from a Shopify theme. The asset is identified by its key within the theme."""
    path: Deprecated202007DeleteThemesParamThemeIdAssetsRequestPath
    query: Deprecated202007DeleteThemesParamThemeIdAssetsRequestQuery | None = None

# Operation: list_webhooks_legacy_202007
class Deprecated202007GetWebhooksRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter webhook subscriptions to only those sending POST requests to this specific URI.")
    limit: Any | None = Field(default=None, description="Maximum number of webhook subscriptions to return per request, between 1 and 250 (defaults to 50).")
    topic: Any | None = Field(default=None, description="Filter webhook subscriptions by topic name. Refer to the webhook topic property documentation for valid topic values.")
class Deprecated202007GetWebhooksRequest(StrictModel):
    """Retrieves a list of webhook subscriptions configured for your Shopify store. Results are paginated using link headers in the response."""
    query: Deprecated202007GetWebhooksRequestQuery | None = None

# Operation: count_webhooks_202007
class Deprecated202007GetWebhooksCountRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter results to webhook subscriptions that deliver POST requests to this specific URI.")
    topic: Any | None = Field(default=None, description="Filter results to webhook subscriptions with a specific topic. Refer to the webhook topic property documentation for valid topic values.")
class Deprecated202007GetWebhooksCountRequest(StrictModel):
    """Retrieves the total count of webhook subscriptions configured in the Shopify store, with optional filtering by delivery address or topic."""
    query: Deprecated202007GetWebhooksCountRequestQuery | None = None

# Operation: get_application_charge
class GetApplicationChargesParamApplicationChargeIdRequestPath(StrictModel):
    application_charge_id: str = Field(default=..., description="The unique identifier of the application charge to retrieve.")
class GetApplicationChargesParamApplicationChargeIdRequest(StrictModel):
    """Retrieves the details of a specific application charge by its ID, including status, price, and billing information."""
    path: GetApplicationChargesParamApplicationChargeIdRequestPath

# Operation: get_application_credit
class GetApplicationCreditsParamApplicationCreditIdRequestPath(StrictModel):
    application_credit_id: str = Field(default=..., description="The unique identifier of the application credit to retrieve.")
class GetApplicationCreditsParamApplicationCreditIdRequest(StrictModel):
    """Retrieves the details of a single application credit by its ID. Use this to fetch information about a specific credit issued to an app."""
    path: GetApplicationCreditsParamApplicationCreditIdRequestPath

# Operation: list_article_tags
class GetArticlesTagsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of tags to return in the response. Limits the size of the result set.")
    popular: Any | None = Field(default=None, description="When included, sorts tags by popularity in descending order (most popular first). Omit this parameter to retrieve tags in default order.")
class GetArticlesTagsRequest(StrictModel):
    """Retrieves all tags used across articles in the online store. Results can be optionally filtered by count and sorted by popularity."""
    query: GetArticlesTagsRequestQuery | None = None

# Operation: list_assigned_fulfillment_orders
class GetAssignedFulfillmentOrdersRequestQuery(StrictModel):
    assignment_status: Any | None = Field(default=None, description="Filter results by the fulfillment request status: use 'cancellation_requested' for orders where the merchant has requested cancellation, 'fulfillment_requested' for pending fulfillment requests, or 'fulfillment_accepted' for orders ready to be fulfilled.")
    location_ids: Any | None = Field(default=None, description="Limit results to fulfillment orders assigned to specific locations by providing their location IDs as a comma-separated list or array. Omit to retrieve orders from all assigned locations.")
class GetAssignedFulfillmentOrdersRequest(StrictModel):
    """Retrieves fulfillment orders assigned to your app on the shop, optionally filtered by assignment status and location. Use this to monitor fulfillment requests, acceptances, and cancellations across your assigned locations."""
    query: GetAssignedFulfillmentOrdersRequestQuery | None = None

# Operation: list_articles
class GetBlogsParamBlogIdArticlesRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog from which to retrieve articles.")
class GetBlogsParamBlogIdArticlesRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of articles to return per request, between 1 and 250 (defaults to 50).")
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: 'published' for published articles only, 'unpublished' for unpublished articles only, or 'any' for all articles regardless of status (defaults to 'any').")
    handle: Any | None = Field(default=None, description="Retrieve a single article by its URL-friendly handle identifier.")
    tag: Any | None = Field(default=None, description="Filter articles to only those tagged with a specific tag.")
    author: Any | None = Field(default=None, description="Filter articles to only those authored by a specific author.")
class GetBlogsParamBlogIdArticlesRequest(StrictModel):
    """Retrieves a paginated list of articles from a specific blog. Uses cursor-based pagination via response headers; the page parameter is not supported."""
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
class GetBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Retrieves a single article from a blog by its ID. Returns the complete article resource including content, metadata, and publishing details."""
    path: GetBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: update_article
class UpdateBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article to update.")
    article_id: str = Field(default=..., description="The unique identifier of the article to update.")
class UpdateBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Updates an existing article within a blog. Modify article content, metadata, and other properties by providing the blog and article identifiers."""
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
    """Retrieves the details of a specific carrier service by its unique identifier. Use this to fetch configuration and capabilities for a single shipping carrier integration."""
    path: GetCarrierServicesParamCarrierServiceIdRequestPath

# Operation: update_carrier_service
class UpdateCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to update.")
class UpdateCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Updates an existing carrier service configuration. Only the app that originally created the carrier service can modify it."""
    path: UpdateCarrierServicesParamCarrierServiceIdRequestPath

# Operation: delete_carrier_service
class DeleteCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to delete. This ID is returned when the carrier service is created.")
class DeleteCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Permanently deletes a carrier service from the store. This removes the shipping method and all associated configurations."""
    path: DeleteCarrierServicesParamCarrierServiceIdRequestPath

# Operation: get_abandoned_checkouts_count
class GetCheckoutsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count by checkout status. Use 'open' to count only active abandoned checkouts, or 'closed' to count only completed/closed abandoned checkouts. Defaults to 'open' if not specified.")
class GetCheckoutsCountRequest(StrictModel):
    """Retrieves the count of abandoned checkouts from the past 90 days, optionally filtered by checkout status."""
    query: GetCheckoutsCountRequestQuery | None = None

# Operation: get_collection_listing
class GetCollectionListingsParamCollectionListingIdRequestPath(StrictModel):
    collection_listing_id: str = Field(default=..., description="The unique identifier of the collection listing to retrieve.")
class GetCollectionListingsParamCollectionListingIdRequest(StrictModel):
    """Retrieve details for a specific collection listing that is published to your sales channel app, including visibility and configuration information."""
    path: GetCollectionListingsParamCollectionListingIdRequestPath

# Operation: publish_collection_to_sales_channel
class UpdateCollectionListingsParamCollectionListingIdRequestPath(StrictModel):
    collection_listing_id: str = Field(default=..., description="The unique identifier of the collection listing to update or create for publishing to the sales channel.")
class UpdateCollectionListingsParamCollectionListingIdRequest(StrictModel):
    """Publish a collection to your sales channel by creating a collection listing. This makes the collection visible and available through your app."""
    path: UpdateCollectionListingsParamCollectionListingIdRequestPath

# Operation: delete_collection_listing
class DeleteCollectionListingsParamCollectionListingIdRequestPath(StrictModel):
    collection_listing_id: str = Field(default=..., description="The unique identifier of the collection listing to delete. This ID represents the specific publication of a collection to a sales channel.")
class DeleteCollectionListingsParamCollectionListingIdRequest(StrictModel):
    """Remove a collection listing to unpublish a collection from your sales channel or app. This operation deletes the listing relationship without affecting the underlying collection."""
    path: DeleteCollectionListingsParamCollectionListingIdRequestPath

# Operation: list_collection_product_ids
class GetCollectionListingsParamCollectionListingIdProductIdsRequestPath(StrictModel):
    collection_listing_id: str = Field(default=..., description="The unique identifier of the collection listing whose published products you want to retrieve.")
class GetCollectionListingsParamCollectionListingIdProductIdsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of product IDs to return per request, ranging from 1 to 1000 (defaults to 50).")
class GetCollectionListingsParamCollectionListingIdProductIdsRequest(StrictModel):
    """Retrieve the product IDs that are published to a specific collection. Results are paginated using link headers in the response."""
    path: GetCollectionListingsParamCollectionListingIdProductIdsRequestPath
    query: GetCollectionListingsParamCollectionListingIdProductIdsRequestQuery | None = None

# Operation: get_collection
class GetCollectionsParamCollectionIdRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection to retrieve.")
class GetCollectionsParamCollectionIdRequest(StrictModel):
    """Retrieves the details of a single collection by its ID, including metadata such as name, description, and product associations."""
    path: GetCollectionsParamCollectionIdRequestPath

# Operation: list_collection_products
class GetCollectionsParamCollectionIdProductsRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection whose products you want to retrieve.")
class GetCollectionsParamCollectionIdProductsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of products to return per request, ranging from 1 to 250 products (defaults to 50 if not specified).")
class GetCollectionsParamCollectionIdProductsRequest(StrictModel):
    """Retrieve products belonging to a specific collection, sorted according to the collection's configured sort order. Results are paginated using link-based navigation provided in response headers."""
    path: GetCollectionsParamCollectionIdProductsRequestPath
    query: GetCollectionsParamCollectionIdProductsRequestQuery | None = None

# Operation: list_collects
class GetCollectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of collects to return per request, between 1 and 250. Defaults to 50 if not specified.")
class GetCollectsRequest(StrictModel):
    """Retrieves a paginated list of collects (product-to-collection associations) from the store. Uses cursor-based pagination via response headers; the limit parameter controls batch size."""
    query: GetCollectsRequestQuery | None = None

# Operation: get_collects_count
class GetCollectsCountRequestQuery(StrictModel):
    collection_id: int | None = Field(default=None, description="Filter the count to only include collects within a specific collection. If omitted, returns the count of all collects across the store.")
class GetCollectsCountRequest(StrictModel):
    """Retrieves the total count of collects (product-to-collection associations) in the store, optionally filtered by a specific collection."""
    query: GetCollectsCountRequestQuery | None = None

# Operation: get_collect
class GetCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect to retrieve.")
class GetCollectsParamCollectIdRequest(StrictModel):
    """Retrieves a specific product collection by its ID. Use this to fetch detailed information about a single collect resource."""
    path: GetCollectsParamCollectIdRequestPath

# Operation: remove_product_from_collection
class DeleteCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect relationship to remove. This ID represents the link between a product and a collection.")
class DeleteCollectsParamCollectIdRequest(StrictModel):
    """Removes a product from a collection by deleting the collect relationship. This operation unlinks a product from a specific collection without affecting the product or collection itself."""
    path: DeleteCollectsParamCollectIdRequestPath

# Operation: get_country
class GetCountriesParamCountryIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country to retrieve. This is a numeric ID assigned by Shopify.")
class GetCountriesParamCountryIdRequest(StrictModel):
    """Retrieves detailed information about a specific country, including provinces, taxes, and shipping settings configured in the Shopify store."""
    path: GetCountriesParamCountryIdRequestPath

# Operation: delete_country
class DeleteCountriesParamCountryIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country to delete. This is a numeric ID assigned by Shopify.")
class DeleteCountriesParamCountryIdRequest(StrictModel):
    """Permanently deletes a country from the store's shipping and tax configuration. This action cannot be undone."""
    path: DeleteCountriesParamCountryIdRequestPath

# Operation: list_provinces_for_country
class GetCountriesParamCountryIdProvincesRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve provinces. This ID must correspond to a valid country in the Shopify system.")
class GetCountriesParamCountryIdProvincesRequest(StrictModel):
    """Retrieves a list of provinces or states for a specific country. Use this to populate province/state selectors or validate province information for a given country."""
    path: GetCountriesParamCountryIdProvincesRequestPath

# Operation: get_province_count_for_country
class GetCountriesParamCountryIdProvincesCountRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve the province count.")
class GetCountriesParamCountryIdProvincesCountRequest(StrictModel):
    """Retrieves the total count of provinces or states for a specified country. Useful for understanding administrative divisions available in a particular country."""
    path: GetCountriesParamCountryIdProvincesCountRequestPath

# Operation: get_province_for_country
class GetCountriesParamCountryIdProvincesParamProvinceIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier for the country. This ID is used to scope the province lookup to the correct country.")
    province_id: str = Field(default=..., description="The unique identifier for the province within the specified country. This ID identifies which province's details to retrieve.")
class GetCountriesParamCountryIdProvincesParamProvinceIdRequest(StrictModel):
    """Retrieves detailed information about a specific province within a country. Use this to fetch province data such as name, code, and tax information for a given country."""
    path: GetCountriesParamCountryIdProvincesParamProvinceIdRequestPath

# Operation: list_custom_collections
class GetCustomCollectionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 if not specified.")
    ids: Any | None = Field(default=None, description="Filter results to only collections with IDs matching this comma-separated list of collection IDs.")
    title: Any | None = Field(default=None, description="Filter results to only collections with an exact title match.")
    product_id: Any | None = Field(default=None, description="Filter results to only collections that contain a specific product, identified by product ID.")
    handle: Any | None = Field(default=None, description="Filter results by the collection's URL-friendly handle identifier.")
    published_status: Any | None = Field(default=None, description="Filter by publication status: 'published' for published collections only, 'unpublished' for unpublished collections only, or 'any' for all collections regardless of status. Defaults to 'any'.")
class GetCustomCollectionsRequest(StrictModel):
    """Retrieves a list of custom collections with optional filtering and pagination. Results are paginated using link headers in the response; the page parameter is not supported."""
    query: GetCustomCollectionsRequestQuery | None = None

# Operation: count_custom_collections
class GetCustomCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter the count to include only custom collections with this exact title.")
    product_id: Any | None = Field(default=None, description="Filter the count to include only custom collections that contain the specified product.")
    published_status: Any | None = Field(default=None, description="Filter the count by publication status: 'published' for published collections only, 'unpublished' for unpublished collections only, or 'any' for all collections regardless of status. Defaults to 'any'.")
class GetCustomCollectionsCountRequest(StrictModel):
    """Retrieves the total count of custom collections in the store, with optional filtering by title, product inclusion, or published status."""
    query: GetCustomCollectionsCountRequestQuery | None = None

# Operation: get_custom_collection
class GetCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to retrieve.")
class GetCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Retrieves the details of a single custom collection by its ID, including its products, metadata, and configuration."""
    path: GetCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: update_custom_collection
class UpdateCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to update. This ID is returned when the collection is created and is required to target the specific collection for modification.")
class UpdateCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Updates the properties of an existing custom collection, such as title, description, image, or sorting rules. Use this to modify collection metadata and organization settings."""
    path: UpdateCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: delete_custom_collection
class DeleteCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to delete.")
class DeleteCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Permanently deletes a custom collection from the store. This action cannot be undone."""
    path: DeleteCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: list_customers
class GetCustomersRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only include customers with the specified IDs. Provide as a comma-separated list of customer ID values.")
    limit: Any | None = Field(default=None, description="Maximum number of customer records to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
class GetCustomersRequest(StrictModel):
    """Retrieves a paginated list of customers from the store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: GetCustomersRequestQuery | None = None

# Operation: search_customers
class GetCustomersSearchRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="Specifies the field and direction to sort results. Use format: field_name ASC or DESC (e.g., last_order_date DESC). Defaults to sorting by last order date in descending order.")
    query: Any | None = Field(default=None, description="The search query text to match against customer data such as names, emails, and other customer attributes.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, ranging from 1 to 250. Defaults to 50 results.")
class GetCustomersSearchRequest(StrictModel):
    """Searches for customers in the shop by matching a query against customer data. Results are paginated using link-based navigation provided in response headers."""
    query: GetCustomersSearchRequestQuery | None = None

# Operation: get_customer
class GetCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to retrieve. This is a numeric ID assigned by Shopify.")
class GetCustomersParamCustomerIdRequest(StrictModel):
    """Retrieves detailed information for a single customer by their unique identifier. Use this to fetch customer profile data including contact information, addresses, and account details."""
    path: GetCustomersParamCustomerIdRequestPath

# Operation: update_customer
class UpdateCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to update. This is a required string value that identifies which customer record to modify.")
class UpdateCustomersParamCustomerIdRequest(StrictModel):
    """Updates an existing customer's information in Shopify. Provide the customer ID and the fields you want to modify in the request body."""
    path: UpdateCustomersParamCustomerIdRequestPath

# Operation: delete_customer
class DeleteCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to delete. This is a numeric ID assigned by Shopify.")
class DeleteCustomersParamCustomerIdRequest(StrictModel):
    """Permanently deletes a customer from the store. Note that a customer cannot be deleted if they have any existing orders associated with their account."""
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
    """Retrieves all addresses associated with a specific customer. Uses cursor-based pagination via response headers; page parameters are not supported."""
    path: GetCustomersParamCustomerIdAddressesRequestPath

# Operation: create_address_for_customer
class CreateCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer for whom the address is being created.")
class CreateCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Creates a new address for a customer. The address will be added to the customer's address book and can be used for shipping or billing purposes."""
    path: CreateCustomersParamCustomerIdAddressesRequestPath

# Operation: bulk_update_customer_addresses
class UpdateCustomersParamCustomerIdAddressesSetRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses will be modified.")
class UpdateCustomersParamCustomerIdAddressesSetRequestQuery(StrictModel):
    address_ids: int | None = Field(default=None, validation_alias="address_ids[]", serialization_alias="address_ids[]", description="Array of address IDs to target for the bulk operation. The order of IDs may affect processing sequence depending on the operation type.")
    operation: str | None = Field(default=None, description="The type of bulk operation to perform on the specified addresses (e.g., delete, set as default). Consult API documentation for valid operation values.")
class UpdateCustomersParamCustomerIdAddressesSetRequest(StrictModel):
    """Performs bulk operations on multiple addresses for a specific customer, allowing you to update, delete, or modify address records in a single request."""
    path: UpdateCustomersParamCustomerIdAddressesSetRequestPath
    query: UpdateCustomersParamCustomerIdAddressesSetRequestQuery | None = None

# Operation: get_customer_address
class GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who owns the address.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to retrieve.")
class GetCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Retrieves the details of a specific address associated with a customer account."""
    path: GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: update_customer_address
class UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being updated.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to update for the customer.")
class UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Updates an existing address for a specific customer. Provide the customer ID and address ID to modify the address details."""
    path: UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: delete_customer_address
class DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being removed.")
    address_id: str = Field(default=..., description="The unique identifier of the address to be deleted from the customer's address list.")
class DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Permanently removes a specific address from a customer's address list. The address will no longer be available for that customer."""
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
    """Retrieves all orders for a specific customer. Supports filtering and sorting through standard Order resource query parameters."""
    path: GetCustomersParamCustomerIdOrdersRequestPath

# Operation: send_customer_invite
class CreateCustomersParamCustomerIdSendInviteRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who will receive the account invite.")
class CreateCustomersParamCustomerIdSendInviteRequest(StrictModel):
    """Sends an account invitation email to a customer, allowing them to create or access their account on the store."""
    path: CreateCustomersParamCustomerIdSendInviteRequestPath

# Operation: lookup_discount_code_location
class GetDiscountCodesLookupRequestQuery(StrictModel):
    code: str | None = Field(default=None, description="The discount code to look up (e.g. 'SUMMER20')")
class GetDiscountCodesLookupRequest(StrictModel):
    """Retrieves the location URI of a discount code. The discount code's location is returned in the HTTP Location header rather than in the response body, allowing you to fetch the full discount code resource from the returned URI."""
    query: GetDiscountCodesLookupRequestQuery | None = None

# Operation: list_events
class GetEventsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of events to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
    filter_: Any | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filters events to show only those matching the specified criteria. Use this to narrow results to specific event types or conditions.")
    verb: Any | None = Field(default=None, description="Filters events to show only those of a specific type or action (e.g., 'create', 'update', 'delete'). Narrows results to events matching the specified verb.")
class GetEventsRequest(StrictModel):
    """Retrieves a paginated list of events from the store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: GetEventsRequestQuery | None = None

# Operation: get_event
class GetEventsParamEventIdRequestPath(StrictModel):
    event_id: str = Field(default=..., description="The unique identifier of the event to retrieve. This ID is returned when events are listed or created.")
class GetEventsParamEventIdRequest(StrictModel):
    """Retrieves a single event by its unique identifier. Use this to fetch detailed information about a specific event that occurred in your Shopify store."""
    path: GetEventsParamEventIdRequestPath

# Operation: get_fulfillment_order
class GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to retrieve.")
class GetFulfillmentOrdersParamFulfillmentOrderIdRequest(StrictModel):
    """Retrieves the details of a specific fulfillment order by its ID, including order status, line items, and fulfillment requirements."""
    path: GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath

# Operation: cancel_fulfillment_order
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel. This ID references a specific fulfillment order within your Shopify store.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest(StrictModel):
    """Cancels a fulfillment order, marking it as no longer needed for processing. This operation prevents further fulfillment actions on the specified order."""
    path: CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath

# Operation: send_fulfillment_order_cancellation_request
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel. This ID references a specific fulfillment order in the system.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for the cancellation request. This provides context to the fulfillment service about why the order is being cancelled.")
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
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which you are rejecting the cancellation request.")
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
    """Sends a fulfillment request to the fulfillment service for a specific fulfillment order, optionally specifying which line items to fulfill and including a message for the fulfillment service."""
    path: CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath
    query: CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery | None = None

# Operation: accept_fulfillment_request
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request is being accepted.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message providing context or reasoning for accepting the fulfillment request.")
class CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest(StrictModel):
    """Accepts a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, confirming that the fulfillment service will proceed with fulfilling the order."""
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

# Operation: list_fulfillments_for_fulfillment_order
class GetFulfillmentOrdersParamFulfillmentOrderIdFulfillmentsRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to retrieve associated fulfillments.")
class GetFulfillmentOrdersParamFulfillmentOrderIdFulfillmentsRequest(StrictModel):
    """Retrieves all fulfillments associated with a specific fulfillment order, including fulfillment details and status information."""
    path: GetFulfillmentOrdersParamFulfillmentOrderIdFulfillmentsRequestPath

# Operation: list_locations_for_fulfillment_order_move
class GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to retrieve available move destinations.")
class GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest(StrictModel):
    """Retrieves all locations where a fulfillment order can be moved to, sorted alphabetically by location name. Use this to determine valid destination locations before initiating a fulfillment order transfer."""
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

# Operation: get_fulfillment_service
class GetFulfillmentServicesParamFulfillmentServiceIdRequestPath(StrictModel):
    fulfillment_service_id: str = Field(default=..., description="The unique identifier of the fulfillment service to retrieve. This ID is assigned by Shopify when the fulfillment service is created or integrated.")
class GetFulfillmentServicesParamFulfillmentServiceIdRequest(StrictModel):
    """Retrieve detailed information about a specific fulfillment service by its ID. Use this to fetch configuration, capabilities, and status of a fulfillment service integrated with your Shopify store."""
    path: GetFulfillmentServicesParamFulfillmentServiceIdRequestPath

# Operation: update_fulfillment_service
class UpdateFulfillmentServicesParamFulfillmentServiceIdRequestPath(StrictModel):
    fulfillment_service_id: str = Field(default=..., description="The unique identifier of the fulfillment service to update. This ID is returned when a fulfillment service is created and is required to target the correct service for modification.")
class UpdateFulfillmentServicesParamFulfillmentServiceIdRequest(StrictModel):
    """Update the configuration and settings of a specific fulfillment service. This allows you to modify fulfillment service details such as name, callback URLs, and other operational parameters."""
    path: UpdateFulfillmentServicesParamFulfillmentServiceIdRequestPath

# Operation: delete_fulfillment_service
class DeleteFulfillmentServicesParamFulfillmentServiceIdRequestPath(StrictModel):
    fulfillment_service_id: str = Field(default=..., description="The unique identifier of the fulfillment service to delete.")
class DeleteFulfillmentServicesParamFulfillmentServiceIdRequest(StrictModel):
    """Permanently delete a fulfillment service from your Shopify store. This removes the service and its associated configuration."""
    path: DeleteFulfillmentServicesParamFulfillmentServiceIdRequestPath

# Operation: cancel_fulfillment_direct
class CreateFulfillmentsParamFulfillmentIdCancelRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to cancel. This must be a valid fulfillment ID from your Shopify store.")
class CreateFulfillmentsParamFulfillmentIdCancelRequest(StrictModel):
    """Cancels an existing fulfillment, preventing further processing or shipment of the associated items."""
    path: CreateFulfillmentsParamFulfillmentIdCancelRequestPath

# Operation: update_fulfillment_tracking
class CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment whose tracking information should be updated.")
class CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest(StrictModel):
    """Updates tracking information for a specific fulfillment, allowing you to modify shipment tracking details after the fulfillment has been created."""
    path: CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath

# Operation: list_gift_cards
class GetGiftCardsRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter results by gift card status. Use 'enabled' to show only active gift cards or 'disabled' to show only inactive gift cards. Omit to retrieve all gift cards regardless of status.")
    limit: Any | None = Field(default=None, description="Maximum number of gift cards to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
class GetGiftCardsRequest(StrictModel):
    """Retrieves a paginated list of gift cards from the store. Results are paginated using cursor-based links provided in the response header rather than page parameters."""
    query: GetGiftCardsRequestQuery | None = None

# Operation: get_gift_cards_count
class GetGiftCardsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count to only include gift cards with a specific status: enabled for active gift cards, or disabled for inactive gift cards. Omit this parameter to count all gift cards regardless of status.")
class GetGiftCardsCountRequest(StrictModel):
    """Retrieves the total count of gift cards in the store, optionally filtered by their enabled or disabled status."""
    query: GetGiftCardsCountRequestQuery | None = None

# Operation: search_gift_cards
class GetGiftCardsSearchRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="The field and direction to sort results by. Defaults to most recently disabled gift cards first. Specify a field name followed by ASC or DESC.")
    query: Any | None = Field(default=None, description="The search query text to match against indexed gift card fields including created_at, updated_at, disabled_at, balance, initial_value, amount_spent, email, and last_characters.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 results.")
class GetGiftCardsSearchRequest(StrictModel):
    """Search for gift cards matching a query across indexed fields like balance, email, and creation date. Results are paginated using link-based navigation provided in response headers."""
    query: GetGiftCardsSearchRequestQuery | None = None

# Operation: get_gift_card
class GetGiftCardsParamGiftCardIdRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to retrieve.")
class GetGiftCardsParamGiftCardIdRequest(StrictModel):
    """Retrieves the details of a single gift card by its unique identifier. Use this to fetch information such as balance, expiration date, and creation details for a specific gift card."""
    path: GetGiftCardsParamGiftCardIdRequestPath

# Operation: update_gift_card
class UpdateGiftCardsParamGiftCardIdRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to update.")
class UpdateGiftCardsParamGiftCardIdRequest(StrictModel):
    """Updates an existing gift card's expiry date, note, and template suffix. The gift card's balance cannot be modified through this API."""
    path: UpdateGiftCardsParamGiftCardIdRequestPath

# Operation: disable_gift_card
class CreateGiftCardsParamGiftCardIdDisableRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to disable.")
class CreateGiftCardsParamGiftCardIdDisableRequest(StrictModel):
    """Permanently disables a gift card, preventing it from being used for future transactions. This action cannot be reversed."""
    path: CreateGiftCardsParamGiftCardIdDisableRequestPath

# Operation: list_inventory_items
class GetInventoryItemsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of inventory items to return per request. Accepts values between 1 and 250, with a default of 50 if not specified.")
    ids: int | None = Field(default=None, description="Filter results to only inventory items with the specified IDs. Provide one or more comma-separated integer IDs to retrieve specific items.")
class GetInventoryItemsRequest(StrictModel):
    """Retrieves a paginated list of inventory items from the store. Results are paginated using cursor-based links provided in the response header; use the link relations to navigate pages rather than the page parameter."""
    query: GetInventoryItemsRequestQuery | None = None

# Operation: get_inventory_item
class GetInventoryItemsParamInventoryItemIdRequestPath(StrictModel):
    inventory_item_id: str = Field(default=..., description="The unique identifier of the inventory item to retrieve. This ID corresponds to a specific product variant's inventory record.")
class GetInventoryItemsParamInventoryItemIdRequest(StrictModel):
    """Retrieves detailed information about a single inventory item by its unique identifier. Use this to fetch inventory tracking data for a specific product variant."""
    path: GetInventoryItemsParamInventoryItemIdRequestPath

# Operation: update_inventory_item
class UpdateInventoryItemsParamInventoryItemIdRequestPath(StrictModel):
    inventory_item_id: str = Field(default=..., description="The unique identifier of the inventory item to update. This ID is required to target the specific inventory item for modification.")
class UpdateInventoryItemsParamInventoryItemIdRequest(StrictModel):
    """Updates an existing inventory item in your Shopify store. Modify properties like SKU, tracked status, and cost for a specific inventory item."""
    path: UpdateInventoryItemsParamInventoryItemIdRequestPath

# Operation: list_inventory_levels
class GetInventoryLevelsRequestQuery(StrictModel):
    inventory_item_ids: Any | None = Field(default=None, description="Comma-separated list of inventory item IDs to filter results. Maximum of 50 IDs per request.")
    location_ids: Any | None = Field(default=None, description="Comma-separated list of location IDs to filter results. Maximum of 50 IDs per request. Use the Location resource to find location IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of inventory levels to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
class GetInventoryLevelsRequest(StrictModel):
    """Retrieves inventory levels across your store's locations. You must filter by at least one inventory item ID or location ID to retrieve results."""
    query: GetInventoryLevelsRequestQuery | None = None

# Operation: delete_inventory_level
class DeleteInventoryLevelsRequestQuery(StrictModel):
    inventory_item_id: int | None = Field(default=None, description="The unique identifier of the inventory item whose level should be deleted. Required to identify which item's inventory level to remove.")
    location_id: int | None = Field(default=None, description="The unique identifier of the location where the inventory level should be deleted. Required to specify which location's inventory connection should be removed.")
class DeleteInventoryLevelsRequest(StrictModel):
    """Removes an inventory level for a specific inventory item at a location. This disconnects the item from that location; note that every inventory item must maintain at least one inventory level, so you must connect the item to another location before deleting its last level."""
    query: DeleteInventoryLevelsRequestQuery | None = None

# Operation: get_location
class GetLocationsParamLocationIdRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location to retrieve. This ID is assigned by Shopify when the location is created.")
class GetLocationsParamLocationIdRequest(StrictModel):
    """Retrieves detailed information about a specific inventory location by its ID. Use this to fetch location details such as name, address, and fulfillment capabilities."""
    path: GetLocationsParamLocationIdRequestPath

# Operation: list_inventory_levels_for_location
class GetLocationsParamLocationIdInventoryLevelsRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location for which to retrieve inventory levels.")
class GetLocationsParamLocationIdInventoryLevelsRequest(StrictModel):
    """Retrieves a paginated list of inventory levels for a specific location. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""
    path: GetLocationsParamLocationIdInventoryLevelsRequestPath

# Operation: list_metafields_for_product_image
class GetMetafieldsRequestQuery(StrictModel):
    metafield_owner_id: int | None = Field(default=None, validation_alias="metafield[owner_id]", serialization_alias="metafield[owner_id]", description="The unique identifier of the Product Image resource that owns the metafields. Required when filtering metafields for a specific image.")
    metafield_owner_resource: str | None = Field(default=None, validation_alias="metafield[owner_resource]", serialization_alias="metafield[owner_resource]", description="The resource type that owns the metafields. For this operation, this should be set to 'product_image' to retrieve metafields belonging to a Product Image.")
class GetMetafieldsRequest(StrictModel):
    """Retrieves all metafields associated with a specific Product Image resource. Use the owner_id and owner_resource parameters to filter metafields for a particular image."""
    query: GetMetafieldsRequestQuery | None = None

# Operation: get_metafield
class GetMetafieldsParamMetafieldIdRequestPath(StrictModel):
    metafield_id: str = Field(default=..., description="The unique identifier of the metafield to retrieve.")
class GetMetafieldsParamMetafieldIdRequest(StrictModel):
    """Retrieves a single metafield by its ID. Use this to fetch detailed information about a specific metafield attached to a Shopify resource."""
    path: GetMetafieldsParamMetafieldIdRequestPath

# Operation: update_metafield
class UpdateMetafieldsParamMetafieldIdRequestPath(StrictModel):
    metafield_id: str = Field(default=..., description="The unique identifier of the metafield to update. This ID is returned when a metafield is created and is required to target the specific metafield for modification.")
class UpdateMetafieldsParamMetafieldIdRequest(StrictModel):
    """Updates an existing metafield by its ID. Use this to modify metafield properties such as namespace, key, value, and type."""
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
    limit: Any | None = Field(default=None, description="Maximum number of fulfillments to return per request, ranging from 1 to 250 (defaults to 50).")
class GetOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Retrieves all fulfillments associated with a specific order. Results are paginated using link-based navigation provided in response headers rather than page parameters."""
    path: GetOrdersParamOrderIdFulfillmentsRequestPath
    query: GetOrdersParamOrderIdFulfillmentsRequestQuery | None = None

# Operation: create_fulfillment_for_order
class CreateOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the fulfillment. Required to specify which order's line items should be fulfilled.")
class CreateOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Create a fulfillment for an order, marking specified line items as shipped. The fulfillment status depends on the fulfillment service type: manual/custom services set status immediately, while external services queue the fulfillment with pending status until processed."""
    path: CreateOrdersParamOrderIdFulfillmentsRequestPath

# Operation: get_fulfillments_count_for_order
class GetOrdersParamOrderIdFulfillmentsCountRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve the fulfillment count.")
class GetOrdersParamOrderIdFulfillmentsCountRequest(StrictModel):
    """Retrieves the total count of fulfillments associated with a specific order. Useful for understanding how many fulfillment records exist for an order without fetching the full fulfillment details."""
    path: GetOrdersParamOrderIdFulfillmentsCountRequestPath

# Operation: get_fulfillment
class GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to retrieve.")
class GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Retrieve detailed information about a specific fulfillment for an order, including tracking information and line item fulfillment status."""
    path: GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: update_fulfillment
class UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to update.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to update.")
class UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Update fulfillment details for a specific order, such as tracking information or fulfillment status."""
    path: UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: cancel_fulfillment
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to cancel.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to cancel within the specified order.")
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequest(StrictModel):
    """Cancel an active fulfillment for a specific order. This operation prevents further tracking and updates for the fulfillment."""
    path: CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequestPath

# Operation: complete_fulfillment
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to be completed.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to mark as complete.")
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest(StrictModel):
    """Mark a fulfillment as complete, indicating that all items in the fulfillment have been shipped and the order fulfillment process is finished."""
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
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment. This order must exist and be accessible in the store.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment within the specified order. This fulfillment must exist and belong to the given order.")
class CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest(StrictModel):
    """Creates a fulfillment event for a specific fulfillment within an order. Fulfillment events track status changes and milestones in the fulfillment lifecycle, such as preparation, shipment, or delivery notifications."""
    path: CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath

# Operation: get_fulfillment_event
class GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment within the order.")
    event_id: str = Field(default=..., description="The unique identifier of the specific fulfillment event to retrieve.")
class GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsParamEventIdRequest(StrictModel):
    """Retrieves a specific event associated with a fulfillment, such as notifications about shipment status changes or delivery updates."""
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
    """Mark a fulfillment as open, allowing it to receive additional items or changes. This operation transitions a fulfillment from a closed state back to an open state."""
    path: CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequestPath

# Operation: list_order_refunds
class GetOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve refunds.")
class GetOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of refunds to return per request, between 1 and 250 (defaults to 50).")
    in_shop_currency: Any | None = Field(default=None, description="When true, displays refund amounts in the shop's currency for the underlying transaction; defaults to false.")
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
    shipping: Any | None = Field(default=None, description="Shipping refund configuration. Specify either full_refund to refund all remaining shipping, or amount to refund a specific shipping amount (takes precedence over full_refund).")
    refund_line_items: Any | None = Field(default=None, description="A list of line items to refund, each specifying the line_item_id, quantity to refund, restock_type (no_restock, cancel, or return), and location_id (required for cancel or return restock types).")
    transactions: Any | None = Field(default=None, description="A list of transactions to process as refunds. Typically generated by the calculate endpoint.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required for multi-currency orders when an amount property is provided.")
class CreateOrdersParamOrderIdRefundsRequest(StrictModel):
    """Creates a refund for an order. Use the calculate endpoint first to determine the correct transaction amounts. For multi-currency orders, the currency property is required whenever an amount is specified."""
    path: CreateOrdersParamOrderIdRefundsRequestPath
    query: CreateOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: calculate_order_refund
class CreateOrdersParamOrderIdRefundsCalculateRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to calculate the refund.")
class CreateOrdersParamOrderIdRefundsCalculateRequestQuery(StrictModel):
    shipping: Any | None = Field(default=None, description="Shipping refund configuration. Specify either full_refund to refund all remaining shipping costs, or amount to refund a specific shipping amount (takes precedence over full_refund).")
    refund_line_items: Any | None = Field(default=None, description="Array of line items to refund, each specifying the line item ID, quantity to refund, restock instructions (no_restock, cancel, or return), and optionally the location ID where items should be restocked. The endpoint will suggest a suitable location if not provided for return or cancel restocks.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required whenever a shipping amount is specified, particularly important for multi-currency orders.")
class CreateOrdersParamOrderIdRefundsCalculateRequest(StrictModel):
    """Calculate refund transactions for an order based on line items and shipping costs. Use this endpoint to generate accurate refund details before creating an actual refund, including any necessary adjustments to restock instructions."""
    path: CreateOrdersParamOrderIdRefundsCalculateRequestPath
    query: CreateOrdersParamOrderIdRefundsCalculateRequestQuery | None = None

# Operation: get_refund
class GetOrdersParamOrderIdRefundsParamRefundIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the refund.")
    refund_id: str = Field(default=..., description="The unique identifier of the refund to retrieve.")
class GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery(StrictModel):
    in_shop_currency: Any | None = Field(default=None, description="When enabled, displays all monetary amounts in the shop's native currency rather than the transaction currency. Defaults to false.")
class GetOrdersParamOrderIdRefundsParamRefundIdRequest(StrictModel):
    """Retrieves the details of a specific refund for an order, including refund amounts, line items, and transaction information."""
    path: GetOrdersParamOrderIdRefundsParamRefundIdRequestPath
    query: GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery | None = None

# Operation: list_order_risks
class GetOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve associated risks.")
class GetOrdersParamOrderIdRisksRequest(StrictModel):
    """Retrieves all fraud and risk assessments associated with a specific order. This endpoint uses cursor-based pagination via response headers."""
    path: GetOrdersParamOrderIdRisksRequestPath

# Operation: create_order_risk
class CreateOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the risk record. This must be a valid order ID from your Shopify store.")
class CreateOrdersParamOrderIdRisksRequest(StrictModel):
    """Creates a risk assessment record for a specific order. Use this to flag potential issues or concerns associated with an order that may require review or action."""
    path: CreateOrdersParamOrderIdRisksRequestPath

# Operation: get_order_risk
class GetOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk assessment.")
    risk_id: str = Field(default=..., description="The unique identifier of the specific risk record to retrieve.")
class GetOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Retrieves a specific risk assessment associated with an order. Use this to view details about a flagged risk for fraud detection or order validation purposes."""
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
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to be deleted.")
    risk_id: str = Field(default=..., description="The unique identifier of the risk to be deleted from the order.")
class DeleteOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Deletes a specific risk associated with an order. Note that you cannot delete an order risk that was created by another application."""
    path: DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: create_discount_codes_batch
class CreatePriceRulesParamPriceRuleIdBatchRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which discount codes will be created.")
class CreatePriceRulesParamPriceRuleIdBatchRequest(StrictModel):
    """Asynchronously creates up to 100 discount codes for a price rule in a single batch job. Returns a discount code creation job object that can be monitored for completion status, including counts of successful and failed code creations."""
    path: CreatePriceRulesParamPriceRuleIdBatchRequestPath

# Operation: get_discount_code_batch
class GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch job.")
    batch_id: str = Field(default=..., description="The unique identifier of the discount code creation batch job to retrieve.")
class GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest(StrictModel):
    """Retrieves the status and details of a discount code creation job batch for a specific price rule."""
    path: GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath

# Operation: list_discount_codes_for_batch
class GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch.")
    batch_id: str = Field(default=..., description="The unique identifier of the discount code creation batch job to retrieve codes from.")
class GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest(StrictModel):
    """Retrieves all discount codes generated from a specific discount code creation batch job. Results include successfully created codes with populated IDs and codes that failed with error details."""
    path: GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath

# Operation: list_discount_codes_for_price_rule
class GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which to retrieve associated discount codes.")
class GetPriceRulesParamPriceRuleIdDiscountCodesRequest(StrictModel):
    """Retrieve all discount codes associated with a specific price rule. Results are paginated using link-based navigation provided in response headers."""
    path: GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath

# Operation: create_discount_code_for_price_rule
class CreatePriceRulesParamPriceRuleIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule to which this discount code will be attached. This price rule must already exist.")
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
    """Permanently removes a discount code from a price rule. This action cannot be undone."""
    path: DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: list_products
class GetProductsRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only include products with specific IDs. Provide as a comma-separated list of product IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of products to return per page. Defaults to 50 and cannot exceed 250.")
    title: Any | None = Field(default=None, description="Filter results to only include products matching the specified title.")
    vendor: Any | None = Field(default=None, description="Filter results to only include products from a specific vendor.")
    handle: Any | None = Field(default=None, description="Filter results to only include products with the specified handle (URL-friendly identifier).")
    product_type: Any | None = Field(default=None, description="Filter results to only include products of a specific type.")
    status: Any | None = Field(default=None, description="Filter results by product status: active (default) shows only active products, archived shows only archived products, or draft shows only draft products.")
    collection_id: Any | None = Field(default=None, description="Filter results to only include products belonging to a specific collection by collection ID.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: published shows only published products, unpublished shows only unpublished products, or any (default) shows all products regardless of publication status.")
    presentment_currencies: Any | None = Field(default=None, description="Return presentment prices in only the specified currencies. Provide as a comma-separated list of ISO 4217 currency codes.")
class GetProductsRequest(StrictModel):
    """Retrieves a paginated list of products from your store, with support for filtering by various attributes and sorting options. Results are paginated using link-based navigation provided in response headers."""
    query: GetProductsRequestQuery | None = None

# Operation: get_products_count
class GetProductsCountRequestQuery(StrictModel):
    vendor: Any | None = Field(default=None, description="Filter the count to include only products from a specific vendor.")
    product_type: Any | None = Field(default=None, description="Filter the count to include only products of a specific product type.")
    collection_id: Any | None = Field(default=None, description="Filter the count to include only products belonging to a specific collection by its ID.")
    published_status: Any | None = Field(default=None, description="Filter the count by product publication status: use 'published' for only published products, 'unpublished' for only unpublished products, or 'any' to include all products regardless of status (default is 'any').")
class GetProductsCountRequest(StrictModel):
    """Retrieves the total count of products in the store, with optional filtering by vendor, product type, collection, or published status."""
    query: GetProductsCountRequestQuery | None = None

# Operation: get_product
class GetProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to retrieve.")
class GetProductsParamProductIdRequest(StrictModel):
    """Retrieves detailed information for a single product by its ID from the Shopify store."""
    path: GetProductsParamProductIdRequestPath

# Operation: update_product
class UpdateProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to update.")
class UpdateProductsParamProductIdRequest(StrictModel):
    """Updates a product's details, variants, images, and SEO metadata. Use metafields_global_title_tag and metafields_global_description_tag to optimize the product's search engine visibility."""
    path: UpdateProductsParamProductIdRequestPath

# Operation: delete_product
class DeleteProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to delete. This is a numeric ID assigned by Shopify.")
class DeleteProductsParamProductIdRequest(StrictModel):
    """Permanently deletes a product from the store. This action cannot be undone and will remove the product and all associated data."""
    path: DeleteProductsParamProductIdRequestPath

# Operation: list_product_images
class GetProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product whose images you want to retrieve.")
class GetProductsParamProductIdImagesRequest(StrictModel):
    """Retrieve all images associated with a specific product. Returns a collection of image objects containing URLs, alt text, and metadata for the product."""
    path: GetProductsParamProductIdImagesRequestPath

# Operation: create_product_image
class CreateProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to which the image will be added.")
class CreateProductsParamProductIdImagesRequest(StrictModel):
    """Create a new image for a specific product. The image will be added to the product's image gallery and can be used for product display across storefronts."""
    path: CreateProductsParamProductIdImagesRequestPath

# Operation: get_product_images_count
class GetProductsParamProductIdImagesCountRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product for which to retrieve the image count.")
class GetProductsParamProductIdImagesCountRequest(StrictModel):
    """Retrieve the total count of images associated with a specific product. Useful for understanding product image inventory without fetching the full image list."""
    path: GetProductsParamProductIdImagesCountRequestPath

# Operation: get_product_image
class GetProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product that contains the image.")
    image_id: str = Field(default=..., description="The unique identifier of the specific image to retrieve.")
class GetProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Retrieve a specific product image by its ID. Returns detailed metadata for the image including URL, alt text, and position within the product's image gallery."""
    path: GetProductsParamProductIdImagesParamImageIdRequestPath

# Operation: update_product_image
class UpdateProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product that contains the image to be updated.")
    image_id: str = Field(default=..., description="The unique identifier of the image within the product to be updated.")
class UpdateProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Update the properties of an existing product image, such as alt text, position, or other image metadata associated with a specific product."""
    path: UpdateProductsParamProductIdImagesParamImageIdRequestPath

# Operation: delete_product_image
class DeleteProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product containing the image to delete.")
    image_id: str = Field(default=..., description="The unique identifier of the image to delete from the product.")
class DeleteProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Delete a specific image from a product. This removes the image association from the product permanently."""
    path: DeleteProductsParamProductIdImagesParamImageIdRequestPath

# Operation: get_recurring_application_charge
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to retrieve.")
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(StrictModel):
    """Retrieves the details of a single recurring application charge by its ID. Use this to fetch current status, pricing, and other metadata for a specific recurring charge."""
    path: GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath

# Operation: delete_recurring_application_charge
class DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to cancel. This ID is returned when the charge is initially created.")
class DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(StrictModel):
    """Cancels an active recurring application charge for a Shopify app. This operation permanently removes the recurring billing arrangement between the app and the merchant."""
    path: DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath

# Operation: update_recurring_application_charge_capped_amount
class UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to customize.")
class UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery(StrictModel):
    recurring_application_charge_capped_amount: int | None = Field(default=None, validation_alias="recurring_application_charge[capped_amount]", serialization_alias="recurring_application_charge[capped_amount]", description="The new capped amount for the recurring charge. This sets the maximum total amount that will be billed to the merchant for this charge.")
class UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest(StrictModel):
    """Updates the capped amount of an active recurring application charge. This allows you to modify the maximum billing cap for an existing charge without canceling and recreating it."""
    path: UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath
    query: UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery | None = None

# Operation: list_usage_charges_for_recurring_application_charge
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge for which to retrieve usage charges.")
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Retrieves all usage charges associated with a specific recurring application charge. Usage charges represent variable fees billed on top of a recurring application charge."""
    path: GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath

# Operation: create_usage_charge_for_recurring_application_charge
class CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to which this usage charge will be applied. This must be a valid, active recurring application charge ID.")
class CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Creates a usage charge against an existing recurring application charge. Usage charges allow you to bill merchants for variable usage on top of their recurring subscription."""
    path: CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath

# Operation: get_usage_charge_for_recurring_application_charge
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge that contains the usage charge you want to retrieve.")
    usage_charge_id: str = Field(default=..., description="The unique identifier of the specific usage charge to retrieve.")
class GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest(StrictModel):
    """Retrieves a single usage charge associated with a recurring application charge. Use this to fetch details about a specific metered billing charge."""
    path: GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath

# Operation: list_redirects
class GetRedirectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of redirects to return per request, between 1 and 250. Defaults to 50 if not specified.")
    path: Any | None = Field(default=None, description="Filter results to show only redirects with this specific path value.")
    target: Any | None = Field(default=None, description="Filter results to show only redirects with this specific target URL.")
class GetRedirectsRequest(StrictModel):
    """Retrieves a paginated list of URL redirects configured in the store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
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
class GetRedirectsParamRedirectIdRequest(StrictModel):
    """Retrieves a single redirect by its ID from the Shopify online store. Use this to fetch details about a specific URL redirect configuration."""
    path: GetRedirectsParamRedirectIdRequestPath

# Operation: update_redirect
class UpdateRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to update. This ID is returned when the redirect is created and is required to target the specific redirect for modification.")
class UpdateRedirectsParamRedirectIdRequest(StrictModel):
    """Updates an existing redirect in the online store. Modify redirect rules such as the source path and target destination URL."""
    path: UpdateRedirectsParamRedirectIdRequestPath

# Operation: delete_redirect
class DeleteRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to delete.")
class DeleteRedirectsParamRedirectIdRequest(StrictModel):
    """Permanently deletes a redirect from the online store. Once deleted, the redirect cannot be recovered."""
    path: DeleteRedirectsParamRedirectIdRequestPath

# Operation: list_reports
class GetReportsRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to specific reports by providing a comma-separated list of report IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of reports to return per request, between 1 and 250 (defaults to 50).")
class GetReportsRequest(StrictModel):
    """Retrieves a list of reports from the Shopify Admin API. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: GetReportsRequestQuery | None = None

# Operation: create_report
class CreateReportsRequestQuery(StrictModel):
    name: Any | None = Field(default=None, description="The display name for the report. Must not exceed 255 characters.")
    shopify_ql: Any | None = Field(default=None, description="The ShopifyQL query string that defines what data the report will retrieve and analyze.")
class CreateReportsRequest(StrictModel):
    """Creates a new custom report in the Shopify admin. The report can be configured with a name and ShopifyQL query to analyze store data."""
    query: CreateReportsRequestQuery | None = None

# Operation: get_report
class GetReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to retrieve.")
class GetReportsParamReportIdRequest(StrictModel):
    """Retrieves a single report that was created by your app. Use this to fetch details about a specific report by its ID."""
    path: GetReportsParamReportIdRequestPath

# Operation: update_report
class UpdateReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to update. This ID is required to target the specific report for modification.")
class UpdateReportsParamReportIdRequest(StrictModel):
    """Updates an existing report configuration in Shopify Admin. Modify report settings and parameters by providing the report ID."""
    path: UpdateReportsParamReportIdRequestPath

# Operation: delete_report
class DeleteReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to delete. This is a required string value that identifies which report should be removed.")
class DeleteReportsParamReportIdRequest(StrictModel):
    """Permanently deletes a specific report from the Shopify admin. This action cannot be undone."""
    path: DeleteReportsParamReportIdRequestPath

# Operation: list_script_tags
class GetScriptTagsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of script tags to return per request. Accepts values between 1 and 250, with a default of 50 results.")
class GetScriptTagsRequest(StrictModel):
    """Retrieves a paginated list of all script tags in the store. Results are paginated using cursor-based links provided in the response header; use the link relations to navigate pages rather than the limit parameter alone."""
    query: GetScriptTagsRequestQuery | None = None

# Operation: get_script_tag
class GetScriptTagsParamScriptTagIdRequestPath(StrictModel):
    script_tag_id: str = Field(default=..., description="The unique identifier of the script tag to retrieve.")
class GetScriptTagsParamScriptTagIdRequest(StrictModel):
    """Retrieves a single script tag by its ID from the Shopify online store. Use this to fetch details about a specific script tag resource."""
    path: GetScriptTagsParamScriptTagIdRequestPath

# Operation: update_script_tag
class UpdateScriptTagsParamScriptTagIdRequestPath(StrictModel):
    script_tag_id: str = Field(default=..., description="The unique identifier of the script tag to update. This ID is returned when the script tag is created and is required to target the specific tag for modification.")
class UpdateScriptTagsParamScriptTagIdRequest(StrictModel):
    """Updates an existing script tag in the Shopify online store. Modify script tag properties such as source URL, event triggers, or display scope."""
    path: UpdateScriptTagsParamScriptTagIdRequestPath

# Operation: delete_script_tag
class DeleteScriptTagsParamScriptTagIdRequestPath(StrictModel):
    script_tag_id: str = Field(default=..., description="The unique identifier of the script tag to delete.")
class DeleteScriptTagsParamScriptTagIdRequest(StrictModel):
    """Permanently deletes a script tag from the store. This removes the associated script injection from all store pages."""
    path: DeleteScriptTagsParamScriptTagIdRequestPath

# Operation: list_shopify_payments_payouts
class GetShopifyPaymentsPayoutsRequestQuery(StrictModel):
    date_min: Any | None = Field(default=None, description="Filter payouts to include only those made on or after the specified date (inclusive). Use ISO 8601 format.")
    date_max: Any | None = Field(default=None, description="Filter payouts to include only those made on or before the specified date (inclusive). Use ISO 8601 format.")
    status: Any | None = Field(default=None, description="Filter payouts by their current status (e.g., pending, paid, failed, cancelled).")
class GetShopifyPaymentsPayoutsRequest(StrictModel):
    """Retrieves a paginated list of all Shopify Payments payouts ordered by payout date, with the most recent first. Uses cursor-based pagination via response headers."""
    query: GetShopifyPaymentsPayoutsRequestQuery | None = None

# Operation: get_payout
class GetShopifyPaymentsPayoutsParamPayoutIdRequestPath(StrictModel):
    payout_id: str = Field(default=..., description="The unique identifier of the payout to retrieve.")
class GetShopifyPaymentsPayoutsParamPayoutIdRequest(StrictModel):
    """Retrieves detailed information about a specific Shopify Payments payout by its unique identifier."""
    path: GetShopifyPaymentsPayoutsParamPayoutIdRequestPath

# Operation: list_smart_collections
class GetSmartCollectionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of smart collections to return per request. Defaults to 50 and cannot exceed 250.")
    ids: Any | None = Field(default=None, description="Filter results to only smart collections with the specified IDs. Provide as a comma-separated list of numeric IDs.")
    title: Any | None = Field(default=None, description="Filter results to smart collections matching the exact title.")
    product_id: Any | None = Field(default=None, description="Filter results to only smart collections that contain the specified product ID.")
    handle: Any | None = Field(default=None, description="Filter results by the smart collection's URL-friendly handle.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for published collections only, 'unpublished' for unpublished only, or 'any' for all collections. Defaults to 'any'.")
class GetSmartCollectionsRequest(StrictModel):
    """Retrieves a paginated list of smart collections from your store. Results are paginated using link headers in the response."""
    query: GetSmartCollectionsRequestQuery | None = None

# Operation: count_smart_collections
class GetSmartCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter to smart collections with an exact matching title.")
    product_id: Any | None = Field(default=None, description="Filter to smart collections that contain the specified product ID.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for live collections, 'unpublished' for draft collections, or 'any' to include all collections regardless of status. Defaults to 'any'.")
class GetSmartCollectionsCountRequest(StrictModel):
    """Retrieves the total count of smart collections in the store, with optional filtering by title, product inclusion, or published status."""
    query: GetSmartCollectionsCountRequestQuery | None = None

# Operation: get_smart_collection
class GetSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to retrieve.")
class GetSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Retrieves the details of a single smart collection by its ID, including its configuration, products, and metadata."""
    path: GetSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: update_smart_collection
class UpdateSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to update. This ID is returned when the collection is created and is required to target the correct collection for modification.")
class UpdateSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Updates the configuration and rules of an existing smart collection, allowing you to modify its title, conditions, sorting, and other properties."""
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
    products: Any | None = Field(default=None, description="An ordered array of product IDs that should appear at the top of the collection. Passing an empty array clears any previously applied custom sorting.")
    sort_order: Any | None = Field(default=None, description="The sorting method to apply to the collection (e.g., alphabetical, price, newest). If not specified, the current sorting method is retained.")
class UpdateSmartCollectionsParamSmartCollectionIdOrderRequest(StrictModel):
    """Reorder products within a smart collection by specifying a custom product sequence and/or changing the collection's sorting method."""
    path: UpdateSmartCollectionsParamSmartCollectionIdOrderRequestPath
    query: UpdateSmartCollectionsParamSmartCollectionIdOrderRequestQuery | None = None

# Operation: delete_storefront_access_token
class DeleteStorefrontAccessTokensParamStorefrontAccessTokenIdRequestPath(StrictModel):
    storefront_access_token_id: str = Field(default=..., description="The unique identifier of the storefront access token to delete.")
class DeleteStorefrontAccessTokensParamStorefrontAccessTokenIdRequest(StrictModel):
    """Permanently deletes a storefront access token by its ID. This revokes the token's access to the Storefront API."""
    path: DeleteStorefrontAccessTokensParamStorefrontAccessTokenIdRequestPath

# Operation: list_tender_transactions
class GetTenderTransactionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 if not specified.")
    processed_at_min: Any | None = Field(default=None, description="Filter to show only tender transactions processed on or after this date (ISO 8601 format).")
    processed_at_max: Any | None = Field(default=None, description="Filter to show only tender transactions processed on or before this date (ISO 8601 format).")
    order: Any | None = Field(default=None, description="Sort results by processed_at timestamp in either ascending or descending order.")
class GetTenderTransactionsRequest(StrictModel):
    """Retrieves a paginated list of tender transactions processed through the store. Results are paginated using link headers in the response."""
    query: GetTenderTransactionsRequestQuery | None = None

# Operation: get_theme
class GetThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to retrieve.")
class GetThemesParamThemeIdRequest(StrictModel):
    """Retrieves the details of a single theme by its ID, including theme metadata and configuration."""
    path: GetThemesParamThemeIdRequestPath

# Operation: delete_theme
class DeleteThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to delete, returned as a string by the Shopify API.")
class DeleteThemesParamThemeIdRequest(StrictModel):
    """Permanently deletes a theme from the Shopify store. The theme must not be the currently active theme."""
    path: DeleteThemesParamThemeIdRequestPath

# Operation: get_theme_asset
class GetThemesParamThemeIdAssetsRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme from which to retrieve the asset.")
class GetThemesParamThemeIdAssetsRequestQuery(StrictModel):
    asset_key: str | None = Field(default=None, validation_alias="asset[key]", serialization_alias="asset[key]", description="The file path key of the asset to retrieve within the theme (e.g., templates/index.liquid, assets/style.css). Required to fetch a specific asset.")
class GetThemesParamThemeIdAssetsRequest(StrictModel):
    """Retrieves a single asset file from a theme by its key. The asset key specifies the file path within the theme (e.g., templates/index.liquid)."""
    path: GetThemesParamThemeIdAssetsRequestPath
    query: GetThemesParamThemeIdAssetsRequestQuery | None = None

# Operation: delete_theme_asset
class DeleteThemesParamThemeIdAssetsRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme from which the asset will be deleted.")
class DeleteThemesParamThemeIdAssetsRequestQuery(StrictModel):
    asset_key: str | None = Field(default=None, validation_alias="asset[key]", serialization_alias="asset[key]", description="The asset key (file path) identifying which asset to delete from the theme, such as 'templates/product.json' or 'assets/style.css'.")
class DeleteThemesParamThemeIdAssetsRequest(StrictModel):
    """Removes a specific asset file from a Shopify theme. The asset is identified by its key path within the theme."""
    path: DeleteThemesParamThemeIdAssetsRequestPath
    query: DeleteThemesParamThemeIdAssetsRequestQuery | None = None

# Operation: get_user
class GetUsersParamUserIdRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to retrieve. This is a required string value that identifies which user's information to fetch.")
class GetUsersParamUserIdRequest(StrictModel):
    """Retrieves detailed information for a specific user by their unique identifier. Use this to fetch user profile data, permissions, and account details."""
    path: GetUsersParamUserIdRequestPath

# Operation: list_webhooks
class GetWebhooksRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter webhooks by the URI endpoint that receives POST requests. Only webhooks sending to this address will be returned.")
    limit: Any | None = Field(default=None, description="Maximum number of webhooks to return per request, between 1 and 250. Defaults to 50 if not specified.")
    topic: Any | None = Field(default=None, description="Filter webhooks by topic (event type). Only webhooks subscribed to the specified topic will be returned. Refer to the Shopify webhook topics documentation for valid values.")
class GetWebhooksRequest(StrictModel):
    """Retrieves a list of webhooks configured for your Shopify store. Results are paginated using link headers in the response."""
    query: GetWebhooksRequestQuery | None = None

# Operation: get_webhooks_count
class GetWebhooksCountRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter the count to only include webhook subscriptions that send POST requests to this specific URI.")
    topic: Any | None = Field(default=None, description="Filter the count to only include webhook subscriptions for a specific event topic. Refer to the webhook topic property documentation for valid topic values.")
class GetWebhooksCountRequest(StrictModel):
    """Retrieves the total count of webhook subscriptions configured in the Shopify store, with optional filtering by destination address or event topic."""
    query: GetWebhooksCountRequestQuery | None = None

# Operation: get_webhook
class GetWebhooksParamWebhookIdRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook subscription to retrieve.")
class GetWebhooksParamWebhookIdRequest(StrictModel):
    """Retrieves the details of a specific webhook subscription by its ID, including its configuration, topics, and delivery settings."""
    path: GetWebhooksParamWebhookIdRequestPath

# Operation: get_application_charge_202101
class Deprecated202101GetApplicationChargesParamApplicationChargeIdRequestPath(StrictModel):
    application_charge_id: str = Field(default=..., description="The unique identifier of the application charge to retrieve.")
class Deprecated202101GetApplicationChargesParamApplicationChargeIdRequest(StrictModel):
    """Retrieves the details of a specific application charge by its ID. Use this to fetch information about a charge created for your app."""
    path: Deprecated202101GetApplicationChargesParamApplicationChargeIdRequestPath

# Operation: list_blog_articles
class Deprecated202101GetBlogsParamBlogIdArticlesRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog from which to retrieve articles.")
class Deprecated202101GetBlogsParamBlogIdArticlesRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of articles to return per request, between 1 and 250 (defaults to 50).")
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: published (only published articles), unpublished (only unpublished articles), or any (all articles regardless of status). Defaults to any.")
    handle: Any | None = Field(default=None, description="Retrieve a single article by its unique handle identifier.")
    tag: Any | None = Field(default=None, description="Filter articles to only those tagged with a specific tag.")
    author: Any | None = Field(default=None, description="Filter articles to only those written by a specific author.")
class Deprecated202101GetBlogsParamBlogIdArticlesRequest(StrictModel):
    """Retrieves a paginated list of articles from a specific blog. Results are paginated using link headers in the response; the page parameter is not supported."""
    path: Deprecated202101GetBlogsParamBlogIdArticlesRequestPath
    query: Deprecated202101GetBlogsParamBlogIdArticlesRequestQuery | None = None

# Operation: create_article_for_blog_202101
class Deprecated202101CreateBlogsParamBlogIdArticlesRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog where the article will be created.")
class Deprecated202101CreateBlogsParamBlogIdArticlesRequest(StrictModel):
    """Creates a new article for a specified blog. The article will be added to the blog's collection of articles."""
    path: Deprecated202101CreateBlogsParamBlogIdArticlesRequestPath

# Operation: get_article_count_for_blog_2021_01
class Deprecated202101GetBlogsParamBlogIdArticlesCountRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog for which to count articles.")
class Deprecated202101GetBlogsParamBlogIdArticlesCountRequestQuery(StrictModel):
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: use 'published' to count only published articles, 'unpublished' to count only unpublished articles, or 'any' to count all articles regardless of status. Defaults to 'any' if not specified.")
class Deprecated202101GetBlogsParamBlogIdArticlesCountRequest(StrictModel):
    """Retrieves the total count of articles in a specific blog, with optional filtering by publication status."""
    path: Deprecated202101GetBlogsParamBlogIdArticlesCountRequestPath
    query: Deprecated202101GetBlogsParamBlogIdArticlesCountRequestQuery | None = None

# Operation: get_article_202101
class Deprecated202101GetBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article.")
    article_id: str = Field(default=..., description="The unique identifier of the article to retrieve.")
class Deprecated202101GetBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Retrieves a single article from a blog by its ID. Use this to fetch detailed information about a specific article in the Shopify online store."""
    path: Deprecated202101GetBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: update_article_202101
class Deprecated202101UpdateBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article to update.")
    article_id: str = Field(default=..., description="The unique identifier of the article to update.")
class Deprecated202101UpdateBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Updates an existing article within a blog. Modify article content, metadata, and other properties by providing the blog and article identifiers."""
    path: Deprecated202101UpdateBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: delete_article_202101
class Deprecated202101DeleteBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article to delete.")
    article_id: str = Field(default=..., description="The unique identifier of the article to delete.")
class Deprecated202101DeleteBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Permanently deletes an article from a blog. This action cannot be undone."""
    path: Deprecated202101DeleteBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: update_carrier_service_202101
class Deprecated202101UpdateCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to update.")
class Deprecated202101UpdateCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Updates an existing carrier service. Only the app that originally created the carrier service can modify it."""
    path: Deprecated202101UpdateCarrierServicesParamCarrierServiceIdRequestPath

# Operation: delete_carrier_service_2021_01
class Deprecated202101DeleteCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to delete.")
class Deprecated202101DeleteCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Permanently deletes a carrier service from the store. This action cannot be undone and will remove the carrier service configuration."""
    path: Deprecated202101DeleteCarrierServicesParamCarrierServiceIdRequestPath

# Operation: get_abandoned_checkouts_count_202101
class Deprecated202101GetCheckoutsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count by checkout status. Use 'open' to count only active abandoned checkouts or 'closed' to count only completed/closed abandoned checkouts. Defaults to 'open' if not specified.")
class Deprecated202101GetCheckoutsCountRequest(StrictModel):
    """Retrieves the count of abandoned checkouts from the past 90 days, optionally filtered by checkout status."""
    query: Deprecated202101GetCheckoutsCountRequestQuery | None = None

# Operation: complete_checkout_2021_01
class Deprecated202101CreateCheckoutsParamTokenCompleteRequestPath(StrictModel):
    token: str = Field(default=..., description="The unique identifier token for the checkout to complete. This token is provided when the checkout is created and is required to identify which checkout should be finalized.")
class Deprecated202101CreateCheckoutsParamTokenCompleteRequest(StrictModel):
    """Completes a checkout by finalizing the transaction and converting it to an order. This operation marks the checkout as complete and processes the payment."""
    path: Deprecated202101CreateCheckoutsParamTokenCompleteRequestPath

# Operation: list_shipping_rates_for_checkout_2021_01
class Deprecated202101GetCheckoutsParamTokenShippingRatesRequestPath(StrictModel):
    token: str = Field(default=..., description="The unique identifier for the checkout. This token is used to retrieve shipping rates specific to that checkout.")
class Deprecated202101GetCheckoutsParamTokenShippingRatesRequest(StrictModel):
    """Retrieves available shipping rates for a checkout. Poll this endpoint until rates become available, then use the returned rates to display updated pricing (subtotal, tax, total) or apply a rate by updating the checkout's shipping line."""
    path: Deprecated202101GetCheckoutsParamTokenShippingRatesRequestPath

# Operation: delete_collection_listing_202101
class Deprecated202101DeleteCollectionListingsParamCollectionListingIdRequestPath(StrictModel):
    collection_listing_id: str = Field(default=..., description="The unique identifier of the collection listing to delete.")
class Deprecated202101DeleteCollectionListingsParamCollectionListingIdRequest(StrictModel):
    """Remove a collection listing to unpublish a collection from your sales channel or app."""
    path: Deprecated202101DeleteCollectionListingsParamCollectionListingIdRequestPath

# Operation: list_product_ids_for_collection_listing_v2021
class Deprecated202101GetCollectionListingsParamCollectionListingIdProductIdsRequestPath(StrictModel):
    collection_listing_id: str = Field(default=..., description="The unique identifier for the collection listing whose published products you want to retrieve.")
class Deprecated202101GetCollectionListingsParamCollectionListingIdProductIdsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of product IDs to return per request, ranging from 1 to 1000 (defaults to 50).")
class Deprecated202101GetCollectionListingsParamCollectionListingIdProductIdsRequest(StrictModel):
    """Retrieve the product IDs that are published to a specific collection listing. Results are paginated using link headers in the response."""
    path: Deprecated202101GetCollectionListingsParamCollectionListingIdProductIdsRequestPath
    query: Deprecated202101GetCollectionListingsParamCollectionListingIdProductIdsRequestQuery | None = None

# Operation: get_collection_202101
class Deprecated202101GetCollectionsParamCollectionIdRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection to retrieve.")
class Deprecated202101GetCollectionsParamCollectionIdRequest(StrictModel):
    """Retrieves the details of a single collection by its ID, including metadata such as name, description, and product associations."""
    path: Deprecated202101GetCollectionsParamCollectionIdRequestPath

# Operation: list_collection_products_202101
class Deprecated202101GetCollectionsParamCollectionIdProductsRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection whose products you want to retrieve.")
class Deprecated202101GetCollectionsParamCollectionIdProductsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of products to return per request, ranging from 1 to 250 products (defaults to 50 if not specified).")
class Deprecated202101GetCollectionsParamCollectionIdProductsRequest(StrictModel):
    """Retrieve products belonging to a specific collection, sorted by the collection's configured sort order. Results are paginated using link-based navigation provided in response headers."""
    path: Deprecated202101GetCollectionsParamCollectionIdProductsRequestPath
    query: Deprecated202101GetCollectionsParamCollectionIdProductsRequestQuery | None = None

# Operation: list_collects_2021_01
class Deprecated202101GetCollectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, ranging from 1 to 250 items. Defaults to 50 if not specified.")
class Deprecated202101GetCollectsRequest(StrictModel):
    """Retrieves a list of collects (product-to-collection associations) from the store. Results are paginated using link-based navigation provided in response headers rather than page parameters."""
    query: Deprecated202101GetCollectsRequestQuery | None = None

# Operation: get_collects_count_202101
class Deprecated202101GetCollectsCountRequestQuery(StrictModel):
    collection_id: int | None = Field(default=None, description="Filter the count to only collects belonging to a specific collection. Omit to get the total count across all collections.")
class Deprecated202101GetCollectsCountRequest(StrictModel):
    """Retrieves the total count of collects, optionally filtered by a specific collection. Useful for understanding collection membership size without fetching individual collect records."""
    query: Deprecated202101GetCollectsCountRequestQuery | None = None

# Operation: get_collect_202101
class Deprecated202101GetCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect record to retrieve.")
class Deprecated202101GetCollectsParamCollectIdRequest(StrictModel):
    """Retrieves a specific product collection assignment by its ID. Use this to fetch details about how a product is organized within a collection."""
    path: Deprecated202101GetCollectsParamCollectIdRequestPath

# Operation: remove_product_from_collection_2021_01
class Deprecated202101DeleteCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect relationship to remove. This ID represents the specific product-collection association being deleted.")
class Deprecated202101DeleteCollectsParamCollectIdRequest(StrictModel):
    """Removes a product from a collection by deleting the collect relationship. This operation unlinks a product from a specific collection without affecting the product or collection itself."""
    path: Deprecated202101DeleteCollectsParamCollectIdRequestPath

# Operation: delete_country_202101
class Deprecated202101DeleteCountriesParamCountryIdRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country to delete. This is a required string value that specifies which country record to remove.")
class Deprecated202101DeleteCountriesParamCountryIdRequest(StrictModel):
    """Permanently deletes a country from the store. This operation removes the country record and cannot be undone."""
    path: Deprecated202101DeleteCountriesParamCountryIdRequestPath

# Operation: list_provinces_for_country_202101
class Deprecated202101GetCountriesParamCountryIdProvincesRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve provinces. This ID must correspond to a valid country in the Shopify system.")
class Deprecated202101GetCountriesParamCountryIdProvincesRequest(StrictModel):
    """Retrieves a list of provinces or states for a specified country. Use this to populate province/state selectors or validate province data for a given country."""
    path: Deprecated202101GetCountriesParamCountryIdProvincesRequestPath

# Operation: get_province_count_for_country_202101
class Deprecated202101GetCountriesParamCountryIdProvincesCountRequestPath(StrictModel):
    country_id: str = Field(default=..., description="The unique identifier of the country for which to retrieve the province count.")
class Deprecated202101GetCountriesParamCountryIdProvincesCountRequest(StrictModel):
    """Retrieves the total count of provinces or states for a specified country. Useful for understanding administrative divisions within a country."""
    path: Deprecated202101GetCountriesParamCountryIdProvincesCountRequestPath

# Operation: count_custom_collections_2021_01
class Deprecated202101GetCustomCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter the count to include only custom collections with this exact title.")
    product_id: Any | None = Field(default=None, description="Filter the count to include only custom collections that contain this specific product.")
    published_status: Any | None = Field(default=None, description="Filter the count by publication status: 'published' for only published collections, 'unpublished' for only unpublished collections, or 'any' for all collections regardless of status. Defaults to 'any' if not specified.")
class Deprecated202101GetCustomCollectionsCountRequest(StrictModel):
    """Retrieves the total count of custom collections in the store, with optional filtering by title, product inclusion, or published status."""
    query: Deprecated202101GetCustomCollectionsCountRequestQuery | None = None

# Operation: update_custom_collection_202101
class Deprecated202101UpdateCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to update.")
class Deprecated202101UpdateCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Updates an existing custom collection in your Shopify store. Modify collection details such as title, description, image, and other properties."""
    path: Deprecated202101UpdateCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: delete_custom_collection_legacy_202101
class Deprecated202101DeleteCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to delete.")
class Deprecated202101DeleteCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Permanently deletes a custom collection from the store. This action cannot be undone."""
    path: Deprecated202101DeleteCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: get_customer_saved_search_202101
class Deprecated202101GetCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath(StrictModel):
    customer_saved_search_id: str = Field(default=..., description="The unique identifier of the customer saved search to retrieve.")
class Deprecated202101GetCustomerSavedSearchesParamCustomerSavedSearchIdRequest(StrictModel):
    """Retrieves a single customer saved search by its ID. Use this to fetch details about a specific saved search that a customer has created."""
    path: Deprecated202101GetCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath

# Operation: delete_customer_saved_search_202101
class Deprecated202101DeleteCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath(StrictModel):
    customer_saved_search_id: str = Field(default=..., description="The unique identifier of the customer saved search to delete.")
class Deprecated202101DeleteCustomerSavedSearchesParamCustomerSavedSearchIdRequest(StrictModel):
    """Permanently deletes a customer saved search by its ID. This action cannot be undone."""
    path: Deprecated202101DeleteCustomerSavedSearchesParamCustomerSavedSearchIdRequestPath

# Operation: list_customers_for_saved_search_2021_01
class Deprecated202101GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestPath(StrictModel):
    customer_saved_search_id: str = Field(default=..., description="The unique identifier of the customer saved search to retrieve customers for.")
class Deprecated202101GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="Specifies the field and direction to sort results by (e.g., 'last_order_date DESC'). Defaults to sorting by last order date in descending order.")
    limit: Any | None = Field(default=None, description="The maximum number of customer records to return per request. Defaults to 50 and cannot exceed 250.")
class Deprecated202101GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequest(StrictModel):
    """Retrieves all customers that match the criteria defined in a customer saved search. Results can be ordered and paginated."""
    path: Deprecated202101GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestPath
    query: Deprecated202101GetCustomerSavedSearchesParamCustomerSavedSearchIdCustomersRequestQuery | None = None

# Operation: list_customers_202101
class Deprecated202101GetCustomersRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only include customers with the specified IDs. Provide as a comma-separated list of customer ID values.")
    limit: Any | None = Field(default=None, description="Maximum number of customer records to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
class Deprecated202101GetCustomersRequest(StrictModel):
    """Retrieves a paginated list of customers from the store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: Deprecated202101GetCustomersRequestQuery | None = None

# Operation: search_customers_202101
class Deprecated202101GetCustomersSearchRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="Specify the field and direction to sort results. Use format: field_name ASC or DESC (default: last_order_date DESC).")
    query: Any | None = Field(default=None, description="Text to search across customer data fields such as name, email, phone, and address information.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250 (default: 50).")
class Deprecated202101GetCustomersSearchRequest(StrictModel):
    """Search for customers in the shop by query text. Returns matching customer records with pagination support via response headers."""
    query: Deprecated202101GetCustomersSearchRequestQuery | None = None

# Operation: get_customer_202101
class Deprecated202101GetCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to retrieve.")
class Deprecated202101GetCustomersParamCustomerIdRequest(StrictModel):
    """Retrieves a single customer by their unique identifier from the Shopify store."""
    path: Deprecated202101GetCustomersParamCustomerIdRequestPath

# Operation: update_customer_202101
class Deprecated202101UpdateCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to update. This ID is required to specify which customer record should be modified.")
class Deprecated202101UpdateCustomersParamCustomerIdRequest(StrictModel):
    """Updates an existing customer's information in Shopify. Modify customer details such as email, name, phone, and other profile attributes."""
    path: Deprecated202101UpdateCustomersParamCustomerIdRequestPath

# Operation: delete_customer_v202101
class Deprecated202101DeleteCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to delete.")
class Deprecated202101DeleteCustomersParamCustomerIdRequest(StrictModel):
    """Permanently deletes a customer from the store. The deletion will fail if the customer has any existing orders."""
    path: Deprecated202101DeleteCustomersParamCustomerIdRequestPath

# Operation: generate_customer_account_activation_url_2021_01
class Deprecated202101CreateCustomersParamCustomerIdAccountActivationUrlRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer for whom to generate the account activation URL.")
class Deprecated202101CreateCustomersParamCustomerIdAccountActivationUrlRequest(StrictModel):
    """Generate a one-time account activation URL for a customer whose account is not yet enabled. The URL expires after 30 days; generating a new URL invalidates any previously generated URLs."""
    path: Deprecated202101CreateCustomersParamCustomerIdAccountActivationUrlRequestPath

# Operation: list_customer_addresses_202101
class Deprecated202101GetCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses you want to retrieve.")
class Deprecated202101GetCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Retrieves all addresses associated with a specific customer. Uses cursor-based pagination via response headers; the page parameter is not supported."""
    path: Deprecated202101GetCustomersParamCustomerIdAddressesRequestPath

# Operation: create_customer_address_v202101
class Deprecated202101CreateCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer for whom the address is being created.")
class Deprecated202101CreateCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Creates a new address for a customer. The address is added to the customer's address list and can be set as their default billing or shipping address."""
    path: Deprecated202101CreateCustomersParamCustomerIdAddressesRequestPath

# Operation: bulk_update_customer_addresses_202101
class Deprecated202101UpdateCustomersParamCustomerIdAddressesSetRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses will be modified.")
class Deprecated202101UpdateCustomersParamCustomerIdAddressesSetRequestQuery(StrictModel):
    address_ids: int | None = Field(default=None, validation_alias="address_ids[]", serialization_alias="address_ids[]", description="Array of address IDs to target for the bulk operation. The order may be significant depending on the operation type.")
    operation: str | None = Field(default=None, description="The type of bulk operation to perform on the specified addresses (e.g., delete, set as default). Refer to API documentation for valid operation values.")
class Deprecated202101UpdateCustomersParamCustomerIdAddressesSetRequest(StrictModel):
    """Performs bulk operations on multiple customer addresses, allowing you to update, delete, or modify address records in a single request."""
    path: Deprecated202101UpdateCustomersParamCustomerIdAddressesSetRequestPath
    query: Deprecated202101UpdateCustomersParamCustomerIdAddressesSetRequestQuery | None = None

# Operation: get_customer_address_202101
class Deprecated202101GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who owns the address.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to retrieve.")
class Deprecated202101GetCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Retrieves the details of a specific customer address by customer ID and address ID."""
    path: Deprecated202101GetCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: update_customer_address_2021_01
class Deprecated202101UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being updated.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to update for the customer.")
class Deprecated202101UpdateCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Updates an existing customer address by customer ID and address ID. Use this to modify address details such as street, city, postal code, or other address information for a specific customer."""
    path: Deprecated202101UpdateCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: delete_customer_address_202101
class Deprecated202101DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being removed.")
    address_id: str = Field(default=..., description="The unique identifier of the address to be deleted from the customer's address list.")
class Deprecated202101DeleteCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Removes a specific address from a customer's address list. This operation permanently deletes the address record associated with the given customer."""
    path: Deprecated202101DeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: set_default_customer_address
class Deprecated202101UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose default address is being updated.")
    address_id: str = Field(default=..., description="The unique identifier of the address to set as the customer's default address.")
class Deprecated202101UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest(StrictModel):
    """Sets a specific address as the default address for a customer. This address will be used as the primary address for the customer's account."""
    path: Deprecated202101UpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath

# Operation: list_customer_orders_202101
class Deprecated202101GetCustomersParamCustomerIdOrdersRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose orders should be retrieved.")
class Deprecated202101GetCustomersParamCustomerIdOrdersRequest(StrictModel):
    """Retrieves all orders for a specific customer. Supports filtering and sorting through standard Order resource query parameters."""
    path: Deprecated202101GetCustomersParamCustomerIdOrdersRequestPath

# Operation: send_customer_invite_202101
class Deprecated202101CreateCustomersParamCustomerIdSendInviteRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who will receive the account invite.")
class Deprecated202101CreateCustomersParamCustomerIdSendInviteRequest(StrictModel):
    """Sends an account invitation email to a customer, allowing them to create or access their account."""
    path: Deprecated202101CreateCustomersParamCustomerIdSendInviteRequestPath

# Operation: list_events_202101
class Deprecated202101GetEventsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of events to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
    filter_: Any | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filters events to show only those matching the specified criteria. Use this to narrow results to specific event types or conditions.")
    verb: Any | None = Field(default=None, description="Filters events to show only those of a specific action type or verb (e.g., create, update, delete).")
class Deprecated202101GetEventsRequest(StrictModel):
    """Retrieves a paginated list of events from the store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: Deprecated202101GetEventsRequestQuery | None = None

# Operation: get_event_2021_01
class Deprecated202101GetEventsParamEventIdRequestPath(StrictModel):
    event_id: str = Field(default=..., description="The unique identifier of the event to retrieve.")
class Deprecated202101GetEventsParamEventIdRequest(StrictModel):
    """Retrieves a single event by its ID from the Shopify admin. Use this to fetch detailed information about a specific event that occurred in your store."""
    path: Deprecated202101GetEventsParamEventIdRequestPath

# Operation: get_fulfillment_order_202101
class Deprecated202101GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to retrieve.")
class Deprecated202101GetFulfillmentOrdersParamFulfillmentOrderIdRequest(StrictModel):
    """Retrieves the details of a specific fulfillment order by its ID. Use this to fetch current status, line items, and fulfillment information for a particular order."""
    path: Deprecated202101GetFulfillmentOrdersParamFulfillmentOrderIdRequestPath

# Operation: cancel_fulfillment_order_2021_01
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel. This ID references a specific fulfillment order that should be marked as cancelled.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest(StrictModel):
    """Cancels a fulfillment order, marking it as no longer needed for processing. This operation is useful when a fulfillment order must be abandoned before it's been fulfilled."""
    path: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath

# Operation: send_fulfillment_order_cancellation_request_2021_01
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel. This ID references a specific fulfillment order in the system.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for the cancellation request. This provides context to the fulfillment service about why the order is being cancelled.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest(StrictModel):
    """Sends a cancellation request to the fulfillment service for a specific fulfillment order. This notifies the fulfillment provider to stop processing or cancel an already-placed fulfillment order."""
    path: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath
    query: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery | None = None

# Operation: accept_fulfillment_order_cancellation_request_2021_01
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to accept the cancellation request.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for accepting the cancellation request.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest(StrictModel):
    """Accepts a cancellation request for a fulfillment order, confirming that the fulfillment service should cancel the specified order. Optionally include a reason message for the acceptance."""
    path: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath
    query: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_order_cancellation_request_2021_01
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which you are rejecting the cancellation request.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining why the cancellation request is being rejected. This reason will be communicated to the fulfillment service.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest(StrictModel):
    """Rejects a cancellation request that was sent to a fulfillment service for a specific fulfillment order. Use this when you need to decline a cancellation and optionally provide a reason to the fulfillment service."""
    path: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath
    query: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery | None = None

# Operation: close_fulfillment_order_2021_01
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to close.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional reason or note explaining why the fulfillment order is being marked as incomplete.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest(StrictModel):
    """Marks an in-progress fulfillment order as incomplete, indicating the fulfillment service cannot ship remaining items and is closing the order."""
    path: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath
    query: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery | None = None

# Operation: send_fulfillment_request_202101
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to request fulfillment for.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message to include with the fulfillment request for communication with the fulfillment service.")
    fulfillment_order_line_items: Any | None = Field(default=None, description="An optional array of fulfillment order line items to request for fulfillment. If omitted, all line items in the fulfillment order will be requested.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest(StrictModel):
    """Sends a fulfillment request to the fulfillment service for a specific fulfillment order, optionally targeting specific line items or including a message."""
    path: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath
    query: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery | None = None

# Operation: accept_fulfillment_request_2021_01
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request is being accepted.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message providing context or reasoning for accepting the fulfillment request.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest(StrictModel):
    """Accepts a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, confirming that the fulfillment service will proceed with fulfilling the order."""
    path: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath
    query: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_request_202101
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request should be rejected.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for rejecting the fulfillment request.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest(StrictModel):
    """Rejects a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, optionally providing a reason for the rejection."""
    path: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath
    query: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery | None = None

# Operation: list_locations_for_fulfillment_order_move_2021_01
class Deprecated202101GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to retrieve available move destinations.")
class Deprecated202101GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest(StrictModel):
    """Retrieves all locations where a fulfillment order can be moved to, sorted alphabetically by location name. Use this to determine valid destination locations before initiating a fulfillment order transfer."""
    path: Deprecated202101GetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath

# Operation: open_fulfillment_order
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdOpenRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to open for processing.")
class Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdOpenRequest(StrictModel):
    """Marks a scheduled fulfillment order as ready for fulfillment, allowing merchants to begin work on it before its originally scheduled fulfill_at datetime."""
    path: Deprecated202101CreateFulfillmentOrdersParamFulfillmentOrderIdOpenRequestPath

# Operation: cancel_fulfillment_202101
class Deprecated202101CreateFulfillmentsParamFulfillmentIdCancelRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to cancel. This ID references a specific fulfillment order that has been previously created.")
class Deprecated202101CreateFulfillmentsParamFulfillmentIdCancelRequest(StrictModel):
    """Cancels an existing fulfillment order. This operation marks the specified fulfillment as cancelled and updates its status accordingly."""
    path: Deprecated202101CreateFulfillmentsParamFulfillmentIdCancelRequestPath

# Operation: update_fulfillment_tracking_2021_01
class Deprecated202101CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment whose tracking information should be updated.")
class Deprecated202101CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest(StrictModel):
    """Updates the tracking information for a fulfillment, allowing you to modify shipment tracking details after the fulfillment has been created."""
    path: Deprecated202101CreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath

# Operation: list_gift_cards_2021_01
class Deprecated202101GetGiftCardsRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter results to gift cards with a specific status: enabled to show only active gift cards, or disabled to show only inactive gift cards.")
    limit: Any | None = Field(default=None, description="Maximum number of gift cards to return per request, between 1 and 250 (defaults to 50).")
class Deprecated202101GetGiftCardsRequest(StrictModel):
    """Retrieves a paginated list of gift cards, optionally filtered by status. Results are paginated using link headers in the response rather than page parameters."""
    query: Deprecated202101GetGiftCardsRequestQuery | None = None

# Operation: count_gift_cards_v202101
class Deprecated202101GetGiftCardsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count to only include gift cards with a specific status: enabled for active gift cards, or disabled for inactive gift cards. Omit to count all gift cards regardless of status.")
class Deprecated202101GetGiftCardsCountRequest(StrictModel):
    """Retrieves the total count of gift cards, optionally filtered by their enabled or disabled status."""
    query: Deprecated202101GetGiftCardsCountRequestQuery | None = None

# Operation: search_gift_cards_202101
class Deprecated202101GetGiftCardsSearchRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="The field and sort direction for ordering results. Defaults to most recently disabled gift cards first.")
    query: Any | None = Field(default=None, description="The search query text to match against indexed gift card fields including created_at, updated_at, disabled_at, balance, initial_value, amount_spent, email, and last_characters.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250. Defaults to 50 results.")
class Deprecated202101GetGiftCardsSearchRequest(StrictModel):
    """Search for gift cards using indexed fields like balance, email, or creation date. Results are paginated and returned via link headers."""
    query: Deprecated202101GetGiftCardsSearchRequestQuery | None = None

# Operation: update_gift_card_202101
class Deprecated202101UpdateGiftCardsParamGiftCardIdRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to update.")
class Deprecated202101UpdateGiftCardsParamGiftCardIdRequest(StrictModel):
    """Updates an existing gift card's expiry date, note, and template suffix. The gift card's balance cannot be modified through this API."""
    path: Deprecated202101UpdateGiftCardsParamGiftCardIdRequestPath

# Operation: disable_gift_card_202101
class Deprecated202101CreateGiftCardsParamGiftCardIdDisableRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to disable.")
class Deprecated202101CreateGiftCardsParamGiftCardIdDisableRequest(StrictModel):
    """Permanently disables a gift card, preventing it from being used for future transactions. This action cannot be reversed."""
    path: Deprecated202101CreateGiftCardsParamGiftCardIdDisableRequestPath

# Operation: list_inventory_items_202101
class Deprecated202101GetInventoryItemsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of inventory items to return per request, between 1 and 250 items. Defaults to 50 if not specified.")
    ids: int | None = Field(default=None, description="Filter results to only inventory items with the specified IDs. Provide one or more comma-separated integer IDs.")
class Deprecated202101GetInventoryItemsRequest(StrictModel):
    """Retrieves a paginated list of inventory items. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: Deprecated202101GetInventoryItemsRequestQuery | None = None

# Operation: update_inventory_item_legacy_202101
class Deprecated202101UpdateInventoryItemsParamInventoryItemIdRequestPath(StrictModel):
    inventory_item_id: str = Field(default=..., description="The unique identifier of the inventory item to update.")
class Deprecated202101UpdateInventoryItemsParamInventoryItemIdRequest(StrictModel):
    """Updates an existing inventory item in your Shopify store. Modify properties like SKU, tracked status, and cost for a specific inventory item."""
    path: Deprecated202101UpdateInventoryItemsParamInventoryItemIdRequestPath

# Operation: list_inventory_levels_202101
class Deprecated202101GetInventoryLevelsRequestQuery(StrictModel):
    inventory_item_ids: Any | None = Field(default=None, description="Comma-separated list of inventory item IDs to filter results. Maximum of 50 IDs per request.")
    location_ids: Any | None = Field(default=None, description="Comma-separated list of location IDs to filter results. Maximum of 50 IDs per request. Use the Location resource to find location IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
class Deprecated202101GetInventoryLevelsRequest(StrictModel):
    """Retrieves inventory levels across your store's locations. You must filter by at least one inventory item ID or location ID to retrieve results."""
    query: Deprecated202101GetInventoryLevelsRequestQuery | None = None

# Operation: delete_inventory_level_202101
class Deprecated202101DeleteInventoryLevelsRequestQuery(StrictModel):
    inventory_item_id: int | None = Field(default=None, description="The unique identifier of the inventory item whose level should be deleted.")
    location_id: int | None = Field(default=None, description="The unique identifier of the location where the inventory level should be removed.")
class Deprecated202101DeleteInventoryLevelsRequest(StrictModel):
    """Removes an inventory level for a specific inventory item at a location. This disconnects the item from that location; note that every inventory item must maintain at least one inventory level, so you must connect the item to another location before deleting its last level."""
    query: Deprecated202101DeleteInventoryLevelsRequestQuery | None = None

# Operation: get_location_202101
class Deprecated202101GetLocationsParamLocationIdRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location to retrieve.")
class Deprecated202101GetLocationsParamLocationIdRequest(StrictModel):
    """Retrieves a single location by its ID from the Shopify inventory system. Use this to fetch detailed information about a specific store location."""
    path: Deprecated202101GetLocationsParamLocationIdRequestPath

# Operation: list_inventory_levels_for_location_202101
class Deprecated202101GetLocationsParamLocationIdInventoryLevelsRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location for which to retrieve inventory levels.")
class Deprecated202101GetLocationsParamLocationIdInventoryLevelsRequest(StrictModel):
    """Retrieves all inventory levels for a specific location. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""
    path: Deprecated202101GetLocationsParamLocationIdInventoryLevelsRequestPath

# Operation: list_fulfillment_orders_for_order_2021_01
class Deprecated202101GetOrdersParamOrderIdFulfillmentOrdersRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve fulfillment orders.")
class Deprecated202101GetOrdersParamOrderIdFulfillmentOrdersRequest(StrictModel):
    """Retrieves all fulfillment orders associated with a specific order. Fulfillment orders represent the items in an order that need to be fulfilled."""
    path: Deprecated202101GetOrdersParamOrderIdFulfillmentOrdersRequestPath

# Operation: list_fulfillments_for_order_v202101
class Deprecated202101GetOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order whose fulfillments you want to retrieve.")
class Deprecated202101GetOrdersParamOrderIdFulfillmentsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of fulfillments to return per request, between 1 and 250 (defaults to 50).")
class Deprecated202101GetOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Retrieves all fulfillments associated with a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the limit parameter."""
    path: Deprecated202101GetOrdersParamOrderIdFulfillmentsRequestPath
    query: Deprecated202101GetOrdersParamOrderIdFulfillmentsRequestQuery | None = None

# Operation: create_fulfillment_for_order_legacy_202101
class Deprecated202101CreateOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the fulfillment.")
class Deprecated202101CreateOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Create a fulfillment for specified line items in an order. The fulfillment status depends on the fulfillment service type: manual/custom services set status immediately, while external services queue the fulfillment with pending status until processed."""
    path: Deprecated202101CreateOrdersParamOrderIdFulfillmentsRequestPath

# Operation: get_fulfillment_count_for_order_2021_01
class Deprecated202101GetOrdersParamOrderIdFulfillmentsCountRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve the fulfillment count.")
class Deprecated202101GetOrdersParamOrderIdFulfillmentsCountRequest(StrictModel):
    """Retrieves the total count of fulfillments associated with a specific order. Useful for understanding fulfillment status and logistics tracking without fetching full fulfillment details."""
    path: Deprecated202101GetOrdersParamOrderIdFulfillmentsCountRequestPath

# Operation: get_fulfillment_202101
class Deprecated202101GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to retrieve.")
class Deprecated202101GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Retrieve detailed information about a specific fulfillment for an order. Use this to access fulfillment status, tracking information, and line item details."""
    path: Deprecated202101GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: update_fulfillment_202101
class Deprecated202101UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to update.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to update.")
class Deprecated202101UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Update fulfillment details for a specific order, such as tracking information or fulfillment status."""
    path: Deprecated202101UpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: cancel_fulfillment_order_202101
class Deprecated202101CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to cancel.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to cancel within the specified order.")
class Deprecated202101CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequest(StrictModel):
    """Cancel a fulfillment for a specific order. This operation marks the fulfillment as cancelled and prevents further processing of the associated shipment."""
    path: Deprecated202101CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequestPath

# Operation: complete_fulfillment_2021_01
class Deprecated202101CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to be completed.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment within the order that should be marked as complete.")
class Deprecated202101CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest(StrictModel):
    """Mark a fulfillment as complete, indicating that all items in the fulfillment have been shipped or delivered to the customer."""
    path: Deprecated202101CreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath

# Operation: list_fulfillment_events_202101
class Deprecated202101GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment within the specified order.")
class Deprecated202101GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest(StrictModel):
    """Retrieves all events associated with a specific fulfillment for an order. Events track status changes and milestones throughout the fulfillment lifecycle."""
    path: Deprecated202101GetOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath

# Operation: list_order_refunds_202101
class Deprecated202101GetOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve refunds.")
class Deprecated202101GetOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of refunds to return per request, between 1 and 250 (defaults to 50).")
    in_shop_currency: Any | None = Field(default=None, description="When true, displays refund amounts in the shop's currency for the underlying transaction; defaults to false.")
class Deprecated202101GetOrdersParamOrderIdRefundsRequest(StrictModel):
    """Retrieves a list of refunds for a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    path: Deprecated202101GetOrdersParamOrderIdRefundsRequestPath
    query: Deprecated202101GetOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: create_order_refund_202101
class Deprecated202101CreateOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create a refund.")
class Deprecated202101CreateOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    notify: Any | None = Field(default=None, description="Whether to send a refund notification email to the customer.")
    note: Any | None = Field(default=None, description="An optional note to attach to the refund for internal reference.")
    discrepancy_reason: Any | None = Field(default=None, description="An optional reason explaining any discrepancy between calculated and actual refund amounts. Valid values are: restock, damage, customer, or other.")
    shipping: Any | None = Field(default=None, description="Shipping refund details. Specify either full_refund to refund all remaining shipping, or amount to refund a specific shipping amount (takes precedence over full_refund).")
    refund_line_items: Any | None = Field(default=None, description="A list of line items to refund, each with the line item ID, quantity to refund, restock type (no_restock, cancel, or return), and location ID for restocking (required for cancel and return types).")
    transactions: Any | None = Field(default=None, description="A list of transactions to process as refunds. Should be obtained from the calculate endpoint for accuracy.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required for multi-currency orders when an amount property is provided.")
class Deprecated202101CreateOrdersParamOrderIdRefundsRequest(StrictModel):
    """Creates a refund for an order. Use the calculate endpoint first to determine the correct transactions to submit. For multi-currency orders, the currency property is required whenever an amount is specified."""
    path: Deprecated202101CreateOrdersParamOrderIdRefundsRequestPath
    query: Deprecated202101CreateOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: calculate_order_refund_2021_01
class Deprecated202101CreateOrdersParamOrderIdRefundsCalculateRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to calculate the refund.")
class Deprecated202101CreateOrdersParamOrderIdRefundsCalculateRequestQuery(StrictModel):
    shipping: Any | None = Field(default=None, description="Shipping refund configuration. Specify either full_refund to refund all remaining shipping, or amount to refund a specific shipping cost. The amount property takes precedence over full_refund.")
    refund_line_items: Any | None = Field(default=None, description="List of line items to refund, each specifying the line item ID, quantity to refund, restock instructions (no_restock, cancel, or return), and optionally the location ID where items should be restocked. If location_id is omitted for return or cancel restocks, the endpoint will suggest an appropriate location.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required whenever a shipping amount is specified, particularly important for multi-currency orders.")
class Deprecated202101CreateOrdersParamOrderIdRefundsCalculateRequest(StrictModel):
    """Calculate refund transactions for an order based on line items and shipping costs. Use this endpoint to generate accurate refund details before creating an actual refund, including any necessary adjustments to restock instructions."""
    path: Deprecated202101CreateOrdersParamOrderIdRefundsCalculateRequestPath
    query: Deprecated202101CreateOrdersParamOrderIdRefundsCalculateRequestQuery | None = None

# Operation: get_refund_for_order_202101
class Deprecated202101GetOrdersParamOrderIdRefundsParamRefundIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the refund.")
    refund_id: str = Field(default=..., description="The unique identifier of the refund to retrieve.")
class Deprecated202101GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery(StrictModel):
    in_shop_currency: Any | None = Field(default=None, description="When enabled, displays all monetary amounts in the shop's native currency rather than the transaction currency. Defaults to false.")
class Deprecated202101GetOrdersParamOrderIdRefundsParamRefundIdRequest(StrictModel):
    """Retrieves the details of a specific refund associated with an order. Use this to view refund information including amounts, line items, and status."""
    path: Deprecated202101GetOrdersParamOrderIdRefundsParamRefundIdRequestPath
    query: Deprecated202101GetOrdersParamOrderIdRefundsParamRefundIdRequestQuery | None = None

# Operation: list_order_risks_2021_01
class Deprecated202101GetOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve risk data.")
class Deprecated202101GetOrdersParamOrderIdRisksRequest(StrictModel):
    """Retrieves all fraud and risk assessments associated with a specific order. Results are paginated using link headers in the response."""
    path: Deprecated202101GetOrdersParamOrderIdRisksRequestPath

# Operation: create_order_risk_202101
class Deprecated202101CreateOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the risk record.")
class Deprecated202101CreateOrdersParamOrderIdRisksRequest(StrictModel):
    """Creates a risk assessment record for a specific order. Use this to flag potential issues or concerns associated with an order that may require review or action."""
    path: Deprecated202101CreateOrdersParamOrderIdRisksRequestPath

# Operation: get_order_risk_202101
class Deprecated202101GetOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk assessment.")
    risk_id: str = Field(default=..., description="The unique identifier of the specific risk assessment to retrieve.")
class Deprecated202101GetOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Retrieves a specific risk assessment associated with an order. Use this to fetch details about a fraud or security risk that has been flagged for a particular order."""
    path: Deprecated202101GetOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: update_order_risk_202101
class Deprecated202101UpdateOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to be updated.")
    risk_id: str = Field(default=..., description="The unique identifier of the order risk to be updated.")
class Deprecated202101UpdateOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Updates an existing order risk for a specific order. Note that you cannot modify an order risk that was created by another application."""
    path: Deprecated202101UpdateOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: delete_order_risk_202101
class Deprecated202101DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to be deleted.")
    risk_id: str = Field(default=..., description="The unique identifier of the risk assessment to be deleted from the order.")
class Deprecated202101DeleteOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Removes a specific risk assessment from an order. Note that you can only delete risks created by your application; risks created by other applications cannot be deleted."""
    path: Deprecated202101DeleteOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: create_discount_code_batch
class Deprecated202101CreatePriceRulesParamPriceRuleIdBatchRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which discount codes will be created.")
class Deprecated202101CreatePriceRulesParamPriceRuleIdBatchRequest(StrictModel):
    """Asynchronously creates up to 100 discount codes for a price rule in a single batch job. Returns a discount code creation object that can be monitored for completion status, including counts of successful and failed code creations."""
    path: Deprecated202101CreatePriceRulesParamPriceRuleIdBatchRequestPath

# Operation: get_discount_code_batch_202101
class Deprecated202101GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch.")
    batch_id: str = Field(default=..., description="The unique identifier of the batch job to retrieve status and results for.")
class Deprecated202101GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest(StrictModel):
    """Retrieves the status and details of a discount code creation job batch for a specific price rule. Use this to check the progress and results of bulk discount code generation."""
    path: Deprecated202101GetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath

# Operation: list_discount_codes_for_batch_202101
class Deprecated202101GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code batch job.")
    batch_id: str = Field(default=..., description="The unique identifier of the batch job for which to retrieve discount codes.")
class Deprecated202101GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest(StrictModel):
    """Retrieves all discount codes generated from a specific batch job within a price rule. Results include successfully created codes with populated IDs and codes that failed with error details."""
    path: Deprecated202101GetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath

# Operation: list_discount_codes_for_price_rule_2021_01
class Deprecated202101GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which to retrieve associated discount codes.")
class Deprecated202101GetPriceRulesParamPriceRuleIdDiscountCodesRequest(StrictModel):
    """Retrieve all discount codes associated with a specific price rule. Results are paginated using link-based navigation provided in response headers."""
    path: Deprecated202101GetPriceRulesParamPriceRuleIdDiscountCodesRequestPath

# Operation: get_discount_code_202101
class Deprecated202101GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to retrieve.")
class Deprecated202101GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Retrieves a single discount code associated with a specific price rule. Use this to fetch detailed information about a discount code by its ID."""
    path: Deprecated202101GetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: update_discount_code_202101
class Deprecated202101UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code being updated.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to update.")
class Deprecated202101UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Updates an existing discount code associated with a price rule. Modify discount code properties such as code value, usage limits, and other settings."""
    path: Deprecated202101UpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: delete_discount_code_202101
class Deprecated202101DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code to be deleted.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to be deleted.")
class Deprecated202101DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Permanently deletes a specific discount code associated with a price rule. This action cannot be undone."""
    path: Deprecated202101DeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: list_products_2021_01
class Deprecated202101GetProductsRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only include products with IDs matching this comma-separated list of product identifiers.")
    limit: Any | None = Field(default=None, description="Maximum number of products to return per page, between 1 and 250 (defaults to 50).")
    title: Any | None = Field(default=None, description="Filter results to only include products whose title contains this text.")
    vendor: Any | None = Field(default=None, description="Filter results to only include products from this vendor.")
    handle: Any | None = Field(default=None, description="Filter results to only include products with this handle (URL-friendly identifier).")
    product_type: Any | None = Field(default=None, description="Filter results to only include products of this type.")
    status: Any | None = Field(default=None, description="Filter results by product status: active (default), archived, or draft.")
    collection_id: Any | None = Field(default=None, description="Filter results to only include products assigned to this collection ID.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: published, unpublished, or any (default shows all).")
    presentment_currencies: Any | None = Field(default=None, description="Return prices in only these currencies, specified as a comma-separated list of ISO 4217 currency codes.")
class Deprecated202101GetProductsRequest(StrictModel):
    """Retrieves a paginated list of products from the store, with support for filtering by various attributes and sorting options. Uses cursor-based pagination via response headers rather than page parameters."""
    query: Deprecated202101GetProductsRequestQuery | None = None

# Operation: get_products_count_202101
class Deprecated202101GetProductsCountRequestQuery(StrictModel):
    vendor: Any | None = Field(default=None, description="Filter the count to include only products from a specific vendor.")
    product_type: Any | None = Field(default=None, description="Filter the count to include only products of a specific product type.")
    collection_id: Any | None = Field(default=None, description="Filter the count to include only products belonging to a specific collection by its ID.")
    published_status: Any | None = Field(default=None, description="Filter products by their publication status: use 'published' for only published products, 'unpublished' for only unpublished products, or 'any' to include all products regardless of status (default is 'any').")
class Deprecated202101GetProductsCountRequest(StrictModel):
    """Retrieves the total count of products in the store, with optional filtering by vendor, product type, collection, or published status."""
    query: Deprecated202101GetProductsCountRequestQuery | None = None

# Operation: get_product_202101
class Deprecated202101GetProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to retrieve.")
class Deprecated202101GetProductsParamProductIdRequest(StrictModel):
    """Retrieves detailed information for a single product by its ID from the Shopify store."""
    path: Deprecated202101GetProductsParamProductIdRequestPath

# Operation: delete_product_202101
class Deprecated202101DeleteProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to delete. This is a numeric ID assigned by Shopify.")
class Deprecated202101DeleteProductsParamProductIdRequest(StrictModel):
    """Permanently deletes a product from the store. This action cannot be undone and will remove the product and all associated data."""
    path: Deprecated202101DeleteProductsParamProductIdRequestPath

# Operation: list_product_images_202101
class Deprecated202101GetProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product whose images you want to retrieve.")
class Deprecated202101GetProductsParamProductIdImagesRequest(StrictModel):
    """Retrieve all images associated with a specific product. Returns a collection of image resources for the given product."""
    path: Deprecated202101GetProductsParamProductIdImagesRequestPath

# Operation: create_product_image_202101
class Deprecated202101CreateProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to which the image will be added.")
class Deprecated202101CreateProductsParamProductIdImagesRequest(StrictModel):
    """Create a new image for a specific product. The image will be associated with the product and can be used to display product visuals in the storefront."""
    path: Deprecated202101CreateProductsParamProductIdImagesRequestPath

# Operation: get_product_images_count_202101
class Deprecated202101GetProductsParamProductIdImagesCountRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product for which to retrieve the image count.")
class Deprecated202101GetProductsParamProductIdImagesCountRequest(StrictModel):
    """Retrieve the total count of images associated with a specific product. Useful for determining how many product images exist without fetching the full image data."""
    path: Deprecated202101GetProductsParamProductIdImagesCountRequestPath

# Operation: update_product_image_202101
class Deprecated202101UpdateProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product that contains the image to be updated.")
    image_id: str = Field(default=..., description="The unique identifier of the specific image within the product to be updated.")
class Deprecated202101UpdateProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Update the properties of an existing product image, such as alt text, position, or other image metadata."""
    path: Deprecated202101UpdateProductsParamProductIdImagesParamImageIdRequestPath

# Operation: delete_product_image_202101
class Deprecated202101DeleteProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product containing the image to delete.")
    image_id: str = Field(default=..., description="The unique identifier of the image to delete from the product.")
class Deprecated202101DeleteProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Delete a specific image associated with a product. This removes the image from the product's image gallery."""
    path: Deprecated202101DeleteProductsParamProductIdImagesParamImageIdRequestPath

# Operation: get_recurring_application_charge_202101
class Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to retrieve.")
class Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(StrictModel):
    """Retrieves the details of a single recurring application charge by its ID. Use this to fetch current status, pricing, and other metadata for a specific recurring charge."""
    path: Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath

# Operation: delete_recurring_application_charge_2021_01
class Deprecated202101DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to cancel.")
class Deprecated202101DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(StrictModel):
    """Cancels an active recurring application charge for a Shopify app, preventing future billing cycles."""
    path: Deprecated202101DeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath

# Operation: update_recurring_application_charge_capped_amount_2021_01
class Deprecated202101UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to update.")
class Deprecated202101UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery(StrictModel):
    recurring_application_charge_capped_amount: int | None = Field(default=None, validation_alias="recurring_application_charge[capped_amount]", serialization_alias="recurring_application_charge[capped_amount]", description="The new capped amount limit for the recurring charge, specified as a whole number representing the maximum billable amount.")
class Deprecated202101UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest(StrictModel):
    """Updates the capped amount limit for an active recurring application charge. This allows you to modify the maximum amount that can be charged to the merchant for this recurring billing plan."""
    path: Deprecated202101UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath
    query: Deprecated202101UpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery | None = None

# Operation: list_usage_charges_for_recurring_application_charge_2021_01
class Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge for which to retrieve associated usage charges.")
class Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Retrieves all usage charges associated with a specific recurring application charge. Usage charges represent variable fees billed on top of a recurring application charge."""
    path: Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath

# Operation: create_usage_charge_for_recurring_application_charge_202101
class Deprecated202101CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge for which to create the usage charge.")
class Deprecated202101CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Creates a usage charge against an existing recurring application charge. Usage charges allow you to bill merchants for variable usage on top of their recurring subscription."""
    path: Deprecated202101CreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath

# Operation: get_usage_charge_for_recurring_application_charge_202101
class Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge that contains the usage charge you want to retrieve.")
    usage_charge_id: str = Field(default=..., description="The unique identifier of the specific usage charge to retrieve.")
class Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest(StrictModel):
    """Retrieves a single usage charge associated with a recurring application charge. Use this to fetch details about a specific metered billing charge."""
    path: Deprecated202101GetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath

# Operation: list_redirects_202101
class Deprecated202101GetRedirectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of redirects to return per request, between 1 and 250. Defaults to 50 if not specified.")
    path: Any | None = Field(default=None, description="Filter results to show only redirects with a specific source path.")
    target: Any | None = Field(default=None, description="Filter results to show only redirects pointing to a specific target URL.")
class Deprecated202101GetRedirectsRequest(StrictModel):
    """Retrieves a list of URL redirects configured in the online store. Results are paginated using link headers in the response."""
    query: Deprecated202101GetRedirectsRequestQuery | None = None

# Operation: get_redirects_count_2021_01
class Deprecated202101GetRedirectsCountRequestQuery(StrictModel):
    path: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific path value.")
    target: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific target URL.")
class Deprecated202101GetRedirectsCountRequest(StrictModel):
    """Retrieves the total count of URL redirects in the store, with optional filtering by path or target URL."""
    query: Deprecated202101GetRedirectsCountRequestQuery | None = None

# Operation: get_redirect_202101
class Deprecated202101GetRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to retrieve.")
class Deprecated202101GetRedirectsParamRedirectIdRequest(StrictModel):
    """Retrieves a single redirect by its ID from the Shopify online store."""
    path: Deprecated202101GetRedirectsParamRedirectIdRequestPath

# Operation: update_redirect_v202101
class Deprecated202101UpdateRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to update. This ID is required to locate and modify the correct redirect.")
class Deprecated202101UpdateRedirectsParamRedirectIdRequest(StrictModel):
    """Updates an existing redirect in the online store. Modify redirect settings such as the target path or status for a specific redirect by its ID."""
    path: Deprecated202101UpdateRedirectsParamRedirectIdRequestPath

# Operation: delete_redirect_v202101
class Deprecated202101DeleteRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to delete.")
class Deprecated202101DeleteRedirectsParamRedirectIdRequest(StrictModel):
    """Permanently deletes a redirect from the online store. This action cannot be undone."""
    path: Deprecated202101DeleteRedirectsParamRedirectIdRequestPath

# Operation: create_report_legacy_202101
class Deprecated202101CreateReportsRequestQuery(StrictModel):
    name: Any | None = Field(default=None, description="The display name for the report. Must not exceed 255 characters.")
    shopify_ql: Any | None = Field(default=None, description="The ShopifyQL query string that defines what data the report will retrieve and analyze.")
class Deprecated202101CreateReportsRequest(StrictModel):
    """Creates a new custom report in the Shopify admin. The report can be configured with a name and ShopifyQL query to analyze store data."""
    query: Deprecated202101CreateReportsRequestQuery | None = None

# Operation: get_report_202101
class Deprecated202101GetReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to retrieve.")
class Deprecated202101GetReportsParamReportIdRequest(StrictModel):
    """Retrieves a single report that was created by your app. Use this to fetch details about a specific report by its ID."""
    path: Deprecated202101GetReportsParamReportIdRequestPath

# Operation: update_report_legacy
class Deprecated202101UpdateReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to update. This ID is used to locate and modify the specific report in the system.")
class Deprecated202101UpdateReportsParamReportIdRequest(StrictModel):
    """Updates an existing report configuration in the Shopify Admin API. This operation modifies report settings and properties for the specified report."""
    path: Deprecated202101UpdateReportsParamReportIdRequestPath

# Operation: delete_report_202101
class Deprecated202101DeleteReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to delete. This is a required string value that identifies which report should be removed.")
class Deprecated202101DeleteReportsParamReportIdRequest(StrictModel):
    """Permanently deletes a specific report from the Shopify admin. This action cannot be undone."""
    path: Deprecated202101DeleteReportsParamReportIdRequestPath

# Operation: list_shopify_payments_payouts_2021_01
class Deprecated202101GetShopifyPaymentsPayoutsRequestQuery(StrictModel):
    date_min: Any | None = Field(default=None, description="Filter payouts to include only those made on or after the specified date (inclusive).")
    date_max: Any | None = Field(default=None, description="Filter payouts to include only those made on or before the specified date (inclusive).")
    status: Any | None = Field(default=None, description="Filter payouts by their current status (e.g., pending, paid, failed, cancelled).")
class Deprecated202101GetShopifyPaymentsPayoutsRequest(StrictModel):
    """Retrieves a list of all payouts from Shopify Payments, ordered by payout date with the most recent first. Results are paginated using link headers in the response."""
    query: Deprecated202101GetShopifyPaymentsPayoutsRequestQuery | None = None

# Operation: get_shopify_payments_payout_2021_01
class Deprecated202101GetShopifyPaymentsPayoutsParamPayoutIdRequestPath(StrictModel):
    payout_id: str = Field(default=..., description="The unique identifier of the payout to retrieve.")
class Deprecated202101GetShopifyPaymentsPayoutsParamPayoutIdRequest(StrictModel):
    """Retrieves details for a specific Shopify Payments payout by its unique identifier."""
    path: Deprecated202101GetShopifyPaymentsPayoutsParamPayoutIdRequestPath

# Operation: list_smart_collections_202101
class Deprecated202101GetSmartCollectionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of smart collections to return per request. Must be between 1 and 250, defaults to 50.")
    ids: Any | None = Field(default=None, description="Filter results to only smart collections with the specified IDs. Provide as a comma-separated list of numeric IDs.")
    title: Any | None = Field(default=None, description="Filter results to smart collections matching the exact title.")
    product_id: Any | None = Field(default=None, description="Filter results to smart collections that contain the specified product ID.")
    handle: Any | None = Field(default=None, description="Filter results by the smart collection's URL-friendly handle.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for published collections only, 'unpublished' for unpublished only, or 'any' for all collections. Defaults to 'any'.")
class Deprecated202101GetSmartCollectionsRequest(StrictModel):
    """Retrieves a paginated list of smart collections from your store. Results are paginated using link headers in the response."""
    query: Deprecated202101GetSmartCollectionsRequestQuery | None = None

# Operation: count_smart_collections_202101
class Deprecated202101GetSmartCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter to only count smart collections with this exact title.")
    product_id: Any | None = Field(default=None, description="Filter to only count smart collections that include the specified product.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for only published collections, 'unpublished' for only unpublished collections, or 'any' to include all collections regardless of status. Defaults to 'any'.")
class Deprecated202101GetSmartCollectionsCountRequest(StrictModel):
    """Retrieves the total count of smart collections in the store, with optional filtering by title, product inclusion, or published status."""
    query: Deprecated202101GetSmartCollectionsCountRequestQuery | None = None

# Operation: delete_smart_collection_202101
class Deprecated202101DeleteSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to delete.")
class Deprecated202101DeleteSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Permanently removes a smart collection from the store. This action cannot be undone."""
    path: Deprecated202101DeleteSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: list_tender_transactions_202101
class Deprecated202101GetTenderTransactionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250 (defaults to 50).")
    processed_at_min: Any | None = Field(default=None, description="Filter to show only tender transactions processed on or after this date (ISO 8601 format).")
    processed_at_max: Any | None = Field(default=None, description="Filter to show only tender transactions processed on or before this date (ISO 8601 format).")
    order: Any | None = Field(default=None, description="Sort results by processed_at timestamp in ascending or descending order.")
class Deprecated202101GetTenderTransactionsRequest(StrictModel):
    """Retrieves a paginated list of tender transactions processed through the store. Results are paginated using link headers in the response."""
    query: Deprecated202101GetTenderTransactionsRequestQuery | None = None

# Operation: get_theme_202101
class Deprecated202101GetThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to retrieve.")
class Deprecated202101GetThemesParamThemeIdRequest(StrictModel):
    """Retrieves a single theme by its ID from the Shopify online store. Use this to fetch detailed information about a specific theme."""
    path: Deprecated202101GetThemesParamThemeIdRequestPath

# Operation: delete_theme_2021_01
class Deprecated202101DeleteThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to delete.")
class Deprecated202101DeleteThemesParamThemeIdRequest(StrictModel):
    """Permanently deletes a theme from the Shopify store. This action cannot be undone."""
    path: Deprecated202101DeleteThemesParamThemeIdRequestPath

# Operation: delete_theme_asset_202101
class Deprecated202101DeleteThemesParamThemeIdAssetsRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme from which the asset will be deleted.")
class Deprecated202101DeleteThemesParamThemeIdAssetsRequestQuery(StrictModel):
    asset_key: str | None = Field(default=None, validation_alias="asset[key]", serialization_alias="asset[key]", description="The key (file path) of the asset to delete from the theme. This identifies which specific asset file to remove.")
class Deprecated202101DeleteThemesParamThemeIdAssetsRequest(StrictModel):
    """Removes a specific asset file from a Shopify theme. The asset is identified by its key within the theme."""
    path: Deprecated202101DeleteThemesParamThemeIdAssetsRequestPath
    query: Deprecated202101DeleteThemesParamThemeIdAssetsRequestQuery | None = None

# Operation: list_webhooks_legacy_202101
class Deprecated202101GetWebhooksRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter webhooks by the URI endpoint that receives POST requests. Only webhooks sending to this address will be returned.")
    limit: Any | None = Field(default=None, description="Maximum number of webhooks to return per request, between 1 and 250. Defaults to 50 if not specified.")
    topic: Any | None = Field(default=None, description="Filter webhooks by topic to return only subscriptions for specific events. Refer to the Shopify webhook topics documentation for valid values.")
class Deprecated202101GetWebhooksRequest(StrictModel):
    """Retrieves a list of webhook subscriptions configured for your Shopify store. Results are paginated using link headers in the response."""
    query: Deprecated202101GetWebhooksRequestQuery | None = None

# Operation: count_webhooks_202101
class Deprecated202101GetWebhooksCountRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter the webhook count to only subscriptions that deliver POST requests to this specific URI.")
    topic: Any | None = Field(default=None, description="Filter the webhook count to only subscriptions listening to this specific topic. Refer to the webhook topic property documentation for valid topic values.")
class Deprecated202101GetWebhooksCountRequest(StrictModel):
    """Retrieves the total count of webhook subscriptions configured in the Shopify store, with optional filtering by delivery address or topic."""
    query: Deprecated202101GetWebhooksCountRequestQuery | None = None

# Operation: get_application_charge_unstable
class DeprecatedUnstableGetApplicationChargesParamApplicationChargeIdRequestPath(StrictModel):
    application_charge_id: str = Field(default=..., description="The unique identifier of the application charge to retrieve.")
class DeprecatedUnstableGetApplicationChargesParamApplicationChargeIdRequest(StrictModel):
    """Retrieves details for a specific application charge by its ID. Use this to fetch the current status and information of a billing charge associated with your app."""
    path: DeprecatedUnstableGetApplicationChargesParamApplicationChargeIdRequestPath

# Operation: get_application_credit_unstable
class DeprecatedUnstableGetApplicationCreditsParamApplicationCreditIdRequestPath(StrictModel):
    application_credit_id: str = Field(default=..., description="The unique identifier of the application credit to retrieve.")
class DeprecatedUnstableGetApplicationCreditsParamApplicationCreditIdRequest(StrictModel):
    """Retrieves the details of a single application credit by its ID. Use this to fetch information about a specific credit issued to an app."""
    path: DeprecatedUnstableGetApplicationCreditsParamApplicationCreditIdRequestPath

# Operation: list_article_tags_unstable
class DeprecatedUnstableGetArticlesTagsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of tags to return in the response. Limits the size of the result set.")
    popular: Any | None = Field(default=None, description="When included, sorts tags by popularity in descending order (most popular first). Omit this parameter to retrieve tags in default order.")
class DeprecatedUnstableGetArticlesTagsRequest(StrictModel):
    """Retrieves all tags used across articles in the online store. Results can be optionally limited and sorted by popularity."""
    query: DeprecatedUnstableGetArticlesTagsRequestQuery | None = None

# Operation: list_blog_articles_unstable
class DeprecatedUnstableGetBlogsParamBlogIdArticlesRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog from which to retrieve articles.")
class DeprecatedUnstableGetBlogsParamBlogIdArticlesRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of articles to return per request, between 1 and 250 (defaults to 50).")
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: published (published articles only), unpublished (unpublished articles only), or any (all articles regardless of status, default).")
    handle: Any | None = Field(default=None, description="Retrieve a single article by its unique handle identifier.")
    tag: Any | None = Field(default=None, description="Filter articles to only those tagged with a specific tag.")
    author: Any | None = Field(default=None, description="Filter articles to only those written by a specific author.")
class DeprecatedUnstableGetBlogsParamBlogIdArticlesRequest(StrictModel):
    """Retrieves a paginated list of articles from a specific blog. Results are paginated using link headers in the response; the page parameter is not supported."""
    path: DeprecatedUnstableGetBlogsParamBlogIdArticlesRequestPath
    query: DeprecatedUnstableGetBlogsParamBlogIdArticlesRequestQuery | None = None

# Operation: get_article_count_for_blog
class DeprecatedUnstableGetBlogsParamBlogIdArticlesCountRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog for which to retrieve the article count.")
class DeprecatedUnstableGetBlogsParamBlogIdArticlesCountRequestQuery(StrictModel):
    published_status: Any | None = Field(default=None, description="Filter articles by publication status: use 'published' to count only published articles, 'unpublished' to count only unpublished articles, or 'any' to count all articles regardless of status. Defaults to 'any' if not specified.")
class DeprecatedUnstableGetBlogsParamBlogIdArticlesCountRequest(StrictModel):
    """Retrieves the total count of articles in a specified blog, with optional filtering by publication status."""
    path: DeprecatedUnstableGetBlogsParamBlogIdArticlesCountRequestPath
    query: DeprecatedUnstableGetBlogsParamBlogIdArticlesCountRequestQuery | None = None

# Operation: update_article_unstable
class DeprecatedUnstableUpdateBlogsParamBlogIdArticlesParamArticleIdRequestPath(StrictModel):
    blog_id: str = Field(default=..., description="The unique identifier of the blog containing the article to update.")
    article_id: str = Field(default=..., description="The unique identifier of the article to update.")
class DeprecatedUnstableUpdateBlogsParamBlogIdArticlesParamArticleIdRequest(StrictModel):
    """Updates an article within a specific blog. Modify article content, metadata, and other properties using this endpoint."""
    path: DeprecatedUnstableUpdateBlogsParamBlogIdArticlesParamArticleIdRequestPath

# Operation: update_carrier_service_unstable
class DeprecatedUnstableUpdateCarrierServicesParamCarrierServiceIdRequestPath(StrictModel):
    carrier_service_id: str = Field(default=..., description="The unique identifier of the carrier service to update.")
class DeprecatedUnstableUpdateCarrierServicesParamCarrierServiceIdRequest(StrictModel):
    """Updates an existing carrier service. Only the app that originally created the carrier service can modify it."""
    path: DeprecatedUnstableUpdateCarrierServicesParamCarrierServiceIdRequestPath

# Operation: get_abandoned_checkouts_count_unstable
class DeprecatedUnstableGetCheckoutsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count by checkout status. Use 'open' to count only active abandoned checkouts, or 'closed' to count only completed/closed abandoned checkouts. Defaults to 'open' if not specified.")
class DeprecatedUnstableGetCheckoutsCountRequest(StrictModel):
    """Retrieves the count of abandoned checkouts from the past 90 days, optionally filtered by checkout status."""
    query: DeprecatedUnstableGetCheckoutsCountRequestQuery | None = None

# Operation: get_collection_unstable
class DeprecatedUnstableGetCollectionsParamCollectionIdRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection to retrieve.")
class DeprecatedUnstableGetCollectionsParamCollectionIdRequest(StrictModel):
    """Retrieves the details of a single collection by its ID. Use this to fetch collection information such as name, description, and other metadata."""
    path: DeprecatedUnstableGetCollectionsParamCollectionIdRequestPath

# Operation: list_collection_products_unstable
class DeprecatedUnstableGetCollectionsParamCollectionIdProductsRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection whose products you want to retrieve.")
class DeprecatedUnstableGetCollectionsParamCollectionIdProductsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="The maximum number of products to return per request, between 1 and 250 (defaults to 50).")
class DeprecatedUnstableGetCollectionsParamCollectionIdProductsRequest(StrictModel):
    """Retrieve products belonging to a specific collection, sorted by the collection's configured sort order. Results are paginated using link-based navigation provided in response headers."""
    path: DeprecatedUnstableGetCollectionsParamCollectionIdProductsRequestPath
    query: DeprecatedUnstableGetCollectionsParamCollectionIdProductsRequestQuery | None = None

# Operation: list_collects_unstable
class DeprecatedUnstableGetCollectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of collects to return per request, between 1 and 250 (defaults to 50).")
class DeprecatedUnstableGetCollectsRequest(StrictModel):
    """Retrieves a list of collects (product-to-collection associations). Uses cursor-based pagination via response header links; the page parameter is not supported."""
    query: DeprecatedUnstableGetCollectsRequestQuery | None = None

# Operation: get_collects_count_unstable
class DeprecatedUnstableGetCollectsCountRequestQuery(StrictModel):
    collection_id: int | None = Field(default=None, description="Filter the count to only include collects belonging to a specific collection. Omit this parameter to get the total count across all collections.")
class DeprecatedUnstableGetCollectsCountRequest(StrictModel):
    """Retrieves the total count of collects, optionally filtered by a specific collection. Use this to determine how many products are associated with a collection without fetching individual collect records."""
    query: DeprecatedUnstableGetCollectsCountRequestQuery | None = None

# Operation: get_collect_unstable
class DeprecatedUnstableGetCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect record to retrieve.")
class DeprecatedUnstableGetCollectsParamCollectIdRequest(StrictModel):
    """Retrieves a specific product collection by its ID. Use this to fetch details about how a product is organized within a collection."""
    path: DeprecatedUnstableGetCollectsParamCollectIdRequestPath

# Operation: remove_product_from_collection_unstable
class DeprecatedUnstableDeleteCollectsParamCollectIdRequestPath(StrictModel):
    collect_id: str = Field(default=..., description="The unique identifier of the collect relationship to remove. This ID represents the link between a product and a collection.")
class DeprecatedUnstableDeleteCollectsParamCollectIdRequest(StrictModel):
    """Removes a product from a collection by deleting the collect relationship. This operation unlinks a product from a specific collection without affecting the product or collection itself."""
    path: DeprecatedUnstableDeleteCollectsParamCollectIdRequestPath

# Operation: list_custom_collections_unstable
class DeprecatedUnstableGetCustomCollectionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of collections to return per request, between 1 and 250. Defaults to 50 if not specified.")
    ids: Any | None = Field(default=None, description="Filter results to only collections with the specified IDs. Provide as a comma-separated list of numeric IDs.")
    title: Any | None = Field(default=None, description="Filter results to only collections matching the exact title.")
    product_id: Any | None = Field(default=None, description="Filter results to only collections that contain the specified product ID.")
    handle: Any | None = Field(default=None, description="Filter results to only collections with the specified URL-friendly handle.")
    published_status: Any | None = Field(default=None, description="Filter by publication status: 'published' for published collections only, 'unpublished' for unpublished only, or 'any' for all collections regardless of status. Defaults to 'any'.")
class DeprecatedUnstableGetCustomCollectionsRequest(StrictModel):
    """Retrieves a list of custom collections from your store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: DeprecatedUnstableGetCustomCollectionsRequestQuery | None = None

# Operation: count_custom_collections_unstable
class DeprecatedUnstableGetCustomCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter the count to include only custom collections with this exact title.")
    product_id: Any | None = Field(default=None, description="Filter the count to include only custom collections that contain this specific product.")
    published_status: Any | None = Field(default=None, description="Filter the count by publication status: 'published' for only published collections, 'unpublished' for only unpublished collections, or 'any' for all collections regardless of status. Defaults to 'any'.")
class DeprecatedUnstableGetCustomCollectionsCountRequest(StrictModel):
    """Retrieves the total count of custom collections in the store, with optional filtering by title, product inclusion, or published status."""
    query: DeprecatedUnstableGetCustomCollectionsCountRequestQuery | None = None

# Operation: get_custom_collection_unstable
class DeprecatedUnstableGetCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to retrieve.")
class DeprecatedUnstableGetCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Retrieves a single custom collection by its ID from the Shopify admin API. Use this to fetch detailed information about a specific custom collection."""
    path: DeprecatedUnstableGetCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: update_custom_collection_unstable
class DeprecatedUnstableUpdateCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to update. This ID is required to specify which collection should be modified.")
class DeprecatedUnstableUpdateCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Updates an existing custom collection in your Shopify store. Modify collection details such as title, description, image, and other properties."""
    path: DeprecatedUnstableUpdateCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: delete_custom_collection_unstable
class DeprecatedUnstableDeleteCustomCollectionsParamCustomCollectionIdRequestPath(StrictModel):
    custom_collection_id: str = Field(default=..., description="The unique identifier of the custom collection to delete.")
class DeprecatedUnstableDeleteCustomCollectionsParamCustomCollectionIdRequest(StrictModel):
    """Permanently deletes a custom collection from the store. This action cannot be undone."""
    path: DeprecatedUnstableDeleteCustomCollectionsParamCustomCollectionIdRequestPath

# Operation: list_customers_unstable
class DeprecatedUnstableGetCustomersRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results to only include customers with the specified IDs. Provide as a comma-separated list of customer ID values.")
    limit: Any | None = Field(default=None, description="Maximum number of customer records to return per request. Defaults to 50 if not specified; maximum allowed is 250.")
class DeprecatedUnstableGetCustomersRequest(StrictModel):
    """Retrieves a paginated list of customers from the Shopify store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: DeprecatedUnstableGetCustomersRequestQuery | None = None

# Operation: search_customers_unstable
class DeprecatedUnstableGetCustomersSearchRequestQuery(StrictModel):
    order: Any | None = Field(default=None, description="Specify which field to sort results by and the sort direction (ascending or descending). Defaults to sorting by most recent order date in descending order.")
    query: Any | None = Field(default=None, description="Text query to search across customer data fields such as name, email, phone, and address information.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, ranging from 1 to 250. Defaults to 50 results.")
class DeprecatedUnstableGetCustomersSearchRequest(StrictModel):
    """Search for customers in the shop by query text. Results are paginated using link headers in the response."""
    query: DeprecatedUnstableGetCustomersSearchRequestQuery | None = None

# Operation: get_customer_unstable
class DeprecatedUnstableGetCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to retrieve.")
class DeprecatedUnstableGetCustomersParamCustomerIdRequest(StrictModel):
    """Retrieves detailed information for a single customer by their unique identifier."""
    path: DeprecatedUnstableGetCustomersParamCustomerIdRequestPath

# Operation: update_customer_unstable
class DeprecatedUnstableUpdateCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to update. This is a required string value that specifies which customer record to modify.")
class DeprecatedUnstableUpdateCustomersParamCustomerIdRequest(StrictModel):
    """Updates an existing customer's information in the Shopify store. This operation modifies customer details such as name, email, phone, and other profile attributes."""
    path: DeprecatedUnstableUpdateCustomersParamCustomerIdRequestPath

# Operation: delete_customer_unstable
class DeprecatedUnstableDeleteCustomersParamCustomerIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer to delete.")
class DeprecatedUnstableDeleteCustomersParamCustomerIdRequest(StrictModel):
    """Permanently deletes a customer from the store. The deletion will fail if the customer has any existing orders."""
    path: DeprecatedUnstableDeleteCustomersParamCustomerIdRequestPath

# Operation: generate_customer_account_activation_url_unstable
class DeprecatedUnstableCreateCustomersParamCustomerIdAccountActivationUrlRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer for whom to generate the account activation URL.")
class DeprecatedUnstableCreateCustomersParamCustomerIdAccountActivationUrlRequest(StrictModel):
    """Generate a one-time account activation URL for a customer whose account is not yet enabled. The URL expires after 30 days; generating a new URL invalidates any previously generated URLs."""
    path: DeprecatedUnstableCreateCustomersParamCustomerIdAccountActivationUrlRequestPath

# Operation: list_customer_addresses_unstable
class DeprecatedUnstableGetCustomersParamCustomerIdAddressesRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses you want to retrieve.")
class DeprecatedUnstableGetCustomersParamCustomerIdAddressesRequest(StrictModel):
    """Retrieves all addresses associated with a specific customer. Uses cursor-based pagination via response headers; the page parameter is not supported."""
    path: DeprecatedUnstableGetCustomersParamCustomerIdAddressesRequestPath

# Operation: bulk_update_customer_addresses_unstable
class DeprecatedUnstableUpdateCustomersParamCustomerIdAddressesSetRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose addresses will be modified.")
class DeprecatedUnstableUpdateCustomersParamCustomerIdAddressesSetRequestQuery(StrictModel):
    address_ids: int | None = Field(default=None, validation_alias="address_ids[]", serialization_alias="address_ids[]", description="Array of address IDs to include in the bulk operation. The order may be significant depending on the operation type.")
    operation: str | None = Field(default=None, description="The type of bulk operation to perform on the specified addresses (e.g., set as default, delete, or update).")
class DeprecatedUnstableUpdateCustomersParamCustomerIdAddressesSetRequest(StrictModel):
    """Perform bulk operations on multiple addresses for a specific customer, such as setting default addresses or updating address properties in batch."""
    path: DeprecatedUnstableUpdateCustomersParamCustomerIdAddressesSetRequestPath
    query: DeprecatedUnstableUpdateCustomersParamCustomerIdAddressesSetRequestQuery | None = None

# Operation: get_customer_address_unstable
class DeprecatedUnstableGetCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who owns the address.")
    address_id: str = Field(default=..., description="The unique identifier of the specific address to retrieve.")
class DeprecatedUnstableGetCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Retrieves the details of a specific customer address by customer ID and address ID."""
    path: DeprecatedUnstableGetCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: delete_customer_address_unstable
class DeprecatedUnstableDeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose address is being removed.")
    address_id: str = Field(default=..., description="The unique identifier of the address to be deleted from the customer's address list.")
class DeprecatedUnstableDeleteCustomersParamCustomerIdAddressesParamAddressIdRequest(StrictModel):
    """Permanently removes a specific address from a customer's address list. This action cannot be undone."""
    path: DeprecatedUnstableDeleteCustomersParamCustomerIdAddressesParamAddressIdRequestPath

# Operation: set_customer_default_address_unstable
class DeprecatedUnstableUpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose default address is being updated.")
    address_id: str = Field(default=..., description="The unique identifier of the address to set as the customer's default address.")
class DeprecatedUnstableUpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequest(StrictModel):
    """Sets a specific address as the default address for a customer. The customer's default address is used for shipping and billing purposes unless overridden during checkout."""
    path: DeprecatedUnstableUpdateCustomersParamCustomerIdAddressesParamAddressIdDefaultRequestPath

# Operation: list_customer_orders_unstable
class DeprecatedUnstableGetCustomersParamCustomerIdOrdersRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer whose orders should be retrieved.")
class DeprecatedUnstableGetCustomersParamCustomerIdOrdersRequest(StrictModel):
    """Retrieves all orders for a specific customer. Supports the same query parameters available for the Order resource to enable filtering, sorting, and pagination."""
    path: DeprecatedUnstableGetCustomersParamCustomerIdOrdersRequestPath

# Operation: send_customer_invite_unstable
class DeprecatedUnstableCreateCustomersParamCustomerIdSendInviteRequestPath(StrictModel):
    customer_id: str = Field(default=..., description="The unique identifier of the customer who will receive the account invite.")
class DeprecatedUnstableCreateCustomersParamCustomerIdSendInviteRequest(StrictModel):
    """Sends an account invitation to a customer, allowing them to create or access their account on the store."""
    path: DeprecatedUnstableCreateCustomersParamCustomerIdSendInviteRequestPath

# Operation: list_events_unstable
class DeprecatedUnstableGetEventsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of events to return per request, between 1 and 250. Defaults to 50 if not specified.")
    filter_: Any | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter events by specific criteria to narrow results to relevant events only.")
    verb: Any | None = Field(default=None, description="Filter events by type or action (e.g., 'create', 'update', 'delete') to show only events of a certain kind.")
class DeprecatedUnstableGetEventsRequest(StrictModel):
    """Retrieves a paginated list of events from your Shopify store. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the page parameter."""
    query: DeprecatedUnstableGetEventsRequestQuery | None = None

# Operation: get_fulfillment_order_unstable
class DeprecatedUnstableGetFulfillmentOrdersParamFulfillmentOrderIdRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to retrieve.")
class DeprecatedUnstableGetFulfillmentOrdersParamFulfillmentOrderIdRequest(StrictModel):
    """Retrieves the details of a specific fulfillment order by its ID. Use this to fetch current status, line items, and fulfillment information for a particular order."""
    path: DeprecatedUnstableGetFulfillmentOrdersParamFulfillmentOrderIdRequestPath

# Operation: cancel_fulfillment_order_unstable
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel. This ID references a specific fulfillment order in the system.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequest(StrictModel):
    """Cancels a fulfillment order, marking it as no longer needed for processing. This operation is useful when orders need to be cancelled before they are fulfilled."""
    path: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancelRequestPath

# Operation: send_fulfillment_order_cancellation_request_unstable
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to cancel. This ID must correspond to an existing fulfillment order in the system.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for the cancellation request. This message is typically sent to the fulfillment service to provide context for the cancellation.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequest(StrictModel):
    """Sends a cancellation request to the fulfillment service for a specific fulfillment order. This notifies the fulfillment provider that the order should be cancelled if not yet processed."""
    path: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestPath
    query: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestQuery | None = None

# Operation: accept_fulfillment_order_cancellation_request_unstable
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to accept the cancellation request.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for accepting the cancellation request.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequest(StrictModel):
    """Accepts a cancellation request for a fulfillment order, notifying the fulfillment service that the cancellation has been approved. Optionally include a reason for accepting the cancellation."""
    path: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestPath
    query: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_order_cancellation_request_unstable
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which you are rejecting the cancellation request.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining why the cancellation request is being rejected. This reason may be communicated to the fulfillment service.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequest(StrictModel):
    """Rejects a cancellation request that was sent to a fulfillment service for a specific fulfillment order. Use this to deny a cancellation and keep the fulfillment order active."""
    path: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestPath
    query: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCancellationRequestRejectRequestQuery | None = None

# Operation: close_fulfillment_order_unstable
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to close.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional reason or message explaining why the fulfillment order is being marked as incomplete.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequest(StrictModel):
    """Marks an in-progress fulfillment order as incomplete, indicating the fulfillment service cannot ship remaining items and is closing the order."""
    path: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestPath
    query: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdCloseRequestQuery | None = None

# Operation: send_fulfillment_request_unstable
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to request fulfillment for.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message to include with the fulfillment request, such as special instructions or notes for the fulfillment service.")
    fulfillment_order_line_items: Any | None = Field(default=None, description="An optional list of specific line items from the fulfillment order to request for fulfillment. If omitted, all line items in the fulfillment order will be requested for fulfillment.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequest(StrictModel):
    """Sends a fulfillment request to the fulfillment service for a specific fulfillment order, optionally specifying which line items to fulfill and including an optional message."""
    path: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestPath
    query: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestQuery | None = None

# Operation: accept_fulfillment_request_unstable
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request is being accepted.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message providing context or reasoning for accepting the fulfillment request.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequest(StrictModel):
    """Accepts a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, confirming that the fulfillment service will proceed with fulfilling the order."""
    path: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestPath
    query: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestAcceptRequestQuery | None = None

# Operation: reject_fulfillment_request_unstable
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which the fulfillment request should be rejected.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery(StrictModel):
    message: Any | None = Field(default=None, description="An optional message explaining the reason for rejecting the fulfillment request.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequest(StrictModel):
    """Rejects a fulfillment request that was sent to a fulfillment service for a specific fulfillment order, optionally providing a reason for the rejection."""
    path: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestPath
    query: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdFulfillmentRequestRejectRequestQuery | None = None

# Operation: list_locations_for_fulfillment_order_move_unstable
class DeprecatedUnstableGetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order for which to retrieve available move destinations.")
class DeprecatedUnstableGetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequest(StrictModel):
    """Retrieves an alphabetically sorted list of locations where a fulfillment order can be moved. Use this to determine valid destination locations before initiating a fulfillment order transfer."""
    path: DeprecatedUnstableGetFulfillmentOrdersParamFulfillmentOrderIdLocationsForMoveRequestPath

# Operation: open_fulfillment_order_unstable
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdOpenRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to open for fulfillment.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdOpenRequest(StrictModel):
    """Marks a scheduled fulfillment order as ready for fulfillment, allowing merchants to begin work on it before its scheduled fulfill_at datetime."""
    path: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdOpenRequestPath

# Operation: reschedule_fulfillment_order
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdRescheduleRequestPath(StrictModel):
    fulfillment_order_id: str = Field(default=..., description="The unique identifier of the fulfillment order to reschedule.")
class DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdRescheduleRequest(StrictModel):
    """Reschedule a fulfillment order by updating its fulfill_at time. Use this to change when a scheduled fulfillment order will be marked as ready for fulfillment."""
    path: DeprecatedUnstableCreateFulfillmentOrdersParamFulfillmentOrderIdRescheduleRequestPath

# Operation: cancel_fulfillment_unstable
class DeprecatedUnstableCreateFulfillmentsParamFulfillmentIdCancelRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to cancel. This ID references a specific fulfillment order that has been previously created.")
class DeprecatedUnstableCreateFulfillmentsParamFulfillmentIdCancelRequest(StrictModel):
    """Cancels an existing fulfillment order. This operation marks the specified fulfillment as cancelled and updates its status accordingly."""
    path: DeprecatedUnstableCreateFulfillmentsParamFulfillmentIdCancelRequestPath

# Operation: update_fulfillment_tracking_unstable
class DeprecatedUnstableCreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath(StrictModel):
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment whose tracking information should be updated.")
class DeprecatedUnstableCreateFulfillmentsParamFulfillmentIdUpdateTrackingRequest(StrictModel):
    """Updates tracking information for a specific fulfillment, allowing you to modify shipment tracking details after the fulfillment has been created."""
    path: DeprecatedUnstableCreateFulfillmentsParamFulfillmentIdUpdateTrackingRequestPath

# Operation: get_gift_cards_count_unstable
class DeprecatedUnstableGetGiftCardsCountRequestQuery(StrictModel):
    status: Any | None = Field(default=None, description="Filter the count to only include gift cards with a specific status: enabled for active gift cards, or disabled for inactive gift cards. Omit to count all gift cards regardless of status.")
class DeprecatedUnstableGetGiftCardsCountRequest(StrictModel):
    """Retrieves the total count of gift cards, optionally filtered by their enabled or disabled status."""
    query: DeprecatedUnstableGetGiftCardsCountRequestQuery | None = None

# Operation: get_gift_card_unstable
class DeprecatedUnstableGetGiftCardsParamGiftCardIdRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to retrieve.")
class DeprecatedUnstableGetGiftCardsParamGiftCardIdRequest(StrictModel):
    """Retrieves a single gift card by its unique identifier. Use this to fetch detailed information about a specific gift card."""
    path: DeprecatedUnstableGetGiftCardsParamGiftCardIdRequestPath

# Operation: update_gift_card_unstable
class DeprecatedUnstableUpdateGiftCardsParamGiftCardIdRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to update.")
class DeprecatedUnstableUpdateGiftCardsParamGiftCardIdRequest(StrictModel):
    """Updates an existing gift card's expiry date, note, and template suffix. The gift card's balance cannot be modified through this API."""
    path: DeprecatedUnstableUpdateGiftCardsParamGiftCardIdRequestPath

# Operation: disable_gift_card_unstable
class DeprecatedUnstableCreateGiftCardsParamGiftCardIdDisableRequestPath(StrictModel):
    gift_card_id: str = Field(default=..., description="The unique identifier of the gift card to disable.")
class DeprecatedUnstableCreateGiftCardsParamGiftCardIdDisableRequest(StrictModel):
    """Permanently disables a gift card, preventing it from being used for future transactions. This action cannot be reversed."""
    path: DeprecatedUnstableCreateGiftCardsParamGiftCardIdDisableRequestPath

# Operation: list_inventory_items_unstable
class DeprecatedUnstableGetInventoryItemsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of inventory items to return per request, between 1 and 250 items (defaults to 50).")
    ids: str | None = Field(default=None, description="Filter results to specific inventory items by their numeric IDs. Provide as a comma-separated list of integers.")
class DeprecatedUnstableGetInventoryItemsRequest(StrictModel):
    """Retrieves a paginated list of inventory items. Uses cursor-based pagination via response headers; the page parameter is not supported."""
    query: DeprecatedUnstableGetInventoryItemsRequestQuery | None = None

# Operation: get_inventory_item_unstable
class DeprecatedUnstableGetInventoryItemsParamInventoryItemIdRequestPath(StrictModel):
    inventory_item_id: str = Field(default=..., description="The unique identifier of the inventory item to retrieve.")
class DeprecatedUnstableGetInventoryItemsParamInventoryItemIdRequest(StrictModel):
    """Retrieves a single inventory item by its ID. Use this to fetch detailed information about a specific inventory item in your Shopify store."""
    path: DeprecatedUnstableGetInventoryItemsParamInventoryItemIdRequestPath

# Operation: list_inventory_levels_unstable
class DeprecatedUnstableGetInventoryLevelsRequestQuery(StrictModel):
    inventory_item_ids: Any | None = Field(default=None, description="Comma-separated list of inventory item IDs to filter results. Maximum of 50 IDs per request.")
    location_ids: Any | None = Field(default=None, description="Comma-separated list of location IDs to filter results. Maximum of 50 IDs per request. Use the Location resource to find location IDs.")
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request. Defaults to 50 if not specified; cannot exceed 250.")
class DeprecatedUnstableGetInventoryLevelsRequest(StrictModel):
    """Retrieves inventory levels across your store's locations and inventory items. You must filter by at least one inventory item ID or location ID to retrieve results."""
    query: DeprecatedUnstableGetInventoryLevelsRequestQuery | None = None

# Operation: delete_inventory_level_unstable
class DeprecatedUnstableDeleteInventoryLevelsRequestQuery(StrictModel):
    inventory_item_id: int | None = Field(default=None, description="The unique identifier of the inventory item whose level should be deleted.")
    location_id: int | None = Field(default=None, description="The unique identifier of the location from which the inventory item should be removed.")
class DeprecatedUnstableDeleteInventoryLevelsRequest(StrictModel):
    """Removes an inventory level for a specific inventory item at a location. This disconnects the inventory item from that location; note that every inventory item must maintain at least one inventory level, so ensure the item is connected to another location before deleting its last level."""
    query: DeprecatedUnstableDeleteInventoryLevelsRequestQuery | None = None

# Operation: get_location_unstable
class DeprecatedUnstableGetLocationsParamLocationIdRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location to retrieve.")
class DeprecatedUnstableGetLocationsParamLocationIdRequest(StrictModel):
    """Retrieves a single location by its ID from the Shopify inventory system. Use this to fetch detailed information about a specific location."""
    path: DeprecatedUnstableGetLocationsParamLocationIdRequestPath

# Operation: list_inventory_levels_for_location_unstable
class DeprecatedUnstableGetLocationsParamLocationIdInventoryLevelsRequestPath(StrictModel):
    location_id: str = Field(default=..., description="The unique identifier of the location for which to retrieve inventory levels.")
class DeprecatedUnstableGetLocationsParamLocationIdInventoryLevelsRequest(StrictModel):
    """Retrieves all inventory levels for a specific location. Uses cursor-based pagination via response headers; the page parameter is not supported."""
    path: DeprecatedUnstableGetLocationsParamLocationIdInventoryLevelsRequestPath

# Operation: get_metafield_unstable
class DeprecatedUnstableGetMetafieldsParamMetafieldIdRequestPath(StrictModel):
    metafield_id: str = Field(default=..., description="The unique identifier of the metafield to retrieve.")
class DeprecatedUnstableGetMetafieldsParamMetafieldIdRequest(StrictModel):
    """Retrieves a single metafield by its ID from the Shopify admin API. Use this to fetch detailed information about a specific metafield resource."""
    path: DeprecatedUnstableGetMetafieldsParamMetafieldIdRequestPath

# Operation: update_metafield_unstable
class DeprecatedUnstableUpdateMetafieldsParamMetafieldIdRequestPath(StrictModel):
    metafield_id: str = Field(default=..., description="The unique identifier of the metafield to update. This ID is returned when a metafield is created and is required to target the specific metafield for modification.")
class DeprecatedUnstableUpdateMetafieldsParamMetafieldIdRequest(StrictModel):
    """Updates an existing metafield with new values. Modify metafield properties such as namespace, key, value, and type for the specified metafield resource."""
    path: DeprecatedUnstableUpdateMetafieldsParamMetafieldIdRequestPath

# Operation: list_fulfillment_orders_for_order
class DeprecatedUnstableGetOrdersParamOrderIdFulfillmentOrdersRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve fulfillment orders.")
class DeprecatedUnstableGetOrdersParamOrderIdFulfillmentOrdersRequest(StrictModel):
    """Retrieves all fulfillment orders associated with a specific order, allowing you to track fulfillment status and details across multiple fulfillment locations."""
    path: DeprecatedUnstableGetOrdersParamOrderIdFulfillmentOrdersRequestPath

# Operation: list_fulfillments_for_order_unstable
class DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order whose fulfillments you want to retrieve.")
class DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of fulfillments to return per request, between 1 and 250 (defaults to 50).")
class DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Retrieves all fulfillments associated with a specific order. Results are paginated using link headers in the response; use the provided links to navigate pages rather than the limit parameter."""
    path: DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsRequestPath
    query: DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsRequestQuery | None = None

# Operation: create_fulfillment_for_order_unstable
class DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the fulfillment.")
class DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsRequest(StrictModel):
    """Create a fulfillment for specified line items in an order. The fulfillment status depends on the fulfillment service type: manual/custom services set status immediately, while external services queue the fulfillment with pending status until processed."""
    path: DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsRequestPath

# Operation: get_fulfillment_count_for_order_unstable
class DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsCountRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve the fulfillment count.")
class DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsCountRequest(StrictModel):
    """Retrieves the total count of fulfillments associated with a specific order. Useful for understanding how many fulfillment operations have been created for an order without fetching full fulfillment details."""
    path: DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsCountRequestPath

# Operation: get_fulfillment_unstable
class DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to retrieve.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to retrieve.")
class DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Retrieve detailed information about a specific fulfillment for an order, including its status, line items, and tracking information."""
    path: DeprecatedUnstableGetOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: update_fulfillment_unstable
class DeprecatedUnstableUpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to update.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to update.")
class DeprecatedUnstableUpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequest(StrictModel):
    """Update fulfillment details for a specific order, such as tracking information or fulfillment status."""
    path: DeprecatedUnstableUpdateOrdersParamOrderIdFulfillmentsParamFulfillmentIdRequestPath

# Operation: cancel_fulfillment_order_unstable_2
class DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to cancel.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to cancel within the specified order.")
class DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequest(StrictModel):
    """Cancel an active fulfillment for a specific order. This operation marks the fulfillment as cancelled and prevents further shipment processing."""
    path: DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCancelRequestPath

# Operation: complete_fulfillment_unstable
class DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to be completed.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to mark as complete.")
class DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequest(StrictModel):
    """Mark a fulfillment as complete, indicating that all items in the fulfillment have been shipped or delivered to the customer."""
    path: DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdCompleteRequestPath

# Operation: create_fulfillment_event_unstable
class DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment for which to create the event.")
class DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequest(StrictModel):
    """Creates a fulfillment event for a specific fulfillment within an order. This records status updates and tracking information for the fulfillment."""
    path: DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdEventsRequestPath

# Operation: open_fulfillment_unstable
class DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the fulfillment to be opened.")
    fulfillment_id: str = Field(default=..., description="The unique identifier of the fulfillment to mark as open.")
class DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequest(StrictModel):
    """Mark a fulfillment as open, allowing it to receive additional items or changes. This operation transitions a fulfillment from a closed or pending state to an open state."""
    path: DeprecatedUnstableCreateOrdersParamOrderIdFulfillmentsParamFulfillmentIdOpenRequestPath

# Operation: list_order_refunds_unstable
class DeprecatedUnstableGetOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve refunds.")
class DeprecatedUnstableGetOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of refunds to return per request, between 1 and 250 (defaults to 50).")
    in_shop_currency: Any | None = Field(default=None, description="When true, displays monetary amounts in the shop's currency for the underlying transaction; defaults to false.")
class DeprecatedUnstableGetOrdersParamOrderIdRefundsRequest(StrictModel):
    """Retrieves a paginated list of refunds for a specific order. Results are paginated using link headers in the response; the page parameter is not supported."""
    path: DeprecatedUnstableGetOrdersParamOrderIdRefundsRequestPath
    query: DeprecatedUnstableGetOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: create_order_refund_unstable
class DeprecatedUnstableCreateOrdersParamOrderIdRefundsRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create a refund.")
class DeprecatedUnstableCreateOrdersParamOrderIdRefundsRequestQuery(StrictModel):
    notify: Any | None = Field(default=None, description="Whether to send a refund notification email to the customer.")
    note: Any | None = Field(default=None, description="An optional note to attach to the refund for internal reference.")
    discrepancy_reason: Any | None = Field(default=None, description="An optional reason explaining any discrepancy between calculated and actual refund amounts. Valid values are: restock, damage, customer, or other.")
    shipping: Any | None = Field(default=None, description="Shipping refund details. Specify either full_refund to refund all remaining shipping, or amount to refund a specific shipping amount (takes precedence over full_refund).")
    refund_line_items: Any | None = Field(default=None, description="A list of line items to refund, each with the line item ID, quantity to refund, restock type (no_restock, cancel, or return), and location ID (required for cancel or return restock types).")
    transactions: Any | None = Field(default=None, description="A list of transactions to process as refunds. Should be obtained from the calculate endpoint for accuracy.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required for multi-currency orders when an amount property is provided.")
class DeprecatedUnstableCreateOrdersParamOrderIdRefundsRequest(StrictModel):
    """Creates a refund for an order. Use the calculate endpoint first to determine the correct transactions to submit. For multi-currency orders, the currency property is required whenever an amount is specified."""
    path: DeprecatedUnstableCreateOrdersParamOrderIdRefundsRequestPath
    query: DeprecatedUnstableCreateOrdersParamOrderIdRefundsRequestQuery | None = None

# Operation: calculate_refund_for_order
class DeprecatedUnstableCreateOrdersParamOrderIdRefundsCalculateRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to calculate the refund.")
class DeprecatedUnstableCreateOrdersParamOrderIdRefundsCalculateRequestQuery(StrictModel):
    shipping: Any | None = Field(default=None, description="Specifies how much shipping to refund. Provide either a full refund flag or a specific amount; if both are provided, the amount takes precedence.")
    refund_line_items: Any | None = Field(default=None, description="A list of line items to refund, each specifying the line item ID, quantity to refund, how it affects inventory (no_restock, cancel, or return), and optionally the location where items should be restocked. If no location is provided for return or cancel operations, the endpoint will suggest one.")
    currency: Any | None = Field(default=None, description="The three-letter ISO 4217 currency code for the refund. Required whenever a shipping amount is specified; essential for multi-currency orders.")
class DeprecatedUnstableCreateOrdersParamOrderIdRefundsCalculateRequest(StrictModel):
    """Calculates refund transactions for an order based on specified line items, quantities, restock instructions, and shipping costs. Use this endpoint to generate accurate refund details before creating an actual refund; the response includes suggested transactions that must be converted to refund transactions in the creation request."""
    path: DeprecatedUnstableCreateOrdersParamOrderIdRefundsCalculateRequestPath
    query: DeprecatedUnstableCreateOrdersParamOrderIdRefundsCalculateRequestQuery | None = None

# Operation: get_refund_unstable
class DeprecatedUnstableGetOrdersParamOrderIdRefundsParamRefundIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the refund.")
    refund_id: str = Field(default=..., description="The unique identifier of the refund to retrieve.")
class DeprecatedUnstableGetOrdersParamOrderIdRefundsParamRefundIdRequestQuery(StrictModel):
    in_shop_currency: Any | None = Field(default=None, description="When enabled, displays all monetary amounts in the shop's native currency rather than the transaction currency. Defaults to false.")
class DeprecatedUnstableGetOrdersParamOrderIdRefundsParamRefundIdRequest(StrictModel):
    """Retrieves the details of a specific refund for an order. Use this to view refund information including amounts, reason, and status."""
    path: DeprecatedUnstableGetOrdersParamOrderIdRefundsParamRefundIdRequestPath
    query: DeprecatedUnstableGetOrdersParamOrderIdRefundsParamRefundIdRequestQuery | None = None

# Operation: list_order_risks_unstable
class DeprecatedUnstableGetOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to retrieve risk assessments.")
class DeprecatedUnstableGetOrdersParamOrderIdRisksRequest(StrictModel):
    """Retrieves all fraud and risk assessments associated with a specific order. Results are paginated using link headers in the response."""
    path: DeprecatedUnstableGetOrdersParamOrderIdRisksRequestPath

# Operation: create_order_risk_unstable
class DeprecatedUnstableCreateOrdersParamOrderIdRisksRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order for which to create the risk record. This must be a valid order ID from your Shopify store.")
class DeprecatedUnstableCreateOrdersParamOrderIdRisksRequest(StrictModel):
    """Creates a risk assessment record for a specific order. Use this to flag potential issues or concerns associated with an order that may require review or action."""
    path: DeprecatedUnstableCreateOrdersParamOrderIdRisksRequestPath

# Operation: get_order_risk_unstable
class DeprecatedUnstableGetOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk assessment.")
    risk_id: str = Field(default=..., description="The unique identifier of the specific risk assessment to retrieve.")
class DeprecatedUnstableGetOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Retrieves a single risk assessment for an order. Use this to fetch detailed information about a specific fraud or security risk flagged on an order."""
    path: DeprecatedUnstableGetOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: update_order_risk_unstable
class DeprecatedUnstableUpdateOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to be updated.")
    risk_id: str = Field(default=..., description="The unique identifier of the order risk to be updated.")
class DeprecatedUnstableUpdateOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Updates an existing order risk. Note that you cannot modify an order risk that was created by another application."""
    path: DeprecatedUnstableUpdateOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: delete_order_risk_unstable
class DeprecatedUnstableDeleteOrdersParamOrderIdRisksParamRiskIdRequestPath(StrictModel):
    order_id: str = Field(default=..., description="The unique identifier of the order containing the risk to be deleted.")
    risk_id: str = Field(default=..., description="The unique identifier of the risk assessment to be deleted from the order.")
class DeprecatedUnstableDeleteOrdersParamOrderIdRisksParamRiskIdRequest(StrictModel):
    """Removes a specific risk assessment from an order. Note that you can only delete risks created by your application; risks created by other applications cannot be deleted."""
    path: DeprecatedUnstableDeleteOrdersParamOrderIdRisksParamRiskIdRequestPath

# Operation: create_discount_codes_batch_unstable
class DeprecatedUnstableCreatePriceRulesParamPriceRuleIdBatchRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which discount codes will be created.")
class DeprecatedUnstableCreatePriceRulesParamPriceRuleIdBatchRequest(StrictModel):
    """Asynchronously creates up to 100 discount codes for a price rule in a single batch job. Returns a discount code creation job object that can be monitored for completion status, including counts of successful and failed code creations."""
    path: DeprecatedUnstableCreatePriceRulesParamPriceRuleIdBatchRequestPath

# Operation: get_discount_code_batch_unstable
class DeprecatedUnstableGetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch job.")
    batch_id: str = Field(default=..., description="The unique identifier of the batch job to retrieve status and results for.")
class DeprecatedUnstableGetPriceRulesParamPriceRuleIdBatchParamBatchIdRequest(StrictModel):
    """Retrieves the status and details of a discount code creation job batch for a specific price rule."""
    path: DeprecatedUnstableGetPriceRulesParamPriceRuleIdBatchParamBatchIdRequestPath

# Operation: list_discount_codes_for_batch_unstable
class DeprecatedUnstableGetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule associated with the discount code batch job.")
    batch_id: str = Field(default=..., description="The unique identifier of the batch job that generated the discount codes.")
class DeprecatedUnstableGetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequest(StrictModel):
    """Retrieves all discount codes generated from a batch creation job for a specific price rule. Results include successfully created codes with populated IDs and codes that failed with error details."""
    path: DeprecatedUnstableGetPriceRulesParamPriceRuleIdBatchParamBatchIdDiscountCodesRequestPath

# Operation: list_discount_codes_for_price_rule_unstable
class DeprecatedUnstableGetPriceRulesParamPriceRuleIdDiscountCodesRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule for which to retrieve associated discount codes.")
class DeprecatedUnstableGetPriceRulesParamPriceRuleIdDiscountCodesRequest(StrictModel):
    """Retrieve all discount codes associated with a specific price rule. Results are paginated using link headers in the response; use the provided links to navigate pages rather than query parameters."""
    path: DeprecatedUnstableGetPriceRulesParamPriceRuleIdDiscountCodesRequestPath

# Operation: get_discount_code_unstable
class DeprecatedUnstableGetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to retrieve.")
class DeprecatedUnstableGetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Retrieves a single discount code associated with a specific price rule. Use this to fetch details about a discount code by its ID."""
    path: DeprecatedUnstableGetPriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: update_discount_code_for_price_rule
class DeprecatedUnstableUpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code being updated.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to update.")
class DeprecatedUnstableUpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Updates an existing discount code associated with a price rule. Modify discount code properties such as code value, usage limits, or other configurations."""
    path: DeprecatedUnstableUpdatePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: delete_discount_code_for_price_rule
class DeprecatedUnstableDeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath(StrictModel):
    price_rule_id: str = Field(default=..., description="The unique identifier of the price rule that contains the discount code to be deleted.")
    discount_code_id: str = Field(default=..., description="The unique identifier of the discount code to be deleted from the price rule.")
class DeprecatedUnstableDeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequest(StrictModel):
    """Removes a specific discount code associated with a price rule. This operation permanently deletes the discount code and cannot be undone."""
    path: DeprecatedUnstableDeletePriceRulesParamPriceRuleIdDiscountCodesParamDiscountCodeIdRequestPath

# Operation: get_product_unstable
class DeprecatedUnstableGetProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to retrieve.")
class DeprecatedUnstableGetProductsParamProductIdRequest(StrictModel):
    """Retrieves detailed information for a single product by its ID from the Shopify store."""
    path: DeprecatedUnstableGetProductsParamProductIdRequestPath

# Operation: update_product_unstable
class DeprecatedUnstableUpdateProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to update.")
class DeprecatedUnstableUpdateProductsParamProductIdRequest(StrictModel):
    """Updates a product's details, variants, images, and SEO metadata. Use metafields_global_title_tag and metafields_global_description_tag to manage SEO title and description tags."""
    path: DeprecatedUnstableUpdateProductsParamProductIdRequestPath

# Operation: delete_product_unstable
class DeprecatedUnstableDeleteProductsParamProductIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to delete. This is a required string value that specifies which product should be removed.")
class DeprecatedUnstableDeleteProductsParamProductIdRequest(StrictModel):
    """Permanently deletes a product from the store. This action cannot be undone and will remove the product and all associated data."""
    path: DeprecatedUnstableDeleteProductsParamProductIdRequestPath

# Operation: list_product_images_unstable
class DeprecatedUnstableGetProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product whose images you want to retrieve.")
class DeprecatedUnstableGetProductsParamProductIdImagesRequest(StrictModel):
    """Retrieve all images associated with a specific product. Returns a collection of product image objects for the given product ID."""
    path: DeprecatedUnstableGetProductsParamProductIdImagesRequestPath

# Operation: create_product_image_unstable
class DeprecatedUnstableCreateProductsParamProductIdImagesRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product to which the image will be added.")
class DeprecatedUnstableCreateProductsParamProductIdImagesRequest(StrictModel):
    """Create a new image for a product. The image will be associated with the specified product and can be used to display the product in your storefront."""
    path: DeprecatedUnstableCreateProductsParamProductIdImagesRequestPath

# Operation: get_product_images_count_unstable
class DeprecatedUnstableGetProductsParamProductIdImagesCountRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product for which to retrieve the image count.")
class DeprecatedUnstableGetProductsParamProductIdImagesCountRequest(StrictModel):
    """Retrieve the total count of images associated with a specific product. Useful for understanding product image inventory without fetching the full image list."""
    path: DeprecatedUnstableGetProductsParamProductIdImagesCountRequestPath

# Operation: delete_product_image_unstable
class DeprecatedUnstableDeleteProductsParamProductIdImagesParamImageIdRequestPath(StrictModel):
    product_id: str = Field(default=..., description="The unique identifier of the product containing the image to delete.")
    image_id: str = Field(default=..., description="The unique identifier of the image to delete from the product.")
class DeprecatedUnstableDeleteProductsParamProductIdImagesParamImageIdRequest(StrictModel):
    """Delete a specific image from a product. This operation removes the image association from the product permanently."""
    path: DeprecatedUnstableDeleteProductsParamProductIdImagesParamImageIdRequestPath

# Operation: delete_recurring_application_charge_unstable
class DeprecatedUnstableDeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to cancel. This ID is returned when the charge is created.")
class DeprecatedUnstableDeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequest(StrictModel):
    """Cancels an active recurring application charge for the app. This operation permanently removes the recurring billing arrangement between the app and the store."""
    path: DeprecatedUnstableDeleteRecurringApplicationChargesParamRecurringApplicationChargeIdRequestPath

# Operation: update_recurring_application_charge_capped_amount_unstable
class DeprecatedUnstableUpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge to customize.")
class DeprecatedUnstableUpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery(StrictModel):
    recurring_application_charge_capped_amount: int | None = Field(default=None, validation_alias="recurring_application_charge[capped_amount]", serialization_alias="recurring_application_charge[capped_amount]", description="The new capped amount in cents. This sets the maximum charge amount for the billing cycle.")
class DeprecatedUnstableUpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequest(StrictModel):
    """Updates the capped amount for an active recurring application charge. This allows you to modify the maximum amount that will be charged to the merchant during the billing cycle."""
    path: DeprecatedUnstableUpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestPath
    query: DeprecatedUnstableUpdateRecurringApplicationChargesParamRecurringApplicationChargeIdCustomizeRequestQuery | None = None

# Operation: list_usage_charges_for_recurring_application_charge_unstable
class DeprecatedUnstableGetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge for which to retrieve usage charges.")
class DeprecatedUnstableGetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Retrieves all usage charges associated with a specific recurring application charge. Usage charges represent variable billing amounts applied to a recurring subscription."""
    path: DeprecatedUnstableGetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath

# Operation: create_usage_charge_for_recurring_application_charge_unstable
class DeprecatedUnstableCreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge for which to create the usage charge.")
class DeprecatedUnstableCreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequest(StrictModel):
    """Creates a usage charge against an existing recurring application charge. Usage charges allow you to bill customers for variable usage on top of their recurring subscription."""
    path: DeprecatedUnstableCreateRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesRequestPath

# Operation: get_usage_charge_for_recurring_application_charge_unstable
class DeprecatedUnstableGetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath(StrictModel):
    recurring_application_charge_id: str = Field(default=..., description="The unique identifier of the recurring application charge that contains the usage charge you want to retrieve.")
    usage_charge_id: str = Field(default=..., description="The unique identifier of the specific usage charge to retrieve.")
class DeprecatedUnstableGetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequest(StrictModel):
    """Retrieves a single usage charge associated with a recurring application charge. Use this to fetch details about a specific metered billing charge."""
    path: DeprecatedUnstableGetRecurringApplicationChargesParamRecurringApplicationChargeIdUsageChargesParamUsageChargeIdRequestPath

# Operation: list_redirects_unstable
class DeprecatedUnstableGetRedirectsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of redirects to return per request, between 1 and 250 (defaults to 50).")
    path: Any | None = Field(default=None, description="Filter results to show only redirects with a specific source path.")
    target: Any | None = Field(default=None, description="Filter results to show only redirects pointing to a specific target URL.")
class DeprecatedUnstableGetRedirectsRequest(StrictModel):
    """Retrieves a list of URL redirects configured in the online store. Results are paginated using link headers in the response rather than page parameters."""
    query: DeprecatedUnstableGetRedirectsRequestQuery | None = None

# Operation: count_redirects
class DeprecatedUnstableGetRedirectsCountRequestQuery(StrictModel):
    path: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific path value.")
    target: Any | None = Field(default=None, description="Filter the count to only include redirects with this specific target URL.")
class DeprecatedUnstableGetRedirectsCountRequest(StrictModel):
    """Retrieves the total count of URL redirects in the store, with optional filtering by path or target URL."""
    query: DeprecatedUnstableGetRedirectsCountRequestQuery | None = None

# Operation: get_redirect_unstable
class DeprecatedUnstableGetRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to retrieve.")
class DeprecatedUnstableGetRedirectsParamRedirectIdRequest(StrictModel):
    """Retrieves a single redirect by its ID from the Shopify online store. Use this to fetch details about a specific URL redirect configuration."""
    path: DeprecatedUnstableGetRedirectsParamRedirectIdRequestPath

# Operation: update_redirect_unstable
class DeprecatedUnstableUpdateRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to update. This ID is required to locate and modify the specific redirect rule.")
class DeprecatedUnstableUpdateRedirectsParamRedirectIdRequest(StrictModel):
    """Updates an existing redirect configuration in the online store. Modify redirect rules by providing the redirect ID and updated redirect details."""
    path: DeprecatedUnstableUpdateRedirectsParamRedirectIdRequestPath

# Operation: delete_redirect_unstable
class DeprecatedUnstableDeleteRedirectsParamRedirectIdRequestPath(StrictModel):
    redirect_id: str = Field(default=..., description="The unique identifier of the redirect to delete. This is a required string value that specifies which redirect rule to remove.")
class DeprecatedUnstableDeleteRedirectsParamRedirectIdRequest(StrictModel):
    """Permanently deletes a redirect from the online store. This operation removes the redirect rule and cannot be undone."""
    path: DeprecatedUnstableDeleteRedirectsParamRedirectIdRequestPath

# Operation: list_reports_unstable
class DeprecatedUnstableGetReportsRequestQuery(StrictModel):
    ids: Any | None = Field(default=None, description="Filter results by one or more report IDs using a comma-separated list.")
    limit: Any | None = Field(default=None, description="Maximum number of reports to return per request, ranging from 1 to 250 (defaults to 50).")
class DeprecatedUnstableGetReportsRequest(StrictModel):
    """Retrieves a list of reports from the Shopify Admin API. This endpoint uses cursor-based pagination via response headers; the legacy page parameter is not supported."""
    query: DeprecatedUnstableGetReportsRequestQuery | None = None

# Operation: delete_report_unstable
class DeprecatedUnstableDeleteReportsParamReportIdRequestPath(StrictModel):
    report_id: str = Field(default=..., description="The unique identifier of the report to delete. This ID must correspond to an existing report in your Shopify store.")
class DeprecatedUnstableDeleteReportsParamReportIdRequest(StrictModel):
    """Permanently deletes a report from the Shopify Admin. This operation removes the report and all associated data."""
    path: DeprecatedUnstableDeleteReportsParamReportIdRequestPath

# Operation: list_script_tags_unstable
class DeprecatedUnstableGetScriptTagsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of script tags to return per request, between 1 and 250 (defaults to 50).")
class DeprecatedUnstableGetScriptTagsRequest(StrictModel):
    """Retrieves a list of all script tags from the online store. Uses cursor-based pagination via response headers; the page parameter is not supported."""
    query: DeprecatedUnstableGetScriptTagsRequestQuery | None = None

# Operation: list_shopify_payments_payouts_unstable
class DeprecatedUnstableGetShopifyPaymentsPayoutsRequestQuery(StrictModel):
    date_min: Any | None = Field(default=None, description="Filter payouts to include only those made on or after this date (inclusive). Specify as an ISO 8601 formatted date.")
    date_max: Any | None = Field(default=None, description="Filter payouts to include only those made on or before this date (inclusive). Specify as an ISO 8601 formatted date.")
    status: Any | None = Field(default=None, description="Filter payouts by their current status (e.g., pending, completed, failed, cancelled).")
class DeprecatedUnstableGetShopifyPaymentsPayoutsRequest(StrictModel):
    """Retrieves a list of all payouts from Shopify Payments, ordered by payout date with the most recent first. Results are paginated using link headers in the response."""
    query: DeprecatedUnstableGetShopifyPaymentsPayoutsRequestQuery | None = None

# Operation: get_shopify_payments_payout
class DeprecatedUnstableGetShopifyPaymentsPayoutsParamPayoutIdRequestPath(StrictModel):
    payout_id: str = Field(default=..., description="The unique identifier of the payout to retrieve.")
class DeprecatedUnstableGetShopifyPaymentsPayoutsParamPayoutIdRequest(StrictModel):
    """Retrieves details for a specific Shopify Payments payout by its unique identifier."""
    path: DeprecatedUnstableGetShopifyPaymentsPayoutsParamPayoutIdRequestPath

# Operation: list_smart_collections_unstable
class DeprecatedUnstableGetSmartCollectionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of smart collections to return per request. Defaults to 50 and cannot exceed 250.")
    ids: Any | None = Field(default=None, description="Filter results to only smart collections with the specified IDs. Provide as a comma-separated list of numeric IDs.")
    title: Any | None = Field(default=None, description="Filter results to smart collections matching the exact title.")
    product_id: Any | None = Field(default=None, description="Filter results to only smart collections that contain the specified product ID.")
    handle: Any | None = Field(default=None, description="Filter results by smart collection handle (the URL-friendly identifier).")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: 'published' for published collections only, 'unpublished' for unpublished collections only, or 'any' for all collections regardless of status. Defaults to 'any'.")
class DeprecatedUnstableGetSmartCollectionsRequest(StrictModel):
    """Retrieves a paginated list of smart collections from the store. Results are paginated using link headers in the response."""
    query: DeprecatedUnstableGetSmartCollectionsRequestQuery | None = None

# Operation: count_smart_collections_unstable
class DeprecatedUnstableGetSmartCollectionsCountRequestQuery(StrictModel):
    title: Any | None = Field(default=None, description="Filter to smart collections with an exact matching title.")
    product_id: Any | None = Field(default=None, description="Filter to smart collections that contain the specified product ID.")
    published_status: Any | None = Field(default=None, description="Filter results by publication status: published (live collections only), unpublished (draft collections only), or any (all collections). Defaults to any.")
class DeprecatedUnstableGetSmartCollectionsCountRequest(StrictModel):
    """Retrieves the total count of smart collections, with optional filtering by title, product inclusion, or published status."""
    query: DeprecatedUnstableGetSmartCollectionsCountRequestQuery | None = None

# Operation: get_smart_collection_unstable
class DeprecatedUnstableGetSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to retrieve.")
class DeprecatedUnstableGetSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Retrieves the details of a single smart collection by its ID. Use this to fetch configuration, rules, and metadata for a specific smart collection."""
    path: DeprecatedUnstableGetSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: update_smart_collection_unstable
class DeprecatedUnstableUpdateSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to update.")
class DeprecatedUnstableUpdateSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Updates the configuration and settings of an existing smart collection, allowing you to modify its rules, name, and other properties."""
    path: DeprecatedUnstableUpdateSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: delete_smart_collection_unstable
class DeprecatedUnstableDeleteSmartCollectionsParamSmartCollectionIdRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to delete.")
class DeprecatedUnstableDeleteSmartCollectionsParamSmartCollectionIdRequest(StrictModel):
    """Permanently removes a smart collection from the store. This action cannot be undone."""
    path: DeprecatedUnstableDeleteSmartCollectionsParamSmartCollectionIdRequestPath

# Operation: update_smart_collection_order_unstable
class DeprecatedUnstableUpdateSmartCollectionsParamSmartCollectionIdOrderRequestPath(StrictModel):
    smart_collection_id: str = Field(default=..., description="The unique identifier of the smart collection to update.")
class DeprecatedUnstableUpdateSmartCollectionsParamSmartCollectionIdOrderRequestQuery(StrictModel):
    products: Any | None = Field(default=None, description="An ordered array of product IDs to pin at the top of the collection. When provided as an empty array, any previously pinned products are cleared and the collection reverts to its sort_order configuration.")
    sort_order: Any | None = Field(default=None, description="The sorting method to apply to the collection. Valid options include alphabetical, price-based, newest, and best-selling. If not specified, the current sort order is preserved.")
class DeprecatedUnstableUpdateSmartCollectionsParamSmartCollectionIdOrderRequest(StrictModel):
    """Updates the sorting configuration for products in a smart collection, allowing you to manually order specific products at the top or apply a predefined sort type across the entire collection."""
    path: DeprecatedUnstableUpdateSmartCollectionsParamSmartCollectionIdOrderRequestPath
    query: DeprecatedUnstableUpdateSmartCollectionsParamSmartCollectionIdOrderRequestQuery | None = None

# Operation: delete_storefront_access_token_unstable
class DeprecatedUnstableDeleteStorefrontAccessTokensParamStorefrontAccessTokenIdRequestPath(StrictModel):
    storefront_access_token_id: str = Field(default=..., description="The unique identifier of the storefront access token to delete.")
class DeprecatedUnstableDeleteStorefrontAccessTokensParamStorefrontAccessTokenIdRequest(StrictModel):
    """Permanently deletes a storefront access token, revoking its access to the Storefront API. This action cannot be undone."""
    path: DeprecatedUnstableDeleteStorefrontAccessTokensParamStorefrontAccessTokenIdRequestPath

# Operation: list_tender_transactions_unstable
class DeprecatedUnstableGetTenderTransactionsRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of results to return per request, between 1 and 250 (defaults to 50).")
    processed_at_min: Any | None = Field(default=None, description="Filter to show only tender transactions processed on or after this date (ISO 8601 format).")
    processed_at_max: Any | None = Field(default=None, description="Filter to show only tender transactions processed on or before this date (ISO 8601 format).")
    order: Any | None = Field(default=None, description="Sort results by processed_at timestamp in either ascending or descending order.")
class DeprecatedUnstableGetTenderTransactionsRequest(StrictModel):
    """Retrieves a paginated list of tender transactions processed within a specified date range. Results are paginated using link headers provided in the response."""
    query: DeprecatedUnstableGetTenderTransactionsRequestQuery | None = None

# Operation: get_theme_unstable
class DeprecatedUnstableGetThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to retrieve.")
class DeprecatedUnstableGetThemesParamThemeIdRequest(StrictModel):
    """Retrieves a single theme by its ID from the Shopify online store. Use this to fetch detailed information about a specific theme."""
    path: DeprecatedUnstableGetThemesParamThemeIdRequestPath

# Operation: delete_theme_unstable
class DeprecatedUnstableDeleteThemesParamThemeIdRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme to delete.")
class DeprecatedUnstableDeleteThemesParamThemeIdRequest(StrictModel):
    """Permanently deletes a theme from the store. This action cannot be undone."""
    path: DeprecatedUnstableDeleteThemesParamThemeIdRequestPath

# Operation: delete_theme_asset_unstable
class DeprecatedUnstableDeleteThemesParamThemeIdAssetsRequestPath(StrictModel):
    theme_id: str = Field(default=..., description="The unique identifier of the theme from which the asset will be deleted.")
class DeprecatedUnstableDeleteThemesParamThemeIdAssetsRequestQuery(StrictModel):
    asset_key: str | None = Field(default=None, validation_alias="asset[key]", serialization_alias="asset[key]", description="The key (file path) of the asset to delete from the theme. This identifies which specific asset file to remove.")
class DeprecatedUnstableDeleteThemesParamThemeIdAssetsRequest(StrictModel):
    """Removes a specific asset file from a Shopify theme. The asset is identified by its key within the theme."""
    path: DeprecatedUnstableDeleteThemesParamThemeIdAssetsRequestPath
    query: DeprecatedUnstableDeleteThemesParamThemeIdAssetsRequestQuery | None = None

# Operation: list_users_unstable
class DeprecatedUnstableGetUsersRequestQuery(StrictModel):
    limit: Any | None = Field(default=None, description="Maximum number of users to return per page, between 1 and 250 results (defaults to 50).")
    page_info: Any | None = Field(default=None, description="Cursor token for accessing a specific page of results, obtained from the Link header of the previous response.")
class DeprecatedUnstableGetUsersRequest(StrictModel):
    """Retrieves a paginated list of all users in the system. This endpoint uses cursor-based pagination via link headers rather than page numbers."""
    query: DeprecatedUnstableGetUsersRequestQuery | None = None

# Operation: get_user_unstable
class DeprecatedUnstableGetUsersParamUserIdRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to retrieve.")
class DeprecatedUnstableGetUsersParamUserIdRequest(StrictModel):
    """Retrieves a single user by their ID from the Shopify admin system. This endpoint is part of the unstable API and may change."""
    path: DeprecatedUnstableGetUsersParamUserIdRequestPath

# Operation: count_webhooks
class DeprecatedUnstableGetWebhooksCountRequestQuery(StrictModel):
    address: Any | None = Field(default=None, description="Filter results to webhook subscriptions that deliver POST requests to this specific URI.")
    topic: Any | None = Field(default=None, description="Filter results to webhook subscriptions with a specific topic. Refer to the webhook topic property documentation for valid topic values.")
class DeprecatedUnstableGetWebhooksCountRequest(StrictModel):
    """Retrieves the total count of webhook subscriptions configured in the store, with optional filtering by delivery address or topic."""
    query: DeprecatedUnstableGetWebhooksCountRequestQuery | None = None

# Operation: get_webhook_unstable
class DeprecatedUnstableGetWebhooksParamWebhookIdRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook subscription to retrieve.")
class DeprecatedUnstableGetWebhooksParamWebhookIdRequest(StrictModel):
    """Retrieves the details of a single webhook subscription by its ID, including its configuration, topics, and delivery settings."""
    path: DeprecatedUnstableGetWebhooksParamWebhookIdRequestPath

# Operation: delete_webhook
class DeprecatedUnstableDeleteWebhooksParamWebhookIdRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook subscription to delete.")
class DeprecatedUnstableDeleteWebhooksParamWebhookIdRequest(StrictModel):
    """Delete a webhook subscription by its ID. This permanently removes the webhook and stops it from receiving events."""
    path: DeprecatedUnstableDeleteWebhooksParamWebhookIdRequestPath

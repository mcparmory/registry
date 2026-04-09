"""
Klaviyo Api MCP Server - Pydantic Models

Generated: 2026-04-09 17:25:38 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "AddCategoriesToCatalogItemRequest",
    "AddItemsToCatalogCategoryRequest",
    "AddProfilesToListRequest",
    "AssignTemplateToCampaignMessageRequest",
    "BulkCreateCatalogCategoriesRequest",
    "BulkCreateCatalogItemsRequest",
    "BulkCreateCatalogVariantsRequest",
    "BulkCreateCouponCodesRequest",
    "BulkCreateDataSourceRecordsRequest",
    "BulkCreateEventsRequest",
    "BulkDeleteCatalogCategoriesRequest",
    "BulkDeleteCatalogItemsRequest",
    "BulkDeleteCatalogVariantsRequest",
    "BulkImportProfilesRequest",
    "BulkSubscribeProfilesRequest",
    "BulkSuppressProfilesRequest",
    "BulkUnsubscribeProfilesRequest",
    "BulkUnsuppressProfilesRequest",
    "BulkUpdateCatalogCategoriesRequest",
    "BulkUpdateCatalogItemsRequest",
    "BulkUpdateCatalogVariantsRequest",
    "CancelCampaignSendRequest",
    "CloneTemplateRequest",
    "CreateBackInStockSubscriptionRequest",
    "CreateCampaignCloneRequest",
    "CreateCatalogCategoryRequest",
    "CreateCatalogItemRequest",
    "CreateCatalogVariantRequest",
    "CreateClientBackInStockSubscriptionRequest",
    "CreateClientProfileRequest",
    "CreateClientReviewRequest",
    "CreateClientSubscriptionRequest",
    "CreateCouponCodeRequest",
    "CreateCouponRequest",
    "CreateCustomMetricRequest",
    "CreateDataSourceRecordRequest",
    "CreateDataSourceRequest",
    "CreateEventRequest",
    "CreateFormRequest",
    "CreateListRequest",
    "CreateOrUpdateProfileRequest",
    "CreateProfileRequest",
    "CreatePushTokenRequest",
    "CreateSegmentRequest",
    "CreateTagGroupRequest",
    "CreateTagRequest",
    "CreateTemplateRequest",
    "CreateUniversalContentRequest",
    "CreateWebFeedRequest",
    "DeleteCampaignRequest",
    "DeleteCatalogCategoryRequest",
    "DeleteCatalogItemRequest",
    "DeleteCatalogVariantRequest",
    "DeleteCouponCodeRequest",
    "DeleteCouponRequest",
    "DeleteCustomMetricRequest",
    "DeleteDataSourceRequest",
    "DeleteFlowRequest",
    "DeleteFormRequest",
    "DeleteListRequest",
    "DeletePushTokenRequest",
    "DeleteSegmentRequest",
    "DeleteTagGroupRequest",
    "DeleteTagRequest",
    "DeleteTemplateRequest",
    "DeleteUniversalContentRequest",
    "DeleteWebFeedRequest",
    "DeleteWebhookRequest",
    "GetAccountRequest",
    "GetAccountsRequest",
    "GetActionForFlowMessageRequest",
    "GetActionIdForFlowMessageRequest",
    "GetActionIdsForFlowRequest",
    "GetActionsForFlowRequest",
    "GetAllUniversalContentRequest",
    "GetBulkCreateCatalogItemsJobRequest",
    "GetBulkCreateCatalogItemsJobsRequest",
    "GetBulkCreateCategoriesJobRequest",
    "GetBulkCreateCategoriesJobsRequest",
    "GetBulkCreateCouponCodeJobsRequest",
    "GetBulkCreateCouponCodesJobRequest",
    "GetBulkCreateVariantsJobRequest",
    "GetBulkCreateVariantsJobsRequest",
    "GetBulkDeleteCatalogItemsJobRequest",
    "GetBulkDeleteCatalogItemsJobsRequest",
    "GetBulkDeleteCategoriesJobRequest",
    "GetBulkDeleteCategoriesJobsRequest",
    "GetBulkDeleteVariantsJobRequest",
    "GetBulkDeleteVariantsJobsRequest",
    "GetBulkImportProfilesJobRequest",
    "GetBulkImportProfilesJobsRequest",
    "GetBulkSuppressProfilesJobRequest",
    "GetBulkSuppressProfilesJobsRequest",
    "GetBulkUnsuppressProfilesJobRequest",
    "GetBulkUnsuppressProfilesJobsRequest",
    "GetBulkUpdateCatalogItemsJobRequest",
    "GetBulkUpdateCatalogItemsJobsRequest",
    "GetBulkUpdateCategoriesJobRequest",
    "GetBulkUpdateCategoriesJobsRequest",
    "GetBulkUpdateVariantsJobRequest",
    "GetBulkUpdateVariantsJobsRequest",
    "GetCampaignForCampaignMessageRequest",
    "GetCampaignIdForCampaignMessageRequest",
    "GetCampaignIdsForTagRequest",
    "GetCampaignMessageRequest",
    "GetCampaignRecipientEstimationJobRequest",
    "GetCampaignRecipientEstimationRequest",
    "GetCampaignRequest",
    "GetCampaignSendJobRequest",
    "GetCampaignsRequest",
    "GetCatalogCategoriesRequest",
    "GetCatalogCategoryRequest",
    "GetCatalogItemRequest",
    "GetCatalogItemsRequest",
    "GetCatalogVariantRequest",
    "GetCatalogVariantsRequest",
    "GetCategoriesForCatalogItemRequest",
    "GetCategoryIdsForCatalogItemRequest",
    "GetClientReviewsRequest",
    "GetClientReviewValuesReportsRequest",
    "GetCouponCodeIdsForCouponRequest",
    "GetCouponCodeRequest",
    "GetCouponCodesForCouponRequest",
    "GetCouponCodesRequest",
    "GetCouponForCouponCodeRequest",
    "GetCouponIdForCouponCodeRequest",
    "GetCouponRequest",
    "GetCouponsRequest",
    "GetCustomMetricForMappedMetricRequest",
    "GetCustomMetricIdForMappedMetricRequest",
    "GetCustomMetricRequest",
    "GetCustomMetricsRequest",
    "GetDataSourceRequest",
    "GetDataSourcesRequest",
    "GetErrorsForBulkImportProfilesJobRequest",
    "GetEventRequest",
    "GetEventsRequest",
    "GetFlowActionMessagesRequest",
    "GetFlowActionRequest",
    "GetFlowForFlowActionRequest",
    "GetFlowIdForFlowActionRequest",
    "GetFlowIdsForTagRequest",
    "GetFlowMessageRequest",
    "GetFlowRequest",
    "GetFlowsRequest",
    "GetFlowsTriggeredByListRequest",
    "GetFlowsTriggeredByMetricRequest",
    "GetFlowsTriggeredBySegmentRequest",
    "GetFormForFormVersionRequest",
    "GetFormIdForFormVersionRequest",
    "GetFormRequest",
    "GetFormsRequest",
    "GetFormVersionRequest",
    "GetIdsForFlowsTriggeredByListRequest",
    "GetIdsForFlowsTriggeredByMetricRequest",
    "GetIdsForFlowsTriggeredBySegmentRequest",
    "GetImageForCampaignMessageRequest",
    "GetImageIdForCampaignMessageRequest",
    "GetImageRequest",
    "GetImagesRequest",
    "GetItemIdsForCatalogCategoryRequest",
    "GetItemsForCatalogCategoryRequest",
    "GetListForBulkImportProfilesJobRequest",
    "GetListIdsForBulkImportProfilesJobRequest",
    "GetListIdsForProfileRequest",
    "GetListIdsForTagRequest",
    "GetListRequest",
    "GetListsForProfileRequest",
    "GetListsRequest",
    "GetMappedMetricRequest",
    "GetMappedMetricsRequest",
    "GetMessageIdsForCampaignRequest",
    "GetMessageIdsForFlowActionRequest",
    "GetMessagesForCampaignRequest",
    "GetMetricForEventRequest",
    "GetMetricForMappedMetricRequest",
    "GetMetricForMetricPropertyRequest",
    "GetMetricIdForEventRequest",
    "GetMetricIdForMappedMetricRequest",
    "GetMetricIdForMetricPropertyRequest",
    "GetMetricIdsForCustomMetricRequest",
    "GetMetricPropertyRequest",
    "GetMetricRequest",
    "GetMetricsForCustomMetricRequest",
    "GetMetricsRequest",
    "GetProfileForEventRequest",
    "GetProfileForPushTokenRequest",
    "GetProfileIdForEventRequest",
    "GetProfileIdForPushTokenRequest",
    "GetProfileIdsForBulkImportProfilesJobRequest",
    "GetProfileIdsForListRequest",
    "GetProfileIdsForSegmentRequest",
    "GetProfileRequest",
    "GetProfilesForBulkImportProfilesJobRequest",
    "GetProfilesForListRequest",
    "GetProfilesForSegmentRequest",
    "GetProfilesRequest",
    "GetPropertiesForMetricRequest",
    "GetPropertyIdsForMetricRequest",
    "GetPushTokenIdsForProfileRequest",
    "GetPushTokenRequest",
    "GetPushTokensForProfileRequest",
    "GetPushTokensRequest",
    "GetReviewRequest",
    "GetReviewsRequest",
    "GetSegmentIdsForProfileRequest",
    "GetSegmentIdsForTagRequest",
    "GetSegmentRequest",
    "GetSegmentsForProfileRequest",
    "GetSegmentsRequest",
    "GetTagGroupForTagRequest",
    "GetTagGroupIdForTagRequest",
    "GetTagGroupRequest",
    "GetTagGroupsRequest",
    "GetTagIdsForCampaignRequest",
    "GetTagIdsForFlowRequest",
    "GetTagIdsForListRequest",
    "GetTagIdsForSegmentRequest",
    "GetTagIdsForTagGroupRequest",
    "GetTagRequest",
    "GetTagsForCampaignRequest",
    "GetTagsForFlowRequest",
    "GetTagsForListRequest",
    "GetTagsForSegmentRequest",
    "GetTagsForTagGroupRequest",
    "GetTagsRequest",
    "GetTemplateForCampaignMessageRequest",
    "GetTemplateForFlowMessageRequest",
    "GetTemplateIdForCampaignMessageRequest",
    "GetTemplateIdForFlowMessageRequest",
    "GetTemplateRequest",
    "GetTemplatesRequest",
    "GetTrackingSettingRequest",
    "GetTrackingSettingsRequest",
    "GetUniversalContentRequest",
    "GetVariantIdsForCatalogItemRequest",
    "GetVariantsForCatalogItemRequest",
    "GetVersionIdsForFormRequest",
    "GetVersionsForFormRequest",
    "GetWebFeedRequest",
    "GetWebFeedsRequest",
    "GetWebhookRequest",
    "GetWebhooksRequest",
    "GetWebhookTopicRequest",
    "GetWebhookTopicsRequest",
    "MergeProfilesRequest",
    "QueryCampaignValuesRequest",
    "QueryFlowSeriesRequest",
    "QueryFlowValuesRequest",
    "QueryFormSeriesRequest",
    "QueryFormValuesRequest",
    "QueryMetricAggregatesRequest",
    "QuerySegmentSeriesRequest",
    "QuerySegmentValuesRequest",
    "RefreshCampaignRecipientEstimationRequest",
    "RemoveCategoriesFromCatalogItemRequest",
    "RemoveItemsFromCatalogCategoryRequest",
    "RemoveProfilesFromListRequest",
    "RemoveTagFromCampaignsRequest",
    "RemoveTagFromFlowsRequest",
    "RemoveTagFromListsRequest",
    "RemoveTagFromSegmentsRequest",
    "RenderTemplateRequest",
    "RequestProfileDeletionRequest",
    "SendCampaignRequest",
    "TagCampaignsRequest",
    "TagFlowsRequest",
    "TagListsRequest",
    "TagSegmentsRequest",
    "UpdateCampaignMessageRequest",
    "UpdateCampaignRequest",
    "UpdateCatalogCategoryRequest",
    "UpdateCatalogItemRequest",
    "UpdateCatalogVariantRequest",
    "UpdateCategoriesForCatalogItemRequest",
    "UpdateCouponCodeRequest",
    "UpdateCouponRequest",
    "UpdateCustomMetricRequest",
    "UpdateFlowRequest",
    "UpdateImageForCampaignMessageRequest",
    "UpdateImageRequest",
    "UpdateItemsForCatalogCategoryRequest",
    "UpdateListRequest",
    "UpdateMappedMetricRequest",
    "UpdateProfileRequest",
    "UpdateReviewRequest",
    "UpdateSegmentRequest",
    "UpdateTagGroupRequest",
    "UpdateTagRequest",
    "UpdateTemplateRequest",
    "UpdateUniversalContentRequest",
    "UpdateWebFeedRequest",
    "UpdateWebhookRequest",
    "UploadImageFromFileRequest",
    "UploadImageFromUrlRequest",
    "AddCategoriesToCatalogItemBodyDataItem",
    "AddItemsToCatalogCategoryBodyDataItem",
    "AddProfilesToListBodyDataItem",
    "BulkImportProfilesBodyDataRelationshipsListsDataItem",
    "ButtonBlock",
    "CampaignsEmailTrackingOptions",
    "CampaignsSmsTrackingOptions",
    "CatalogCategoryCreateQueryResourceObject",
    "CatalogCategoryDeleteQueryResourceObject",
    "CatalogCategoryUpdateQueryResourceObject",
    "CatalogItemCreateQueryResourceObject",
    "CatalogItemDeleteQueryResourceObject",
    "CatalogItemUpdateQueryResourceObject",
    "CatalogVariantCreateQueryResourceObject",
    "CatalogVariantDeleteQueryResourceObject",
    "CatalogVariantUpdateQueryResourceObject",
    "ConditionGroup",
    "CouponCodeCreateQueryResourceObject",
    "CreateCatalogCategoryBodyDataRelationshipsItemsDataItem",
    "CreateCatalogItemBodyDataRelationshipsCategoriesDataItem",
    "CreateClientSubscriptionBodyDataAttributesProfile",
    "CreateEventBodyDataAttributesProfile",
    "CreatePushTokenBodyDataAttributesDeviceMetadata",
    "CreatePushTokenBodyDataAttributesProfile",
    "CustomMetricGroup",
    "CustomQuestionDto",
    "CustomTimeframe",
    "DataSourceRecordResourceObject",
    "DropShadowBlock",
    "EmailMessageDefinition",
    "EmailSendOptions",
    "EventsBulkCreateQueryResourceObject",
    "HorizontalRuleBlock",
    "HtmlBlock",
    "ImageBlock",
    "ImmediateSendStrategy",
    "MergeProfilesBodyDataRelationshipsProfilesDataItem",
    "MobilePushMessageSilentDefinitionUpdate",
    "MobilePushMessageStandardDefinitionUpdate",
    "ProfileSubscriptionCreateQueryResourceObject",
    "ProfileSubscriptionDeleteQueryResourceObject",
    "ProfileSuppressionCreateQueryResourceObject",
    "ProfileSuppressionDeleteQueryResourceObject",
    "ProfileUpsertQueryResourceObject",
    "PushSendOptions",
    "RemoveCategoriesFromCatalogItemBodyDataItem",
    "RemoveItemsFromCatalogCategoryBodyDataItem",
    "RemoveProfilesFromListBodyDataItem",
    "RemoveTagFromCampaignsBodyDataItem",
    "RemoveTagFromFlowsBodyDataItem",
    "RemoveTagFromListsBodyDataItem",
    "RemoveTagFromSegmentsBodyDataItem",
    "ReviewStatusFeatured",
    "ReviewStatusPending",
    "ReviewStatusPublished",
    "ReviewStatusRejected",
    "ReviewStatusUnpublished",
    "SmartSendTimeStrategy",
    "SmsMessageDefinitionCreate",
    "SmsSendOptions",
    "SpacerBlock",
    "StaticSendStrategy",
    "TagCampaignsBodyDataItem",
    "TagFlowsBodyDataItem",
    "TagListsBodyDataItem",
    "TagSegmentsBodyDataItem",
    "TextBlock",
    "ThrottledSendStrategy",
    "Timeframe",
    "UpdateCatalogCategoryBodyDataRelationshipsItemsDataItem",
    "UpdateCatalogItemBodyDataRelationshipsCategoriesDataItem",
    "UpdateCategoriesForCatalogItemBodyDataItem",
    "UpdateItemsForCatalogCategoryBodyDataItem",
    "UpdateWebhookBodyDataRelationshipsWebhookTopicsDataItem",
    "Version",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_accounts
class GetAccountsRequestQuery(StrictModel):
    fields_account: list[Literal["contact_information", "contact_information.default_sender_email", "contact_information.default_sender_name", "contact_information.organization_name", "contact_information.street_address", "contact_information.street_address.address1", "contact_information.street_address.address2", "contact_information.street_address.city", "contact_information.street_address.country", "contact_information.street_address.region", "contact_information.street_address.zip", "contact_information.website_url", "industry", "locale", "preferred_currency", "public_api_key", "test_account", "timezone"]] | None = Field(default=None, validation_alias="fields[account]", serialization_alias="fields[account]", description="Specify which account fields to include in the response using sparse fieldsets for optimized data retrieval. See API documentation for available field names.")
class GetAccountsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetAccountsRequest(StrictModel):
    """Retrieve account information associated with your private API key, including contact details, timezone, currency, and public API key. Use this to access account-specific data or verify API key ownership before performing other operations."""
    query: GetAccountsRequestQuery | None = None
    header: GetAccountsRequestHeader

# Operation: get_account
class GetAccountRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the account to retrieve (e.g., AbC123).")
class GetAccountRequestQuery(StrictModel):
    fields_account: list[Literal["contact_information", "contact_information.default_sender_email", "contact_information.default_sender_name", "contact_information.organization_name", "contact_information.street_address", "contact_information.street_address.address1", "contact_information.street_address.address2", "contact_information.street_address.city", "contact_information.street_address.country", "contact_information.street_address.region", "contact_information.street_address.zip", "contact_information.website_url", "industry", "locale", "preferred_currency", "public_api_key", "test_account", "timezone"]] | None = Field(default=None, validation_alias="fields[account]", serialization_alias="fields[account]", description="Optional list of specific account fields to include in the response. Use sparse fieldsets to reduce payload size and improve performance. Refer to the API documentation for available field names.")
class GetAccountRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetAccountRequest(StrictModel):
    """Retrieve a single account object by its ID. You can only access the account associated with the private API key used for authentication."""
    path: GetAccountRequestPath
    query: GetAccountRequestQuery | None = None
    header: GetAccountRequestHeader

# Operation: list_campaigns
class GetCampaignsRequestQuery(StrictModel):
    filter_: str = Field(default=..., validation_alias="filter", serialization_alias="filter", description="Filter expression to narrow campaign results. A channel filter is required—use equals(messages.channel,'email'), equals(messages.channel,'sms'), or equals(messages.channel,'mobile_push'). You can combine with additional filters on id, name (contains), status, archived state, or timestamps (created_at, scheduled_at, updated_at). See API documentation for full filtering syntax.")
class GetCampaignsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetCampaignsRequest(StrictModel):
    """Retrieve campaigns filtered by channel (email, SMS, or mobile push) and optional criteria like name, status, or date range. A channel filter is required to list campaigns."""
    query: GetCampaignsRequestQuery
    header: GetCampaignsRequestHeader

# Operation: get_campaign
class GetCampaignRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign to retrieve.")
class GetCampaignRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class GetCampaignRequest(StrictModel):
    """Retrieve a specific campaign by its ID. Returns detailed campaign information for the requested resource."""
    path: GetCampaignRequestPath
    header: GetCampaignRequestHeader

# Operation: update_campaign
class UpdateCampaignRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign to update.")
class UpdateCampaignRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v2). Defaults to 2026-01-15 if not specified.")
class UpdateCampaignRequestBodyDataAttributesAudiences(StrictModel):
    included: list[str] | None = Field(default=None, validation_alias="included", serialization_alias="included", description="A list of audience IDs to include in the campaign. Providing this list will replace any previously included audiences. Order and format follow the audience ID system.")
    excluded: list[str] | None = Field(default=None, validation_alias="excluded", serialization_alias="excluded", description="A list of audience IDs to exclude from the campaign. Providing this list will replace any previously excluded audiences. Order and format follow the audience ID system.")
class UpdateCampaignRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name for the campaign (e.g., 'My new campaign').")
    send_options: EmailSendOptions | SmsSendOptions | PushSendOptions | None = Field(default=None, validation_alias="send_options", serialization_alias="send_options", description="Configuration options that control how the campaign will be sent, including delivery timing and method preferences.")
    tracking_options: CampaignsEmailTrackingOptions | CampaignsSmsTrackingOptions | None = Field(default=None, validation_alias="tracking_options", serialization_alias="tracking_options", description="Tracking configuration for the campaign, including metrics collection and event monitoring settings.")
    send_strategy: StaticSendStrategy | ThrottledSendStrategy | ImmediateSendStrategy | SmartSendTimeStrategy | None = Field(default=None, validation_alias="send_strategy", serialization_alias="send_strategy", description="The delivery strategy that determines how the campaign will be distributed to recipients (e.g., immediate, scheduled, or progressive send).")
    audiences: UpdateCampaignRequestBodyDataAttributesAudiences | None = None
class UpdateCampaignRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign being updated; must match the path ID parameter.")
    type_: Literal["campaign"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'campaign'.")
    attributes: UpdateCampaignRequestBodyDataAttributes | None = None
class UpdateCampaignRequestBody(StrictModel):
    """Update a campaign and return it"""
    data: UpdateCampaignRequestBodyData
class UpdateCampaignRequest(StrictModel):
    """Update an existing campaign's configuration including name, audience targeting, send options, tracking, and delivery strategy. Requires the campaign ID and current revision for optimistic concurrency control."""
    path: UpdateCampaignRequestPath
    header: UpdateCampaignRequestHeader
    body: UpdateCampaignRequestBody

# Operation: delete_campaign
class DeleteCampaignRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign to delete.")
class DeleteCampaignRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class DeleteCampaignRequest(StrictModel):
    """Permanently delete a campaign by its ID. This action cannot be undone and will remove all associated campaign data."""
    path: DeleteCampaignRequestPath
    header: DeleteCampaignRequestHeader

# Operation: get_campaign_message
class GetCampaignMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign message to retrieve.")
class GetCampaignMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v2). Defaults to 2026-01-15 if not specified.")
class GetCampaignMessageRequest(StrictModel):
    """Retrieves a specific campaign message by its ID. Returns the message details for the specified revision of the API."""
    path: GetCampaignMessageRequestPath
    header: GetCampaignMessageRequestHeader

# Operation: update_campaign_message
class UpdateCampaignMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign message to update.")
class UpdateCampaignMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class UpdateCampaignMessageRequestBodyDataRelationshipsImageData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the image to associate with this campaign message. Required for mobile_push message types.")
    type_: Literal["image"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for the associated image. Must be set to 'image'.")
class UpdateCampaignMessageRequestBodyDataRelationshipsImage(StrictModel):
    data: UpdateCampaignMessageRequestBodyDataRelationshipsImageData
class UpdateCampaignMessageRequestBodyDataRelationships(StrictModel):
    image: UpdateCampaignMessageRequestBodyDataRelationshipsImage
class UpdateCampaignMessageRequestBodyDataAttributes(StrictModel):
    definition: EmailMessageDefinition | SmsMessageDefinitionCreate | MobilePushMessageStandardDefinitionUpdate | MobilePushMessageSilentDefinitionUpdate | None = Field(default=None, validation_alias="definition", serialization_alias="definition", description="The campaign message contents and configuration settings, including template variables, targeting rules, and delivery preferences.")
class UpdateCampaignMessageRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign message being updated. Must match the message ID in the URL path.")
    type_: Literal["campaign-message"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for the campaign message. Must be set to 'campaign-message'.")
    relationships: UpdateCampaignMessageRequestBodyDataRelationships
    attributes: UpdateCampaignMessageRequestBodyDataAttributes | None = None
class UpdateCampaignMessageRequestBody(StrictModel):
    """Update a message and return it"""
    data: UpdateCampaignMessageRequestBodyData
class UpdateCampaignMessageRequest(StrictModel):
    """Update an existing campaign message with new content and settings. Supports modifying message definition, associated images for mobile push notifications, and other campaign message properties."""
    path: UpdateCampaignMessageRequestPath
    header: UpdateCampaignMessageRequestHeader
    body: UpdateCampaignMessageRequestBody

# Operation: get_campaign_send_job
class GetCampaignSendJobRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign send job to retrieve.")
class GetCampaignSendJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetCampaignSendJobRequest(StrictModel):
    """Retrieve details about a specific campaign send job by its ID. Use this to check the status and metadata of a campaign send operation."""
    path: GetCampaignSendJobRequestPath
    header: GetCampaignSendJobRequestHeader

# Operation: update_campaign_send_job
class CancelCampaignSendRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign send job to modify.")
class CancelCampaignSendRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15.")
class CancelCampaignSendRequestBodyDataAttributes(StrictModel):
    action: Literal["cancel", "revert"] = Field(default=..., validation_alias="action", serialization_alias="action", description="The action to perform: 'cancel' to permanently stop the send, or 'revert' to return the campaign to draft status.")
class CancelCampaignSendRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign send job being modified; must match the path ID.")
    type_: Literal["campaign-send-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be 'campaign-send-job'.")
    attributes: CancelCampaignSendRequestBodyDataAttributes
class CancelCampaignSendRequestBody(StrictModel):
    """Permanently cancel the campaign, setting the status to CANCELED or
revert the campaign, setting the status back to DRAFT"""
    data: CancelCampaignSendRequestBodyData
class CancelCampaignSendRequest(StrictModel):
    """Cancel an in-progress campaign send or revert it back to draft status. Use 'cancel' to permanently stop the send, or 'revert' to return the campaign to draft for further editing."""
    path: CancelCampaignSendRequestPath
    header: CancelCampaignSendRequestHeader
    body: CancelCampaignSendRequestBody

# Operation: get_campaign_recipient_estimation_job
class GetCampaignRecipientEstimationJobRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign recipient estimation job whose status you want to retrieve.")
class GetCampaignRecipientEstimationJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetCampaignRecipientEstimationJobRequest(StrictModel):
    """Retrieve the current status and results of a recipient estimation job for a campaign. Use this to poll the asynchronous job triggered by the Create Campaign Recipient Estimation Job endpoint."""
    path: GetCampaignRecipientEstimationJobRequestPath
    header: GetCampaignRecipientEstimationJobRequestHeader

# Operation: get_campaign_recipient_estimation
class GetCampaignRecipientEstimationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign for which to retrieve the estimated recipient count.")
class GetCampaignRecipientEstimationRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class GetCampaignRecipientEstimationRequest(StrictModel):
    """Retrieve the estimated recipient count for a campaign. Use the Create Campaign Recipient Estimation Job endpoint to refresh this estimate."""
    path: GetCampaignRecipientEstimationRequestPath
    header: GetCampaignRecipientEstimationRequestHeader

# Operation: clone_campaign
class CreateCampaignCloneRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15 if not specified.")
class CreateCampaignCloneRequestBodyDataAttributes(StrictModel):
    new_name: str | None = Field(default=None, validation_alias="new_name", serialization_alias="new_name", description="Optional custom name for the newly cloned campaign. If not provided, a default name will be generated based on the original campaign.")
class CreateCampaignCloneRequestBodyData(StrictModel):
    type_: Literal["campaign"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type being cloned. Must be set to 'campaign' for this operation.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign to clone.")
    attributes: CreateCampaignCloneRequestBodyDataAttributes | None = None
class CreateCampaignCloneRequestBody(StrictModel):
    """Clones a campaign from an existing campaign"""
    data: CreateCampaignCloneRequestBodyData
class CreateCampaignCloneRequest(StrictModel):
    """Creates a duplicate of an existing campaign with a new ID and optional custom name. The cloned campaign inherits all settings and configuration from the original."""
    header: CreateCampaignCloneRequestHeader
    body: CreateCampaignCloneRequestBody

# Operation: assign_template_to_campaign_message
class AssignTemplateToCampaignMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to 2026-01-15 if not specified.")
class AssignTemplateToCampaignMessageRequestBodyDataRelationshipsTemplateData(StrictModel):
    type_: Literal["template"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier for the template relationship. Must be set to 'template'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template to assign to the campaign message.")
class AssignTemplateToCampaignMessageRequestBodyDataRelationshipsTemplate(StrictModel):
    data: AssignTemplateToCampaignMessageRequestBodyDataRelationshipsTemplateData
class AssignTemplateToCampaignMessageRequestBodyDataRelationships(StrictModel):
    template: AssignTemplateToCampaignMessageRequestBodyDataRelationshipsTemplate
class AssignTemplateToCampaignMessageRequestBodyData(StrictModel):
    type_: Literal["campaign-message"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier for the campaign message. Must be set to 'campaign-message'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign message that will receive the template assignment.")
    relationships: AssignTemplateToCampaignMessageRequestBodyDataRelationships
class AssignTemplateToCampaignMessageRequestBody(StrictModel):
    """Takes a reusable template, clones it, and assigns the non-reusable clone to the message."""
    data: AssignTemplateToCampaignMessageRequestBodyData
class AssignTemplateToCampaignMessageRequest(StrictModel):
    """Assigns a template to a campaign message by creating a non-reusable copy of the template linked to that specific message. This operation requires campaigns:write scope and is subject to rate limits of 10 requests per second (burst) and 150 requests per minute (steady state)."""
    header: AssignTemplateToCampaignMessageRequestHeader
    body: AssignTemplateToCampaignMessageRequestBody

# Operation: send_campaign
class SendCampaignRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class SendCampaignRequestBodyData(StrictModel):
    type_: Literal["campaign-send-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for this operation, which must be 'campaign-send-job'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign to send. This campaign must exist and be in a valid state for sending.")
class SendCampaignRequestBody(StrictModel):
    """Trigger the campaign to send asynchronously"""
    data: SendCampaignRequestBodyData
class SendCampaignRequest(StrictModel):
    """Trigger an asynchronous campaign send job to deliver messages to recipients. The operation queues the campaign for processing and returns immediately."""
    header: SendCampaignRequestHeader
    body: SendCampaignRequestBody

# Operation: trigger_campaign_recipient_estimation
class RefreshCampaignRecipientEstimationRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class RefreshCampaignRecipientEstimationRequestBodyData(StrictModel):
    type_: Literal["campaign-recipient-estimation-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier; must be set to 'campaign-recipient-estimation-job' to specify the job type being created.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign for which to estimate recipient count.")
class RefreshCampaignRecipientEstimationRequestBody(StrictModel):
    """Trigger an asynchronous job to update the estimated number of recipients
for the given campaign ID. Use the `Get Campaign Recipient Estimation
Job` endpoint to retrieve the status of this estimation job. Use the
`Get Campaign Recipient Estimation` endpoint to retrieve the estimated
recipient count for a given campaign."""
    data: RefreshCampaignRecipientEstimationRequestBodyData
class RefreshCampaignRecipientEstimationRequest(StrictModel):
    """Initiate an asynchronous job to recalculate the estimated recipient count for a campaign. Poll the job status endpoint or retrieve the final estimation once processing completes."""
    header: RefreshCampaignRecipientEstimationRequestHeader
    body: RefreshCampaignRecipientEstimationRequestBody

# Operation: get_campaign_for_campaign_message
class GetCampaignForCampaignMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign message for which to retrieve the associated campaign.")
class GetCampaignForCampaignMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetCampaignForCampaignMessageRequest(StrictModel):
    """Retrieve the campaign associated with a specific campaign message. This operation returns the parent campaign details for the given message."""
    path: GetCampaignForCampaignMessageRequestPath
    header: GetCampaignForCampaignMessageRequestHeader

# Operation: get_campaign_id_for_campaign_message
class GetCampaignIdForCampaignMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign message for which to retrieve the associated campaign ID.")
class GetCampaignIdForCampaignMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetCampaignIdForCampaignMessageRequest(StrictModel):
    """Retrieve the ID of the campaign associated with a specific campaign message. This operation returns the relationship data linking a message to its parent campaign."""
    path: GetCampaignIdForCampaignMessageRequestPath
    header: GetCampaignIdForCampaignMessageRequestHeader

# Operation: get_template_for_campaign_message
class GetTemplateForCampaignMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign message whose template you want to retrieve.")
class GetTemplateForCampaignMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetTemplateForCampaignMessageRequest(StrictModel):
    """Retrieve the template associated with a specific campaign message. Returns the template configuration used by the campaign message."""
    path: GetTemplateForCampaignMessageRequestPath
    header: GetTemplateForCampaignMessageRequestHeader

# Operation: get_template_id_for_campaign_message
class GetTemplateIdForCampaignMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign message for which to retrieve the related template ID.")
class GetTemplateIdForCampaignMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetTemplateIdForCampaignMessageRequest(StrictModel):
    """Retrieve the ID of the template associated with a specific campaign message. This operation returns only the template relationship identifier, useful for determining which template is used by a campaign message."""
    path: GetTemplateIdForCampaignMessageRequestPath
    header: GetTemplateIdForCampaignMessageRequestHeader

# Operation: get_image_for_campaign_message
class GetImageForCampaignMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign message for which to retrieve the associated image.")
class GetImageForCampaignMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetImageForCampaignMessageRequest(StrictModel):
    """Retrieve the image associated with a specific campaign message. Returns the image resource linked to the campaign message identified by the provided ID."""
    path: GetImageForCampaignMessageRequestPath
    header: GetImageForCampaignMessageRequestHeader

# Operation: get_image_id_for_campaign_message
class GetImageIdForCampaignMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign message whose related image ID you want to retrieve.")
class GetImageIdForCampaignMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetImageIdForCampaignMessageRequest(StrictModel):
    """Retrieve the ID of the image associated with a specific campaign message. This operation returns only the image relationship identifier, not the full image resource."""
    path: GetImageIdForCampaignMessageRequestPath
    header: GetImageIdForCampaignMessageRequestHeader

# Operation: update_image_for_campaign_message
class UpdateImageForCampaignMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign message whose image should be updated.")
class UpdateImageForCampaignMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class UpdateImageForCampaignMessageRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the image to associate with the campaign message.")
    type_: Literal["image"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, which must be 'image' to specify the relationship type being updated.")
class UpdateImageForCampaignMessageRequestBody(StrictModel):
    data: UpdateImageForCampaignMessageRequestBodyData
class UpdateImageForCampaignMessageRequest(StrictModel):
    """Replace the image associated with a campaign message. Requires both the campaign message ID and the image ID to establish the relationship."""
    path: UpdateImageForCampaignMessageRequestPath
    header: UpdateImageForCampaignMessageRequestHeader
    body: UpdateImageForCampaignMessageRequestBody

# Operation: list_tags_for_campaign
class GetTagsForCampaignRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign for which to retrieve tags.")
class GetTagsForCampaignRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use for this request.")
class GetTagsForCampaignRequest(StrictModel):
    """Retrieve all tags associated with a specific campaign. Returns a collection of tags that have been assigned to the campaign."""
    path: GetTagsForCampaignRequestPath
    header: GetTagsForCampaignRequestHeader

# Operation: list_tag_ids_for_campaign
class GetTagIdsForCampaignRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign for which to retrieve associated tag IDs.")
class GetTagIdsForCampaignRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class GetTagIdsForCampaignRequest(StrictModel):
    """Retrieves all tag IDs associated with a specific campaign. Returns a collection of tag identifiers linked to the campaign."""
    path: GetTagIdsForCampaignRequestPath
    header: GetTagIdsForCampaignRequestHeader

# Operation: list_messages_for_campaign
class GetMessagesForCampaignRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign for which to retrieve messages.")
class GetMessagesForCampaignRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format (optionally with a suffix). Defaults to 2026-01-15 if not specified.")
class GetMessagesForCampaignRequest(StrictModel):
    """Retrieve all messages associated with a specific campaign. Returns a collection of messages that have been created or assigned to the campaign."""
    path: GetMessagesForCampaignRequestPath
    header: GetMessagesForCampaignRequestHeader

# Operation: list_message_ids_for_campaign
class GetMessageIdsForCampaignRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the campaign whose associated message IDs you want to retrieve.")
class GetMessageIdsForCampaignRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetMessageIdsForCampaignRequest(StrictModel):
    """Retrieves all message IDs associated with a specific campaign. Use this to discover which messages are linked to a campaign for further operations."""
    path: GetMessageIdsForCampaignRequestPath
    header: GetMessageIdsForCampaignRequestHeader

# Operation: list_catalog_items
class GetCatalogItemsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter catalog items by specific criteria. Supports filtering by item IDs (using `any` operator), category ID (exact match), item title (partial match), or published status (exact match). Provide filters in the format specified by the API filtering documentation.")
class GetCatalogItemsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetCatalogItemsRequest(StrictModel):
    """Retrieve all catalog items in your account with optional filtering and sorting. Returns up to 100 items per request."""
    query: GetCatalogItemsRequestQuery | None = None
    header: GetCatalogItemsRequestHeader

# Operation: create_catalog_item
class CreateCatalogItemRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to 2026-01-15 if not specified.")
class CreateCatalogItemRequestBodyDataAttributes(StrictModel):
    external_id: str = Field(default=..., validation_alias="external_id", serialization_alias="external_id", description="A unique identifier for this catalog item in your external system or inventory management platform (e.g., SKU or product ID).")
    integration_type: Literal["$custom"] | None = Field(default=None, validation_alias="integration_type", serialization_alias="integration_type", description="The integration type for this catalog item. Currently only '$custom' is supported for custom integrations.")
    title: str = Field(default=..., validation_alias="title", serialization_alias="title", description="The display name of the catalog item. This title appears in email campaigns and customer-facing content.")
    price: float | None = Field(default=None, validation_alias="price", serialization_alias="price", description="The price of the catalog item displayed in emails and campaigns. If you have variants with different prices, update their prices separately using the variant endpoint.")
    description: str = Field(default=..., validation_alias="description", serialization_alias="description", description="A detailed description of the catalog item, including key features and characteristics. This text is used in email content and product displays.")
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="The full URL to the catalog item's product page on your website. This link is used in emails and integrations to direct customers to the item.")
    images: list[str] | None = Field(default=None, validation_alias="images", serialization_alias="images", description="An array of URLs pointing to product images. Include multiple images to provide different views or angles of the item.")
    custom_metadata: dict[str, Any] | None = Field(default=None, validation_alias="custom_metadata", serialization_alias="custom_metadata", description="A flat JSON object containing custom metadata about the item (e.g., {'Top Pick': true, 'Season': 'Summer'}). Total size must not exceed 100KB.")
    published: bool | None = Field(default=None, validation_alias="published", serialization_alias="published", description="Boolean flag indicating whether the catalog item is published and visible. Defaults to true if not specified.")
class CreateCatalogItemRequestBodyDataRelationshipsCategories(StrictModel):
    data: list[CreateCatalogItemBodyDataRelationshipsCategoriesDataItem] | None = Field(default=None, validation_alias="data", serialization_alias="data", description="Additional data payload for the catalog item. Structure and usage depend on your integration requirements.")
class CreateCatalogItemRequestBodyDataRelationships(StrictModel):
    categories: CreateCatalogItemRequestBodyDataRelationshipsCategories | None = None
class CreateCatalogItemRequestBodyData(StrictModel):
    type_: Literal["catalog-item"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'catalog-item' to indicate this is a catalog item resource.")
    attributes: CreateCatalogItemRequestBodyDataAttributes
    relationships: CreateCatalogItemRequestBodyDataRelationships | None = None
class CreateCatalogItemRequestBody(StrictModel):
    data: CreateCatalogItemRequestBodyData
class CreateCatalogItemRequest(StrictModel):
    """Create a new catalog item in your product catalog. The item will be assigned a unique identifier and can include pricing, images, and custom metadata for use in email campaigns and integrations."""
    header: CreateCatalogItemRequestHeader
    body: CreateCatalogItemRequestBody

# Operation: get_catalog_item
class GetCatalogItemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The compound identifier for the catalog item, formatted as `{integration}:::{catalog}:::{external_id}`. Use `$custom` for the integration type and `$default` for the catalog name, followed by your item's external identifier.")
class GetCatalogItemRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetCatalogItemRequest(StrictModel):
    """Retrieve a specific catalog item by its compound ID. The item ID combines integration type, catalog name, and external identifier in a structured format."""
    path: GetCatalogItemRequestPath
    header: GetCatalogItemRequestHeader

# Operation: update_catalog_item
class UpdateCatalogItemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog item's compound ID in format `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your unique external item identifier.")
class UpdateCatalogItemRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class UpdateCatalogItemRequestBodyDataAttributes(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="The display name of the catalog item.")
    price: float | None = Field(default=None, validation_alias="price", serialization_alias="price", description="The item's price as a decimal number. This price is displayed in emails and should typically be updated alongside variant prices using the Update Catalog Variant endpoint.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A text description of the catalog item's features, details, or other relevant information.")
    url: str | None = Field(default=None, validation_alias="url", serialization_alias="url", description="A fully qualified URL pointing to the item's product page on your website.")
    images: list[str] | None = Field(default=None, validation_alias="images", serialization_alias="images", description="An array of image URLs for the catalog item. Order may be significant for display purposes. Each URL should point to a valid image resource.")
    custom_metadata: dict[str, Any] | None = Field(default=None, validation_alias="custom_metadata", serialization_alias="custom_metadata", description="A flat JSON object containing custom metadata about the item. Total size must not exceed 100 kilobytes.")
    published: bool | None = Field(default=None, validation_alias="published", serialization_alias="published", description="Boolean flag indicating whether the catalog item is currently published and visible.")
class UpdateCatalogItemRequestBodyDataRelationshipsCategories(StrictModel):
    data: list[UpdateCatalogItemBodyDataRelationshipsCategoriesDataItem] | None = Field(default=None, validation_alias="data", serialization_alias="data", description="Reserved parameter for internal use.")
class UpdateCatalogItemRequestBodyDataRelationships(StrictModel):
    categories: UpdateCatalogItemRequestBodyDataRelationshipsCategories | None = None
class UpdateCatalogItemRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog item's compound ID in format `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your unique external item identifier.")
    type_: Literal["catalog-item"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to `catalog-item`.")
    attributes: UpdateCatalogItemRequestBodyDataAttributes | None = None
    relationships: UpdateCatalogItemRequestBodyDataRelationships | None = None
class UpdateCatalogItemRequestBody(StrictModel):
    data: UpdateCatalogItemRequestBodyData
class UpdateCatalogItemRequest(StrictModel):
    """Update an existing catalog item with new metadata, pricing, images, or publication status. Use the compound ID format to identify the item, and include the required revision date for API versioning."""
    path: UpdateCatalogItemRequestPath
    header: UpdateCatalogItemRequestHeader
    body: UpdateCatalogItemRequestBody

# Operation: delete_catalog_item
class DeleteCatalogItemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the catalog item in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for the integration and `$default` for the catalog, followed by your item's external ID (e.g., `$custom:::$default:::SAMPLE-DATA-ITEM-1`).")
class DeleteCatalogItemRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format (optionally with a suffix). Defaults to 2026-01-15 if not specified.")
class DeleteCatalogItemRequest(StrictModel):
    """Permanently delete a catalog item from the default catalog. Requires the item's compound ID and the API revision date to ensure consistency."""
    path: DeleteCatalogItemRequestPath
    header: DeleteCatalogItemRequestHeader

# Operation: list_catalog_variants
class GetCatalogVariantsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter variants by specific criteria using supported fields and operators. You can filter by variant IDs (using `any` operator), item ID, SKU, title (partial match), or publication status. Provide filters in the format specified by the API filtering documentation.")
class GetCatalogVariantsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetCatalogVariantsRequest(StrictModel):
    """Retrieve all catalog variants in your account with optional filtering and sorting. Returns up to 100 variants per request."""
    query: GetCatalogVariantsRequestQuery | None = None
    header: GetCatalogVariantsRequestHeader

# Operation: create_catalog_variant
class CreateCatalogVariantRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15.")
class CreateCatalogVariantRequestBodyDataRelationshipsItemData(StrictModel):
    type_: Literal["catalog-item"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type for the parent catalog item relationship. Must be set to 'catalog-item'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the parent catalog item for which this variant is being created.")
class CreateCatalogVariantRequestBodyDataRelationshipsItem(StrictModel):
    data: CreateCatalogVariantRequestBodyDataRelationshipsItemData
class CreateCatalogVariantRequestBodyDataRelationships(StrictModel):
    item: CreateCatalogVariantRequestBodyDataRelationshipsItem
class CreateCatalogVariantRequestBodyDataAttributes(StrictModel):
    external_id: str = Field(default=..., validation_alias="external_id", serialization_alias="external_id", description="Unique identifier for this variant in your external system (e.g., your inventory management or e-commerce platform).")
    integration_type: Literal["$custom"] | None = Field(default=None, validation_alias="integration_type", serialization_alias="integration_type", description="Integration type for the variant source. Currently only '$custom' is supported for custom integrations.")
    title: str = Field(default=..., validation_alias="title", serialization_alias="title", description="Display name for the variant (e.g., 'Ocean Blue Shirt (Sample) Variant Medium'). Should be descriptive enough to distinguish this variant from others.")
    description: str = Field(default=..., validation_alias="description", serialization_alias="description", description="Detailed description of the variant's characteristics, materials, fit, or other distinguishing features.")
    sku: str = Field(default=..., validation_alias="sku", serialization_alias="sku", description="Stock keeping unit (SKU) code for inventory tracking and order fulfillment.")
    inventory_policy: Literal[0, 1, 2] | None = Field(default=None, validation_alias="inventory_policy", serialization_alias="inventory_policy", description="Controls variant visibility in dynamic product recommendation feeds. Use 1 to hide out-of-stock variants, or 0/2 to show regardless of inventory level. Defaults to 0.")
    inventory_quantity: float = Field(default=..., validation_alias="inventory_quantity", serialization_alias="inventory_quantity", description="Current stock quantity for this variant. Use a numeric value representing available units.")
    price: float = Field(default=..., validation_alias="price", serialization_alias="price", description="Price displayed for this variant in emails and product blocks. Update the parent item's price separately if needed for consistency across your catalog.")
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="Direct URL to this variant's product page on your website.")
    images: list[str] | None = Field(default=None, validation_alias="images", serialization_alias="images", description="Array of image URLs for the variant. Order matters—the first image is typically used as the primary product image.")
    custom_metadata: dict[str, Any] | None = Field(default=None, validation_alias="custom_metadata", serialization_alias="custom_metadata", description="Custom metadata as a flat JSON object (max 100KB). Use for storing additional variant attributes not covered by standard fields.")
    published: bool | None = Field(default=None, validation_alias="published", serialization_alias="published", description="Whether the variant is published and visible in your catalog. Defaults to true.")
class CreateCatalogVariantRequestBodyData(StrictModel):
    type_: Literal["catalog-variant"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier. Must be set to 'catalog-variant'.")
    relationships: CreateCatalogVariantRequestBodyDataRelationships
    attributes: CreateCatalogVariantRequestBodyDataAttributes
class CreateCatalogVariantRequestBody(StrictModel):
    data: CreateCatalogVariantRequestBodyData
class CreateCatalogVariantRequest(StrictModel):
    """Create a new variant for a catalog item, such as a specific size, color, or SKU. Variants inherit from their parent catalog item and can have distinct pricing, inventory, and product URLs."""
    header: CreateCatalogVariantRequestHeader
    body: CreateCatalogVariantRequestBody

# Operation: get_catalog_variant
class GetCatalogVariantRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The compound identifier for the catalog variant, formatted as {integration}:::{catalog}:::{external_id}. Use $custom for the integration type and $default for the catalog name, followed by your external variant identifier.")
class GetCatalogVariantRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetCatalogVariantRequest(StrictModel):
    """Retrieve a specific catalog item variant by its compound ID. The variant ID combines integration type, catalog name, and external identifier in a structured format."""
    path: GetCatalogVariantRequestPath
    header: GetCatalogVariantRequestHeader

# Operation: update_catalog_variant
class UpdateCatalogVariantRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog variant's compound ID in format `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your unique external identifier.")
class UpdateCatalogVariantRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to 2026-01-15.")
class UpdateCatalogVariantRequestBodyDataAttributes(StrictModel):
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="The display name for this variant (e.g., 'Ocean Blue Shirt (Sample) Variant Medium').")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed description of the variant's features, materials, and characteristics.")
    sku: str | None = Field(default=None, validation_alias="sku", serialization_alias="sku", description="The stock keeping unit (SKU) code for inventory and ordering purposes.")
    inventory_policy: Literal[0, 1, 2] | None = Field(default=None, validation_alias="inventory_policy", serialization_alias="inventory_policy", description="Controls variant visibility in dynamic product feeds. Use `1` to hide out-of-stock items, or `0`/`2` to show regardless of inventory status.")
    inventory_quantity: float | None = Field(default=None, validation_alias="inventory_quantity", serialization_alias="inventory_quantity", description="The current quantity of this variant in stock.")
    price: float | None = Field(default=None, validation_alias="price", serialization_alias="price", description="The price displayed for this variant in emails and product blocks. Consider also updating the parent item's price for consistency.")
    url: str | None = Field(default=None, validation_alias="url", serialization_alias="url", description="A direct URL to this variant's product page on your website.")
    images: list[str] | None = Field(default=None, validation_alias="images", serialization_alias="images", description="An array of image URLs for this variant. Order matters—the first image is typically used as the primary product image.")
    custom_metadata: dict[str, Any] | None = Field(default=None, validation_alias="custom_metadata", serialization_alias="custom_metadata", description="A flat JSON object for storing custom metadata about the variant (e.g., `{'Top Pick': true}`). Must not exceed 100KB.")
    published: bool | None = Field(default=None, validation_alias="published", serialization_alias="published", description="Set to `true` to make this variant visible in your catalog, or `false` to hide it.")
class UpdateCatalogVariantRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog variant's compound ID in format `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your unique external identifier.")
    type_: Literal["catalog-variant"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier. Must be set to `catalog-variant`.")
    attributes: UpdateCatalogVariantRequestBodyDataAttributes | None = None
class UpdateCatalogVariantRequestBody(StrictModel):
    data: UpdateCatalogVariantRequestBodyData
class UpdateCatalogVariantRequest(StrictModel):
    """Update a catalog item variant by its compound ID. Modify variant details such as title, description, pricing, inventory, images, and custom metadata to keep your product catalog current."""
    path: UpdateCatalogVariantRequestPath
    header: UpdateCatalogVariantRequestHeader
    body: UpdateCatalogVariantRequestBody

# Operation: delete_catalog_variant
class DeleteCatalogVariantRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The compound identifier for the catalog variant in the format {integration}:::{catalog}:::{external_id}. Use $custom as the integration type and $default as the catalog name, followed by your external variant identifier.")
class DeleteCatalogVariantRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class DeleteCatalogVariantRequest(StrictModel):
    """Permanently delete a catalog item variant by its compound ID. The variant ID must follow the format {integration}:::{catalog}:::{external_id}, where integration is $custom and catalog is $default."""
    path: DeleteCatalogVariantRequestPath
    header: DeleteCatalogVariantRequestHeader

# Operation: list_catalog_categories
class GetCatalogCategoriesRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results using supported fields and operators. You can filter by category IDs using the `any` operator, item IDs using `equals`, or category names using `contains` for partial matching.")
class GetCatalogCategoriesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetCatalogCategoriesRequest(StrictModel):
    """Retrieve all catalog categories in your account. Returns up to 100 categories per request, supporting filtering by IDs, item IDs, or category names."""
    query: GetCatalogCategoriesRequestQuery | None = None
    header: GetCatalogCategoriesRequestHeader

# Operation: create_catalog_category
class CreateCatalogCategoryRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class CreateCatalogCategoryRequestBodyDataAttributes(StrictModel):
    external_id: str = Field(default=..., validation_alias="external_id", serialization_alias="external_id", description="A unique identifier for this category in your external system. Use this to reference the category across integrations.")
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name for the catalog category. This is the human-readable label shown in your catalog.")
    integration_type: Literal["$custom"] | None = Field(default=None, validation_alias="integration_type", serialization_alias="integration_type", description="The integration type for this category. Currently only '$custom' is supported for custom integrations.")
class CreateCatalogCategoryRequestBodyDataRelationshipsItems(StrictModel):
    data: list[CreateCatalogCategoryBodyDataRelationshipsItemsDataItem] | None = Field(default=None, validation_alias="data", serialization_alias="data", description="Optional array of custom data fields to attach to this category. Item format and order significance depend on your integration requirements.")
class CreateCatalogCategoryRequestBodyDataRelationships(StrictModel):
    items: CreateCatalogCategoryRequestBodyDataRelationshipsItems | None = None
class CreateCatalogCategoryRequestBodyData(StrictModel):
    type_: Literal["catalog-category"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'catalog-category' for this operation.")
    attributes: CreateCatalogCategoryRequestBodyDataAttributes
    relationships: CreateCatalogCategoryRequestBodyDataRelationships | None = None
class CreateCatalogCategoryRequestBody(StrictModel):
    data: CreateCatalogCategoryRequestBodyData
class CreateCatalogCategoryRequest(StrictModel):
    """Create a new catalog category in your product catalog. The category will be identified by an external system ID and can include custom metadata."""
    header: CreateCatalogCategoryRequestHeader
    body: CreateCatalogCategoryRequestBody

# Operation: get_catalog_category
class GetCatalogCategoryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The compound identifier for the catalog category, formatted as `{integration}:::{catalog}:::{external_id}`. Currently supports only the `$custom` integration type and `$default` catalog. The external ID is a custom string that uniquely identifies the category within the catalog.")
class GetCatalogCategoryRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified.")
class GetCatalogCategoryRequest(StrictModel):
    """Retrieve a specific catalog category by its compound ID. The category ID combines integration type, catalog name, and external identifier to uniquely identify the category."""
    path: GetCatalogCategoryRequestPath
    header: GetCatalogCategoryRequestHeader

# Operation: update_catalog_category
class UpdateCatalogCategoryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog category identifier in compound format: {integration}:::{catalog}:::{external_id}. Use $custom for integration and $default for catalog, followed by your category's external ID (e.g., $custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL).")
class UpdateCatalogCategoryRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class UpdateCatalogCategoryRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name for the catalog category (e.g., 'Sample Data Category Apparel'). Optional field for updating category metadata.")
class UpdateCatalogCategoryRequestBodyDataRelationshipsItems(StrictModel):
    data: list[UpdateCatalogCategoryBodyDataRelationshipsItemsDataItem] | None = Field(default=None, validation_alias="data", serialization_alias="data", description="Additional structured data for the catalog category. Format and contents depend on the specific catalog structure requirements.")
class UpdateCatalogCategoryRequestBodyDataRelationships(StrictModel):
    items: UpdateCatalogCategoryRequestBodyDataRelationshipsItems | None = None
class UpdateCatalogCategoryRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog category identifier in compound format: {integration}:::{catalog}:::{external_id}. Must match the path ID and use $custom for integration and $default for catalog (e.g., $custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL).")
    type_: Literal["catalog-category"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'catalog-category' for this operation.")
    attributes: UpdateCatalogCategoryRequestBodyDataAttributes | None = None
    relationships: UpdateCatalogCategoryRequestBodyDataRelationships | None = None
class UpdateCatalogCategoryRequestBody(StrictModel):
    data: UpdateCatalogCategoryRequestBodyData
class UpdateCatalogCategoryRequest(StrictModel):
    """Update an existing catalog category by ID. Modifies category metadata such as name while maintaining the compound ID structure."""
    path: UpdateCatalogCategoryRequestPath
    header: UpdateCatalogCategoryRequestHeader
    body: UpdateCatalogCategoryRequestBody

# Operation: delete_catalog_category
class DeleteCatalogCategoryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The compound identifier for the catalog category, formatted as {integration}:::{catalog}:::{external_id}. Use $custom as the integration and $default as the catalog name.")
class DeleteCatalogCategoryRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class DeleteCatalogCategoryRequest(StrictModel):
    """Permanently delete a catalog category by its compound ID. The category ID must follow the format {integration}:::{catalog}:::{external_id}, where integration is $custom and catalog is $default."""
    path: DeleteCatalogCategoryRequestPath
    header: DeleteCatalogCategoryRequestHeader

# Operation: list_bulk_create_catalog_items_jobs
class GetBulkCreateCatalogItemsJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status using the equals operator (e.g., to show only processing jobs). Supports the status field only.")
class GetBulkCreateCatalogItemsJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkCreateCatalogItemsJobsRequest(StrictModel):
    """Retrieve all catalog item bulk create jobs with optional filtering by status. Returns up to 100 jobs per request."""
    query: GetBulkCreateCatalogItemsJobsRequestQuery | None = None
    header: GetBulkCreateCatalogItemsJobsRequestHeader

# Operation: create_catalog_items_bulk_job
class BulkCreateCatalogItemsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class BulkCreateCatalogItemsRequestBodyDataAttributesItems(StrictModel):
    data: list[CatalogItemCreateQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of catalog item objects to create. Accepts up to 100 items per request. Each item must conform to the catalog item schema. Order is preserved in processing.")
class BulkCreateCatalogItemsRequestBodyDataAttributes(StrictModel):
    items: BulkCreateCatalogItemsRequestBodyDataAttributesItems
class BulkCreateCatalogItemsRequestBodyData(StrictModel):
    type_: Literal["catalog-item-bulk-create-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The job type identifier. Must be set to 'catalog-item-bulk-create-job' to specify this operation creates catalog items in bulk.")
    attributes: BulkCreateCatalogItemsRequestBodyDataAttributes
class BulkCreateCatalogItemsRequestBody(StrictModel):
    data: BulkCreateCatalogItemsRequestBodyData
class BulkCreateCatalogItemsRequest(StrictModel):
    """Initiate a bulk job to create up to 100 catalog items in a single request. The operation queues the job for asynchronous processing with a maximum payload size of 5MB and a limit of 500 concurrent jobs."""
    header: BulkCreateCatalogItemsRequestHeader
    body: BulkCreateCatalogItemsRequestBody

# Operation: get_bulk_create_catalog_items_job
class GetBulkCreateCatalogItemsJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk create job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH).")
class GetBulkCreateCatalogItemsJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request.")
class GetBulkCreateCatalogItemsJobRequest(StrictModel):
    """Retrieve the status and details of a catalog item bulk create job by its ID. Optionally include related catalog items in the response."""
    path: GetBulkCreateCatalogItemsJobRequestPath
    header: GetBulkCreateCatalogItemsJobRequestHeader

# Operation: list_catalog_item_bulk_update_jobs
class GetBulkUpdateCatalogItemsJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Supports the status field only.")
class GetBulkUpdateCatalogItemsJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkUpdateCatalogItemsJobsRequest(StrictModel):
    """Retrieve all catalog item bulk update jobs with optional filtering by status. Returns up to 100 jobs per request."""
    query: GetBulkUpdateCatalogItemsJobsRequestQuery | None = None
    header: GetBulkUpdateCatalogItemsJobsRequestHeader

# Operation: create_catalog_item_bulk_update_job
class BulkUpdateCatalogItemsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class BulkUpdateCatalogItemsRequestBodyDataAttributesItems(StrictModel):
    data: list[CatalogItemUpdateQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of catalog items to update. Each item should contain the fields to be modified. Maximum 100 items per request; total payload cannot exceed 5MB.")
class BulkUpdateCatalogItemsRequestBodyDataAttributes(StrictModel):
    items: BulkUpdateCatalogItemsRequestBodyDataAttributesItems
class BulkUpdateCatalogItemsRequestBodyData(StrictModel):
    type_: Literal["catalog-item-bulk-update-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of bulk operation job being created. Must be set to 'catalog-item-bulk-update-job' to indicate this is a catalog item update operation.")
    attributes: BulkUpdateCatalogItemsRequestBodyDataAttributes
class BulkUpdateCatalogItemsRequestBody(StrictModel):
    data: BulkUpdateCatalogItemsRequestBodyData
class BulkUpdateCatalogItemsRequest(StrictModel):
    """Create a bulk update job to modify up to 100 catalog items in a single request. The job processes asynchronously and you can have up to 500 jobs in progress simultaneously."""
    header: BulkUpdateCatalogItemsRequestHeader
    body: BulkUpdateCatalogItemsRequestBody

# Operation: get_bulk_update_catalog_items_job
class GetBulkUpdateCatalogItemsJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk update job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH).")
class GetBulkUpdateCatalogItemsJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request.")
class GetBulkUpdateCatalogItemsJobRequest(StrictModel):
    """Retrieve the status and details of a catalog item bulk update job by its ID. Optionally include related catalog items in the response."""
    path: GetBulkUpdateCatalogItemsJobRequestPath
    header: GetBulkUpdateCatalogItemsJobRequestHeader

# Operation: list_bulk_delete_catalog_items_jobs
class GetBulkDeleteCatalogItemsJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status using the equals operator (e.g., to show only processing jobs). Omit to retrieve jobs in all statuses.")
class GetBulkDeleteCatalogItemsJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetBulkDeleteCatalogItemsJobsRequest(StrictModel):
    """Retrieve all catalog item bulk delete jobs with optional filtering by status. Returns up to 100 jobs per request."""
    query: GetBulkDeleteCatalogItemsJobsRequestQuery | None = None
    header: GetBulkDeleteCatalogItemsJobsRequestHeader

# Operation: create_catalog_item_bulk_delete_job
class BulkDeleteCatalogItemsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this operation.")
class BulkDeleteCatalogItemsRequestBodyDataAttributesItems(StrictModel):
    data: list[CatalogItemDeleteQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of catalog items to delete. Submit up to 100 items per request. Each item should contain the necessary identifiers for deletion.")
class BulkDeleteCatalogItemsRequestBodyDataAttributes(StrictModel):
    items: BulkDeleteCatalogItemsRequestBodyDataAttributesItems
class BulkDeleteCatalogItemsRequestBodyData(StrictModel):
    type_: Literal["catalog-item-bulk-delete-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The job type identifier. Must be set to 'catalog-item-bulk-delete-job' to indicate this is a bulk delete operation.")
    attributes: BulkDeleteCatalogItemsRequestBodyDataAttributes
class BulkDeleteCatalogItemsRequestBody(StrictModel):
    data: BulkDeleteCatalogItemsRequestBodyData
class BulkDeleteCatalogItemsRequest(StrictModel):
    """Create a bulk delete job to remove a batch of catalog items. Submit up to 100 items per request with a maximum payload of 5MB, and maintain no more than 500 concurrent jobs."""
    header: BulkDeleteCatalogItemsRequestHeader
    body: BulkDeleteCatalogItemsRequestBody

# Operation: get_bulk_delete_catalog_items_job
class GetBulkDeleteCatalogItemsJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk delete job to retrieve. This ID is returned when the bulk delete operation is initiated.")
class GetBulkDeleteCatalogItemsJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkDeleteCatalogItemsJobRequest(StrictModel):
    """Retrieve the status and details of a catalog item bulk delete job by its ID. Use this to monitor the progress of an in-progress or completed bulk deletion operation."""
    path: GetBulkDeleteCatalogItemsJobRequestPath
    header: GetBulkDeleteCatalogItemsJobRequestHeader

# Operation: list_bulk_create_variants_jobs
class GetBulkCreateVariantsJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Omit to return jobs of all statuses.")
class GetBulkCreateVariantsJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkCreateVariantsJobsRequest(StrictModel):
    """Retrieve all catalog variant bulk create jobs with optional filtering by status. Returns up to 100 jobs per request."""
    query: GetBulkCreateVariantsJobsRequestQuery | None = None
    header: GetBulkCreateVariantsJobsRequestHeader

# Operation: create_catalog_variants_bulk
class BulkCreateCatalogVariantsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15 if not specified.")
class BulkCreateCatalogVariantsRequestBodyDataAttributesVariants(StrictModel):
    data: list[CatalogVariantCreateQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of catalog variant objects to create. Accepts up to 100 variants per request with a maximum payload size of 5MB. Each item represents a single catalog variant to be created.")
class BulkCreateCatalogVariantsRequestBodyDataAttributes(StrictModel):
    variants: BulkCreateCatalogVariantsRequestBodyDataAttributesVariants
class BulkCreateCatalogVariantsRequestBodyData(StrictModel):
    type_: Literal["catalog-variant-bulk-create-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The job type identifier. Must be set to 'catalog-variant-bulk-create-job' to specify this operation.")
    attributes: BulkCreateCatalogVariantsRequestBodyDataAttributes
class BulkCreateCatalogVariantsRequestBody(StrictModel):
    data: BulkCreateCatalogVariantsRequestBodyData
class BulkCreateCatalogVariantsRequest(StrictModel):
    """Initiate a bulk job to create up to 100 catalog variants in a single request. The job processes asynchronously and allows up to 500 concurrent jobs per account."""
    header: BulkCreateCatalogVariantsRequestHeader
    body: BulkCreateCatalogVariantsRequestBody

# Operation: get_bulk_create_variants_job
class GetBulkCreateVariantsJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk create job to retrieve (format: alphanumeric string).")
class GetBulkCreateVariantsJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class GetBulkCreateVariantsJobRequest(StrictModel):
    """Retrieve the status and details of a catalog variant bulk create job by its ID. Optionally include related variant data in the response."""
    path: GetBulkCreateVariantsJobRequestPath
    header: GetBulkCreateVariantsJobRequestHeader

# Operation: list_bulk_update_variants_jobs
class GetBulkUpdateVariantsJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Supports filtering on the status field only.")
class GetBulkUpdateVariantsJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkUpdateVariantsJobsRequest(StrictModel):
    """Retrieve all catalog variant bulk update jobs with optional filtering by status. Returns up to 100 jobs per request."""
    query: GetBulkUpdateVariantsJobsRequestQuery | None = None
    header: GetBulkUpdateVariantsJobsRequestHeader

# Operation: create_catalog_variant_bulk_update_job
class BulkUpdateCatalogVariantsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15 if not specified.")
class BulkUpdateCatalogVariantsRequestBodyDataAttributesVariants(StrictModel):
    data: list[CatalogVariantUpdateQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of catalog variant objects to update. Accepts up to 100 variants per request with a maximum payload size of 5MB. Order is preserved for processing.")
class BulkUpdateCatalogVariantsRequestBodyDataAttributes(StrictModel):
    variants: BulkUpdateCatalogVariantsRequestBodyDataAttributesVariants
class BulkUpdateCatalogVariantsRequestBodyData(StrictModel):
    type_: Literal["catalog-variant-bulk-update-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The job type identifier. Must be set to 'catalog-variant-bulk-update-job' to indicate this is a bulk variant update operation.")
    attributes: BulkUpdateCatalogVariantsRequestBodyDataAttributes
class BulkUpdateCatalogVariantsRequestBody(StrictModel):
    data: BulkUpdateCatalogVariantsRequestBodyData
class BulkUpdateCatalogVariantsRequest(StrictModel):
    """Create a bulk update job to modify up to 100 catalog variants in a single request. The job processes asynchronously with a maximum of 500 concurrent jobs allowed per account."""
    header: BulkUpdateCatalogVariantsRequestHeader
    body: BulkUpdateCatalogVariantsRequestBody

# Operation: get_bulk_update_variants_job
class GetBulkUpdateVariantsJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk update job to retrieve.")
class GetBulkUpdateVariantsJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15).")
class GetBulkUpdateVariantsJobRequest(StrictModel):
    """Retrieve the status and details of a catalog variant bulk update job by its ID. Optionally include related variant data in the response."""
    path: GetBulkUpdateVariantsJobRequestPath
    header: GetBulkUpdateVariantsJobRequestHeader

# Operation: list_bulk_delete_variants_jobs
class GetBulkDeleteVariantsJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status using the equals operator (e.g., to show only processing jobs). Omit to retrieve jobs in all statuses.")
class GetBulkDeleteVariantsJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkDeleteVariantsJobsRequest(StrictModel):
    """Retrieve all catalog variant bulk delete jobs with optional filtering by status. Returns up to 100 jobs per request."""
    query: GetBulkDeleteVariantsJobsRequestQuery | None = None
    header: GetBulkDeleteVariantsJobsRequestHeader

# Operation: create_catalog_variant_bulk_delete_job
class BulkDeleteCatalogVariantsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this operation.")
class BulkDeleteCatalogVariantsRequestBodyDataAttributesVariants(StrictModel):
    data: list[CatalogVariantDeleteQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of catalog variant identifiers to delete. Accepts up to 100 variants per request with a maximum payload size of 5MB. Order is not significant.")
class BulkDeleteCatalogVariantsRequestBodyDataAttributes(StrictModel):
    variants: BulkDeleteCatalogVariantsRequestBodyDataAttributesVariants
class BulkDeleteCatalogVariantsRequestBodyData(StrictModel):
    type_: Literal["catalog-variant-bulk-delete-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of bulk job being created. Must be set to 'catalog-variant-bulk-delete-job' to indicate this is a variant deletion operation.")
    attributes: BulkDeleteCatalogVariantsRequestBodyDataAttributes
class BulkDeleteCatalogVariantsRequestBody(StrictModel):
    data: BulkDeleteCatalogVariantsRequestBodyData
class BulkDeleteCatalogVariantsRequest(StrictModel):
    """Create a bulk delete job to remove up to 100 catalog variants in a single request. The job is processed asynchronously, with a maximum of 500 jobs allowed in progress simultaneously."""
    header: BulkDeleteCatalogVariantsRequestHeader
    body: BulkDeleteCatalogVariantsRequestBody

# Operation: get_bulk_delete_variants_job
class GetBulkDeleteVariantsJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk delete job to retrieve. This ID is returned when the job is initially created.")
class GetBulkDeleteVariantsJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkDeleteVariantsJobRequest(StrictModel):
    """Retrieve the status and details of a catalog variant bulk delete job by its ID. Use this to monitor the progress and outcome of asynchronous variant deletion operations."""
    path: GetBulkDeleteVariantsJobRequestPath
    header: GetBulkDeleteVariantsJobRequestHeader

# Operation: list_bulk_create_categories_jobs
class GetBulkCreateCategoriesJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Supports the status field only.")
class GetBulkCreateCategoriesJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkCreateCategoriesJobsRequest(StrictModel):
    """Retrieve all catalog category bulk create jobs with optional filtering by status. Returns up to 100 jobs per request."""
    query: GetBulkCreateCategoriesJobsRequestQuery | None = None
    header: GetBulkCreateCategoriesJobsRequestHeader

# Operation: create_catalog_categories_bulk_job
class BulkCreateCatalogCategoriesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15 if not specified.")
class BulkCreateCatalogCategoriesRequestBodyDataAttributesCategories(StrictModel):
    data: list[CatalogCategoryCreateQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of catalog category objects to create. Accepts up to 100 items per request with a maximum payload size of 5MB. Order is preserved for processing.")
class BulkCreateCatalogCategoriesRequestBodyDataAttributes(StrictModel):
    categories: BulkCreateCatalogCategoriesRequestBodyDataAttributesCategories
class BulkCreateCatalogCategoriesRequestBodyData(StrictModel):
    type_: Literal["catalog-category-bulk-create-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The job type identifier. Must be set to 'catalog-category-bulk-create-job' to specify this operation creates catalog categories.")
    attributes: BulkCreateCatalogCategoriesRequestBodyDataAttributes
class BulkCreateCatalogCategoriesRequestBody(StrictModel):
    data: BulkCreateCatalogCategoriesRequestBodyData
class BulkCreateCatalogCategoriesRequest(StrictModel):
    """Initiate a bulk job to create up to 100 catalog categories in a single request. The job processes asynchronously and allows up to 500 concurrent jobs per account."""
    header: BulkCreateCatalogCategoriesRequestHeader
    body: BulkCreateCatalogCategoriesRequestBody

# Operation: get_bulk_create_categories_job
class GetBulkCreateCategoriesJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk create job to retrieve (format: alphanumeric string).")
class GetBulkCreateCategoriesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class GetBulkCreateCategoriesJobRequest(StrictModel):
    """Retrieve the status and details of a catalog category bulk create job by its ID. Optionally include related category resources in the response."""
    path: GetBulkCreateCategoriesJobRequestPath
    header: GetBulkCreateCategoriesJobRequestHeader

# Operation: list_bulk_update_categories_jobs
class GetBulkUpdateCategoriesJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Supports filtering on the status field only.")
class GetBulkUpdateCategoriesJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkUpdateCategoriesJobsRequest(StrictModel):
    """Retrieve all catalog category bulk update jobs with optional filtering by status. Returns up to 100 jobs per request."""
    query: GetBulkUpdateCategoriesJobsRequestQuery | None = None
    header: GetBulkUpdateCategoriesJobsRequestHeader

# Operation: create_catalog_category_bulk_update_job
class BulkUpdateCatalogCategoriesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15 if not specified.")
class BulkUpdateCatalogCategoriesRequestBodyDataAttributesCategories(StrictModel):
    data: list[CatalogCategoryUpdateQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of catalog category objects to update. Supports up to 100 categories per request with a maximum payload size of 5MB. Order is preserved for processing.")
class BulkUpdateCatalogCategoriesRequestBodyDataAttributes(StrictModel):
    categories: BulkUpdateCatalogCategoriesRequestBodyDataAttributesCategories
class BulkUpdateCatalogCategoriesRequestBodyData(StrictModel):
    type_: Literal["catalog-category-bulk-update-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The job type identifier. Must be set to 'catalog-category-bulk-update-job' to indicate this is a bulk category update operation.")
    attributes: BulkUpdateCatalogCategoriesRequestBodyDataAttributes
class BulkUpdateCatalogCategoriesRequestBody(StrictModel):
    data: BulkUpdateCatalogCategoriesRequestBodyData
class BulkUpdateCatalogCategoriesRequest(StrictModel):
    """Create a bulk update job to modify up to 100 catalog categories in a single request. The job processes asynchronously with a maximum of 500 concurrent jobs allowed per account."""
    header: BulkUpdateCatalogCategoriesRequestHeader
    body: BulkUpdateCatalogCategoriesRequestBody

# Operation: get_bulk_update_categories_job
class GetBulkUpdateCategoriesJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk update job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH).")
class GetBulkUpdateCategoriesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class GetBulkUpdateCategoriesJobRequest(StrictModel):
    """Retrieve the status and details of a catalog category bulk update job by its ID. Optionally include related category data in the response."""
    path: GetBulkUpdateCategoriesJobRequestPath
    header: GetBulkUpdateCategoriesJobRequestHeader

# Operation: list_bulk_delete_categories_jobs
class GetBulkDeleteCategoriesJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Omit to return jobs in all statuses.")
class GetBulkDeleteCategoriesJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkDeleteCategoriesJobsRequest(StrictModel):
    """Retrieve all catalog category bulk delete jobs with optional filtering by status. Returns up to 100 jobs per request."""
    query: GetBulkDeleteCategoriesJobsRequestQuery | None = None
    header: GetBulkDeleteCategoriesJobsRequestHeader

# Operation: create_catalog_category_bulk_delete_job
class BulkDeleteCatalogCategoriesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class BulkDeleteCatalogCategoriesRequestBodyDataAttributesCategories(StrictModel):
    data: list[CatalogCategoryDeleteQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of catalog category identifiers to delete. Accepts up to 100 categories per request. The total payload size must not exceed 5MB.")
class BulkDeleteCatalogCategoriesRequestBodyDataAttributes(StrictModel):
    categories: BulkDeleteCatalogCategoriesRequestBodyDataAttributesCategories
class BulkDeleteCatalogCategoriesRequestBodyData(StrictModel):
    type_: Literal["catalog-category-bulk-delete-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of bulk job being created. Must be set to 'catalog-category-bulk-delete-job' to indicate this is a catalog category deletion operation.")
    attributes: BulkDeleteCatalogCategoriesRequestBodyDataAttributes
class BulkDeleteCatalogCategoriesRequestBody(StrictModel):
    data: BulkDeleteCatalogCategoriesRequestBodyData
class BulkDeleteCatalogCategoriesRequest(StrictModel):
    """Create a bulk delete job to remove up to 100 catalog categories in a single request. The job is processed asynchronously and you can have up to 500 jobs in progress simultaneously."""
    header: BulkDeleteCatalogCategoriesRequestHeader
    body: BulkDeleteCatalogCategoriesRequestBody

# Operation: get_bulk_delete_categories_job
class GetBulkDeleteCategoriesJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk delete job to retrieve. This ID is returned when the bulk delete operation is initiated.")
class GetBulkDeleteCategoriesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkDeleteCategoriesJobRequest(StrictModel):
    """Retrieve the status and details of a catalog category bulk delete job by its ID. Use this to monitor the progress of an asynchronous bulk deletion operation."""
    path: GetBulkDeleteCategoriesJobRequestPath
    header: GetBulkDeleteCategoriesJobRequestHeader

# Operation: create_back_in_stock_subscription
class CreateBackInStockSubscriptionRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class CreateBackInStockSubscriptionRequestBodyDataAttributesProfileDataAttributes(StrictModel):
    email: str | None = Field(default=None, validation_alias="email", serialization_alias="email", description="The email address of the profile. Used to identify or create the profile if no profile ID is provided.")
    phone_number: str | None = Field(default=None, validation_alias="phone_number", serialization_alias="phone_number", description="The phone number of the profile in E.164 format (e.g., +15005550006). Used to identify or create the profile if no profile ID is provided.")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="An external identifier that links this Klaviyo profile to a profile in another system (such as a point-of-sale system). Format varies based on the external system.")
class CreateBackInStockSubscriptionRequestBodyDataAttributesProfileData(StrictModel):
    type_: Literal["profile"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Profile resource type identifier. Must be set to 'profile'.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the profile to subscribe. This is a Klaviyo-generated ID that uniquely identifies the profile in the system.")
    attributes: CreateBackInStockSubscriptionRequestBodyDataAttributesProfileDataAttributes | None = None
class CreateBackInStockSubscriptionRequestBodyDataAttributesProfile(StrictModel):
    data: CreateBackInStockSubscriptionRequestBodyDataAttributesProfileData
class CreateBackInStockSubscriptionRequestBodyDataAttributes(StrictModel):
    channels: list[Literal["EMAIL", "PUSH", "SMS", "WHATSAPP"]] = Field(default=..., validation_alias="channels", serialization_alias="channels", description="One or more notification channels through which the profile will receive back in stock alerts. Valid channels are EMAIL and SMS. Multiple channels can be specified as a comma-separated list or array.")
    profile: CreateBackInStockSubscriptionRequestBodyDataAttributesProfile
class CreateBackInStockSubscriptionRequestBodyDataRelationshipsVariantData(StrictModel):
    type_: Literal["catalog-variant"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Catalog variant resource type identifier. Must be set to 'catalog-variant'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog variant ID for which to create the subscription. Format is integrationType:::catalogId:::externalId (e.g., $custom:::$default:::SAMPLE-DATA-ITEM-1-VARIANT-MEDIUM or $shopify:::$default:::33001893429341).")
class CreateBackInStockSubscriptionRequestBodyDataRelationshipsVariant(StrictModel):
    data: CreateBackInStockSubscriptionRequestBodyDataRelationshipsVariantData
class CreateBackInStockSubscriptionRequestBodyDataRelationships(StrictModel):
    variant: CreateBackInStockSubscriptionRequestBodyDataRelationshipsVariant
class CreateBackInStockSubscriptionRequestBodyData(StrictModel):
    type_: Literal["back-in-stock-subscription"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier. Must be set to 'back-in-stock-subscription'.")
    attributes: CreateBackInStockSubscriptionRequestBodyDataAttributes
    relationships: CreateBackInStockSubscriptionRequestBodyDataRelationships
class CreateBackInStockSubscriptionRequestBody(StrictModel):
    data: CreateBackInStockSubscriptionRequestBodyData
class CreateBackInStockSubscriptionRequest(StrictModel):
    """Subscribe a profile to receive notifications when a catalog variant is back in stock. The profile can be identified by ID, email, phone number, or external ID, and will receive notifications through their preferred channels (email, SMS, or both)."""
    header: CreateBackInStockSubscriptionRequestHeader
    body: CreateBackInStockSubscriptionRequestBody

# Operation: list_items_for_catalog_category
class GetItemsForCatalogCategoryRequestPath(StrictModel):
    id_: str | None = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog category identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your category's external ID (e.g., `$custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL`).")
class GetItemsForCatalogCategoryRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results. Supports filtering by item IDs (any match), category ID (exact match), item title (contains), or publication status (exact match). Use the format specified in Klaviyo's filtering documentation.")
class GetItemsForCatalogCategoryRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format (e.g., 2026-01-15). Defaults to the latest stable revision if not specified.")
class GetItemsForCatalogCategoryRequest(StrictModel):
    """Retrieve all items in a specific catalog category. Results can be sorted by creation date and filtered by item IDs, category, title, or publication status, with a maximum of 100 items returned per request."""
    path: GetItemsForCatalogCategoryRequestPath
    query: GetItemsForCatalogCategoryRequestQuery | None = None
    header: GetItemsForCatalogCategoryRequestHeader

# Operation: list_item_ids_for_catalog_category
class GetItemIdsForCatalogCategoryRequestPath(StrictModel):
    id_: str | None = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog category identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your external category ID (e.g., `$custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL`).")
class GetItemIdsForCatalogCategoryRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results. Supports filtering by item IDs (any match), category ID (exact match), item title (contains), or published status (exact match). Use the format specified in Klaviyo's filtering documentation.")
class GetItemIdsForCatalogCategoryRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetItemIdsForCatalogCategoryRequest(StrictModel):
    """Retrieve all item IDs belonging to a specific catalog category. Returns up to 100 items per request and supports filtering by item IDs, category, title, or publication status."""
    path: GetItemIdsForCatalogCategoryRequestPath
    query: GetItemIdsForCatalogCategoryRequestQuery | None = None
    header: GetItemIdsForCatalogCategoryRequestHeader

# Operation: add_items_to_catalog_category
class AddItemsToCatalogCategoryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog category identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for the integration and `$default` for the catalog, followed by your category's external ID (e.g., `$custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL`).")
class AddItemsToCatalogCategoryRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class AddItemsToCatalogCategoryRequestBody(StrictModel):
    data: list[AddItemsToCatalogCategoryBodyDataItem] = Field(default=..., description="An array of item objects to associate with the category. Each item in the array will be linked to the specified catalog category.")
class AddItemsToCatalogCategoryRequest(StrictModel):
    """Associate one or more items with a catalog category by creating item relationships. This operation links items to the specified category within your catalog."""
    path: AddItemsToCatalogCategoryRequestPath
    header: AddItemsToCatalogCategoryRequestHeader
    body: AddItemsToCatalogCategoryRequestBody

# Operation: update_items_for_catalog_category
class UpdateItemsForCatalogCategoryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog category identifier in compound format: {integration}:::{catalog}:::{external_id}. Use integration type `$custom` and catalog `$default` with your external category ID (e.g., `$custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL`).")
class UpdateItemsForCatalogCategoryRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified.")
class UpdateItemsForCatalogCategoryRequestBody(StrictModel):
    data: list[UpdateItemsForCatalogCategoryBodyDataItem] = Field(default=..., description="An array of item relationship objects to associate with the category. Order and structure follow the JSON:API relationships specification.")
class UpdateItemsForCatalogCategoryRequest(StrictModel):
    """Update the item relationships associated with a catalog category. This operation modifies which items are linked to the specified category."""
    path: UpdateItemsForCatalogCategoryRequestPath
    header: UpdateItemsForCatalogCategoryRequestHeader
    body: UpdateItemsForCatalogCategoryRequestBody

# Operation: remove_items_from_catalog_category
class RemoveItemsFromCatalogCategoryRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog category identifier in compound format: {integration}:::{catalog}:::{external_id}. Use $custom as the integration and $default as the catalog, followed by your external category ID (e.g., $custom:::$default:::SAMPLE-DATA-CATEGORY-APPAREL).")
class RemoveItemsFromCatalogCategoryRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class RemoveItemsFromCatalogCategoryRequestBody(StrictModel):
    data: list[RemoveItemsFromCatalogCategoryBodyDataItem] = Field(default=..., description="Array of item identifiers to remove from the category. Each item in the array will be unlinked from the specified category.")
class RemoveItemsFromCatalogCategoryRequest(StrictModel):
    """Remove item relationships from a catalog category. Deletes the specified items from the given category, identified by its compound ID."""
    path: RemoveItemsFromCatalogCategoryRequestPath
    header: RemoveItemsFromCatalogCategoryRequestHeader
    body: RemoveItemsFromCatalogCategoryRequestBody

# Operation: list_variants_for_catalog_item
class GetVariantsForCatalogItemRequestPath(StrictModel):
    id_: str | None = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog item identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Currently only `$custom` integration and `$default` catalog are supported (e.g., `$custom:::$default:::SAMPLE-DATA-ITEM-1`).")
class GetVariantsForCatalogItemRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results. Supports filtering by variant IDs (any match), item ID (exact match), SKU (exact match), title (partial match), and published status (exact match). Use the Klaviyo filtering syntax for complex queries.")
class GetVariantsForCatalogItemRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API revision date in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request.")
class GetVariantsForCatalogItemRequest(StrictModel):
    """Retrieve all variants associated with a catalog item. Results can be sorted by creation date and are limited to 100 variants per request."""
    path: GetVariantsForCatalogItemRequestPath
    query: GetVariantsForCatalogItemRequestQuery | None = None
    header: GetVariantsForCatalogItemRequestHeader

# Operation: list_variant_ids_for_catalog_item
class GetVariantIdsForCatalogItemRequestPath(StrictModel):
    id_: str | None = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog item identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your external item ID (e.g., `$custom:::$default:::SAMPLE-DATA-ITEM-1`).")
class GetVariantIdsForCatalogItemRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results. Supports filtering by variant IDs (any match), item ID (exact match), SKU (exact match), title (partial match), and published status (exact match). Use the format specified in Klaviyo's filtering documentation.")
class GetVariantIdsForCatalogItemRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API revision date in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetVariantIdsForCatalogItemRequest(StrictModel):
    """Retrieve all variant IDs associated with a specific catalog item. Results can be filtered and sorted by creation date, with a maximum of 100 variants returned per request."""
    path: GetVariantIdsForCatalogItemRequestPath
    query: GetVariantIdsForCatalogItemRequestQuery | None = None
    header: GetVariantIdsForCatalogItemRequestHeader

# Operation: list_categories_for_catalog_item
class GetCategoriesForCatalogItemRequestPath(StrictModel):
    id_: str | None = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog item identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your item's external ID.")
class GetCategoriesForCatalogItemRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results by category IDs, item ID, or category name. Supports `ids` (any match), `item.id` (exact match), and `name` (partial match) operators.")
class GetCategoriesForCatalogItemRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API revision date in YYYY-MM-DD format (or with optional suffix). Defaults to the latest stable revision if not specified.")
class GetCategoriesForCatalogItemRequest(StrictModel):
    """Retrieve all catalog categories that contain a specific catalog item. Results can be sorted by creation date and are limited to 100 categories per request."""
    path: GetCategoriesForCatalogItemRequestPath
    query: GetCategoriesForCatalogItemRequestQuery | None = None
    header: GetCategoriesForCatalogItemRequestHeader

# Operation: list_category_ids_for_catalog_item
class GetCategoryIdsForCatalogItemRequestPath(StrictModel):
    id_: str | None = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog item identifier in compound format: `{integration}:::{catalog}:::{external_id}`. Use `$custom` for integration and `$default` for catalog, followed by your item's external ID.")
class GetCategoryIdsForCatalogItemRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter to narrow results by category IDs, item ID, or category name. Supports `ids` (any match), `item.id` (exact match), and `name` (partial match) operators.")
class GetCategoryIdsForCatalogItemRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to the latest stable version.")
class GetCategoryIdsForCatalogItemRequest(StrictModel):
    """Retrieve all catalog categories assigned to a specific catalog item. Returns up to 100 categories per request."""
    path: GetCategoryIdsForCatalogItemRequestPath
    query: GetCategoryIdsForCatalogItemRequestQuery | None = None
    header: GetCategoryIdsForCatalogItemRequestHeader

# Operation: add_categories_to_catalog_item
class AddCategoriesToCatalogItemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the catalog item, formatted as a compound ID with three colon-separated segments: integration type, catalog name, and external ID (e.g., $custom:::$default:::SAMPLE-DATA-ITEM-1). Currently only the $custom integration and $default catalog are supported.")
class AddCategoriesToCatalogItemRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class AddCategoriesToCatalogItemRequestBody(StrictModel):
    data: list[AddCategoriesToCatalogItemBodyDataItem] = Field(default=..., description="An array of category objects to associate with the catalog item. Each entry represents a category relationship to create.")
class AddCategoriesToCatalogItemRequest(StrictModel):
    """Associate one or more categories with a catalog item by creating category relationships. This operation links existing categories to the specified item in your catalog."""
    path: AddCategoriesToCatalogItemRequestPath
    header: AddCategoriesToCatalogItemRequestHeader
    body: AddCategoriesToCatalogItemRequestBody

# Operation: update_categories_for_catalog_item
class UpdateCategoriesForCatalogItemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the catalog item, formatted as a compound ID with three colon-separated segments: integration type, catalog name, and external ID. Use the format `$custom:::$default:::` followed by your item's external identifier.")
class UpdateCategoriesForCatalogItemRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class UpdateCategoriesForCatalogItemRequestBody(StrictModel):
    data: list[UpdateCategoriesForCatalogItemBodyDataItem] = Field(default=..., description="An array of category objects to associate with the catalog item. Each element defines a category relationship to be added or updated.")
class UpdateCategoriesForCatalogItemRequest(StrictModel):
    """Update the category relationships for a specific catalog item. This operation allows you to modify which categories are associated with an item in your catalog."""
    path: UpdateCategoriesForCatalogItemRequestPath
    header: UpdateCategoriesForCatalogItemRequestHeader
    body: UpdateCategoriesForCatalogItemRequestBody

# Operation: remove_categories_from_catalog_item
class RemoveCategoriesFromCatalogItemRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog item identifier in compound format: {integration}:::{catalog}:::{external_id}. Use $custom for integration and $default for catalog, followed by your item's external ID (e.g., $custom:::$default:::SAMPLE-DATA-ITEM-1).")
class RemoveCategoriesFromCatalogItemRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class RemoveCategoriesFromCatalogItemRequestBody(StrictModel):
    data: list[RemoveCategoriesFromCatalogItemBodyDataItem] = Field(default=..., description="Array of category relationship objects to remove from the catalog item. Each entry specifies a category to unlink.")
class RemoveCategoriesFromCatalogItemRequest(StrictModel):
    """Remove category relationships from a catalog item. Specify which categories to unlink from the item using a compound ID that identifies the integration, catalog, and external item reference."""
    path: RemoveCategoriesFromCatalogItemRequestPath
    header: RemoveCategoriesFromCatalogItemRequestHeader
    body: RemoveCategoriesFromCatalogItemRequestBody

# Operation: list_coupons
class GetCouponsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified.")
class GetCouponsRequest(StrictModel):
    """Retrieve all coupons in your Klaviyo account. Use this to view your complete coupon inventory and their details."""
    header: GetCouponsRequestHeader

# Operation: create_coupon
class CreateCouponRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v2). Defaults to 2026-01-15 if not specified.")
class CreateCouponRequestBodyDataAttributes(StrictModel):
    external_id: str = Field(default=..., validation_alias="external_id", serialization_alias="external_id", description="A unique identifier for this coupon in your external systems (such as Shopify or Magento). This ID is used to sync and reference the coupon across integrations.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of the coupon's purpose and terms (e.g., discount percentage, minimum purchase requirements, or promotional details).")
    monitor_configuration: dict[str, Any] | None = Field(default=None, validation_alias="monitor_configuration", serialization_alias="monitor_configuration", description="Configuration settings for monitoring coupon health and usage. Specify thresholds such as low_balance_threshold to trigger alerts when coupon balance falls below a specified amount.")
class CreateCouponRequestBodyData(StrictModel):
    type_: Literal["coupon"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'coupon' to indicate this operation creates a coupon resource.")
    attributes: CreateCouponRequestBodyDataAttributes
class CreateCouponRequestBody(StrictModel):
    data: CreateCouponRequestBodyData
class CreateCouponRequest(StrictModel):
    """Creates a new coupon for use in promotions and discounts. Requires a unique external identifier that maps to your integrated systems like Shopify or Magento."""
    header: CreateCouponRequestHeader
    body: CreateCouponRequestBody

# Operation: get_coupon
class GetCouponRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the coupon to retrieve (e.g., '10OFF'). This ID is consistent across internal and external integration systems.")
class GetCouponRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use for this request.")
class GetCouponRequest(StrictModel):
    """Retrieve a specific coupon by its ID. The coupon ID matches both the internal identifier and the external ID stored in integrated systems."""
    path: GetCouponRequestPath
    header: GetCouponRequestHeader

# Operation: update_coupon
class UpdateCouponRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the coupon to update (e.g., '10OFF'). This ID is consistent between the internal system and external integrations.")
class UpdateCouponRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API contract version to use for this request.")
class UpdateCouponRequestBodyDataAttributes(StrictModel):
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A human-readable description of the coupon's purpose or offer (e.g., '10% off for purchases over $50'). Optional field for documentation purposes.")
    monitor_configuration: dict[str, Any] | None = Field(default=None, validation_alias="monitor_configuration", serialization_alias="monitor_configuration", description="Configuration settings for monitoring the coupon's usage and health, such as balance thresholds. Accepts an object with monitoring parameters like low_balance_threshold.")
class UpdateCouponRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the coupon being updated (e.g., '10OFF'). Must match the ID in the path parameter.")
    type_: Literal["coupon"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'coupon' to identify this as a coupon update operation.")
    attributes: UpdateCouponRequestBodyDataAttributes | None = None
class UpdateCouponRequestBody(StrictModel):
    data: UpdateCouponRequestBodyData
class UpdateCouponRequest(StrictModel):
    """Update an existing coupon's properties such as description and monitoring configuration. Requires the coupon ID and current revision for optimistic concurrency control."""
    path: UpdateCouponRequestPath
    header: UpdateCouponRequestHeader
    body: UpdateCouponRequestBody

# Operation: delete_coupon
class DeleteCouponRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the coupon to delete. This ID matches both the internal system ID and the external ID used in integrations (e.g., '10OFF').")
class DeleteCouponRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use for this request.")
class DeleteCouponRequest(StrictModel):
    """Permanently delete a coupon by its ID. This operation requires the coupons:write scope and is subject to rate limits of 3 requests per second (burst) and 60 requests per minute (steady state)."""
    path: DeleteCouponRequestPath
    header: DeleteCouponRequestHeader

# Operation: list_coupon_codes
class GetCouponCodesRequestQuery(StrictModel):
    filter_: str = Field(default=..., validation_alias="filter", serialization_alias="filter", description="Filter expression to narrow results by coupon ID(s), profile ID(s), expiration date range, or status. At least one coupon or profile filter is required. Use 'any' operator to match multiple IDs, 'equals' for single matches, and comparison operators (greater-than, less-than, etc.) for date ranges. Format: operator(field,'value') or operator(field,'value1','value2',...)")
class GetCouponCodesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetCouponCodesRequest(StrictModel):
    """Retrieve coupon codes filtered by coupon ID(s) and/or profile ID(s). Use filter parameters to specify which coupons or customer profiles to retrieve codes for, and optionally filter by expiration date or status."""
    query: GetCouponCodesRequestQuery
    header: GetCouponCodesRequestHeader

# Operation: create_coupon_code
class CreateCouponCodeRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request.")
class CreateCouponCodeRequestBodyDataRelationshipsCouponData(StrictModel):
    type_: Literal["coupon"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Related resource type identifier; must be set to 'coupon' to indicate the relationship points to a coupon resource.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="Unique identifier for the coupon code (e.g., '10OFF'). Used as a reference key for this coupon code resource.")
class CreateCouponCodeRequestBodyDataRelationshipsCoupon(StrictModel):
    data: CreateCouponCodeRequestBodyDataRelationshipsCouponData
class CreateCouponCodeRequestBodyDataRelationships(StrictModel):
    coupon: CreateCouponCodeRequestBodyDataRelationshipsCoupon
class CreateCouponCodeRequestBodyDataAttributes(StrictModel):
    unique_code: str = Field(default=..., validation_alias="unique_code", serialization_alias="unique_code", description="A unique alphanumeric string assigned to each customer or profile to identify and track this specific coupon code instance.")
    expires_at: str | None = Field(default=None, validation_alias="expires_at", serialization_alias="expires_at", description="Optional expiration date and time in ISO 8601 format (e.g., 2022-11-08T00:00:00+00:00). If omitted or null, the code automatically expires 1 year from creation.", json_schema_extra={'format': 'date-time'})
class CreateCouponCodeRequestBodyData(StrictModel):
    type_: Literal["coupon-code"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier; must be set to 'coupon-code' to indicate this is a coupon code resource.")
    relationships: CreateCouponCodeRequestBodyDataRelationships
    attributes: CreateCouponCodeRequestBodyDataAttributes
class CreateCouponCodeRequestBody(StrictModel):
    data: CreateCouponCodeRequestBodyData
class CreateCouponCodeRequest(StrictModel):
    """Creates a unique coupon code linked to a specific coupon, enabling per-customer or per-profile discount distribution. The code will automatically expire after 1 year unless a custom expiration date is provided."""
    header: CreateCouponCodeRequestHeader
    body: CreateCouponCodeRequestBody

# Operation: get_coupon_code
class GetCouponCodeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The combined identifier for the coupon code, consisting of the unique code and its associated coupon ID (e.g., '10OFF-ASD325FHK324UJDOI2M3JNES99').")
class GetCouponCodeRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class GetCouponCodeRequest(StrictModel):
    """Retrieve a specific coupon code by its combined identifier (code + coupon ID). Returns the full coupon code details including associated metadata."""
    path: GetCouponCodeRequestPath
    header: GetCouponCodeRequestHeader

# Operation: update_coupon_code
class UpdateCouponCodeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the coupon code, formatted as the coupon code combined with its associated coupon ID (e.g., '10OFF-ASD325FHK324UJDOI2M3JNES99').")
class UpdateCouponCodeRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class UpdateCouponCodeRequestBodyDataAttributes(StrictModel):
    status: Literal["ASSIGNED_TO_PROFILE", "DELETING", "PROCESSING", "UNASSIGNED", "USED", "VERSION_NOT_ACTIVE"] | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The current status of the coupon code in the system. Valid statuses include: ASSIGNED_TO_PROFILE (linked to a customer), UNASSIGNED (available for use), USED (already redeemed), PROCESSING (being created), DELETING (being removed), or VERSION_NOT_ACTIVE (associated coupon is inactive).")
    expires_at: str | None = Field(default=None, validation_alias="expires_at", serialization_alias="expires_at", description="The date and time when this coupon code expires, specified in ISO 8601 format with timezone (e.g., '2022-11-08T00:00:00+00:00'). If omitted or set to null, the expiration will automatically default to one year from the current date.", json_schema_extra={'format': 'date-time'})
class UpdateCouponCodeRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the coupon code being updated, formatted as the coupon code combined with its associated coupon ID (e.g., '10OFF-ASD325FHK324UJDOI2M3JNES99'). Must match the path ID.")
    type_: Literal["coupon-code"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'coupon-code'.")
    attributes: UpdateCouponCodeRequestBodyDataAttributes | None = None
class UpdateCouponCodeRequestBody(StrictModel):
    data: UpdateCouponCodeRequestBodyData
class UpdateCouponCodeRequest(StrictModel):
    """Update the status or expiration date of a coupon code. This operation allows you to modify coupon code lifecycle properties such as assignment status and expiration timing."""
    path: UpdateCouponCodeRequestPath
    header: UpdateCouponCodeRequestHeader
    body: UpdateCouponCodeRequestBody

# Operation: delete_coupon_code
class DeleteCouponCodeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier combining the coupon code and its associated coupon ID (e.g., '10OFF-ASD325FHK324UJDOI2M3JNES99').")
class DeleteCouponCodeRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class DeleteCouponCodeRequest(StrictModel):
    """Permanently deletes a coupon code by its identifier. The operation will fail if the coupon code has an assigned profile."""
    path: DeleteCouponCodeRequestPath
    header: DeleteCouponCodeRequestHeader

# Operation: list_coupon_code_bulk_create_jobs
class GetBulkCreateCouponCodeJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status using the equals operator (e.g., to retrieve only processing jobs). Supports filtering on the status field only.")
class GetBulkCreateCouponCodeJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetBulkCreateCouponCodeJobsRequest(StrictModel):
    """Retrieve all coupon code bulk create jobs with optional filtering by status. Returns up to 100 jobs per request."""
    query: GetBulkCreateCouponCodeJobsRequestQuery | None = None
    header: GetBulkCreateCouponCodeJobsRequestHeader

# Operation: create_coupon_code_bulk_job
class BulkCreateCouponCodesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v2). Defaults to 2026-01-15 if not specified.")
class BulkCreateCouponCodesRequestBodyDataAttributesCouponCodes(StrictModel):
    data: list[CouponCodeCreateQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of coupon code definitions to create in this bulk job. Maximum 1,000 items per job. Each item should contain the coupon code configuration details.")
class BulkCreateCouponCodesRequestBodyDataAttributes(StrictModel):
    coupon_codes: BulkCreateCouponCodesRequestBodyDataAttributesCouponCodes = Field(default=..., validation_alias="coupon-codes", serialization_alias="coupon-codes")
class BulkCreateCouponCodesRequestBodyData(StrictModel):
    type_: Literal["coupon-code-bulk-create-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The job type identifier. Must be set to 'coupon-code-bulk-create-job' to specify this operation.")
    attributes: BulkCreateCouponCodesRequestBodyDataAttributes
class BulkCreateCouponCodesRequestBody(StrictModel):
    data: BulkCreateCouponCodesRequestBodyData
class BulkCreateCouponCodesRequest(StrictModel):
    """Initiate a bulk job to create up to 1,000 coupon codes at once. You can queue up to 100 jobs simultaneously, with rate limits of 75 requests per second (burst) or 700 per minute (steady state)."""
    header: BulkCreateCouponCodesRequestHeader
    body: BulkCreateCouponCodesRequestBody

# Operation: get_coupon_code_bulk_create_job
class GetBulkCreateCouponCodesJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk create job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH).")
class GetBulkCreateCouponCodesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkCreateCouponCodesJobRequest(StrictModel):
    """Retrieve the status and details of a coupon code bulk create job by its ID. Use this to monitor the progress and results of asynchronous bulk coupon code creation operations."""
    path: GetBulkCreateCouponCodesJobRequestPath
    header: GetBulkCreateCouponCodesJobRequestHeader

# Operation: get_coupon_for_coupon_code
class GetCouponForCouponCodeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the coupon code to retrieve the associated coupon for (e.g., '10OFF').")
class GetCouponForCouponCodeRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class GetCouponForCouponCodeRequest(StrictModel):
    """Retrieve the coupon associated with a specific coupon code ID. This operation allows you to look up the relationship between a coupon code and its corresponding coupon details."""
    path: GetCouponForCouponCodeRequestPath
    header: GetCouponForCouponCodeRequestHeader

# Operation: get_coupon_relationship_for_coupon_code
class GetCouponIdForCouponCodeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The coupon code ID to look up (e.g., '10OFF'). This is the identifier of the coupon code whose associated coupon you want to retrieve.")
class GetCouponIdForCouponCodeRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use for this request.")
class GetCouponIdForCouponCodeRequest(StrictModel):
    """Retrieves the coupon relationship associated with a specific coupon code. Use this to find which coupon is linked to a given coupon code ID."""
    path: GetCouponIdForCouponCodeRequestPath
    header: GetCouponIdForCouponCodeRequestHeader

# Operation: list_coupon_codes_for_coupon
class GetCouponCodesForCouponRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the coupon to retrieve associated codes for (e.g., '10OFF').")
class GetCouponCodesForCouponRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results by expiration date (using comparison operators), status, or related coupon/profile identifiers. Supports multiple filter conditions.")
class GetCouponCodesForCouponRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15).")
class GetCouponCodesForCouponRequest(StrictModel):
    """Retrieve all coupon codes associated with a specific coupon. Supports filtering by expiration date, status, and related coupon or profile IDs."""
    path: GetCouponCodesForCouponRequestPath
    query: GetCouponCodesForCouponRequestQuery | None = None
    header: GetCouponCodesForCouponRequestHeader

# Operation: list_coupon_code_ids_for_coupon
class GetCouponCodeIdsForCouponRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the coupon to retrieve associated coupon codes for (e.g., '10OFF').")
class GetCouponCodeIdsForCouponRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results. Supports filtering by expiration date (using comparison operators like less-than or greater-than), status (exact match), coupon ID, or profile ID. See API documentation for filter syntax details.")
class GetCouponCodeIdsForCouponRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (defaults to 2026-01-15). Specify a different revision date if needed for API version compatibility.")
class GetCouponCodeIdsForCouponRequest(StrictModel):
    """Retrieves the list of coupon code IDs associated with a specific coupon. Use optional filters to narrow results by expiration date, status, or related coupon/profile IDs."""
    path: GetCouponCodeIdsForCouponRequestPath
    query: GetCouponCodeIdsForCouponRequestQuery | None = None
    header: GetCouponCodeIdsForCouponRequestHeader

# Operation: list_data_sources
class GetDataSourcesRequestQuery(StrictModel):
    fields_data_source: list[Literal["description", "namespace", "title", "visibility"]] | None = Field(default=None, validation_alias="fields[data-source]", serialization_alias="fields[data-source]", description="Specify which data source fields to include in the response for sparse fieldset optimization. Omit to return all available fields.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of data sources to return per page. Defaults to 20 results; valid range is 1 to 100 items per page.", ge=1, le=100)
class GetDataSourcesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (optionally with a suffix). Defaults to 2026-01-15 if not specified.")
class GetDataSourcesRequest(StrictModel):
    """Retrieve all data sources configured in your account. Supports pagination and sparse fieldset selection to optimize response payload."""
    query: GetDataSourcesRequestQuery | None = None
    header: GetDataSourcesRequestHeader

# Operation: create_data_source
class CreateDataSourceRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class CreateDataSourceRequestBodyDataAttributes(StrictModel):
    title: str = Field(default=..., validation_alias="title", serialization_alias="title", description="A unique display name for the data source within its namespace. Must be between 1 and 255 characters long.")
    visibility: Literal["private", "shared"] | None = Field(default=None, validation_alias="visibility", serialization_alias="visibility", description="Controls who can access this data source. Choose 'private' for account-only access or 'shared' for broader visibility. Defaults to 'private'.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Optional descriptive text providing additional context about the data source's purpose or contents.")
    namespace: str | None = Field(default=None, validation_alias="namespace", serialization_alias="namespace", description="The organizational container for this data source. Defaults to 'custom-objects' if not specified, which is the standard namespace for custom object definitions.")
class CreateDataSourceRequestBodyData(StrictModel):
    type_: Literal["data-source"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'data-source' to indicate this operation creates a data source.")
    attributes: CreateDataSourceRequestBodyDataAttributes
class CreateDataSourceRequestBody(StrictModel):
    """Create data source"""
    data: CreateDataSourceRequestBodyData
class CreateDataSourceRequest(StrictModel):
    """Create a new data source within an account namespace. Data sources serve as containers for custom object definitions and can be configured with different visibility levels."""
    header: CreateDataSourceRequestHeader
    body: CreateDataSourceRequestBody

# Operation: get_data_source
class GetDataSourceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the data source to retrieve.")
class GetDataSourceRequestQuery(StrictModel):
    fields_data_source: list[Literal["description", "namespace", "title", "visibility"]] | None = Field(default=None, validation_alias="fields[data-source]", serialization_alias="fields[data-source]", description="Optional list of specific data source fields to include in the response. Omit to retrieve all available fields. See API documentation for valid field names.")
class GetDataSourceRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetDataSourceRequest(StrictModel):
    """Retrieve a specific data source by ID from your account. Use this to fetch detailed information about a configured data source."""
    path: GetDataSourceRequestPath
    query: GetDataSourceRequestQuery | None = None
    header: GetDataSourceRequestHeader

# Operation: delete_data_source
class DeleteDataSourceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the data source to delete.")
class DeleteDataSourceRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class DeleteDataSourceRequest(StrictModel):
    """Permanently delete a data source from your account. This operation requires the data source ID and the current API revision to ensure consistency."""
    path: DeleteDataSourceRequestPath
    header: DeleteDataSourceRequestHeader

# Operation: create_data_source_records_bulk
class BulkCreateDataSourceRecordsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class BulkCreateDataSourceRecordsRequestBodyDataRelationshipsDataSourceData(StrictModel):
    type_: Literal["data-source"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for the data source relationship, which must be 'data-source'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the data source to which these records belong (e.g., '01J7C23V8XWMRG13FMD7VZN6GW').")
class BulkCreateDataSourceRecordsRequestBodyDataRelationshipsDataSource(StrictModel):
    data: BulkCreateDataSourceRecordsRequestBodyDataRelationshipsDataSourceData
class BulkCreateDataSourceRecordsRequestBodyDataRelationships(StrictModel):
    data_source: BulkCreateDataSourceRecordsRequestBodyDataRelationshipsDataSource = Field(default=..., validation_alias="data-source", serialization_alias="data-source")
class BulkCreateDataSourceRecordsRequestBodyDataAttributesDataSourceRecords(StrictModel):
    data: list[DataSourceRecordResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of record objects to import. Supports up to 500 records per request, with each record not exceeding 512KB in size.")
class BulkCreateDataSourceRecordsRequestBodyDataAttributes(StrictModel):
    data_source_records: BulkCreateDataSourceRecordsRequestBodyDataAttributesDataSourceRecords = Field(default=..., validation_alias="data-source-records", serialization_alias="data-source-records")
class BulkCreateDataSourceRecordsRequestBodyData(StrictModel):
    type_: Literal["data-source-record-bulk-create-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type identifier for this operation, which must be 'data-source-record-bulk-create-job'.")
    relationships: BulkCreateDataSourceRecordsRequestBodyDataRelationships
    attributes: BulkCreateDataSourceRecordsRequestBodyDataAttributes
class BulkCreateDataSourceRecordsRequestBody(StrictModel):
    """Create a data source record job"""
    data: BulkCreateDataSourceRecordsRequestBodyData
class BulkCreateDataSourceRecordsRequest(StrictModel):
    """Initiate a bulk import job to create up to 500 data source records in a single request. The operation accepts a batch of records with a maximum payload size of 4MB total and 512KB per individual record."""
    header: BulkCreateDataSourceRecordsRequestHeader
    body: BulkCreateDataSourceRecordsRequestBody

# Operation: create_data_source_record
class CreateDataSourceRecordRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class CreateDataSourceRecordRequestBodyDataAttributesDataSourceRecordDataAttributes(StrictModel):
    record: dict[str, Any] = Field(default=..., validation_alias="record", serialization_alias="record", description="The record object containing the data to be imported. Must not exceed 512KB in size.")
class CreateDataSourceRecordRequestBodyDataAttributesDataSourceRecordData(StrictModel):
    type_: Literal["data-source-record"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type identifier for the data source record. Must be 'data-source-record'.")
    attributes: CreateDataSourceRecordRequestBodyDataAttributesDataSourceRecordDataAttributes
class CreateDataSourceRecordRequestBodyDataAttributesDataSourceRecord(StrictModel):
    data: CreateDataSourceRecordRequestBodyDataAttributesDataSourceRecordData
class CreateDataSourceRecordRequestBodyDataAttributes(StrictModel):
    data_source_record: CreateDataSourceRecordRequestBodyDataAttributesDataSourceRecord = Field(default=..., validation_alias="data-source-record", serialization_alias="data-source-record")
class CreateDataSourceRecordRequestBodyDataRelationshipsDataSourceData(StrictModel):
    type_: Literal["data-source"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type identifier for the data source relationship. Must be 'data-source'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the data source to which this record belongs (e.g., 01J7C23V8XWMRG13FMD7VZN6GW).")
class CreateDataSourceRecordRequestBodyDataRelationshipsDataSource(StrictModel):
    data: CreateDataSourceRecordRequestBodyDataRelationshipsDataSourceData
class CreateDataSourceRecordRequestBodyDataRelationships(StrictModel):
    data_source: CreateDataSourceRecordRequestBodyDataRelationshipsDataSource = Field(default=..., validation_alias="data-source", serialization_alias="data-source")
class CreateDataSourceRecordRequestBodyData(StrictModel):
    type_: Literal["data-source-record-create-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of job being created. Must be 'data-source-record-create-job'.")
    attributes: CreateDataSourceRecordRequestBodyDataAttributes
    relationships: CreateDataSourceRecordRequestBodyDataRelationships
class CreateDataSourceRecordRequestBody(StrictModel):
    """Create a data source record job"""
    data: CreateDataSourceRecordRequestBodyData
class CreateDataSourceRecordRequest(StrictModel):
    """Create a single data source record import job. The record payload must not exceed 512KB. Requires custom-objects:write scope."""
    header: CreateDataSourceRecordRequestHeader
    body: CreateDataSourceRecordRequestBody

# Operation: create_profile_deletion_job
class RequestProfileDeletionRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15.")
class RequestProfileDeletionRequestBodyDataAttributesProfileDataAttributes(StrictModel):
    email: str | None = Field(default=None, validation_alias="email", serialization_alias="email", description="Email address of the individual whose profile(s) should be deleted. Provide this, phone_number, or neither—but not multiple identifier types together.")
    phone_number: str | None = Field(default=None, validation_alias="phone_number", serialization_alias="phone_number", description="Phone number in E.164 format (e.g., +1 country code and number) of the individual whose profile(s) should be deleted. Provide this, email, or neither—but not multiple identifier types together.")
class RequestProfileDeletionRequestBodyDataAttributesProfileData(StrictModel):
    type_: Literal["profile"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier for the profile being deleted. Must be set to 'profile'.")
    attributes: RequestProfileDeletionRequestBodyDataAttributesProfileDataAttributes | None = None
class RequestProfileDeletionRequestBodyDataAttributesProfile(StrictModel):
    data: RequestProfileDeletionRequestBodyDataAttributesProfileData
class RequestProfileDeletionRequestBodyDataAttributes(StrictModel):
    profile: RequestProfileDeletionRequestBodyDataAttributesProfile
class RequestProfileDeletionRequestBodyData(StrictModel):
    type_: Literal["data-privacy-deletion-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier for the deletion job request. Must be set to 'data-privacy-deletion-job'.")
    attributes: RequestProfileDeletionRequestBodyDataAttributes
class RequestProfileDeletionRequestBody(StrictModel):
    data: RequestProfileDeletionRequestBodyData
class RequestProfileDeletionRequest(StrictModel):
    """Request asynchronous deletion of all profiles matching a specified identifier (email, phone number, or profile ID). Only one identifier type may be provided per request. Deleted profiles will appear on the Deleted Profiles page once processing completes."""
    header: RequestProfileDeletionRequestHeader
    body: RequestProfileDeletionRequestBody

# Operation: list_events
class GetEventsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter events by specific criteria using comparison operators. Supports filtering by metric_id, profile_id, profile relationship, or datetime/timestamp ranges (e.g., events after a specific date). Custom metrics are not supported in metric_id filters. See API documentation for detailed filter syntax.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of events to return per page. Defaults to 200 if not specified; must be between 1 and 1000.", ge=1, le=1000)
class GetEventsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15.")
class GetEventsRequest(StrictModel):
    """Retrieve all events from an account with optional filtering by metric, profile, or datetime range. Returns up to 200 events per page."""
    query: GetEventsRequestQuery | None = None
    header: GetEventsRequestHeader

# Operation: create_event
class CreateEventRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class CreateEventRequestBodyDataAttributesMetricDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="Name of the event. Must be less than 128 characters.")
class CreateEventRequestBodyDataAttributesMetricData(StrictModel):
    type_: Literal["metric"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Metric resource type identifier. Must be set to 'metric'.")
    attributes: CreateEventRequestBodyDataAttributesMetricDataAttributes
class CreateEventRequestBodyDataAttributesMetric(StrictModel):
    data: CreateEventRequestBodyDataAttributesMetricData
class CreateEventRequestBodyDataAttributes(StrictModel):
    properties: dict[str, Any] = Field(default=..., validation_alias="properties", serialization_alias="properties", description="Custom properties for this event. Supports up to 400 properties with a maximum payload size of 5 MB total and 100 KB per string value. Top-level non-object properties can be used to create segments; use the $extra property for non-segmentable values like HTML templates.")
    time_: str | None = Field(default=None, validation_alias="time", serialization_alias="time", description="ISO 8601 timestamp indicating when the event occurred. If omitted, the server's current time is used. Timestamps are truncated to the second and must be after 2000 and no more than 1 year in the future.", json_schema_extra={'format': 'date-time'})
    value: float | None = Field(default=None, validation_alias="value", serialization_alias="value", description="Numeric monetary value associated with the event, such as purchase amount or revenue.")
    value_currency: str | None = Field(default=None, validation_alias="value_currency", serialization_alias="value_currency", description="ISO 4217 currency code for the event value (e.g., USD, EUR). Should be provided if a value is specified.")
    unique_id: str | None = Field(default=None, validation_alias="unique_id", serialization_alias="unique_id", description="Unique identifier for deduplication. If the same unique_id is submitted for the same profile and metric, only the first processed event is recorded. Defaults to timestamp precision of one second, limiting one event per profile per second.")
    profile: CreateEventBodyDataAttributesProfile | None = Field(default=None, validation_alias="profile", serialization_alias="profile", description="Profile associated with the event: email, phone, name, location, and custom properties.")
    metric: CreateEventRequestBodyDataAttributesMetric
class CreateEventRequestBodyData(StrictModel):
    type_: Literal["event"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier. Must be set to 'event'.")
    attributes: CreateEventRequestBodyDataAttributes
class CreateEventRequestBody(StrictModel):
    data: CreateEventRequestBodyData
class CreateEventRequest(StrictModel):
    """Track a profile's activity by creating a new event. This operation also allows you to create a new profile or update an existing profile's properties in a single request. The event is validated and queued for processing immediately, though processing may not complete instantly."""
    header: CreateEventRequestHeader
    body: CreateEventRequestBody

# Operation: get_event
class GetEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event to retrieve.")
class GetEventRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class GetEventRequest(StrictModel):
    """Retrieve a specific event by its ID. Returns the complete event details for the requested event."""
    path: GetEventRequestPath
    header: GetEventRequestHeader

# Operation: create_events_bulk
class BulkCreateEventsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class BulkCreateEventsRequestBodyDataAttributesEventsBulkCreate(StrictModel):
    data: list[EventsBulkCreateQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of event objects to create, with a maximum of 1,000 events per request and 5MB total payload size. Each event must include at least one profile identifier (id, email, or phone_number) and a metric name. Individual string values cannot exceed 100KB.")
class BulkCreateEventsRequestBodyDataAttributes(StrictModel):
    events_bulk_create: BulkCreateEventsRequestBodyDataAttributesEventsBulkCreate = Field(default=..., validation_alias="events-bulk-create", serialization_alias="events-bulk-create")
class BulkCreateEventsRequestBodyData(StrictModel):
    type_: Literal["event-bulk-create-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of bulk job being created. Must be set to 'event-bulk-create-job' to indicate this is an event creation operation.")
    attributes: BulkCreateEventsRequestBodyDataAttributes
class BulkCreateEventsRequestBody(StrictModel):
    data: BulkCreateEventsRequestBodyData
class BulkCreateEventsRequest(StrictModel):
    """Create a batch of up to 1,000 events for one or more profiles in a single request. This operation supports creating new profiles or updating existing profile properties alongside event creation."""
    header: BulkCreateEventsRequestHeader
    body: BulkCreateEventsRequestBody

# Operation: get_metric_for_event
class GetMetricForEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event for which to retrieve the associated metric.")
class GetMetricForEventRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class GetMetricForEventRequest(StrictModel):
    """Retrieve the metric associated with a specific event. This operation returns metric data linked to the event identified by the provided event ID."""
    path: GetMetricForEventRequestPath
    header: GetMetricForEventRequestHeader

# Operation: list_metrics_for_event
class GetMetricIdForEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event for which to retrieve associated metrics.")
class GetMetricIdForEventRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class GetMetricIdForEventRequest(StrictModel):
    """Retrieve all metrics associated with a specific event. Returns a list of related metric identifiers linked to the event."""
    path: GetMetricIdForEventRequestPath
    header: GetMetricIdForEventRequestHeader

# Operation: get_profile_for_event
class GetProfileForEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event whose associated profile you want to retrieve.")
class GetProfileForEventRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified.")
class GetProfileForEventRequest(StrictModel):
    """Retrieve the profile associated with a specific event. Returns the profile data linked to the event identified by the provided event ID."""
    path: GetProfileForEventRequestPath
    header: GetProfileForEventRequestHeader

# Operation: get_profile_id_for_event
class GetProfileIdForEventRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event for which you want to retrieve the associated profile relationship.")
class GetProfileIdForEventRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetProfileIdForEventRequest(StrictModel):
    """Retrieve the profile relationship for a specific event, returning the associated profile ID. This operation allows you to identify which profile is linked to a given event."""
    path: GetProfileIdForEventRequestPath
    header: GetProfileIdForEventRequestHeader

# Operation: list_flows
class GetFlowsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter flows using comparison operators on specific fields. Supports filtering by id (any match), name (contains, starts-with, ends-with, equals), status (equals), archived status (equals), creation/update timestamps (equals, greater-than, greater-or-equal, less-than, less-or-equal), and trigger_type (equals). See API documentation for filter syntax.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of flows to return per page. Must be between 1 and 50, defaults to 50.", ge=1, le=50)
class GetFlowsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15.")
class GetFlowsRequest(StrictModel):
    """Retrieve all flows in an account with cursor-based pagination. Returns up to 50 flows per request, filterable by multiple criteria including name, status, and timestamps."""
    query: GetFlowsRequestQuery | None = None
    header: GetFlowsRequestHeader

# Operation: get_flow
class GetFlowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow to retrieve.")
class GetFlowRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetFlowRequest(StrictModel):
    """Retrieve a specific flow by its ID. Returns the complete flow definition and configuration for the given flow identifier."""
    path: GetFlowRequestPath
    header: GetFlowRequestHeader

# Operation: update_flow_status
class UpdateFlowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow to update (e.g., XVTP5Q).")
class UpdateFlowRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15).")
class UpdateFlowRequestBodyDataAttributes(StrictModel):
    status: str = Field(default=..., validation_alias="status", serialization_alias="status", description="The target status for the flow: 'draft' for unpublished changes, 'manual' for manual execution mode, or 'live' for active production status.")
class UpdateFlowRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow being updated; must match the flow ID in the path parameter.")
    type_: Literal["flow"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'flow'.")
    attributes: UpdateFlowRequestBodyDataAttributes
class UpdateFlowRequestBody(StrictModel):
    data: UpdateFlowRequestBodyData
class UpdateFlowRequest(StrictModel):
    """Update the status of a flow and all its associated actions. The flow can be transitioned to draft, manual, or live status."""
    path: UpdateFlowRequestPath
    header: UpdateFlowRequestHeader
    body: UpdateFlowRequestBody

# Operation: delete_flow
class DeleteFlowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow to delete (e.g., XVTP5Q).")
class DeleteFlowRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specify the revision to ensure compatibility with the intended API version.")
class DeleteFlowRequest(StrictModel):
    """Permanently delete a flow by its ID. This operation requires the flow's current revision to ensure safe deletion and prevent accidental overwrites in concurrent scenarios."""
    path: DeleteFlowRequestPath
    header: DeleteFlowRequestHeader

# Operation: get_flow_action
class GetFlowActionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow action to retrieve.")
class GetFlowActionRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetFlowActionRequest(StrictModel):
    """Retrieve a specific flow action by its ID. Returns the complete flow action details including configuration and metadata."""
    path: GetFlowActionRequestPath
    header: GetFlowActionRequestHeader

# Operation: get_flow_message
class GetFlowMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow message to retrieve.")
class GetFlowMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetFlowMessageRequest(StrictModel):
    """Retrieve a specific flow message by its ID. Returns the complete message details from the associated flow."""
    path: GetFlowMessageRequestPath
    header: GetFlowMessageRequestHeader

# Operation: list_actions_for_flow
class GetActionsForFlowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow for which to retrieve associated actions.")
class GetActionsForFlowRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by action properties. Supports filtering on: id (any operator), action_type (any/equals), status (equals), and created/updated timestamps (equals, greater-or-equal, greater-than, less-or-equal, less-than operators). See API documentation for filter syntax details.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of actions to return per page. Must be between 1 and 50, defaults to 50.", ge=1, le=50)
class GetActionsForFlowRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15.")
class GetActionsForFlowRequest(StrictModel):
    """Retrieve all flow actions associated with a specific flow. Results are paginated with a maximum of 50 actions per request using cursor-based pagination."""
    path: GetActionsForFlowRequestPath
    query: GetActionsForFlowRequestQuery | None = None
    header: GetActionsForFlowRequestHeader

# Operation: list_action_ids_for_flow
class GetActionIdsForFlowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow for which to retrieve associated actions.")
class GetActionIdsForFlowRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by action properties. Supports filtering on: id (any match), action_type (any or exact match), status (exact match), and created/updated timestamps (exact match or comparison operators). See API documentation for filter syntax.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of results to return per page. Must be between 1 and 50, defaults to 50.", ge=1, le=50)
class GetActionIdsForFlowRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15.")
class GetActionIdsForFlowRequest(StrictModel):
    """Retrieve all action IDs associated with a specific flow. Returns up to 100 results per request with cursor-based pagination support."""
    path: GetActionIdsForFlowRequestPath
    query: GetActionIdsForFlowRequestQuery | None = None
    header: GetActionIdsForFlowRequestHeader

# Operation: get_tags_for_flow
class GetTagsForFlowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow for which to retrieve associated tags.")
class GetTagsForFlowRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetTagsForFlowRequest(StrictModel):
    """Retrieve all tags associated with a specific flow. Returns a collection of tags linked to the flow identified by the provided ID."""
    path: GetTagsForFlowRequestPath
    header: GetTagsForFlowRequestHeader

# Operation: list_tag_ids_for_flow
class GetTagIdsForFlowRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow whose associated tags you want to retrieve.")
class GetTagIdsForFlowRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetTagIdsForFlowRequest(StrictModel):
    """Retrieve all tag IDs associated with a specific flow. Returns a collection of tag identifiers linked to the given flow resource."""
    path: GetTagIdsForFlowRequestPath
    header: GetTagIdsForFlowRequestHeader

# Operation: get_flow_for_flow_action
class GetFlowForFlowActionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow action for which to retrieve the associated flow.")
class GetFlowForFlowActionRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). This parameter controls which version of the API contract is used for the request.")
class GetFlowForFlowActionRequest(StrictModel):
    """Retrieves the flow associated with a specific flow action by its ID. This operation requires the flows:read scope and is subject to rate limits of 3 requests per second (burst) and 60 requests per minute (steady state)."""
    path: GetFlowForFlowActionRequestPath
    header: GetFlowForFlowActionRequestHeader

# Operation: get_flow_relationship_for_flow_action
class GetFlowIdForFlowActionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow action for which to retrieve the associated flow.")
class GetFlowIdForFlowActionRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetFlowIdForFlowActionRequest(StrictModel):
    """Retrieve the flow associated with a specific flow action by its ID. Returns the flow relationship data for the given action."""
    path: GetFlowIdForFlowActionRequestPath
    header: GetFlowIdForFlowActionRequestHeader

# Operation: list_flow_action_messages
class GetFlowActionMessagesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow action for which to retrieve associated messages.")
class GetFlowActionMessagesRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by message properties. Supports filtering on id (any operator), name (contains, ends-with, equals, starts-with), created timestamp, and updated timestamp (all timestamp filters support equals, greater-than, greater-or-equal, less-than, less-or-equal operators).")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of messages to return per page. Must be between 1 and 50, defaults to 50.", ge=1, le=50)
class GetFlowActionMessagesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15.")
class GetFlowActionMessagesRequest(StrictModel):
    """Retrieve all flow messages associated with a specific flow action. Returns up to 50 messages per request with cursor-based pagination support."""
    path: GetFlowActionMessagesRequestPath
    query: GetFlowActionMessagesRequestQuery | None = None
    header: GetFlowActionMessagesRequestHeader

# Operation: list_message_ids_for_flow_action
class GetMessageIdsForFlowActionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow action for which to retrieve associated message relationships.")
class GetMessageIdsForFlowActionRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by message properties. Supports filtering on `name` (contains, ends-with, equals, starts-with), `created` (equals, greater-or-equal, greater-than, less-or-equal, less-than), and `updated` (equals, greater-or-equal, greater-than, less-or-equal, less-than) fields.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of message relationships to return per page. Must be between 1 and 50, defaults to 50.", ge=1, le=50)
class GetMessageIdsForFlowActionRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15.")
class GetMessageIdsForFlowActionRequest(StrictModel):
    """Retrieve all flow message IDs associated with a specific flow action. Results are paginated with a maximum of 50 relationships per request using cursor-based pagination."""
    path: GetMessageIdsForFlowActionRequestPath
    query: GetMessageIdsForFlowActionRequestQuery | None = None
    header: GetMessageIdsForFlowActionRequestHeader

# Operation: get_flow_action_for_message
class GetActionForFlowMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow message for which to retrieve the associated flow action.")
class GetActionForFlowMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetActionForFlowMessageRequest(StrictModel):
    """Retrieve the flow action associated with a specific flow message. This operation returns the action configuration that should be executed for the given message within a flow."""
    path: GetActionForFlowMessageRequestPath
    header: GetActionForFlowMessageRequestHeader

# Operation: get_flow_action_for_flow_message
class GetActionIdForFlowMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow message for which to retrieve the associated flow action relationship.")
class GetActionIdForFlowMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetActionIdForFlowMessageRequest(StrictModel):
    """Retrieve the flow action relationship associated with a specific flow message. This returns the relationship link to the flow action that governs the behavior of the given flow message."""
    path: GetActionIdForFlowMessageRequestPath
    header: GetActionIdForFlowMessageRequestHeader

# Operation: get_template_for_flow_message
class GetTemplateForFlowMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow message for which to retrieve the associated template.")
class GetTemplateForFlowMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetTemplateForFlowMessageRequest(StrictModel):
    """Retrieve the template associated with a specific flow message. Returns the template configuration used by the flow message."""
    path: GetTemplateForFlowMessageRequestPath
    header: GetTemplateForFlowMessageRequestHeader

# Operation: get_template_id_for_flow_message
class GetTemplateIdForFlowMessageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the flow message for which to retrieve the associated template ID.")
class GetTemplateIdForFlowMessageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use for this request.")
class GetTemplateIdForFlowMessageRequest(StrictModel):
    """Retrieves the ID of the template associated with a specific flow message. This operation returns the relationship between a flow message and its related template."""
    path: GetTemplateIdForFlowMessageRequestPath
    header: GetTemplateIdForFlowMessageRequestHeader

# Operation: list_forms
class GetFormsRequestQuery(StrictModel):
    fields_form: list[Literal["ab_test", "created_at", "name", "status", "updated_at"]] | None = Field(default=None, validation_alias="fields[form]", serialization_alias="fields[form]", description="Specify which form fields to include in the response using sparse fieldsets for optimized data retrieval.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter forms by id, name, ab_test status, creation/update timestamps, or status. Supports operators like equals, contains, any, and temporal comparisons (greater-than, less-than, etc.).")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of forms to return per page. Must be between 1 and 100 items; defaults to 20.", ge=1, le=100)
class GetFormsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Required for version compatibility.")
class GetFormsRequest(StrictModel):
    """Retrieve all forms in an account with optional filtering, field selection, and pagination. Supports filtering by form properties like name, status, and timestamps."""
    query: GetFormsRequestQuery | None = None
    header: GetFormsRequestHeader

# Operation: create_form
class CreateFormRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class CreateFormRequestBodyDataAttributesDefinition(StrictModel):
    versions: list[Version] = Field(default=..., validation_alias="versions", serialization_alias="versions", description="An array of form versions to associate with this form. Specify the versions in the order they should be applied or referenced.")
class CreateFormRequestBodyDataAttributes(StrictModel):
    status: Literal["draft", "live"] = Field(default=..., validation_alias="status", serialization_alias="status", description="The initial status of the form: either 'draft' for unpublished forms or 'live' for published forms.")
    ab_test: bool = Field(default=..., validation_alias="ab_test", serialization_alias="ab_test", description="A boolean flag indicating whether this form has an A/B test configured. Set to true to enable A/B testing for this form.")
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The display name of the form. Use a descriptive name that identifies the form's purpose (e.g., 'Cyber Monday Deals').")
    definition: CreateFormRequestBodyDataAttributesDefinition
class CreateFormRequestBodyData(StrictModel):
    type_: Literal["form"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'form' for this operation.")
    attributes: CreateFormRequestBodyDataAttributes
class CreateFormRequestBody(StrictModel):
    """Creates a Form from parameters"""
    data: CreateFormRequestBodyData
class CreateFormRequest(StrictModel):
    """Create a new form with specified configuration, including versioning, status, and optional A/B testing setup. The form will be created in the specified status (draft or live) and can be configured for A/B testing."""
    header: CreateFormRequestHeader
    body: CreateFormRequestBody

# Operation: get_form
class GetFormRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form to retrieve (e.g., 'Y6nRLr').")
class GetFormRequestQuery(StrictModel):
    fields_form: list[Literal["ab_test", "created_at", "definition", "definition.versions", "name", "status", "updated_at"]] | None = Field(default=None, validation_alias="fields[form]", serialization_alias="fields[form]", description="Optional sparse fieldset to limit returned form fields. See API documentation for supported field names and filtering syntax.")
class GetFormRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format, with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request.")
class GetFormRequest(StrictModel):
    """Retrieve a specific form by its ID. Use optional field filtering to customize the response payload."""
    path: GetFormRequestPath
    query: GetFormRequestQuery | None = None
    header: GetFormRequestHeader

# Operation: delete_form
class DeleteFormRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form to delete (e.g., 'Y6nRLr')")
class DeleteFormRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)")
class DeleteFormRequest(StrictModel):
    """Permanently delete a form by its ID. This operation requires the form ID and API revision to be specified."""
    path: DeleteFormRequestPath
    header: DeleteFormRequestHeader

# Operation: get_form_version
class GetFormVersionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form version to retrieve (e.g., '1234567').")
class GetFormVersionRequestQuery(StrictModel):
    fields_form_version: list[Literal["ab_test", "ab_test.variation_name", "created_at", "form_type", "status", "updated_at", "variation_name"]] | None = Field(default=None, validation_alias="fields[form-version]", serialization_alias="fields[form-version]", description="Optional sparse fieldset to limit returned fields for the form-version resource. Reduces response payload by selecting only needed fields.")
class GetFormVersionRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetFormVersionRequest(StrictModel):
    """Retrieve a specific form version by its ID. Use optional field filtering to customize the response payload."""
    path: GetFormVersionRequestPath
    query: GetFormVersionRequestQuery | None = None
    header: GetFormVersionRequestHeader

# Operation: list_versions_for_form
class GetVersionsForFormRequestPath(StrictModel):
    id_: str | None = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form whose versions you want to retrieve.")
class GetVersionsForFormRequestQuery(StrictModel):
    fields_form_version: list[Literal["ab_test", "ab_test.variation_name", "created_at", "form_type", "status", "updated_at", "variation_name"]] | None = Field(default=None, validation_alias="fields[form-version]", serialization_alias="fields[form-version]", description="Specify which form-version fields to include in the response to reduce payload size. Omit to return all fields.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by form type (popup, embedded, etc.), status, or creation/update timestamps. Supports equality checks and date range comparisons (greater than, less than, etc.).")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of results per page for pagination. Defaults to 20, with a range of 1 to 100 results.", ge=1, le=100)
class GetVersionsForFormRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15.")
class GetVersionsForFormRequest(StrictModel):
    """Retrieve all versions of a specific form, with optional filtering by form type, status, or date range, and support for sparse fieldsets and pagination."""
    path: GetVersionsForFormRequestPath
    query: GetVersionsForFormRequestQuery | None = None
    header: GetVersionsForFormRequestHeader

# Operation: list_version_ids_for_form
class GetVersionIdsForFormRequestPath(StrictModel):
    id_: str | None = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form to retrieve versions for.")
class GetVersionIdsForFormRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by form type (any or equals), status (equals), or timestamps (created_at/updated_at with greater-than, greater-or-equal, less-than, less-or-equal operators). See API documentation for filter syntax.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of results per page. Must be between 1 and 100, defaults to 20.", ge=1, le=100)
class GetVersionIdsForFormRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15.")
class GetVersionIdsForFormRequest(StrictModel):
    """Retrieve the version IDs for a specific form. Supports filtering by form type, status, and creation/update timestamps, with pagination support."""
    path: GetVersionIdsForFormRequestPath
    query: GetVersionIdsForFormRequestQuery | None = None
    header: GetVersionIdsForFormRequestHeader

# Operation: get_form_for_form_version
class GetFormForFormVersionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form version you want to retrieve the form for (e.g., '1234567').")
class GetFormForFormVersionRequestQuery(StrictModel):
    fields_form: list[Literal["ab_test", "created_at", "name", "status", "updated_at"]] | None = Field(default=None, validation_alias="fields[form]", serialization_alias="fields[form]", description="Optional sparse fieldset to limit which form fields are returned in the response. Specify an array of field names to include only those fields in the result.")
class GetFormForFormVersionRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetFormForFormVersionRequest(StrictModel):
    """Retrieve the form associated with a specific form version. Use this to access the complete form definition linked to a particular version."""
    path: GetFormForFormVersionRequestPath
    query: GetFormForFormVersionRequestQuery | None = None
    header: GetFormForFormVersionRequestHeader

# Operation: get_form_id_for_form_version
class GetFormIdForFormVersionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form version for which you want to retrieve the associated form ID.")
class GetFormIdForFormVersionRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetFormIdForFormVersionRequest(StrictModel):
    """Retrieve the ID of the form associated with a specific form version. This operation returns the relationship between a form version and its parent form."""
    path: GetFormIdForFormVersionRequestPath
    header: GetFormIdForFormVersionRequestHeader

# Operation: list_images
class GetImagesRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results using field-specific operators. Supports filtering by ID (any/equals), updated_at (comparison operators), format (any/equals), name (text matching), size (numeric comparison), and hidden status (any/equals). Provide filter expressions in the format: operator(field,'value').")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of images to return per page. Defaults to 20 results; minimum is 1, maximum is 100.", ge=1, le=100)
class GetImagesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15.")
class GetImagesRequest(StrictModel):
    """Retrieve all images in your account with optional filtering and pagination. Supports filtering by ID, update date, format, name, size, and visibility status."""
    query: GetImagesRequestQuery | None = None
    header: GetImagesRequestHeader

# Operation: import_image_from_url
class UploadImageFromUrlRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class UploadImageFromUrlRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="Optional display name for the imported image. If omitted, the filename from the URL will be used. If the name matches an existing image, a numeric suffix will be automatically appended to ensure uniqueness.")
    import_from_url: str = Field(default=..., validation_alias="import_from_url", serialization_alias="import_from_url", description="The source URL or base64-encoded data URI for the image to import. Accepts standard HTTP/HTTPS URLs or data URIs in the format data:image/[format];base64,[encoded_data]. Supported formats are JPEG, PNG, and GIF, with a maximum file size of 5MB.")
    hidden: bool | None = Field(default=None, validation_alias="hidden", serialization_alias="hidden", description="Optional flag to exclude this image from the asset library UI. When true, the image is stored but not displayed in browsable asset lists. Defaults to false (image is visible).")
class UploadImageFromUrlRequestBodyData(StrictModel):
    type_: Literal["image"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier. Must be set to 'image' for this operation.")
    attributes: UploadImageFromUrlRequestBodyDataAttributes
class UploadImageFromUrlRequestBody(StrictModel):
    data: UploadImageFromUrlRequestBodyData
class UploadImageFromUrlRequest(StrictModel):
    """Import an image into your asset library from a publicly accessible URL or base64-encoded data URI. Supports JPEG, PNG, and GIF formats up to 5MB in size."""
    header: UploadImageFromUrlRequestHeader
    body: UploadImageFromUrlRequestBody

# Operation: get_image
class GetImageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the image to retrieve (e.g., '7'). This ID must correspond to an existing image in the system.")
class GetImageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision to use for this request, specified in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). This ensures compatibility with specific API versions.")
class GetImageRequest(StrictModel):
    """Retrieve a specific image by its ID. Returns the image metadata and content for the requested image resource."""
    path: GetImageRequestPath
    header: GetImageRequestHeader

# Operation: update_image
class UpdateImageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the image to update (e.g., '7')")
class UpdateImageRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)")
class UpdateImageRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="A display name for the image; optional and can be any string value")
    hidden: bool | None = Field(default=None, validation_alias="hidden", serialization_alias="hidden", description="Controls image visibility in the asset library; when true, the image is hidden from the library view")
class UpdateImageRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the image being updated; must match the ID in the path parameter (e.g., '7')")
    type_: Literal["image"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type; must be set to 'image'")
    attributes: UpdateImageRequestBodyDataAttributes | None = None
class UpdateImageRequestBody(StrictModel):
    data: UpdateImageRequestBodyData
class UpdateImageRequest(StrictModel):
    """Update an image's metadata, including its name and visibility settings. Requires the image ID and API revision to be specified."""
    path: UpdateImageRequestPath
    header: UpdateImageRequestHeader
    body: UpdateImageRequestBody

# Operation: create_image_from_file
class UploadImageFromFileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15).")
class UploadImageFromFileRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The image file to upload as binary data. Supported formats: JPEG, PNG, GIF. Maximum file size is 5MB.", json_schema_extra={'format': 'binary'})
    name: str | None = Field(default=None, description="Optional name for the image. If not provided, defaults to the original filename. If the name matches an existing image, a numeric suffix will be automatically added.")
    hidden: bool | None = Field(default=None, description="If true, the image will be hidden from the asset library. Defaults to false.")
class UploadImageFromFileRequest(StrictModel):
    """Upload an image file to create a new image asset. Supports JPEG, PNG, and GIF formats up to 5MB. For importing images from URLs or data URIs, use the Upload Image From URL endpoint instead."""
    header: UploadImageFromFileRequestHeader
    body: UploadImageFromFileRequestBody

# Operation: list_lists
class GetListsRequestQuery(StrictModel):
    fields_list: list[Literal["created", "name", "opt_in_process", "updated"]] | None = Field(default=None, validation_alias="fields[list]", serialization_alias="fields[list]", description="Specify which list fields to include in the response for sparse fieldset optimization. Reduces payload size by returning only requested fields.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter lists by name, id, creation date, or last update date. Supports exact matching for name and id, or date range queries using greater-than operators. Use the format: operator(field,[values]).")
class GetListsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API version in YYYY-MM-DD format (e.g., 2026-01-15). Defaults to 2026-01-15 if not specified.")
class GetListsRequest(StrictModel):
    """Retrieve all lists in your account with optional filtering and field selection. Results are paginated with a maximum of 10 lists per page."""
    query: GetListsRequestQuery | None = None
    header: GetListsRequestHeader

# Operation: create_list
class CreateListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this operation.")
class CreateListRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A descriptive name for the list to help identify it in your account (e.g., 'Newsletter', 'Product Updates'). Used for display and organization purposes.")
    opt_in_process: Literal["double_opt_in", "single_opt_in"] | None = Field(default=None, validation_alias="opt_in_process", serialization_alias="opt_in_process", description="The subscriber opt-in verification method for this list: 'double_opt_in' requires confirmation via email, while 'single_opt_in' adds subscribers immediately. If not specified, your account's default opt-in process will be used.")
class CreateListRequestBodyData(StrictModel):
    type_: Literal["list"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type being created. Must be set to 'list' for this operation.")
    attributes: CreateListRequestBodyDataAttributes
class CreateListRequestBody(StrictModel):
    data: CreateListRequestBodyData
class CreateListRequest(StrictModel):
    """Create a new mailing list for managing subscribers. The list will be configured with your specified name and opt-in process preference."""
    header: CreateListRequestHeader
    body: CreateListRequestBody

# Operation: get_list
class GetListRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the list, generated by Klaviyo (e.g., 'Y6nRLr').")
class GetListRequestQuery(StrictModel):
    fields_list: list[Literal["created", "name", "opt_in_process", "profile_count", "updated"]] | None = Field(default=None, validation_alias="fields[list]", serialization_alias="fields[list]", description="Optional array of field names to include in the response for sparse fieldsets. Omit to return all default fields. See API documentation for available fields.")
class GetListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request.")
class GetListRequest(StrictModel):
    """Retrieve a specific list by its ID. Use optional field selection to customize the response payload and control rate limit impact."""
    path: GetListRequestPath
    query: GetListRequestQuery | None = None
    header: GetListRequestHeader

# Operation: update_list
class UpdateListRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the list to update, generated by Klaviyo (e.g., 'Y6nRLr').")
class UpdateListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified.")
class UpdateListRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="A descriptive name for the list to help identify it (e.g., 'Newsletter'). Optional field.")
    opt_in_process: Literal["double_opt_in", "single_opt_in"] | None = Field(default=None, validation_alias="opt_in_process", serialization_alias="opt_in_process", description="The opt-in process type for this list: 'double_opt_in' requires confirmation, while 'single_opt_in' adds subscribers immediately. Optional field.")
class UpdateListRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the list being updated in the request body. Must match the ID in the URL path.")
    type_: Literal["list"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'list' for this operation.")
    attributes: UpdateListRequestBodyDataAttributes | None = None
class UpdateListRequestBody(StrictModel):
    data: UpdateListRequestBodyData
class UpdateListRequest(StrictModel):
    """Update a list's name and opt-in process settings. Requires the list ID in both the URL path and request body, along with the API revision date."""
    path: UpdateListRequestPath
    header: UpdateListRequestHeader
    body: UpdateListRequestBody

# Operation: delete_list
class DeleteListRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the list to delete, generated by Klaviyo (e.g., 'Y6nRLr').")
class DeleteListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified.")
class DeleteListRequest(StrictModel):
    """Permanently delete a list by its ID. This action cannot be undone and will remove the list and all associated data."""
    path: DeleteListRequestPath
    header: DeleteListRequestHeader

# Operation: list_tags_for_list
class GetTagsForListRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the list, generated by Klaviyo (e.g., 'Y6nRLr').")
class GetTagsForListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class GetTagsForListRequest(StrictModel):
    """Retrieve all tags associated with a specific list. Returns a collection of tags linked to the given list ID."""
    path: GetTagsForListRequestPath
    header: GetTagsForListRequestHeader

# Operation: list_tag_ids_for_list
class GetTagIdsForListRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the list, generated by Klaviyo (e.g., 'Y6nRLr').")
class GetTagIdsForListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetTagIdsForListRequest(StrictModel):
    """Retrieve all tags associated with a specific list. Returns tag IDs that are linked to the given list."""
    path: GetTagIdsForListRequestPath
    header: GetTagIdsForListRequestHeader

# Operation: list_profiles_for_list
class GetProfilesForListRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the list (generated by Klaviyo). Example format: 'Y6nRLr'.")
class GetProfilesForListRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter profiles by email, phone number, push token, or join date. Supports exact matching and range operators (greater-than, less-than, etc.) for dates. Use the format specified in the API filtering guide.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of profiles to return per page. Must be between 1 and 100. Defaults to 20 if not specified.", ge=1, le=100)
class GetProfilesForListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (e.g., 2026-01-15). Defaults to the latest version if not specified.")
class GetProfilesForListRequest(StrictModel):
    """Retrieve all profiles within a specific list. Optionally filter by email, phone number, push token, or group join date, and sort results by join date in ascending or descending order."""
    path: GetProfilesForListRequestPath
    query: GetProfilesForListRequestQuery | None = None
    header: GetProfilesForListRequestHeader

# Operation: list_profile_ids_for_list
class GetProfileIdsForListRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the list. This is a Klaviyo-generated ID (e.g., 'Y6nRLr').")
class GetProfileIdsForListRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter to narrow results by profile attributes. Supports filtering by email, phone number, push token, Klaviyo ID (_kx), or group join date. Use operators like 'equals', 'any', 'greater-than', or 'less-than' depending on the field. See API documentation for filter syntax.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of results per page. Must be between 1 and 100. Defaults to 20 if not specified.", ge=1, le=100)
class GetProfileIdsForListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (e.g., '2026-01-15'). Defaults to the latest version if not specified.")
class GetProfileIdsForListRequest(StrictModel):
    """Retrieve the profile IDs that are members of a specific list. Use filtering to narrow results by email, phone number, push token, or other profile attributes, and pagination to manage large result sets."""
    path: GetProfileIdsForListRequestPath
    query: GetProfileIdsForListRequestQuery | None = None
    header: GetProfileIdsForListRequestHeader

# Operation: add_profiles_to_list
class AddProfilesToListRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the list to which profiles will be added.")
class AddProfilesToListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class AddProfilesToListRequestBody(StrictModel):
    data: list[AddProfilesToListBodyDataItem] = Field(default=..., description="Array of profile objects to add to the list. Maximum 1000 profiles per request. Order is not significant.")
class AddProfilesToListRequest(StrictModel):
    """Add one or more profiles to a list. Accepts up to 1000 profiles per request. For granting email or SMS marketing consent, use the Subscribe Profiles endpoint instead."""
    path: AddProfilesToListRequestPath
    header: AddProfilesToListRequestHeader
    body: AddProfilesToListRequestBody

# Operation: remove_profiles_from_list
class RemoveProfilesFromListRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the list from which profiles will be removed.")
class RemoveProfilesFromListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified.")
class RemoveProfilesFromListRequestBody(StrictModel):
    data: list[RemoveProfilesFromListBodyDataItem] = Field(default=..., description="An array of profiles to remove from the list. Supports up to 1000 profiles per request. Each item should contain the profile identifier in the format expected by the API.")
class RemoveProfilesFromListRequest(StrictModel):
    """Remove one or more profiles from a marketing list. Removed profiles will no longer receive marketing communications from that list, but their overall consent and subscription status remain unchanged."""
    path: RemoveProfilesFromListRequestPath
    header: RemoveProfilesFromListRequestHeader
    body: RemoveProfilesFromListRequestBody

# Operation: list_flows_triggered_by_list
class GetFlowsTriggeredByListRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the list (generated by Klaviyo) for which you want to find associated flow triggers.")
class GetFlowsTriggeredByListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified.")
class GetFlowsTriggeredByListRequest(StrictModel):
    """Retrieve all automation flows that are configured to trigger when the specified list is used as a trigger source. This helps identify which workflows depend on a particular list."""
    path: GetFlowsTriggeredByListRequestPath
    header: GetFlowsTriggeredByListRequestHeader

# Operation: list_flow_trigger_ids_for_list
class GetIdsForFlowsTriggeredByListRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the list, generated by Klaviyo (e.g., 'Y6nRLr'). This ID specifies which list's flow triggers you want to retrieve.")
class GetIdsForFlowsTriggeredByListRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetIdsForFlowsTriggeredByListRequest(StrictModel):
    """Retrieve the IDs of all flows that are triggered by a specific list. This helps identify which automation workflows depend on a given list as their trigger source."""
    path: GetIdsForFlowsTriggeredByListRequestPath
    header: GetIdsForFlowsTriggeredByListRequestHeader

# Operation: list_metrics
class GetMetricsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter metrics by integration name or category using equality operators. Specify as a filter expression (e.g., equals(integration.name,'value') or equals(integration.category,'value')).")
class GetMetricsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetMetricsRequest(StrictModel):
    """Retrieve all metrics in your account with optional filtering by integration name or category. Returns up to 200 results per page."""
    query: GetMetricsRequestQuery | None = None
    header: GetMetricsRequestHeader

# Operation: get_metric
class GetMetricRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the metric to retrieve.")
class GetMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class GetMetricRequest(StrictModel):
    """Retrieve a specific metric by its ID. Returns the metric details for the specified metric identifier."""
    path: GetMetricRequestPath
    header: GetMetricRequestHeader

# Operation: get_metric_property
class GetMetricPropertyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the metric property to retrieve (UUID format).")
class GetMetricPropertyRequestQuery(StrictModel):
    fields_metric_property: list[Literal["inferred_type", "label", "property", "sample_values"]] | None = Field(default=None, validation_alias="fields[metric-property]", serialization_alias="fields[metric-property]", description="Optional sparse fieldset to limit the response to specific metric property fields. Specify which fields to include in the response to optimize payload size.")
class GetMetricPropertyRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetMetricPropertyRequest(StrictModel):
    """Retrieve a specific metric property by its ID. Use this to fetch detailed information about a metric property for inspection or integration purposes."""
    path: GetMetricPropertyRequestPath
    query: GetMetricPropertyRequestQuery | None = None
    header: GetMetricPropertyRequestHeader

# Operation: list_custom_metrics
class GetCustomMetricsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class GetCustomMetricsRequest(StrictModel):
    """Retrieve all custom metrics configured in your account. This operation requires the metrics:read scope and is subject to rate limits of 3 requests per second (burst) and 60 requests per minute (steady state)."""
    header: GetCustomMetricsRequestHeader

# Operation: create_custom_metric
class CreateCustomMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class CreateCustomMetricRequestBodyDataAttributesDefinition(StrictModel):
    aggregation_method: Literal["count", "value"] = Field(default=..., validation_alias="aggregation_method", serialization_alias="aggregation_method", description="Aggregation method determining how metric measurements are combined. Use 'value' for revenue-based metrics (like Placed Order) or 'count' for conversion-based metrics (like Active on Site).")
    metric_groups: list[CustomMetricGroup] = Field(default=..., validation_alias="metric_groups", serialization_alias="metric_groups", description="Array of metric groups to associate with this custom metric. Specifies the grouping categories for organizing metric data.")
class CreateCustomMetricRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="Unique name for the custom metric within your account. Duplicate names will be rejected with a 400 error.")
    definition: CreateCustomMetricRequestBodyDataAttributesDefinition
class CreateCustomMetricRequestBodyData(StrictModel):
    type_: Literal["custom-metric"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier; must be set to 'custom-metric' for this operation.")
    attributes: CreateCustomMetricRequestBodyDataAttributes
class CreateCustomMetricRequestBody(StrictModel):
    """Create a custom metric."""
    data: CreateCustomMetricRequestBodyData
class CreateCustomMetricRequest(StrictModel):
    """Create a new custom metric for tracking account-specific measurements. Custom metrics require a unique name and aggregation method to define how measurements are combined."""
    header: CreateCustomMetricRequestHeader
    body: CreateCustomMetricRequestBody

# Operation: get_custom_metric
class GetCustomMetricRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom metric to retrieve, formatted as a hexadecimal string.")
class GetCustomMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetCustomMetricRequest(StrictModel):
    """Retrieve a custom metric by its unique identifier. Returns the metric definition and configuration for the specified custom metric ID."""
    path: GetCustomMetricRequestPath
    header: GetCustomMetricRequestHeader

# Operation: update_custom_metric
class UpdateCustomMetricRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom metric to update, formatted as a 32-character hexadecimal string.")
class UpdateCustomMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class UpdateCustomMetricRequestBodyDataAttributesDefinition(StrictModel):
    aggregation_method: Literal["count", "value"] = Field(default=..., validation_alias="aggregation_method", serialization_alias="aggregation_method", description="The aggregation method determines how metric measurements are combined. Use 'value' for revenue-based metrics (e.g., Placed Order) or 'count' for conversion-based metrics (e.g., Active on Site).")
    metric_groups: list[CustomMetricGroup] = Field(default=..., validation_alias="metric_groups", serialization_alias="metric_groups", description="An array of metric group configurations associated with this custom metric. Specify the order and structure of each group as required by your metric definition.")
class UpdateCustomMetricRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name for the custom metric. Names must be unique within your account; attempting to use a duplicate name will result in a 400 error.")
    definition: UpdateCustomMetricRequestBodyDataAttributesDefinition
class UpdateCustomMetricRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom metric being updated; must match the path ID parameter.")
    type_: Literal["custom-metric"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'custom-metric' to indicate this is a custom metric resource.")
    attributes: UpdateCustomMetricRequestBodyDataAttributes
class UpdateCustomMetricRequestBody(StrictModel):
    """Update a custom metric by ID."""
    data: UpdateCustomMetricRequestBodyData
class UpdateCustomMetricRequest(StrictModel):
    """Update an existing custom metric by ID. Modify the metric's name, aggregation method, and metric groups while maintaining the metric's identity and revision."""
    path: UpdateCustomMetricRequestPath
    header: UpdateCustomMetricRequestHeader
    body: UpdateCustomMetricRequestBody

# Operation: delete_custom_metric
class DeleteCustomMetricRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom metric to delete, formatted as a 32-character hexadecimal string.")
class DeleteCustomMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class DeleteCustomMetricRequest(StrictModel):
    """Permanently delete a custom metric by its ID. This operation requires the metrics:write scope and is subject to rate limits of 3 requests per second (burst) or 60 per minute (steady state)."""
    path: DeleteCustomMetricRequestPath
    header: DeleteCustomMetricRequestHeader

# Operation: list_mapped_metrics
class GetMappedMetricsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with an optional suffix. Defaults to 2026-01-15 if not specified.")
class GetMappedMetricsRequest(StrictModel):
    """Retrieve all mapped metrics configured in your account. This operation returns the complete set of metrics that have been mapped for use in your system."""
    header: GetMappedMetricsRequestHeader

# Operation: get_mapped_metric
class GetMappedMetricRequestPath(StrictModel):
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(default=..., validation_alias="id", serialization_alias="id", description="The metric type identifier. Must be one of the supported conversion event types: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product.")
class GetMappedMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetMappedMetricRequest(StrictModel):
    """Retrieve a mapped metric by its identifier. Mapped metrics represent conversion events tracked across your analytics platform, such as revenue, product views, or checkout initiations."""
    path: GetMappedMetricRequestPath
    header: GetMappedMetricRequestHeader

# Operation: update_mapped_metric
class UpdateMappedMetricRequestPath(StrictModel):
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(default=..., validation_alias="id", serialization_alias="id", description="The mapped metric type identifier being updated. Must be one of: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product.")
class UpdateMappedMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15).")
class UpdateMappedMetricRequestBodyDataRelationshipsMetricData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the standard metric to associate with this mapping. Pass null to remove the metric association.")
    type_: Literal["metric"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for the metric relationship. Must be set to 'metric'.")
class UpdateMappedMetricRequestBodyDataRelationshipsMetric(StrictModel):
    data: UpdateMappedMetricRequestBodyDataRelationshipsMetricData
class UpdateMappedMetricRequestBodyDataRelationshipsCustomMetricData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the custom metric to associate with this mapping. Pass null to remove the custom metric association.")
    type_: Literal["custom-metric"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for the custom metric relationship. Must be set to 'custom-metric'.")
class UpdateMappedMetricRequestBodyDataRelationshipsCustomMetric(StrictModel):
    data: UpdateMappedMetricRequestBodyDataRelationshipsCustomMetricData
class UpdateMappedMetricRequestBodyDataRelationships(StrictModel):
    metric: UpdateMappedMetricRequestBodyDataRelationshipsMetric
    custom_metric: UpdateMappedMetricRequestBodyDataRelationshipsCustomMetric = Field(default=..., validation_alias="custom-metric", serialization_alias="custom-metric")
class UpdateMappedMetricRequestBodyData(StrictModel):
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(default=..., validation_alias="id", serialization_alias="id", description="The mapped metric type identifier in the request body. Must match the path ID and be one of: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product.")
    type_: Literal["mapped-metric"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'mapped-metric'.")
    relationships: UpdateMappedMetricRequestBodyDataRelationships
class UpdateMappedMetricRequestBody(StrictModel):
    """Update a mapped metric by ID"""
    data: UpdateMappedMetricRequestBodyData
class UpdateMappedMetricRequest(StrictModel):
    """Update a mapped metric to change its associations with standard or custom metrics. Use null values to unset metric mappings."""
    path: UpdateMappedMetricRequestPath
    header: UpdateMappedMetricRequestHeader
    body: UpdateMappedMetricRequestBody

# Operation: query_metric_aggregates
class QueryMetricAggregatesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15.")
class QueryMetricAggregatesRequestBodyDataAttributes(StrictModel):
    metric_id: str = Field(default=..., validation_alias="metric_id", serialization_alias="metric_id", description="The unique identifier of the metric to aggregate. Example: '0rG4eQ'.")
    measurements: list[Literal["count", "sum_value", "unique"]] = Field(default=..., validation_alias="measurements", serialization_alias="measurements", description="One or more measurement types to calculate, such as 'count', 'unique', or 'sum_value'. Order is preserved in results.")
    interval: Literal["day", "hour", "month", "week"] | None = Field(default=None, validation_alias="interval", serialization_alias="interval", description="Time interval for grouping aggregation results. Supported intervals are hour, day, week, or month. Defaults to day.")
    page_size: int | None = Field(default=None, validation_alias="page_size", serialization_alias="page_size", description="Maximum number of result rows returned per page. Defaults to 500.")
    by: list[Literal["$attributed_channel", "$attributed_flow", "$attributed_message", "$attributed_variation", "$campaign_channel", "$flow", "$flow_channel", "$message", "$message_send_cohort", "$usage_amount", "$value_currency", "$variation", "$variation_send_cohort", "Bot Click", "Bounce Type", "Campaign Name", "Client Canonical", "Client Name", "Client Type", "Email Domain", "Failure Source", "Failure Type", "From Number", "From Phone Region", "Inbox Provider", "List", "Message Name", "Message Type", "Method", "Segment Count", "Subject", "To Number", "To Phone Region", "URL", "form_id"]] | None = Field(default=None, validation_alias="by", serialization_alias="by", description="Optional attributes to partition results by, such as '$message' for message type. Enables multi-dimensional analysis of aggregated data.")
    return_fields: list[str] | None = Field(default=None, validation_alias="return_fields", serialization_alias="return_fields", description="Optional list of fields to include in the response. If omitted, all available fields are returned.")
    filter_: list[str] = Field(default=..., validation_alias="filter", serialization_alias="filter", description="Required list of filter conditions to constrain results. Must include a time range using ISO 8601 format (YYYY-MM-DDTHH:MM:SS.mmmmmm) with 'greater-or-equal' and 'less-than' operators on the 'datetime' field, plus any additional attribute filters.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="IANA timezone for query processing, such as 'America/New_York'. Defaults to UTC. Case-sensitive. Most timezones are supported except Factory, Europe/Kyiv, and Pacific/Kanton.")
class QueryMetricAggregatesRequestBodyData(StrictModel):
    type_: Literal["metric-aggregate"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier. Must be set to 'metric-aggregate'.")
    attributes: QueryMetricAggregatesRequestBodyDataAttributes
class QueryMetricAggregatesRequestBody(StrictModel):
    """Retrieve Metric Aggregations"""
    data: QueryMetricAggregatesRequestBodyData
class QueryMetricAggregatesRequest(StrictModel):
    """Query and aggregate event data for a metric across native Klaviyo metrics, integrations, and custom events. Results can be filtered by time range and grouped by time intervals, event properties, or profile dimensions."""
    header: QueryMetricAggregatesRequestHeader
    body: QueryMetricAggregatesRequestBody

# Operation: list_flows_triggered_by_metric
class GetFlowsTriggeredByMetricRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the metric to query for associated flow triggers.")
class GetFlowsTriggeredByMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetFlowsTriggeredByMetricRequest(StrictModel):
    """Retrieve all workflows that use the specified metric as a trigger condition. This helps identify which flows depend on a particular metric for activation."""
    path: GetFlowsTriggeredByMetricRequestPath
    header: GetFlowsTriggeredByMetricRequestHeader

# Operation: list_flow_ids_triggered_by_metric
class GetIdsForFlowsTriggeredByMetricRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the metric for which to retrieve triggered flows.")
class GetIdsForFlowsTriggeredByMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetIdsForFlowsTriggeredByMetricRequest(StrictModel):
    """Retrieve the IDs of all flows that use the specified metric as their trigger condition. This allows you to identify which flows are dependent on a particular metric."""
    path: GetIdsForFlowsTriggeredByMetricRequestPath
    header: GetIdsForFlowsTriggeredByMetricRequestHeader

# Operation: get_metric_properties
class GetPropertiesForMetricRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the metric to retrieve properties for (e.g., '925e38').")
class GetPropertiesForMetricRequestQuery(StrictModel):
    fields_metric_property: list[Literal["inferred_type", "label", "property", "sample_values"]] | None = Field(default=None, validation_alias="fields[metric-property]", serialization_alias="fields[metric-property]", description="Optional list of specific metric-property fields to include in the response. When omitted, all available fields are returned. See API documentation for available field names.")
class GetPropertiesForMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetPropertiesForMetricRequest(StrictModel):
    """Retrieve all properties associated with a specific metric by its ID. Use optional field filtering to request only specific metric property attributes."""
    path: GetPropertiesForMetricRequestPath
    query: GetPropertiesForMetricRequestQuery | None = None
    header: GetPropertiesForMetricRequestHeader

# Operation: list_property_ids_for_metric
class GetPropertyIdsForMetricRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the metric (e.g., '925e38'). This ID specifies which metric's properties you want to retrieve.")
class GetPropertyIdsForMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specify a revision to ensure consistent API behavior across requests.")
class GetPropertyIdsForMetricRequest(StrictModel):
    """Retrieve the IDs of all metric properties associated with a specific metric. Use this to discover which properties are linked to a metric."""
    path: GetPropertyIdsForMetricRequestPath
    header: GetPropertyIdsForMetricRequestHeader

# Operation: get_metric_for_metric_property
class GetMetricForMetricPropertyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the metric property. Use the metric property ID to look up its associated metric.")
class GetMetricForMetricPropertyRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class GetMetricForMetricPropertyRequest(StrictModel):
    """Retrieve the metric associated with a specific metric property. This operation fetches the metric data linked to the given metric property ID."""
    path: GetMetricForMetricPropertyRequestPath
    header: GetMetricForMetricPropertyRequestHeader

# Operation: get_metric_id_for_metric_property
class GetMetricIdForMetricPropertyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the metric property. Use the metric property ID (a 32-character hexadecimal string) to specify which property's metric relationship you want to retrieve.")
class GetMetricIdForMetricPropertyRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetMetricIdForMetricPropertyRequest(StrictModel):
    """Retrieve the metric ID associated with a specific metric property. This operation resolves the relationship between a metric property and its parent metric."""
    path: GetMetricIdForMetricPropertyRequestPath
    header: GetMetricIdForMetricPropertyRequestHeader

# Operation: get_metrics_for_custom_metric
class GetMetricsForCustomMetricRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom metric. Use the custom metric ID returned when the metric was created or retrieved from a list operation.")
class GetMetricsForCustomMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified, allowing you to control which API version behavior is used.")
class GetMetricsForCustomMetricRequest(StrictModel):
    """Retrieve all metrics associated with a specific custom metric by its ID. This operation allows you to fetch the complete set of metric data points for a given custom metric configuration."""
    path: GetMetricsForCustomMetricRequestPath
    header: GetMetricsForCustomMetricRequestHeader

# Operation: list_metrics_for_custom_metric
class GetMetricIdsForCustomMetricRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom metric. This is a 32-character hexadecimal string that uniquely identifies the custom metric resource.")
class GetMetricIdsForCustomMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified, allowing you to target specific API versions.")
class GetMetricIdsForCustomMetricRequest(StrictModel):
    """Retrieve all metric IDs associated with a specific custom metric. Use this to discover which metrics are linked to a custom metric configuration."""
    path: GetMetricIdsForCustomMetricRequestPath
    header: GetMetricIdsForCustomMetricRequestHeader

# Operation: get_metric_for_mapped_metric
class GetMetricForMappedMetricRequestPath(StrictModel):
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(default=..., validation_alias="id", serialization_alias="id", description="The mapped metric type identifier. Must be one of the predefined metric mapping types: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product.")
class GetMetricForMappedMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetMetricForMappedMetricRequest(StrictModel):
    """Retrieve the metric associated with a specific mapped metric. This operation returns the underlying metric data for a given mapped metric ID, if one exists."""
    path: GetMetricForMappedMetricRequestPath
    header: GetMetricForMappedMetricRequestHeader

# Operation: get_metric_id_for_mapped_metric
class GetMetricIdForMappedMetricRequestPath(StrictModel):
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(default=..., validation_alias="id", serialization_alias="id", description="The type of mapped metric to query. Must be one of the predefined mapping types: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product.")
class GetMetricIdForMappedMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetMetricIdForMappedMetricRequest(StrictModel):
    """Retrieve the metric ID associated with a specific mapped metric. This operation resolves the relationship between a mapped metric and its underlying metric."""
    path: GetMetricIdForMappedMetricRequestPath
    header: GetMetricIdForMappedMetricRequestHeader

# Operation: get_custom_metric_for_mapped_metric
class GetCustomMetricForMappedMetricRequestPath(StrictModel):
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(default=..., validation_alias="id", serialization_alias="id", description="The mapped metric type identifier. Must be one of the predefined event types: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product.")
class GetCustomMetricForMappedMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetCustomMetricForMappedMetricRequest(StrictModel):
    """Retrieve the custom metric associated with a specific mapped metric. Returns the custom metric details if one exists for the given mapped metric ID."""
    path: GetCustomMetricForMappedMetricRequestPath
    header: GetCustomMetricForMappedMetricRequestHeader

# Operation: get_custom_metric_id_for_mapped_metric
class GetCustomMetricIdForMappedMetricRequestPath(StrictModel):
    id_: Literal["added_to_cart", "cancelled_sales", "ordered_product", "refunded_sales", "revenue", "started_checkout", "viewed_product"] = Field(default=..., validation_alias="id", serialization_alias="id", description="The type of metric mapping to query. Must be one of the predefined mapping types: added_to_cart, cancelled_sales, ordered_product, refunded_sales, revenue, started_checkout, or viewed_product.")
class GetCustomMetricIdForMappedMetricRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetCustomMetricIdForMappedMetricRequest(StrictModel):
    """Retrieve the custom metric ID associated with a specific mapped metric. This operation returns the relationship between a mapped metric and its underlying custom metric."""
    path: GetCustomMetricIdForMappedMetricRequestPath
    header: GetCustomMetricIdForMappedMetricRequestHeader

# Operation: list_profiles
class GetProfilesRequestQuery(StrictModel):
    fields_push_token: list[Literal["background", "created", "enablement_status", "metadata", "metadata.app_build", "metadata.app_id", "metadata.app_name", "metadata.app_version", "metadata.device_id", "metadata.device_model", "metadata.environment", "metadata.klaviyo_sdk", "metadata.manufacturer", "metadata.os_name", "metadata.os_version", "metadata.sdk_version", "platform", "recorded_date", "token", "vendor"]] | None = Field(default=None, validation_alias="fields[push-token]", serialization_alias="fields[push-token]", description="Specify which push token fields to include in the response using sparse fieldsets for optimized data retrieval.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter profiles by id, email, phone_number, external_id, _kx identifier, creation/update timestamps, or email subscription and suppression details. Use operators like equals, any, greater-than, and less-than depending on the field.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of profiles to return per page, between 1 and 100 (default: 20).", ge=1, le=100)
class GetProfilesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (required; defaults to 2026-01-15).")
class GetProfilesRequest(StrictModel):
    """Retrieve all profiles in an account with optional filtering, sorting, and enrichment. Supports subscriptions and predictive analytics data via the additional-fields parameter, with different rate limits depending on which enrichments are requested."""
    query: GetProfilesRequestQuery | None = None
    header: GetProfilesRequestHeader

# Operation: create_profile
class CreateProfileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15).")
class CreateProfileRequestBodyDataAttributesLocation(StrictModel):
    address1: str | None = Field(default=None, validation_alias="address1", serialization_alias="address1", description="First line of the street address.")
    address2: str | None = Field(default=None, validation_alias="address2", serialization_alias="address2", description="Second line of the street address (e.g., apartment or suite number).")
    city: str | None = Field(default=None, validation_alias="city", serialization_alias="city", description="City name.")
    country: str | None = Field(default=None, validation_alias="country", serialization_alias="country", description="Country name.")
    latitude: str | None = Field(default=None, validation_alias="latitude", serialization_alias="latitude", description="Latitude coordinate; provide at least four decimal places for precision. Accepts string or number format.")
    longitude: str | None = Field(default=None, validation_alias="longitude", serialization_alias="longitude", description="Longitude coordinate; provide at least four decimal places for precision. Accepts string or number format.")
    region: str | None = Field(default=None, validation_alias="region", serialization_alias="region", description="Region within a country, such as state or province (e.g., NY).")
    zip_: str | None = Field(default=None, validation_alias="zip", serialization_alias="zip", description="Zip or postal code.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="Time zone name using the IANA Time Zone Database (e.g., America/New_York).")
    ip: str | None = Field(default=None, validation_alias="ip", serialization_alias="ip", description="IP address of the individual.")
class CreateProfileRequestBodyDataAttributes(StrictModel):
    email: str | None = Field(default=None, validation_alias="email", serialization_alias="email", description="Individual's email address (e.g., sarah.mason@klaviyo-demo.com).")
    phone_number: str | None = Field(default=None, validation_alias="phone_number", serialization_alias="phone_number", description="Individual's phone number in E.164 format (e.g., +15005550006).")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="Unique identifier to link this Klaviyo profile with an external system such as a point-of-sale platform; format varies by external system.")
    first_name: str | None = Field(default=None, validation_alias="first_name", serialization_alias="first_name", description="Individual's first name.")
    last_name: str | None = Field(default=None, validation_alias="last_name", serialization_alias="last_name", description="Individual's last name.")
    organization: str | None = Field(default=None, validation_alias="organization", serialization_alias="organization", description="Name of the company or organization where the individual works.")
    locale: str | None = Field(default=None, validation_alias="locale", serialization_alias="locale", description="Profile locale in IETF BCP 47 format (e.g., en-US for English-United States).")
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="Individual's job title.")
    image: str | None = Field(default=None, validation_alias="image", serialization_alias="image", description="URL pointing to the profile's image.")
    properties: dict[str, Any] | None = Field(default=None, validation_alias="properties", serialization_alias="properties", description="Custom key-value properties to attach to the profile (e.g., {'pseudonym': 'Dr. Octopus'}).")
    location: CreateProfileRequestBodyDataAttributesLocation | None = None
class CreateProfileRequestBodyData(StrictModel):
    type_: Literal["profile"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Profile resource type; must be set to 'profile'.")
    attributes: CreateProfileRequestBodyDataAttributes | None = None
class CreateProfileRequestBody(StrictModel):
    data: CreateProfileRequestBodyData
class CreateProfileRequest(StrictModel):
    """Create a new customer profile with contact information, location data, and custom properties. Use the `additional-fields` parameter to include subscriptions and predictive analytics in the response."""
    header: CreateProfileRequestHeader
    body: CreateProfileRequestBody

# Operation: get_profile
class GetProfileRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the profile to retrieve.")
class GetProfileRequestQuery(StrictModel):
    fields_list: list[Literal["created", "name", "opt_in_process", "updated"]] | None = Field(default=None, validation_alias="fields[list]", serialization_alias="fields[list]", description="Optional sparse fieldset for list-related profile fields. Specify which fields to include in the response to optimize data transfer.")
    fields_push_token: list[Literal["background", "created", "enablement_status", "metadata", "metadata.app_build", "metadata.app_id", "metadata.app_name", "metadata.app_version", "metadata.device_id", "metadata.device_model", "metadata.environment", "metadata.klaviyo_sdk", "metadata.manufacturer", "metadata.os_name", "metadata.os_version", "metadata.sdk_version", "platform", "recorded_date", "token", "vendor"]] | None = Field(default=None, validation_alias="fields[push-token]", serialization_alias="fields[push-token]", description="Optional sparse fieldset for push-token-related profile fields. Specify which fields to include in the response to optimize data transfer.")
    fields_segment: list[Literal["created", "definition", "definition.condition_groups", "is_active", "is_processing", "is_starred", "name", "updated"]] | None = Field(default=None, validation_alias="fields[segment]", serialization_alias="fields[segment]", description="Optional sparse fieldset for segment-related profile fields. Specify which fields to include in the response to optimize data transfer. Note: Using this parameter reduces rate limits to 1 request per second (burst) and 15 requests per minute (steady).")
class GetProfileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetProfileRequest(StrictModel):
    """Retrieve a profile by ID with optional support for subscriptions and predictive analytics data. Be aware of rate limits that vary based on the `fields` parameters used."""
    path: GetProfileRequestPath
    query: GetProfileRequestQuery | None = None
    header: GetProfileRequestHeader

# Operation: update_profile
class UpdateProfileRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique profile identifier (Klaviyo-generated) that specifies which profile to update.")
class UpdateProfileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15.")
class UpdateProfileRequestBodyDataAttributesLocation(StrictModel):
    address1: str | None = Field(default=None, validation_alias="address1", serialization_alias="address1", description="The first line of the street address.")
    address2: str | None = Field(default=None, validation_alias="address2", serialization_alias="address2", description="The second line of the street address (e.g., apartment or suite number).")
    city: str | None = Field(default=None, validation_alias="city", serialization_alias="city", description="The city name.")
    country: str | None = Field(default=None, validation_alias="country", serialization_alias="country", description="The country name.")
    latitude: str | None = Field(default=None, validation_alias="latitude", serialization_alias="latitude", description="The latitude coordinate; provide at least four decimal places for precision.")
    longitude: str | None = Field(default=None, validation_alias="longitude", serialization_alias="longitude", description="The longitude coordinate; provide at least four decimal places for precision.")
    region: str | None = Field(default=None, validation_alias="region", serialization_alias="region", description="The region within the country, such as a state or province.")
    zip_: str | None = Field(default=None, validation_alias="zip", serialization_alias="zip", description="The postal or zip code.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="The time zone name using the IANA Time Zone Database (e.g., America/New_York).")
    ip: str | None = Field(default=None, validation_alias="ip", serialization_alias="ip", description="The IP address associated with the profile.")
class UpdateProfileRequestBodyDataAttributes(StrictModel):
    email: str | None = Field(default=None, validation_alias="email", serialization_alias="email", description="The individual's email address.")
    phone_number: str | None = Field(default=None, validation_alias="phone_number", serialization_alias="phone_number", description="The individual's phone number in E.164 format (e.g., +1 followed by country and number).")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="A unique identifier from an external system (such as a point-of-sale system) to link this Klaviyo profile with external records.")
    first_name: str | None = Field(default=None, validation_alias="first_name", serialization_alias="first_name", description="The individual's first name.")
    last_name: str | None = Field(default=None, validation_alias="last_name", serialization_alias="last_name", description="The individual's last name.")
    organization: str | None = Field(default=None, validation_alias="organization", serialization_alias="organization", description="The name of the company or organization where the individual works.")
    locale: str | None = Field(default=None, validation_alias="locale", serialization_alias="locale", description="The profile's locale in IETF BCP 47 format (e.g., en-US for English-United States).")
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="The individual's job title.")
    image: str | None = Field(default=None, validation_alias="image", serialization_alias="image", description="A URL pointing to the profile's image.")
    properties: dict[str, Any] | None = Field(default=None, validation_alias="properties", serialization_alias="properties", description="A key-value object containing custom properties assigned to this profile.")
    location: UpdateProfileRequestBodyDataAttributesLocation | None = None
class UpdateProfileRequestBodyDataMetaPatchProperties(StrictModel):
    append: dict[str, Any] | None = Field(default=None, validation_alias="append", serialization_alias="append", description="Append one or more simple values to an existing property array (e.g., add SKUs to a list).")
    unappend: dict[str, Any] | None = Field(default=None, validation_alias="unappend", serialization_alias="unappend", description="Remove one or more simple values from an existing property array (e.g., remove SKUs from a list).")
    unset: str | list[str] | None = Field(default=None, validation_alias="unset", serialization_alias="unset", description="Remove one or more keys (and their values) completely from the properties object.")
class UpdateProfileRequestBodyDataMeta(StrictModel):
    patch_properties: UpdateProfileRequestBodyDataMetaPatchProperties | None = None
class UpdateProfileRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique profile identifier in the request body; must match the path ID.")
    type_: Literal["profile"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type; must be 'profile'.")
    attributes: UpdateProfileRequestBodyDataAttributes | None = None
    meta: UpdateProfileRequestBodyDataMeta | None = None
class UpdateProfileRequestBody(StrictModel):
    data: UpdateProfileRequestBodyData
class UpdateProfileRequest(StrictModel):
    """Update an existing customer profile with new or modified information. Use the `additional-fields` parameter to include subscriptions and predictive analytics data in the response. Setting a field to `null` clears it; omitting a field leaves it unchanged."""
    path: UpdateProfileRequestPath
    header: UpdateProfileRequestHeader
    body: UpdateProfileRequestBody

# Operation: list_bulk_import_profiles_jobs
class GetBulkImportProfilesJobsRequestQuery(StrictModel):
    fields_profile_bulk_import_job: list[Literal["completed_at", "completed_count", "created_at", "expires_at", "failed_count", "started_at", "status", "total_count"]] | None = Field(default=None, validation_alias="fields[profile-bulk-import-job]", serialization_alias="fields[profile-bulk-import-job]", description="Specify which fields to include in the response for each bulk import job. Supports sparse fieldsets to optimize payload size.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status using equality or any-match operators. Supported field: `status` with operators `equals` and `any`.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of jobs to return per page. Must be between 1 and 100, with a default of 20.", ge=1, le=100)
class GetBulkImportProfilesJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15.")
class GetBulkImportProfilesJobsRequest(StrictModel):
    """Retrieve all bulk profile import jobs with optional filtering and pagination. Returns up to 100 jobs per request."""
    query: GetBulkImportProfilesJobsRequestQuery | None = None
    header: GetBulkImportProfilesJobsRequestHeader

# Operation: create_profile_bulk_import_job
class BulkImportProfilesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class BulkImportProfilesRequestBodyDataAttributesProfiles(StrictModel):
    data: list[ProfileUpsertQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of profile objects to import. Each profile can be up to 100KB. The array can contain up to 10,000 profiles per request. Order is preserved during processing.")
class BulkImportProfilesRequestBodyDataAttributes(StrictModel):
    profiles: BulkImportProfilesRequestBodyDataAttributesProfiles
class BulkImportProfilesRequestBodyDataRelationshipsLists(StrictModel):
    data: list[BulkImportProfilesBodyDataRelationshipsListsDataItem] | None = Field(default=None, validation_alias="data", serialization_alias="data", description="Optional array of list identifiers to associate the imported profiles with. Profiles will be added to these lists upon successful import.")
class BulkImportProfilesRequestBodyDataRelationships(StrictModel):
    lists: BulkImportProfilesRequestBodyDataRelationshipsLists | None = None
class BulkImportProfilesRequestBodyData(StrictModel):
    type_: Literal["profile-bulk-import-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier for this operation. Must be set to 'profile-bulk-import-job'.")
    attributes: BulkImportProfilesRequestBodyDataAttributes
    relationships: BulkImportProfilesRequestBodyDataRelationships | None = None
class BulkImportProfilesRequestBody(StrictModel):
    data: BulkImportProfilesRequestBodyData
class BulkImportProfilesRequest(StrictModel):
    """Create a bulk import job to efficiently create or update up to 10,000 profiles in a single request. The job processes profiles asynchronously and supports payloads up to 5MB total (100KB per profile)."""
    header: BulkImportProfilesRequestHeader
    body: BulkImportProfilesRequestBody

# Operation: get_bulk_import_profiles_job
class GetBulkImportProfilesJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk import job to retrieve (format: alphanumeric string).")
class GetBulkImportProfilesJobRequestQuery(StrictModel):
    fields_list: list[Literal["created", "name", "opt_in_process", "updated"]] | None = Field(default=None, validation_alias="fields[list]", serialization_alias="fields[list]", description="Optional list of top-level resource types to include in the response. Specify resource types to retrieve only those fields across all included resources.")
    fields_profile_bulk_import_job: list[Literal["completed_at", "completed_count", "created_at", "expires_at", "failed_count", "started_at", "status", "total_count"]] | None = Field(default=None, validation_alias="fields[profile-bulk-import-job]", serialization_alias="fields[profile-bulk-import-job]", description="Optional list of fields specific to the profile bulk import job resource. Specify field names to retrieve only those attributes for the job.")
class GetBulkImportProfilesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetBulkImportProfilesJobRequest(StrictModel):
    """Retrieve the status and details of a bulk profile import job by its ID. Use this to monitor the progress and results of profile import operations."""
    path: GetBulkImportProfilesJobRequestPath
    query: GetBulkImportProfilesJobRequestQuery | None = None
    header: GetBulkImportProfilesJobRequestHeader

# Operation: list_bulk_suppress_profiles_jobs
class GetBulkSuppressProfilesJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status, list ID, or segment ID using equality operators. Specify filters in the format `field_name=value` (e.g., `status=processing`).")
class GetBulkSuppressProfilesJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkSuppressProfilesJobsRequest(StrictModel):
    """Retrieve the status of all bulk profile suppression jobs. Use filtering to narrow results by job status, list ID, or segment ID."""
    query: GetBulkSuppressProfilesJobsRequestQuery | None = None
    header: GetBulkSuppressProfilesJobsRequestHeader

# Operation: create_profile_suppression_bulk_job
class BulkSuppressProfilesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15.")
class BulkSuppressProfilesRequestBodyDataRelationshipsListData(StrictModel):
    type_: Literal["list"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier for list-based suppression. Must be set to 'list' when suppressing by list membership.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="ID of the list whose current members should be suppressed. Provide this to suppress all profiles in a specific list, or use the email addresses array for individual suppressions.")
class BulkSuppressProfilesRequestBodyDataRelationshipsList(StrictModel):
    data: BulkSuppressProfilesRequestBodyDataRelationshipsListData
class BulkSuppressProfilesRequestBodyDataRelationshipsSegmentData(StrictModel):
    type_: Literal["segment"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier for segment-based suppression. Must be set to 'segment' when suppressing by segment membership.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="ID of the segment whose current members should be suppressed. Provide this to suppress all profiles in a specific segment, or use the email addresses array for individual suppressions.")
class BulkSuppressProfilesRequestBodyDataRelationshipsSegment(StrictModel):
    data: BulkSuppressProfilesRequestBodyDataRelationshipsSegmentData
class BulkSuppressProfilesRequestBodyDataRelationships(StrictModel):
    list_: BulkSuppressProfilesRequestBodyDataRelationshipsList = Field(default=..., validation_alias="list", serialization_alias="list")
    segment: BulkSuppressProfilesRequestBodyDataRelationshipsSegment
class BulkSuppressProfilesRequestBodyDataAttributesProfiles(StrictModel):
    data: list[ProfileSuppressionCreateQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of email addresses to suppress. Maximum 100 email addresses per request. Specify this to suppress individual profiles, or use list/segment ID instead to suppress all members of a group.")
class BulkSuppressProfilesRequestBodyDataAttributes(StrictModel):
    profiles: BulkSuppressProfilesRequestBodyDataAttributesProfiles
class BulkSuppressProfilesRequestBodyData(StrictModel):
    type_: Literal["profile-suppression-bulk-create-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier for the bulk suppression job. Must be set to 'profile-suppression-bulk-create-job'.")
    relationships: BulkSuppressProfilesRequestBodyDataRelationships
    attributes: BulkSuppressProfilesRequestBodyDataAttributes
class BulkSuppressProfilesRequestBody(StrictModel):
    """Suppresses one or more profiles from receiving marketing. Currently, supports email only. If a profile is not found with the given email, one will be created and immediately suppressed."""
    data: BulkSuppressProfilesRequestBodyData
class BulkSuppressProfilesRequest(StrictModel):
    """Create a bulk job to suppress profiles from receiving email marketing. Suppress profiles by providing individual email addresses (up to 100 per request) or by specifying a segment or list ID to suppress all current members."""
    header: BulkSuppressProfilesRequestHeader
    body: BulkSuppressProfilesRequestBody

# Operation: get_bulk_suppress_profiles_job
class GetBulkSuppressProfilesJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk suppress profiles job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH).")
class GetBulkSuppressProfilesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkSuppressProfilesJobRequest(StrictModel):
    """Retrieve the status and details of a bulk suppress profiles job by its ID. Use this to monitor the progress and results of profile suppression operations."""
    path: GetBulkSuppressProfilesJobRequestPath
    header: GetBulkSuppressProfilesJobRequestHeader

# Operation: list_bulk_unsuppress_profiles_jobs
class GetBulkUnsuppressProfilesJobsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by job status, list ID, or segment ID using equality operators. Specify filters in the format `field_name=value` (e.g., `status=processing` to show only processing jobs).")
class GetBulkUnsuppressProfilesJobsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetBulkUnsuppressProfilesJobsRequest(StrictModel):
    """Retrieve all bulk unsuppress profiles jobs with optional filtering by status, list ID, or segment ID. Use this to monitor the progress and status of profile unsuppression operations."""
    query: GetBulkUnsuppressProfilesJobsRequestQuery | None = None
    header: GetBulkUnsuppressProfilesJobsRequestHeader

# Operation: remove_profile_suppressions_bulk
class BulkUnsuppressProfilesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15.")
class BulkUnsuppressProfilesRequestBodyDataRelationshipsListData(StrictModel):
    type_: Literal["list"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier for list relationships. Must be 'list'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the list whose current members should have suppressions removed. Provide either this or segment.data.id, not both.")
class BulkUnsuppressProfilesRequestBodyDataRelationshipsList(StrictModel):
    data: BulkUnsuppressProfilesRequestBodyDataRelationshipsListData
class BulkUnsuppressProfilesRequestBodyDataRelationshipsSegmentData(StrictModel):
    type_: Literal["segment"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier for segment relationships. Must be 'segment'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the segment whose current members should have suppressions removed. Provide either this or list.data.id, not both.")
class BulkUnsuppressProfilesRequestBodyDataRelationshipsSegment(StrictModel):
    data: BulkUnsuppressProfilesRequestBodyDataRelationshipsSegmentData
class BulkUnsuppressProfilesRequestBodyDataRelationships(StrictModel):
    list_: BulkUnsuppressProfilesRequestBodyDataRelationshipsList = Field(default=..., validation_alias="list", serialization_alias="list")
    segment: BulkUnsuppressProfilesRequestBodyDataRelationshipsSegment
class BulkUnsuppressProfilesRequestBodyDataAttributesProfiles(StrictModel):
    data: list[ProfileSuppressionDeleteQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of email addresses to unsuppress. Maximum 100 email addresses per request.")
class BulkUnsuppressProfilesRequestBodyDataAttributes(StrictModel):
    profiles: BulkUnsuppressProfilesRequestBodyDataAttributesProfiles
class BulkUnsuppressProfilesRequestBodyData(StrictModel):
    type_: Literal["profile-suppression-bulk-delete-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier for the bulk suppression deletion job. Must be 'profile-suppression-bulk-delete-job'.")
    relationships: BulkUnsuppressProfilesRequestBodyDataRelationships
    attributes: BulkUnsuppressProfilesRequestBodyDataAttributes
class BulkUnsuppressProfilesRequestBody(StrictModel):
    """Unsuppresses one or more profiles from receiving marketing. Currently, supports email only. If a profile is not
found with the given email, no action will be taken."""
    data: BulkUnsuppressProfilesRequestBodyData
class BulkUnsuppressProfilesRequest(StrictModel):
    """Bulk remove USER_SUPPRESSED suppressions from profiles by email address or by unsuppressing all members of a specified segment or list. Other suppression reasons (unsubscribed, invalid email, hard bounce) are not affected."""
    header: BulkUnsuppressProfilesRequestHeader
    body: BulkUnsuppressProfilesRequestBody

# Operation: get_bulk_unsuppress_profiles_job
class GetBulkUnsuppressProfilesJobRequestPath(StrictModel):
    job_id: str = Field(default=..., description="The unique identifier of the bulk unsuppress job to retrieve (e.g., 01GSQPBF74KQ5YTDEPP41T1BZH).")
class GetBulkUnsuppressProfilesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class GetBulkUnsuppressProfilesJobRequest(StrictModel):
    """Retrieve the status and details of a bulk unsuppress profiles job by its ID. Use this to monitor the progress of profile unsuppression operations."""
    path: GetBulkUnsuppressProfilesJobRequestPath
    header: GetBulkUnsuppressProfilesJobRequestHeader

# Operation: list_push_tokens
class GetPushTokensRequestQuery(StrictModel):
    fields_push_token: list[Literal["background", "created", "enablement_status", "metadata", "metadata.app_build", "metadata.app_id", "metadata.app_name", "metadata.app_version", "metadata.device_id", "metadata.device_model", "metadata.environment", "metadata.klaviyo_sdk", "metadata.manufacturer", "metadata.os_name", "metadata.os_version", "metadata.sdk_version", "platform", "recorded_date", "token", "vendor"]] | None = Field(default=None, validation_alias="fields[push-token]", serialization_alias="fields[push-token]", description="Specify which push token fields to include in the response using sparse fieldsets for optimized payload size.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by push token properties. Supported filters: token ID, associated profile ID, enablement status, or platform. Use equals operator with the format: field_name equals('value').")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of results per page. Must be between 1 and 100 items. Defaults to 20 if not specified.", ge=1, le=100)
class GetPushTokensRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetPushTokensRequest(StrictModel):
    """Retrieve push tokens associated with your company account. Supports filtering by token ID, profile ID, enablement status, and platform, with optional sparse fieldset selection."""
    query: GetPushTokensRequestQuery | None = None
    header: GetPushTokensRequestHeader

# Operation: create_or_update_push_token
class CreatePushTokenRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15.")
class CreatePushTokenRequestBodyDataAttributes(StrictModel):
    token: str = Field(default=..., validation_alias="token", serialization_alias="token", description="The push token string from APNS (Apple) or FCM (Google). This is the credential needed to send push notifications to the device.")
    platform: Literal["android", "ios"] = Field(default=..., validation_alias="platform", serialization_alias="platform", description="The mobile platform where the push token was generated. Must be either 'ios' or 'android'.")
    enablement_status: Literal["AUTHORIZED", "DENIED", "NOT_DETERMINED", "PROVISIONAL", "UNAUTHORIZED"] | None = Field(default=None, validation_alias="enablement_status", serialization_alias="enablement_status", description="Authorization status for this push token. Indicates whether the user has granted, denied, or not yet determined push notification permissions. Defaults to 'AUTHORIZED'.")
    vendor: Literal["apns", "fcm"] = Field(default=..., validation_alias="vendor", serialization_alias="vendor", description="The push service provider. Must be 'apns' for Apple devices or 'fcm' for Android devices.")
    background: Literal["AVAILABLE", "DENIED", "RESTRICTED"] | None = Field(default=None, validation_alias="background", serialization_alias="background", description="Whether the device can receive background push notifications. Defaults to 'AVAILABLE'. Use 'DENIED' or 'RESTRICTED' if background delivery is not permitted.")
    device_metadata: CreatePushTokenBodyDataAttributesDeviceMetadata | None = Field(default=None, validation_alias="device_metadata", serialization_alias="device_metadata", description="Device metadata: device_id, model, OS, app info, SDK version, and environment.")
    profile: CreatePushTokenBodyDataAttributesProfile | None = Field(default=None, validation_alias="profile", serialization_alias="profile", description="Profile to associate with the push token: email, phone, name, location, and custom properties.")
class CreatePushTokenRequestBodyData(StrictModel):
    type_: Literal["push-token"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier. Must be 'push-token'.")
    attributes: CreatePushTokenRequestBodyDataAttributes
class CreatePushTokenRequestBody(StrictModel):
    data: CreatePushTokenRequestBodyData
class CreatePushTokenRequest(StrictModel):
    """Create or update a push token for a user's device, enabling push notification delivery. This endpoint supports migrating push tokens from other platforms and accepts device metadata to enhance targeting and analytics."""
    header: CreatePushTokenRequestHeader
    body: CreatePushTokenRequestBody

# Operation: get_push_token
class GetPushTokenRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the push token to retrieve.")
class GetPushTokenRequestQuery(StrictModel):
    fields_push_token: list[Literal["background", "created", "enablement_status", "metadata", "metadata.app_build", "metadata.app_id", "metadata.app_name", "metadata.app_version", "metadata.device_id", "metadata.device_model", "metadata.environment", "metadata.klaviyo_sdk", "metadata.manufacturer", "metadata.os_name", "metadata.os_version", "metadata.sdk_version", "platform", "recorded_date", "token", "vendor"]] | None = Field(default=None, validation_alias="fields[push-token]", serialization_alias="fields[push-token]", description="Specify which fields to include in the push token response using sparse fieldsets. Omit to receive all available fields.")
class GetPushTokenRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetPushTokenRequest(StrictModel):
    """Retrieve a specific push token by its ID. Returns detailed information about the push token configuration and status."""
    path: GetPushTokenRequestPath
    query: GetPushTokenRequestQuery | None = None
    header: GetPushTokenRequestHeader

# Operation: delete_push_token
class DeletePushTokenRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the push token to delete, typically a 32-character hexadecimal string.")
class DeletePushTokenRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class DeletePushTokenRequest(StrictModel):
    """Permanently delete a push token by its ID. This operation requires write access to push tokens and is subject to rate limits (3 requests per second burst, 60 per minute steady)."""
    path: DeletePushTokenRequestPath
    header: DeletePushTokenRequestHeader

# Operation: create_or_update_profile
class CreateOrUpdateProfileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15).")
class CreateOrUpdateProfileRequestBodyDataAttributesLocation(StrictModel):
    address1: str | None = Field(default=None, validation_alias="address1", serialization_alias="address1", description="First line of the street address.")
    address2: str | None = Field(default=None, validation_alias="address2", serialization_alias="address2", description="Second line of the street address (e.g., apartment or floor number).")
    city: str | None = Field(default=None, validation_alias="city", serialization_alias="city", description="City name.")
    country: str | None = Field(default=None, validation_alias="country", serialization_alias="country", description="Country name.")
    latitude: str | None = Field(default=None, validation_alias="latitude", serialization_alias="latitude", description="Latitude coordinate; recommend precision of four decimal places. Accepts string or number format.")
    longitude: str | None = Field(default=None, validation_alias="longitude", serialization_alias="longitude", description="Longitude coordinate; recommend precision of four decimal places. Accepts string or number format.")
    region: str | None = Field(default=None, validation_alias="region", serialization_alias="region", description="Region within a country, such as state or province (e.g., NY).")
    zip_: str | None = Field(default=None, validation_alias="zip", serialization_alias="zip", description="Zip or postal code.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="Time zone name using the IANA Time Zone Database format (e.g., America/New_York).")
    ip: str | None = Field(default=None, validation_alias="ip", serialization_alias="ip", description="IP address associated with the profile.")
class CreateOrUpdateProfileRequestBodyDataAttributes(StrictModel):
    email: str | None = Field(default=None, validation_alias="email", serialization_alias="email", description="Individual's email address (e.g., sarah.mason@klaviyo-demo.com).")
    phone_number: str | None = Field(default=None, validation_alias="phone_number", serialization_alias="phone_number", description="Individual's phone number in E.164 format (e.g., +15005550006).")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="Unique external identifier to associate this Klaviyo profile with a profile in an external system such as a point-of-sale system. Format varies by external system.")
    kx: str | None = Field(default=None, validation_alias="_kx", serialization_alias="_kx", description="Encrypted exchange identifier used by Klaviyo's web tracking to identify profiles. Can be used as a filter when retrieving profiles.")
    first_name: str | None = Field(default=None, validation_alias="first_name", serialization_alias="first_name", description="Individual's first name.")
    last_name: str | None = Field(default=None, validation_alias="last_name", serialization_alias="last_name", description="Individual's last name.")
    organization: str | None = Field(default=None, validation_alias="organization", serialization_alias="organization", description="Name of the company or organization where the individual works.")
    locale: str | None = Field(default=None, validation_alias="locale", serialization_alias="locale", description="Profile locale in IETF BCP 47 format (e.g., en-US for English-United States).")
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="Individual's job title.")
    image: str | None = Field(default=None, validation_alias="image", serialization_alias="image", description="URL pointing to the profile's image.")
    properties: dict[str, Any] | None = Field(default=None, validation_alias="properties", serialization_alias="properties", description="Object containing custom key-value pairs for profile properties. Setting a field to null clears it; omitting a field leaves it unchanged.")
    location: CreateOrUpdateProfileRequestBodyDataAttributesLocation | None = None
class CreateOrUpdateProfileRequestBodyDataMetaPatchProperties(StrictModel):
    append: dict[str, Any] | None = Field(default=None, validation_alias="append", serialization_alias="append", description="Object specifying simple values to append to property arrays (e.g., add SKUs to an existing list).")
    unappend: dict[str, Any] | None = Field(default=None, validation_alias="unappend", serialization_alias="unappend", description="Object specifying simple values to remove from property arrays (e.g., remove SKUs from an existing list).")
    unset: str | list[str] | None = Field(default=None, validation_alias="unset", serialization_alias="unset", description="Array or string specifying property keys to remove completely from the profile, including all their values.")
class CreateOrUpdateProfileRequestBodyDataMeta(StrictModel):
    patch_properties: CreateOrUpdateProfileRequestBodyDataMetaPatchProperties | None = None
class CreateOrUpdateProfileRequestBodyData(StrictModel):
    type_: Literal["profile"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier; must be set to 'profile'.")
    attributes: CreateOrUpdateProfileRequestBodyDataAttributes | None = None
    meta: CreateOrUpdateProfileRequestBodyDataMeta | None = None
class CreateOrUpdateProfileRequestBody(StrictModel):
    data: CreateOrUpdateProfileRequestBodyData
class CreateOrUpdateProfileRequest(StrictModel):
    """Create a new profile or update an existing one with the provided attributes. Returns 201 for newly created profiles and 200 for updates. Use the `additional-fields` parameter to include subscriptions and predictive analytics in the response."""
    header: CreateOrUpdateProfileRequestHeader
    body: CreateOrUpdateProfileRequestBody

# Operation: merge_profiles
class MergeProfilesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class MergeProfilesRequestBodyDataRelationshipsProfiles(StrictModel):
    data: list[MergeProfilesBodyDataRelationshipsProfilesDataItem] | None = Field(default=None, validation_alias="data", serialization_alias="data", description="Array containing the source profile relationship to be merged into the destination profile. Only one source profile is accepted per request.")
class MergeProfilesRequestBodyDataRelationships(StrictModel):
    profiles: MergeProfilesRequestBodyDataRelationshipsProfiles | None = None
class MergeProfilesRequestBodyData(StrictModel):
    type_: Literal["profile-merge"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of operation being performed. Must be set to 'profile-merge'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the destination profile that will receive merged data from the source profile.")
    relationships: MergeProfilesRequestBodyDataRelationships | None = None
class MergeProfilesRequestBody(StrictModel):
    data: MergeProfilesRequestBodyData
class MergeProfilesRequest(StrictModel):
    """Merge a source profile into a destination profile by ID. This operation queues an asynchronous task that consolidates data from the source profile into the destination profile and deletes the source profile. Only one source profile can be merged per request."""
    header: MergeProfilesRequestHeader
    body: MergeProfilesRequestBody

# Operation: subscribe_profiles_bulk
class BulkSubscribeProfilesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15).")
class BulkSubscribeProfilesRequestBodyDataRelationshipsListData(StrictModel):
    type_: Literal["list"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type for the list relationship; must be 'list'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the list to add newly subscribed profiles to (e.g., 'Y6nRLr').")
class BulkSubscribeProfilesRequestBodyDataRelationshipsList(StrictModel):
    data: BulkSubscribeProfilesRequestBodyDataRelationshipsListData
class BulkSubscribeProfilesRequestBodyDataRelationships(StrictModel):
    list_: BulkSubscribeProfilesRequestBodyDataRelationshipsList = Field(default=..., validation_alias="list", serialization_alias="list")
class BulkSubscribeProfilesRequestBodyDataAttributesProfiles(StrictModel):
    data: list[ProfileSubscriptionCreateQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of profile objects to subscribe. Each profile should include subscription channel preferences and optional push tokens. Maximum 1,000 profiles per request.")
class BulkSubscribeProfilesRequestBodyDataAttributes(StrictModel):
    custom_source: str | None = Field(default=None, validation_alias="custom_source", serialization_alias="custom_source", description="Optional custom label or source to record on consent records (e.g., 'Marketing Event'). Useful for tracking subscription origin.")
    historical_import: bool | None = Field(default=None, validation_alias="historical_import", serialization_alias="historical_import", description="Set to true when importing historical subscription data where consent was already collected. When enabled, bypasses double opt-in emails and 'Added to list' flows, and requires the consented_at field in the past for each profile.")
    profiles: BulkSubscribeProfilesRequestBodyDataAttributesProfiles
class BulkSubscribeProfilesRequestBodyData(StrictModel):
    type_: Literal["profile-subscription-bulk-create-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier; must be 'profile-subscription-bulk-create-job'.")
    relationships: BulkSubscribeProfilesRequestBodyDataRelationships
    attributes: BulkSubscribeProfilesRequestBodyDataAttributes
class BulkSubscribeProfilesRequestBody(StrictModel):
    """Subscribes one or more profiles to marketing, with support for push channel and push tokens.
All profiles will be added to the provided list. Either email or phone number is required.
Both may be specified to subscribe to both channels. If a profile cannot be found matching
the given identifier(s), a new profile will be created and then subscribed."""
    data: BulkSubscribeProfilesRequestBodyData
class BulkSubscribeProfilesRequest(StrictModel):
    """Subscribe up to 1,000 profiles to email, SMS, WhatsApp, or push marketing channels. Profiles will be immediately subscribed or sent a double opt-in confirmation based on list settings or account defaults. Removes any existing unsubscribe, spam report, or suppression flags from the profiles."""
    header: BulkSubscribeProfilesRequestHeader
    body: BulkSubscribeProfilesRequestBody

# Operation: unsubscribe_profiles_bulk
class BulkUnsubscribeProfilesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15.")
class BulkUnsubscribeProfilesRequestBodyDataRelationshipsListData(StrictModel):
    type_: Literal["list"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of resource being referenced. Must be 'list'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the list from which to unsubscribe the profiles.")
class BulkUnsubscribeProfilesRequestBodyDataRelationshipsList(StrictModel):
    data: BulkUnsubscribeProfilesRequestBodyDataRelationshipsListData
class BulkUnsubscribeProfilesRequestBodyDataRelationships(StrictModel):
    list_: BulkUnsubscribeProfilesRequestBodyDataRelationshipsList = Field(default=..., validation_alias="list", serialization_alias="list")
class BulkUnsubscribeProfilesRequestBodyDataAttributesProfiles(StrictModel):
    data: list[ProfileSubscriptionDeleteQueryResourceObject] = Field(default=..., validation_alias="data", serialization_alias="data", description="Array of profile objects to unsubscribe. Maximum 100 profiles per request. Each profile should include the necessary identifiers for the unsubscribe operation.")
class BulkUnsubscribeProfilesRequestBodyDataAttributes(StrictModel):
    profiles: BulkUnsubscribeProfilesRequestBodyDataAttributesProfiles
class BulkUnsubscribeProfilesRequestBodyData(StrictModel):
    type_: Literal["profile-subscription-bulk-delete-job"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of job being created. Must be 'profile-subscription-bulk-delete-job'.")
    relationships: BulkUnsubscribeProfilesRequestBodyDataRelationships
    attributes: BulkUnsubscribeProfilesRequestBodyDataAttributes
class BulkUnsubscribeProfilesRequestBody(StrictModel):
    """Unsubscribes one or more profiles from marketing. Currently, supports email and SMS only. All profiles will be removed from the provided list.
Either email or phone number is required. If a profile cannot be found matching the given identifier(s), a new profile will be created and then unsubscribed."""
    data: BulkUnsubscribeProfilesRequestBodyData
class BulkUnsubscribeProfilesRequest(StrictModel):
    """Bulk unsubscribe one or more profiles (up to 100 per request) from email marketing, SMS marketing, or both. ⚠️ Profiles not in the specified list will be globally unsubscribed—always verify list membership before calling to avoid unintended global unsubscribes."""
    header: BulkUnsubscribeProfilesRequestHeader
    body: BulkUnsubscribeProfilesRequestBody

# Operation: list_push_tokens_for_profile
class GetPushTokensForProfileRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the profile whose push tokens should be retrieved.")
class GetPushTokensForProfileRequestQuery(StrictModel):
    fields_push_token: list[Literal["background", "created", "enablement_status", "metadata", "metadata.app_build", "metadata.app_id", "metadata.app_name", "metadata.app_version", "metadata.device_id", "metadata.device_model", "metadata.environment", "metadata.klaviyo_sdk", "metadata.manufacturer", "metadata.os_name", "metadata.os_version", "metadata.sdk_version", "platform", "recorded_date", "token", "vendor"]] | None = Field(default=None, validation_alias="fields[push-token]", serialization_alias="fields[push-token]", description="Optional sparse fieldset to limit which push token attributes are included in the response. Specify as a comma-separated list of field names.")
class GetPushTokensForProfileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetPushTokensForProfileRequest(StrictModel):
    """Retrieve all push tokens associated with a specific profile. Use sparse fieldsets to customize which push token attributes are returned in the response."""
    path: GetPushTokensForProfileRequestPath
    query: GetPushTokensForProfileRequestQuery | None = None
    header: GetPushTokensForProfileRequestHeader

# Operation: list_push_token_ids_for_profile
class GetPushTokenIdsForProfileRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the profile for which to retrieve associated push token IDs.")
class GetPushTokenIdsForProfileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetPushTokenIdsForProfileRequest(StrictModel):
    """Retrieve all push token IDs associated with a specific profile. Returns a collection of push token identifiers linked to the given profile."""
    path: GetPushTokenIdsForProfileRequestPath
    header: GetPushTokenIdsForProfileRequestHeader

# Operation: list_lists_for_profile
class GetListsForProfileRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the profile whose list memberships you want to retrieve.")
class GetListsForProfileRequestQuery(StrictModel):
    fields_list: list[Literal["created", "name", "opt_in_process", "updated"]] | None = Field(default=None, validation_alias="fields[list]", serialization_alias="fields[list]", description="Specify which fields to include in the response using sparse fieldsets. Omit to return default fields. See API documentation for available field names.")
class GetListsForProfileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetListsForProfileRequest(StrictModel):
    """Retrieve all list memberships for a specific profile. Returns the lists that a profile belongs to, with support for sparse fieldsets to customize the response."""
    path: GetListsForProfileRequestPath
    query: GetListsForProfileRequestQuery | None = None
    header: GetListsForProfileRequestHeader

# Operation: get_lists_for_profile_relationship
class GetListIdsForProfileRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the profile to retrieve list memberships for.")
class GetListIdsForProfileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class GetListIdsForProfileRequest(StrictModel):
    """Retrieve all list memberships for a specific profile. Returns the IDs of lists that the profile belongs to."""
    path: GetListIdsForProfileRequestPath
    header: GetListIdsForProfileRequestHeader

# Operation: get_segments_for_profile
class GetSegmentsForProfileRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the profile to retrieve segments for.")
class GetSegmentsForProfileRequestQuery(StrictModel):
    fields_segment: list[Literal["created", "definition", "definition.condition_groups", "is_active", "is_processing", "is_starred", "name", "updated"]] | None = Field(default=None, validation_alias="fields[segment]", serialization_alias="fields[segment]", description="Optional list of specific segment fields to include in the response. Use sparse fieldsets to reduce payload size and improve performance by requesting only needed fields.")
class GetSegmentsForProfileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetSegmentsForProfileRequest(StrictModel):
    """Retrieve all segment memberships for a specific profile. Returns which segments the profile belongs to, with optional field filtering for sparse responses."""
    path: GetSegmentsForProfileRequestPath
    query: GetSegmentsForProfileRequestQuery | None = None
    header: GetSegmentsForProfileRequestHeader

# Operation: list_segment_ids_for_profile
class GetSegmentIdsForProfileRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the profile whose segment memberships you want to retrieve.")
class GetSegmentIdsForProfileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetSegmentIdsForProfileRequest(StrictModel):
    """Retrieve all segment IDs that a profile is a member of. Returns the segment membership relationships for the specified profile."""
    path: GetSegmentIdsForProfileRequestPath
    header: GetSegmentIdsForProfileRequestHeader

# Operation: get_lists_for_bulk_import_profiles_job
class GetListForBulkImportProfilesJobRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk import profiles job.")
class GetListForBulkImportProfilesJobRequestQuery(StrictModel):
    fields_list: list[Literal["created", "name", "opt_in_process", "updated"]] | None = Field(default=None, validation_alias="fields[list]", serialization_alias="fields[list]", description="Specify which fields to include in the response using sparse fieldsets. Omit to receive all available fields.")
class GetListForBulkImportProfilesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetListForBulkImportProfilesJobRequest(StrictModel):
    """Retrieve the lists associated with a bulk profile import job. Use this to see which lists will receive the imported profiles."""
    path: GetListForBulkImportProfilesJobRequestPath
    query: GetListForBulkImportProfilesJobRequestQuery | None = None
    header: GetListForBulkImportProfilesJobRequestHeader

# Operation: get_list_ids_for_bulk_import_profiles_job
class GetListIdsForBulkImportProfilesJobRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk profile import job for which to retrieve associated list IDs.")
class GetListIdsForBulkImportProfilesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetListIdsForBulkImportProfilesJobRequest(StrictModel):
    """Retrieve the list IDs associated with a specific bulk profile import job. This operation returns the relationship between a bulk import job and its related lists."""
    path: GetListIdsForBulkImportProfilesJobRequestPath
    header: GetListIdsForBulkImportProfilesJobRequestHeader

# Operation: list_profiles_for_bulk_import_job
class GetProfilesForBulkImportProfilesJobRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk import job whose profiles you want to retrieve.")
class GetProfilesForBulkImportProfilesJobRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of profiles to return per page. Defaults to 20 profiles; must be between 1 and 100.", ge=1, le=100)
class GetProfilesForBulkImportProfilesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15.")
class GetProfilesForBulkImportProfilesJobRequest(StrictModel):
    """Retrieve profiles associated with a bulk profile import job. Results are paginated and support customizable page sizes."""
    path: GetProfilesForBulkImportProfilesJobRequestPath
    query: GetProfilesForBulkImportProfilesJobRequestQuery | None = None
    header: GetProfilesForBulkImportProfilesJobRequestHeader

# Operation: list_profile_ids_for_bulk_import_job
class GetProfileIdsForBulkImportProfilesJobRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk import profiles job.")
class GetProfileIdsForBulkImportProfilesJobRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of profile IDs to return per page. Defaults to 20, with a maximum of 100 results per page.", ge=1, le=100)
class GetProfileIdsForBulkImportProfilesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15.")
class GetProfileIdsForBulkImportProfilesJobRequest(StrictModel):
    """Retrieve the profile IDs associated with a bulk import job. Returns paginated profile relationships for the specified bulk profile import job."""
    path: GetProfileIdsForBulkImportProfilesJobRequestPath
    query: GetProfileIdsForBulkImportProfilesJobRequestQuery | None = None
    header: GetProfileIdsForBulkImportProfilesJobRequestHeader

# Operation: list_import_errors_for_bulk_import_profiles_job
class GetErrorsForBulkImportProfilesJobRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk import job to retrieve errors for.")
class GetErrorsForBulkImportProfilesJobRequestQuery(StrictModel):
    fields_import_error: list[Literal["code", "detail", "original_payload", "source", "source.pointer", "title"]] | None = Field(default=None, validation_alias="fields[import-error]", serialization_alias="fields[import-error]", description="Specify which fields to include in the import-error response using sparse fieldsets. Omit to return all available fields.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of errors to return per page. Must be between 1 and 100 (default: 20).", ge=1, le=100)
class GetErrorsForBulkImportProfilesJobRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (default: 2026-01-15). Determines the response schema version.")
class GetErrorsForBulkImportProfilesJobRequest(StrictModel):
    """Retrieve import errors for a bulk profile import job. Returns detailed error information for profiles that failed during the import process, with pagination support."""
    path: GetErrorsForBulkImportProfilesJobRequestPath
    query: GetErrorsForBulkImportProfilesJobRequestQuery | None = None
    header: GetErrorsForBulkImportProfilesJobRequestHeader

# Operation: get_profile_for_push_token
class GetProfileForPushTokenRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The push token identifier whose associated profile you want to retrieve.")
class GetProfileForPushTokenRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetProfileForPushTokenRequest(StrictModel):
    """Retrieve the user profile associated with a specific push token. This operation allows you to look up profile information linked to a push notification token."""
    path: GetProfileForPushTokenRequestPath
    header: GetProfileForPushTokenRequestHeader

# Operation: get_profile_id_for_push_token
class GetProfileIdForPushTokenRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the push token for which you want to retrieve the associated profile ID.")
class GetProfileIdForPushTokenRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetProfileIdForPushTokenRequest(StrictModel):
    """Retrieve the profile ID associated with a specific push token. This operation returns the relationship between a push token and its linked user profile."""
    path: GetProfileIdForPushTokenRequestPath
    header: GetProfileIdForPushTokenRequestHeader

# Operation: query_campaign_values_report
class QueryCampaignValuesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class QueryCampaignValuesRequestBodyDataAttributes(StrictModel):
    statistics: list[Literal["average_order_value", "bounce_rate", "bounced", "bounced_or_failed", "bounced_or_failed_rate", "click_rate", "click_to_open_rate", "clicks", "clicks_unique", "conversion_rate", "conversion_uniques", "conversion_value", "conversions", "delivered", "delivery_rate", "failed", "failed_rate", "message_segment_count_sum", "open_rate", "opens", "opens_unique", "recipients", "revenue_per_recipient", "spam_complaint_rate", "spam_complaints", "text_message_credit_usage_amount", "text_message_roi", "text_message_spend", "unsubscribe_rate", "unsubscribe_uniques", "unsubscribes"]] = Field(default=..., validation_alias="statistics", serialization_alias="statistics", description="Comma-separated list of metrics to retrieve (e.g., opens, open_rate, clicks, conversions). Rate-based statistics are returned as decimal values between 0.0 and 1.0.")
    timeframe: Timeframe | CustomTimeframe = Field(default=..., validation_alias="timeframe", serialization_alias="timeframe", description="Time period for data retrieval in a supported timeframe format. Maximum span is 1 year. Refer to available timeframes documentation for valid formats.")
    conversion_metric_id: str = Field(default=..., validation_alias="conversion_metric_id", serialization_alias="conversion_metric_id", description="Unique identifier of the conversion metric to use for calculating conversion-related statistics in the report.")
    group_by: list[Literal["campaign_id", "campaign_message_id", "campaign_message_name", "group", "group_name", "send_channel", "tag_id", "tag_name", "text_message_format", "variation", "variation_name"]] | None = Field(default=None, validation_alias="group_by", serialization_alias="group_by", description="Optional list of dimensions to group results by. Supported dimensions include campaign_id, campaign_message_id, campaign_message_name, group, group_name, send_channel, tag_id, tag_name, text_message_format, variation, and variation_name. Campaign_id and campaign_message_id are required if grouping is specified. Defaults to grouping by campaign_id, campaign_message_id, and send_channel if omitted.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results using AND-combined conditions. Scalar attributes (send_channel, campaign_id, campaign_message_id, campaign_message_name, variation, variation_name, text_message_format) support equals and contains-any operators. List attributes (tag_id, tag_name) support contains-any and contains-all operators. Send_channel values are limited to email, sms, push-notification, and whatsapp. Maximum 100 items per list filter.")
class QueryCampaignValuesRequestBodyData(StrictModel):
    type_: Literal["campaign-values-report"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Report type identifier. Must be set to 'campaign-values-report' to query campaign analytics data.")
    attributes: QueryCampaignValuesRequestBodyDataAttributes
class QueryCampaignValuesRequestBody(StrictModel):
    data: QueryCampaignValuesRequestBodyData
class QueryCampaignValuesRequest(StrictModel):
    """Retrieve campaign analytics data for specified statistics across a given timeframe, with optional grouping and filtering capabilities. Results include conversion metrics and can be segmented by campaign, channel, tags, and other dimensions."""
    header: QueryCampaignValuesRequestHeader
    body: QueryCampaignValuesRequestBody

# Operation: query_flow_values_report
class QueryFlowValuesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.1). Defaults to 2026-01-15 if not specified.")
class QueryFlowValuesRequestBodyDataAttributes(StrictModel):
    statistics: list[Literal["average_order_value", "bounce_rate", "bounced", "bounced_or_failed", "bounced_or_failed_rate", "click_rate", "click_to_open_rate", "clicks", "clicks_unique", "conversion_rate", "conversion_uniques", "conversion_value", "conversions", "delivered", "delivery_rate", "failed", "failed_rate", "message_segment_count_sum", "open_rate", "opens", "opens_unique", "recipients", "revenue_per_recipient", "spam_complaint_rate", "spam_complaints", "text_message_credit_usage_amount", "text_message_roi", "text_message_spend", "unsubscribe_rate", "unsubscribe_uniques", "unsubscribes"]] = Field(default=..., validation_alias="statistics", serialization_alias="statistics", description="List of metrics to retrieve for each result row. Rate-based statistics (like open_rate, click_rate) are returned as decimal values between 0.0 and 1.0. Examples include 'opens', 'clicks', 'open_rate', 'conversion_count'. Specify the exact metrics needed for your analysis.")
    timeframe: Timeframe | CustomTimeframe = Field(default=..., validation_alias="timeframe", serialization_alias="timeframe", description="Time period for the report, with a maximum span of 1 year. Refer to the available time frames documentation for supported formats (e.g., relative ranges like 'last_30_days' or absolute date ranges).")
    conversion_metric_id: str = Field(default=..., validation_alias="conversion_metric_id", serialization_alias="conversion_metric_id", description="Metric ID used to calculate conversion-related statistics in the report. Provide the ID of the conversion metric you want to measure (e.g., 'RESQ6t').")
    group_by: list[Literal["flow_id", "flow_message_id", "flow_message_name", "flow_name", "send_channel", "tag_id", "tag_name", "text_message_format", "variation", "variation_name"]] | None = Field(default=None, validation_alias="group_by", serialization_alias="group_by", description="Optional list of attributes to group results by. Allowed values include flow_id, flow_message_id, flow_message_name, flow_name, send_channel, tag_id, tag_name, text_message_format, variation, and variation_name. The attributes flow_message_id and flow_id are always required in the grouping. If omitted, results default to grouping by flow_id, flow_message_id, and send_channel.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results. Use operators like 'equals' and 'contains-any' for scalar attributes (flow_id, flow_name, send_channel, flow_message_id, flow_message_name, text_message_format, variation, variation_name), and 'contains-any' or 'contains-all' for list attributes (tag_id, tag_name). Combine conditions with AND only. Limited to 100 items per list filter. For send_channel, valid values are email, sms, push-notification, and whatsapp.")
class QueryFlowValuesRequestBodyData(StrictModel):
    type_: Literal["flow-values-report"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Report type identifier. Must be set to 'flow-values-report' to query flow analytics data.")
    attributes: QueryFlowValuesRequestBodyDataAttributes
class QueryFlowValuesRequestBody(StrictModel):
    data: QueryFlowValuesRequestBodyData
class QueryFlowValuesRequest(StrictModel):
    """Retrieve flow analytics data including performance metrics like opens, clicks, conversions, and engagement rates. Results can be filtered and grouped by flow, message, channel, tags, and other dimensions to analyze campaign performance over a specified time period."""
    header: QueryFlowValuesRequestHeader
    body: QueryFlowValuesRequestBody

# Operation: get_flow_series_analytics
class QueryFlowSeriesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.beta). Defaults to 2026-01-15.")
class QueryFlowSeriesRequestBodyDataAttributes(StrictModel):
    statistics: list[Literal["average_order_value", "bounce_rate", "bounced", "bounced_or_failed", "bounced_or_failed_rate", "click_rate", "click_to_open_rate", "clicks", "clicks_unique", "conversion_rate", "conversion_uniques", "conversion_value", "conversions", "delivered", "delivery_rate", "failed", "failed_rate", "message_segment_count_sum", "open_rate", "opens", "opens_unique", "recipients", "revenue_per_recipient", "spam_complaint_rate", "spam_complaints", "text_message_credit_usage_amount", "text_message_roi", "text_message_spend", "unsubscribe_rate", "unsubscribe_uniques", "unsubscribes"]] = Field(default=..., validation_alias="statistics", serialization_alias="statistics", description="One or more statistics to retrieve for each data point. Rate statistics (like open_rate) are returned as decimals between 0.0 and 1.0. Examples: opens, open_rate, clicks, click_rate, conversions.")
    timeframe: Timeframe | CustomTimeframe = Field(default=..., validation_alias="timeframe", serialization_alias="timeframe", description="The date range for the report, with a maximum span of 1 year. Refer to available time frames in the Klaviyo reporting API documentation for supported formats.")
    interval: Literal["daily", "hourly", "monthly", "weekly"] = Field(default=..., validation_alias="interval", serialization_alias="interval", description="The time bucket size for aggregating data. Hourly intervals are limited to 7-day timeframes, daily to 60 days, and monthly to 52 weeks.")
    conversion_metric_id: str = Field(default=..., validation_alias="conversion_metric_id", serialization_alias="conversion_metric_id", description="The metric ID used to calculate conversion statistics. This determines which conversion event is tracked in the results.")
    group_by: list[Literal["flow_id", "flow_message_id", "flow_message_name", "flow_name", "send_channel", "tag_id", "tag_name", "text_message_format", "variation", "variation_name"]] | None = Field(default=None, validation_alias="group_by", serialization_alias="group_by", description="Optional list of attributes to group results by (e.g., flow_id, flow_name, send_channel, tag_name). Flow_message_id and flow_id are always required. If omitted, data defaults to grouping by flow_id, flow_message_id, and send_channel.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results by scalar attributes (flow_id, flow_name, send_channel, etc.) or list attributes (tag_id, tag_name). Use equals or contains-any for scalars, contains-any or contains-all for lists. Combine multiple filters with AND only. Maximum 100 items per list filter.")
class QueryFlowSeriesRequestBodyData(StrictModel):
    type_: Literal["flow-series-report"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of report being requested. Must be 'flow-series-report'.")
    attributes: QueryFlowSeriesRequestBodyDataAttributes
class QueryFlowSeriesRequestBody(StrictModel):
    data: QueryFlowSeriesRequestBodyData
class QueryFlowSeriesRequest(StrictModel):
    """Retrieve time-series analytics data for flows, including performance metrics like opens, clicks, and conversions aggregated at your specified interval over a given timeframe."""
    header: QueryFlowSeriesRequestHeader
    body: QueryFlowSeriesRequestBody

# Operation: query_form_values_report
class QueryFormValuesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class QueryFormValuesRequestBodyDataAttributes(StrictModel):
    statistics: list[Literal["closed_form", "closed_form_uniques", "qualified_form", "qualified_form_uniques", "submit_rate", "submits", "submitted_form_step", "submitted_form_step_uniques", "viewed_form", "viewed_form_step", "viewed_form_step_uniques", "viewed_form_uniques"]] = Field(default=..., validation_alias="statistics", serialization_alias="statistics", description="One or more statistics to retrieve for the specified time period. Rate statistics are returned as decimal values between 0.0 and 1.0. Examples include 'viewed_form' and 'submit_rate'.")
    timeframe: Timeframe | CustomTimeframe = Field(default=..., validation_alias="timeframe", serialization_alias="timeframe", description="The time period for which to retrieve data, with a maximum span of 1 year. Use the available time frame formats documented in the reporting API overview.")
    group_by: list[Literal["form_id", "form_version_id"]] | None = Field(default=None, validation_alias="group_by", serialization_alias="group_by", description="Optional list of attributes to group results by. Supported values are 'form_id' and 'form_version_id'. Defaults to 'form_id' if not provided. When grouping by 'form_version_id', 'form_id' must also be included.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results by form_id or form_version_id using equals or any operators. Combine multiple filters with AND. The 'any' operator supports up to 100 values per filter.")
class QueryFormValuesRequestBodyData(StrictModel):
    type_: Literal["form-values-report"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of report to query. Must be 'form-values-report' to retrieve form analytics data.")
    attributes: QueryFormValuesRequestBodyDataAttributes
class QueryFormValuesRequestBody(StrictModel):
    data: QueryFormValuesRequestBodyData
class QueryFormValuesRequest(StrictModel):
    """Retrieve form analytics data including submission rates, views, and other performance metrics. Results can be filtered by form and grouped by form or form version over a specified time period (up to 1 year)."""
    header: QueryFormValuesRequestHeader
    body: QueryFormValuesRequestBody

# Operation: get_form_series_analytics
class QueryFormSeriesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15).")
class QueryFormSeriesRequestBodyDataAttributes(StrictModel):
    statistics: list[Literal["closed_form", "closed_form_uniques", "qualified_form", "qualified_form_uniques", "submit_rate", "submits", "submitted_form_step", "submitted_form_step_uniques", "viewed_form", "viewed_form_step", "viewed_form_step_uniques", "viewed_form_uniques"]] = Field(default=..., validation_alias="statistics", serialization_alias="statistics", description="List of statistics to retrieve (e.g., 'viewed_form', 'submit_rate'). Rate statistics are returned as decimal values between 0.0 and 1.0.")
    timeframe: Timeframe | CustomTimeframe = Field(default=..., validation_alias="timeframe", serialization_alias="timeframe", description="The time period for data retrieval, with a maximum span of 1 year. Refer to available time frames in the reporting API documentation.")
    interval: Literal["daily", "hourly", "monthly", "weekly"] = Field(default=..., validation_alias="interval", serialization_alias="interval", description="Aggregation interval for the data series. Hourly intervals are limited to 7-day timeframes, daily to 60 days, and monthly to 52 weeks.")
    group_by: list[Literal["form_id", "form_version_id"]] | None = Field(default=None, validation_alias="group_by", serialization_alias="group_by", description="Optional list of attributes to group results by (form_id or form_version_id). Defaults to form_id if not specified. When grouping by form_version_id, form_id must also be included.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter expression to narrow results by form_id or form_version_id using equals or any operators. Combine multiple filters with AND; any operator supports up to 100 values.")
class QueryFormSeriesRequestBodyData(StrictModel):
    type_: Literal["form-series-report"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of report to query; must be 'form-series-report'.")
    attributes: QueryFormSeriesRequestBodyDataAttributes
class QueryFormSeriesRequestBody(StrictModel):
    data: QueryFormSeriesRequestBodyData
class QueryFormSeriesRequest(StrictModel):
    """Retrieve time-series analytics data for forms, including metrics like view counts and submission rates aggregated over your specified timeframe and interval."""
    header: QueryFormSeriesRequestHeader
    body: QueryFormSeriesRequestBody

# Operation: get_segment_values_report
class QuerySegmentValuesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use.")
class QuerySegmentValuesRequestBodyDataAttributes(StrictModel):
    statistics: list[Literal["members_added", "members_removed", "net_members_changed", "total_members"]] = Field(default=..., validation_alias="statistics", serialization_alias="statistics", description="Array of metric names to retrieve for each segment. Examples include 'total_members' and 'net_members_changed'. At least one statistic is required.")
    timeframe: Timeframe | CustomTimeframe = Field(default=..., validation_alias="timeframe", serialization_alias="timeframe", description="Time period for the report query. Must span no more than 1 year and cannot include dates before June 1st, 2023. Use ISO 8601 format or refer to available timeframe options in the API documentation.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter to narrow results to specific segments. Use 'equals' operator for a single segment ID or 'any' operator to include up to 100 segment IDs. Only one filter per attribute is allowed.")
class QuerySegmentValuesRequestBodyData(StrictModel):
    type_: Literal["segment-values-report"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Report type identifier. Must be set to 'segment-values-report' to query segment analytics data.")
    attributes: QuerySegmentValuesRequestBodyDataAttributes
class QuerySegmentValuesRequestBody(StrictModel):
    data: QuerySegmentValuesRequestBodyData
class QuerySegmentValuesRequest(StrictModel):
    """Retrieve analytics data for segment values across specified statistics and timeframe. Returns aggregated metrics like member counts and changes for one or more segments."""
    header: QuerySegmentValuesRequestHeader
    body: QuerySegmentValuesRequestBody

# Operation: get_segment_series_report
class QuerySegmentSeriesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Controls the API contract version used for this request.")
class QuerySegmentSeriesRequestBodyDataAttributes(StrictModel):
    statistics: list[Literal["members_added", "members_removed", "net_members_changed", "total_members"]] = Field(default=..., validation_alias="statistics", serialization_alias="statistics", description="Array of metric names to retrieve for each time period. Common metrics include total_members and net_members_changed. Order is preserved in results.")
    timeframe: Timeframe | CustomTimeframe = Field(default=..., validation_alias="timeframe", serialization_alias="timeframe", description="Time range for the report. Must span no longer than 1 year and cannot include dates before June 1st, 2023. Use ISO 8601 date format or relative time frame identifiers as documented in the reporting API overview.")
    interval: Literal["daily", "hourly", "monthly", "weekly"] = Field(default=..., validation_alias="interval", serialization_alias="interval", description="Aggregation granularity for the time series. Hourly intervals are limited to 7-day windows, daily to 60 days, weekly to 1 year, and monthly to 52 weeks. Choose based on your timeframe and desired detail level.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter to narrow results to specific segments. Use 'equals' for a single segment ID or 'any' to include up to 100 segment IDs. Format: any(segment_id,[\"id1\",\"id2\"]) or equals(segment_id,\"id\").")
class QuerySegmentSeriesRequestBodyData(StrictModel):
    type_: Literal["segment-series-report"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Report type identifier. Must be set to 'segment-series-report' to query segment analytics series data.")
    attributes: QuerySegmentSeriesRequestBodyDataAttributes
class QuerySegmentSeriesRequestBody(StrictModel):
    data: QuerySegmentSeriesRequestBodyData
class QuerySegmentSeriesRequest(StrictModel):
    """Retrieve time-series analytics data for one or more segments, aggregated at your specified interval. Supports filtering by segment ID and covers data from June 1st, 2023 onward, with a maximum lookback period of 1 year."""
    header: QuerySegmentSeriesRequestHeader
    body: QuerySegmentSeriesRequestBody

# Operation: list_reviews
class GetReviewsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter reviews using comparison and matching operators. Supports filtering by creation date (date range), rating (any value, equals, or range), IDs, content keywords, status, review type, and verification status. Use the format specified in the Klaviyo filtering documentation.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of reviews to return per page. Defaults to 20 results; must be between 1 and 100.", ge=1, le=100)
class GetReviewsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15.")
class GetReviewsRequest(StrictModel):
    """Retrieve all reviews with optional filtering and pagination. Supports filtering by creation date, rating, ID, item ID, content, status, review type, and verification status."""
    query: GetReviewsRequestQuery | None = None
    header: GetReviewsRequestHeader

# Operation: get_review
class GetReviewRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the review to retrieve (e.g., '2134228')")
class GetReviewRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this request.")
class GetReviewRequest(StrictModel):
    """Retrieve a specific review by its ID. Returns the full review details including content, metadata, and associated information."""
    path: GetReviewRequestPath
    header: GetReviewRequestHeader

# Operation: update_review
class UpdateReviewRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the review to update. Must match the review ID provided in the request body.")
class UpdateReviewRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which API version to use for this operation.")
class UpdateReviewRequestBodyDataAttributes(StrictModel):
    status: ReviewStatusRejected | ReviewStatusFeatured | ReviewStatusPublished | ReviewStatusUnpublished | ReviewStatusPending | None = Field(default=None, validation_alias="status", serialization_alias="status", description="The new status to assign to the review. Valid status values depend on the review workflow configuration.")
class UpdateReviewRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the review being updated. Must match the path ID parameter.")
    type_: Literal["review"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'review' to indicate this operation targets a review resource.")
    attributes: UpdateReviewRequestBodyDataAttributes | None = None
class UpdateReviewRequestBody(StrictModel):
    """DTO for updating reviews"""
    data: UpdateReviewRequestBodyData
class UpdateReviewRequest(StrictModel):
    """Update an existing review by its ID. Requires the review:write scope and respects rate limits of 10 requests per second (burst) and 150 requests per minute (steady state)."""
    path: UpdateReviewRequestPath
    header: UpdateReviewRequestHeader
    body: UpdateReviewRequestBody

# Operation: list_segments
class GetSegmentsRequestQuery(StrictModel):
    fields_segment: list[Literal["created", "definition", "definition.condition_groups", "is_active", "is_processing", "is_starred", "name", "updated"]] | None = Field(default=None, validation_alias="fields[segment]", serialization_alias="fields[segment]", description="Specify which segment fields to include in the response using sparse fieldsets for optimized data retrieval.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter segments by name, ID, creation date, update date, active status, or starred status. Supports exact matching and partial matching operators depending on the field.")
class GetSegmentsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetSegmentsRequest(StrictModel):
    """Retrieve all segments in an account with optional filtering and field selection. Returns up to 10 results per page."""
    query: GetSegmentsRequestQuery | None = None
    header: GetSegmentsRequestHeader

# Operation: create_segment
class CreateSegmentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class CreateSegmentRequestBodyDataAttributesDefinition(StrictModel):
    condition_groups: list[ConditionGroup] = Field(default=..., validation_alias="condition_groups", serialization_alias="condition_groups", description="An array of condition groups that define the segment's matching criteria. Each group contains conditions that users must satisfy to be included in the segment.")
class CreateSegmentRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A descriptive name for the segment that identifies its purpose or target audience.")
    is_starred: bool | None = Field(default=None, validation_alias="is_starred", serialization_alias="is_starred", description="Optional flag to mark the segment as starred for quick access. Defaults to false if not specified.")
    definition: CreateSegmentRequestBodyDataAttributesDefinition
class CreateSegmentRequestBodyData(StrictModel):
    type_: Literal["segment"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, which must be 'segment' for this operation.")
    attributes: CreateSegmentRequestBodyDataAttributes
class CreateSegmentRequestBody(StrictModel):
    data: CreateSegmentRequestBodyData
class CreateSegmentRequest(StrictModel):
    """Create a new audience segment defined by condition groups. Segments are used to target specific groups of users based on matching criteria."""
    header: CreateSegmentRequestHeader
    body: CreateSegmentRequestBody

# Operation: get_segment
class GetSegmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the segment to retrieve.")
class GetSegmentRequestQuery(StrictModel):
    fields_segment: list[Literal["created", "definition", "definition.condition_groups", "is_active", "is_processing", "is_starred", "name", "profile_count", "updated"]] | None = Field(default=None, validation_alias="fields[segment]", serialization_alias="fields[segment]", description="Optional list of segment fields to include in the response. Use sparse fieldsets to optimize payload size and performance. Refer to the API overview documentation for available fields.")
class GetSegmentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (e.g., 2026-01-15), optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class GetSegmentRequest(StrictModel):
    """Retrieve a segment by its ID. Optionally include additional fields like profile count, which has stricter rate limits."""
    path: GetSegmentRequestPath
    query: GetSegmentRequestQuery | None = None
    header: GetSegmentRequestHeader

# Operation: update_segment
class UpdateSegmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the segment to update.")
class UpdateSegmentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15).")
class UpdateSegmentRequestBodyDataAttributesDefinition(StrictModel):
    condition_groups: list[ConditionGroup] = Field(default=..., validation_alias="condition_groups", serialization_alias="condition_groups", description="Array of condition groups that define the segment's membership criteria. Order may be significant for evaluation logic.")
class UpdateSegmentRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="Human-readable name for the segment.")
    is_starred: bool | None = Field(default=None, validation_alias="is_starred", serialization_alias="is_starred", description="Whether to star/favorite this segment for quick access.")
    is_active: bool | None = Field(default=None, validation_alias="is_active", serialization_alias="is_active", description="Activation status of the segment. Set to false to deactivate (this must be the only attribute in the request); set to true to reactivate. Deactivating impacts campaigns, flows, ad syncs, forms, helpdesk routing, and other dependent features.")
    definition: UpdateSegmentRequestBodyDataAttributesDefinition
class UpdateSegmentRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The segment's unique identifier, must match the segment being updated.")
    type_: Literal["segment"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type, must be set to 'segment'.")
    attributes: UpdateSegmentRequestBodyDataAttributes
class UpdateSegmentRequestBody(StrictModel):
    data: UpdateSegmentRequestBodyData
class UpdateSegmentRequest(StrictModel):
    """Update an existing segment's configuration, including name, activation status, and condition groups. Note: deactivation must be performed as a standalone operation and cannot be combined with other updates."""
    path: UpdateSegmentRequestPath
    header: UpdateSegmentRequestHeader
    body: UpdateSegmentRequestBody

# Operation: delete_segment
class DeleteSegmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the segment to delete.")
class DeleteSegmentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v2). Defaults to 2026-01-15 if not specified.")
class DeleteSegmentRequest(StrictModel):
    """Permanently delete a segment by its ID. Requires the segment's current revision to ensure safe deletion and prevent conflicts from concurrent modifications."""
    path: DeleteSegmentRequestPath
    header: DeleteSegmentRequestHeader

# Operation: list_tags_for_segment
class GetTagsForSegmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the segment for which to retrieve associated tags.")
class GetTagsForSegmentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15). Specifies which version of the API contract to use.")
class GetTagsForSegmentRequest(StrictModel):
    """Retrieve all tags associated with a specific segment. Returns a collection of tags linked to the given segment ID."""
    path: GetTagsForSegmentRequestPath
    header: GetTagsForSegmentRequestHeader

# Operation: list_tag_ids_for_segment
class GetTagIdsForSegmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the segment for which to retrieve associated tag IDs.")
class GetTagIdsForSegmentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetTagIdsForSegmentRequest(StrictModel):
    """Retrieve all tag IDs associated with a specific segment. Returns a collection of tag identifiers linked to the given segment."""
    path: GetTagIdsForSegmentRequestPath
    header: GetTagIdsForSegmentRequestHeader

# Operation: list_profiles_for_segment
class GetProfilesForSegmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique segment identifier generated by Klaviyo (e.g., 'Y6nRLr').")
class GetProfilesForSegmentRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter profiles by profile_id, email, phone_number, push_token, _kx, or joined_group_at. Use operators like 'equals', 'any', 'greater-than', 'less-than', etc. For details on filter syntax, see the API documentation.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of profiles to return per page. Must be between 1 and 100 (default: 20).", ge=1, le=100)
class GetProfilesForSegmentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (default: 2026-01-15).")
class GetProfilesForSegmentRequest(StrictModel):
    """Retrieve all profiles within a specific segment. Optionally filter and sort results to find profiles matching specific criteria like email, phone number, or join date."""
    path: GetProfilesForSegmentRequestPath
    query: GetProfilesForSegmentRequestQuery | None = None
    header: GetProfilesForSegmentRequestHeader

# Operation: list_profile_ids_for_segment
class GetProfileIdsForSegmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the segment. This is a Klaviyo-generated ID (e.g., 'Y6nRLr').")
class GetProfileIdsForSegmentRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results by profile attributes or membership metadata. Supports filtering by profile_id, email, phone_number, push_token, _kx identifier, or joined_group_at timestamp. Use operators like 'equals' for exact matches or 'any' for multiple values, and comparison operators (greater-than, less-than, etc.) for date ranges.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of results per page. Must be between 1 and 100, with a default of 20.", ge=1, le=100)
class GetProfileIdsForSegmentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (e.g., '2026-01-15'). Defaults to the latest stable version.")
class GetProfileIdsForSegmentRequest(StrictModel):
    """Retrieve all profile IDs that are members of a specific segment. Use filtering and pagination to narrow results and manage large datasets."""
    path: GetProfileIdsForSegmentRequestPath
    query: GetProfileIdsForSegmentRequestQuery | None = None
    header: GetProfileIdsForSegmentRequestHeader

# Operation: list_flows_triggered_by_segment
class GetFlowsTriggeredBySegmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the segment. This is a Klaviyo-generated primary key (e.g., 'Y6nRLr').")
class GetFlowsTriggeredBySegmentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetFlowsTriggeredBySegmentRequest(StrictModel):
    """Retrieve all automation flows that are triggered by a specific segment. This operation identifies which flows use the given segment as their entry point trigger."""
    path: GetFlowsTriggeredBySegmentRequestPath
    header: GetFlowsTriggeredBySegmentRequestHeader

# Operation: list_flow_ids_triggered_by_segment
class GetIdsForFlowsTriggeredBySegmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the segment, generated by Klaviyo (e.g., 'Y6nRLr'). This segment will be checked to find all flows using it as a trigger.")
class GetIdsForFlowsTriggeredBySegmentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format (or with an optional suffix). Defaults to 2026-01-15 if not specified.")
class GetIdsForFlowsTriggeredBySegmentRequest(StrictModel):
    """Retrieve the IDs of all flows that use the specified segment as their trigger condition. This helps identify which automation workflows are activated by a particular audience segment."""
    path: GetIdsForFlowsTriggeredBySegmentRequestPath
    header: GetIdsForFlowsTriggeredBySegmentRequestHeader

# Operation: list_tags
class GetTagsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter tags by name using comparison operators (equals, contains, starts-with, ends-with). For example, filter by exact name match or partial name patterns.")
class GetTagsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetTagsRequest(StrictModel):
    """Retrieve all tags in an account with optional filtering and sorting. Results are paginated with a maximum of 50 tags per request."""
    query: GetTagsRequestQuery | None = None
    header: GetTagsRequestHeader

# Operation: create_tag
class CreateTagRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class CreateTagRequestBodyDataRelationshipsTagGroupData(StrictModel):
    type_: Literal["tag-group"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier for the tag group relationship. Must be set to 'tag-group'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the tag group to associate this tag with. If omitted, the tag will be assigned to your account's default tag group. Provide a UUID-formatted identifier.")
class CreateTagRequestBodyDataRelationshipsTagGroup(StrictModel):
    data: CreateTagRequestBodyDataRelationshipsTagGroupData
class CreateTagRequestBodyDataRelationships(StrictModel):
    tag_group: CreateTagRequestBodyDataRelationshipsTagGroup = Field(default=..., validation_alias="tag-group", serialization_alias="tag-group")
class CreateTagRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The name of the tag being created. This is a user-facing label for organizing and categorizing items.")
class CreateTagRequestBodyData(StrictModel):
    type_: Literal["tag"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'tag'.")
    relationships: CreateTagRequestBodyDataRelationships
    attributes: CreateTagRequestBodyDataAttributes
class CreateTagRequestBody(StrictModel):
    data: CreateTagRequestBodyData
class CreateTagRequest(StrictModel):
    """Create a new tag within your account. Tags are organized into tag groups; if no tag group is specified, the tag will be added to your account's default tag group. Note: accounts are limited to 500 unique tags."""
    header: CreateTagRequestHeader
    body: CreateTagRequestBody

# Operation: get_tag
class GetTagRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the tag to retrieve, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class GetTagRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified.")
class GetTagRequest(StrictModel):
    """Retrieve a specific tag by its ID. Requires the tags:read scope and is subject to rate limits of 3 requests per second (burst) and 60 requests per minute (steady state)."""
    path: GetTagRequestPath
    header: GetTagRequestHeader

# Operation: update_tag
class UpdateTagRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to update, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class UpdateTagRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class UpdateTagRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The new name for the tag. Can be any string value (e.g., 'My Tag').")
class UpdateTagRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag being updated, formatted as a UUID. Must match the tag ID in the path parameter.")
    type_: Literal["tag"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'tag' for this operation.")
    attributes: UpdateTagRequestBodyDataAttributes
class UpdateTagRequestBody(StrictModel):
    data: UpdateTagRequestBodyData
class UpdateTagRequest(StrictModel):
    """Update a tag's name by its ID. Only the tag name can be modified; tags cannot be moved between tag groups."""
    path: UpdateTagRequestPath
    header: UpdateTagRequestHeader
    body: UpdateTagRequestBody

# Operation: delete_tag
class DeleteTagRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to delete, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class DeleteTagRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified.")
class DeleteTagRequest(StrictModel):
    """Permanently delete a tag by its ID. This operation removes the tag and all its associations with other resources."""
    path: DeleteTagRequestPath
    header: DeleteTagRequestHeader

# Operation: list_tag_groups
class GetTagGroupsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter tag groups by name (using contains, ends-with, equals, or starts-with matching), exclusivity status, or default status. Provide filter expressions in the format: operator(field,'value').")
class GetTagGroupsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetTagGroupsRequest(StrictModel):
    """Retrieve all tag groups in an account with optional filtering and sorting. Every account includes one default tag group, and results are paginated with a maximum of 25 tag groups per request."""
    query: GetTagGroupsRequestQuery | None = None
    header: GetTagGroupsRequestHeader

# Operation: create_tag_group
class CreateTagGroupRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class CreateTagGroupRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A descriptive name for the tag group. This is the human-readable identifier used to reference the tag group.")
    exclusive: bool | None = Field(default=None, validation_alias="exclusive", serialization_alias="exclusive", description="Controls whether resources can be linked to multiple tags within this group. When true, resources can only be linked to one tag; when false (default), resources can be linked to multiple tags from this group.")
class CreateTagGroupRequestBodyData(StrictModel):
    type_: Literal["tag-group"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'tag-group' for this operation.")
    attributes: CreateTagGroupRequestBodyDataAttributes
class CreateTagGroupRequestBody(StrictModel):
    data: CreateTagGroupRequestBodyData
class CreateTagGroupRequest(StrictModel):
    """Create a new tag group to organize and categorize tags within your account. Tag groups can be configured as exclusive (allowing only one tag per resource) or non-exclusive (allowing multiple tags per resource). Accounts are limited to 50 unique tag groups."""
    header: CreateTagGroupRequestHeader
    body: CreateTagGroupRequestBody

# Operation: get_tag_group
class GetTagGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag group to retrieve, formatted as a UUID (e.g., zyxw9876-vu54-ts32-rq10-zyxwvu654321).")
class GetTagGroupRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetTagGroupRequest(StrictModel):
    """Retrieve a specific tag group by its ID. Requires read access to tags and supports API versioning through the revision parameter."""
    path: GetTagGroupRequestPath
    header: GetTagGroupRequestHeader

# Operation: update_tag_group
class UpdateTagGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag group to update, formatted as a UUID.")
class UpdateTagGroupRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15).")
class UpdateTagGroupRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="The new name for the tag group. This is the only updatable field.")
    return_fields: list[str] | None = Field(default=None, validation_alias="return_fields", serialization_alias="return_fields", description="Optional list of fields to include in the response. If not specified, default fields are returned.")
class UpdateTagGroupRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The tag group ID being updated; must match the ID in the path parameter.")
    type_: Literal["tag-group"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier; must be set to 'tag-group'.")
    attributes: UpdateTagGroupRequestBodyDataAttributes
class UpdateTagGroupRequestBody(StrictModel):
    data: UpdateTagGroupRequestBodyData
class UpdateTagGroupRequest(StrictModel):
    """Update a tag group's name by ID. Only the name field can be modified; exclusive and default properties are immutable after creation."""
    path: UpdateTagGroupRequestPath
    header: UpdateTagGroupRequestHeader
    body: UpdateTagGroupRequestBody

# Operation: delete_tag_group
class DeleteTagGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag group to delete, formatted as a UUID (e.g., zyxw9876-vu54-ts32-rq10-zyxwvu654321).")
class DeleteTagGroupRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class DeleteTagGroupRequest(StrictModel):
    """Permanently delete a tag group and all associated tags and their relationships with other resources. Note that the default tag group cannot be deleted."""
    path: DeleteTagGroupRequestPath
    header: DeleteTagGroupRequestHeader

# Operation: list_flows_for_tag
class GetFlowIdsForTagRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag. Must be a valid UUID in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.")
class GetFlowIdsForTagRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetFlowIdsForTagRequest(StrictModel):
    """Retrieve all flow IDs associated with a specific tag. Returns a collection of flow identifiers linked to the given tag."""
    path: GetFlowIdsForTagRequestPath
    header: GetFlowIdsForTagRequestHeader

# Operation: add_flows_to_tag
class TagFlowsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to associate with flows, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class TagFlowsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class TagFlowsRequestBody(StrictModel):
    data: list[TagFlowsBodyDataItem] = Field(default=..., description="Array of flow IDs to associate with the tag. Each ID should be a valid flow identifier; order is not significant.")
class TagFlowsRequest(StrictModel):
    """Associate one or more flows with a tag. Each flow can be tagged with up to 100 tags maximum."""
    path: TagFlowsRequestPath
    header: TagFlowsRequestHeader
    body: TagFlowsRequestBody

# Operation: remove_tag_from_flows
class RemoveTagFromFlowsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to remove from flows, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class RemoveTagFromFlowsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class RemoveTagFromFlowsRequestBody(StrictModel):
    data: list[RemoveTagFromFlowsBodyDataItem] = Field(default=..., description="An array of flow IDs to remove the tag association from. Each item should be a flow ID string. Order is not significant.")
class RemoveTagFromFlowsRequest(StrictModel):
    """Remove a tag's association with one or more flows by specifying the flow IDs in the request body. This operation breaks the relationship between the tag and the specified flows."""
    path: RemoveTagFromFlowsRequestPath
    header: RemoveTagFromFlowsRequestHeader
    body: RemoveTagFromFlowsRequestBody

# Operation: list_campaign_ids_for_tag
class GetCampaignIdsForTagRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag. Must be a valid UUID in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.")
class GetCampaignIdsForTagRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetCampaignIdsForTagRequest(StrictModel):
    """Retrieve all campaign IDs associated with a specific tag. Use this to discover which campaigns are linked to a given tag."""
    path: GetCampaignIdsForTagRequestPath
    header: GetCampaignIdsForTagRequestHeader

# Operation: add_campaigns_to_tag
class TagCampaignsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to associate with campaigns. Use UUID format (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class TagCampaignsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class TagCampaignsRequestBody(StrictModel):
    data: list[TagCampaignsBodyDataItem] = Field(default=..., description="Array of campaign IDs to associate with the tag. Each ID should be a valid campaign identifier. Order is not significant.")
class TagCampaignsRequest(StrictModel):
    """Associate one or more campaigns with a tag. Each campaign can be tagged with up to 100 tags maximum."""
    path: TagCampaignsRequestPath
    header: TagCampaignsRequestHeader
    body: TagCampaignsRequestBody

# Operation: remove_tag_from_campaigns
class RemoveTagFromCampaignsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to disassociate from campaigns, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class RemoveTagFromCampaignsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class RemoveTagFromCampaignsRequestBody(StrictModel):
    data: list[RemoveTagFromCampaignsBodyDataItem] = Field(default=..., description="An array of campaign IDs to remove from the tag's associations. Each item should be a campaign identifier.")
class RemoveTagFromCampaignsRequest(StrictModel):
    """Remove a tag's association with one or more campaigns by specifying the campaign IDs in the request body."""
    path: RemoveTagFromCampaignsRequestPath
    header: RemoveTagFromCampaignsRequestHeader
    body: RemoveTagFromCampaignsRequestBody

# Operation: list_lists_for_tag
class GetListIdsForTagRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag. Must be a valid UUID in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.")
class GetListIdsForTagRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetListIdsForTagRequest(StrictModel):
    """Retrieve all list IDs associated with a specific tag. Returns a collection of list identifiers linked to the given tag."""
    path: GetListIdsForTagRequestPath
    header: GetListIdsForTagRequestHeader

# Operation: associate_lists_with_tag
class TagListsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to associate with lists, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class TagListsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class TagListsRequestBody(StrictModel):
    data: list[TagListsBodyDataItem] = Field(default=..., description="An array of list IDs to associate with the tag. Each ID should be a valid list identifier.")
class TagListsRequest(StrictModel):
    """Associate one or more lists with a tag. Each list can be associated with a maximum of 100 tags."""
    path: TagListsRequestPath
    header: TagListsRequestHeader
    body: TagListsRequestBody

# Operation: remove_tag_from_lists
class RemoveTagFromListsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to remove from lists, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class RemoveTagFromListsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class RemoveTagFromListsRequestBody(StrictModel):
    data: list[RemoveTagFromListsBodyDataItem] = Field(default=..., description="An array of list IDs to disassociate from the tag. Each item should be a list identifier; order is not significant.")
class RemoveTagFromListsRequest(StrictModel):
    """Remove a tag's association with one or more lists by specifying the list IDs in the request body."""
    path: RemoveTagFromListsRequestPath
    header: RemoveTagFromListsRequestHeader
    body: RemoveTagFromListsRequestBody

# Operation: list_segment_ids_for_tag
class GetSegmentIdsForTagRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag. Must be a valid UUID in the format xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.")
class GetSegmentIdsForTagRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetSegmentIdsForTagRequest(StrictModel):
    """Retrieve all segment IDs associated with a specific tag. Returns a collection of segment identifiers linked to the given tag."""
    path: GetSegmentIdsForTagRequestPath
    header: GetSegmentIdsForTagRequestHeader

# Operation: add_segments_to_tag
class TagSegmentsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to associate with segments. Use UUID format (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class TagSegmentsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class TagSegmentsRequestBody(StrictModel):
    data: list[TagSegmentsBodyDataItem] = Field(default=..., description="Array of segment IDs to associate with the tag. Each ID should be a valid segment identifier. Order is not significant.")
class TagSegmentsRequest(StrictModel):
    """Associate one or more segments with a tag. Each segment can be tagged with a maximum of 100 tags total."""
    path: TagSegmentsRequestPath
    header: TagSegmentsRequestHeader
    body: TagSegmentsRequestBody

# Operation: remove_tag_from_segments
class RemoveTagFromSegmentsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag to disassociate from segments, formatted as a UUID (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class RemoveTagFromSegmentsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class RemoveTagFromSegmentsRequestBody(StrictModel):
    data: list[RemoveTagFromSegmentsBodyDataItem] = Field(default=..., description="An array of segment IDs to remove from the tag's associations. Each item should be a segment identifier.")
class RemoveTagFromSegmentsRequest(StrictModel):
    """Remove a tag's association with one or more segments by specifying the segment IDs in the request body."""
    path: RemoveTagFromSegmentsRequestPath
    header: RemoveTagFromSegmentsRequestHeader
    body: RemoveTagFromSegmentsRequestBody

# Operation: get_tag_group_for_tag
class GetTagGroupForTagRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag in UUID format (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class GetTagGroupForTagRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified.")
class GetTagGroupForTagRequest(StrictModel):
    """Retrieves the tag group resource associated with a specific tag. Use this to find the parent group classification for a given tag ID."""
    path: GetTagGroupForTagRequestPath
    header: GetTagGroupForTagRequestHeader

# Operation: get_tag_group_id_for_tag
class GetTagGroupIdForTagRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag in UUID format (e.g., abcd1234-ef56-gh78-ij90-abcdef123456).")
class GetTagGroupIdForTagRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified.")
class GetTagGroupIdForTagRequest(StrictModel):
    """Retrieves the ID of the tag group associated with a specific tag. Use this to determine which tag group a tag belongs to."""
    path: GetTagGroupIdForTagRequestPath
    header: GetTagGroupIdForTagRequestHeader

# Operation: list_tags_for_tag_group
class GetTagsForTagGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag group. Use the tag group ID in UUID format (e.g., zyxw9876-vu54-ts32-rq10-zyxwvu654321).")
class GetTagsForTagGroupRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetTagsForTagGroupRequest(StrictModel):
    """Retrieve all tags associated with a specific tag group. Returns a collection of tags organized under the given tag group ID."""
    path: GetTagsForTagGroupRequestPath
    header: GetTagsForTagGroupRequestHeader

# Operation: list_tag_ids_for_tag_group
class GetTagIdsForTagGroupRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the tag group. Use the tag group ID in UUID format (e.g., zyxw9876-vu54-ts32-rq10-zyxwvu654321).")
class GetTagIdsForTagGroupRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified.")
class GetTagIdsForTagGroupRequest(StrictModel):
    """Retrieve all tag IDs contained within a specific tag group. This operation returns a collection of tag identifiers that belong to the given tag group."""
    path: GetTagIdsForTagGroupRequestPath
    header: GetTagIdsForTagGroupRequestHeader

# Operation: list_templates
class GetTemplatesRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter templates by id, name, created date, or updated date. Supports exact matching, partial text search, and date range comparisons. See API documentation for filter syntax details.")
class GetTemplatesRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API revision date in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetTemplatesRequest(StrictModel):
    """Retrieve all templates in your account with optional filtering and sorting. Results are paginated with a maximum of 10 templates per page."""
    query: GetTemplatesRequestQuery | None = None
    header: GetTemplatesRequestHeader

# Operation: create_template
class CreateTemplateRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15.")
class CreateTemplateRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="Human-readable name for the template (e.g., 'Monthly Newsletter Template').")
    editor_type: str = Field(default=..., validation_alias="editor_type", serialization_alias="editor_type", description="Template editor type. Must be either CODE (for custom HTML editing) or USER_DRAGGABLE (for visual drag-and-drop editor).")
    html: str | None = Field(default=None, validation_alias="html", serialization_alias="html", description="The HTML markup content of the template. Provide a complete, valid HTML document structure.")
    text: str | None = Field(default=None, validation_alias="text", serialization_alias="text", description="Plain text version of the template content, used as a fallback for email clients that don't support HTML.")
    amp: str | None = Field(default=None, validation_alias="amp", serialization_alias="amp", description="AMP (Accelerated Mobile Pages) version of the template for dynamic email content. Requires AMP Email to be enabled in your account; refer to the AMP Email setup guide for configuration details.")
class CreateTemplateRequestBodyData(StrictModel):
    type_: Literal["template"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier. Must be set to 'template'.")
    attributes: CreateTemplateRequestBodyDataAttributes
class CreateTemplateRequestBody(StrictModel):
    data: CreateTemplateRequestBodyData
class CreateTemplateRequest(StrictModel):
    """Create a new custom HTML email template. Note that accounts are limited to 1,000 templates via the API; creation will fail if this limit is reached."""
    header: CreateTemplateRequestHeader
    body: CreateTemplateRequestBody

# Operation: get_template
class GetTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template to retrieve.")
class GetTemplateRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class GetTemplateRequest(StrictModel):
    """Retrieve a specific template by its ID. Returns the template configuration and metadata for the requested template."""
    path: GetTemplateRequestPath
    header: GetTemplateRequestHeader

# Operation: update_template
class UpdateTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template to update. Must match the ID provided in the request body.")
class UpdateTemplateRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to 2026-01-15 if not specified.")
class UpdateTemplateRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The display name for the template (e.g., 'Monthly Newsletter Template'). Optional field for updating template identification.")
    html: str | None = Field(default=None, validation_alias="html", serialization_alias="html", description="The HTML markup content of the template. Provide complete, valid HTML structure. Optional field for updating template rendering.")
    text: str | None = Field(default=None, validation_alias="text", serialization_alias="text", description="The plaintext version of the template content. Used as fallback for email clients that don't support HTML. Optional field for updating template text representation.")
    amp: str | None = Field(default=None, validation_alias="amp", serialization_alias="amp", description="The AMP for Email version of the template. Requires AMP Email to be enabled in your Klaviyo account to use. Refer to the AMP Email setup guide for implementation details. Optional field for updating dynamic email content.")
class UpdateTemplateRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template being updated. Must match the path ID parameter.")
    type_: Literal["template"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier. Must be set to 'template'.")
    attributes: UpdateTemplateRequestBodyDataAttributes | None = None
class UpdateTemplateRequestBody(StrictModel):
    data: UpdateTemplateRequestBodyData
class UpdateTemplateRequest(StrictModel):
    """Update an existing email template by ID. Allows modification of template name, HTML content, plaintext version, and AMP email format. Note: drag & drop templates are not currently supported for updates."""
    path: UpdateTemplateRequestPath
    header: UpdateTemplateRequestHeader
    body: UpdateTemplateRequestBody

# Operation: delete_template
class DeleteTemplateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template to delete.")
class DeleteTemplateRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class DeleteTemplateRequest(StrictModel):
    """Permanently delete a template by its ID. This operation requires the template ID and API revision to ensure the correct version is targeted."""
    path: DeleteTemplateRequestPath
    header: DeleteTemplateRequestHeader

# Operation: list_universal_content
class GetAllUniversalContentRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results using Klaviyo's filter syntax. Supports filtering by ID, name, creation/update timestamps (with comparison operators), content type, and definition type. See Klaviyo's filtering documentation for syntax details.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of results to return per page. Must be between 1 and 100 items; defaults to 20 if not specified.", ge=1, le=100)
class GetAllUniversalContentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not provided.")
class GetAllUniversalContentRequest(StrictModel):
    """Retrieve all universal content items in your account. Supports filtering by ID, name, creation/update dates, and content type, with pagination for managing large result sets."""
    query: GetAllUniversalContentRequestQuery | None = None
    header: GetAllUniversalContentRequestHeader

# Operation: create_universal_content
class CreateUniversalContentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)")
class CreateUniversalContentRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A descriptive name for this universal content block")
    definition: ButtonBlock | DropShadowBlock | HorizontalRuleBlock | HtmlBlock | ImageBlock | SpacerBlock | TextBlock = Field(default=..., validation_alias="definition", serialization_alias="definition", description="The block configuration object defining the content structure and properties. Supported block types are: button, drop_shadow, horizontal_rule, html, image, spacer, and text")
class CreateUniversalContentRequestBodyData(StrictModel):
    type_: Literal["template-universal-content"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier, must be set to 'template-universal-content'")
    attributes: CreateUniversalContentRequestBodyDataAttributes
class CreateUniversalContentRequestBody(StrictModel):
    """Create a template universal content"""
    data: CreateUniversalContentRequestBodyData
class CreateUniversalContentRequest(StrictModel):
    """Create a universal content block for use in templates. Supports multiple block types including buttons, images, text, HTML, spacing elements, and decorative components."""
    header: CreateUniversalContentRequestHeader
    body: CreateUniversalContentRequestBody

# Operation: get_universal_content
class GetUniversalContentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the universal content template to retrieve (e.g., 01HWWWKAW4RHXQJCMW4R2KRYR4).")
class GetUniversalContentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class GetUniversalContentRequest(StrictModel):
    """Retrieve a specific universal content template by its ID. Returns the template configuration and content for the specified revision."""
    path: GetUniversalContentRequestPath
    header: GetUniversalContentRequestHeader

# Operation: update_template_universal_content
class UpdateUniversalContentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template universal content to update, formatted as a ULID.")
class UpdateUniversalContentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class UpdateUniversalContentRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="A human-readable name for this template universal content.")
    definition: ButtonBlock | DropShadowBlock | HorizontalRuleBlock | HtmlBlock | ImageBlock | SpacerBlock | TextBlock | None = Field(default=None, validation_alias="definition", serialization_alias="definition", description="The block definition configuration. Only supported for button, drop_shadow, horizontal_rule, html, image, spacer, and text block types.")
class UpdateUniversalContentRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template universal content being updated; must match the path ID parameter.")
    type_: Literal["template-universal-content"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'template-universal-content'.")
    attributes: UpdateUniversalContentRequestBodyDataAttributes | None = None
class UpdateUniversalContentRequestBody(StrictModel):
    """Update a universal content by ID"""
    data: UpdateUniversalContentRequestBodyData
class UpdateUniversalContentRequest(StrictModel):
    """Update universal content within a template. Only specific block types (button, drop_shadow, horizontal_rule, html, image, spacer, and text) support definition field updates."""
    path: UpdateUniversalContentRequestPath
    header: UpdateUniversalContentRequestHeader
    body: UpdateUniversalContentRequestBody

# Operation: delete_universal_content
class DeleteUniversalContentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template universal content to delete. Use the full ID string (e.g., 01HWWWKAW4RHXQJCMW4R2KRYR4).")
class DeleteUniversalContentRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally followed by a suffix. Defaults to 2026-01-15 if not specified.")
class DeleteUniversalContentRequest(StrictModel):
    """Permanently delete a universal content template by its ID. This operation requires the templates:write scope and is subject to rate limits of 75 requests per second (burst) or 700 per minute (steady state)."""
    path: DeleteUniversalContentRequestPath
    header: DeleteUniversalContentRequestHeader

# Operation: render_template
class RenderTemplateRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class RenderTemplateRequestBodyDataAttributes(StrictModel):
    context: dict[str, Any] = Field(default=..., validation_alias="context", serialization_alias="context", description="A JSON object containing template variable values. Use dot notation to reference nested properties (e.g., user.first_name). Variables without corresponding context values render as empty. See Klaviyo template documentation for supported tag syntax.")
class RenderTemplateRequestBodyData(StrictModel):
    type_: Literal["template"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier. Must be set to 'template' to specify this operation targets email templates.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email template to render.")
    attributes: RenderTemplateRequestBodyDataAttributes
class RenderTemplateRequestBody(StrictModel):
    data: RenderTemplateRequestBodyData
class RenderTemplateRequest(StrictModel):
    """Render an email template with provided context variables, returning AMP, HTML, and plain text versions. Template variables use dot notation for nested access and are treated as false when missing from context."""
    header: RenderTemplateRequestHeader
    body: RenderTemplateRequestBody

# Operation: create_template_clone
class CloneTemplateRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class CloneTemplateRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="Optional custom name for the cloned template. If not provided, the system will assign a default name.")
class CloneTemplateRequestBodyData(StrictModel):
    type_: Literal["template"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier; must be set to 'template' for this operation.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the template to clone.")
    attributes: CloneTemplateRequestBodyDataAttributes | None = None
class CloneTemplateRequestBody(StrictModel):
    data: CloneTemplateRequestBodyData
class CloneTemplateRequest(StrictModel):
    """Create a duplicate of an existing template by its ID. Note that accounts are limited to 1,000 templates created via API; cloning will fail if this limit is reached."""
    header: CloneTemplateRequestHeader
    body: CloneTemplateRequestBody

# Operation: get_tracking_settings
class GetTrackingSettingsRequestQuery(StrictModel):
    fields_tracking_setting: list[Literal["auto_add_parameters", "custom_parameters", "utm_campaign", "utm_campaign.campaign", "utm_campaign.campaign.type", "utm_campaign.campaign.value", "utm_campaign.flow", "utm_campaign.flow.type", "utm_campaign.flow.value", "utm_id", "utm_id.campaign", "utm_id.campaign.type", "utm_id.campaign.value", "utm_id.flow", "utm_id.flow.type", "utm_id.flow.value", "utm_medium", "utm_medium.campaign", "utm_medium.campaign.type", "utm_medium.campaign.value", "utm_medium.flow", "utm_medium.flow.type", "utm_medium.flow.value", "utm_source", "utm_source.campaign", "utm_source.campaign.type", "utm_source.campaign.value", "utm_source.flow", "utm_source.flow.type", "utm_source.flow.value", "utm_term", "utm_term.campaign", "utm_term.campaign.type", "utm_term.campaign.value", "utm_term.flow", "utm_term.flow.type", "utm_term.flow.value"]] | None = Field(default=None, validation_alias="fields[tracking-setting]", serialization_alias="fields[tracking-setting]", description="Specify which fields to include in the response for each tracking setting. Use sparse fieldsets to optimize payload size by requesting only the fields you need.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of results to return per page. This endpoint supports only a single result, so the maximum value is 1.", ge=1, le=1)
class GetTrackingSettingsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (optionally with a suffix). Defaults to the latest stable revision.")
class GetTrackingSettingsRequest(StrictModel):
    """Retrieve all UTM tracking settings configured for your Klaviyo account. Returns an array containing the account's tracking setting configuration."""
    query: GetTrackingSettingsRequestQuery | None = None
    header: GetTrackingSettingsRequestHeader

# Operation: get_tracking_setting
class GetTrackingSettingRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The account ID of the tracking setting to retrieve (e.g., 'abCdEf').")
class GetTrackingSettingRequestQuery(StrictModel):
    fields_tracking_setting: list[Literal["auto_add_parameters", "custom_parameters", "utm_campaign", "utm_campaign.campaign", "utm_campaign.campaign.type", "utm_campaign.campaign.value", "utm_campaign.flow", "utm_campaign.flow.type", "utm_campaign.flow.value", "utm_id", "utm_id.campaign", "utm_id.campaign.type", "utm_id.campaign.value", "utm_id.flow", "utm_id.flow.type", "utm_id.flow.value", "utm_medium", "utm_medium.campaign", "utm_medium.campaign.type", "utm_medium.campaign.value", "utm_medium.flow", "utm_medium.flow.type", "utm_medium.flow.value", "utm_source", "utm_source.campaign", "utm_source.campaign.type", "utm_source.campaign.value", "utm_source.flow", "utm_source.flow.type", "utm_source.flow.value", "utm_term", "utm_term.campaign", "utm_term.campaign.type", "utm_term.campaign.value", "utm_term.flow", "utm_term.flow.type", "utm_term.flow.value"]] | None = Field(default=None, validation_alias="fields[tracking-setting]", serialization_alias="fields[tracking-setting]", description="Specify which fields to include in the response for the tracking-setting resource. Use sparse fieldsets to optimize payload size by requesting only needed fields.")
class GetTrackingSettingRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetTrackingSettingRequest(StrictModel):
    """Retrieve a UTM tracking setting by account ID. Returns the tracking configuration for the specified account, which controls how UTM parameters are captured and processed."""
    path: GetTrackingSettingRequestPath
    query: GetTrackingSettingRequestQuery | None = None
    header: GetTrackingSettingRequestHeader

# Operation: list_web_feeds
class GetWebFeedsRequestQuery(StrictModel):
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter results using comparison operators on feed name, creation date, or last update date. Supports exact matching, partial text matching, and date range queries. See API documentation for detailed filter syntax.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of results to return per page. Must be between 1 and 20 items; defaults to 5 if not specified.", ge=1, le=20)
class GetWebFeedsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API version in YYYY-MM-DD format (optionally with a suffix). Defaults to 2026-01-15 if not provided.")
class GetWebFeedsRequest(StrictModel):
    """Retrieve all web feeds configured for your account. Supports filtering by name, creation date, or last update, with pagination to manage large result sets."""
    query: GetWebFeedsRequestQuery | None = None
    header: GetWebFeedsRequestHeader

# Operation: create_web_feed
class CreateWebFeedRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified).")
class CreateWebFeedRequestBodyDataAttributes(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="A descriptive name for this web feed (e.g., 'Blog_posts'). Used for identification and display purposes.")
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="The URL endpoint from which to fetch the web feed content (e.g., 'https://help.klaviyo.com/api/v2/help_center/en-us/articles.json').")
    request_method: Literal["get", "post"] = Field(default=..., validation_alias="request_method", serialization_alias="request_method", description="The HTTP method to use when requesting the feed; either 'get' for standard retrieval or 'post' for feeds requiring POST requests.")
    content_type: Literal["json", "xml"] = Field(default=..., validation_alias="content_type", serialization_alias="content_type", description="The expected content format of the feed; either 'json' for JSON-formatted feeds or 'xml' for XML-formatted feeds.")
class CreateWebFeedRequestBodyData(StrictModel):
    type_: Literal["web-feed"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'web-feed'.")
    attributes: CreateWebFeedRequestBodyDataAttributes
class CreateWebFeedRequestBody(StrictModel):
    """Create a web feed"""
    data: CreateWebFeedRequestBodyData
class CreateWebFeedRequest(StrictModel):
    """Create a new web feed to aggregate content from a specified URL. The feed will be polled using the specified HTTP method and parsed according to the declared content type."""
    header: CreateWebFeedRequestHeader
    body: CreateWebFeedRequestBody

# Operation: get_web_feed
class GetWebFeedRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the web feed to retrieve (e.g., '925e385b52fb')")
class GetWebFeedRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)")
class GetWebFeedRequest(StrictModel):
    """Retrieve a specific web feed by its ID. Returns the complete feed configuration and metadata for the given feed identifier."""
    path: GetWebFeedRequestPath
    header: GetWebFeedRequestHeader

# Operation: update_web_feed
class UpdateWebFeedRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the web feed to update (e.g., '925e385b52fb')")
class UpdateWebFeedRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15)")
class UpdateWebFeedRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="A descriptive name for the web feed (e.g., 'Blog_posts')")
    url: str | None = Field(default=None, validation_alias="url", serialization_alias="url", description="The URL endpoint from which to fetch the web feed content (e.g., 'https://help.klaviyo.com/api/v2/help_center/en-us/articles.json')")
    request_method: Literal["get", "post"] | None = Field(default=None, validation_alias="request_method", serialization_alias="request_method", description="The HTTP method to use when requesting the web feed; either 'get' or 'post'")
    content_type: Literal["json", "xml"] | None = Field(default=None, validation_alias="content_type", serialization_alias="content_type", description="The expected content format of the web feed; either 'json' or 'xml'")
class UpdateWebFeedRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the web feed being updated; must match the ID in the URL path (e.g., '925e385b52fb')")
    type_: Literal["web-feed"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type identifier; must be set to 'web-feed'")
    attributes: UpdateWebFeedRequestBodyDataAttributes | None = None
class UpdateWebFeedRequestBody(StrictModel):
    """Update a web feed by ID"""
    data: UpdateWebFeedRequestBodyData
class UpdateWebFeedRequest(StrictModel):
    """Update an existing web feed configuration, including its name, URL, request method, and content type. Requires the feed ID and current API revision for the request."""
    path: UpdateWebFeedRequestPath
    header: UpdateWebFeedRequestHeader
    body: UpdateWebFeedRequestBody

# Operation: delete_web_feed
class DeleteWebFeedRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the web feed to delete (e.g., '925e385b52fb')")
class DeleteWebFeedRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision in YYYY-MM-DD format with optional suffix (defaults to 2026-01-15 if not specified)")
class DeleteWebFeedRequest(StrictModel):
    """Permanently delete a web feed by its ID. This operation requires the feed ID and API revision to ensure safe deletion."""
    path: DeleteWebFeedRequestPath
    header: DeleteWebFeedRequestHeader

# Operation: list_webhooks
class GetWebhooksRequestQuery(StrictModel):
    fields_webhook: list[Literal["created_at", "description", "enabled", "endpoint_url", "name", "updated_at"]] | None = Field(default=None, validation_alias="fields[webhook]", serialization_alias="fields[webhook]", description="Specify which webhook fields to include in the response using sparse fieldsets for optimized payload size. Provide as an array of field names.")
class GetWebhooksRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (or with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetWebhooksRequest(StrictModel):
    """Retrieve all webhooks configured in the account. Use optional field filtering to customize the response payload."""
    query: GetWebhooksRequestQuery | None = None
    header: GetWebhooksRequestHeader

# Operation: get_webhook
class GetWebhookRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook to retrieve.")
class GetWebhookRequestQuery(StrictModel):
    fields_webhook: list[Literal["created_at", "description", "enabled", "endpoint_url", "name", "updated_at"]] | None = Field(default=None, validation_alias="fields[webhook]", serialization_alias="fields[webhook]", description="Optional array of specific webhook fields to include in the response. Use sparse fieldsets to reduce payload size and improve performance by requesting only needed fields.")
class GetWebhookRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (optionally with a suffix). Defaults to 2026-01-15 if not specified.")
class GetWebhookRequest(StrictModel):
    """Retrieve a specific webhook by its ID. Returns the webhook configuration and settings for the given identifier."""
    path: GetWebhookRequestPath
    query: GetWebhookRequestQuery | None = None
    header: GetWebhookRequestHeader

# Operation: update_webhook
class UpdateWebhookRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook to update.")
class UpdateWebhookRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15 or 2026-01-15.v1). Defaults to 2026-01-15 if not specified.")
class UpdateWebhookRequestBodyDataAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="A human-readable name for the webhook to help identify its purpose.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="A detailed description explaining what this webhook does or when it triggers.")
    endpoint_url: str | None = Field(default=None, validation_alias="endpoint_url", serialization_alias="endpoint_url", description="The HTTPS URL where webhook events will be sent. Must use the HTTPS protocol for security.")
    secret_key: str | None = Field(default=None, validation_alias="secret_key", serialization_alias="secret_key", description="A secret key used to cryptographically sign webhook requests, allowing the receiver to verify authenticity.")
    enabled: bool | None = Field(default=None, validation_alias="enabled", serialization_alias="enabled", description="Whether the webhook is active and should send events. Set to true to enable or false to disable.")
class UpdateWebhookRequestBodyDataRelationshipsWebhookTopics(StrictModel):
    data: list[UpdateWebhookBodyDataRelationshipsWebhookTopicsDataItem] | None = Field(default=None, validation_alias="data", serialization_alias="data", description="Additional structured data associated with the webhook. Order and format depend on the webhook configuration schema.")
class UpdateWebhookRequestBodyDataRelationships(StrictModel):
    webhook_topics: UpdateWebhookRequestBodyDataRelationshipsWebhookTopics | None = Field(default=None, validation_alias="webhook-topics", serialization_alias="webhook-topics")
class UpdateWebhookRequestBodyData(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook being updated; must match the ID in the path parameter.")
    type_: Literal["webhook"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The resource type; must be set to 'webhook'.")
    attributes: UpdateWebhookRequestBodyDataAttributes | None = None
    relationships: UpdateWebhookRequestBodyDataRelationships | None = None
class UpdateWebhookRequestBody(StrictModel):
    data: UpdateWebhookRequestBodyData
class UpdateWebhookRequest(StrictModel):
    """Update an existing webhook configuration by ID. Modify webhook properties such as name, description, endpoint URL, secret key, and enabled status."""
    path: UpdateWebhookRequestPath
    header: UpdateWebhookRequestHeader
    body: UpdateWebhookRequestBody

# Operation: delete_webhook
class DeleteWebhookRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook to delete.")
class DeleteWebhookRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, optionally with a suffix. Defaults to 2026-01-15 if not specified.")
class DeleteWebhookRequest(StrictModel):
    """Permanently delete a webhook by its ID. This action cannot be undone and will stop all event deliveries to the webhook's configured endpoint."""
    path: DeleteWebhookRequestPath
    header: DeleteWebhookRequestHeader

# Operation: list_webhook_topics
class GetWebhookTopicsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified.")
class GetWebhookTopicsRequest(StrictModel):
    """Retrieve all available webhook topics in a Klaviyo account. Webhook topics define the events that can trigger webhooks for your integration."""
    header: GetWebhookTopicsRequestHeader

# Operation: get_webhook_topic
class GetWebhookTopicRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook topic to retrieve (e.g., 'event:klaviyo.sent_sms'). Use this ID to fetch the specific topic's configuration.")
class GetWebhookTopicRequestHeader(StrictModel):
    revision: str = Field(default=..., description="The API endpoint revision date in YYYY-MM-DD format, with optional suffix. Defaults to 2026-01-15 if not specified, ensuring compatibility with the desired API version.")
class GetWebhookTopicRequest(StrictModel):
    """Retrieve a specific webhook topic by its ID to view its configuration and details. Useful for inspecting webhook topic settings before subscribing to events."""
    path: GetWebhookTopicRequestPath
    header: GetWebhookTopicRequestHeader

# Operation: list_client_review_values_reports
class GetClientReviewValuesReportsRequestQuery(StrictModel):
    company_id: str = Field(default=..., description="Your Klaviyo Public API Key / Site ID, used to identify your account. See Klaviyo documentation for details on locating this identifier.")
    fields_review_values_report: list[Literal["results"]] | None = Field(default=None, validation_alias="fields[review-values-report]", serialization_alias="fields[review-values-report]", description="Optional sparse fieldset to limit which fields are returned in the review-values-report objects. Specify as a comma-separated list of field names.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter to narrow results by product external IDs. Supports 'equals' for exact match or 'any' to match multiple IDs. Use comma-separated format for multiple values with the 'any' operator.")
    group_by: Literal["company_id", "product_id"] = Field(default=..., description="Required grouping dimension for the report. Choose 'company_id' to aggregate across your entire account or 'product_id' to break down metrics by individual product.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Optional page size for results, ranging from 1 to 100 items per page. Defaults to 20 if not specified.", ge=1, le=100)
    statistics: str = Field(default=..., description="Required comma-separated list of statistics to calculate for each group, such as 'average_rating' or 'total_reviews'. Specify all metrics you need in a single value.")
    timeframe: Literal["all_time", "last_30_days", "last_365_days", "last_90_days"] = Field(default=..., description="Required timeframe window for the report. Choose from 'all_time', 'last_30_days', 'last_90_days', or 'last_365_days' to define the data collection period.")
class GetClientReviewValuesReportsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to the latest stable version if not specified.")
class GetClientReviewValuesReportsRequest(StrictModel):
    """Retrieve aggregated review metrics reports for your account, grouped by company or product with customizable statistics and timeframe filtering."""
    query: GetClientReviewValuesReportsRequestQuery
    header: GetClientReviewValuesReportsRequestHeader

# Operation: list_client_reviews
class GetClientReviewsRequestQuery(StrictModel):
    company_id: str = Field(default=..., description="Your Public API Key or Site ID, used to identify your account. See the Klaviyo help article for instructions on locating this value.")
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter reviews by specific criteria such as status, rating, review type, verification status, or content properties. Supports operators like equals, contains, has, and range comparisons (greater-or-equal, less-or-equal). For detailed filtering syntax, see the API overview documentation.")
    page_size: int | None = Field(default=None, validation_alias="page[size]", serialization_alias="page[size]", description="Number of reviews to return per page. Must be between 1 and 100; defaults to 20 if not specified.", ge=1, le=100)
class GetClientReviewsRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class GetClientReviewsRequest(StrictModel):
    """Retrieve all product reviews for a client-side environment. Use this endpoint for client-side applications; for server-side implementations, refer to the server-side reviews endpoint."""
    query: GetClientReviewsRequestQuery
    header: GetClientReviewsRequestHeader

# Operation: create_client_review
class CreateClientReviewRequestQuery(StrictModel):
    company_id: str = Field(default=..., description="Your Public API Key / Site ID used to identify your Klaviyo account. This is required for authentication.")
class CreateClientReviewRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to 2026-01-15 if not specified.")
class CreateClientReviewRequestBodyDataRelationshipsOrderData(StrictModel):
    type_: Literal["order"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Fixed relationship type identifier for the associated order. Must be set to 'order'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="Order ID that this review is associated with. Links the review to a specific customer purchase.")
class CreateClientReviewRequestBodyDataRelationshipsOrder(StrictModel):
    data: CreateClientReviewRequestBodyDataRelationshipsOrderData
class CreateClientReviewRequestBodyDataRelationships(StrictModel):
    order: CreateClientReviewRequestBodyDataRelationshipsOrder
class CreateClientReviewRequestBodyDataAttributesProduct(StrictModel):
    external_id: str = Field(default=..., validation_alias="external_id", serialization_alias="external_id", description="Unique product identifier from your e-commerce platform (e.g., Shopify product ID). Used to link the review to the correct product.")
    integration_key: Literal["shopify", "woocommerce"] = Field(default=..., validation_alias="integration_key", serialization_alias="integration_key", description="Integration platform identifier in lowercase. Specifies whether the product comes from Shopify, WooCommerce, or another supported platform.")
class CreateClientReviewRequestBodyDataAttributes(StrictModel):
    review_type: Literal["question", "rating", "review", "store"] = Field(default=..., validation_alias="review_type", serialization_alias="review_type", description="Classifies the submission type: 'review' for product reviews, 'rating' for ratings only, 'question' for customer questions, or 'store' for store-level reviews.")
    email: str = Field(default=..., validation_alias="email", serialization_alias="email", description="Email address of the review author. Used to identify and contact the reviewer.")
    author: str = Field(default=..., validation_alias="author", serialization_alias="author", description="Display name of the review author. This is shown publicly with the review.")
    content: str = Field(default=..., validation_alias="content", serialization_alias="content", description="Main text content of the review or question. Provide detailed feedback about the product or ask a specific question.")
    incentive_type: Literal["coupon_or_discount", "employee_review", "free_product", "loyalty_points", "other", "paid_promotion", "sweepstakes_entry"] | None = Field(default=None, validation_alias="incentive_type", serialization_alias="incentive_type", description="Optional classification of how the reviewer was incentivized, if at all. Valid types include coupon/discount, free product, loyalty points, employee review, paid promotion, sweepstakes entry, or other.")
    rating: Literal[1, 2, 3, 4, 5] | None = Field(default=None, validation_alias="rating", serialization_alias="rating", description="Numeric rating on a scale of 1 to 5, where 1 is lowest and 5 is highest. Only applicable for review and rating types; null for question types.")
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="Optional headline or summary for the review. Provides a brief overview of the reviewer's main point.")
    custom_questions: list[CustomQuestionDto] | None = Field(default=None, validation_alias="custom_questions", serialization_alias="custom_questions", description="Optional array of custom question responses. Each item contains a question ID and an array of selected answers (e.g., size or color selections).")
    images: list[str] | None = Field(default=None, validation_alias="images", serialization_alias="images", description="Optional list of image URLs or base-64 encoded data URIs attached to the review. Supports multiple images; empty array if no images provided.")
    product: CreateClientReviewRequestBodyDataAttributesProduct
class CreateClientReviewRequestBodyData(StrictModel):
    type_: Literal["review"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Fixed resource type identifier. Must be set to 'review'.")
    relationships: CreateClientReviewRequestBodyDataRelationships
    attributes: CreateClientReviewRequestBodyDataAttributes
class CreateClientReviewRequestBody(StrictModel):
    data: CreateClientReviewRequestBodyData
class CreateClientReviewRequest(StrictModel):
    """Submit a product review from a client-side environment. This endpoint creates a review or question for a product associated with an order, supporting ratings, custom questions, and image attachments."""
    query: CreateClientReviewRequestQuery
    header: CreateClientReviewRequestHeader
    body: CreateClientReviewRequestBody

# Operation: create_client_subscription
class CreateClientSubscriptionRequestQuery(StrictModel):
    company_id: str = Field(default=..., description="Your public API key (site ID) for client-side authentication. Required for all requests to this endpoint.")
class CreateClientSubscriptionRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix. Defaults to 2026-01-15 if not specified.")
class CreateClientSubscriptionRequestBodyDataRelationshipsListData(StrictModel):
    type_: Literal["list"] = Field(default=..., validation_alias="type", serialization_alias="type", description="List resource type identifier. Must be set to 'list'.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the list to add the newly subscribed profile to. Required to associate the subscription with a specific audience list.")
class CreateClientSubscriptionRequestBodyDataRelationshipsList(StrictModel):
    data: CreateClientSubscriptionRequestBodyDataRelationshipsListData
class CreateClientSubscriptionRequestBodyDataRelationships(StrictModel):
    list_: CreateClientSubscriptionRequestBodyDataRelationshipsList = Field(default=..., validation_alias="list", serialization_alias="list")
class CreateClientSubscriptionRequestBodyDataAttributes(StrictModel):
    custom_source: str | None = Field(default=None, validation_alias="custom_source", serialization_alias="custom_source", description="Optional custom source or method detail to record on the consent records, such as 'Homepage footer signup form' or other signup origin.")
    profile: CreateClientSubscriptionBodyDataAttributesProfile | None = Field(default=None, validation_alias="profile", serialization_alias="profile", description="Profile to subscribe: email, phone, name, location, subscription consents, and custom properties.")
class CreateClientSubscriptionRequestBodyData(StrictModel):
    type_: Literal["subscription"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier. Must be set to 'subscription'.")
    relationships: CreateClientSubscriptionRequestBodyDataRelationships
    attributes: CreateClientSubscriptionRequestBodyDataAttributes | None = None
class CreateClientSubscriptionRequestBody(StrictModel):
    data: CreateClientSubscriptionRequestBodyData
class CreateClientSubscriptionRequest(StrictModel):
    """Subscribe a contact to email and/or SMS marketing channels by creating a subscription and consent record. Must be called from client-side environments only using a public API key. Provide either an email address or phone number (or both) to identify the contact."""
    query: CreateClientSubscriptionRequestQuery
    header: CreateClientSubscriptionRequestHeader
    body: CreateClientSubscriptionRequestBody

# Operation: create_or_update_client_profile
class CreateClientProfileRequestQuery(StrictModel):
    company_id: str = Field(default=..., description="Your public API key (also called Site ID), required to authenticate client-side requests. Obtain this from your Klaviyo account settings.")
class CreateClientProfileRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision in YYYY-MM-DD format with optional suffix (e.g., 2026-01-15). Defaults to the latest stable version.")
class CreateClientProfileRequestBodyDataAttributesLocation(StrictModel):
    address1: str | None = Field(default=None, validation_alias="address1", serialization_alias="address1", description="First line of the street address.")
    address2: str | None = Field(default=None, validation_alias="address2", serialization_alias="address2", description="Second line of the street address (e.g., apartment, suite, or floor number).")
    city: str | None = Field(default=None, validation_alias="city", serialization_alias="city", description="City name.")
    country: str | None = Field(default=None, validation_alias="country", serialization_alias="country", description="Country name.")
    latitude: str | None = Field(default=None, validation_alias="latitude", serialization_alias="latitude", description="Latitude coordinate for geographic location. Provide with four decimal places precision for accuracy. Accepts string or numeric format.")
    longitude: str | None = Field(default=None, validation_alias="longitude", serialization_alias="longitude", description="Longitude coordinate for geographic location. Provide with four decimal places precision for accuracy. Accepts string or numeric format.")
    region: str | None = Field(default=None, validation_alias="region", serialization_alias="region", description="Region, state, or province within the country.")
    zip_: str | None = Field(default=None, validation_alias="zip", serialization_alias="zip", description="Postal or zip code.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="Time zone name using the IANA Time Zone Database format (e.g., America/New_York, Europe/London). Used for scheduling and localization.")
    ip: str | None = Field(default=None, validation_alias="ip", serialization_alias="ip", description="IP address of the profile (IPv4 or IPv6 format). Useful for geolocation and fraud detection.")
class CreateClientProfileRequestBodyDataAttributes(StrictModel):
    email: str | None = Field(default=None, validation_alias="email", serialization_alias="email", description="Individual's email address. Use this as a primary identifier for profile matching and updates.")
    phone_number: str | None = Field(default=None, validation_alias="phone_number", serialization_alias="phone_number", description="Individual's phone number in E.164 format (e.g., +1 country code followed by number). Use this as an alternative or supplementary identifier.")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="A unique identifier from an external system (such as a point-of-sale or CRM system) to link Klaviyo profiles with your internal records. Format depends on your external system.")
    anonymous_id: str | None = Field(default=None, validation_alias="anonymous_id", serialization_alias="anonymous_id", description="An anonymous identifier used when profile identity is not yet known. Useful for tracking before email or phone collection.")
    kx: str | None = Field(default=None, validation_alias="_kx", serialization_alias="_kx", description="Encrypted exchange identifier (kx) used by Klaviyo's web tracking to identify profiles. Can be used as a filter when retrieving profiles.")
    first_name: str | None = Field(default=None, validation_alias="first_name", serialization_alias="first_name", description="Individual's first name.")
    last_name: str | None = Field(default=None, validation_alias="last_name", serialization_alias="last_name", description="Individual's last name.")
    organization: str | None = Field(default=None, validation_alias="organization", serialization_alias="organization", description="Name of the company or organization where the individual works.")
    locale: str | None = Field(default=None, validation_alias="locale", serialization_alias="locale", description="Profile's locale in IETF BCP 47 format (e.g., en-US, fr-FR). Follows ISO 639-1/2 language codes and ISO 3166 country codes.")
    title: str | None = Field(default=None, validation_alias="title", serialization_alias="title", description="Individual's job title or professional role.")
    image: str | None = Field(default=None, validation_alias="image", serialization_alias="image", description="URL pointing to a profile image or avatar.")
    properties: dict[str, Any] | None = Field(default=None, validation_alias="properties", serialization_alias="properties", description="Custom properties as key-value pairs. Use this to store additional profile attributes specific to your business (e.g., customer tier, preferences, or metadata).")
    location: CreateClientProfileRequestBodyDataAttributesLocation | None = None
class CreateClientProfileRequestBodyDataMetaPatchProperties(StrictModel):
    append: dict[str, Any] | None = Field(default=None, validation_alias="append", serialization_alias="append", description="Append values to existing array properties. Specify property names with values to add. Useful for accumulating list-based attributes without replacing existing data.")
    unappend: dict[str, Any] | None = Field(default=None, validation_alias="unappend", serialization_alias="unappend", description="Remove specific values from existing array properties. Specify property names with values to remove. Useful for cleaning up list-based attributes.")
    unset: str | list[str] | None = Field(default=None, validation_alias="unset", serialization_alias="unset", description="Remove one or more properties entirely from the profile. Specify property names as a string or array to delete them and their values completely.")
class CreateClientProfileRequestBodyDataMeta(StrictModel):
    patch_properties: CreateClientProfileRequestBodyDataMetaPatchProperties | None = None
class CreateClientProfileRequestBodyData(StrictModel):
    type_: Literal["profile"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Resource type identifier. Must be set to 'profile' for this operation.")
    attributes: CreateClientProfileRequestBodyDataAttributes | None = None
    meta: CreateClientProfileRequestBodyDataMeta | None = None
class CreateClientProfileRequestBody(StrictModel):
    data: CreateClientProfileRequestBodyData
class CreateClientProfileRequest(StrictModel):
    """Create or update a customer profile with identity and property information from client-side environments. This endpoint requires a public API key and is designed for browser-based implementations; use server-side endpoints for identifier updates or server applications."""
    query: CreateClientProfileRequestQuery
    header: CreateClientProfileRequestHeader
    body: CreateClientProfileRequestBody

# Operation: subscribe_profile_to_back_in_stock_notifications
class CreateClientBackInStockSubscriptionRequestQuery(StrictModel):
    company_id: str = Field(default=..., description="Your public API key (also called Site ID), which identifies your Klaviyo account. Required for client-side authentication.")
class CreateClientBackInStockSubscriptionRequestHeader(StrictModel):
    revision: str = Field(default=..., description="API endpoint revision date in YYYY-MM-DD format (with optional suffix). Defaults to 2026-01-15 if not specified.")
class CreateClientBackInStockSubscriptionRequestBodyDataAttributesProfileDataAttributes(StrictModel):
    email: str | None = Field(default=None, validation_alias="email", serialization_alias="email", description="The profile's email address. Use this to identify or create a profile if profile ID is not provided.")
    phone_number: str | None = Field(default=None, validation_alias="phone_number", serialization_alias="phone_number", description="The profile's phone number in E.164 format (e.g., +1 country code and number). Use this to identify or create a profile if profile ID is not provided.")
    external_id: str | None = Field(default=None, validation_alias="external_id", serialization_alias="external_id", description="An external identifier from your system (such as a customer ID from your point-of-sale or CRM) to link this Klaviyo profile with your internal records.")
class CreateClientBackInStockSubscriptionRequestBodyDataAttributesProfileData(StrictModel):
    type_: Literal["profile"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Fixed value that identifies the nested profile object type.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique Klaviyo profile ID (generated by Klaviyo) if subscribing an existing profile. Either this or email/phone_number must be provided to identify the profile.")
    attributes: CreateClientBackInStockSubscriptionRequestBodyDataAttributesProfileDataAttributes | None = None
class CreateClientBackInStockSubscriptionRequestBodyDataAttributesProfile(StrictModel):
    data: CreateClientBackInStockSubscriptionRequestBodyDataAttributesProfileData
class CreateClientBackInStockSubscriptionRequestBodyDataAttributes(StrictModel):
    channels: list[Literal["EMAIL", "PUSH", "SMS", "WHATSAPP"]] = Field(default=..., validation_alias="channels", serialization_alias="channels", description="One or more notification channels the profile prefers to receive back-in-stock alerts through. Valid options are EMAIL, SMS, or both as an array.")
    profile: CreateClientBackInStockSubscriptionRequestBodyDataAttributesProfile
class CreateClientBackInStockSubscriptionRequestBodyDataRelationshipsVariantData(StrictModel):
    type_: Literal["catalog-variant"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Fixed value that identifies the catalog variant object type in the relationship.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The catalog variant ID in the format integrationType:::catalogId:::externalId (e.g., $custom:::$default:::VARIANT-ID or $shopify:::$default:::33001893429341). Identifies which product variant the profile is subscribing to.")
class CreateClientBackInStockSubscriptionRequestBodyDataRelationshipsVariant(StrictModel):
    data: CreateClientBackInStockSubscriptionRequestBodyDataRelationshipsVariantData
class CreateClientBackInStockSubscriptionRequestBodyDataRelationships(StrictModel):
    variant: CreateClientBackInStockSubscriptionRequestBodyDataRelationshipsVariant
class CreateClientBackInStockSubscriptionRequestBodyData(StrictModel):
    type_: Literal["back-in-stock-subscription"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Fixed value that identifies this as a back-in-stock-subscription resource type.")
    attributes: CreateClientBackInStockSubscriptionRequestBodyDataAttributes
    relationships: CreateClientBackInStockSubscriptionRequestBodyDataRelationships
class CreateClientBackInStockSubscriptionRequestBody(StrictModel):
    data: CreateClientBackInStockSubscriptionRequestBodyData
class CreateClientBackInStockSubscriptionRequest(StrictModel):
    """Subscribe a customer profile to receive back-in-stock notifications for a specific product variant through their preferred channels (email, SMS, or both). This client-side endpoint requires a public API key and is designed for browser-based implementations."""
    query: CreateClientBackInStockSubscriptionRequestQuery
    header: CreateClientBackInStockSubscriptionRequestHeader
    body: CreateClientBackInStockSubscriptionRequestBody

# ============================================================================
# Component Models
# ============================================================================

class AddCategoriesToCatalogItemBodyDataItem(PermissiveModel):
    type_: Literal["catalog-category"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog category IDs representing the categories the item is in")

class AddItemsToCatalogCategoryBodyDataItem(PermissiveModel):
    type_: Literal["catalog-item"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog item IDs that are in the given category.")

class AddProfilesToListBodyDataItem(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class AdditionalField(PermissiveModel):
    name: str
    value: str

class AfterCloseTimeoutProperties(PermissiveModel):
    timeout_days: int | None = 5

class AfterCloseTimeout(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["after_close_or_submit_timeout"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: AfterCloseTimeoutProperties | None = None

class AlltimeDateFilter(PermissiveModel):
    type_: Literal["date"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["alltime"] = Field(..., description="Operators for alltime date filters.")

class AnniversaryDateFilter(PermissiveModel):
    type_: Literal["date"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["anniversary", "anniversary-month"] = Field(..., description="Operators for anniversary date filters.")

class BackInStockDynamicButtonBorderStyles(PermissiveModel):
    enabled: bool | None = False
    color: str | None = '#000000'
    style: Literal["dashed", "dotted", "solid"] | None = Field('solid', description="Border pattern enumeration.")
    width: int | None = 1

class BackInStockDynamicButtonDropShadowStyles(PermissiveModel):
    enabled: bool | None = False
    color: str | None = '#000000'
    blur: int | None = 15
    x_offset: int | None = 0
    y_offset: int | None = 0

class BackInStockDynamicButtonStyles(PermissiveModel):
    color: str | None = '#000000'
    border_radius: int | None = 0
    height: int | None = 44
    width: Literal["fitToText", "fullWidth"] | None = Field('fullWidth', description="Back In Stock Dynamic Button display type enumeration.")
    alignment: Literal["center", "left", "right"] | None = Field('center', description="Horizontal alignment enumeration.")
    border: BackInStockDynamicButtonBorderStyles | None = None
    drop_shadow: BackInStockDynamicButtonDropShadowStyles | None = None

class BackInStockDynamicButtonTextStyles(PermissiveModel):
    font_family: str | None = "Arial, 'Helvetica Neue', Helvetica, sans-serif"
    font_size: int | None = 16
    font_weight: Literal[100, 200, 300, 400, 500, 600, 700, 800, 900] | None = Field(400, description="Font weight enumeration.")
    font_color: str | None = '#FFFFFF'
    font_style: str | None = None
    text_decoration: str | None = None
    letter_spacing: int | None = 0

class BackInStockDynamicButtonData(PermissiveModel):
    label: str | None = ''
    display: Literal["NEXT_TO", "REPLACE"] | None = Field('REPLACE', description="Back In Stock Dynamic Button display type enumeration.")
    text_styles: BackInStockDynamicButtonTextStyles | None = None
    button_styles: BackInStockDynamicButtonStyles | None = None

class BackInStockMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["back_in_stock"]

class BackInStockProperties(PermissiveModel):
    tag_allowlist: list[str] | None = None
    tag_blocklist: list[str] | None = None

class BackInStock(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["back_in_stock"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: BackInStockProperties | None = None

class BackgroundImageStyles(PermissiveModel):
    horizontal_alignment: Literal["center", "left", "right"] | None = Field('center', description="Horizontal alignment enumeration.")
    width: int | None = None
    position: Literal["contain", "cover", "custom"] | None = Field('contain', description="Image position enumeration.")
    vertical_alignment: Literal["bottom", "center", "top"] | None = Field('center', description="Vertical alignment enumeration.")
    custom_width: int | None = None

class BannerStyles(PermissiveModel):
    desktop_position: Literal["bottom", "top"] | None = Field('top', description="Positioning of banner forms.")
    mobile_position: Literal["bottom", "top"] | None = Field('top', description="Positioning of banner forms.")
    scroll_with_page: bool | None = True

class BooleanFilter(PermissiveModel):
    type_: Literal["boolean"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["equals"] = Field(..., description="Operators for boolean filters.")
    value: bool

class BorderStyle(PermissiveModel):
    radius: int | None = 8
    color: str | None = None
    style: Literal["dashed", "dotted", "solid"] | None = Field(None, description="Border pattern enumeration.")
    thickness: int | None = None

class BulkImportProfilesBodyDataRelationshipsListsDataItem(PermissiveModel):
    type_: Literal["list"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Optional list to add the profiles to")

class BulkRemoveMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["bulk_remove"]

class ButtonBlock(PermissiveModel):
    content_type: Literal["block"]
    type_: Literal["button"] = Field(..., validation_alias="type", serialization_alias="type")
    data: Any | None = Field(...)

class ButtonDropShadowStyles(PermissiveModel):
    enabled: bool | None = False
    color: str | None = '#000000'
    blur: int | None = 15
    x_offset: int | None = 0
    y_offset: int | None = 0

class ButtonProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    label: str
    additional_fields: list[AdditionalField] | None = None

class CalendarDateFilter(PermissiveModel):
    type_: Literal["date"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["calendar-month"] = Field(..., description="Operators for calendar date filters.")
    value: int

class CampaignMessageIncrement(PermissiveModel):
    badge_config: Literal["increment_one"]

class CampaignMessageProperty(PermissiveModel):
    badge_config: Literal["set_property"]
    set_from_property: str

class CampaignMessageStaticCount(PermissiveModel):
    badge_config: Literal["set_count"]
    value: str

class CarrierDeactivationMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["carrier_deactivation"]

class CartItemCountProperties(PermissiveModel):
    comparison: Literal["equals", "greater_than", "less_than"] | None = Field(None, description="Number comparison enumeration.")
    value: int | None = None

class CartItemCount(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["cart_item_count"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: CartItemCountProperties | None = None

class CartProductProperties(PermissiveModel):
    type_: Literal["brand", "categories", "id", "name"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Product descriptor enumeration.")
    value: str | None = None

class CartProduct(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["cart_product"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: CartProductProperties | None = None

class CartValueProperties(PermissiveModel):
    comparison: Literal["equals", "greater_than", "less_than"] | None = Field(None, description="Number comparison enumeration.")
    value: float | None = None

class CartValue(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["cart_value"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: CartValueProperties | None = None

class CatalogCategoryCreateQueryResourceObjectAttributes(PermissiveModel):
    external_id: str = Field(..., description="The ID of the catalog category in an external system.")
    name: str = Field(..., description="The name of the catalog category.")
    integration_type: Literal["$custom"] | None = Field('$custom', description="The integration type. Currently only \"$custom\" is supported.")
    catalog_type: str | None = Field('$default', description="The type of catalog. Currently only \"$default\" is supported.")

class CatalogCategoryCreateQueryResourceObjectRelationshipsItemsDataItem(PermissiveModel):
    type_: Literal["catalog-item"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog item IDs that are in the given category.")

class CatalogCategoryCreateQueryResourceObjectRelationshipsItems(PermissiveModel):
    data: list[CatalogCategoryCreateQueryResourceObjectRelationshipsItemsDataItem] | None = None

class CatalogCategoryCreateQueryResourceObjectRelationships(PermissiveModel):
    items: CatalogCategoryCreateQueryResourceObjectRelationshipsItems | None = None

class CatalogCategoryCreateQueryResourceObject(PermissiveModel):
    type_: Literal["catalog-category"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: CatalogCategoryCreateQueryResourceObjectAttributes
    relationships: CatalogCategoryCreateQueryResourceObjectRelationships | None = None

class CatalogCategoryDeleteQueryResourceObject(PermissiveModel):
    type_: Literal["catalog-category"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The catalog category ID is a compound ID (string), with format: `{integration}:::{catalog}:::{external_id}`. Currently, the only supported integration type is `$custom`, and the only supported catalog is `$default`.")

class CatalogCategoryUpdateQueryResourceObjectAttributes(PermissiveModel):
    name: str | None = Field(None, description="The name of the catalog category.")

class CatalogCategoryUpdateQueryResourceObjectRelationshipsItemsDataItem(PermissiveModel):
    type_: Literal["catalog-item"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog item IDs that are in the given category.")

class CatalogCategoryUpdateQueryResourceObjectRelationshipsItems(PermissiveModel):
    data: list[CatalogCategoryUpdateQueryResourceObjectRelationshipsItemsDataItem] | None = None

class CatalogCategoryUpdateQueryResourceObjectRelationships(PermissiveModel):
    items: CatalogCategoryUpdateQueryResourceObjectRelationshipsItems | None = None

class CatalogCategoryUpdateQueryResourceObject(PermissiveModel):
    type_: Literal["catalog-category"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The catalog category ID is a compound ID (string), with format: `{integration}:::{catalog}:::{external_id}`. Currently, the only supported integration type is `$custom`, and the only supported catalog is `$default`.")
    attributes: CatalogCategoryUpdateQueryResourceObjectAttributes
    relationships: CatalogCategoryUpdateQueryResourceObjectRelationships | None = None

class CatalogItemCreateQueryResourceObjectAttributes(PermissiveModel):
    external_id: str = Field(..., description="The ID of the catalog item in an external system.")
    integration_type: Literal["$custom"] | None = Field('$custom', description="The integration type. Currently only \"$custom\" is supported.")
    title: str = Field(..., description="The title of the catalog item.")
    price: float | None = Field(None, description="This field can be used to set the price on the catalog item, which is what gets displayed for the item when included in emails. For most price-update use cases, you will also want to update the `price` on any child variants, using the [Update Catalog Variant Endpoint](https://developers.klaviyo.com/en/reference/update_catalog_variant).")
    catalog_type: str | None = Field('$default', description="The type of catalog. Currently only \"$default\" is supported.")
    description: str = Field(..., description="A description of the catalog item.")
    url: str = Field(..., description="URL pointing to the location of the catalog item on your website.")
    image_full_url: str | None = Field(None, description="URL pointing to the location of a full image of the catalog item.")
    image_thumbnail_url: str | None = Field(None, description="URL pointing to the location of an image thumbnail of the catalog item")
    images: list[str] | None = Field(None, description="List of URLs pointing to the locations of images of the catalog item.")
    custom_metadata: dict[str, Any] | None = Field(None, description="Flat JSON blob to provide custom metadata about the catalog item. May not exceed 100kb.")
    published: bool | None = Field(True, description="Boolean value indicating whether the catalog item is published.")

class CatalogItemCreateQueryResourceObjectRelationshipsCategoriesDataItem(PermissiveModel):
    type_: Literal["catalog-category"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog category IDs representing the categories the item is in")

class CatalogItemCreateQueryResourceObjectRelationshipsCategories(PermissiveModel):
    data: list[CatalogItemCreateQueryResourceObjectRelationshipsCategoriesDataItem] | None = None

class CatalogItemCreateQueryResourceObjectRelationships(PermissiveModel):
    categories: CatalogItemCreateQueryResourceObjectRelationshipsCategories | None = None

class CatalogItemCreateQueryResourceObject(PermissiveModel):
    type_: Literal["catalog-item"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: CatalogItemCreateQueryResourceObjectAttributes
    relationships: CatalogItemCreateQueryResourceObjectRelationships | None = None

class CatalogItemDeleteQueryResourceObject(PermissiveModel):
    type_: Literal["catalog-item"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The catalog item ID is a compound ID (string), with format: `{integration}:::{catalog}:::{external_id}`. Currently, the only supported integration type is `$custom`, and the only supported catalog is `$default`.")

class CatalogItemUpdateQueryResourceObjectAttributes(PermissiveModel):
    title: str | None = Field(None, description="The title of the catalog item.")
    price: float | None = Field(None, description="This field can be used to set the price on the catalog item, which is what gets displayed for the item when included in emails. For most price-update use cases, you will also want to update the `price` on any child variants, using the [Update Catalog Variant Endpoint](https://developers.klaviyo.com/en/reference/update_catalog_variant).")
    description: str | None = Field(None, description="A description of the catalog item.")
    url: str | None = Field(None, description="URL pointing to the location of the catalog item on your website.")
    image_full_url: str | None = Field(None, description="URL pointing to the location of a full image of the catalog item.")
    image_thumbnail_url: str | None = Field(None, description="URL pointing to the location of an image thumbnail of the catalog item")
    images: list[str] | None = Field(None, description="List of URLs pointing to the locations of images of the catalog item.")
    custom_metadata: dict[str, Any] | None = Field(None, description="Flat JSON blob to provide custom metadata about the catalog item. May not exceed 100kb.")
    published: bool | None = Field(None, description="Boolean value indicating whether the catalog item is published.")

class CatalogItemUpdateQueryResourceObjectRelationshipsCategoriesDataItem(PermissiveModel):
    type_: Literal["catalog-category"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog category IDs representing the categories the item is in")

class CatalogItemUpdateQueryResourceObjectRelationshipsCategories(PermissiveModel):
    data: list[CatalogItemUpdateQueryResourceObjectRelationshipsCategoriesDataItem] | None = None

class CatalogItemUpdateQueryResourceObjectRelationships(PermissiveModel):
    categories: CatalogItemUpdateQueryResourceObjectRelationshipsCategories | None = None

class CatalogItemUpdateQueryResourceObject(PermissiveModel):
    type_: Literal["catalog-item"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The catalog item ID is a compound ID (string), with format: `{integration}:::{catalog}:::{external_id}`. Currently, the only supported integration type is `$custom`, and the only supported catalog is `$default`.")
    attributes: CatalogItemUpdateQueryResourceObjectAttributes
    relationships: CatalogItemUpdateQueryResourceObjectRelationships | None = None

class CatalogVariantCreateQueryResourceObjectAttributes(PermissiveModel):
    external_id: str = Field(..., description="The ID of the catalog item variant in an external system.")
    catalog_type: str | None = Field('$default', description="The type of catalog. Currently only \"$default\" is supported.")
    integration_type: Literal["$custom"] | None = Field('$custom', description="The integration type. Currently only \"$custom\" is supported.")
    title: str = Field(..., description="The title of the catalog item variant.")
    description: str = Field(..., description="A description of the catalog item variant.")
    sku: str = Field(..., description="The SKU of the catalog item variant.")
    inventory_policy: Literal[0, 1, 2] | None = Field(0, description="This field controls the visibility of this catalog item variant in product feeds/blocks. This field supports the following values:\n`1`: a product will not appear in dynamic product recommendation feeds and blocks if it is out of stock.\n`0` or `2`: a product can appear in dynamic product recommendation feeds and blocks regardless of inventory quantity.")
    inventory_quantity: float = Field(..., description="The quantity of the catalog item variant currently in stock.")
    price: float = Field(..., description="This field can be used to set the price on the catalog item variant, which is what gets displayed for the item variant when included in emails. For most price-update use cases, you will also want to update the `price` on any parent items using the [Update Catalog Item Endpoint](https://developers.klaviyo.com/en/reference/update_catalog_item).")
    url: str = Field(..., description="URL pointing to the location of the catalog item variant on your website.")
    image_full_url: str | None = Field(None, description="URL pointing to the location of a full image of the catalog item variant.")
    image_thumbnail_url: str | None = Field(None, description="URL pointing to the location of an image thumbnail of the catalog item variant.")
    images: list[str] | None = Field(None, description="List of URLs pointing to the locations of images of the catalog item variant.")
    custom_metadata: dict[str, Any] | None = Field(None, description="Flat JSON blob to provide custom metadata about the catalog item variant. May not exceed 100kb.")
    published: bool | None = Field(True, description="Boolean value indicating whether the catalog item variant is published.")

class CatalogVariantCreateQueryResourceObjectRelationshipsItemData(PermissiveModel):
    type_: Literal["catalog-item"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The original catalog item ID for which this is a variant.")

class CatalogVariantCreateQueryResourceObjectRelationshipsItem(PermissiveModel):
    data: CatalogVariantCreateQueryResourceObjectRelationshipsItemData | None = None

class CatalogVariantCreateQueryResourceObjectRelationships(PermissiveModel):
    item: CatalogVariantCreateQueryResourceObjectRelationshipsItem

class CatalogVariantCreateQueryResourceObject(PermissiveModel):
    type_: Literal["catalog-variant"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: CatalogVariantCreateQueryResourceObjectAttributes
    relationships: CatalogVariantCreateQueryResourceObjectRelationships

class CatalogVariantDeleteQueryResourceObject(PermissiveModel):
    type_: Literal["catalog-variant"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The catalog variant ID is a compound ID (string), with format: `{integration}:::{catalog}:::{external_id}`. Currently, the only supported integration type is `$custom`, and the only supported catalog is `$default`.")

class CatalogVariantUpdateQueryResourceObjectAttributes(PermissiveModel):
    title: str | None = Field(None, description="The title of the catalog item variant.")
    description: str | None = Field(None, description="A description of the catalog item variant.")
    sku: str | None = Field(None, description="The SKU of the catalog item variant.")
    inventory_policy: Literal[0, 1, 2] | None = Field(None, description="This field controls the visibility of this catalog item variant in product feeds/blocks. This field supports the following values:\n`1`: a product will not appear in dynamic product recommendation feeds and blocks if it is out of stock.\n`0` or `2`: a product can appear in dynamic product recommendation feeds and blocks regardless of inventory quantity.")
    inventory_quantity: float | None = Field(None, description="The quantity of the catalog item variant currently in stock.")
    price: float | None = Field(None, description="This field can be used to set the price on the catalog item variant, which is what gets displayed for the item variant when included in emails. For most price-update use cases, you will also want to update the `price` on any parent items using the [Update Catalog Item Endpoint](https://developers.klaviyo.com/en/reference/update_catalog_item).")
    url: str | None = Field(None, description="URL pointing to the location of the catalog item variant on your website.")
    image_full_url: str | None = Field(None, description="URL pointing to the location of a full image of the catalog item variant.")
    image_thumbnail_url: str | None = Field(None, description="URL pointing to the location of an image thumbnail of the catalog item variant.")
    images: list[str] | None = Field(None, description="List of URLs pointing to the locations of images of the catalog item variant.")
    custom_metadata: dict[str, Any] | None = Field(None, description="Flat JSON blob to provide custom metadata about the catalog item variant. May not exceed 100kb.")
    published: bool | None = Field(None, description="Boolean value indicating whether the catalog item variant is published.")

class CatalogVariantUpdateQueryResourceObject(PermissiveModel):
    type_: Literal["catalog-variant"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The catalog variant ID is a compound ID (string), with format: `{integration}:::{catalog}:::{external_id}`. Currently, the only supported integration type is `$custom`, and the only supported catalog is `$default`.")
    attributes: CatalogVariantUpdateQueryResourceObjectAttributes

class ChannelProperties(PermissiveModel):
    channel: Literal["email", "sms"] = Field(..., description="Channel type enumeration.")

class Channel(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["channel"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: ChannelProperties

class CheckoutMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["checkout"]

class CloseProperties(PermissiveModel):
    list_id: str | None = None

class Close(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    submit: bool
    type_: Literal["close"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: CloseProperties | None = None

class ConstantContactIntegrationFilter(PermissiveModel):
    type_: Literal["string"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["in"]
    value: list[Literal["constant_contact"]]

class ConstantContactIntegrationMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["integration"]
    filter_: ConstantContactIntegrationFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class ContentRepeat(PermissiveModel):
    repeat_for: str
    item_alias: str

class BlockDisplayOptions(PermissiveModel):
    show_on: Literal["all", "desktop", "mobile"] | None = Field(None, description="Show on.")
    visible_check: str | None = None
    content_repeat: ContentRepeat | None = None

class CouponCodeCreateQueryResourceObjectAttributes(PermissiveModel):
    unique_code: str = Field(..., description="This is a unique string that will be or is assigned to each customer/profile and is associated with a coupon.")
    expires_at: str | None = Field(None, description="The datetime when this coupon code will expire. If not specified or set to null, it will be automatically set to 1 year.", json_schema_extra={'format': 'date-time'})

class CouponCodeCreateQueryResourceObjectRelationshipsCouponData(PermissiveModel):
    type_: Literal["coupon"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class CouponCodeCreateQueryResourceObjectRelationshipsCoupon(PermissiveModel):
    data: CouponCodeCreateQueryResourceObjectRelationshipsCouponData | None = None

class CouponCodeCreateQueryResourceObjectRelationships(PermissiveModel):
    coupon: CouponCodeCreateQueryResourceObjectRelationshipsCoupon

class CouponCodeCreateQueryResourceObject(PermissiveModel):
    type_: Literal["coupon-code"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: CouponCodeCreateQueryResourceObjectAttributes
    relationships: CouponCodeCreateQueryResourceObjectRelationships

class CreateCatalogCategoryBodyDataRelationshipsItemsDataItem(PermissiveModel):
    type_: Literal["catalog-item"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog item IDs that are in the given category.")

class CreateCatalogItemBodyDataRelationshipsCategoriesDataItem(PermissiveModel):
    type_: Literal["catalog-category"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog category IDs representing the categories the item is in")

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesLocation(PermissiveModel):
    address1: str | None = Field(None, description="First line of street address")
    address2: str | None = Field(None, description="Second line of street address")
    city: str | None = Field(None, description="City name")
    country: str | None = Field(None, description="Country name")
    latitude: str | float | None = Field(None, description="Latitude coordinate. We recommend providing a precision of four decimal places.")
    longitude: str | float | None = Field(None, description="Longitude coordinate. We recommend providing a precision of four decimal places.")
    region: str | None = Field(None, description="Region within a country, such as state or province")
    zip_: str | None = Field(None, validation_alias="zip", serialization_alias="zip", description="Zip code")
    timezone_: str | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="Time zone name. We recommend using time zones from the IANA Time Zone Database.")
    ip: str | None = Field(None, description="IP Address")

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesMetaPatchProperties(PermissiveModel):
    """Specify one or more patch operations to apply to existing property data"""
    append: dict[str, Any] | None = Field(None, description="Append a simple value or values to this property array")
    unappend: dict[str, Any] | None = Field(None, description="Remove a simple value or values from this property array")
    unset: str | list[str] | None = Field(None, description="Remove a key or keys (and their values) completely from properties")

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesMeta(PermissiveModel):
    patch_properties: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesMetaPatchProperties | None = Field(None, description="Specify one or more patch operations to apply to existing property data")

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsEmailMarketing(PermissiveModel):
    """The parameters to subscribe to on the "EMAIL" Channel. Currently supports "MARKETING"."""
    consent: Literal["SUBSCRIBED"] = Field(..., description="The Consent status to be set as part of the subscribe call. Currently supports \"SUBSCRIBED\".")
    consented_at: str | None = Field(None, description="The timestamp of when the profile's consent was gathered. This should only be used when syncing over historical consent info to Klaviyo; if the `historical_import` flag is not included, providing any value for this field will raise an error.", json_schema_extra={'format': 'date-time'})

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsEmail(PermissiveModel):
    """The subscription parameters to subscribe to on the "EMAIL" Channel."""
    marketing: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsEmailMarketing = Field(..., description="The parameters to subscribe to on the \"EMAIL\" Channel. Currently supports \"MARKETING\".")

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsPushMarketing(PermissiveModel):
    """The parameters to subscribe to marketing on the "Push" channel."""
    consent: Literal["SUBSCRIBED"] = Field(..., description="The Consent status to be set as part of the subscribe call. Currently supports \"SUBSCRIBED\".")
    consented_at: str | None = Field(None, description="The timestamp of when the profile's consent was gathered. This should only be used when syncing over historical consent info to Klaviyo; if the `historical_import` flag is not included, providing any value for this field will raise an error.", json_schema_extra={'format': 'date-time'})

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsSmsMarketing(PermissiveModel):
    """The parameters to subscribe to marketing on the "SMS" Channel."""
    consent: Literal["SUBSCRIBED"] = Field(..., description="The Consent status to be set as part of the subscribe call. Currently supports \"SUBSCRIBED\".")
    consented_at: str | None = Field(None, description="The timestamp of when the profile's consent was gathered. This should only be used when syncing over historical consent info to Klaviyo; if the `historical_import` flag is not included, providing any value for this field will raise an error.", json_schema_extra={'format': 'date-time'})

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsSmsTransactional(PermissiveModel):
    """The parameters to subscribe to transactional messaging on the "SMS" Channel."""
    consent: Literal["SUBSCRIBED"] = Field(..., description="The Consent status to be set as part of the subscribe call. Currently supports \"SUBSCRIBED\".")
    consented_at: str | None = Field(None, description="The timestamp of when the profile's consent was gathered. This should only be used when syncing over historical consent info to Klaviyo; if the `historical_import` flag is not included, providing any value for this field will raise an error.", json_schema_extra={'format': 'date-time'})

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsSms(PermissiveModel):
    """The subscription parameters to subscribe to on the "SMS" Channel."""
    marketing: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsSmsMarketing | None = Field(None, description="The parameters to subscribe to marketing on the \"SMS\" Channel.")
    transactional: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsSmsTransactional | None = Field(None, description="The parameters to subscribe to transactional messaging on the \"SMS\" Channel.")

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsWhatsappMarketing(PermissiveModel):
    """The parameters to subscribe to marketing on the "WhatsApp" Channel."""
    consent: Literal["SUBSCRIBED"] = Field(..., description="The Consent status to be set as part of the subscribe call. Currently supports \"SUBSCRIBED\".")
    consented_at: str | None = Field(None, description="The timestamp of when the profile's consent was gathered. This should only be used when syncing over historical consent info to Klaviyo; if the `historical_import` flag is not included, providing any value for this field will raise an error.", json_schema_extra={'format': 'date-time'})

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsWhatsappTransactional(PermissiveModel):
    """The parameters to subscribe to transactional messaging on the "WhatsApp" Channel."""
    consent: Literal["SUBSCRIBED"] = Field(..., description="The Consent status to be set as part of the subscribe call. Currently supports \"SUBSCRIBED\".")
    consented_at: str | None = Field(None, description="The timestamp of when the profile's consent was gathered. This should only be used when syncing over historical consent info to Klaviyo; if the `historical_import` flag is not included, providing any value for this field will raise an error.", json_schema_extra={'format': 'date-time'})

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsWhatsapp(PermissiveModel):
    """The subscription parameters to subscribe to on the "WhatsApp" Channel."""
    marketing: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsWhatsappMarketing | None = Field(None, description="The parameters to subscribe to marketing on the \"WhatsApp\" Channel.")
    transactional: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsWhatsappTransactional | None = Field(None, description="The parameters to subscribe to transactional messaging on the \"WhatsApp\" Channel.")

class CreateEventBodyDataAttributesProfileDataAttributesLocation(PermissiveModel):
    address1: str | None = Field(None, description="First line of street address")
    address2: str | None = Field(None, description="Second line of street address")
    city: str | None = Field(None, description="City name")
    country: str | None = Field(None, description="Country name")
    latitude: str | float | None = Field(None, description="Latitude coordinate. We recommend providing a precision of four decimal places.")
    longitude: str | float | None = Field(None, description="Longitude coordinate. We recommend providing a precision of four decimal places.")
    region: str | None = Field(None, description="Region within a country, such as state or province")
    zip_: str | None = Field(None, validation_alias="zip", serialization_alias="zip", description="Zip code")
    timezone_: str | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="Time zone name. We recommend using time zones from the IANA Time Zone Database.")
    ip: str | None = Field(None, description="IP Address")

class CreateEventBodyDataAttributesProfileDataAttributesMetaPatchProperties(PermissiveModel):
    """Specify one or more patch operations to apply to existing property data"""
    append: dict[str, Any] | None = Field(None, description="Append a simple value or values to this property array")
    unappend: dict[str, Any] | None = Field(None, description="Remove a simple value or values from this property array")
    unset: str | list[str] | None = Field(None, description="Remove a key or keys (and their values) completely from properties")

class CreateEventBodyDataAttributesProfileDataAttributesMeta(PermissiveModel):
    patch_properties: CreateEventBodyDataAttributesProfileDataAttributesMetaPatchProperties | None = Field(None, description="Specify one or more patch operations to apply to existing property data")

class CreateEventBodyDataAttributesProfileDataAttributes(PermissiveModel):
    email: str | None = Field(None, description="Individual's email address")
    phone_number: str | None = Field(None, description="Individual's phone number in E.164 format")
    external_id: str | None = Field(None, description="A unique identifier used by customers to associate Klaviyo profiles with profiles in an external system, such as a point-of-sale system. Format varies based on the external system.")
    anonymous_id: str | None = None
    kx: str | None = Field(None, validation_alias="_kx", serialization_alias="_kx", description="Also known as the `exchange_id`, this is an encrypted identifier used for identifying a\nprofile by Klaviyo's web tracking.\n\nYou can use this field as a filter when retrieving profiles via the Get Profiles endpoint.")
    first_name: str | None = Field(None, description="Individual's first name")
    last_name: str | None = Field(None, description="Individual's last name")
    organization: str | None = Field(None, description="Name of the company or organization within the company for whom the individual works")
    locale: str | None = Field(None, description="The locale of the profile, in the IETF BCP 47 language tag format like (ISO 639-1/2)-(ISO 3166 alpha-2)")
    title: str | None = Field(None, description="Individual's job title")
    image: str | None = Field(None, description="URL pointing to the location of a profile image")
    location: CreateEventBodyDataAttributesProfileDataAttributesLocation | None = None
    properties: dict[str, Any] | None = Field(None, description="An object containing key/value pairs for any custom properties assigned to this profile")
    meta: CreateEventBodyDataAttributesProfileDataAttributesMeta | None = None

class CreateEventBodyDataAttributesProfileData(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Primary key that uniquely identifies this profile. Generated by Klaviyo.")
    attributes: CreateEventBodyDataAttributesProfileDataAttributes

class CreateEventBodyDataAttributesProfile(PermissiveModel):
    """Profile associated with the event: email, phone, name, location, and custom properties."""
    data: CreateEventBodyDataAttributesProfileData

class CreatePushTokenBodyDataAttributesDeviceMetadata(PermissiveModel):
    """Device metadata: device_id, model, OS, app info, SDK version, and environment."""
    device_id: str | None = Field(None, description="Relatively stable ID for the device. Will update on app uninstall and reinstall")
    klaviyo_sdk: Literal["android", "flutter", "flutter_community", "react_native", "swift"] | None = Field(None, description="The name of the SDK used to create the push token.")
    sdk_version: str | None = Field(None, description="The version of the SDK used to create the push token")
    device_model: str | None = Field(None, description="The model of the device")
    os_name: Literal["android", "ios", "ipados", "macos", "tvos"] | None = Field(None, description="The name of the operating system on the device.")
    os_version: str | None = Field(None, description="The version of the operating system on the device")
    manufacturer: str | None = Field(None, description="The manufacturer of the device")
    app_name: str | None = Field(None, description="The name of the app that created the push token")
    app_version: str | None = Field(None, description="The version of the app that created the push token")
    app_build: str | None = Field(None, description="The build of the app that created the push token")
    app_id: str | None = Field(None, description="The ID of the app that created the push token")
    environment: Literal["debug", "release"] | None = Field(None, description="The environment in which the push token was created")

class CreatePushTokenBodyDataAttributesProfileDataAttributesLocation(PermissiveModel):
    address1: str | None = Field(None, description="First line of street address")
    address2: str | None = Field(None, description="Second line of street address")
    city: str | None = Field(None, description="City name")
    country: str | None = Field(None, description="Country name")
    latitude: str | float | None = Field(None, description="Latitude coordinate. We recommend providing a precision of four decimal places.")
    longitude: str | float | None = Field(None, description="Longitude coordinate. We recommend providing a precision of four decimal places.")
    region: str | None = Field(None, description="Region within a country, such as state or province")
    zip_: str | None = Field(None, validation_alias="zip", serialization_alias="zip", description="Zip code")
    timezone_: str | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="Time zone name. We recommend using time zones from the IANA Time Zone Database.")
    ip: str | None = Field(None, description="IP Address")

class CreatePushTokenBodyDataAttributesProfileDataAttributesMetaPatchProperties(PermissiveModel):
    """Specify one or more patch operations to apply to existing property data"""
    append: dict[str, Any] | None = Field(None, description="Append a simple value or values to this property array")
    unappend: dict[str, Any] | None = Field(None, description="Remove a simple value or values from this property array")
    unset: str | list[str] | None = Field(None, description="Remove a key or keys (and their values) completely from properties")

class CreatePushTokenBodyDataAttributesProfileDataAttributesMeta(PermissiveModel):
    patch_properties: CreatePushTokenBodyDataAttributesProfileDataAttributesMetaPatchProperties | None = Field(None, description="Specify one or more patch operations to apply to existing property data")

class CreatePushTokenBodyDataAttributesProfileDataAttributes(PermissiveModel):
    phone_number: str | None = Field(None, description="Individual's phone number in E.164 format")
    external_id: str | None = Field(None, description="A unique identifier used by customers to associate Klaviyo profiles with profiles in an external system, such as a point-of-sale system. Format varies based on the external system.")
    kx: str | None = Field(None, validation_alias="_kx", serialization_alias="_kx", description="Also known as the `exchange_id`, this is an encrypted identifier used for identifying a\nprofile by Klaviyo's web tracking.\n\nYou can use this field as a filter when retrieving profiles via the Get Profiles endpoint.")
    first_name: str | None = Field(None, description="Individual's first name")
    last_name: str | None = Field(None, description="Individual's last name")
    organization: str | None = Field(None, description="Name of the company or organization within the company for whom the individual works")
    locale: str | None = Field(None, description="The locale of the profile, in the IETF BCP 47 language tag format like (ISO 639-1/2)-(ISO 3166 alpha-2)")
    title: str | None = Field(None, description="Individual's job title")
    image: str | None = Field(None, description="URL pointing to the location of a profile image")
    location: CreatePushTokenBodyDataAttributesProfileDataAttributesLocation | None = None
    properties: dict[str, Any] | None = Field(None, description="An object containing key/value pairs for any custom properties assigned to this profile")
    meta: CreatePushTokenBodyDataAttributesProfileDataAttributesMeta | None = None
    email: str | None = Field(None, description="Individual's email address")

class CreatePushTokenBodyDataAttributesProfileData(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Primary key that uniquely identifies this profile. Generated by Klaviyo.")
    attributes: CreatePushTokenBodyDataAttributesProfileDataAttributes

class CreatePushTokenBodyDataAttributesProfile(PermissiveModel):
    """Profile to associate with the push token: email, phone, name, location, and custom properties."""
    data: CreatePushTokenBodyDataAttributesProfileData

class CustomQuestionDto(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the custom question")
    answers: list[str] = Field(..., description="The answers to the custom question")

class CustomTimeframe(PermissiveModel):
    start: str = Field(..., description="A datetime that represents the start of a custom time frame. Offset is ignored and the company timezone is used.", json_schema_extra={'format': 'date-time'})
    end: str = Field(..., description="A datetime that represents the end of a custom time frame. Offset is ignored and the company timezone is used.", json_schema_extra={'format': 'date-time'})

class DataSourceRecordResourceObjectAttributes(PermissiveModel):
    record: dict[str, Any]

class DataSourceRecordResourceObject(PermissiveModel):
    type_: Literal["data-source-record"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: DataSourceRecordResourceObjectAttributes

class DataWarehouseImportMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["data_warehouse_import"]

class DelayProperties(PermissiveModel):
    seconds: int | None = 5

class Delay(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["delay"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: DelayProperties | None = None

class DeviceProperties(PermissiveModel):
    device: Literal["both", "desktop", "mobile"] | None = Field('desktop', description="Enumeration for mobile and desktop.")

class Device(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["device"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: DeviceProperties | None = None

class DoubleOptinFilter(PermissiveModel):
    field: Literal["is_double_opt_in"]
    filter_: BooleanFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class DropShadow(PermissiveModel):
    enabled: bool | None = False
    blur: int | None = 30
    color: str | None = 'rgba(0,0,0,0.15)'

class DropShadowBlock(PermissiveModel):
    content_type: Literal["block"]
    type_: Literal["drop_shadow"] = Field(..., validation_alias="type", serialization_alias="type")
    data: Any | None = Field(...)

class DynamicButton(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["BACK_IN_STOCK_OPEN"] = Field(..., validation_alias="type", serialization_alias="type", description="Dynamic Button type enumeration.")
    data: BackInStockDynamicButtonData

class DynamicTrackingParam(PermissiveModel):
    type_: Literal["dynamic"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the tracking parameter")
    value: Literal["campaign_id", "campaign_name", "campaign_name_id", "campaign_name_send_day", "email_subject", "group_id", "group_name", "group_name_id", "link_alt_text", "message_type", "profile_external_id", "profile_id"] = Field(..., description="The value of the tracking parameter")
    name: str = Field(..., description="Name of the tracking param")

class EmailContent(PermissiveModel):
    subject: str | None = Field(None, description="The subject of the message")
    preview_text: str | None = Field(None, description="Preview text associated with the message")
    from_email: str | None = Field(None, description="The email the message should be sent from")
    from_label: str | None = Field(None, description="The label associated with the from_email")
    reply_to_email: str | None = Field(None, description="Optional Reply-To email address")
    cc_email: str | None = Field(None, description="Optional CC email address")
    bcc_email: str | None = Field(None, description="Optional BCC email address")

class EmailMessageDefinition(PermissiveModel):
    channel: Literal["email"]
    label: str | None = Field(None, description="The label or name on the message")
    content: EmailContent | None = Field(None, description="Additional attributes relating to the content of the message")

class EmailSendOptions(PermissiveModel):
    use_smart_sending: bool | None = Field(True, description="Use smart sending.")

class EqualsStringFilter(PermissiveModel):
    type_: Literal["string"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["equals"]
    value: str | None = Field(...)

class CustomSourceFilter(PermissiveModel):
    field: Literal["custom_source"]
    filter_: EqualsStringFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class ErrorMessages(PermissiveModel):
    required: str | None = 'This field is required'
    invalid: str | None = 'This field is invalid'

class AgeGateProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    label: str | None = None
    show_label: bool | None = False
    placeholder: str | None = None
    error_messages: ErrorMessages | None = None
    property_name: Literal["$age_gated_date_of_birth"] | None = '$age_gated_date_of_birth'
    date_format: str | None = 'MM/DD/YYYY'
    sms_country_code: Literal["AT", "AU", "CH", "DE", "ES", "FR", "GB", "IE", "IT", "PT", "US"] | None = Field('US', description="SMS County Code Enum.")
    required: Literal[True] | None = True

class BackInStockEmailConsentCheckboxProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    label: str | None = None
    show_label: bool | None = False
    error_messages: ErrorMessages | None = None
    required: Literal[False] | None = False
    property_name: Literal["opt_in_promotional_email"] | None = 'opt_in_promotional_email'
    checkbox_text: str
    placeholder: None = None

class DateProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    property_name: str
    label: str | None = None
    show_label: bool | None = False
    placeholder: str | None = None
    required: bool | None = False
    error_messages: ErrorMessages | None = None
    date_format: str | None = 'MM/DD'

class EmailProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    label: str | None = None
    show_label: bool | None = False
    placeholder: str | None = None
    required: bool | None = False
    error_messages: ErrorMessages | None = None
    property_name: Literal["$email"] | None = '$email'

class ExistenceOperatorExistenceFilter(PermissiveModel):
    type_: Literal["existence"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["is-set", "not-set"] = Field(..., description="Operators for existence filters.")

class FailedAgeGateMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["failed_age_gate"]

class FixedTimerConfiguration(PermissiveModel):
    type_: Literal["fixed"] = Field(..., validation_alias="type", serialization_alias="type")
    timezone_: Literal["Africa/Abidjan", "Africa/Accra", "Africa/Addis_Ababa", "Africa/Algiers", "Africa/Asmara", "Africa/Asmera", "Africa/Bamako", "Africa/Bangui", "Africa/Banjul", "Africa/Bissau", "Africa/Blantyre", "Africa/Brazzaville", "Africa/Bujumbura", "Africa/Cairo", "Africa/Casablanca", "Africa/Ceuta", "Africa/Conakry", "Africa/Dakar", "Africa/Dar_es_Salaam", "Africa/Djibouti", "Africa/Douala", "Africa/El_Aaiun", "Africa/Freetown", "Africa/Gaborone", "Africa/Harare", "Africa/Johannesburg", "Africa/Juba", "Africa/Kampala", "Africa/Khartoum", "Africa/Kigali", "Africa/Kinshasa", "Africa/Lagos", "Africa/Libreville", "Africa/Lome", "Africa/Luanda", "Africa/Lubumbashi", "Africa/Lusaka", "Africa/Malabo", "Africa/Maputo", "Africa/Maseru", "Africa/Mbabane", "Africa/Mogadishu", "Africa/Monrovia", "Africa/Nairobi", "Africa/Ndjamena", "Africa/Niamey", "Africa/Nouakchott", "Africa/Ouagadougou", "Africa/Porto-Novo", "Africa/Sao_Tome", "Africa/Timbuktu", "Africa/Tripoli", "Africa/Tunis", "Africa/Windhoek", "America/Adak", "America/Anchorage", "America/Anguilla", "America/Antigua", "America/Araguaina", "America/Argentina/Buenos_Aires", "America/Argentina/Catamarca", "America/Argentina/ComodRivadavia", "America/Argentina/Cordoba", "America/Argentina/Jujuy", "America/Argentina/La_Rioja", "America/Argentina/Mendoza", "America/Argentina/Rio_Gallegos", "America/Argentina/Salta", "America/Argentina/San_Juan", "America/Argentina/San_Luis", "America/Argentina/Tucuman", "America/Argentina/Ushuaia", "America/Aruba", "America/Asuncion", "America/Atikokan", "America/Atka", "America/Bahia", "America/Bahia_Banderas", "America/Barbados", "America/Belem", "America/Belize", "America/Blanc-Sablon", "America/Boa_Vista", "America/Bogota", "America/Boise", "America/Buenos_Aires", "America/Cambridge_Bay", "America/Campo_Grande", "America/Cancun", "America/Caracas", "America/Catamarca", "America/Cayenne", "America/Cayman", "America/Chicago", "America/Chihuahua", "America/Ciudad_Juarez", "America/Coral_Harbour", "America/Cordoba", "America/Costa_Rica", "America/Creston", "America/Cuiaba", "America/Curacao", "America/Danmarkshavn", "America/Dawson", "America/Dawson_Creek", "America/Denver", "America/Detroit", "America/Dominica", "America/Edmonton", "America/Eirunepe", "America/El_Salvador", "America/Ensenada", "America/Fort_Nelson", "America/Fort_Wayne", "America/Fortaleza", "America/Glace_Bay", "America/Godthab", "America/Goose_Bay", "America/Grand_Turk", "America/Grenada", "America/Guadeloupe", "America/Guatemala", "America/Guayaquil", "America/Guyana", "America/Halifax", "America/Havana", "America/Hermosillo", "America/Indiana/Indianapolis", "America/Indiana/Knox", "America/Indiana/Marengo", "America/Indiana/Petersburg", "America/Indiana/Tell_City", "America/Indiana/Vevay", "America/Indiana/Vincennes", "America/Indiana/Winamac", "America/Indianapolis", "America/Inuvik", "America/Iqaluit", "America/Jamaica", "America/Jujuy", "America/Juneau", "America/Kentucky/Louisville", "America/Kentucky/Monticello", "America/Knox_IN", "America/Kralendijk", "America/La_Paz", "America/Lima", "America/Los_Angeles", "America/Louisville", "America/Lower_Princes", "America/Maceio", "America/Managua", "America/Manaus", "America/Marigot", "America/Martinique", "America/Matamoros", "America/Mazatlan", "America/Mendoza", "America/Menominee", "America/Merida", "America/Metlakatla", "America/Mexico_City", "America/Miquelon", "America/Moncton", "America/Monterrey", "America/Montevideo", "America/Montreal", "America/Montserrat", "America/Nassau", "America/New_York", "America/Nipigon", "America/Nome", "America/Noronha", "America/North_Dakota/Beulah", "America/North_Dakota/Center", "America/North_Dakota/New_Salem", "America/Nuuk", "America/Ojinaga", "America/Panama", "America/Pangnirtung", "America/Paramaribo", "America/Phoenix", "America/Port-au-Prince", "America/Port_of_Spain", "America/Porto_Acre", "America/Porto_Velho", "America/Puerto_Rico", "America/Punta_Arenas", "America/Rainy_River", "America/Rankin_Inlet", "America/Recife", "America/Regina", "America/Resolute", "America/Rio_Branco", "America/Rosario", "America/Santa_Isabel", "America/Santarem", "America/Santiago", "America/Santo_Domingo", "America/Sao_Paulo", "America/Scoresbysund", "America/Shiprock", "America/Sitka", "America/St_Barthelemy", "America/St_Johns", "America/St_Kitts", "America/St_Lucia", "America/St_Thomas", "America/St_Vincent", "America/Swift_Current", "America/Tegucigalpa", "America/Thule", "America/Thunder_Bay", "America/Tijuana", "America/Toronto", "America/Tortola", "America/Vancouver", "America/Virgin", "America/Whitehorse", "America/Winnipeg", "America/Yakutat", "America/Yellowknife", "Antarctica/Casey", "Antarctica/Davis", "Antarctica/DumontDUrville", "Antarctica/Macquarie", "Antarctica/Mawson", "Antarctica/McMurdo", "Antarctica/Palmer", "Antarctica/Rothera", "Antarctica/South_Pole", "Antarctica/Syowa", "Antarctica/Troll", "Antarctica/Vostok", "Arctic/Longyearbyen", "Asia/Aden", "Asia/Almaty", "Asia/Amman", "Asia/Anadyr", "Asia/Aqtau", "Asia/Aqtobe", "Asia/Ashgabat", "Asia/Ashkhabad", "Asia/Atyrau", "Asia/Baghdad", "Asia/Bahrain", "Asia/Baku", "Asia/Bangkok", "Asia/Barnaul", "Asia/Beirut", "Asia/Bishkek", "Asia/Brunei", "Asia/Calcutta", "Asia/Chita", "Asia/Choibalsan", "Asia/Chongqing", "Asia/Chungking", "Asia/Colombo", "Asia/Dacca", "Asia/Damascus", "Asia/Dhaka", "Asia/Dili", "Asia/Dubai", "Asia/Dushanbe", "Asia/Famagusta", "Asia/Gaza", "Asia/Harbin", "Asia/Hebron", "Asia/Ho_Chi_Minh", "Asia/Hong_Kong", "Asia/Hovd", "Asia/Irkutsk", "Asia/Istanbul", "Asia/Jakarta", "Asia/Jayapura", "Asia/Jerusalem", "Asia/Kabul", "Asia/Kamchatka", "Asia/Karachi", "Asia/Kashgar", "Asia/Kathmandu", "Asia/Katmandu", "Asia/Khandyga", "Asia/Kolkata", "Asia/Krasnoyarsk", "Asia/Kuala_Lumpur", "Asia/Kuching", "Asia/Kuwait", "Asia/Macao", "Asia/Macau", "Asia/Magadan", "Asia/Makassar", "Asia/Manila", "Asia/Muscat", "Asia/Nicosia", "Asia/Novokuznetsk", "Asia/Novosibirsk", "Asia/Omsk", "Asia/Oral", "Asia/Phnom_Penh", "Asia/Pontianak", "Asia/Pyongyang", "Asia/Qatar", "Asia/Qostanay", "Asia/Qyzylorda", "Asia/Rangoon", "Asia/Riyadh", "Asia/Saigon", "Asia/Sakhalin", "Asia/Samarkand", "Asia/Seoul", "Asia/Shanghai", "Asia/Singapore", "Asia/Srednekolymsk", "Asia/Taipei", "Asia/Tashkent", "Asia/Tbilisi", "Asia/Tehran", "Asia/Tel_Aviv", "Asia/Thimbu", "Asia/Thimphu", "Asia/Tokyo", "Asia/Tomsk", "Asia/Ujung_Pandang", "Asia/Ulaanbaatar", "Asia/Ulan_Bator", "Asia/Urumqi", "Asia/Ust-Nera", "Asia/Vientiane", "Asia/Vladivostok", "Asia/Yakutsk", "Asia/Yangon", "Asia/Yekaterinburg", "Asia/Yerevan", "Atlantic/Azores", "Atlantic/Bermuda", "Atlantic/Canary", "Atlantic/Cape_Verde", "Atlantic/Faeroe", "Atlantic/Faroe", "Atlantic/Jan_Mayen", "Atlantic/Madeira", "Atlantic/Reykjavik", "Atlantic/South_Georgia", "Atlantic/St_Helena", "Atlantic/Stanley", "Australia/ACT", "Australia/Adelaide", "Australia/Brisbane", "Australia/Broken_Hill", "Australia/Canberra", "Australia/Currie", "Australia/Darwin", "Australia/Eucla", "Australia/Hobart", "Australia/LHI", "Australia/Lindeman", "Australia/Lord_Howe", "Australia/Melbourne", "Australia/NSW", "Australia/North", "Australia/Perth", "Australia/Queensland", "Australia/South", "Australia/Sydney", "Australia/Tasmania", "Australia/Victoria", "Australia/West", "Australia/Yancowinna", "Brazil/Acre", "Brazil/DeNoronha", "Brazil/East", "Brazil/West", "CET", "CST6CDT", "Canada/Atlantic", "Canada/Central", "Canada/Eastern", "Canada/Mountain", "Canada/Newfoundland", "Canada/Pacific", "Canada/Saskatchewan", "Canada/Yukon", "Chile/Continental", "Chile/EasterIsland", "Cuba", "EET", "EST", "EST5EDT", "Egypt", "Eire", "Etc/GMT", "Etc/GMT+0", "Etc/GMT+1", "Etc/GMT+10", "Etc/GMT+11", "Etc/GMT+12", "Etc/GMT+2", "Etc/GMT+3", "Etc/GMT+4", "Etc/GMT+5", "Etc/GMT+6", "Etc/GMT+7", "Etc/GMT+8", "Etc/GMT+9", "Etc/GMT-0", "Etc/GMT-1", "Etc/GMT-10", "Etc/GMT-11", "Etc/GMT-12", "Etc/GMT-13", "Etc/GMT-14", "Etc/GMT-2", "Etc/GMT-3", "Etc/GMT-4", "Etc/GMT-5", "Etc/GMT-6", "Etc/GMT-7", "Etc/GMT-8", "Etc/GMT-9", "Etc/GMT0", "Etc/Greenwich", "Etc/UCT", "Etc/UTC", "Etc/Universal", "Etc/Zulu", "Europe/Amsterdam", "Europe/Andorra", "Europe/Astrakhan", "Europe/Athens", "Europe/Belfast", "Europe/Belgrade", "Europe/Berlin", "Europe/Bratislava", "Europe/Brussels", "Europe/Bucharest", "Europe/Budapest", "Europe/Busingen", "Europe/Chisinau", "Europe/Copenhagen", "Europe/Dublin", "Europe/Gibraltar", "Europe/Guernsey", "Europe/Helsinki", "Europe/Isle_of_Man", "Europe/Istanbul", "Europe/Jersey", "Europe/Kaliningrad", "Europe/Kiev", "Europe/Kirov", "Europe/Kyiv", "Europe/Lisbon", "Europe/Ljubljana", "Europe/London", "Europe/Luxembourg", "Europe/Madrid", "Europe/Malta", "Europe/Mariehamn", "Europe/Minsk", "Europe/Monaco", "Europe/Moscow", "Europe/Nicosia", "Europe/Oslo", "Europe/Paris", "Europe/Podgorica", "Europe/Prague", "Europe/Riga", "Europe/Rome", "Europe/Samara", "Europe/San_Marino", "Europe/Sarajevo", "Europe/Saratov", "Europe/Simferopol", "Europe/Skopje", "Europe/Sofia", "Europe/Stockholm", "Europe/Tallinn", "Europe/Tirane", "Europe/Tiraspol", "Europe/Ulyanovsk", "Europe/Uzhgorod", "Europe/Vaduz", "Europe/Vatican", "Europe/Vienna", "Europe/Vilnius", "Europe/Volgograd", "Europe/Warsaw", "Europe/Zagreb", "Europe/Zaporozhye", "Europe/Zurich", "GB", "GB-Eire", "GMT", "GMT+0", "GMT-0", "GMT0", "Greenwich", "HST", "Hongkong", "Iceland", "Indian/Antananarivo", "Indian/Chagos", "Indian/Christmas", "Indian/Cocos", "Indian/Comoro", "Indian/Kerguelen", "Indian/Mahe", "Indian/Maldives", "Indian/Mauritius", "Indian/Mayotte", "Indian/Reunion", "Iran", "Israel", "Jamaica", "Japan", "Kwajalein", "Libya", "MET", "MST", "MST7MDT", "Mexico/BajaNorte", "Mexico/BajaSur", "Mexico/General", "NZ", "NZ-CHAT", "Navajo", "PRC", "PST8PDT", "Pacific/Apia", "Pacific/Auckland", "Pacific/Bougainville", "Pacific/Chatham", "Pacific/Chuuk", "Pacific/Easter", "Pacific/Efate", "Pacific/Enderbury", "Pacific/Fakaofo", "Pacific/Fiji", "Pacific/Funafuti", "Pacific/Galapagos", "Pacific/Gambier", "Pacific/Guadalcanal", "Pacific/Guam", "Pacific/Honolulu", "Pacific/Johnston", "Pacific/Kanton", "Pacific/Kiritimati", "Pacific/Kosrae", "Pacific/Kwajalein", "Pacific/Majuro", "Pacific/Marquesas", "Pacific/Midway", "Pacific/Nauru", "Pacific/Niue", "Pacific/Norfolk", "Pacific/Noumea", "Pacific/Pago_Pago", "Pacific/Palau", "Pacific/Pitcairn", "Pacific/Pohnpei", "Pacific/Ponape", "Pacific/Port_Moresby", "Pacific/Rarotonga", "Pacific/Saipan", "Pacific/Samoa", "Pacific/Tahiti", "Pacific/Tarawa", "Pacific/Tongatapu", "Pacific/Truk", "Pacific/Wake", "Pacific/Wallis", "Pacific/Yap", "Poland", "Portugal", "ROC", "ROK", "Singapore", "Turkey", "UCT", "US/Alaska", "US/Aleutian", "US/Arizona", "US/Central", "US/East-Indiana", "US/Eastern", "US/Hawaii", "US/Indiana-Starke", "US/Michigan", "US/Mountain", "US/Pacific", "US/Samoa", "UTC", "Universal", "W-SU", "WET", "Zulu"] = Field(..., validation_alias="timezone", serialization_alias="timezone")
    end_time: str | None = Field(None, json_schema_extra={'format': 'date-time'})

class GoToInbox(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    submit: Literal[True] | None = True
    type_: Literal["go_to_inbox"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: None = None

class GreaterThanPositiveNumericFilter(PermissiveModel):
    type_: Literal["numeric"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["greater-than"]
    value: int | float

class HasEmailMarketing(PermissiveModel):
    subscription: Literal["any"]
    filters: Any | None = None

class HasEmailMarketingNeverSubscribed(PermissiveModel):
    subscription: Literal["never_subscribed"]
    filters: Any | None = None

class HorizontalRuleBlock(PermissiveModel):
    content_type: Literal["block"]
    type_: Literal["horizontal_rule"] = Field(..., validation_alias="type", serialization_alias="type")
    data: Any | None = Field(...)

class HtmlBlockData(PermissiveModel):
    content: str
    display_options: BlockDisplayOptions

class HtmlBlock(PermissiveModel):
    content_type: Literal["block"]
    type_: Literal["html"] = Field(..., validation_alias="type", serialization_alias="type")
    data: HtmlBlockData

class HtmlTextProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    content: str | None = ''

class ImageAssetProperties(PermissiveModel):
    src: str | None = None
    alt_text: str | None = None
    original_image_url: str | None = None
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id")
    asset_id: int | None = None

class BackgroundImage(PermissiveModel):
    styles: BackgroundImageStyles | None = None
    properties: ImageAssetProperties

class ColumnStyles(PermissiveModel):
    background_image: BackgroundImage | None = None
    background_color: str | None = None

class ImageBlock(PermissiveModel):
    content_type: Literal["block"]
    type_: Literal["image"] = Field(..., validation_alias="type", serialization_alias="type")
    data: Any | None = Field(...)

class ImageDropShadowStyles(PermissiveModel):
    enabled: bool | None = False
    color: str | None = '#000000'
    blur: int | None = 15
    x_offset: int | None = 0
    y_offset: int | None = 0

class ImageProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    image: ImageAssetProperties | None = Field(...)
    additional_fields: list[AdditionalField] | None = None

class ImmediateSendStrategy(PermissiveModel):
    method: Literal["immediate"]

class ImplicitlyOrExplicitlyReachable(PermissiveModel):
    reachable_status: Literal["implicitly_or_explicitly_reachable"]

class ImplicitlyOrExplicitlyUnreachable(PermissiveModel):
    reachable_status: Literal["implicitly_or_explicitly_unreachable"]

class ImplicitlyReachable(PermissiveModel):
    reachable_status: Literal["implicitly_reachable"]

class ImplicitlyUnreachable(PermissiveModel):
    reachable_status: Literal["implicitly_unreachable"]

class InStringArrayFilter(PermissiveModel):
    type_: Literal["string"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["in"]
    value: list[str]

class ApiMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["api"]
    filter_: InStringArrayFilter | None = Field(None, validation_alias="filter", serialization_alias="filter", description="Optional filter on a specific list of API keys (using last 4 digits of the key)")

class FormMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["form"]
    filter_: InStringArrayFilter | None = Field(None, validation_alias="filter", serialization_alias="filter", description="Optional filter on a specific list of form ids")

class FormSubscribeFilter(PermissiveModel):
    field: Literal["subscribe_method"]
    method: Literal["form"]
    filter_: InStringArrayFilter | None = Field(None, validation_alias="filter", serialization_alias="filter", description="Optional filter on a specific list of form IDs")

class InboundMessageMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["inbound_message"]

class IntegerFilter(PermissiveModel):
    type_: Literal["numeric"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["equals", "greater-than", "greater-than-or-equal", "less-than", "less-than-or-equal", "not-equals"] = Field(..., description="Operators for numeric filters.")
    value: int

class IsSetExistenceFilter(PermissiveModel):
    type_: Literal["existence"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["is-set"]

class LessThanPositiveNumericFilter(PermissiveModel):
    type_: Literal["numeric"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["less-than"]
    value: int | float

class LinkStyles(PermissiveModel):
    color: str | None = '#0066cc'
    decoration: Literal["underline"] | None = 'underline'

class ListContainsOperatorListContainsFilter(PermissiveModel):
    type_: Literal["list"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["contains", "not-contains"] = Field(..., description="Operators for list contains filters.")
    value: int | str | None = Field(...)

class ListLengthFilter(PermissiveModel):
    type_: Literal["list"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["length-equals", "length-greater-than", "length-greater-than-or-equal", "length-less-than", "length-less-than-or-equal"] = Field(..., description="Operators for list length filters.")
    value: int

class ListRegexOperatorListContainsFilter(PermissiveModel):
    type_: Literal["list"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["contains-ends-with", "contains-starts-with", "not-contains-ends-with", "not-contains-starts-with"] = Field(..., description="Operators for list regex filters.")
    value: int | str | None = Field(...)

class ListSetFilter(PermissiveModel):
    type_: Literal["list"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["contains-all", "contains-any", "not-contains-all", "not-contains-any"] = Field(..., description="Operators for list contains set filters.")
    value: list[str]

class ListSubstringFilter(PermissiveModel):
    type_: Literal["list"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["contains-substring", "not-contains-substring"] = Field(..., description="Operators for list substring filters.")
    value: str | None = Field(...)

class ListsAndSegmentsProperties(PermissiveModel):
    allow_list: list[str] | None = None
    deny_list: list[str] | None = None

class ListsAndSegments(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["lists_and_segments"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: ListsAndSegmentsProperties

class LocalStaticSend(PermissiveModel):
    is_local: Literal[True] = Field(..., description="Whether the campaign should be sent with local recipient timezone send (requires UTC time) or statically sent at the given time.")
    send_past_recipients_immediately: bool | None = Field(False, description="Determines if we should send to local recipient timezone if the given time has passed. Only applicable to local sends.")

class LocationProperties(PermissiveModel):
    allow_list: list[Literal["con_AF", "con_AS", "con_EU", "con_EUP", "con_NA", "con_OC", "con_SA"] | Literal["AD", "AE", "AF", "AG", "AI", "AL", "AM", "AN", "AO", "AQ", "AR", "AS", "AT", "AU", "AW", "AX", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BM", "BN", "BO", "BR", "BS", "BT", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN", "CO", "CR", "CU", "CV", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE", "EG", "EH", "ER", "ES", "ET", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF", "GG", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM", "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IO", "IQ", "IR", "IS", "IT", "JE", "JM", "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME", "MG", "MH", "MK", "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM", "PN", "PR", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW", "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "ST", "SV", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI", "VN", "VU", "WF", "WS", "YE", "YT", "ZA", "ZM", "ZW"]] | None = None
    deny_list: list[Literal["con_AF", "con_AS", "con_EU", "con_EUP", "con_NA", "con_OC", "con_SA"] | Literal["AD", "AE", "AF", "AG", "AI", "AL", "AM", "AN", "AO", "AQ", "AR", "AS", "AT", "AU", "AW", "AX", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BM", "BN", "BO", "BR", "BS", "BT", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN", "CO", "CR", "CU", "CV", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE", "EG", "EH", "ER", "ES", "ET", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF", "GG", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM", "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IO", "IQ", "IR", "IS", "IT", "JE", "JM", "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME", "MG", "MH", "MK", "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM", "PN", "PR", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW", "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "ST", "SV", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI", "VN", "VU", "WF", "WS", "YE", "YT", "ZA", "ZM", "ZW"]] | None = None

class Location(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["location"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: LocationProperties

class MailboxProviderMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["mailbox_provider"]

class ManualAddManualMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["manual_add"]
    filter_: InStringArrayFilter | None = Field(None, validation_alias="filter", serialization_alias="filter", description="Optional filter on a specific list of user email addresses who initiated the manual action")

class ManualImportManualMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["manual_import"]
    filter_: InStringArrayFilter | None = Field(None, validation_alias="filter", serialization_alias="filter", description="Optional filter on a specific list of user email addresses who initiated the manual action")

class ManualImportMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["manual_import"]

class ManualRemoveMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["manual_remove"]

class Margin(PermissiveModel):
    left: int | None = 0
    right: int | None = 0
    top: int | None = 0
    bottom: int | None = 0

class CloseButtonStyle(PermissiveModel):
    background_color: str | None = 'rgba(180, 187, 195, 0.65)'
    outline_color: str | None = '#FFFFFF'
    color: str | None = '#FFFFFF'
    stroke: float | None = 2
    size: int | None = 20
    margin: Margin | None = None

class MergeProfilesBodyDataRelationshipsProfilesDataItem(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of a source profile to merge into the destination profile")

class MessageBlockedMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["message_blocked"]

class MethodFilter(PermissiveModel):
    field: Literal["subscribe_method"]
    method: Literal["api", "back_in_stock", "bigcommerce", "bulk_remove", "campaign_monitor", "carrier_deactivation", "checkout", "constant_contact", "exact_target", "facebook", "failed_age_gate", "inbound_message", "integration", "mad_mimi", "magento_two", "mailbox_provider", "manual_add", "manual_import", "manual_remove", "message_blocked", "netsuite", "preference_page", "provided_landline", "provided_no_age", "sftp", "shopify", "social_instagram_message", "spam_complaint", "square", "wix", "woocommerce"] = Field(..., description="Method for subscribing / unsubscribing.")

class MetricCreateQueryResourceObjectAttributes(PermissiveModel):
    name: str = Field(..., description="Name of the event. Must be less than 128 characters.")
    service: str | None = Field(None, description="This is for advanced usage. For api requests, this should use the default, which is set to api.")

class MetricCreateQueryResourceObject(PermissiveModel):
    type_: Literal["metric"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: MetricCreateQueryResourceObjectAttributes

class BaseEventCreateQueryBulkEntryResourceObjectAttributesMetric(PermissiveModel):
    data: MetricCreateQueryResourceObject

class BaseEventCreateQueryBulkEntryResourceObjectAttributes(PermissiveModel):
    properties: dict[str, Any] = Field(..., description="Properties of this event (must not exceed 400 properties). The size of the event payload must not exceed 5 MB,\nand each string cannot be larger than 100 KB. For a full list of data limits on event payloads,\nsee [Limitations](https://developers.klaviyo.com/en/reference/events_api_overview#limitations).\n\nNote any top-level property that is not an object can be\nused to create segments. The `$extra` property records any\nnon-segmentable values that can be referenced later, e.g., HTML templates are\nuseful on a segment but are not used to create a segment.")
    time_: str | None = Field(None, validation_alias="time", serialization_alias="time", description="When this event occurred. By default, the time the request was received will be used.\nThe time is truncated to the second. The time must be after the year 2000 and can only\nbe up to 1 year in the future.", json_schema_extra={'format': 'date-time'})
    value: float | None = Field(None, description="A numeric, monetary value to associate with this event. For example, the dollar amount of a purchase.")
    value_currency: str | None = Field(None, description="The ISO 4217 currency code of the value associated with the event.")
    metric: BaseEventCreateQueryBulkEntryResourceObjectAttributesMetric
    unique_id: str | None = Field(None, description="A unique identifier for an event. If a unique_id is repeated for the same profile and metric,\nthe request will fail and no events will be processed. If this field is not\npresent, this field will use the time to the second. Using the default, this limits only one\nevent per profile per second.")

class BaseEventCreateQueryBulkEntryResourceObject(PermissiveModel):
    type_: Literal["event"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: BaseEventCreateQueryBulkEntryResourceObjectAttributes

class EventsBulkCreateQueryResourceObjectAttributesEvents(PermissiveModel):
    data: list[BaseEventCreateQueryBulkEntryResourceObject]

class MobileOverlay(PermissiveModel):
    color: str | None = 'rgba(20, 20, 20, 0.5)'
    enabled: Literal[False] | None = False

class MobilePushBadge(PermissiveModel):
    display: Literal[True] = Field(..., description="Whether to display a badge on the app icon")
    badge_options: CampaignMessageIncrement | CampaignMessageStaticCount | CampaignMessageProperty | None = Field(None, description="Badge options")

class MobilePushContentUpdate(PermissiveModel):
    title: str | None = Field(None, description="The title of the message")
    body: str | None = Field(None, description="The message body")
    dynamic_image: str | None = Field(None, description="The dynamic image to be used in the push notification")

class MobilePushMessageSilentDefinitionUpdate(PermissiveModel):
    channel: Literal["mobile_push"]
    kv_pairs: dict[str, Any] | None = Field(None, description="The key-value pairs to be sent with the push notification")
    notification_type: Literal["silent"] | None = Field('silent', description="The type of notification to send")

class MobilePushNoBadge(PermissiveModel):
    display: Literal[False] = Field(..., description="Whether to display a badge on the app icon")

class NextStepProperties(PermissiveModel):
    list_id: str | None = None

class NextStep(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    submit: bool
    type_: Literal["next_step"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: NextStepProperties | None = None

class NoPushMarketing(PermissiveModel):
    subscription: Literal["any"]

class NoPushMarketingConsent(PermissiveModel):
    channel: Literal["push"]
    can_receive_marketing: Literal[False]
    consent_status: NoPushMarketing

class NoSmsMarketing(PermissiveModel):
    subscription: Literal["any"]

class NoSmsMarketingNeverSubscribed(PermissiveModel):
    subscription: Literal["never_subscribed"]

class NonLocalStaticSend(PermissiveModel):
    is_local: Literal[False] = Field(..., description="Whether the campaign should be sent with local recipient timezone send (requires UTC time) or statically sent at the given time.")

class NumericOperatorNumericFilter(PermissiveModel):
    type_: Literal["numeric"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["equals", "greater-than", "greater-than-or-equal", "less-than", "less-than-or-equal", "not-equals"] = Field(..., description="Operators for numeric filters.")
    value: int | float

class NumericRangeFilter(PermissiveModel):
    type_: Literal["numeric"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["between"] = Field(..., description="Operators for numeric range filters.")
    start: int | float
    end: int | float

class OneClickUnsubscribeMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["one_click_unsubscribe"]

class OpenFormProperties(PermissiveModel):
    close_form: bool | None = True
    form_id_to_open: str

class OpenForm(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["open_form"] = Field(..., validation_alias="type", serialization_alias="type")
    submit: Literal[True] | None = True
    properties: OpenFormProperties

class OptInCodeProperties(PermissiveModel):
    label: str | None = None
    show_label: bool | None = False
    placeholder: str | None = None
    error_messages: ErrorMessages | None = None
    property_name: Literal["opt_in_code"] | None = 'opt_in_code'
    required: Literal[True] | None = True
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None

class Padding(PermissiveModel):
    left: int | None = 0
    right: int | None = 0
    top: int | None = 0
    bottom: int | None = 0

class AgeGateStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None

class AgeGate(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["age_gate"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: AgeGateStyles | None = None
    properties: AgeGateProperties
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None

class BackInStockEmailConsentCheckboxStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None
    horizontal_alignment: Literal["center", "left", "right"] | None = Field('left', description="Horizontal alignment enumeration.")

class BackInStockEmailConsentCheckbox(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["bis_promotional_email_checkbox"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: BackInStockEmailConsentCheckboxStyles | None = None
    properties: BackInStockEmailConsentCheckboxProperties

class CheckboxesStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None
    arrangement: Literal["horizontal", "vertical"] | None = Field('vertical', description="Arrangement enumeration.")
    alignment: Literal["center", "left", "right"] | None = Field('left', description="Horizontal alignment enumeration.")

class DateStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None

class Date(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["date"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: DateStyles | None = None
    properties: DateProperties

class DropdownStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None

class EmailStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None

class Email(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["email"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: EmailStyles | None = None
    properties: EmailProperties

class HtmlTextStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None

class HtmlText(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["html_text"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: HtmlTextStyles | None = None
    properties: HtmlTextProperties | None = None

class ImageStyles(PermissiveModel):
    horizontal_alignment: Literal["center", "left", "right"] | None = Field('center', description="Horizontal alignment enumeration.")
    width: int | None = None
    padding: Padding | None = None
    background_color: str | None = None
    drop_shadow: ImageDropShadowStyles | None = None

class OptInCodeStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None

class OptInCode(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["opt_in_code"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: OptInCodeStyles | None = None
    properties: OptInCodeProperties

class PageVisitsProperties(PermissiveModel):
    pages: int | None = 3

class PageVisits(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["page_visits"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: PageVisitsProperties | None = None

class PhoneNumberConsentChannelSettings(PermissiveModel):
    consent_type: Literal["phone_number_only", "promotional", "transactional"] | None = Field(None, description="Consent Type Enum.")

class ChannelSettings(PermissiveModel):
    sms: PhoneNumberConsentChannelSettings | None = None
    whatsapp: PhoneNumberConsentChannelSettings | None = None

class PhoneNumberProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    label: str | None = None
    show_label: bool | None = False
    placeholder: str | None = None
    required: bool | None = False
    error_messages: ErrorMessages | None = None
    property_name: str | None = '$phone_number'
    sms_consent_type: list[Literal["phone_number_only", "promotional", "transactional"]] | None = None
    channel_settings: ChannelSettings | None = None

class PhoneNumberStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None

class PhoneNumber(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["phone_number"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: PhoneNumberStyles | None = None
    properties: PhoneNumberProperties

class PreferencePageFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["preference_page"]
    filter_: EqualsStringFilter | None = Field(None, validation_alias="filter", serialization_alias="filter", description="Optional filter on a specific subscribe page url")

class PreferencePageMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["preference_page"]

class ProfileEventTrackedProperties(PermissiveModel):
    metric: str

class ProfileEventTracked(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["profile_event_tracked"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: ProfileEventTrackedProperties

class ProfileLocation(PermissiveModel):
    address1: str | None = Field(None, description="First line of street address")
    address2: str | None = Field(None, description="Second line of street address")
    city: str | None = Field(None, description="City name")
    country: str | None = Field(None, description="Country name")
    latitude: str | float | None = Field(None, description="Latitude coordinate. We recommend providing a precision of four decimal places.")
    longitude: str | float | None = Field(None, description="Longitude coordinate. We recommend providing a precision of four decimal places.")
    region: str | None = Field(None, description="Region within a country, such as state or province")
    zip_: str | None = Field(None, validation_alias="zip", serialization_alias="zip", description="Zip code")
    timezone_: str | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="Time zone name. We recommend using time zones from the IANA Time Zone Database.")
    ip: str | None = Field(None, description="IP Address")

class OnsiteProfileCreateQueryResourceObjectAttributes(PermissiveModel):
    email: str | None = Field(None, description="Individual's email address")
    phone_number: str | None = Field(None, description="Individual's phone number in E.164 format")
    external_id: str | None = Field(None, description="A unique identifier used by customers to associate Klaviyo profiles with profiles in an external system, such as a point-of-sale system. Format varies based on the external system.")
    anonymous_id: str | None = None
    kx: str | None = Field(None, validation_alias="_kx", serialization_alias="_kx", description="Also known as the `exchange_id`, this is an encrypted identifier used for identifying a\nprofile by Klaviyo's web tracking.\n\nYou can use this field as a filter when retrieving profiles via the Get Profiles endpoint.")
    first_name: str | None = Field(None, description="Individual's first name")
    last_name: str | None = Field(None, description="Individual's last name")
    organization: str | None = Field(None, description="Name of the company or organization within the company for whom the individual works")
    locale: str | None = Field(None, description="The locale of the profile, in the IETF BCP 47 language tag format like (ISO 639-1/2)-(ISO 3166 alpha-2)")
    title: str | None = Field(None, description="Individual's job title")
    image: str | None = Field(None, description="URL pointing to the location of a profile image")
    location: ProfileLocation | None = None
    properties: dict[str, Any] | None = Field(None, description="An object containing key/value pairs for any custom properties assigned to this profile")

class ProfileMetaPatchProperties(PermissiveModel):
    append: dict[str, Any] | None = Field(None, description="Append a simple value or values to this property array")
    unappend: dict[str, Any] | None = Field(None, description="Remove a simple value or values from this property array")
    unset: str | list[str] | None = Field(None, description="Remove a key or keys (and their values) completely from properties")

class OnsiteProfileMeta(PermissiveModel):
    patch_properties: ProfileMetaPatchProperties | None = Field(None, description="Specify one or more patch operations to apply to existing property data")

class OnsiteProfileCreateQueryResourceObject(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Primary key that uniquely identifies this profile. Generated by Klaviyo.")
    attributes: OnsiteProfileCreateQueryResourceObjectAttributes
    meta: OnsiteProfileMeta | None = None

class EventsBulkCreateQueryResourceObjectAttributesProfile(PermissiveModel):
    data: OnsiteProfileCreateQueryResourceObject

class EventsBulkCreateQueryResourceObjectAttributes(PermissiveModel):
    profile: EventsBulkCreateQueryResourceObjectAttributesProfile
    events: EventsBulkCreateQueryResourceObjectAttributesEvents

class EventsBulkCreateQueryResourceObject(PermissiveModel):
    type_: Literal["event-bulk-create"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: EventsBulkCreateQueryResourceObjectAttributes

class ProfileMeta(PermissiveModel):
    patch_properties: ProfileMetaPatchProperties | None = Field(None, description="Specify one or more patch operations to apply to existing property data")

class ProfileModificationMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["profile_modification"]

class ProfileNoGroupMembershipCondition(PermissiveModel):
    type_: Literal["profile-group-membership"] = Field(..., validation_alias="type", serialization_alias="type")
    is_member: Literal[False]
    group_ids: list[str]

class ProfilePostalCodeDistanceCondition(PermissiveModel):
    type_: Literal["profile-postal-code-distance"] = Field(..., validation_alias="type", serialization_alias="type")
    country_code: str
    postal_code: str
    unit: Literal["kilometers", "miles"] = Field(..., description="Units for profile postal code distance conditions.")
    filter_: GreaterThanPositiveNumericFilter | LessThanPositiveNumericFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class ProfilePredictiveAnalyticsChannelAffinityPriorityFilter(PermissiveModel):
    type_: Literal["numeric"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["equals"]
    value: int

class ProfilePredictiveAnalyticsChannelAffinityPriorityCondition(PermissiveModel):
    type_: Literal["profile-predictive-analytics"] = Field(..., validation_alias="type", serialization_alias="type")
    dimension: Literal["channel_affinity"] = Field(..., description="Possible dimension for channel affinity criterion.")
    measurement: Literal["priority"]
    predicted_channel: Literal["email", "push", "sms"] = Field(..., description="Possible channels in a channel affinity definition.")
    filter_: ProfilePredictiveAnalyticsChannelAffinityPriorityFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class ProfilePredictiveAnalyticsChannelAffinityRankFilter(PermissiveModel):
    type_: Literal["string"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["equals"] | Literal["not-equals"]
    value: Literal["high", "low", "medium"] = Field(..., description="Possible rank values in a channel affinity definition.")

class ProfilePredictiveAnalyticsChannelAffinityRankCondition(PermissiveModel):
    type_: Literal["profile-predictive-analytics"] = Field(..., validation_alias="type", serialization_alias="type")
    dimension: Literal["channel_affinity"] = Field(..., description="Possible dimension for channel affinity criterion.")
    measurement: Literal["rank"]
    predicted_channel: Literal["email", "push", "sms"] = Field(..., description="Possible channels in a channel affinity definition.")
    filter_: ProfilePredictiveAnalyticsChannelAffinityRankFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class ProfilePredictiveAnalyticsNumericCondition(PermissiveModel):
    type_: Literal["profile-predictive-analytics"] = Field(..., validation_alias="type", serialization_alias="type")
    dimension: Literal["average_days_between_orders", "average_order_value", "churn_probability", "historic_clv", "historic_number_of_orders", "predicted_clv", "predicted_number_of_orders", "total_clv"] = Field(..., description="Dimensions for numeric profile predictive analytics conditions.")
    filter_: NumericOperatorNumericFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class ProfilePredictiveAnalyticsStringFilter(PermissiveModel):
    type_: Literal["string"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["equals"] | Literal["not-equals"]
    value: Literal["likely_female", "likely_male", "uncertain"] = Field(..., description="Values for profile predictive analytics gender conditions.")

class ProfilePredictiveAnalyticsStringCondition(PermissiveModel):
    type_: Literal["profile-predictive-analytics"] = Field(..., validation_alias="type", serialization_alias="type")
    dimension: Literal["predicted_gender"] = Field(..., description="Dimension for string profile predictive analytics conditions.")
    filter_: ProfilePredictiveAnalyticsStringFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class ProfileRegionCondition(PermissiveModel):
    type_: Literal["profile-region"] = Field(..., validation_alias="type", serialization_alias="type")
    in_region: bool
    region: Literal["european_union", "united_states"] = Field(..., description="Regions for profile region conditions.")

class ProfileSuppressionCreateQueryResourceObjectAttributes(PermissiveModel):
    email: str = Field(..., description="The email of the profile to suppress.")

class ProfileSuppressionCreateQueryResourceObject(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: ProfileSuppressionCreateQueryResourceObjectAttributes

class ProfileSuppressionDeleteQueryResourceObjectAttributes(PermissiveModel):
    email: str = Field(..., description="The email of the profile to unsuppress.")

class ProfileSuppressionDeleteQueryResourceObject(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: ProfileSuppressionDeleteQueryResourceObjectAttributes

class ProfileUpsertQueryResourceObjectAttributes(PermissiveModel):
    email: str | None = Field(None, description="Individual's email address")
    phone_number: str | None = Field(None, description="Individual's phone number in E.164 format")
    external_id: str | None = Field(None, description="A unique identifier used by customers to associate Klaviyo profiles with profiles in an external system, such as a point-of-sale system. Format varies based on the external system.")
    kx: str | None = Field(None, validation_alias="_kx", serialization_alias="_kx", description="Also known as the `exchange_id`, this is an encrypted identifier used for identifying a\nprofile by Klaviyo's web tracking.\n\nYou can use this field as a filter when retrieving profiles via the Get Profiles endpoint.")
    first_name: str | None = Field(None, description="Individual's first name")
    last_name: str | None = Field(None, description="Individual's last name")
    organization: str | None = Field(None, description="Name of the company or organization within the company for whom the individual works")
    locale: str | None = Field(None, description="The locale of the profile, in the IETF BCP 47 language tag format like (ISO 639-1/2)-(ISO 3166 alpha-2)")
    title: str | None = Field(None, description="Individual's job title")
    image: str | None = Field(None, description="URL pointing to the location of a profile image")
    location: ProfileLocation | None = None
    properties: dict[str, Any] | None = Field(None, description="An object containing key/value pairs for any custom properties assigned to this profile")

class ProfileUpsertQueryResourceObject(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Primary key that uniquely identifies this profile. Generated by Klaviyo.")
    attributes: ProfileUpsertQueryResourceObjectAttributes
    meta: ProfileMeta | None = None

class PromotionalSmsSubscription(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    submit: Literal[True] | None = True
    type_: Literal["promotional_sms_subscription"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: None = None

class PropertyOption(PermissiveModel):
    label: str
    value: str

class CheckboxesProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    property_name: str
    label: str | None = None
    show_label: bool | None = False
    required: bool | None = False
    error_messages: ErrorMessages | None = None
    options: list[PropertyOption]
    placeholder: str | None = None

class Checkboxes(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["checkboxes"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: CheckboxesStyles | None = None
    properties: CheckboxesProperties

class DropdownProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    property_name: str
    label: str | None = None
    show_label: bool | None = False
    required: bool | None = False
    error_messages: ErrorMessages | None = None
    options: list[PropertyOption]
    placeholder: str | None = None

class Dropdown(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["dropdown"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: DropdownStyles | None = None
    properties: DropdownProperties

class ProvidedLandlineMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["provided_landline"]

class ProvidedNoAgeMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["provided_no_age"]

class PushOnOpenApp(PermissiveModel):
    type_: Literal["open_app"] = Field(..., validation_alias="type", serialization_alias="type")

class PushOnOpenDeepLink(PermissiveModel):
    type_: Literal["deep_link"] = Field(..., validation_alias="type", serialization_alias="type")
    ios_deep_link: str | None = Field(None, description="required for all platforms enabled for push")
    android_deep_link: str | None = Field(None, description="required for all platforms enabled for push")

class MobilePushOptions(PermissiveModel):
    on_open: PushOnOpenApp | PushOnOpenDeepLink | None = None
    badge: MobilePushBadge | MobilePushNoBadge | None = Field(None, description="Only supported on iOS.")
    play_sound: bool | None = Field(False, description="Only supported on iOS.")

class MobilePushMessageStandardDefinitionUpdate(PermissiveModel):
    channel: Literal["mobile_push"]
    kv_pairs: dict[str, Any] | None = Field(None, description="The key-value pairs to be sent with the push notification")
    content: MobilePushContentUpdate | None = Field(None, description="Additional attributes relating to the content of the message")
    options: MobilePushOptions | None = Field(None, description="Additional device specific options for the push notification")
    notification_type: Literal["standard"] | None = Field('standard', description="The type of notification to send")

class PushSendOptions(PermissiveModel):
    use_smart_sending: bool | None = Field(True, description="Use smart sending.")

class PushTokenDeviceMetadata(PermissiveModel):
    device_id: str | None = Field(None, description="Relatively stable ID for the device. Will update on app uninstall and reinstall")
    klaviyo_sdk: Literal["android", "flutter", "flutter_community", "react_native", "swift"] | None = Field(None, description="The name of the SDK used to create the push token.")
    sdk_version: str | None = Field(None, description="The version of the SDK used to create the push token")
    device_model: str | None = Field(None, description="The model of the device")
    os_name: Literal["android", "ios", "ipados", "macos", "tvos"] | None = Field(None, description="The name of the operating system on the device.")
    os_version: str | None = Field(None, description="The version of the operating system on the device")
    manufacturer: str | None = Field(None, description="The manufacturer of the device")
    app_name: str | None = Field(None, description="The name of the app that created the push token")
    app_version: str | None = Field(None, description="The version of the app that created the push token")
    app_build: str | None = Field(None, description="The build of the app that created the push token")
    app_id: str | None = Field(None, description="The ID of the app that created the push token")
    environment: Literal["debug", "release"] | None = Field(None, description="The environment in which the push token was created")

class PushTokenEntry(PermissiveModel):
    token: str = Field(..., description="A push token from APNS or FCM.")
    platform: Literal["android", "ios"] = Field(..., description="The platform on which the push token was created. Either \"ios\" or \"android\".")
    vendor: Literal["apns", "fcm"] = Field(..., description="The vendor of the push token. Either \"apns\" or \"fcm\".")
    enablement_status: Literal["AUTHORIZED", "DENIED", "NOT_DETERMINED", "PROVISIONAL", "UNAUTHORIZED"] | None = Field(None, description="The enablement status for the push token.")
    background: Literal["AVAILABLE", "DENIED", "RESTRICTED"] | None = Field(None, description="The background state of the push token.")
    device_metadata: PushTokenDeviceMetadata | None = Field(None, description="Metadata about the device that created the push token.")

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsPush(PermissiveModel):
    """The subscription parameters to subscribe to on the "Push" Channel."""
    marketing: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsPushMarketing = Field(..., description="The parameters to subscribe to marketing on the \"Push\" channel.")
    tokens: list[PushTokenEntry] | None = Field(None, description="A list of push tokens to register for this profile.")
    anonymous_id: str | None = Field(None, description="An anonymous identifier for push-only profiles with no email/phone.")

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptions(PermissiveModel):
    email: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsEmail | None = Field(None, description="The subscription parameters to subscribe to on the \"EMAIL\" Channel.")
    sms: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsSms | None = Field(None, description="The subscription parameters to subscribe to on the \"SMS\" Channel.")
    whatsapp: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsWhatsapp | None = Field(None, description="The subscription parameters to subscribe to on the \"WhatsApp\" Channel.")
    push: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsPush | None = Field(None, description="The subscription parameters to subscribe to on the \"Push\" Channel.")

class CreateClientSubscriptionBodyDataAttributesProfileDataAttributes(PermissiveModel):
    email: str | None = Field(None, description="Individual's email address")
    phone_number: str | None = Field(None, description="Individual's phone number in E.164 format")
    external_id: str | None = Field(None, description="A unique identifier used by customers to associate Klaviyo profiles with profiles in an external system, such as a point-of-sale system. Format varies based on the external system.")
    kx: str | None = Field(None, validation_alias="_kx", serialization_alias="_kx", description="Also known as the `exchange_id`, this is an encrypted identifier used for identifying a\nprofile by Klaviyo's web tracking.\n\nYou can use this field as a filter when retrieving profiles via the Get Profiles endpoint.")
    first_name: str | None = Field(None, description="Individual's first name")
    last_name: str | None = Field(None, description="Individual's last name")
    organization: str | None = Field(None, description="Name of the company or organization within the company for whom the individual works")
    locale: str | None = Field(None, description="The locale of the profile, in the IETF BCP 47 language tag format like (ISO 639-1/2)-(ISO 3166 alpha-2)")
    title: str | None = Field(None, description="Individual's job title")
    image: str | None = Field(None, description="URL pointing to the location of a profile image")
    location: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesLocation | None = None
    properties: dict[str, Any] | None = Field(None, description="An object containing key/value pairs for any custom properties assigned to this profile")
    meta: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesMeta | None = None
    subscriptions: CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptions | None = None

class CreateClientSubscriptionBodyDataAttributesProfileData(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Primary key that uniquely identifies this profile. Generated by Klaviyo.")
    attributes: CreateClientSubscriptionBodyDataAttributesProfileDataAttributes

class CreateClientSubscriptionBodyDataAttributesProfile(PermissiveModel):
    """Profile to subscribe: email, phone, name, location, subscription consents, and custom properties."""
    data: CreateClientSubscriptionBodyDataAttributesProfileData

class QuoteStyle(PermissiveModel):
    font_family: str | None = "Arial, 'Helvetica Neue', Helvetica, sans-serif"
    font_size: int | None = 16
    text_color: str | None = '#000000'
    character_spacing: int | None = 0
    font_weight: int | None = 400
    alignment: Literal["center", "left", "right"] | None = Field('center', description="Horizontal alignment enumeration.")
    line_height: float | None = 1.5

class RadioButtonsProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    property_name: str
    label: str | None = None
    show_label: bool | None = False
    required: bool | None = False
    error_messages: ErrorMessages | None = None
    options: list[PropertyOption]
    placeholder: str | None = None

class RadioButtonsStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None
    arrangement: Literal["horizontal", "vertical"] | None = Field('vertical', description="Arrangement enumeration.")
    alignment: Literal["center", "left", "right"] | None = Field('left', description="Horizontal alignment enumeration.")

class RadioButtons(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["radio_buttons"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: RadioButtonsStyles | None = None
    properties: RadioButtonsProperties

class RatingStyle(PermissiveModel):
    color: str | None = '#F8BE00'
    empty_color: str | None = '#EBEEEF'
    font_size: int | None = 16
    shape: Literal["circle", "heart", "star"] | None = Field('star', description="Enumeration for review shapes.")
    alignment: Literal["center", "left", "right"] | None = Field('center', description="Horizontal alignment enumeration.")
    character_spacing: float | None = 0

class RedirectProperties(PermissiveModel):
    list_id: str | None = None
    url: str
    new_window: bool | None = False

class Redirect(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    submit: bool
    type_: Literal["redirect"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: RedirectProperties

class RejectReasonFake(PermissiveModel):
    reason: Literal["fake"] = Field(..., description="rejected due to fake content")

class RejectReasonMisleading(PermissiveModel):
    reason: Literal["false_or_misleading"] = Field(..., description="rejected due to false or misleading content")

class RejectReasonOther(PermissiveModel):
    reason: Literal["other"] = Field(..., description="reject reason is other")
    status_explanation: str | None = Field(None, description="If review reject reason is other, we can provide further explanation")

class RejectReasonPrivateInformation(PermissiveModel):
    reason: Literal["private_information"] = Field(..., description="rejected due to private information")

class RejectReasonProfanity(PermissiveModel):
    reason: Literal["profanity_or_inappropriate"] = Field(..., description="rejected due to profanity or inappropriate content")

class RejectReasonUnrelated(PermissiveModel):
    reason: Literal["unrelated"] = Field(..., description="rejected due to unrelated content")

class RelativeAnniversaryDateFilter(PermissiveModel):
    type_: Literal["date"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["anniversary-last", "anniversary-next"] = Field(..., description="Operators for relative date filters.\n\ne.g. \"anniversary in the last 10 days\"")
    unit: Literal["day", "hour", "week"] = Field(..., description="Units for relative date filters.")
    quantity: int

class RelativeDateOperatorBaseRelativeDateFilter(PermissiveModel):
    type_: Literal["date"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["at-least", "in-the-last", "in-the-next"] = Field(..., description="Operators for relative date filters.\n\ne.g. \"in the last 10 days\"")
    unit: Literal["day", "hour", "week"] = Field(..., description="Units for relative date filters.")
    quantity: int

class RelativeDateRangeFilter(PermissiveModel):
    type_: Literal["date"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["between"] = Field(..., description="Operators for relative date range filters.\n\ne.g. \"between 10 and 20 days ago\"")
    start: int
    end: int
    unit: Literal["day", "hour", "week"] = Field(..., description="Units for relative date filters.")

class RemoveCategoriesFromCatalogItemBodyDataItem(PermissiveModel):
    type_: Literal["catalog-category"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog category IDs representing the categories the item is in")

class RemoveItemsFromCatalogCategoryBodyDataItem(PermissiveModel):
    type_: Literal["catalog-item"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog item IDs that are in the given category.")

class RemoveProfilesFromListBodyDataItem(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class RemoveTagFromCampaignsBodyDataItem(PermissiveModel):
    type_: Literal["campaign"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The IDs of the campaigns to link or unlink with the given Tag ID")

class RemoveTagFromFlowsBodyDataItem(PermissiveModel):
    type_: Literal["flow"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The IDs of the flows to link or unlink with the given Tag ID")

class RemoveTagFromListsBodyDataItem(PermissiveModel):
    type_: Literal["list"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The IDs of the lists to link or unlink with the given Tag ID")

class RemoveTagFromSegmentsBodyDataItem(PermissiveModel):
    type_: Literal["segment"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The IDs of the segments to link or unlink with the given Tag ID")

class RenderOptions(PermissiveModel):
    shorten_links: bool | None = True
    add_org_prefix: bool | None = True
    add_info_link: bool | None = True
    add_opt_out_language: bool | None = False

class ResendOptInCode(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    submit: Literal[False] | None = False
    type_: Literal["resend_opt_in_code"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: None = None

class ReviewProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    author: str | None = None
    content: str | None = None
    rating: int | None = 5
    verified: bool | None = False
    review_id: int | None = None
    show_rating: bool | None = True
    show_author: bool | None = True
    show_verified: bool | None = True

class ReviewStatusFeatured(PermissiveModel):
    value: Literal["featured"] = Field(..., description="Featured review status")

class ReviewStatusPending(PermissiveModel):
    value: Literal["pending"] = Field(..., description="Pending review status")

class ReviewStatusPublished(PermissiveModel):
    value: Literal["published"] = Field(..., description="Published review status")

class ReviewStatusRejected(PermissiveModel):
    value: Literal["rejected"] = Field(..., description="Rejected review status")
    rejection_reason: RejectReasonOther | RejectReasonFake | RejectReasonMisleading | RejectReasonPrivateInformation | RejectReasonProfanity | RejectReasonUnrelated = Field(..., description="The updated status intended for the review with this ID")

class ReviewStatusUnpublished(PermissiveModel):
    value: Literal["unpublished"] = Field(..., description="Unpublished review status")

class ReviewerNameStyle(PermissiveModel):
    layout: Literal["inline", "stacked"] | None = Field('stacked', description="Enumeration for review name layouts.")
    font_family: str | None = "Arial, 'Helvetica Neue', Helvetica, sans-serif"
    font_size: int | None = 16
    text_color: str | None = '#000000'
    character_spacing: int | None = 0
    font_weight: int | None = 400
    alignment: Literal["center", "left", "right"] | None = Field('center', description="Horizontal alignment enumeration.")
    line_height: float | None = 1.5

class ReviewStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None
    rating_style: RatingStyle | None = None
    quote_style: QuoteStyle | None = None
    reviewer_name_style: ReviewerNameStyle | None = None
    block_background_color: str | None = 'rgba(255, 255, 255, 0)'

class Review(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["review"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: ReviewStyles | None = None
    properties: ReviewProperties

class RichTextMargin(PermissiveModel):
    left: Literal[0] | None = 0
    right: Literal[0] | None = 0
    top: Literal[0] | None = 0
    bottom: int | None = 0

class RichTextStyle(PermissiveModel):
    font_family: str | None = "Arial, 'Helvetica Neue', Helvetica, sans-serif"
    font_size: int | None = 16
    font_weight: Literal[100, 200, 300, 400, 500, 600, 700, 800, 900] | None = Field(400, description="Font weight enumeration.")
    text_color: str | None = '#000000'
    font_style: str | None = None
    text_decoration: str | None = None
    line_spacing: float | None = 1
    character_spacing: int | None = 0
    alignment: Literal["center", "left", "right"] | None = Field('left', description="Horizontal alignment enumeration.")
    margin: RichTextMargin | None = None

class RichTextStyles(PermissiveModel):
    body: RichTextStyle | None = None
    link: LinkStyles | None = None
    h1: RichTextStyle | None = None
    h2: RichTextStyle | None = None
    h3: RichTextStyle | None = None
    h4: RichTextStyle | None = None
    h5: RichTextStyle | None = None
    h6: RichTextStyle | None = None

class ScrollProperties(PermissiveModel):
    percentage: int | None = 30

class Scroll(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["scroll_percentage"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: ScrollProperties | None = None

class SftpMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["sftp"]

class ShopifyIntegrationFilter(PermissiveModel):
    type_: Literal["string"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["in"]
    value: list[Literal["shopify"]]

class ShopifyIntegrationMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["integration"]
    filter_: ShopifyIntegrationFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class SideImageSettings(PermissiveModel):
    size: Literal["large", "medium", "small"] | None = Field('medium', description="Side image size enumeration.")
    alignment: Literal["left", "right"] | None = Field('left', description="Side image alignment enumeration.")
    device_type: list[Literal["both", "desktop", "mobile"]] | None = None

class SignupCounterProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    timeframe: Literal["1_hour", "24_hours", "30_days", "7_days"] = Field(..., description="Timeframes for the signup counter lookback.")
    min_submits: int
    content: str

class SignupCounterStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None

class SignupCounter(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["signup_counter"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: SignupCounterStyles | None = None
    properties: SignupCounterProperties

class SkipToSuccessProperties(RootModel[dict[str, Any]]):
    pass

class SkipToSuccess(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["skip_to_success"] = Field(..., validation_alias="type", serialization_alias="type")
    submit: Literal[False] | None = False
    properties: SkipToSuccessProperties

class SmartSendTimeStrategy(PermissiveModel):
    method: Literal["smart_send_time"]
    date: str = Field(..., description="The day to send on", json_schema_extra={'format': 'date'})

class SmsConsentCheckboxProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    label: str | None = None
    show_label: bool | None = False
    error_messages: ErrorMessages | None = None
    required: Literal[False] | None = False
    property_name: Literal["opt_in_promotional_sms"] | None = 'opt_in_promotional_sms'
    checkbox_text: str
    placeholder: None = None
    channels: list[Literal["sms", "whatsapp"]] | None = None

class SmsConsentCheckboxStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None
    horizontal_alignment: Literal["center", "left", "right"] | None = Field('left', description="Horizontal alignment enumeration.")

class SmsConsentCheckbox(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["promotional_sms_checkbox"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: SmsConsentCheckboxStyles | None = None
    properties: SmsConsentCheckboxProperties

class SmsContentCreate(PermissiveModel):
    body: str | None = Field(None, description="The message body")

class SmsDisclosureAccountDefault(PermissiveModel):
    type_: Literal["account_default"] = Field(..., validation_alias="type", serialization_alias="type")
    html: Any | None = None

class SmsDisclosureCustom(PermissiveModel):
    type_: Literal["custom"] = Field(..., validation_alias="type", serialization_alias="type")
    compliance_company_name: str | None = '[company name]'
    privacy_policy_url: str | None = '[link]'
    terms_of_service_url: str | None = '[link]'
    html: str | None = ''

class SmsDisclosureProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    content: SmsDisclosureCustom | SmsDisclosureAccountDefault | None = None

class SmsDisclosureTextStyle(PermissiveModel):
    font_family: str | None = "Arial, 'Helvetica Neue', Helvetica, sans-serif"
    font_size: int | None = 16
    font_weight: Literal[100, 200, 300, 400, 500, 600, 700, 800, 900] | None = Field(400, description="Font weight enumeration.")
    text_color: str | None = '#000000'
    character_spacing: int | None = 0
    font_style: str | None = None
    text_decoration: str | None = None

class SmsDisclosureStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None
    link_styles: SmsDisclosureTextStyle | None = None
    text_styles: SmsDisclosureTextStyle | None = None

class SmsDisclosure(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["sms_disclosure"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: SmsDisclosureStyles | None = None
    properties: SmsDisclosureProperties | None = None

class SmsMessageDefinitionCreate(PermissiveModel):
    channel: Literal["sms"]
    content: SmsContentCreate | None = Field(None, description="Additional attributes relating to the content of the message")
    render_options: RenderOptions | None = Field(None, description="Additional options for rendering the message")

class SmsSendOptions(PermissiveModel):
    use_smart_sending: bool | None = Field(True, description="Use smart sending.")

class SpacerBlock(PermissiveModel):
    content_type: Literal["block"]
    type_: Literal["spacer"] = Field(..., validation_alias="type", serialization_alias="type")
    data: Any | None = Field(...)

class SpamComplaintMethodFilter(PermissiveModel):
    field: Literal["method"]
    method: Literal["spam_complaint"]

class SpinToWinSliceConfig(PermissiveModel):
    label: str
    probability: int
    step_id: str

class SpinToWinProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    duplicate_slices: bool | None = False
    slices: list[SpinToWinSliceConfig]

class SpinToWinSliceStyle(PermissiveModel):
    background_color: str | None = 'rgba(0,0,0,1)'
    text_color: str | None = 'rgba(255,255,255,1)'

class StaticCouponConfig(PermissiveModel):
    type_: Literal["static"] = Field(..., validation_alias="type", serialization_alias="type")
    text: str | None = None

class StaticDateFilter(PermissiveModel):
    type_: Literal["date"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["after", "before"] = Field(..., description="Operators for static date filters.\n\nE.g. \"before 2023-01-01\"")
    date: str = Field(..., json_schema_extra={'format': 'date-time'})

class StaticDateRangeFilter(PermissiveModel):
    type_: Literal["date"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["between-static"] = Field(..., description="Operators for static date range filters.\n\nE.g. \"between 2023-01-01 and 2023-02-01\"")
    start: str = Field(..., json_schema_extra={'format': 'date-time'})
    end: str = Field(..., json_schema_extra={'format': 'date-time'})

class BounceDateFilter(PermissiveModel):
    field: Literal["bounce_date"]
    filter_: StaticDateFilter | StaticDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter | RelativeAnniversaryDateFilter | RelativeDateRangeFilter | CalendarDateFilter | AnniversaryDateFilter | IsSetExistenceFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class EffectiveDateFilter(PermissiveModel):
    field: Literal["effective_date"]
    filter_: StaticDateFilter | StaticDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter | RelativeAnniversaryDateFilter | RelativeDateRangeFilter | CalendarDateFilter | AnniversaryDateFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class InvalidEmailDateFilter(PermissiveModel):
    field: Literal["invalid_email_date"]
    filter_: StaticDateFilter | StaticDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter | RelativeAnniversaryDateFilter | RelativeDateRangeFilter | CalendarDateFilter | AnniversaryDateFilter | IsSetExistenceFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class ManualSuppressionDateFilter(PermissiveModel):
    field: Literal["manual_suppression_date"]
    filter_: StaticDateFilter | StaticDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter | RelativeAnniversaryDateFilter | RelativeDateRangeFilter | CalendarDateFilter | AnniversaryDateFilter | IsSetExistenceFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class NoEmailMarketing(PermissiveModel):
    subscription: Literal["any"]
    filters: list[BounceDateFilter | ManualSuppressionDateFilter | InvalidEmailDateFilter] | None = None

class NoEmailMarketingNeverSubscribed(PermissiveModel):
    subscription: Literal["never_subscribed"]
    filters: list[BounceDateFilter | ManualSuppressionDateFilter | InvalidEmailDateFilter]

class NoEmailMarketingSubscribed(PermissiveModel):
    subscription: Literal["subscribed"]
    filters: list[BounceDateFilter | ManualSuppressionDateFilter | InvalidEmailDateFilter]

class ProfileHasGroupMembershipCondition(PermissiveModel):
    type_: Literal["profile-group-membership"] = Field(..., validation_alias="type", serialization_alias="type")
    is_member: Literal[True]
    group_ids: list[str]
    timeframe_filter: StaticDateFilter | StaticDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter | RelativeDateRangeFilter | None = None

class ProfilePredictiveAnalyticsDateCondition(PermissiveModel):
    dimension: Literal["expected_date_of_next_purchase"] = Field(..., description="Dimension for date profile predictive analytics conditions.")
    filter_: StaticDateFilter | StaticDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter | RelativeAnniversaryDateFilter | RelativeDateRangeFilter | CalendarDateFilter | AnniversaryDateFilter = Field(..., validation_alias="filter", serialization_alias="filter")
    type_: Literal["profile-predictive-analytics"] = Field(..., validation_alias="type", serialization_alias="type")

class RecordedDateFilter(PermissiveModel):
    field: Literal["recorded_date"]
    filter_: StaticDateFilter | StaticDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter | RelativeAnniversaryDateFilter | RelativeDateRangeFilter | CalendarDateFilter | AnniversaryDateFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class ExplicitlyReachable(PermissiveModel):
    reachable_status: Literal["explicitly_reachable"]
    filters: list[EffectiveDateFilter | RecordedDateFilter | MethodFilter | FormSubscribeFilter]

class ExplicitlyUnreachable(PermissiveModel):
    reachable_status: Literal["explicitly_unreachable"]
    filters: list[EffectiveDateFilter | RecordedDateFilter | MethodFilter | FormSubscribeFilter]

class ProfilePermissionsCondition(PermissiveModel):
    type_: Literal["profile-permissions"] = Field(..., validation_alias="type", serialization_alias="type")
    permission: ExplicitlyReachable | ImplicitlyReachable | ImplicitlyOrExplicitlyReachable | ExplicitlyUnreachable | ImplicitlyUnreachable | ImplicitlyOrExplicitlyUnreachable
    channel: Literal["whatsapp_marketing", "whatsapp_transactional"] = Field(..., description="Possible channels for profile permissions criterion.")

class StaticSendStrategy(PermissiveModel):
    method: Literal["static"]
    datetime_: str = Field(..., validation_alias="datetime", serialization_alias="datetime", description="The time to send at", json_schema_extra={'format': 'date-time'})
    options: LocalStaticSend | NonLocalStaticSend | None = Field(None, description="If the campaign should be sent with local recipient timezone send (requires UTC time) or statically sent at the given time.")

class StaticTrackingParam(PermissiveModel):
    type_: Literal["static"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the tracking parameter")
    value: str = Field(..., description="The value of the tracking parameter")
    name: str = Field(..., description="Name of the tracking param")

class CampaignsEmailTrackingOptions(PermissiveModel):
    add_tracking_params: bool | None = Field(None, description="Whether the campaign needs custom tracking parameters. If set to False, tracking params will not be used.")
    custom_tracking_params: list[DynamicTrackingParam | StaticTrackingParam] | None = Field(None, description="A list of custom tracking parameters. If an empty list is given and add_tracking_params is True, uses company defaults.")
    is_tracking_clicks: bool | None = Field(None, description="Whether the campaign is tracking click events. If not specified, uses company defaults.")
    is_tracking_opens: bool | None = Field(None, description="Whether the campaign is tracking open events. If not specified, uses company defaults.")

class CampaignsSmsTrackingOptions(PermissiveModel):
    add_tracking_params: bool | None = Field(None, description="Whether the campaign needs custom tracking parameters. If set to False, tracking params will not be used.")
    custom_tracking_params: list[DynamicTrackingParam | StaticTrackingParam] | None = Field(None, description="A list of custom tracking parameters. If an empty list is given and add_tracking_params is True, uses company defaults.")

class StatusDateFilter(PermissiveModel):
    field: Literal["status_date"]
    filter_: StaticDateFilter | StaticDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter | RelativeAnniversaryDateFilter | RelativeDateRangeFilter | CalendarDateFilter | AnniversaryDateFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class HasEmailMarketingSubscribed(PermissiveModel):
    subscription: Literal["subscribed"]
    filters: list[DoubleOptinFilter | StatusDateFilter | CustomSourceFilter | FormMethodFilter | PreferencePageFilter | ApiMethodFilter | InboundMessageMethodFilter | BackInStockMethodFilter | SftpMethodFilter | ManualImportManualMethodFilter | ManualAddManualMethodFilter | ShopifyIntegrationMethodFilter] | None = None

class HasEmailMarketingConsent(PermissiveModel):
    channel: Literal["email"]
    can_receive_marketing: Literal[True]
    consent_status: HasEmailMarketing | HasEmailMarketingSubscribed | HasEmailMarketingNeverSubscribed

class HasPushMarketing(PermissiveModel):
    subscription: Literal["any"]
    filters: list[StatusDateFilter] | None = None

class HasPushMarketingConsent(PermissiveModel):
    channel: Literal["push"]
    can_receive_marketing: Literal[True]
    consent_status: HasPushMarketing

class NoEmailMarketingUnsubscribed(PermissiveModel):
    subscription: Literal["unsubscribed"]
    filters: list[StatusDateFilter | ApiMethodFilter | InboundMessageMethodFilter | PreferencePageMethodFilter | ManualRemoveMethodFilter | SpamComplaintMethodFilter | MailboxProviderMethodFilter | OneClickUnsubscribeMethodFilter | ManualImportMethodFilter | SftpMethodFilter | DataWarehouseImportMethodFilter | ProfileModificationMethodFilter | ConstantContactIntegrationMethodFilter] | list[BounceDateFilter | ManualSuppressionDateFilter | InvalidEmailDateFilter] | None = None

class NoEmailMarketingConsent(PermissiveModel):
    channel: Literal["email"]
    can_receive_marketing: Literal[False]
    consent_status: NoEmailMarketing | NoEmailMarketingUnsubscribed | NoEmailMarketingNeverSubscribed | NoEmailMarketingSubscribed

class NoSmsMarketingUnsubscribed(PermissiveModel):
    subscription: Literal["unsubscribed"]
    filters: list[StatusDateFilter | FormMethodFilter | ManualImportManualMethodFilter | ManualAddManualMethodFilter | ManualRemoveMethodFilter | BulkRemoveMethodFilter | CheckoutMethodFilter | InboundMessageMethodFilter | PreferencePageMethodFilter | SftpMethodFilter | CarrierDeactivationMethodFilter | ProvidedLandlineMethodFilter | MessageBlockedMethodFilter | ProvidedNoAgeMethodFilter | FailedAgeGateMethodFilter | ShopifyIntegrationMethodFilter] | None = None

class NoSmsMarketingConsent(PermissiveModel):
    channel: Literal["sms"]
    can_receive_marketing: Literal[False]
    consent_status: NoSmsMarketing | NoSmsMarketingUnsubscribed | NoSmsMarketingNeverSubscribed

class StringArrayOperatorStringArrayFilter(PermissiveModel):
    type_: Literal["string"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["in", "not-in"] = Field(..., description="Operators for string-in-array filters.")
    value: list[str]

class StringInArrayFilter(PermissiveModel):
    operator: Literal["in"]
    value: list[str]
    type_: Literal["string"] = Field(..., validation_alias="type", serialization_alias="type")

class StringOperatorStringFilter(PermissiveModel):
    type_: Literal["string"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["contains", "ends-with", "equals", "not-contains", "not-ends-with", "not-equals", "not-starts-with", "nregex", "regex", "starts-with"] = Field(..., description="Operators for string filters.")
    value: str | None = Field(...)

class CustomMetricCondition(PermissiveModel):
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    filter_: NumericOperatorNumericFilter | StringInArrayFilter | ExistenceOperatorExistenceFilter | BooleanFilter | StringOperatorStringFilter | ListContainsOperatorListContainsFilter | ListRegexOperatorListContainsFilter | ListSubstringFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class CustomMetricGroup(PermissiveModel):
    metric_id: str = Field(..., description="The ID of the metric that composes the custom metric.")
    metric_filters: list[CustomMetricCondition] | None = Field(None, description="An optional array of objects for filtering on properties of the metric.")
    value_property: str | None = Field(None, description="\nIf the custom metric has a `value` aggregation method, the `value_property` of each `metric_group` of the `definition` should specify the property to calculate the conversion value. If null, the default `$value` property will be used.\n")

class ProfileHasCustomObjectFilter(PermissiveModel):
    property_id: int
    filter_: StringOperatorStringFilter | StringArrayOperatorStringArrayFilter | NumericOperatorNumericFilter | NumericRangeFilter | BooleanFilter | StaticDateFilter | StaticDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter | RelativeAnniversaryDateFilter | RelativeDateRangeFilter | ExistenceOperatorExistenceFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class ProfileHasCustomObjectCondition(PermissiveModel):
    type_: Literal["profile-has-custom-object"] = Field(..., validation_alias="type", serialization_alias="type")
    object_type_id: str
    object_type_relationship_id: str
    filter_: IntegerFilter = Field(..., validation_alias="filter", serialization_alias="filter")
    filters: list[ProfileHasCustomObjectFilter]

class ProfileMetricPropertyFilter(PermissiveModel):
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    filter_: StringOperatorStringFilter | StringArrayOperatorStringArrayFilter | ExistenceOperatorExistenceFilter | ListSetFilter | ListLengthFilter | ListSubstringFilter | BooleanFilter | NumericOperatorNumericFilter | None = Field(None, validation_alias="filter", serialization_alias="filter")

class ProfileMetricFunnelSteps(PermissiveModel):
    metric_exists: bool
    metric_id: str
    metric_filters: list[ProfileMetricPropertyFilter] | None = None

class SegmentsProfileMetricCondition(PermissiveModel):
    type_: Literal["profile-metric"] = Field(..., validation_alias="type", serialization_alias="type")
    metric_id: str
    measurement: Literal["count", "sum"] = Field(..., description="Measurements for profile metrics.")
    measurement_filter: NumericOperatorNumericFilter
    timeframe_filter: StaticDateFilter | StaticDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter | RelativeAnniversaryDateFilter | RelativeDateRangeFilter | AlltimeDateFilter
    metric_filters: list[ProfileMetricPropertyFilter] | None = None

class SegmentsProfileMetricFunnelCondition(PermissiveModel):
    type_: Literal["profile-metric-funnel"] = Field(..., validation_alias="type", serialization_alias="type")
    timeframe_filter: StaticDateRangeFilter | RelativeDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter
    completion_window_seconds: Literal["DAYS_1", "DAYS_180", "DAYS_3", "DAYS_30", "DAYS_5", "DAYS_90", "HOURS_1", "WEEKS_1", "YEARS_1"] | None = Field(None, description="Allowed completion window durations for funnel conditions (in\n    seconds).")
    steps: list[ProfileMetricFunnelSteps]

class StringPhoneOperatorStringArrayFilter(PermissiveModel):
    type_: Literal["string"] = Field(..., validation_alias="type", serialization_alias="type")
    operator: Literal["phone-country-code-in", "phone-country-code-not-in"] = Field(..., description="Operators for phone string array filters.\n\nExample condition using this filter:\n        {")
    value: list[str]

class ProfilePropertyCondition(PermissiveModel):
    type_: Literal["profile-property"] = Field(..., validation_alias="type", serialization_alias="type")
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    filter_: StringOperatorStringFilter | StringArrayOperatorStringArrayFilter | StringPhoneOperatorStringArrayFilter | NumericOperatorNumericFilter | BooleanFilter | StaticDateFilter | StaticDateRangeFilter | RelativeDateOperatorBaseRelativeDateFilter | RelativeAnniversaryDateFilter | RelativeDateRangeFilter | CalendarDateFilter | AnniversaryDateFilter | ListContainsOperatorListContainsFilter | ListLengthFilter | ExistenceOperatorExistenceFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class SubmitBackInStockProperties(PermissiveModel):
    list_id: str | None = None

class SubmitBackInStock(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["submit_back_in_stock"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: SubmitBackInStockProperties | None = None
    submit: Literal[True] | None = True

class SubmitOptInCode(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    submit: Literal[True] | None = True
    type_: Literal["submit_opt_in_code"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: None = None

class SubscribeViaSmsProperties(PermissiveModel):
    opt_in_keyword: str | None = Field(...)
    opt_in_message: str
    sending_number: str | None = Field(...)

class SubscribeViaSms(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    submit: Literal[True] | None = True
    type_: Literal["subscribe_via_sms"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: SubscribeViaSmsProperties

class SubscribeViaWhatsAppProperties(PermissiveModel):
    opt_in_keyword: str | None = Field(...)
    opt_in_message: str
    sending_number: str | None = Field(...)

class SubscribeViaWhatsApp(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    submit: Literal[True] | None = True
    type_: Literal["subscribe_via_whatsapp"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: SubscribeViaWhatsAppProperties

class Image(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["image"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: ImageStyles | None = None
    properties: ImageProperties
    action: Close | NextStep | OpenForm | PromotionalSmsSubscription | Redirect | ResendOptInCode | SubmitOptInCode | SubscribeViaSms | SubscribeViaWhatsApp | GoToInbox | SubmitBackInStock | SkipToSuccess | None = None

class SubscribedSmsIsRcsCapableFilter(PermissiveModel):
    field: Literal["is_rcs_capable"]
    filter_: BooleanFilter = Field(..., validation_alias="filter", serialization_alias="filter")

class HasSmsMarketingSubscribed(PermissiveModel):
    subscription: Literal["subscribed"]
    filters: list[StatusDateFilter | FormMethodFilter | ManualImportManualMethodFilter | ManualAddManualMethodFilter | CheckoutMethodFilter | InboundMessageMethodFilter | PreferencePageMethodFilter | SftpMethodFilter | ShopifyIntegrationMethodFilter | SubscribedSmsIsRcsCapableFilter] | None = None

class HasSmsMarketingConsent(PermissiveModel):
    channel: Literal["sms"]
    can_receive_marketing: Literal[True]
    consent_status: HasSmsMarketingSubscribed

class ProfileMarketingConsentCondition(PermissiveModel):
    type_: Literal["profile-marketing-consent"] = Field(..., validation_alias="type", serialization_alias="type")
    consent: HasEmailMarketingConsent | NoEmailMarketingConsent | HasSmsMarketingConsent | NoSmsMarketingConsent | HasPushMarketingConsent | NoPushMarketingConsent

class ConditionGroup(PermissiveModel):
    conditions: list[ProfileHasGroupMembershipCondition | ProfileNoGroupMembershipCondition | SegmentsProfileMetricCondition | ProfileMarketingConsentCondition | ProfilePostalCodeDistanceCondition | ProfilePropertyCondition | ProfileRegionCondition | ProfilePredictiveAnalyticsDateCondition | ProfilePredictiveAnalyticsNumericCondition | ProfilePredictiveAnalyticsStringCondition | ProfilePredictiveAnalyticsChannelAffinityPriorityCondition | ProfilePredictiveAnalyticsChannelAffinityRankCondition | ProfileHasCustomObjectCondition | ProfilePermissionsCondition | SegmentsProfileMetricFunnelCondition]

class SubscriptionParameters(PermissiveModel):
    consent: Literal["SUBSCRIBED"] = Field(..., description="The Consent status to be set as part of the subscribe call. Currently supports \"SUBSCRIBED\".")
    consented_at: str | None = Field(None, description="The timestamp of when the profile's consent was gathered. This should only be used when syncing over historical consent info to Klaviyo; if the `historical_import` flag is not included, providing any value for this field will raise an error.", json_schema_extra={'format': 'date-time'})

class EmailSubscriptionParameters(PermissiveModel):
    marketing: SubscriptionParameters = Field(..., description="The parameters to subscribe to on the \"EMAIL\" Channel. Currently supports \"MARKETING\".")

class PushSubscriptionParameters(PermissiveModel):
    marketing: SubscriptionParameters = Field(..., description="The parameters to subscribe to marketing on the \"Push\" channel.")
    tokens: list[PushTokenEntry] | None = Field(None, description="A list of push tokens to register for this profile.")
    anonymous_id: str | None = Field(None, description="An anonymous identifier for push-only profiles with no email/phone.")

class SmsSubscriptionParameters(PermissiveModel):
    marketing: SubscriptionParameters | None = Field(None, description="The parameters to subscribe to marketing on the \"SMS\" Channel.")
    transactional: SubscriptionParameters | None = Field(None, description="The parameters to subscribe to transactional messaging on the \"SMS\" Channel.")

class TagCampaignsBodyDataItem(PermissiveModel):
    type_: Literal["campaign"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The IDs of the campaigns to link or unlink with the given Tag ID")

class TagFlowsBodyDataItem(PermissiveModel):
    type_: Literal["flow"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The IDs of the flows to link or unlink with the given Tag ID")

class TagListsBodyDataItem(PermissiveModel):
    type_: Literal["list"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The IDs of the lists to link or unlink with the given Tag ID")

class TagSegmentsBodyDataItem(PermissiveModel):
    type_: Literal["segment"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The IDs of the segments to link or unlink with the given Tag ID")

class TeaserStyles(PermissiveModel):
    background_color: str | None = '#FFFFFF'
    drop_shadow: DropShadow | None = None
    corner_radius: int | None = 4
    background_image: BackgroundImage | None = None
    close_button: CloseButtonStyle | None = None
    margin: Margin | None = None

class Teaser(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    content: str
    display_order: Literal["after", "before", "before_and_after"] | None = Field('after', description="Teaser display order enumeration.")
    teaser_type: Literal["circle", "corner", "rectangle"] | None = Field('rectangle', description="Teaser display order enumeration.")
    location: Literal["bottom_center", "bottom_left", "bottom_right", "center_left", "center_right", "top_center", "top_left", "top_right"] | None = Field('bottom_left', description="Display location enumeration.")
    size: Literal["custom", "large", "medium", "small"] | None = Field('small', description="Teaser size enumeration.")
    custom_size: int | None = None
    styles: TeaserStyles | None = None
    close_button: bool | None = True
    device_type: Literal["both", "desktop", "mobile"] | None = Field('both', description="Enumeration for mobile and desktop.")

class TextBlockStyles(PermissiveModel):
    background_color: str | None = None
    block_background_color: str | None = None
    block_border_color: str | None = None
    block_border_style: Literal["dashed", "dotted", "groove", "inset", "none", "outset", "ridge", "solid"] | None = Field(None, description="Border style.")
    block_border_width: int | None = None
    block_padding_bottom: int | None = None
    block_padding_left: int | None = None
    block_padding_right: int | None = None
    block_padding_top: int | None = None
    color: str | None = None
    extra_css_class: str | None = None
    font_family: str | None = None
    font_size: int | None = None
    font_style: Literal["italic", "normal"] | None = Field(None, description="Font style.")
    font_weight: str | None = None
    inner_padding_bottom: int | None = None
    inner_padding_left: int | None = None
    inner_padding_right: int | None = None
    inner_padding_top: int | None = None
    letter_spacing: int | None = None
    line_height: float | None = None
    mobile_stretch_content: bool | None = None
    text_align: Literal["center", "left", "right"] | None = Field(None, description="Text Alignment.")
    text_decoration: str | None = None
    text_table_layout: Literal["auto", "fixed", "inherit", "initial"] | None = Field(None, description="Text table layout.")

class TextBlockData(PermissiveModel):
    content: str
    display_options: BlockDisplayOptions
    styles: TextBlockStyles

class TextBlock(PermissiveModel):
    content_type: Literal["block"]
    type_: Literal["text"] = Field(..., validation_alias="type", serialization_alias="type")
    data: TextBlockData

class TextProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    property_name: str
    label: str | None = None
    show_label: bool | None = False
    placeholder: str | None = None
    required: bool | None = False
    error_messages: ErrorMessages | None = None

class TextStyle(PermissiveModel):
    font_family: str | None = "Arial, 'Helvetica Neue', Helvetica, sans-serif"
    font_size: int | None = 16
    font_weight: Literal[100, 200, 300, 400, 500, 600, 700, 800, 900] | None = Field(400, description="Font weight enumeration.")
    text_color: str | None = '#000000'
    character_spacing: int | None = 0
    font_style: str | None = None
    text_decoration: str | None = None

class ButtonStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None
    width: Literal["fill", "fit"] | None = Field('fill', description="Valid button block widths.")
    height: int | None = 50
    hover_background_color: str | None = None
    hover_text_color: str | None = None
    border_styles: BorderStyle | None = None
    text_styles: TextStyle | None = None
    color: str | None = None
    drop_shadow: ButtonDropShadowStyles | None = None

class Button(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["button"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: ButtonStyles | None = None
    properties: ButtonProperties
    action: Close | NextStep | OpenForm | PromotionalSmsSubscription | Redirect | ResendOptInCode | SubmitOptInCode | SubscribeViaSms | SubscribeViaWhatsApp | GoToInbox | SubmitBackInStock | SkipToSuccess | None = None

class CountdownTimerStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None
    text_styles: TextStyle | None = None
    card_color: str | None = 'rgba(100,100,100, 1.0)'
    label_font_size: int | None = 12
    label_font_weight: Literal[100, 200, 300, 400, 500, 600, 700, 800, 900] | None = Field(400, description="Font weight enumeration.")

class CouponStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None
    text_styles: TextStyle | None = None
    border_styles: BorderStyle | None = None
    coupon_background_color: str | None = '#EEEEEE'

class InputStyles(PermissiveModel):
    text_styles: TextStyle | None = None
    label_color: str | None = '#303B43'
    text_color: str | None = '#000000'
    placeholder_color: str | None = '#949596'
    background_color: str | None = '#FFFFFF'
    border_color: str | None = '#949596'
    border_focus_color: str | None = '#000000'
    focus_outline_color: str | None = '#1C65AD'
    corner_radius: int | None = 2
    field_height: int | None = 38

class SpinToWinStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None
    slice_styles: list[SpinToWinSliceStyle] | None = None
    text_styles: TextStyle | None = None
    center_color: str | None = 'rgba(255,255,255,1)'
    outline_color: str | None = 'rgba(0,0,0,1)'
    outline_thickness: int | None = 12
    pin_color: str | None = 'rgba(255,255,255,1)'
    wheel_size: int | None = 400

class SpinToWin(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    properties: SpinToWinProperties
    type_: Literal["spin_to_win"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: SpinToWinStyles | None = None

class TextStyles(PermissiveModel):
    padding: Padding | None = None
    background_color: str | None = None

class Text(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["text"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: TextStyles | None = None
    properties: TextProperties

class ThrottledSendStrategy(PermissiveModel):
    method: Literal["throttled"]
    datetime_: str = Field(..., validation_alias="datetime", serialization_alias="datetime", description="The time to send at", json_schema_extra={'format': 'date-time'})
    throttle_percentage: Literal[10, 11, 13, 14, 17, 20, 25, 33, 50] = Field(..., description="The percentage of recipients per hour to send to.")

class Timeframe(PermissiveModel):
    key: Literal["last_12_months", "last_30_days", "last_365_days", "last_3_months", "last_7_days", "last_90_days", "last_month", "last_week", "last_year", "this_month", "this_week", "this_year", "today", "yesterday"] = Field(..., description="Pre-defined key that represents a set timeframe")

class TriggerBaseProperties(RootModel[dict[str, Any]]):
    pass

class CustomJavascript(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    properties: TriggerBaseProperties | None = None
    type_: Literal["custom_javascript"] = Field(..., validation_alias="type", serialization_alias="type")

class ExitIntent(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    properties: TriggerBaseProperties | None = None
    type_: Literal["exit_intent"] = Field(..., validation_alias="type", serialization_alias="type")

class IdentifiedProfiles(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    properties: TriggerBaseProperties | None = None
    type_: Literal["identified_profiles"] = Field(..., validation_alias="type", serialization_alias="type")

class PreviouslySubmitted(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    properties: TriggerBaseProperties | None = None
    type_: Literal["previously_submitted"] = Field(..., validation_alias="type", serialization_alias="type")

class UnidentifiedProfiles(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    properties: TriggerBaseProperties | None = None
    type_: Literal["unidentified_profiles"] = Field(..., validation_alias="type", serialization_alias="type")

class UniqueCouponConfig(PermissiveModel):
    type_: Literal["unique"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id")
    code: str | None = None
    fallback_coupon_code: str | None = None
    integration: Literal["api", "magento_two", "prestashop", "shopify", "uploaded", "woocommerce"] | None = Field('shopify', description="Coupon integration types for unique coupon blocks.")

class CouponProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    coupon: UniqueCouponConfig | StaticCouponConfig
    success_message: str | None = None

class Coupon(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["coupon"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: CouponStyles | None = None
    properties: CouponProperties

class UnsubscriptionParameters(PermissiveModel):
    consent: Literal["UNSUBSCRIBED"] = Field(..., description="The Consent status to be set as part of the unsubscribe call. Currently supports \"UNSUBSCRIBED\".")

class EmailUnsubscriptionParameters(PermissiveModel):
    marketing: UnsubscriptionParameters = Field(..., description="The parameters to unsubscribe from marketing on the \"EMAIL\" channel.")

class SmsUnsubscriptionParameters(PermissiveModel):
    marketing: UnsubscriptionParameters | None = Field(None, description="The parameters to unsubscribe from marketing on the \"SMS\" channel.")
    transactional: UnsubscriptionParameters | None = Field(None, description="The parameters to unsubscribe from transactional messaging on the \"SMS\" channel.")

class UpdateCatalogCategoryBodyDataRelationshipsItemsDataItem(PermissiveModel):
    type_: Literal["catalog-item"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog item IDs that are in the given category.")

class UpdateCatalogItemBodyDataRelationshipsCategoriesDataItem(PermissiveModel):
    type_: Literal["catalog-category"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog category IDs representing the categories the item is in")

class UpdateCategoriesForCatalogItemBodyDataItem(PermissiveModel):
    type_: Literal["catalog-category"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog category IDs representing the categories the item is in")

class UpdateItemsForCatalogCategoryBodyDataItem(PermissiveModel):
    type_: Literal["catalog-item"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of catalog item IDs that are in the given category.")

class UpdateWebhookBodyDataRelationshipsWebhookTopicsDataItem(PermissiveModel):
    type_: Literal["webhook-topic"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A list of topics to subscribe to.")

class UrlPatternsProperties(PermissiveModel):
    allow_list: list[str] | None = None
    deny_list: list[str] | None = None

class UrlPatterns(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["url_patterns"] = Field(..., validation_alias="type", serialization_alias="type")
    properties: UrlPatternsProperties | None = None

class VariableTimerConfiguration(PermissiveModel):
    type_: Literal["variable"] = Field(..., validation_alias="type", serialization_alias="type")
    days: int
    hours: int
    minutes: int

class CountdownTimerProperties(PermissiveModel):
    display_device: list[Literal["both", "desktop", "mobile"]] | None = None
    clock_face: Literal["flip", "simple"] | None = Field('simple', description="Options for displaying a timer.")
    animation: Literal["flash", "heartbeat", "pulse"] | None = Field('heartbeat', description="Options for timer completion animations.")
    configuration: FixedTimerConfiguration | VariableTimerConfiguration

class CountdownTimer(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    type_: Literal["countdown_timer"] = Field(..., validation_alias="type", serialization_alias="type")
    styles: CountdownTimerStyles | None = None
    properties: CountdownTimerProperties

class Row(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    blocks: list[Button | AgeGate | Coupon | Date | Email | HtmlText | OptInCode | PhoneNumber | SmsConsentCheckbox | Text | Checkboxes | RadioButtons | Dropdown | Image | CountdownTimer | SignupCounter | SpinToWin | SmsDisclosure | BackInStockEmailConsentCheckbox | Review]

class Column(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    rows: list[Row] | None = None
    styles: ColumnStyles | None = None

class VersionProperties(PermissiveModel):
    side_image_settings: SideImageSettings | None = None
    click_outside_to_close: list[Literal["both", "desktop", "mobile"]] | None = None
    rule_based_trigger_evaluation: Literal["all", "any"] | None = Field('any', description="Side image alignment enumeration.")
    record_utm_params_on_submit: bool | None = False
    show_close_button: bool | None = True

class VersionStyles(PermissiveModel):
    wrap_content: Literal[False] | None = False
    border_styles: BorderStyle | None = None
    close_button: CloseButtonStyle | None = None
    margin: Margin | None = None
    padding: Padding | None = None
    minimum_height: int | None = 250
    width: Literal["custom", "large", "medium", "small"] | None = Field('medium', description="Version width enumeration.")
    custom_width: int | None = None
    background_image: BackgroundImage | None = None
    background_color: str | None = '#FFFFFF'
    input_styles: InputStyles | None = None
    drop_shadow: DropShadow | None = None
    overlay_color: str | None = 'rgba(20,20,20,0.6)'
    rich_text_styles: RichTextStyles | None = None
    mobile_overlay: MobileOverlay | None = None
    banner_styles: BannerStyles | None = None

class WhatsAppSubscriptionParameters(PermissiveModel):
    marketing: SubscriptionParameters | None = Field(None, description="The parameters to subscribe to marketing on the \"WhatsApp\" Channel.")
    transactional: SubscriptionParameters | None = Field(None, description="The parameters to subscribe to transactional messaging on the \"WhatsApp\" Channel.")

class SubscriptionChannels(PermissiveModel):
    email: EmailSubscriptionParameters | None = Field(None, description="The subscription parameters to subscribe to on the \"EMAIL\" Channel.")
    sms: SmsSubscriptionParameters | None = Field(None, description="The subscription parameters to subscribe to on the \"SMS\" Channel.")
    whatsapp: WhatsAppSubscriptionParameters | None = Field(None, description="The subscription parameters to subscribe to on the \"WhatsApp\" Channel.")
    push: PushSubscriptionParameters | None = Field(None, description="The subscription parameters to subscribe to on the \"Push\" Channel.")

class ProfileSubscriptionCreateQueryResourceObjectAttributes(PermissiveModel):
    email: str | None = Field(None, description="The email address relating to the email subscription included in `subscriptions`. If the email channel is omitted from `subscriptions`, this will be set on the profile.")
    phone_number: str | None = Field(None, description="The phone number relating to the SMS subscription included in `subscriptions`. If the SMS channel is omitted from `subscriptions`, this will be set on the profile. This must be in E.164 format.")
    subscriptions: SubscriptionChannels = Field(..., description="Specifies the channel and message types that the profile will be consented to.")
    age_gated_date_of_birth: str | None = Field(None, description="The profile's date of birth. This field is required to update SMS consent for accounts using age-gating: https://help.klaviyo.com/hc/en-us/articles/17252552814875", json_schema_extra={'format': 'date'})

class ProfileSubscriptionCreateQueryResourceObject(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the profile to subscribe. If provided, this will be used to perform the lookup.")
    attributes: ProfileSubscriptionCreateQueryResourceObjectAttributes

class WhatsAppUnsubscriptionParameters(PermissiveModel):
    marketing: UnsubscriptionParameters | None = Field(None, description="The parameters to unsubscribe from marketing on the \"WhatsApp\" channel.")
    transactional: UnsubscriptionParameters | None = Field(None, description="The parameters to unsubscribe from transactional messaging on the \"WhatsApp\" channel.")
    conversational: UnsubscriptionParameters | None = Field(None, description="The parameters to unsubscribe from conversational messaging on the \"WhatsApp\" channel.")

class UnsubscriptionChannels(PermissiveModel):
    email: EmailUnsubscriptionParameters | None = Field(None, description="The subscription parameters to unsubscribe from the \"EMAIL\" Channel.")
    sms: SmsUnsubscriptionParameters | None = Field(None, description="The subscription parameters to unsubscribe from the \"SMS\" Channel.")
    whatsapp: WhatsAppUnsubscriptionParameters | None = Field(None, description="The subscription parameters to unsubscribe from the \"WhatsApp\" Channel.")

class ProfileSubscriptionDeleteQueryResourceObjectAttributes(PermissiveModel):
    email: str | None = Field(None, description="The email address to unsubscribe.")
    phone_number: str | None = Field(None, description="The phone number to unsubscribe. This must be in E.164 format.")
    subscriptions: UnsubscriptionChannels = Field(..., description="Specifies the channel and message types that the profile will have consent revoked from.")

class ProfileSubscriptionDeleteQueryResourceObject(PermissiveModel):
    type_: Literal["profile"] = Field(..., validation_alias="type", serialization_alias="type")
    attributes: ProfileSubscriptionDeleteQueryResourceObjectAttributes

class Step(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    columns: list[Column]
    name: str | None = None
    steps: list[Step] | None = None

class Version(PermissiveModel):
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", description="Not allowed on create.")
    steps: list[Step]
    triggers: list[AfterCloseTimeout | CartItemCount | CartProduct | CartValue | Channel | CustomJavascript | Delay | Device | ExitIntent | IdentifiedProfiles | ListsAndSegments | Location | PageVisits | PreviouslySubmitted | ProfileEventTracked | Scroll | UnidentifiedProfiles | UrlPatterns | BackInStock] | None = None
    teasers: list[Teaser] | None = None
    dynamic_button: DynamicButton | None = None
    name: str | None = None
    styles: VersionStyles | None = None
    properties: VersionProperties | None = None
    type_: Literal["banner", "embed", "flyout", "full_screen", "popup"] | None = Field('popup', validation_alias="type", serialization_alias="type", description="Form type enumeration.")
    location: Literal["bottom_center", "bottom_left", "bottom_right", "center_left", "center_right", "top_center", "top_left", "top_right"] | None = Field(None, description="Display location enumeration.")
    status: Literal["draft", "live"] | None = Field('draft', description="Form status enumeration.")
    ab_test: bool | None = False
    specialties: list[Literal["BACK_IN_STOCK"]] | None = None


# Rebuild models to resolve forward references (required for circular refs)
AddCategoriesToCatalogItemBodyDataItem.model_rebuild()
AddItemsToCatalogCategoryBodyDataItem.model_rebuild()
AdditionalField.model_rebuild()
AddProfilesToListBodyDataItem.model_rebuild()
AfterCloseTimeout.model_rebuild()
AfterCloseTimeoutProperties.model_rebuild()
AgeGate.model_rebuild()
AgeGateProperties.model_rebuild()
AgeGateStyles.model_rebuild()
AlltimeDateFilter.model_rebuild()
AnniversaryDateFilter.model_rebuild()
ApiMethodFilter.model_rebuild()
BackgroundImage.model_rebuild()
BackgroundImageStyles.model_rebuild()
BackInStock.model_rebuild()
BackInStockDynamicButtonBorderStyles.model_rebuild()
BackInStockDynamicButtonData.model_rebuild()
BackInStockDynamicButtonDropShadowStyles.model_rebuild()
BackInStockDynamicButtonStyles.model_rebuild()
BackInStockDynamicButtonTextStyles.model_rebuild()
BackInStockEmailConsentCheckbox.model_rebuild()
BackInStockEmailConsentCheckboxProperties.model_rebuild()
BackInStockEmailConsentCheckboxStyles.model_rebuild()
BackInStockMethodFilter.model_rebuild()
BackInStockProperties.model_rebuild()
BannerStyles.model_rebuild()
BaseEventCreateQueryBulkEntryResourceObject.model_rebuild()
BaseEventCreateQueryBulkEntryResourceObjectAttributes.model_rebuild()
BaseEventCreateQueryBulkEntryResourceObjectAttributesMetric.model_rebuild()
BlockDisplayOptions.model_rebuild()
BooleanFilter.model_rebuild()
BorderStyle.model_rebuild()
BounceDateFilter.model_rebuild()
BulkImportProfilesBodyDataRelationshipsListsDataItem.model_rebuild()
BulkRemoveMethodFilter.model_rebuild()
Button.model_rebuild()
ButtonBlock.model_rebuild()
ButtonDropShadowStyles.model_rebuild()
ButtonProperties.model_rebuild()
ButtonStyles.model_rebuild()
CalendarDateFilter.model_rebuild()
CampaignMessageIncrement.model_rebuild()
CampaignMessageProperty.model_rebuild()
CampaignMessageStaticCount.model_rebuild()
CampaignsEmailTrackingOptions.model_rebuild()
CampaignsSmsTrackingOptions.model_rebuild()
CarrierDeactivationMethodFilter.model_rebuild()
CartItemCount.model_rebuild()
CartItemCountProperties.model_rebuild()
CartProduct.model_rebuild()
CartProductProperties.model_rebuild()
CartValue.model_rebuild()
CartValueProperties.model_rebuild()
CatalogCategoryCreateQueryResourceObject.model_rebuild()
CatalogCategoryCreateQueryResourceObjectAttributes.model_rebuild()
CatalogCategoryCreateQueryResourceObjectRelationships.model_rebuild()
CatalogCategoryCreateQueryResourceObjectRelationshipsItems.model_rebuild()
CatalogCategoryCreateQueryResourceObjectRelationshipsItemsDataItem.model_rebuild()
CatalogCategoryDeleteQueryResourceObject.model_rebuild()
CatalogCategoryUpdateQueryResourceObject.model_rebuild()
CatalogCategoryUpdateQueryResourceObjectAttributes.model_rebuild()
CatalogCategoryUpdateQueryResourceObjectRelationships.model_rebuild()
CatalogCategoryUpdateQueryResourceObjectRelationshipsItems.model_rebuild()
CatalogCategoryUpdateQueryResourceObjectRelationshipsItemsDataItem.model_rebuild()
CatalogItemCreateQueryResourceObject.model_rebuild()
CatalogItemCreateQueryResourceObjectAttributes.model_rebuild()
CatalogItemCreateQueryResourceObjectRelationships.model_rebuild()
CatalogItemCreateQueryResourceObjectRelationshipsCategories.model_rebuild()
CatalogItemCreateQueryResourceObjectRelationshipsCategoriesDataItem.model_rebuild()
CatalogItemDeleteQueryResourceObject.model_rebuild()
CatalogItemUpdateQueryResourceObject.model_rebuild()
CatalogItemUpdateQueryResourceObjectAttributes.model_rebuild()
CatalogItemUpdateQueryResourceObjectRelationships.model_rebuild()
CatalogItemUpdateQueryResourceObjectRelationshipsCategories.model_rebuild()
CatalogItemUpdateQueryResourceObjectRelationshipsCategoriesDataItem.model_rebuild()
CatalogVariantCreateQueryResourceObject.model_rebuild()
CatalogVariantCreateQueryResourceObjectAttributes.model_rebuild()
CatalogVariantCreateQueryResourceObjectRelationships.model_rebuild()
CatalogVariantCreateQueryResourceObjectRelationshipsItem.model_rebuild()
CatalogVariantCreateQueryResourceObjectRelationshipsItemData.model_rebuild()
CatalogVariantDeleteQueryResourceObject.model_rebuild()
CatalogVariantUpdateQueryResourceObject.model_rebuild()
CatalogVariantUpdateQueryResourceObjectAttributes.model_rebuild()
Channel.model_rebuild()
ChannelProperties.model_rebuild()
ChannelSettings.model_rebuild()
Checkboxes.model_rebuild()
CheckboxesProperties.model_rebuild()
CheckboxesStyles.model_rebuild()
CheckoutMethodFilter.model_rebuild()
Close.model_rebuild()
CloseButtonStyle.model_rebuild()
CloseProperties.model_rebuild()
Column.model_rebuild()
ColumnStyles.model_rebuild()
ConditionGroup.model_rebuild()
ConstantContactIntegrationFilter.model_rebuild()
ConstantContactIntegrationMethodFilter.model_rebuild()
ContentRepeat.model_rebuild()
CountdownTimer.model_rebuild()
CountdownTimerProperties.model_rebuild()
CountdownTimerStyles.model_rebuild()
Coupon.model_rebuild()
CouponCodeCreateQueryResourceObject.model_rebuild()
CouponCodeCreateQueryResourceObjectAttributes.model_rebuild()
CouponCodeCreateQueryResourceObjectRelationships.model_rebuild()
CouponCodeCreateQueryResourceObjectRelationshipsCoupon.model_rebuild()
CouponCodeCreateQueryResourceObjectRelationshipsCouponData.model_rebuild()
CouponProperties.model_rebuild()
CouponStyles.model_rebuild()
CreateCatalogCategoryBodyDataRelationshipsItemsDataItem.model_rebuild()
CreateCatalogItemBodyDataRelationshipsCategoriesDataItem.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfile.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileData.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributes.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesLocation.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesMeta.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesMetaPatchProperties.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptions.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsEmail.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsEmailMarketing.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsPush.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsPushMarketing.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsSms.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsSmsMarketing.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsSmsTransactional.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsWhatsapp.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsWhatsappMarketing.model_rebuild()
CreateClientSubscriptionBodyDataAttributesProfileDataAttributesSubscriptionsWhatsappTransactional.model_rebuild()
CreateEventBodyDataAttributesProfile.model_rebuild()
CreateEventBodyDataAttributesProfileData.model_rebuild()
CreateEventBodyDataAttributesProfileDataAttributes.model_rebuild()
CreateEventBodyDataAttributesProfileDataAttributesLocation.model_rebuild()
CreateEventBodyDataAttributesProfileDataAttributesMeta.model_rebuild()
CreateEventBodyDataAttributesProfileDataAttributesMetaPatchProperties.model_rebuild()
CreatePushTokenBodyDataAttributesDeviceMetadata.model_rebuild()
CreatePushTokenBodyDataAttributesProfile.model_rebuild()
CreatePushTokenBodyDataAttributesProfileData.model_rebuild()
CreatePushTokenBodyDataAttributesProfileDataAttributes.model_rebuild()
CreatePushTokenBodyDataAttributesProfileDataAttributesLocation.model_rebuild()
CreatePushTokenBodyDataAttributesProfileDataAttributesMeta.model_rebuild()
CreatePushTokenBodyDataAttributesProfileDataAttributesMetaPatchProperties.model_rebuild()
CustomJavascript.model_rebuild()
CustomMetricCondition.model_rebuild()
CustomMetricGroup.model_rebuild()
CustomQuestionDto.model_rebuild()
CustomSourceFilter.model_rebuild()
CustomTimeframe.model_rebuild()
DataSourceRecordResourceObject.model_rebuild()
DataSourceRecordResourceObjectAttributes.model_rebuild()
DataWarehouseImportMethodFilter.model_rebuild()
Date.model_rebuild()
DateProperties.model_rebuild()
DateStyles.model_rebuild()
Delay.model_rebuild()
DelayProperties.model_rebuild()
Device.model_rebuild()
DeviceProperties.model_rebuild()
DoubleOptinFilter.model_rebuild()
Dropdown.model_rebuild()
DropdownProperties.model_rebuild()
DropdownStyles.model_rebuild()
DropShadow.model_rebuild()
DropShadowBlock.model_rebuild()
DynamicButton.model_rebuild()
DynamicTrackingParam.model_rebuild()
EffectiveDateFilter.model_rebuild()
Email.model_rebuild()
EmailContent.model_rebuild()
EmailMessageDefinition.model_rebuild()
EmailProperties.model_rebuild()
EmailSendOptions.model_rebuild()
EmailStyles.model_rebuild()
EmailSubscriptionParameters.model_rebuild()
EmailUnsubscriptionParameters.model_rebuild()
EqualsStringFilter.model_rebuild()
ErrorMessages.model_rebuild()
EventsBulkCreateQueryResourceObject.model_rebuild()
EventsBulkCreateQueryResourceObjectAttributes.model_rebuild()
EventsBulkCreateQueryResourceObjectAttributesEvents.model_rebuild()
EventsBulkCreateQueryResourceObjectAttributesProfile.model_rebuild()
ExistenceOperatorExistenceFilter.model_rebuild()
ExitIntent.model_rebuild()
ExplicitlyReachable.model_rebuild()
ExplicitlyUnreachable.model_rebuild()
FailedAgeGateMethodFilter.model_rebuild()
FixedTimerConfiguration.model_rebuild()
FormMethodFilter.model_rebuild()
FormSubscribeFilter.model_rebuild()
GoToInbox.model_rebuild()
GreaterThanPositiveNumericFilter.model_rebuild()
HasEmailMarketing.model_rebuild()
HasEmailMarketingConsent.model_rebuild()
HasEmailMarketingNeverSubscribed.model_rebuild()
HasEmailMarketingSubscribed.model_rebuild()
HasPushMarketing.model_rebuild()
HasPushMarketingConsent.model_rebuild()
HasSmsMarketingConsent.model_rebuild()
HasSmsMarketingSubscribed.model_rebuild()
HorizontalRuleBlock.model_rebuild()
HtmlBlock.model_rebuild()
HtmlBlockData.model_rebuild()
HtmlText.model_rebuild()
HtmlTextProperties.model_rebuild()
HtmlTextStyles.model_rebuild()
IdentifiedProfiles.model_rebuild()
Image.model_rebuild()
ImageAssetProperties.model_rebuild()
ImageBlock.model_rebuild()
ImageDropShadowStyles.model_rebuild()
ImageProperties.model_rebuild()
ImageStyles.model_rebuild()
ImmediateSendStrategy.model_rebuild()
ImplicitlyOrExplicitlyReachable.model_rebuild()
ImplicitlyOrExplicitlyUnreachable.model_rebuild()
ImplicitlyReachable.model_rebuild()
ImplicitlyUnreachable.model_rebuild()
InboundMessageMethodFilter.model_rebuild()
InputStyles.model_rebuild()
InStringArrayFilter.model_rebuild()
IntegerFilter.model_rebuild()
InvalidEmailDateFilter.model_rebuild()
IsSetExistenceFilter.model_rebuild()
LessThanPositiveNumericFilter.model_rebuild()
LinkStyles.model_rebuild()
ListContainsOperatorListContainsFilter.model_rebuild()
ListLengthFilter.model_rebuild()
ListRegexOperatorListContainsFilter.model_rebuild()
ListsAndSegments.model_rebuild()
ListsAndSegmentsProperties.model_rebuild()
ListSetFilter.model_rebuild()
ListSubstringFilter.model_rebuild()
LocalStaticSend.model_rebuild()
Location.model_rebuild()
LocationProperties.model_rebuild()
MailboxProviderMethodFilter.model_rebuild()
ManualAddManualMethodFilter.model_rebuild()
ManualImportManualMethodFilter.model_rebuild()
ManualImportMethodFilter.model_rebuild()
ManualRemoveMethodFilter.model_rebuild()
ManualSuppressionDateFilter.model_rebuild()
Margin.model_rebuild()
MergeProfilesBodyDataRelationshipsProfilesDataItem.model_rebuild()
MessageBlockedMethodFilter.model_rebuild()
MethodFilter.model_rebuild()
MetricCreateQueryResourceObject.model_rebuild()
MetricCreateQueryResourceObjectAttributes.model_rebuild()
MobileOverlay.model_rebuild()
MobilePushBadge.model_rebuild()
MobilePushContentUpdate.model_rebuild()
MobilePushMessageSilentDefinitionUpdate.model_rebuild()
MobilePushMessageStandardDefinitionUpdate.model_rebuild()
MobilePushNoBadge.model_rebuild()
MobilePushOptions.model_rebuild()
NextStep.model_rebuild()
NextStepProperties.model_rebuild()
NoEmailMarketing.model_rebuild()
NoEmailMarketingConsent.model_rebuild()
NoEmailMarketingNeverSubscribed.model_rebuild()
NoEmailMarketingSubscribed.model_rebuild()
NoEmailMarketingUnsubscribed.model_rebuild()
NonLocalStaticSend.model_rebuild()
NoPushMarketing.model_rebuild()
NoPushMarketingConsent.model_rebuild()
NoSmsMarketing.model_rebuild()
NoSmsMarketingConsent.model_rebuild()
NoSmsMarketingNeverSubscribed.model_rebuild()
NoSmsMarketingUnsubscribed.model_rebuild()
NumericOperatorNumericFilter.model_rebuild()
NumericRangeFilter.model_rebuild()
OneClickUnsubscribeMethodFilter.model_rebuild()
OnsiteProfileCreateQueryResourceObject.model_rebuild()
OnsiteProfileCreateQueryResourceObjectAttributes.model_rebuild()
OnsiteProfileMeta.model_rebuild()
OpenForm.model_rebuild()
OpenFormProperties.model_rebuild()
OptInCode.model_rebuild()
OptInCodeProperties.model_rebuild()
OptInCodeStyles.model_rebuild()
Padding.model_rebuild()
PageVisits.model_rebuild()
PageVisitsProperties.model_rebuild()
PhoneNumber.model_rebuild()
PhoneNumberConsentChannelSettings.model_rebuild()
PhoneNumberProperties.model_rebuild()
PhoneNumberStyles.model_rebuild()
PreferencePageFilter.model_rebuild()
PreferencePageMethodFilter.model_rebuild()
PreviouslySubmitted.model_rebuild()
ProfileEventTracked.model_rebuild()
ProfileEventTrackedProperties.model_rebuild()
ProfileHasCustomObjectCondition.model_rebuild()
ProfileHasCustomObjectFilter.model_rebuild()
ProfileHasGroupMembershipCondition.model_rebuild()
ProfileLocation.model_rebuild()
ProfileMarketingConsentCondition.model_rebuild()
ProfileMeta.model_rebuild()
ProfileMetaPatchProperties.model_rebuild()
ProfileMetricFunnelSteps.model_rebuild()
ProfileMetricPropertyFilter.model_rebuild()
ProfileModificationMethodFilter.model_rebuild()
ProfileNoGroupMembershipCondition.model_rebuild()
ProfilePermissionsCondition.model_rebuild()
ProfilePostalCodeDistanceCondition.model_rebuild()
ProfilePredictiveAnalyticsChannelAffinityPriorityCondition.model_rebuild()
ProfilePredictiveAnalyticsChannelAffinityPriorityFilter.model_rebuild()
ProfilePredictiveAnalyticsChannelAffinityRankCondition.model_rebuild()
ProfilePredictiveAnalyticsChannelAffinityRankFilter.model_rebuild()
ProfilePredictiveAnalyticsDateCondition.model_rebuild()
ProfilePredictiveAnalyticsNumericCondition.model_rebuild()
ProfilePredictiveAnalyticsStringCondition.model_rebuild()
ProfilePredictiveAnalyticsStringFilter.model_rebuild()
ProfilePropertyCondition.model_rebuild()
ProfileRegionCondition.model_rebuild()
ProfileSubscriptionCreateQueryResourceObject.model_rebuild()
ProfileSubscriptionCreateQueryResourceObjectAttributes.model_rebuild()
ProfileSubscriptionDeleteQueryResourceObject.model_rebuild()
ProfileSubscriptionDeleteQueryResourceObjectAttributes.model_rebuild()
ProfileSuppressionCreateQueryResourceObject.model_rebuild()
ProfileSuppressionCreateQueryResourceObjectAttributes.model_rebuild()
ProfileSuppressionDeleteQueryResourceObject.model_rebuild()
ProfileSuppressionDeleteQueryResourceObjectAttributes.model_rebuild()
ProfileUpsertQueryResourceObject.model_rebuild()
ProfileUpsertQueryResourceObjectAttributes.model_rebuild()
PromotionalSmsSubscription.model_rebuild()
PropertyOption.model_rebuild()
ProvidedLandlineMethodFilter.model_rebuild()
ProvidedNoAgeMethodFilter.model_rebuild()
PushOnOpenApp.model_rebuild()
PushOnOpenDeepLink.model_rebuild()
PushSendOptions.model_rebuild()
PushSubscriptionParameters.model_rebuild()
PushTokenDeviceMetadata.model_rebuild()
PushTokenEntry.model_rebuild()
QuoteStyle.model_rebuild()
RadioButtons.model_rebuild()
RadioButtonsProperties.model_rebuild()
RadioButtonsStyles.model_rebuild()
RatingStyle.model_rebuild()
RecordedDateFilter.model_rebuild()
Redirect.model_rebuild()
RedirectProperties.model_rebuild()
RejectReasonFake.model_rebuild()
RejectReasonMisleading.model_rebuild()
RejectReasonOther.model_rebuild()
RejectReasonPrivateInformation.model_rebuild()
RejectReasonProfanity.model_rebuild()
RejectReasonUnrelated.model_rebuild()
RelativeAnniversaryDateFilter.model_rebuild()
RelativeDateOperatorBaseRelativeDateFilter.model_rebuild()
RelativeDateRangeFilter.model_rebuild()
RemoveCategoriesFromCatalogItemBodyDataItem.model_rebuild()
RemoveItemsFromCatalogCategoryBodyDataItem.model_rebuild()
RemoveProfilesFromListBodyDataItem.model_rebuild()
RemoveTagFromCampaignsBodyDataItem.model_rebuild()
RemoveTagFromFlowsBodyDataItem.model_rebuild()
RemoveTagFromListsBodyDataItem.model_rebuild()
RemoveTagFromSegmentsBodyDataItem.model_rebuild()
RenderOptions.model_rebuild()
ResendOptInCode.model_rebuild()
Review.model_rebuild()
ReviewerNameStyle.model_rebuild()
ReviewProperties.model_rebuild()
ReviewStatusFeatured.model_rebuild()
ReviewStatusPending.model_rebuild()
ReviewStatusPublished.model_rebuild()
ReviewStatusRejected.model_rebuild()
ReviewStatusUnpublished.model_rebuild()
ReviewStyles.model_rebuild()
RichTextMargin.model_rebuild()
RichTextStyle.model_rebuild()
RichTextStyles.model_rebuild()
Row.model_rebuild()
Scroll.model_rebuild()
ScrollProperties.model_rebuild()
SegmentsProfileMetricCondition.model_rebuild()
SegmentsProfileMetricFunnelCondition.model_rebuild()
SftpMethodFilter.model_rebuild()
ShopifyIntegrationFilter.model_rebuild()
ShopifyIntegrationMethodFilter.model_rebuild()
SideImageSettings.model_rebuild()
SignupCounter.model_rebuild()
SignupCounterProperties.model_rebuild()
SignupCounterStyles.model_rebuild()
SkipToSuccess.model_rebuild()
SkipToSuccessProperties.model_rebuild()
SmartSendTimeStrategy.model_rebuild()
SmsConsentCheckbox.model_rebuild()
SmsConsentCheckboxProperties.model_rebuild()
SmsConsentCheckboxStyles.model_rebuild()
SmsContentCreate.model_rebuild()
SmsDisclosure.model_rebuild()
SmsDisclosureAccountDefault.model_rebuild()
SmsDisclosureCustom.model_rebuild()
SmsDisclosureProperties.model_rebuild()
SmsDisclosureStyles.model_rebuild()
SmsDisclosureTextStyle.model_rebuild()
SmsMessageDefinitionCreate.model_rebuild()
SmsSendOptions.model_rebuild()
SmsSubscriptionParameters.model_rebuild()
SmsUnsubscriptionParameters.model_rebuild()
SpacerBlock.model_rebuild()
SpamComplaintMethodFilter.model_rebuild()
SpinToWin.model_rebuild()
SpinToWinProperties.model_rebuild()
SpinToWinSliceConfig.model_rebuild()
SpinToWinSliceStyle.model_rebuild()
SpinToWinStyles.model_rebuild()
StaticCouponConfig.model_rebuild()
StaticDateFilter.model_rebuild()
StaticDateRangeFilter.model_rebuild()
StaticSendStrategy.model_rebuild()
StaticTrackingParam.model_rebuild()
StatusDateFilter.model_rebuild()
Step.model_rebuild()
StringArrayOperatorStringArrayFilter.model_rebuild()
StringInArrayFilter.model_rebuild()
StringOperatorStringFilter.model_rebuild()
StringPhoneOperatorStringArrayFilter.model_rebuild()
SubmitBackInStock.model_rebuild()
SubmitBackInStockProperties.model_rebuild()
SubmitOptInCode.model_rebuild()
SubscribedSmsIsRcsCapableFilter.model_rebuild()
SubscribeViaSms.model_rebuild()
SubscribeViaSmsProperties.model_rebuild()
SubscribeViaWhatsApp.model_rebuild()
SubscribeViaWhatsAppProperties.model_rebuild()
SubscriptionChannels.model_rebuild()
SubscriptionParameters.model_rebuild()
TagCampaignsBodyDataItem.model_rebuild()
TagFlowsBodyDataItem.model_rebuild()
TagListsBodyDataItem.model_rebuild()
TagSegmentsBodyDataItem.model_rebuild()
Teaser.model_rebuild()
TeaserStyles.model_rebuild()
Text.model_rebuild()
TextBlock.model_rebuild()
TextBlockData.model_rebuild()
TextBlockStyles.model_rebuild()
TextProperties.model_rebuild()
TextStyle.model_rebuild()
TextStyles.model_rebuild()
ThrottledSendStrategy.model_rebuild()
Timeframe.model_rebuild()
TriggerBaseProperties.model_rebuild()
UnidentifiedProfiles.model_rebuild()
UniqueCouponConfig.model_rebuild()
UnsubscriptionChannels.model_rebuild()
UnsubscriptionParameters.model_rebuild()
UpdateCatalogCategoryBodyDataRelationshipsItemsDataItem.model_rebuild()
UpdateCatalogItemBodyDataRelationshipsCategoriesDataItem.model_rebuild()
UpdateCategoriesForCatalogItemBodyDataItem.model_rebuild()
UpdateItemsForCatalogCategoryBodyDataItem.model_rebuild()
UpdateWebhookBodyDataRelationshipsWebhookTopicsDataItem.model_rebuild()
UrlPatterns.model_rebuild()
UrlPatternsProperties.model_rebuild()
VariableTimerConfiguration.model_rebuild()
Version.model_rebuild()
VersionProperties.model_rebuild()
VersionStyles.model_rebuild()
WhatsAppSubscriptionParameters.model_rebuild()
WhatsAppUnsubscriptionParameters.model_rebuild()

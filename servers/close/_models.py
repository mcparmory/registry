"""
Close Api MCP Server - Pydantic Models

Generated: 2026-04-06 18:43:55 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "DeleteV1ActivityCallIdRequest",
    "DeleteV1ActivityCustomIdRequest",
    "DeleteV1ActivityEmailIdRequest",
    "DeleteV1ActivityEmailthreadIdRequest",
    "DeleteV1ActivityFormSubmissionIdRequest",
    "DeleteV1ActivityMeetingIdRequest",
    "DeleteV1ActivityNoteIdRequest",
    "DeleteV1ActivitySmsIdRequest",
    "DeleteV1ActivityStatusChangeLeadIdRequest",
    "DeleteV1ActivityStatusChangeOpportunityIdRequest",
    "DeleteV1ActivityTaskCompletedIdRequest",
    "DeleteV1ActivityWhatsappMessageIdRequest",
    "DeleteV1CommentCommentIdRequest",
    "DeleteV1ContactIdRequest",
    "DeleteV1CustomActivityIdRequest",
    "DeleteV1CustomFieldActivityCustomFieldIdRequest",
    "DeleteV1CustomFieldContactCustomFieldIdRequest",
    "DeleteV1CustomFieldCustomObjectTypeCustomFieldIdRequest",
    "DeleteV1CustomFieldLeadCustomFieldIdRequest",
    "DeleteV1CustomFieldOpportunityCustomFieldIdRequest",
    "DeleteV1CustomFieldSharedCustomFieldIdAssociationObjectTypeRequest",
    "DeleteV1CustomFieldSharedCustomFieldIdRequest",
    "DeleteV1CustomObjectIdRequest",
    "DeleteV1CustomObjectTypeIdRequest",
    "DeleteV1EmailTemplateIdRequest",
    "DeleteV1GroupGroupIdMemberUserIdRequest",
    "DeleteV1GroupGroupIdRequest",
    "DeleteV1IntegrationLinkIdRequest",
    "DeleteV1LeadIdRequest",
    "DeleteV1OpportunityIdRequest",
    "DeleteV1OutcomeIdRequest",
    "DeleteV1PhoneNumberIdRequest",
    "DeleteV1PipelinePipelineIdRequest",
    "DeleteV1RoleRoleIdRequest",
    "DeleteV1SavedSearchIdRequest",
    "DeleteV1SchedulingLinkIdRequest",
    "DeleteV1SchedulingLinkIntegrationSourceIdRequest",
    "DeleteV1SendAsIdRequest",
    "DeleteV1SendAsRequest",
    "DeleteV1SequenceIdRequest",
    "DeleteV1SharedSchedulingLinkIdRequest",
    "DeleteV1SmsTemplateIdRequest",
    "DeleteV1StatusLeadStatusIdRequest",
    "DeleteV1StatusOpportunityStatusIdRequest",
    "DeleteV1TaskIdRequest",
    "DeleteV1UnsubscribeEmailEmailAddressRequest",
    "DeleteV1WebhookIdRequest",
    "GetV1ActivityCallIdRequest",
    "GetV1ActivityCallRequest",
    "GetV1ActivityCreatedIdRequest",
    "GetV1ActivityCreatedRequest",
    "GetV1ActivityCustomIdRequest",
    "GetV1ActivityCustomRequest",
    "GetV1ActivityEmailIdRequest",
    "GetV1ActivityEmailRequest",
    "GetV1ActivityEmailthreadIdRequest",
    "GetV1ActivityEmailthreadRequest",
    "GetV1ActivityFormSubmissionIdRequest",
    "GetV1ActivityFormSubmissionRequest",
    "GetV1ActivityLeadMergeIdRequest",
    "GetV1ActivityLeadMergeRequest",
    "GetV1ActivityMeetingIdRequest",
    "GetV1ActivityMeetingRequest",
    "GetV1ActivityNoteIdRequest",
    "GetV1ActivityNoteRequest",
    "GetV1ActivityRequest",
    "GetV1ActivitySmsIdRequest",
    "GetV1ActivitySmsRequest",
    "GetV1ActivityStatusChangeLeadIdRequest",
    "GetV1ActivityStatusChangeLeadRequest",
    "GetV1ActivityStatusChangeOpportunityIdRequest",
    "GetV1ActivityStatusChangeOpportunityRequest",
    "GetV1ActivityTaskCompletedIdRequest",
    "GetV1ActivityTaskCompletedRequest",
    "GetV1ActivityWhatsappMessageIdRequest",
    "GetV1ActivityWhatsappMessageRequest",
    "GetV1BulkActionDeleteIdRequest",
    "GetV1BulkActionEditIdRequest",
    "GetV1BulkActionEmailIdRequest",
    "GetV1BulkActionSequenceSubscriptionIdRequest",
    "GetV1CommentCommentIdRequest",
    "GetV1CommentRequest",
    "GetV1CommentThreadRequest",
    "GetV1CommentThreadThreadIdRequest",
    "GetV1ConnectedAccountIdRequest",
    "GetV1ContactIdRequest",
    "GetV1ContactRequest",
    "GetV1CustomActivityIdRequest",
    "GetV1CustomFieldActivityIdRequest",
    "GetV1CustomFieldActivityRequest",
    "GetV1CustomFieldContactIdRequest",
    "GetV1CustomFieldContactRequest",
    "GetV1CustomFieldCustomObjectTypeIdRequest",
    "GetV1CustomFieldLeadIdRequest",
    "GetV1CustomFieldLeadRequest",
    "GetV1CustomFieldOpportunityIdRequest",
    "GetV1CustomFieldOpportunityRequest",
    "GetV1CustomFieldSchemaObjectTypeRequest",
    "GetV1CustomObjectIdRequest",
    "GetV1CustomObjectRequest",
    "GetV1CustomObjectTypeIdRequest",
    "GetV1DialerIdRequest",
    "GetV1DialerRequest",
    "GetV1EmailTemplateIdRenderRequest",
    "GetV1EmailTemplateIdRequest",
    "GetV1EmailTemplateRequest",
    "GetV1EventIdRequest",
    "GetV1EventRequest",
    "GetV1ExportIdRequest",
    "GetV1ExportRequest",
    "GetV1GroupGroupIdRequest",
    "GetV1GroupRequest",
    "GetV1IntegrationLinkIdRequest",
    "GetV1LeadIdRequest",
    "GetV1LeadRequest",
    "GetV1MembershipIdPinnedViewsRequest",
    "GetV1OpportunityIdRequest",
    "GetV1OpportunityRequest",
    "GetV1OrganizationIdRequest",
    "GetV1OutcomeIdRequest",
    "GetV1PhoneNumberIdRequest",
    "GetV1PhoneNumberRequest",
    "GetV1ReportCustomOrganizationIdRequest",
    "GetV1ReportSentEmailsOrganizationIdRequest",
    "GetV1ReportStatusesLeadOrganizationIdRequest",
    "GetV1ReportStatusesOpportunityOrganizationIdRequest",
    "GetV1RoleIdRequest",
    "GetV1SavedSearchIdRequest",
    "GetV1SchedulingLinkIdRequest",
    "GetV1SendAsIdRequest",
    "GetV1SendAsRequest",
    "GetV1SequenceIdRequest",
    "GetV1SequenceRequest",
    "GetV1SequenceSubscriptionIdRequest",
    "GetV1SequenceSubscriptionRequest",
    "GetV1SharedSchedulingLinkIdRequest",
    "GetV1SmsTemplateIdRequest",
    "GetV1SmsTemplateRequest",
    "GetV1TaskIdRequest",
    "GetV1TaskRequest",
    "GetV1UserAvailabilityRequest",
    "GetV1UserIdRequest",
    "GetV1UserRequest",
    "GetV1WebhookIdRequest",
    "PostApiV1DataSearchRequest",
    "PostV1ActivityCallRequest",
    "PostV1ActivityCustomRequest",
    "PostV1ActivityEmailRequest",
    "PostV1ActivityMeetingIdIntegrationRequest",
    "PostV1ActivityNoteRequest",
    "PostV1ActivitySmsRequest",
    "PostV1ActivityStatusChangeLeadRequest",
    "PostV1ActivityStatusChangeOpportunityRequest",
    "PostV1ActivityWhatsappMessageRequest",
    "PostV1BulkActionDeleteRequest",
    "PostV1BulkActionEditRequest",
    "PostV1BulkActionEmailRequest",
    "PostV1BulkActionSequenceSubscriptionRequest",
    "PostV1CommentRequest",
    "PostV1ContactRequest",
    "PostV1CustomActivityRequest",
    "PostV1CustomFieldActivityRequest",
    "PostV1CustomFieldContactRequest",
    "PostV1CustomFieldCustomObjectTypeRequest",
    "PostV1CustomFieldLeadRequest",
    "PostV1CustomFieldOpportunityRequest",
    "PostV1CustomFieldSharedRequest",
    "PostV1CustomFieldSharedSharedCustomFieldIdAssociationRequest",
    "PostV1CustomObjectRequest",
    "PostV1CustomObjectTypeRequest",
    "PostV1EmailTemplateRequest",
    "PostV1EnrichFieldRequest",
    "PostV1ExportLeadRequest",
    "PostV1ExportOpportunityRequest",
    "PostV1FilesUploadRequest",
    "PostV1GroupGroupIdMemberRequest",
    "PostV1GroupRequest",
    "PostV1IntegrationLinkRequest",
    "PostV1LeadMergeRequest",
    "PostV1LeadRequest",
    "PostV1MembershipRequest",
    "PostV1OutcomeRequest",
    "PostV1PhoneNumberRequestInternalRequest",
    "PostV1PipelineRequest",
    "PostV1ReportActivityRequest",
    "PostV1ReportFunnelOpportunityStagesRequest",
    "PostV1ReportFunnelOpportunityTotalsRequest",
    "PostV1RoleRequest",
    "PostV1SavedSearchRequest",
    "PostV1SchedulingLinkIntegrationRequest",
    "PostV1SchedulingLinkRequest",
    "PostV1SendAsBulkRequest",
    "PostV1SendAsRequest",
    "PostV1SequenceRequest",
    "PostV1SequenceSubscriptionRequest",
    "PostV1SharedSchedulingLinkAssociationRequest",
    "PostV1SharedSchedulingLinkAssociationUnmapRequest",
    "PostV1SharedSchedulingLinkRequest",
    "PostV1SmsTemplateRequest",
    "PostV1StatusLeadRequest",
    "PostV1StatusOpportunityRequest",
    "PostV1TaskRequest",
    "PostV1UnsubscribeEmailRequest",
    "PostV1WebhookRequest",
    "PutV1ActivityCallIdRequest",
    "PutV1ActivityCustomIdRequest",
    "PutV1ActivityEmailIdRequest",
    "PutV1ActivityMeetingIdRequest",
    "PutV1ActivityNoteIdRequest",
    "PutV1ActivitySmsIdRequest",
    "PutV1ActivityWhatsappMessageIdRequest",
    "PutV1CommentCommentIdRequest",
    "PutV1ContactIdRequest",
    "PutV1CustomActivityIdRequest",
    "PutV1CustomFieldActivityCustomFieldIdRequest",
    "PutV1CustomFieldContactCustomFieldIdRequest",
    "PutV1CustomFieldCustomObjectTypeCustomFieldIdRequest",
    "PutV1CustomFieldLeadCustomFieldIdRequest",
    "PutV1CustomFieldOpportunityCustomFieldIdRequest",
    "PutV1CustomFieldSchemaObjectTypeRequest",
    "PutV1CustomFieldSharedCustomFieldIdRequest",
    "PutV1CustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequest",
    "PutV1CustomObjectIdRequest",
    "PutV1CustomObjectTypeIdRequest",
    "PutV1EmailTemplateIdRequest",
    "PutV1GroupGroupIdRequest",
    "PutV1IntegrationLinkIdRequest",
    "PutV1LeadIdRequest",
    "PutV1MembershipIdPinnedViewsRequest",
    "PutV1MembershipIdRequest",
    "PutV1MembershipRequest",
    "PutV1OpportunityIdRequest",
    "PutV1OrganizationIdRequest",
    "PutV1OutcomeIdRequest",
    "PutV1PhoneNumberIdRequest",
    "PutV1PipelinePipelineIdRequest",
    "PutV1RoleRoleIdRequest",
    "PutV1SavedSearchIdRequest",
    "PutV1SchedulingLinkIdRequest",
    "PutV1SequenceIdRequest",
    "PutV1SequenceSubscriptionIdRequest",
    "PutV1SharedSchedulingLinkIdRequest",
    "PutV1SmsTemplateIdRequest",
    "PutV1StatusLeadStatusIdRequest",
    "PutV1StatusOpportunityStatusIdRequest",
    "PutV1TaskIdRequest",
    "PutV1TaskRequest",
    "PutV1WebhookIdRequest",
    "PostApiV1DataSearchBodySortItem",
    "PostV1ActivityEmailBodyAttachmentsItem",
    "PostV1ActivityNoteBodyAttachmentsItem",
    "PostV1ActivityWhatsappMessageBodyAttachmentsItem",
    "PostV1WebhookBodyEventsItem",
    "PutV1CustomFieldSchemaObjectTypeBodyFieldsItem",
    "PutV1PipelinePipelineIdBodyStatusesItem",
    "PutV1WebhookIdBodyEventsItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_leads
class GetV1LeadRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of leads to return in a single request. Must be at least 1.", ge=1)
class GetV1LeadRequest(StrictModel):
    """Retrieve a list of all leads with optional pagination support. Use the limit parameter to control the number of results returned per request."""
    query: GetV1LeadRequestQuery | None = None

# Operation: create_lead
class PostV1LeadRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The name of the lead being created.")
class PostV1LeadRequest(StrictModel):
    """Create a new lead in the system. Nested contacts, addresses, and custom fields can be included in the request, while activities, tasks, and opportunities should be created separately."""
    body: PostV1LeadRequestBody | None = None

# Operation: get_lead
class GetV1LeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the lead to retrieve.")
class GetV1LeadIdRequest(StrictModel):
    """Retrieve a lead by ID with basic information, related tasks, opportunities, and custom fields. Note that activities must be fetched separately using a dedicated endpoint."""
    path: GetV1LeadIdRequestPath

# Operation: update_lead
class PutV1LeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the lead to update.")
class PutV1LeadIdRequestBody(StrictModel):
    custom_field_id_add: str | None = Field(default=None, validation_alias="custom.FIELD_ID.add", serialization_alias="custom.FIELD_ID.add", description="Add a value to a multi-value custom field. Use the field ID in the parameter name to target the specific custom field.")
    custom_field_id_remove: str | None = Field(default=None, validation_alias="custom.FIELD_ID.remove", serialization_alias="custom.FIELD_ID.remove", description="Remove a value from a multi-value custom field. Use the field ID in the parameter name to target the specific custom field.")
class PutV1LeadIdRequest(StrictModel):
    """Update an existing lead with support for non-destructive patches. Modify lead status, custom fields, and manage multi-value custom field entries using add/remove modifiers."""
    path: PutV1LeadIdRequestPath
    body: PutV1LeadIdRequestBody | None = None

# Operation: delete_lead
class DeleteV1LeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the lead to delete.")
class DeleteV1LeadIdRequest(StrictModel):
    """Permanently delete a lead from the system by its ID. This action cannot be undone."""
    path: DeleteV1LeadIdRequestPath

# Operation: merge_leads
class PostV1LeadMergeRequestBody(StrictModel):
    source: str | None = Field(default=None, description="The ID of the lead to merge from. This lead's data will be consolidated into the destination lead.")
    destination: str | None = Field(default=None, description="The ID of the lead to merge into. This lead will retain the merged data and become the primary record after the operation completes.")
class PostV1LeadMergeRequest(StrictModel):
    """Merge two leads by consolidating data from a source lead into a destination lead. The source lead's information is transferred to the destination lead, which becomes the primary record."""
    body: PostV1LeadMergeRequestBody | None = None

# Operation: list_contacts
class GetV1ContactRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of contacts to return in a single request. Defaults to 100 if not specified.")
class GetV1ContactRequest(StrictModel):
    """Retrieve a paginated list of all contacts in the system. Use the limit parameter to control the number of results returned per request."""
    query: GetV1ContactRequestQuery | None = None

# Operation: create_contact
class PostV1ContactRequestBody(StrictModel):
    name: str = Field(default=..., description="The full name of the contact.")
    emails: list[dict[str, Any]] | None = Field(default=None, description="A list of email addresses associated with the contact. Order is preserved as provided.")
    phones: list[dict[str, Any]] | None = Field(default=None, description="A list of phone numbers associated with the contact. Order is preserved as provided.")
    urls: list[dict[str, Any]] | None = Field(default=None, description="A list of URLs associated with the contact (e.g., website, social profiles). Order is preserved as provided.")
class PostV1ContactRequest(StrictModel):
    """Create a new contact and optionally associate it with an existing lead. If no lead is specified, a new lead will be automatically created using the contact's name."""
    body: PostV1ContactRequestBody

# Operation: get_contact
class GetV1ContactIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the contact to retrieve.")
class GetV1ContactIdRequest(StrictModel):
    """Retrieve a specific contact by its unique identifier. Returns the complete contact details including name, email, phone, and other associated information."""
    path: GetV1ContactIdRequestPath

# Operation: update_contact
class PutV1ContactIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the contact to update.")
class PutV1ContactIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The contact's full name or display name.")
    emails: list[dict[str, Any]] | None = Field(default=None, description="A list of email addresses associated with the contact. Order is preserved as provided.")
    phones: list[dict[str, Any]] | None = Field(default=None, description="A list of phone numbers associated with the contact. Order is preserved as provided.")
    urls: list[dict[str, Any]] | None = Field(default=None, description="A list of URLs associated with the contact (e.g., website, social profiles). Order is preserved as provided.")
class PutV1ContactIdRequest(StrictModel):
    """Update an existing contact's information including name, email addresses, phone numbers, and URLs. Supports adding or removing individual values from multi-value custom fields using .add or .remove suffixes."""
    path: PutV1ContactIdRequestPath
    body: PutV1ContactIdRequestBody | None = None

# Operation: delete_contact
class DeleteV1ContactIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the contact to delete.")
class DeleteV1ContactIdRequest(StrictModel):
    """Permanently delete a contact from the system by its ID. This action cannot be undone."""
    path: DeleteV1ContactIdRequestPath

# Operation: list_activities
class GetV1ActivityRequestQuery(StrictModel):
    user_id__in: list[str] | None = Field(default=None, description="Filter results to activities created by specific users. Only applicable when querying activities for a single lead.")
    contact_id__in: list[str] | None = Field(default=None, description="Filter results to activities associated with specific contacts. Only applicable when querying activities for a single lead.")
    type__in: list[str] | None = Field(default=None, validation_alias="_type__in", serialization_alias="_type__in", description="Filter results to specific activity types by type ID or name. Supports multiple types including 'Custom' for custom activity types. Only applicable when querying activities for a single lead.")
    activity_at__gt: str | None = Field(default=None, description="Return only activities that occurred after this date and time (ISO 8601 format). Requires sorting by activity_at in descending order.", json_schema_extra={'format': 'date-time'})
    activity_at__lt: str | None = Field(default=None, description="Return only activities that occurred before this date and time (ISO 8601 format). Requires sorting by activity_at in descending order.", json_schema_extra={'format': 'date-time'})
    order_by: str | None = Field(default=None, validation_alias="_order_by", serialization_alias="_order_by", description="Sort results by date_created or activity_at. Prefix with '-' for descending order (e.g., -activity_at for newest first).")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return per request.")
    thread_emails: Literal["true", "only"] | None = Field(default=None, description="Controls email object formatting in results. Use 'true' to group emails into threads with condensed email objects, or 'only' to return threads exclusively without individual email objects.")
class GetV1ActivityRequest(StrictModel):
    """Retrieve and filter activities across your CRM. Supports filtering by lead, user, contact, activity type, and date ranges, with flexible sorting and email threading options."""
    query: GetV1ActivityRequestQuery | None = None

# Operation: list_call_activities
class GetV1ActivityCallRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of call activity records to return in a single response for pagination purposes.")
class GetV1ActivityCallRequest(StrictModel):
    """Retrieve a list of all Call activities with optional filtering and pagination support. Use query parameters to narrow results by lead, user, or date range as needed."""
    query: GetV1ActivityCallRequestQuery | None = None

# Operation: log_call_activity
class PostV1ActivityCallRequestBody(StrictModel):
    direction: Literal["outbound", "inbound"] | None = Field(default=None, description="Specifies whether the call was inbound or outbound. If not provided, the direction will not be recorded.")
    recording_url: str | None = Field(default=None, description="HTTPS URL pointing to an MP3 recording of the call. Must use HTTPS protocol for security purposes.", json_schema_extra={'format': 'uri'})
class PostV1ActivityCallRequest(StrictModel):
    """Manually log a call activity for calls made outside the Close VoIP system. The activity status defaults to completed upon creation."""
    body: PostV1ActivityCallRequestBody | None = None

# Operation: get_call_activity
class GetV1ActivityCallIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Call activity record to retrieve.")
class GetV1ActivityCallIdRequest(StrictModel):
    """Retrieve a single Call activity record by its unique identifier. Use this to fetch detailed information about a specific call interaction."""
    path: GetV1ActivityCallIdRequestPath

# Operation: update_call_activity
class PutV1ActivityCallIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Call activity to update.")
class PutV1ActivityCallIdRequestBody(StrictModel):
    outcome_id: str | None = Field(default=None, description="The user-defined outcome ID to assign to this call activity, indicating how the call concluded.")
class PutV1ActivityCallIdRequest(StrictModel):
    """Update a Call activity record, such as adding notes or changing the outcome. Note that certain fields like status, duration, and direction cannot be modified for calls made through Close's VoIP system."""
    path: PutV1ActivityCallIdRequestPath
    body: PutV1ActivityCallIdRequestBody | None = None

# Operation: delete_call_activity
class DeleteV1ActivityCallIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Call activity to delete.")
class DeleteV1ActivityCallIdRequest(StrictModel):
    """Permanently delete a Call activity record by its ID. This action cannot be undone."""
    path: DeleteV1ActivityCallIdRequestPath

# Operation: list_created_activities
class GetV1ActivityCreatedRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return in the response. Defaults to 100 if not specified.")
class GetV1ActivityCreatedRequest(StrictModel):
    """Retrieve a list of all Created activities, which represent the time and method by which leads were initially created in the system. Results can be limited to control response size."""
    query: GetV1ActivityCreatedRequestQuery | None = None

# Operation: get_activity_created
class GetV1ActivityCreatedIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Created activity record to retrieve.")
class GetV1ActivityCreatedIdRequest(StrictModel):
    """Retrieve a single Created activity by ID. Created activities record when and how a lead was initially created in the system."""
    path: GetV1ActivityCreatedIdRequestPath

# Operation: list_email_activities
class GetV1ActivityEmailRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of email activities to return in the response. Must be at least 1.", ge=1)
class GetV1ActivityEmailRequest(StrictModel):
    """Retrieve a list of email activities, with one object returned per email message. Use the limit parameter to control the number of results returned."""
    query: GetV1ActivityEmailRequestQuery | None = None

# Operation: create_email_activity
class PostV1ActivityEmailRequestBody(StrictModel):
    status: Literal["inbox", "draft", "scheduled", "outbox", "sent", "error"] = Field(default=..., description="The current state of the email. Must be one of: inbox (received), draft (unsent), scheduled (queued for future send), outbox (pending send), sent (successfully delivered), or error (failed to send).")
    followup_date: str | None = Field(default=None, description="Optional ISO 8601 date-time for when a follow-up task should be created if no response is received by that time.", json_schema_extra={'format': 'date-time'})
    template_id: str | None = Field(default=None, description="Optional ID of a pre-defined email template to render on the server side, which will populate the email content.")
    sender: str | None = Field(default=None, description="Optional sender email address. Can be a plain email address or formatted as 'Display Name' <email@example.com>.")
    attachments: list[PostV1ActivityEmailBodyAttachmentsItem] | None = Field(default=None, description="Optional array of attachment objects to include with the email. Order is preserved as provided.")
class PostV1ActivityEmailRequest(StrictModel):
    """Create a new email activity with a specified status. Use this to log incoming emails, draft new messages, schedule sends, or record sent/outbox items."""
    body: PostV1ActivityEmailRequestBody

# Operation: get_email_activity
class GetV1ActivityEmailIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email activity record to retrieve.")
class GetV1ActivityEmailIdRequest(StrictModel):
    """Retrieve a single email activity record by its unique identifier. Use this to fetch detailed information about a specific email interaction."""
    path: GetV1ActivityEmailIdRequestPath

# Operation: update_email_activity
class PutV1ActivityEmailIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email activity to update.")
class PutV1ActivityEmailIdRequestBody(StrictModel):
    sender: str | None = Field(default=None, description="The sender's email address, optionally formatted as a display name with the email address (e.g., \"Name\" <email@example.com>). Required when changing the activity status to scheduled or outbox if not previously set.")
    followup_date: str | None = Field(default=None, description="The date and time for an associated follow-up task, specified in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class PutV1ActivityEmailIdRequest(StrictModel):
    """Update an email activity to modify draft content or change its status. Use this operation to transition emails between draft, scheduled, and outbox states, or to adjust follow-up timing."""
    path: PutV1ActivityEmailIdRequestPath
    body: PutV1ActivityEmailIdRequestBody | None = None

# Operation: delete_email_activity
class DeleteV1ActivityEmailIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email activity to delete.")
class DeleteV1ActivityEmailIdRequest(StrictModel):
    """Permanently delete an email activity record by its ID. This action cannot be undone."""
    path: DeleteV1ActivityEmailIdRequestPath

# Operation: list_email_threads
class GetV1ActivityEmailthreadRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of email threads to return in the response; omit to retrieve all available results.")
class GetV1ActivityEmailthreadRequest(StrictModel):
    """Retrieve a list of email thread activities, with each result representing one email conversation typically grouped by subject line."""
    query: GetV1ActivityEmailthreadRequestQuery | None = None

# Operation: get_email_thread
class GetV1ActivityEmailthreadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email thread activity to retrieve.")
class GetV1ActivityEmailthreadIdRequest(StrictModel):
    """Retrieve a specific email thread activity by its unique identifier. Use this to fetch details about a single email thread conversation."""
    path: GetV1ActivityEmailthreadIdRequestPath

# Operation: delete_email_thread
class DeleteV1ActivityEmailthreadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email thread activity to delete.")
class DeleteV1ActivityEmailthreadIdRequest(StrictModel):
    """Delete an email thread activity and all associated email activities within that thread. This is a permanent operation that removes the entire thread conversation."""
    path: DeleteV1ActivityEmailthreadIdRequestPath

# Operation: list_lead_status_changes
class GetV1ActivityStatusChangeLeadRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return. Must be at least 1.", ge=1)
class GetV1ActivityStatusChangeLeadRequest(StrictModel):
    """Retrieve a list of all lead status change activities, with optional filtering by result limit. Use this to track when and how lead statuses have been modified."""
    query: GetV1ActivityStatusChangeLeadRequestQuery | None = None

# Operation: log_lead_status_change
class PostV1ActivityStatusChangeLeadRequestBody(StrictModel):
    lead_id: str = Field(default=..., description="The unique identifier of the lead for which to log the status change.")
    old_status_id: str | None = Field(default=None, description="The unique identifier of the status the lead was transitioning from. Optional if only recording the new status.")
    new_status_id: str | None = Field(default=None, description="The unique identifier of the status the lead was transitioning to. Optional if only recording the previous status.")
class PostV1ActivityStatusChangeLeadRequest(StrictModel):
    """Log a historical lead status change event in the activity feed without modifying the lead's current status. Use this operation to import status change records from another system or organization."""
    body: PostV1ActivityStatusChangeLeadRequestBody

# Operation: get_lead_status_change
class GetV1ActivityStatusChangeLeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the lead status change activity record to retrieve.")
class GetV1ActivityStatusChangeLeadIdRequest(StrictModel):
    """Retrieve a specific lead status change activity record by its ID. Use this to view details about when and how a lead's status was modified."""
    path: GetV1ActivityStatusChangeLeadIdRequestPath

# Operation: delete_lead_status_change
class DeleteV1ActivityStatusChangeLeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the LeadStatusChange activity to delete.")
class DeleteV1ActivityStatusChangeLeadIdRequest(StrictModel):
    """Remove a LeadStatusChange activity from a lead's activity feed. This deletion only removes the status change event record and does not alter the lead's current status; use this when a status change event is irrelevant or causing integration issues with external systems."""
    path: DeleteV1ActivityStatusChangeLeadIdRequestPath

# Operation: search_meeting_by_calendar_event
class GetV1ActivityMeetingRequestQuery(StrictModel):
    provider_calendar_event_id: str = Field(default=..., description="The unique identifier of the calendar event from the provider (Google, Microsoft, etc.) that the meeting was synced from. This is the primary search criterion.")
    provider_calendar_id: str | None = Field(default=None, description="The unique identifier of the calendar from the provider where the event originated. Use this to narrow results to a specific calendar.")
    provider_calendar_type: Literal["google", "microsoft"] | None = Field(default=None, description="The calendar provider type. Specify either 'google' for Google Calendar or 'microsoft' for Microsoft Outlook/Exchange.")
    starts_at: str | None = Field(default=None, description="The meeting start time in ISO 8601 format. Useful for distinguishing meetings created from different instances of recurring calendar events.", json_schema_extra={'format': 'date-time'})
class GetV1ActivityMeetingRequest(StrictModel):
    """Search for meetings by their synced calendar event information. Use the provider calendar event ID along with optional filters like calendar ID, provider type, or start time to locate specific meetings."""
    query: GetV1ActivityMeetingRequestQuery

# Operation: get_meeting
class GetV1ActivityMeetingIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Meeting activity to retrieve.")
class GetV1ActivityMeetingIdRequest(StrictModel):
    """Retrieve a specific Meeting activity by its unique identifier. Use this to fetch details about a scheduled or completed meeting."""
    path: GetV1ActivityMeetingIdRequestPath

# Operation: update_meeting
class PutV1ActivityMeetingIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Meeting activity to update.")
class PutV1ActivityMeetingIdRequestBody(StrictModel):
    user_note_html: str | None = Field(default=None, description="Rich text HTML content for meeting notes. Allows formatted text documentation of meeting details and discussion points.")
    outcome_id: str | None = Field(default=None, description="Custom outcome identifier to associate with the meeting, used for tracking meeting results or classifications.")
class PutV1ActivityMeetingIdRequest(StrictModel):
    """Update a Meeting activity by modifying notes or outcome. Commonly used to record meeting notes in rich text format or assign a custom outcome to the meeting."""
    path: PutV1ActivityMeetingIdRequestPath
    body: PutV1ActivityMeetingIdRequestBody | None = None

# Operation: delete_meeting
class DeleteV1ActivityMeetingIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Meeting activity to delete.")
class DeleteV1ActivityMeetingIdRequest(StrictModel):
    """Permanently delete a specific Meeting activity by its ID. This action cannot be undone."""
    path: DeleteV1ActivityMeetingIdRequestPath

# Operation: create_or_update_meeting_integration
class PostV1ActivityMeetingIdIntegrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the meeting activity to integrate with a third-party service.")
class PostV1ActivityMeetingIdIntegrationRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="Integration configuration object. Submitting an empty object will not perform any action. The structure depends on the third-party service being integrated.")
class PostV1ActivityMeetingIdIntegrationRequest(StrictModel):
    """Create a new third-party meeting integration or update an existing one for a specific meeting activity. This operation is only available to OAuth applications; API key authentication will result in an error."""
    path: PostV1ActivityMeetingIdIntegrationRequestPath
    body: PostV1ActivityMeetingIdIntegrationRequestBody

# Operation: list_activity_notes
class GetV1ActivityNoteRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return per request. Must be at least 1.", ge=1)
class GetV1ActivityNoteRequest(StrictModel):
    """Retrieve a list of Note activities with optional pagination. Use this to view all notes or filter results by applying additional query parameters."""
    query: GetV1ActivityNoteRequestQuery | None = None

# Operation: create_note
class PostV1ActivityNoteRequestBody(StrictModel):
    attachments: list[PostV1ActivityNoteBodyAttachmentsItem] | None = Field(default=None, description="Array of attachments to include with the note. Each attachment object should contain a URL from the Files API, filename, and content type. Attachments are displayed in the order provided.")
    pinned: bool | None = Field(default=None, description="Set to true to pin this note, making it appear at the top of the activity feed for easy reference.")
class PostV1ActivityNoteRequest(StrictModel):
    """Create a new Note activity with optional rich-text content, attachments, and pinning. Rich HTML content takes precedence over plain text if both are provided."""
    body: PostV1ActivityNoteRequestBody | None = None

# Operation: get_activity_note
class GetV1ActivityNoteIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Note activity to retrieve.")
class GetV1ActivityNoteIdRequest(StrictModel):
    """Retrieve a single Note activity by its unique identifier. Use this to fetch detailed information about a specific note entry."""
    path: GetV1ActivityNoteIdRequestPath

# Operation: update_note
class PutV1ActivityNoteIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the note activity to update.")
class PutV1ActivityNoteIdRequestBody(StrictModel):
    attachments: list[dict[str, Any]] | None = Field(default=None, description="List of attachment objects to associate with the note. Attachments are processed in the order provided.")
    pinned: bool | None = Field(default=None, description="Set to true to pin the note for visibility, or false to unpin it.")
class PutV1ActivityNoteIdRequest(StrictModel):
    """Update an existing note activity, including its content, attachments, and pin status. You can modify the note text, add or remove attachments, and pin or unpin the note."""
    path: PutV1ActivityNoteIdRequestPath
    body: PutV1ActivityNoteIdRequestBody | None = None

# Operation: delete_activity_note
class DeleteV1ActivityNoteIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Note activity to delete.")
class DeleteV1ActivityNoteIdRequest(StrictModel):
    """Permanently delete a Note activity by its ID. This action cannot be undone."""
    path: DeleteV1ActivityNoteIdRequestPath

# Operation: list_opportunity_status_changes
class GetV1ActivityStatusChangeOpportunityRequestQuery(StrictModel):
    opportunity_id: str | None = Field(default=None, description="Filter results to show status changes for a specific opportunity by its ID.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Limit the number of status change records returned in the response.")
class GetV1ActivityStatusChangeOpportunityRequest(StrictModel):
    """Retrieve a list of opportunity status change activities with optional filtering by opportunity ID and result limits."""
    query: GetV1ActivityStatusChangeOpportunityRequestQuery | None = None

# Operation: log_opportunity_status_change
class PostV1ActivityStatusChangeOpportunityRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The status change event details including the opportunity identifier, previous status, new status, and any additional context about the change.")
class PostV1ActivityStatusChangeOpportunityRequest(StrictModel):
    """Log a historical opportunity status change event in the activity feed. This operation records a status change event without modifying the actual opportunity status, and is intended for importing historical status changes from external systems or organizations."""
    body: PostV1ActivityStatusChangeOpportunityRequestBody

# Operation: get_opportunity_status_change
class GetV1ActivityStatusChangeOpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the opportunity status change activity record to retrieve.")
class GetV1ActivityStatusChangeOpportunityIdRequest(StrictModel):
    """Retrieve a single opportunity status change activity by its ID. Use this to fetch details about when and how an opportunity's status was modified."""
    path: GetV1ActivityStatusChangeOpportunityIdRequestPath

# Operation: delete_opportunity_status_change
class DeleteV1ActivityStatusChangeOpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the OpportunityStatusChange activity to delete.")
class DeleteV1ActivityStatusChangeOpportunityIdRequest(StrictModel):
    """Remove an OpportunityStatusChange activity from the activity feed. This deletion only removes the status change event record and does not affect the actual opportunity status; use this only when the status change event is irrelevant or causing integration issues with external systems."""
    path: DeleteV1ActivityStatusChangeOpportunityIdRequestPath

# Operation: list_sms_activities
class GetV1ActivitySmsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of SMS activity records to return in the response. Limits the result set size for pagination or performance optimization.")
class GetV1ActivitySmsRequest(StrictModel):
    """Retrieve a list of SMS activities with optional filtering. Includes MMS messages (SMS with attachments) where attachments contain URLs, filenames, sizes, content types, and optional thumbnails accessible via authenticated S3 URLs."""
    query: GetV1ActivitySmsRequestQuery | None = None

# Operation: create_sms_activity
class PostV1ActivitySmsRequestQuery(StrictModel):
    send_to_inbox: bool | None = Field(default=None, description="When creating an SMS with inbox status, set to true to automatically generate a corresponding Inbox Notification for the SMS.")
class PostV1ActivitySmsRequestBody(StrictModel):
    status: Literal["inbox", "draft", "scheduled", "outbox", "sent"] = Field(default=..., description="The current status of the SMS activity. Use inbox to log a received SMS, draft to create an editable SMS, scheduled to send at a future date/time, outbox to send immediately, or sent to log an already-sent SMS.")
    local_phone: str | None = Field(default=None, description="The phone number to send the SMS from. Must be associated with a Phone Number configured as type internal. Required unless using a template_id.")
    template_id: str | None = Field(default=None, description="The ID of an SMS template to use instead of providing raw text content.")
    direction: Literal["inbound", "outbound"] | None = Field(default=None, description="The direction of the SMS flow. Defaults to inbound when status is inbox, otherwise defaults to outbound.")
class PostV1ActivitySmsRequest(StrictModel):
    """Create an SMS activity with various statuses (inbox, draft, scheduled, outbox, or sent) to log, draft, schedule, or send SMS messages. Only draft SMS activities can be modified after creation."""
    query: PostV1ActivitySmsRequestQuery | None = None
    body: PostV1ActivitySmsRequestBody

# Operation: get_sms_activity
class GetV1ActivitySmsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS activity record to retrieve.")
class GetV1ActivitySmsIdRequest(StrictModel):
    """Retrieve details of a specific SMS activity by its unique identifier. Use this to fetch information about a single SMS message or communication event."""
    path: GetV1ActivitySmsIdRequestPath

# Operation: update_sms_activity
class PutV1ActivitySmsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS activity to update.")
class PutV1ActivitySmsIdRequest(StrictModel):
    """Update an SMS activity to modify draft content or change its send status. Use this to send immediately by setting status to outbox, or schedule for later by setting status to scheduled with a date_scheduled value."""
    path: PutV1ActivitySmsIdRequestPath

# Operation: delete_sms_activity
class DeleteV1ActivitySmsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS activity to delete.")
class DeleteV1ActivitySmsIdRequest(StrictModel):
    """Permanently delete a specific SMS activity record by its ID. This action cannot be undone."""
    path: DeleteV1ActivitySmsIdRequestPath

# Operation: list_completed_tasks
class GetV1ActivityTaskCompletedRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return in the response. Must be at least 1.", ge=1)
class GetV1ActivityTaskCompletedRequest(StrictModel):
    """Retrieve a list of task completion activities. Task completed activities are generated when a task is marked as finished on a lead record."""
    query: GetV1ActivityTaskCompletedRequestQuery | None = None

# Operation: get_completed_task
class GetV1ActivityTaskCompletedIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the completed task activity to retrieve.")
class GetV1ActivityTaskCompletedIdRequest(StrictModel):
    """Retrieve details of a specific completed task activity by its unique identifier."""
    path: GetV1ActivityTaskCompletedIdRequestPath

# Operation: delete_completed_task
class DeleteV1ActivityTaskCompletedIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the TaskCompleted activity to delete.")
class DeleteV1ActivityTaskCompletedIdRequest(StrictModel):
    """Remove a completed task activity from the system. This permanently deletes the TaskCompleted activity record identified by the provided ID."""
    path: DeleteV1ActivityTaskCompletedIdRequestPath

# Operation: list_lead_merges
class GetV1ActivityLeadMergeRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of LeadMerge activities to return in the response. Useful for pagination or controlling result set size.")
class GetV1ActivityLeadMergeRequest(StrictModel):
    """Retrieve a list of LeadMerge activities, which are automatically created when one lead is merged into another. Use optional filtering to limit the number of results returned."""
    query: GetV1ActivityLeadMergeRequestQuery | None = None

# Operation: get_lead_merge
class GetV1ActivityLeadMergeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the LeadMerge activity record to retrieve.")
class GetV1ActivityLeadMergeIdRequest(StrictModel):
    """Retrieve a specific LeadMerge activity record by its unique identifier. Use this to fetch details about a lead merge operation."""
    path: GetV1ActivityLeadMergeIdRequestPath

# Operation: list_whatsapp_messages
class GetV1ActivityWhatsappMessageRequestQuery(StrictModel):
    external_whatsapp_message_id: str | None = Field(default=None, description="Filter results to a specific WhatsApp message by its external message ID. Useful for locating a particular message in Close that corresponds to a WhatsApp message ID.")
class GetV1ActivityWhatsappMessageRequest(StrictModel):
    """Retrieve WhatsApp message activities from Close, with optional filtering by external WhatsApp message ID. Use this to sync message data between WhatsApp and Close, or to locate specific messages for updates or deletion."""
    query: GetV1ActivityWhatsappMessageRequestQuery | None = None

# Operation: create_whatsapp_message
class PostV1ActivityWhatsappMessageRequestQuery(StrictModel):
    send_to_inbox: bool | None = Field(default=None, description="When the message direction is set to 'incoming', set this to true to automatically create a corresponding Inbox Notification for the message.")
class PostV1ActivityWhatsappMessageRequestBody(StrictModel):
    external_whatsapp_message_id: str = Field(default=..., description="The unique identifier of the message as assigned by WhatsApp. This is required to link the activity to the original message.")
    message_markdown: str = Field(default=..., description="The message content formatted using WhatsApp Markdown syntax. This is the body text that will be displayed in the activity.")
    attachments: list[PostV1ActivityWhatsappMessageBodyAttachmentsItem] | None = Field(default=None, description="An optional array of file attachments previously uploaded via the Files API. Each attachment should include its URL, filename, and content type. The combined size of all attachments cannot exceed 25MB.")
    integration_link: str | None = Field(default=None, description="An optional URL provided by the integration partner that links back to this message in the external WhatsApp system, enabling cross-system navigation.")
    response_to_id: str | None = Field(default=None, description="The Close activity ID of another WhatsApp message activity that this message is replying to, establishing a conversation thread.")
class PostV1ActivityWhatsappMessageRequest(StrictModel):
    """Create a new WhatsApp message activity in Close. The message must reference a valid WhatsApp message ID and include the message body in WhatsApp Markdown format. Any attachments must be pre-uploaded via the Files API and cannot exceed 25MB in total size."""
    query: PostV1ActivityWhatsappMessageRequestQuery | None = None
    body: PostV1ActivityWhatsappMessageRequestBody

# Operation: get_whatsapp_message
class GetV1ActivityWhatsappMessageIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the WhatsApp message activity to retrieve.")
class GetV1ActivityWhatsappMessageIdRequest(StrictModel):
    """Retrieve a specific WhatsApp message activity by its unique identifier. Use this to fetch details about a single WhatsApp message interaction."""
    path: GetV1ActivityWhatsappMessageIdRequestPath

# Operation: update_whatsapp_message
class PutV1ActivityWhatsappMessageIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the WhatsApp message activity to update.")
class PutV1ActivityWhatsappMessageIdRequestBody(StrictModel):
    message_markdown: str | None = Field(default=None, description="The message body formatted using WhatsApp Markdown syntax for text styling and formatting.")
    attachments: list[dict[str, Any]] | None = Field(default=None, description="An ordered array of file or media attachments to include with the message. Each attachment should specify its file reference or media identifier.")
class PutV1ActivityWhatsappMessageIdRequest(StrictModel):
    """Update an existing WhatsApp message activity, including its text content and any attached files or media."""
    path: PutV1ActivityWhatsappMessageIdRequestPath
    body: PutV1ActivityWhatsappMessageIdRequestBody | None = None

# Operation: delete_whatsapp_message
class DeleteV1ActivityWhatsappMessageIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the WhatsApp message activity to delete.")
class DeleteV1ActivityWhatsappMessageIdRequest(StrictModel):
    """Delete a WhatsApp message activity record. This removes the activity log entry for a specific WhatsApp message interaction."""
    path: DeleteV1ActivityWhatsappMessageIdRequestPath

# Operation: list_form_submissions
class GetV1ActivityFormSubmissionRequestQuery(StrictModel):
    organization_id: str | None = Field(default=None, description="Filter results to a specific organization. Only activities belonging to this organization will be returned.")
    form_id__in: list[str] | None = Field(default=None, description="Filter results to one or more specific forms by providing their IDs. Only submissions from the specified forms will be included in the results.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return. Use this to control pagination and response size.")
class GetV1ActivityFormSubmissionRequest(StrictModel):
    """Retrieve a list of form submission activities, with support for filtering by organization and specific forms. Use standard activity filtering parameters along with form-specific filters to narrow results."""
    query: GetV1ActivityFormSubmissionRequestQuery | None = None

# Operation: get_form_submission
class GetV1ActivityFormSubmissionIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form submission activity to retrieve.")
class GetV1ActivityFormSubmissionIdRequest(StrictModel):
    """Retrieve a specific form submission activity by its unique identifier. Use this to access details about a completed or in-progress form submission."""
    path: GetV1ActivityFormSubmissionIdRequestPath

# Operation: delete_form_submission
class DeleteV1ActivityFormSubmissionIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the FormSubmission activity to delete.")
class DeleteV1ActivityFormSubmissionIdRequest(StrictModel):
    """Permanently delete a FormSubmission activity record. This action cannot be undone."""
    path: DeleteV1ActivityFormSubmissionIdRequestPath

# Operation: list_opportunities
class GetV1OpportunityRequestQuery(StrictModel):
    status_type: Literal["active", "won", "lost"] | None = Field(default=None, description="Filter opportunities by status. Use active for ongoing deals, won for closed-won, or lost for closed-lost. Multiple statuses can be specified together.")
    date_created__lte: str | None = Field(default=None, description="Filter opportunities created on or before this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date_created__gte: str | None = Field(default=None, description="Filter opportunities created on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date_updated__lte: str | None = Field(default=None, description="Filter opportunities last updated on or before this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date_updated__gte: str | None = Field(default=None, description="Filter opportunities last updated on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date_won__lte: str | None = Field(default=None, description="Filter opportunities won on or before this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date_won__gte: str | None = Field(default=None, description="Filter opportunities won on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    value_period: Literal["one_time", "monthly", "annual"] | None = Field(default=None, description="Filter opportunities by revenue period type: one_time for single payments, monthly for recurring monthly revenue, or annual for recurring annual revenue. Multiple periods can be specified together.")
    order_by: str | None = Field(default=None, validation_alias="_order_by", serialization_alias="_order_by", description="Sort results by a specific field in ascending order, or prepend a minus sign for descending order. Sortable fields include date_won, date_updated, date_created, confidence, user_name, value, annualized_value, and annualized_expected_value.")
    group_by: str | None = Field(default=None, validation_alias="_group_by", serialization_alias="_group_by", description="Group results by a dimension such as user_id or time-based periods (week, month, quarter, or year based on date_won). Grouping aggregates metrics across matching opportunities.")
    lead_saved_search_id: str | None = Field(default=None, description="Filter opportunities by a saved lead search (Smart View) ID to narrow results to leads matching that view.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return. If not specified, all matching opportunities are returned.")
class GetV1OpportunityRequest(StrictModel):
    """Retrieve and filter opportunities with optional filtering by lead, user, status, and dates. Returns aggregated metrics for all matching opportunities."""
    query: GetV1OpportunityRequestQuery | None = None

# Operation: get_opportunity
class GetV1OpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the opportunity to retrieve.")
class GetV1OpportunityIdRequest(StrictModel):
    """Retrieve a single opportunity by its unique identifier. Use this to fetch detailed information about a specific opportunity."""
    path: GetV1OpportunityIdRequestPath

# Operation: update_opportunity
class PutV1OpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the opportunity to update.")
class PutV1OpportunityIdRequestBody(StrictModel):
    date_won: str | None = Field(default=None, description="The date when the opportunity was won, specified in ISO 8601 date-time format. If omitted and the opportunity status is set to won, this will be automatically set to the current date.", json_schema_extra={'format': 'date-time'})
class PutV1OpportunityIdRequest(StrictModel):
    """Update an opportunity's details. Automatically sets the win date to today if the opportunity status is changed to won and no win date is explicitly provided."""
    path: PutV1OpportunityIdRequestPath
    body: PutV1OpportunityIdRequestBody | None = None

# Operation: delete_opportunity
class DeleteV1OpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the opportunity to delete.")
class DeleteV1OpportunityIdRequest(StrictModel):
    """Permanently delete an opportunity from the system by its ID. This action cannot be undone."""
    path: DeleteV1OpportunityIdRequestPath

# Operation: list_tasks
class GetV1TaskRequestQuery(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Filter results to a specific task by its unique identifier.")
    date__lt: str | None = Field(default=None, description="Return only tasks with a due date before the specified date and time (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date__gt: str | None = Field(default=None, description="Return only tasks with a due date after the specified date and time (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date__lte: str | None = Field(default=None, description="Return only tasks with a due date on or before the specified date and time (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date__gte: str | None = Field(default=None, description="Return only tasks with a due date on or after the specified date and time (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date_created__lte: str | None = Field(default=None, description="Return only tasks created on or before the specified date and time (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date_created__gte: str | None = Field(default=None, description="Return only tasks created on or after the specified date and time (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    view: Literal["inbox", "future", "archive"] | None = Field(default=None, description="Use a predefined view to quickly access common task categories: 'inbox' for incomplete tasks through end of day, 'future' for incomplete tasks starting tomorrow, or 'archive' for completed tasks only.")
    order_by: str | None = Field(default=None, validation_alias="_order_by", serialization_alias="_order_by", description="Sort results by 'date' (due date) or 'date_created' (creation date). Prepend a minus sign for descending order (e.g., '-date' for newest first).")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return. Must be at least 1.", ge=1)
class GetV1TaskRequest(StrictModel):
    """Retrieve and filter tasks with flexible viewing options. Use convenience views (inbox, future, archive) for quick access to common task categories, or apply custom date-based filters and sorting."""
    query: GetV1TaskRequestQuery | None = None

# Operation: create_task
class PostV1TaskRequestBody(StrictModel):
    type_: Literal["lead", "outgoing_call"] = Field(default=..., validation_alias="_type", serialization_alias="_type", description="The category of task to create. Choose 'lead' for lead-related tasks or 'outgoing_call' for call tracking tasks.")
class PostV1TaskRequest(StrictModel):
    """Create a new task in the system. Supports task types for lead management and outgoing call tracking."""
    body: PostV1TaskRequestBody

# Operation: bulk_update_tasks
class PutV1TaskRequestBody(StrictModel):
    is_complete: bool | None = Field(default=None, description="Mark the task as complete or incomplete.")
    assigned_to: str | None = Field(default=None, description="The user ID to assign the task to.")
    date: str | None = Field(default=None, description="The task date in ISO 8601 format, either as a date only (YYYY-MM-DD) or as a full timestamp with timezone information.", json_schema_extra={'format': 'date-time'})
class PutV1TaskRequest(StrictModel):
    """Update multiple tasks at once by applying changes to tasks matching specified filter criteria. Supports bulk modifications of completion status, task assignment, and task dates."""
    body: PutV1TaskRequestBody | None = None

# Operation: get_task
class GetV1TaskIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the task to retrieve.")
class GetV1TaskIdRequest(StrictModel):
    """Retrieve detailed information about a specific task, including its current status, metadata, and associated data."""
    path: GetV1TaskIdRequestPath

# Operation: update_task
class PutV1TaskIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the task to update.")
class PutV1TaskIdRequestBody(StrictModel):
    date: str | None = Field(default=None, description="The task date in either date-only format (YYYY-MM-DD) or ISO 8601 date-time format with timezone information.", json_schema_extra={'format': 'date-time'})
class PutV1TaskIdRequest(StrictModel):
    """Update an existing task by ID. You can modify the assignee, date, and completion status on any task. For lead-type tasks, you can also update the task text."""
    path: PutV1TaskIdRequestPath
    body: PutV1TaskIdRequestBody | None = None

# Operation: delete_task
class DeleteV1TaskIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the task to delete.")
class DeleteV1TaskIdRequest(StrictModel):
    """Permanently delete a task by its ID. This action cannot be undone."""
    path: DeleteV1TaskIdRequestPath

# Operation: create_outcome
class PostV1OutcomeRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for this outcome. This is what users will see when viewing or assigning outcomes.")
    applies_to: list[Literal["calls", "meetings"]] = Field(default=..., description="An array specifying which object types this outcome can be assigned to. Each item defines a valid target for this outcome.")
    description: str | None = Field(default=None, description="An optional explanation of what this outcome represents and the circumstances under which it should be used.")
class PostV1OutcomeRequest(StrictModel):
    """Create a new outcome for your organization. Outcomes define measurable results that can be assigned to specific object types to track progress and success."""
    body: PostV1OutcomeRequestBody

# Operation: get_outcome
class GetV1OutcomeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the outcome to retrieve.")
class GetV1OutcomeIdRequest(StrictModel):
    """Retrieve a specific outcome by its unique identifier. Use this to fetch detailed information about a single outcome."""
    path: GetV1OutcomeIdRequestPath

# Operation: update_outcome
class PutV1OutcomeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the outcome to update.")
class PutV1OutcomeIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the outcome.")
    description: str | None = Field(default=None, description="The new description providing details about the outcome.")
    applies_to: list[Literal["calls", "meetings"]] | None = Field(default=None, description="An updated list of objects or entities that this outcome applies to, specified as an array of objects.")
class PutV1OutcomeIdRequest(StrictModel):
    """Update an existing outcome by modifying its name, description, applicable scope, or type classification."""
    path: PutV1OutcomeIdRequestPath
    body: PutV1OutcomeIdRequestBody | None = None

# Operation: delete_outcome
class DeleteV1OutcomeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the outcome to delete.")
class DeleteV1OutcomeIdRequest(StrictModel):
    """Delete an existing outcome. Associated calls and meetings will retain their outcome references, but the outcome will no longer be available for assignment to new calls and meetings."""
    path: DeleteV1OutcomeIdRequestPath

# Operation: update_membership
class PutV1MembershipIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the membership to update.")
class PutV1MembershipIdRequestBody(StrictModel):
    role_id: Literal["admin", "superuser", "user", "restricteduser"] | None = Field(default=None, description="The role to assign to this membership. Can be a predefined role ('admin', 'superuser', 'user', or 'restricteduser') or a custom Role ID.")
    auto_record_calls: Literal["unset", "disabled", "enabled"] | None = Field(default=None, description="Controls automatic call recording behavior. Set to 'enabled' to record calls automatically, 'disabled' to prevent automatic recording, or 'unset' to use default settings.")
class PutV1MembershipIdRequest(StrictModel):
    """Update a membership's role and automatic call recording settings. Allows modification of user permissions through role assignment and control over whether calls are automatically recorded."""
    path: PutV1MembershipIdRequestPath
    body: PutV1MembershipIdRequestBody | None = None

# Operation: provision_membership
class PostV1MembershipRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address of the user to provision. Must be a valid email format.", json_schema_extra={'format': 'email'})
    role_id: Literal["admin", "superuser", "user", "restricteduser"] = Field(default=..., description="The role to assign to the user. Use one of the predefined roles ('admin', 'superuser', 'user', 'restricteduser') or provide a custom Role ID.")
class PostV1MembershipRequest(StrictModel):
    """Provision or activate a membership for a user by email address. Creates a new user if they don't exist, or adds an existing user to your organization with the specified role. Requires 'Manage Organization' permissions and OAuth authentication."""
    body: PostV1MembershipRequestBody

# Operation: bulk_update_memberships
class PutV1MembershipRequestQuery(StrictModel):
    id__in: str = Field(default=..., description="Comma-separated list of membership IDs to update. All specified memberships will receive the same updates.")
class PutV1MembershipRequestBody(StrictModel):
    role_id: Literal["admin", "superuser", "user", "restricteduser"] | None = Field(default=None, description="Role to assign to the memberships. Can be a specific role ID or one of the predefined roles: admin, superuser, user, or restricteduser.")
    auto_record_calls: Literal["unset", "disabled", "enabled"] | None = Field(default=None, description="Automatic call recording setting for the memberships. Choose unset to clear the setting, disabled to turn off recording, or enabled to turn on recording.")
class PutV1MembershipRequest(StrictModel):
    """Update multiple memberships in bulk with the same settings. Apply role assignments or call recording preferences across multiple membership IDs simultaneously."""
    query: PutV1MembershipRequestQuery
    body: PutV1MembershipRequestBody | None = None

# Operation: list_pinned_views
class GetV1MembershipIdPinnedViewsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the membership whose pinned views should be retrieved.")
class GetV1MembershipIdPinnedViewsRequest(StrictModel):
    """Retrieve the ordered list of pinned views for a specific membership. Pinned views are displayed in a user-defined sequence for quick access."""
    path: GetV1MembershipIdPinnedViewsRequestPath

# Operation: set_membership_pinned_views
class PutV1MembershipIdPinnedViewsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the membership whose pinned views should be updated.")
class PutV1MembershipIdPinnedViewsRequestBody(StrictModel):
    body: list[dict[str, Any]] = Field(default=..., description="An ordered array of view identifiers to pin for this membership. The order determines the display sequence, and providing this list will completely replace any existing pinned views.")
class PutV1MembershipIdPinnedViewsRequest(StrictModel):
    """Update the pinned views for a membership by providing an ordered list that completely replaces the current pinned views configuration."""
    path: PutV1MembershipIdPinnedViewsRequestPath
    body: PutV1MembershipIdPinnedViewsRequestBody

# Operation: get_user
class GetV1UserIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the user to retrieve.")
class GetV1UserIdRequest(StrictModel):
    """Retrieve a single user by their unique identifier. Returns the complete user profile for the specified ID."""
    path: GetV1UserIdRequestPath

# Operation: list_users
class GetV1UserRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of user records to return in the response. Use this to control pagination and response size.")
class GetV1UserRequest(StrictModel):
    """Retrieve all users who are members of your organizations. This returns a filtered list based on your organization memberships."""
    query: GetV1UserRequestQuery | None = None

# Operation: list_user_availability
class GetV1UserAvailabilityRequestQuery(StrictModel):
    organization_id: str | None = Field(default=None, description="Filter the availability results to a specific organization. If not provided, returns availability for all accessible users.")
class GetV1UserAvailabilityRequest(StrictModel):
    """Retrieve the current availability status of all users in an organization, including details about any active calls they are participating in."""
    query: GetV1UserAvailabilityRequestQuery | None = None

# Operation: get_organization
class GetV1OrganizationIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the organization to retrieve.")
class GetV1OrganizationIdRequest(StrictModel):
    """Retrieve detailed information about an organization, including its current members, inactive members, and configured lead and opportunity statuses. By default, membership data includes user information with a user_ prefix; use the _expand parameter to nest full user objects instead."""
    path: GetV1OrganizationIdRequestPath

# Operation: update_organization
class PutV1OrganizationIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the organization to update.")
class PutV1OrganizationIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the organization. If provided, replaces the current organization name.")
    currency: str | None = Field(default=None, description="The currency code for the organization (e.g., USD, EUR, GBP). If provided, updates the organization's default currency.")
    lead_statuses: list[dict[str, Any]] | None = Field(default=None, description="An ordered array of lead status identifiers to reorder how statuses appear in the organization. The order in this array determines the sequence of lead statuses.")
class PutV1OrganizationIdRequest(StrictModel):
    """Update an organization's profile including its name, currency, and the ordering of lead statuses. Changes are applied immediately to the organization."""
    path: PutV1OrganizationIdRequestPath
    body: PutV1OrganizationIdRequestBody | None = None

# Operation: get_role
class GetV1RoleIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the role to retrieve.")
class GetV1RoleIdRequest(StrictModel):
    """Retrieve a specific role by its unique identifier. Use this to fetch detailed information about a single role."""
    path: GetV1RoleIdRequestPath

# Operation: create_role
class PostV1RoleRequestBody(StrictModel):
    visibility_user_lcf_behavior: Literal["require_assignment", "allow_unassigned"] | None = Field(default=None, description="Controls lead visibility behavior for unassigned leads when the role does not have view_all_leads permission. Choose 'require_assignment' to restrict visibility to assigned leads only, or 'allow_unassigned' to permit access to leads without assigned users. Leave empty if the role has view_all_leads permission.")
class PostV1RoleRequest(StrictModel):
    """Create a new role with configurable lead visibility settings. Use this to define a new role and specify how users with this role can access leads that lack assigned users."""
    body: PostV1RoleRequestBody | None = None

# Operation: update_role
class PutV1RoleRoleIdRequestPath(StrictModel):
    role_id: str = Field(default=..., description="The unique identifier of the role to update.")
class PutV1RoleRoleIdRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The role configuration object containing the properties to update, such as name, description, permissions, and other role attributes.")
class PutV1RoleRoleIdRequest(StrictModel):
    """Update an existing role with new configuration and properties. Specify the role to modify using its ID and provide the updated role details in the request body."""
    path: PutV1RoleRoleIdRequestPath
    body: PutV1RoleRoleIdRequestBody

# Operation: delete_role
class DeleteV1RoleRoleIdRequestPath(StrictModel):
    role_id: str = Field(default=..., description="The unique identifier of the role to delete.")
class DeleteV1RoleRoleIdRequest(StrictModel):
    """Permanently delete a role from the system. Ensure all users assigned to this role are reassigned to a different role before deletion, as roles cannot be deleted while users are still associated with them."""
    path: DeleteV1RoleRoleIdRequestPath

# Operation: create_lead_status
class PostV1StatusLeadRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the lead status. This name will appear in lead management interfaces and status selection dropdowns.")
class PostV1StatusLeadRequest(StrictModel):
    """Create a new custom status that can be assigned to leads in your pipeline. This allows you to define custom workflow stages beyond default statuses."""
    body: PostV1StatusLeadRequestBody

# Operation: rename_lead_status
class PutV1StatusLeadStatusIdRequestPath(StrictModel):
    status_id: str = Field(default=..., description="The unique identifier of the lead status to rename.")
class PutV1StatusLeadStatusIdRequestBody(StrictModel):
    name: str = Field(default=..., description="The new display name for the lead status.")
class PutV1StatusLeadStatusIdRequest(StrictModel):
    """Rename an existing lead status. This updates the display name of a status category used to organize leads in your pipeline."""
    path: PutV1StatusLeadStatusIdRequestPath
    body: PutV1StatusLeadStatusIdRequestBody

# Operation: delete_lead_status
class DeleteV1StatusLeadStatusIdRequestPath(StrictModel):
    status_id: str = Field(default=..., description="The unique identifier of the lead status to delete.")
class DeleteV1StatusLeadStatusIdRequest(StrictModel):
    """Delete a lead status from your system. Ensure no leads are currently assigned this status before deletion, as the operation will fail if the status is in use."""
    path: DeleteV1StatusLeadStatusIdRequestPath

# Operation: create_opportunity_status
class PostV1StatusOpportunityRequestBody(StrictModel):
    label: str = Field(default=..., description="The display name for this opportunity status.")
    status_type: Literal["active", "won", "lost"] = Field(default=..., description="The category of this status: active for ongoing opportunities, won for successfully closed deals, or lost for unsuccessful deals.")
    pipeline_id: str | None = Field(default=None, description="Optional pipeline identifier to create this status within a specific pipeline. If omitted, the status is created at the account level.")
class PostV1StatusOpportunityRequest(StrictModel):
    """Create a new opportunity status for tracking deal progression. Statuses can be classified as active (ongoing), won (closed successfully), or lost (closed unsuccessfully), and can optionally be scoped to a specific pipeline."""
    body: PostV1StatusOpportunityRequestBody

# Operation: rename_opportunity_status
class PutV1StatusOpportunityStatusIdRequestPath(StrictModel):
    status_id: str = Field(default=..., description="The unique identifier of the opportunity status to rename.")
class PutV1StatusOpportunityStatusIdRequestBody(StrictModel):
    label: str = Field(default=..., description="The new display label for the opportunity status.")
class PutV1StatusOpportunityStatusIdRequest(StrictModel):
    """Rename an existing opportunity status by providing its ID and the new label. This updates the display name of the status in your opportunity pipeline."""
    path: PutV1StatusOpportunityStatusIdRequestPath
    body: PutV1StatusOpportunityStatusIdRequestBody

# Operation: delete_opportunity_status
class DeleteV1StatusOpportunityStatusIdRequestPath(StrictModel):
    status_id: str = Field(default=..., description="The unique identifier of the opportunity status to delete.")
class DeleteV1StatusOpportunityStatusIdRequest(StrictModel):
    """Delete an opportunity status from the system. Ensure no opportunities are currently assigned this status before deletion."""
    path: DeleteV1StatusOpportunityStatusIdRequestPath

# Operation: create_pipeline
class PostV1PipelineRequestBody(StrictModel):
    name: str = Field(default=..., description="The name identifier for the pipeline. Used to reference and organize the pipeline within your workspace.")
class PostV1PipelineRequest(StrictModel):
    """Create a new pipeline with the specified name. Pipelines serve as containers for organizing and executing workflows."""
    body: PostV1PipelineRequestBody

# Operation: update_pipeline
class PutV1PipelinePipelineIdRequestPath(StrictModel):
    pipeline_id: str = Field(default=..., description="The unique identifier of the pipeline to update.")
class PutV1PipelinePipelineIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the pipeline. Provide a descriptive name to identify the pipeline.")
    statuses: list[PutV1PipelinePipelineIdBodyStatusesItem] | None = Field(default=None, description="An ordered array of opportunity statuses for this pipeline. Each status should include its ID; to move a status from another pipeline, include an object with the status ID from the source pipeline. The order of statuses in the array determines their display sequence.")
class PutV1PipelinePipelineIdRequest(StrictModel):
    """Update an existing pipeline by modifying its name, reordering opportunity statuses, or moving statuses from other pipelines into this one."""
    path: PutV1PipelinePipelineIdRequestPath
    body: PutV1PipelinePipelineIdRequestBody | None = None

# Operation: delete_pipeline
class DeleteV1PipelinePipelineIdRequestPath(StrictModel):
    pipeline_id: str = Field(default=..., description="The unique identifier of the pipeline to delete.")
class DeleteV1PipelinePipelineIdRequest(StrictModel):
    """Delete a pipeline from your workspace. The pipeline must be empty of all opportunity statuses before deletion—migrate or remove any existing opportunity statuses first."""
    path: DeleteV1PipelinePipelineIdRequestPath

# Operation: list_groups
class GetV1GroupRequestQuery(StrictModel):
    fields: str = Field(default=..., validation_alias="_fields", serialization_alias="_fields", description="Comma-separated list of fields to include in the response. Must include at least 'name' and 'members' to retrieve group information.")
class GetV1GroupRequest(StrictModel):
    """Retrieve all groups in your organization. Use this endpoint for a complete group listing; for detailed member information, query individual groups separately."""
    query: GetV1GroupRequestQuery

# Operation: create_group
class PostV1GroupRequestQuery(StrictModel):
    fields: str = Field(default=..., validation_alias="_fields", serialization_alias="_fields", description="Comma-separated list of fields to include in the response. Must include at least 'name' and 'members'.")
class PostV1GroupRequestBody(StrictModel):
    name: str = Field(default=..., description="The name of the group to create.")
class PostV1GroupRequest(StrictModel):
    """Create a new empty group. Use the member endpoint to add or remove users from the group after creation."""
    query: PostV1GroupRequestQuery
    body: PostV1GroupRequestBody

# Operation: get_group
class GetV1GroupGroupIdRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group to retrieve.")
class GetV1GroupGroupIdRequestQuery(StrictModel):
    fields: str = Field(default=..., validation_alias="_fields", serialization_alias="_fields", description="Comma-separated list of fields to include in the response. Must include at least 'name' and 'members' to retrieve group details and membership information.")
class GetV1GroupGroupIdRequest(StrictModel):
    """Retrieve a specific group by its ID, including group name and member information."""
    path: GetV1GroupGroupIdRequestPath
    query: GetV1GroupGroupIdRequestQuery

# Operation: update_group
class PutV1GroupGroupIdRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group to update.")
class PutV1GroupGroupIdRequestQuery(StrictModel):
    fields: str = Field(default=..., validation_alias="_fields", serialization_alias="_fields", description="Comma-separated list of fields to include in the response. Must include at least 'name' and 'members' to retrieve the updated group information.")
class PutV1GroupGroupIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the group. Must be unique across all groups in the system.")
class PutV1GroupGroupIdRequest(StrictModel):
    """Update an existing group's properties, such as renaming it. Group names must be unique within the system."""
    path: PutV1GroupGroupIdRequestPath
    query: PutV1GroupGroupIdRequestQuery
    body: PutV1GroupGroupIdRequestBody | None = None

# Operation: delete_group
class DeleteV1GroupGroupIdRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group to delete.")
class DeleteV1GroupGroupIdRequest(StrictModel):
    """Delete a group from the system. This operation is only permitted if the group is not currently referenced by any saved reports or smart views."""
    path: DeleteV1GroupGroupIdRequestPath

# Operation: add_user_to_group
class PostV1GroupGroupIdMemberRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group to which the user will be added.")
class PostV1GroupGroupIdMemberRequestBody(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to add to the group.")
class PostV1GroupGroupIdMemberRequest(StrictModel):
    """Add a user to a group. If the user is already a member, the operation completes without making changes."""
    path: PostV1GroupGroupIdMemberRequestPath
    body: PostV1GroupGroupIdMemberRequestBody

# Operation: remove_group_member
class DeleteV1GroupGroupIdMemberUserIdRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group from which the user will be removed.")
    user_id: str = Field(default=..., description="The unique identifier of the user to remove from the group.")
class DeleteV1GroupGroupIdMemberUserIdRequest(StrictModel):
    """Remove a user from a group. If the user is not a member of the group, the operation completes without error."""
    path: DeleteV1GroupGroupIdMemberUserIdRequestPath

# Operation: generate_activity_report
class PostV1ReportActivityRequestBodyQuery(StrictModel):
    saved_search_id: str | None = Field(default=None, validation_alias="saved_search_id", serialization_alias="saved_search_id", description="The ID of a saved search to apply as a filter for the report results.")
class PostV1ReportActivityRequestBody(StrictModel):
    relative_range: Literal["today", "this-week", "this-month", "this-quarter", "this-year", "yesterday", "last-week", "last-month", "last-quarter", "last-year", "all-time"] | None = Field(default=None, description="A relative time range for the report data. Choose from predefined ranges like 'today', 'this-week', 'this-month', or 'all-time'. Either this or a specific datetime range must be provided.")
    type_: Literal["overview", "comparison"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The report format: 'overview' for organization-wide metrics by time period, or 'comparison' for metrics broken down by individual users.")
    users: list[str] | None = Field(default=None, description="A list of user IDs to filter the report to specific users. When provided, the report will only include data for these users.")
    metrics: list[str] = Field(default=..., description="A list of metric names to include in the report. Specify which metrics you want calculated and returned in the results.")
    query: PostV1ReportActivityRequestBodyQuery | None = None
class PostV1ReportActivityRequest(StrictModel):
    """Generate an activity report showing organizational metrics aggregated by time period (overview) or broken down by user (comparison). Specify the time range and metrics to include in the report."""
    body: PostV1ReportActivityRequestBody

# Operation: list_sent_emails_report
class GetV1ReportSentEmailsOrganizationIdRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization for which to retrieve the sent emails report.")
class GetV1ReportSentEmailsOrganizationIdRequestQuery(StrictModel):
    date_start: str | None = Field(default=None, description="The start date for filtering the report results, specified in date format (YYYY-MM-DD). If provided, only emails sent on or after this date will be included.", json_schema_extra={'format': 'date'})
    date_end: str | None = Field(default=None, description="The end date for filtering the report results, specified in date format (YYYY-MM-DD). If provided, only emails sent on or before this date will be included.", json_schema_extra={'format': 'date'})
class GetV1ReportSentEmailsOrganizationIdRequest(StrictModel):
    """Retrieve a report of sent emails grouped by template for an organization, optionally filtered by a date range."""
    path: GetV1ReportSentEmailsOrganizationIdRequestPath
    query: GetV1ReportSentEmailsOrganizationIdRequestQuery | None = None

# Operation: get_lead_status_report
class GetV1ReportStatusesLeadOrganizationIdRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier for the organization whose lead status changes should be reported.")
class GetV1ReportStatusesLeadOrganizationIdRequestQuery(StrictModel):
    date_start: str | None = Field(default=None, description="The start date for the report period in date format. If omitted, the report begins from the earliest available data.", json_schema_extra={'format': 'date'})
    date_end: str | None = Field(default=None, description="The end date for the report period in date format. If omitted, the report extends to the most recent data.", json_schema_extra={'format': 'date'})
class GetV1ReportStatusesLeadOrganizationIdRequest(StrictModel):
    """Retrieve a report of lead status changes for an organization, optionally filtered by a specific date range. If no dates are specified, the report covers all historical data."""
    path: GetV1ReportStatusesLeadOrganizationIdRequestPath
    query: GetV1ReportStatusesLeadOrganizationIdRequestQuery | None = None

# Operation: get_opportunity_status_report
class GetV1ReportStatusesOpportunityOrganizationIdRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier for the organization whose opportunity status changes should be reported.")
class GetV1ReportStatusesOpportunityOrganizationIdRequestQuery(StrictModel):
    date_start: str | None = Field(default=None, description="The start date for the reporting period in date format (YYYY-MM-DD). Only status changes on or after this date will be included.", json_schema_extra={'format': 'date'})
    date_end: str | None = Field(default=None, description="The end date for the reporting period in date format (YYYY-MM-DD). Only status changes on or before this date will be included.", json_schema_extra={'format': 'date'})
    smart_view_id: str | None = Field(default=None, description="Filter the report to include only opportunities within a specific smart view, identified by its unique ID.")
class GetV1ReportStatusesOpportunityOrganizationIdRequest(StrictModel):
    """Retrieve a status change report for opportunities within an organization, showing how opportunities transitioned between different statuses over a specified time period. Results can be filtered by smart view to focus on specific opportunity subsets."""
    path: GetV1ReportStatusesOpportunityOrganizationIdRequestPath
    query: GetV1ReportStatusesOpportunityOrganizationIdRequestQuery | None = None

# Operation: generate_custom_report
class GetV1ReportCustomOrganizationIdRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier for the organization whose data will be included in the report.")
class GetV1ReportCustomOrganizationIdRequestQuery(StrictModel):
    y: str | None = Field(default=None, description="The metric to display on the Y axis, such as lead.count, call.duration, or opportunity.value. Defaults to lead.count if not specified.")
    x: str | None = Field(default=None, description="The field to display on the X axis, such as lead.custom.MRR or opportunity.date_created. Can be time-based or numeric.")
    interval: str | None = Field(default=None, description="The granularity for bucketing data. For time-based X axes, use auto, hour, day, week, month, quarter, or year. For numeric X axes, specify an integer interval. Defaults to auto.")
    group_by: str | None = Field(default=None, description="Optional field name to segment the report data into separate series or groups.")
    transform_y: Literal["sum", "avg", "min", "max"] | None = Field(default=None, description="The aggregation function applied to Y-axis values. Choose from sum, avg, min, or max. Defaults to sum.")
    start: str | None = Field(default=None, description="The start of the X-axis range as a date or integer value. For dates, defaults to your organization's creation date if not provided.")
    end: str | None = Field(default=None, description="The end of the X-axis range as a date or integer value. For dates, defaults to the current date and time if not provided.")
class GetV1ReportCustomOrganizationIdRequest(StrictModel):
    """Generate a custom analytics report for any Close object with flexible metrics, grouping, and time-based or numeric axis configuration. Powers the Explorer visualization in the UI."""
    path: GetV1ReportCustomOrganizationIdRequestPath
    query: GetV1ReportCustomOrganizationIdRequestQuery | None = None

# Operation: get_funnel_opportunity_totals
class PostV1ReportFunnelOpportunityTotalsRequestBodyQuery(StrictModel):
    type_: Literal["saved_search"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The query type for filtering opportunities; use 'saved_search' to apply a predefined search filter.")
    saved_search_id: str | None = Field(default=None, validation_alias="saved_search_id", serialization_alias="saved_search_id", description="The ID of a saved search to apply as a filter when query.type is set to 'saved_search'.")
class PostV1ReportFunnelOpportunityTotalsRequestBody(StrictModel):
    pipeline: str = Field(default=..., description="The pipeline ID that defines the funnel stages used to categorize opportunities.")
    type_: Literal["created-cohort", "active-stage-cohort"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The report type determining how opportunities are grouped: either by creation cohort or by their current active stage.")
    report_datetime_range: dict[str, Any] | None = Field(default=None, description="The time range for which to fetch report data, specified as a date range object.")
    cohort_datetime_range: dict[str, Any] | None = Field(default=None, description="The time range defining which opportunities to include in the cohort, specified as a date range object.")
    compared_custom_range: dict[str, Any] | None = Field(default=None, description="An optional time range for fetching comparison data to analyze trends across different periods.")
    users: list[str] | None = Field(default=None, description="A list of user IDs or group IDs to limit report results to specific team members or groups.")
    query: PostV1ReportFunnelOpportunityTotalsRequestBodyQuery | None = None
class PostV1ReportFunnelOpportunityTotalsRequest(StrictModel):
    """Retrieve aggregated pipeline funnel metrics for opportunities, with support for cohort analysis and optional per-user breakdowns. Results can be filtered by time ranges, saved searches, and specific users or groups."""
    body: PostV1ReportFunnelOpportunityTotalsRequestBody

# Operation: get_opportunity_funnel_stages_report
class PostV1ReportFunnelOpportunityStagesRequestBodyQuery(StrictModel):
    type_: Literal["saved_search"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Optional query type; when set to 'saved_search', applies a saved search filter to the report data.")
    saved_search_id: str | None = Field(default=None, validation_alias="saved_search_id", serialization_alias="saved_search_id", description="The ID of a saved search to apply as a filter; used when query.type is set to 'saved_search'.")
class PostV1ReportFunnelOpportunityStagesRequestBody(StrictModel):
    pipeline: str = Field(default=..., description="The pipeline ID that defines the funnel stages to report on.")
    type_: Literal["created-cohort", "active-stage-cohort"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The report type: either 'created-cohort' to analyze opportunities by creation date, or 'active-stage-cohort' to analyze opportunities by their current stage.")
    report_datetime_range: dict[str, Any] | None = Field(default=None, description="Optional time range for fetching the report data. Specify as a date range object to limit results to a specific period.")
    cohort_datetime_range: dict[str, Any] | None = Field(default=None, description="Optional time range defining which opportunities to include in the cohort based on their creation date.")
    compared_custom_range: dict[str, Any] | None = Field(default=None, description="Optional time range for fetching comparison data to analyze trends or changes over different periods.")
    users: list[str] | None = Field(default=None, description="Optional list of user IDs or group IDs to segment the report results by specific team members or groups.")
    query: PostV1ReportFunnelOpportunityStagesRequestBodyQuery | None = None
class PostV1ReportFunnelOpportunityStagesRequest(StrictModel):
    """Generate a funnel report analyzing pipeline stage metrics for opportunities. Returns aggregated metrics in JSON format, with optional per-user breakdowns available in JSON or CSV formats."""
    body: PostV1ReportFunnelOpportunityStagesRequestBody

# Operation: list_email_templates
class GetV1EmailTemplateRequestQuery(StrictModel):
    is_archived: bool | None = Field(default=None, description="Filter results to show only archived templates (true), only active templates (false), or all templates regardless of status (omit parameter). Useful for managing template lifecycle.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Limit the number of results returned in a single response. Must be at least 1. Use pagination to retrieve large template collections efficiently.", ge=1)
class GetV1EmailTemplateRequest(StrictModel):
    """Retrieve all email templates with optional filtering by archive status and pagination support. Use this to browse available templates for sending or management purposes."""
    query: GetV1EmailTemplateRequestQuery | None = None

# Operation: create_email_template
class PostV1EmailTemplateRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="Email template configuration object containing template name, subject, body content, and any variable placeholders for dynamic content insertion.")
class PostV1EmailTemplateRequest(StrictModel):
    """Create a new email template that can be used for sending emails. Define the template structure, content, and variables for reuse across email communications."""
    body: PostV1EmailTemplateRequestBody

# Operation: get_email_template
class GetV1EmailTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email template to retrieve.")
class GetV1EmailTemplateIdRequest(StrictModel):
    """Retrieve a specific email template by its unique identifier. Use this to fetch template details for viewing or further processing."""
    path: GetV1EmailTemplateIdRequestPath

# Operation: update_email_template
class PutV1EmailTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email template to update.")
class PutV1EmailTemplateIdRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The email template data to update, including fields such as subject, body, variables, and other template configuration.")
class PutV1EmailTemplateIdRequest(StrictModel):
    """Update an existing email template with new content, settings, or configuration. Specify the template ID and provide the updated template data in the request body."""
    path: PutV1EmailTemplateIdRequestPath
    body: PutV1EmailTemplateIdRequestBody

# Operation: delete_email_template
class DeleteV1EmailTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email template to delete.")
class DeleteV1EmailTemplateIdRequest(StrictModel):
    """Permanently delete an email template by its ID. This action cannot be undone."""
    path: DeleteV1EmailTemplateIdRequestPath

# Operation: render_email_template
class GetV1EmailTemplateIdRenderRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email template to render.")
class GetV1EmailTemplateIdRenderRequestQuery(StrictModel):
    mode: Literal["lead", "contact"] | None = Field(default=None, description="Specifies which contact data to use for rendering: 'lead' renders the first contact associated with the lead (default), or 'contact' to render a specific contact by index.")
class GetV1EmailTemplateIdRenderRequest(StrictModel):
    """Render an email template with actual data from a lead or contact to preview the final formatted output. Use this to see how the template will appear before sending."""
    path: GetV1EmailTemplateIdRenderRequestPath
    query: GetV1EmailTemplateIdRenderRequestQuery | None = None

# Operation: list_sms_templates
class GetV1SmsTemplateRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of SMS templates to return in the response. Useful for pagination or controlling result set size.")
class GetV1SmsTemplateRequest(StrictModel):
    """Retrieve a list of SMS templates available in your account. Use the limit parameter to control the number of results returned."""
    query: GetV1SmsTemplateRequestQuery | None = None

# Operation: create_sms_template
class PostV1SmsTemplateRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="Template configuration object containing the SMS template details such as name, content, and any variable placeholders for dynamic content.")
class PostV1SmsTemplateRequest(StrictModel):
    """Create a new SMS template that can be used for sending templated SMS messages. Define the template content and configuration for reuse across multiple SMS campaigns."""
    body: PostV1SmsTemplateRequestBody

# Operation: get_sms_template
class GetV1SmsTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS template to retrieve.")
class GetV1SmsTemplateIdRequest(StrictModel):
    """Retrieve a specific SMS template by its unique identifier. Use this to fetch template details for viewing or further processing."""
    path: GetV1SmsTemplateIdRequestPath

# Operation: update_sms_template
class PutV1SmsTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS template to update.")
class PutV1SmsTemplateIdRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The updated SMS template configuration and content.")
class PutV1SmsTemplateIdRequest(StrictModel):
    """Update an existing SMS template by ID. Modify the template content and configuration to reflect your current messaging needs."""
    path: PutV1SmsTemplateIdRequestPath
    body: PutV1SmsTemplateIdRequestBody

# Operation: delete_sms_template
class DeleteV1SmsTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS template to delete.")
class DeleteV1SmsTemplateIdRequest(StrictModel):
    """Permanently delete an SMS template by its ID. This action cannot be undone."""
    path: DeleteV1SmsTemplateIdRequestPath

# Operation: get_connected_account
class GetV1ConnectedAccountIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the connected account to retrieve.")
class GetV1ConnectedAccountIdRequest(StrictModel):
    """Retrieve details for a specific connected account by its unique identifier. Use this to fetch account information such as authentication status, configuration, and metadata."""
    path: GetV1ConnectedAccountIdRequestPath

# Operation: list_send_as_associations
class GetV1SendAsRequestQuery(StrictModel):
    allowing_user_id: str | None = Field(default=None, description="Filter associations by the user ID who is granting Send As permission. Must be your own user ID if provided.")
    allowed_user_id: str | None = Field(default=None, description="Filter associations by the user ID who is receiving Send As permission. Must be your own user ID if provided.")
class GetV1SendAsRequest(StrictModel):
    """Retrieve all Send As associations for the authenticated user. You can filter by either the user granting permission (allowing_user_id) or the user receiving permission (allowed_user_id), and at least one must match your user ID."""
    query: GetV1SendAsRequestQuery | None = None

# Operation: create_send_as_association
class PostV1SendAsRequestBody(StrictModel):
    allowing_user_id: str = Field(default=..., description="Your user ID that will grant send-as permission to another user. This must match your own user ID.")
    allowed_user_id: str = Field(default=..., description="The user ID of the person who will be granted permission to send messages as the allowing user.")
class PostV1SendAsRequest(StrictModel):
    """Grant another user permission to send messages on your behalf by creating a Send As Association. The allowing_user_id must match your own user ID."""
    body: PostV1SendAsRequestBody

# Operation: revoke_send_as_permission
class DeleteV1SendAsRequestQuery(StrictModel):
    allowing_user_id: str = Field(default=..., description="The user ID of the person who granted send-as permission. This must match your own user ID.")
    allowed_user_id: str = Field(default=..., description="The user ID of the person whose send-as permission is being revoked.")
class DeleteV1SendAsRequest(StrictModel):
    """Revoke a user's permission to send emails on behalf of another user. Both the authorizing user and the authorized user must be specified to remove the association."""
    query: DeleteV1SendAsRequestQuery

# Operation: get_send_as
class GetV1SendAsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Send As Association to retrieve.")
class GetV1SendAsIdRequest(StrictModel):
    """Retrieve a single Send As Association by its unique identifier. Use this to fetch details about a specific email sending configuration."""
    path: GetV1SendAsIdRequestPath

# Operation: delete_send_as
class DeleteV1SendAsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Send As Association to delete.")
class DeleteV1SendAsIdRequest(StrictModel):
    """Remove a Send As Association by its ID, preventing further use of that sender identity."""
    path: DeleteV1SendAsIdRequestPath

# Operation: update_send_as_permissions_bulk
class PostV1SendAsBulkRequestBody(StrictModel):
    allow: list[str] | None = Field(default=None, description="List of user IDs to grant Send As permission to. These users will be able to send messages as you.")
    disallow: list[str] | None = Field(default=None, description="List of user IDs to revoke Send As permission from. These users will no longer be able to send messages as you.")
class PostV1SendAsBulkRequest(StrictModel):
    """Manage multiple Send As permissions in a single request by granting or revoking the ability for other users to send messages on your behalf. Returns all current Send As associations after the update is complete."""
    body: PostV1SendAsBulkRequestBody | None = None

# Operation: list_sequences
class GetV1SequenceRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of sequences to return in a single request. Useful for controlling response size and implementing pagination.")
class GetV1SequenceRequest(StrictModel):
    """Retrieve a paginated list of all sequences. Use the limit parameter to control the maximum number of results returned."""
    query: GetV1SequenceRequestQuery | None = None

# Operation: create_sequence
class PostV1SequenceRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The sequence configuration object containing all required properties to define the new sequence.")
class PostV1SequenceRequest(StrictModel):
    """Create a new sequence with the specified configuration. This operation initializes a sequence resource that can be used for ordered processing or workflow management."""
    body: PostV1SequenceRequestBody

# Operation: get_sequence
class GetV1SequenceIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the sequence to retrieve.")
class GetV1SequenceIdRequest(StrictModel):
    """Retrieve a specific sequence by its unique identifier. Use this operation to fetch detailed information about a sequence."""
    path: GetV1SequenceIdRequestPath

# Operation: update_sequence
class PutV1SequenceIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the sequence to update.")
class PutV1SequenceIdRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The sequence configuration object containing the fields to update, including an optional steps array that defines the sequence's workflow steps.")
class PutV1SequenceIdRequest(StrictModel):
    """Update an existing sequence by modifying its configuration. Any steps included in the request will replace the sequence's current steps; steps not included will be removed."""
    path: PutV1SequenceIdRequestPath
    body: PutV1SequenceIdRequestBody

# Operation: delete_sequence
class DeleteV1SequenceIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the sequence to delete.")
class DeleteV1SequenceIdRequest(StrictModel):
    """Permanently delete a sequence by its ID. This action cannot be undone."""
    path: DeleteV1SequenceIdRequestPath

# Operation: list_sequence_subscriptions
class GetV1SequenceSubscriptionRequestQuery(StrictModel):
    sequence_id: str | None = Field(default=None, description="Filter results to show subscriptions for a specific sequence. Use the sequence's unique identifier.")
class GetV1SequenceSubscriptionRequest(StrictModel):
    """Retrieve a list of sequence subscriptions filtered by sequence, contact, or lead. At least one filter parameter is required to execute this operation."""
    query: GetV1SequenceSubscriptionRequestQuery | None = None

# Operation: subscribe_contact_to_sequence
class PostV1SequenceSubscriptionRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The subscription details including the contact identifier and sequence to subscribe them to. This object should contain the necessary identifiers and configuration for the sequence subscription.")
class PostV1SequenceSubscriptionRequest(StrictModel):
    """Subscribe a contact to an automation sequence. This creates a new sequence subscription that will trigger the contact to receive the sequence's automated messages and actions."""
    body: PostV1SequenceSubscriptionRequestBody

# Operation: get_sequence_subscription
class GetV1SequenceSubscriptionIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the sequence subscription to retrieve.")
class GetV1SequenceSubscriptionIdRequest(StrictModel):
    """Retrieve a specific sequence subscription by its unique identifier. Use this to fetch details about an individual sequence subscription."""
    path: GetV1SequenceSubscriptionIdRequestPath

# Operation: update_sequence_subscription
class PutV1SequenceSubscriptionIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the sequence subscription to update.")
class PutV1SequenceSubscriptionIdRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The subscription data to update. Include the fields you want to modify in the request body.")
class PutV1SequenceSubscriptionIdRequest(StrictModel):
    """Update an existing sequence subscription with new configuration or settings. Modify subscription parameters such as status, frequency, or other subscription-specific properties."""
    path: PutV1SequenceSubscriptionIdRequestPath
    body: PutV1SequenceSubscriptionIdRequestBody

# Operation: list_dialer_sessions
class GetV1DialerRequestQuery(StrictModel):
    source_value: str | None = Field(default=None, description="Filter results by the source identifier, which can be either a Smart View ID or Shared Entry ID depending on the source type.")
    source_type: Literal["saved-search", "shared-entry"] | None = Field(default=None, description="Filter results by source type. Must be either 'saved-search' for Smart View sources or 'shared-entry' for Shared Entry sources.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of dialer sessions to return in the response. Use this to control result set size.")
class GetV1DialerRequest(StrictModel):
    """Retrieve and filter dialer sessions with details about their source, type, and associated users. Use optional filters to narrow results by source value or type."""
    query: GetV1DialerRequestQuery | None = None

# Operation: get_dialer_session
class GetV1DialerIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dialer session to retrieve.")
class GetV1DialerIdRequest(StrictModel):
    """Retrieve details of a specific dialer session by its unique identifier. Use this to fetch current status, configuration, and activity information for an active or completed dialing session."""
    path: GetV1DialerIdRequestPath

# Operation: create_smart_view
class PostV1SavedSearchRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the Smart View. This is the label users will see when accessing their saved views.")
    query: dict[str, Any] = Field(default=..., description="A filter query object that defines which records appear in the Smart View. Must include an object_type clause specifying either 'Lead' or 'Contact' to determine the record type being filtered.")
class PostV1SavedSearchRequest(StrictModel):
    """Create a new Smart View for organizing and filtering Leads or Contacts. Smart Views use advanced filtering queries to automatically group records based on specified criteria."""
    body: PostV1SavedSearchRequestBody

# Operation: get_smart_view
class GetV1SavedSearchIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Smart View to retrieve.")
class GetV1SavedSearchIdRequest(StrictModel):
    """Retrieve a specific Smart View by its unique identifier. Use this to fetch detailed information about a saved search view."""
    path: GetV1SavedSearchIdRequestPath

# Operation: update_smart_view
class PutV1SavedSearchIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Smart View to update.")
class PutV1SavedSearchIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the Smart View. Provide a descriptive name to help identify this saved search.")
class PutV1SavedSearchIdRequest(StrictModel):
    """Update an existing Smart View by modifying its name or other properties. Use the Smart View ID to identify which view to update."""
    path: PutV1SavedSearchIdRequestPath
    body: PutV1SavedSearchIdRequestBody | None = None

# Operation: delete_smart_view
class DeleteV1SavedSearchIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Smart View to delete.")
class DeleteV1SavedSearchIdRequest(StrictModel):
    """Delete a Smart View by its unique identifier. This operation permanently removes the saved search and cannot be undone."""
    path: DeleteV1SavedSearchIdRequestPath

# Operation: send_bulk_email
class PostV1BulkActionEmailRequestBody(StrictModel):
    s_query: dict[str, Any] = Field(default=..., description="Structured query object defining which leads to target, using the same filtering syntax as the Advanced Filtering API.")
    results_limit: int | None = Field(default=None, description="Maximum number of leads to include in this bulk email action. If not specified, all matching leads will be affected.")
    sort: list[dict[str, Any]] | None = Field(default=None, description="Sort order for the leads, specified as an array of sort criteria. Order matters and determines which leads are prioritized when results_limit is applied.")
    contact_preference: Literal["lead", "contact"] | None = Field(default=None, description="Determines email recipient scope: 'lead' sends to only the primary contact email of each lead, while 'contact' sends to the first contact email of each contact associated with the lead.")
    send_done_email: bool | None = Field(default=None, description="Whether to send a confirmation email upon completion of the bulk email action. Enabled by default.")
class PostV1BulkActionEmailRequest(StrictModel):
    """Send bulk emails to leads matching specified criteria. Choose whether to email the primary lead contact or all contacts associated with each lead."""
    body: PostV1BulkActionEmailRequestBody

# Operation: get_bulk_email
class GetV1BulkActionEmailIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk email action to retrieve.")
class GetV1BulkActionEmailIdRequest(StrictModel):
    """Retrieve details of a specific bulk email action by its ID. Returns the complete configuration and status information for the bulk email operation."""
    path: GetV1BulkActionEmailIdRequestPath

# Operation: bulk_subscribe_sequence
class PostV1BulkActionSequenceSubscriptionRequestBody(StrictModel):
    s_query: dict[str, Any] = Field(default=..., description="Structured query object that defines which leads or contacts to affect. Uses the same query format as the Advanced Filtering API to specify filtering, matching, and selection criteria.")
    results_limit: int | None = Field(default=None, description="Maximum number of leads to process in this bulk action. If not specified, all matching leads will be affected.")
    sort: list[dict[str, Any]] | None = Field(default=None, description="Sort order for the results. Specify as an array of sort criteria to control which leads are prioritized when a results_limit is applied.")
    action_type: Literal["subscribe", "resume", "resume_finished", "pause"] = Field(default=..., description="The subscription action to perform: 'subscribe' to add leads to a sequence, 'resume' to restart paused sequences, 'resume_finished' to restart completed sequences, or 'pause' to pause active sequences.")
    sequence_id: str | None = Field(default=None, description="The ID of the sequence to subscribe leads to. Required when action_type is 'subscribe'.")
    sender_account_id: str | None = Field(default=None, description="The account ID of the sender who will be associated with the sequence. Required when action_type is 'subscribe'.")
    contact_preference: Literal["lead", "contact"] | None = Field(default=None, description="Subscription scope: 'lead' to subscribe only the primary/first contact email, or 'contact' to subscribe the primary email of each contact in the lead record. Required when action_type is 'subscribe'.")
    sender_name: dict | None = Field(default=None, description="Sender name (required if action_type is 'subscribe')")
    sender_email: str | None = Field(default=None, description="Sender email (required if action_type is 'subscribe')", json_schema_extra={'format': 'email'})
class PostV1BulkActionSequenceSubscriptionRequest(StrictModel):
    """Bulk subscribe, resume, or pause contacts in a sequence. Use this operation to perform subscription actions on multiple leads or contacts matching your query criteria, such as subscribing them to a new sequence, resuming paused sequences, or pausing active sequences."""
    body: PostV1BulkActionSequenceSubscriptionRequestBody

# Operation: get_bulk_sequence_subscription
class GetV1BulkActionSequenceSubscriptionIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk sequence subscription action to retrieve.")
class GetV1BulkActionSequenceSubscriptionIdRequest(StrictModel):
    """Retrieve details of a specific bulk sequence subscription, including its configuration and status."""
    path: GetV1BulkActionSequenceSubscriptionIdRequestPath

# Operation: delete_leads_bulk
class PostV1BulkActionDeleteRequestBody(StrictModel):
    s_query: dict[str, Any] = Field(default=..., description="Structured query object defining which leads to delete, using the same format as the Advanced Filtering API query field.")
    results_limit: int | None = Field(default=None, description="Maximum number of leads to delete in this operation; if not specified, all matching leads will be affected.")
    sort: list[dict[str, Any]] | None = Field(default=None, description="Sort specification to order results before deletion; order matters and determines which leads are affected when combined with results_limit.")
    send_done_email: bool | None = Field(default=None, description="Whether to send a confirmation email upon completion; defaults to true if not specified.")
class PostV1BulkActionDeleteRequest(StrictModel):
    """Initiate a bulk delete operation to remove multiple leads matching specified criteria. Optionally receive a confirmation email when the operation completes."""
    body: PostV1BulkActionDeleteRequestBody

# Operation: get_bulk_delete_action
class GetV1BulkActionDeleteIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk delete action to retrieve.")
class GetV1BulkActionDeleteIdRequest(StrictModel):
    """Retrieve details of a specific bulk delete action, including its status, progress, and configuration."""
    path: GetV1BulkActionDeleteIdRequestPath

# Operation: bulk_edit_leads
class PostV1BulkActionEditRequestBody(StrictModel):
    s_query: dict[str, Any] = Field(default=..., description="Structured query object that defines which leads to target, using the same format as the Advanced Filtering API.")
    results_limit: int | None = Field(default=None, description="Maximum number of leads to affect with this bulk edit action. If not specified, all matching leads will be updated.")
    sort: list[dict[str, Any]] | None = Field(default=None, description="Sort specification to order the leads before applying the bulk edit. Specify as an array of sort criteria.")
    type_: Literal["set_lead_status", "clear_custom_field", "set_custom_field"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of bulk edit to perform: 'set_lead_status' to change lead status, 'clear_custom_field' to remove a custom field value, or 'set_custom_field' to update a custom field value.")
    lead_status_id: str | None = Field(default=None, description="The ID of the Lead Status to assign. Required when type is 'set_lead_status'.")
    custom_field_name: str | None = Field(default=None, description="The name of the custom field to modify. Required when type is 'clear_custom_field' or 'set_custom_field', unless you provide custom_field_id instead.")
    custom_field_values: list[Any] | None = Field(default=None, description="Array of values to set for custom fields that support multiple values. Use with 'set_custom_field' type.")
    custom_field_operation: Literal["replace", "add", "remove"] | None = Field(default=None, description="How to apply values to multi-value custom fields: 'replace' to overwrite existing values, 'add' to append new values, or 'remove' to delete specific values. Defaults to 'replace'.")
    send_done_email: bool | None = Field(default=None, description="Whether to send a confirmation email when the bulk edit completes. Defaults to true; set to false to skip the notification.")
class PostV1BulkActionEditRequest(StrictModel):
    """Initiate a bulk edit action on leads matching your query criteria. Choose from updating lead status, clearing a custom field, or setting custom field values across multiple leads."""
    body: PostV1BulkActionEditRequestBody

# Operation: get_bulk_edit
class GetV1BulkActionEditIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk edit action to retrieve.")
class GetV1BulkActionEditIdRequest(StrictModel):
    """Retrieve the details and status of a specific bulk edit action by its ID."""
    path: GetV1BulkActionEditIdRequestPath

# Operation: create_integration_link
class PostV1IntegrationLinkRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for this integration link, shown as clickable link text to users.")
    url: str = Field(default=..., description="The URL template that defines where this integration link directs to. Use this to specify dynamic routing based on the integration type.")
    type_: Literal["lead", "contact", "opportunity"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The entity type this integration link applies to. Must be one of: lead, contact, or opportunity.")
class PostV1IntegrationLinkRequest(StrictModel):
    """Create a new integration link for your organization. This operation is restricted to organization administrators only."""
    body: PostV1IntegrationLinkRequestBody

# Operation: get_integration_link
class GetV1IntegrationLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the integration link to retrieve.")
class GetV1IntegrationLinkIdRequest(StrictModel):
    """Retrieve a specific integration link by its unique identifier. Use this to fetch details about a configured integration connection."""
    path: GetV1IntegrationLinkIdRequestPath

# Operation: update_integration_link
class PutV1IntegrationLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the integration link to update.")
class PutV1IntegrationLinkIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The text displayed as the clickable link in the user interface.")
    url: str | None = Field(default=None, description="The URL template that defines the target destination, supporting dynamic variable substitution.")
class PutV1IntegrationLinkIdRequest(StrictModel):
    """Update an existing integration link's display name and URL template. Requires organization admin privileges."""
    path: PutV1IntegrationLinkIdRequestPath
    body: PutV1IntegrationLinkIdRequestBody | None = None

# Operation: delete_integration_link
class DeleteV1IntegrationLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the integration link to delete.")
class DeleteV1IntegrationLinkIdRequest(StrictModel):
    """Delete an integration link from your organization. This action is restricted to organization administrators only."""
    path: DeleteV1IntegrationLinkIdRequestPath

# Operation: export_records
class PostV1ExportLeadRequestQuery(StrictModel):
    s_query: str | None = Field(default=None, description="Advanced search query to filter which records to export. Uses the Advanced Filtering API syntax to narrow results.")
    results_limit: int | None = Field(default=None, description="Maximum number of records to include in the export. Limits the result set size.")
    sort: str | None = Field(default=None, description="Field and direction to sort results by. Uses the Advanced Filtering API syntax (e.g., field name with optional sort order).")
    format_: Literal["csv", "json"] = Field(default=..., validation_alias="format", serialization_alias="format", description="Output file format for the export. Choose between CSV or JSON.")
    type_: Literal["leads", "contacts", "lead_opps"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Category of records to export: leads, contacts, or opportunities associated with leads.")
    date_format: Literal["original", "iso8601", "excel"] | None = Field(default=None, description="Date format for exported date fields in CSV exports. Choose original format, ISO 8601 standard, or Excel-compatible format. Only applies to CSV format.")
    fields: list[str] | None = Field(default=None, description="Specific fields to include in the export. If not specified, all available fields are included. Provide as a list of field names.")
    include_activities: bool | None = Field(default=None, description="Include activity records in the export. Only applies when exporting leads in JSON format.")
    include_smart_fields: bool | None = Field(default=None, description="Include smart fields (computed/derived fields) in the export. Supported for leads in JSON format or any record type in CSV format.")
    send_done_email: bool = Field(default=..., description="Send a confirmation email when the export completes. Set to false to skip the notification email.")
class PostV1ExportLeadRequest(StrictModel):
    """Export leads, contacts, or opportunities from Close as a compressed file. The export is processed asynchronously and delivered via email with a download link."""
    query: PostV1ExportLeadRequestQuery

# Operation: export_opportunities
class PostV1ExportOpportunityRequestQuery(StrictModel):
    params: dict[str, Any] | None = Field(default=None, description="Filter criteria to narrow down which opportunities to export, using the same filter parameters supported by the opportunities endpoint.")
    format_: Literal["csv", "json"] = Field(default=..., validation_alias="format", serialization_alias="format", description="File format for the exported data. Choose between CSV or JSON format.")
    date_format: Literal["original", "iso8601", "excel"] | None = Field(default=None, description="Date format for exported dates in CSV files only. Choose from original format, ISO 8601 standard format, or Excel-compatible format. Defaults to original format.")
    fields: list[str] | None = Field(default=None, description="Specific fields to include in the export. If not specified, all available fields are included in the export.")
    send_done_email: bool = Field(default=..., description="Whether to send a confirmation email when the export completes. Defaults to true; set to false to skip the notification email.")
class PostV1ExportOpportunityRequest(StrictModel):
    """Export opportunities from Close as a file in your chosen format, with optional filtering and field selection. Optionally receive a confirmation email when the export completes."""
    query: PostV1ExportOpportunityRequestQuery

# Operation: get_export
class GetV1ExportIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the export to retrieve.")
class GetV1ExportIdRequest(StrictModel):
    """Retrieve a single export by ID to check its current status or obtain a download URL for the exported data."""
    path: GetV1ExportIdRequestPath

# Operation: list_exports
class GetV1ExportRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of exports to return in the response. Useful for pagination or reducing payload size.")
class GetV1ExportRequest(StrictModel):
    """Retrieve a list of all exports. Use the limit parameter to control the number of results returned."""
    query: GetV1ExportRequestQuery | None = None

# Operation: list_phone_numbers
class GetV1PhoneNumberRequestQuery(StrictModel):
    number: str | None = Field(default=None, description="Filter results to phone numbers matching this specific number value.")
    is_group_number: bool | None = Field(default=None, description="Filter results by group number status—set to true to show only group numbers, false to show only individual numbers.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return in the response. Limits the result set size.")
class GetV1PhoneNumberRequest(StrictModel):
    """Retrieve a list of phone numbers in your organization, with optional filtering by number value or group status."""
    query: GetV1PhoneNumberRequestQuery | None = None

# Operation: get_phone_number
class GetV1PhoneNumberIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the phone number to retrieve.")
class GetV1PhoneNumberIdRequest(StrictModel):
    """Retrieve a single phone number by its ID. Use this operation to fetch detailed information about a specific phone number in your account."""
    path: GetV1PhoneNumberIdRequestPath

# Operation: update_phone_number
class PutV1PhoneNumberIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the phone number to update.")
class PutV1PhoneNumberIdRequestBody(StrictModel):
    label: str | None = Field(default=None, description="A descriptive label or name for this phone number.")
    forward_to: str | None = Field(default=None, description="The phone number to forward incoming calls to when call forwarding is enabled.")
    forward_to_enabled: bool | None = Field(default=None, description="Enable or disable call forwarding to the specified phone number.")
    voicemail_greeting_url: str | None = Field(default=None, description="HTTPS URL pointing to an MP3 file to use as the voicemail greeting message.", json_schema_extra={'format': 'uri'})
class PutV1PhoneNumberIdRequest(StrictModel):
    """Update phone number settings including label, call forwarding configuration, and voicemail greeting. Requires 'Manage Group Phone Numbers' permission for group numbers; personal numbers can only be updated by their owner."""
    path: PutV1PhoneNumberIdRequestPath
    body: PutV1PhoneNumberIdRequestBody | None = None

# Operation: delete_phone_number
class DeleteV1PhoneNumberIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the phone number to delete.")
class DeleteV1PhoneNumberIdRequest(StrictModel):
    """Delete a phone number from your account. Deleting group phone numbers requires the 'Manage Group Phone Numbers' permission, while personal numbers can only be deleted by their owner."""
    path: DeleteV1PhoneNumberIdRequestPath

# Operation: rent_phone_number
class PostV1PhoneNumberRequestInternalRequestBody(StrictModel):
    country: str = Field(default=..., description="Two-letter ISO country code indicating where the phone number should be rented (e.g., US, GB, DE).")
    sharing: Literal["personal", "group"] = Field(default=..., description="Determines whether the phone number is assigned to an individual user (personal) or shared across a group (group). Group numbers require 'Manage Group Phone Numbers' permission.")
    prefix: str | None = Field(default=None, description="Optional phone number prefix or area code, excluding the country code. Allows you to request a number from a specific region or area.")
    with_sms: bool | None = Field(default=None, description="Optional flag to request SMS capability for the phone number. Defaults based on country support if not specified.")
    with_mms: bool | None = Field(default=None, description="Optional flag to request MMS capability for the phone number. Defaults based on country support if not specified.")
class PostV1PhoneNumberRequestInternalRequest(StrictModel):
    """Rent an internal phone number for personal or group use. Renting a phone number incurs a cost and requires appropriate permissions for group numbers."""
    body: PostV1PhoneNumberRequestInternalRequestBody

# Operation: generate_file_upload_credentials
class PostV1FilesUploadRequestBody(StrictModel):
    filename: str = Field(default=..., description="The name of the file being uploaded, including its extension (e.g., image.jpg, document.pdf).")
    content_type: str = Field(default=..., description="The MIME type of the file being uploaded (e.g., image/jpeg, application/pdf, text/plain).")
class PostV1FilesUploadRequest(StrictModel):
    """Generate signed S3 upload credentials for storing a file. Returns a pre-signed upload URL, form fields for multipart upload, and a download URL for referencing the file in subsequent API calls."""
    body: PostV1FilesUploadRequestBody

# Operation: list_comment_threads
class GetV1CommentThreadRequestQuery(StrictModel):
    object_ids: list[str] | None = Field(default=None, description="Filter results to include only threads associated with specific object IDs. Provide as an array of object identifiers.")
    ids: list[str] | None = Field(default=None, description="Filter results to include only threads with specific thread IDs. Provide as an array of thread identifiers.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of comment threads to return in the response. Must be a positive integer.")
class GetV1CommentThreadRequest(StrictModel):
    """Retrieve multiple comment threads with optional filtering by the objects they reference or by specific thread identifiers."""
    query: GetV1CommentThreadRequestQuery | None = None

# Operation: get_comment_thread
class GetV1CommentThreadThreadIdRequestPath(StrictModel):
    thread_id: str = Field(default=..., description="The unique identifier of the comment thread to retrieve.")
class GetV1CommentThreadThreadIdRequest(StrictModel):
    """Retrieve a specific comment thread by its ID. Use this to fetch the full details and content of an individual discussion thread."""
    path: GetV1CommentThreadThreadIdRequestPath

# Operation: list_comments
class GetV1CommentRequestQuery(StrictModel):
    object_id: str | None = Field(default=None, description="Filter comments by the ID of the object that was commented on. Mutually exclusive with thread_id.")
    thread_id: str | None = Field(default=None, description="Filter comments by the ID of the discussion thread. Mutually exclusive with object_id.")
class GetV1CommentRequest(StrictModel):
    """Retrieve a list of comments filtered by either the object being commented on or the discussion thread. Provide exactly one filter to retrieve relevant comments."""
    query: GetV1CommentRequestQuery | None = None

# Operation: create_comment
class PostV1CommentRequestBody(StrictModel):
    object_type: str = Field(default=..., description="The type of object being commented on (e.g., task, document, issue). This determines where the comment will be attached.")
    object_id: str = Field(default=..., description="The unique identifier of the object being commented on. Must correspond to an existing object of the specified type.")
    body: str = Field(default=..., description="The comment text formatted as rich text. This is the content that will be displayed in the comment thread.")
class PostV1CommentRequest(StrictModel):
    """Create a comment on an object. If a comment thread already exists on that object, a new comment is added to the existing thread; otherwise, a new thread is created automatically."""
    body: PostV1CommentRequestBody

# Operation: get_comment
class GetV1CommentCommentIdRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to retrieve.")
class GetV1CommentCommentIdRequest(StrictModel):
    """Retrieve a specific comment by its unique identifier. Use this to fetch the full details of an individual comment."""
    path: GetV1CommentCommentIdRequestPath

# Operation: update_comment
class PutV1CommentCommentIdRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to update.")
class PutV1CommentCommentIdRequestBody(StrictModel):
    body: str = Field(default=..., description="The new comment content formatted as rich text.")
class PutV1CommentCommentIdRequest(StrictModel):
    """Edit the body of a comment. You can only update comments that you created."""
    path: PutV1CommentCommentIdRequestPath
    body: PutV1CommentCommentIdRequestBody

# Operation: delete_comment
class DeleteV1CommentCommentIdRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to delete.")
class DeleteV1CommentCommentIdRequest(StrictModel):
    """Remove a comment from a thread. The comment body is deleted but the comment object persists until all comments in the thread are removed, at which point the entire thread is deleted. Deletion permissions are based on the user's ability to delete their own or other users' activities."""
    path: DeleteV1CommentCommentIdRequestPath

# Operation: get_event
class GetV1EventIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event to retrieve.")
class GetV1EventIdRequest(StrictModel):
    """Retrieve a single event by its unique identifier. Returns event details in the standard event format."""
    path: GetV1EventIdRequestPath

# Operation: list_events
class GetV1EventRequestQuery(StrictModel):
    date_updated__lte: str | None = Field(default=None, description="Filter to events updated on or before this date and time (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date_updated__gte: str | None = Field(default=None, description="Filter to events updated on or after this date and time (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    object_type: str | None = Field(default=None, description="Filter to events for objects of a specific type (e.g., lead, contact, deal).")
    object_id: str | None = Field(default=None, description="Filter to events for a specific object by its ID. Only events directly related to this object are returned, excluding related object events.")
    action: str | None = Field(default=None, description="Filter to events of a specific action type (e.g., created, updated, deleted).")
    request_id: str | None = Field(default=None, description="Filter to events emitted during the processing of a specific API request.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of events to return per request. Must be between 1 and 50; defaults to 50.", ge=1, le=50)
class GetV1EventRequest(StrictModel):
    """Retrieve a paginated list of events from the event log, filtered by object type, action, timing, and other criteria. Events are always ordered by date with the latest first."""
    query: GetV1EventRequestQuery | None = None

# Operation: create_webhook
class PostV1WebhookRequestBody(StrictModel):
    url: str = Field(default=..., description="The destination URL where webhook events will be sent. Must be a valid URI (e.g., https://example.com/webhook).", json_schema_extra={'format': 'uri'})
    events: list[PostV1WebhookBodyEventsItem] = Field(default=..., description="List of events to subscribe to. Each event specifies an object_type and an action to monitor. Events are processed in the order provided.")
    verify_ssl: bool | None = Field(default=None, description="Whether to verify the SSL certificate of the destination webhook URL. Defaults to true for secure connections.")
class PostV1WebhookRequest(StrictModel):
    """Create a new webhook subscription to receive event notifications at a specified URL. The webhook will send POST requests for each subscribed event."""
    body: PostV1WebhookRequestBody

# Operation: get_webhook
class GetV1WebhookIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook subscription to retrieve.")
class GetV1WebhookIdRequest(StrictModel):
    """Retrieve the details of a specific webhook subscription, including its configuration and status."""
    path: GetV1WebhookIdRequestPath

# Operation: update_webhook
class PutV1WebhookIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook subscription to update.")
class PutV1WebhookIdRequestBody(StrictModel):
    url: str | None = Field(default=None, description="The destination URL where webhook events will be sent. Must be a valid URI format.", json_schema_extra={'format': 'uri'})
    events: list[PutV1WebhookIdBodyEventsItem] | None = Field(default=None, description="A list of events to subscribe to. Each event specifies an object type and an action to trigger the webhook notification.")
    verify_ssl: bool | None = Field(default=None, description="Whether to verify the SSL certificate when sending webhook requests to the destination URL. Enable for production environments to ensure secure connections.")
class PutV1WebhookIdRequest(StrictModel):
    """Update an existing webhook subscription with new configuration. Only provided parameters will be modified, allowing partial updates to the webhook's URL, subscribed events, or SSL verification settings."""
    path: PutV1WebhookIdRequestPath
    body: PutV1WebhookIdRequestBody | None = None

# Operation: delete_webhook
class DeleteV1WebhookIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook subscription to delete.")
class DeleteV1WebhookIdRequest(StrictModel):
    """Remove a webhook subscription to stop receiving event notifications at the configured endpoint."""
    path: DeleteV1WebhookIdRequestPath

# Operation: create_scheduling_link
class PostV1SchedulingLinkRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the scheduling link to help identify its purpose or audience.")
    url: str = Field(default=..., description="The external URL where the scheduling link points to, typically a calendar or booking platform URL.")
    description: str | None = Field(default=None, description="An optional description providing additional context or details about the scheduling link's purpose.")
class PostV1SchedulingLinkRequest(StrictModel):
    """Create a new scheduling link that can be shared with users to access your availability and book meetings. This generates a unique scheduling link with a custom name and optional description."""
    body: PostV1SchedulingLinkRequestBody

# Operation: get_scheduling_link
class GetV1SchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the scheduling link to retrieve.")
class GetV1SchedulingLinkIdRequest(StrictModel):
    """Retrieve a scheduling link by its unique identifier. Use this to fetch details about a specific user's scheduling link."""
    path: GetV1SchedulingLinkIdRequestPath

# Operation: update_scheduling_link
class PutV1SchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the scheduling link to update.")
class PutV1SchedulingLinkIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A display name for the scheduling link to help identify it.")
    url: str | None = Field(default=None, description="The external URL where the scheduling link is hosted or accessible.")
    description: str | None = Field(default=None, description="A detailed description explaining the purpose or details of the scheduling link.")
    source_id: str | None = Field(default=None, description="The identifier for this scheduling link at its source system or origin.")
    source_type: str | None = Field(default=None, description="A short descriptor categorizing the type or source of the scheduling link (e.g., 'calendly', 'acuity', 'custom').")
    duration_in_minutes: int | None = Field(default=None, description="The default duration in minutes for meetings scheduled through this link.")
class PutV1SchedulingLinkIdRequest(StrictModel):
    """Update an existing user scheduling link with new details such as name, URL, description, and meeting duration. This allows you to modify the properties of a scheduling link that users can access to book meetings."""
    path: PutV1SchedulingLinkIdRequestPath
    body: PutV1SchedulingLinkIdRequestBody | None = None

# Operation: delete_scheduling_link
class DeleteV1SchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the scheduling link to delete.")
class DeleteV1SchedulingLinkIdRequest(StrictModel):
    """Delete a scheduling link by its ID. This removes the user's scheduling link and makes it unavailable for scheduling."""
    path: DeleteV1SchedulingLinkIdRequestPath

# Operation: create_or_update_scheduling_link
class PostV1SchedulingLinkIntegrationRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Display name for the scheduling link.")
    url: str | None = Field(default=None, description="Public-facing URL where users can access the scheduling link.")
    description: str | None = Field(default=None, description="Additional details or context about the scheduling link's purpose.")
    source_id: str = Field(default=..., description="Unique identifier from your integrating application used to identify and deduplicate this scheduling link.")
    source_type: str | None = Field(default=None, description="Category or type classification for the scheduling link (e.g., 'meeting', 'consultation', 'demo').")
    duration_in_minutes: int | None = Field(default=None, description="Default meeting duration in minutes for appointments scheduled through this link.")
class PostV1SchedulingLinkIntegrationRequest(StrictModel):
    """Create a new scheduling link or update an existing one through your OAuth application. The source_id field is used to identify and merge duplicate resources across integrations."""
    body: PostV1SchedulingLinkIntegrationRequestBody

# Operation: delete_scheduling_link_integration
class DeleteV1SchedulingLinkIntegrationSourceIdRequestPath(StrictModel):
    source_id: str = Field(default=..., description="The unique source identifier of the scheduling link to delete. This ID was assigned when the scheduling link was originally created by your OAuth application.")
class DeleteV1SchedulingLinkIntegrationSourceIdRequest(StrictModel):
    """Delete a scheduling link that was created by your OAuth application using its source ID. This operation requires OAuth authentication and will permanently remove the scheduling link."""
    path: DeleteV1SchedulingLinkIntegrationSourceIdRequestPath

# Operation: create_scheduling_link_shared
class PostV1SharedSchedulingLinkRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="Configuration object for the scheduling link, including settings such as availability, duration, and access permissions.")
class PostV1SharedSchedulingLinkRequest(StrictModel):
    """Create a new shared scheduling link that allows others to view and book time slots on your calendar."""
    body: PostV1SharedSchedulingLinkRequestBody

# Operation: get_scheduling_link_shared
class GetV1SharedSchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the shared scheduling link to retrieve.")
class GetV1SharedSchedulingLinkIdRequest(StrictModel):
    """Retrieve a shared scheduling link by its unique identifier. Use this to fetch the details and configuration of a previously created scheduling link."""
    path: GetV1SharedSchedulingLinkIdRequestPath

# Operation: update_scheduling_link_shared
class PutV1SharedSchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the shared scheduling link to update.")
class PutV1SharedSchedulingLinkIdRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The updated scheduling link configuration containing the properties to modify.")
class PutV1SharedSchedulingLinkIdRequest(StrictModel):
    """Update the configuration and settings of an existing shared scheduling link. Modify properties such as availability, restrictions, or metadata associated with the link."""
    path: PutV1SharedSchedulingLinkIdRequestPath
    body: PutV1SharedSchedulingLinkIdRequestBody

# Operation: delete_scheduling_link_shared
class DeleteV1SharedSchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the shared scheduling link to delete.")
class DeleteV1SharedSchedulingLinkIdRequest(StrictModel):
    """Delete a shared scheduling link by its ID. This removes the link and prevents further access to the associated scheduling interface."""
    path: DeleteV1SharedSchedulingLinkIdRequestPath

# Operation: map_shared_scheduling_link
class PostV1SharedSchedulingLinkAssociationRequestBody(StrictModel):
    shared_scheduling_link_id: str = Field(default=..., description="The unique identifier of the shared scheduling link to be mapped.")
    user_scheduling_link_id: str | None = Field(default=None, description="The unique identifier of a user scheduling link to map the shared link to. Either this or a URL must be provided.")
    url: str | None = Field(default=None, description="A valid URI to map the shared link to. Either this or a user scheduling link ID must be provided.", json_schema_extra={'format': 'uri'})
class PostV1SharedSchedulingLinkAssociationRequest(StrictModel):
    """Associate a shared scheduling link with either a user scheduling link or a custom URL to enable scheduling access through the mapped destination."""
    body: PostV1SharedSchedulingLinkAssociationRequestBody

# Operation: unmap_shared_scheduling_link
class PostV1SharedSchedulingLinkAssociationUnmapRequestBody(StrictModel):
    shared_scheduling_link_id: str = Field(default=..., description="The unique identifier of the shared scheduling link to unmap from its current association.")
class PostV1SharedSchedulingLinkAssociationUnmapRequest(StrictModel):
    """Remove the association between a shared scheduling link and its mapped user scheduling link or URL, effectively disabling the shared link's access."""
    body: PostV1SharedSchedulingLinkAssociationUnmapRequestBody

# Operation: list_lead_custom_fields
class GetV1CustomFieldLeadRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of lead custom fields to return in the response. Omit to retrieve all available custom fields.")
class GetV1CustomFieldLeadRequest(StrictModel):
    """Retrieve all custom fields configured for leads in your organization. Use the optional limit parameter to control the number of results returned."""
    query: GetV1CustomFieldLeadRequestQuery | None = None

# Operation: create_lead_custom_field
class PostV1CustomFieldLeadRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the custom field that will appear in the lead interface.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type of the custom field (e.g., text, number, date, choice) that determines how the field stores and validates data.")
    accepts_multiple_values: bool | None = Field(default=None, description="When enabled, allows the field to store multiple values instead of a single value.")
    editable_roles: list[str] | None = Field(default=None, description="A list of user roles that have permission to edit this custom field. If not specified, defaults to all roles or system defaults.")
    options: list[dict[str, Any]] | None = Field(default=None, description="An array of predefined choices available for selection-type fields. Each option represents a selectable value in the field.")
class PostV1CustomFieldLeadRequest(StrictModel):
    """Create a new custom field for leads with configurable type, multi-value support, and role-based edit permissions."""
    body: PostV1CustomFieldLeadRequestBody

# Operation: get_lead_custom_field
class GetV1CustomFieldLeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the lead custom field to retrieve.")
class GetV1CustomFieldLeadIdRequest(StrictModel):
    """Retrieve the details of a specific custom field associated with a lead. Use this to access custom field configuration and values for a particular lead."""
    path: GetV1CustomFieldLeadIdRequestPath

# Operation: update_lead_custom_field
class PutV1CustomFieldLeadCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the Lead custom field to update.")
class PutV1CustomFieldLeadCustomFieldIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the custom field.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether this field should accept multiple values (true) or a single value (false).")
    editable_roles: list[str] | None = Field(default=None, description="Array of role identifiers that are permitted to edit this field's values. If specified, only users with these roles can modify the field.")
    options: list[dict[str, Any]] | None = Field(default=None, description="Array of updated choice options for fields with a choice/select type. Each option should include the option identifier and label.")
class PutV1CustomFieldLeadCustomFieldIdRequest(StrictModel):
    """Update an existing Lead Custom Field by modifying its name, value acceptance settings, role-based edit permissions, or choice options."""
    path: PutV1CustomFieldLeadCustomFieldIdRequestPath
    body: PutV1CustomFieldLeadCustomFieldIdRequestBody | None = None

# Operation: delete_lead_custom_field
class DeleteV1CustomFieldLeadCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the lead custom field to delete.")
class DeleteV1CustomFieldLeadCustomFieldIdRequest(StrictModel):
    """Permanently delete a custom field from your Lead records. The field will be immediately removed from all Lead API responses and cannot be recovered."""
    path: DeleteV1CustomFieldLeadCustomFieldIdRequestPath

# Operation: list_contact_custom_fields
class GetV1CustomFieldContactRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of custom fields to return in the response. Omit to retrieve all available custom fields.")
class GetV1CustomFieldContactRequest(StrictModel):
    """Retrieve all custom fields configured for contacts in your organization. Use the optional limit parameter to control the number of results returned."""
    query: GetV1CustomFieldContactRequestQuery | None = None

# Operation: create_contact_custom_field
class PostV1CustomFieldContactRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the custom field that will appear in contact forms and records.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type of the custom field (e.g., text, number, date, choice), which determines how values are stored and validated.")
    accepts_multiple_values: bool | None = Field(default=None, description="When enabled, allows a single contact to have multiple values for this field; when disabled, only one value is permitted.")
    restricted_to_roles: bool | None = Field(default=None, description="When enabled, restricts editing permissions to users with specific roles; when disabled, all users with contact access can edit the field.")
    options: list[dict[str, Any]] | None = Field(default=None, description="A list of predefined values available for selection when the field type is choice-based. Order is preserved for display purposes.")
class PostV1CustomFieldContactRequest(StrictModel):
    """Create a new custom field for contacts with configurable type, value constraints, and role-based access controls. This allows you to extend contact records with domain-specific attributes."""
    body: PostV1CustomFieldContactRequestBody

# Operation: get_contact_custom_field
class GetV1CustomFieldContactIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the contact custom field to retrieve.")
class GetV1CustomFieldContactIdRequest(StrictModel):
    """Retrieve the details of a specific custom field associated with a contact. Use this to access custom field configuration and values for a contact record."""
    path: GetV1CustomFieldContactIdRequestPath

# Operation: update_contact_custom_field
class PutV1CustomFieldContactCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the contact custom field to update.")
class PutV1CustomFieldContactCustomFieldIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the custom field.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether this field should accept multiple values (true) or a single value (false).")
    restricted_to_roles: bool | None = Field(default=None, description="Whether editing this field's values should be restricted to users with specific roles (true) or available to all users (false).")
    options: list[dict[str, Any]] | None = Field(default=None, description="Array of available options for choice-type fields. Each option represents a selectable value that users can assign to this field.")
class PutV1CustomFieldContactCustomFieldIdRequest(StrictModel):
    """Update an existing contact custom field by modifying its name, type configuration, multi-value support, role-based access restrictions, or choice options."""
    path: PutV1CustomFieldContactCustomFieldIdRequestPath
    body: PutV1CustomFieldContactCustomFieldIdRequestBody | None = None

# Operation: delete_contact_custom_field
class DeleteV1CustomFieldContactCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the custom field to delete.")
class DeleteV1CustomFieldContactCustomFieldIdRequest(StrictModel):
    """Permanently delete a custom field from your Contact records. The field will be immediately removed from all Contact API responses."""
    path: DeleteV1CustomFieldContactCustomFieldIdRequestPath

# Operation: list_opportunity_custom_fields
class GetV1CustomFieldOpportunityRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of custom field records to return in the response. Useful for pagination or limiting result set size.")
class GetV1CustomFieldOpportunityRequest(StrictModel):
    """Retrieve all custom fields configured for opportunities in your organization. Use the limit parameter to control the number of results returned."""
    query: GetV1CustomFieldOpportunityRequestQuery | None = None

# Operation: create_opportunity_custom_field
class PostV1CustomFieldOpportunityRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The custom field configuration object containing the field definition, name, type, and any applicable settings for the new Opportunity custom field.")
class PostV1CustomFieldOpportunityRequest(StrictModel):
    """Create a new custom field for Opportunity records. Custom fields allow you to extend the standard Opportunity data model with additional attributes tailored to your business needs."""
    body: PostV1CustomFieldOpportunityRequestBody

# Operation: get_opportunity_custom_field
class GetV1CustomFieldOpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom field to retrieve. This ID specifies which custom field's details should be fetched.")
class GetV1CustomFieldOpportunityIdRequest(StrictModel):
    """Retrieve detailed information about a specific custom field associated with an opportunity. Use this to access custom field configurations and values linked to a particular opportunity record."""
    path: GetV1CustomFieldOpportunityIdRequestPath

# Operation: update_opportunity_custom_field
class PutV1CustomFieldOpportunityCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the custom field to update.")
class PutV1CustomFieldOpportunityCustomFieldIdRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The updated custom field configuration, including name, type, multi-value setting, role restrictions, and choice options if applicable.")
class PutV1CustomFieldOpportunityCustomFieldIdRequest(StrictModel):
    """Update an existing Opportunity custom field, including its name, data type, multi-value support, role-based editing restrictions, and choice options."""
    path: PutV1CustomFieldOpportunityCustomFieldIdRequestPath
    body: PutV1CustomFieldOpportunityCustomFieldIdRequestBody

# Operation: delete_opportunity_custom_field
class DeleteV1CustomFieldOpportunityCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the custom field to delete.")
class DeleteV1CustomFieldOpportunityCustomFieldIdRequest(StrictModel):
    """Permanently delete a custom field from Opportunities. The field will be immediately removed from all Opportunity API responses and cannot be recovered."""
    path: DeleteV1CustomFieldOpportunityCustomFieldIdRequestPath

# Operation: list_activity_custom_fields
class GetV1CustomFieldActivityRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return in a single response for pagination purposes.")
class GetV1CustomFieldActivityRequest(StrictModel):
    """Retrieve all Activity Custom Fields configured for your organization. Supports optional pagination to control the number of results returned."""
    query: GetV1CustomFieldActivityRequestQuery | None = None

# Operation: create_activity_custom_field
class PostV1CustomFieldActivityRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the custom field.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type of the field, such as text, number, date, or choices. The type determines how the field stores and validates data.")
    custom_activity_type_id: str = Field(default=..., description="The unique identifier of the Custom Activity Type that this field belongs to.")
    required: bool | None = Field(default=None, description="Whether this field must be populated before the activity can be published.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether this field can store multiple values simultaneously.")
    options: list[dict[str, Any]] | None = Field(default=None, description="A list of predefined options for choice-type fields. Required when the field type is set to choices.")
class PostV1CustomFieldActivityRequest(StrictModel):
    """Create a new custom field for Activity types. The field will be associated with a specific Custom Activity Type and can be configured as required or to accept multiple values."""
    body: PostV1CustomFieldActivityRequestBody

# Operation: get_activity_custom_field
class GetV1CustomFieldActivityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Activity Custom Field to retrieve.")
class GetV1CustomFieldActivityIdRequest(StrictModel):
    """Retrieve the details of a specific Activity Custom Field by its ID. Use this to fetch configuration and metadata for a custom field associated with activities."""
    path: GetV1CustomFieldActivityIdRequestPath

# Operation: update_activity_custom_field
class PutV1CustomFieldActivityCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the Activity Custom Field to update.")
class PutV1CustomFieldActivityCustomFieldIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the custom field.")
    required: bool | None = Field(default=None, description="Whether this field must be populated when creating or editing activities.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether users can assign multiple values to this field.")
    restricted_to_roles: list[str] | None = Field(default=None, description="List of role identifiers that are permitted to edit this field. If specified, only users with these roles can modify the field value.")
    options: list[dict[str, Any]] | None = Field(default=None, description="Updated list of available options for choice-type fields. Each option should include its identifier and display label.")
class PutV1CustomFieldActivityCustomFieldIdRequest(StrictModel):
    """Update an existing Activity Custom Field by modifying its name, required status, multi-value acceptance, role-based editing restrictions, or choice field options. The field type and associated activity type cannot be changed."""
    path: PutV1CustomFieldActivityCustomFieldIdRequestPath
    body: PutV1CustomFieldActivityCustomFieldIdRequestBody | None = None

# Operation: delete_activity_custom_field
class DeleteV1CustomFieldActivityCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the Activity Custom Field to delete.")
class DeleteV1CustomFieldActivityCustomFieldIdRequest(StrictModel):
    """Permanently delete an Activity Custom Field. The field will be immediately removed from all Custom Activity API responses and cannot be recovered."""
    path: DeleteV1CustomFieldActivityCustomFieldIdRequestPath

# Operation: create_custom_object_field
class PostV1CustomFieldCustomObjectTypeRequestBody(StrictModel):
    custom_object_type_id: str = Field(default=..., description="The unique identifier of the Custom Object Type that this field will belong to.")
    required: bool | None = Field(default=None, description="Whether this field must be populated when saving a custom object instance. When enabled, the field becomes mandatory for object creation and updates.")
class PostV1CustomFieldCustomObjectTypeRequest(StrictModel):
    """Create a new custom field for a specific Custom Object Type. Custom fields extend the data structure of custom objects with additional attributes and validation rules."""
    body: PostV1CustomFieldCustomObjectTypeRequestBody

# Operation: get_custom_field
class GetV1CustomFieldCustomObjectTypeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom field to retrieve.")
class GetV1CustomFieldCustomObjectTypeIdRequest(StrictModel):
    """Retrieve detailed information about a specific custom field associated with a custom object type."""
    path: GetV1CustomFieldCustomObjectTypeIdRequestPath

# Operation: update_custom_object_field
class PutV1CustomFieldCustomObjectTypeCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the custom field to update.")
class PutV1CustomFieldCustomObjectTypeCustomFieldIdRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The field configuration updates to apply, including name, multi-value flag, required flag, role restrictions, and choice options.")
class PutV1CustomFieldCustomObjectTypeCustomFieldIdRequest(StrictModel):
    """Update an existing custom field for a custom object type. Modify field properties such as name, multi-value support, required status, role-based editing restrictions, or choice options. The custom object type and field type cannot be changed after creation."""
    path: PutV1CustomFieldCustomObjectTypeCustomFieldIdRequestPath
    body: PutV1CustomFieldCustomObjectTypeCustomFieldIdRequestBody

# Operation: delete_custom_object_field
class DeleteV1CustomFieldCustomObjectTypeCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the custom field to delete.")
class DeleteV1CustomFieldCustomObjectTypeCustomFieldIdRequest(StrictModel):
    """Permanently delete a custom field from your Custom Object schema. The field will be immediately removed from all Custom Object API responses."""
    path: DeleteV1CustomFieldCustomObjectTypeCustomFieldIdRequestPath

# Operation: create_shared_custom_field
class PostV1CustomFieldSharedRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the custom field. This name will be visible when applying the field to objects.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type of the custom field, which determines what kind of values it can store (e.g., text, number, date, dropdown).")
    associations: list[dict[str, Any]] | None = Field(default=None, description="A list of object types this custom field can be applied to. Specify which objects in your system should have access to this field.")
class PostV1CustomFieldSharedRequest(StrictModel):
    """Create a new shared custom field that can be reused across your organization. Shared custom fields are available for use on specified object types throughout your workspace."""
    body: PostV1CustomFieldSharedRequestBody

# Operation: update_shared_custom_field
class PutV1CustomFieldSharedCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the shared custom field to update.")
class PutV1CustomFieldSharedCustomFieldIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the custom field. If provided, replaces the current name.")
    choices: list[str] | None = Field(default=None, description="Updated list of options for a choices field type. Each item represents a selectable choice option. Only applicable to fields with type 'choices'.")
class PutV1CustomFieldSharedCustomFieldIdRequest(StrictModel):
    """Update a shared custom field by renaming it or modifying its choice options. The field type cannot be changed after creation."""
    path: PutV1CustomFieldSharedCustomFieldIdRequestPath
    body: PutV1CustomFieldSharedCustomFieldIdRequestBody | None = None

# Operation: delete_shared_custom_field
class DeleteV1CustomFieldSharedCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the shared custom field to delete.")
class DeleteV1CustomFieldSharedCustomFieldIdRequest(StrictModel):
    """Permanently delete a shared custom field. The field will be immediately removed from all objects it was assigned to."""
    path: DeleteV1CustomFieldSharedCustomFieldIdRequestPath

# Operation: associate_shared_custom_field
class PostV1CustomFieldSharedSharedCustomFieldIdAssociationRequestPath(StrictModel):
    shared_custom_field_id: str = Field(default=..., description="The unique identifier of the Shared Custom Field to associate.")
class PostV1CustomFieldSharedSharedCustomFieldIdAssociationRequestBody(StrictModel):
    object_type: Literal["lead", "contact", "opportunity", "custom_activity_type", "custom_object_type"] = Field(default=..., description="The object type to associate the field with. Must be one of: lead, contact, opportunity, custom_activity_type, or custom_object_type.")
    custom_activity_type_id: str | None = Field(default=None, description="The ID of the Custom Activity Type being associated. Required only when object_type is set to custom_activity_type.")
    custom_object_type_id: str | None = Field(default=None, description="The ID of the Custom Object Type being associated. Required only when object_type is set to custom_object_type.")
    editable_with_roles: list[str] | None = Field(default=None, description="A list of Role IDs that are permitted to edit the values of this field on the associated object type. If not specified, all roles may edit the field.")
    required: bool | None = Field(default=None, description="Whether a value must be provided for this field on the associated object. Only applicable when object_type is custom_activity_type or custom_object_type.")
class PostV1CustomFieldSharedSharedCustomFieldIdAssociationRequest(StrictModel):
    """Associate a Shared Custom Field with a specific object type (Lead, Contact, Opportunity, or custom types) to enable the field for use on that object type. Once associated, the field can be set and managed on instances of that object type."""
    path: PostV1CustomFieldSharedSharedCustomFieldIdAssociationRequestPath
    body: PostV1CustomFieldSharedSharedCustomFieldIdAssociationRequestBody

# Operation: update_shared_custom_field_association
class PutV1CustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestPath(StrictModel):
    shared_custom_field_id: str = Field(default=..., description="The unique identifier of the shared custom field being updated.")
    object_type: str = Field(default=..., description="The type of object this association applies to: standard types (lead, contact, opportunity) or custom types using the format custom_activity_type/{id} or custom_object_type/{id}.")
class PutV1CustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestBody(StrictModel):
    editable_with_roles: list[str] | None = Field(default=None, description="A list of role identifiers that are permitted to edit this custom field. Omit to leave unchanged.")
    required: bool | None = Field(default=None, description="Whether this custom field must be completed for the specified object type. Omit to leave unchanged.")
class PutV1CustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequest(StrictModel):
    """Update an existing Shared Custom Field Association by modifying its editability permissions and requirement status. Specify which roles can edit the field and whether it should be required for the given object type."""
    path: PutV1CustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestPath
    body: PutV1CustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestBody | None = None

# Operation: remove_custom_field_association
class DeleteV1CustomFieldSharedCustomFieldIdAssociationObjectTypeRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the shared custom field to disassociate.")
    object_type: str = Field(default=..., description="The object type to disassociate from, specified as either a standard type (lead, contact, opportunity, custom_activity_type) or a custom type reference (custom_object_type/<cotype_id>).")
class DeleteV1CustomFieldSharedCustomFieldIdAssociationObjectTypeRequest(StrictModel):
    """Remove a shared custom field from a specific object type (Lead, Contact, Opportunity, Custom Activity Type, or Custom Object Type). The field will be immediately removed from all objects of that type."""
    path: DeleteV1CustomFieldSharedCustomFieldIdAssociationObjectTypeRequestPath

# Operation: get_custom_field_schema
class GetV1CustomFieldSchemaObjectTypeRequestPath(StrictModel):
    object_type: Literal["lead", "contact", "opportunity"] = Field(default=..., description="The type of object for which to retrieve the custom field schema. Must be one of: lead, contact, or opportunity.")
class GetV1CustomFieldSchemaObjectTypeRequest(StrictModel):
    """Retrieve the custom field schema for a specified object type, including all regular and shared custom fields in their defined order."""
    path: GetV1CustomFieldSchemaObjectTypeRequestPath

# Operation: reorder_custom_fields
class PutV1CustomFieldSchemaObjectTypeRequestPath(StrictModel):
    object_type: Literal["lead", "contact", "opportunity"] = Field(default=..., description="The object type for which to reorder custom fields. Must be one of: lead, contact, or opportunity.")
class PutV1CustomFieldSchemaObjectTypeRequestBody(StrictModel):
    fields: list[PutV1CustomFieldSchemaObjectTypeBodyFieldsItem] = Field(default=..., description="An ordered list of field objects containing their IDs. The order of this list determines the new field sequence; any fields omitted from this list will be appended after the specified fields.")
class PutV1CustomFieldSchemaObjectTypeRequest(StrictModel):
    """Reorder custom fields within a schema by specifying field IDs in the desired order. Fields not included in the list are automatically appended to the end."""
    path: PutV1CustomFieldSchemaObjectTypeRequestPath
    body: PutV1CustomFieldSchemaObjectTypeRequestBody

# Operation: enrich_field
class PostV1EnrichFieldRequestQuery(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier for your organization.")
    object_type: Literal["lead", "contact"] = Field(default=..., description="The type of object to enrich, either a lead or contact.")
    object_id: str = Field(default=..., description="The unique identifier of the lead or contact record to enrich.")
    field_id: str = Field(default=..., description="The unique identifier of the custom field to enrich.")
    set_new_value: bool | None = Field(default=None, description="Whether to automatically update the field with the enriched value. Defaults to true.")
    overwrite_existing_value: bool | None = Field(default=None, description="Whether to overwrite the field if it already contains a value. Defaults to false, preserving existing data.")
class PostV1EnrichFieldRequest(StrictModel):
    """Enrich a specific field on a lead or contact using AI analysis. The operation intelligently populates or enhances the field by analyzing existing data and external sources, then returns the enriched value."""
    query: PostV1EnrichFieldRequestQuery

# Operation: create_custom_activity_type
class PostV1CustomActivityRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the custom activity type. This identifies the type throughout the system.")
    description: str | None = Field(default=None, description="A detailed explanation of the custom activity type's purpose and usage.")
    api_create_only: bool | None = Field(default=None, description="When enabled, restricts creation of this activity type to API requests only, preventing creation through the user interface.")
    editable_with_roles: list[str] | None = Field(default=None, description="A list of user roles that have permission to edit this activity type. Roles are specified as strings in the array.")
    is_archived: bool | None = Field(default=None, description="When enabled, marks the activity type as archived, making it unavailable for new activities while preserving existing data.")
class PostV1CustomActivityRequest(StrictModel):
    """Create a new custom activity type that serves as a foundation for adding custom fields to activities. The type must be established before any custom fields can be associated with it."""
    body: PostV1CustomActivityRequestBody

# Operation: get_custom_activity
class GetV1CustomActivityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom activity type to retrieve.")
class GetV1CustomActivityIdRequest(StrictModel):
    """Retrieve a specific custom activity type by its ID, including detailed custom field metadata and configuration."""
    path: GetV1CustomActivityIdRequestPath

# Operation: update_custom_activity
class PutV1CustomActivityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom activity type to update.")
class PutV1CustomActivityIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the custom activity type.")
    description: str | None = Field(default=None, description="A detailed description of the custom activity type's purpose and usage.")
    api_create_only: bool | None = Field(default=None, description="When enabled, restricts creation of this activity type to API requests only, preventing creation through the user interface.")
    editable_with_roles: list[str] | None = Field(default=None, description="A list of role identifiers that are permitted to edit this activity type. Roles not included in this list will have read-only access.")
    is_archived: bool | None = Field(default=None, description="When enabled, archives the activity type and prevents it from being used for new activities while preserving existing data.")
    field_order: list[str] | None = Field(default=None, description="An ordered array of field identifiers that determines the sequence in which fields are displayed in the user interface and API responses.")
class PutV1CustomActivityIdRequest(StrictModel):
    """Update an existing custom activity type's metadata including name, description, creation restrictions, edit permissions, and field display order. Field management (adding, modifying, or removing fields) must be done separately using the Custom Field API."""
    path: PutV1CustomActivityIdRequestPath
    body: PutV1CustomActivityIdRequestBody | None = None

# Operation: delete_custom_activity
class DeleteV1CustomActivityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom activity type to delete.")
class DeleteV1CustomActivityIdRequest(StrictModel):
    """Permanently delete a custom activity type by its ID. This action cannot be undone."""
    path: DeleteV1CustomActivityIdRequestPath

# Operation: list_custom_activities
class GetV1ActivityCustomRequestQuery(StrictModel):
    custom_activity_type_id: str | None = Field(default=None, description="Filter results to a specific custom activity type. When using this filter, the lead_id parameter is required.")
class GetV1ActivityCustomRequest(StrictModel):
    """Retrieve and filter custom activity instances. Use custom_activity_type_id to narrow results by activity type; note that filtering by activity type requires the lead_id parameter to be specified."""
    query: GetV1ActivityCustomRequestQuery | None = None

# Operation: create_custom_activity
class PostV1ActivityCustomRequestBody(StrictModel):
    custom_activity_type_id: str = Field(default=..., description="The unique identifier of the custom activity type to instantiate.")
    lead_id: str = Field(default=..., description="The unique identifier of the lead associated with this activity.")
    pinned: bool | None = Field(default=None, description="Set to true to pin this activity, making it more prominent in the activity list.")
class PostV1ActivityCustomRequest(StrictModel):
    """Create a new custom activity instance for a lead. Activities are published by default with all required fields validated, or can be created as drafts to defer validation. Optionally pin the activity for visibility."""
    body: PostV1ActivityCustomRequestBody

# Operation: get_custom_activity_instance
class GetV1ActivityCustomIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Activity instance to retrieve.")
class GetV1ActivityCustomIdRequest(StrictModel):
    """Retrieve a specific Custom Activity instance by its unique identifier. Use this to fetch details about a single custom activity."""
    path: GetV1ActivityCustomIdRequestPath

# Operation: update_custom_activity_instance
class PutV1ActivityCustomIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Activity instance to update.")
class PutV1ActivityCustomIdRequestBody(StrictModel):
    pinned: bool | None = Field(default=None, description="Whether to pin or unpin the activity. Set to true to pin the activity or false to unpin it.")
class PutV1ActivityCustomIdRequest(StrictModel):
    """Update a Custom Activity instance by modifying custom fields, changing its status between draft and published, or toggling its pinned state."""
    path: PutV1ActivityCustomIdRequestPath
    body: PutV1ActivityCustomIdRequestBody | None = None

# Operation: delete_custom_activity_instance
class DeleteV1ActivityCustomIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Activity instance to delete.")
class DeleteV1ActivityCustomIdRequest(StrictModel):
    """Delete a Custom Activity instance by its unique identifier. This operation permanently removes the specified custom activity from the system."""
    path: DeleteV1ActivityCustomIdRequestPath

# Operation: create_custom_object_type
class PostV1CustomObjectTypeRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name of the Custom Object Type. This is used to identify the type throughout the system.")
    name_plural: str = Field(default=..., description="The plural form of the Custom Object Type name. This is used in UI elements and lists where multiple instances are displayed.")
    description: str | None = Field(default=None, description="An optional longer description that provides additional context about the purpose and use of this Custom Object Type.")
    api_create_only: bool | None = Field(default=None, description="When enabled, only API clients can create new instances of this type. UI-based creation is disabled. Defaults to false, allowing any user to create instances.")
    editable_with_roles: list[str] | None = Field(default=None, description="An optional list of user roles that are permitted to edit instances of this type. When specified, only users with at least one of these roles can make changes. If not specified, any user in your organization can edit instances.")
class PostV1CustomObjectTypeRequest(StrictModel):
    """Create a new Custom Object Type that serves as a blueprint for custom objects in your organization. Custom Object Types must be created before you can add custom fields to instances."""
    body: PostV1CustomObjectTypeRequestBody

# Operation: get_custom_object_type
class GetV1CustomObjectTypeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Object Type to retrieve.")
class GetV1CustomObjectTypeIdRequest(StrictModel):
    """Retrieve a specific Custom Object Type by its ID, including detailed metadata about all associated Custom Fields."""
    path: GetV1CustomObjectTypeIdRequestPath

# Operation: update_custom_object_type
class PutV1CustomObjectTypeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Object Type to update.")
class PutV1CustomObjectTypeIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name of the Custom Object Type.")
    name_plural: str | None = Field(default=None, description="The plural form of the Custom Object Type name, used in API responses and UI contexts.")
    description: str | None = Field(default=None, description="A detailed description explaining the purpose and use of this Custom Object Type.")
    api_create_only: bool | None = Field(default=None, description="When enabled, instances of this type can only be created through API clients, preventing creation through the user interface.")
    editable_with_roles: list[str] | None = Field(default=None, description="A list of role identifiers that are permitted to edit instances of this Custom Object Type. Order is not significant.")
class PutV1CustomObjectTypeIdRequest(StrictModel):
    """Update an existing Custom Object Type's metadata including name, description, and access controls. Field management must be handled separately through the Custom Object Custom Fields API."""
    path: PutV1CustomObjectTypeIdRequestPath
    body: PutV1CustomObjectTypeIdRequestBody | None = None

# Operation: delete_custom_object_type
class DeleteV1CustomObjectTypeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Object Type to delete.")
class DeleteV1CustomObjectTypeIdRequest(StrictModel):
    """Permanently delete a Custom Object Type by its ID. This action removes the custom object type definition and cannot be undone."""
    path: DeleteV1CustomObjectTypeIdRequestPath

# Operation: list_custom_objects
class GetV1CustomObjectRequestQuery(StrictModel):
    lead_id: str = Field(default=..., description="The unique identifier of the lead whose Custom Object instances should be retrieved. This parameter is required to filter results to a specific lead.")
    custom_object_type_id: str | None = Field(default=None, description="Optional filter to retrieve only Custom Object instances of a specific type. When omitted, all Custom Object types for the lead are returned.")
class GetV1CustomObjectRequest(StrictModel):
    """Retrieve all Custom Object instances associated with a specific lead. Use Advanced Filtering to retrieve Custom Objects across multiple leads. Custom field values are returned in the format custom.{custom_field_id}."""
    query: GetV1CustomObjectRequestQuery

# Operation: create_custom_object
class PostV1CustomObjectRequestBody(StrictModel):
    custom_object_type_id: str = Field(default=..., description="The identifier of the Custom Object type being created, which determines which Custom Fields are available for this instance.")
    lead_id: str = Field(default=..., description="The identifier of the lead that this Custom Object instance will be associated with.")
    name: str = Field(default=..., description="A display name for this Custom Object instance.")
class PostV1CustomObjectRequest(StrictModel):
    """Create a new Custom Object instance linked to a specific lead. Custom Field values can be set using the custom.{custom_field_id} format."""
    body: PostV1CustomObjectRequestBody

# Operation: get_custom_object
class GetV1CustomObjectIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Object instance to retrieve.")
class GetV1CustomObjectIdRequest(StrictModel):
    """Retrieve a single Custom Object instance by its unique identifier. Use this operation to fetch detailed information about a specific custom object."""
    path: GetV1CustomObjectIdRequestPath

# Operation: update_custom_object
class PutV1CustomObjectIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Object instance to update.")
class PutV1CustomObjectIdRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The update payload containing the custom fields and/or name property to modify on the Custom Object instance.")
class PutV1CustomObjectIdRequest(StrictModel):
    """Update an existing Custom Object instance by modifying its custom fields or name property. Supports adding, changing, or removing any custom fields associated with the object."""
    path: PutV1CustomObjectIdRequestPath
    body: PutV1CustomObjectIdRequestBody

# Operation: delete_custom_object
class DeleteV1CustomObjectIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Object instance to delete.")
class DeleteV1CustomObjectIdRequest(StrictModel):
    """Permanently delete a Custom Object instance by its ID. This action cannot be undone."""
    path: DeleteV1CustomObjectIdRequestPath

# Operation: unsubscribe_email
class PostV1UnsubscribeEmailRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address to unsubscribe from Close messages. Must be a valid email format.", json_schema_extra={'format': 'email'})
class PostV1UnsubscribeEmailRequest(StrictModel):
    """Remove an email address from Close's messaging system. Use this operation when an email has unsubscribed through another channel and you need to sync that status with Close."""
    body: PostV1UnsubscribeEmailRequestBody

# Operation: resubscribe_email
class DeleteV1UnsubscribeEmailEmailAddressRequestPath(StrictModel):
    email_address: str = Field(default=..., description="The email address to resubscribe. Must be a valid email format.", json_schema_extra={'format': 'email'})
class DeleteV1UnsubscribeEmailEmailAddressRequest(StrictModel):
    """Resubscribe an email address to receive messages from Close. Use this operation to restore messaging delivery for previously unsubscribed email addresses."""
    path: DeleteV1UnsubscribeEmailEmailAddressRequestPath

# Operation: search_contacts_and_leads
class PostApiV1DataSearchRequestBodyQueryField(StrictModel):
    type_: Literal["regular_field", "custom_field"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Specifies whether the field is a standard system field or a custom field defined for your organization.")
    object_type: str | None = Field(default=None, validation_alias="object_type", serialization_alias="object_type", description="The object type that contains the field being filtered, used when querying fields from related objects.")
    field_name: str | None = Field(default=None, validation_alias="field_name", serialization_alias="field_name", description="The name of the regular (system) field to filter by. Use this when filtering standard fields like name, email, or phone.")
class PostApiV1DataSearchRequestBodyQueryCondition(StrictModel):
    type_: Literal["boolean", "current_user", "exists", "text", "term", "reference", "number_range"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of condition to apply when filtering by field value. Choose 'boolean' for true/false fields, 'current_user' to match the authenticated user, 'exists' to check field presence, 'text' for text matching, 'term' for exact value matching, 'reference' for related record matching, or 'number_range' for numeric comparisons.")
    value: dict[str, Any] | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The condition value to match against. Structure depends on the condition type: for 'boolean' use true/false, for 'term' use a single value, for 'number_range' use an object with comparison operators, for 'reference' use object IDs.")
    values: list[str] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="Array of values to match against for 'term' conditions. Results include records where the field matches any value in this list.")
    gt: int | None = Field(default=None, validation_alias="gt", serialization_alias="gt", description="Numeric lower bound (exclusive) for 'number_range' conditions. Use to filter fields with values greater than this number.")
    reference_type: str | None = Field(default=None, validation_alias="reference_type", serialization_alias="reference_type", description="The type of object being referenced in a 'reference' condition, such as 'user' for user-related filters.")
    object_ids: list[str] | None = Field(default=None, validation_alias="object_ids", serialization_alias="object_ids", description="Array of object IDs to match in 'reference' conditions. Results include records that reference any of these objects.")
class PostApiV1DataSearchRequestBodyQuery(StrictModel):
    type_: Literal["and", "or", "id", "object_type", "text", "has_related", "field_condition"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The root query type that determines how to interpret the query structure. Use 'and' or 'or' for combining multiple sub-queries, 'id' to search by object identifier, 'object_type' to filter by record type, 'text' for full-text search, 'has_related' to find records with related objects, or 'field_condition' to filter by specific field values.")
    queries: list[dict[str, Any]] | None = Field(default=None, validation_alias="queries", serialization_alias="queries", description="Array of nested query objects used with 'and' or 'or' query types to combine multiple filter conditions. Each sub-query follows the same structure as the parent query.")
    object_type: Literal["contact", "lead", "contact_phone", "contact_email", "contact_url", "address"] | None = Field(default=None, validation_alias="object_type", serialization_alias="object_type", description="Filter results to a specific object type: 'contact' or 'lead' for primary records, or 'contact_phone', 'contact_email', 'contact_url', 'address' for related contact details.")
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The value to match for 'id' queries (object identifier) or 'text' queries (search term). For text queries, matching behavior is controlled by the 'mode' parameter.")
    mode: Literal["full_words", "phrase"] | None = Field(default=None, validation_alias="mode", serialization_alias="mode", description="Controls text search matching behavior: 'full_words' matches complete words only, 'phrase' matches the exact phrase as entered.")
    negate: bool | None = Field(default=None, validation_alias="negate", serialization_alias="negate", description="When true, inverts the query logic to return records that do NOT match the specified conditions.")
    this_object_type: str | None = Field(default=None, validation_alias="this_object_type", serialization_alias="this_object_type", description="The primary object type for 'has_related' queries. Specifies which object type you're searching (e.g., 'contact').")
    related_object_type: str | None = Field(default=None, validation_alias="related_object_type", serialization_alias="related_object_type", description="The related object type to check for in 'has_related' queries. Specifies what related records to look for (e.g., 'contact_email').")
    related_query: dict[str, Any] | None = Field(default=None, validation_alias="related_query", serialization_alias="related_query", description="A query object defining conditions to apply to the related objects in 'has_related' queries. Only primary records with related objects matching this query are returned.")
    field: PostApiV1DataSearchRequestBodyQueryField | None = None
    condition: PostApiV1DataSearchRequestBodyQueryCondition | None = None
class PostApiV1DataSearchRequestBody(StrictModel):
    fields: dict[str, Any] | None = Field(default=None, validation_alias="_fields", serialization_alias="_fields", description="Specify which fields to include in results for each object type. Use an object with object type keys (e.g., 'contact', 'lead') and arrays of field names as values to customize response data.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Number of results to return per page. Defaults to 10 results. Use with 'cursor' for pagination through large result sets.")
    cursor: str | None = Field(default=None, description="Pagination cursor from a previous response to retrieve the next page of results. Omit for the first request.")
    results_limit: int | None = Field(default=None, description="Maximum total number of results to return across all pages. Limits the overall result set size regardless of pagination.")
    include_counts: bool | None = Field(default=None, description="When true, the response includes counts of total matching results for each object type, useful for understanding result scope before fetching all records.")
    sort: list[PostApiV1DataSearchBodySortItem] | None = Field(default=None, description="Array of sort specifications to order results. Each entry specifies a field name and sort direction (ascending or descending) to organize results by your preferred criteria.")
    query: PostApiV1DataSearchRequestBodyQuery
class PostApiV1DataSearchRequest(StrictModel):
    """Search for Leads or Contacts using advanced filtering with support for complex query conditions, relationships, and pagination. Construct queries with logical operators (and/or), field conditions, text search, and related object filters to find records matching your criteria."""
    body: PostApiV1DataSearchRequestBody

# ============================================================================
# Component Models
# ============================================================================

class PostApiV1DataSearchBodySortItemField(PermissiveModel):
    """Field to sort by"""
    object_type: str | None = None
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")
    field_name: str | None = None

class PostApiV1DataSearchBodySortItem(PermissiveModel):
    direction: Literal["asc", "desc"] | None = Field(None, description="Sort direction")
    field: PostApiV1DataSearchBodySortItemField | None = Field(None, description="Field to sort by")

class PostV1ActivityEmailBodyAttachmentsItem(PermissiveModel):
    url: str = Field(..., description="File URL from Files API")
    filename: str = Field(..., description="Attachment filename")
    content_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")

class PostV1ActivityNoteBodyAttachmentsItem(PermissiveModel):
    url: str | None = Field(None, description="URL from Files API download.url field, must begin https://app.close.com/go/file/")
    filename: str | None = Field(None, description="Filename of the attachment")
    content_type: str | None = Field(None, description="MIME type of the attachment")

class PostV1ActivityWhatsappMessageBodyAttachmentsItem(PermissiveModel):
    url: str = Field(..., description="URL from Files API download.url response, must begin with https://app.close.com/go/file/")
    filename: str = Field(..., description="Filename of the attachment")
    content_type: str = Field(..., description="MIME type of the attachment")

class PostV1WebhookBodyEventsItem(PermissiveModel):
    object_type: str
    action: str

class PutV1CustomFieldSchemaObjectTypeBodyFieldsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="Custom field ID")

class PutV1PipelinePipelineIdBodyStatusesItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Opportunity status ID")

class PutV1WebhookIdBodyEventsItem(PermissiveModel):
    object_type: str | None = None
    action: str | None = None


# Rebuild models to resolve forward references (required for circular refs)
PostApiV1DataSearchBodySortItem.model_rebuild()
PostApiV1DataSearchBodySortItemField.model_rebuild()
PostV1ActivityEmailBodyAttachmentsItem.model_rebuild()
PostV1ActivityNoteBodyAttachmentsItem.model_rebuild()
PostV1ActivityWhatsappMessageBodyAttachmentsItem.model_rebuild()
PostV1WebhookBodyEventsItem.model_rebuild()
PutV1CustomFieldSchemaObjectTypeBodyFieldsItem.model_rebuild()
PutV1PipelinePipelineIdBodyStatusesItem.model_rebuild()
PutV1WebhookIdBodyEventsItem.model_rebuild()

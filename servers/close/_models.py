"""
Close Api MCP Server - Pydantic Models

Generated: 2026-04-07 08:42:04 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "DeleteActivityCallIdRequest",
    "DeleteActivityCustomIdRequest",
    "DeleteActivityEmailIdRequest",
    "DeleteActivityEmailthreadIdRequest",
    "DeleteActivityFormSubmissionIdRequest",
    "DeleteActivityMeetingIdRequest",
    "DeleteActivityNoteIdRequest",
    "DeleteActivitySmsIdRequest",
    "DeleteActivityStatusChangeLeadIdRequest",
    "DeleteActivityStatusChangeOpportunityIdRequest",
    "DeleteActivityTaskCompletedIdRequest",
    "DeleteActivityWhatsappMessageIdRequest",
    "DeleteCommentCommentIdRequest",
    "DeleteContactIdRequest",
    "DeleteCustomActivityIdRequest",
    "DeleteCustomFieldActivityCustomFieldIdRequest",
    "DeleteCustomFieldContactCustomFieldIdRequest",
    "DeleteCustomFieldCustomObjectTypeCustomFieldIdRequest",
    "DeleteCustomFieldLeadCustomFieldIdRequest",
    "DeleteCustomFieldOpportunityCustomFieldIdRequest",
    "DeleteCustomFieldSharedCustomFieldIdAssociationObjectTypeRequest",
    "DeleteCustomFieldSharedCustomFieldIdRequest",
    "DeleteCustomObjectIdRequest",
    "DeleteCustomObjectTypeIdRequest",
    "DeleteEmailTemplateIdRequest",
    "DeleteGroupGroupIdMemberUserIdRequest",
    "DeleteGroupGroupIdRequest",
    "DeleteIntegrationLinkIdRequest",
    "DeleteLeadIdRequest",
    "DeleteOpportunityIdRequest",
    "DeleteOutcomeIdRequest",
    "DeletePhoneNumberIdRequest",
    "DeletePipelinePipelineIdRequest",
    "DeleteRoleRoleIdRequest",
    "DeleteSavedSearchIdRequest",
    "DeleteSchedulingLinkIdRequest",
    "DeleteSchedulingLinkIntegrationSourceIdRequest",
    "DeleteSendAsIdRequest",
    "DeleteSendAsRequest",
    "DeleteSequenceIdRequest",
    "DeleteSharedSchedulingLinkIdRequest",
    "DeleteSmsTemplateIdRequest",
    "DeleteStatusLeadStatusIdRequest",
    "DeleteStatusOpportunityStatusIdRequest",
    "DeleteTaskIdRequest",
    "DeleteUnsubscribeEmailEmailAddressRequest",
    "DeleteWebhookIdRequest",
    "GetActivityCallIdRequest",
    "GetActivityCallRequest",
    "GetActivityCreatedIdRequest",
    "GetActivityCreatedRequest",
    "GetActivityCustomIdRequest",
    "GetActivityCustomRequest",
    "GetActivityEmailIdRequest",
    "GetActivityEmailRequest",
    "GetActivityEmailthreadIdRequest",
    "GetActivityEmailthreadRequest",
    "GetActivityFormSubmissionIdRequest",
    "GetActivityFormSubmissionRequest",
    "GetActivityLeadMergeIdRequest",
    "GetActivityLeadMergeRequest",
    "GetActivityMeetingIdRequest",
    "GetActivityMeetingRequest",
    "GetActivityNoteIdRequest",
    "GetActivityNoteRequest",
    "GetActivityRequest",
    "GetActivitySmsIdRequest",
    "GetActivitySmsRequest",
    "GetActivityStatusChangeLeadIdRequest",
    "GetActivityStatusChangeLeadRequest",
    "GetActivityStatusChangeOpportunityIdRequest",
    "GetActivityStatusChangeOpportunityRequest",
    "GetActivityTaskCompletedIdRequest",
    "GetActivityTaskCompletedRequest",
    "GetActivityWhatsappMessageIdRequest",
    "GetActivityWhatsappMessageRequest",
    "GetBulkActionDeleteIdRequest",
    "GetBulkActionEditIdRequest",
    "GetBulkActionEmailIdRequest",
    "GetBulkActionSequenceSubscriptionIdRequest",
    "GetCommentCommentIdRequest",
    "GetCommentRequest",
    "GetCommentThreadRequest",
    "GetCommentThreadThreadIdRequest",
    "GetConnectedAccountIdRequest",
    "GetContactIdRequest",
    "GetContactRequest",
    "GetCustomActivityIdRequest",
    "GetCustomFieldActivityIdRequest",
    "GetCustomFieldActivityRequest",
    "GetCustomFieldContactIdRequest",
    "GetCustomFieldContactRequest",
    "GetCustomFieldCustomObjectTypeIdRequest",
    "GetCustomFieldLeadIdRequest",
    "GetCustomFieldLeadRequest",
    "GetCustomFieldOpportunityIdRequest",
    "GetCustomFieldOpportunityRequest",
    "GetCustomFieldSchemaObjectTypeRequest",
    "GetCustomObjectIdRequest",
    "GetCustomObjectRequest",
    "GetCustomObjectTypeIdRequest",
    "GetDialerIdRequest",
    "GetDialerRequest",
    "GetEmailTemplateIdRenderRequest",
    "GetEmailTemplateIdRequest",
    "GetEmailTemplateRequest",
    "GetEventIdRequest",
    "GetEventRequest",
    "GetExportIdRequest",
    "GetExportRequest",
    "GetGroupGroupIdRequest",
    "GetGroupRequest",
    "GetIntegrationLinkIdRequest",
    "GetLeadIdRequest",
    "GetLeadRequest",
    "GetMembershipIdPinnedViewsRequest",
    "GetOpportunityIdRequest",
    "GetOpportunityRequest",
    "GetOrganizationIdRequest",
    "GetOutcomeIdRequest",
    "GetPhoneNumberIdRequest",
    "GetPhoneNumberRequest",
    "GetReportCustomOrganizationIdRequest",
    "GetReportSentEmailsOrganizationIdRequest",
    "GetReportStatusesLeadOrganizationIdRequest",
    "GetReportStatusesOpportunityOrganizationIdRequest",
    "GetRoleIdRequest",
    "GetSavedSearchIdRequest",
    "GetSavedSearchRequest",
    "GetSchedulingLinkIdRequest",
    "GetSendAsIdRequest",
    "GetSendAsRequest",
    "GetSequenceIdRequest",
    "GetSequenceRequest",
    "GetSequenceSubscriptionIdRequest",
    "GetSequenceSubscriptionRequest",
    "GetSharedSchedulingLinkIdRequest",
    "GetSmsTemplateIdRequest",
    "GetSmsTemplateRequest",
    "GetTaskIdRequest",
    "GetTaskRequest",
    "GetUserAvailabilityRequest",
    "GetUserIdRequest",
    "GetUserRequest",
    "GetWebhookIdRequest",
    "PostActivityCallRequest",
    "PostActivityCustomRequest",
    "PostActivityEmailRequest",
    "PostActivityMeetingIdIntegrationRequest",
    "PostActivityNoteRequest",
    "PostActivitySmsRequest",
    "PostActivityStatusChangeLeadRequest",
    "PostActivityStatusChangeOpportunityRequest",
    "PostActivityWhatsappMessageRequest",
    "PostApiV1DataSearchRequest",
    "PostBulkActionDeleteRequest",
    "PostBulkActionEditRequest",
    "PostBulkActionEmailRequest",
    "PostBulkActionSequenceSubscriptionRequest",
    "PostCommentRequest",
    "PostContactRequest",
    "PostCustomActivityRequest",
    "PostCustomFieldActivityRequest",
    "PostCustomFieldContactRequest",
    "PostCustomFieldCustomObjectTypeRequest",
    "PostCustomFieldLeadRequest",
    "PostCustomFieldOpportunityRequest",
    "PostCustomFieldSharedRequest",
    "PostCustomFieldSharedSharedCustomFieldIdAssociationRequest",
    "PostCustomObjectRequest",
    "PostCustomObjectTypeRequest",
    "PostEmailTemplateRequest",
    "PostEnrichFieldRequest",
    "PostExportLeadRequest",
    "PostExportOpportunityRequest",
    "PostFilesUploadRequest",
    "PostGroupGroupIdMemberRequest",
    "PostGroupRequest",
    "PostIntegrationLinkRequest",
    "PostLeadMergeRequest",
    "PostLeadRequest",
    "PostMembershipRequest",
    "PostOpportunityRequest",
    "PostOutcomeRequest",
    "PostPhoneNumberRequestInternalRequest",
    "PostPipelineRequest",
    "PostReportActivityRequest",
    "PostReportFunnelOpportunityStagesRequest",
    "PostReportFunnelOpportunityTotalsRequest",
    "PostRoleRequest",
    "PostSavedSearchRequest",
    "PostSchedulingLinkIntegrationRequest",
    "PostSchedulingLinkRequest",
    "PostSendAsBulkRequest",
    "PostSendAsRequest",
    "PostSequenceRequest",
    "PostSequenceSubscriptionRequest",
    "PostSharedSchedulingLinkAssociationRequest",
    "PostSharedSchedulingLinkAssociationUnmapRequest",
    "PostSharedSchedulingLinkRequest",
    "PostSmsTemplateRequest",
    "PostStatusLeadRequest",
    "PostStatusOpportunityRequest",
    "PostTaskRequest",
    "PostUnsubscribeEmailRequest",
    "PostWebhookRequest",
    "PutActivityCallIdRequest",
    "PutActivityCustomIdRequest",
    "PutActivityEmailIdRequest",
    "PutActivityMeetingIdRequest",
    "PutActivityNoteIdRequest",
    "PutActivitySmsIdRequest",
    "PutActivityWhatsappMessageIdRequest",
    "PutCommentCommentIdRequest",
    "PutContactIdRequest",
    "PutCustomActivityIdRequest",
    "PutCustomFieldActivityCustomFieldIdRequest",
    "PutCustomFieldContactCustomFieldIdRequest",
    "PutCustomFieldCustomObjectTypeCustomFieldIdRequest",
    "PutCustomFieldLeadCustomFieldIdRequest",
    "PutCustomFieldOpportunityCustomFieldIdRequest",
    "PutCustomFieldSchemaObjectTypeRequest",
    "PutCustomFieldSharedCustomFieldIdRequest",
    "PutCustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequest",
    "PutCustomObjectIdRequest",
    "PutCustomObjectTypeIdRequest",
    "PutEmailTemplateIdRequest",
    "PutGroupGroupIdRequest",
    "PutIntegrationLinkIdRequest",
    "PutLeadIdRequest",
    "PutMembershipIdPinnedViewsRequest",
    "PutMembershipIdRequest",
    "PutMembershipRequest",
    "PutOpportunityIdRequest",
    "PutOrganizationIdRequest",
    "PutOutcomeIdRequest",
    "PutPhoneNumberIdRequest",
    "PutPipelinePipelineIdRequest",
    "PutRoleRoleIdRequest",
    "PutSavedSearchIdRequest",
    "PutSchedulingLinkIdRequest",
    "PutSequenceIdRequest",
    "PutSequenceSubscriptionIdRequest",
    "PutSharedSchedulingLinkIdRequest",
    "PutSmsTemplateIdRequest",
    "PutStatusLeadStatusIdRequest",
    "PutStatusOpportunityStatusIdRequest",
    "PutTaskIdRequest",
    "PutTaskRequest",
    "PutWebhookIdRequest",
    "PostActivityEmailBodyAttachmentsItem",
    "PostActivityNoteBodyAttachmentsItem",
    "PostActivityWhatsappMessageBodyAttachmentsItem",
    "PostApiV1DataSearchBodySortItem",
    "PostContactBodyEmailsItem",
    "PostContactBodyPhonesItem",
    "PostWebhookBodyEventsItem",
    "PutActivityNoteIdBodyAttachmentsItem",
    "PutActivityWhatsappMessageIdBodyAttachmentsItem",
    "PutCustomFieldSchemaObjectTypeBodyFieldsItem",
    "PutPipelinePipelineIdBodyStatusesItem",
    "PutWebhookIdBodyEventsItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_leads
class GetLeadRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of leads to return in the response. Specify a positive integer to limit the result set size.")
class GetLeadRequest(StrictModel):
    """Retrieve a list of leads with optional pagination control. Use the limit parameter to specify the maximum number of results to return."""
    query: GetLeadRequestQuery | None = None

# Operation: create_lead
class PostLeadRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The name of the lead.")
    contacts: list[dict[str, Any]] | None = Field(default=None, description="An array of nested contact objects to associate with the lead. Order is preserved as provided.")
    addresses: list[dict[str, Any]] | None = Field(default=None, description="An array of nested address objects to associate with the lead. Order is preserved as provided.")
class PostLeadRequest(StrictModel):
    """Create a new lead with optional nested contacts and addresses. Related entities like activities, tasks, and opportunities must be created separately."""
    body: PostLeadRequestBody | None = None

# Operation: get_lead
class GetLeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the lead to retrieve.")
class GetLeadIdRequest(StrictModel):
    """Retrieve a single lead by its unique identifier. Use this operation to fetch detailed information about a specific lead."""
    path: GetLeadIdRequestPath

# Operation: update_lead
class PutLeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the lead to update.")
class PutLeadIdRequestBody(StrictModel):
    custom_field_id: str | None = Field(default=None, validation_alias="custom.FIELD_ID", serialization_alias="custom.FIELD_ID", description="Custom field value to set, update, or remove. Set to null to unset a field. For multi-value fields, use the .add suffix to append values or .remove suffix to delete specific values.")
class PutLeadIdRequest(StrictModel):
    """Update an existing lead with support for partial updates. Modify standard fields like status, custom fields, or multi-value fields using add/remove suffixes without affecting unspecified fields."""
    path: PutLeadIdRequestPath
    body: PutLeadIdRequestBody | None = None

# Operation: delete_lead
class DeleteLeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the lead to delete. This must be a valid lead ID that exists in the system.")
class DeleteLeadIdRequest(StrictModel):
    """Permanently remove a lead from the system by its ID. This action cannot be undone and will delete all associated data."""
    path: DeleteLeadIdRequestPath

# Operation: merge_leads
class PostLeadMergeRequestBody(StrictModel):
    source: str = Field(default=..., description="The ID of the source lead whose data will be consolidated into the destination lead.")
    destination: str = Field(default=..., description="The ID of the destination lead that will retain all merged data and serve as the primary record after the operation completes.")
class PostLeadMergeRequest(StrictModel):
    """Merge two leads by consolidating all data from a source lead into a destination lead. The destination lead becomes the primary record containing the merged information."""
    body: PostLeadMergeRequestBody

# Operation: list_contacts
class GetContactRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of contacts to return in a single request. Allows you to control pagination size for efficient data retrieval.")
class GetContactRequest(StrictModel):
    """Retrieve a paginated list of all contacts in the system. Use the limit parameter to control the number of results returned per request."""
    query: GetContactRequestQuery | None = None

# Operation: create_contact
class PostContactRequestBody(StrictModel):
    lead_id: str = Field(default=..., description="The ID of the lead to associate with this contact. Required to link the contact to an existing lead; if omitted, a new lead will be created automatically.")
    name: str = Field(default=..., description="The full name of the contact. Used to identify the contact and, if no lead_id is provided, to name the newly created lead.")
    title: str | None = Field(default=None, description="The contact's job title or professional role.")
    emails: list[PostContactBodyEmailsItem] | None = Field(default=None, description="A list of email addresses for the contact. Each item should be a valid email address.")
    phones: list[PostContactBodyPhonesItem] | None = Field(default=None, description="A list of phone numbers for the contact. Each item should be a valid phone number.")
class PostContactRequest(StrictModel):
    """Create a new contact and associate it with a lead. If no lead_id is provided, a new lead will be automatically created using the contact's name."""
    body: PostContactRequestBody

# Operation: get_contact
class GetContactIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the contact to retrieve.")
class GetContactIdRequest(StrictModel):
    """Retrieve a single contact by its unique identifier. Use this operation to fetch detailed information about a specific contact."""
    path: GetContactIdRequestPath

# Operation: update_contact
class PutContactIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the contact to update.")
class PutContactIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The contact's full name.")
    emails: list[dict[str, Any]] | None = Field(default=None, description="A list of email addresses associated with the contact. Order is preserved as provided.")
    phones: list[dict[str, Any]] | None = Field(default=None, description="A list of phone numbers associated with the contact. Order is preserved as provided.")
    urls: list[dict[str, Any]] | None = Field(default=None, description="A list of URLs associated with the contact. Order is preserved as provided.")
class PutContactIdRequest(StrictModel):
    """Update an existing contact's information including name, email addresses, phone numbers, and URLs. Use `.add` or `.remove` suffixes on custom field keys to add or remove individual values from multi-value fields."""
    path: PutContactIdRequestPath
    body: PutContactIdRequestBody | None = None

# Operation: delete_contact
class DeleteContactIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the contact to delete.")
class DeleteContactIdRequest(StrictModel):
    """Permanently remove a contact from the system by its ID. This action cannot be undone and will delete all associated data."""
    path: DeleteContactIdRequestPath

# Operation: list_activities
class GetActivityRequestQuery(StrictModel):
    user_id__in: str | None = Field(default=None, description="Filter activities by one or more user IDs (comma-separated). Only available when querying activities for a single lead using lead_id.")
    contact_id__in: str | None = Field(default=None, description="Filter activities by one or more contact IDs (comma-separated). Only available when querying activities for a single lead using lead_id.")
    activity_at__gt: str | None = Field(default=None, description="Return only activities that occurred after this date and time (ISO 8601 format). Requires sorting by -activity_at when used.", json_schema_extra={'format': 'date-time'})
    activity_at__lt: str | None = Field(default=None, description="Return only activities that occurred before this date and time (ISO 8601 format). Requires sorting by -activity_at when used.", json_schema_extra={'format': 'date-time'})
    order_by: Literal["date_created", "-date_created", "activity_at", "-activity_at"] | None = Field(default=None, validation_alias="_order_by", serialization_alias="_order_by", description="Sort results by creation date or activity timestamp. Use date_created for creation order or activity_at for activity order; prefix with hyphen (-) for descending order. Sorting by -activity_at is only available when querying a single lead with lead_id.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return in the response.")
    thread_emails: Literal["true", "only"] | None = Field(default=None, description="Control how emails are grouped in results. Use 'true' to return email threads alongside individual email objects, or 'only' to return email threads without individual email objects. Omit to return individual email objects per message.")
class GetActivityRequest(StrictModel):
    """Retrieve and filter activity records across leads or for a specific lead. Supports advanced filtering by user, contact, and activity timestamp, with optional email threading to group related messages."""
    query: GetActivityRequestQuery | None = None

# Operation: list_calls
class GetActivityCallRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of call records to return in the response. Limits the result set size for pagination or performance optimization.")
class GetActivityCallRequest(StrictModel):
    """Retrieve a list of all Call activities, with optional filtering by result count. Use this to view call records and activity history."""
    query: GetActivityCallRequestQuery | None = None

# Operation: log_call_activity
class PostActivityCallRequestBody(StrictModel):
    direction: Literal["outbound", "inbound"] = Field(default=..., description="Specify whether the call was outbound or inbound.")
    recording_url: str | None = Field(default=None, description="Optional HTTPS URL pointing to an MP3 recording of the call.", json_schema_extra={'format': 'uri'})
    lead_id: str = Field(default=..., description="The ID of the lead associated with this call activity.")
    duration: int | None = Field(default=None, description="Optional call duration specified in seconds.")
class PostActivityCallRequest(StrictModel):
    """Manually log a call activity for calls made outside the Close VoIP system. The activity is automatically marked as completed."""
    body: PostActivityCallRequestBody

# Operation: get_call
class GetActivityCallIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Call activity record to retrieve.")
class GetActivityCallIdRequest(StrictModel):
    """Retrieve a specific Call activity record by its unique identifier. Use this to fetch detailed information about a single call activity."""
    path: GetActivityCallIdRequestPath

# Operation: update_call
class PutActivityCallIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Call activity to update.")
class PutActivityCallIdRequestBody(StrictModel):
    note_html: str | None = Field(default=None, description="HTML-formatted note content to attach to the call activity.")
    outcome_id: str | None = Field(default=None, description="The outcome identifier to associate with this call activity.")
class PutActivityCallIdRequest(StrictModel):
    """Update a Call activity record, typically to modify the call notes or assign an outcome. Note that certain fields like status, duration, and direction cannot be modified for calls made through Close's VoIP system."""
    path: PutActivityCallIdRequestPath
    body: PutActivityCallIdRequestBody | None = None

# Operation: delete_call
class DeleteActivityCallIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Call activity to delete.")
class DeleteActivityCallIdRequest(StrictModel):
    """Permanently delete a Call activity record by its ID. This action cannot be undone and will remove all associated data."""
    path: DeleteActivityCallIdRequestPath

# Operation: list_created_activities
class GetActivityCreatedRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of activities to return in the response. Useful for pagination or limiting result set size.")
class GetActivityCreatedRequest(StrictModel):
    """Retrieve a list of all activities with Created status, optionally limiting the number of results returned."""
    query: GetActivityCreatedRequestQuery | None = None

# Operation: get_activity
class GetActivityCreatedIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Created activity record to retrieve.")
class GetActivityCreatedIdRequest(StrictModel):
    """Retrieve a single Created activity record by its unique identifier. Use this to fetch detailed information about a specific activity that was created."""
    path: GetActivityCreatedIdRequestPath

# Operation: list_email_activities
class GetActivityEmailRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of email activity records to return in the response. Limits the result set size for pagination or performance optimization.")
class GetActivityEmailRequest(StrictModel):
    """Retrieve a list of email activities, with each result representing a single email message. Optionally filter results by specifying a maximum number of records to return."""
    query: GetActivityEmailRequestQuery | None = None

# Operation: create_activity_email
class PostActivityEmailRequestBody(StrictModel):
    status: Literal["inbox", "draft", "scheduled", "outbox", "sent"] = Field(default=..., description="The email's status: use 'inbox' to log received emails, 'draft' to create editable drafts, 'scheduled' to send at a future time, 'outbox' to send immediately, or 'sent' to log already-sent emails.")
    sender: str | None = Field(default=None, description="Sender's name and email address in the format 'Name <email@example.com>'. Required when status is inbox, scheduled, outbox, or sent.")
    followup_date: str | None = Field(default=None, description="ISO 8601 date-time for scheduling a follow-up task if no response is received. Only applicable for scheduled, outbox, or sent emails.", json_schema_extra={'format': 'date-time'})
    template_id: str | None = Field(default=None, description="ID of an email template to render server-side. When using a template, do not include body_text or body_html parameters.")
    attachments: list[PostActivityEmailBodyAttachmentsItem] | None = Field(default=None, description="List of file attachments. All files must be pre-uploaded via the Files API before referencing them here.")
    lead_id: str = Field(default=..., description="The unique identifier of the lead associated with this email activity.")
    subject: str | None = Field(default=None, description="The subject line of the email.")
    to: list[str] | None = Field(default=None, description="Array of recipient email addresses.")
class PostActivityEmailRequest(StrictModel):
    """Create a new email activity with a specified status to log received emails, create drafts, schedule future sends, send immediately, or record already-sent emails. Only draft emails can be modified after creation."""
    body: PostActivityEmailRequestBody

# Operation: get_email_activity
class GetActivityEmailIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email activity record to retrieve.")
class GetActivityEmailIdRequest(StrictModel):
    """Retrieve a single email activity record by its unique identifier. Use this to fetch detailed information about a specific email interaction or communication event."""
    path: GetActivityEmailIdRequestPath

# Operation: update_email_activity
class PutActivityEmailIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email activity to update.")
class PutActivityEmailIdRequestBody(StrictModel):
    sender: str | None = Field(default=None, description="The sender email address. Required when changing the email status to scheduled or outbox if not already set on the email.")
    followup_date: str | None = Field(default=None, description="The date and time for an associated follow-up task, specified in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
class PutActivityEmailIdRequest(StrictModel):
    """Update a draft email activity or change its status to scheduled or outbox. When transitioning to scheduled or outbox status, the sender email address is required if not already set on the email."""
    path: PutActivityEmailIdRequestPath
    body: PutActivityEmailIdRequestBody | None = None

# Operation: delete_email_activity
class DeleteActivityEmailIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email activity record to delete.")
class DeleteActivityEmailIdRequest(StrictModel):
    """Permanently delete an email activity record by its unique identifier. This action cannot be undone and will remove all associated data."""
    path: DeleteActivityEmailIdRequestPath

# Operation: list_email_threads
class GetActivityEmailthreadRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of email threads to return in the response. Limits the result set size for pagination or performance optimization.")
class GetActivityEmailthreadRequest(StrictModel):
    """Retrieve a list of email thread activities, where each thread represents a single email conversation typically grouped by subject line."""
    query: GetActivityEmailthreadRequestQuery | None = None

# Operation: get_email_thread
class GetActivityEmailthreadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email thread activity to retrieve.")
class GetActivityEmailthreadIdRequest(StrictModel):
    """Retrieve a specific email thread activity by its unique identifier. Use this to fetch detailed information about a single email thread record."""
    path: GetActivityEmailthreadIdRequestPath

# Operation: delete_email_thread
class DeleteActivityEmailthreadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email thread activity to delete.")
class DeleteActivityEmailthreadIdRequest(StrictModel):
    """Delete an email thread activity and all associated email activities within that thread. This is a permanent operation that removes the entire thread conversation."""
    path: DeleteActivityEmailthreadIdRequestPath

# Operation: list_lead_status_changes
class GetActivityStatusChangeLeadRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of lead status change records to return in the response. Useful for pagination or limiting result set size.")
class GetActivityStatusChangeLeadRequest(StrictModel):
    """Retrieve a list of all lead status change activities, with optional filtering by result limit. Use this to track when and how lead statuses have been modified."""
    query: GetActivityStatusChangeLeadRequestQuery | None = None

# Operation: log_lead_status_change
class PostActivityStatusChangeLeadRequestBody(StrictModel):
    new_status_id: str | None = Field(default=None, description="The ID of the lead status after the change. Required to document what status the lead transitioned to.")
    old_status_id: str | None = Field(default=None, description="The ID of the lead status before the change. Required to document what status the lead transitioned from.")
class PostActivityStatusChangeLeadRequest(StrictModel):
    """Log a historical lead status change event in the activity feed without modifying the lead's current status. Use this operation to import status change records from external systems or organizations."""
    body: PostActivityStatusChangeLeadRequestBody | None = None

# Operation: get_lead_status_change
class GetActivityStatusChangeLeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the lead status change activity record to retrieve.")
class GetActivityStatusChangeLeadIdRequest(StrictModel):
    """Retrieve details of a specific lead status change activity, including when and how the lead's status was modified."""
    path: GetActivityStatusChangeLeadIdRequestPath

# Operation: delete_lead_status_change
class DeleteActivityStatusChangeLeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the LeadStatusChange activity record to delete.")
class DeleteActivityStatusChangeLeadIdRequest(StrictModel):
    """Remove a status change event from a lead's activity history. This deletes the activity record without affecting the lead's current status, useful when a status change event is outdated or causing sync issues with external systems."""
    path: DeleteActivityStatusChangeLeadIdRequestPath

# Operation: search_meetings
class GetActivityMeetingRequestQuery(StrictModel):
    provider_calendar_event_id: str | None = Field(default=None, description="The unique event identifier from the calendar provider (e.g., Google Calendar or Microsoft Outlook) that the meeting was synced from. Required when searching by any other calendar provider field.")
    provider_calendar_id: str | None = Field(default=None, description="The calendar identifier from the provider where the meeting event is stored.")
    provider_calendar_type: Literal["google", "microsoft"] | None = Field(default=None, description="The calendar service provider type. Supported providers are Google Calendar or Microsoft Outlook.")
class GetActivityMeetingRequest(StrictModel):
    """Search for meetings by their synced calendar provider information, including event ID, calendar ID, provider type, and start time."""
    query: GetActivityMeetingRequestQuery | None = None

# Operation: get_meeting
class GetActivityMeetingIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Meeting activity to retrieve.")
class GetActivityMeetingIdRequest(StrictModel):
    """Retrieve a specific Meeting activity by its unique identifier. Use this to fetch details about a scheduled or completed meeting."""
    path: GetActivityMeetingIdRequestPath

# Operation: update_meeting
class PutActivityMeetingIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Meeting activity to update.")
class PutActivityMeetingIdRequestBody(StrictModel):
    user_note_html: str | None = Field(default=None, description="Rich text HTML content for meeting notes. Allows formatted text documentation of meeting details and discussions.")
    outcome_id: str | None = Field(default=None, description="Custom outcome identifier to associate with the meeting, linking the meeting to a specific result or resolution.")
class PutActivityMeetingIdRequest(StrictModel):
    """Update a Meeting activity by modifying its notes or associated outcome. Use this to record meeting notes in rich text format or link the meeting to a specific outcome."""
    path: PutActivityMeetingIdRequestPath
    body: PutActivityMeetingIdRequestBody | None = None

# Operation: delete_meeting
class DeleteActivityMeetingIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Meeting activity to delete.")
class DeleteActivityMeetingIdRequest(StrictModel):
    """Permanently delete a specific Meeting activity by its ID. This action cannot be undone and will remove all associated data."""
    path: DeleteActivityMeetingIdRequestPath

# Operation: create_or_update_meeting_integration
class PostActivityMeetingIdIntegrationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the meeting activity to integrate with a third-party service.")
class PostActivityMeetingIdIntegrationRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The integration configuration payload. Submit an empty JSON object to perform no action, or include integration details to create or update the integration.")
class PostActivityMeetingIdIntegrationRequest(StrictModel):
    """Create a new third-party meeting integration or update an existing one for a specific meeting activity. This operation is only available to OAuth applications and allows third-party services to be presented as tabs in the activity feed."""
    path: PostActivityMeetingIdIntegrationRequestPath
    body: PostActivityMeetingIdIntegrationRequestBody

# Operation: list_notes
class GetActivityNoteRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of note records to return in the response. Useful for pagination or limiting result set size.")
class GetActivityNoteRequest(StrictModel):
    """Retrieve a list of all Note activities, with optional filtering by result count. Use this to view note records across your activity stream."""
    query: GetActivityNoteRequestQuery | None = None

# Operation: create_note
class PostActivityNoteRequestBody(StrictModel):
    lead_id: str = Field(default=..., description="The lead ID to associate this note with. Required to link the note to a specific lead record.")
    note_html: str | None = Field(default=None, description="Rich-text note content using a subset of HTML tags. When both note_html and note are provided, note_html takes precedence.")
    pinned: bool | None = Field(default=None, description="Whether to pin this note for prominence. Set to true to pin or false to unpin.")
    attachments: list[PostActivityNoteBodyAttachmentsItem] | None = Field(default=None, description="List of file attachments to include with the note. Each attachment must include a URL (beginning with https://app.close.com/go/file/), filename, and content type. Files should be uploaded via the Files API first before referencing them here.")
class PostActivityNoteRequest(StrictModel):
    """Create a note activity associated with a lead. Notes support rich-text formatting, optional attachments, and can be pinned for visibility."""
    body: PostActivityNoteRequestBody

# Operation: get_note
class GetActivityNoteIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the note activity to retrieve.")
class GetActivityNoteIdRequest(StrictModel):
    """Retrieve a single note activity by its unique identifier. Use this to fetch detailed information about a specific note."""
    path: GetActivityNoteIdRequestPath

# Operation: update_note
class PutActivityNoteIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the note activity to update.")
class PutActivityNoteIdRequestBody(StrictModel):
    note_html: str | None = Field(default=None, description="Rich-text note content formatted with a subset of HTML tags. When both note_html and plain text note are provided, this field takes precedence.")
    pinned: bool | None = Field(default=None, description="Set to true to pin this note for visibility, or false to unpin it.")
    attachments: list[PutActivityNoteIdBodyAttachmentsItem] | None = Field(default=None, description="An ordered list of file attachments to associate with this note. Order is preserved as provided.")
class PutActivityNoteIdRequest(StrictModel):
    """Update an existing note activity, including its content, formatting, and pin status. Use note_html for rich-text content with HTML formatting, which takes precedence over plain text if both are provided."""
    path: PutActivityNoteIdRequestPath
    body: PutActivityNoteIdRequestBody | None = None

# Operation: delete_activity_note
class DeleteActivityNoteIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Note activity to delete.")
class DeleteActivityNoteIdRequest(StrictModel):
    """Permanently delete a Note activity by its ID. This action cannot be undone and will remove all associated data."""
    path: DeleteActivityNoteIdRequestPath

# Operation: list_opportunity_status_changes
class GetActivityStatusChangeOpportunityRequestQuery(StrictModel):
    opportunity_id: str | None = Field(default=None, description="Filter results to show status changes for a specific opportunity by its ID.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Limit the number of results returned in the response.")
class GetActivityStatusChangeOpportunityRequest(StrictModel):
    """Retrieve a list of status change activities for opportunities, with optional filtering by opportunity ID and result limiting."""
    query: GetActivityStatusChangeOpportunityRequestQuery | None = None

# Operation: log_opportunity_status_change
class PostActivityStatusChangeOpportunityRequestBody(StrictModel):
    opportunity_id: str | None = Field(default=None, description="The unique identifier of the opportunity associated with this status change event.")
    new_status_id: str | None = Field(default=None, description="The unique identifier of the opportunity status that was transitioned to.")
    old_status_id: str | None = Field(default=None, description="The unique identifier of the opportunity status that was transitioned from.")
class PostActivityStatusChangeOpportunityRequest(StrictModel):
    """Log a historical opportunity status change event in the activity feed without modifying the actual opportunity status. Use this operation to import status change records from external systems or organizations."""
    body: PostActivityStatusChangeOpportunityRequestBody | None = None

# Operation: get_opportunity_status_change
class GetActivityStatusChangeOpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the OpportunityStatusChange activity record to retrieve.")
class GetActivityStatusChangeOpportunityIdRequest(StrictModel):
    """Retrieve details of a specific opportunity status change activity, including what changed and when the transition occurred."""
    path: GetActivityStatusChangeOpportunityIdRequestPath

# Operation: delete_opportunity_status_change
class DeleteActivityStatusChangeOpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the OpportunityStatusChange activity record to delete.")
class DeleteActivityStatusChangeOpportunityIdRequest(StrictModel):
    """Remove a status change activity from an opportunity's activity feed. This deletion does not alter the opportunity's current status—it only removes the historical status change event, useful when the activity is irrelevant or causing integration conflicts."""
    path: DeleteActivityStatusChangeOpportunityIdRequestPath

# Operation: list_sms_activities
class GetActivitySmsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of SMS activities to return in the response. Limits the result set size for pagination or performance optimization.")
class GetActivitySmsRequest(StrictModel):
    """Retrieve a list of SMS activities, including MMS messages with attachments. Attachments contain metadata (URL, filename, size, content type) and optional thumbnails; accessing URLs requires an authenticated session."""
    query: GetActivitySmsRequestQuery | None = None

# Operation: create_sms_activity
class PostActivitySmsRequestQuery(StrictModel):
    send_to_inbox: bool | None = Field(default=None, description="When creating an SMS with inbox status, set to true to automatically generate a corresponding Inbox Notification for the SMS.")
class PostActivitySmsRequestBody(StrictModel):
    status: Literal["inbox", "draft", "scheduled", "outbox", "sent"] = Field(default=..., description="The current status of the SMS activity. Use inbox to log a received SMS, draft to create an editable SMS, scheduled to send at a future date/time, outbox to send immediately, or sent to log an already-sent SMS.")
    template_id: str | None = Field(default=None, description="The ID of an SMS template to use as the content for this activity instead of providing raw text.")
    remote_phone: str | None = Field(default=None, description="The remote phone number for the SMS recipient (when sending) or sender (when receiving).")
class PostActivitySmsRequest(StrictModel):
    """Create an SMS activity to log, draft, schedule, or send SMS messages. Only draft SMS activities can be modified after creation."""
    query: PostActivitySmsRequestQuery | None = None
    body: PostActivitySmsRequestBody

# Operation: get_sms_activity
class GetActivitySmsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS activity record to retrieve.")
class GetActivitySmsIdRequest(StrictModel):
    """Retrieve detailed information about a specific SMS activity by its unique identifier. Use this to fetch the complete record of a single SMS message or communication event."""
    path: GetActivitySmsIdRequestPath

# Operation: update_sms_activity
class PutActivitySmsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS activity to update.")
class PutActivitySmsIdRequest(StrictModel):
    """Update an SMS activity to modify its content, schedule delivery, or send it immediately. Only draft SMS activities can be modified; use status to control whether the SMS is sent immediately (outbox) or scheduled for later delivery (scheduled)."""
    path: PutActivitySmsIdRequestPath

# Operation: delete_sms_activity
class DeleteActivitySmsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS activity record to delete.")
class DeleteActivitySmsIdRequest(StrictModel):
    """Permanently delete a specific SMS activity record by its unique identifier. This action cannot be undone and will remove all associated data."""
    path: DeleteActivitySmsIdRequestPath

# Operation: list_completed_activities
class GetActivityTaskCompletedRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of completed activities to return in the response. Must be at least 1.", ge=1)
class GetActivityTaskCompletedRequest(StrictModel):
    """Retrieve a list of completed task activities, with optional filtering by result count. Use this to view historical task completion records."""
    query: GetActivityTaskCompletedRequestQuery | None = None

# Operation: get_completed_task
class GetActivityTaskCompletedIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the completed task activity to retrieve.")
class GetActivityTaskCompletedIdRequest(StrictModel):
    """Retrieve a single completed task activity by its unique identifier. Use this to fetch details about a specific task that has been marked as completed."""
    path: GetActivityTaskCompletedIdRequestPath

# Operation: delete_completed_task
class DeleteActivityTaskCompletedIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the completed task activity to delete.")
class DeleteActivityTaskCompletedIdRequest(StrictModel):
    """Permanently remove a completed task activity from the system. This action cannot be undone and will delete the TaskCompleted activity record and all associated data."""
    path: DeleteActivityTaskCompletedIdRequestPath

# Operation: list_lead_merges
class GetActivityLeadMergeRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return in a single response. Limits the size of the result set.")
class GetActivityLeadMergeRequest(StrictModel):
    """Retrieve a list of LeadMerge activities, which are created when one lead is merged into another. The source lead is deleted after being merged into the destination lead."""
    query: GetActivityLeadMergeRequestQuery | None = None

# Operation: get_lead_merge
class GetActivityLeadMergeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the LeadMerge activity to retrieve.")
class GetActivityLeadMergeIdRequest(StrictModel):
    """Retrieve a single LeadMerge activity by its ID. Use this to fetch details about a specific lead merge operation."""
    path: GetActivityLeadMergeIdRequestPath

# Operation: list_whatsapp_messages
class GetActivityWhatsappMessageRequestQuery(StrictModel):
    external_whatsapp_message_id: str | None = Field(default=None, description="Filter results to a specific WhatsApp message by its external message ID. Useful for locating a message in Close that corresponds to a WhatsApp message that was updated or deleted.")
class GetActivityWhatsappMessageRequest(StrictModel):
    """Retrieve WhatsApp message activities from Close, optionally filtered by external WhatsApp message ID. Use this to sync message updates or deletions that occurred in WhatsApp."""
    query: GetActivityWhatsappMessageRequestQuery | None = None

# Operation: create_whatsapp_message
class PostActivityWhatsappMessageRequestQuery(StrictModel):
    send_to_inbox: bool | None = Field(default=None, description="Set to true when creating an incoming WhatsApp message to automatically generate a corresponding inbox notification.")
class PostActivityWhatsappMessageRequestBody(StrictModel):
    external_whatsapp_message_id: str = Field(default=..., description="The unique identifier of the message within WhatsApp. Used to track and filter message updates or deletions.")
    message_markdown: str = Field(default=..., description="The message content formatted in WhatsApp Markdown syntax. The system will automatically convert this to HTML for display.")
    attachments: list[PostActivityWhatsappMessageBodyAttachmentsItem] | None = Field(default=None, description="Array of file attachments to include with the message. Files must be pre-uploaded via the Files API. The combined size of all attachments cannot exceed 25MB.")
    integration_link: str | None = Field(default=None, description="Optional URL pointing back to this message in the external system where it was created, enabling cross-system navigation.", json_schema_extra={'format': 'uri'})
    response_to_id: str | None = Field(default=None, description="The Close activity ID of the WhatsApp message this message is replying to (use the Close activity ID starting with 'acti_', not the WhatsApp native message ID).")
class PostActivityWhatsappMessageRequest(StrictModel):
    """Create a new WhatsApp message activity linked to a Close contact or lead. Supports WhatsApp Markdown formatted text and file attachments (up to 25MB total). Incoming messages can automatically generate inbox notifications."""
    query: PostActivityWhatsappMessageRequestQuery | None = None
    body: PostActivityWhatsappMessageRequestBody

# Operation: get_whatsapp_message
class GetActivityWhatsappMessageIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the WhatsApp message activity to retrieve.")
class GetActivityWhatsappMessageIdRequest(StrictModel):
    """Retrieve a specific WhatsApp message activity by its unique identifier. Use this to fetch details about a single WhatsApp message interaction."""
    path: GetActivityWhatsappMessageIdRequestPath

# Operation: update_whatsapp_message
class PutActivityWhatsappMessageIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the WhatsApp message activity to update.")
class PutActivityWhatsappMessageIdRequestBody(StrictModel):
    message_markdown: str | None = Field(default=None, description="The message body formatted in WhatsApp Markdown syntax for rich text formatting.")
    attachments: list[PutActivityWhatsappMessageIdBodyAttachmentsItem] | None = Field(default=None, description="Array of file attachments to include with the message. Order is preserved as provided.")
    integration_link: str | None = Field(default=None, description="A URL that links back to this message in the external system. Must be a valid URI format.", json_schema_extra={'format': 'uri'})
class PutActivityWhatsappMessageIdRequest(StrictModel):
    """Update an existing WhatsApp message activity by its ID. Modify the message content, attachments, or external system link."""
    path: PutActivityWhatsappMessageIdRequestPath
    body: PutActivityWhatsappMessageIdRequestBody | None = None

# Operation: delete_whatsapp_message
class DeleteActivityWhatsappMessageIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the WhatsApp message activity to delete.")
class DeleteActivityWhatsappMessageIdRequest(StrictModel):
    """Delete a WhatsApp message activity by its ID. This removes the activity record from the system."""
    path: DeleteActivityWhatsappMessageIdRequestPath

# Operation: list_form_submissions
class GetActivityFormSubmissionRequestQuery(StrictModel):
    organization_id: str | None = Field(default=None, description="Filter results to form submissions within a specific organization.")
    form_id: str | None = Field(default=None, description="Filter results to submissions from a specific form by its ID.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return in the response. Use to control pagination.")
class GetActivityFormSubmissionRequest(StrictModel):
    """Retrieve a list of form submission activities, with optional filtering by organization and specific form(s). Supports pagination to control result size."""
    query: GetActivityFormSubmissionRequestQuery | None = None

# Operation: get_form_submission
class GetActivityFormSubmissionIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the form submission activity to retrieve.")
class GetActivityFormSubmissionIdRequest(StrictModel):
    """Retrieve a single form submission activity by its unique identifier. Use this to fetch details about a specific form submission event."""
    path: GetActivityFormSubmissionIdRequestPath

# Operation: delete_form_submission
class DeleteActivityFormSubmissionIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the FormSubmission activity to delete.")
class DeleteActivityFormSubmissionIdRequest(StrictModel):
    """Delete a FormSubmission activity by its ID. This operation permanently removes the form submission record from the system."""
    path: DeleteActivityFormSubmissionIdRequestPath

# Operation: list_opportunities
class GetOpportunityRequestQuery(StrictModel):
    status_type: Literal["active", "won", "lost"] | None = Field(default=None, description="Filter opportunities by status. Accepts one or multiple values: active, won, or lost.")
    date_won__lte: str | None = Field(default=None, description="Filter to opportunities won on or before a specific date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    date_won__gte: str | None = Field(default=None, description="Filter to opportunities won on or after a specific date (ISO 8601 format).", json_schema_extra={'format': 'date-time'})
    value_period: Literal["one_time", "monthly", "annual"] | None = Field(default=None, description="Filter opportunities by value period type. Accepts one or multiple values: one_time, monthly, or annual.")
    order_by: Literal["date_won", "-date_won", "date_updated", "-date_updated", "date_created", "-date_created", "confidence", "-confidence", "user_name", "-user_name", "value", "-value", "annualized_value", "-annualized_value", "annualized_expected_value", "-annualized_expected_value"] | None = Field(default=None, validation_alias="_order_by", serialization_alias="_order_by", description="Sort results by a specified field. Supported fields: date_won, date_updated, date_created, confidence, user_name, value, annualized_value, or annualized_expected_value. Prepend a minus sign for descending order.")
    group_by: Literal["user_id", "-user_id", "date_won__week", "-date_won__week", "date_won__month", "-date_won__month", "date_won__quarter", "-date_won__quarter", "date_won__year", "-date_won__year"] | None = Field(default=None, validation_alias="_group_by", serialization_alias="_group_by", description="Group results by the specified criteria: user_id, or date_won by week, month, quarter, or year. Prepend a minus sign to reverse the group order.")
    lead_saved_search_id: str | None = Field(default=None, description="Filter opportunities by a saved lead search (Smart View) ID.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of results to return in the response.")
class GetOpportunityRequest(StrictModel):
    """Retrieve and filter opportunities with optional filtering by status, dates, value period, and lead. Returns aggregated metrics for all matching opportunities, with support for sorting and grouping."""
    query: GetOpportunityRequestQuery | None = None

# Operation: create_opportunity
class PostOpportunityRequestBody(StrictModel):
    date_won: str | None = Field(default=None, description="The date when the opportunity was successfully closed and won, specified in date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    confidence: int | None = Field(default=None, description="The likelihood of winning this opportunity, expressed as a percentage between 0 and 100.")
    value_period: Literal["one_time", "monthly", "annual"] | None = Field(default=None, description="The billing frequency for the opportunity value: one-time payment, monthly recurring, or annual recurring.")
class PostOpportunityRequest(StrictModel):
    """Create a new sales opportunity. If no lead is associated, a new lead will be automatically created for this opportunity."""
    body: PostOpportunityRequestBody | None = None

# Operation: get_opportunity
class GetOpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the opportunity to retrieve.")
class GetOpportunityIdRequest(StrictModel):
    """Retrieve a single opportunity by its unique identifier. Use this to fetch detailed information about a specific opportunity."""
    path: GetOpportunityIdRequestPath

# Operation: update_opportunity
class PutOpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the opportunity to update.")
class PutOpportunityIdRequestBody(StrictModel):
    date_won: str | None = Field(default=None, description="The date when the opportunity was won, specified in date format. If not provided and the status is set to won, this will automatically be set to today's date.", json_schema_extra={'format': 'date'})
    confidence: int | None = Field(default=None, description="The confidence level for this opportunity, expressed as a percentage between 0 and 100.")
    value_period: Literal["one_time", "monthly", "annual"] | None = Field(default=None, description="The billing period for the opportunity value. Choose from one-time, monthly, or annual.")
class PutOpportunityIdRequest(StrictModel):
    """Update an existing opportunity's details. When the status is set to a won status, the date_won will automatically be set to today if not explicitly provided."""
    path: PutOpportunityIdRequestPath
    body: PutOpportunityIdRequestBody | None = None

# Operation: delete_opportunity
class DeleteOpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the opportunity to delete.")
class DeleteOpportunityIdRequest(StrictModel):
    """Permanently remove an opportunity from the system. This action cannot be undone and will delete all associated data."""
    path: DeleteOpportunityIdRequestPath

# Operation: list_tasks
class GetTaskRequestQuery(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Filter results to a specific task by its unique identifier.")
    view: Literal["inbox", "future", "archive"] | None = Field(default=None, description="Use a convenience view to quickly access tasks by status: inbox for incomplete tasks due by end of day, future for incomplete tasks starting tomorrow, or archive for completed tasks only.")
    order_by: Literal["date", "-date", "date_created", "-date_created"] | None = Field(default=None, validation_alias="_order_by", serialization_alias="_order_by", description="Sort results by task date or creation date in ascending or descending order. Prepend a minus sign for descending order (e.g., -date for newest first).")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Limit the number of results returned. Must be at least 1.", ge=1)
class GetTaskRequest(StrictModel):
    """Retrieve and filter tasks with support for convenient views and sorting. By default, only lead-type tasks are returned unless filtering by a specific task type."""
    query: GetTaskRequestQuery | None = None

# Operation: create_task
class PostTaskRequestBody(StrictModel):
    type_: Literal["lead", "outgoing_call"] = Field(default=..., validation_alias="_type", serialization_alias="_type", description="The category of task to create. Choose either 'lead' for lead follow-up tasks or 'outgoing_call' for call scheduling tasks.")
    date: str | None = Field(default=None, description="Optional date or date-time when this task should become actionable. Accepts dates in ISO 8601 format (e.g., YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss±HH:mm).")
class PostTaskRequest(StrictModel):
    """Create a new task for follow-up actions. Supports lead and outgoing call task types, with optional scheduling for when the task becomes actionable."""
    body: PostTaskRequestBody

# Operation: update_tasks
class PutTaskRequestQuery(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Filter tasks by their unique identifier. Only tasks matching this ID will be updated.")
class PutTaskRequestBody(StrictModel):
    is_complete: bool | None = Field(default=None, description="Mark the task as complete or incomplete. Set to true to mark as done, false to mark as pending.")
    assigned_to: str | None = Field(default=None, description="Reassign the task to a different user by specifying their user ID.")
    date: str | None = Field(default=None, description="Set when the task becomes actionable. Accepts a date or full date-time value in ISO 8601 format.")
class PutTaskRequest(StrictModel):
    """Bulk-update multiple tasks matching specified filters. Allows updating task completion status, assignment, and actionable date across matching records in a single operation."""
    query: PutTaskRequestQuery | None = None
    body: PutTaskRequestBody | None = None

# Operation: get_task
class GetTaskIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the task to retrieve.")
class GetTaskIdRequest(StrictModel):
    """Retrieve detailed information about a specific task by its unique identifier."""
    path: GetTaskIdRequestPath

# Operation: update_task
class PutTaskIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the task to update.")
class PutTaskIdRequestBody(StrictModel):
    date: str | None = Field(default=None, description="The date or date-time when the task becomes actionable, specified in ISO 8601 format (e.g., YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss±HH:mm).")
class PutTaskIdRequest(StrictModel):
    """Update an existing task's properties. You can modify the assignee, due date, and completion status on any task. For lead-type tasks, you can also update the task description text."""
    path: PutTaskIdRequestPath
    body: PutTaskIdRequestBody | None = None

# Operation: delete_task
class DeleteTaskIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the task to delete.")
class DeleteTaskIdRequest(StrictModel):
    """Permanently delete a task by its ID. This action cannot be undone and will remove all associated data."""
    path: DeleteTaskIdRequestPath

# Operation: create_outcome
class PostOutcomeRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for this outcome, shown to users whenever they can select or assign outcomes to interactions.")
    applies_to: list[Literal["calls", "meetings"]] = Field(default=..., description="Specifies which interaction types this outcome can be assigned to. Include 'calls', 'meetings', or both as an array of values.")
    description: str | None = Field(default=None, description="Optional explanation of what this outcome represents and the circumstances under which it should be used, helping users apply it correctly.")
class PostOutcomeRequest(StrictModel):
    """Create a new outcome for your organization that can be assigned to calls, meetings, or both. Outcomes help track and categorize interactions, with optional automatic assignment for voicemail drops."""
    body: PostOutcomeRequestBody

# Operation: get_outcome
class GetOutcomeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the outcome to retrieve.")
class GetOutcomeIdRequest(StrictModel):
    """Retrieve a single outcome by its unique identifier. Use this to fetch detailed information about a specific outcome."""
    path: GetOutcomeIdRequestPath

# Operation: update_outcome
class PutOutcomeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the outcome to update.")
class PutOutcomeIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the outcome.")
    description: str | None = Field(default=None, description="The new description for the outcome.")
class PutOutcomeIdRequest(StrictModel):
    """Update an existing outcome by modifying its name, description, applicable channels, or type. Specify which channels the outcome applies to (calls, meetings) and choose between a predefined vm-dropped type or a custom type."""
    path: PutOutcomeIdRequestPath
    body: PutOutcomeIdRequestBody | None = None

# Operation: delete_outcome
class DeleteOutcomeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the outcome to delete.")
class DeleteOutcomeIdRequest(StrictModel):
    """Delete an existing outcome from the system. Associated calls and meetings will retain their references to this outcome, but it will no longer be available for assignment to new calls or meetings."""
    path: DeleteOutcomeIdRequestPath

# Operation: update_membership
class PutMembershipIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the membership to update.")
class PutMembershipIdRequestBody(StrictModel):
    role_id: Literal["admin", "superuser", "user", "restricteduser"] | None = Field(default=None, description="The role to assign to this membership. Choose from predefined roles (admin, superuser, user, restricteduser) or provide a custom Role ID.")
    auto_record_calls: Literal["unset", "disabled", "enabled"] | None = Field(default=None, description="Automatic call recording preference. Set to 'enabled' to record calls automatically, 'disabled' to prevent recording, or 'unset' to use the default behavior.")
class PutMembershipIdRequest(StrictModel):
    """Update a membership's role and call recording settings. Modify the assigned role (admin, superuser, user, restricteduser, or custom) and configure whether calls are automatically recorded."""
    path: PutMembershipIdRequestPath
    body: PutMembershipIdRequestBody | None = None

# Operation: provision_membership
class PostMembershipRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address of the user to provision. Must be a valid email format.", json_schema_extra={'format': 'email'})
    role_id: str = Field(default=..., description="The role to assign to the user. Use one of the predefined roles ('admin', 'superuser', 'user', 'restricteduser') or provide a custom Role ID.")
class PostMembershipRequest(StrictModel):
    """Provision or activate a membership for a user by email address. If the user exists, they are added to your organization; if new, a user account is created. Requires 'Manage Organization' permissions and OAuth authentication."""
    body: PostMembershipRequestBody

# Operation: bulk_update_memberships
class PutMembershipRequestQuery(StrictModel):
    id__in: str = Field(default=..., description="Comma-separated list of membership IDs to update. All specified memberships will be modified with the provided field values.")
class PutMembershipRequestBody(StrictModel):
    role_id: Literal["admin", "superuser", "user", "restricteduser"] | None = Field(default=None, description="Assign a role to the memberships. Valid roles are: admin, superuser, user, or restricteduser.")
    auto_record_calls: Literal["unset", "disabled", "enabled"] | None = Field(default=None, description="Control automatic call recording for the memberships. Set to enabled to record calls automatically, disabled to prevent recording, or unset to use default behavior.")
class PutMembershipRequest(StrictModel):
    """Bulk update multiple memberships at once by specifying their IDs and the fields to modify. Supports updating role assignments and call recording settings across multiple memberships in a single request."""
    query: PutMembershipRequestQuery
    body: PutMembershipRequestBody | None = None

# Operation: list_pinned_views
class GetMembershipIdPinnedViewsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the membership whose pinned views should be retrieved.")
class GetMembershipIdPinnedViewsRequest(StrictModel):
    """Retrieve the ordered list of pinned views for a specific membership. The views are returned in their pinned order."""
    path: GetMembershipIdPinnedViewsRequestPath

# Operation: set_membership_pinned_views
class PutMembershipIdPinnedViewsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the membership whose pinned views should be updated.")
class PutMembershipIdPinnedViewsRequestBody(StrictModel):
    body: list[dict[str, Any]] = Field(default=..., description="An ordered list of view identifiers to pin for this membership. The order determines the display sequence, and providing this list will completely replace any existing pinned views.")
class PutMembershipIdPinnedViewsRequest(StrictModel):
    """Update the pinned views for a membership by providing an ordered list that completely replaces the current pinned views configuration."""
    path: PutMembershipIdPinnedViewsRequestPath
    body: PutMembershipIdPinnedViewsRequestBody

# Operation: get_user
class GetUserIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier that corresponds to the user record you want to retrieve.")
class GetUserIdRequest(StrictModel):
    """Retrieve a single user by their unique identifier. Returns the user's profile information and details."""
    path: GetUserIdRequestPath

# Operation: list_users
class GetUserRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of user records to return in the response. Use this to control pagination and response size.")
class GetUserRequest(StrictModel):
    """Retrieve all users who are members of your organizations. This returns a filtered list based on your organization memberships."""
    query: GetUserRequestQuery | None = None

# Operation: list_user_availability
class GetUserAvailabilityRequestQuery(StrictModel):
    organization_id: str | None = Field(default=None, description="Filter availability results to a specific organization. When omitted, returns availability for all accessible organizations.")
class GetUserAvailabilityRequest(StrictModel):
    """Retrieve the current availability status of all users in an organization, including details about any active calls they are participating in."""
    query: GetUserAvailabilityRequestQuery | None = None

# Operation: get_organization
class GetOrganizationIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the organization to retrieve.")
class GetOrganizationIdRequest(StrictModel):
    """Retrieve detailed information about an organization, including its members, inactive members, and associated lead and opportunity statuses. User data is flattened by default but can be nested using query expansion parameters."""
    path: GetOrganizationIdRequestPath

# Operation: update_organization
class PutOrganizationIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the organization to update.")
class PutOrganizationIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the organization.")
    currency: str | None = Field(default=None, description="The currency code for the organization (e.g., USD, EUR, GBP).")
    lead_statuses: list[dict[str, Any]] | None = Field(default=None, description="An ordered list of existing lead status identifiers to reorder the organization's lead pipeline. The order in this array determines the sequence of statuses in the workflow.")
class PutOrganizationIdRequest(StrictModel):
    """Update an organization's basic settings including name and currency, and reorder its lead status pipeline."""
    path: PutOrganizationIdRequestPath
    body: PutOrganizationIdRequestBody | None = None

# Operation: get_role
class GetRoleIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the role to retrieve.")
class GetRoleIdRequest(StrictModel):
    """Retrieve a single role by its unique identifier. Use this to fetch detailed information about a specific role."""
    path: GetRoleIdRequestPath

# Operation: create_role
class PostRoleRequestBody(StrictModel):
    visibility_user_lcf_ids: list[str] | None = Field(default=None, description="List of Lead Custom Field IDs that determine which leads users with this role can access. Leave empty if the role has the view_all_leads permission.")
    visibility_user_lcf_behavior: Literal["require_assignment", "allow_unassigned"] | None = Field(default=None, description="Determines how lead visibility is handled for leads without assigned users. Choose 'require_assignment' to hide unassigned leads or 'allow_unassigned' to show them. Leave empty if the role has the view_all_leads permission.")
    name: str = Field(default=..., description="The display name for this role.")
    permissions: list[str] | None = Field(default=None, description="List of permission strings that define what actions users with this role can perform.")
class PostRoleRequest(StrictModel):
    """Create a new role with customizable permissions and lead visibility settings. Lead visibility can be restricted to specific custom fields or granted universally based on role permissions."""
    body: PostRoleRequestBody

# Operation: update_role
class PutRoleRoleIdRequestPath(StrictModel):
    role_id: str = Field(default=..., description="The unique identifier of the role to update.")
class PutRoleRoleIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the role.")
    visibility_user_lcf_ids: list[str] | None = Field(default=None, description="A list of Lead Custom Field IDs that determine which leads are visible to users with this role. The order of IDs may affect visibility logic based on the configured behavior.")
    visibility_user_lcf_behavior: Literal["require_assignment", "allow_unassigned"] | None = Field(default=None, description="Controls how lead visibility is handled for leads without assigned users. Use 'require_assignment' to hide unassigned leads, or 'allow_unassigned' to show them regardless of assignment status.")
class PutRoleRoleIdRequest(StrictModel):
    """Update an existing role's properties, including its name and lead visibility settings based on custom field criteria."""
    path: PutRoleRoleIdRequestPath
    body: PutRoleRoleIdRequestBody | None = None

# Operation: delete_role
class DeleteRoleRoleIdRequestPath(StrictModel):
    role_id: str = Field(default=..., description="The unique identifier of the role to delete.")
class DeleteRoleRoleIdRequest(StrictModel):
    """Permanently remove a role from the system. All users currently assigned to this role must be reassigned to another role before deletion can proceed."""
    path: DeleteRoleRoleIdRequestPath

# Operation: create_lead_status
class PostStatusLeadRequestBody(StrictModel):
    label: str = Field(default=..., description="The display name for this lead status, shown in the UI and status selection dropdowns throughout the system.")
class PostStatusLeadRequest(StrictModel):
    """Create a new custom status that can be assigned to leads in your pipeline. This allows you to define custom workflow stages beyond the default statuses."""
    body: PostStatusLeadRequestBody

# Operation: rename_lead_status
class PutStatusLeadStatusIdRequestPath(StrictModel):
    status_id: str = Field(default=..., description="The unique identifier of the lead status to rename.")
class PutStatusLeadStatusIdRequestBody(StrictModel):
    name: str = Field(default=..., description="The new display name for the lead status.")
class PutStatusLeadStatusIdRequest(StrictModel):
    """Rename an existing lead status to update its display name. This operation modifies the status label itself, not the status of individual leads."""
    path: PutStatusLeadStatusIdRequestPath
    body: PutStatusLeadStatusIdRequestBody

# Operation: delete_lead_status
class DeleteStatusLeadStatusIdRequestPath(StrictModel):
    status_id: str = Field(default=..., description="The unique identifier of the lead status to delete.")
class DeleteStatusLeadStatusIdRequest(StrictModel):
    """Delete a lead status from the system. Ensure no leads are currently assigned to this status before deletion, as the operation will fail if leads depend on it."""
    path: DeleteStatusLeadStatusIdRequestPath

# Operation: create_opportunity_status
class PostStatusOpportunityRequestBody(StrictModel):
    label: str = Field(default=..., description="The display name for this opportunity status, used to identify it in the UI and reports.")
    status_type: Literal["active", "won", "lost"] = Field(default=..., description="The classification type for this status: active for ongoing opportunities, won for closed deals, or lost for deals that did not close.")
    pipeline_id: str | None = Field(default=None, description="Optional pipeline ID to scope this status to a specific pipeline; if omitted, the status will be available globally.")
class PostStatusOpportunityRequest(StrictModel):
    """Create a new opportunity status to track deal progression. Statuses can be classified as active, won, or lost, and can optionally be associated with a specific pipeline."""
    body: PostStatusOpportunityRequestBody

# Operation: rename_opportunity_status
class PutStatusOpportunityStatusIdRequestPath(StrictModel):
    status_id: str = Field(default=..., description="The unique identifier of the opportunity status to rename.")
class PutStatusOpportunityStatusIdRequestBody(StrictModel):
    label: str = Field(default=..., description="The new display name for the opportunity status that will be shown in the system.")
class PutStatusOpportunityStatusIdRequest(StrictModel):
    """Update the display name of an existing opportunity status. This allows you to change how a status appears throughout the system."""
    path: PutStatusOpportunityStatusIdRequestPath
    body: PutStatusOpportunityStatusIdRequestBody

# Operation: delete_opportunity_status
class DeleteStatusOpportunityStatusIdRequestPath(StrictModel):
    status_id: str = Field(default=..., description="The unique identifier of the opportunity status to delete.")
class DeleteStatusOpportunityStatusIdRequest(StrictModel):
    """Delete an opportunity status from the system. Ensure no opportunities are currently assigned this status before deletion."""
    path: DeleteStatusOpportunityStatusIdRequestPath

# Operation: create_pipeline
class PostPipelineRequestBody(StrictModel):
    name: str = Field(default=..., description="A unique identifier for the pipeline. This name is used to reference and manage the pipeline in subsequent operations.")
class PostPipelineRequest(StrictModel):
    """Create a new pipeline with the specified name. The pipeline serves as a container for organizing and executing workflow operations."""
    body: PostPipelineRequestBody

# Operation: update_pipeline
class PutPipelinePipelineIdRequestPath(StrictModel):
    pipeline_id: str = Field(default=..., description="The unique identifier of the pipeline to update.")
class PutPipelinePipelineIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name to assign to the pipeline.")
    statuses: list[PutPipelinePipelineIdBodyStatusesItem] | None = Field(default=None, description="An ordered list of opportunity status objects that defines the pipeline's status workflow. Each object must include an 'id' field referencing the status. The order of items in this list determines the sequence of statuses in the pipeline. You can reorder existing statuses or include statuses from other pipelines by their ID to move them into this pipeline.")
class PutPipelinePipelineIdRequest(StrictModel):
    """Update an existing pipeline by modifying its name, reordering opportunity statuses, or moving statuses from other pipelines into this one."""
    path: PutPipelinePipelineIdRequestPath
    body: PutPipelinePipelineIdRequestBody | None = None

# Operation: delete_pipeline
class DeletePipelinePipelineIdRequestPath(StrictModel):
    pipeline_id: str = Field(default=..., description="The unique identifier of the pipeline to delete.")
class DeletePipelinePipelineIdRequest(StrictModel):
    """Permanently delete a pipeline from your workspace. The pipeline must be empty of all opportunity statuses before deletion—migrate or remove any existing opportunity statuses first."""
    path: DeletePipelinePipelineIdRequestPath

# Operation: list_groups
class GetGroupRequestQuery(StrictModel):
    fields: str = Field(default=..., validation_alias="_fields", serialization_alias="_fields", description="Comma-separated list of group attributes to return in the response. Must include at least 'name' and 'members' to retrieve group membership data.")
class GetGroupRequest(StrictModel):
    """Retrieve all groups in your organization. Use the _fields parameter to specify which group attributes to return; to retrieve group members, include 'members' in your field selection."""
    query: GetGroupRequestQuery

# Operation: create_group
class PostGroupRequestQuery(StrictModel):
    fields: str = Field(default=..., validation_alias="_fields", serialization_alias="_fields", description="Comma-separated list of fields to include in the response. Must include at least 'name' and 'members'.")
class PostGroupRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the new group.")
class PostGroupRequest(StrictModel):
    """Create a new empty group with a specified name. Members can be added or removed after creation using the member endpoint."""
    query: PostGroupRequestQuery
    body: PostGroupRequestBody

# Operation: get_group
class GetGroupGroupIdRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group to retrieve.")
class GetGroupGroupIdRequestQuery(StrictModel):
    fields: str = Field(default=..., validation_alias="_fields", serialization_alias="_fields", description="Comma-separated list of fields to include in the response. Must include at least 'name' and 'members' to retrieve group name and member data.")
class GetGroupGroupIdRequest(StrictModel):
    """Retrieve a single group by its ID with specified fields. Returns group details including name and member information."""
    path: GetGroupGroupIdRequestPath
    query: GetGroupGroupIdRequestQuery

# Operation: rename_group
class PutGroupGroupIdRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group to update.")
class PutGroupGroupIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the group. Must be unique and cannot duplicate existing group names.")
class PutGroupGroupIdRequest(StrictModel):
    """Update a group's name. The new name must be unique across all groups in the system."""
    path: PutGroupGroupIdRequestPath
    body: PutGroupGroupIdRequestBody | None = None

# Operation: delete_group
class DeleteGroupGroupIdRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group to delete.")
class DeleteGroupGroupIdRequest(StrictModel):
    """Delete a group from the system. This operation is only permitted if the group is not referenced by any saved reports or smart views."""
    path: DeleteGroupGroupIdRequestPath

# Operation: add_user_to_group
class PostGroupGroupIdMemberRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group where the user will be added.")
class PostGroupGroupIdMemberRequestBody(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to add to the group.")
class PostGroupGroupIdMemberRequest(StrictModel):
    """Add a user to a group. If the user is already a member, the operation completes without changes."""
    path: PostGroupGroupIdMemberRequestPath
    body: PostGroupGroupIdMemberRequestBody

# Operation: remove_group_member
class DeleteGroupGroupIdMemberUserIdRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group from which the user will be removed.")
    user_id: str = Field(default=..., description="The unique identifier of the user to remove from the group.")
class DeleteGroupGroupIdMemberUserIdRequest(StrictModel):
    """Remove a user from a group. If the user is not currently a member, the operation completes without error."""
    path: DeleteGroupGroupIdMemberUserIdRequestPath

# Operation: generate_activity_report
class PostReportActivityRequestHeader(StrictModel):
    accept: Literal["application/json", "text/csv"] | None = Field(default=None, validation_alias="Accept", serialization_alias="Accept", description="Desired response format: JSON for structured data or CSV for spreadsheet export.")
class PostReportActivityRequestBodyQuery(StrictModel):
    saved_search_id: str | None = Field(default=None, validation_alias="saved_search_id", serialization_alias="saved_search_id", description="ID of a previously saved search configuration to apply filters and settings to this report.")
class PostReportActivityRequestBody(StrictModel):
    type_: Literal["overview", "comparison"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Report structure type: 'overview' aggregates metrics across the organization by time period, while 'comparison' breaks down metrics by individual users.")
    metrics: list[str] = Field(default=..., description="List of metric names to include in the report. Specify which data points should be calculated and returned.")
    relative_range: Literal["today", "this-week", "this-month", "this-quarter", "this-year", "yesterday", "last-week", "last-month", "last-quarter", "last-year", "all-time"] | None = Field(default=None, description="Relative time range for the report data, such as 'today', 'this-week', 'last-month', or 'all-time'. Use this or datetime_range, but not both.")
    users: list[str] | None = Field(default=None, description="List of user IDs to filter report results to specific users. When provided, only data for these users will be included.")
    query: PostReportActivityRequestBodyQuery | None = None
class PostReportActivityRequest(StrictModel):
    """Generate an activity report showing organizational metrics aggregated by time period (overview) or broken down by user (comparison). Reports can be returned as JSON or CSV format."""
    header: PostReportActivityRequestHeader | None = None
    body: PostReportActivityRequestBody

# Operation: list_sent_emails_report
class GetReportSentEmailsOrganizationIdRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization for which to retrieve the sent emails report.")
class GetReportSentEmailsOrganizationIdRequestQuery(StrictModel):
    date_start: str | None = Field(default=None, description="The start date for filtering the report period, specified in date format (YYYY-MM-DD). If provided, only emails sent on or after this date will be included.", json_schema_extra={'format': 'date'})
    date_end: str | None = Field(default=None, description="The end date for filtering the report period, specified in date format (YYYY-MM-DD). If provided, only emails sent on or before this date will be included.", json_schema_extra={'format': 'date'})
class GetReportSentEmailsOrganizationIdRequest(StrictModel):
    """Retrieve a report of sent emails grouped by template for a specific organization, optionally filtered by a date range."""
    path: GetReportSentEmailsOrganizationIdRequestPath
    query: GetReportSentEmailsOrganizationIdRequestQuery | None = None

# Operation: get_lead_status_report
class GetReportStatusesLeadOrganizationIdRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier for the organization whose lead status changes should be reported.")
class GetReportStatusesLeadOrganizationIdRequestQuery(StrictModel):
    date_start: str | None = Field(default=None, description="The start date for the report period in date format. If provided, only status changes on or after this date will be included.", json_schema_extra={'format': 'date'})
    date_end: str | None = Field(default=None, description="The end date for the report period in date format. If provided, only status changes on or before this date will be included.", json_schema_extra={'format': 'date'})
class GetReportStatusesLeadOrganizationIdRequest(StrictModel):
    """Retrieve a report of lead status changes for a specific organization, with optional filtering by date range to analyze lead progression over time."""
    path: GetReportStatusesLeadOrganizationIdRequestPath
    query: GetReportStatusesLeadOrganizationIdRequestQuery | None = None

# Operation: get_opportunity_status_report
class GetReportStatusesOpportunityOrganizationIdRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier of the organization for which to retrieve the opportunity status report.")
class GetReportStatusesOpportunityOrganizationIdRequestQuery(StrictModel):
    date_start: str | None = Field(default=None, description="The start date for the report period in date format (YYYY-MM-DD). If omitted, the report begins from the earliest available data.", json_schema_extra={'format': 'date'})
    date_end: str | None = Field(default=None, description="The end date for the report period in date format (YYYY-MM-DD). If omitted, the report extends to the current date.", json_schema_extra={'format': 'date'})
class GetReportStatusesOpportunityOrganizationIdRequest(StrictModel):
    """Retrieve a report of opportunity status changes for an organization over a specified period. Use this to track how opportunities progress through different stages."""
    path: GetReportStatusesOpportunityOrganizationIdRequestPath
    query: GetReportStatusesOpportunityOrganizationIdRequestQuery | None = None

# Operation: generate_custom_report
class GetReportCustomOrganizationIdRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The organization ID for which to generate the report.")
class GetReportCustomOrganizationIdRequestQuery(StrictModel):
    x: str | None = Field(default=None, description="The field to display on the X axis, using dot notation (e.g., 'lead.custom.MRR' or 'opportunity.date_created'). Can be a date field for time-based graphs or numeric field for numeric binning.")
    y: str | None = Field(default=None, description="The metric to display on the Y axis using dot notation (e.g., 'lead.count', 'call.duration', 'opportunity.value'). Must be a numeric field. Defaults to counting leads.")
    interval: Literal["auto", "hour", "day", "week", "month", "quarter", "year"] | None = Field(default=None, description="Controls how the X axis is divided into buckets. For time-based X fields, choose from hourly, daily, weekly, monthly, quarterly, or yearly intervals; 'auto' automatically selects the best interval. For numeric X fields, specify an integer interval size. Defaults to automatic selection.")
    transform_y: Literal["sum", "avg", "min", "max"] | None = Field(default=None, description="Aggregation function applied to Y values within each bucket: sum (total), avg (average), min (minimum), or max (maximum). Defaults to sum.")
    group_by: str | None = Field(default=None, description="Optional field name to split the report into separate series, one per unique value of this field.")
    start: str | None = Field(default=None, description="Start of the X axis range. For date fields, use ISO 8601 format; defaults to the organization's creation date. For numeric fields, provide the numeric start value.")
    end: str | None = Field(default=None, description="End of the X axis range. For date fields, use ISO 8601 format; defaults to the current date/time. For numeric fields, provide the numeric end value.")
class GetReportCustomOrganizationIdRequest(StrictModel):
    """Generate a custom report with arbitrary metrics for data visualization. Returns aggregated data suitable for graphing, supporting flexible field selection, time-based or numeric binning, and optional grouping by category."""
    path: GetReportCustomOrganizationIdRequestPath
    query: GetReportCustomOrganizationIdRequestQuery | None = None

# Operation: get_funnel_opportunity_totals
class PostReportFunnelOpportunityTotalsRequestHeader(StrictModel):
    accept: Literal["application/json", "text/csv"] | None = Field(default=None, description="Response format for the report data. Use application/json to receive both aggregated totals and per-user metrics, or text/csv to receive per-user data only.")
class PostReportFunnelOpportunityTotalsRequestBodyQuery(StrictModel):
    type_: Literal["saved_search"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The query type for filtering opportunities. Currently supports 'saved_search' to use a predefined saved search query.")
    saved_search_id: str | None = Field(default=None, validation_alias="saved_search_id", serialization_alias="saved_search_id", description="ID of a saved search to use for filtering opportunities in the report. Used when query.type is set to 'saved_search'.")
class PostReportFunnelOpportunityTotalsRequestBody(StrictModel):
    pipeline: str = Field(default=..., description="The pipeline ID that defines the funnel stages used to categorize and aggregate the opportunity data.")
    type_: Literal["created-cohort", "active-stage-cohort"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The report type determines how opportunities are grouped. Use 'created-cohort' to analyze opportunities by creation date, or 'active-stage-cohort' to analyze opportunities currently in specific pipeline stages.")
    report_datetime_range: dict[str, Any] | None = Field(default=None, description="Optional time range to filter the report data. Specify the period for which funnel metrics should be calculated.")
    cohort_datetime_range: dict[str, Any] | None = Field(default=None, description="Time range defining which opportunities to include in the cohort. Required when using 'created-cohort' report type (or provide cohort_relative_range instead). Ignored for 'active-stage-cohort' reports.")
    compared_datetime_range: Literal["same-days-last-week", "same-days-last-month", "same-days-last-quarter", "same-days-last-year"] | None = Field(default=None, description="Relative time range for comparison data, such as same period from previous week, month, quarter, or year. Only applicable when report_datetime_range or cohort_datetime_range is specified.")
    compared_custom_range: dict[str, Any] | None = Field(default=None, description="Custom absolute time range for comparison data. Use as an alternative to compared_datetime_range for specific comparison periods.")
    users: list[str] | None = Field(default=None, description="List of user IDs or group IDs to limit report results to specific team members or groups. Leave empty to include all available users in the aggregation.")
    query: PostReportFunnelOpportunityTotalsRequestBodyQuery | None = None
class PostReportFunnelOpportunityTotalsRequest(StrictModel):
    """Retrieve aggregated and per-user pipeline funnel metrics for selected opportunities. Returns totals data in JSON format with optional per-user breakdown, or CSV format for per-user data only."""
    header: PostReportFunnelOpportunityTotalsRequestHeader | None = None
    body: PostReportFunnelOpportunityTotalsRequestBody

# Operation: get_opportunity_funnel_stages_report
class PostReportFunnelOpportunityStagesRequestBodyQuery(StrictModel):
    type_: Literal["saved_search"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The query type for filtering; currently supports 'saved_search' to apply a predefined search filter.")
    saved_search_id: str | None = Field(default=None, validation_alias="saved_search_id", serialization_alias="saved_search_id", description="The ID of a saved search to filter report results. When specified, only opportunities matching the saved search criteria are included.")
class PostReportFunnelOpportunityStagesRequestBody(StrictModel):
    pipeline: str = Field(default=..., description="The pipeline ID that defines the funnel stages to report on.")
    type_: Literal["created-cohort", "active-stage-cohort"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The report type: 'created-cohort' tracks opportunities created within a cohort period, while 'active-stage-cohort' tracks opportunities currently in each stage.")
    report_datetime_range: dict[str, Any] | None = Field(default=None, description="The primary time range for the report data. Required for active-stage-cohort reports unless using a comparison range.")
    cohort_datetime_range: dict[str, Any] | None = Field(default=None, description="The time range defining which opportunities to include in the cohort. Required for created-cohort reports unless using a relative range. Ignored for active-stage-cohort reports.")
    compared_datetime_range: Literal["same-days-last-week", "same-days-last-month", "same-days-last-quarter", "same-days-last-year"] | None = Field(default=None, description="A relative time period to compare against the primary range: same days from the previous week, month, quarter, or year. Only valid when paired with report_datetime_range or cohort_datetime_range.")
    compared_custom_range: dict[str, Any] | None = Field(default=None, description="A custom time range for comparison data. Allows comparing against any specific period, not just relative ranges.")
    users: list[str] | None = Field(default=None, description="A list of user IDs or group IDs to limit results to. When empty or omitted, the report includes all available users.")
    query: PostReportFunnelOpportunityStagesRequestBodyQuery | None = None
class PostReportFunnelOpportunityStagesRequest(StrictModel):
    """Retrieve a funnel report showing pipeline metrics for opportunities aggregated by stage or per-user. Supports comparison against previous time periods and filtering by saved searches or specific users."""
    body: PostReportFunnelOpportunityStagesRequestBody

# Operation: list_email_templates
class GetEmailTemplateRequestQuery(StrictModel):
    is_archived: bool | None = Field(default=None, description="Filter results to show only archived templates (true), only active templates (false), or all templates regardless of status (omit parameter). Useful for managing template lifecycle.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Limit the number of templates returned in the response. Helps with pagination and controlling response size for large template collections.")
class GetEmailTemplateRequest(StrictModel):
    """Retrieve a list of email templates with optional filtering by archived status and pagination support. Use this to browse available templates for sending emails or managing template collections."""
    query: GetEmailTemplateRequestQuery | None = None

# Operation: create_email_template
class PostEmailTemplateRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="Email template configuration object containing template name, subject, body content, and any variable placeholders for dynamic content insertion.")
class PostEmailTemplateRequest(StrictModel):
    """Create a new email template that can be used for sending standardized emails. Define the template structure, content, and variables for reuse across email communications."""
    body: PostEmailTemplateRequestBody

# Operation: get_email_template
class GetEmailTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email template to retrieve.")
class GetEmailTemplateIdRequest(StrictModel):
    """Retrieve a specific email template by its unique identifier. Use this to fetch the full details of an email template for viewing or further processing."""
    path: GetEmailTemplateIdRequestPath

# Operation: update_email_template
class PutEmailTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email template to update.")
class PutEmailTemplateIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the email template.")
    subject: str | None = Field(default=None, description="The subject line that will appear in emails sent using this template.")
    body: str | None = Field(default=None, description="The HTML or plain text content of the email body.")
    is_shared: bool | None = Field(default=None, description="Whether this template is accessible to other members of your organization.")
    is_archived: bool | None = Field(default=None, description="Whether this template is archived and hidden from active template lists.")
class PutEmailTemplateIdRequest(StrictModel):
    """Update an existing email template by modifying its content, metadata, or organizational settings. Specify the template ID and provide any fields you want to change; omitted fields remain unchanged."""
    path: PutEmailTemplateIdRequestPath
    body: PutEmailTemplateIdRequestBody | None = None

# Operation: delete_email_template
class DeleteEmailTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email template to delete.")
class DeleteEmailTemplateIdRequest(StrictModel):
    """Permanently delete an email template by its ID. This action cannot be undone and will remove the template from all systems."""
    path: DeleteEmailTemplateIdRequestPath

# Operation: render_email_template
class GetEmailTemplateIdRenderRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email template to render.")
class GetEmailTemplateIdRenderRequestQuery(StrictModel):
    entry: int | None = Field(default=None, description="When rendering from search query results, the zero-based index of the lead/contact to use (0-99). Omit this parameter when rendering for a specific lead/contact.", ge=0, le=99)
class GetEmailTemplateIdRenderRequest(StrictModel):
    """Render an email template with actual data for a specific lead or contact. Supports rendering against a single lead/contact or previewing from a search query result."""
    path: GetEmailTemplateIdRenderRequestPath
    query: GetEmailTemplateIdRenderRequestQuery | None = None

# Operation: list_sms_templates
class GetSmsTemplateRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of SMS templates to return in a single response. Useful for controlling result set size in paginated requests.")
class GetSmsTemplateRequest(StrictModel):
    """Retrieve a paginated list of SMS templates available in your account. Use the limit parameter to control the number of results returned."""
    query: GetSmsTemplateRequestQuery | None = None

# Operation: create_sms_template
class PostSmsTemplateRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="Template configuration object containing the SMS template details such as name, content, and any variable placeholders for personalization.")
class PostSmsTemplateRequest(StrictModel):
    """Create a new SMS template that can be used for sending standardized text messages. Define the template content and configuration for reuse across SMS campaigns."""
    body: PostSmsTemplateRequestBody

# Operation: get_sms_template
class GetSmsTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS template to retrieve.")
class GetSmsTemplateIdRequest(StrictModel):
    """Retrieve a specific SMS template by its unique identifier. Use this to fetch template details for viewing or further processing."""
    path: GetSmsTemplateIdRequestPath

# Operation: update_sms_template
class PutSmsTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS template to update.")
class PutSmsTemplateIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the SMS template.")
    body: str | None = Field(default=None, description="The message content of the SMS template.")
class PutSmsTemplateIdRequest(StrictModel):
    """Update an existing SMS template by modifying its name and/or body content. Provide the template ID and specify which fields to update."""
    path: PutSmsTemplateIdRequestPath
    body: PutSmsTemplateIdRequestBody | None = None

# Operation: delete_sms_template
class DeleteSmsTemplateIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the SMS template to delete.")
class DeleteSmsTemplateIdRequest(StrictModel):
    """Permanently delete an SMS template by its ID. This action cannot be undone and will remove the template from your account."""
    path: DeleteSmsTemplateIdRequestPath

# Operation: get_connected_account
class GetConnectedAccountIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the connected account to retrieve.")
class GetConnectedAccountIdRequest(StrictModel):
    """Retrieve detailed information about a specific connected account using its unique identifier."""
    path: GetConnectedAccountIdRequestPath

# Operation: list_send_as_associations
class GetSendAsRequestQuery(StrictModel):
    allowing_user_id: str | None = Field(default=None, description="Filter associations where this user is granting Send As permission. Must match your own user ID if provided.")
    allowed_user_id: str | None = Field(default=None, description="Filter associations where this user is receiving Send As permission. Must match your own user ID if provided.")
class GetSendAsRequest(StrictModel):
    """Retrieve all Send As associations for the authenticated user, either as the user granting permission or receiving it. At least one filter parameter should be provided to scope results to your user ID."""
    query: GetSendAsRequestQuery | None = None

# Operation: grant_send_as_permission
class PostSendAsRequestBody(StrictModel):
    allowing_user_id: str = Field(default=..., description="Your user ID that will grant send-as permission. This must match your own user ID to authorize the delegation.")
    allowed_user_id: str = Field(default=..., description="The user ID of the person who will receive permission to send messages as you.")
class PostSendAsRequest(StrictModel):
    """Grant another user permission to send messages on your behalf by creating a Send As Association. The allowing user ID must be your own user ID."""
    body: PostSendAsRequestBody

# Operation: revoke_send_as_permission
class DeleteSendAsRequestQuery(StrictModel):
    allowing_user_id: str = Field(default=..., description="Your user ID — the user who originally granted Send As permission. This must match your authenticated user ID.")
    allowed_user_id: str = Field(default=..., description="The user ID of the user whose Send As permission is being revoked.")
class DeleteSendAsRequest(StrictModel):
    """Revoke Send As permission that was previously granted to another user. The requesting user must be the one who originally granted the permission."""
    query: DeleteSendAsRequestQuery

# Operation: get_send_as
class GetSendAsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Send As Association to retrieve.")
class GetSendAsIdRequest(StrictModel):
    """Retrieve a specific Send As Association by its unique identifier to view its configuration and details."""
    path: GetSendAsIdRequestPath

# Operation: delete_send_as
class DeleteSendAsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Send As Association to delete.")
class DeleteSendAsIdRequest(StrictModel):
    """Remove a Send As Association by its unique identifier. This operation permanently deletes the specified Send As Association, preventing further use of that sending identity."""
    path: DeleteSendAsIdRequestPath

# Operation: update_send_as_permissions
class PostSendAsBulkRequestBody(StrictModel):
    allow: list[str] | None = Field(default=None, description="List of user IDs to grant Send As permission to. Each ID must be a valid user identifier in your organization.")
    disallow: list[str] | None = Field(default=None, description="List of user IDs to revoke Send As permission from. Each ID must be a valid user identifier in your organization.")
class PostSendAsBulkRequest(StrictModel):
    """Grant or revoke Send As permissions for multiple users in a single request. Returns all current Send As associations where you are the allowing user."""
    body: PostSendAsBulkRequestBody | None = None

# Operation: list_sequences
class GetSequenceRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of sequences to return in a single request. Allows you to control pagination size for efficient data retrieval.")
class GetSequenceRequest(StrictModel):
    """Retrieve a paginated list of all sequences. Use the limit parameter to control the number of results returned per request."""
    query: GetSequenceRequestQuery | None = None

# Operation: create_sequence
class PostSequenceRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The sequence configuration object containing all required properties to define the new sequence.")
class PostSequenceRequest(StrictModel):
    """Create a new sequence with the specified configuration. This operation initializes a sequence resource that can be used for ordered processing or workflow management."""
    body: PostSequenceRequestBody

# Operation: get_sequence
class GetSequenceIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier that specifies which sequence to retrieve.")
class GetSequenceIdRequest(StrictModel):
    """Retrieve a single sequence by its unique identifier. Use this operation to fetch detailed information about a specific sequence."""
    path: GetSequenceIdRequestPath

# Operation: update_sequence
class PutSequenceIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the sequence to update.")
class PutSequenceIdRequestBody(StrictModel):
    steps: list[dict[str, Any]] | None = Field(default=None, description="An ordered array of steps that defines the sequence workflow. When provided, this completely replaces all existing steps; any steps not included in the request will be removed from the sequence.")
class PutSequenceIdRequest(StrictModel):
    """Update an existing sequence by modifying its configuration. The steps array, if provided, will completely replace all current steps in the sequence."""
    path: PutSequenceIdRequestPath
    body: PutSequenceIdRequestBody | None = None

# Operation: delete_sequence
class DeleteSequenceIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the sequence to delete.")
class DeleteSequenceIdRequest(StrictModel):
    """Permanently delete a sequence by its unique identifier. This action cannot be undone."""
    path: DeleteSequenceIdRequestPath

# Operation: list_sequence_subscriptions
class GetSequenceSubscriptionRequestQuery(StrictModel):
    sequence_id: str | None = Field(default=None, description="Filter results by sequence ID. At least one of sequence_id, contact_id, or lead_id must be specified.")
class GetSequenceSubscriptionRequest(StrictModel):
    """Retrieve a list of sequence subscriptions filtered by sequence, contact, or lead. At least one filter criterion must be provided."""
    query: GetSequenceSubscriptionRequestQuery | None = None

# Operation: subscribe_contact_to_sequence
class PostSequenceSubscriptionRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="Request body containing the contact ID and sequence ID. Specify which contact to subscribe and which sequence to enroll them in.")
class PostSequenceSubscriptionRequest(StrictModel):
    """Subscribe a contact to an automation sequence. This enrolls the contact in the specified sequence, triggering any configured automation workflows."""
    body: PostSequenceSubscriptionRequestBody

# Operation: get_sequence_subscription
class GetSequenceSubscriptionIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the sequence subscription to retrieve.")
class GetSequenceSubscriptionIdRequest(StrictModel):
    """Retrieve a specific sequence subscription by its unique identifier to view its configuration and status."""
    path: GetSequenceSubscriptionIdRequestPath

# Operation: update_sequence_subscription
class PutSequenceSubscriptionIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the sequence subscription to update.")
class PutSequenceSubscriptionIdRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="The updated configuration and settings for the sequence subscription. Include only the fields you want to modify.")
class PutSequenceSubscriptionIdRequest(StrictModel):
    """Update an existing sequence subscription with new configuration, settings, or other properties. Modifies the subscription identified by the provided ID."""
    path: PutSequenceSubscriptionIdRequestPath
    body: PutSequenceSubscriptionIdRequestBody

# Operation: list_dialer_sessions
class GetDialerRequestQuery(StrictModel):
    source_value: str | None = Field(default=None, description="Filter results by the source identifier, which can be either a Smart View ID or Shared Entry ID.")
    source_type: Literal["saved-search", "shared-entry"] | None = Field(default=None, description="Filter results by source type. Valid options are 'saved-search' for saved search sources or 'shared-entry' for shared entry sources.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of dialer sessions to return in the results.")
class GetDialerRequest(StrictModel):
    """Retrieve and filter dialer sessions to view their source, type, and associated user information. Use filters to narrow results by source identifier or type."""
    query: GetDialerRequestQuery | None = None

# Operation: get_dialer
class GetDialerIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the dialer session to retrieve.")
class GetDialerIdRequest(StrictModel):
    """Retrieve detailed information about a specific dialer session using its unique identifier."""
    path: GetDialerIdRequestPath

# Operation: list_smart_views
class GetSavedSearchRequestQuery(StrictModel):
    type__in: str | None = Field(default=None, description="Filter results by one or more record types using comma-separated values (e.g., lead,contact). Omit this parameter to retrieve Smart Views for all types.")
class GetSavedSearchRequest(StrictModel):
    """Retrieve all Smart Views with optional filtering by record type. Use this to display available saved searches for leads, contacts, or both."""
    query: GetSavedSearchRequestQuery | None = None

# Operation: create_smart_view
class PostSavedSearchRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the Smart View. This is the label users will see when accessing the saved search.")
    query: dict[str, Any] = Field(default=..., description="A filter query object that defines which records appear in the Smart View. Must include an `object_type` clause specifying either 'Lead' or 'Contact' to determine the record type for this Smart View.")
class PostSavedSearchRequest(StrictModel):
    """Create a Smart View (saved search) for Leads or Contacts. The Smart View uses a filter query to automatically populate with matching records based on your specified criteria."""
    body: PostSavedSearchRequestBody

# Operation: get_smart_view
class GetSavedSearchIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Smart View to retrieve.")
class GetSavedSearchIdRequest(StrictModel):
    """Retrieve a single Smart View by its unique identifier. Use this to fetch detailed information about a saved search view."""
    path: GetSavedSearchIdRequestPath

# Operation: update_smart_view
class PutSavedSearchIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Smart View to update. This ID is assigned when the Smart View is created and is used to reference it in subsequent operations.")
class PutSavedSearchIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the Smart View. This is the human-readable label shown in the user interface to identify the Smart View.")
class PutSavedSearchIdRequest(StrictModel):
    """Update an existing Smart View by modifying its properties such as the display name. Use this operation to rename or reconfigure a Smart View that you've previously created."""
    path: PutSavedSearchIdRequestPath
    body: PutSavedSearchIdRequestBody | None = None

# Operation: delete_smart_view
class DeleteSavedSearchIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Smart View to delete.")
class DeleteSavedSearchIdRequest(StrictModel):
    """Permanently delete a Smart View by its unique identifier. This action cannot be undone and will remove all saved search criteria and filters associated with the Smart View."""
    path: DeleteSavedSearchIdRequestPath

# Operation: send_bulk_email
class PostBulkActionEmailRequestBody(StrictModel):
    s_query: dict[str, Any] = Field(default=..., description="Structured query to filter which leads receive the email, using the same query syntax as the Advanced Filtering API.")
    results_limit: int | None = Field(default=None, description="Optional limit on the number of leads to affect. If not specified, all leads matching the query will be included.")
    sort: list[dict[str, Any]] | None = Field(default=None, description="Optional sort criteria to order the filtered leads. Specify as an array of sort expressions.")
    contact_preference: Literal["lead", "contact"] | None = Field(default=None, description="Determines email recipient scope: use 'lead' to email only the primary contact of each lead, or 'contact' to email the first contact email of each individual contact associated with the lead.")
    send_done_email: bool | None = Field(default=None, description="Whether to send a confirmation email after the bulk action completes. Enabled by default.")
class PostBulkActionEmailRequest(StrictModel):
    """Send bulk emails to leads matching specified criteria. Choose whether to email the primary lead contact or each individual contact associated with the leads."""
    body: PostBulkActionEmailRequestBody

# Operation: get_bulk_email
class GetBulkActionEmailIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk email action to retrieve.")
class GetBulkActionEmailIdRequest(StrictModel):
    """Retrieve the details and status of a specific bulk email action by its unique identifier."""
    path: GetBulkActionEmailIdRequestPath

# Operation: apply_sequence_subscription_bulk_action
class PostBulkActionSequenceSubscriptionRequestBody(StrictModel):
    s_query: dict[str, Any] = Field(default=..., description="Structured query object that defines which leads to target with the bulk action. This filter determines the lead set before applying the subscription action.")
    results_limit: int | None = Field(default=None, description="Maximum number of leads to affect with this bulk action. If not specified, all matching leads will be included.")
    sort: list[dict[str, Any]] | None = Field(default=None, description="Sort criteria to order the filtered leads. Specify as an array where order matters for determining which leads are processed first when combined with results_limit.")
    action_type: Literal["subscribe", "resume", "resume_finished", "pause"] = Field(default=..., description="The subscription action to perform: 'subscribe' (enroll leads in a sequence), 'resume' (restart paused sequences), 'resume_finished' (restart completed sequences), or 'pause' (pause active sequences).")
    sequence_id: str | None = Field(default=None, description="ID of the sequence to target. Required when action_type is 'subscribe'; optional for resume and pause actions to target all sequences for matching leads.")
    sender_account_id: str | None = Field(default=None, description="Account ID of the sender. Required when action_type is 'subscribe' to identify which account will send the sequence messages.")
    sender_name: str | None = Field(default=None, description="Display name of the sender. Required when action_type is 'subscribe' to personalize outgoing sequence messages.")
    sender_email: str | None = Field(default=None, description="Email address of the sender. Required when action_type is 'subscribe' as the reply-to and from address for sequence messages. Must be a valid email format.", json_schema_extra={'format': 'email'})
    contact_preference: Literal["lead", "contact"] | None = Field(default=None, description="Determines subscription scope when action_type is 'subscribe': 'lead' subscribes the primary lead contact, or 'contact' subscribes each contact's individual email address. Required when action_type is 'subscribe'.")
    send_done_email: bool | None = Field(default=None, description="Whether to send a confirmation email after the bulk action completes. Defaults to true if not specified.")
class PostBulkActionSequenceSubscriptionRequest(StrictModel):
    """Apply a bulk subscription action (subscribe, resume, pause, or resume finished) to leads matching specified criteria. Use structured queries to filter leads and optionally limit the number affected."""
    body: PostBulkActionSequenceSubscriptionRequestBody

# Operation: get_sequence_subscription_bulk_action
class GetBulkActionSequenceSubscriptionIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk sequence subscription to retrieve.")
class GetBulkActionSequenceSubscriptionIdRequest(StrictModel):
    """Retrieve a single bulk sequence subscription by its ID. Use this to fetch details about a specific sequence subscription object."""
    path: GetBulkActionSequenceSubscriptionIdRequestPath

# Operation: delete_leads_bulk
class PostBulkActionDeleteRequestBody(StrictModel):
    s_query: dict[str, Any] = Field(default=..., description="Structured query object that defines which leads to delete based on filter conditions.")
    results_limit: int | None = Field(default=None, description="Maximum number of leads to delete in this bulk action. If not specified, all matching leads will be deleted.")
    sort: list[dict[str, Any]] | None = Field(default=None, description="Array of sort criteria to order the leads before deletion. Order matters and determines which leads are processed first if a results limit is applied.")
    send_done_email: bool | None = Field(default=None, description="Whether to send a confirmation email after the bulk delete completes. Defaults to true if not specified.")
class PostBulkActionDeleteRequest(StrictModel):
    """Initiate a bulk delete action to remove multiple leads matching specified criteria. Optionally receive a confirmation email when the deletion completes."""
    body: PostBulkActionDeleteRequestBody

# Operation: get_bulk_delete
class GetBulkActionDeleteIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk delete operation to retrieve.")
class GetBulkActionDeleteIdRequest(StrictModel):
    """Retrieve details of a specific bulk delete operation by its ID. Use this to check the status and configuration of a previously initiated bulk deletion."""
    path: GetBulkActionDeleteIdRequestPath

# Operation: bulk_edit_leads
class PostBulkActionEditRequestBody(StrictModel):
    s_query: dict[str, Any] = Field(default=..., description="Structured query object that defines which leads to include in the bulk edit operation.")
    results_limit: int | None = Field(default=None, description="Maximum number of leads to affect with this bulk edit action. If not specified, all matching leads will be included.")
    sort: list[dict[str, Any]] | None = Field(default=None, description="Array of sort criteria to order the leads before applying the bulk edit. Order matters and determines which leads are prioritized if results_limit is applied.")
    type_: Literal["set_lead_status", "clear_custom_field", "set_custom_field"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of bulk edit operation to perform: set_lead_status updates lead status, clear_custom_field removes a custom field value, or set_custom_field assigns a custom field value.")
    lead_status_id: str | None = Field(default=None, description="The ID of the Lead Status to assign. Required when type is 'set_lead_status'.")
    custom_field_name: str | None = Field(default=None, description="The exact name of the custom field to modify. Required when type is 'clear_custom_field' or 'set_custom_field' (unless custom_field_id is provided instead).")
    custom_field_values: list[str] | None = Field(default=None, description="Array of values to set for custom fields that support multiple values. Used only when type is 'set_custom_field'.")
    custom_field_operation: Literal["replace", "add", "remove"] | None = Field(default=None, description="How to apply values to multi-value custom fields: 'replace' overwrites existing values, 'add' appends new values, or 'remove' deletes specified values. Defaults to 'replace' and only applies when type is 'set_custom_field'.")
    send_done_email: bool | None = Field(default=None, description="Whether to send a confirmation email after the bulk edit completes. Defaults to true; set to false to skip the notification.")
class PostBulkActionEditRequest(StrictModel):
    """Execute a bulk edit action on leads matching specified criteria. Supports updating lead status, clearing custom fields, or setting custom field values across multiple leads."""
    body: PostBulkActionEditRequestBody

# Operation: get_bulk_edit
class GetBulkActionEditIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the bulk edit action to retrieve.")
class GetBulkActionEditIdRequest(StrictModel):
    """Retrieve the details and current status of a specific bulk edit action by its unique identifier."""
    path: GetBulkActionEditIdRequestPath

# Operation: create_integration_link
class PostIntegrationLinkRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for this integration link, shown as clickable link text to users.")
    type_: Literal["lead", "contact", "opportunity"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The entity type this integration link applies to. Must be one of: lead, contact, or opportunity.")
    url: str = Field(default=..., description="The URL template that defines where this integration link directs to. Use template variables to dynamically construct URLs based on entity data.")
class PostIntegrationLinkRequest(StrictModel):
    """Create a new integration link for your organization to connect entities to external systems. This operation is restricted to organization administrators only."""
    body: PostIntegrationLinkRequestBody

# Operation: get_integration_link
class GetIntegrationLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the integration link to retrieve.")
class GetIntegrationLinkIdRequest(StrictModel):
    """Retrieve a specific integration link by its unique identifier. Use this to fetch details about a configured integration connection."""
    path: GetIntegrationLinkIdRequestPath

# Operation: update_integration_link
class PutIntegrationLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the integration link to update.")
class PutIntegrationLinkIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The text displayed as the clickable link in the user interface.")
    url: str | None = Field(default=None, description="The URL template that defines the target destination, supporting dynamic variable substitution (e.g., using placeholders for dynamic values).")
class PutIntegrationLinkIdRequest(StrictModel):
    """Update an existing integration link's display name and URL template. Requires organization admin privileges."""
    path: PutIntegrationLinkIdRequestPath
    body: PutIntegrationLinkIdRequestBody | None = None

# Operation: delete_integration_link
class DeleteIntegrationLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the integration link to delete.")
class DeleteIntegrationLinkIdRequest(StrictModel):
    """Permanently delete an integration link from your organization. This action is restricted to organization administrators only and cannot be undone."""
    path: DeleteIntegrationLinkIdRequestPath

# Operation: export_leads
class PostExportLeadRequestBody(StrictModel):
    s_query: dict[str, Any] | None = Field(default=None, description="Advanced query filter to narrow the exported results. If omitted, all records of the specified type are exported.")
    results_limit: int | None = Field(default=None, description="Maximum number of records to include in the export. If not specified, all matching records are exported.")
    sort: list[dict[str, Any]] | None = Field(default=None, description="Sort order for the exported results. Specify as an array of sort criteria to control result ordering.")
    format_: Literal["csv", "json"] = Field(default=..., validation_alias="format", serialization_alias="format", description="Output file format. Choose CSV for spreadsheet compatibility or JSON for raw data backups and migrations. JSON is recommended for data preservation.")
    type_: Literal["leads", "contacts", "lead_opps"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Record type to export: leads (one row per lead or complete JSON structure), contacts (one row per contact), or lead_opps (one row per opportunity).")
    date_format: Literal["original", "iso8601", "excel"] | None = Field(default=None, description="Date format for CSV exports only. Choose original (as-is), ISO 8601 (standardized format), or excel (spreadsheet-compatible format). Defaults to original format.")
    fields: list[str] | None = Field(default=None, description="Specific fields to include in the export. If omitted, all available fields are exported.")
    include_activities: bool | None = Field(default=None, description="Include associated activities in the export. Only applies when exporting leads in JSON format.")
    include_smart_fields: bool | None = Field(default=None, description="Include smart fields in the export. Works with leads in JSON format or any record type in CSV format.")
    send_done_email: bool | None = Field(default=None, description="Send a confirmation email when the export completes. Set to false to skip the notification email.")
class PostExportLeadRequest(StrictModel):
    """Export leads, contacts, or opportunities to a compressed file based on search criteria. The generated file will be sent to your email once the export completes."""
    body: PostExportLeadRequestBody

# Operation: export_opportunities
class PostExportOpportunityRequestBody(StrictModel):
    params: dict[str, Any] | None = Field(default=None, description="Filter criteria to select which opportunities to export, using the same filter options available in the opportunities endpoint.")
    format_: Literal["csv", "json"] = Field(default=..., validation_alias="format", serialization_alias="format", description="File format for the exported data. Choose between CSV for spreadsheet compatibility or JSON for structured data interchange.")
    date_format: Literal["original", "iso8601", "excel"] | None = Field(default=None, description="Date formatting style for CSV exports only. Choose 'original' to preserve the source format, 'iso8601' for standardized date-time strings, or 'excel' for Excel-compatible date values.")
    fields: list[str] | None = Field(default=None, description="Specific fields to include in the export. If not specified, all available data fields are included. Provide as an ordered list of field names.")
    send_done_email: bool | None = Field(default=None, description="Set to false to skip the confirmation email after the export completes. By default, a confirmation email is sent.")
class PostExportOpportunityRequest(StrictModel):
    """Export opportunities matching specified filters to a file in your chosen format. A confirmation email is sent upon completion unless explicitly disabled."""
    body: PostExportOpportunityRequestBody

# Operation: get_export
class GetExportIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the export to retrieve.")
class GetExportIdRequest(StrictModel):
    """Retrieve a single export by its unique identifier to check its current processing status or obtain a download URL once completed. Status values include: created, started, in_progress, done, and error."""
    path: GetExportIdRequestPath

# Operation: list_exports
class GetExportRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of exports to return in the response. Useful for pagination and controlling response size.")
class GetExportRequest(StrictModel):
    """Retrieve a list of all exports with optional pagination control. Use the limit parameter to restrict the number of results returned."""
    query: GetExportRequestQuery | None = None

# Operation: list_phone_numbers
class GetPhoneNumberRequestQuery(StrictModel):
    number: str | None = Field(default=None, description="Filter results to phone numbers matching this specific value. Leave empty to include all numbers regardless of their value.")
    is_group_number: bool | None = Field(default=None, description="Filter results to show only group numbers (true) or non-group numbers (false). Omit to include both types.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of phone numbers to return in the response. Useful for pagination or limiting large result sets.")
class GetPhoneNumberRequest(StrictModel):
    """Retrieve phone numbers from your organization with optional filtering by number value, group status, or result limit. Use this to search for specific phone numbers or get an overview of all numbers in your system."""
    query: GetPhoneNumberRequestQuery | None = None

# Operation: get_phone_number
class GetPhoneNumberIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the phone number to retrieve.")
class GetPhoneNumberIdRequest(StrictModel):
    """Retrieve detailed information for a specific phone number by its unique identifier."""
    path: GetPhoneNumberIdRequestPath

# Operation: update_phone_number
class PutPhoneNumberIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the phone number to update.")
class PutPhoneNumberIdRequestBody(StrictModel):
    label: str | None = Field(default=None, description="A custom label or name for this phone number to help identify it.")
    forward_to: str | None = Field(default=None, description="The phone number to forward incoming calls to when call forwarding is enabled.")
    forward_to_enabled: bool | None = Field(default=None, description="Enable or disable call forwarding for this phone number.")
    voicemail_greeting_url: str | None = Field(default=None, description="HTTPS URL pointing to an MP3 audio file to play as the voicemail greeting when callers reach voicemail.", json_schema_extra={'format': 'uri'})
class PutPhoneNumberIdRequest(StrictModel):
    """Update settings for a phone number including its label, call forwarding configuration, and voicemail greeting. Personal numbers can only be updated by their owner, while group numbers require 'Manage Group Phone Numbers' permission."""
    path: PutPhoneNumberIdRequestPath
    body: PutPhoneNumberIdRequestBody | None = None

# Operation: delete_phone_number
class DeletePhoneNumberIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the phone number to delete.")
class DeletePhoneNumberIdRequest(StrictModel):
    """Delete a phone number from your account or group. Requires 'Manage Group Phone Numbers' permission to delete group numbers; personal numbers can only be deleted by their owner."""
    path: DeletePhoneNumberIdRequestPath

# Operation: rent_phone_number
class PostPhoneNumberRequestInternalRequestBody(StrictModel):
    country: str = Field(default=..., description="Two-letter ISO country code indicating where the phone number should be rented (e.g., US for United States).")
    sharing: Literal["personal", "group"] = Field(default=..., description="Scope of the phone number: 'personal' for an individual user or 'group' for a shared group number.")
    prefix: str | None = Field(default=None, description="Optional phone number prefix or area code, excluding the country code.")
    with_sms: bool | None = Field(default=None, description="Optional flag to control SMS capability. When true, forces an SMS-capable number; when false, allows non-SMS-capable numbers. By default, SMS-capable numbers are rented if supported in the country.")
    with_mms: bool | None = Field(default=None, description="Optional flag to control MMS capability. When true, forces an MMS-capable number; when false, allows non-MMS-capable numbers. By default, MMS-capable numbers are rented if supported in the country.")
class PostPhoneNumberRequestInternalRequest(StrictModel):
    """Rent an internal phone number for personal or group use. Renting incurs a cost and requires appropriate permissions for group numbers."""
    body: PostPhoneNumberRequestInternalRequestBody

# Operation: generate_file_upload_credentials
class PostFilesUploadRequestBody(StrictModel):
    filename: str = Field(default=..., description="The name of the file being uploaded, including its file extension (e.g., image.jpg, document.pdf).")
    content_type: str = Field(default=..., description="The MIME type of the file being uploaded (e.g., image/jpeg, application/pdf, text/plain).")
class PostFilesUploadRequest(StrictModel):
    """Generate signed S3 upload credentials and a download URL for storing a file. Use the returned credentials to upload your file directly to S3, then reference the download URL in other API endpoints."""
    body: PostFilesUploadRequestBody

# Operation: list_comment_threads
class GetCommentThreadRequestQuery(StrictModel):
    object_ids: list[str] | None = Field(default=None, description="Filter results to include only threads associated with specific object IDs. Provide as an array of object identifiers.")
    ids: list[str] | None = Field(default=None, description="Filter results to include only threads with specific thread IDs. Provide as an array of thread identifiers.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of comment threads to return in the response. Limits the result set size.")
class GetCommentThreadRequest(StrictModel):
    """Retrieve multiple comment threads with optional filtering by associated objects or specific thread identifiers. Useful for fetching discussions related to particular items or retrieving known threads."""
    query: GetCommentThreadRequestQuery | None = None

# Operation: get_comment_thread
class GetCommentThreadThreadIdRequestPath(StrictModel):
    thread_id: str = Field(default=..., description="The unique identifier that specifies which comment thread to retrieve.")
class GetCommentThreadThreadIdRequest(StrictModel):
    """Retrieve a specific comment thread by its unique identifier. Use this to fetch the full details of a single comment thread including all associated metadata."""
    path: GetCommentThreadThreadIdRequestPath

# Operation: list_comments
class GetCommentRequestQuery(StrictModel):
    object_id: str | None = Field(default=None, description="Filter comments by the ID of the object that was commented on. Cannot be used together with thread_id.")
    thread_id: str | None = Field(default=None, description="Filter comments by the discussion thread ID. Cannot be used together with object_id.")
class GetCommentRequest(StrictModel):
    """Retrieve comments filtered by either the object being commented on or the discussion thread. Provide exactly one filter to retrieve the relevant comments."""
    query: GetCommentRequestQuery | None = None

# Operation: create_comment
class PostCommentRequestBody(StrictModel):
    object_type: str = Field(default=..., description="The type of object being commented on (e.g., task, document, issue).")
    object_id: str = Field(default=..., description="The unique identifier of the object being commented on.")
    body: str = Field(default=..., description="The comment text formatted as rich text.")
class PostCommentRequest(StrictModel):
    """Create a comment on an object, automatically creating a comment thread if one doesn't already exist, or adding to an existing thread if it does."""
    body: PostCommentRequestBody

# Operation: get_comment
class GetCommentCommentIdRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to retrieve.")
class GetCommentCommentIdRequest(StrictModel):
    """Retrieve a specific comment by its unique identifier. Use this to fetch the full details of an individual comment."""
    path: GetCommentCommentIdRequestPath

# Operation: update_comment
class PutCommentCommentIdRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment you want to update.")
class PutCommentCommentIdRequestBody(StrictModel):
    body: str = Field(default=..., description="The new comment text formatted as rich text.")
class PutCommentCommentIdRequest(StrictModel):
    """Edit the body of a comment. You can only update comments that you created."""
    path: PutCommentCommentIdRequestPath
    body: PutCommentCommentIdRequestBody

# Operation: delete_comment
class DeleteCommentCommentIdRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to delete.")
class DeleteCommentCommentIdRequest(StrictModel):
    """Remove a comment from a thread. The comment content is deleted but the comment object remains until all comments in the thread are removed, at which point the entire thread is deleted. Deletion permissions are based on the user's ability to delete their own or other users' activities."""
    path: DeleteCommentCommentIdRequestPath

# Operation: get_event
class GetEventIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the event to retrieve.")
class GetEventIdRequest(StrictModel):
    """Retrieve a single event by its unique identifier. Returns a dictionary containing the event details."""
    path: GetEventIdRequestPath

# Operation: list_events
class GetEventRequestQuery(StrictModel):
    object_type: str | None = Field(default=None, description="Filter results to events for objects of a specific type (e.g., lead). When specified, only events matching this object type are returned.")
    object_id: str | None = Field(default=None, description="Filter results to events for a specific object by its ID (e.g., lead_123). Returns only direct events for this object, excluding related object events.")
    action: str | None = Field(default=None, description="Filter results to events of specific action types (e.g., deleted). Only events matching the specified action are returned.")
    request_id: str | None = Field(default=None, description="Filter results to events emitted during processing of a specific API request. Use this to trace all events generated by a single request.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of events to return in the response. Limited to a maximum of 50 events; defaults to 50 if not specified.", le=50)
class GetEventRequest(StrictModel):
    """Retrieve a paginated list of events from the event log, ordered by date with the most recent first. Supports filtering by object type, object ID, action, lead ID, user ID, and request ID to narrow results to specific events of interest."""
    query: GetEventRequestQuery | None = None

# Operation: create_webhook
class PostWebhookRequestBody(StrictModel):
    url: str = Field(default=..., description="The destination URL where webhook events will be sent. Must be a valid URI (e.g., https://example.com/webhook).", json_schema_extra={'format': 'uri'})
    events: list[PostWebhookBodyEventsItem] = Field(default=..., description="List of events to subscribe to. Each event specifies an object type and action to monitor (e.g., user.created, order.updated). Only events matching these subscriptions will be sent to your webhook URL.")
    verify_ssl: bool | None = Field(default=None, description="Whether to verify the SSL certificate when sending events to your webhook URL. Enabled by default for security; disable only if using self-signed certificates in development.")
class PostWebhookRequest(StrictModel):
    """Create a new webhook subscription to receive event notifications at a specified URL. The webhook will automatically send POST requests to your endpoint whenever subscribed events occur."""
    body: PostWebhookRequestBody

# Operation: get_webhook
class GetWebhookIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook subscription to retrieve.")
class GetWebhookIdRequest(StrictModel):
    """Retrieve the details of a specific webhook subscription by its unique identifier. Returns configuration, status, and event settings for the webhook."""
    path: GetWebhookIdRequestPath

# Operation: update_webhook
class PutWebhookIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook subscription to update.")
class PutWebhookIdRequestBody(StrictModel):
    url: str | None = Field(default=None, description="The destination URL where webhook events will be sent. Must be a valid URI.", json_schema_extra={'format': 'uri'})
    events: list[PutWebhookIdBodyEventsItem] | None = Field(default=None, description="List of events to subscribe to. Each event specifies an object type and an action to trigger the webhook.")
    verify_ssl: bool | None = Field(default=None, description="Whether to verify the SSL certificate of the destination webhook URL. Set to true for production environments to ensure secure connections.")
class PutWebhookIdRequest(StrictModel):
    """Update an existing webhook subscription with new configuration. Only the parameters you provide will be updated; omitted parameters retain their current values."""
    path: PutWebhookIdRequestPath
    body: PutWebhookIdRequestBody | None = None

# Operation: delete_webhook
class DeleteWebhookIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the webhook subscription to delete.")
class DeleteWebhookIdRequest(StrictModel):
    """Delete a webhook subscription to stop receiving event notifications at the configured endpoint."""
    path: DeleteWebhookIdRequestPath

# Operation: create_scheduling_link
class PostSchedulingLinkRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the scheduling link to help identify it among your other scheduling links.")
    url: str = Field(default=..., description="The external URL where the scheduling link points to. Must be a valid URI format.", json_schema_extra={'format': 'uri'})
    description: str | None = Field(default=None, description="An optional description providing additional context or details about the scheduling link's purpose.")
class PostSchedulingLinkRequest(StrictModel):
    """Create a new scheduling link that can be shared with users to access your availability and book meetings."""
    body: PostSchedulingLinkRequestBody

# Operation: get_scheduling_link
class GetSchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the scheduling link to retrieve.")
class GetSchedulingLinkIdRequest(StrictModel):
    """Retrieve a scheduling link by its unique identifier to access its configuration and sharing details."""
    path: GetSchedulingLinkIdRequestPath

# Operation: update_scheduling_link
class PutSchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the scheduling link to update.")
class PutSchedulingLinkIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A display name for the scheduling link as shown in the Close application.")
    url: str | None = Field(default=None, description="The external URL for the scheduling link. Must be a valid URI format.", json_schema_extra={'format': 'uri'})
    description: str | None = Field(default=None, description="A description for the scheduling link displayed in the Close application.")
    source_id: str | None = Field(default=None, description="The identifier for this scheduling link in the source or integrating application.")
    source_type: str | None = Field(default=None, description="A short descriptor identifying the type or category of the scheduling link.")
    duration_in_minutes: int | None = Field(default=None, description="The duration of meetings scheduled with this link, specified in minutes.")
class PutSchedulingLinkIdRequest(StrictModel):
    """Update an existing scheduling link by its unique identifier. Modify scheduling link details such as name, URL, description, and meeting duration."""
    path: PutSchedulingLinkIdRequestPath
    body: PutSchedulingLinkIdRequestBody | None = None

# Operation: delete_scheduling_link
class DeleteSchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the scheduling link to delete.")
class DeleteSchedulingLinkIdRequest(StrictModel):
    """Remove a scheduling link by its unique identifier. This permanently deletes the scheduling link and prevents further access to it."""
    path: DeleteSchedulingLinkIdRequestPath

# Operation: upsert_scheduling_link
class PostSchedulingLinkIntegrationRequestBody(StrictModel):
    source_id: str = Field(default=..., description="Your OAuth application's unique identifier for this scheduling link. Used to identify and deduplicate resources created by your app.")
    name: str | None = Field(default=None, description="Human-readable name displayed to users for this scheduling link.")
    url: str | None = Field(default=None, description="Public-facing URL where users can access and interact with this scheduling link. Must be a valid URI.", json_schema_extra={'format': 'uri'})
    description: str | None = Field(default=None, description="Additional context or explanation about the scheduling link's purpose and usage.")
    source_type: str | None = Field(default=None, description="Category or classification type for organizing and filtering scheduling links.")
    duration_in_minutes: int | None = Field(default=None, description="Default meeting duration in minutes for scheduling sessions created through this link.")
class PostSchedulingLinkIntegrationRequest(StrictModel):
    """Create a new scheduling link or update an existing one using your OAuth application's unique identifier. The system uses the source_id to detect and merge duplicate resources, ensuring only one scheduling link exists per source_id."""
    body: PostSchedulingLinkIntegrationRequestBody

# Operation: delete_scheduling_link_oauth
class DeleteSchedulingLinkIntegrationSourceIdRequestPath(StrictModel):
    source_id: str = Field(default=..., description="The unique source identifier of the scheduling link to delete, as assigned by your OAuth application when the link was created.")
class DeleteSchedulingLinkIntegrationSourceIdRequest(StrictModel):
    """Delete a scheduling link by its source identifier. This operation is only available to OAuth applications and uses the source_id assigned by your OAuth app to identify and remove the scheduling link."""
    path: DeleteSchedulingLinkIntegrationSourceIdRequestPath

# Operation: create_scheduling_link_shared
class PostSharedSchedulingLinkRequestBody(StrictModel):
    body: dict[str, Any] = Field(default=..., description="Configuration object for the shared scheduling link, including settings such as availability windows, booking constraints, and link customization options.")
class PostSharedSchedulingLinkRequest(StrictModel):
    """Create a shared scheduling link that allows others to view your available time slots and book meetings directly on your calendar without needing direct access to your calendar."""
    body: PostSharedSchedulingLinkRequestBody

# Operation: get_scheduling_link_shared
class GetSharedSchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the shared scheduling link to retrieve.")
class GetSharedSchedulingLinkIdRequest(StrictModel):
    """Retrieve a specific shared scheduling link by its unique identifier to access its configuration and sharing details."""
    path: GetSharedSchedulingLinkIdRequestPath

# Operation: update_scheduling_link_shared
class PutSharedSchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the shared scheduling link to update.")
class PutSharedSchedulingLinkIdRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="An object containing the scheduling link properties to modify. Only provided fields will be updated; omitted fields remain unchanged.")
class PutSharedSchedulingLinkIdRequest(StrictModel):
    """Modify the configuration and settings of an existing shared scheduling link, such as availability windows, meeting duration, or access permissions."""
    path: PutSharedSchedulingLinkIdRequestPath
    body: PutSharedSchedulingLinkIdRequestBody | None = None

# Operation: delete_scheduling_link_shared
class DeleteSharedSchedulingLinkIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the shared scheduling link to delete.")
class DeleteSharedSchedulingLinkIdRequest(StrictModel):
    """Permanently delete a shared scheduling link by its ID. This action cannot be undone and will immediately revoke access to the scheduling link for all users."""
    path: DeleteSharedSchedulingLinkIdRequestPath

# Operation: associate_shared_scheduling_link
class PostSharedSchedulingLinkAssociationRequestBody(StrictModel):
    shared_scheduling_link_id: str = Field(default=..., description="The unique identifier of the shared scheduling link to associate.")
    user_scheduling_link_id: str | None = Field(default=None, description="The unique identifier of the user scheduling link to associate with the shared link. Either this parameter or url must be provided.")
    url: str | None = Field(default=None, description="A valid URI to associate with the shared link. Either this parameter or user_scheduling_link_id must be provided.", json_schema_extra={'format': 'uri'})
class PostSharedSchedulingLinkAssociationRequest(StrictModel):
    """Associate a shared scheduling link with either a user scheduling link or a custom URL to enable scheduling access through the shared link."""
    body: PostSharedSchedulingLinkAssociationRequestBody

# Operation: disable_shared_scheduling_link
class PostSharedSchedulingLinkAssociationUnmapRequestBody(StrictModel):
    shared_scheduling_link_id: str = Field(default=..., description="The unique identifier of the shared scheduling link to disable.")
class PostSharedSchedulingLinkAssociationUnmapRequest(StrictModel):
    """Disable a shared scheduling link by removing its association with a user scheduling link or URL, preventing further access through that shared link."""
    body: PostSharedSchedulingLinkAssociationUnmapRequestBody

# Operation: list_lead_custom_fields
class GetCustomFieldLeadRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of custom fields to return in the response. Omit to retrieve all available custom fields.")
class GetCustomFieldLeadRequest(StrictModel):
    """Retrieve all custom fields configured for leads in your organization. Use the optional limit parameter to control the number of results returned."""
    query: GetCustomFieldLeadRequestQuery | None = None

# Operation: create_lead_custom_field
class PostCustomFieldLeadRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the custom field that will appear in the UI and API responses.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type of the custom field (e.g., text, number, date, choice). This determines how the field stores and validates data.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether this field can store multiple values simultaneously. Useful for fields like tags or multi-select options.")
    options: list[dict[str, Any]] | None = Field(default=None, description="Predefined options available for choice-type fields. Each option becomes a selectable value when the field type supports choices.")
    editable_roles: list[str] | None = Field(default=None, description="List of user roles that have permission to edit this custom field. If not specified, defaults to system defaults or all roles.")
class PostCustomFieldLeadRequest(StrictModel):
    """Create a new custom field for leads with configurable data type, multiple value support, and role-based edit permissions."""
    body: PostCustomFieldLeadRequestBody

# Operation: get_lead_custom_field
class GetCustomFieldLeadIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the lead custom field to retrieve.")
class GetCustomFieldLeadIdRequest(StrictModel):
    """Retrieve the details of a specific custom field associated with a lead, including its configuration and current values."""
    path: GetCustomFieldLeadIdRequestPath

# Operation: update_lead_custom_field
class PutCustomFieldLeadCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the Lead custom field to update.")
class PutCustomFieldLeadCustomFieldIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new display name for the custom field.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether this field should accept multiple values simultaneously.")
    editable_roles: list[str] | None = Field(default=None, description="List of role identifiers that are permitted to edit this field's values. Only users with these roles can modify the field.")
    options: list[dict[str, Any]] | None = Field(default=None, description="Array of choice options for fields with choice/select type. Each option represents a selectable value in the field.")
class PutCustomFieldLeadCustomFieldIdRequest(StrictModel):
    """Update a Lead custom field's configuration including its name, type, multi-value support, role-based edit permissions, and choice options. Changes take effect immediately in the Close UI."""
    path: PutCustomFieldLeadCustomFieldIdRequestPath
    body: PutCustomFieldLeadCustomFieldIdRequestBody | None = None

# Operation: delete_lead_custom_field
class DeleteCustomFieldLeadCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the Lead custom field to delete.")
class DeleteCustomFieldLeadCustomFieldIdRequest(StrictModel):
    """Permanently delete a custom field from your Lead records. The field will be immediately removed from all Lead API responses and cannot be recovered."""
    path: DeleteCustomFieldLeadCustomFieldIdRequestPath

# Operation: list_contact_custom_fields
class GetCustomFieldContactRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of custom fields to return in the response. Useful for pagination or limiting result set size.")
class GetCustomFieldContactRequest(StrictModel):
    """Retrieve all custom fields configured for contacts in your organization. Use the limit parameter to control the number of results returned."""
    query: GetCustomFieldContactRequestQuery | None = None

# Operation: create_contact_custom_field
class PostCustomFieldContactRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the custom field. This is the label users will see when viewing or editing contact records.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type for the custom field. Supported types include text, number, date, and choice. The type determines how the field stores and validates data.")
    accepts_multiple_values: bool | None = Field(default=None, description="Enable this to allow the field to store multiple values. Useful for fields like tags, skills, or other multi-select attributes.")
    options: list[dict[str, Any]] | None = Field(default=None, description="A list of predefined options for choice-type fields. Each option becomes a selectable value when users interact with the field. Only applicable when type is set to choice.")
    restricted_to_roles: bool | None = Field(default=None, description="Enable this to restrict field editing permissions to users with specific roles. When enabled, only authorized users can modify values in this field.")
class PostCustomFieldContactRequest(StrictModel):
    """Create a new custom field for contacts with configurable data types and optional multi-value support. Use this to extend contact records with additional attributes tailored to your business needs."""
    body: PostCustomFieldContactRequestBody

# Operation: get_contact_custom_field
class GetCustomFieldContactIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the contact custom field to retrieve.")
class GetCustomFieldContactIdRequest(StrictModel):
    """Retrieve the details of a specific custom field associated with a contact. Use this to access custom field configuration and values for a particular contact."""
    path: GetCustomFieldContactIdRequestPath

# Operation: update_contact_custom_field
class PutCustomFieldContactCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the contact custom field to update.")
class PutCustomFieldContactCustomFieldIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new display name for the custom field as it will appear in the Close UI.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether this field can store multiple values simultaneously.")
    restricted_to_roles: bool | None = Field(default=None, description="Whether editing this field's values should be restricted to users with specific roles.")
    options: list[dict[str, Any]] | None = Field(default=None, description="A list of predefined values available for selection when the field type is choice-based. Order and format should match the field's expected choice structure.")
class PutCustomFieldContactCustomFieldIdRequest(StrictModel):
    """Update a contact custom field's configuration including its display name, value multiplicity, role-based access restrictions, and available options for choice-based fields. Changes take effect immediately in the Close UI."""
    path: PutCustomFieldContactCustomFieldIdRequestPath
    body: PutCustomFieldContactCustomFieldIdRequestBody | None = None

# Operation: delete_contact_custom_field
class DeleteCustomFieldContactCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the custom field to delete.")
class DeleteCustomFieldContactCustomFieldIdRequest(StrictModel):
    """Permanently delete a custom field from your Contact system. The field will be immediately removed from all Contact API responses and cannot be recovered."""
    path: DeleteCustomFieldContactCustomFieldIdRequestPath

# Operation: list_opportunity_custom_fields
class GetCustomFieldOpportunityRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of custom fields to return in the response. Useful for pagination when dealing with large numbers of custom fields.")
class GetCustomFieldOpportunityRequest(StrictModel):
    """Retrieve all custom fields configured for opportunities in your organization. Use this to understand the custom data structure available for opportunity records."""
    query: GetCustomFieldOpportunityRequestQuery | None = None

# Operation: create_opportunity_custom_field
class PostCustomFieldOpportunityRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the custom field. This is how the field will be identified throughout the system.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type that determines how the field stores and validates data (e.g., text, number, date, choice).")
    accepts_multiple_values: bool | None = Field(default=None, description="When enabled, allows the field to store multiple values simultaneously rather than a single value.")
    editable_with_roles: list[str] | None = Field(default=None, description="A list of role identifiers that have permission to edit this field. If not specified, default role permissions apply.")
    options: list[dict[str, Any]] | None = Field(default=None, description="A list of predefined choices available for selection when the field type is set to choice or similar selection-based types. Order may be significant for display purposes.")
class PostCustomFieldOpportunityRequest(StrictModel):
    """Create a new custom field for Opportunity records. Define the field's name, data type, and optionally configure multi-value support, role-based editing permissions, and predefined options for choice fields."""
    body: PostCustomFieldOpportunityRequestBody

# Operation: get_opportunity_custom_field
class GetCustomFieldOpportunityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom field to retrieve. This ID must correspond to an existing custom field in the opportunity.")
class GetCustomFieldOpportunityIdRequest(StrictModel):
    """Retrieve detailed information about a specific custom field associated with an opportunity. Use this to fetch custom field values and metadata for a given opportunity."""
    path: GetCustomFieldOpportunityIdRequestPath

# Operation: update_opportunity_custom_field
class PutCustomFieldOpportunityCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the custom field to update.")
class PutCustomFieldOpportunityCustomFieldIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new display name for the custom field.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether the field should accept multiple values simultaneously.")
    restricted_to_roles: bool | None = Field(default=None, description="Whether editing this field's values should be restricted to users with specific roles.")
    options: list[dict[str, Any]] | None = Field(default=None, description="Updated list of available options for a choices field type. Order is preserved and determines the display sequence in the UI.")
class PutCustomFieldOpportunityCustomFieldIdRequest(StrictModel):
    """Update an Opportunity Custom Field by modifying its name, type, value acceptance settings, role restrictions, or choice options. Changes take effect immediately in the Close UI, and type conversions are handled automatically when required."""
    path: PutCustomFieldOpportunityCustomFieldIdRequestPath
    body: PutCustomFieldOpportunityCustomFieldIdRequestBody | None = None

# Operation: delete_opportunity_custom_field
class DeleteCustomFieldOpportunityCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the custom field to delete.")
class DeleteCustomFieldOpportunityCustomFieldIdRequest(StrictModel):
    """Permanently delete a custom field from Opportunities. The field will be immediately removed from all Opportunity records and API responses, and this action cannot be undone."""
    path: DeleteCustomFieldOpportunityCustomFieldIdRequestPath

# Operation: list_activity_custom_fields
class GetCustomFieldActivityRequestQuery(StrictModel):
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Maximum number of custom fields to return in the response. Limits the result set size for pagination or performance optimization.")
class GetCustomFieldActivityRequest(StrictModel):
    """Retrieve all custom fields configured for activities in your organization. Use the limit parameter to control the number of results returned."""
    query: GetCustomFieldActivityRequestQuery | None = None

# Operation: create_activity_custom_field
class PostCustomFieldActivityRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the custom field. This is the label shown to users when interacting with the field.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type of the field, which determines what kind of values it can store (e.g., text, number, date, choice).")
    custom_activity_type_id: str = Field(default=..., description="The ID of the Custom Activity Type this field belongs to. The field will be associated with and available only for activities of this type.")
    required: bool | None = Field(default=None, description="Whether this field must be populated before an activity can be published. When enabled, the field becomes mandatory for activity creation.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether this field can store multiple values simultaneously. When enabled, the field can hold a collection of values instead of a single value.")
    options: list[dict[str, Any]] | None = Field(default=None, description="A list of predefined options available for selection in choice-type fields. Each option represents a valid value users can select from.")
class PostCustomFieldActivityRequest(StrictModel):
    """Create a new custom field for a specific Custom Activity Type. Custom fields extend activity records with additional data attributes and can be configured as required or optional."""
    body: PostCustomFieldActivityRequestBody

# Operation: get_activity_custom_field
class GetCustomFieldActivityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Activity Custom Field to retrieve.")
class GetCustomFieldActivityIdRequest(StrictModel):
    """Retrieve the details of a specific Activity Custom Field by its unique identifier. Use this to access configuration, metadata, and settings for a custom field associated with activities."""
    path: GetCustomFieldActivityIdRequestPath

# Operation: update_activity_custom_field
class PutCustomFieldActivityCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the Activity Custom Field to update.")
class PutCustomFieldActivityCustomFieldIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="New display name for the custom field.")
    required: bool | None = Field(default=None, description="Whether this field must be populated before publishing an activity.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether this field allows users to select or enter multiple values.")
    restricted_to_roles: list[str] | None = Field(default=None, description="List of role identifiers that are permitted to edit this field. If specified, only users with these roles can modify the field value.")
    options: list[dict[str, Any]] | None = Field(default=None, description="Updated list of available choices for a choices-type field. Each option should include its identifier and display label.")
class PutCustomFieldActivityCustomFieldIdRequest(StrictModel):
    """Update an existing Activity Custom Field by modifying its name, requirements, multi-value support, role-based access restrictions, or choice options. The field type and associated activity type cannot be changed."""
    path: PutCustomFieldActivityCustomFieldIdRequestPath
    body: PutCustomFieldActivityCustomFieldIdRequestBody | None = None

# Operation: delete_activity_custom_field
class DeleteCustomFieldActivityCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the Activity Custom Field to delete.")
class DeleteCustomFieldActivityCustomFieldIdRequest(StrictModel):
    """Permanently delete an Activity Custom Field. The field will be immediately removed from all Custom Activity API responses and cannot be recovered."""
    path: DeleteCustomFieldActivityCustomFieldIdRequestPath

# Operation: create_custom_object_field
class PostCustomFieldCustomObjectTypeRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the custom field, shown in the user interface.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type that defines what kind of values this field accepts (e.g., text, number, date, choice).")
    custom_object_type_id: str = Field(default=..., description="The unique identifier of the Custom Object Type that this field belongs to.")
    required: bool | None = Field(default=None, description="Whether this field must have a value before the custom object can be saved.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether this field can store multiple values instead of a single value.")
    editable_with_roles: list[str] | None = Field(default=None, description="A list of role identifiers that are permitted to edit this field. If not specified, all roles may edit the field.")
    options: list[dict[str, Any]] | None = Field(default=None, description="A list of predefined options available for selection when the field type is set to choice. Each option should be formatted as specified by the field type.")
class PostCustomFieldCustomObjectTypeRequest(StrictModel):
    """Create a new custom field for a specific Custom Object Type. The field will be added to the object type's schema and can be configured as required or optional, with support for multiple values and role-based edit permissions."""
    body: PostCustomFieldCustomObjectTypeRequestBody

# Operation: get_custom_field
class GetCustomFieldCustomObjectTypeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom field to retrieve.")
class GetCustomFieldCustomObjectTypeIdRequest(StrictModel):
    """Retrieve the details of a specific custom field associated with a custom object type. This includes field configuration, type, and metadata."""
    path: GetCustomFieldCustomObjectTypeIdRequestPath

# Operation: update_custom_field
class PutCustomFieldCustomObjectTypeCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the custom field to update.")
class PutCustomFieldCustomObjectTypeCustomFieldIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new display name for the custom field.")
    required: bool | None = Field(default=None, description="Whether this field must be populated to save the custom object.")
    accepts_multiple_values: bool | None = Field(default=None, description="Whether this field can store multiple values simultaneously.")
    editable_with_roles: list[str] | None = Field(default=None, description="List of role identifiers that are permitted to edit this field's values. If specified, only users with these roles can modify the field.")
    options: list[dict[str, Any]] | None = Field(default=None, description="Updated list of available choices for a choices-type field. Each item represents a selectable option.")
class PutCustomFieldCustomObjectTypeCustomFieldIdRequest(StrictModel):
    """Update a custom object field's configuration, including its name, requirement status, multi-value support, role-based edit restrictions, and choice options. The field type and custom object type cannot be modified."""
    path: PutCustomFieldCustomObjectTypeCustomFieldIdRequestPath
    body: PutCustomFieldCustomObjectTypeCustomFieldIdRequestBody | None = None

# Operation: delete_custom_field
class DeleteCustomFieldCustomObjectTypeCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the custom field to delete.")
class DeleteCustomFieldCustomObjectTypeCustomFieldIdRequest(StrictModel):
    """Permanently delete a custom field from a custom object type. The field will be immediately removed from all Custom Object API responses."""
    path: DeleteCustomFieldCustomObjectTypeCustomFieldIdRequestPath

# Operation: create_shared_custom_field
class PostCustomFieldSharedRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the custom field. This is the label users will see when interacting with this field.")
    type_: str = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type that defines how values in this custom field are stored and validated (e.g., text, number, date, dropdown).")
    associations: list[dict[str, Any]] | None = Field(default=None, description="A list of object types this custom field can be applied to. Specifies which entities in your workspace can use this shared custom field.")
class PostCustomFieldSharedRequest(StrictModel):
    """Create a new shared custom field that can be reused across multiple object types in your workspace. Shared custom fields provide consistent data structure and validation across associated objects."""
    body: PostCustomFieldSharedRequestBody

# Operation: update_shared_custom_field
class PutCustomFieldSharedCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the shared custom field to update.")
class PutCustomFieldSharedCustomFieldIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the custom field. Provide a descriptive name to identify the field's purpose.")
    choices: list[str] | None = Field(default=None, description="Updated list of options for a choices field type. Each item represents an available choice that users can select. Only applicable for fields with a choices type.")
class PutCustomFieldSharedCustomFieldIdRequest(StrictModel):
    """Update a shared custom field by modifying its name or the available options for a choices field type. The field type itself cannot be changed after creation."""
    path: PutCustomFieldSharedCustomFieldIdRequestPath
    body: PutCustomFieldSharedCustomFieldIdRequestBody | None = None

# Operation: delete_custom_field_shared
class DeleteCustomFieldSharedCustomFieldIdRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the shared custom field to delete.")
class DeleteCustomFieldSharedCustomFieldIdRequest(StrictModel):
    """Permanently delete a shared custom field. The field will be immediately removed from all objects it was assigned to."""
    path: DeleteCustomFieldSharedCustomFieldIdRequestPath

# Operation: associate_shared_custom_field
class PostCustomFieldSharedSharedCustomFieldIdAssociationRequestPath(StrictModel):
    shared_custom_field_id: str = Field(default=..., description="The unique identifier of the Shared Custom Field to associate with an object type.")
class PostCustomFieldSharedSharedCustomFieldIdAssociationRequestBody(StrictModel):
    object_type: Literal["lead", "contact", "opportunity", "custom_activity_type", "custom_object_type"] = Field(default=..., description="The object type to associate the field with. Must be one of: lead, contact, opportunity, custom_activity_type, or custom_object_type.")
    custom_activity_type_id: str | None = Field(default=None, description="The ID of the Custom Activity Type. Required only when object_type is set to custom_activity_type.")
    custom_object_type_id: str | None = Field(default=None, description="The ID of the Custom Object Type. Required only when object_type is set to custom_object_type.")
    editable_with_roles: list[str] | None = Field(default=None, description="A list of Role IDs that are permitted to edit the values of this field on the associated object. Roles not included in this list will have read-only access.")
    required: bool | None = Field(default=None, description="Whether a value must be provided for this field on the associated object. Only applicable when object_type is custom_activity_type or custom_object_type.")
class PostCustomFieldSharedSharedCustomFieldIdAssociationRequest(StrictModel):
    """Associates a Shared Custom Field with a specific object type (Lead, Contact, Opportunity, Custom Activity Type, or Custom Object Type), optionally configuring edit permissions and field requirements."""
    path: PostCustomFieldSharedSharedCustomFieldIdAssociationRequestPath
    body: PostCustomFieldSharedSharedCustomFieldIdAssociationRequestBody

# Operation: update_shared_custom_field_association
class PutCustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestPath(StrictModel):
    shared_custom_field_id: str = Field(default=..., description="The unique identifier of the Shared Custom Field being associated.")
    object_type: str = Field(default=..., description="The object type to associate with this field. Valid values are: lead, contact, opportunity, custom_activity_type/<catype_id>, or custom_object_type/<cotype_id>.")
class PutCustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestBody(StrictModel):
    editable_with_roles: list[str] | None = Field(default=None, description="List of Role IDs that are permitted to edit the values of this field. Roles not included in this list cannot modify the field value.")
    required: bool | None = Field(default=None, description="Whether a value is mandatory for this field on the specified object type. When true, users must provide a value; when false, the field is optional.")
class PutCustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequest(StrictModel):
    """Update an existing Shared Custom Field Association by modifying its required status and role-based edit permissions. Specify the object type (lead, contact, opportunity, or custom types) to target the correct association."""
    path: PutCustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestPath
    body: PutCustomFieldSharedSharedCustomFieldIdAssociationObjectTypeRequestBody | None = None

# Operation: remove_shared_custom_field_association
class DeleteCustomFieldSharedCustomFieldIdAssociationObjectTypeRequestPath(StrictModel):
    custom_field_id: str = Field(default=..., description="The unique identifier of the Shared Custom Field to disassociate.")
    object_type: str = Field(default=..., description="The object type to disassociate from. Valid values are: lead, contact, opportunity, custom_activity_type/<catype_id>, or custom_object_type/<cotype_id>, where <catype_id> and <cotype_id> are the respective type identifiers.")
class DeleteCustomFieldSharedCustomFieldIdAssociationObjectTypeRequest(StrictModel):
    """Remove a Shared Custom Field association from a specific object type (Lead, Contact, Opportunity, Custom Activity Type, or Custom Object Type). This disassociates the custom field from the target object type."""
    path: DeleteCustomFieldSharedCustomFieldIdAssociationObjectTypeRequestPath

# Operation: get_custom_field_schema
class GetCustomFieldSchemaObjectTypeRequestPath(StrictModel):
    object_type: str = Field(default=..., description="The object type to fetch the schema for. Use standard types (lead, contact, opportunity), activity with a category ID (activity/<cat_id>), or custom object with a type ID (custom_object/<cotype_id>).")
class GetCustomFieldSchemaObjectTypeRequest(StrictModel):
    """Retrieve the custom field schema for a specific object type, including all regular and shared custom fields in their defined order. Supports standard objects (lead, contact, opportunity) and dynamic objects (activities and custom objects)."""
    path: GetCustomFieldSchemaObjectTypeRequestPath

# Operation: reorder_custom_fields
class PutCustomFieldSchemaObjectTypeRequestPath(StrictModel):
    object_type: str = Field(default=..., description="The object type whose custom field schema should be reordered. Valid values include lead, contact, opportunity, activity with a category ID, or custom_object with a custom object type ID.")
class PutCustomFieldSchemaObjectTypeRequestBody(StrictModel):
    fields: list[PutCustomFieldSchemaObjectTypeBodyFieldsItem] = Field(default=..., description="An ordered array of field ID objects that defines the new field sequence. Each item should contain an id property; fields not included in this list will be automatically appended to the end.")
class PutCustomFieldSchemaObjectTypeRequest(StrictModel):
    """Reorder custom fields within a schema by specifying the desired field order. Fields omitted from the list will be appended at the end; to remove fields, delete them or disassociate shared custom fields instead."""
    path: PutCustomFieldSchemaObjectTypeRequestPath
    body: PutCustomFieldSchemaObjectTypeRequestBody

# Operation: enrich_field
class PostEnrichFieldRequestBody(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier for your organization.")
    object_type: Literal["lead", "contact"] = Field(default=..., description="The type of object to enrich: either 'lead' or 'contact'.")
    object_id: str = Field(default=..., description="The unique identifier of the lead or contact record to enrich.")
    field_id: str = Field(default=..., description="The unique identifier of the custom field to enrich.")
    set_new_value: bool | None = Field(default=None, description="Whether to persist the enriched value to the field. Defaults to true if not specified.")
    overwrite_existing_value: bool | None = Field(default=None, description="Whether to replace any existing field value with the enriched result. Defaults to false, preserving existing data unless explicitly overwritten.")
class PostEnrichFieldRequest(StrictModel):
    """Intelligently enrich a specific field on a lead or contact by analyzing existing data and external sources. The operation completes synchronously and optionally updates the field with the enriched value."""
    body: PostEnrichFieldRequestBody

# Operation: create_custom_activity_type
class PostCustomActivityRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for this custom activity type. This name identifies the activity type throughout the system.")
    description: str | None = Field(default=None, description="A detailed explanation of what this custom activity type is used for and its purpose.")
    api_create_only: bool | None = Field(default=None, description="When enabled, activity instances of this type can only be created through API calls, preventing creation through the user interface.")
    editable_with_roles: list[str] | None = Field(default=None, description="A list of role identifiers that are permitted to edit activities of this type. If not specified, default role permissions apply.")
    is_archived: bool | None = Field(default=None, description="When enabled, this activity type is marked as archived and will not appear in active selections, though existing instances remain accessible.")
class PostCustomActivityRequest(StrictModel):
    """Create a new custom activity type that serves as a template for activity instances. Custom activity types must be created before you can add custom fields to activities of that type."""
    body: PostCustomActivityRequestBody

# Operation: get_custom_activity
class GetCustomActivityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Activity Type to retrieve.")
class GetCustomActivityIdRequest(StrictModel):
    """Retrieve a specific Custom Activity Type by its ID, including detailed metadata about associated custom fields."""
    path: GetCustomActivityIdRequestPath

# Operation: update_custom_activity
class PutCustomActivityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Activity Type to update.")
class PutCustomActivityIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the custom activity type.")
    description: str | None = Field(default=None, description="A detailed explanation of the custom activity type's purpose and usage.")
    api_create_only: bool | None = Field(default=None, description="When enabled, instances of this activity type can only be created through API calls, preventing creation via the user interface.")
    editable_with_roles: list[str] | None = Field(default=None, description="A list of role identifiers that are permitted to edit instances of this activity type. Roles not included will be unable to modify activities of this type.")
    is_archived: bool | None = Field(default=None, description="When enabled, this activity type is marked as archived and becomes unavailable for new instance creation.")
    field_order: list[str] | None = Field(default=None, description="An ordered array of field IDs that determines the display sequence of fields in the user interface. The order specified here controls how fields appear to users.")
class PutCustomActivityIdRequest(StrictModel):
    """Update an existing Custom Activity Type's metadata including name, description, creation restrictions, editor permissions, archive status, and field display order. Field structure changes require the Custom Field API."""
    path: PutCustomActivityIdRequestPath
    body: PutCustomActivityIdRequestBody | None = None

# Operation: delete_custom_activity
class DeleteCustomActivityIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the custom activity type to delete.")
class DeleteCustomActivityIdRequest(StrictModel):
    """Permanently delete a custom activity type by its ID. This action cannot be undone and will remove the activity type from your system."""
    path: DeleteCustomActivityIdRequestPath

# Operation: list_custom_activities_instances
class GetActivityCustomRequestQuery(StrictModel):
    custom_activity_type_id: str | None = Field(default=None, description="Filter results to a specific custom activity type. When using this filter, the lead_id parameter is required to scope the results appropriately.")
class GetActivityCustomRequest(StrictModel):
    """Retrieve and filter custom activity instances. Supports filtering by custom activity type, with results including custom fields formatted as custom.{custom_field_id}."""
    query: GetActivityCustomRequestQuery | None = None

# Operation: create_custom_activity
class PostActivityCustomRequestBody(StrictModel):
    custom_activity_type_id: str = Field(default=..., description="The unique identifier of the Custom Activity Type to instantiate.")
    lead_id: str = Field(default=..., description="The unique identifier of the lead to associate with this activity.")
    pinned: bool | None = Field(default=None, description="Whether to pin this activity for increased visibility. Defaults to unpinned if not specified.")
class PostActivityCustomRequest(StrictModel):
    """Create a new Custom Activity instance for a lead. Activities are published by default with all required fields validated, or can be created as drafts to defer validation. Optionally pin the activity for visibility."""
    body: PostActivityCustomRequestBody

# Operation: get_custom_activity_instance
class GetActivityCustomIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Activity instance to retrieve.")
class GetActivityCustomIdRequest(StrictModel):
    """Retrieve a specific Custom Activity instance by its unique identifier. Use this to fetch detailed information about a single custom activity."""
    path: GetActivityCustomIdRequestPath

# Operation: update_custom_activity_instance
class PutActivityCustomIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Activity instance to update.")
class PutActivityCustomIdRequestBody(StrictModel):
    pinned: bool | None = Field(default=None, description="Set to true to pin the activity or false to unpin it. Omit to leave the pinned status unchanged.")
class PutActivityCustomIdRequest(StrictModel):
    """Update an existing Custom Activity instance by modifying custom fields, changing its status between draft and published states, or adjusting its pinned status."""
    path: PutActivityCustomIdRequestPath
    body: PutActivityCustomIdRequestBody | None = None

# Operation: delete_custom_activity_instance
class DeleteActivityCustomIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Activity instance to delete.")
class DeleteActivityCustomIdRequest(StrictModel):
    """Permanently delete a Custom Activity instance by its ID. This action cannot be undone."""
    path: DeleteActivityCustomIdRequestPath

# Operation: create_custom_object_type
class PostCustomObjectTypeRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name of the Custom Object Type. This is used to identify the type throughout the system.")
    name_plural: str = Field(default=..., description="The plural form of the Custom Object Type name. This is used in UI displays and lists where multiple instances are shown.")
    description: str | None = Field(default=None, description="An optional longer description that provides additional context or details about the purpose and use of this Custom Object Type.")
    api_create_only: bool | None = Field(default=None, description="When enabled, instances of this Custom Object Type can only be created through API clients. UI-based creation will be restricted. Defaults to false, allowing creation through all available interfaces.")
    editable_with_roles: list[str] | None = Field(default=None, description="An optional list of user roles that are permitted to edit instances of this Custom Object Type. If specified, only users with one of these roles can modify instances. If not specified, default role-based permissions apply.")
class PostCustomObjectTypeRequest(StrictModel):
    """Create a new Custom Object Type that serves as a blueprint for custom objects in your system. Custom Object Types must be created before you can add custom fields or create instances of that type."""
    body: PostCustomObjectTypeRequestBody

# Operation: get_custom_object_type
class GetCustomObjectTypeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier that specifies which Custom Object Type to retrieve.")
class GetCustomObjectTypeIdRequest(StrictModel):
    """Retrieve a specific Custom Object Type by its unique identifier, including comprehensive Custom Field metadata associated with it."""
    path: GetCustomObjectTypeIdRequestPath

# Operation: update_custom_object_type
class PutCustomObjectTypeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Object Type to update.")
class PutCustomObjectTypeIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name of the Custom Object Type.")
    name_plural: str | None = Field(default=None, description="The pluralized form of the Custom Object Type name, used in API responses and UI contexts.")
    description: str | None = Field(default=None, description="A detailed description explaining the purpose and use of this Custom Object Type.")
    api_create_only: bool | None = Field(default=None, description="When enabled, only API clients can create new instances of this type; UI-based creation is disabled.")
    editable_with_roles: list[str] | None = Field(default=None, description="A list of role identifiers whose members are permitted to edit instances of this type. If empty or omitted, all users with general edit permissions can modify instances.")
class PutCustomObjectTypeIdRequest(StrictModel):
    """Update an existing Custom Object Type's metadata including name, description, and access controls. Field structure cannot be modified through this operation."""
    path: PutCustomObjectTypeIdRequestPath
    body: PutCustomObjectTypeIdRequestBody | None = None

# Operation: delete_custom_object_type
class DeleteCustomObjectTypeIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Object Type to delete.")
class DeleteCustomObjectTypeIdRequest(StrictModel):
    """Permanently delete a Custom Object Type and remove it from your system. This action cannot be undone."""
    path: DeleteCustomObjectTypeIdRequestPath

# Operation: list_custom_objects
class GetCustomObjectRequestQuery(StrictModel):
    lead_id: str = Field(default=..., description="The unique identifier of the lead whose Custom Object instances you want to retrieve.")
    custom_object_type_id: str | None = Field(default=None, description="Optional filter to narrow results to a specific Custom Object Type by its unique identifier.")
class GetCustomObjectRequest(StrictModel):
    """Retrieve all Custom Object instances associated with a specific lead, with optional filtering by Custom Object Type. Custom field values are returned using the format custom.{custom_field_id}."""
    query: GetCustomObjectRequestQuery

# Operation: create_custom_object
class PostCustomObjectRequestBody(StrictModel):
    custom_object_type_id: str = Field(default=..., description="The type identifier for the Custom Object being created, which determines which Custom Fields are available for this instance.")
    lead_id: str = Field(default=..., description="The Lead identifier that this Custom Object instance will be associated with.")
    name: str = Field(default=..., description="A display name for this Custom Object instance.")
class PostCustomObjectRequest(StrictModel):
    """Create a new Custom Object instance linked to a lead. Custom Field values can be set using the custom.{custom_field_id} format."""
    body: PostCustomObjectRequestBody

# Operation: get_custom_object
class GetCustomObjectIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Object instance to retrieve.")
class GetCustomObjectIdRequest(StrictModel):
    """Retrieve a single Custom Object instance by its unique identifier. Returns the complete object data for the specified Custom Object."""
    path: GetCustomObjectIdRequestPath

# Operation: update_custom_object
class PutCustomObjectIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Object instance to update.")
class PutCustomObjectIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for this Custom Object instance.")
class PutCustomObjectIdRequest(StrictModel):
    """Update a Custom Object instance by modifying its custom fields and display name. Use this operation to add, change, or remove custom field values and update the instance's name property."""
    path: PutCustomObjectIdRequestPath
    body: PutCustomObjectIdRequestBody | None = None

# Operation: delete_custom_object
class DeleteCustomObjectIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the Custom Object instance to delete.")
class DeleteCustomObjectIdRequest(StrictModel):
    """Permanently delete a Custom Object instance by its unique identifier. This action cannot be undone."""
    path: DeleteCustomObjectIdRequestPath

# Operation: unsubscribe_email
class PostUnsubscribeEmailRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address to unsubscribe from Close's messaging system. Must be a valid email format.", json_schema_extra={'format': 'email'})
class PostUnsubscribeEmailRequest(StrictModel):
    """Remove an email address from Close's messaging system. Use this when an email has unsubscribed through external channels (such as a mailing list) and needs to be marked as unsubscribed in Close."""
    body: PostUnsubscribeEmailRequestBody

# Operation: resubscribe_email
class DeleteUnsubscribeEmailEmailAddressRequestPath(StrictModel):
    email_address: str = Field(default=..., description="The email address to resubscribe. Must be a valid email format.", json_schema_extra={'format': 'email'})
class DeleteUnsubscribeEmailEmailAddressRequest(StrictModel):
    """Resubscribe an email address to receive messages from Close. Use this operation to restore messaging delivery for an email that was previously unsubscribed."""
    path: DeleteUnsubscribeEmailEmailAddressRequestPath

# Operation: search_contacts_and_leads
class PostApiV1DataSearchRequestBodyQueryField(StrictModel):
    type_: Literal["regular_field", "custom_field"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Specifies whether the field is a standard built-in field or a custom field defined for your organization.")
    object_type: str | None = Field(default=None, validation_alias="object_type", serialization_alias="object_type", description="The object type that contains the field being filtered on (e.g., 'contact' or 'lead').")
    field_name: str | None = Field(default=None, validation_alias="field_name", serialization_alias="field_name", description="The name of the field to filter on when using 'field_condition' query type.")
class PostApiV1DataSearchRequestBodyQueryCondition(StrictModel):
    type_: Literal["boolean", "current_user", "exists", "text", "term", "reference", "number_range"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of condition to apply: 'boolean' for true/false values, 'current_user' to reference the authenticated user, 'exists' to check field presence, 'text' for text matching, 'term' for exact value matching, 'reference' for linked objects, or 'number_range' for numeric comparisons.")
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The value to match against for boolean or text-based conditions.")
    mode: Literal["full_words", "phrase"] | None = Field(default=None, validation_alias="mode", serialization_alias="mode", description="Text matching strategy: 'full_words' matches complete words only, 'phrase' matches the exact phrase as entered.")
    values: list[str] | None = Field(default=None, validation_alias="values", serialization_alias="values", description="Array of values to match against for 'term' conditions; returns objects where the field matches any value in the list.")
    reference_type: str | None = Field(default=None, validation_alias="reference_type", serialization_alias="reference_type", description="The type of object being referenced in a 'reference' condition (e.g., 'user', 'company').")
    object_ids: list[str] | None = Field(default=None, validation_alias="object_ids", serialization_alias="object_ids", description="Array of object IDs to match against in a 'reference' condition; returns objects linked to any of these IDs.")
    gt: float | None = Field(default=None, validation_alias="gt", serialization_alias="gt", description="Lower bound (exclusive) for numeric range filtering; matches values strictly greater than this number.")
    gte: float | None = Field(default=None, validation_alias="gte", serialization_alias="gte", description="Lower bound (inclusive) for numeric range filtering; matches values greater than or equal to this number.")
    lt: float | None = Field(default=None, validation_alias="lt", serialization_alias="lt", description="Upper bound (exclusive) for numeric range filtering; matches values strictly less than this number.")
    lte: float | None = Field(default=None, validation_alias="lte", serialization_alias="lte", description="Upper bound (inclusive) for numeric range filtering; matches values less than or equal to this number.")
class PostApiV1DataSearchRequestBodyQuery(StrictModel):
    type_: Literal["and", "or", "id", "object_type", "text", "has_related", "field_condition"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of query to execute: 'and'/'or' for combining multiple conditions, 'id' to search by object ID, 'object_type' to filter by entity type, 'text' for full-text search, 'has_related' to find objects with related entities, or 'field_condition' for attribute-based filtering.")
    queries: list[dict[str, Any]] | None = Field(default=None, validation_alias="queries", serialization_alias="queries", description="Array of nested query objects used with 'and'/'or' query types to combine multiple filter conditions.")
    object_type: Literal["contact", "lead", "contact_phone", "contact_email", "contact_url", "address"] | None = Field(default=None, validation_alias="object_type", serialization_alias="object_type", description="The entity type to filter by: 'contact', 'lead', 'contact_phone', 'contact_email', 'contact_url', or 'address'.")
    this_object_type: str | None = Field(default=None, validation_alias="this_object_type", serialization_alias="this_object_type", description="The primary object type being queried in a 'has_related' query (e.g., 'contact' or 'lead').")
    related_object_type: str | None = Field(default=None, validation_alias="related_object_type", serialization_alias="related_object_type", description="The related object type to check for existence in a 'has_related' query (e.g., 'contact_email' or 'contact_phone').")
    related_query: dict[str, Any] | None = Field(default=None, validation_alias="related_query", serialization_alias="related_query", description="A query object defining conditions that related objects must satisfy in a 'has_related' query.")
    negate: bool | None = Field(default=None, validation_alias="negate", serialization_alias="negate", description="When enabled, inverts the query logic to return objects that do NOT match the specified conditions.")
    field: PostApiV1DataSearchRequestBodyQueryField | None = None
    condition: PostApiV1DataSearchRequestBodyQueryCondition | None = None
class PostApiV1DataSearchRequestBody(StrictModel):
    fields: dict[str, Any] | None = Field(default=None, validation_alias="_fields", serialization_alias="_fields", description="Specify which fields to include in results for each object type. Provide as an object where keys are object type names (e.g., 'contact', 'lead') and values are arrays of field names to return.")
    results_limit: int | None = Field(default=None, description="Maximum total number of results to return across all pages. Set to 0 with include_counts enabled to retrieve only the result count without fetching records.", ge=0)
    include_counts: bool | None = Field(default=None, description="When enabled, the response includes a count object showing both the limited count (results returned) and total count (all matching records).")
    sort: list[PostApiV1DataSearchBodySortItem] | None = Field(default=None, description="Array of sort specifications to order results. Only numeric, date, and text fields directly on the object can be sorted; specify field name and direction for each sort criterion.")
    limit: int | None = Field(default=None, validation_alias="_limit", serialization_alias="_limit", description="Number of results to return per page for pagination; must be at least 1.", ge=1)
    query: PostApiV1DataSearchRequestBodyQuery
class PostApiV1DataSearchRequest(StrictModel):
    """Search and filter contacts and leads using advanced query logic with support for complex conditions, text search, and related object queries. Returns paginated results with optional field selection and sorting."""
    body: PostApiV1DataSearchRequestBody

# ============================================================================
# Component Models
# ============================================================================

class PostActivityEmailBodyAttachmentsItem(PermissiveModel):
    url: str = Field(..., description="URL from Files API download.url field. Must begin with https://app.close.com/go/file/", json_schema_extra={'format': 'uri'})
    filename: str = Field(..., description="Filename of the attachment.")
    content_type: str = Field(..., description="MIME type of the attachment.")
    size: int = Field(..., description="Size of the attachment in bytes.")

class PostActivityNoteBodyAttachmentsItem(PermissiveModel):
    url: str = Field(..., description="URL from the Files API download.url field. Must begin with https://app.close.com/go/file/.")
    filename: str = Field(..., description="Name of the attachment file.")
    content_type: str = Field(..., description="MIME type of the attachment.")

class PostActivityWhatsappMessageBodyAttachmentsItem(PermissiveModel):
    url: str = Field(..., description="URL from the Files API download.url field. Must begin with https://app.close.com/go/file/.", json_schema_extra={'format': 'uri'})
    filename: str = Field(..., description="The filename of the attachment.")
    content_type: str = Field(..., description="The MIME content type of the attachment.")

class PostApiV1DataSearchBodySortItemField(PermissiveModel):
    """Field to sort by"""
    object_type: str | None = None
    type_: Literal["regular_field", "custom_field"] | None = Field(None, validation_alias="type", serialization_alias="type")
    field_name: str | None = None

class PostApiV1DataSearchBodySortItem(PermissiveModel):
    direction: Literal["asc", "desc"] | None = Field(None, description="Sort direction")
    field: PostApiV1DataSearchBodySortItemField | None = Field(None, description="Field to sort by")

class PostContactBodyEmailsItem(PermissiveModel):
    email: str | None = None
    type_: Literal["office", "direct", "mobile", "home", "other"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostContactBodyPhonesItem(PermissiveModel):
    phone: str | None = None
    type_: Literal["office", "direct", "mobile", "home", "fax", "other"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostWebhookBodyEventsItem(PermissiveModel):
    object_type: str = Field(..., description="The type of object for this event")
    action: str = Field(..., description="The action for this event")

class PutActivityNoteIdBodyAttachmentsItem(PermissiveModel):
    url: str = Field(..., description="URL from the Files API download.url field. Must begin with https://app.close.com/go/file/.")
    filename: str = Field(..., description="Name of the attachment file.")
    content_type: str = Field(..., description="MIME type of the attachment.")

class PutActivityWhatsappMessageIdBodyAttachmentsItem(PermissiveModel):
    url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    filename: str | None = None
    content_type: str | None = None

class PutCustomFieldSchemaObjectTypeBodyFieldsItem(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the Custom Field.")

class PutPipelinePipelineIdBodyStatusesItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the opportunity status.")

class PutWebhookIdBodyEventsItem(PermissiveModel):
    object_type: str
    action: str


# Rebuild models to resolve forward references (required for circular refs)
PostActivityEmailBodyAttachmentsItem.model_rebuild()
PostActivityNoteBodyAttachmentsItem.model_rebuild()
PostActivityWhatsappMessageBodyAttachmentsItem.model_rebuild()
PostApiV1DataSearchBodySortItem.model_rebuild()
PostApiV1DataSearchBodySortItemField.model_rebuild()
PostContactBodyEmailsItem.model_rebuild()
PostContactBodyPhonesItem.model_rebuild()
PostWebhookBodyEventsItem.model_rebuild()
PutActivityNoteIdBodyAttachmentsItem.model_rebuild()
PutActivityWhatsappMessageIdBodyAttachmentsItem.model_rebuild()
PutCustomFieldSchemaObjectTypeBodyFieldsItem.model_rebuild()
PutPipelinePipelineIdBodyStatusesItem.model_rebuild()
PutWebhookIdBodyEventsItem.model_rebuild()

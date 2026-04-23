"""
Mailersend MCP Server - Pydantic Models

Generated: 2026-04-23 21:27:16 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "AddADomainRequest",
    "AddASenderIdentityRequest",
    "AddBlocklistRecipientsRequest",
    "AddHardBouncesRecipientsRequest",
    "AddSpamComplaintsRecipientsRequest",
    "AddUnsubscribesRecipientsRequest",
    "CreateAnEmailVerificationListRequest",
    "DeleteADomainRequest",
    "DeleteAnInboundRouteRequest",
    "DeleteAnSmsInboundRouteRequest",
    "DeleteAnSmsPhoneNumberRequest",
    "DeleteAnSmsWebhookRequest",
    "DeleteARecipientRequest",
    "DeleteASenderIdentityByEmailRequest",
    "DeleteASenderIdentityRequest",
    "DeleteATokenRequest",
    "DeleteAUserRequest",
    "DeleteAWebhookRequest",
    "DeleteBlocklistRecipientsRequest",
    "DeleteHardBouncesRecipientsRequest",
    "DeleteScheduledMessageRequest",
    "DeleteSmtpUserRequest",
    "DeleteSpamComplaintsRecipientsRequest",
    "DeleteUnsubscribesRecipientsRequest",
    "GetActivityDataByDateRequest",
    "GetActivityOfSingleSmsMessageRequest",
    "GetAnSmsMessageRequest",
    "GetAnSmsPhoneNumberRequest",
    "GetAnSmsRecipientRequest",
    "GetAWebhookRequest",
    "GetBulkEmailStatusRequest",
    "GetDnsRecordsRequest",
    "GetEmailVerificationListResultsRequest",
    "GetInformationForSingleMessageRequest",
    "GetListOfActivitiesRequest",
    "GetListOfSmsWebhooksRequest",
    "GetListOfSmtpUsersRequest",
    "GetListOfWebhooksRequest",
    "GetOneUserRequest",
    "GetOpensByCountryRequest",
    "GetOpensByReadingEnvironmentRequest",
    "GetOpensByUserAgentRequest",
    "GetRecipientsForADomainRequest",
    "GetSingleActivityRequest",
    "GetSingleDomainRequest",
    "GetSingleEmailVerificationListRequest",
    "GetSingleInboundRouteRequest",
    "GetSingleRecipientRequest",
    "GetSingleScheduledMessageRequest",
    "GetSingleSenderIdentityByEmailRequest",
    "GetSingleSenderIdentityRequest",
    "GetSingleSmsInboundRouteRequest",
    "GetSingleSmsWebhookRequest",
    "GetSingleSmtpUserRequest",
    "GetVerificationStatusRequest",
    "SendAnEmailRequest",
    "SendAnSmsRequest",
    "SendBulkEmailsRequest",
    "UpdateAnInboundRouteRequest",
    "UpdateASenderIdentityByEmailRequest",
    "UpdateASenderIdentityRequest",
    "UpdateATokenSettingsRequest",
    "UpdateDomainSettingsRequest",
    "UpdateSingleSmsPhoneNumberRequest",
    "UpdateSingleSmsRecipientRequest",
    "UpdateSingleSmsWebhookRequest",
    "UpdateSmsInboundRouteRequest",
    "UpdateSmtpUserRequest",
    "UpdateUserRequest",
    "VerifyAnEmailRequest",
    "VerifyAnEmailVerificationListRequest",
    "EmailTo",
    "SendAnSmsBodyPersonalizationItem",
    "SendEmailRequest",
    "UpdateAnInboundRouteBodyForwardsItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: send_email
class SendAnEmailRequestBodyFrom(StrictModel):
    email: str = Field(default=..., validation_alias="email", serialization_alias="email", description="The sender's email address in standard email format (e.g., info@yourdomain.com). This address will appear as the 'From' field in the email.", json_schema_extra={'format': 'email'}, examples=['info@yourdomain.com'])
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The sender's display name or organization name that appears alongside the email address (e.g., 'Company Name'). Optional; if omitted, only the email address will be displayed.", examples=['Company Name'])
class SendAnEmailRequestBody(StrictModel):
    to: list[EmailTo] = Field(default=..., description="Array of recipient email addresses. Each address should be in standard email format. At least one recipient is required.")
    subject: str = Field(default=..., description="The email subject line. Provide a clear, concise subject that summarizes the email content (e.g., 'Hello Client').", examples=['Hello Client'])
    text: str = Field(default=..., description="The email message body as plain text. Include the main content and any relevant information for the recipient (e.g., 'This is just a friendly hello from your friends.').", examples=['This is just a friendly hello from your friends.'])
    from_: SendAnEmailRequestBodyFrom = Field(default=..., validation_alias="from", serialization_alias="from")
class SendAnEmailRequest(StrictModel):
    """Send an email message from a specified sender address to one or more recipients. Use this operation to deliver transactional or notification emails with a subject line and message body."""
    body: SendAnEmailRequestBody

# Operation: send_bulk_emails
class SendBulkEmailsRequestBody(StrictModel):
    body: list[SendEmailRequest] = Field(default=..., description="Array of email objects to send. Each object should contain recipient, subject, and message content. Order is preserved for processing.")
class SendBulkEmailsRequest(StrictModel):
    """Send multiple emails in a single batch request. Accepts an array of email configurations to be processed and delivered."""
    body: SendBulkEmailsRequestBody

# Operation: get_bulk_email_status
class GetBulkEmailStatusRequestPath(StrictModel):
    bulk_email_id: str = Field(default=..., description="The unique identifier of the bulk email campaign whose status you want to retrieve.")
class GetBulkEmailStatusRequest(StrictModel):
    """Retrieve the current status and details of a bulk email campaign. Use this to check delivery progress, completion state, and any associated metrics for a specific bulk email operation."""
    path: GetBulkEmailStatusRequestPath

# Operation: list_activities_for_domain
class GetListOfActivitiesRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain for which to retrieve activities.")
class GetListOfActivitiesRequestQuery(StrictModel):
    date_from: int = Field(default=..., description="The start of the activity time range as a Unix timestamp in UTC. Activities on or after this date will be included.", json_schema_extra={'format': 'unix-timestamp'})
    date_to: int = Field(default=..., description="The end of the activity time range as a Unix timestamp in UTC. Activities on or before this date will be included.", json_schema_extra={'format': 'unix-timestamp'})
class GetListOfActivitiesRequest(StrictModel):
    """Retrieve a list of activities for a specific domain within a given time range. Results are filtered by start and end dates in UTC."""
    path: GetListOfActivitiesRequestPath
    query: GetListOfActivitiesRequestQuery

# Operation: get_activity
class GetSingleActivityRequestPath(StrictModel):
    activity_id: str = Field(default=..., description="The unique identifier of the activity to retrieve.")
class GetSingleActivityRequest(StrictModel):
    """Retrieve detailed information about a specific activity by its unique identifier."""
    path: GetSingleActivityRequestPath

# Operation: get_activity_data_by_date_range
class GetActivityDataByDateRequestQuery(StrictModel):
    date_from: int = Field(default=..., description="Start of the date range as a Unix timestamp (seconds since epoch). Must be earlier than or equal to date_to.", json_schema_extra={'format': 'unix-timestamp'})
    date_to: int = Field(default=..., description="End of the date range as a Unix timestamp (seconds since epoch). Must be later than or equal to date_from.", json_schema_extra={'format': 'unix-timestamp'})
    events: list[str] = Field(default=..., description="List of event types to include in the results. Specify which activity events to retrieve (e.g., user_login, page_view, transaction). Order may affect result grouping or filtering behavior.")
class GetActivityDataByDateRequest(StrictModel):
    """Retrieves activity data for a specified date range. Returns analytics events that occurred between the provided start and end timestamps."""
    query: GetActivityDataByDateRequestQuery

# Operation: list_opens_by_country
class GetOpensByCountryRequestQuery(StrictModel):
    date_from: int = Field(default=..., description="Start of the date range as a Unix timestamp (seconds since epoch). Defines the beginning of the analytics period to query.", json_schema_extra={'format': 'unix-timestamp'})
    date_to: int = Field(default=..., description="End of the date range as a Unix timestamp (seconds since epoch). Defines the end of the analytics period to query. Must be equal to or after date_from.", json_schema_extra={'format': 'unix-timestamp'})
class GetOpensByCountryRequest(StrictModel):
    """Retrieve email open metrics aggregated by country for a specified date range. Returns open counts and statistics grouped by geographic location."""
    query: GetOpensByCountryRequestQuery

# Operation: list_opens_by_user_agent
class GetOpensByUserAgentRequestQuery(StrictModel):
    date_from: int = Field(default=..., description="Start of the time range as a Unix timestamp (seconds since epoch). This defines the beginning of the analytics period to query.", json_schema_extra={'format': 'unix-timestamp'})
    date_to: int = Field(default=..., description="End of the time range as a Unix timestamp (seconds since epoch). This defines the end of the analytics period to query.", json_schema_extra={'format': 'unix-timestamp'})
class GetOpensByUserAgentRequest(StrictModel):
    """Retrieves analytics data showing the number of opens grouped by user-agent within a specified time range. Use this to understand which browsers, devices, and applications are opening your content."""
    query: GetOpensByUserAgentRequestQuery

# Operation: get_opens_by_reading_environment
class GetOpensByReadingEnvironmentRequestQuery(StrictModel):
    date_from: int = Field(default=..., description="Start of the date range as a Unix timestamp (seconds since epoch). This defines the beginning of the analytics period to query.", json_schema_extra={'format': 'unix-timestamp'})
    date_to: int = Field(default=..., description="End of the date range as a Unix timestamp (seconds since epoch). This defines the end of the analytics period to query.", json_schema_extra={'format': 'unix-timestamp'})
class GetOpensByReadingEnvironmentRequest(StrictModel):
    """Retrieves analytics data on content opens segmented by reading environment (e.g., web, mobile, app). Results are filtered by the specified date range."""
    query: GetOpensByReadingEnvironmentRequestQuery

# Operation: create_domain
class AddADomainRequestBody(StrictModel):
    name: str = Field(default=..., description="The fully-qualified domain name to register (e.g., domain.com). Must be a valid domain format.", examples=['domain.com'])
class AddADomainRequest(StrictModel):
    """Register a new domain in the system. The domain name should be a valid fully-qualified domain name (e.g., domain.com)."""
    body: AddADomainRequestBody

# Operation: get_domain
class GetSingleDomainRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain to retrieve.")
class GetSingleDomainRequest(StrictModel):
    """Retrieve detailed information about a specific domain by its ID. Returns the domain's configuration, status, and metadata."""
    path: GetSingleDomainRequestPath

# Operation: delete_domain
class DeleteADomainRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain to delete.")
class DeleteADomainRequest(StrictModel):
    """Permanently delete a domain and remove it from the system. This action cannot be undone."""
    path: DeleteADomainRequestPath

# Operation: list_recipients_for_domain
class GetRecipientsForADomainRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain for which to retrieve recipients.")
class GetRecipientsForADomainRequest(StrictModel):
    """Retrieve all recipients associated with a specific domain. This returns the list of email recipients configured for the given domain."""
    path: GetRecipientsForADomainRequestPath

# Operation: update_domain_settings
class UpdateDomainSettingsRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain whose settings should be updated.")
class UpdateDomainSettingsRequestBody(StrictModel):
    track_content: bool | None = Field(default=None, description="Enable or disable content tracking for this domain. When enabled, the system will monitor and record domain content activity.", examples=[False])
class UpdateDomainSettingsRequest(StrictModel):
    """Update configuration settings for a specific domain. Allows modification of domain-level preferences including content tracking behavior."""
    path: UpdateDomainSettingsRequestPath
    body: UpdateDomainSettingsRequestBody | None = None

# Operation: list_dns_records
class GetDnsRecordsRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain for which to retrieve DNS records.")
class GetDnsRecordsRequest(StrictModel):
    """Retrieve all DNS records configured for a specific domain. Returns a collection of DNS records including their types, values, and configuration details."""
    path: GetDnsRecordsRequestPath

# Operation: get_domain_verification_status
class GetVerificationStatusRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain whose verification status you want to check.")
class GetVerificationStatusRequest(StrictModel):
    """Retrieve the current verification status of a domain, including whether it has been successfully verified and any relevant verification details."""
    path: GetVerificationStatusRequestPath

# Operation: create_sender_identity
class AddASenderIdentityRequestBody(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of your domain where this sender identity will be registered.", examples=['{domain_id}'])
    email: str = Field(default=..., description="The email address for this sender identity. Must be a valid email format (e.g., user@example.com).", json_schema_extra={'format': 'email'}, examples=['client@email.com'])
    name: str = Field(default=..., description="The display name associated with this sender identity, shown to recipients when emails are sent (e.g., 'John Smith' or 'Support Team').", examples=['Client Name'])
class AddASenderIdentityRequest(StrictModel):
    """Register a new sender identity for your domain, enabling you to send emails from a specific email address with an associated display name."""
    body: AddASenderIdentityRequestBody

# Operation: get_sender_identity
class GetSingleSenderIdentityRequestPath(StrictModel):
    identity_id: str = Field(default=..., description="The unique identifier of the sender identity to retrieve.")
class GetSingleSenderIdentityRequest(StrictModel):
    """Retrieve detailed information about a specific sender identity by its ID. Use this to view configuration and settings for an individual sender identity."""
    path: GetSingleSenderIdentityRequestPath

# Operation: update_sender_identity
class UpdateASenderIdentityRequestPath(StrictModel):
    identity_id: str = Field(default=..., description="The unique identifier of the sender identity to update.")
class UpdateASenderIdentityRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new display name for the sender identity. This is how the identity will be presented in outgoing messages.", examples=['New Name'])
class UpdateASenderIdentityRequest(StrictModel):
    """Update the configuration of an existing sender identity, such as its display name. This allows you to modify how your sender identity appears in outgoing communications."""
    path: UpdateASenderIdentityRequestPath
    body: UpdateASenderIdentityRequestBody | None = None

# Operation: delete_sender_identity
class DeleteASenderIdentityRequestPath(StrictModel):
    identity_id: str = Field(default=..., description="The unique identifier of the sender identity to delete. This ID must correspond to an existing sender identity in your account.")
class DeleteASenderIdentityRequest(StrictModel):
    """Permanently delete a sender identity from your account. Once deleted, this identity can no longer be used to send messages."""
    path: DeleteASenderIdentityRequestPath

# Operation: get_sender_identity_by_email
class GetSingleSenderIdentityByEmailRequestPath(StrictModel):
    client_email_com: str = Field(default=..., validation_alias="client@email.com", serialization_alias="client@email.com", description="The email address of the sender identity to retrieve. Must be a valid email format.", json_schema_extra={'format': 'email'})
class GetSingleSenderIdentityByEmailRequest(StrictModel):
    """Retrieve a single sender identity by its email address. Use this to look up configuration and details for a specific sender."""
    path: GetSingleSenderIdentityByEmailRequestPath

# Operation: update_sender_identity_by_email
class UpdateASenderIdentityByEmailRequestPath(StrictModel):
    client_email_com: str = Field(default=..., validation_alias="client@email.com", serialization_alias="client@email.com", description="The email address of the sender identity to update. Must be a valid email format.", json_schema_extra={'format': 'email'})
class UpdateASenderIdentityByEmailRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new display name for the sender identity. Optional field to customize how the sender appears in outgoing communications.", examples=['New Name'])
class UpdateASenderIdentityByEmailRequest(StrictModel):
    """Update the configuration of a sender identity using its email address. Allows modification of sender identity properties such as the display name."""
    path: UpdateASenderIdentityByEmailRequestPath
    body: UpdateASenderIdentityByEmailRequestBody | None = None

# Operation: delete_sender_identity_by_email
class DeleteASenderIdentityByEmailRequestPath(StrictModel):
    client_email_com: str = Field(default=..., validation_alias="client@email.com", serialization_alias="client@email.com", description="The email address of the sender identity to delete. Must be a valid email format.", json_schema_extra={'format': 'email'})
class DeleteASenderIdentityByEmailRequest(StrictModel):
    """Permanently delete a sender identity from your account using its email address. This action cannot be undone."""
    path: DeleteASenderIdentityByEmailRequestPath

# Operation: get_inbound_route
class GetSingleInboundRouteRequestPath(StrictModel):
    inbound_id: str = Field(default=..., description="The unique identifier of the inbound route to retrieve.")
class GetSingleInboundRouteRequest(StrictModel):
    """Retrieve the configuration and details of a specific inbound route by its ID. Use this to view routing rules, destination settings, and other properties of an individual inbound route."""
    path: GetSingleInboundRouteRequestPath

# Operation: update_inbound_route
class UpdateAnInboundRouteRequestPath(StrictModel):
    inbound_id: str = Field(default=..., description="The unique identifier of the inbound route to update. This ID is required to target the specific route for modification.")
class UpdateAnInboundRouteRequestBodyMatchFilter(StrictModel):
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of matching filter to apply. Use 'match_all' to process all requests, or specify a more restrictive filter type to target specific request patterns.", examples=['match_all'])
class UpdateAnInboundRouteRequestBodyCatchFilter(StrictModel):
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of catch filter to apply as a fallback. Use 'catch_all' to handle requests that don't match other filters, or specify a more specific filter type.", examples=['catch_all'])
class UpdateAnInboundRouteRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable name for the inbound route to help identify its purpose or destination.", examples=['New Route Name'])
    domain_enabled: bool | None = Field(default=None, description="Enable or disable domain-based routing for this inbound route. When enabled, the route processes domain-specific logic.", examples=[False])
    inbound_priority: int | None = Field(default=None, description="The priority level for this route when multiple routes could match the same inbound request. Lower numbers indicate higher priority and are evaluated first.", examples=[10])
    forwards: list[UpdateAnInboundRouteBodyForwardsItem] | None = Field(default=None, description="An ordered list of forwarding destinations where matched inbound requests should be routed. The order determines the sequence in which destinations are attempted.")
    match_filter: UpdateAnInboundRouteRequestBodyMatchFilter | None = None
    catch_filter: UpdateAnInboundRouteRequestBodyCatchFilter | None = None
class UpdateAnInboundRouteRequest(StrictModel):
    """Update configuration settings for an inbound route, including its name, domain enablement, priority, and filtering rules. Changes take effect immediately for new incoming requests matching this route."""
    path: UpdateAnInboundRouteRequestPath
    body: UpdateAnInboundRouteRequestBody | None = None

# Operation: delete_inbound_route
class DeleteAnInboundRouteRequestPath(StrictModel):
    inbound_id: str = Field(default=..., description="The unique identifier of the inbound route to delete. This must be a valid inbound route ID that exists in the system.")
class DeleteAnInboundRouteRequest(StrictModel):
    """Permanently delete an inbound route by its ID. This action cannot be undone and will remove all routing rules associated with the specified inbound route."""
    path: DeleteAnInboundRouteRequestPath

# Operation: get_message
class GetInformationForSingleMessageRequestPath(StrictModel):
    message_id: str = Field(default=..., description="The unique identifier of the message to retrieve.")
class GetInformationForSingleMessageRequest(StrictModel):
    """Retrieve detailed information for a specific message by its ID. Returns the complete message data including content, metadata, and timestamps."""
    path: GetInformationForSingleMessageRequestPath

# Operation: get_scheduled_message
class GetSingleScheduledMessageRequestPath(StrictModel):
    message_id: str = Field(default=..., description="The unique identifier of the scheduled message to retrieve.")
class GetSingleScheduledMessageRequest(StrictModel):
    """Retrieve the details of a single scheduled message by its ID, including its content, schedule, and delivery status."""
    path: GetSingleScheduledMessageRequestPath

# Operation: delete_scheduled_message
class DeleteScheduledMessageRequestPath(StrictModel):
    message_id: str = Field(default=..., description="The unique identifier of the scheduled message to delete.")
class DeleteScheduledMessageRequest(StrictModel):
    """Permanently delete a scheduled message by its ID, preventing it from being sent at its scheduled time."""
    path: DeleteScheduledMessageRequestPath

# Operation: add_blocklist_recipients
class AddBlocklistRecipientsRequestBody(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier for the domain to which blocklist recipients will be added.", examples=['{domain_id}'])
    recipients: list[str] = Field(default=..., description="An array of email recipient addresses to add to the blocklist. Each item should be a valid email address string.")
class AddBlocklistRecipientsRequest(StrictModel):
    """Add one or more email recipients to the blocklist suppression list for a specific domain. Blocklisted recipients will not receive emails sent through this domain."""
    body: AddBlocklistRecipientsRequestBody

# Operation: delete_blocklist_recipients
class DeleteBlocklistRecipientsRequestBody(StrictModel):
    all_: bool | None = Field(default=None, validation_alias="all", serialization_alias="all", description="When set to true, removes all recipients from the blocklist. Omit or set to false to delete only specified recipients.", examples=[True])
class DeleteBlocklistRecipientsRequest(StrictModel):
    """Remove recipients from the blocklist suppression list. Use the all parameter to delete all blocklisted recipients at once, or omit it to delete specific recipients via request body."""
    body: DeleteBlocklistRecipientsRequestBody | None = None

# Operation: add_recipients_to_hard_bounces_suppression
class AddHardBouncesRecipientsRequestBody(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain to which the hard bounce suppression list applies.", examples=['{domain_id}'])
    recipients: list[str] = Field(default=..., description="An array of email recipient addresses to add to the hard bounces suppression list. Each item should be a valid email address string.")
class AddHardBouncesRecipientsRequest(StrictModel):
    """Add one or more email recipients to the hard bounces suppression list for a specific domain. Hard-bounced addresses will be suppressed from future email sends to prevent delivery failures."""
    body: AddHardBouncesRecipientsRequestBody

# Operation: delete_hard_bounces_recipients
class DeleteHardBouncesRecipientsRequestBody(StrictModel):
    all_: bool | None = Field(default=None, validation_alias="all", serialization_alias="all", description="When set to true, removes all recipients from the hard bounces suppression list. Omit this parameter to remove specific recipients instead.", examples=[True])
class DeleteHardBouncesRecipientsRequest(StrictModel):
    """Remove recipients from the hard bounces suppression list. Set the all parameter to true to clear all hard bounced addresses, or omit it to remove specific recipients."""
    body: DeleteHardBouncesRecipientsRequestBody | None = None

# Operation: add_spam_complaints_recipients
class AddSpamComplaintsRecipientsRequestBody(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain to which spam complaint suppressions will be applied.", examples=['{domain_id}'])
    recipients: list[str] = Field(default=..., description="A list of email addresses to add to the spam complaints suppression list. Each item should be a valid email address string.")
class AddSpamComplaintsRecipientsRequest(StrictModel):
    """Add one or more email recipients to the spam complaints suppression list for a specific domain. Suppressed recipients will not receive emails sent through this domain."""
    body: AddSpamComplaintsRecipientsRequestBody

# Operation: delete_spam_complaints_recipients
class DeleteSpamComplaintsRecipientsRequestBody(StrictModel):
    all_: bool | None = Field(default=None, validation_alias="all", serialization_alias="all", description="When set to true, removes all recipients from the spam complaints suppression list. Omit or set to false to delete only specified recipients.", examples=[True])
class DeleteSpamComplaintsRecipientsRequest(StrictModel):
    """Remove recipients from the spam complaints suppression list. Use the 'all' parameter to delete all recipients at once, or omit it to delete specific recipients via request body."""
    body: DeleteSpamComplaintsRecipientsRequestBody | None = None

# Operation: add_unsubscribe_recipients
class AddUnsubscribesRecipientsRequestBody(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier for the domain to which the unsubscribe recipients will be added.", examples=['{domain_id}'])
    recipients: list[str] = Field(default=..., description="A list of email recipients to add to the unsubscribes suppression list. Each item should be a valid email address.")
class AddUnsubscribesRecipientsRequest(StrictModel):
    """Add one or more email recipients to the unsubscribes suppression list for a specific domain, preventing them from receiving future messages."""
    body: AddUnsubscribesRecipientsRequestBody

# Operation: delete_unsubscribed_recipients
class DeleteUnsubscribesRecipientsRequestBody(StrictModel):
    all_: bool | None = Field(default=None, validation_alias="all", serialization_alias="all", description="When set to true, removes all recipients from the unsubscribes suppression list. Omit or set to false to perform targeted removals.", examples=[True])
class DeleteUnsubscribesRecipientsRequest(StrictModel):
    """Remove recipients from the unsubscribes suppression list. Set the all parameter to true to clear all unsubscribed recipients at once."""
    body: DeleteUnsubscribesRecipientsRequestBody | None = None

# Operation: get_recipient
class GetSingleRecipientRequestPath(StrictModel):
    recipient_id: str = Field(default=..., description="The unique identifier of the recipient to retrieve.")
class GetSingleRecipientRequest(StrictModel):
    """Retrieve detailed information for a specific recipient by their unique identifier."""
    path: GetSingleRecipientRequestPath

# Operation: delete_recipient
class DeleteARecipientRequestPath(StrictModel):
    recipient_id: str = Field(default=..., description="The unique identifier of the recipient to delete.")
class DeleteARecipientRequest(StrictModel):
    """Permanently delete a recipient from the system. This action cannot be undone."""
    path: DeleteARecipientRequestPath

# Operation: list_webhooks
class GetListOfWebhooksRequestQuery(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain for which to retrieve webhooks.")
class GetListOfWebhooksRequest(StrictModel):
    """Retrieve all webhooks configured for a specific domain. Returns a list of webhook configurations including their endpoints, event subscriptions, and status."""
    query: GetListOfWebhooksRequestQuery

# Operation: get_webhook
class GetAWebhookRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook to retrieve.")
class GetAWebhookRequest(StrictModel):
    """Retrieve the details of a specific webhook by its ID. Returns the webhook configuration including its URL, events, and status."""
    path: GetAWebhookRequestPath

# Operation: delete_webhook
class DeleteAWebhookRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook to delete.")
class DeleteAWebhookRequest(StrictModel):
    """Permanently delete a webhook by its ID. This action cannot be undone and will stop all event notifications to the webhook's configured endpoint."""
    path: DeleteAWebhookRequestPath

# Operation: verify_email
class VerifyAnEmailRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address to verify. Must be a valid email format (e.g., user@domain.com).", json_schema_extra={'format': 'email'}, examples=['info@mailersend.com'])
class VerifyAnEmailRequest(StrictModel):
    """Verify the validity and deliverability of an email address. This operation checks whether the provided email address is properly formatted and active."""
    body: VerifyAnEmailRequestBody

# Operation: create_email_verification_list
class CreateAnEmailVerificationListRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the email verification list (e.g., 'List'). Used to identify and organize verification batches.", examples=['List'])
    emails: list[str] = Field(default=..., description="An array of email addresses to include in the verification list. Each item should be a valid email address string.")
class CreateAnEmailVerificationListRequest(StrictModel):
    """Create a new email verification list with a name and set of email addresses to verify. This list can be used to batch-process email validation across multiple addresses."""
    body: CreateAnEmailVerificationListRequestBody

# Operation: get_email_verification_list
class GetSingleEmailVerificationListRequestPath(StrictModel):
    email_verification_id: str = Field(default=..., description="The unique identifier of the email verification list to retrieve.")
class GetSingleEmailVerificationListRequest(StrictModel):
    """Retrieve a single email verification list by its unique identifier. Use this to fetch details about a specific email verification list for review or further processing."""
    path: GetSingleEmailVerificationListRequestPath

# Operation: verify_email_verification_list
class VerifyAnEmailVerificationListRequestPath(StrictModel):
    email_verification_id: str = Field(default=..., description="The unique identifier of the email verification list to verify. This ID references a specific list that will be processed and validated.")
class VerifyAnEmailVerificationListRequest(StrictModel):
    """Verify an email verification list by its ID. This operation processes and validates the email addresses in the specified verification list."""
    path: VerifyAnEmailVerificationListRequestPath

# Operation: list_email_verification_results
class GetEmailVerificationListResultsRequestPath(StrictModel):
    email_verification_id: str = Field(default=..., description="The unique identifier of the email verification list for which to retrieve results.")
class GetEmailVerificationListResultsRequest(StrictModel):
    """Retrieve the verification results for a completed email verification list. Returns detailed status and outcome information for each email address that was processed."""
    path: GetEmailVerificationListResultsRequestPath

# Operation: update_token_status
class UpdateATokenSettingsRequestPath(StrictModel):
    token_id: str = Field(default=..., description="The unique identifier of the token whose status you want to update.")
class UpdateATokenSettingsRequestBody(StrictModel):
    status: Literal["pause", "active"] = Field(default=..., description="The desired operational status for the token. Set to 'active' to enable the token or 'pause' to temporarily disable it.", examples=['pause'])
class UpdateATokenSettingsRequest(StrictModel):
    """Update the operational status of a token by pausing or activating it. Use this to control whether a token is currently active or temporarily paused."""
    path: UpdateATokenSettingsRequestPath
    body: UpdateATokenSettingsRequestBody

# Operation: delete_token
class DeleteATokenRequestPath(StrictModel):
    token_id: str = Field(default=..., description="The unique identifier of the token to delete.")
class DeleteATokenRequest(StrictModel):
    """Permanently delete a token by its ID. This action cannot be undone and will immediately invalidate the token for all future requests."""
    path: DeleteATokenRequestPath

# Operation: get_user
class GetOneUserRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to retrieve.")
class GetOneUserRequest(StrictModel):
    """Retrieve a single user by their unique identifier. Returns the user's profile information and details."""
    path: GetOneUserRequestPath

# Operation: update_user_role
class UpdateUserRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose role should be updated.")
class UpdateUserRequestBody(StrictModel):
    role: str = Field(default=..., description="The new role to assign to the user. Valid roles include Admin and other predefined role types supported by the system.", examples=['Admin'])
class UpdateUserRequest(StrictModel):
    """Update the role assignment for a specific user. This operation allows you to change a user's access level or permissions by assigning them a new role (e.g., Admin)."""
    path: UpdateUserRequestPath
    body: UpdateUserRequestBody

# Operation: delete_user
class DeleteAUserRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to delete. This must be a valid user ID that exists in the system.")
class DeleteAUserRequest(StrictModel):
    """Permanently delete a user account and all associated data from the system. This action cannot be undone."""
    path: DeleteAUserRequestPath

# Operation: send_sms
class SendAnSmsRequestBody(StrictModel):
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The sender's phone number in E.164 format (e.g., +19191234567). This is the number that will appear as the message source.", examples=['+19191234567'])
    to: list[str] = Field(default=..., description="Array of recipient phone numbers in E.164 format. Each number will receive the message independently.")
    text: str = Field(default=..., description="The message content as a string. Supports template variables (e.g., {{name}}) that will be replaced with values from the personalization array for each recipient.", examples=['Hey {{name}}! This is just a friendly hello :D'])
    personalization: list[SendAnSmsBodyPersonalizationItem] | None = Field(default=None, description="Optional array of personalization objects that map template variables to recipient-specific values. Used to customize message content for each recipient based on template variables in the text parameter.")
class SendAnSmsRequest(StrictModel):
    """Send an SMS message to one or more recipients with optional personalization support. Supports template variables for dynamic content customization."""
    body: SendAnSmsRequestBody

# Operation: get_sms_phone_number
class GetAnSmsPhoneNumberRequestPath(StrictModel):
    sms_number_id: str = Field(default=..., description="The unique identifier of the SMS phone number to retrieve.")
class GetAnSmsPhoneNumberRequest(StrictModel):
    """Retrieve details for a specific SMS phone number by its ID. Returns the phone number configuration and associated metadata."""
    path: GetAnSmsPhoneNumberRequestPath

# Operation: update_sms_phone_number_pause_status
class UpdateSingleSmsPhoneNumberRequestPath(StrictModel):
    sms_number_id: str = Field(default=..., description="The unique identifier of the SMS phone number to update.")
class UpdateSingleSmsPhoneNumberRequestBody(StrictModel):
    paused: bool = Field(default=..., description="Set to true to pause the SMS phone number (disable message sending), or false to resume it.", examples=[True])
class UpdateSingleSmsPhoneNumberRequest(StrictModel):
    """Update the pause status of an SMS phone number. Use this to temporarily disable or re-enable an SMS phone number for sending messages."""
    path: UpdateSingleSmsPhoneNumberRequestPath
    body: UpdateSingleSmsPhoneNumberRequestBody

# Operation: delete_sms_number
class DeleteAnSmsPhoneNumberRequestPath(StrictModel):
    sms_number_id: str = Field(default=..., description="The unique identifier of the SMS phone number to delete.")
class DeleteAnSmsPhoneNumberRequest(StrictModel):
    """Permanently delete an SMS phone number from your account. This action cannot be undone and will remove the number from all associated configurations."""
    path: DeleteAnSmsPhoneNumberRequestPath

# Operation: get_sms_message
class GetAnSmsMessageRequestPath(StrictModel):
    sms_message_id: str = Field(default=..., description="The unique identifier of the SMS message to retrieve.")
class GetAnSmsMessageRequest(StrictModel):
    """Retrieve a specific SMS message by its unique identifier. Returns the full message details including content, sender, recipient, timestamp, and delivery status."""
    path: GetAnSmsMessageRequestPath

# Operation: get_sms_message_activity
class GetActivityOfSingleSmsMessageRequestPath(StrictModel):
    sms_message_id: str = Field(default=..., description="The unique identifier of the SMS message whose activity you want to retrieve.")
class GetActivityOfSingleSmsMessageRequest(StrictModel):
    """Retrieve the activity history and delivery status for a specific SMS message. This includes details about message processing, delivery attempts, and any related events."""
    path: GetActivityOfSingleSmsMessageRequestPath

# Operation: get_sms_recipient
class GetAnSmsRecipientRequestPath(StrictModel):
    sms_recipient_id: str = Field(default=..., description="The unique identifier of the SMS recipient to retrieve.")
class GetAnSmsRecipientRequest(StrictModel):
    """Retrieve detailed information about a specific SMS recipient by their unique identifier."""
    path: GetAnSmsRecipientRequestPath

# Operation: update_sms_recipient_status
class UpdateSingleSmsRecipientRequestPath(StrictModel):
    sms_recipient_id: str = Field(default=..., description="The unique identifier of the SMS recipient whose status you want to update.")
class UpdateSingleSmsRecipientRequestBody(StrictModel):
    status: Literal["opt_out", "active"] = Field(default=..., description="The new subscription status for the recipient. Set to 'active' to enable SMS communications or 'opt_out' to disable them.", examples=['opt_out'])
class UpdateSingleSmsRecipientRequest(StrictModel):
    """Update the subscription status of an SMS recipient. Use this to activate a recipient or mark them as opted out from SMS communications."""
    path: UpdateSingleSmsRecipientRequestPath
    body: UpdateSingleSmsRecipientRequestBody

# Operation: list_sms_webhooks
class GetListOfSmsWebhooksRequestQuery(StrictModel):
    sms_number_id: str = Field(default=..., description="The unique identifier of the SMS phone number for which you want to retrieve configured webhooks.")
class GetListOfSmsWebhooksRequest(StrictModel):
    """Retrieve all SMS webhooks configured for a specific SMS phone number. This allows you to view all webhook endpoints that are currently set up to receive SMS events for the given number."""
    query: GetListOfSmsWebhooksRequestQuery

# Operation: get_sms_webhook
class GetSingleSmsWebhookRequestPath(StrictModel):
    sms_webhook_id: str = Field(default=..., description="The unique identifier of the SMS webhook to retrieve.")
class GetSingleSmsWebhookRequest(StrictModel):
    """Retrieve the configuration and details of a specific SMS webhook by its ID. Use this to inspect webhook settings, URL, event subscriptions, and other metadata."""
    path: GetSingleSmsWebhookRequestPath

# Operation: update_sms_webhook
class UpdateSingleSmsWebhookRequestPath(StrictModel):
    sms_webhook_id: str = Field(default=..., description="The unique identifier of the SMS webhook to update.")
class UpdateSingleSmsWebhookRequestBody(StrictModel):
    enabled: bool = Field(default=..., description="Whether the SMS webhook should be active and receive events. Set to true to enable or false to disable.", examples=[False])
class UpdateSingleSmsWebhookRequest(StrictModel):
    """Update the configuration of an SMS webhook by enabling or disabling it. This allows you to control whether the webhook is active without deleting it."""
    path: UpdateSingleSmsWebhookRequestPath
    body: UpdateSingleSmsWebhookRequestBody

# Operation: delete_sms_webhook
class DeleteAnSmsWebhookRequestPath(StrictModel):
    sms_webhook_id: str = Field(default=..., description="The unique identifier of the SMS webhook to delete.")
class DeleteAnSmsWebhookRequestBody(StrictModel):
    enabled: bool = Field(default=..., description="A boolean flag indicating the desired state. Set to false to proceed with deletion.", examples=[False])
class DeleteAnSmsWebhookRequest(StrictModel):
    """Permanently delete an SMS webhook by its ID. Once deleted, the webhook will no longer receive SMS events."""
    path: DeleteAnSmsWebhookRequestPath
    body: DeleteAnSmsWebhookRequestBody

# Operation: get_sms_inbound_route
class GetSingleSmsInboundRouteRequestPath(StrictModel):
    sms_inbound_id: str = Field(default=..., description="The unique identifier of the SMS inbound route to retrieve.")
class GetSingleSmsInboundRouteRequest(StrictModel):
    """Retrieve the configuration and details of a specific SMS inbound route by its unique identifier."""
    path: GetSingleSmsInboundRouteRequestPath

# Operation: update_sms_inbound_route
class UpdateSmsInboundRouteRequestPath(StrictModel):
    sms_inbound_id: str = Field(default=..., description="The unique identifier of the SMS inbound route to update.")
class UpdateSmsInboundRouteRequestBody(StrictModel):
    sms_number_id: str = Field(default=..., description="The ID of the SMS phone number to associate with this inbound route.", examples=['{sms_number_id}'])
    name: str = Field(default=..., description="A descriptive name for this inbound route (e.g., 'Inbound').", examples=['Inbound'])
    forward_url: str = Field(default=..., description="The webhook URL where incoming SMS messages will be forwarded. Must be a valid URI (e.g., https://yourapp.com/hook).", json_schema_extra={'format': 'uri'}, examples=['https://yourapp.com/hook'])
    enabled: bool = Field(default=..., description="Whether this inbound route is active and should process incoming messages.", examples=[True])
class UpdateSmsInboundRouteRequest(StrictModel):
    """Update an existing inbound SMS route configuration, including the associated phone number, display name, webhook destination, and activation status."""
    path: UpdateSmsInboundRouteRequestPath
    body: UpdateSmsInboundRouteRequestBody

# Operation: delete_sms_inbound_route
class DeleteAnSmsInboundRouteRequestPath(StrictModel):
    sms_inbound_id: str = Field(default=..., description="The unique identifier of the SMS inbound route to delete.")
class DeleteAnSmsInboundRouteRequest(StrictModel):
    """Permanently delete an SMS inbound route by its ID. This action cannot be undone and will stop processing inbound SMS messages for this route."""
    path: DeleteAnSmsInboundRouteRequestPath

# Operation: list_smtp_users
class GetListOfSmtpUsersRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain for which to retrieve SMTP users.")
class GetListOfSmtpUsersRequest(StrictModel):
    """Retrieve all SMTP users configured for a specific domain. Returns a list of SMTP user accounts associated with the domain."""
    path: GetListOfSmtpUsersRequestPath

# Operation: get_smtp_user
class GetSingleSmtpUserRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain that contains the SMTP user.")
    smtp_user_id: str = Field(default=..., description="The unique identifier of the SMTP user to retrieve.")
class GetSingleSmtpUserRequest(StrictModel):
    """Retrieve detailed information about a specific SMTP user within a domain. Use this to fetch configuration, credentials, and status for a single SMTP user account."""
    path: GetSingleSmtpUserRequestPath

# Operation: update_smtp_user
class UpdateSmtpUserRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain containing the SMTP user.")
    smtp_user_id: str = Field(default=..., description="The unique identifier of the SMTP user to be updated.")
class UpdateSmtpUserRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the SMTP user (e.g., 'New Name').", examples=['New Name'])
    enabled: bool = Field(default=..., description="Whether the SMTP user account is active and can be used for authentication.", examples=[False])
class UpdateSmtpUserRequest(StrictModel):
    """Update an SMTP user's configuration within a domain, including their display name and enabled status."""
    path: UpdateSmtpUserRequestPath
    body: UpdateSmtpUserRequestBody

# Operation: delete_smtp_user
class DeleteSmtpUserRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain that contains the SMTP user to be deleted.")
    smtp_user_id: str = Field(default=..., description="The unique identifier of the SMTP user to be deleted from the domain.")
class DeleteSmtpUserRequest(StrictModel):
    """Permanently delete an SMTP user from a domain. This action cannot be undone and will immediately revoke the user's ability to send emails through this domain."""
    path: DeleteSmtpUserRequestPath

# ============================================================================
# Component Models
# ============================================================================

class EmailFrom(PermissiveModel):
    email: str = Field(..., json_schema_extra={'format': 'email'})
    name: str | None = None

class EmailTo(PermissiveModel):
    email: str = Field(..., json_schema_extra={'format': 'email'})
    name: str | None = None

class SendAnSmsBodyPersonalizationItemData(PermissiveModel):
    name: str | None = None

class SendAnSmsBodyPersonalizationItem(PermissiveModel):
    phone_number: str | None = None
    data: SendAnSmsBodyPersonalizationItemData | None = None

class SendEmailRequest(PermissiveModel):
    from_: EmailFrom = Field(..., validation_alias="from", serialization_alias="from")
    to: list[EmailTo]
    subject: str
    text: str
    html: str | None = None

class UpdateAnInboundRouteBodyForwardsItem(PermissiveModel):
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type")
    value: str | None = Field(None, json_schema_extra={'format': 'uri'})

class UpdateSmsInboundRouteRequestFilter(PermissiveModel):
    comparer: str | None = None
    value: str | None = None


# Rebuild models to resolve forward references (required for circular refs)
EmailFrom.model_rebuild()
EmailTo.model_rebuild()
SendAnSmsBodyPersonalizationItem.model_rebuild()
SendAnSmsBodyPersonalizationItemData.model_rebuild()
SendEmailRequest.model_rebuild()
UpdateAnInboundRouteBodyForwardsItem.model_rebuild()
UpdateSmsInboundRouteRequestFilter.model_rebuild()

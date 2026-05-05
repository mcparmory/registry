"""
Resend MCP Server - Pydantic Models

Generated: 2026-05-05 16:08:58 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "DeleteApiKeysRequest",
    "DeleteBroadcastsRequest",
    "DeleteContactPropertiesRequest",
    "DeleteContactsRequest",
    "DeleteContactsSegmentsRequest",
    "DeleteDomainsRequest",
    "DeleteSegmentsRequest",
    "DeleteTemplatesRequest",
    "DeleteTopicsRequest",
    "DeleteWebhooksRequest",
    "GetApiKeysRequest",
    "GetBroadcastsByIdRequest",
    "GetBroadcastsRequest",
    "GetContactPropertiesByIdRequest",
    "GetContactPropertiesRequest",
    "GetContactsByIdRequest",
    "GetContactsRequest",
    "GetContactsSegmentsRequest",
    "GetContactsTopicsRequest",
    "GetDomainsByDomainIdRequest",
    "GetDomainsRequest",
    "GetEmailsByEmailIdAttachmentsByAttachmentIdRequest",
    "GetEmailsByEmailIdAttachmentsRequest",
    "GetEmailsByEmailIdRequest",
    "GetEmailsReceivingByEmailIdAttachmentsByAttachmentIdRequest",
    "GetEmailsReceivingByEmailIdAttachmentsRequest",
    "GetEmailsReceivingByEmailIdRequest",
    "GetEmailsReceivingRequest",
    "GetEmailsRequest",
    "GetLogsByLogIdRequest",
    "GetLogsRequest",
    "GetSegmentsByIdRequest",
    "GetSegmentsRequest",
    "GetTemplatesByIdRequest",
    "GetTemplatesRequest",
    "GetTopicsByIdRequest",
    "GetTopicsRequest",
    "GetWebhooksByWebhookIdRequest",
    "GetWebhooksRequest",
    "PatchBroadcastsRequest",
    "PatchContactPropertiesRequest",
    "PatchContactsRequest",
    "PatchDomainsRequest",
    "PatchTemplatesRequest",
    "PatchTopicsRequest",
    "PatchWebhooksRequest",
    "PostApiKeysRequest",
    "PostBroadcastsRequest",
    "PostBroadcastsSendRequest",
    "PostContactPropertiesRequest",
    "PostContactsRequest",
    "PostContactsSegmentsRequest",
    "PostDomainsRequest",
    "PostDomainsVerifyRequest",
    "PostEmailsBatchRequest",
    "PostEmailsCancelRequest",
    "PostEmailsRequest",
    "PostSegmentsRequest",
    "PostTemplatesDuplicateRequest",
    "PostTemplatesPublishRequest",
    "PostTemplatesRequest",
    "PostTopicsRequest",
    "PostWebhooksRequest",
    "Attachment",
    "PostContactsBodyTopicsItem",
    "PostEmailsBodyTemplate",
    "SendEmailRequest",
    "Tag",
    "TemplateVariableInput",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_emails
class GetEmailsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of emails to return in this request. Must be between 1 and 100 items.", ge=1, le=100)
class GetEmailsRequest(StrictModel):
    """Retrieve a paginated list of emails. Use the limit parameter to control how many emails are returned in a single request."""
    query: GetEmailsRequestQuery | None = None

# Operation: send_email
class PostEmailsRequestBody(StrictModel):
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="Sender email address. Include a friendly name using the format 'Your Name <sender@domain.com>' to display a custom sender name.")
    to: str | list[str] = Field(default=..., description="Recipient email address or array of addresses. Supports up to 50 recipients; provide as a single string for one recipient or an array of strings for multiple.")
    subject: str = Field(default=..., description="Email subject line.")
    bcc: str | list[str] | None = Field(default=None, description="Blind carbon copy recipient email address or array of addresses. Provide as a single string or array of strings for multiple recipients.")
    cc: str | list[str] | None = Field(default=None, description="Carbon copy recipient email address or array of addresses. Provide as a single string or array of strings for multiple recipients.")
    reply_to: str | list[str] | None = Field(default=None, description="Reply-to email address or array of addresses. Provide as a single string or array of strings for multiple addresses. Overrides the sender address for reply routing.")
    template: PostEmailsBodyTemplate | None = Field(default=None, description="Email template identifier to use for rendering the email body. If specified, the template content is used instead of a raw body parameter.")
    headers: dict[str, Any] | None = Field(default=None, description="Custom HTTP headers to include in the email message. Provide as key-value pairs.")
    scheduled_at: str | None = Field(default=None, description="Schedule the email to be sent at a future date and time. Specify the date in ISO 8601 format (e.g., 2024-12-25T10:30:00Z). If omitted, the email is sent immediately.")
    attachments: list[Attachment] | None = Field(default=None, description="Array of file attachments to include with the email. Each attachment should specify the file content and metadata.")
    tags: list[Tag] | None = Field(default=None, description="Array of tags to categorize or label the email for tracking and organization purposes.")
    topic_id: str | None = Field(default=None, description="Topic ID to enforce subscription-based delivery rules. If the recipient is a contact, the email is sent only if they're opted-in to the topic; if opted-out, it's blocked. For non-contacts, delivery follows the topic's default subscription setting (opt-in or opt-out).")
    html: str | None = Field(default=None, description="The HTML version of the message.")
    text: str | None = Field(default=None, description="The plain text version of the message.")
class PostEmailsRequest(StrictModel):
    """Send an email to one or more recipients with optional scheduling, attachments, and custom headers. Supports templating and topic-based subscription management for opt-in/opt-out compliance."""
    body: PostEmailsRequestBody

# Operation: get_email
class GetEmailsByEmailIdRequestPath(StrictModel):
    email_id: str = Field(default=..., description="The unique identifier of the email to retrieve.")
class GetEmailsByEmailIdRequest(StrictModel):
    """Retrieve a single email message by its unique identifier. Returns the complete email record including headers, body, and metadata."""
    path: GetEmailsByEmailIdRequestPath

# Operation: cancel_email
class PostEmailsCancelRequestPath(StrictModel):
    email_id: str = Field(default=..., description="The unique identifier of the email to cancel.")
class PostEmailsCancelRequest(StrictModel):
    """Cancel the scheduled delivery of an email. This prevents a scheduled email from being sent."""
    path: PostEmailsCancelRequestPath

# Operation: send_emails_batch
class PostEmailsBatchRequestBody(StrictModel):
    body: list[SendEmailRequest] | None = Field(default=None, description="Array of email objects to send, with a maximum of 100 items per request. Each item in the array represents a single email configuration with its own recipient, subject, and content details.")
class PostEmailsBatchRequest(StrictModel):
    """Send up to 100 emails in a single batch request. This operation allows efficient bulk email delivery by processing multiple email configurations simultaneously."""
    body: PostEmailsBatchRequestBody | None = None

# Operation: list_attachments_for_email
class GetEmailsByEmailIdAttachmentsRequestPath(StrictModel):
    email_id: str = Field(default=..., description="The unique identifier of the email, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetEmailsByEmailIdAttachmentsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of attachments to return in the response. Useful for pagination or limiting results.")
class GetEmailsByEmailIdAttachmentsRequest(StrictModel):
    """Retrieve all attachments associated with a specific sent email. Use this to access files that were included when the email was sent."""
    path: GetEmailsByEmailIdAttachmentsRequestPath
    query: GetEmailsByEmailIdAttachmentsRequestQuery | None = None

# Operation: get_email_attachment
class GetEmailsByEmailIdAttachmentsByAttachmentIdRequestPath(StrictModel):
    email_id: str = Field(default=..., description="The unique identifier of the email containing the attachment. Must be a valid UUID.", json_schema_extra={'format': 'uuid'})
    attachment_id: str = Field(default=..., description="The unique identifier of the attachment to retrieve. Must be a valid UUID.", json_schema_extra={'format': 'uuid'})
class GetEmailsByEmailIdAttachmentsByAttachmentIdRequest(StrictModel):
    """Retrieve a specific attachment from a sent email by providing both the email ID and attachment ID."""
    path: GetEmailsByEmailIdAttachmentsByAttachmentIdRequestPath

# Operation: list_emails_receiving
class GetEmailsReceivingRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of received emails to return in a single response. Limits the size of the result set to improve performance and reduce payload size.")
class GetEmailsReceivingRequest(StrictModel):
    """Retrieve a list of received emails from your inbox. Use the limit parameter to control how many emails are returned in the response."""
    query: GetEmailsReceivingRequestQuery | None = None

# Operation: get_received_email
class GetEmailsReceivingByEmailIdRequestPath(StrictModel):
    email_id: str = Field(default=..., description="The unique identifier of the received email, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetEmailsReceivingByEmailIdRequest(StrictModel):
    """Retrieve a single received email by its unique identifier. Use this to fetch the full details of a specific email in your inbox."""
    path: GetEmailsReceivingByEmailIdRequestPath

# Operation: list_email_attachments
class GetEmailsReceivingByEmailIdAttachmentsRequestPath(StrictModel):
    email_id: str = Field(default=..., description="The unique identifier of the received email, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetEmailsReceivingByEmailIdAttachmentsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of attachments to return in the response. Useful for pagination or limiting results when dealing with emails containing many files.")
class GetEmailsReceivingByEmailIdAttachmentsRequest(StrictModel):
    """Retrieve all attachments associated with a received email. Use this to access files that were included with an incoming message."""
    path: GetEmailsReceivingByEmailIdAttachmentsRequestPath
    query: GetEmailsReceivingByEmailIdAttachmentsRequestQuery | None = None

# Operation: get_received_email_attachment
class GetEmailsReceivingByEmailIdAttachmentsByAttachmentIdRequestPath(StrictModel):
    email_id: str = Field(default=..., description="The unique identifier (UUID) of the received email containing the attachment.", json_schema_extra={'format': 'uuid'})
    attachment_id: str = Field(default=..., description="The unique identifier (UUID) of the attachment to retrieve.", json_schema_extra={'format': 'uuid'})
class GetEmailsReceivingByEmailIdAttachmentsByAttachmentIdRequest(StrictModel):
    """Retrieve a specific attachment from a received email by providing both the email ID and attachment ID. Returns the attachment file and metadata."""
    path: GetEmailsReceivingByEmailIdAttachmentsByAttachmentIdRequestPath

# Operation: list_domains
class GetDomainsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of domains to return in this request. Must be between 1 and 100 items.", ge=1, le=100)
class GetDomainsRequest(StrictModel):
    """Retrieve a paginated list of domains. Use the limit parameter to control the number of results returned in a single request."""
    query: GetDomainsRequestQuery | None = None

# Operation: create_domain
class PostDomainsRequestBody(StrictModel):
    name: str = Field(default=..., description="The domain name to create (e.g., mail.example.com). This will be used as your sending domain.")
    region: Literal["us-east-1", "eu-west-1", "sa-east-1", "ap-northeast-1"] | None = Field(default=None, description="The AWS region where emails will be sent from. Defaults to us-east-1 if not specified. Choose from: us-east-1 (N. Virginia), eu-west-1 (Ireland), sa-east-1 (São Paulo), or ap-northeast-1 (Tokyo).")
    custom_return_path: str | None = Field(default=None, description="A custom subdomain for the Return-Path address used in bounce handling. Defaults to 'send' (resulting in send.yourdomain.tld). Use this for advanced routing scenarios.")
    open_tracking: bool | None = Field(default=None, description="Enable open rate tracking by injecting a tracking pixel into each email. Disabled by default.")
    click_tracking: bool | None = Field(default=None, description="Enable click tracking to monitor links clicked within HTML email bodies. Disabled by default.")
    tls: Literal["opportunistic", "enforced"] | None = Field(default=None, description="TLS encryption mode for outbound emails. 'Opportunistic' attempts a secure connection but falls back to unencrypted if unavailable. 'Enforced' requires TLS or the email will not be sent. Defaults to opportunistic.")
class PostDomainsRequest(StrictModel):
    """Create a new domain for sending emails. Configure the domain with optional settings for region, tracking, TLS security, and custom return path."""
    body: PostDomainsRequestBody

# Operation: get_domain
class GetDomainsByDomainIdRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain to retrieve.")
class GetDomainsByDomainIdRequest(StrictModel):
    """Retrieve detailed information about a specific domain by its unique identifier."""
    path: GetDomainsByDomainIdRequestPath

# Operation: update_domain
class PatchDomainsRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain to update.")
class PatchDomainsRequestBody(StrictModel):
    open_tracking: bool | None = Field(default=None, description="Enable or disable tracking of email open rates. When enabled, the system monitors whether recipients open emails sent from this domain.")
    click_tracking: bool | None = Field(default=None, description="Enable or disable tracking of link clicks within HTML email bodies. When enabled, the system monitors which links recipients click in emails from this domain.")
    tls: str | None = Field(default=None, description="Set the TLS security mode for outgoing emails: use 'enforced' to require TLS encryption for all connections, or 'opportunistic' to use TLS when available but allow unencrypted fallback. Defaults to 'opportunistic'.")
class PatchDomainsRequest(StrictModel):
    """Update email tracking and TLS security settings for an existing domain. Modify open rate tracking, click tracking, and TLS enforcement preferences."""
    path: PatchDomainsRequestPath
    body: PatchDomainsRequestBody | None = None

# Operation: delete_domain
class DeleteDomainsRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain to be deleted.")
class DeleteDomainsRequest(StrictModel):
    """Permanently remove a domain from the system. This action cannot be undone."""
    path: DeleteDomainsRequestPath

# Operation: verify_domain
class PostDomainsVerifyRequestPath(StrictModel):
    domain_id: str = Field(default=..., description="The unique identifier of the domain to verify.")
class PostDomainsVerifyRequest(StrictModel):
    """Verify ownership or configuration of an existing domain by triggering validation checks against the specified domain."""
    path: PostDomainsVerifyRequestPath

# Operation: list_api_keys
class GetApiKeysRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of API keys to return in the response. Must be between 1 and 100 items.", ge=1, le=100)
class GetApiKeysRequest(StrictModel):
    """Retrieve a paginated list of API keys for the authenticated user or organization. Use the limit parameter to control the number of results returned."""
    query: GetApiKeysRequestQuery | None = None

# Operation: create_api_key
class PostApiKeysRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the API key to help identify its purpose and usage.")
    permission: Literal["full_access", "sending_access"] | None = Field(default=None, description="The access level for the API key: full_access grants permissions to create, delete, get, and update any resource, while sending_access restricts the key to only sending emails.")
    domain_id: str | None = Field(default=None, description="When using sending_access permission, optionally restrict the API key to send emails only from a specific domain by providing its domain ID.")
class PostApiKeysRequest(StrictModel):
    """Create a new API key for authenticating requests to the Resend API. The key can be configured with either full access to all resources or restricted to sending emails only."""
    body: PostApiKeysRequestBody

# Operation: delete_api_key
class DeleteApiKeysRequestPath(StrictModel):
    api_key_id: str = Field(default=..., description="The unique identifier of the API key to delete.")
class DeleteApiKeysRequest(StrictModel):
    """Permanently remove an API key by its ID. Once deleted, the key can no longer be used for authentication and cannot be recovered."""
    path: DeleteApiKeysRequestPath

# Operation: list_templates
class GetTemplatesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of templates to return in the response. Must be between 1 and 100 items.", ge=1, le=100)
class GetTemplatesRequest(StrictModel):
    """Retrieve a paginated list of available templates. Use the limit parameter to control the number of results returned."""
    query: GetTemplatesRequestQuery | None = None

# Operation: create_template
class PostTemplatesRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for this template. Used to identify and reference the template when sending emails.")
    alias: str | None = Field(default=None, description="An alternative identifier for the template. Useful for programmatic references or shorter naming conventions.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="The sender's email address, optionally formatted with a friendly name using the format 'Display Name <email@domain.com>'.")
    subject: str | None = Field(default=None, description="The subject line for emails sent using this template. Supports variable substitution if variables are defined.")
    reply_to: list[str] | None = Field(default=None, description="One or more email addresses where recipients can reply. Specify as an array of email addresses.")
    html: str = Field(default=..., description="The HTML content of the template. This is the main body rendered in email clients that support HTML. Supports variable substitution using defined variables.")
    variables: list[TemplateVariableInput] | None = Field(default=None, description="Template variables that can be dynamically substituted in the subject, HTML content, and sender field. Specify as an array of variable definitions.")
class PostTemplatesRequest(StrictModel):
    """Create a new email template with HTML content and optional configuration for sender, subject, and reply-to addresses. Templates can be referenced by name or alias for sending emails."""
    body: PostTemplatesRequestBody

# Operation: get_template
class GetTemplatesByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier or alias of the template to retrieve. Can be either the template's ID or a human-readable alias if supported by the API.")
class GetTemplatesByIdRequest(StrictModel):
    """Retrieve a single template by its ID or alias. Use this operation to fetch the full details of a specific template for viewing or further processing."""
    path: GetTemplatesByIdRequestPath

# Operation: update_template
class PatchTemplatesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier or alias of the template to update.")
class PatchTemplatesRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the template.")
    alias: str | None = Field(default=None, description="A unique alias or slug for referencing the template programmatically.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="The sender's email address; optionally include a friendly name using the format 'Display Name <email@domain.com>'.")
    subject: str | None = Field(default=None, description="The subject line for emails sent using this template.")
    reply_to: list[str] | None = Field(default=None, description="One or more email addresses to set as reply-to destinations for responses to emails sent with this template.")
    variables: list[TemplateVariableInput] | None = Field(default=None, description="Template variables that can be dynamically substituted when sending emails; specify as an array of variable definitions.")
class PatchTemplatesRequest(StrictModel):
    """Update an existing email template by modifying its name, alias, sender information, subject, reply-to addresses, or variables."""
    path: PatchTemplatesRequestPath
    body: PatchTemplatesRequestBody | None = None

# Operation: delete_template
class DeleteTemplatesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier or alias of the template to delete. Can be either the template's ID or a configured alias.")
class DeleteTemplatesRequest(StrictModel):
    """Permanently remove a template by its ID or alias. This action cannot be undone."""
    path: DeleteTemplatesRequestPath

# Operation: publish_template
class PostTemplatesPublishRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier or alias of the template to publish. Can be either the template's ID or a configured alias.")
class PostTemplatesPublishRequest(StrictModel):
    """Publish a template to make it available for use. Once published, the template can be accessed and utilized by users or systems."""
    path: PostTemplatesPublishRequestPath

# Operation: duplicate_template
class PostTemplatesDuplicateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier or alias of the template to duplicate. Can be either the template's ID or a configured alias.")
class PostTemplatesDuplicateRequest(StrictModel):
    """Creates a copy of an existing template, allowing you to reuse template configurations with a new instance."""
    path: PostTemplatesDuplicateRequestPath

# Operation: list_contacts
class GetContactsRequestQuery(StrictModel):
    segment_id: str | None = Field(default=None, description="Filter the returned contacts to only those belonging to a specific segment. Omit to retrieve contacts from all segments.")
    limit: int | None = Field(default=None, description="Maximum number of contacts to return in the response. Must be between 1 and 100 items.", ge=1, le=100)
class GetContactsRequest(StrictModel):
    """Retrieve a list of contacts, optionally filtered by segment and limited to a specific number of results."""
    query: GetContactsRequestQuery | None = None

# Operation: create_contact
class PostContactsRequestBody(StrictModel):
    email: str = Field(default=..., description="Email address uniquely identifying the contact (e.g., steve.wozniak@gmail.com). Required to create the contact.")
    first_name: str | None = Field(default=None, description="First name of the contact for personalization and identification purposes.")
    last_name: str | None = Field(default=None, description="Last name of the contact for personalization and identification purposes.")
    unsubscribed: bool | None = Field(default=None, description="Global subscription status for the contact. When set to true, the contact is unsubscribed from all broadcasts and communications.")
    properties: dict[str, Any] | None = Field(default=None, description="Custom key-value pairs to store additional contact attributes beyond standard fields. Values can be strings, numbers, or other JSON-compatible types.")
    segments: list[str] | None = Field(default=None, description="List of segment IDs to automatically add this contact to upon creation. Segments organize contacts into groups for targeted campaigns.")
    topics: list[PostContactsBodyTopicsItem] | None = Field(default=None, description="List of topic IDs representing the contact's subscription preferences. Topics control which types of communications the contact receives.")
class PostContactsRequest(StrictModel):
    """Create a new contact in the system with email as the required identifier. Optionally include personal details, custom properties, segment assignments, and topic subscriptions."""
    body: PostContactsRequestBody

# Operation: get_contact
class GetContactsByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the contact or the contact's email address. Either format is accepted to retrieve the contact record.")
class GetContactsByIdRequest(StrictModel):
    """Retrieve a single contact by its unique identifier or email address. Use this operation to fetch detailed information about a specific contact."""
    path: GetContactsByIdRequestPath

# Operation: update_contact
class PatchContactsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the contact, either as a Contact ID or email address.")
class PatchContactsRequestBody(StrictModel):
    email: str | None = Field(default=None, description="The contact's email address in standard email format (e.g., user@example.com).")
    first_name: str | None = Field(default=None, description="The contact's first name.")
    last_name: str | None = Field(default=None, description="The contact's last name.")
    unsubscribed: bool | None = Field(default=None, description="Global subscription status for the contact. Set to true to unsubscribe the contact from all Broadcasts; false to maintain or restore subscription.")
    properties: dict[str, Any] | None = Field(default=None, description="A map of custom property keys and their values to update or add to the contact's profile.")
class PatchContactsRequest(StrictModel):
    """Update contact details by ID or email address. Modify any combination of email, name, subscription status, or custom properties for an existing contact."""
    path: PatchContactsRequestPath
    body: PatchContactsRequestBody | None = None

# Operation: delete_contact
class DeleteContactsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier for the contact, provided as either the contact ID or the email address associated with the contact.")
class DeleteContactsRequest(StrictModel):
    """Permanently remove a contact from the system by specifying either its unique ID or email address."""
    path: DeleteContactsRequestPath

# Operation: list_broadcasts
class GetBroadcastsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of broadcasts to return in the response. Must be between 1 and 100 items.", ge=1, le=100)
class GetBroadcastsRequest(StrictModel):
    """Retrieve a paginated list of broadcasts. Use the limit parameter to control how many broadcasts are returned in a single request."""
    query: GetBroadcastsRequestQuery | None = None

# Operation: create_broadcast
class PostBroadcastsRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable name to identify this broadcast for internal reference.")
    segment_id: str = Field(default=..., description="The unique identifier of the audience segment that will receive this broadcast. This parameter determines who the email will be sent to.")
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The email address that will appear as the sender of this broadcast.")
    subject: str = Field(default=..., description="The subject line displayed to recipients when they receive the email.")
    reply_to: list[str] | None = Field(default=None, description="One or more email addresses where recipient replies should be directed. Provide as an array of email addresses.")
    preview_text: str | None = Field(default=None, description="A short preview or snippet of the email content that appears in email clients before the full message is opened.")
    topic_id: str | None = Field(default=None, description="The unique identifier of a topic to scope this broadcast to, allowing you to organize broadcasts by topic.")
    send: bool | None = Field(default=None, description="Set to true to send the broadcast immediately, or false to save it as a draft. If true, you can optionally use scheduled_at to send at a future time.")
    scheduled_at: str | None = Field(default=None, description="The date and time when the broadcast should be sent, specified in ISO 8601 format. This can only be used when send is set to true.")
    html: str | None = Field(default=None, description="The HTML version of the message.")
    text: str | None = Field(default=None, description="The plain text version of the message.")
class PostBroadcastsRequest(StrictModel):
    """Create an email broadcast to be sent to a specific audience segment. The broadcast can be sent immediately or scheduled for a future time, or saved as a draft for later editing."""
    body: PostBroadcastsRequestBody

# Operation: get_broadcast
class GetBroadcastsByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the broadcast to retrieve.")
class GetBroadcastsByIdRequest(StrictModel):
    """Retrieve detailed information about a specific broadcast by its unique identifier."""
    path: GetBroadcastsByIdRequestPath

# Operation: update_broadcast
class PatchBroadcastsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the broadcast to update.")
class PatchBroadcastsRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the broadcast.")
    segment_id: str | None = Field(default=None, description="The unique identifier of the audience segment that will receive this broadcast.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="The email address that will appear as the sender of the broadcast.")
    subject: str | None = Field(default=None, description="The subject line displayed in recipients' email clients.")
    reply_to: list[str] | None = Field(default=None, description="One or more email addresses where replies to this broadcast should be directed. Specify as an array of email addresses.")
    preview_text: str | None = Field(default=None, description="The preview text shown in email clients before the recipient opens the message.")
    topic_id: str | None = Field(default=None, description="The unique identifier of the topic this broadcast is associated with for organizational and filtering purposes.")
class PatchBroadcastsRequest(StrictModel):
    """Update an existing broadcast's configuration including name, recipient segment, sender details, subject line, and topic association."""
    path: PatchBroadcastsRequestPath
    body: PatchBroadcastsRequestBody | None = None

# Operation: delete_broadcast
class DeleteBroadcastsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the broadcast to delete. Must reference a broadcast in draft status.")
class DeleteBroadcastsRequest(StrictModel):
    """Permanently remove a broadcast that is currently in draft status. Only draft broadcasts can be deleted; published or scheduled broadcasts cannot be removed through this operation."""
    path: DeleteBroadcastsRequestPath

# Operation: send_broadcast
class PostBroadcastsSendRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the broadcast to send or schedule.")
class PostBroadcastsSendRequestBody(StrictModel):
    scheduled_at: str | None = Field(default=None, description="Optional ISO 8601 formatted date and time to schedule the broadcast for future delivery. If omitted, the broadcast will be sent immediately.")
class PostBroadcastsSendRequest(StrictModel):
    """Send a broadcast immediately or schedule it to be sent at a specified future time. Use the scheduled_at parameter to defer delivery, or omit it to send right away."""
    path: PostBroadcastsSendRequestPath
    body: PostBroadcastsSendRequestBody | None = None

# Operation: list_webhooks
class GetWebhooksRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of webhooks to return in the response. Useful for pagination and controlling response size.")
class GetWebhooksRequest(StrictModel):
    """Retrieve a paginated list of webhooks configured for this API. Use the limit parameter to control the maximum number of results returned."""
    query: GetWebhooksRequestQuery | None = None

# Operation: create_webhook
class PostWebhooksRequestBody(StrictModel):
    endpoint: str = Field(default=..., description="The HTTPS URL endpoint where webhook event notifications will be delivered. Must be a valid, publicly accessible URL that can receive POST requests.")
    events: list[str] = Field(default=..., description="A list of one or more event types to subscribe to. Each event type is a string identifier (e.g., 'email.sent', 'email.delivered'). At least one event type is required. Order does not matter.", min_length=1)
class PostWebhooksRequest(StrictModel):
    """Create a new webhook subscription to receive HTTP POST notifications for specified email events. The webhook will be triggered whenever any of the subscribed events occur."""
    body: PostWebhooksRequestBody

# Operation: get_webhook
class GetWebhooksByWebhookIdRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetWebhooksByWebhookIdRequest(StrictModel):
    """Retrieve the details of a specific webhook by its unique identifier. Use this to inspect webhook configuration, status, and settings."""
    path: GetWebhooksByWebhookIdRequestPath

# Operation: update_webhook
class PatchWebhooksRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class PatchWebhooksRequestBody(StrictModel):
    endpoint: str | None = Field(default=None, description="The HTTPS URL where webhook events will be delivered. This endpoint must be publicly accessible and capable of receiving POST requests.")
    events: list[str] | None = Field(default=None, description="A list of event types this webhook should subscribe to. At least one event type is required. Events are specified as dot-separated strings (e.g., 'email.sent', 'email.delivered').", min_length=1)
    status: Literal["enabled", "disabled"] | None = Field(default=None, description="The operational state of the webhook. Set to 'enabled' to activate event delivery or 'disabled' to pause it without removing the configuration.")
class PatchWebhooksRequest(StrictModel):
    """Update the configuration of an existing webhook, including its endpoint URL, subscribed event types, and operational status."""
    path: PatchWebhooksRequestPath
    body: PatchWebhooksRequestBody | None = None

# Operation: delete_webhook
class DeleteWebhooksRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook to delete, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class DeleteWebhooksRequest(StrictModel):
    """Permanently remove a webhook by its unique identifier. This action cannot be undone."""
    path: DeleteWebhooksRequestPath

# Operation: list_segments
class GetSegmentsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of segments to return per request. Must be between 1 and 100 items.", ge=1, le=100)
class GetSegmentsRequest(StrictModel):
    """Retrieve a paginated list of segments. Use the limit parameter to control the number of results returned in a single request."""
    query: GetSegmentsRequestQuery | None = None

# Operation: create_segment
class PostSegmentsRequestBody(StrictModel):
    name: str = Field(default=..., description="The display name for the segment. Used to identify and reference the segment in the system.")
    filter_: dict[str, Any] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Optional filter conditions that define which records belong to this segment. Specify filter criteria as a structured object to narrow the segment's scope.")
class PostSegmentsRequest(StrictModel):
    """Create a new segment with a name and optional filter conditions to organize and target specific data subsets."""
    body: PostSegmentsRequestBody

# Operation: get_segment
class GetSegmentsByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the segment to retrieve.")
class GetSegmentsByIdRequest(StrictModel):
    """Retrieve a single segment by its unique identifier. Returns the complete segment details including configuration and metadata."""
    path: GetSegmentsByIdRequestPath

# Operation: delete_segment
class DeleteSegmentsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the segment to delete.")
class DeleteSegmentsRequest(StrictModel):
    """Permanently remove a segment by its ID. This action cannot be undone."""
    path: DeleteSegmentsRequestPath

# Operation: list_topics
class GetTopicsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of topics to return in the response. Must be between 1 and 100 items.", ge=1, le=100)
class GetTopicsRequest(StrictModel):
    """Retrieve a paginated list of available topics. Use the limit parameter to control the number of results returned."""
    query: GetTopicsRequestQuery | None = None

# Operation: create_topic
class PostTopicsRequestBody(StrictModel):
    name: str = Field(default=..., description="The topic name, up to 50 characters. Used to identify the topic in subscription management interfaces.", max_length=50)
    default_subscription: Literal["opt_in", "opt_out"] = Field(default=..., description="The default subscription behavior for new contacts: 'opt_in' requires explicit subscription, 'opt_out' subscribes by default. This setting is permanent and cannot be changed after topic creation.")
    description: str | None = Field(default=None, description="Optional description of the topic's purpose, up to 200 characters. Helps contacts understand what the topic covers.", max_length=200)
    visibility: Literal["public", "private"] | None = Field(default=None, description="Controls topic visibility: 'public' topics appear on the unsubscribe page for all contacts, 'private' topics only appear for already opted-in contacts. Defaults to 'private'.")
class PostTopicsRequest(StrictModel):
    """Create a new topic for managing contact subscriptions. Topics define subscription preferences that cannot be modified after creation."""
    body: PostTopicsRequestBody

# Operation: get_topic
class GetTopicsByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the topic to retrieve.")
class GetTopicsByIdRequest(StrictModel):
    """Retrieve a single topic by its unique identifier. Returns the complete topic details including metadata and content."""
    path: GetTopicsByIdRequestPath

# Operation: update_topic
class PatchTopicsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the topic to update.")
class PatchTopicsRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the topic. Must not exceed 50 characters.", max_length=50)
    description: str | None = Field(default=None, description="A detailed description of the topic's purpose or content. Must not exceed 200 characters.", max_length=200)
    visibility: Literal["public", "private"] | None = Field(default=None, description="Controls who can access this topic. Choose either 'public' for unrestricted access or 'private' for restricted access.")
class PatchTopicsRequest(StrictModel):
    """Update an existing topic's metadata including its name, description, and visibility settings. Provide the topic ID and specify which fields to modify."""
    path: PatchTopicsRequestPath
    body: PatchTopicsRequestBody | None = None

# Operation: delete_topic
class DeleteTopicsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the topic to delete.")
class DeleteTopicsRequest(StrictModel):
    """Permanently remove a topic by its ID. This action cannot be undone."""
    path: DeleteTopicsRequestPath

# Operation: list_contact_properties
class GetContactPropertiesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of contact properties to return per request. Must be between 1 and 100 items.", ge=1, le=100)
class GetContactPropertiesRequest(StrictModel):
    """Retrieve a paginated list of available contact properties. Use the limit parameter to control the number of properties returned in a single request."""
    query: GetContactPropertiesRequestQuery | None = None

# Operation: create_contact_property
class PostContactPropertiesRequestBody(StrictModel):
    key: str = Field(default=..., description="A unique identifier for the property using only alphanumeric characters and underscores, up to 50 characters in length.")
    type_: Literal["string", "number"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type for this property, either string or number, which determines the format of values stored and the type required for the fallback value.")
    fallback_value: str | None = Field(default=None, description="An optional default value returned when the property is not set on a contact. The value must match the specified property type (string or number).")
class PostContactPropertiesRequest(StrictModel):
    """Create a new custom property for contacts. This property can be used to store additional data on contact records, with an optional default value applied when the property is not explicitly set."""
    body: PostContactPropertiesRequestBody

# Operation: get_contact_property
class GetContactPropertiesByIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the contact property to retrieve.")
class GetContactPropertiesByIdRequest(StrictModel):
    """Retrieve a single contact property by its unique identifier. Use this to fetch detailed information about a specific contact property."""
    path: GetContactPropertiesByIdRequestPath

# Operation: update_contact_property
class PatchContactPropertiesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the contact property to update.")
class PatchContactPropertiesRequestBody(StrictModel):
    fallback_value: str | None = Field(default=None, description="The default value to use when this property is not set for a contact. Must be compatible with the property's data type (string or number).")
class PatchContactPropertiesRequest(StrictModel):
    """Update the fallback value for an existing contact property. The fallback value is used as the default when the property is not set for a specific contact."""
    path: PatchContactPropertiesRequestPath
    body: PatchContactPropertiesRequestBody | None = None

# Operation: delete_contact_property
class DeleteContactPropertiesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the contact property to delete.")
class DeleteContactPropertiesRequest(StrictModel):
    """Permanently remove a contact property from the system by its ID. This action cannot be undone."""
    path: DeleteContactPropertiesRequestPath

# Operation: list_contact_segments
class GetContactsSegmentsRequestPath(StrictModel):
    contact_id: str = Field(default=..., description="The unique identifier for the contact. Accepts either the contact's ID or email address.")
class GetContactsSegmentsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of segments to return in the response. Must be between 1 and 100 items.", ge=1, le=100)
class GetContactsSegmentsRequest(StrictModel):
    """Retrieve all segments that a contact belongs to. Use the contact's ID or email address to fetch their segment memberships."""
    path: GetContactsSegmentsRequestPath
    query: GetContactsSegmentsRequestQuery | None = None

# Operation: add_contact_to_segment
class PostContactsSegmentsRequestPath(StrictModel):
    contact_id: str = Field(default=..., description="The unique identifier or email address of the contact to add to the segment.")
    segment_id: str = Field(default=..., description="The unique identifier of the segment to which the contact will be added.")
class PostContactsSegmentsRequest(StrictModel):
    """Add a contact to a segment, enabling you to organize and group contacts for targeted campaigns or management purposes."""
    path: PostContactsSegmentsRequestPath

# Operation: remove_contact_from_segment
class DeleteContactsSegmentsRequestPath(StrictModel):
    contact_id: str = Field(default=..., description="The unique identifier for the contact, provided as either the Contact ID or the contact's email address.")
    segment_id: str = Field(default=..., description="The unique identifier for the segment from which the contact should be removed.")
class DeleteContactsSegmentsRequest(StrictModel):
    """Remove a contact from a segment, effectively unsubscribing or disassociating them from that segment's audience."""
    path: DeleteContactsSegmentsRequestPath

# Operation: list_contact_topics
class GetContactsTopicsRequestPath(StrictModel):
    contact_id: str = Field(default=..., description="The unique identifier for the contact, which can be either the contact ID or the contact's email address.")
class GetContactsTopicsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of topics to return in the response. Must be between 1 and 100 items.", ge=1, le=100)
class GetContactsTopicsRequest(StrictModel):
    """Retrieve a list of topics associated with a specific contact. Use the contact ID or email address to fetch their related topics with optional pagination."""
    path: GetContactsTopicsRequestPath
    query: GetContactsTopicsRequestQuery | None = None

# Operation: list_logs
class GetLogsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of log entries to return in the response. Must be between 1 and 100 items.", ge=1, le=100)
class GetLogsRequest(StrictModel):
    """Retrieve a paginated list of logs from the system. Use the limit parameter to control how many log entries are returned in a single request."""
    query: GetLogsRequestQuery | None = None

# Operation: get_log
class GetLogsByLogIdRequestPath(StrictModel):
    log_id: str = Field(default=..., description="The unique identifier of the log to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class GetLogsByLogIdRequest(StrictModel):
    """Retrieve a single log entry by its unique identifier. Returns the complete log record matching the provided ID."""
    path: GetLogsByLogIdRequestPath

# ============================================================================
# Component Models
# ============================================================================

class Attachment(PermissiveModel):
    content: str | None = Field(None, description="Content of an attached file.", json_schema_extra={'format': 'binary'})
    filename: str | None = Field(None, description="Name of attached file.")
    path: str | None = Field(None, description="Path where the attachment file is hosted")
    content_type: str | None = Field(None, description="Optional content type for the attachment, if not set it will be derived from the filename property")
    content_id: str | None = Field(None, description="Content ID for embedding inline images using cid references (e.g., cid:image001).")

class Email(PermissiveModel):
    object_: str | None = Field(None, validation_alias="object", serialization_alias="object", description="The type of object.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the email.")
    to: list[str] | None = None
    from_: str | None = Field(None, validation_alias="from", serialization_alias="from", description="The email address of the sender.")
    created_at: str | None = Field(None, description="The date and time the email was created.", json_schema_extra={'format': 'date-time'})
    subject: str | None = Field(None, description="The subject line of the email.")
    html: str | None = Field(None, description="The HTML body of the email.")
    text: str | None = Field(None, description="The plain text body of the email.")
    bcc: list[str] | None = Field(None, description="The email addresses of the blind carbon copy recipients.")
    cc: list[str] | None = Field(None, description="The email addresses of the carbon copy recipients.")
    reply_to: list[str] | None = Field(None, description="The email addresses to which replies should be sent.")
    last_event: str | None = Field(None, description="The status of the email.")

class EmailTemplateInput(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the published email template.")
    variables: dict[str, str | float] | None = Field(None, description="Template variables object with key/value pairs.")

class PostContactsBodyTopicsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The topic ID.")
    subscription: Literal["opt_in", "opt_out"] | None = Field(None, description="The subscription status for this topic.")

class PostEmailsBodyTemplate(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The id of the published email template.")
    variables: dict[str, str | float] | None = Field(None, description="Template variables object with key/value pairs.")

class Tag(PermissiveModel):
    name: str | None = Field(None, description="The name of the email tag. It can only contain ASCII letters (a–z, A–Z), numbers (0–9), underscores (_), or dashes (-). It can contain no more than 256 characters.")
    value: str | None = Field(None, description="The value of the email tag.It can only contain ASCII letters (a–z, A–Z), numbers (0–9), underscores (_), or dashes (-). It can contain no more than 256 characters.")

class SendEmailRequest(PermissiveModel):
    from_: str = Field(..., validation_alias="from", serialization_alias="from", description="Sender email address. To include a friendly name, use the format \"Your Name <sender@domain.com>\".")
    to: str | list[str] = Field(..., description="Recipient email address. For multiple addresses, send as an array of strings. Max 50.")
    subject: str = Field(..., description="Email subject.")
    bcc: str | list[str] | None = Field(None, description="Bcc recipient email address. For multiple addresses, send as an array of strings.")
    cc: str | list[str] | None = Field(None, description="Cc recipient email address. For multiple addresses, send as an array of strings.")
    reply_to: str | list[str] | None = Field(None, description="Reply-to email address. For multiple addresses, send as an array of strings.")
    html: str | None = Field(None, description="The HTML version of the message.")
    text: str | None = Field(None, description="The plain text version of the message.")
    template: EmailTemplateInput | None = None
    headers: dict[str, Any] | None = Field(None, description="Custom headers to add to the email.")
    scheduled_at: str | None = Field(None, description="Schedule email to be sent later. The date should be in ISO 8601 format.")
    attachments: list[Attachment] | None = None
    tags: list[Tag] | None = None
    topic_id: str | None = Field(None, description="The topic ID to scope the email to. If the recipient is a contact and opted-in to the topic, the email is sent. If opted-out, the email is not sent. If the recipient is not a contact, the email is sent if the topic's default subscription is opt_in.")

class TemplateVariable(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the template variable.")
    key: str = Field(..., description="The key of the variable.")
    type_: Literal["string", "number", "boolean", "object", "list"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the variable.")
    fallback_value: str | float | bool | dict[str, Any] | list[Any] | None = Field(None, description="The fallback value of the variable.")
    created_at: str | None = Field(None, description="Timestamp indicating when the variable was created.", json_schema_extra={'format': 'date-time'})
    updated_at: str | None = Field(None, description="Timestamp indicating when the variable was last updated.", json_schema_extra={'format': 'date-time'})

class Template(PermissiveModel):
    object_: str | None = Field(None, validation_alias="object", serialization_alias="object", description="The type of object.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the template.")
    current_version_id: str | None = Field(None, description="The ID of the current version of the template.")
    name: str | None = Field(None, description="The name of the template.")
    alias: str | None = Field(None, description="The alias of the template.")
    from_: str | None = Field(None, validation_alias="from", serialization_alias="from", description="Sender email address. To include a friendly name, use the format \"Your Name <sender@domain.com>\".")
    subject: str | None = Field(None, description="Email subject.")
    reply_to: list[str] | None = Field(None, description="Reply-to email addresses.")
    html: str | None = Field(None, description="The HTML version of the template.")
    text: str | None = Field(None, description="The plain text version of the template.")
    variables: list[TemplateVariable] | None = None
    created_at: str | None = Field(None, description="Timestamp indicating when the template was created.", json_schema_extra={'format': 'date-time'})
    updated_at: str | None = Field(None, description="Timestamp indicating when the template was last updated.", json_schema_extra={'format': 'date-time'})
    status: Literal["draft", "published"] | None = Field(None, description="The publication status of the template.")
    published_at: str | None = Field(None, description="Timestamp indicating when the template was published.", json_schema_extra={'format': 'date-time'})
    has_unpublished_versions: bool | None = Field(None, description="Indicates whether the template has unpublished versions.")

class TemplateVariableInput(PermissiveModel):
    key: str = Field(..., description="The key of the variable.")
    type_: Literal["string", "number", "boolean", "object", "list"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the variable.")
    fallback_value: str | float | bool | dict[str, Any] | list[Any] | None = Field(None, description="The fallback value of the variable.")


# Rebuild models to resolve forward references (required for circular refs)
Attachment.model_rebuild()
Email.model_rebuild()
EmailTemplateInput.model_rebuild()
PostContactsBodyTopicsItem.model_rebuild()
PostEmailsBodyTemplate.model_rebuild()
SendEmailRequest.model_rebuild()
Tag.model_rebuild()
Template.model_rebuild()
TemplateVariable.model_rebuild()
TemplateVariableInput.model_rebuild()

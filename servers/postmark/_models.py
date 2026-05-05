"""
Postmark MCP Server - Pydantic Models

Generated: 2026-05-05 13:51:55 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "DeleteTemplatesRequest",
    "GetBouncesByBounceidRequest",
    "GetBouncesDumpRequest",
    "GetBouncesRequest",
    "GetMessagesInboundDetailsRequest",
    "GetMessagesInboundRequest",
    "GetMessagesOutboundClicksByMessageidRequest",
    "GetMessagesOutboundClicksRequest",
    "GetMessagesOutboundDetailsRequest",
    "GetMessagesOutboundDumpRequest",
    "GetMessagesOutboundOpensByMessageidRequest",
    "GetMessagesOutboundOpensRequest",
    "GetMessagesOutboundRequest",
    "GetStatsOutboundBouncesRequest",
    "GetStatsOutboundClicksLocationRequest",
    "GetStatsOutboundClicksPlatformsRequest",
    "GetStatsOutboundClicksRequest",
    "GetStatsOutboundOpensEmailclientsRequest",
    "GetStatsOutboundOpensPlatformsRequest",
    "GetStatsOutboundOpensRequest",
    "GetStatsOutboundRequest",
    "GetStatsOutboundSendsRequest",
    "GetStatsOutboundSpamRequest",
    "GetStatsOutboundTrackedRequest",
    "GetTemplatesByTemplateIdOrAliasRequest",
    "GetTemplatesRequest",
    "GetTriggersInboundrulesRequest",
    "PostEmailBatchRequest",
    "PostEmailBatchWithTemplatesRequest",
    "PostEmailRequest",
    "PostEmailWithTemplateRequest",
    "PostTemplatesRequest",
    "PostTemplatesValidateRequest",
    "PutBouncesActivateRequest",
    "PutMessagesInboundBypassRequest",
    "PutMessagesInboundRetryRequest",
    "PutTemplatesRequest",
    "Attachment",
    "EmailWithTemplateRequest",
    "MessageHeader",
    "SendEmailRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_bounces
class GetBouncesRequestQuery(StrictModel):
    count: int = Field(default=..., description="Number of bounce records to return per request, up to a maximum of 500.", le=500)
    offset: int = Field(default=..., description="Number of bounce records to skip from the beginning of the result set for pagination.")
    type_: Literal["HardBounce", "Transient", "Unsubscribe", "Subscribe", "AutoResponder", "AddressChange", "DnsError", "SpamNotification", "OpenRelayTest", "Unknown", "SoftBounce", "VirusNotification", "MailFrontier Matador.", "BadEmailAddress", "SpamComplaint", "ManuallyDeactivated", "Unconfirmed", "Blocked", "SMTPApiError", "InboundError", "DMARCPolicy", "TemplateRenderingFailed"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter results by bounce type category (e.g., HardBounce, SoftBounce, SpamComplaint, DMARCPolicy, etc.).")
    inactive: bool | None = Field(default=None, description="Filter results to show only emails that were deactivated by Postmark (true), only active emails (false), or both if not specified.")
    email_filter: str | None = Field(default=None, validation_alias="emailFilter", serialization_alias="emailFilter", description="Filter results by a specific email address.", json_schema_extra={'format': 'email'})
    message_id: str | None = Field(default=None, validation_alias="messageID", serialization_alias="messageID", description="Filter results by the message ID associated with the bounce.")
    tag: str | None = Field(default=None, description="Filter results by a tag assigned to the message.")
    todate: str | None = Field(default=None, description="Filter results to include only bounces up to and including this date (format: YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    fromdate: str | None = Field(default=None, description="Filter results to include only bounces starting from and after this date (format: YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class GetBouncesRequest(StrictModel):
    """Retrieve a paginated list of email bounces from your Postmark server, with optional filtering by bounce type, email address, date range, and other criteria."""
    query: GetBouncesRequestQuery

# Operation: get_bounce_by_id
class GetBouncesByBounceidRequestPath(StrictModel):
    bounceid: int = Field(default=..., description="The unique identifier of the bounce record to retrieve. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetBouncesByBounceidRequest(StrictModel):
    """Retrieve detailed information about a specific bounce event by its ID. Use this to inspect bounce details such as type, email address, and timestamp for a particular bounce occurrence."""
    path: GetBouncesByBounceidRequestPath

# Operation: activate_bounce
class PutBouncesActivateRequestPath(StrictModel):
    bounceid: int = Field(default=..., description="The unique identifier of the bounce record to activate. Must be a valid 64-bit integer.", json_schema_extra={'format': 'int64'})
class PutBouncesActivateRequest(StrictModel):
    """Reactivate a bounce record in Postmark, allowing it to be processed again. This operation marks a previously bounced email address as active."""
    path: PutBouncesActivateRequestPath

# Operation: get_bounce_dump
class GetBouncesDumpRequestPath(StrictModel):
    bounceid: int = Field(default=..., description="The unique identifier of the bounce event whose dump data you want to retrieve. Must be a positive integer.", json_schema_extra={'format': 'int64'})
class GetBouncesDumpRequest(StrictModel):
    """Retrieve the detailed dump data for a specific bounce event. This provides comprehensive information about why a message bounced, including diagnostic details and headers."""
    path: GetBouncesDumpRequestPath

# Operation: send_email
class PostEmailRequestBody(StrictModel):
    attachments: list[Attachment] | None = Field(default=None, validation_alias="Attachments", serialization_alias="Attachments", description="Array of file attachments to include with the email. Each attachment should specify the file content, name, and MIME type.")
    from_: str | None = Field(default=None, validation_alias="From", serialization_alias="From", description="Sender email address. Must correspond to a registered and confirmed Sender Signature in your Postmark account.")
    headers: list[MessageHeader] | None = Field(default=None, validation_alias="Headers", serialization_alias="Headers", description="Array of custom email headers to include in the message. Each header should specify the name and value.")
    reply_to: str | None = Field(default=None, validation_alias="ReplyTo", serialization_alias="ReplyTo", description="Email address to use for reply-to functionality. Overrides the default Reply To address configured in the sender signature.")
    subject: str | None = Field(default=None, validation_alias="Subject", serialization_alias="Subject", description="Subject line for the email message.")
    tag: str | None = Field(default=None, validation_alias="Tag", serialization_alias="Tag", description="Categorical tag for organizing and tracking email statistics. Useful for segmenting outgoing emails by type or campaign.")
    to: str | None = Field(default=None, validation_alias="To", serialization_alias="To", description="Recipient email address or addresses. Multiple recipients should be comma-separated. Maximum of 50 recipients per request.")
    track_links: Literal["None", "HtmlAndText", "HtmlOnly", "TextOnly"] | None = Field(default=None, validation_alias="TrackLinks", serialization_alias="TrackLinks", description="Link tracking mode for click analytics. Options are None (no tracking), HtmlAndText (track both HTML and plain text links), HtmlOnly (track HTML links only), or TextOnly (track plain text links only). Defaults to the server's LinkTracking setting if not specified.")
    track_opens: bool | None = Field(default=None, validation_alias="TrackOpens", serialization_alias="TrackOpens", description="Enable open tracking for this email to measure when recipients open the message.")
    text_body: str | None = Field(default=None, validation_alias="TextBody", serialization_alias="TextBody", description="If no HtmlBody specified Plain text email message")
    html_body: str | None = Field(default=None, validation_alias="HtmlBody", serialization_alias="HtmlBody", description="If no TextBody specified HTML email message")
class PostEmailRequest(StrictModel):
    """Send a single email message through Postmark. Supports attachments, custom headers, link and open tracking, and email tagging for analytics."""
    body: PostEmailRequestBody | None = None

# Operation: send_emails_batch
class PostEmailBatchRequestBody(StrictModel):
    body: list[SendEmailRequest] | None = Field(default=None, description="Array of email objects to send in this batch. Each object should contain the email details (recipient, subject, body, etc.) in Postmark's standard email format. Order is preserved for processing.")
class PostEmailBatchRequest(StrictModel):
    """Send multiple emails in a single batch request to efficiently deliver messages through Postmark's email service."""
    body: PostEmailBatchRequestBody | None = None

# Operation: send_email_batch_with_templates
class PostEmailBatchWithTemplatesRequestBody(StrictModel):
    messages: list[EmailWithTemplateRequest] | None = Field(default=None, validation_alias="Messages", serialization_alias="Messages", description="Array of email message objects to send, each containing template identifiers and recipient details. Order is preserved for batch processing.")
class PostEmailBatchWithTemplatesRequest(StrictModel):
    """Send multiple emails in a single batch request using predefined email templates. This operation allows efficient bulk email delivery with template-based content."""
    body: PostEmailBatchWithTemplatesRequestBody | None = None

# Operation: send_email_with_template
class PostEmailWithTemplateRequestBody(StrictModel):
    attachments: list[Attachment] | None = Field(default=None, validation_alias="Attachments", serialization_alias="Attachments", description="Array of file attachments to include with the email. Each attachment should specify the file content, filename, and MIME type.")
    from_: str = Field(default=..., validation_alias="From", serialization_alias="From", description="Sender email address. Must be a valid email format and typically should be a verified sender on your Postmark account.", json_schema_extra={'format': 'email'})
    headers: list[MessageHeader] | None = Field(default=None, validation_alias="Headers", serialization_alias="Headers", description="Array of custom email headers to add to the message. Each header should include the header name and value.")
    inline_css: bool | None = Field(default=None, validation_alias="InlineCss", serialization_alias="InlineCss", description="Whether to automatically inline CSS styles from the template's style tags into individual HTML elements. Defaults to true.")
    reply_to: str | None = Field(default=None, validation_alias="ReplyTo", serialization_alias="ReplyTo", description="Email address to set as the reply-to destination. Must be a valid email format if provided.")
    tag: str | None = Field(default=None, validation_alias="Tag", serialization_alias="Tag", description="Arbitrary label or category tag to organize and filter this email in Postmark analytics and logs.")
    template_alias: str = Field(default=..., validation_alias="TemplateAlias", serialization_alias="TemplateAlias", description="Template identifier using a human-readable alias string. Either this or TemplateId must be provided to identify which template to use.")
    template_id: int = Field(default=..., validation_alias="TemplateId", serialization_alias="TemplateId", description="Template identifier using a numeric ID. Either this or TemplateAlias must be provided to identify which template to use.")
    template_model: dict[str, Any] = Field(default=..., validation_alias="TemplateModel", serialization_alias="TemplateModel", description="Object containing key-value pairs that populate dynamic placeholders in the template. Structure should match the variables defined in your template.")
    to: str = Field(default=..., validation_alias="To", serialization_alias="To", description="Recipient email address. Must be a valid email format.", json_schema_extra={'format': 'email'})
    track_links: Literal["None", "HtmlAndText", "HtmlOnly", "TextOnly"] | None = Field(default=None, validation_alias="TrackLinks", serialization_alias="TrackLinks", description="Enable click tracking by rewriting links in the email content. Options are: None (no tracking), HtmlAndText (track both HTML and plain text links), HtmlOnly (track HTML links only), or TextOnly (track plain text links only). Defaults to the server's LinkTracking setting if not specified.")
    track_opens: bool | None = Field(default=None, validation_alias="TrackOpens", serialization_alias="TrackOpens", description="Whether to track when this email is opened by the recipient. When enabled, Postmark injects a tracking pixel into the email.")
class PostEmailWithTemplateRequest(StrictModel):
    """Send an email to one or more recipients using a pre-defined email template. The template can be identified by either its numeric ID or string alias, and dynamic content is populated via the TemplateModel object."""
    body: PostEmailWithTemplateRequestBody

# Operation: search_messages_inbound
class GetMessagesInboundRequestQuery(StrictModel):
    count: int = Field(default=..., description="Number of messages to return per request, between 1 and 500.")
    offset: int = Field(default=..., description="Number of messages to skip from the beginning of results for pagination.")
    recipient: str | None = Field(default=None, description="Filter results to messages received by a specific email address.", json_schema_extra={'format': 'email'})
    fromemail: str | None = Field(default=None, description="Filter results to messages sent from a specific email address.", json_schema_extra={'format': 'email'})
    subject: str | None = Field(default=None, description="Filter results to messages with a matching subject line.")
    mailboxhash: str | None = Field(default=None, description="Filter results to messages associated with a specific mailbox hash identifier.")
    tag: str | None = Field(default=None, description="Filter results to messages with a specific tag label.")
    status: Literal["blocked", "processed", "queued", "failed", "scheduled"] | None = Field(default=None, description="Filter results by message processing status: blocked, processed, queued, failed, or scheduled.")
    todate: str | None = Field(default=None, description="Filter results to messages received on or before this date (format: YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    fromdate: str | None = Field(default=None, description="Filter results to messages received on or after this date (format: YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class GetMessagesInboundRequest(StrictModel):
    """Search and retrieve inbound messages with filtering by recipient, sender, subject, status, date range, and other metadata. Results are paginated using count and offset parameters."""
    query: GetMessagesInboundRequestQuery

# Operation: bypass_inbound_message_rules
class PutMessagesInboundBypassRequestPath(StrictModel):
    messageid: str = Field(default=..., description="The unique identifier of the inbound message that should be exempted from rule filtering.")
class PutMessagesInboundBypassRequest(StrictModel):
    """Allow a blocked inbound message to bypass email filtering rules. Use this to whitelist or recover messages that were incorrectly filtered by the server's inbound rules."""
    path: PutMessagesInboundBypassRequestPath

# Operation: get_inbound_message_details
class GetMessagesInboundDetailsRequestPath(StrictModel):
    messageid: str = Field(default=..., description="The unique identifier of the inbound message whose details you want to retrieve.")
class GetMessagesInboundDetailsRequest(StrictModel):
    """Retrieve detailed information about a specific inbound message, including its content, metadata, and delivery status."""
    path: GetMessagesInboundDetailsRequestPath

# Operation: retry_inbound_message
class PutMessagesInboundRetryRequestPath(StrictModel):
    messageid: str = Field(default=..., description="The unique identifier of the inbound message to retry. This should be the message ID returned from the inbound message service.")
class PutMessagesInboundRetryRequest(StrictModel):
    """Retry processing of a previously failed inbound message. Use this operation to reprocess a message that encountered an error during initial delivery or processing."""
    path: PutMessagesInboundRetryRequestPath

# Operation: search_messages_outbound
class GetMessagesOutboundRequestQuery(StrictModel):
    count: int = Field(default=..., description="Number of messages to return per request, between 1 and 500.")
    offset: int = Field(default=..., description="Number of messages to skip from the beginning of results for pagination.")
    recipient: str | None = Field(default=None, description="Filter results to messages received by a specific email address.", json_schema_extra={'format': 'email'})
    fromemail: str | None = Field(default=None, description="Filter results to messages sent from a specific email address.", json_schema_extra={'format': 'email'})
    tag: str | None = Field(default=None, description="Filter results to messages with a specific tag.")
    status: Literal["queued", "sent"] | None = Field(default=None, description="Filter results by message status: either queued (pending delivery) or sent (successfully delivered).")
    todate: str | None = Field(default=None, description="Filter results to messages sent on or before this date (ISO 8601 format, e.g., 2014-02-01).", json_schema_extra={'format': 'date'})
    fromdate: str | None = Field(default=None, description="Filter results to messages sent on or after this date (ISO 8601 format, e.g., 2014-02-01).", json_schema_extra={'format': 'date'})
class GetMessagesOutboundRequest(StrictModel):
    """Search and retrieve outbound messages with filtering by recipient, sender, status, date range, and tags. Results are paginated using count and offset parameters."""
    query: GetMessagesOutboundRequestQuery

# Operation: list_outbound_message_clicks
class GetMessagesOutboundClicksRequestQuery(StrictModel):
    count: int = Field(default=..., description="Number of click records to return per request, up to a maximum of 500 results.")
    offset: int = Field(default=..., description="Number of click records to skip before returning results, used for pagination.")
    recipient: str | None = Field(default=None, description="Filter results by recipient email address (To, Cc, or Bcc field).")
    tag: str | None = Field(default=None, description="Filter results by message tag or label.")
    client_company: str | None = Field(default=None, description="Filter results by email client company name (e.g., Microsoft, Apple, Google).")
    client_family: str | None = Field(default=None, description="Filter results by email client family or product line (e.g., OS X, Chrome).")
    os_family: str | None = Field(default=None, description="Filter results by operating system family without version specificity (e.g., OS X, Windows).")
    platform: str | None = Field(default=None, description="Filter results by device platform type (e.g., webmail, desktop, mobile).")
    country: str | None = Field(default=None, description="Filter results by country where the message was clicked.")
    city: str | None = Field(default=None, description="Filter results by city or region name where the message was clicked.")
class GetMessagesOutboundClicksRequest(StrictModel):
    """Retrieve click events from outbound messages with pagination and optional filtering by recipient, tags, client details, device information, and geographic location."""
    query: GetMessagesOutboundClicksRequestQuery

# Operation: list_message_outbound_clicks
class GetMessagesOutboundClicksByMessageidRequestPath(StrictModel):
    messageid: str = Field(default=..., description="The unique identifier of the outbound message for which to retrieve click statistics.")
class GetMessagesOutboundClicksByMessageidRequestQuery(StrictModel):
    count: int = Field(default=..., description="The number of click records to return per request, between 1 and 500 clicks.", ge=1, le=500)
    offset: int = Field(default=..., description="The number of click records to skip before returning results, used for pagination. Must be zero or greater.", ge=0)
class GetMessagesOutboundClicksByMessageidRequest(StrictModel):
    """Retrieve click statistics for a specific outbound message, including details about each click event with pagination support."""
    path: GetMessagesOutboundClicksByMessageidRequestPath
    query: GetMessagesOutboundClicksByMessageidRequestQuery

# Operation: list_message_opens
class GetMessagesOutboundOpensRequestQuery(StrictModel):
    count: int = Field(default=..., description="Number of open events to return per request, between 1 and 500.")
    offset: int = Field(default=..., description="Number of open events to skip before returning results, used for pagination.")
    recipient: str | None = Field(default=None, description="Filter results by recipient email address (To, Cc, or Bcc field).")
    tag: str | None = Field(default=None, description="Filter results by message tag.")
    client_company: str | None = Field(default=None, description="Filter results by client company name (e.g., Microsoft, Apple, Google).")
    client_family: str | None = Field(default=None, description="Filter results by client family (e.g., OS X, Chrome).")
    os_family: str | None = Field(default=None, description="Filter results by operating system family without version specificity (e.g., OS X, Windows).")
    platform: str | None = Field(default=None, description="Filter results by platform type where the message was opened (e.g., webmail, desktop, mobile).")
    country: str | None = Field(default=None, description="Filter results by country where the message was opened (e.g., Denmark, Russia).")
    city: str | None = Field(default=None, description="Filter results by city or region name where the message was opened (e.g., Moscow, New York).")
class GetMessagesOutboundOpensRequest(StrictModel):
    """Retrieve a paginated list of message open events across all messages, with optional filtering by recipient, tags, client details, location, and platform."""
    query: GetMessagesOutboundOpensRequestQuery

# Operation: get_message_opens_by_id
class GetMessagesOutboundOpensByMessageidRequestPath(StrictModel):
    messageid: str = Field(default=..., description="The unique identifier of the outbound message for which to retrieve open statistics.")
class GetMessagesOutboundOpensByMessageidRequestQuery(StrictModel):
    count: int = Field(default=..., description="The number of open records to return in this request. Must be between 1 and 500 (defaults to 1).", ge=1, le=500)
    offset: int = Field(default=..., description="The number of open records to skip before returning results, used for pagination. Must be 0 or greater (defaults to 0).", ge=0)
class GetMessagesOutboundOpensByMessageidRequest(StrictModel):
    """Retrieve a paginated list of open events for a specific outbound message. Use offset and count parameters to navigate through the results."""
    path: GetMessagesOutboundOpensByMessageidRequestPath
    query: GetMessagesOutboundOpensByMessageidRequestQuery

# Operation: get_outbound_message_details
class GetMessagesOutboundDetailsRequestPath(StrictModel):
    messageid: str = Field(default=..., description="The unique identifier of the outbound message whose details you want to retrieve.")
class GetMessagesOutboundDetailsRequest(StrictModel):
    """Retrieve detailed information about a specific outbound message, including delivery status, recipient information, and message content."""
    path: GetMessagesOutboundDetailsRequestPath

# Operation: get_outbound_message_dump
class GetMessagesOutboundDumpRequestPath(StrictModel):
    messageid: str = Field(default=..., description="The unique identifier of the outbound message for which to retrieve the complete dump data.")
class GetMessagesOutboundDumpRequest(StrictModel):
    """Retrieve the full dump of an outbound message, including all metadata and content details. This operation requires authentication via a Postmark server token."""
    path: GetMessagesOutboundDumpRequestPath

# Operation: get_outbound_stats
class GetStatsOutboundRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter statistics to a specific tag, useful for segmenting results by campaign, sender, or other classification.")
    fromdate: str | None = Field(default=None, description="Start date for the statistics range in ISO 8601 format (YYYY-MM-DD). Results will include data from this date onward.", json_schema_extra={'format': 'date'})
    todate: str | None = Field(default=None, description="End date for the statistics range in ISO 8601 format (YYYY-MM-DD). Results will include data up to and including this date.", json_schema_extra={'format': 'date'})
class GetStatsOutboundRequest(StrictModel):
    """Retrieve outbound email statistics and performance overview. Optionally filter results by tag and date range to analyze specific sending campaigns or time periods."""
    query: GetStatsOutboundRequestQuery | None = None

# Operation: get_outbound_bounce_statistics
class GetStatsOutboundBouncesRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter bounce statistics to a specific tag associated with your emails.")
    fromdate: str | None = Field(default=None, description="Filter statistics to include data starting from this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    todate: str | None = Field(default=None, description="Filter statistics to include data up to this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class GetStatsOutboundBouncesRequest(StrictModel):
    """Retrieve bounce statistics for outbound emails, with optional filtering by tag and date range to analyze delivery failures."""
    query: GetStatsOutboundBouncesRequestQuery | None = None

# Operation: get_outbound_click_stats
class GetStatsOutboundClicksRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter statistics to only include clicks associated with a specific tag.")
    fromdate: str | None = Field(default=None, description="Filter statistics to include only clicks from this date forward (inclusive). Specify as a calendar date in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    todate: str | None = Field(default=None, description="Filter statistics to include only clicks up to this date (inclusive). Specify as a calendar date in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
class GetStatsOutboundClicksRequest(StrictModel):
    """Retrieve click count statistics for outbound links, with optional filtering by tag and date range to analyze link performance over time."""
    query: GetStatsOutboundClicksRequestQuery | None = None

# Operation: get_outbound_clicks_by_location
class GetStatsOutboundClicksLocationRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter results to include only clicks from messages tagged with this value.")
    fromdate: str | None = Field(default=None, description="Include statistics starting from this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    todate: str | None = Field(default=None, description="Include statistics up to this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class GetStatsOutboundClicksLocationRequest(StrictModel):
    """Retrieve click statistics for outbound links aggregated by body location. Use optional filters to narrow results by tag and date range."""
    query: GetStatsOutboundClicksLocationRequestQuery | None = None

# Operation: list_outbound_click_stats_by_platform
class GetStatsOutboundClicksPlatformsRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter results to include only clicks associated with a specific tag.")
    fromdate: str | None = Field(default=None, description="Filter results to include only statistics from this date forward, specified in ISO 8601 format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    todate: str | None = Field(default=None, description="Filter results to include only statistics up to and including this date, specified in ISO 8601 format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class GetStatsOutboundClicksPlatformsRequest(StrictModel):
    """Retrieve outbound click statistics aggregated by browser platform. Use optional filters to narrow results by tag and date range."""
    query: GetStatsOutboundClicksPlatformsRequestQuery | None = None

# Operation: get_outbound_email_opens
class GetStatsOutboundOpensRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter results to only include statistics for messages tagged with this value.")
    fromdate: str | None = Field(default=None, description="Filter statistics to include only data from this date forward, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    todate: str | None = Field(default=None, description="Filter statistics to include only data up to and including this date, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class GetStatsOutboundOpensRequest(StrictModel):
    """Retrieve email open statistics for outbound messages, with optional filtering by tag and date range to analyze engagement metrics."""
    query: GetStatsOutboundOpensRequestQuery | None = None

# Operation: list_outbound_email_opens_by_client
class GetStatsOutboundOpensEmailclientsRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter results to only include opens from messages tagged with this value.")
    fromdate: str | None = Field(default=None, description="Include opens starting from this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    todate: str | None = Field(default=None, description="Include opens up to this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class GetStatsOutboundOpensEmailclientsRequest(StrictModel):
    """Retrieve email client statistics for outbound message opens, optionally filtered by tag and date range. Use this to analyze which email clients your recipients use when opening messages."""
    query: GetStatsOutboundOpensEmailclientsRequestQuery | None = None

# Operation: list_email_opens_by_platform
class GetStatsOutboundOpensPlatformsRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter statistics to only include opens from messages tagged with this value.")
    fromdate: str | None = Field(default=None, description="Include statistics starting from this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    todate: str | None = Field(default=None, description="Include statistics up to this date (inclusive). Specify in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class GetStatsOutboundOpensPlatformsRequest(StrictModel):
    """Retrieve email open statistics aggregated by email client platform. Filter results by tag and date range to analyze which platforms your recipients use to open emails."""
    query: GetStatsOutboundOpensPlatformsRequestQuery | None = None

# Operation: get_outbound_send_stats
class GetStatsOutboundSendsRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter results to only include statistics for messages with this specific tag.")
    fromdate: str | None = Field(default=None, description="Filter statistics to include only data from this date forward, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    todate: str | None = Field(default=None, description="Filter statistics to include only data up to and including this date, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
class GetStatsOutboundSendsRequest(StrictModel):
    """Retrieve statistics on sent messages, with optional filtering by tag and date range. Use this to analyze outbound sending activity over time."""
    query: GetStatsOutboundSendsRequestQuery | None = None

# Operation: get_outbound_spam_stats
class GetStatsOutboundSpamRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter statistics by a specific tag to isolate metrics for tagged message groups.")
    fromdate: str | None = Field(default=None, description="Start date for the statistics query in ISO 8601 format (YYYY-MM-DD). Results will include data from this date onward.", json_schema_extra={'format': 'date'})
    todate: str | None = Field(default=None, description="End date for the statistics query in ISO 8601 format (YYYY-MM-DD). Results will include data up to and including this date.", json_schema_extra={'format': 'date'})
class GetStatsOutboundSpamRequest(StrictModel):
    """Retrieve spam complaint statistics for outbound messages. Filter results by tag and date range to analyze spam performance metrics."""
    query: GetStatsOutboundSpamRequestQuery | None = None

# Operation: get_outbound_tracked_email_stats
class GetStatsOutboundTrackedRequestQuery(StrictModel):
    tag: str | None = Field(default=None, description="Filter results to only include emails associated with this specific tag.")
    fromdate: str | None = Field(default=None, description="Start date for the stats query in ISO 8601 format (YYYY-MM-DD). Only emails sent on or after this date will be included.", json_schema_extra={'format': 'date'})
    todate: str | None = Field(default=None, description="End date for the stats query in ISO 8601 format (YYYY-MM-DD). Only emails sent on or before this date will be included.", json_schema_extra={'format': 'date'})
class GetStatsOutboundTrackedRequest(StrictModel):
    """Retrieve counts of tracked outbound emails, with optional filtering by tag and date range. Use this to monitor email delivery metrics for a specific time period or tag."""
    query: GetStatsOutboundTrackedRequestQuery | None = None

# Operation: list_templates
class GetTemplatesRequestQuery(StrictModel):
    count: int = Field(default=..., validation_alias="Count", serialization_alias="Count", description="The maximum number of templates to return in this request. Must be a positive integer.")
    offset: int = Field(default=..., validation_alias="Offset", serialization_alias="Offset", description="The number of templates to skip before returning results, enabling pagination through your template collection. Must be a non-negative integer.")
class GetTemplatesRequest(StrictModel):
    """Retrieve a paginated list of email templates associated with this Postmark server. Use Count and Offset parameters to control pagination through your template collection."""
    query: GetTemplatesRequestQuery

# Operation: create_template
class PostTemplatesRequestBody(StrictModel):
    alias: str | None = Field(default=None, validation_alias="Alias", serialization_alias="Alias", description="Optional unique identifier for this template using alphanumeric characters, dots, hyphens, and underscores. Must start with a letter. Useful for programmatic template references.")
    name: str = Field(default=..., validation_alias="Name", serialization_alias="Name", description="Human-readable name for the template displayed in the Postmark dashboard and API responses.")
    subject: str = Field(default=..., validation_alias="Subject", serialization_alias="Subject", description="Template definition for the email subject line. Supports template variables and dynamic content using Postmark's templating syntax.")
    text_body: str | None = Field(default=None, validation_alias="TextBody", serialization_alias="TextBody", description="The Text template definition for this Template.")
    html_body: str | None = Field(default=None, validation_alias="HtmlBody", serialization_alias="HtmlBody", description="The HTML template definition for this Template.")
class PostTemplatesRequest(StrictModel):
    """Create a new email template with a subject line and optional alias for easy reference. Templates can be used to standardize email content across your application."""
    body: PostTemplatesRequestBody

# Operation: validate_template
class PostTemplatesValidateRequestBody(StrictModel):
    inline_css_for_html_test_render: bool | None = Field(default=None, validation_alias="InlineCssForHtmlTestRender", serialization_alias="InlineCssForHtmlTestRender", description="When validating HTML content, controls whether CSS style blocks are inlined as style attributes on matching elements. Defaults to true; set to false to disable CSS inlining.")
    subject: str | None = Field(default=None, validation_alias="Subject", serialization_alias="Subject", description="The subject line template content to validate using Postmark's template language syntax. Required if neither HtmlBody nor TextBody is provided.")
    test_render_model: dict[str, Any] | None = Field(default=None, validation_alias="TestRenderModel", serialization_alias="TestRenderModel", description="A data object used to render and test the template content, allowing validation of dynamic variable substitution and template logic.")
class PostTemplatesValidateRequest(StrictModel):
    """Validate template content by testing subject lines, HTML, and text body rendering with optional CSS inlining and a test data model."""
    body: PostTemplatesValidateRequestBody | None = None

# Operation: get_template
class GetTemplatesByTemplateIdOrAliasRequestPath(StrictModel):
    template_id_or_alias: str = Field(default=..., validation_alias="templateIdOrAlias", serialization_alias="templateIdOrAlias", description="The unique identifier or alias of the template to retrieve. You can use either the TemplateID (numeric identifier) or the Alias (custom name) to look up the template.")
class GetTemplatesByTemplateIdOrAliasRequest(StrictModel):
    """Retrieve a specific email template by its unique identifier or alias. Use this to fetch template details for rendering, previewing, or managing email communications."""
    path: GetTemplatesByTemplateIdOrAliasRequestPath

# Operation: update_template
class PutTemplatesRequestPath(StrictModel):
    template_id_or_alias: str = Field(default=..., validation_alias="templateIdOrAlias", serialization_alias="templateIdOrAlias", description="The unique identifier or alias of the template to update. Use either the numeric TemplateID or the string Alias value.")
class PutTemplatesRequestBody(StrictModel):
    alias: str | None = Field(default=None, validation_alias="Alias", serialization_alias="Alias", description="Optional string identifier for the template using letters, numbers, and the characters '.', '-', '_'. Must start with a letter.")
    name: str | None = Field(default=None, validation_alias="Name", serialization_alias="Name", description="Optional human-readable name for the template displayed in the UI.")
    subject: str | None = Field(default=None, validation_alias="Subject", serialization_alias="Subject", description="Optional subject line template definition that supports variable substitution for dynamic email subjects.")
class PutTemplatesRequest(StrictModel):
    """Update an existing email template by its ID or alias. Modify the template's name, subject line, or alias identifier."""
    path: PutTemplatesRequestPath
    body: PutTemplatesRequestBody | None = None

# Operation: delete_template
class DeleteTemplatesRequestPath(StrictModel):
    template_id_or_alias: str = Field(default=..., validation_alias="templateIdOrAlias", serialization_alias="templateIdOrAlias", description="The unique identifier or alias of the template to delete. You can use either the TemplateID or the Alias value.")
class DeleteTemplatesRequest(StrictModel):
    """Permanently delete a template by its ID or alias. This action cannot be undone."""
    path: DeleteTemplatesRequestPath

# Operation: list_inbound_rule_triggers
class GetTriggersInboundrulesRequestQuery(StrictModel):
    count: int = Field(default=..., description="The maximum number of trigger records to return in this request. Must be a positive integer.")
    offset: int = Field(default=..., description="The number of records to skip before returning results, enabling pagination through large result sets. Must be a non-negative integer.")
class GetTriggersInboundrulesRequest(StrictModel):
    """Retrieve a paginated list of inbound rule triggers configured for the server. Use count and offset parameters to control pagination through the results."""
    query: GetTriggersInboundrulesRequestQuery

# ============================================================================
# Component Models
# ============================================================================

class Attachment(PermissiveModel):
    """An attachment for an email message."""
    content: str | None = Field(None, validation_alias="Content", serialization_alias="Content")
    content_id: str | None = Field(None, validation_alias="ContentID", serialization_alias="ContentID")
    content_type: str | None = Field(None, validation_alias="ContentType", serialization_alias="ContentType")
    name: str | None = Field(None, validation_alias="Name", serialization_alias="Name")

class AttachmentCollection(RootModel[list[Attachment]]):
    pass

class MessageHeader(PermissiveModel):
    """A single header for an email message."""
    name: str | None = Field(None, validation_alias="Name", serialization_alias="Name", description="The header's name.")
    value: str | None = Field(None, validation_alias="Value", serialization_alias="Value", description="The header's value.")

class HeaderCollection(RootModel[list[MessageHeader]]):
    pass

class EmailWithTemplateRequest(PermissiveModel):
    attachments: AttachmentCollection | None = Field(None, validation_alias="Attachments", serialization_alias="Attachments")
    bcc: str | None = Field(None, validation_alias="Bcc", serialization_alias="Bcc", json_schema_extra={'format': 'email'})
    cc: str | None = Field(None, validation_alias="Cc", serialization_alias="Cc", json_schema_extra={'format': 'email'})
    from_: str = Field(..., validation_alias="From", serialization_alias="From", json_schema_extra={'format': 'email'})
    headers: HeaderCollection | None = Field(None, validation_alias="Headers", serialization_alias="Headers")
    inline_css: bool | None = Field(True, validation_alias="InlineCss", serialization_alias="InlineCss")
    reply_to: str | None = Field(None, validation_alias="ReplyTo", serialization_alias="ReplyTo")
    tag: str | None = Field(None, validation_alias="Tag", serialization_alias="Tag")
    template_alias: str = Field(..., validation_alias="TemplateAlias", serialization_alias="TemplateAlias", description="Required if 'TemplateId' is not specified.")
    template_id: int = Field(..., validation_alias="TemplateId", serialization_alias="TemplateId", description="Required if 'TemplateAlias' is not specified.")
    template_model: dict[str, Any] = Field(..., validation_alias="TemplateModel", serialization_alias="TemplateModel")
    to: str = Field(..., validation_alias="To", serialization_alias="To", json_schema_extra={'format': 'email'})
    track_links: Literal["None", "HtmlAndText", "HtmlOnly", "TextOnly"] | None = Field(None, validation_alias="TrackLinks", serialization_alias="TrackLinks", description="Replace links in content to enable \"click tracking\" stats. Default is 'null', which uses the server's LinkTracking setting'.")
    track_opens: bool | None = Field(None, validation_alias="TrackOpens", serialization_alias="TrackOpens", description="Activate open tracking for this email.")

class SendEmailRequest(PermissiveModel):
    attachments: AttachmentCollection | None = Field(None, validation_alias="Attachments", serialization_alias="Attachments")
    bcc: str | None = Field(None, validation_alias="Bcc", serialization_alias="Bcc", description="Bcc recipient email address. Multiple addresses are comma seperated. Max 50.")
    cc: str | None = Field(None, validation_alias="Cc", serialization_alias="Cc", description="Recipient email address. Multiple addresses are comma seperated. Max 50.")
    from_: str | None = Field(None, validation_alias="From", serialization_alias="From", description="The sender email address. Must have a registered and confirmed Sender Signature.")
    headers: HeaderCollection | None = Field(None, validation_alias="Headers", serialization_alias="Headers")
    html_body: str | None = Field(None, validation_alias="HtmlBody", serialization_alias="HtmlBody", description="If no TextBody specified HTML email message")
    reply_to: str | None = Field(None, validation_alias="ReplyTo", serialization_alias="ReplyTo", description="Reply To override email address. Defaults to the Reply To set in the sender signature.")
    subject: str | None = Field(None, validation_alias="Subject", serialization_alias="Subject", description="Email Subject")
    tag: str | None = Field(None, validation_alias="Tag", serialization_alias="Tag", description="Email tag that allows you to categorize outgoing emails and get detailed statistics.")
    text_body: str | None = Field(None, validation_alias="TextBody", serialization_alias="TextBody", description="If no HtmlBody specified Plain text email message")
    to: str | None = Field(None, validation_alias="To", serialization_alias="To", description="Recipient email address. Multiple addresses are comma seperated. Max 50.")
    track_links: Literal["None", "HtmlAndText", "HtmlOnly", "TextOnly"] | None = Field(None, validation_alias="TrackLinks", serialization_alias="TrackLinks", description="Replace links in content to enable \"click tracking\" stats. Default is 'null', which uses the server's LinkTracking setting'.")
    track_opens: bool | None = Field(None, validation_alias="TrackOpens", serialization_alias="TrackOpens", description="Activate open tracking for this email.")


# Rebuild models to resolve forward references (required for circular refs)
Attachment.model_rebuild()
AttachmentCollection.model_rebuild()
EmailWithTemplateRequest.model_rebuild()
HeaderCollection.model_rebuild()
MessageHeader.model_rebuild()
SendEmailRequest.model_rebuild()

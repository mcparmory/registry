"""
Mailtrap MCP Server - Pydantic Models

Generated: 2026-04-14 18:25:51 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "CreateSendingDomainRequest",
    "DeleteSendingDomainRequest",
    "DeleteSuppressionRequest",
    "GetAccountSendingStatsByCategoriesRequest",
    "GetAccountSendingStatsByDateRequest",
    "GetAccountSendingStatsByDomainsRequest",
    "GetAccountSendingStatsByEmailServiceProvidersRequest",
    "GetAccountSendingStatsRequest",
    "GetEmailLogMessageRequest",
    "GetSendingDomainRequest",
    "GetSendingDomainsRequest",
    "GetSuppressionsRequest",
    "ListEmailLogsRequest",
    "SendSendingDomainSetupInstructionsRequest",
    "EmailLogsListFilters",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_sending_domains
class GetSendingDomainsRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for the account. Must be a positive integer.")
class GetSendingDomainsRequest(StrictModel):
    """Retrieve all sending domains configured for an account along with their current verification status. Use this to view domain authentication and readiness for email sending."""
    path: GetSendingDomainsRequestPath

# Operation: create_sending_domain
class CreateSendingDomainRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for your account. This is a positive integer that specifies which account owns the sending domain.")
class CreateSendingDomainRequestBodySendingDomain(StrictModel):
    domain_name: str = Field(default=..., validation_alias="domain_name", serialization_alias="domain_name", description="The domain name you want to use for sending emails (e.g., example.com). Must be a valid hostname format.", json_schema_extra={'format': 'hostname'})
class CreateSendingDomainRequestBody(StrictModel):
    sending_domain: CreateSendingDomainRequestBodySendingDomain
class CreateSendingDomainRequest(StrictModel):
    """Create a sending domain for email authentication. After creation, you'll need to add DNS records (SPF, DKIM, DMARC) and verify them before sending emails through this domain."""
    path: CreateSendingDomainRequestPath
    body: CreateSendingDomainRequestBody

# Operation: get_sending_domain
class GetSendingDomainRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for your account.")
    sending_domain_id: int = Field(default=..., description="The unique identifier for the sending domain whose details and verification status you want to retrieve.")
class GetSendingDomainRequest(StrictModel):
    """Retrieve detailed information and verification status for a specific sending domain associated with your account."""
    path: GetSendingDomainRequestPath

# Operation: delete_sending_domain
class DeleteSendingDomainRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for your account. This is a positive integer that specifies which account owns the sending domain being deleted.")
    sending_domain_id: int = Field(default=..., description="The unique identifier for the sending domain to be deleted. This is a positive integer that identifies the specific domain configuration to remove from your account.")
class DeleteSendingDomainRequest(StrictModel):
    """Permanently remove a sending domain from your account. This action cannot be undone and will prevent further email transmission through this domain."""
    path: DeleteSendingDomainRequestPath

# Operation: send_sending_domain_setup_instructions
class SendSendingDomainSetupInstructionsRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for the account that owns the sending domain.")
    sending_domain_id: int = Field(default=..., description="The unique identifier for the sending domain to configure.")
class SendSendingDomainSetupInstructionsRequestBody(StrictModel):
    email: str = Field(default=..., description="The email address where the DNS setup instructions will be sent. Must be a valid email format.", json_schema_extra={'format': 'email'})
class SendSendingDomainSetupInstructionsRequest(StrictModel):
    """Send DNS configuration setup instructions to a specified email address for a sending domain. This allows domain administrators to receive the necessary steps to configure DNS records for email authentication."""
    path: SendSendingDomainSetupInstructionsRequestPath
    body: SendSendingDomainSetupInstructionsRequestBody

# Operation: list_suppressions
class GetSuppressionsRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for your account.")
class GetSuppressionsRequestQuery(StrictModel):
    email: str | None = Field(default=None, description="Filter results to a specific email address. Must be a valid email format.", json_schema_extra={'format': 'email'})
    start_time: str | None = Field(default=None, description="Filter results to show only emails suppressed after this timestamp. Use ISO 8601 date-time format (e.g., 2025-01-01T00:00:00Z).", json_schema_extra={'format': 'date-time'})
class GetSuppressionsRequest(StrictModel):
    """Retrieve a list of suppressed email addresses for your account. Suppressed addresses will not receive any emails. Results are limited to 1000 suppressions per request and can be filtered by email address or suppression date."""
    path: GetSuppressionsRequestPath
    query: GetSuppressionsRequestQuery | None = None

# Operation: delete_suppression
class DeleteSuppressionRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for the account containing the suppression record. Must be a positive integer.")
    suppression_id: int = Field(default=..., description="The unique identifier for the suppression record to delete. Must be a positive integer.")
class DeleteSuppressionRequest(StrictModel):
    """Remove an email address from the suppression list, allowing it to receive messages again. This operation permanently deletes the suppression record for the specified account."""
    path: DeleteSuppressionRequestPath

# Operation: get_account_sending_stats
class GetAccountSendingStatsRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for the account whose sending statistics should be retrieved.")
class GetAccountSendingStatsRequestQuery(StrictModel):
    start_date: str = Field(default=..., description="The beginning of the date range for which to retrieve statistics, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    end_date: str = Field(default=..., description="The end of the date range for which to retrieve statistics, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    sending_domain_ids: list[int] | None = Field(default=None, validation_alias="sending_domain_ids[]", serialization_alias="sending_domain_ids[]", description="Optional list of sending domain IDs to filter results. When provided, only statistics for the specified domains are included; omit to retrieve results for all sending domains.")
    sending_streams: list[Literal["transactional", "bulk"]] | None = Field(default=None, validation_alias="sending_streams[]", serialization_alias="sending_streams[]", description="Optional list of sending stream types to filter results (e.g., transactional, bulk). When provided, only statistics for the specified streams are included; omit to retrieve results for all sending streams.")
    categories: list[str] | None = Field(default=None, validation_alias="categories[]", serialization_alias="categories[]", description="Optional list of email categories to filter results (e.g., Welcome Email, Password Reset). When provided, only statistics for the specified categories are included; omit to retrieve results for all categories.")
    email_service_providers: list[Literal["Google", "Yahoo", "Outlook", "Hey", "Google Workspace", "Zoho Email", "ProtonMail", "Yandex", "iCloud", "Office 365", "Amazon SES (Simple Email Service)", "Proofpoint Email Protection", "Mimecast Email Protection", "GMX.net", "Rackspace", "OVH hosted", "Linode hosted", "GoDaddy", "Symantec Email Protection", "Barracuda Email Protection", "Cisco Email Protection", "FastMail", "Naver", "Seznam", "Comcast", "Spectrum"]] | None = Field(default=None, validation_alias="email_service_providers[]", serialization_alias="email_service_providers[]", description="Optional list of email service providers to filter results (e.g., Google, Yahoo). When provided, only statistics for the specified ESPs are included; omit to retrieve results for all email service providers.")
class GetAccountSendingStatsRequest(StrictModel):
    """Retrieve sending statistics for an account over a specified date range, with optional filtering by sending domains, streams, categories, and email service providers."""
    path: GetAccountSendingStatsRequestPath
    query: GetAccountSendingStatsRequestQuery

# Operation: get_account_sending_stats_by_domains
class GetAccountSendingStatsByDomainsRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for the account whose sending statistics should be retrieved.")
class GetAccountSendingStatsByDomainsRequestQuery(StrictModel):
    start_date: str = Field(default=..., description="The beginning of the date range (inclusive) for which to retrieve statistics, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    end_date: str = Field(default=..., description="The end of the date range (inclusive) for which to retrieve statistics, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    sending_domain_ids: list[int] | None = Field(default=None, validation_alias="sending_domain_ids[]", serialization_alias="sending_domain_ids[]", description="Optional list of sending domain IDs to filter results. When provided, only statistics for the specified domains are included; omit to include all domains.")
    sending_streams: list[Literal["transactional", "bulk"]] | None = Field(default=None, validation_alias="sending_streams[]", serialization_alias="sending_streams[]", description="Optional list of sending stream types to filter results (e.g., transactional, bulk). When provided, only statistics for the specified streams are included; omit to include all streams.")
    categories: list[str] | None = Field(default=None, validation_alias="categories[]", serialization_alias="categories[]", description="Optional list of message categories to filter results (e.g., Welcome Email, Password Reset). When provided, only statistics for the specified categories are included; omit to include all categories.")
    email_service_providers: list[Literal["Google", "Yahoo", "Outlook", "Hey", "Google Workspace", "Zoho Email", "ProtonMail", "Yandex", "iCloud", "Office 365", "Amazon SES (Simple Email Service)", "Proofpoint Email Protection", "Mimecast Email Protection", "GMX.net", "Rackspace", "OVH hosted", "Linode hosted", "GoDaddy", "Symantec Email Protection", "Barracuda Email Protection", "Cisco Email Protection", "FastMail", "Naver", "Seznam", "Comcast", "Spectrum"]] | None = Field(default=None, validation_alias="email_service_providers[]", serialization_alias="email_service_providers[]", description="Optional list of email service provider names to filter results (e.g., Google, Yahoo). When provided, only statistics for the specified providers are included; omit to include all providers.")
class GetAccountSendingStatsByDomainsRequest(StrictModel):
    """Retrieve sending statistics for an account aggregated by sending domains over a specified date range. Use optional filters to narrow results by specific domains, sending streams, message categories, or email service providers."""
    path: GetAccountSendingStatsByDomainsRequestPath
    query: GetAccountSendingStatsByDomainsRequestQuery

# Operation: get_sending_stats_by_categories
class GetAccountSendingStatsByCategoriesRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for the account whose sending statistics should be retrieved.")
class GetAccountSendingStatsByCategoriesRequestQuery(StrictModel):
    start_date: str = Field(default=..., description="The beginning of the date range (inclusive) for which to retrieve statistics, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    end_date: str = Field(default=..., description="The end of the date range (inclusive) for which to retrieve statistics, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    sending_domain_ids: list[int] | None = Field(default=None, validation_alias="sending_domain_ids[]", serialization_alias="sending_domain_ids[]", description="Optional list of sending domain IDs to filter results. When provided, only statistics for the specified domains are included; omit to include all domains.")
    sending_streams: list[Literal["transactional", "bulk"]] | None = Field(default=None, validation_alias="sending_streams[]", serialization_alias="sending_streams[]", description="Optional list of sending stream types to filter results (e.g., 'transactional', 'bulk'). When provided, only statistics for the specified streams are included; omit to include all streams.")
    categories: list[str] | None = Field(default=None, validation_alias="categories[]", serialization_alias="categories[]", description="Optional list of email category names to filter results (e.g., 'Welcome Email', 'Password Reset'). When provided, only statistics for the specified categories are included; omit to include all categories.")
    email_service_providers: list[Literal["Google", "Yahoo", "Outlook", "Hey", "Google Workspace", "Zoho Email", "ProtonMail", "Yandex", "iCloud", "Office 365", "Amazon SES (Simple Email Service)", "Proofpoint Email Protection", "Mimecast Email Protection", "GMX.net", "Rackspace", "OVH hosted", "Linode hosted", "GoDaddy", "Symantec Email Protection", "Barracuda Email Protection", "Cisco Email Protection", "FastMail", "Naver", "Seznam", "Comcast", "Spectrum"]] | None = Field(default=None, validation_alias="email_service_providers[]", serialization_alias="email_service_providers[]", description="Optional list of email service provider names to filter results (e.g., 'Google', 'Yahoo'). When provided, only statistics for the specified providers are included; omit to include all providers.")
class GetAccountSendingStatsByCategoriesRequest(StrictModel):
    """Retrieve sending statistics aggregated by email categories for a specified account and date range. Use optional filters to narrow results by sending domain, stream type, category name, or email service provider."""
    path: GetAccountSendingStatsByCategoriesRequestPath
    query: GetAccountSendingStatsByCategoriesRequestQuery

# Operation: get_account_sending_stats_by_email_service_providers
class GetAccountSendingStatsByEmailServiceProvidersRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for the account whose sending statistics should be retrieved.")
class GetAccountSendingStatsByEmailServiceProvidersRequestQuery(StrictModel):
    start_date: str = Field(default=..., description="The beginning of the date range (inclusive) for which to include sending statistics, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    end_date: str = Field(default=..., description="The end of the date range (inclusive) for which to include sending statistics, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    sending_domain_ids: list[int] | None = Field(default=None, validation_alias="sending_domain_ids[]", serialization_alias="sending_domain_ids[]", description="Optional list of sending domain IDs to filter results. When provided, only statistics for the specified domains are included; omit to include all domains.")
    sending_streams: list[Literal["transactional", "bulk"]] | None = Field(default=None, validation_alias="sending_streams[]", serialization_alias="sending_streams[]", description="Optional list of sending stream types to filter results (e.g., transactional, bulk). When provided, only statistics for the specified streams are included; omit to include all streams.")
    categories: list[str] | None = Field(default=None, validation_alias="categories[]", serialization_alias="categories[]", description="Optional list of email categories to filter results (e.g., Welcome Email, Password Reset). When provided, only statistics for the specified categories are included; omit to include all categories.")
    email_service_providers: list[Literal["Google", "Yahoo", "Outlook", "Hey", "Google Workspace", "Zoho Email", "ProtonMail", "Yandex", "iCloud", "Office 365", "Amazon SES (Simple Email Service)", "Proofpoint Email Protection", "Mimecast Email Protection", "GMX.net", "Rackspace", "OVH hosted", "Linode hosted", "GoDaddy", "Symantec Email Protection", "Barracuda Email Protection", "Cisco Email Protection", "FastMail", "Naver", "Seznam", "Comcast", "Spectrum"]] | None = Field(default=None, validation_alias="email_service_providers[]", serialization_alias="email_service_providers[]", description="Optional list of email service provider names to filter results (e.g., Google, Yahoo). When provided, only statistics for the specified ESPs are included; omit to include all providers.")
class GetAccountSendingStatsByEmailServiceProvidersRequest(StrictModel):
    """Retrieve sending statistics for an account aggregated by email service providers over a specified date range. Apply optional filters by sending domain, stream type, category, or specific ESP to narrow results."""
    path: GetAccountSendingStatsByEmailServiceProvidersRequestPath
    query: GetAccountSendingStatsByEmailServiceProvidersRequestQuery

# Operation: get_account_sending_stats_by_date
class GetAccountSendingStatsByDateRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for the account whose sending statistics should be retrieved.")
class GetAccountSendingStatsByDateRequestQuery(StrictModel):
    start_date: str = Field(default=..., description="The beginning of the date range (inclusive) for which to retrieve statistics, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    end_date: str = Field(default=..., description="The end of the date range (inclusive) for which to retrieve statistics, specified in ISO 8601 date format (YYYY-MM-DD).", json_schema_extra={'format': 'date'})
    sending_domain_ids: list[int] | None = Field(default=None, validation_alias="sending_domain_ids[]", serialization_alias="sending_domain_ids[]", description="Optional list of sending domain IDs to filter results. When omitted, statistics for all sending domains are included.")
    sending_streams: list[Literal["transactional", "bulk"]] | None = Field(default=None, validation_alias="sending_streams[]", serialization_alias="sending_streams[]", description="Optional list of sending stream types (e.g., transactional, bulk) to filter results. When omitted, statistics for all sending streams are included.")
    categories: list[str] | None = Field(default=None, validation_alias="categories[]", serialization_alias="categories[]", description="Optional list of email categories (e.g., Welcome Email, Password Reset) to filter results. When omitted, statistics for all categories are included.")
    email_service_providers: list[Literal["Google", "Yahoo", "Outlook", "Hey", "Google Workspace", "Zoho Email", "ProtonMail", "Yandex", "iCloud", "Office 365", "Amazon SES (Simple Email Service)", "Proofpoint Email Protection", "Mimecast Email Protection", "GMX.net", "Rackspace", "OVH hosted", "Linode hosted", "GoDaddy", "Symantec Email Protection", "Barracuda Email Protection", "Cisco Email Protection", "FastMail", "Naver", "Seznam", "Comcast", "Spectrum"]] | None = Field(default=None, validation_alias="email_service_providers[]", serialization_alias="email_service_providers[]", description="Optional list of email service provider names (e.g., Google, Yahoo) to filter results. When omitted, statistics for all ESPs are included.")
class GetAccountSendingStatsByDateRequest(StrictModel):
    """Retrieve sending statistics for an account over a specified date range, with optional filtering by sending domains, streams, categories, and email service providers."""
    path: GetAccountSendingStatsByDateRequestPath
    query: GetAccountSendingStatsByDateRequestQuery

# Operation: list_email_logs
class ListEmailLogsRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The unique identifier for the account whose email logs you want to retrieve. Must be a positive integer.")
class ListEmailLogsRequestQuery(StrictModel):
    search_after: str | None = Field(default=None, description="Pagination cursor for fetching the next page of results. Use the message_id UUID value from the previous response's next_page_cursor field to continue pagination.", json_schema_extra={'format': 'uuid'})
    filters: EmailLogsListFilters | None = Field(default=None, description="Filter criteria to narrow results using deep object syntax (e.g., filters[field][operator] and filters[field][value]). For array values, use bracket notation (e.g., filters[field][value][]=item1). Date range filtering is supported via filters[sent_after] and filters[sent_before] using ISO 8601 format. Unknown or invalid filters are silently ignored.")
class ListEmailLogsRequest(StrictModel):
    """Retrieve a paginated list of email logs for the account, filtered by sending domains accessible to the authenticated token. Results are sorted by sent_at in descending order."""
    path: ListEmailLogsRequestPath
    query: ListEmailLogsRequestQuery | None = None

# Operation: get_email_log_message
class GetEmailLogMessageRequestPath(StrictModel):
    account_id: int = Field(default=..., description="The numeric identifier of the account that owns the email message.")
    sending_message_id: str = Field(default=..., description="The unique identifier (UUID) of the email message to retrieve from the log.", json_schema_extra={'format': 'uuid'})
class GetEmailLogMessageRequest(StrictModel):
    """Retrieve a specific email message from the account's email log by its unique message identifier. The message must belong to the specified account and an accessible sending domain."""
    path: GetEmailLogMessageRequestPath

# ============================================================================
# Component Models
# ============================================================================

class FilterCategory(PermissiveModel):
    operator: Literal["equal", "not_equal"]
    value: str | list[str]

class FilterCiContainString(PermissiveModel):
    operator: Literal["ci_contain", "ci_not_contain"] = Field(..., description="ci_* = case-insensitive")
    value: str

class FilterCiEqualString(PermissiveModel):
    operator: Literal["ci_equal", "ci_not_equal"] = Field(..., description="ci_* = case-insensitive")
    value: str | list[str]

class FilterClicksCount(PermissiveModel):
    operator: Literal["equal", "greater_than", "less_than"]
    value: int

class FilterContainString(PermissiveModel):
    operator: Literal["contain", "not_contain"]
    value: str

class FilterEmailServiceProvider(PermissiveModel):
    operator: Literal["equal", "not_equal"]
    value: str | list[str]

class FilterEmailServiceProviderResponse(RootModel[Annotated[
    FilterCiEqualString
    | FilterCiContainString,
    Field(discriminator="operator")
]]):
    pass

class FilterEmptyString(PermissiveModel):
    operator: Literal["empty", "not_empty"]

class FilterEqualString(PermissiveModel):
    operator: Literal["equal", "not_equal"]
    value: str | list[str]

class FilterClientIp(RootModel[Annotated[
    FilterEqualString
    | FilterContainString,
    Field(discriminator="operator")
]]):
    pass

class FilterEvents(PermissiveModel):
    operator: Literal["include_event", "not_include_event"]
    value: Literal["delivery", "open", "click", "bounce", "spam", "unsubscribe", "soft_bounce", "reject", "suspension"] | list[Literal["delivery", "open", "click", "bounce", "spam", "unsubscribe", "soft_bounce", "reject", "suspension"]]

class FilterFrom(RootModel[Annotated[
    FilterCiEqualString
    | FilterCiContainString,
    Field(discriminator="operator")
]]):
    pass

class FilterOpensCount(PermissiveModel):
    operator: Literal["equal", "greater_than", "less_than"]
    value: int

class FilterRecipientMx(RootModel[Annotated[
    FilterCiEqualString
    | FilterCiContainString,
    Field(discriminator="operator")
]]):
    pass

class FilterSendingDomainId(PermissiveModel):
    operator: Literal["equal", "not_equal"]
    value: int | list[int]

class FilterSendingIp(RootModel[Annotated[
    FilterEqualString
    | FilterContainString,
    Field(discriminator="operator")
]]):
    pass

class FilterSendingStream(PermissiveModel):
    operator: Literal["equal", "not_equal"]
    value: Literal["transactional", "bulk"] | list[Literal["transactional", "bulk"]]

class FilterStatus(PermissiveModel):
    operator: Literal["equal", "not_equal"]
    value: Literal["delivered", "not_delivered", "enqueued", "opted_out"] | list[Literal["delivered", "not_delivered", "enqueued", "opted_out"]]

class FilterSubject(RootModel[Annotated[
    FilterCiEqualString
    | FilterCiContainString
    | FilterEmptyString,
    Field(discriminator="operator")
]]):
    pass

class FilterTo(RootModel[Annotated[
    FilterCiEqualString
    | FilterCiContainString,
    Field(discriminator="operator")
]]):
    pass

class EmailLogsListFilters(PermissiveModel):
    """Key-value map of filter name to filter spec. Each spec has operator and optional value.
Date range uses sent_after / sent_before at top level of filters (see below).
In query params, array values use bracket notation: `filters[field][value][]=a&filters[field][value][]=b`.
"""
    sent_after: str | None = Field(None, description="Start of sent-at range (ISO 8601). Must be before or equal to sent_before.", json_schema_extra={'format': 'date-time'})
    sent_before: str | None = Field(None, description="End of sent-at range (ISO 8601). Must be after or equal to sent_after.", json_schema_extra={'format': 'date-time'})
    to: FilterTo | None = None
    from_: FilterFrom | None = Field(None, validation_alias="from", serialization_alias="from")
    subject: FilterSubject | None = None
    status: FilterStatus | None = None
    events: FilterEvents | None = None
    clicks_count: FilterClicksCount | None = None
    opens_count: FilterOpensCount | None = None
    client_ip: FilterClientIp | None = None
    sending_ip: FilterSendingIp | None = None
    email_service_provider_response: FilterEmailServiceProviderResponse | None = None
    email_service_provider: FilterEmailServiceProvider | None = None
    recipient_mx: FilterRecipientMx | None = None
    category: FilterCategory | None = None
    sending_domain_id: FilterSendingDomainId | None = None
    sending_stream: FilterSendingStream | None = None


# Rebuild models to resolve forward references (required for circular refs)
EmailLogsListFilters.model_rebuild()
FilterCategory.model_rebuild()
FilterCiContainString.model_rebuild()
FilterCiEqualString.model_rebuild()
FilterClicksCount.model_rebuild()
FilterClientIp.model_rebuild()
FilterContainString.model_rebuild()
FilterEmailServiceProvider.model_rebuild()
FilterEmailServiceProviderResponse.model_rebuild()
FilterEmptyString.model_rebuild()
FilterEqualString.model_rebuild()
FilterEvents.model_rebuild()
FilterFrom.model_rebuild()
FilterOpensCount.model_rebuild()
FilterRecipientMx.model_rebuild()
FilterSendingDomainId.model_rebuild()
FilterSendingIp.model_rebuild()
FilterSendingStream.model_rebuild()
FilterStatus.model_rebuild()
FilterSubject.model_rebuild()
FilterTo.model_rebuild()

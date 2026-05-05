"""
Apollo MCP Server - Pydantic Models

Generated: 2026-05-05 14:14:40 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "GetApiV1AccountsIdRequest",
    "GetApiV1ContactsContactIdRequest",
    "GetApiV1EmailerMessagesIdActivitiesRequest",
    "GetApiV1EmailerMessagesSearchRequest",
    "GetApiV1FieldsRequest",
    "GetApiV1NotesRequest",
    "GetApiV1OpportunitiesOpportunityIdRequest",
    "GetApiV1OpportunitiesSearchRequest",
    "GetApiV1OrganizationsEnrichRequest",
    "GetApiV1OrganizationsIdRequest",
    "GetApiV1OrganizationsOrganizationIdJobPostingsRequest",
    "GetApiV1PhoneCallsSearchRequest",
    "PatchApiV1AccountsAccountIdRequest",
    "PatchApiV1ContactsContactIdRequest",
    "PatchApiV1OpportunitiesOpportunityIdRequest",
    "PostApiV1AccountsBulkCreateRequest",
    "PostApiV1AccountsBulkUpdateRequest",
    "PostApiV1AccountsRequest",
    "PostApiV1AccountsSearchRequest",
    "PostApiV1AccountsUpdateOwnersRequest",
    "PostApiV1ContactsBulkCreateRequest",
    "PostApiV1ContactsBulkUpdateRequest",
    "PostApiV1ContactsRequest",
    "PostApiV1ContactsSearchRequest",
    "PostApiV1ContactsUpdateOwnersRequest",
    "PostApiV1ContactsUpdateStagesRequest",
    "PostApiV1EmailerCampaignsRemoveOrStopContactIdsRequest",
    "PostApiV1EmailerCampaignsSearchRequest",
    "PostApiV1EmailerCampaignsSequenceIdAbortRequest",
    "PostApiV1EmailerCampaignsSequenceIdAddContactIdsRequest",
    "PostApiV1EmailerCampaignsSequenceIdApproveRequest",
    "PostApiV1EmailerCampaignsSequenceIdArchiveRequest",
    "PostApiV1FieldsRequest",
    "PostApiV1MixedCompaniesSearchRequest",
    "PostApiV1MixedPeopleApiSearchRequest",
    "PostApiV1NewsArticlesSearchRequest",
    "PostApiV1OpportunitiesRequest",
    "PostApiV1OrganizationsBulkEnrichRequest",
    "PostApiV1PeopleBulkMatchRequest",
    "PostApiV1PeopleMatchRequest",
    "PostApiV1PhoneCallsRequest",
    "PostApiV1TasksBulkCreateRequest",
    "PostApiV1TasksRequest",
    "PostApiV1TasksSearchRequest",
    "PutApiV1PhoneCallsIdRequest",
    "PostApiV1AccountsBulkCreateBodyAccountsItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: enrich_person
class PostApiV1PeopleMatchRequestQuery(StrictModel):
    name: str | None = Field(default=None, description="The person's full name, typically first and last name separated by a space. Use this as an alternative to providing separate first_name and last_name parameters.")
    hashed_email: str | None = Field(default=None, description="The hashed email address of the person in MD5 or SHA-256 format. Use this to match against the database when you have a hashed email available.")
    domain: str | None = Field(default=None, description="The domain name of the person's employer (current or previous). Provide only the domain without www, @, or other prefixes (e.g., apollo.io).")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique Apollo ID assigned to the person in the database. Use this when you already have the Apollo identifier for direct lookup.")
    linkedin_url: str | None = Field(default=None, description="The URL to the person's LinkedIn profile. Provide the full profile URL to help identify and enrich the correct person.", json_schema_extra={'format': 'uri'})
    run_waterfall_email: bool | None = Field(default=None, description="Enable email waterfall enrichment to discover additional email addresses beyond standard matching. Set to true to activate this enrichment method.")
    run_waterfall_phone: bool | None = Field(default=None, description="Enable phone waterfall enrichment to discover additional phone numbers beyond standard matching. Set to true to activate this enrichment method.")
    reveal_personal_emails: bool | None = Field(default=None, description="Reveal the person's personal email addresses in the response. This may consume credits and will not return emails for individuals in GDPR-compliant regions. Set to true to include personal emails in enrichment results.")
    reveal_phone_number: bool | None = Field(default=None, description="Reveal all available phone numbers including mobile numbers in the response. This may consume credits and requires a webhook_url to be specified for asynchronous phone number verification results. Set to true to request phone number enrichment.")
    webhook_url: str | None = Field(default=None, description="The webhook URL where Apollo will send phone number verification results asynchronously. Required only when reveal_phone_number is set to true. Provide a valid HTTPS endpoint to receive the phone enrichment response.", json_schema_extra={'format': 'uri'})
class PostApiV1PeopleMatchRequest(StrictModel):
    """Enrich data for a single person by matching against the Apollo database. Provide identifying information such as name, email, domain, or LinkedIn profile to locate and return enriched contact details. Optionally reveal personal emails and phone numbers, or enable waterfall enrichment for additional data discovery."""
    query: PostApiV1PeopleMatchRequestQuery | None = None

# Operation: enrich_people_bulk
class PostApiV1PeopleBulkMatchRequestQuery(StrictModel):
    run_waterfall_email: bool | None = Field(default=None, description="Enable email waterfall enrichment to progressively search multiple data sources for email addresses when initial matches don't return results.")
    run_waterfall_phone: bool | None = Field(default=None, description="Enable phone waterfall enrichment to progressively search multiple data sources for phone numbers when initial matches don't return results.")
    reveal_personal_emails: bool | None = Field(default=None, description="Include personal email addresses in enriched results for all matched people. This may consume credits based on your plan. Personal emails will not be revealed for people in GDPR-compliant regions.")
    reveal_phone_number: bool | None = Field(default=None, description="Include all available phone numbers (including mobile) in enriched results for matched people. Requires a valid webhook_url to receive asynchronous phone verification results.")
    webhook_url: str | None = Field(default=None, description="Webhook endpoint URL where Apollo will send phone number verification results asynchronously. Required when reveal_phone_number is enabled. Must be a valid HTTPS or HTTP URI.", json_schema_extra={'format': 'uri'})
class PostApiV1PeopleBulkMatchRequestBody(StrictModel):
    details: list[dict[str, Any]] = Field(default=..., description="Array of up to 10 person objects containing identifying information (name, email, company, location, etc.) to match and enrich. Each object should include available details to improve match accuracy.")
class PostApiV1PeopleBulkMatchRequest(StrictModel):
    """Enrich contact and professional data for up to 10 people in a single request. Apollo uses the provided person details to identify and match records, then returns enriched information with optional email, phone, and waterfall verification."""
    query: PostApiV1PeopleBulkMatchRequestQuery | None = None
    body: PostApiV1PeopleBulkMatchRequestBody

# Operation: enrich_organization
class GetApiV1OrganizationsEnrichRequestQuery(StrictModel):
    domain: str = Field(default=..., description="The company domain to enrich (e.g., apollo.io). Provide the domain without www prefix, @ symbol, or other special characters.")
class GetApiV1OrganizationsEnrichRequest(StrictModel):
    """Enrich company data by domain to retrieve detailed organizational information including industry, revenue, employee counts, funding details, and contact information. Each call consumes credits from your Apollo pricing plan."""
    query: GetApiV1OrganizationsEnrichRequestQuery

# Operation: enrich_organizations
class PostApiV1OrganizationsBulkEnrichRequestQuery(StrictModel):
    domains: list[str] = Field(default=..., validation_alias="domains[]", serialization_alias="domains[]", description="Array of company domains to enrich, up to 10 domains per request. Provide domains without www prefix, @ symbol, or other modifiers (e.g., apollo.io, microsoft.com).")
class PostApiV1OrganizationsBulkEnrichRequest(StrictModel):
    """Enrich company data for up to 10 organizations in a single request. Returns enriched information including industry, revenue, employee count, funding details, phone numbers, and locations."""
    query: PostApiV1OrganizationsBulkEnrichRequestQuery

# Operation: search_people
class PostApiV1MixedPeopleApiSearchRequestQuery(StrictModel):
    person_titles: list[str] | None = Field(default=None, validation_alias="person_titles[]", serialization_alias="person_titles[]", description="Filter by job titles held by people. Results include titles containing the same terms, even if not exact matches.")
    q_keywords: str | None = Field(default=None, description="Filter results by keywords that appear in person profiles.")
    person_locations: list[str] | None = Field(default=None, validation_alias="person_locations[]", serialization_alias="person_locations[]", description="Filter by the locations where people currently live, including cities, US states, and countries.")
    person_seniorities: list[Literal["owner", "founder", "c_suite", "partner", "vp", "head", "director", "manager", "senior", "entry", "intern"]] | None = Field(default=None, validation_alias="person_seniorities[]", serialization_alias="person_seniorities[]", description="Filter by the seniority level of people's current job positions (e.g., entry-level, mid-level, executive).")
    organization_locations: list[str] | None = Field(default=None, validation_alias="organization_locations[]", serialization_alias="organization_locations[]", description="Filter by the headquarters location of people's current employers, including cities, US states, and countries.")
    q_organization_domains_list: list[str] | None = Field(default=None, validation_alias="q_organization_domains_list[]", serialization_alias="q_organization_domains_list[]", description="Filter by employer domain names. Accepts up to 1,000 domains per request.")
    contact_email_status: list[Literal["verified", "unverified", "likely to engage", "unavailable"]] | None = Field(default=None, validation_alias="contact_email_status[]", serialization_alias="contact_email_status[]", description="Filter by email verification status of people (e.g., verified, unverified, bounced).")
    organization_ids: list[str] | None = Field(default=None, validation_alias="organization_ids[]", serialization_alias="organization_ids[]", description="Filter by Apollo organization IDs to include only people employed at specific companies.")
    organization_num_employees_ranges: list[str] | None = Field(default=None, validation_alias="organization_num_employees_ranges[]", serialization_alias="organization_num_employees_ranges[]", description="Filter by employee count ranges of people's current employers. Specify as comma-separated lower and upper bounds (e.g., '1,10' for 1-10 employees).")
    currently_using_all_of_technology_uids: list[str] | None = Field(default=None, validation_alias="currently_using_all_of_technology_uids[]", serialization_alias="currently_using_all_of_technology_uids[]", description="Filter by people whose employers use all of the specified technologies. Supports 1,500+ technology identifiers.")
    currently_using_any_of_technology_uids: list[str] | None = Field(default=None, validation_alias="currently_using_any_of_technology_uids[]", serialization_alias="currently_using_any_of_technology_uids[]", description="Filter by people whose employers use any of the specified technologies. Supports 1,500+ technology identifiers.")
    currently_not_using_any_of_technology_uids: list[str] | None = Field(default=None, validation_alias="currently_not_using_any_of_technology_uids[]", serialization_alias="currently_not_using_any_of_technology_uids[]", description="Exclude people whose employers use any of the specified technologies. Supports 1,500+ technology identifiers.")
    q_organization_job_titles: list[str] | None = Field(default=None, validation_alias="q_organization_job_titles[]", serialization_alias="q_organization_job_titles[]", description="Filter by job titles listed in active job postings at people's current employers.")
    organization_job_locations: list[str] | None = Field(default=None, validation_alias="organization_job_locations[]", serialization_alias="organization_job_locations[]", description="Filter by locations where people's current employers are actively recruiting for open positions.")
class PostApiV1MixedPeopleApiSearchRequest(StrictModel):
    """Search the Apollo database for people matching specified criteria such as job title, location, seniority, and employer technology stack. This API-optimized endpoint does not consume credits and returns up to 50,000 records without email addresses or phone numbers."""
    query: PostApiV1MixedPeopleApiSearchRequestQuery | None = None

# Operation: search_companies
class PostApiV1MixedCompaniesSearchRequestQuery(StrictModel):
    q_organization_domains_list: list[str] | None = Field(default=None, validation_alias="q_organization_domains_list[]", serialization_alias="q_organization_domains_list[]", description="Filter by company domain names (e.g., apollo.io, microsoft.com). Omit www, @, and similar prefixes. Accepts up to 1,000 domains per request to find companies by their current or previous employer domains.")
    organization_num_employees_ranges: list[str] | None = Field(default=None, validation_alias="organization_num_employees_ranges[]", serialization_alias="organization_num_employees_ranges[]", description="Filter by company headcount ranges. Specify ranges as comma-separated pairs (e.g., 1,10 or 250,500). Add multiple ranges to broaden results and find companies within specific employee count brackets.")
    organization_locations: list[str] | None = Field(default=None, validation_alias="organization_locations[]", serialization_alias="organization_locations[]", description="Filter by company headquarters location using city, US state, or country names. Results are based on headquarters location even if the company has multiple offices.")
    organization_not_locations: list[str] | None = Field(default=None, validation_alias="organization_not_locations[]", serialization_alias="organization_not_locations[]", description="Exclude companies from results based on headquarters location. Specify cities, US states, or countries to filter out unwanted geographic regions.")
    currently_using_any_of_technology_uids: list[str] | None = Field(default=None, validation_alias="currently_using_any_of_technology_uids[]", serialization_alias="currently_using_any_of_technology_uids[]", description="Filter by technologies currently in use at companies. Apollo supports 1,500+ technologies; use underscores to replace spaces and periods in technology names (e.g., google_analytics, wordpress_org).")
    q_organization_keyword_tags: list[str] | None = Field(default=None, validation_alias="q_organization_keyword_tags[]", serialization_alias="q_organization_keyword_tags[]", description="Filter by industry or business keywords associated with companies (e.g., mining, consulting). Enables targeted searches by company classification or sector.")
    q_organization_name: str | None = Field(default=None, description="Filter by specific company name. Partial name matches are supported to find companies with similar naming patterns.")
    organization_ids: list[str] | None = Field(default=None, validation_alias="organization_ids[]", serialization_alias="organization_ids[]", description="Filter by Apollo's unique company identifiers. Provide one or more company IDs to retrieve specific organizations from the database.")
    q_organization_job_titles: list[str] | None = Field(default=None, validation_alias="q_organization_job_titles[]", serialization_alias="q_organization_job_titles[]", description="Filter by job titles listed in active company job postings. Find companies actively recruiting for specific roles (e.g., sales manager, research analyst).")
    organization_job_locations: list[str] | None = Field(default=None, validation_alias="organization_job_locations[]", serialization_alias="organization_job_locations[]", description="Filter by geographic locations where companies are actively recruiting. Specify cities or countries to find organizations hiring in particular regions.")
class PostApiV1MixedCompaniesSearchRequest(StrictModel):
    """Search the Apollo database for companies using multiple filter criteria including domain, location, technology stack, and hiring activity. Results are paginated at 100 records per page (up to 500 pages, 50,000 record limit) and consume credits based on your Apollo plan."""
    query: PostApiV1MixedCompaniesSearchRequestQuery | None = None

# Operation: list_organization_job_postings
class GetApiV1OrganizationsOrganizationIdJobPostingsRequestPath(StrictModel):
    organization_id: str = Field(default=..., description="The unique identifier for the organization whose job postings you want to retrieve. You can find organization IDs by calling the Organization Search endpoint.")
class GetApiV1OrganizationsOrganizationIdJobPostingsRequest(StrictModel):
    """Retrieve current job postings for a specific organization to identify companies expanding headcount in strategically important areas. This endpoint is useful for competitive intelligence and hiring trend analysis."""
    path: GetApiV1OrganizationsOrganizationIdJobPostingsRequestPath

# Operation: get_organization
class GetApiV1OrganizationsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The Apollo organization ID to retrieve details for. You can find organization IDs by calling the Organization Search endpoint and extracting the organization_id value from the results.")
class GetApiV1OrganizationsIdRequest(StrictModel):
    """Retrieve complete details about a specific organization from the Apollo database, including company information, contact data, and other organizational metadata. Requires a master API key for authentication."""
    path: GetApiV1OrganizationsIdRequestPath

# Operation: search_company_news
class PostApiV1NewsArticlesSearchRequestQuery(StrictModel):
    organization_ids: list[str] = Field(default=..., validation_alias="organization_ids[]", serialization_alias="organization_ids[]", description="One or more Apollo company IDs to search for news coverage. Retrieve company IDs from the Organization Search endpoint. Results will include news for all specified companies.")
    categories: list[str] | None = Field(default=None, validation_alias="categories[]", serialization_alias="categories[]", description="Optional news categories or sub-categories to filter results (e.g., hires, investment, contract). When specified, only articles matching these categories are returned. Omit to include all available categories.")
class PostApiV1NewsArticlesSearchRequest(StrictModel):
    """Search for news articles related to companies in the Apollo database. Filter results by company IDs and optionally by news categories to find relevant coverage. Note: This operation consumes credits from your Apollo plan."""
    query: PostApiV1NewsArticlesSearchRequestQuery

# Operation: create_account
class PostApiV1AccountsRequestBody(StrictModel):
    name: str = Field(default=..., description="The human-readable name of the account/company you are creating.")
    domain: str = Field(default=..., description="The domain name for the account, without www or similar prefixes (e.g., apollo.io).")
    owner_id: str | None = Field(default=None, description="The Apollo user ID of the team member who will own this account.")
    account_stage_id: str | None = Field(default=None, description="The Apollo ID of the account stage (pipeline status) to assign to this account.")
    phone: str | None = Field(default=None, description="The primary phone number for the account. Apollo automatically formats phone numbers regardless of input format.")
    raw_address: str | None = Field(default=None, description="The corporate headquarters location for the account, which may include city, state, and country.")
    typed_custom_fields: dict[str, Any] | None = Field(default=None, description="Custom field values specific to your team's Apollo account, provided as key-value pairs where keys are custom field IDs and values are the field data.")
class PostApiV1AccountsRequest(StrictModel):
    """Create a new account (company) in your Apollo team database. Note that Apollo does not deduplicate accounts, so creating an account with the same name, domain, or details as an existing account will result in a duplicate entry rather than an update. Requires a master API key."""
    body: PostApiV1AccountsRequestBody

# Operation: update_account
class PatchApiV1AccountsAccountIdRequestPath(StrictModel):
    account_id: str = Field(default=..., description="The unique Apollo identifier for the account to update.")
class PatchApiV1AccountsAccountIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable name for the account (e.g., 'The Fast Irish Copywriters').")
    domain: str | None = Field(default=None, description="The domain name associated with the account, without www or protocol prefix (e.g., 'apollo.io' or 'microsoft.com').")
    owner_id: str | None = Field(default=None, description="The Apollo ID of the team member who owns this account.")
    account_stage_id: str | None = Field(default=None, description="The Apollo ID of the account stage to assign to this account, determining its position in your sales pipeline.")
    raw_address: str | None = Field(default=None, description="The corporate headquarters location or primary office address (e.g., 'Belfield, Dublin 4, Ireland' or 'Dallas, United States').")
    phone: str | None = Field(default=None, description="The primary contact phone number for the account in any standard format (e.g., '555-303-1234' or '+44 7911 123456').")
    typed_custom_fields: dict[str, Any] | None = Field(default=None, description="Custom field values specific to your Apollo workspace. Structure as key-value pairs where keys match your configured custom field names.")
class PatchApiV1AccountsAccountIdRequest(StrictModel):
    """Update an existing account in your Apollo workspace. Requires a master API key and the account ID. You can modify account details such as name, domain, owner, stage, location, phone, and custom fields."""
    path: PatchApiV1AccountsAccountIdRequestPath
    body: PatchApiV1AccountsAccountIdRequestBody | None = None

# Operation: bulk_create_accounts
class PostApiV1AccountsBulkCreateRequestBody(StrictModel):
    accounts: list[PostApiV1AccountsBulkCreateBodyAccountsItem] = Field(default=..., description="Array of account objects to create, up to 100 accounts per request. Each object should contain the account attributes you want to set.")
    append_label_names: list[str] | None = Field(default=None, description="Optional array of label names to apply to all accounts created in this request.")
    run_dedupe: bool | None = Field(default=None, description="Enable aggressive deduplication matching by domain, organization_id, and name in addition to CRM IDs. When disabled (default), only CRM ID matching is used. Existing accounts are returned without modification regardless of this setting.")
class PostApiV1AccountsBulkCreateRequest(StrictModel):
    """Create up to 100 accounts in a single request with intelligent deduplication. The endpoint returns newly created accounts and existing matches separately without modifying existing accounts."""
    body: PostApiV1AccountsBulkCreateRequestBody

# Operation: bulk_update_accounts
class PostApiV1AccountsBulkUpdateRequestBody(StrictModel):
    account_ids: list[str] | None = Field(default=None, description="List of account IDs to update with identical values. Use this when applying the same changes across multiple accounts. Required if account_attributes is not provided.")
    account_attributes: list[dict[str, Any]] | None = Field(default=None, description="List of account objects, each containing an ID and the specific fields to update for that account. Use this for applying different updates to individual accounts. Required if account_ids is not provided. Not compatible with async processing.")
    name: str | None = Field(default=None, description="New name to assign to all accounts when using account_ids. Ignored when using account_attributes.")
    owner_id: str | None = Field(default=None, description="Owner ID to assign to all accounts when using account_ids. Ignored when using account_attributes.")
    account_stage_id: str | None = Field(default=None, description="Account stage ID to assign to all accounts when using account_ids. Ignored when using account_attributes.")
    async_: bool | None = Field(default=None, validation_alias="async", serialization_alias="async", description="Enable asynchronous processing for the bulk update. Only available when using account_ids with uniform updates; will fail if used with account_attributes. Defaults to false for synchronous processing.")
class PostApiV1AccountsBulkUpdateRequest(StrictModel):
    """Update multiple accounts simultaneously with common or individual field changes. Supports updating up to 1000 accounts per request, with optional asynchronous processing when applying uniform updates."""
    body: PostApiV1AccountsBulkUpdateRequestBody | None = None

# Operation: search_accounts
class PostApiV1AccountsSearchRequestBody(StrictModel):
    q_organization_name: str | None = Field(default=None, description="Keywords to filter accounts by name. The search matches keywords against account names, supporting partial matches. Examples include company names like 'apollo', 'microsoft', or 'marketing'.")
    account_stage_ids: list[str] | None = Field(default=None, description="Apollo IDs of account stages to include in results. Provide as an array of stage IDs to filter accounts by their current stage.")
    account_label_ids: list[str] | None = Field(default=None, description="Apollo IDs of labels to include in results. Provide as an array of label IDs to filter accounts by their assigned labels.")
    sort_by_field: Literal["account_last_activity_date", "account_created_at", "account_updated_at"] | None = Field(default=None, description="Field to sort results by. Choose from account activity date, creation date, or last update date.")
    sort_ascending: bool | None = Field(default=None, description="Sort results in ascending order. Only applies when sort_by_field is specified. Defaults to descending order when not provided.")
class PostApiV1AccountsSearchRequest(StrictModel):
    """Search for accounts that have been added to your team's Apollo database. Filter by name, stage, labels, and sort results by activity or creation date. Results are paginated with a maximum of 50,000 records (100 per page)."""
    body: PostApiV1AccountsSearchRequestBody | None = None

# Operation: get_account
class GetApiV1AccountsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The Apollo ID of the account to retrieve. You can find account IDs by calling the Search for Accounts endpoint.")
class GetApiV1AccountsIdRequest(StrictModel):
    """Retrieve detailed information for a specific account (company) in your Apollo database. Requires a master API key."""
    path: GetApiV1AccountsIdRequestPath

# Operation: assign_accounts_to_owner
class PostApiV1AccountsUpdateOwnersRequestQuery(StrictModel):
    account_ids: list[str] = Field(default=..., validation_alias="account_ids[]", serialization_alias="account_ids[]", description="Array of Apollo account IDs to reassign to the new owner. Retrieve account IDs from the Search for Accounts endpoint. Each ID should be a valid Apollo account identifier.")
    owner_id: str = Field(default=..., description="The Apollo user ID of the team member who will become the owner of the specified accounts. Retrieve available user IDs from the Get a List of Users endpoint.")
class PostApiV1AccountsUpdateOwnersRequest(StrictModel):
    """Assign multiple accounts to a different owner within your team's Apollo account. This operation requires a master API key and allows bulk reassignment of account ownership."""
    query: PostApiV1AccountsUpdateOwnersRequestQuery

# Operation: create_contact
class PostApiV1ContactsRequestBody(StrictModel):
    title: str | None = Field(default=None, description="The contact's current job title (e.g., 'senior research analyst').")
    account_id: str | None = Field(default=None, description="The Apollo ID of the account to associate with this contact.")
    website_url: str | None = Field(default=None, description="The corporate website URL in URI format (e.g., https://example.com).", json_schema_extra={'format': 'uri'})
    label_names: list[str] | None = Field(default=None, description="An array of list names to which this contact should be added.")
    contact_stage_id: str | None = Field(default=None, description="The Apollo ID of the contact stage to assign to this contact.")
    present_raw_address: str | None = Field(default=None, description="The contact's personal location or address (e.g., 'Atlanta, United States').")
    typed_custom_fields: dict[str, Any] | None = Field(default=None, description="An object containing custom field data specific to your Apollo account. Field names and values should match your team's configured custom fields.")
    run_dedupe: bool | None = Field(default=None, description="Set to true to enable deduplication logic that prevents creating duplicate contacts. Defaults to false.")
class PostApiV1ContactsRequest(StrictModel):
    """Add a new contact to your Apollo account. By default, deduplication is disabled; enable it by setting `run_dedupe` to true to prevent creating duplicate contacts."""
    body: PostApiV1ContactsRequestBody | None = None

# Operation: get_contact
class GetApiV1ContactsContactIdRequestPath(StrictModel):
    contact_id: str = Field(default=..., description="The unique Apollo identifier for the contact you want to retrieve. You can find contact IDs by using the search contacts endpoint.")
class GetApiV1ContactsContactIdRequest(StrictModel):
    """Retrieve detailed information for a specific contact in your Apollo database. This endpoint returns enriched contact data including email addresses, phone numbers, and other profile information."""
    path: GetApiV1ContactsContactIdRequestPath

# Operation: update_contact
class PatchApiV1ContactsContactIdRequestPath(StrictModel):
    contact_id: str = Field(default=..., description="The Apollo ID of the contact to update. Retrieve contact IDs using the Search for Contacts endpoint.")
class PatchApiV1ContactsContactIdRequestBody(StrictModel):
    title: str | None = Field(default=None, description="The contact's job title (e.g., 'senior research analyst').")
    account_id: str | None = Field(default=None, description="The Apollo account ID to associate with this contact.")
    website_url: str | None = Field(default=None, description="The employer's website URL in standard URI format (e.g., https://www.apollo.io/).", json_schema_extra={'format': 'uri'})
    label_names: list[str] | None = Field(default=None, description="List of label names to assign to this contact. Providing new values will completely replace any existing list assignments.")
    contact_stage_id: str | None = Field(default=None, description="The contact stage ID to update the contact's pipeline stage.")
    present_raw_address: str | None = Field(default=None, description="The contact's location as a city/state/country string (e.g., 'Atlanta, United States').")
    typed_custom_fields: dict[str, Any] | None = Field(default=None, description="Custom field data specific to your Apollo account. Provide as key-value pairs where keys match your team's custom field identifiers.")
class PatchApiV1ContactsContactIdRequest(StrictModel):
    """Update an existing contact in your Apollo account. Modify contact details such as job title, account association, location, stage, and custom fields. List assignments are replaced entirely when provided."""
    path: PatchApiV1ContactsContactIdRequestPath
    body: PatchApiV1ContactsContactIdRequestBody | None = None

# Operation: bulk_create_contacts
class PostApiV1ContactsBulkCreateRequestBody(StrictModel):
    contacts: list[dict[str, Any]] = Field(default=..., description="Array of contact objects to create. Maximum of 100 contacts per request. Order is preserved in the response.")
    append_label_names: list[str] | None = Field(default=None, description="Optional array of label names to apply to all contacts created in this request.")
    run_dedupe: bool | None = Field(default=None, description="Enable intelligent deduplication across all data sources by matching on email, CRM IDs, or name plus organization. When disabled (default), duplicates are created for non-email import sources while email import placeholders are still merged. When enabled, existing contacts are returned without modification except for email import placeholder merging.")
class PostApiV1ContactsBulkCreateRequest(StrictModel):
    """Create up to 100 contacts in a single request with optional deduplication and bulk label assignment. The endpoint intelligently separates newly created contacts from existing ones in the response."""
    body: PostApiV1ContactsBulkCreateRequestBody

# Operation: bulk_update_contacts
class PostApiV1ContactsBulkUpdateRequestBody(StrictModel):
    contact_ids: list[str] = Field(default=..., description="List of contact IDs to update. All contacts in this list will receive the same field updates.")
    owner_id: str | None = Field(default=None, description="ID of the user to assign as owner for all specified contacts.")
    title: str | None = Field(default=None, description="Job title to apply to all specified contacts.")
    account_id: str | None = Field(default=None, description="Account ID to associate with all specified contacts.")
    present_raw_address: str | None = Field(default=None, description="Physical address to apply to all specified contacts.")
    linkedin_url: str | None = Field(default=None, description="LinkedIn profile URL for all specified contacts. Must be a valid URI format.", json_schema_extra={'format': 'uri'})
    typed_custom_fields: dict[str, Any] | None = Field(default=None, description="Custom field key-value pairs to apply to all specified contacts. Structure as an object with field names as keys.")
    async_: bool | None = Field(default=None, validation_alias="async", serialization_alias="async", description="Force asynchronous processing of the update request. Automatically enabled when updating more than 100 contacts. Defaults to false for smaller batches.")
class PostApiV1ContactsBulkUpdateRequest(StrictModel):
    """Update multiple contacts simultaneously with common field values. Supports updating up to 100 contacts per request, with automatic asynchronous processing for larger batches."""
    body: PostApiV1ContactsBulkUpdateRequestBody

# Operation: search_contacts
class PostApiV1ContactsSearchRequestBody(StrictModel):
    q_keywords: str | None = Field(default=None, description="Keywords to filter contacts by name, job title, employer, or email address. Supports multiple search terms combined together.")
    contact_stage_ids: list[str] | None = Field(default=None, description="Apollo IDs of contact stages to include in the search results. Provide as an array of stage IDs to filter by one or more stages.")
    contact_label_ids: list[str] | None = Field(default=None, description="Apollo IDs of labels to include in the search results. Provide as an array of label IDs to filter by one or more labels.")
    sort_by_field: dict | None = Field(default=None, description="Sort the matching contacts by one of the following options: contact_last_activity_date, contact_email_last_opened_at, contact_email_last_clicked_at, contact_created_at, contact_updated_at")
    sort_ascending: bool | None = Field(default=None, description="Set to true to sort the matching contacts in ascending order. Must be used with sort_by_field.")
class PostApiV1ContactsSearchRequest(StrictModel):
    """Search for contacts in your team's Apollo account by keywords, stage, or labels. Results are paginated with a maximum of 100 records per page, up to 500 pages (50,000 total records)."""
    body: PostApiV1ContactsSearchRequestBody | None = None

# Operation: update_contact_stages
class PostApiV1ContactsUpdateStagesRequestQuery(StrictModel):
    contact_ids: list[str] = Field(default=..., validation_alias="contact_ids[]", serialization_alias="contact_ids[]", description="Array of Apollo contact IDs to update. Retrieve contact IDs from the Search for Contacts endpoint. All specified contacts will be assigned to the same target stage.")
    contact_stage_id: str = Field(default=..., description="The Apollo ID of the contact stage to assign to the specified contacts. Retrieve available stage IDs from the List Contact Stages endpoint.")
class PostApiV1ContactsUpdateStagesRequest(StrictModel):
    """Update the stage assignment for multiple contacts in your Apollo account. Specify the contacts to update and the target stage they should be assigned to."""
    query: PostApiV1ContactsUpdateStagesRequestQuery

# Operation: assign_contacts_to_owner
class PostApiV1ContactsUpdateOwnersRequestQuery(StrictModel):
    contact_ids: list[str] = Field(default=..., description="Array of Apollo contact IDs to reassign. Retrieve contact IDs from the Search for Contacts endpoint by identifying the `id` field for each contact you want to update.")
    owner_id: str = Field(default=..., description="The Apollo user ID of the team member who will become the owner of the specified contacts. Retrieve available user IDs from the Get a List of Users endpoint.")
class PostApiV1ContactsUpdateOwnersRequest(StrictModel):
    """Reassign multiple contacts to a different owner within your Apollo account. This operation allows you to bulk update contact ownership across your team."""
    query: PostApiV1ContactsUpdateOwnersRequestQuery

# Operation: create_deal
class PostApiV1OpportunitiesRequestBody(StrictModel):
    name: str = Field(default=..., description="A human-readable name for the deal (e.g., 'Massive Q3 Deal').")
    owner_id: str | None = Field(default=None, description="The ID of the team member who owns this deal within your Apollo account.")
    account_id: str | None = Field(default=None, description="The ID of the target company account within your Apollo instance that this deal is associated with.")
    amount: str | None = Field(default=None, description="The monetary value of the deal as a numeric amount. Enter only digits without commas or currency symbols.")
    opportunity_stage_id: str | None = Field(default=None, description="The ID of the deal stage (pipeline stage) within your Apollo account that categorizes this deal's progress.")
    closed_date: str | None = Field(default=None, description="The estimated close date for the deal in YYYY-MM-DD format. Can be a future or past date.", json_schema_extra={'format': 'date'})
    typed_custom_fields: dict[str, Any] | None = Field(default=None, description="Custom field data specific to your Apollo account. Structure and available fields depend on your team's custom field configuration.")
class PostApiV1OpportunitiesRequest(StrictModel):
    """Create a new deal in your Apollo account to track account activity, including deal value, ownership, and pipeline stage. Requires a master API key."""
    body: PostApiV1OpportunitiesRequestBody

# Operation: list_opportunities
class GetApiV1OpportunitiesSearchRequestQuery(StrictModel):
    sort_by_field: Literal["amount", "is_closed", "is_won"] | None = Field(default=None, description="Sort results by one of three criteria: amount (largest deal values first), is_closed (closed deals first), or is_won (won deals first). If not specified, results are returned in default order.")
class GetApiV1OpportunitiesSearchRequest(StrictModel):
    """Retrieve all deals created in your Apollo account. This endpoint requires a master API key and returns a complete list of opportunities for your team."""
    query: GetApiV1OpportunitiesSearchRequestQuery | None = None

# Operation: get_deal
class GetApiV1OpportunitiesOpportunityIdRequestPath(StrictModel):
    opportunity_id: str = Field(default=..., description="The unique identifier for the deal you want to retrieve. Use the List All Deals endpoint to find the ID of the desired deal.")
class GetApiV1OpportunitiesOpportunityIdRequest(StrictModel):
    """Retrieve complete details about a specific deal in your Apollo account, including deal owner, monetary value, stage, and associated account information. Requires a master API key."""
    path: GetApiV1OpportunitiesOpportunityIdRequestPath

# Operation: update_opportunity
class PatchApiV1OpportunitiesOpportunityIdRequestPath(StrictModel):
    opportunity_id: str = Field(default=..., description="The unique identifier of the deal to update.")
class PatchApiV1OpportunitiesOpportunityIdRequestBody(StrictModel):
    owner_id: str | None = Field(default=None, description="The user ID of the deal owner within your team. Retrieve available user IDs from the Get a List of Users endpoint.")
    name: str | None = Field(default=None, description="A human-readable name for the deal.")
    amount: str | None = Field(default=None, description="The monetary value of the deal as a numeric string without commas or currency symbols. The currency is determined by your Apollo account settings.")
    opportunity_stage_id: str | None = Field(default=None, description="The ID of the deal stage for this opportunity. Retrieve available stage IDs from the List Deal Stages endpoint.")
    closed_date: str | None = Field(default=None, description="The estimated close date for the deal in YYYY-MM-DD format.", json_schema_extra={'format': 'date'})
    typed_custom_fields: dict[str, Any] | None = Field(default=None, description="Custom field values specific to your team's Apollo account. Use the Get a List of All Custom Fields endpoint to identify field IDs and their required data types.")
class PatchApiV1OpportunitiesOpportunityIdRequest(StrictModel):
    """Update an existing deal in your Apollo account. Modify deal details such as name, monetary value, owner, stage, and close date to keep your pipeline current."""
    path: PatchApiV1OpportunitiesOpportunityIdRequestPath
    body: PatchApiV1OpportunitiesOpportunityIdRequestBody | None = None

# Operation: search_sequences
class PostApiV1EmailerCampaignsSearchRequestQuery(StrictModel):
    q_name: str | None = Field(default=None, description="Keywords to filter sequences by name. The search will match sequences whose names contain any of the provided keywords.")
class PostApiV1EmailerCampaignsSearchRequest(StrictModel):
    """Search for email sequences in your Apollo account by name. This endpoint requires a master API key and returns sequences matching your search criteria."""
    query: PostApiV1EmailerCampaignsSearchRequestQuery | None = None

# Operation: add_contacts_to_sequence
class PostApiV1EmailerCampaignsSequenceIdAddContactIdsRequestPath(StrictModel):
    sequence_id: str = Field(default=..., description="The Apollo ID of the sequence to add contacts to. Retrieve sequence IDs using the Search for Sequences endpoint.")
class PostApiV1EmailerCampaignsSequenceIdAddContactIdsRequestQuery(StrictModel):
    emailer_campaign_id: str = Field(default=..., description="The Apollo ID of the emailer campaign, which must match the sequence_id value.")
    contact_ids: list[str] | None = Field(default=None, validation_alias="contact_ids[]", serialization_alias="contact_ids[]", description="Array of Apollo contact IDs to add to the sequence. Retrieve contact IDs using the Search for Contacts endpoint. Either this or label_names[] must be provided.")
    label_names: list[str] | None = Field(default=None, validation_alias="label_names[]", serialization_alias="label_names[]", description="Array of label names to identify contacts for addition to the sequence. Contacts matching any of these labels will be added. Either this or contact_ids[] must be provided.")
    send_email_from_email_account_id: str = Field(default=..., description="The Apollo ID of the email account to use for sending emails to added contacts. Retrieve email account IDs using the Get a List of Email Accounts endpoint.")
    send_email_from_email_address: str | None = Field(default=None, description="Optional specific email address within the selected email account to send from.")
    sequence_no_email: bool | None = Field(default=None, description="Set to true to add contacts to the sequence even if they lack an email address. Defaults to false.")
    sequence_unverified_email: bool | None = Field(default=None, description="Set to true to add contacts with unverified email addresses to the sequence. Defaults to false.")
    sequence_job_change: bool | None = Field(default=None, description="Set to true to add contacts to the sequence even if they have recently changed jobs. Defaults to false.")
    sequence_active_in_other_campaigns: bool | None = Field(default=None, description="Set to true to add contacts to the sequence even if they are already active in other sequences. Defaults to false.")
    sequence_finished_in_other_campaigns: bool | None = Field(default=None, description="Set to true to add contacts to the sequence if they have previously completed another sequence. Defaults to false.")
    sequence_same_company_in_same_campaign: bool | None = Field(default=None, description="Set to true to add contacts to the sequence even if other contacts from the same company are already enrolled. Defaults to false.")
    contacts_without_ownership_permission: bool | None = Field(default=None, description="Set to true to add contacts to the sequence even if you lack ownership permissions for them. Defaults to false.")
    add_if_in_queue: bool | None = Field(default=None, description="Set to true to add contacts to the sequence even if they are currently queued for processing. Defaults to false.")
    contact_verification_skipped: bool | None = Field(default=None, description="Set to true to skip contact verification during the addition process. Defaults to false.")
    user_id: str | None = Field(default=None, description="The Apollo user ID of the team member performing this action. This user will be recorded in the activity log. Retrieve user IDs using the Get a List of Users endpoint.")
    status: Literal["active", "paused"] | None = Field(default=None, description="Initial enrollment status for added contacts. Use 'paused' with auto_unpause_at to schedule contact addition. Valid values are 'active' or 'paused'.")
    auto_unpause_at: str | None = Field(default=None, description="ISO 8601 datetime when paused contacts should automatically resume. Must be used together with status set to 'paused'.", json_schema_extra={'format': 'date-time'})
class PostApiV1EmailerCampaignsSequenceIdAddContactIdsRequest(StrictModel):
    """Add contacts to an email sequence in your Apollo account. Contacts can be specified by individual IDs or by label names. Requires a master API key and a valid email account to send from."""
    path: PostApiV1EmailerCampaignsSequenceIdAddContactIdsRequestPath
    query: PostApiV1EmailerCampaignsSequenceIdAddContactIdsRequestQuery

# Operation: update_sequence_contact_status
class PostApiV1EmailerCampaignsRemoveOrStopContactIdsRequestQuery(StrictModel):
    emailer_campaign_ids: list[str] = Field(default=..., validation_alias="emailer_campaign_ids[]", serialization_alias="emailer_campaign_ids[]", description="One or more Apollo sequence IDs to update. When multiple sequences are specified, the contact status change applies across all selected sequences.")
    contact_ids: list[str] = Field(default=..., validation_alias="contact_ids[]", serialization_alias="contact_ids[]", description="One or more Apollo contact IDs whose sequence status should be updated. These contacts must exist within the specified sequences.")
    mode: Literal["mark_as_finished", "remove", "stop"] = Field(default=..., description="The action to perform on the contacts: mark_as_finished to indicate sequence completion, remove to delete contacts from the sequence, or stop to pause their progress.")
class PostApiV1EmailerCampaignsRemoveOrStopContactIdsRequest(StrictModel):
    """Update the status of contacts within email sequences by marking them as finished, removing them entirely, or stopping their progress. Requires a master API key."""
    query: PostApiV1EmailerCampaignsRemoveOrStopContactIdsRequestQuery

# Operation: activate_email_sequence
class PostApiV1EmailerCampaignsSequenceIdApproveRequestPath(StrictModel):
    sequence_id: str = Field(default=..., description="The Apollo ID of the email sequence to activate. Retrieve sequence IDs by calling the Search for Sequences endpoint.")
class PostApiV1EmailerCampaignsSequenceIdApproveRequest(StrictModel):
    """Activate an inactive email sequence to begin sending emails to its contacts on the configured schedule. The sequence must have at least one step configured before activation."""
    path: PostApiV1EmailerCampaignsSequenceIdApproveRequestPath

# Operation: abort_email_sequence
class PostApiV1EmailerCampaignsSequenceIdAbortRequestPath(StrictModel):
    sequence_id: str = Field(default=..., description="The unique Apollo identifier for the email sequence you want to abort. This is a 24-character hexadecimal string that uniquely identifies the sequence in the system.")
class PostApiV1EmailerCampaignsSequenceIdAbortRequest(StrictModel):
    """Stop an active email sequence and pause all contacts from receiving further emails. Once aborted, the sequence halts all outgoing communications."""
    path: PostApiV1EmailerCampaignsSequenceIdAbortRequestPath

# Operation: archive_sequence
class PostApiV1EmailerCampaignsSequenceIdArchiveRequestPath(StrictModel):
    sequence_id: str = Field(default=..., description="The Apollo ID of the sequence to archive. This is a unique identifier in the format of a 24-character hexadecimal string.")
class PostApiV1EmailerCampaignsSequenceIdArchiveRequest(StrictModel):
    """Archive an email sequence to mark it as inactive and automatically finish all contacts currently enrolled in it. Only the sequence owner or users with full access sharing permissions can perform this action, and a master API key is required."""
    path: PostApiV1EmailerCampaignsSequenceIdArchiveRequestPath

# Operation: search_outreach_emails
class GetApiV1EmailerMessagesSearchRequestQuery(StrictModel):
    emailer_message_stats: list[Literal["delivered", "scheduled", "drafted", "not_opened", "opened", "clicked", "unsubscribed", "demoed", "bounced", "spam_blocked", "failed_other"]] | None = Field(default=None, validation_alias="emailer_message_stats[]", serialization_alias="emailer_message_stats[]", description="Filter emails by their delivery status (e.g., delivered, opened, bounced). Accepts multiple status values to broaden results.")
    emailer_message_reply_classes: list[Literal["willing_to_meet", "follow_up_question", "person_referral", "out_of_office", "already_left_company_or_not_right_person", "not_interested", "unsubscribe", "none_of_the_above"]] | None = Field(default=None, validation_alias="emailer_message_reply_classes[]", serialization_alias="emailer_message_reply_classes[]", description="Filter emails by recipient response sentiment, such as interest in meeting or follow-up questions. Accepts multiple response types.")
    user_ids: list[str] | None = Field(default=None, validation_alias="user_ids[]", serialization_alias="user_ids[]", description="Filter emails sent by specific team members. Provide user IDs as an array; retrieve user IDs from the Get a List of Users endpoint.")
    email_account_id_and_aliases: str | None = Field(default=None, description="Filter results by a specific email account ID and its associated aliases.")
    not_emailer_campaign_ids: list[str] | None = Field(default=None, validation_alias="not_emailer_campaign_ids[]", serialization_alias="not_emailer_campaign_ids[]", description="Exclude emails from specific sequences. Provide sequence IDs as an array; all sequences not listed will be included in results. Retrieve sequence IDs from the Search for Sequences endpoint.")
    emailer_message_date_range_mode: Literal["due_at", "completed_at"] | None = Field(default=None, description="Specify the date field to filter by: use 'due_at' for scheduled delivery dates or 'completed_at' for actual delivery dates. Use with the min/max date range parameters.")
    not_sent_reason_cds: list[Literal["contact_stage_safeguard", "same_account_reply", "account_stage_safeguard", "email_unverified", "snippets_missing", "personalized_opener_missing", "thread_reply_original_email_missing", "no_active_email_account", "email_format_invalid", "ownership_permission", "email_service_provider_delivery_failure", "sendgrid_dropped_email", "mailgun_dropped_email", "gdpr_compliance", "not_valid_hard_bounce_detected", "other_safeguard", "new_job_change_detected", "email_on_global_bounce_list"]] | None = Field(default=None, validation_alias="not_sent_reason_cds[]", serialization_alias="not_sent_reason_cds[]", description="Filter emails by the reason they were not sent (e.g., invalid address, bounced). Accepts multiple reasons.")
    q_keywords: str | None = Field(default=None, description="Narrow results by keywords that match email content. Keywords must directly match at least part of an email's body or subject.")
class GetApiV1EmailerMessagesSearchRequest(StrictModel):
    """Search for outreach emails created and sent through Apollo sequences by your team. Returns up to 50,000 records with pagination support (100 records per page, maximum 500 pages). Requires a master API key."""
    query: GetApiV1EmailerMessagesSearchRequestQuery | None = None

# Operation: get_email_activities
class GetApiV1EmailerMessagesIdActivitiesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the email message. This ID is assigned to each outreach email in Apollo and can be obtained by calling the search emails endpoint.")
class GetApiV1EmailerMessagesIdActivitiesRequest(StrictModel):
    """Retrieve detailed statistics and activity information for a specific email sent through an Apollo sequence, including email contents, engagement metrics (opens and clicks), and recipient contact details."""
    path: GetApiV1EmailerMessagesIdActivitiesRequestPath

# Operation: create_task
class PostApiV1TasksRequestBody(StrictModel):
    user_id: str = Field(default=..., description="The ID of the team member who will own this task. Retrieve user IDs from the Get a List of Users endpoint.")
    contact_id: str = Field(default=..., description="The Apollo ID of the contact associated with this task. Use the Search for Contacts endpoint to find valid contact IDs.")
    type_: Literal["call", "outreach_manual_email", "linkedin_step_connect", "linkedin_step_message", "linkedin_step_view_profile", "linkedin_step_interact_post", "action_item"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of action required for this task. Choose from: call, outreach via manual email, LinkedIn connection request, LinkedIn message, LinkedIn profile view, LinkedIn post interaction, or general action item.")
    priority: Literal["high", "medium", "low"] | None = Field(default=None, description="The priority level for this task. Defaults to medium if not specified. Options are high, medium, or low.")
    status: str = Field(default=..., description="The current status of the task. Use 'scheduled' for future tasks or 'completed'/'skipped' for already-finished tasks.")
    due_at: str = Field(default=..., description="The due date and time for this task in ISO 8601 format (UTC/GMT). Example: 2025-02-15T08:10:30Z.", json_schema_extra={'format': 'date-time'})
    title: str | None = Field(default=None, description="An optional title for the task. If not provided, Apollo will auto-generate a title based on the task type and contact name.")
    note: str | None = Field(default=None, description="An optional description providing context for the task owner about the action they need to take.")
class PostApiV1TasksRequest(StrictModel):
    """Create a task to track upcoming actions for you and your team, such as calls, emails, or LinkedIn outreach. The created task is assigned to a specific team member and linked to a contact."""
    body: PostApiV1TasksRequestBody

# Operation: bulk_create_tasks
class PostApiV1TasksBulkCreateRequestBody(StrictModel):
    user_id: str = Field(default=..., description="The ID of the team member who will own and execute these tasks within your Apollo account.")
    contact_ids: list[str] = Field(default=..., description="Array of Apollo contact IDs to assign tasks to. A separate task will be created for each contact using the same task configuration.")
    type_: Literal["call", "outreach_manual_email", "linkedin_step_connect", "linkedin_step_message", "linkedin_step_view_profile", "linkedin_step_interact_post", "action_item"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of action for the task: call, outreach_manual_email, linkedin_step_connect, linkedin_step_message, linkedin_step_view_profile, linkedin_step_interact_post, or action_item.")
    priority: Literal["high", "medium", "low"] | None = Field(default=None, description="Priority level for the task. Defaults to medium if not specified.")
    status: str = Field(default=..., description="The task status: use 'scheduled' for future tasks, or 'completed'/'skipped' for tasks already finished.")
    due_at: str = Field(default=..., description="The due date and time for the task in ISO 8601 format (e.g., 2025-02-15T08:10:30Z). Apollo uses Greenwich Mean Time (GMT) by default.", json_schema_extra={'format': 'date-time'})
    note: str | None = Field(default=None, description="Optional description providing context for the task owner about the action they need to take.")
class PostApiV1TasksBulkCreateRequest(StrictModel):
    """Create multiple tasks in a single request, with one task generated per contact. Returns a success status and array of created tasks. Requires a master API key."""
    body: PostApiV1TasksBulkCreateRequestBody

# Operation: search_tasks
class PostApiV1TasksSearchRequestQuery(StrictModel):
    sort_by_field: Literal["task_due_at", "task_priority"] | None = Field(default=None, description="Sort results by task due date (future dates first) or priority level (highest priority first).")
    open_factor_names: list[str] | None = Field(default=None, validation_alias="open_factor_names[]", serialization_alias="open_factor_names[]", description="Request task type counts in the response by including task_types. When specified, the response includes a task_types array with count values for each task type.")
class PostApiV1TasksSearchRequest(StrictModel):
    """Search for tasks created in Apollo across your team. Returns up to 50,000 records with pagination support (100 records per page, maximum 500 pages). Requires a master API key."""
    query: PostApiV1TasksSearchRequestQuery | None = None

# Operation: create_phone_call
class PostApiV1PhoneCallsRequestQuery(StrictModel):
    logged: bool | None = Field(default=None, description="Whether to create an individual call record in Apollo. Defaults to true if not specified.")
    user_id: list[str] | None = Field(default=None, validation_alias="user_id[]", serialization_alias="user_id[]", description="IDs of team members who made the call. Retrieve available user IDs from the Get a List of Users endpoint. Accepts multiple user IDs as an array.")
    account_id: str | None = Field(default=None, description="ID of the account associated with this call. Retrieve available account IDs from the Search for Accounts endpoint.")
    status: Literal["queued", "ringing", "in-progress", "completed", "no_answer", "failed", "busy"] | None = Field(default=None, description="Current status of the call. Valid statuses are: queued, ringing, in-progress, completed, no_answer, failed, or busy.")
    start_time: str | None = Field(default=None, description="Timestamp when the call started, formatted in ISO 8601 date-time format using Greenwich Mean Time (GMT).", json_schema_extra={'format': 'date-time'})
    end_time: str | None = Field(default=None, description="Timestamp when the call ended, formatted in ISO 8601 date-time format using Greenwich Mean Time (GMT).", json_schema_extra={'format': 'date-time'})
    duration: int | None = Field(default=None, description="Length of the call in seconds (not minutes).")
    phone_call_purpose_id: str | None = Field(default=None, description="ID of the call purpose category to assign to this record. Call purposes are custom to your Apollo account.")
    phone_call_outcome_id: str | None = Field(default=None, description="ID of the call outcome to assign to this record. Call outcomes are custom to your Apollo account.")
    note: str | None = Field(default=None, description="Additional notes or context about the call to include in the record.")
class PostApiV1PhoneCallsRequest(StrictModel):
    """Log phone calls made through external systems (such as Orum or Nooks) into Apollo. This endpoint records call metadata and outcomes but cannot initiate calls. Requires a master API key."""
    query: PostApiV1PhoneCallsRequestQuery | None = None

# Operation: search_phone_calls
class GetApiV1PhoneCallsSearchRequestQuery(StrictModel):
    date_range_min: str | None = Field(default=None, validation_alias="date_range[min]", serialization_alias="date_range[min]", description="Lower bound of the date range to search (YYYY-MM-DD format). Must be earlier than date_range[max] if both are specified.", json_schema_extra={'format': 'date'})
    date_range_max: str | None = Field(default=None, validation_alias="date_range[max]", serialization_alias="date_range[max]", description="Upper bound of the date range to search (YYYY-MM-DD format). Must be later than date_range[min] if both are specified.", json_schema_extra={'format': 'date'})
    duration_min: int | None = Field(default=None, validation_alias="duration[min]", serialization_alias="duration[min]", description="Minimum call duration in seconds. Must be smaller than duration[max] if both are specified.")
    duration_max: int | None = Field(default=None, validation_alias="duration[max]", serialization_alias="duration[max]", description="Maximum call duration in seconds. Must be larger than duration[min] if both are specified.")
    inbound: Literal["incoming", "outgoing"] | None = Field(default=None, description="Filter by call direction: 'incoming' for calls received by your team, or 'outgoing' for calls made by your team.")
    user_ids: list[str] | None = Field(default=None, validation_alias="user_ids[]", serialization_alias="user_ids[]", description="Filter calls by one or more team members. Provide an array of user IDs from your Apollo account.")
    contact_label_ids: list[str] | None = Field(default=None, validation_alias="contact_label_ids[]", serialization_alias="contact_label_ids[]", description="Filter calls by one or more contacts in your Apollo database. Provide an array of contact IDs.")
    phone_call_purpose_ids: list[str] | None = Field(default=None, validation_alias="phone_call_purpose_ids[]", serialization_alias="phone_call_purpose_ids[]", description="Filter calls by their purpose. Provide an array of call purpose IDs configured in your Apollo account.")
    phone_call_outcome_ids: list[str] | None = Field(default=None, validation_alias="phone_call_outcome_ids[]", serialization_alias="phone_call_outcome_ids[]", description="Filter calls by their outcome or disposition. Provide an array of call outcome IDs configured in your Apollo account.")
    q_keywords: str | None = Field(default=None, description="Narrow search results by keywords found in call records.")
class GetApiV1PhoneCallsSearchRequest(StrictModel):
    """Search for phone calls made or received by your team using the Apollo dialer. Filter results by date range, duration, call direction, team members, contacts, call purposes, outcomes, and keywords."""
    query: GetApiV1PhoneCallsSearchRequestQuery | None = None

# Operation: update_call
class PutApiV1PhoneCallsIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique Apollo identifier for the call record to update.")
class PutApiV1PhoneCallsIdRequestQuery(StrictModel):
    logged: bool | None = Field(default=None, description="Set to true to create an individual record for this phone call in Apollo.")
    user_id: list[str] | None = Field(default=None, validation_alias="user_id[]", serialization_alias="user_id[]", description="Array of user IDs from your Apollo account to designate who made the call.")
    account_id: str | None = Field(default=None, description="The Apollo account ID to associate this call with.")
    status: Literal["queued", "ringing", "in-progress", "completed", "no_answer", "failed", "busy"] | None = Field(default=None, description="The current status of the call: queued, ringing, in-progress, completed, no_answer, failed, or busy.")
    start_time: str | None = Field(default=None, description="The date and time when the call started, formatted in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    end_time: str | None = Field(default=None, description="The date and time when the call ended, formatted in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    duration: int | None = Field(default=None, description="The total duration of the call in seconds.")
    phone_call_purpose_id: str | None = Field(default=None, description="The Apollo ID of the call purpose category to assign to this record.")
    phone_call_outcome_id: str | None = Field(default=None, description="The Apollo ID of the call outcome to assign to this record.")
    note: str | None = Field(default=None, description="A text note to add to the call record for additional context or details.")
class PutApiV1PhoneCallsIdRequest(StrictModel):
    """Update an existing call record in Apollo with new details such as status, timing, duration, purpose, outcome, and notes. Requires a master API key."""
    path: PutApiV1PhoneCallsIdRequestPath
    query: PutApiV1PhoneCallsIdRequestQuery | None = None

# Operation: list_fields
class GetApiV1FieldsRequestQuery(StrictModel):
    source: Literal["system", "custom", "crm_synced"] | None = Field(default=None, description="Filter the returned fields by their source type: system fields (built-in), custom fields (user-created), or crm_synced fields (synchronized from your CRM).")
class GetApiV1FieldsRequest(StrictModel):
    """Retrieve all fields available in your Apollo account, with optional filtering by source type. Requires a master API key for authentication."""
    query: GetApiV1FieldsRequestQuery | None = None

# Operation: create_custom_field
class PostApiV1FieldsRequestBody(StrictModel):
    label: str = Field(default=..., description="The display name for the custom field (e.g., 'Test Name'). This is how the field will appear in your Apollo account.")
    modality: Literal["contact", "account", "opportunity"] = Field(default=..., description="The entity type this custom field applies to: contact, account, or opportunity. This determines where the field will be available in your Apollo workspace.")
    type_: Literal["string", "textarea", "number", "date", "datetime", "boolean"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The data type for the custom field. Choose from: string (single-line text), textarea (multi-line text), number, date, datetime, or boolean (true/false).")
    meta: dict[str, Any] | None = Field(default=None, description="Optional metadata object to store additional configuration or properties for the custom field.")
class PostApiV1FieldsRequest(StrictModel):
    """Create a custom field in your Apollo account to capture unique details about contacts, accounts, or deals. Custom fields enable your team to store specialized information and personalize outreach sequences."""
    body: PostApiV1FieldsRequestBody

# Operation: list_notes
class GetApiV1NotesRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, description="The ID of the account to retrieve notes for.")
    opportunity_id: str | None = Field(default=None, description="The ID of the opportunity to retrieve notes for.")
    calendar_event_id: str | None = Field(default=None, description="The ID of the calendar event to retrieve notes for.")
    conversation_ids: list[str] | None = Field(default=None, description="One or more conversation IDs to filter notes by multiple conversations.")
    contact_ids: list[str] | None = Field(default=None, description="One or more contact IDs to filter notes by multiple contacts.")
    start_date: str | None = Field(default=None, description="Filter notes to only those created on or after this date (ISO 8601 format).", json_schema_extra={'format': 'date'})
    sort_by_field: Literal["created_at", "updated_at"] | None = Field(default=None, description="Field to sort results by. Defaults to creation date. Options are creation date or last update date.")
    sort_direction: Literal["asc", "desc"] | None = Field(default=None, description="Sort direction for results. Defaults to descending (newest first). Use ascending for oldest first.")
    skip: int | None = Field(default=None, description="Number of notes to skip for pagination. Must be zero or greater. Defaults to 0.", ge=0)
    limit: int | None = Field(default=None, description="Maximum number of notes to return per request. Must be between 1 and 100. Defaults to 25.", ge=1, le=100)
class GetApiV1NotesRequest(StrictModel):
    """Retrieve notes associated with a specific contact, account, opportunity, calendar event, or conversation. At least one relation parameter must be provided to filter results, with support for sorting and pagination."""
    query: GetApiV1NotesRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class PostApiV1AccountsBulkCreateBodyAccountsItem(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Account ID")
    name: str | None = Field(None, description="Account name")
    domain: str | None = Field(None, description="Company domain")
    team_id: str | None = Field(None, description="Team ID")
    owner_id: str | None = Field(None, description="Account owner ID")
    account_stage_id: str | None = Field(None, description="Account stage ID")
    phone: str | None = Field(None, description="Company phone number")
    linkedin_url: str | None = Field(None, description="LinkedIn company URL", json_schema_extra={'format': 'uri'})


# Rebuild models to resolve forward references (required for circular refs)
PostApiV1AccountsBulkCreateBodyAccountsItem.model_rebuild()

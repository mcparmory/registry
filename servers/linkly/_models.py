"""
Linkly MCP Server - Pydantic Models

Generated: 2026-04-14 18:25:25 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "CreateDomainInWorkspaceRequest",
    "CreateDomainRequest",
    "CreateOrUpdateLink2Request",
    "CreateOrUpdateLinkRequest",
    "DeleteDomainRequest",
    "DeleteLinkRequest",
    "DeleteLinksRequest",
    "ExportLinksRequest",
    "GetClickCountersRequest",
    "GetClicksRequest",
    "GetLink2Request",
    "GetLinkRequest",
    "ListDomainsRequest",
    "ListLinksRequest",
    "ListLinkWebhooksRequest",
    "UnsubscribeWebhookFromLinkRequest",
    "UpdateDomainFaviconRequest",
    "CreateOrUpdateLinkBodyRulesItem",
    "Rule",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: add_domain_to_workspace
class CreateDomainRequestBody(StrictModel):
    """Parameters"""
    name: str | None = Field(default=None, description="The name of the custom domain to add to your workspace.")
    workspace_id: int = Field(default=..., description="The unique identifier of the workspace where the domain will be added.")
class CreateDomainRequest(StrictModel):
    """Add a new custom domain to your workspace. Ensure DNS CNAME record configuration is completed before adding the domain."""
    body: CreateDomainRequestBody

# Operation: get_link
class GetLinkRequestPath(StrictModel):
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the link to retrieve (e.g., 24).")
class GetLinkRequest(StrictModel):
    """Retrieve detailed information about a specific link by its unique identifier."""
    path: GetLinkRequestPath

# Operation: create_or_update_link
class CreateOrUpdateLinkRequestBody(StrictModel):
    """Parameters"""
    block_bots: bool | None = Field(default=None, description="Prevent automated bots and crawlers from accessing this link.")
    body_tags: str | None = Field(default=None, description="Custom HTML tags to inject into the page body for tracking or functionality purposes.")
    cloaking: bool | None = Field(default=None, description="Enable URL cloaking to hide the destination URL from users and analytics.")
    deleted: bool | None = Field(default=None, description="Mark the link as deleted. Set to true to soft-delete without removing the record.")
    enabled: bool | None = Field(default=None, description="Enable or disable the link. Disabled links will not redirect.")
    fb_pixel_id: str | None = Field(default=None, description="Facebook Pixel ID for conversion tracking and audience building.")
    forward_params: bool | None = Field(default=None, description="Forward query parameters from the shortened link to the destination URL.")
    ga4_tag_id: str | None = Field(default=None, description="Google Analytics 4 measurement ID for tracking link performance.")
    gtm_id: str | None = Field(default=None, description="Google Tag Manager container ID for advanced event tracking and tag management.")
    head_tags: str | None = Field(default=None, description="Custom HTML tags to inject into the page head for scripts, metadata, or tracking.")
    hide_referrer: bool | None = Field(default=None, description="Hide the HTTP referrer header when redirecting to prevent the destination from seeing the source.")
    id_: int | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Unique identifier of the link to update. Required when updating an existing link; omit when creating new.")
    linkify_words: str | None = Field(default=None, description="Comma-separated list of words to automatically convert into links within the destination page content.")
    name: str | None = Field(default=None, description="Human-readable name or title for the link to aid organization and identification.")
    note: str | None = Field(default=None, description="Internal note or memo for reference; not visible to end users.")
    og_description: str | None = Field(default=None, description="Open Graph description displayed when the link is shared on social media platforms.")
    og_image: str | None = Field(default=None, description="Open Graph image URL displayed when the link is shared on social media platforms.")
    og_title: str | None = Field(default=None, description="Open Graph title displayed when the link is shared on social media platforms.")
    replacements: str | None = Field(default=None, description="String-encoded replacement rules for dynamic URL parameter substitution or content modification.")
    rules: list[CreateOrUpdateLinkBodyRulesItem] | None = Field(default=None, description="Array of conditional redirect rules that determine the destination URL based on user attributes, device type, or other criteria. Rules are evaluated in order.")
    slug: str | None = Field(default=None, description="Custom URL slug for the shortened link. If omitted, a random slug is generated automatically.")
    spam: bool | None = Field(default=None, description="Mark the link as spam or suspicious content.")
    tiktok_pixel_id: str | None = Field(default=None, description="TikTok Pixel ID for conversion tracking and audience building on TikTok.")
    url: str | None = Field(default=None, description="Destination URL to redirect to. Required when creating a new link; must be a valid URI.", json_schema_extra={'format': 'uri'})
    workspace_id: int | None = Field(default=None, description="Workspace ID")
class CreateOrUpdateLinkRequest(StrictModel):
    """Create a new shortened link or update an existing one. Provide `url` and `workspace_id` to create; provide `id` and fields to update. Supports custom slugs, UTM parameters, tracking pixels, Open Graph metadata, and conditional redirect rules."""
    body: CreateOrUpdateLinkRequestBody | None = None

# Operation: get_link_analytics
class GetLink2RequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the link to retrieve. Use the link ID provided when the link was created.")
class GetLink2RequestQuery(StrictModel):
    workspace_id: str | None = Field(default=None, description="Workspace ID. Optional when using OAuth2 Bearer token.")
class GetLink2Request(StrictModel):
    """Retrieve detailed information about a specific link, including click statistics, UTM parameters, and configuration settings."""
    path: GetLink2RequestPath
    query: GetLink2RequestQuery | None = None

# Operation: list_webhooks_for_link
class ListLinkWebhooksRequestPath(StrictModel):
    link_id: int = Field(default=..., description="The unique identifier of the link whose webhooks you want to retrieve. Must be a positive integer.")
class ListLinkWebhooksRequest(StrictModel):
    """Retrieve all webhook subscriptions configured for a specific link. Returns a list of webhooks that are actively monitoring events for the given link."""
    path: ListLinkWebhooksRequestPath

# Operation: get_clicks_analytics
class GetClicksRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace to retrieve click analytics for.")
class GetClicksRequestQuery(StrictModel):
    start: str | None = Field(default=None, description="The start date for filtering clicks, specified in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ). If omitted, defaults to the beginning of available data.")
    end: str | None = Field(default=None, description="The end date for filtering clicks, specified in ISO 8601 format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ). If omitted, defaults to the current date.")
    country: str | None = Field(default=None, description="Filter results to clicks from a specific country using its ISO 3166-1 alpha-2 code (e.g., US, GB, DE).")
    browser: str | None = Field(default=None, description="Filter results to clicks from a specific browser (e.g., Chrome, Firefox, Safari).")
    platform: str | None = Field(default=None, description="Filter results to clicks from a specific platform or operating system (e.g., Windows, Mac, iOS, Android).")
    referer: str | None = Field(default=None, description="Filter results to clicks originating from a specific referrer domain.")
    isp: str | None = Field(default=None, description="Filter results to clicks from a specific Internet Service Provider.")
    format_: Literal["json", "csv", "tsv"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="Specify the response format: 'json' (default), 'csv', or 'tsv'.")
    pivot: Literal["link_id"] | None = Field(default=None, description="Transform the response into a matrix format where dates appear as rows and links as columns. When set to 'link_id', CSV/TSV responses include header rows with link name, full URL, and ID.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="The timezone to apply for date and time calculations (e.g., America/New_York). Affects how dates are bucketed and displayed.")
    frequency: Literal["day", "hour"] | None = Field(default=None, description="The time granularity for aggregating data points: 'day' (default) for daily buckets or 'hour' for hourly buckets.")
class GetClicksRequest(StrictModel):
    """Retrieve click analytics for a workspace with flexible filtering and aggregation options. Returns time-series data suitable for charting, with support for multiple output formats and pivot transformations."""
    path: GetClicksRequestPath
    query: GetClicksRequestQuery | None = None

# Operation: get_click_counters_by_dimension
class GetClickCountersRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The workspace identifier that contains the click analytics data.")
    counter: Literal["country", "platform", "browser", "referer", "isp", "link_id", "top_params"] = Field(default=..., description="The dimension to group clicks by. Choose from: country (geographic location), platform (device type), browser (web browser), referer (HTTP referrer), isp (internet service provider), link_id (specific tracked link), or top_params (query parameters).")
class GetClickCountersRequestQuery(StrictModel):
    start: str | None = Field(default=None, description="The start date for filtering analytics data, specified in YYYY-MM-DD format. If omitted, defaults to the earliest available data.")
    end: str | None = Field(default=None, description="The end date for filtering analytics data, specified in YYYY-MM-DD format. If omitted, defaults to the current date.")
    country: str | None = Field(default=None, description="Filter results to a specific country using its ISO 3166-1 alpha-2 country code (e.g., 'US', 'GB', 'DE'). If omitted, all countries are included.")
    format_: Literal["json", "csv", "tsv"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The response format for the analytics data. Choose from JSON (default, structured format), CSV (comma-separated values), or TSV (tab-separated values).")
class GetClickCountersRequest(StrictModel):
    """Retrieve aggregated click analytics grouped by a specified dimension (such as country, platform, or browser). Returns click counts for each unique value within the selected dimension, with optional filtering by date range, country, and response format."""
    path: GetClickCountersRequestPath
    query: GetClickCountersRequestQuery | None = None

# Operation: list_domains
class ListDomainsRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace whose domains you want to list.")
class ListDomainsRequest(StrictModel):
    """Retrieve all custom domains configured for a workspace. These domains can be used as targets when creating short links."""
    path: ListDomainsRequestPath

# Operation: add_domain_to_workspace_by_id
class CreateDomainInWorkspaceRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace where the domain will be added.")
class CreateDomainInWorkspaceRequestBody(StrictModel):
    """Parameters"""
    name: str = Field(default=..., description="The fully qualified domain name to add (e.g., links.example.com). Ensure the corresponding CNAME record is configured in your DNS provider before adding.")
class CreateDomainInWorkspaceRequest(StrictModel):
    """Add a custom domain to a workspace. The domain must have a CNAME record configured in DNS before being added."""
    path: CreateDomainInWorkspaceRequestPath
    body: CreateDomainInWorkspaceRequestBody

# Operation: delete_domain
class DeleteDomainRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace containing the domain to be deleted.")
    domain_id: str = Field(default=..., description="The unique identifier of the domain to be removed from the workspace.")
class DeleteDomainRequest(StrictModel):
    """Remove a custom domain from your workspace. Once deleted, any links using this domain will no longer be functional."""
    path: DeleteDomainRequestPath

# Operation: update_domain_favicon
class UpdateDomainFaviconRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace containing the domain. Typically a numeric ID.")
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the domain whose favicon should be updated. Typically a numeric ID.")
class UpdateDomainFaviconRequestBody(StrictModel):
    """Parameters"""
    favicon_url: str | None = Field(default=None, description="A valid URI pointing to the favicon image file. Common formats include .ico, .png, and .svg. If omitted, the favicon will not be updated.", json_schema_extra={'format': 'uri'})
class UpdateDomainFaviconRequest(StrictModel):
    """Update the favicon URL for a custom domain within a workspace. The favicon will be displayed in browser tabs and bookmarks for the domain."""
    path: UpdateDomainFaviconRequestPath
    body: UpdateDomainFaviconRequestBody | None = None

# Operation: create_or_update_link_batch
class CreateOrUpdateLink2RequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The workspace identifier where the link will be created or updated.")
class CreateOrUpdateLink2RequestBody(StrictModel):
    """Link"""
    fb_pixel_id: str | None = Field(default=None, description="Facebook Pixel ID for tracking conversions on Facebook.")
    tiktok_pixel_id: str | None = Field(default=None, description="TikTok Pixel ID for tracking conversions on TikTok.")
    hide_referrer: bool | None = Field(default=None, description="When enabled, prevents the referrer information from being passed to the destination URL.")
    expiry_datetime: str | None = Field(default=None, description="Date and time when the link automatically expires and becomes inactive. Use ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    expiry_destination: str | None = Field(default=None, description="URL to redirect users to after the link expires.")
    rules: list[Rule] | None = Field(default=None, description="Array of redirect rules that determine where users are sent based on conditions like device type, location, or custom parameters.")
    domain_id: int | None = Field(default=None, description="Numeric identifier of the domain to use for this link. Use this as an alternative to specifying a domain name.")
    cloaking: bool | None = Field(default=None, description="When enabled, hides the actual destination URL and displays a cloaked URL instead.")
    linkify_words: str | None = Field(default=None, description="Specific words within the link that should be converted into clickable links.")
    og_description: str | None = Field(default=None, description="Open Graph description text displayed when the link is shared on social media.")
    skip_social_crawler_tracking: bool | None = Field(default=None, description="When enabled, prevents tracking of requests from social media crawlers and bots.")
    body_tags: str | None = Field(default=None, description="Custom HTML tags to inject into the body section of the destination page.")
    og_title: str | None = Field(default=None, description="Open Graph title text displayed when the link is shared on social media.")
    note: str | None = Field(default=None, description="Private internal note for reference; not visible to end users.")
    name: str | None = Field(default=None, description="Human-readable nickname or label for this link to help identify it in your workspace.")
    id_: int | None = Field(default=None, validation_alias="id", serialization_alias="id", description="Numeric identifier of an existing link to update. Omit this field to create a new link.")
    gtm_id: str | None = Field(default=None, description="Google Tag Manager container ID for tracking and analytics.")
    og_image: str | None = Field(default=None, description="URL of an image to display when the link is shared on social media.")
    block_bots: bool | None = Field(default=None, description="When enabled, blocks traffic from known bots and automated crawlers.")
    enabled: bool | None = Field(default=None, description="Controls whether the link is active and functional. Set to false to disable without deleting.")
    url: str = Field(default=..., description="The destination URL where users will be redirected. Must be a valid URI.", json_schema_extra={'format': 'uri'})
    replacements: str | None = Field(default=None, description="URL parameter replacements to transform or modify query parameters before forwarding to the destination.")
    qr_styles: dict[str, Any] | None = Field(default=None, description="Object containing styling options for QR codes generated from this link, such as colors and patterns.")
    webhooks: list[str] | None = Field(default=None, description="Array of webhook URLs that receive notifications when link events occur, such as clicks or conversions.")
    expiry_clicks: int | None = Field(default=None, description="Number of clicks after which the link automatically expires and becomes inactive.")
    public_analytics: bool | None = Field(default=None, description="When enabled, analytics data for this link is publicly accessible without authentication.")
    slug: str | None = Field(default=None, description="Custom URL slug for this link. Must start with a forward slash (/) and be unique within the workspace.")
    forward_params: bool | None = Field(default=None, description="When enabled, query parameters from the shortened link are automatically forwarded to the destination URL.")
    head_tags: str | None = Field(default=None, description="Custom HTML tags to inject into the head section of the destination page.")
    ga4_tag_id: str | None = Field(default=None, description="Google Analytics 4 measurement ID for tracking events and conversions.")
class CreateOrUpdateLink2Request(StrictModel):
    """Create a new link or update an existing one in a workspace. Include an 'id' field to update an existing link, or omit it to create a new one. Supports batch operations by accepting an array of links."""
    path: CreateOrUpdateLink2RequestPath
    body: CreateOrUpdateLink2RequestBody

# Operation: delete_links
class DeleteLinksRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace containing the links to delete.")
class DeleteLinksRequestBody(StrictModel):
    """Parameters"""
    ids: list[int] | None = Field(default=None, description="Array of link IDs to delete. If not provided, no links will be deleted.")
class DeleteLinksRequest(StrictModel):
    """Permanently delete one or more links from a workspace by their IDs. This action cannot be undone."""
    path: DeleteLinksRequestPath
    body: DeleteLinksRequestBody | None = None

# Operation: export_links
class ExportLinksRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace containing the links to export.")
class ExportLinksRequestQuery(StrictModel):
    format_: Literal["json", "csv"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The output format for the exported links. Choose between JSON (default) or CSV.")
    search: str | None = Field(default=None, description="Optional search query to filter which links are included in the export. Only links matching the query will be returned.")
class ExportLinksRequest(StrictModel):
    """Export all links in a workspace in JSON or CSV format, with optional filtering by search query."""
    path: ExportLinksRequestPath
    query: ExportLinksRequestQuery | None = None

# Operation: delete_link
class DeleteLinkRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace containing the link to delete.")
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the link to delete.")
class DeleteLinkRequest(StrictModel):
    """Permanently delete a specific link from a workspace by its ID. This action cannot be undone."""
    path: DeleteLinkRequestPath

# Operation: list_links
class ListLinksRequestPath(StrictModel):
    workspace_id: str = Field(default=..., description="The unique identifier of the workspace containing the links to retrieve.")
class ListLinksRequestQuery(StrictModel):
    search: str | None = Field(default=None, description="Optional search query to filter links by matching against link properties. Searches across relevant link fields to narrow results.")
    page: int | None = Field(default=None, description="The page number for pagination, starting from 1. Defaults to the first page if not specified.")
    page_size: int | None = Field(default=None, description="The maximum number of links to return per page. Defaults to 1000 if not specified.")
    sort_by: str | None = Field(default=None, description="The field name to sort results by. Common sortable fields include creation date, click count, and link name.")
    sort_dir: str | None = Field(default=None, description="The sort direction for results: ascending or descending order.")
class ListLinksRequest(StrictModel):
    """Retrieve a paginated list of all links in a workspace with support for searching, sorting, and filtering. Results include click statistics and link metadata for each entry."""
    path: ListLinksRequestPath
    query: ListLinksRequestQuery | None = None

# Operation: delete_webhook_from_link
class UnsubscribeWebhookFromLinkRequestPath(StrictModel):
    link_id: int = Field(default=..., description="The unique identifier of the link from which to remove the webhook subscription.")
    hook_id: str = Field(default=..., description="The webhook URL to unsubscribe, provided in URL-encoded format (e.g., https%3A%2F%2Fhooks.example.com%2Fabc123).")
class UnsubscribeWebhookFromLinkRequest(StrictModel):
    """Remove a webhook subscription from a link by unsubscribing the specified webhook URL. This operation permanently deletes the webhook subscription relationship."""
    path: UnsubscribeWebhookFromLinkRequestPath

# ============================================================================
# Component Models
# ============================================================================

class CreateOrUpdateLinkBodyRulesItem(PermissiveModel):
    matches: str | None = None
    percentage: str | None = None
    rule_url: str | None = None
    url: str | None = None
    what: str | None = None

class Rule(PermissiveModel):
    matches: str | None = None
    percentage: int | None = None
    url: str | None = None
    what: str | None = None

class Link(PermissiveModel):
    """Response schema for a link"""
    fb_pixel_id: str | None = None
    tiktok_pixel_id: str | None = None
    hide_referrer: bool | None = None
    expiry_datetime: str | None = None
    expiry_destination: str | None = Field(None, json_schema_extra={'format': 'uri'})
    rules: list[Rule] | None = None
    cloaking: bool | None = None
    linkify_words: str | None = None
    full_url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    og_description: str | None = None
    body_tags: str | None = None
    og_title: str | None = None
    note: str | None = None
    name: str | None = None
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id")
    gtm_id: str | None = None
    og_image: str | None = None
    block_bots: bool | None = None
    utm_content: str | None = None
    enabled: bool | None = None
    url: str | None = Field(None, json_schema_extra={'format': 'uri'})
    replacements: str | None = None
    deleted: bool | None = None
    expiry_clicks: int | None = None
    workspace_id: int | None = None
    public_analytics: bool | None = None
    utm_source: str | None = None
    slug: str | None = None
    domain: str | None = None
    forward_params: bool | None = None
    utm_medium: str | None = None
    head_tags: str | None = None
    ga4_tag_id: str | None = None
    utm_term: str | None = None
    utm_campaign: str | None = None


# Rebuild models to resolve forward references (required for circular refs)
CreateOrUpdateLinkBodyRulesItem.model_rebuild()
Link.model_rebuild()
Rule.model_rebuild()

"""
Agentql MCP Server - Pydantic Models

Generated: 2026-04-14 18:12:54 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "CreateSessionV1TetraSessionsPostRequest",
    "ListSessionUsageV1TetraUsageGetRequest",
    "QueryDataServiceV1QueryDataPostRequest",
    "CustomProxy",
    "TetraProxy",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: query_webpage_data
class QueryDataServiceV1QueryDataPostRequestHeader(StrictModel):
    content_type: str = Field(default=..., validation_alias="content-type", serialization_alias="content-type", description="MIME type of the request body, required to correctly parse the payload.")
class QueryDataServiceV1QueryDataPostRequestBodyParams(StrictModel):
    mode: Literal["fast", "standard"] | None = Field(default=None, validation_alias="mode", serialization_alias="mode", description="Controls the response generation strategy: 'fast' prioritizes speed, 'standard' prioritizes accuracy and completeness.")
    wait_for: int | None = Field(default=None, validation_alias="wait_for", serialization_alias="wait_for", description="Number of seconds to wait for dynamic page content to load before capturing the snapshot. Maximum allowed wait time is 10 seconds.")
    is_scroll_to_bottom_enabled: bool | None = Field(default=None, validation_alias="is_scroll_to_bottom_enabled", serialization_alias="is_scroll_to_bottom_enabled", description="When enabled, the browser scrolls to the bottom of the page before capturing the snapshot, useful for triggering lazy-loaded content.")
    is_screenshot_enabled: bool | None = Field(default=None, validation_alias="is_screenshot_enabled", serialization_alias="is_screenshot_enabled", description="When enabled, a screenshot of the page is captured during the query session, which may be useful for debugging or visual verification.")
    browser_profile: Literal["light", "stealth", "tf-browser"] | None = Field(default=None, validation_alias="browser_profile", serialization_alias="browser_profile", description="Determines the browser profile used for the session: 'light' uses a fast headless browser, 'stealth' applies anti-detection techniques for bot-protected pages.")
    proxy: TetraProxy | CustomProxy | None = Field(default=None, validation_alias="proxy", serialization_alias="proxy", description="Optional proxy configuration to route the browser session through a specific proxy server, useful for geo-restricted or access-controlled pages.")
class QueryDataServiceV1QueryDataPostRequestBody(StrictModel):
    query: str | None = Field(default=None, description="An AgentQL (AQL) query string specifying the exact data fields to extract from the page. If omitted, a query will be auto-generated from the prompt.")
    prompt: str | None = Field(default=None, description="A natural language description of the data to extract, used to auto-generate an AgentQL query when no explicit query is provided.")
    url: str | None = Field(default=None, description="The fully qualified URL of the webpage to load and query. Either url or html must be provided as the data source.")
    html: str | None = Field(default=None, description="Raw HTML content of the webpage to query, used as an alternative to providing a live URL.")
    params: QueryDataServiceV1QueryDataPostRequestBodyParams | None = None
class QueryDataServiceV1QueryDataPostRequest(StrictModel):
    """Extracts structured data from a webpage using an AgentQL query or a natural language prompt. Accepts either a live URL or raw HTML as the data source."""
    header: QueryDataServiceV1QueryDataPostRequestHeader
    body: QueryDataServiceV1QueryDataPostRequestBody | None = None

# Operation: create_browser_session
class CreateSessionV1TetraSessionsPostRequestBody(StrictModel):
    browser_ua_preset: Literal["windows", "macos", "linux"] | None = Field(default=None, description="The operating system user agent preset the browser will identify as, affecting how websites perceive the client environment.")
    browser_profile: Literal["light", "stealth", "tf-browser"] | None = Field(default=None, description="The browser profile determining capability and detection resistance: 'light' prioritizes speed with minimal overhead, 'stealth' enables full anti-detection features, and 'tf-browser' uses a custom TF Browser configuration.")
    shutdown_mode: Literal["on_disconnect", "on_inactivity_timeout"] | None = Field(default=None, description="Controls session teardown behavior on disconnect: 'on_disconnect' immediately stops the session when all connections close, while 'on_inactivity_timeout' keeps the session alive to allow reconnection until the inactivity timeout elapses.")
    inactivity_timeout_seconds: int | None = Field(default=None, description="How long the session remains alive without active connections before being shut down, applicable when shutdown_mode is 'on_inactivity_timeout'. Accepts values between 5 seconds and 86400 seconds (24 hours).", ge=5, le=86400)
    proxy: TetraProxy | CustomProxy | None = Field(default=None, description="Proxy server configuration to route browser traffic through for this session, such as host, port, protocol, and credentials.")
    sub_user_id: str | None = Field(default=None, description="An optional identifier used to associate this session with a specific sub-user within your account, useful for tracking and auditing sessions across multiple users.")
class CreateSessionV1TetraSessionsPostRequest(StrictModel):
    """Creates a new Tetra browser session with configurable user agent, profile, proxy, and lifecycle settings. Returns session details needed to connect and interact with the browser."""
    body: CreateSessionV1TetraSessionsPostRequestBody | None = None

# Operation: list_session_usage
class ListSessionUsageV1TetraUsageGetRequestQuery(StrictModel):
    sub_user_id: str | None = Field(default=None, description="Filter results to only include sessions belonging to a specific sub-user under the authenticated account.")
    session_id: str | None = Field(default=None, description="Filter results to a specific browser session by its unique session identifier.")
    start_after: str | None = Field(default=None, description="Return only sessions that started after this timestamp, specified in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    end_before: str | None = Field(default=None, description="Return only sessions that ended before this timestamp, specified in ISO 8601 date-time format.", json_schema_extra={'format': 'date-time'})
    status: Literal["running", "ended"] | None = Field(default=None, description="Filter sessions by their current lifecycle status; use 'running' for active sessions or 'ended' for completed sessions.")
    limit: int | None = Field(default=None, description="Maximum number of session records to return per page; must be between 1 and 1000.", ge=1, le=1000)
    page: int | None = Field(default=None, description="Page number to retrieve for paginated results; must be 1 or greater.", ge=1)
class ListSessionUsageV1TetraUsageGetRequest(StrictModel):
    """Retrieve a paginated list of Tetra browser session usage records for the authenticated user, with optional filtering by user, session, time range, and status."""
    query: ListSessionUsageV1TetraUsageGetRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class CustomProxy(StrictModel):
    """Custom external proxy configuration"""
    type_: Literal["custom"] | None = Field('custom', validation_alias="type", serialization_alias="type", description="Type of proxy: 'custom' for external proxy")
    url: str = Field(..., description="Proxy server URL")
    username: str | None = Field(None, description="Username for proxy authentication")
    password: str | None = Field(None, description="Password for proxy authentication")

class TetraProxy(StrictModel):
    """Tetra built-in proxy configuration"""
    type_: Literal["tetra"] | None = Field('tetra', validation_alias="type", serialization_alias="type", description="Type of proxy: 'tetra' for built-in proxy")
    country_code: str | None = Field('US', description="Country code for tetra proxy")


# Rebuild models to resolve forward references (required for circular refs)
CustomProxy.model_rebuild()
TetraProxy.model_rebuild()

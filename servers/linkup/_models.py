"""
Linkup MCP Server - Pydantic Models

Generated: 2026-05-05 15:29:03 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "CreateResearchRequest",
    "FetchRequest",
    "GetResearchRequest",
    "SearchRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_webpage
class FetchRequestBody(StrictModel):
    url: str = Field(default=..., description="The full URL of the webpage to fetch (must be a valid URI format, e.g., https://example.com).", json_schema_extra={'format': 'uri'})
    render_js: bool | None = Field(default=None, validation_alias="renderJs", serialization_alias="renderJs", description="Whether to render JavaScript before extracting content. Disabled by default; enable for dynamic pages that require script execution.")
    include_raw_html: bool | None = Field(default=None, validation_alias="includeRawHtml", serialization_alias="includeRawHtml", description="Whether to include the raw HTML markup in the response. Disabled by default; enable if you need the unprocessed HTML source.")
    extract_images: bool | None = Field(default=None, validation_alias="extractImages", serialization_alias="extractImages", description="Whether to extract and return images found on the webpage. Disabled by default; enable to retrieve image URLs and metadata.")
class FetchRequest(StrictModel):
    """Fetch and parse a single webpage from a given URL, with optional JavaScript rendering, raw HTML inclusion, and image extraction."""
    body: FetchRequestBody

# Operation: search_web_content
class SearchRequestBody(StrictModel):
    q: str = Field(default=..., description="The natural language question or search query for which you want to retrieve web content.")
    structured_output_schema: str | None = Field(default=None, validation_alias="structuredOutputSchema", serialization_alias="structuredOutputSchema", description="A JSON schema (as a string) defining the desired response structure when using `structured` output type. The root element must be an object type.", json_schema_extra={'format': 'json'})
    include_sources: bool | None = Field(default=None, validation_alias="includeSources", serialization_alias="includeSources", description="When using `structured` output type, include source citations in the response. Note that enabling this modifies the response schema structure.")
    include_images: bool | None = Field(default=None, validation_alias="includeImages", serialization_alias="includeImages", description="Include images in the search results alongside text content.")
    from_date: str | None = Field(default=None, validation_alias="fromDate", serialization_alias="fromDate", description="Filter results to content published on or after this date, specified in ISO 8601 format (YYYY-MM-DD). Must be after 1970-01-01 and before the `toDate` if provided.")
    to_date: str | None = Field(default=None, validation_alias="toDate", serialization_alias="toDate", description="Filter results to content published on or before this date, specified in ISO 8601 format (YYYY-MM-DD). Must be after 1970-01-01 and after the `fromDate` if provided.")
    include_domains: list[str] | None = Field(default=None, validation_alias="includeDomains", serialization_alias="includeDomains", description="Restrict search to specific domains only. Provide up to 100 domain names. By default, all domains are searched.")
    exclude_domains: list[str] | None = Field(default=None, validation_alias="excludeDomains", serialization_alias="excludeDomains", description="Exclude specific domains from search results. By default, no domains are excluded.")
    include_inline_citations: bool | None = Field(default=None, validation_alias="includeInlineCitations", serialization_alias="includeInlineCitations", description="When using `sourcedAnswer` output type, include inline citations within the answer text to indicate source attribution.")
    max_results: float | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of results to return. The actual number of results returned will not exceed this value.")
    depth: Literal["deep", "fast", "standard"] = Field(default=..., description="Controls search precision and comprehensiveness. Use `fast` for quick, focused queries; `standard` for broader multi-topic queries with agentic search; `deep` for comprehensive results across multiple iterations of agentic search.")
    output_type: Literal["searchResults", "sourcedAnswer", "structured"] = Field(default=..., validation_alias="outputType", serialization_alias="outputType", description="Specifies the response format. Use `searchResults` for raw search results, `sourcedAnswer` for an answer with source attribution, or `structured` for a custom JSON format defined by `structuredOutputSchema`.")
class SearchRequest(StrictModel):
    """Retrieve web content by natural language query with configurable search depth, output formatting, and result filtering. Supports structured responses, date ranges, domain filtering, and optional citations or images."""
    body: SearchRequestBody

# Operation: create_research_task
class CreateResearchRequestBody(StrictModel):
    q: str = Field(default=..., description="The natural language question or research topic you want to investigate. Examples: 'What is Microsoft's 2024 revenue?' or 'Latest developments in quantum computing'.")
    structured_output_schema: str | None = Field(default=None, validation_alias="structuredOutputSchema", serialization_alias="structuredOutputSchema", description="A JSON schema (as a string) defining the desired response structure when using `structured` output type. The schema root must be an object type. Required only when `outputType` is set to `structured`.", json_schema_extra={'format': 'json'})
    include_sources: bool | None = Field(default=None, validation_alias="includeSources", serialization_alias="includeSources", description="When using `structured` output type, set to `true` to include source citations in the response. Note that enabling this modifies the response schema structure. Defaults to `false`.")
    include_images: bool | None = Field(default=None, validation_alias="includeImages", serialization_alias="includeImages", description="Set to `true` to include relevant images in the research results. Defaults to `false`.")
    from_date: str | None = Field(default=None, validation_alias="fromDate", serialization_alias="fromDate", description="Filter results to only include sources published on or after this date, specified in ISO 8601 format (YYYY-MM-DD). Must be after 1970-01-01 and before `toDate` if both are provided.")
    to_date: str | None = Field(default=None, validation_alias="toDate", serialization_alias="toDate", description="Filter results to only include sources published on or before this date, specified in ISO 8601 format (YYYY-MM-DD). Must be after 1970-01-01 and after `fromDate` if both are provided.")
    include_domains: list[str] | None = Field(default=None, validation_alias="includeDomains", serialization_alias="includeDomains", description="Restrict search to specific domains only. Provide up to 100 domain names (e.g., 'microsoft.com', 'github.com'). By default, all domains are searched.")
    exclude_domains: list[str] | None = Field(default=None, validation_alias="excludeDomains", serialization_alias="excludeDomains", description="Exclude specific domains from the search results. Provide domain names to filter out (e.g., 'wikipedia.com'). By default, no domains are excluded.")
    include_inline_citations: bool | None = Field(default=None, validation_alias="includeInlineCitations", serialization_alias="includeInlineCitations", description="When using `sourcedAnswer` output type, set to `true` to include inline citations within the answer text. Defaults to `false`.")
    max_results: float | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of search results to return. The actual number of results returned will not exceed this value.")
    output_type: Literal["sourcedAnswer", "structured"] = Field(default=..., validation_alias="outputType", serialization_alias="outputType", description="The format for the research response. Use `sourcedAnswer` for a natural language answer with optional citations, or `structured` for a custom-formatted response matching the provided `structuredOutputSchema`.")
class CreateResearchRequest(StrictModel):
    """Creates an asynchronous web research task that performs comprehensive research based on a natural language question. Returns structured or sourced answers with optional filtering by date range, domains, and result count."""
    body: CreateResearchRequestBody

# Operation: get_research
class GetResearchRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the research task to retrieve.")
class GetResearchRequest(StrictModel):
    """Retrieves detailed information about a specific research task by its identifier. This endpoint is currently in beta and may be subject to changes."""
    path: GetResearchRequestPath

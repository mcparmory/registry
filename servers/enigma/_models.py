"""
Enigma MCP Server - Pydantic Models

Generated: 2026-04-07 11:44:26 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "GetBusinessesEnigmaIdRequest",
    "PostBusinessesMatchRequest",
    "PostEvaluationSanctionsScreenRequest",
    "PostV1KybRequest",
    "PostEvaluationSanctionsScreenBodySearchesItem",
    "PostV1KybBodyDataAddressesItem",
    "PostV1KybBodyDataPersonsItem",
    "PostV1KybBodyDataPersonsToScreenItem",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: match_business
class PostBusinessesMatchRequestQuery(StrictModel):
    show_non_matches: int | None = Field(default=None, description="Include non-matching results (where is_matched is false) in the response. Disabled by default to return only confirmed matches.")
    match_threshold: float | None = Field(default=None, description="Minimum confidence score required for a match to be included in results, on a scale from 0 to 1. Defaults to 0.5 (50% confidence).")
    top_n: int | None = Field(default=None, description="Maximum number of matching results to return. Defaults to returning only the single best match.")
    business_entity_type: Literal["business", "business_location", "registrations"] | None = Field(default=None, description="Type of Enigma profile data to return: business entity records, business location records, or registration records. Defaults to business location results.")
class PostBusinessesMatchRequestBody(StrictModel):
    address: dict[str, Any] | None = Field(default=None, description="The company's mailing address or physical site address. Used to improve matching accuracy when provided alongside other company details.")
    person: dict[str, Any] | None = Field(default=None, description="A person associated with the company such as an owner, officer, or attorney. Including person details can improve matching precision.")
class PostBusinessesMatchRequest(StrictModel):
    """Match a business to an Enigma profile using company details and optional person information. Returns matching profiles with configurable confidence thresholds and result limits."""
    query: PostBusinessesMatchRequestQuery | None = None
    body: PostBusinessesMatchRequestBody | None = None

# Operation: get_business
class GetBusinessesEnigmaIdRequestPath(StrictModel):
    enigma_id: str = Field(default=..., description="The unique Enigma identifier for the business. This ID is provided in responses from other business endpoints.")
class GetBusinessesEnigmaIdRequestQuery(StrictModel):
    attrs: str | None = Field(default=None, description="Request specific premium attributes by providing their codes as a comma-separated list. Only requested attributes will be included in the response.")
    lookback_months: int | None = Field(default=None, description="Specify how many months of historical data to retrieve for attributes with monthly tracking. Use any positive integer for a specific number of months, or use an asterisk (*) to return all available historical data. Defaults to 1 month if not specified.")
class GetBusinessesEnigmaIdRequest(StrictModel):
    """Retrieve detailed business profile information using an Enigma ID, optionally including premium attributes and historical data."""
    path: GetBusinessesEnigmaIdRequestPath
    query: GetBusinessesEnigmaIdRequestQuery | None = None

# Operation: verify_business
class PostV1KybRequestQuery(StrictModel):
    package: Literal["identify", "verify"] | None = Field(default=None, description="The data package scope for returned attributes. Choose 'identify' for basic identification data or 'verify' (default) for comprehensive verification attributes.")
    attrs: str | None = Field(default=None, description="Comma-separated list of additional attributes beyond the selected package, such as watchlist screening, tax ID verification, social security verification, or bankruptcy history.")
    match_threshold: float | None = Field(default=None, description="Minimum confidence score (0 to 1) required to return a candidate match. Lower values return more candidates; higher values return only stronger matches. Defaults to 0.5.", ge=0, le=1)
    top_n: int | None = Field(default=None, description="Maximum number of matches to return, ordered by confidence. Each result will meet or exceed the match_threshold. Defaults to returning the single best match.", ge=1)
class PostV1KybRequestBodyData(StrictModel):
    persons_to_screen: list[PostV1KybBodyDataPersonsToScreenItem] | None = Field(default=None, validation_alias="persons_to_screen", serialization_alias="persons_to_screen", description="Array of persons to screen against watchlists and sanctions lists. Accepts up to 4 individuals.")
    names: list[str] | None = Field(default=None, validation_alias="names", serialization_alias="names", description="Array of business names to match against records. Accepts up to 2 names; useful for matching variations or alternate legal names.")
    addresses: list[PostV1KybBodyDataAddressesItem] | None = Field(default=None, validation_alias="addresses", serialization_alias="addresses", description="Array of business addresses to match against records. Accepts up to 2 addresses; useful for matching current and historical locations.")
    persons: list[PostV1KybBodyDataPersonsItem] | None = Field(default=None, validation_alias="persons", serialization_alias="persons", description="Array of persons associated with the business (owners, officers, principals). Accepts up to 1 person record.")
    websites: list[str] | None = Field(default=None, validation_alias="websites", serialization_alias="websites", description="Array of business website URLs. Accepts up to 1 website for business verification.")
    tins: list[str] | None = Field(default=None, validation_alias="tins", serialization_alias="tins", description="Array of Taxpayer Identification Numbers (TINs) to verify against business records. Accepts up to 1 TIN.")
class PostV1KybRequestBody(StrictModel):
    data: PostV1KybRequestBodyData | None = None
class PostV1KybRequest(StrictModel):
    """Verify a business entity against authoritative state records and official datasets. Returns registration, industry, and optional sanctions screening data to support customer verification workflows."""
    query: PostV1KybRequestQuery | None = None
    body: PostV1KybRequestBody | None = None

# Operation: screen_sanctions
class PostEvaluationSanctionsScreenRequestHeader(StrictModel):
    x_api_key: str = Field(default=..., validation_alias="x-api-key", serialization_alias="x-api-key", description="API authentication key required for all requests.")
    account_name: str | None = Field(default=None, validation_alias="Account-Name", serialization_alias="Account-Name", description="Optional account identifier to scope the screening request to a specific account context (e.g., 'public_evaluation').")
class PostEvaluationSanctionsScreenRequestBodyConfigurationOverridesEntityWeights(StrictModel):
    person_name: float | None = Field(default=None, validation_alias="person_name", serialization_alias="person_name", description="Relevance weight for person name matching in entity searches, expressed as a numeric score.")
    dob: float | None = Field(default=None, validation_alias="dob", serialization_alias="dob", description="Relevance weight for date of birth matching in entity searches, expressed as a numeric score.")
    country_of_affiliation: float | None = Field(default=None, validation_alias="country_of_affiliation", serialization_alias="country_of_affiliation", description="Relevance weight for country of affiliation matching in entity searches, expressed as a numeric score.")
    address: float | None = Field(default=None, validation_alias="address", serialization_alias="address", description="Relevance weight for address matching in entity searches, expressed as a numeric score.")
    org_name: float | None = Field(default=None, validation_alias="org_name", serialization_alias="org_name", description="Relevance weight for organization name matching in entity searches, expressed as a numeric score.")
class PostEvaluationSanctionsScreenRequestBodyConfigurationOverridesEntity(StrictModel):
    max_results: int | None = Field(default=None, validation_alias="max_results", serialization_alias="max_results", description="Maximum number of results to return per search. Defaults to a system-defined limit if not specified.")
    weights: PostEvaluationSanctionsScreenRequestBodyConfigurationOverridesEntityWeights | None = None
class PostEvaluationSanctionsScreenRequestBodyConfigurationOverridesGeneral(StrictModel):
    entity_detail_level: Literal["minimum", "standard", "full"] | None = Field(default=None, validation_alias="entity_detail_level", serialization_alias="entity_detail_level", description="Controls the depth of information returned for matched entities: 'minimum' for basic data, 'standard' for typical details, or 'full' for comprehensive information.")
class PostEvaluationSanctionsScreenRequestBodyConfigurationOverrides(StrictModel):
    list_groups: list[str] | None = Field(default=None, validation_alias="list_groups", serialization_alias="list_groups", description="Watchlist groups to screen against (e.g., 'pos/sdn/all', 'pos/non_sdn/all'). If omitted, all configured groups are screened.")
    entity: PostEvaluationSanctionsScreenRequestBodyConfigurationOverridesEntity | None = None
    general: PostEvaluationSanctionsScreenRequestBodyConfigurationOverridesGeneral | None = None
class PostEvaluationSanctionsScreenRequestBody(StrictModel):
    tag: str = Field(default=..., description="Unique identifier or description for this screening request, used for tracking and audit purposes.")
    query_type: str = Field(default=..., description="The query type configured for your account that determines screening behavior and data sources (e.g., 'enigma_data').")
    searches: list[PostEvaluationSanctionsScreenBodySearchesItem] = Field(default=..., description="Array of search objects defining the entities or text to screen. Each search specifies the type (ENTITY or TEXT) and relevant search criteria.")
    configuration_overrides: PostEvaluationSanctionsScreenRequestBodyConfigurationOverrides | None = None
class PostEvaluationSanctionsScreenRequest(StrictModel):
    """Screen customers and transactions against sanctions lists and other watchlists. Supports entity and text-based searches across configured watchlist groups to identify potential compliance risks."""
    header: PostEvaluationSanctionsScreenRequestHeader
    body: PostEvaluationSanctionsScreenRequestBody

# ============================================================================
# Component Models
# ============================================================================

class PostEvaluationSanctionsScreenBodySearchesItemEntityDescription(PermissiveModel):
    """Entity details for ENTITY type searches"""
    person_name: list[str] | None = Field(None, description="Person name(s)")
    dob: list[str] | None = Field(None, description="Date of birth(s)")
    country_of_affiliation: list[str] | None = Field(None, description="Country/countries of affiliation")
    address: list[str] | None = Field(None, description="Address(es)")
    org_name: list[str] | None = Field(None, description="Organization name(s)")

class PostEvaluationSanctionsScreenBodySearchesItem(PermissiveModel):
    type_: Literal["ENTITY", "TEXT"] = Field(..., validation_alias="type", serialization_alias="type", description="Search type")
    tag: str | None = Field(None, description="Optional identifier for the search")
    entity_description: PostEvaluationSanctionsScreenBodySearchesItemEntityDescription | None = Field(None, description="Entity details for ENTITY type searches")
    text: str | None = Field(None, description="Unstructured text for TEXT type searches")

class PostV1KybBodyDataAddressesItem(PermissiveModel):
    street_address1: str | None = None
    street_address2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None

class PostV1KybBodyDataPersonsItem(PermissiveModel):
    first_name: str | None = None
    last_name: str | None = None
    ssn: str | None = None

class PostV1KybBodyDataPersonsToScreenItemAddress(PermissiveModel):
    street_address1: str | None = None
    street_address2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None

class PostV1KybBodyDataPersonsToScreenItem(PermissiveModel):
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: str | None = Field(None, json_schema_extra={'format': 'date'})
    address: PostV1KybBodyDataPersonsToScreenItemAddress | None = None


# Rebuild models to resolve forward references (required for circular refs)
PostEvaluationSanctionsScreenBodySearchesItem.model_rebuild()
PostEvaluationSanctionsScreenBodySearchesItemEntityDescription.model_rebuild()
PostV1KybBodyDataAddressesItem.model_rebuild()
PostV1KybBodyDataPersonsItem.model_rebuild()
PostV1KybBodyDataPersonsToScreenItem.model_rebuild()
PostV1KybBodyDataPersonsToScreenItemAddress.model_rebuild()

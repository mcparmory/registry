"""
Opencage Geocoding MCP Server - Pydantic Models

Generated: 2026-05-12 11:59:19 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "GetGeojsonRequest",
    "GetJsonRequest",
    "GetXmlRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: search_location
class GetJsonRequestQuery(StrictModel):
    q: str = Field(default=..., description="The location to geocode: either a place name (e.g., 'Times Square, New York, USA'), landmark name (e.g., 'Eiffel Tower'), or coordinates in lat,lng format. Minimum 2 characters.", min_length=2, examples=['52.5432379, 13.4142133', 'Times Square, New York, USA', 'Eiffel Tower'])
    abbrv: bool | None = Field(default=None, description="When enabled, abbreviates the formatted address field in results (e.g., 'USA' instead of 'United States of America').")
    address_only: bool | None = Field(default=None, description="When enabled, returns only the address portion in the formatted field, excluding additional details like business names or landmarks.")
    bounds: str | None = Field(default=None, description="Restricts results to a geographic area using a bounding box defined by southwest and northeast corner coordinates in lat,lng format.", examples=['-0.563160,51.280430,0.278970,51.683979'])
    countrycode: str | None = Field(default=None, description="Limits results to specific countries using a comma-separated list of ISO 3166-1 Alpha 2 country codes (e.g., 'de' for Germany, 'ch,li' for Switzerland and Liechtenstein).", min_length=2, examples=['de', 'at', 'ch,li'])
    language: str | None = Field(default=None, description="Sets the language for results using an IETF language code (e.g., 'de' for German, 'pt-BR' for Brazilian Portuguese) or 'native' to use the location's native language.", examples=['de', 'pt-BR', 'native'])
    limit: int | None = Field(default=None, description="Maximum number of results to return, between 1 and 100. Defaults to 10 results.", ge=1, le=100, examples=[1, 3])
    proximity: str | None = Field(default=None, description="Biases results toward a specific location using coordinates in lat,lng format, prioritizing nearby matches.", pattern='^-?[0-9]{1,2}(\\.[0-9]+)?,\\s*-?[0-9]{1,3}(\\.[0-9]+)?$', examples=['52.3877830, 9.7334394', '51.522618,-0.102530', '42.359578,-71.091982'])
    roadinfo: bool | None = Field(default=None, description="When enabled, geocodes to the nearest road and includes detailed road information in the results.")
class GetJsonRequest(StrictModel):
    """Search for geographic locations by address, place name, or coordinates and return detailed geocoding results in JSON format."""
    query: GetJsonRequestQuery

# Operation: search_location_xml
class GetXmlRequestQuery(StrictModel):
    q: str = Field(default=..., description="The location to geocode: either a place name/address (e.g., 'Times Square, New York, USA') or latitude,longitude coordinates (e.g., '52.5432379, 13.4142133'). Minimum 2 characters.", min_length=2, examples=['52.5432379, 13.4142133', 'Times Square, New York, USA', 'Eiffel Tower'])
    abbrv: bool | None = Field(default=None, description="When enabled, abbreviates the formatted address field in results (e.g., 'St' instead of 'Street').")
    address_only: bool | None = Field(default=None, description="When enabled, returns only the address portion in the formatted field, excluding additional details.")
    bounds: str | None = Field(default=None, description="Restricts results to a geographic bounding box defined by southwest and northeast corner coordinates in the format: min_longitude,min_latitude,max_longitude,max_latitude.", examples=['-0.563160,51.280430,0.278970,51.683979'])
    countrycode: str | None = Field(default=None, description="Limits results to specific countries using a comma-separated list of ISO 3166-1 Alpha 2 country codes (e.g., 'de' for Germany, 'ch,li' for Switzerland and Liechtenstein).", min_length=2, examples=['de', 'at', 'ch,li'])
    language: str | None = Field(default=None, description="Returns results in the specified language using IETF language codes (e.g., 'de' for German, 'pt-BR' for Brazilian Portuguese), or 'native' for the region's native language.", examples=['de', 'pt-BR', 'native'])
    limit: int | None = Field(default=None, description="Maximum number of results to return, between 1 and 100. Defaults to 10 if not specified.", ge=1, le=100, examples=[1, 3])
    proximity: str | None = Field(default=None, description="Biases results toward a specific location using latitude,longitude coordinates, prioritizing nearby matches.", pattern='^-?[0-9]{1,2}(\\.[0-9]+)?,\\s*-?[0-9]{1,3}(\\.[0-9]+)?$', examples=['52.3877830, 9.7334394', '51.522618,-0.102530', '42.359578,-71.091982'])
    roadinfo: bool | None = Field(default=None, description="When enabled, geocodes to the nearest road and includes road information annotations in the results.")
class GetXmlRequest(StrictModel):
    """Geocode a location query or coordinate pair and return results in XML format. Supports forward geocoding (address to coordinates) and reverse geocoding (coordinates to address)."""
    query: GetXmlRequestQuery

# Operation: search_geojson
class GetGeojsonRequestQuery(StrictModel):
    q: str = Field(default=..., description="The location to geocode: either a place name (e.g., 'Times Square, New York, USA'), landmark name (e.g., 'Eiffel Tower'), or coordinates in lat,lng format. Minimum 2 characters required.", min_length=2, examples=['52.5432379, 13.4142133', 'Times Square, New York, USA', 'Eiffel Tower'])
    address_only: bool | None = Field(default=None, description="When enabled, limits the formatted field in results to address details only, excluding other metadata.")
    bounds: str | None = Field(default=None, description="Restrict results to a geographic area by specifying a bounding box as four coordinates: southwest corner latitude, southwest corner longitude, northeast corner latitude, northeast corner longitude.", examples=['-0.563160,51.280430,0.278970,51.683979'])
    countrycode: str | None = Field(default=None, description="Limit results to specific countries by providing a comma-separated list of ISO 3166-1 Alpha 2 country codes (e.g., 'de' for Germany, 'ch,li' for Switzerland and Liechtenstein).", min_length=2, examples=['de', 'at', 'ch,li'])
    language: str | None = Field(default=None, description="Return results in a specific language using IETF language codes (e.g., 'de' for German, 'pt-BR' for Brazilian Portuguese), or use 'native' for the location's native language.", examples=['de', 'pt-BR', 'native'])
    limit: int | None = Field(default=None, description="Maximum number of results to return. Must be between 1 and 100; defaults to 10 if not specified.", ge=1, le=100, examples=[1, 3])
    proximity: str | None = Field(default=None, description="Bias results toward a specific location by providing coordinates in lat,lng format. Useful for prioritizing results near the user's current location.", pattern='^-?[0-9]{1,2}(\\.[0-9]+)?,\\s*-?[0-9]{1,3}(\\.[0-9]+)?$', examples=['52.3877830, 9.7334394', '51.522618,-0.102530', '42.359578,-71.091982'])
    roadinfo: bool | None = Field(default=None, description="When enabled, geocodes to the nearest road and includes detailed road information in the results.")
class GetGeojsonRequest(StrictModel):
    """Search for geographic locations and return results in GeoJSON format. Supports geocoding by address, place name, or coordinates with optional filtering and result customization."""
    query: GetGeojsonRequestQuery

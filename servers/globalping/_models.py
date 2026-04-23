"""
Globalping MCP Server - Pydantic Models

Generated: 2026-04-23 21:20:15 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "CreateMeasurementRequest",
    "GetMeasurementRequest",
    "MeasurementRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: create_measurement
class CreateMeasurementRequestBody(StrictModel):
    """Use the request body to set the measurement parameters."""
    body: MeasurementRequest | None = Field(default=None, description="Measurement configuration specifying the probe type (ping, traceroute, dns, http), target host or URL, geographic locations or probe IDs to measure from, and optional measurement parameters. Locations can be filtered by country code, region, city, ASN, cloud provider, or magic string matching. Reuse a previous measurement's ID to run identical probes across multiple measurements.", examples=[{'type': 'ping', 'target': 'cdn.jsdelivr.net', 'locations': [{'country': 'DE'}, {'country': 'PL'}]}, {'type': 'ping', 'target': 'cdn.jsdelivr.net', 'locations': [{'country': 'DE', 'limit': 4}, {'country': 'PL', 'limit': 2}]}, {'type': 'ping', 'target': 'cdn.jsdelivr.net', 'locations': [{'magic': 'FR'}, {'magic': 'Poland'}, {'magic': 'Berlin+Germany'}, {'magic': 'California'}, {'magic': 'Europe'}, {'magic': 'Western Europe'}, {'magic': 'AS13335'}, {'magic': 'aws-us-east-1'}, {'magic': 'Google'}]}, {'type': 'ping', 'target': 'cdn.jsdelivr.net', 'measurementOptions': {'packets': 6}}, {'type': 'ping', 'target': 'cdn.jsdelivr.net', 'locations': '1wzMrzLBZfaPoT1c'}])
class CreateMeasurementRequest(StrictModel):
    """Initiates a new network measurement that runs asynchronously. Monitor progress via the URL provided in the Location response header, or enable real-time updates by setting inProgressUpdates to true for interactive applications."""
    body: CreateMeasurementRequestBody | None = None

# Operation: poll_measurement
class GetMeasurementRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the measurement to retrieve. This ID is provided in the Location header when the measurement is created.")
class GetMeasurementRequest(StrictModel):
    """Retrieve the current status and results of a measurement. Use polling to check status until the measurement completes, waiting at least 500ms between requests."""
    path: GetMeasurementRequestPath

# ============================================================================
# Component Models
# ============================================================================

class MeasurementDnsOptionsQuery(StrictModel):
    """The DNS query properties."""
    type_: Literal["A", "AAAA", "ANY", "CNAME", "DNSKEY", "DS", "HTTPS", "MX", "NS", "NSEC", "PTR", "RRSIG", "SOA", "TXT", "SRV", "SVCB"] | None = Field(None, validation_alias="type", serialization_alias="type")

class MeasurementDnsOptions(StrictModel):
    query: MeasurementDnsOptionsQuery | None = Field(None, description="The DNS query properties.")
    resolver: str | str | str | None = None
    protocol: Literal["TCP", "UDP"] | None = None
    port: int | None = Field(53, description="The port number to send the query to.", ge=0, le=65535)
    ip_version: Literal[4, 6] | None = Field(None, validation_alias="ipVersion", serialization_alias="ipVersion")
    trace_: bool | None = Field(False, validation_alias="trace", serialization_alias="trace", description="Toggles tracing of the delegation path from the root servers down to the target domain name.\n")

class MeasurementHttpOptionsRequest(StrictModel):
    """The HTTP request properties."""
    host: str | None = Field(None, description="An optional override for the `Host` header. The default value is based on the `target`.\n")
    path: str | None = Field(None, description="The path portion of the URL.")
    query: str | None = Field(None, description="The query string portion of the URL.")
    method: Literal["HEAD", "GET", "OPTIONS"] | None = None
    headers: dict[str, str] | None = Field(None, description="Additional request headers. Note that the `Host` and `User-Agent` are reserved and internally overridden.\n")

class MeasurementHttpOptions(StrictModel):
    request: MeasurementHttpOptionsRequest | None = Field(None, description="The HTTP request properties.")
    resolver: str | str | None = None
    protocol: Literal["HTTP", "HTTPS", "HTTP2"] | None = None
    port: int | None = Field(80, description="The port number to use.", ge=0, le=65535)
    ip_version: Literal[4, 6] | None = Field(None, validation_alias="ipVersion", serialization_alias="ipVersion")

class MeasurementMtrOptions(StrictModel):
    packets: int | None = Field(3, description="The number of packets to send to each hop.", ge=1, le=16)
    protocol: Literal["ICMP", "TCP", "UDP"] | None = None
    port: int | None = Field(80, description="The destination port for the packets. Applies only for the `TCP` and `UDP` protocols.\n", ge=0, le=65535)
    ip_version: Literal[4, 6] | None = Field(None, validation_alias="ipVersion", serialization_alias="ipVersion")

class MeasurementOptionsConditions(PermissiveModel):
    pass

class MeasurementPingOptions(StrictModel):
    packets: int | None = Field(3, description="The number of packets to send.", ge=1, le=16)
    protocol: Literal["ICMP", "TCP"] | None = None
    port: int | None = Field(80, description="The destination port for the packets. Applies only for the `TCP` protocol.\n", ge=0, le=65535)
    ip_version: Literal[4, 6] | None = Field(None, validation_alias="ipVersion", serialization_alias="ipVersion")

class MeasurementTracerouteOptions(StrictModel):
    protocol: Literal["ICMP", "TCP", "UDP"] | None = None
    port: int | None = Field(80, description="The destination port for the packets. Applies only for the `TCP` protocol.\n", ge=0, le=65535)
    ip_version: Literal[4, 6] | None = Field(None, validation_alias="ipVersion", serialization_alias="ipVersion")

class Tags(RootModel[list[str]]):
    pass

class MeasurementLocationOption(StrictModel):
    continent: Literal["AF", "AN", "AS", "EU", "NA", "OC", "SA"] | None = None
    region: Literal["Northern Africa", "Eastern Africa", "Middle Africa", "Southern Africa", "Western Africa", "Caribbean", "Central America", "South America", "Northern America", "Central Asia", "Eastern Asia", "South-eastern Asia", "Southern Asia", "Western Asia", "Eastern Europe", "Northern Europe", "Southern Europe", "Western Europe", "Australia and New Zealand", "Melanesia", "Micronesia", "Polynesia"] | None = None
    country: str | None = None
    state: str | None = None
    city: str | None = None
    asn: int | None = None
    network: str | None = None
    tags: Tags | None = None
    magic: str | None = Field(None, description="Locations defined in a single string instead of the respective location properties.\nThe API performs fuzzy matching on the `country`, `city`, `state` (using `US-` prefix, e.g., `US-NY`), `continent`, `region`, `asn` (using `AS` prefix, e.g., `AS123`), `tags`, and `network` values.\nSupports full names, ISO codes (where applicable), and common aliases.\nMultiple conditions can be combined using the `+` character, which behaves as a logical `AND`.\n\nNote that in some cases, the names of cities, states, and countries, as well as the ISO codes of countries and continents, overlap. Additionally, city names are not unique across countries.\nWe recommend that you:\n - refer to US states via their full [ISO 3166-2](https://en.wikipedia.org/wiki/ISO_3166-2:US) codes, e.g., `US-NY`,\n - refer to cities in combination with their country or US state,\n - refer to continents by their name (not the two letter codes).\n")
    limit: int | None = Field(1, description="The maximum number of probes that should run the measurement in this location.\nNon-authenticated requests are limited to a maximum of 50 probes.\nThe result count might be lower if there aren't enough probes available in this location.\nMutually exclusive with the global `limit` property.\n", ge=1, le=200)

class MeasurementRequest(StrictModel):
    type_: Literal["ping", "traceroute", "dns", "mtr", "http"] = Field(..., validation_alias="type", serialization_alias="type")
    target: str
    in_progress_updates: bool | None = Field(False, validation_alias="inProgressUpdates", serialization_alias="inProgressUpdates", description="Indicates whether you want to get partial results while the measurement is still running:\n- If `true`, partial results are returned as soon as they are available, and you can present them to the user in real time. Note that only the first 5 tests from the `results` array will update in real time.\n- If `false`, the result of each test is updated only after the test finishes.\n")
    locations: list[MeasurementLocationOption] | str | None = None
    limit: int | None = None
    measurement_options: MeasurementPingOptions | MeasurementTracerouteOptions | MeasurementDnsOptions | MeasurementMtrOptions | MeasurementHttpOptions | None = Field(None, validation_alias="measurementOptions", serialization_alias="measurementOptions")


# Rebuild models to resolve forward references (required for circular refs)
MeasurementDnsOptions.model_rebuild()
MeasurementDnsOptionsQuery.model_rebuild()
MeasurementHttpOptions.model_rebuild()
MeasurementHttpOptionsRequest.model_rebuild()
MeasurementLocationOption.model_rebuild()
MeasurementMtrOptions.model_rebuild()
MeasurementOptionsConditions.model_rebuild()
MeasurementPingOptions.model_rebuild()
MeasurementRequest.model_rebuild()
MeasurementTracerouteOptions.model_rebuild()
Tags.model_rebuild()

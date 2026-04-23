"""
Ip2location.io Ip Geolocation MCP Server - Pydantic Models

Generated: 2026-04-23 21:24:00 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "IpGeolocationRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: lookup_ip_geolocation
class IpGeolocationRequestQuery(StrictModel):
    ip: str = Field(default=..., description="The IP address (IPv4 or IPv6 format) to geolocate. If omitted, the server's IP address will be used instead.")
    format_: Literal["json", "xml"] | None = Field(default=None, validation_alias="format", serialization_alias="format", description="The response format: either JSON or XML. Defaults to JSON if not specified.")
    lang: Literal["ar", "cs", "da", "de", "en", "es", "et", "fi", "fr", "ga", "it", "ja", "ko", "ms", "nl", "pt", "ru", "sv", "tr", "vi", "zh-cn", "zh-tw"] | None = Field(default=None, description="ISO 639-1 language code for translating location names (continent, country, region, city). Only available on Plus and Security plans. Supports major languages including English, Spanish, French, German, Chinese, Japanese, and others.")
class IpGeolocationRequest(StrictModel):
    """Retrieve geolocation information for a given IP address, including continent, country, region, and city details. Supports both IPv4 and IPv6 addresses with optional response formatting and language translation."""
    query: IpGeolocationRequestQuery

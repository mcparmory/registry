"""
Google Maps Platform MCP Server - Pydantic Models

Generated: 2026-05-12 11:31:00 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "AutocompleteRequest",
    "DirectionsRequest",
    "DistanceMatrixRequest",
    "ElevationRequest",
    "FindPlaceFromTextRequest",
    "GeocodeRequest",
    "GeolocateRequest",
    "NearbySearchRequest",
    "NearestRoadsRequest",
    "PlaceDetailsRequest",
    "PlacePhotoRequest",
    "QueryAutocompleteRequest",
    "SnapToRoadsRequest",
    "StreetViewMetadataRequest",
    "StreetViewRequest",
    "TextSearchRequest",
    "TimezoneRequest",
    "CellTower",
    "WiFiAccessPoint",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: locate_device
class GeolocateRequestBody(StrictModel):
    """The request body must be formatted as JSON."""
    home_mobile_country_code: int | None = Field(default=None, validation_alias="homeMobileCountryCode", serialization_alias="homeMobileCountryCode", description="The Mobile Country Code (MCC) of the primary cell tower. Used to identify the country of the cellular network.")
    home_mobile_network_code: int | None = Field(default=None, validation_alias="homeMobileNetworkCode", serialization_alias="homeMobileNetworkCode", description="The Mobile Network Code (MNC) of the primary cell tower. For GSM and WCDMA networks this is the MNC; for CDMA networks this is the System ID (SID).")
    radio_type: str | None = Field(default=None, validation_alias="radioType", serialization_alias="radioType", description="The type of mobile radio technology in use. Supported values are lte, gsm, cdma, and wcdma. Including this value improves location accuracy when available.")
    carrier: str | None = Field(default=None, description="The name of the cellular carrier or network operator.")
    consider_ip: str | None = Field(default=None, validation_alias="considerIp", serialization_alias="considerIp", description="Whether to use IP address geolocation as a fallback when cell tower and WiFi signals are unavailable. Defaults to true; set to false to disable IP-based fallback.")
    cell_towers: list[CellTower] | None = Field(default=None, validation_alias="cellTowers", serialization_alias="cellTowers", description="An array of cell tower objects detected by the device. Each object should contain signal strength and tower identification data. Order does not affect results.")
    wifi_access_points: list[WiFiAccessPoint] | None = Field(default=None, validation_alias="wifiAccessPoints", serialization_alias="wifiAccessPoints", description="An array of at least two WiFi access point objects detected by the device. Each object should contain BSSID and signal strength data. More access points improve accuracy.")
class GeolocateRequest(StrictModel):
    """Determines a device's geographic location based on detected cell towers and WiFi access points. Returns coordinates with an accuracy radius, with optional fallback to IP-based geolocation."""
    body: GeolocateRequestBody | None = None

# Operation: calculate_directions
class DirectionsRequestQuery(StrictModel):
    alternatives: bool | None = Field(default=None, description="Allow the service to return multiple alternative routes. Only available for requests without intermediate waypoints. Note that providing alternatives may increase response time.")
    avoid: str | None = Field(default=None, description="Specify route features to avoid, such as tolls, highways, ferries, or indoor steps. Multiple restrictions can be combined using the pipe character separator.", examples=['highways', 'tolls|highways|ferries'])
    destination: str = Field(default=..., description="The destination location as a place ID (prefixed with 'place_id:'), street address, latitude/longitude coordinates, or plus code. Place IDs are recommended for accuracy and performance.")
    origin: str = Field(default=..., description="The starting location as a place ID (prefixed with 'place_id:'), street address, latitude/longitude coordinates, or plus code. Place IDs are recommended for accuracy and performance over addresses or raw coordinates.", examples=['Vancouver, BC', 'side_of_road:37.7663444,-122.4412006', 'heading=90:37.773279,-122.468780'])
    units: Literal["imperial", "metric"] | None = Field(default=None, description="The unit system for displaying distances in results. Choose 'metric' for kilometers and meters, or 'imperial' for miles and feet. Defaults to the origin country's standard system.")
    waypoints: str | None = Field(default=None, description="Intermediate locations to route through or stop at between origin and destination. Supports up to 25 waypoints using place IDs, addresses, coordinates, or encoded polylines separated by pipes. Use 'via:' prefix to route through without stopping, or 'optimize:true' to reorder waypoints for efficiency. Requests with 11+ waypoints or optimization incur higher billing.", examples=['MA|Lexington,MA', 'Charlestown,MA|via:Lexington,MA', 'optimize:true|Barossa+Valley,SA|Clare,SA|Connawarra,SA|McLaren+Vale,SA', 'ChIJGwVKWe5w44kRcr4b9E25-Go', '-34.92788%2C138.60008', 'enc:lexeF{~wsZejrPjtye@:', 'via:enc:wc~oAwquwMdlTxiKtqLyiK:|enc:c~vnAamswMvlTor@tjGi}L:| via:enc:udymA{~bxM:', 'side_of_road:via:enc:lexeF{~wsZejrPjtye@:'])
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(default=None, description="The language for returned results. Defaults to the Accept-Language header preference. Supports 40+ languages including regional variants like en-GB and pt-BR.")
    mode: Literal["driving", "bicycling", "transit", "walking"] | None = Field(default=None, description="The transportation mode for calculating directions. Choose 'driving' (default), 'walking', 'bicycling', or 'transit'. Transit directions support optional departure/arrival times and transit preferences.")
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(default=None, description="The region code as a two-character ccTLD to bias results toward a specific country. Defaults to 'en'. Use country-specific codes like 'uk' for United Kingdom or 'au' for Australia.")
    traffic_model: Literal["best_guess", "pessimistic", "optimistic"] | None = Field(default=None, description="Traffic prediction model for driving directions with a departure time. Choose 'best_guess' (default) for balanced predictions, 'pessimistic' for longer estimates, or 'optimistic' for shorter estimates.")
    transit_mode: str | None = Field(default=None, description="Preferred transit modes to prioritize in the route calculation. Supports 'bus', 'subway', 'train', 'tram', or 'rail' (combines train, tram, and subway). Multiple modes can be combined using pipe separators.")
    transit_routing_preference: Literal["less_walking", "fewer_transfers"] | None = Field(default=None, description="Transit routing preference to bias results. Choose 'less_walking' to minimize walking distance or 'fewer_transfers' to reduce the number of transit transfers.")
class DirectionsRequest(StrictModel):
    """Calculate directions and distances between locations using various transportation modes. Supports multiple routes, waypoints, and real-time traffic data for driving directions."""
    query: DirectionsRequestQuery

# Operation: get_elevation
class ElevationRequestQuery(StrictModel):
    samples: float | None = Field(default=None, description="Number of elevation samples to return along a path. Required when querying elevation along a path instead of discrete locations. Specifies how many evenly-distributed points along the path should be sampled for elevation data.")
class ElevationRequest(StrictModel):
    """Retrieve elevation data for specific locations or sample elevation along a path. The API returns elevation values relative to local mean sea level, with interpolated values for locations where exact measurements aren't available."""
    query: ElevationRequestQuery | None = None

# Operation: geocode_address
class GeocodeRequestQuery(StrictModel):
    address: str | None = Field(default=None, description="Street address or plus code to geocode. Use standard postal service format for the country (e.g., '24 Sussex Drive Ottawa ON'). Plus codes should be formatted as global codes (4-character area + 6+ character local code) or compound codes (6+ character local code with location). At least one of address or components is required.")
    bounds: list[str] | None = Field(default=None, description="Bounding box to bias results toward a specific viewport region. Specified as an array of two coordinate pairs [southwest, northeast] in latitude,longitude format. Results are influenced but not strictly restricted to this area.")
    components: list[str] | None = Field(default=None, description="Component filters to restrict results by address elements (postal_code, country, route, locality, administrative_area). Use pipe-separated key:value pairs. Country codes should be ISO 3166-1 format. Do not repeat country, postal_code, or route filters. At least one of address or components is required.")
    location_type: list[Literal["APPROXIMATE", "GEOMETRIC_CENTER", "RANGE_INTERPOLATED", "ROOFTOP"]] | None = Field(default=None, description="Filter results by location precision type using pipe-separated values. Options include ROOFTOP (street address precision), RANGE_INTERPOLATED (approximated between intersections), GEOMETRIC_CENTER (polyline/polygon centers), and APPROXIMATE (characterized as approximate). Acts as a post-search filter on returned results.")
    place_id: str | None = Field(default=None, description="Unique textual identifier for a place returned from Place Search. Use this to retrieve the address for a known place ID instead of searching by address or coordinates.")
    result_type: list[Literal["administrative_area_level_1", "administrative_area_level_2", "administrative_area_level_3", "administrative_area_level_4", "administrative_area_level_5", "airport", "colloquial_area", "country", "intersection", "locality", "natural_feature", "neighborhood", "park", "plus_code", "political", "postal_code", "premise", "route", "street_address", "sublocality", "subpremise"]] | None = Field(default=None, description="Filter results by address type using pipe-separated values. Supported types include street_address, route, intersection, locality, administrative areas (level 1-5), postal_code, country, airport, park, point_of_interest, and others. Acts as a post-search filter on returned results.")
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(default=None, description="Language code for result formatting. Defaults to English. Supports ISO 639-1 language codes with optional region variants (e.g., en-GB, pt-BR). Street addresses are returned in local language when possible; other components use the preferred language.")
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(default=None, description="Region code (ccTLD format) to bias results toward a specific country or region. Uses two-character country code top-level domains (e.g., 'uk' for United Kingdom, 'us' for United States). Influences result selection and ordering.")
class GeocodeRequest(StrictModel):
    """Convert addresses to geographic coordinates (geocoding) or coordinates to human-readable addresses (reverse geocoding). Supports street addresses, plus codes, and place IDs across multiple countries with varying accuracy levels."""
    query: GeocodeRequestQuery | None = None

# Operation: get_timezone
class TimezoneRequestQuery(StrictModel):
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(default=None, description="The language for the time zone name and results. Supports 40+ languages including major variants like English, Spanish, Chinese, and others. Defaults to English if not specified or falls back to the Accept-Language header preference.")
    location: str = Field(default=..., description="The geographic coordinates as a comma-separated latitude,longitude pair (e.g., 39.6034810,-119.6822510). Required to identify the location for time zone lookup.")
    timestamp: float = Field(default=..., description="The target date and time as a Unix timestamp (seconds since January 1, 1970 UTC). Used to determine whether daylight savings time applies at the specified location. Historical time zone changes are not considered.")
class TimezoneRequest(StrictModel):
    """Retrieves the time zone information for a specific geographic location, including the time zone name, UTC offset, and daylight savings offset for a given date and time."""
    query: TimezoneRequestQuery

# Operation: snap_coordinates_to_roads
class SnapToRoadsRequestQuery(StrictModel):
    path: list[str] = Field(default=..., description="A sequence of latitude/longitude coordinate pairs representing the GPS path to be snapped. Coordinates are formatted as comma-separated lat/lon values and separated by pipe characters (e.g., lat1,lon1|lat2,lon2). For best results, consecutive points should be within 300 meters of each other to ensure accurate snapping and handle GPS signal loss or noise.")
    interpolate: bool | None = Field(default=None, description="When enabled, generates additional interpolated points along the snapped road geometry to create a smooth, continuous path that follows road curves and geometry. The resulting path will typically contain more points than the original input. Defaults to false.")
class SnapToRoadsRequest(StrictModel):
    """Snaps GPS coordinates to the most likely road geometry, returning corrected points that align with actual road paths. Optionally interpolates additional points to create a smooth path following road geometry."""
    query: SnapToRoadsRequestQuery

# Operation: snap_points_to_roads
class NearestRoadsRequestQuery(StrictModel):
    points: list[str] = Field(default=..., description="A list of GPS coordinates to snap to roads, provided as latitude/longitude pairs separated by pipes. Each coordinate pair should be comma-separated (e.g., latitude,longitude|latitude,longitude). Supports up to 100 points; the points do not need to form a continuous path.")
class NearestRoadsRequest(StrictModel):
    """Snaps GPS coordinates to the nearest road segments. Accepts up to 100 latitude/longitude points and returns the closest matching road for each point, useful for map matching and route analysis."""
    query: NearestRoadsRequestQuery

# Operation: calculate_distance_matrix
class DistanceMatrixRequestQuery(StrictModel):
    avoid: str | None = Field(default=None, description="Specify route restrictions to avoid. Supports tolls, highways, ferries, and indoor steps. Note that restrictions bias results toward favorable routes but do not guarantee avoidance.")
    destinations: list[str] = Field(default=..., description="One or more destination locations where travel ends. Accepts place IDs (prefixed with 'place_id:'), addresses, latitude/longitude coordinates, plus codes, or encoded polylines. Place IDs are preferred for accuracy.")
    origins: list[str] = Field(default=..., description="One or more starting locations for travel calculation. Accepts place IDs (prefixed with 'place_id:'), addresses, latitude/longitude coordinates, plus codes, or encoded polylines. Multiple origins can be separated by pipe characters or provided as encoded polylines. Place IDs are preferred for accuracy.")
    units: Literal["imperial", "metric"] | None = Field(default=None, description="Unit system for displaying distance results. Choose between imperial (miles/feet) or metric (kilometers/meters). Note that distance values are always returned in meters regardless of this setting.")
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(default=None, description="Language for result text. Defaults to English. Supports 40+ languages including regional variants. The API returns street addresses in the local language when available, transliterated to the preferred language if necessary.")
    mode: Literal["driving", "bicycling", "transit", "walking"] | None = Field(default=None, description="Transportation mode for route calculation. Defaults to driving. Walking and bicycling may lack clear pedestrian or bicycle paths and will include warnings. Transit mode supports optional departure/arrival times and transit preferences.")
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(default=None, description="Region bias using two-character country code (ccTLD format). Influences result selection and ordering. Defaults to 'en'. Use country-specific codes like 'uk' for United Kingdom or 'gb' for ISO standard.")
    traffic_model: Literal["best_guess", "pessimistic", "optimistic"] | None = Field(default=None, description="Traffic prediction model for driving directions with departure times. 'best_guess' (default) balances historical and live traffic; 'pessimistic' estimates longer times; 'optimistic' estimates shorter times. Only applies to driving mode with specified departure_time.")
    transit_mode: str | None = Field(default=None, description="Preferred transit modes to favor in route calculation. Supports bus, subway, train, tram, and rail (combination of train/tram/subway). Multiple modes can be specified separated by pipe characters. Only applies to transit mode.")
    transit_routing_preference: Literal["less_walking", "fewer_transfers"] | None = Field(default=None, description="Transit route preferences to bias results. Choose 'less_walking' to minimize walking distance or 'fewer_transfers' to reduce transfer count. Only applies to transit mode.")
class DistanceMatrixRequest(StrictModel):
    """Calculate travel distances and durations between multiple origin and destination points using various transportation modes. Returns a matrix of distance and time values for each origin-destination pair based on Google Maps routing."""
    query: DistanceMatrixRequestQuery

# Operation: get_place_details
class PlaceDetailsRequestQuery(StrictModel):
    place_id: str = Field(default=..., description="Unique identifier for the place, obtained from a Place Search request. This ID is required to retrieve the place's detailed information.")
    fields: list[str] | None = Field(default=None, description="Comma-separated list of specific place data fields to return (e.g., formatted_address,name,geometry). Use forward slashes for nested fields (e.g., opening_hours/open_now). Omit to return default fields, or use '*' for all available fields. Fields are categorized as Basic (no extra charge), Contact, or Atmosphere (higher billing rates).", min_length=1, examples=[['formatted_address'], ['formatted_address', 'name', 'geometry'], ['opening_hours/open_now'], ['*']])
    sessiontoken: str | None = Field(default=None, description="Unique session identifier for grouping related autocomplete and details requests for billing optimization. Generate a fresh UUID for each new user session and reuse it across multiple requests within the same session.")
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(default=None, description="Language code for returned results (e.g., en, es, fr, ja). Defaults to English. The API will attempt to use the Accept-Language header if not specified. Affects address formatting and review translation preferences.")
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(default=None, description="Two-character country/region code (ccTLD format, e.g., us, gb, de) to bias results toward a specific region. Defaults to 'en'. Influences address interpretation and result prioritization.")
    reviews_sort: str | None = Field(default=None, description="Sort order for returned reviews: 'most_relevant' (default, language-aware) or 'newest' (chronological). Recommend displaying the sort method to end users.")
    reviews_no_translations: bool | None = Field(default=None, description="Set to true to return reviews in their original language without translation, or false/omitted to enable translation using the specified or preferred language.")
class PlaceDetailsRequest(StrictModel):
    """Retrieve comprehensive information about a specific place including address, contact details, opening hours, ratings, and reviews. Use a place ID from a prior search to fetch detailed establishment or location data."""
    query: PlaceDetailsRequestQuery

# Operation: search_place_by_text
class FindPlaceFromTextRequestQuery(StrictModel):
    fields: list[str] | None = Field(default=None, description="Comma-separated list of place data fields to return in the response. Omitting this parameter returns only the place_id. Fields are categorized as Basic (no additional charge), Contact, or Atmosphere (higher billing rates). Use forward slash notation for compound fields (e.g., opening_hours/open_now). Specify '*' to request all available fields.", min_length=1, examples=[['formatted_address'], ['formatted_address', 'name', 'geometry'], ['opening_hours/open_now'], ['*']])
    input_: str = Field(default=..., validation_alias="input", serialization_alias="input", description="The search text input, which can be a place name, street address, or phone number. The API returns candidate matches ordered by perceived relevance based on this input.")
    inputtype: Literal["textquery", "phonenumber"] = Field(default=..., description="The type of input being searched: 'textquery' for place names and addresses, or 'phonenumber' for phone numbers in international E.164 format (e.g., +1-555-0123).")
    locationbias: str | None = Field(default=None, description="Optional geographic bias to prefer results in a specific area. Specify 'ipbias' to use IP-based biasing, a circular area using 'circle:radius_meters@latitude,longitude', or a rectangular area using 'rectangle:south,west|north,east'. If omitted, IP address biasing is applied by default.", examples=['ipbias', 'point:37.781157,-122.398720', 'circle:1000@37.781157,-122.398720', 'rectangle:37.7,-122.4|37.8,-122.3'])
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(default=None, description="The language for returned results. Defaults to English. Affects how addresses and place names are displayed, with the API attempting to provide locally-readable transliterations when applicable. Supports 40+ language codes including regional variants (e.g., en-GB, pt-BR).")
class FindPlaceFromTextRequest(StrictModel):
    """Search for a place using text input such as a name, address, or phone number. Returns matching places with optional detailed information based on requested fields."""
    query: FindPlaceFromTextRequestQuery

# Operation: search_nearby_places
class NearbySearchRequestQuery(StrictModel):
    keyword: str | None = Field(default=None, description="Search term for places, such as a business name, address, or category (e.g., 'restaurant', '123 Main Street'). Combining location information in this parameter may conflict with the location and radius parameters. Omitting this parameter will exclude temporarily or permanently closed places from results.")
    location: str = Field(default=..., description="Center point for the search area, specified as latitude and longitude separated by a comma (e.g., 40,-110).")
    opennow: bool | None = Field(default=None, description="When enabled, returns only places currently open for business. Places without specified opening hours in the Google Places database will be excluded.")
    rankby: Literal["prominence", "distance"] | None = Field(default=None, description="Determines result ordering: 'prominence' (default) ranks by importance and requires the radius parameter, while 'distance' orders by proximity and requires at least one of keyword, name, or type but disallows radius.")
    radius: float = Field(default=..., description="Search radius in meters around the location. Maximum values vary by search type: up to 50,000 meters for keyword or name searches, dynamically adjusted for searches without keywords or names. When rankby is set to 'distance', this parameter is not allowed.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Restrict results to a single place type (e.g., 'hospital', 'pharmacy'). Only the first type is used if multiple are provided. Combining the same value as both keyword and type may return no results.")
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(default=None, description="Language for result content, supporting 40+ languages including regional variants (e.g., 'en', 'es', 'zh-CN'). Defaults to 'en' if not specified. The API uses the Accept-Language header as a fallback and returns street addresses in the local language when possible.")
class NearbySearchRequest(StrictModel):
    """Search for places within a specified geographic area. Refine results by keywords, place types, or business status to discover relevant locations near a given coordinate."""
    query: NearbySearchRequestQuery

# Operation: search_places_by_text
class TextSearchRequestQuery(StrictModel):
    opennow: bool | None = Field(default=None, description="Filter results to only include places currently open for business. Places without specified opening hours in the database will be excluded when this filter is applied.")
    query: str = Field(default=..., description="The search query string, such as a place name (e.g., 'pizza'), address (e.g., '123 Main Street'), or category (e.g., 'restaurants'). Results are ranked by perceived relevance to this query.")
    radius: float = Field(default=..., description="Search radius in meters, up to a maximum of 50,000 meters. Results within this circle are preferred, though places outside may still be returned. The API may adjust this radius based on result density.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Restrict results to a single place type from the supported types list. If multiple types are provided, only the first is used; others are ignored.")
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(default=None, description="Language code for result content. Defaults to English. Affects how addresses and place names are returned and transliterated. The API uses the Accept-Language header if not specified.")
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(default=None, description="Two-character region code (ccTLD format, e.g., 'us', 'gb', 'uk') to bias results to a specific country or region. Defaults to 'en'.")
class TextSearchRequest(StrictModel):
    """Search for places using a text query string, optionally filtered by location radius, type, and opening status. Returns a ranked list of matching places with basic information."""
    query: TextSearchRequestQuery

# Operation: get_place_photo
class PlacePhotoRequestQuery(StrictModel):
    photo_reference: str = Field(default=..., description="A unique identifier for the photo, obtained from Place Search, Nearby Search, Text Search, or Place Details requests. This reference is required to retrieve the actual photo image.")
class PlacePhotoRequest(StrictModel):
    """Retrieve a high-quality photo for a place using a photo reference. Returns the image data that can be resized and displayed in your application, with attribution requirements included when necessary."""
    query: PlacePhotoRequestQuery

# Operation: get_query_suggestions
class QueryAutocompleteRequestQuery(StrictModel):
    input_: str = Field(default=..., validation_alias="input", serialization_alias="input", description="The search text to get predictions for. The service matches this string against both full words and substrings to return relevant suggestions ordered by perceived relevance.")
    offset: float | None = Field(default=None, description="Optional character position in the input text where matching should stop. Useful for matching against partial input (e.g., matching \"Goo\" when input is \"Google\"). Typically set to the text caret position. If omitted, the entire input term is used for matching.")
    radius: float = Field(default=..., description="The search radius in meters within which to prefer returning results. Maximum of 50,000 meters. Results outside this radius may still be returned. Helps bias suggestions to a geographic area when combined with a location.")
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(default=None, description="The language for returned results. Defaults to English. Supports 40+ languages including regional variants (e.g., en-GB, pt-BR). If not specified, the API attempts to use the language from the Accept-Language header.")
class QueryAutocompleteRequest(StrictModel):
    """Get autocomplete suggestions for geographic queries as users type. Returns predicted queries based on categorical searches like "pizza near New York", matching both full words and substrings."""
    query: QueryAutocompleteRequestQuery

# Operation: autocomplete_place
class AutocompleteRequestQuery(StrictModel):
    input_: str = Field(default=..., validation_alias="input", serialization_alias="input", description="The search text to match against place names, addresses, and plus codes. The service returns predictions ordered by perceived relevance to this input.")
    sessiontoken: str | None = Field(default=None, description="A unique identifier for this autocomplete session used for billing optimization. Generate a fresh UUID for each new user search session. All requests within a session must use the same API key and project.")
    components: str | None = Field(default=None, description="Restrict results to specific countries using ISO 3166-1 Alpha-2 country codes. Separate multiple countries with a pipe character (e.g., country:us|country:ca). Up to 5 countries can be specified.")
    strictbounds: bool | None = Field(default=None, description="When enabled, returns only places strictly within the region defined by location and radius, excluding any matches outside the boundary.")
    offset: float | None = Field(default=None, description="The character position in the input text where matching should end. Useful for matching against partial words as the user types. If omitted, the entire input term is used for matching.")
    origin: str | None = Field(default=None, description="The starting point for calculating straight-line distance to results. Specify as latitude,longitude in decimal degrees. Distance is returned in the response as distance_meters.")
    locationbias: str | None = Field(default=None, description="Prefer results in a specified area using IP-based biasing, a circular radius, or a rectangular bounding box. Circular format: circle:radius_in_meters@latitude,longitude. Rectangular format: rectangle:south,west|north,east.", examples=['ipbias', 'point:37.781157,-122.398720', 'circle:1000@37.781157,-122.398720', 'rectangle:37.7,-122.4|37.8,-122.3'])
    locationrestriction: str | None = Field(default=None, description="Strictly limit results to a specified area using a circular radius or rectangular bounding box. Unlike location bias, results outside this area will not be returned. Circular format: circle:radius_in_meters@latitude,longitude. Rectangular format: rectangle:south,west|north,east.", examples=['circle:1000@37.781157,-122.398720', 'rectangle:37.7,-122.4|37.8,-122.3'])
    radius: float = Field(default=..., description="The search radius in meters within which to prefer results. Maximum 50,000 meters for autocomplete. Results outside this radius may still be returned if they match the input.")
    types: str | None = Field(default=None, description="Filter results to specific place types. Specify up to 5 types separated by pipe characters (e.g., book_store|cafe), or use a single type collection filter. See supported types documentation for valid values.")
    language: Literal["ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "en-AU", "en-GB", "es", "eu", "fa", "fi", "fil", "fr", "gl", "gu", "hi", "hr", "hu", "id", "it", "iw", "ja", "kn", "ko", "lt", "lv", "ml", "mr", "nl", "no", "pl", "pt", "pt-BR", "pt-PT", "ro", "ru", "sk", "sl", "sr", "sv", "ta", "te", "th", "tl", "tr", "uk", "vi", "zh-CN", "zh-TW"] | None = Field(default=None, description="The language for returned results. Defaults to English. Affects how place names and addresses are translated and formatted. See supported languages list for valid codes.")
    region: Literal["ac", "ad", "ae", "af", "ag", "ai", "al", "am", "an", "ao", "aq", "ar", "as", "at", "au", "aw", "ax", "az", "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bl", "bm", "bn", "bo", "bq", "br", "bs", "bt", "bv", "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr", "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "eh", "en", "er", "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh", "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr", "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp", "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk", "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mf", "mg", "mh", "mk", "ml", "mm", "mn", "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf", "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl", "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc", "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "ss", "st", "su", "sv", "sx", "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tp", "tr", "tt", "tv", "tw", "tz", "ua", "ug", "uk", "um", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf", "ws", "ye", "yt", "za", "zm", "zw"] | None = Field(default=None, description="The region code as a ccTLD (country code top-level domain) to bias results and interpretation. Defaults to 'en'. Use two-character codes like 'uk' for United Kingdom or 'de' for Germany.")
class AutocompleteRequest(StrictModel):
    """Get place predictions as a user types a geographic search query. Returns matching businesses, addresses, and points of interest based on the input text, with optional geographic filtering and biasing."""
    query: AutocompleteRequestQuery

# Operation: get_street_view
class StreetViewRequestQuery(StrictModel):
    fov: float | None = Field(default=None, description="Controls the horizontal zoom level of the image in degrees. Accepts values from 0 to 120, where smaller values provide higher zoom. Defaults to 90 degrees if not specified.")
    heading: float | None = Field(default=None, description="Sets the compass direction the camera faces, using values from 0 to 360 degrees where 0 and 360 represent North, 90 represents East, and 180 represents South. If omitted, the camera automatically orients toward the specified location from the nearest available photograph.")
    pano: str | None = Field(default=None, description="Targets a specific panorama by its unique identifier. Panorama IDs are generally persistent but may change as Street View imagery is updated.")
    pitch: float | None = Field(default=None, description="Adjusts the vertical camera angle relative to the Street View vehicle. Positive values tilt upward (90 degrees points straight up), negative values tilt downward (-90 degrees points straight down). Defaults to 0 for horizontal orientation.")
    size: str = Field(default=..., description="Specifies the output image dimensions as width by height in pixels. Both dimensions must not exceed 640 pixels; larger values default to 640. Use the format widthxheight (for example, 600x400).")
    source: Literal["default", "outdoor"] | None = Field(default=None, description="Restricts Street View results to specific imagery sources. Use 'default' to search all available sources, or 'outdoor' to exclude indoor collections. Note that outdoor panoramas may not exist for all locations, and PhotoSpheres are excluded from outdoor searches due to unknown indoor/outdoor classification.")
class StreetViewRequest(StrictModel):
    """Retrieve a static Street View image for a specified location or panorama. Returns a static image without interactive elements, useful for embedding Street View imagery in web pages."""
    query: StreetViewRequestQuery

# Operation: get_street_view_metadata
class StreetViewMetadataRequestQuery(StrictModel):
    heading: float | None = Field(default=None, description="The compass heading of the camera in degrees, ranging from 0 to 360 where 0 and 360 indicate North, 90 indicates East, and 180 indicates South. If not specified, the heading will be automatically calculated to point toward the location from the nearest available photograph.")
    pano: str | None = Field(default=None, description="A specific panorama ID to retrieve metadata for. Panorama IDs are generally stable identifiers, though they may change as Street View imagery is updated.")
    pitch: float | None = Field(default=None, description="The vertical angle of the camera relative to the Street View vehicle, ranging from -90 degrees (straight down) to 90 degrees (straight up), with 0 as the default horizontal position.")
    size: str | None = Field(default=None, description="The output image dimensions specified as width by height in pixels (e.g., 600x400 for a 600-pixel wide by 400-pixel high image).")
    source: Literal["default", "outdoor"] | None = Field(default=None, description="Limits Street View searches to specific sources: use 'default' to search all available sources, or 'outdoor' to search only outdoor collections and exclude indoor panoramas. Note that outdoor panoramas may not exist for all locations, and PhotoSpheres are excluded from outdoor searches since their indoor/outdoor status cannot be determined.")
class StreetViewMetadataRequest(StrictModel):
    """Retrieve metadata about a Street View panorama at a specific location or panorama ID, including availability, coordinates, panorama ID, capture date, and copyright information to customize error handling in your application."""
    query: StreetViewMetadataRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class AddressComponent(PermissiveModel):
    long_name: str = Field(..., description="The full text description or name of the address component as returned by the Geocoder.")
    short_name: str = Field(..., description="An abbreviated textual name for the address component, if available. For example, an address component for the state of Alaska may have a long_name of \"Alaska\" and a short_name of \"AK\" using the 2-letter postal abbreviation.")
    types: list[str] = Field(..., description="An array indicating the type of the address component. See the list of [supported types](https://developers.google.com/maps/documentation/places/web-service/supported_types).")

class CellTower(PermissiveModel):
    """Attributes used to describe a cell tower. The following optional fields are not currently used, but may be included if values are available: `age`, `signalStrength`, `timingAdvance`."""
    cell_id: int = Field(..., validation_alias="cellId", serialization_alias="cellId", description="Unique identifier of the cell. On GSM, this is the Cell ID (CID); CDMA networks use the Base Station ID (BID). WCDMA networks use the UTRAN/GERAN Cell Identity (UC-Id), which is a 32-bit value concatenating the Radio Network Controller (RNC) and Cell ID. Specifying only the 16-bit Cell ID value in WCDMA networks may return inaccurate results.")
    location_area_code: int = Field(..., validation_alias="locationAreaCode", serialization_alias="locationAreaCode", description="The Location Area Code (LAC) for GSM and WCDMA networks. The Network ID (NID) for CDMA networks.")
    mobile_country_code: int = Field(..., validation_alias="mobileCountryCode", serialization_alias="mobileCountryCode", description="The cell tower's Mobile Country Code (MCC).")
    mobile_network_code: int = Field(..., validation_alias="mobileNetworkCode", serialization_alias="mobileNetworkCode", description="The cell tower's Mobile Network Code. This is the MNC for GSM and WCDMA; CDMA uses the System ID (SID).")
    age: int | None = Field(None, description="The number of milliseconds since this cell was primary. If age is 0, the cellId represents a current measurement.")
    signal_strength: float | None = Field(None, validation_alias="signalStrength", serialization_alias="signalStrength", description="Radio signal strength measured in dBm.")
    timing_advance: float | None = Field(None, validation_alias="timingAdvance", serialization_alias="timingAdvance", description="The timing advance value.")

class LatLngLiteral(PermissiveModel):
    """An object describing a specific location with Latitude and Longitude in decimal degrees."""
    lat: float = Field(..., description="Latitude in decimal degrees")
    lng: float = Field(..., description="Longitude in decimal degrees")

class Bounds(PermissiveModel):
    """A rectangle in geographical coordinates from points at the southwest and northeast corners."""
    northeast: LatLngLiteral
    southwest: LatLngLiteral

class Geometry(PermissiveModel):
    """An object describing the location."""
    location: LatLngLiteral
    viewport: Bounds

class PlaceEditorialSummary(PermissiveModel):
    """Contains a summary of the place. A summary is comprised of a textual overview, and also includes the language code for these if applicable. Summary text must be presented as-is and can not be modified or altered."""
    overview: str | None = Field(None, description="A medium-length textual summary of the place.")
    language: str | None = Field(None, description="The language of the previous fields. May not always be present.")

class PlaceOpeningHoursPeriodDetail(PermissiveModel):
    date: str | None = Field(None, description="A date expressed in RFC3339 format in the local timezone for the place, for example 2010-12-31.")
    day: float = Field(..., description="A number from 0–6, corresponding to the days of the week, starting on Sunday. For example, 2 means Tuesday.")
    time_: str = Field(..., validation_alias="time", serialization_alias="time", description="May contain a time of day in 24-hour hhmm format. Values are in the range 0000–2359. The time will be reported in the place’s time zone.")
    truncated: bool | None = Field(None, description="True if a given period was truncated due to a seven-day cutoff, where the period starts before midnight on the date of the request and/or ends at or after  midnight on the last day. This property indicates that the period for open or close can extend past this seven-day cutoff.")

class PlaceOpeningHoursPeriod(PermissiveModel):
    open_: PlaceOpeningHoursPeriodDetail = Field(..., validation_alias="open", serialization_alias="open", description="Contains a pair of day and time objects describing when the place opens.")
    close: PlaceOpeningHoursPeriodDetail | None = Field(None, description="May contain a pair of day and time objects describing when the place closes. If a place is always open, the close section will be missing from the response. Clients can rely on always-open being represented as an open period containing day with value `0` and time with value `0000`, and no `close`.\n")

class PlacePhoto(PermissiveModel):
    """A photo of a Place. The photo can be accesed via the [Place Photo](https://developers.google.com/places/web-service/photos) API using an url in the following pattern:

```
https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference=photo_reference&key=YOUR_API_KEY
```

See [Place Photos](https://developers.google.com/places/web-service/photos) for more information.
"""
    height: float = Field(..., description="The height of the photo.")
    width: float = Field(..., description="The width of the photo.")
    html_attributions: list[str] = Field(..., description="The HTML attributions for the photo.")
    photo_reference: str = Field(..., description="A string used to identify the photo when you perform a Photo request.")

class PlaceReview(PermissiveModel):
    """A review of the place submitted by a user."""
    author_name: str = Field(..., description="The name of the user who submitted the review. Anonymous reviews are attributed to \"A Google user\".")
    author_url: str | None = Field(None, description="The URL to the user's Google Maps Local Guides profile, if available.")
    profile_photo_url: str | None = Field(None, description="The URL to the user's profile photo, if available.")
    language: str | None = Field(None, description="An IETF language code indicating the language of the returned review.\nThis field contains the main language tag only, and not the secondary tag indicating country or region. For example, all the English reviews are tagged as 'en', and not 'en-AU' or 'en-UK' and so on.\nThis field is empty if there is only a rating with no review text. \n")
    original_language: str | None = Field(None, description="An IETF language code indicating the original language of the review. If the review has been translated, then `original_language` != `language`.\nThis field contains the main language tag only, and not the secondary tag indicating country or region. For example, all the English reviews are tagged as 'en', and not 'en-AU' or 'en-UK' and so on.\nThis field is empty if there is only a rating with no review text.\n")
    rating: float = Field(..., description="The user's overall rating for this place. This is a whole number, ranging from 1 to 5.")
    relative_time_description: str = Field(..., description="The time that the review was submitted in text, relative to the current time.")
    text: str | None = Field(None, description="The user's review. When reviewing a location with Google Places, text reviews are considered optional. Therefore, this field may be empty. Note that this field may include simple HTML markup. For example, the entity reference `&amp;` may represent an ampersand character.")
    time_: float = Field(..., validation_alias="time", serialization_alias="time", description="The time that the review was submitted, measured in the number of seconds since since midnight, January 1, 1970 UTC.")
    translated: bool | None = Field(None, description="A boolean value indicating if the review was translated from the original language it was written in.\nIf a review has been translated, corresponding to a value of true, Google recommends that you indicate this to your users. For example, you can add the following string, “Translated by Google”, to the review.\n")

class PlaceSpecialDay(PermissiveModel):
    date: str | None = Field(None, description="A date expressed in RFC3339 format in the local timezone for the place, for example 2010-12-31.")
    exceptional_hours: bool | None = Field(None, description="True if there are exceptional hours for this day. If `true`, this means that there is at least one exception for this day. Exceptions cause different values to occur in the subfields of `current_opening_hours` and `secondary_opening_hours` such as `periods`, `weekday_text`, `open_now`. The exceptions apply to the hours, and the hours are used to generate the other fields.")

class PlaceOpeningHours(PermissiveModel):
    """An object describing the opening hours of a place."""
    open_now: bool | None = Field(None, description="A boolean value indicating if the place is open at the current time.")
    periods: list[PlaceOpeningHoursPeriod] | None = Field(None, description="An array of opening periods covering seven days, starting from Sunday, in chronological order.\n")
    special_days: list[PlaceSpecialDay] | None = Field(None, description="An array of up to seven entries corresponding to the next seven days.\n")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="A type string used to identify the type of secondary hours (for example, `DRIVE_THROUGH`, `HAPPY_HOUR`, `DELIVERY`, `TAKEOUT`, `KITCHEN`, `BREAKFAST`, `LUNCH`, `DINNER`, `BRUNCH`, `PICKUP`, `SENIOR_HOURS`). Set for `secondary_opening_hours` only.")
    weekday_text: list[str] | None = Field(None, description="An array of strings describing in human-readable text the hours of the place.")

class PlusCode(PermissiveModel):
    """An encoded location reference, derived from latitude and longitude coordinates, that represents an area, 1/8000th of a degree by 1/8000th of a degree (about 14m x 14m at the equator) or smaller. Plus codes can be used as a replacement for street addresses in places where they do not exist (where buildings are not numbered or streets are not named)."""
    compound_code: str | None = Field(None, description="The `compound_code` is a 6 character or longer local code with an explicit location (`CWC8+R9, Mountain View, CA, USA`). Some APIs may return an empty string if the `compound_code` is not available.")
    global_code: str = Field(..., description="The `global_code` is a 4 character area code and 6 character or longer local code (`849VCWC8+R9`).")

class Place(PermissiveModel):
    """Attributes describing a place. Not all attributes will be available for all place types."""
    address_components: list[AddressComponent] | None = Field(None, description="An array containing the separate components applicable to this address.")
    adr_address: str | None = Field(None, description="A representation of the place's address in the [adr microformat](http://microformats.org/wiki/adr).")
    business_status: Literal["OPERATIONAL", "CLOSED_TEMPORARILY", "CLOSED_PERMANENTLY"] | None = Field(None, description="Indicates the operational status of the place, if it is a business. If no data exists, `business_status` is not returned.\n")
    curbside_pickup: bool | None = Field(None, description="Specifies if the business supports curbside pickup.")
    current_opening_hours: PlaceOpeningHours | None = Field(None, description="Contains the hours of operation for the next seven days (including today). The time period starts at midnight on the date of the request and ends at 11:59 pm six days later. This field includes the `special_days` subfield of all hours, set for dates that have exceptional hours.")
    delivery: bool | None = Field(None, description="Specifies if the business supports delivery.")
    dine_in: bool | None = Field(None, description="Specifies if the business supports indoor or outdoor seating options.")
    editorial_summary: PlaceEditorialSummary | None = Field(None, description="Contains a summary of the place. A summary is comprised of a textual overview, and also includes the language code for these if applicable. Summary text must be presented as-is and can not be modified or altered.")
    formatted_address: str | None = Field(None, description="A string containing the human-readable address of this place.\n\nOften this address is equivalent to the postal address. Note that some countries, such as the United Kingdom, do not allow distribution of true postal addresses due to licensing restrictions.\n\nThe formatted address is logically composed of one or more address components. For example, the address \"111 8th Avenue, New York, NY\" consists of the following components: \"111\" (the street number), \"8th Avenue\" (the route), \"New York\" (the city) and \"NY\" (the US state).\n\nDo not parse the formatted address programmatically. Instead you should use the individual address components, which the API response includes in addition to the formatted address field.\n")
    formatted_phone_number: str | None = Field(None, description="Contains the place's phone number in its [local format](http://en.wikipedia.org/wiki/Local_conventions_for_writing_telephone_numbers).")
    geometry: Geometry | None = Field(None, description="Contains the location and viewport for the location.")
    icon: str | None = Field(None, description="Contains the URL of a suggested icon which may be displayed to the user when indicating this result on a map.")
    icon_background_color: str | None = Field(None, description="Contains the default HEX color code for the place's category.")
    icon_mask_base_uri: str | None = Field(None, description="Contains the URL of a recommended icon, minus the `.svg` or `.png` file type extension.")
    international_phone_number: str | None = Field(None, description="Contains the place's phone number in international format. International format includes the country code, and is prefixed with the plus, +, sign. For example, the international_phone_number for Google's Sydney, Australia office is `+61 2 9374 4000`.")
    name: str | None = Field(None, description="Contains the human-readable name for the returned result. For `establishment` results, this is usually the canonicalized business name.")
    opening_hours: PlaceOpeningHours | None = Field(None, description="Contains the regular hours of operation.")
    permanently_closed: bool | None = Field(None, description="Use `business_status` to get the operational status of businesses.")
    photos: list[PlacePhoto] | None = Field(None, description="An array of photo objects, each containing a reference to an image. A request may return up to ten photos. More information about place photos and how you can use the images in your application can be found in the [Place Photos](https://developers.google.com/maps/documentation/places/web-service/photos) documentation.")
    place_id: str | None = Field(None, description="A textual identifier that uniquely identifies a place. To retrieve information about the place, pass this identifier in the `place_id` field of a Places API request. For more information about place IDs, see the [place ID overview](https://developers.google.com/maps/documentation/places/web-service/place-id).")
    plus_code: PlusCode | None = Field(None, description="An encoded location reference, derived from latitude and longitude coordinates, that represents an area: 1/8000th of a degree by 1/8000th of a degree (about 14m x 14m at the equator) or smaller. Plus codes can be used as a replacement for street addresses in places where they do not exist (where buildings are not numbered or streets are not named). See [Open Location Code](https://en.wikipedia.org/wiki/Open_Location_Code) and [plus codes](https://plus.codes/).\n")
    price_level: float | None = Field(None, description="The price level of the place, on a scale of 0 to 4. The exact amount indicated by a specific value will vary from region to region. Price levels are interpreted as follows:\n- 0 Free\n- 1 Inexpensive\n- 2 Moderate\n- 3 Expensive\n- 4 Very Expensive\n")
    rating: float | None = Field(None, description="Contains the place's rating, from 1.0 to 5.0, based on aggregated user reviews.")
    reference: str | None = None
    reservable: bool | None = Field(None, description="Specifies if the place supports reservations.")
    reviews: list[PlaceReview] | None = Field(None, description="A JSON array of up to five reviews. By default, the reviews are sorted in order of relevance. Use the `reviews_sort` request parameter to control sorting.\n\n- For `most_relevant` (default), reviews are sorted by relevance; the service will bias the results to return reviews originally written in the preferred language.\n- For `newest`, reviews are sorted in chronological order; the preferred language does not affect the sort order.\nGoogle recommends indicating to users whether results are ordered by `most_relevant` or `newest`.\n")
    serves_beer: bool | None = Field(None, description="Specifies if the place serves beer.")
    serves_breakfast: bool | None = Field(None, description="Specifies if the place serves breakfast.")
    serves_brunch: bool | None = Field(None, description="Specifies if the place serves brunch.")
    serves_dinner: bool | None = Field(None, description="Specifies if the place serves dinner.")
    serves_lunch: bool | None = Field(None, description="Specifies if the place serves lunch.")
    serves_vegetarian_food: bool | None = Field(None, description="Specifies if the place serves vegetarian food.")
    serves_wine: bool | None = Field(None, description="Specifies if the place serves wine.")
    scope: str | None = None
    secondary_opening_hours: list[PlaceOpeningHours] | None = Field(None, description="Contains an array of entries for the next seven days including information about secondary hours of a business. Secondary hours are different from a business's main hours. For example, a restaurant can specify drive through hours or delivery hours as its secondary hours. This field populates the `type` subfield, which draws from a predefined list of opening hours types (such as `DRIVE_THROUGH`, `PICKUP`, or `TAKEOUT`) based on the types of the place. This field includes the `special_days` subfield of all hours, set for dates that have exceptional hours.")
    takeout: bool | None = Field(None, description="Specifies if the business supports takeout.")
    types: list[str] | None = Field(None, description="Contains an array of feature types describing the given result. See the list of [supported types](https://developers.google.com/maps/documentation/places/web-service/supported_types#table2).")
    url: str | None = Field(None, description="Contains the URL of the official Google page for this place. This will be the Google-owned page that contains the best available information about the place. Applications must link to or embed this page on any screen that shows detailed results about the place to the user.")
    user_ratings_total: float | None = Field(None, description="The total number of reviews, with or without text, for this place.")
    utc_offset: float | None = Field(None, description="Contains the number of minutes this place’s current timezone is offset from UTC. For example, for places in Sydney, Australia during daylight saving time this would be 660 (+11 hours from UTC), and for places in California outside of daylight saving time this would be -480 (-8 hours from UTC).")
    vicinity: str | None = Field(None, description="For establishment (`types:[\"establishment\", ...])` results only, the `vicinity` field contains a simplified address for the place, including the street name, street number, and locality, but not the province/state, postal code, or country.\n\nFor all other results, the `vicinity` field contains the name of the narrowest political (`types:[\"political\", ...]`) feature that is present in the address of the result.\n\nThis content is meant to be read as-is. Do not programmatically parse the formatted address.\n")
    website: str | None = Field(None, description="The authoritative website for this place, such as a business' homepage.")
    wheelchair_accessible_entrance: bool | None = Field(None, description="Specifies if the place has an entrance that is wheelchair-accessible.")

class WiFiAccessPoint(PermissiveModel):
    """Attributes used to describe a WiFi access point."""
    mac_address: str = Field(..., validation_alias="macAddress", serialization_alias="macAddress", description="The MAC address of the WiFi node. It's typically called a BSS, BSSID or MAC address. Separators must be `:` (colon).")
    signal_strength: int | None = Field(None, validation_alias="signalStrength", serialization_alias="signalStrength", description="The current signal strength measured in dBm.")
    signal_to_noise_ratio: int | None = Field(None, validation_alias="signalToNoiseRatio", serialization_alias="signalToNoiseRatio", description="The current signal to noise ratio measured in dB.")
    age: int | None = Field(None, description="The number of milliseconds since this access point was detected.")
    channel: int | None = Field(None, description="The channel over which the client is communication with the access point.")


# Rebuild models to resolve forward references (required for circular refs)
AddressComponent.model_rebuild()
Bounds.model_rebuild()
CellTower.model_rebuild()
Geometry.model_rebuild()
LatLngLiteral.model_rebuild()
Place.model_rebuild()
PlaceEditorialSummary.model_rebuild()
PlaceOpeningHours.model_rebuild()
PlaceOpeningHoursPeriod.model_rebuild()
PlaceOpeningHoursPeriodDetail.model_rebuild()
PlacePhoto.model_rebuild()
PlaceReview.model_rebuild()
PlaceSpecialDay.model_rebuild()
PlusCode.model_rebuild()
WiFiAccessPoint.model_rebuild()

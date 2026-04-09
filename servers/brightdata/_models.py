"""
Bright Data MCP Server - Pydantic Models

Generated: 2026-04-09 17:15:53 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "DeleteZoneBlacklistRequest",
    "DeleteZoneIpsRequest",
    "DeleteZoneRequest",
    "DeleteZoneVipsRequest",
    "DeleteZoneWhitelistRequest",
    "GetCitiesRequest",
    "GetCustomerBwRequest",
    "GetZoneBlacklistRequest",
    "GetZoneBwRequest",
    "GetZoneCostRequest",
    "GetZoneCountAvailableIpsRequest",
    "GetZoneIpsRequest",
    "GetZonePasswordsRequest",
    "GetZoneProxiesPendingReplacementRequest",
    "GetZoneRecentIpsRequest",
    "GetZoneRequest",
    "GetZoneRouteIpsRequest",
    "GetZoneRouteVipsRequest",
    "GetZoneStaticCitiesRequest",
    "GetZoneStatusRequest",
    "GetZoneWhitelistRequest",
    "PostZoneBlacklistRequest",
    "PostZoneChangeDisableRequest",
    "PostZoneDomainPermRequest",
    "PostZoneIpsMigrateRequest",
    "PostZoneIpsRefreshRequest",
    "PostZoneIpsRequest",
    "PostZoneRequest",
    "PostZoneSwitch100uptimeRequest",
    "PostZoneWhitelistRequest",
    "GetZoneCountAvailableIpsQueryPlan",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_cities
class GetCitiesRequestQuery(StrictModel):
    country: str = Field(default=..., description="The ISO 3166-1 alpha-2 two-letter country code identifying the country whose cities should be retrieved.")
class GetCitiesRequest(StrictModel):
    """Retrieves a list of cities belonging to a specified country. Useful for populating location options or validating city data within a given country."""
    query: GetCitiesRequestQuery

# Operation: get_bandwidth_stats
class GetCustomerBwRequestQuery(StrictModel):
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="The start of the time range for which to retrieve bandwidth stats, specified as an ISO 8601 datetime string.")
    to: str | None = Field(default=None, description="The end of the time range for which to retrieve bandwidth stats, specified as an ISO 8601 datetime string.")
class GetCustomerBwRequest(StrictModel):
    """Retrieves bandwidth usage statistics aggregated across all your Zones. Optionally filter results to a specific time window using start and end timestamps."""
    query: GetCustomerBwRequestQuery | None = None

# Operation: get_zone_info
class GetZoneRequestQuery(StrictModel):
    zone: str = Field(default=..., description="The identifier or name of the zone whose status you want to retrieve.")
class GetZoneRequest(StrictModel):
    """Retrieves the current status and details of a specified zone. Use this to monitor zone health, availability, or configuration state."""
    query: GetZoneRequestQuery

# Operation: create_zone
class PostZoneRequestBodyZone(StrictModel):
    name: str = Field(default=..., validation_alias="name", serialization_alias="name", description="Unique name to identify the zone within your account.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The proxy category for the zone, such as serp, isp, mobile, or resident. Determines the underlying proxy network used.")
class PostZoneRequestBodyPlan(StrictModel):
    type_: Literal["static", "resident", "unblocker", "browser_api"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The billing and access plan type for the zone. Controls how the zone is provisioned and billed.")
    domain_whitelist: str | None = Field(default=None, validation_alias="domain_whitelist", serialization_alias="domain_whitelist", description="Space-separated list of domains permitted to use this zone. Required when `ips_type` is set to `selective`.")
    ips_type: Literal["shared", "dedicated", "selective"] | None = Field(default=None, validation_alias="ips_type", serialization_alias="ips_type", description="Determines how IPs are allocated to the zone. Use `selective` to restrict usage to specific domains defined in `domain_whitelist`.")
    bandwidth: Literal["bandwidth", "unlimited"] | None = Field(default=None, validation_alias="bandwidth", serialization_alias="bandwidth", description="Controls bandwidth billing mode. Set to `unlimited` to enable flat-rate unlimited bandwidth instead of pay-per-GB billing.")
    ip_alloc_preset: Literal["shared_block", "shared_res_block"] | None = Field(default=None, validation_alias="ip_alloc_preset", serialization_alias="ip_alloc_preset", description="Preset for configuring a Shared Pay-Per-Usage IP allocation type on the zone.")
    ips: int | None = Field(default=None, validation_alias="ips", serialization_alias="ips", description="Number of static IPs to allocate to the zone at creation time.")
    country: str | None = Field(default=None, validation_alias="country", serialization_alias="country", description="Lowercase ISO 3166-1 alpha-2 country code specifying the country from which IPs should be allocated. Must be lowercase — uppercase codes will cause a misleading 'no IPs available' error. Use `any` to allow IPs from any country.")
    country_city: str | None = Field(default=None, validation_alias="country_city", serialization_alias="country_city", description="Country code and city combination specifying the city-level location for IP allocation. Use when `ips_type` is `static`. Format is a lowercase country code followed by a hyphen and city name.")
    mobile: bool | None = Field(default=None, validation_alias="mobile", serialization_alias="mobile", description="Set to `true` to configure this zone as a Mobile proxy zone. Requires `body.zone.type` to be `resident`.")
    serp: bool | None = Field(default=None, validation_alias="serp", serialization_alias="serp", description="Set to `true` to configure this zone as a SERP API zone for search engine result page scraping.")
    city: bool | None = Field(default=None, validation_alias="city", serialization_alias="city", description="Set to `true` to enable city-level targeting permission for this zone.")
    asn: bool | None = Field(default=None, validation_alias="asn", serialization_alias="asn", description="Set to `true` to enable ASN (Autonomous System Number) targeting permission for this zone.")
    vip: bool | None = Field(default=None, validation_alias="vip", serialization_alias="vip", description="Set to `true` to allocate gIPs (groups of IPs) to the zone instead of individual IPs.")
    vips_type: Literal["shared", "domain"] | None = Field(default=None, validation_alias="vips_type", serialization_alias="vips_type", description="Specifies the gIP sharing model for Residential or Mobile zones. Use `domain` to restrict gIP usage to specific domains.")
    vips: int | None = Field(default=None, validation_alias="vips", serialization_alias="vips", description="Number of gIPs (groups of IPs) to allocate to the zone. Requires `vip` to be `true`.")
    vip_country: str | None = Field(default=None, validation_alias="vip_country", serialization_alias="vip_country", description="Lowercase ISO 3166-1 alpha-2 country code specifying the country for gIP allocation. Applicable when `ips_type` is `resident` and `vip` is `true`.")
    vip_country_city: str | None = Field(default=None, validation_alias="vip_country_city", serialization_alias="vip_country_city", description="Country code and city combination specifying the city-level location for gIP allocation. Applicable when `ips_type` is `resident` and `vip` is `true`. Format is a lowercase country code followed by a hyphen and city name.")
    pool_ip_type: Literal["dc", "static_res"] | None = Field(default=None, validation_alias="pool_ip_type", serialization_alias="pool_ip_type", description="Determines the IP pool type for the zone. Set to `static_res` to create an ISP proxy zone. Required when `body.zone.type` is `ISP` — omitting this field will result in a Datacenter zone being created instead.")
    unl_bw_tiers: Literal["std"] | None = Field(default=None, validation_alias="unl_bw_tiers", serialization_alias="unl_bw_tiers", description="Bandwidth tier applied when unlimited bandwidth is enabled. Required when `bandwidth` is `unlimited` and `ips_type` is `shared` or `dedicated`; omitting this field causes the zone to default to pay-per-GB billing regardless of the `bandwidth` setting.")
    ub_premium: bool | None = Field(default=None, validation_alias="ub_premium", serialization_alias="ub_premium", description="Set to `true` to enable access to premium domains for Unblocker zones.")
    solve_captcha_disable: bool | None = Field(default=None, validation_alias="solve_captcha_disable", serialization_alias="solve_captcha_disable", description="Set to `true` to disable automatic captcha solving for this zone.")
    custom_headers: bool | None = Field(default=None, validation_alias="custom_headers", serialization_alias="custom_headers", description="Set to `true` to allow custom HTTP headers to be included in requests routed through this zone.")
class PostZoneRequestBody(StrictModel):
    zone: PostZoneRequestBodyZone
    plan: PostZoneRequestBodyPlan
class PostZoneRequest(StrictModel):
    """Creates a new proxy zone with the specified configuration, including zone type, IP allocation, targeting options, and bandwidth settings. Supports Datacenter, Residential, Mobile, ISP, SERP, Unblocker, and Browser API zone types."""
    body: PostZoneRequestBody

# Operation: delete_zone
class DeleteZoneRequestBody(StrictModel):
    zone: str | None = Field(default=None, description="The name of the zone to delete. If omitted, all zones associated with your account will be deleted.")
class DeleteZoneRequest(StrictModel):
    """Deletes a specified DNS zone or, if no zone is provided, deletes all zones associated with your account. Use with caution as this action is irreversible."""
    body: DeleteZoneRequestBody | None = None

# Operation: list_zone_blacklisted_ips
class GetZoneBlacklistRequestQuery(StrictModel):
    zones: str | None = Field(default=None, description="A comma-separated list of zone identifiers to filter results by. Omitting this parameter defaults to all zones.")
class GetZoneBlacklistRequest(StrictModel):
    """Retrieves the list of denylisted (blacklisted) IP addresses for one or more specified zones. If no zones are specified, results are returned across all zones."""
    query: GetZoneBlacklistRequestQuery | None = None

# Operation: add_ips_to_zone_denylist
class PostZoneBlacklistRequestBody(StrictModel):
    zone: str | None = Field(default=None, description="The name of the zone to apply the denylist entry to. If omitted, the IP block will be applied across all your zones.")
    ip: str | list[str] = Field(default=..., description="One or more IP addresses to block, accepted as a single IP string, an array of IP strings, a hyphenated IP range, a CIDR subnet, or a netmask notation subnet. Each IP string in an array must be individually quoted.")
class PostZoneBlacklistRequest(StrictModel):
    """Adds one or more IP addresses to the denylist (blacklist) for a specific zone or all zones, blocking traffic from those IPs. Supports single IPs, arrays, ranges, subnets, and netmask notation."""
    body: PostZoneBlacklistRequestBody

# Operation: delete_blacklist_entry
class DeleteZoneBlacklistRequestBody(StrictModel):
    zone: str | None = Field(default=None, description="The name of the zone whose blacklist should be modified. If omitted, the deletion applies across all your zones.")
    ip: str | None = Field(default=None, description="The IP address or address group to remove from the blacklist. Accepts a single IP address, a hyphen-delimited IP range, a CIDR subnet, or a subnet mask notation.")
class DeleteZoneBlacklistRequest(StrictModel):
    """Removes one or more IP addresses from the blacklist for a specific zone or all zones. Supports deletion of single IPs, IP ranges, subnets, and masked addresses."""
    body: DeleteZoneBlacklistRequestBody | None = None

# Operation: get_zone_bandwidth_stats
class GetZoneBwRequestQuery(StrictModel):
    zone: str = Field(default=..., description="The name of the zone for which to retrieve bandwidth statistics.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="The start of the time range for filtering bandwidth stats, specified in ISO 8601 datetime format. If omitted, results may default to the earliest available data.")
    to: str | None = Field(default=None, description="The end of the time range for filtering bandwidth stats, specified in ISO 8601 datetime format. If omitted, results may default to the most recent available data.")
class GetZoneBwRequest(StrictModel):
    """Retrieves bandwidth usage statistics for a specified zone, optionally filtered by a time range. Useful for monitoring data transfer consumption over a given period."""
    query: GetZoneBwRequestQuery

# Operation: set_zone_status
class PostZoneChangeDisableRequestBody(StrictModel):
    zone: str = Field(default=..., description="The name of the DNS zone whose active status will be changed.")
    disable: Literal[0, 1] = Field(default=..., description="Controls the zone's active state: use 0 to activate the zone or 1 to disable it.")
class PostZoneChangeDisableRequest(StrictModel):
    """Activates or disables a specified DNS zone, controlling whether the zone is actively served or suspended."""
    body: PostZoneChangeDisableRequestBody

# Operation: count_available_ips
class GetZoneCountAvailableIpsRequestQuery(StrictModel):
    zone: str | None = Field(default=None, description="The name of the zone for which to count available IP addresses. If omitted, results may reflect a default or global scope.")
    plan: GetZoneCountAvailableIpsQueryPlan | None = Field(default=None, description="A plan object used to filter the available IP count based on specific plan criteria or resource tier constraints.")
class GetZoneCountAvailableIpsRequest(StrictModel):
    """Retrieves the number of available IP addresses in a specified zone, optionally filtered by plan. Useful for capacity planning and determining IP availability before provisioning resources."""
    query: GetZoneCountAvailableIpsRequestQuery | None = None

# Operation: get_zone_cost
class GetZoneCostRequestQuery(StrictModel):
    zone: str = Field(default=..., description="The name of the zone for which to retrieve cost and bandwidth statistics.")
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="The start of the date range for filtering results, specified in ISO 8601 format.")
    to: str | None = Field(default=None, description="The end of the date range for filtering results, specified in ISO 8601 format.")
class GetZoneCostRequest(StrictModel):
    """Retrieves the total cost and bandwidth statistics for a specified zone. Optionally filter results by a date range using start and end timestamps."""
    query: GetZoneCostRequestQuery

# Operation: add_zone_domain_permission
class PostZoneDomainPermRequestBody(StrictModel):
    zone: str = Field(default=..., description="The name of the zone to which the domain permission rule will be applied.")
    type_: Literal["whitelist", "blacklist"] = Field(default=..., validation_alias="type", serialization_alias="type", description="Determines whether the specified domains are added to the allowlist (permitted) or denylist (blocked) for the zone. Use 'whitelist' to allow domains or 'blacklist' to deny them.")
    domain: str | None = Field(default=None, description="One or more domains to add to the specified list, provided as a space-separated string.")
class PostZoneDomainPermRequest(StrictModel):
    """Add one or more domains to a zone's allowlist or denylist to control which domains are permitted or blocked within that zone."""
    body: PostZoneDomainPermRequestBody

# Operation: list_zone_ips
class GetZoneIpsRequestQuery(StrictModel):
    zone: str = Field(default=..., description="The name of the zone whose static IPs should be retrieved.")
    ip_per_country: str | None = Field(default=None, description="When provided, the response includes the total number of IPs available per country for the specified zone.")
class GetZoneIpsRequest(StrictModel):
    """Retrieves the static (Datacenter/ISP) IP addresses assigned to a specified zone. Optionally returns a breakdown of the total IP count grouped by country."""
    query: GetZoneIpsRequestQuery

# Operation: add_zone_static_ips
class PostZoneIpsRequestBody(StrictModel):
    customer: str = Field(default=..., description="The unique identifier of the customer account to which the zone belongs.")
    zone: str = Field(default=..., description="The name of the zone to which the static IPs will be added.")
    count: float = Field(default=..., description="The number of static IPs to allocate to the zone.")
    country: str | None = Field(default=None, description="Two-letter country code used to restrict the newly allocated IPs to a specific country.")
    country_city: str | None = Field(default=None, description="Country and city code used to restrict the newly allocated IPs to a specific city, formatted as a country-city pair.")
class PostZoneIpsRequest(StrictModel):
    """Allocates a specified number of static IPs to a zone for Datacenter or ISP proxy types. Optionally scopes the new IPs to a specific country or city."""
    body: PostZoneIpsRequestBody

# Operation: remove_zone_ips
class DeleteZoneIpsRequestBody(StrictModel):
    zone: str | None = Field(default=None, description="The name of the zone from which the specified IP addresses will be removed.")
    ips: list[str] | None = Field(default=None, description="A list of IP addresses to delete from the zone. Each item should be a valid IPv4 or IPv6 address string; order is not significant.")
class DeleteZoneIpsRequest(StrictModel):
    """Removes one or more IP addresses from a specified zone. Use this to revoke or clean up IP entries associated with a named zone."""
    body: DeleteZoneIpsRequestBody | None = None

# Operation: migrate_zone_ips
class PostZoneIpsMigrateRequestBody(StrictModel):
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="The name of the source zone from which the specified Static IPs will be migrated.")
    to: str = Field(default=..., description="The name of the destination zone to which the specified Static IPs will be migrated.")
    ips: str = Field(default=..., description="The list of Static IP addresses to migrate from the source zone to the destination zone. Each item should be a valid IPv4 address string; order is not significant.")
class PostZoneIpsMigrateRequest(StrictModel):
    """Migrate one or more Static IPs from a source zone to a destination zone across Datacenter or ISP zone types. Both zones must be specified along with the list of IPs to transfer."""
    body: PostZoneIpsMigrateRequestBody

# Operation: refresh_zone_ips
class PostZoneIpsRefreshRequestBody(StrictModel):
    zone: str = Field(default=..., description="The name of the zone whose IPs should be refreshed.")
    vips: list[str] | None = Field(default=None, description="List of dedicated residential virtual IPs (VIPs) to refresh. Omit this parameter to refresh all allocated VIPs in the zone. Only applicable for Dedicated Residential IPs.")
    ips: list[str] | None = Field(default=None, description="List of specific IPs to refresh. Omit this parameter to refresh all allocated IPs in the zone.")
    country: str | None = Field(default=None, description="The target country for the newly assigned IPs, specified as a two-letter country code.")
    country_city: str | None = Field(default=None, description="The target city for the newly assigned IPs, specified as a country-city slug.")
class PostZoneIpsRefreshRequest(StrictModel):
    """Refreshes (rotates) allocated IPs within a specified zone, optionally targeting specific IPs and assigning a new country or city location. Omit the IP parameters to refresh all allocated IPs in the zone."""
    body: PostZoneIpsRefreshRequestBody

# Operation: list_zone_passwords
class GetZonePasswordsRequestQuery(StrictModel):
    zone: str = Field(default=..., description="The identifier of the zone whose passwords should be retrieved.")
class GetZonePasswordsRequest(StrictModel):
    """Retrieves all passwords associated with a specified zone. Useful for managing zone-level credentials and access configurations."""
    query: GetZonePasswordsRequestQuery

# Operation: list_proxies_pending_replacement
class GetZoneProxiesPendingReplacementRequestQuery(StrictModel):
    zone: str | None = Field(default=None, description="The zone identifier used to filter proxies pending replacement. If omitted, results may span all accessible zones.")
class GetZoneProxiesPendingReplacementRequest(StrictModel):
    """Retrieves all proxies within a specified zone that are currently pending replacement. Useful for monitoring and managing proxy lifecycle transitions within a zone."""
    query: GetZoneProxiesPendingReplacementRequestQuery | None = None

# Operation: list_zone_recent_ips
class GetZoneRecentIpsRequestQuery(StrictModel):
    zones: str | None = Field(default=None, description="Specifies which zones to retrieve recent attempting IPs for. Use a wildcard to include all zones, or provide a specific zone identifier to filter results.")
class GetZoneRecentIpsRequest(StrictModel):
    """Retrieves a list of IP addresses that have recently attempted to access your zones. Useful for monitoring access patterns and identifying suspicious activity."""
    query: GetZoneRecentIpsRequestQuery | None = None

# Operation: list_zone_route_ips
class GetZoneRouteIpsRequestQuery(StrictModel):
    zone: str = Field(default=..., description="The name of the zone for which to retrieve available IPs.")
    country: str | None = Field(default=None, description="Filters the returned IPs to only those belonging to the specified country, provided as a 2-letter ISO 3166-1 alpha-2 country code.")
    list_countries: bool | None = Field(default=None, description="When set to true, returns a JSON array of objects pairing each IP with its country code instead of a plain list of IP addresses.")
class GetZoneRouteIpsRequest(StrictModel):
    """Retrieves the available Data Center and ISP IP addresses for a specified zone. Optionally filter by country or request enriched output pairing each IP with its country code."""
    query: GetZoneRouteIpsRequestQuery

# Operation: list_zone_dedicated_ips
class GetZoneRouteVipsRequestQuery(StrictModel):
    zone: str = Field(default=..., description="The name of the zone for which to retrieve available residential dedicated IPs.")
class GetZoneRouteVipsRequest(StrictModel):
    """Retrieves all available residential dedicated IPs (VIPs) assigned to a specified zone. Use this to discover static IP resources available within a given zone for dedicated routing."""
    query: GetZoneRouteVipsRequestQuery

# Operation: list_static_cities
class GetZoneStaticCitiesRequestQuery(StrictModel):
    country: str = Field(default=..., description="The country for which to retrieve available static network cities, specified as a country code.")
    pool_ip_type: Literal["dc", "static_res"] | None = Field(default=None, description="The static network type to filter cities by: datacenter ('dc') or ISP/residential ('static_res').")
class GetZoneStaticCitiesRequest(StrictModel):
    """Retrieves the list of cities available in the static residential network for a specified country. Results can be filtered by network type (Datacenter or ISP)."""
    query: GetZoneStaticCitiesRequestQuery

# Operation: get_zone_status
class GetZoneStatusRequestQuery(StrictModel):
    zone: str = Field(default=..., description="The identifier or name of the zone whose status you want to retrieve.")
class GetZoneStatusRequest(StrictModel):
    """Retrieves the current status of a specified zone. Use this to monitor zone health, availability, or operational state."""
    query: GetZoneStatusRequestQuery

# Operation: toggle_zone_failover
class PostZoneSwitch100uptimeRequestBody(StrictModel):
    zone: str | None = Field(default=None, description="The name of the Static zone for which automatic failover should be toggled.")
    active: Literal[0, 1] | None = Field(default=None, description="Controls whether automatic failover is enabled or disabled for the zone. Use 1 to enable automatic failover and 0 to disable it.")
class PostZoneSwitch100uptimeRequest(StrictModel):
    """Enable or disable automatic failover (100% uptime mode) for a specified Static zone. When enabled, traffic is automatically rerouted to a backup in the event of a zone failure."""
    body: PostZoneSwitch100uptimeRequestBody | None = None

# Operation: remove_zone_vips
class DeleteZoneVipsRequestBody(StrictModel):
    zone: str = Field(default=..., description="The name of the zone from which the specified VIPs will be removed.")
    gips: list[str] = Field(default=..., description="A list of Virtual IP addresses to remove from the zone. Order is not significant; each item should be a valid IP address string.")
class DeleteZoneVipsRequest(StrictModel):
    """Removes one or more Virtual IPs (VIPs) from a specified zone. Use this to decommission or reassign VIP addresses that are no longer needed within the zone."""
    body: DeleteZoneVipsRequestBody

# Operation: list_zone_whitelisted_ips
class GetZoneWhitelistRequestQuery(StrictModel):
    zones: str | None = Field(default=None, description="A comma-separated list of zone identifiers to filter results by. When omitted, results are returned for all zones.")
class GetZoneWhitelistRequest(StrictModel):
    """Retrieves the list of allowlisted IP addresses for one or more specified zones. Useful for auditing or reviewing which IPs have been granted access within a zone."""
    query: GetZoneWhitelistRequestQuery | None = None

# Operation: add_zone_whitelist_ip
class PostZoneWhitelistRequestBody(StrictModel):
    zone: str | None = Field(default=None, description="The name of the zone whose allowlist will be updated. If omitted, the IP(s) will be added to the allowlist for all zones associated with your account.")
    ip: str | list[str] = Field(default=..., description="One or more IP addresses to add to the allowlist, accepted as a single IP string, an array of IP strings, a hyphenated IP range, a CIDR subnet, or a netmask notation subnet.")
class PostZoneWhitelistRequest(StrictModel):
    """Adds one or more IP addresses to the allowlist for a specific zone or all zones, restricting access to only the specified IPs. Supports single IPs, IP arrays, ranges, subnets, and netmask notation."""
    body: PostZoneWhitelistRequestBody

# Operation: delete_whitelist_ip
class DeleteZoneWhitelistRequestBody(StrictModel):
    zone: str | None = Field(default=None, description="The name of the zone whose whitelist will be modified. If omitted, the deletion applies to all zones associated with your account.")
    ip: str | None = Field(default=None, description="The IP address or address group to remove from the whitelist. Accepts a single IP address, a hyphen-delimited IP range, a CIDR subnet notation, or an IP with a subnet mask.")
class DeleteZoneWhitelistRequest(StrictModel):
    """Removes one or more IP addresses from the whitelist of a specific zone or all zones. Supports deletion of single IPs, IP ranges, subnets, and IP mask formats."""
    body: DeleteZoneWhitelistRequestBody | None = None

# ============================================================================
# Component Models
# ============================================================================

class GetZoneCountAvailableIpsQueryPlanGeoDb(PermissiveModel):
    """turns on/off using of the IP`s location databases"""
    maxmind: bool | None = Field(True, description="use MaxMind IP location DB")
    dbip: bool | None = Field(True, description="use DB-IP IP location DB")
    google: bool | None = Field(True, description="use Google IP location DB")
    ip2location: bool | None = Field(True, description="use IP2Location IP location DB")
    ipcn: bool | None = Field(True, description="use ip.cn IP location DB")

class GetZoneCountAvailableIpsQueryPlan(PermissiveModel):
    pool_ip_type: str | None = Field('static_res', description="use in case you want to get the amount of ISP IPs available, the default amount for that API endpoint is data center peer IPs.")
    ips_type: str | None = Field(None, description="type of IPs. \n\n `shared`: For shared \n\n `selective`: For selective \n\n `dedicated`: For dedicated \n\n")
    country: str | None = Field(None, description="IPs location country")
    country_city: str | None = Field(None, description="defines the city location of the IPs")
    city: bool | None = Field(None, description="required with `country_city` parameter")
    domain_whitelist: str | None = Field(None, description="Space separated list of domains \n\n **Note**: for `curl` the spaces should be urlencoded : `d1.com%20d2.com`")
    geo_db: GetZoneCountAvailableIpsQueryPlanGeoDb | None = Field(None, description="turns on/off using of the IP`s location databases")


# Rebuild models to resolve forward references (required for circular refs)
GetZoneCountAvailableIpsQueryPlan.model_rebuild()
GetZoneCountAvailableIpsQueryPlanGeoDb.model_rebuild()

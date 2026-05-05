"""
Google Search Api MCP Server - Pydantic Models

Generated: 2026-05-05 15:14:39 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "SearchGoogleRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: search_google
class SearchGoogleRequestQuery(StrictModel):
    engine: Literal["google"] = Field(default=..., description="The search engine identifier. Must be set to 'google' to use Google's search engine.")
    api_key: str = Field(default=..., description="Authentication key for API requests. Provide as a query parameter or in the Authorization header using Bearer token format.")
    q: str | None = Field(default=None, description="The search query string. Supports Google's advanced search operators (inurl:, site:, intitle:, etc.). Either this or kgmid must be provided.")
    kgmid: str | None = Field(default=None, description="A Knowledge Graph identifier representing a specific entity. Format: Location identifiers start with /m/ followed by 2-7 characters; general entity identifiers start with /g/ followed by longer alphanumeric strings. Find identifiers via Wikidata's Freebase ID. Either this or q must be provided.")
    device: Literal["desktop", "mobile", "tablet"] | None = Field(default=None, description="The device type for search results. Choose from desktop (default), mobile, or tablet to simulate searches from different device types.")
    uule: str | None = Field(default=None, description="Google-encoded location parameter for geographically-targeted results. Cannot be used together with the location parameter. SearchApi generates this automatically when using location.")
    gl: Literal["af", "al", "dz", "as", "ad", "ao", "ai", "aq", "ag", "ar", "am", "aw", "au", "at", "az", "bs", "bh", "bd", "bb", "by", "be", "bz", "bj", "bm", "bt", "bo", "ba", "bw", "bv", "br", "io", "bn", "bg", "bf", "bi", "kh", "cm", "ca", "cv", "ky", "cf", "td", "cl", "cn", "cx", "cc", "co", "km", "cg", "cd", "ck", "cr", "ci", "hr", "cu", "cy", "cz", "dk", "dj", "dm", "do", "ec", "eg", "sv", "gq", "er", "ee", "et", "fk", "fo", "fj", "fi", "fr", "gf", "pf", "tf", "ga", "gm", "ge", "de", "gh", "gi", "gr", "gl", "gd", "gp", "gu", "gt", "gn", "gw", "gy", "ht", "hm", "va", "hn", "hk", "hu", "is", "in", "id", "ir", "iq", "ie", "il", "it", "jm", "jp", "jo", "kz", "ke", "ki", "kp", "kr", "kw", "kg", "la", "lv", "lb", "ls", "lr", "ly", "li", "lt", "lu", "mo", "mk", "mg", "mw", "my", "mv", "ml", "mt", "mh", "mq", "mr", "mu", "yt", "mx", "fm", "md", "mc", "mn", "ms", "ma", "mz", "mm", "na", "nr", "np", "nl", "nc", "nz", "ni", "ne", "ng", "nu", "nf", "mp", "no", "om", "pk", "pw", "ps", "pa", "pg", "py", "pe", "ph", "pn", "pl", "pt", "pr", "qa", "re", "ro", "ru", "rw", "sh", "kn", "lc", "pm", "vc", "ws", "sm", "st", "sa", "sn", "rs", "sc", "sl", "sg", "sk", "si", "sb", "so", "za", "gs", "es", "lk", "sd", "sr", "sj", "sz", "se", "ch", "sy", "tw", "tj", "tz", "th", "tl", "tg", "tk", "to", "tt", "tn", "tr", "tm", "tc", "tv", "ug", "ua", "ae", "uk", "gb", "us", "um", "uy", "uz", "vu", "ve", "vn", "vg", "vi", "wf", "eh", "ye", "zm", "zw", "gg", "je", "im", "me"] | None = Field(default=None, description="Two-letter country code (e.g., 'us', 'gb', 'de') to restrict results to a specific country. Defaults to 'us'. See Google Shopping countries list for all supported codes.")
    hl: Literal["af", "ak", "sq", "am", "ar", "hy", "az", "eu", "be", "bem", "bn", "bh", "xx-bork", "bs", "br", "bg", "km", "ca", "chr", "ny", "zh-cn", "zh-tw", "co", "hr", "cs", "da", "nl", "xx-elmer", "en", "eo", "et", "ee", "fo", "tl", "fi", "fr", "fy", "gaa", "gl", "ka", "de", "el", "kl", "gn", "gu", "xx-hacker", "ht", "ha", "haw", "iw", "hi", "hu", "is", "ig", "id", "ia", "ga", "it", "ja", "jw", "kn", "kk", "rw", "rn", "xx-klingon", "kg", "ko", "kri", "ku", "ckb", "ky", "lo", "la", "lv", "ln", "lt", "loz", "lg", "ach", "mk", "mg", "my", "ms", "ml", "mt", "mv", "mi", "mr", "mfe", "mo", "mn", "sr-me", "ne", "pcm", "nso", "no", "nn", "oc", "or", "om", "ps", "fa", "xx-pirate", "pl", "pt", "pt-br", "pt-pt", "pa", "qu", "ro", "rm", "nyn", "ru", "gd", "sr", "sh", "st", "tn", "crs", "sn", "sd", "si", "sk", "sl", "so", "es", "es-419", "su", "sw", "sv", "tg", "ta", "tt", "te", "th", "ti", "to", "lua", "tum", "tr", "tk", "tw", "ug", "uk", "ur", "uz", "vu", "vi", "cy", "wo", "xh", "yi", "yo", "zu"] | None = Field(default=None, description="Two-letter language code (e.g., 'en', 'fr', 'ja') to set the search interface language. Defaults to 'en'. Supports all Google interface languages.")
    lr: str | None = Field(default=None, description="Restricts results to documents in specific languages using the format lang_XX or multiple languages with pipe separation (e.g., lang_en|lang_de). Google identifies language via TLD, meta tags, or document content.", pattern='^lang_[a-z]{2}(-[A-Z]{2})?(\\|lang_[a-z]{2}(-[A-Z]{2})?)*$')
    cr: str | None = Field(default=None, description="Restricts results to documents originating from a specific country, determined by the document's top-level domain or server IP geolocation.")
    filter_: Literal["0", "1"] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Controls duplicate content and host crowding filters. Set to '1' (default) to enable filters or '0' to disable them.")
    safe: Literal["active", "blur", "off"] | None = Field(default=None, description="SafeSearch filtering level. Use 'active' for strict filtering, 'blur' (default) to blur explicit images, or 'off' to disable SafeSearch entirely.")
    time_period_min: str | None = Field(default=None, description="Start date for filtering results by publication date. Format: MM/DD/YYYY. Use with time_period_max to define a date range.", pattern='^(0?[1-9]|1[0-2])\\/(0?[1-9]|[12][0-9]|3[01])\\/(19|20)\\d\\d$')
    time_period_max: str | None = Field(default=None, description="End date for filtering results by publication date. Format: MM/DD/YYYY. Use with time_period_min to define a date range.", pattern='^(0?[1-9]|1[0-2])\\/(0?[1-9]|[12][0-9]|3[01])\\/(19|20)\\d\\d$')
    page: int | None = Field(default=None, description="Results page number to retrieve, starting from 1 (default). Use for pagination through search results.", ge=1)
    optimization_strategy: Literal["performance", "ads"] | None = Field(default=None, description="Optimization strategy for the request. Use 'performance' (default) for faster responses or 'ads' to optimize for higher ad collection success rates at the cost of longer processing times.")
    verbatim: Literal["true"] | None = Field(default=None, description="Forces exact keyword matching by disabling spelling corrections, synonyms, and query variations. Set to 'true' to enable. Stricter than nfpr parameter.")
class SearchGoogleRequest(StrictModel):
    """Execute a Google search with customizable filters, location targeting, and result pagination. Supports advanced search operators, Knowledge Graph entity lookups, and device-specific results."""
    query: SearchGoogleRequestQuery

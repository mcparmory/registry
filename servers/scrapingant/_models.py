"""
Scrapingant MCP Server - Pydantic Models

Generated: 2026-05-12 12:34:25 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "ScrapingantGeneralRequestV2GeneralGet2Request",
    "ScrapingantGeneralRequestV2GeneralGet3Request",
    "ScrapingantGeneralRequestV2GeneralGet4Request",
    "ScrapingantGeneralRequestV2GeneralGet5Request",
    "ScrapingantGeneralRequestV2GeneralGetRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: scrape_webpage
class ScrapingantGeneralRequestV2GeneralGet4RequestQuery(StrictModel):
    url: str = Field(default=..., description="The target URL to scrape. Must be a valid, complete URL.")
    browser: bool | None = Field(default=None, description="Whether to render the page using a headless browser to execute JavaScript and load dynamic content. Enabled by default. Disable to retrieve raw server response only.")
    return_page_source: bool | None = Field(default=None, description="Return the unaltered HTML source from the server without browser-based JavaScript rendering. Only applies when browser rendering is enabled. Useful for comparing server-side vs. client-side rendered content.")
    cookies: str | None = Field(default=None, description="Session cookies to include with the scraping request, formatted as semicolon-separated key-value pairs (e.g., name1=value1;name2=value2). Useful for authenticated scraping.")
    js_snippet: str | None = Field(default=None, description="Base64-encoded JavaScript code to execute after the page loads in the browser. Only applies when browser rendering is enabled. Useful for custom interactions like scrolling or form submission.")
    proxy_type: str | None = Field(default=None, description="Proxy type for the request: datacenter (faster, shared IPs) or residential (slower, real user IPs). Defaults to datacenter.")
    proxy_country: str | None = Field(default=None, description="Country code for the proxy location (e.g., US, GB, DE). If not specified, a random country will be used. Only applies when using a proxy.")
    wait_for_selector: str | None = Field(default=None, description="CSS selector of an element to wait for before returning results. The scraper will poll until the element appears in the DOM. Only applies when browser rendering is enabled. Useful for waiting on dynamically loaded content.")
    block_resource: str | None = Field(default=None, description="Resource types to block from loading in the browser (e.g., image, stylesheet, script, font). Can be specified multiple times for multiple types. Only applies when browser rendering is enabled. Useful for faster scraping when certain resources aren't needed.")
class ScrapingantGeneralRequestV2GeneralGet4Request(StrictModel):
    """Scrape content from a webpage with optional browser rendering, JavaScript execution, and proxy configuration. Supports cookie injection, resource blocking, and element-specific wait conditions for dynamic content."""
    query: ScrapingantGeneralRequestV2GeneralGet4RequestQuery

# Operation: scrape_webpage_submit
class ScrapingantGeneralRequestV2GeneralGet5RequestQuery(StrictModel):
    url: str = Field(default=..., description="The target URL to scrape. Must be a valid, complete URL.")
    browser: bool | None = Field(default=None, description="Enable headless browser rendering to execute JavaScript and handle dynamic content. Defaults to true. When disabled, only raw server response is returned.")
    return_page_source: bool | None = Field(default=None, description="Return the unaltered page source as received from the server without JavaScript rendering. Only applies when browser is enabled. Defaults to false.")
    cookies: str | None = Field(default=None, description="HTTP cookies to include with the scraping request, formatted as semicolon-separated key-value pairs (e.g., name1=value1;name2=value2).")
    js_snippet: str | None = Field(default=None, description="Base64-encoded JavaScript code to execute after the page loads in the browser. Only applies when browser is enabled. Useful for interactions, scrolling, or data extraction.")
    proxy_type: str | None = Field(default=None, description="Proxy type for the request: datacenter (faster, shared IPs) or residential (slower, real user IPs). Defaults to datacenter.")
    proxy_country: str | None = Field(default=None, description="Country code for proxy location (e.g., US, GB, DE). If not specified, a random country is selected. Only applies when using a proxy.")
    wait_for_selector: str | None = Field(default=None, description="CSS selector of an element to wait for before returning results. The scraper will poll until the element appears or timeout occurs. Only applies when browser is enabled.")
    block_resource: str | None = Field(default=None, description="Resource types to block from loading in the browser (e.g., image, stylesheet, script, font). Reduces bandwidth and speeds up scraping. Only applies when browser is enabled. Can be specified multiple times for multiple resource types.")
class ScrapingantGeneralRequestV2GeneralGet5Request(StrictModel):
    """Scrape content from a webpage using optional headless browser rendering, JavaScript execution, and proxy configuration. Supports cookie injection, resource blocking, and element-specific wait conditions for dynamic content."""
    query: ScrapingantGeneralRequestV2GeneralGet5RequestQuery

# Operation: scrape_webpage_replace
class ScrapingantGeneralRequestV2GeneralGet3RequestQuery(StrictModel):
    url: str = Field(default=..., description="The target URL to scrape. Must be a valid HTTP or HTTPS URL.")
    browser: bool | None = Field(default=None, description="Whether to use a headless browser for scraping to render JavaScript and handle dynamic content. Enabled by default. Required for JS execution, page source capture, and element waiting.")
    return_page_source: bool | None = Field(default=None, description="Return the unaltered HTML returned by the server without JavaScript rendering. Only applies when browser is enabled. When true, JavaScript will not be executed.")
    cookies: str | None = Field(default=None, description="Cookies to include with the scraping request, formatted as semicolon-separated key-value pairs (e.g., name1=value1;name2=value2).")
    js_snippet: str | None = Field(default=None, description="Base64-encoded JavaScript code to execute after the page loads in the browser. Only applies when browser is enabled. Useful for interactions, scrolling, or data extraction.")
    proxy_type: str | None = Field(default=None, description="Type of proxy to use for the request: datacenter (default) for speed or residential for authenticity. Datacenter proxies are faster; residential proxies better mimic real users.")
    proxy_country: str | None = Field(default=None, description="Country code for the proxy location (e.g., US, GB, DE). If not specified, a random country will be used. Only applies when using proxies.")
    wait_for_selector: str | None = Field(default=None, description="CSS selector of an element to wait for before returning results. The scraper will poll until the element appears in the DOM. Only applies when browser is enabled.")
    block_resource: str | None = Field(default=None, description="Resource types to block from loading in the browser (e.g., image, stylesheet, script, font). Can be specified multiple times for multiple types. Only applies when browser is enabled. Reduces bandwidth and speeds up scraping.")
class ScrapingantGeneralRequestV2GeneralGet3Request(StrictModel):
    """Scrape a webpage with optional browser rendering, JavaScript execution, and proxy configuration. Supports cookie injection, resource blocking, and element-based wait conditions for dynamic content."""
    query: ScrapingantGeneralRequestV2GeneralGet3RequestQuery

# Operation: scrape_webpage_modify
class ScrapingantGeneralRequestV2GeneralGetRequestQuery(StrictModel):
    url: str = Field(default=..., description="The target URL to scrape. Must be a valid HTTP or HTTPS URL.")
    browser: bool | None = Field(default=None, description="Whether to use a headless browser for scraping to render JavaScript and handle dynamic content. Enabled by default. Required for JS execution, page waiting, and resource blocking features.")
    return_page_source: bool | None = Field(default=None, description="Return the unaltered HTML source as received from the server without JavaScript rendering. Only applies when browser is enabled. Disabled by default.")
    cookies: str | None = Field(default=None, description="HTTP cookies to include with the scraping request, formatted as semicolon-separated key-value pairs (e.g., name1=value1;name2=value2).")
    js_snippet: str | None = Field(default=None, description="Base64-encoded JavaScript code to execute after the page loads in the browser. Only applies when browser is enabled. Useful for interactions, data extraction, or triggering additional content loads.")
    proxy_type: str | None = Field(default=None, description="Type of proxy to route the request through: datacenter (faster, shared IPs) or residential (slower, real user IPs). Defaults to datacenter.")
    proxy_country: str | None = Field(default=None, description="Country code for the proxy location (e.g., US, GB, DE). If not specified, a random country will be used. Only applies when using a proxy.")
    wait_for_selector: str | None = Field(default=None, description="CSS selector of an element to wait for before returning results. The scraper will poll until the element appears in the DOM. Only applies when browser is enabled.")
    block_resource: str | None = Field(default=None, description="Resource types to block from loading in the browser (e.g., image, stylesheet, script, font, xhr, fetch). Reduces bandwidth and speeds up scraping. Only applies when browser is enabled. Can be specified multiple times for multiple resource types.")
class ScrapingantGeneralRequestV2GeneralGetRequest(StrictModel):
    """Scrape a webpage with optional browser rendering, JavaScript execution, and proxy configuration. Supports waiting for dynamic content, blocking resources, and injecting custom scripts."""
    query: ScrapingantGeneralRequestV2GeneralGetRequestQuery

# Operation: scrape_webpage_remove
class ScrapingantGeneralRequestV2GeneralGet2RequestQuery(StrictModel):
    url: str = Field(default=..., description="The target URL to scrape. Must be a valid, complete URL.")
    browser: bool | None = Field(default=None, description="Whether to use a headless browser for scraping to handle JavaScript-rendered content. Enabled by default. Required for JS execution and resource blocking features.")
    return_page_source: bool | None = Field(default=None, description="Return the unaltered HTML as received from the server without JavaScript rendering. Only applies when browser is enabled. Disabled by default.")
    cookies: str | None = Field(default=None, description="HTTP cookies to include with the scraping request, formatted as semicolon-separated key-value pairs (e.g., name1=value1;name2=value2).")
    js_snippet: str | None = Field(default=None, description="Base64-encoded JavaScript code to execute after the page loads in the browser. Only applies when browser is enabled. Useful for interactions, scrolling, or data extraction.")
    proxy_type: str | None = Field(default=None, description="Type of proxy to route the request through: datacenter (faster, shared IPs) or residential (slower, real user IPs). Defaults to datacenter.")
    proxy_country: str | None = Field(default=None, description="Country code for the proxy location (e.g., US, GB, DE). If not specified, a random country will be used.")
    wait_for_selector: str | None = Field(default=None, description="CSS selector of an element to wait for before returning results. The service will poll until the element appears in the DOM. Only applies when browser is enabled.")
    block_resource: str | None = Field(default=None, description="Resource types to block from loading in the browser (e.g., image, stylesheet, script, font). Reduces bandwidth and speeds up scraping. Only applies when browser is enabled. Can be specified multiple times for multiple resource types.")
class ScrapingantGeneralRequestV2GeneralGet2Request(StrictModel):
    """Scrape a webpage with optional browser rendering, JavaScript execution, and proxy configuration. Supports cookie injection, resource blocking, and element-waiting strategies for dynamic content extraction."""
    query: ScrapingantGeneralRequestV2GeneralGet2RequestQuery

"""
Firecrawl MCP Server - Pydantic Models

Generated: 2026-05-05 14:59:29 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "CancelBatchScrapeRequest",
    "CancelCrawlRequest",
    "CrawlUrlsRequest",
    "ExtractDataRequest",
    "GenerateLlMsTxtRequest",
    "GetBatchScrapeErrorsRequest",
    "GetBatchScrapeStatusRequest",
    "GetCrawlErrorsRequest",
    "GetCrawlStatusRequest",
    "GetDeepResearchStatusRequest",
    "GetExtractStatusRequest",
    "GetHistoricalCreditUsageRequest",
    "GetHistoricalTokenUsageRequest",
    "GetLlMsTxtStatusRequest",
    "MapUrlsRequest",
    "ScrapeAndExtractFromUrlRequest",
    "ScrapeAndExtractFromUrlsRequest",
    "SearchAndScrapeRequest",
    "StartDeepResearchRequest",
    "ScrapeAndExtractFromUrlBody",
    "ScrapeAndExtractFromUrlsBody",
    "ScrapeOptions",
    "SearchAndScrapeBodyScrapeOptions",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: scrape_and_extract_webpage
class ScrapeAndExtractFromUrlRequestBody(StrictModel):
    body: ScrapeAndExtractFromUrlBody = Field(default=..., description="Request payload containing the URL to scrape and extraction parameters, including the target URL and optional LLM extraction instructions or schema.")
class ScrapeAndExtractFromUrlRequest(StrictModel):
    """Scrapes content from a specified URL and uses LLM-powered extraction to identify and structure relevant information from the page."""
    body: ScrapeAndExtractFromUrlRequestBody

# Operation: scrape_and_extract_urls
class ScrapeAndExtractFromUrlsRequestBody(StrictModel):
    body: ScrapeAndExtractFromUrlsBody = Field(default=..., description="Request payload containing the list of URLs to scrape and extraction configuration. Specify target URLs, extraction rules, and LLM processing options for batch operations.")
class ScrapeAndExtractFromUrlsRequest(StrictModel):
    """Scrape content from multiple URLs and extract structured information using LLM-powered analysis. Supports batch processing with optional intelligent data extraction."""
    body: ScrapeAndExtractFromUrlsRequestBody

# Operation: get_batch_scrape_status
class GetBatchScrapeStatusRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the batch scrape job to check status for.", json_schema_extra={'format': 'uuid'})
class GetBatchScrapeStatusRequest(StrictModel):
    """Retrieve the current status and progress of a batch scraping job. Use this to monitor ongoing or completed scrape operations."""
    path: GetBatchScrapeStatusRequestPath

# Operation: cancel_batch_scrape
class CancelBatchScrapeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the batch scraping job to cancel.", json_schema_extra={'format': 'uuid'})
class CancelBatchScrapeRequest(StrictModel):
    """Cancels an active batch scraping job by its ID. The job will stop processing immediately and any pending tasks will be abandoned."""
    path: CancelBatchScrapeRequestPath

# Operation: list_batch_scrape_errors
class GetBatchScrapeErrorsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the batch scraping job for which to retrieve errors.", json_schema_extra={'format': 'uuid'})
class GetBatchScrapeErrorsRequest(StrictModel):
    """Retrieve all errors that occurred during a batch scraping job. Use this to diagnose failures and understand which URLs or data extraction steps encountered issues."""
    path: GetBatchScrapeErrorsRequestPath

# Operation: get_crawl_status
class GetCrawlStatusRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the crawl job to retrieve status for. Must be a valid UUID.", json_schema_extra={'format': 'uuid'})
class GetCrawlStatusRequest(StrictModel):
    """Retrieve the current status and progress of a crawl job by its unique identifier. Use this to monitor ongoing or completed web crawling operations."""
    path: GetCrawlStatusRequestPath

# Operation: cancel_crawl
class CancelCrawlRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the crawl job to cancel. Must be a valid UUID.", json_schema_extra={'format': 'uuid'})
class CancelCrawlRequest(StrictModel):
    """Cancel an active or pending crawl job by its ID. Once cancelled, the crawl will stop processing and cannot be resumed."""
    path: CancelCrawlRequestPath

# Operation: list_crawl_errors
class GetCrawlErrorsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the crawl job for which to retrieve errors.", json_schema_extra={'format': 'uuid'})
class GetCrawlErrorsRequest(StrictModel):
    """Retrieve all errors encountered during a specific crawl job. Returns detailed error information to help diagnose and troubleshoot crawling issues."""
    path: GetCrawlErrorsRequestPath

# Operation: crawl_urls
class CrawlUrlsRequestBodyWebhook(StrictModel):
    url: str = Field(default=..., validation_alias="url", serialization_alias="url", description="Webhook endpoint that receives crawl lifecycle events: crawl.started (when crawling begins), crawl.page (for each page processed), and crawl.completed or crawl.failed (when finished). Response format matches the /scrape endpoint.")
    headers: dict[str, str] | None = Field(default=None, validation_alias="headers", serialization_alias="headers", description="Custom HTTP headers to include in all webhook requests sent to the webhook URL.")
    metadata: dict[str, Any] | None = Field(default=None, validation_alias="metadata", serialization_alias="metadata", description="Custom metadata object included in all webhook payloads for this crawl. Useful for tracking, correlation, or passing context through the crawl lifecycle.")
    events: list[Literal["completed", "page", "failed", "started"]] | None = Field(default=None, validation_alias="events", serialization_alias="events", description="Array of event types to send to the webhook URL. If not specified, all event types are sent. Valid events include crawl.started, crawl.page, crawl.completed, and crawl.failed.")
class CrawlUrlsRequestBody(StrictModel):
    url: str = Field(default=..., description="The base URL where crawling begins. All discovered URLs must be relative to this domain unless external link following is enabled.", json_schema_extra={'format': 'uri'})
    exclude_paths: list[str] | None = Field(default=None, validation_alias="excludePaths", serialization_alias="excludePaths", description="Regular expression patterns to exclude URL paths from crawling. Patterns match against the path component of URLs (e.g., 'blog/.*' excludes all blog paths). Multiple patterns can be specified as an array.")
    include_paths: list[str] | None = Field(default=None, validation_alias="includePaths", serialization_alias="includePaths", description="Regular expression patterns to include only matching URL paths in crawling results. Only paths matching these patterns will be processed. Multiple patterns can be specified as an array.")
    regex_on_full_url: bool | None = Field(default=None, validation_alias="regexOnFullURL", serialization_alias="regexOnFullURL", description="When true, includePaths and excludePaths patterns match against the full URL including query parameters. When false, patterns match only the path component.")
    max_depth: int | None = Field(default=None, validation_alias="maxDepth", serialization_alias="maxDepth", description="Maximum absolute depth from the base URL's path. Represents the maximum number of forward slashes allowed in discovered URL paths relative to the base.")
    max_discovery_depth: int | None = Field(default=None, validation_alias="maxDiscoveryDepth", serialization_alias="maxDiscoveryDepth", description="Maximum discovery depth based on link traversal order. Root pages and sitemap-discovered pages have depth 0. Each subsequent level of links increases depth by 1.")
    ignore_query_parameters: bool | None = Field(default=None, validation_alias="ignoreQueryParameters", serialization_alias="ignoreQueryParameters", description="When true, prevents re-crawling the same path with different query parameters. Treats URLs with identical paths but different query strings as duplicates.")
    limit: int | None = Field(default=None, description="Maximum number of pages to crawl. Crawling stops once this limit is reached.")
    crawl_entire_domain: bool | None = Field(default=None, validation_alias="crawlEntireDomain", serialization_alias="crawlEntireDomain", description="When true, crawler follows internal links at any level (sibling, parent, child paths). When false, crawler only follows deeper nested paths. Set to true to comprehensively cover the entire site structure.")
    allow_external_links: bool | None = Field(default=None, validation_alias="allowExternalLinks", serialization_alias="allowExternalLinks", description="When true, crawler follows links to external domains outside the base domain. When false, only internal links are followed.")
    allow_subdomains: bool | None = Field(default=None, validation_alias="allowSubdomains", serialization_alias="allowSubdomains", description="When true, crawler follows links to subdomains under the main domain. When false, only the primary domain is crawled.")
    delay: float | None = Field(default=None, description="Wait time in seconds between consecutive scraping requests. Use to respect website rate limits and avoid overwhelming target servers.")
    max_concurrency: int | None = Field(default=None, validation_alias="maxConcurrency", serialization_alias="maxConcurrency", description="Maximum number of concurrent scraping operations. Limits parallelism for this crawl job. If not specified, the team's concurrency limit applies.")
    scrape_options: ScrapeOptions | None = Field(default=None, validation_alias="scrapeOptions", serialization_alias="scrapeOptions", description="Additional scraping options to apply to all pages discovered during crawling. Inherits configuration from the /scrape endpoint.")
    webhook: CrawlUrlsRequestBodyWebhook
class CrawlUrlsRequest(StrictModel):
    """Crawl multiple URLs from a base domain with configurable filtering, depth limits, and webhook notifications. Supports path-based inclusion/exclusion patterns, subdomain traversal, and concurrent scraping with rate limiting."""
    body: CrawlUrlsRequestBody

# Operation: crawl_urls_map
class MapUrlsRequestBody(StrictModel):
    url: str = Field(default=..., description="The base URL where crawling begins. Must be a valid URI.", json_schema_extra={'format': 'uri'})
    search: str | None = Field(default=None, description="Search query to filter mapped URLs. During alpha phase, smart search features are limited to the first 500 results, though the map operation may discover additional results beyond this limit.")
    sitemap_only: bool | None = Field(default=None, validation_alias="sitemapOnly", serialization_alias="sitemapOnly", description="If enabled, return only links that are included in the website's sitemap.")
    include_subdomains: bool | None = Field(default=None, validation_alias="includeSubdomains", serialization_alias="includeSubdomains", description="If enabled, include URLs from the site's subdomains in the results.")
    limit: int | None = Field(default=None, description="Maximum number of links to return. The API can discover up to 30,000 links, but results are capped at this limit.", le=30000)
class MapUrlsRequest(StrictModel):
    """Crawl and map multiple URLs from a website based on specified options. Discovers all accessible links starting from a base URL, with optional filtering by search query, sitemap, subdomains, and result limits."""
    body: MapUrlsRequestBody

# Operation: extract_structured_data
class ExtractDataRequestBody(StrictModel):
    urls: list[str] = Field(default=..., description="List of URLs to extract structured data from. URLs are processed in the order provided.")
    enable_web_search: bool | None = Field(default=None, validation_alias="enableWebSearch", serialization_alias="enableWebSearch", description="Enable web search to supplement data extraction with additional information from search results.")
    include_subdomains: bool | None = Field(default=None, validation_alias="includeSubdomains", serialization_alias="includeSubdomains", description="Include subdomains of the specified URLs in the extraction scope.")
    show_sources: bool | None = Field(default=None, validation_alias="showSources", serialization_alias="showSources", description="Include source attribution in the response, showing which sources were used to extract each data point.")
    scrape_options: ScrapeOptions | None = Field(default=None, validation_alias="scrapeOptions", serialization_alias="scrapeOptions", description="Additional configuration options for the scraping behavior, such as timeout settings, headers, or parsing preferences.")
class ExtractDataRequest(StrictModel):
    """Extract structured data from web pages using LLM analysis. Optionally augment extraction with web search, subdomain scanning, and source attribution."""
    body: ExtractDataRequestBody

# Operation: get_extraction_status
class GetExtractStatusRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the extraction job to check status for.", json_schema_extra={'format': 'uuid'})
class GetExtractStatusRequest(StrictModel):
    """Retrieve the current status of a data extraction job using its unique identifier. Returns the job's progress, completion state, and any relevant metadata."""
    path: GetExtractStatusRequestPath

# Operation: initiate_deep_research
class StartDeepResearchRequestBodyJsonOptions(StrictModel):
    system_prompt: str | None = Field(default=None, validation_alias="systemPrompt", serialization_alias="systemPrompt", description="System prompt for controlling JSON output generation behavior and formatting")
class StartDeepResearchRequestBody(StrictModel):
    query: str = Field(default=..., description="The research topic or question to investigate")
    max_depth: int | None = Field(default=None, validation_alias="maxDepth", serialization_alias="maxDepth", description="Controls the depth of iterative research cycles, determining how many levels of follow-up analysis to perform", ge=1, le=12)
    max_urls: int | None = Field(default=None, validation_alias="maxUrls", serialization_alias="maxUrls", description="Limits the number of URLs to analyze during the research process", ge=1, le=1000)
    analysis_prompt: str | None = Field(default=None, validation_alias="analysisPrompt", serialization_alias="analysisPrompt", description="Custom prompt template for formatting the final analysis results in Markdown. Used to structure the output according to specific requirements")
    formats: list[Literal["markdown", "json"]] | None = Field(default=None, description="Output formats for the research results. Specifies which format types to include in the response")
    json_options: StartDeepResearchRequestBodyJsonOptions | None = Field(default=None, validation_alias="jsonOptions", serialization_alias="jsonOptions")
class StartDeepResearchRequest(StrictModel):
    """Initiates a comprehensive research process that iteratively analyzes multiple sources to deeply investigate a query. Returns structured findings formatted according to specified analysis requirements."""
    body: StartDeepResearchRequestBody

# Operation: get_deep_research_status
class GetDeepResearchStatusRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the research job to retrieve status for.", json_schema_extra={'format': 'uuid'})
class GetDeepResearchStatusRequest(StrictModel):
    """Retrieve the current status and results of a deep research job. Use this to check progress and access findings from an ongoing or completed research task."""
    path: GetDeepResearchStatusRequestPath

# Operation: list_credit_usage_history
class GetHistoricalCreditUsageRequestQuery(StrictModel):
    by_api_key: bool | None = Field(default=None, validation_alias="byApiKey", serialization_alias="byApiKey", description="When enabled, returns credit usage history grouped by API key instead of aggregated team-level data.")
class GetHistoricalCreditUsageRequest(StrictModel):
    """Retrieve the credit usage history for the authenticated team. Optionally filter results to show credit consumption broken down by individual API keys."""
    query: GetHistoricalCreditUsageRequestQuery | None = None

# Operation: list_token_usage_history
class GetHistoricalTokenUsageRequestQuery(StrictModel):
    by_api_key: bool | None = Field(default=None, validation_alias="byApiKey", serialization_alias="byApiKey", description="When enabled, returns token usage broken down by each API key instead of aggregated team totals.")
class GetHistoricalTokenUsageRequest(StrictModel):
    """Retrieve historical token usage data for the authenticated team. Optionally break down usage by individual API keys."""
    query: GetHistoricalTokenUsageRequestQuery | None = None

# Operation: search_and_scrape_results
class SearchAndScrapeRequestBody(StrictModel):
    query: str = Field(default=..., description="The search query string to execute.")
    limit: int | None = Field(default=None, description="Maximum number of search results to return. Valid range is 1 to 100 results.", ge=1, le=100)
    tbs: str | None = Field(default=None, description="Time-based search filter. Supports predefined ranges (last hour, day, week, month, year) or custom date ranges with minimum and maximum dates.")
    location: str | None = Field(default=None, description="Geographic location to filter search results by region or locality.")
    scrape_options: SearchAndScrapeBodyScrapeOptions | None = Field(default=None, validation_alias="scrapeOptions", serialization_alias="scrapeOptions", description="Configuration options for scraping content from search results, such as depth, timeout, or content extraction preferences.")
class SearchAndScrapeRequest(StrictModel):
    """Execute a web search and optionally scrape detailed content from the results. Supports time-based filtering, location-specific searches, and customizable scraping behavior."""
    body: SearchAndScrapeRequestBody

# Operation: generate_llms_txt
class GenerateLlMsTxtRequestBody(StrictModel):
    url: str = Field(default=..., description="The website URL to analyze and generate the LLMs.txt file from. Must be a valid URI.", json_schema_extra={'format': 'uri'})
    max_urls: int | None = Field(default=None, validation_alias="maxUrls", serialization_alias="maxUrls", description="Maximum number of URLs to crawl and analyze from the starting URL. Controls the scope of content extraction.")
    show_full_text: bool | None = Field(default=None, validation_alias="showFullText", serialization_alias="showFullText", description="Include the complete extracted text content in the response. When disabled, returns only metadata and summary information.")
class GenerateLlMsTxtRequest(StrictModel):
    """Generate an LLMs.txt file for a website to improve AI model discoverability and interaction. This operation crawls the specified URL and extracts relevant content to create a standardized LLMs.txt file."""
    body: GenerateLlMsTxtRequestBody

# Operation: get_llms_txt_generation_status
class GetLlMsTxtStatusRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the LLMs.txt generation job to retrieve status for.", json_schema_extra={'format': 'uuid'})
class GetLlMsTxtStatusRequest(StrictModel):
    """Retrieve the current status and results of an LLMs.txt generation job. Use this to check if a generation job has completed and access the generated content."""
    path: GetLlMsTxtStatusRequestPath

# ============================================================================
# Component Models
# ============================================================================

class BaseScrapeOptionsActionsItemV0(PermissiveModel):
    type_: Literal["wait"] = Field(..., validation_alias="type", serialization_alias="type", description="指定したミリ秒間待機します")
    milliseconds: int | None = Field(None, description="待機する時間（ミリ秒）", ge=1)
    selector: str | None = Field(None, description="要素を検索するためのクエリセレクタ")

class BaseScrapeOptionsActionsItemV1(PermissiveModel):
    type_: Literal["screenshot"] = Field(..., validation_alias="type", serialization_alias="type", description="スクリーンショットを撮影します。リンクはレスポンスの `actions.screenshots` 配列に含まれます。")
    full_page: bool | None = Field(False, validation_alias="fullPage", serialization_alias="fullPage", description="ページ全体のスクリーンショットを取得するか、現在のビューポートに限定するかを指定します。")
    quality: int | None = Field(None, description="スクリーンショットの品質を1〜100で指定します。100が最高品質です。")

class BaseScrapeOptionsActionsItemV2(PermissiveModel):
    type_: Literal["click"] = Field(..., validation_alias="type", serialization_alias="type", description="要素をクリックします")
    selector: str = Field(..., description="要素を検索するためのクエリセレクタ")
    all_: bool | None = Field(False, validation_alias="all", serialization_alias="all", description="セレクターに一致する要素を、最初のものだけでなくすべてクリックします。セレクターに一致する要素が存在しない場合でも、エラーは発生しません。")

class BaseScrapeOptionsActionsItemV3(PermissiveModel):
    type_: Literal["write"] = Field(..., validation_alias="type", serialization_alias="type", description="入力フィールド、テキストエリア、または contenteditable 要素にテキストを入力します。注意: テキストを入力する前に、必ず「click」アクションで要素にフォーカスを当ててください。テキストはキーボード入力をシミュレートするため、1文字ずつタイプされます。")
    text: str = Field(..., description="入力するテキスト")

class BaseScrapeOptionsActionsItemV4(PermissiveModel):
    """ページ上でキーを押してください。キーコードについては https://asawicki.info/nosense/doc/devices/keyboard/key_codes.html を参照してください。"""
    type_: Literal["press"] = Field(..., validation_alias="type", serialization_alias="type", description="このページでいずれかのキーを押してください")
    key: str = Field(..., description="押下するキー")

class BaseScrapeOptionsActionsItemV5(PermissiveModel):
    type_: Literal["scroll"] = Field(..., validation_alias="type", serialization_alias="type", description="ページ全体または特定の要素をスクロールする")
    direction: Literal["up", "down"] | None = Field('down', description="スクロール方向")
    selector: str | None = Field(None, description="スクロール対象要素のクエリセレクター")

class BaseScrapeOptionsActionsItemV6(PermissiveModel):
    type_: Literal["scrape"] = Field(..., validation_alias="type", serialization_alias="type", description="現在のページの内容をスクレイピングし、URL と HTML を返します。")

class BaseScrapeOptionsActionsItemV7(PermissiveModel):
    type_: Literal["executeJavascript"] = Field(..., validation_alias="type", serialization_alias="type", description="ページ上で JavaScript コードを実行する")
    script: str = Field(..., description="実行する JavaScript コード")

class BaseScrapeOptionsActionsItemV8(PermissiveModel):
    type_: Literal["pdf"] = Field(..., validation_alias="type", serialization_alias="type", description="現在のページの PDF を生成します。PDF はレスポンスの `actions.pdfs` 配列で返されます。")
    format_: Literal["A0", "A1", "A2", "A3", "A4", "A5", "A6", "Letter", "Legal", "Tabloid", "Ledger"] | None = Field('Letter', validation_alias="format", serialization_alias="format", description="出力されるPDFのページサイズ")
    landscape: bool | None = Field(False, description="PDF を横向きで生成するかどうか")
    scale: float | None = Field(1, description="生成される PDF の拡大縮小倍率")

class BaseScrapeOptionsJsonOptions(PermissiveModel):
    """JSON オプションオブジェクト"""
    schema_: dict[str, Any] | None = Field(None, validation_alias="schema", serialization_alias="schema", description="抽出に使用するスキーマ（任意）。[JSON Schema](https://json-schema.org/) に準拠したものである必要があります。")
    system_prompt: str | None = Field(None, validation_alias="systemPrompt", serialization_alias="systemPrompt", description="抽出に使用するシステムプロンプト（任意）")
    prompt: str | None = Field(None, description="スキーマなしで抽出を行う際に使用するプロンプト（任意）")

class BaseScrapeOptionsLocation(PermissiveModel):
    """リクエストに対するロケーション設定です。指定されている場合、利用可能であれば適切なプロキシを使用し、対応する言語およびタイムゾーン設定を再現します。指定されていない場合は、デフォルトで 'US' が使用されます。"""
    country: str | None = Field('US', description="ISO 3166-1 alpha-2国コード（例：「US」「AU」「DE」「JP」）", pattern="^[A-Z]{2}$")
    languages: list[str] | None = Field(None, description="リクエストに対して優先順位順に指定する言語およびロケール。指定がない場合は、指定された location の言語がデフォルトになります。詳細は https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language を参照してください。")

class BaseScrapeOptions(PermissiveModel):
    only_main_content: bool | None = Field(True, validation_alias="onlyMainContent", serialization_alias="onlyMainContent", description="ヘッダー、ナビゲーション、フッターなどを除き、ページのメインコンテンツのみを返します。")
    include_tags: list[str] | None = Field(None, validation_alias="includeTags", serialization_alias="includeTags", description="出力に含めるタグ。")
    exclude_tags: list[str] | None = Field(None, validation_alias="excludeTags", serialization_alias="excludeTags", description="出力結果から除外するタグ。")
    max_age: int | None = Field(0, validation_alias="maxAge", serialization_alias="maxAge", description="ページのキャッシュが、このミリ秒数以内に生成されたものであれば、そのキャッシュされたバージョンを返します。キャッシュされたページがこの値より古い場合は、ページをスクレイピングします。極めて最新のデータが不要な場合、これを有効にすることでスクレイピングを最大 500% 高速化できます。デフォルトは 0 で、この場合キャッシュは無効になります。")
    headers: dict[str, Any] | None = Field(None, description="リクエストに付与して送信するヘッダー。Cookie や User-Agent などを送るために使用できます。")
    wait_for: int | None = Field(0, validation_alias="waitFor", serialization_alias="waitFor", description="コンテンツを取得する前に待機する時間（ディレイ）をミリ秒単位で指定します。これにより、ページが十分に読み込まれるまでの時間を確保できます。")
    mobile: bool | None = Field(False, description="モバイル端末からのスクレイピングを模擬したい場合は true に設定してください。レスポンシブページのテストやモバイル画面のスクリーンショット取得に便利です。")
    skip_tls_verification: bool | None = Field(False, validation_alias="skipTlsVerification", serialization_alias="skipTlsVerification", description="リクエスト時に TLS 証明書の検証をスキップする")
    timeout: int | None = Field(30000, description="リクエストのタイムアウト（ミリ秒）")
    parse_pdf: bool | None = Field(True, validation_alias="parsePDF", serialization_alias="parsePDF", description="スクレイピング中のPDFファイルの処理方法を制御します。true の場合、PDFのコンテンツを抽出してMarkdown形式に変換し、課金はページ数に基づきます（1ページあたり1クレジット）。false の場合、PDFファイルはbase64エンコードされたデータとして返され、合計1クレジットの定額課金となります。")
    json_options: BaseScrapeOptionsJsonOptions | None = Field(None, validation_alias="jsonOptions", serialization_alias="jsonOptions", description="JSON オプションオブジェクト")
    actions: list[BaseScrapeOptionsActionsItemV0 | BaseScrapeOptionsActionsItemV1 | BaseScrapeOptionsActionsItemV2 | BaseScrapeOptionsActionsItemV3 | BaseScrapeOptionsActionsItemV4 | BaseScrapeOptionsActionsItemV5 | BaseScrapeOptionsActionsItemV6 | BaseScrapeOptionsActionsItemV7 | BaseScrapeOptionsActionsItemV8] | None = Field(None, description="ページからコンテンツを取得する前に実行するアクション")
    location: BaseScrapeOptionsLocation | None = Field(None, description="リクエストに対するロケーション設定です。指定されている場合、利用可能であれば適切なプロキシを使用し、対応する言語およびタイムゾーン設定を再現します。指定されていない場合は、デフォルトで 'US' が使用されます。")
    remove_base64_images: bool | None = Field(True, validation_alias="removeBase64Images", serialization_alias="removeBase64Images", description="出力から、非常に長くなりがちな Base64 画像をすべて削除します。画像の alt テキストは出力内に残りますが、URL はプレースホルダーに置き換えられます。")
    block_ads: bool | None = Field(True, validation_alias="blockAds", serialization_alias="blockAds", description="広告とクッキーポップアップのブロックを有効にします。")
    proxy: Literal["basic", "enhanced", "auto"] | None = Field(None, description="使用するプロキシの種類を指定します。\n\n - **basic**: ボット対策がない、または基本的なボット対策のみが導入されているサイト向けのプロキシです。高速で、ほとんどの場合はこれで十分です。\n - **enhanced**: 高度なボット対策が導入されているサイト向けの強化プロキシです。速度は遅くなりますが、特定のサイトではより信頼性があります。1 リクエストあたり最大 5 クレジット消費します。\n - **auto**: basic プロキシでのスクレイピングが失敗した場合に、Firecrawl が自動的に enhanced プロキシで再試行します。enhanced での再試行が成功した場合、そのスクレイピングには 5 クレジットが請求されます。最初の basic での試行が成功した場合は、通常どおりのコストのみが請求されます。\n\nプロキシを指定しない場合、Firecrawl はデフォルトで basic を使用します。")
    store_in_cache: bool | None = Field(True, validation_alias="storeInCache", serialization_alias="storeInCache", description="true の場合、そのページは Firecrawl のインデックスおよびキャッシュに保存されます。スクレイピング内容がデータ保護上の懸念を伴う可能性がある場合は、これを false に設定するのが有効です。機密性の高いスクレイピングに関連する一部のパラメータ（アクションやヘッダーなど）を使用すると、このパラメータは強制的に false に設定されます。")

class ScrapeAndExtractFromUrlBodyActionsItemV0(PermissiveModel):
    type_: Literal["wait"] = Field(..., validation_alias="type", serialization_alias="type", description="指定したミリ秒間待機します")
    milliseconds: int | None = Field(None, description="待機する時間（ミリ秒）", ge=1)
    selector: str | None = Field(None, description="要素を検索するためのクエリセレクタ")

class ScrapeAndExtractFromUrlBodyActionsItemV1(PermissiveModel):
    type_: Literal["screenshot"] = Field(..., validation_alias="type", serialization_alias="type", description="スクリーンショットを撮影します。リンクはレスポンスの `actions.screenshots` 配列に含まれます。")
    full_page: bool | None = Field(False, validation_alias="fullPage", serialization_alias="fullPage", description="ページ全体のスクリーンショットを取得するか、現在のビューポートに限定するかを指定します。")
    quality: int | None = Field(None, description="スクリーンショットの品質を1〜100で指定します。100が最高品質です。")

class ScrapeAndExtractFromUrlBodyActionsItemV2(PermissiveModel):
    type_: Literal["click"] = Field(..., validation_alias="type", serialization_alias="type", description="要素をクリックします")
    selector: str = Field(..., description="要素を検索するためのクエリセレクタ")
    all_: bool | None = Field(False, validation_alias="all", serialization_alias="all", description="セレクターに一致する要素を、最初のものだけでなくすべてクリックします。セレクターに一致する要素が存在しない場合でも、エラーは発生しません。")

class ScrapeAndExtractFromUrlBodyActionsItemV3(PermissiveModel):
    type_: Literal["write"] = Field(..., validation_alias="type", serialization_alias="type", description="入力フィールド、テキストエリア、または contenteditable 要素にテキストを入力します。注意: テキストを入力する前に、必ず「click」アクションで要素にフォーカスを当ててください。テキストはキーボード入力をシミュレートするため、1文字ずつタイプされます。")
    text: str = Field(..., description="入力するテキスト")

class ScrapeAndExtractFromUrlBodyActionsItemV4(PermissiveModel):
    """ページ上でキーを押してください。キーコードについては https://asawicki.info/nosense/doc/devices/keyboard/key_codes.html を参照してください。"""
    type_: Literal["press"] = Field(..., validation_alias="type", serialization_alias="type", description="このページでいずれかのキーを押してください")
    key: str = Field(..., description="押下するキー")

class ScrapeAndExtractFromUrlBodyActionsItemV5(PermissiveModel):
    type_: Literal["scroll"] = Field(..., validation_alias="type", serialization_alias="type", description="ページ全体または特定の要素をスクロールする")
    direction: Literal["up", "down"] | None = Field('down', description="スクロール方向")
    selector: str | None = Field(None, description="スクロール対象要素のクエリセレクター")

class ScrapeAndExtractFromUrlBodyActionsItemV6(PermissiveModel):
    type_: Literal["scrape"] = Field(..., validation_alias="type", serialization_alias="type", description="現在のページの内容をスクレイピングし、URL と HTML を返します。")

class ScrapeAndExtractFromUrlBodyActionsItemV7(PermissiveModel):
    type_: Literal["executeJavascript"] = Field(..., validation_alias="type", serialization_alias="type", description="ページ上で JavaScript コードを実行する")
    script: str = Field(..., description="実行する JavaScript コード")

class ScrapeAndExtractFromUrlBodyActionsItemV8(PermissiveModel):
    type_: Literal["pdf"] = Field(..., validation_alias="type", serialization_alias="type", description="現在のページの PDF を生成します。PDF はレスポンスの `actions.pdfs` 配列で返されます。")
    format_: Literal["A0", "A1", "A2", "A3", "A4", "A5", "A6", "Letter", "Legal", "Tabloid", "Ledger"] | None = Field('Letter', validation_alias="format", serialization_alias="format", description="出力されるPDFのページサイズ")
    landscape: bool | None = Field(False, description="PDF を横向きで生成するかどうか")
    scale: float | None = Field(1, description="生成される PDF の拡大縮小倍率")

class ScrapeAndExtractFromUrlBodyChangeTrackingOptions(PermissiveModel):
    """変更追跡用のオプション（ベータ版）。changeTracking がフォーマットに含まれている場合にのみ有効です。変更追跡を使用する際は、markdown フォーマットも指定する必要があります。"""
    modes: list[Literal["git-diff", "json"]] | None = Field(None, description="変更追跡に使用するモード。`git-diff` は詳細な差分を提供し、`json` は抽出された JSON データを比較します。")
    schema_: dict[str, Any] | None = Field(None, validation_alias="schema", serialization_alias="schema", description="'json' モード使用時の JSON 抽出用スキーマです。抽出および比較するデータの構造を定義します。[JSON Schema](https://json-schema.org/) に準拠している必要があります。")
    prompt: str | None = Field(None, description="「json」モードで変更追跡を行う際に使用するプロンプトです。指定しない場合は、デフォルトのプロンプトが使用されます。")
    tag: str | None = Field(None, description="変更トラッキングに使用するタグ。タグを使うことで、変更トラッキングの履歴を別々の「ブランチ」に分割でき、特定のタグでの変更トラッキングは同じタグで実行されたスクレイプとだけ比較されます。指定しない場合は、デフォルトタグ（null）が使用されます。")

class ScrapeAndExtractFromUrlBodyJsonOptions(PermissiveModel):
    """JSON オプションオブジェクト"""
    schema_: dict[str, Any] | None = Field(None, validation_alias="schema", serialization_alias="schema", description="抽出に使用するスキーマ（任意）。[JSON Schema](https://json-schema.org/) に準拠したものである必要があります。")
    system_prompt: str | None = Field(None, validation_alias="systemPrompt", serialization_alias="systemPrompt", description="抽出に使用するシステムプロンプト（任意）")
    prompt: str | None = Field(None, description="スキーマなしで抽出を行う際に使用するプロンプト（任意）")

class ScrapeAndExtractFromUrlBodyLocation(PermissiveModel):
    """リクエストに対するロケーション設定です。指定されている場合、利用可能であれば適切なプロキシを使用し、対応する言語およびタイムゾーン設定を再現します。指定されていない場合は、デフォルトで 'US' が使用されます。"""
    country: str | None = Field('US', description="ISO 3166-1 alpha-2国コード（例：「US」「AU」「DE」「JP」）", pattern="^[A-Z]{2}$")
    languages: list[str] | None = Field(None, description="リクエストに対して優先順位順に指定する言語およびロケール。指定がない場合は、指定された location の言語がデフォルトになります。詳細は https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language を参照してください。")

class ScrapeAndExtractFromUrlBody(PermissiveModel):
    url: str = Field(..., description="スクレイプ対象のURL", json_schema_extra={'format': 'uri'})
    only_main_content: bool | None = Field(True, validation_alias="onlyMainContent", serialization_alias="onlyMainContent", description="ヘッダー、ナビゲーション、フッターなどを除き、ページのメインコンテンツのみを返します。")
    include_tags: list[str] | None = Field(None, validation_alias="includeTags", serialization_alias="includeTags", description="出力に含めるタグ。")
    exclude_tags: list[str] | None = Field(None, validation_alias="excludeTags", serialization_alias="excludeTags", description="出力結果から除外するタグ。")
    max_age: int | None = Field(0, validation_alias="maxAge", serialization_alias="maxAge", description="ページのキャッシュが、このミリ秒数以内に生成されたものであれば、そのキャッシュされたバージョンを返します。キャッシュされたページがこの値より古い場合は、ページをスクレイピングします。極めて最新のデータが不要な場合、これを有効にすることでスクレイピングを最大 500% 高速化できます。デフォルトは 0 で、この場合キャッシュは無効になります。")
    headers: dict[str, Any] | None = Field(None, description="リクエストに付与して送信するヘッダー。Cookie や User-Agent などを送るために使用できます。")
    wait_for: int | None = Field(0, validation_alias="waitFor", serialization_alias="waitFor", description="コンテンツを取得する前に待機する時間（ディレイ）をミリ秒単位で指定します。これにより、ページが十分に読み込まれるまでの時間を確保できます。")
    mobile: bool | None = Field(False, description="モバイル端末からのスクレイピングを模擬したい場合は true に設定してください。レスポンシブページのテストやモバイル画面のスクリーンショット取得に便利です。")
    skip_tls_verification: bool | None = Field(False, validation_alias="skipTlsVerification", serialization_alias="skipTlsVerification", description="リクエスト時に TLS 証明書の検証をスキップする")
    timeout: int | None = Field(30000, description="リクエストのタイムアウト（ミリ秒）")
    parse_pdf: bool | None = Field(True, validation_alias="parsePDF", serialization_alias="parsePDF", description="スクレイピング中のPDFファイルの処理方法を制御します。true の場合、PDFのコンテンツを抽出してMarkdown形式に変換し、課金はページ数に基づきます（1ページあたり1クレジット）。false の場合、PDFファイルはbase64エンコードされたデータとして返され、合計1クレジットの定額課金となります。")
    json_options: ScrapeAndExtractFromUrlBodyJsonOptions | None = Field(None, validation_alias="jsonOptions", serialization_alias="jsonOptions", description="JSON オプションオブジェクト")
    actions: list[ScrapeAndExtractFromUrlBodyActionsItemV0 | ScrapeAndExtractFromUrlBodyActionsItemV1 | ScrapeAndExtractFromUrlBodyActionsItemV2 | ScrapeAndExtractFromUrlBodyActionsItemV3 | ScrapeAndExtractFromUrlBodyActionsItemV4 | ScrapeAndExtractFromUrlBodyActionsItemV5 | ScrapeAndExtractFromUrlBodyActionsItemV6 | ScrapeAndExtractFromUrlBodyActionsItemV7 | ScrapeAndExtractFromUrlBodyActionsItemV8] | None = Field(None, description="ページからコンテンツを取得する前に実行するアクション")
    location: ScrapeAndExtractFromUrlBodyLocation | None = Field(None, description="リクエストに対するロケーション設定です。指定されている場合、利用可能であれば適切なプロキシを使用し、対応する言語およびタイムゾーン設定を再現します。指定されていない場合は、デフォルトで 'US' が使用されます。")
    remove_base64_images: bool | None = Field(True, validation_alias="removeBase64Images", serialization_alias="removeBase64Images", description="出力から、非常に長くなりがちな Base64 画像をすべて削除します。画像の alt テキストは出力内に残りますが、URL はプレースホルダーに置き換えられます。")
    block_ads: bool | None = Field(True, validation_alias="blockAds", serialization_alias="blockAds", description="広告とクッキーポップアップのブロックを有効にします。")
    proxy: Literal["basic", "enhanced", "auto"] | None = Field(None, description="使用するプロキシの種類を指定します。\n\n - **basic**: ボット対策がない、または基本的なボット対策のみが導入されているサイト向けのプロキシです。高速で、ほとんどの場合はこれで十分です。\n - **enhanced**: 高度なボット対策が導入されているサイト向けの強化プロキシです。速度は遅くなりますが、特定のサイトではより信頼性があります。1 リクエストあたり最大 5 クレジット消費します。\n - **auto**: basic プロキシでのスクレイピングが失敗した場合に、Firecrawl が自動的に enhanced プロキシで再試行します。enhanced での再試行が成功した場合、そのスクレイピングには 5 クレジットが請求されます。最初の basic での試行が成功した場合は、通常どおりのコストのみが請求されます。\n\nプロキシを指定しない場合、Firecrawl はデフォルトで basic を使用します。")
    store_in_cache: bool | None = Field(True, validation_alias="storeInCache", serialization_alias="storeInCache", description="true の場合、そのページは Firecrawl のインデックスおよびキャッシュに保存されます。スクレイピング内容がデータ保護上の懸念を伴う可能性がある場合は、これを false に設定するのが有効です。機密性の高いスクレイピングに関連する一部のパラメータ（アクションやヘッダーなど）を使用すると、このパラメータは強制的に false に設定されます。")
    formats: list[Literal["markdown", "html", "rawHtml", "links", "screenshot", "screenshot@fullPage", "json", "changeTracking"]] | None = Field(None, description="出力に含めるフォーマット。")
    change_tracking_options: ScrapeAndExtractFromUrlBodyChangeTrackingOptions | None = Field(None, validation_alias="changeTrackingOptions", serialization_alias="changeTrackingOptions", description="変更追跡用のオプション（ベータ版）。changeTracking がフォーマットに含まれている場合にのみ有効です。変更追跡を使用する際は、markdown フォーマットも指定する必要があります。")
    zero_data_retention: bool | None = Field(False, validation_alias="zeroDataRetention", serialization_alias="zeroDataRetention", description="true の場合、このスクレイプではデータを一切保持しないゼロデータ保持モードが有効になります。この機能を有効にするには、help@firecrawl.dev までご連絡ください。")

class ScrapeAndExtractFromUrlsBodyActionsItemV0(PermissiveModel):
    type_: Literal["wait"] = Field(..., validation_alias="type", serialization_alias="type", description="指定したミリ秒間待機します")
    milliseconds: int | None = Field(None, description="待機する時間（ミリ秒）", ge=1)
    selector: str | None = Field(None, description="要素を検索するためのクエリセレクタ")

class ScrapeAndExtractFromUrlsBodyActionsItemV1(PermissiveModel):
    type_: Literal["screenshot"] = Field(..., validation_alias="type", serialization_alias="type", description="スクリーンショットを撮影します。リンクはレスポンスの `actions.screenshots` 配列に含まれます。")
    full_page: bool | None = Field(False, validation_alias="fullPage", serialization_alias="fullPage", description="ページ全体のスクリーンショットを取得するか、現在のビューポートに限定するかを指定します。")
    quality: int | None = Field(None, description="スクリーンショットの品質を1〜100で指定します。100が最高品質です。")

class ScrapeAndExtractFromUrlsBodyActionsItemV2(PermissiveModel):
    type_: Literal["click"] = Field(..., validation_alias="type", serialization_alias="type", description="要素をクリックします")
    selector: str = Field(..., description="要素を検索するためのクエリセレクタ")
    all_: bool | None = Field(False, validation_alias="all", serialization_alias="all", description="セレクターに一致する要素を、最初のものだけでなくすべてクリックします。セレクターに一致する要素が存在しない場合でも、エラーは発生しません。")

class ScrapeAndExtractFromUrlsBodyActionsItemV3(PermissiveModel):
    type_: Literal["write"] = Field(..., validation_alias="type", serialization_alias="type", description="入力フィールド、テキストエリア、または contenteditable 要素にテキストを入力します。注意: テキストを入力する前に、必ず「click」アクションで要素にフォーカスを当ててください。テキストはキーボード入力をシミュレートするため、1文字ずつタイプされます。")
    text: str = Field(..., description="入力するテキスト")

class ScrapeAndExtractFromUrlsBodyActionsItemV4(PermissiveModel):
    """ページ上でキーを押してください。キーコードについては https://asawicki.info/nosense/doc/devices/keyboard/key_codes.html を参照してください。"""
    type_: Literal["press"] = Field(..., validation_alias="type", serialization_alias="type", description="このページでいずれかのキーを押してください")
    key: str = Field(..., description="押下するキー")

class ScrapeAndExtractFromUrlsBodyActionsItemV5(PermissiveModel):
    type_: Literal["scroll"] = Field(..., validation_alias="type", serialization_alias="type", description="ページ全体または特定の要素をスクロールする")
    direction: Literal["up", "down"] | None = Field('down', description="スクロール方向")
    selector: str | None = Field(None, description="スクロール対象要素のクエリセレクター")

class ScrapeAndExtractFromUrlsBodyActionsItemV6(PermissiveModel):
    type_: Literal["scrape"] = Field(..., validation_alias="type", serialization_alias="type", description="現在のページの内容をスクレイピングし、URL と HTML を返します。")

class ScrapeAndExtractFromUrlsBodyActionsItemV7(PermissiveModel):
    type_: Literal["executeJavascript"] = Field(..., validation_alias="type", serialization_alias="type", description="ページ上で JavaScript コードを実行する")
    script: str = Field(..., description="実行する JavaScript コード")

class ScrapeAndExtractFromUrlsBodyActionsItemV8(PermissiveModel):
    type_: Literal["pdf"] = Field(..., validation_alias="type", serialization_alias="type", description="現在のページの PDF を生成します。PDF はレスポンスの `actions.pdfs` 配列で返されます。")
    format_: Literal["A0", "A1", "A2", "A3", "A4", "A5", "A6", "Letter", "Legal", "Tabloid", "Ledger"] | None = Field('Letter', validation_alias="format", serialization_alias="format", description="出力されるPDFのページサイズ")
    landscape: bool | None = Field(False, description="PDF を横向きで生成するかどうか")
    scale: float | None = Field(1, description="生成される PDF の拡大縮小倍率")

class ScrapeAndExtractFromUrlsBodyChangeTrackingOptions(PermissiveModel):
    """変更追跡用のオプション（ベータ版）。changeTracking がフォーマットに含まれている場合にのみ有効です。変更追跡を使用する際は、markdown フォーマットも指定する必要があります。"""
    modes: list[Literal["git-diff", "json"]] | None = Field(None, description="変更追跡に使用するモード。`git-diff` は詳細な差分を提供し、`json` は抽出された JSON データを比較します。")
    schema_: dict[str, Any] | None = Field(None, validation_alias="schema", serialization_alias="schema", description="'json' モード使用時の JSON 抽出用スキーマです。抽出および比較するデータの構造を定義します。[JSON Schema](https://json-schema.org/) に準拠している必要があります。")
    prompt: str | None = Field(None, description="「json」モードで変更追跡を行う際に使用するプロンプトです。指定しない場合は、デフォルトのプロンプトが使用されます。")
    tag: str | None = Field(None, description="変更トラッキングに使用するタグ。タグを使うことで、変更トラッキングの履歴を別々の「ブランチ」に分割でき、特定のタグでの変更トラッキングは同じタグで実行されたスクレイプとだけ比較されます。指定しない場合は、デフォルトタグ（null）が使用されます。")

class ScrapeAndExtractFromUrlsBodyJsonOptions(PermissiveModel):
    """JSON オプションオブジェクト"""
    schema_: dict[str, Any] | None = Field(None, validation_alias="schema", serialization_alias="schema", description="抽出に使用するスキーマ（任意）。[JSON Schema](https://json-schema.org/) に準拠したものである必要があります。")
    system_prompt: str | None = Field(None, validation_alias="systemPrompt", serialization_alias="systemPrompt", description="抽出に使用するシステムプロンプト（任意）")
    prompt: str | None = Field(None, description="スキーマなしで抽出を行う際に使用するプロンプト（任意）")

class ScrapeAndExtractFromUrlsBodyLocation(PermissiveModel):
    """リクエストに対するロケーション設定です。指定されている場合、利用可能であれば適切なプロキシを使用し、対応する言語およびタイムゾーン設定を再現します。指定されていない場合は、デフォルトで 'US' が使用されます。"""
    country: str | None = Field('US', description="ISO 3166-1 alpha-2国コード（例：「US」「AU」「DE」「JP」）", pattern="^[A-Z]{2}$")
    languages: list[str] | None = Field(None, description="リクエストに対して優先順位順に指定する言語およびロケール。指定がない場合は、指定された location の言語がデフォルトになります。詳細は https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language を参照してください。")

class ScrapeAndExtractFromUrlsBodyWebhook(PermissiveModel):
    """Webhook の仕様を表すオブジェクト。"""
    url: str = Field(..., description="Webhook の送信先 URL です。バッチスクレイプの開始時（batch_scrape.started）、各ページのスクレイプ時（batch_scrape.page）、およびバッチスクレイプが完了したとき（batch_scrape.completed または batch_scrape.failed）にトリガーされます。レスポンスは `/scrape` エンドポイントと同じです。")
    headers: dict[str, str] | None = Field(None, description="Webhook URL に送信する HTTP ヘッダー。")
    metadata: dict[str, Any] | None = Field(None, description="このクロールのすべてのWebhookペイロードに含まれるカスタムメタデータ")
    events: list[Literal["completed", "page", "failed", "started"]] | None = Field(None, description="Webhook URL に送信するイベントの種類。（デフォルト: すべて）")

class ScrapeAndExtractFromUrlsBody(PermissiveModel):
    urls: list[str]
    webhook: ScrapeAndExtractFromUrlsBodyWebhook | None = Field(None, description="Webhook の仕様を表すオブジェクト。")
    max_concurrency: int | None = Field(None, validation_alias="maxConcurrency", serialization_alias="maxConcurrency", description="同時スクレイプの最大数。このパラメータで、このバッチスクレイプにおける同時実行数の上限を設定できます。指定しない場合は、チームの同時実行数の上限が適用されます。")
    ignore_invalid_ur_ls: bool | None = Field(False, validation_alias="ignoreInvalidURLs", serialization_alias="ignoreInvalidURLs", description="urls 配列に無効な URL が含まれている場合、それらは無視されます。無効な URL が原因でリクエスト全体が失敗するのではなく、残りの有効な URL のみを使ってバッチスクレイプが実行され、無効な URL はレスポンスの invalidURLs フィールドで返されます。")
    only_main_content: bool | None = Field(True, validation_alias="onlyMainContent", serialization_alias="onlyMainContent", description="ヘッダー、ナビゲーション、フッターなどを除き、ページのメインコンテンツのみを返します。")
    include_tags: list[str] | None = Field(None, validation_alias="includeTags", serialization_alias="includeTags", description="出力に含めるタグ。")
    exclude_tags: list[str] | None = Field(None, validation_alias="excludeTags", serialization_alias="excludeTags", description="出力結果から除外するタグ。")
    max_age: int | None = Field(0, validation_alias="maxAge", serialization_alias="maxAge", description="ページのキャッシュが、このミリ秒数以内に生成されたものであれば、そのキャッシュされたバージョンを返します。キャッシュされたページがこの値より古い場合は、ページをスクレイピングします。極めて最新のデータが不要な場合、これを有効にすることでスクレイピングを最大 500% 高速化できます。デフォルトは 0 で、この場合キャッシュは無効になります。")
    headers: dict[str, Any] | None = Field(None, description="リクエストに付与して送信するヘッダー。Cookie や User-Agent などを送るために使用できます。")
    wait_for: int | None = Field(0, validation_alias="waitFor", serialization_alias="waitFor", description="コンテンツを取得する前に待機する時間（ディレイ）をミリ秒単位で指定します。これにより、ページが十分に読み込まれるまでの時間を確保できます。")
    mobile: bool | None = Field(False, description="モバイル端末からのスクレイピングを模擬したい場合は true に設定してください。レスポンシブページのテストやモバイル画面のスクリーンショット取得に便利です。")
    skip_tls_verification: bool | None = Field(False, validation_alias="skipTlsVerification", serialization_alias="skipTlsVerification", description="リクエスト時に TLS 証明書の検証をスキップする")
    timeout: int | None = Field(30000, description="リクエストのタイムアウト（ミリ秒）")
    parse_pdf: bool | None = Field(True, validation_alias="parsePDF", serialization_alias="parsePDF", description="スクレイピング中のPDFファイルの処理方法を制御します。true の場合、PDFのコンテンツを抽出してMarkdown形式に変換し、課金はページ数に基づきます（1ページあたり1クレジット）。false の場合、PDFファイルはbase64エンコードされたデータとして返され、合計1クレジットの定額課金となります。")
    json_options: ScrapeAndExtractFromUrlsBodyJsonOptions | None = Field(None, validation_alias="jsonOptions", serialization_alias="jsonOptions", description="JSON オプションオブジェクト")
    actions: list[ScrapeAndExtractFromUrlsBodyActionsItemV0 | ScrapeAndExtractFromUrlsBodyActionsItemV1 | ScrapeAndExtractFromUrlsBodyActionsItemV2 | ScrapeAndExtractFromUrlsBodyActionsItemV3 | ScrapeAndExtractFromUrlsBodyActionsItemV4 | ScrapeAndExtractFromUrlsBodyActionsItemV5 | ScrapeAndExtractFromUrlsBodyActionsItemV6 | ScrapeAndExtractFromUrlsBodyActionsItemV7 | ScrapeAndExtractFromUrlsBodyActionsItemV8] | None = Field(None, description="ページからコンテンツを取得する前に実行するアクション")
    location: ScrapeAndExtractFromUrlsBodyLocation | None = Field(None, description="リクエストに対するロケーション設定です。指定されている場合、利用可能であれば適切なプロキシを使用し、対応する言語およびタイムゾーン設定を再現します。指定されていない場合は、デフォルトで 'US' が使用されます。")
    remove_base64_images: bool | None = Field(True, validation_alias="removeBase64Images", serialization_alias="removeBase64Images", description="出力から、非常に長くなりがちな Base64 画像をすべて削除します。画像の alt テキストは出力内に残りますが、URL はプレースホルダーに置き換えられます。")
    block_ads: bool | None = Field(True, validation_alias="blockAds", serialization_alias="blockAds", description="広告とクッキーポップアップのブロックを有効にします。")
    proxy: Literal["basic", "enhanced", "auto"] | None = Field(None, description="使用するプロキシの種類を指定します。\n\n - **basic**: ボット対策がない、または基本的なボット対策のみが導入されているサイト向けのプロキシです。高速で、ほとんどの場合はこれで十分です。\n - **enhanced**: 高度なボット対策が導入されているサイト向けの強化プロキシです。速度は遅くなりますが、特定のサイトではより信頼性があります。1 リクエストあたり最大 5 クレジット消費します。\n - **auto**: basic プロキシでのスクレイピングが失敗した場合に、Firecrawl が自動的に enhanced プロキシで再試行します。enhanced での再試行が成功した場合、そのスクレイピングには 5 クレジットが請求されます。最初の basic での試行が成功した場合は、通常どおりのコストのみが請求されます。\n\nプロキシを指定しない場合、Firecrawl はデフォルトで basic を使用します。")
    store_in_cache: bool | None = Field(True, validation_alias="storeInCache", serialization_alias="storeInCache", description="true の場合、そのページは Firecrawl のインデックスおよびキャッシュに保存されます。スクレイピング内容がデータ保護上の懸念を伴う可能性がある場合は、これを false に設定するのが有効です。機密性の高いスクレイピングに関連する一部のパラメータ（アクションやヘッダーなど）を使用すると、このパラメータは強制的に false に設定されます。")
    formats: list[Literal["markdown", "html", "rawHtml", "links", "screenshot", "screenshot@fullPage", "json", "changeTracking"]] | None = Field(None, description="出力に含めるフォーマット。")
    change_tracking_options: ScrapeAndExtractFromUrlsBodyChangeTrackingOptions | None = Field(None, validation_alias="changeTrackingOptions", serialization_alias="changeTrackingOptions", description="変更追跡用のオプション（ベータ版）。changeTracking がフォーマットに含まれている場合にのみ有効です。変更追跡を使用する際は、markdown フォーマットも指定する必要があります。")
    zero_data_retention: bool | None = Field(False, validation_alias="zeroDataRetention", serialization_alias="zeroDataRetention", description="true の場合、このバッチスクレイプではデータを一切保持しないゼロデータ保持モードが有効になります。この機能を有効にするには、help@firecrawl.dev までご連絡ください。")

class ScrapeOptionsActionsItemV0(PermissiveModel):
    type_: Literal["wait"] = Field(..., validation_alias="type", serialization_alias="type", description="指定したミリ秒間待機します")
    milliseconds: int | None = Field(None, description="待機する時間（ミリ秒）", ge=1)
    selector: str | None = Field(None, description="要素を検索するためのクエリセレクタ")

class ScrapeOptionsActionsItemV1(PermissiveModel):
    type_: Literal["screenshot"] = Field(..., validation_alias="type", serialization_alias="type", description="スクリーンショットを撮影します。リンクはレスポンスの `actions.screenshots` 配列に含まれます。")
    full_page: bool | None = Field(False, validation_alias="fullPage", serialization_alias="fullPage", description="ページ全体のスクリーンショットを取得するか、現在のビューポートに限定するかを指定します。")
    quality: int | None = Field(None, description="スクリーンショットの品質を1〜100で指定します。100が最高品質です。")

class ScrapeOptionsActionsItemV2(PermissiveModel):
    type_: Literal["click"] = Field(..., validation_alias="type", serialization_alias="type", description="要素をクリックします")
    selector: str = Field(..., description="要素を検索するためのクエリセレクタ")
    all_: bool | None = Field(False, validation_alias="all", serialization_alias="all", description="セレクターに一致する要素を、最初のものだけでなくすべてクリックします。セレクターに一致する要素が存在しない場合でも、エラーは発生しません。")

class ScrapeOptionsActionsItemV3(PermissiveModel):
    type_: Literal["write"] = Field(..., validation_alias="type", serialization_alias="type", description="入力フィールド、テキストエリア、または contenteditable 要素にテキストを入力します。注意: テキストを入力する前に、必ず「click」アクションで要素にフォーカスを当ててください。テキストはキーボード入力をシミュレートするため、1文字ずつタイプされます。")
    text: str = Field(..., description="入力するテキスト")

class ScrapeOptionsActionsItemV4(PermissiveModel):
    """ページ上でキーを押してください。キーコードについては https://asawicki.info/nosense/doc/devices/keyboard/key_codes.html を参照してください。"""
    type_: Literal["press"] = Field(..., validation_alias="type", serialization_alias="type", description="このページでいずれかのキーを押してください")
    key: str = Field(..., description="押下するキー")

class ScrapeOptionsActionsItemV5(PermissiveModel):
    type_: Literal["scroll"] = Field(..., validation_alias="type", serialization_alias="type", description="ページ全体または特定の要素をスクロールする")
    direction: Literal["up", "down"] | None = Field('down', description="スクロール方向")
    selector: str | None = Field(None, description="スクロール対象要素のクエリセレクター")

class ScrapeOptionsActionsItemV6(PermissiveModel):
    type_: Literal["scrape"] = Field(..., validation_alias="type", serialization_alias="type", description="現在のページの内容をスクレイピングし、URL と HTML を返します。")

class ScrapeOptionsActionsItemV7(PermissiveModel):
    type_: Literal["executeJavascript"] = Field(..., validation_alias="type", serialization_alias="type", description="ページ上で JavaScript コードを実行する")
    script: str = Field(..., description="実行する JavaScript コード")

class ScrapeOptionsActionsItemV8(PermissiveModel):
    type_: Literal["pdf"] = Field(..., validation_alias="type", serialization_alias="type", description="現在のページの PDF を生成します。PDF はレスポンスの `actions.pdfs` 配列で返されます。")
    format_: Literal["A0", "A1", "A2", "A3", "A4", "A5", "A6", "Letter", "Legal", "Tabloid", "Ledger"] | None = Field('Letter', validation_alias="format", serialization_alias="format", description="出力されるPDFのページサイズ")
    landscape: bool | None = Field(False, description="PDF を横向きで生成するかどうか")
    scale: float | None = Field(1, description="生成される PDF の拡大縮小倍率")

class ScrapeOptionsChangeTrackingOptions(PermissiveModel):
    """変更追跡用のオプション（ベータ版）。changeTracking がフォーマットに含まれている場合にのみ有効です。変更追跡を使用する際は、markdown フォーマットも指定する必要があります。"""
    modes: list[Literal["git-diff", "json"]] | None = Field(None, description="変更追跡に使用するモード。`git-diff` は詳細な差分を提供し、`json` は抽出された JSON データを比較します。")
    schema_: dict[str, Any] | None = Field(None, validation_alias="schema", serialization_alias="schema", description="'json' モード使用時の JSON 抽出用スキーマです。抽出および比較するデータの構造を定義します。[JSON Schema](https://json-schema.org/) に準拠している必要があります。")
    prompt: str | None = Field(None, description="「json」モードで変更追跡を行う際に使用するプロンプトです。指定しない場合は、デフォルトのプロンプトが使用されます。")
    tag: str | None = Field(None, description="変更トラッキングに使用するタグ。タグを使うことで、変更トラッキングの履歴を別々の「ブランチ」に分割でき、特定のタグでの変更トラッキングは同じタグで実行されたスクレイプとだけ比較されます。指定しない場合は、デフォルトタグ（null）が使用されます。")

class ScrapeOptionsJsonOptions(PermissiveModel):
    """JSON オプションオブジェクト"""
    schema_: dict[str, Any] | None = Field(None, validation_alias="schema", serialization_alias="schema", description="抽出に使用するスキーマ（任意）。[JSON Schema](https://json-schema.org/) に準拠したものである必要があります。")
    system_prompt: str | None = Field(None, validation_alias="systemPrompt", serialization_alias="systemPrompt", description="抽出に使用するシステムプロンプト（任意）")
    prompt: str | None = Field(None, description="スキーマなしで抽出を行う際に使用するプロンプト（任意）")

class ScrapeOptionsLocation(PermissiveModel):
    """リクエストに対するロケーション設定です。指定されている場合、利用可能であれば適切なプロキシを使用し、対応する言語およびタイムゾーン設定を再現します。指定されていない場合は、デフォルトで 'US' が使用されます。"""
    country: str | None = Field('US', description="ISO 3166-1 alpha-2国コード（例：「US」「AU」「DE」「JP」）", pattern="^[A-Z]{2}$")
    languages: list[str] | None = Field(None, description="リクエストに対して優先順位順に指定する言語およびロケール。指定がない場合は、指定された location の言語がデフォルトになります。詳細は https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language を参照してください。")

class ScrapeOptions(PermissiveModel):
    only_main_content: bool | None = Field(True, validation_alias="onlyMainContent", serialization_alias="onlyMainContent", description="ヘッダー、ナビゲーション、フッターなどを除き、ページのメインコンテンツのみを返します。")
    include_tags: list[str] | None = Field(None, validation_alias="includeTags", serialization_alias="includeTags", description="出力に含めるタグ。")
    exclude_tags: list[str] | None = Field(None, validation_alias="excludeTags", serialization_alias="excludeTags", description="出力結果から除外するタグ。")
    max_age: int | None = Field(0, validation_alias="maxAge", serialization_alias="maxAge", description="ページのキャッシュが、このミリ秒数以内に生成されたものであれば、そのキャッシュされたバージョンを返します。キャッシュされたページがこの値より古い場合は、ページをスクレイピングします。極めて最新のデータが不要な場合、これを有効にすることでスクレイピングを最大 500% 高速化できます。デフォルトは 0 で、この場合キャッシュは無効になります。")
    headers: dict[str, Any] | None = Field(None, description="リクエストに付与して送信するヘッダー。Cookie や User-Agent などを送るために使用できます。")
    wait_for: int | None = Field(0, validation_alias="waitFor", serialization_alias="waitFor", description="コンテンツを取得する前に待機する時間（ディレイ）をミリ秒単位で指定します。これにより、ページが十分に読み込まれるまでの時間を確保できます。")
    mobile: bool | None = Field(False, description="モバイル端末からのスクレイピングを模擬したい場合は true に設定してください。レスポンシブページのテストやモバイル画面のスクリーンショット取得に便利です。")
    skip_tls_verification: bool | None = Field(False, validation_alias="skipTlsVerification", serialization_alias="skipTlsVerification", description="リクエスト時に TLS 証明書の検証をスキップする")
    timeout: int | None = Field(30000, description="リクエストのタイムアウト（ミリ秒）")
    parse_pdf: bool | None = Field(True, validation_alias="parsePDF", serialization_alias="parsePDF", description="スクレイピング中のPDFファイルの処理方法を制御します。true の場合、PDFのコンテンツを抽出してMarkdown形式に変換し、課金はページ数に基づきます（1ページあたり1クレジット）。false の場合、PDFファイルはbase64エンコードされたデータとして返され、合計1クレジットの定額課金となります。")
    json_options: ScrapeOptionsJsonOptions | None = Field(None, validation_alias="jsonOptions", serialization_alias="jsonOptions", description="JSON オプションオブジェクト")
    actions: list[ScrapeOptionsActionsItemV0 | ScrapeOptionsActionsItemV1 | ScrapeOptionsActionsItemV2 | ScrapeOptionsActionsItemV3 | ScrapeOptionsActionsItemV4 | ScrapeOptionsActionsItemV5 | ScrapeOptionsActionsItemV6 | ScrapeOptionsActionsItemV7 | ScrapeOptionsActionsItemV8] | None = Field(None, description="ページからコンテンツを取得する前に実行するアクション")
    location: ScrapeOptionsLocation | None = Field(None, description="リクエストに対するロケーション設定です。指定されている場合、利用可能であれば適切なプロキシを使用し、対応する言語およびタイムゾーン設定を再現します。指定されていない場合は、デフォルトで 'US' が使用されます。")
    remove_base64_images: bool | None = Field(True, validation_alias="removeBase64Images", serialization_alias="removeBase64Images", description="出力から、非常に長くなりがちな Base64 画像をすべて削除します。画像の alt テキストは出力内に残りますが、URL はプレースホルダーに置き換えられます。")
    block_ads: bool | None = Field(True, validation_alias="blockAds", serialization_alias="blockAds", description="広告とクッキーポップアップのブロックを有効にします。")
    proxy: Literal["basic", "enhanced", "auto"] | None = Field(None, description="使用するプロキシの種類を指定します。\n\n - **basic**: ボット対策がない、または基本的なボット対策のみが導入されているサイト向けのプロキシです。高速で、ほとんどの場合はこれで十分です。\n - **enhanced**: 高度なボット対策が導入されているサイト向けの強化プロキシです。速度は遅くなりますが、特定のサイトではより信頼性があります。1 リクエストあたり最大 5 クレジット消費します。\n - **auto**: basic プロキシでのスクレイピングが失敗した場合に、Firecrawl が自動的に enhanced プロキシで再試行します。enhanced での再試行が成功した場合、そのスクレイピングには 5 クレジットが請求されます。最初の basic での試行が成功した場合は、通常どおりのコストのみが請求されます。\n\nプロキシを指定しない場合、Firecrawl はデフォルトで basic を使用します。")
    store_in_cache: bool | None = Field(True, validation_alias="storeInCache", serialization_alias="storeInCache", description="true の場合、そのページは Firecrawl のインデックスおよびキャッシュに保存されます。スクレイピング内容がデータ保護上の懸念を伴う可能性がある場合は、これを false に設定するのが有効です。機密性の高いスクレイピングに関連する一部のパラメータ（アクションやヘッダーなど）を使用すると、このパラメータは強制的に false に設定されます。")
    formats: list[Literal["markdown", "html", "rawHtml", "links", "screenshot", "screenshot@fullPage", "json", "changeTracking"]] | None = Field(None, description="出力に含めるフォーマット。")
    change_tracking_options: ScrapeOptionsChangeTrackingOptions | None = Field(None, validation_alias="changeTrackingOptions", serialization_alias="changeTrackingOptions", description="変更追跡用のオプション（ベータ版）。changeTracking がフォーマットに含まれている場合にのみ有効です。変更追跡を使用する際は、markdown フォーマットも指定する必要があります。")

class ScrapeOptionsV1ChangeTrackingOptions(PermissiveModel):
    """変更追跡用のオプション（ベータ版）。changeTracking がフォーマットに含まれている場合にのみ有効です。変更追跡を使用する際は、markdown フォーマットも指定する必要があります。"""
    modes: list[Literal["git-diff", "json"]] | None = Field(None, description="変更追跡に使用するモード。`git-diff` は詳細な差分を提供し、`json` は抽出された JSON データを比較します。")
    schema_: dict[str, Any] | None = Field(None, validation_alias="schema", serialization_alias="schema", description="'json' モード使用時の JSON 抽出用スキーマです。抽出および比較するデータの構造を定義します。[JSON Schema](https://json-schema.org/) に準拠している必要があります。")
    prompt: str | None = Field(None, description="「json」モードで変更追跡を行う際に使用するプロンプトです。指定しない場合は、デフォルトのプロンプトが使用されます。")
    tag: str | None = Field(None, description="変更トラッキングに使用するタグ。タグを使うことで、変更トラッキングの履歴を別々の「ブランチ」に分割でき、特定のタグでの変更トラッキングは同じタグで実行されたスクレイプとだけ比較されます。指定しない場合は、デフォルトタグ（null）が使用されます。")

class SearchAndScrapeBodyScrapeOptionsActionsItemV0(PermissiveModel):
    type_: Literal["wait"] = Field(..., validation_alias="type", serialization_alias="type", description="指定したミリ秒間待機します")
    milliseconds: int | None = Field(None, description="待機する時間（ミリ秒）", ge=1)
    selector: str | None = Field(None, description="要素を検索するためのクエリセレクタ")

class SearchAndScrapeBodyScrapeOptionsActionsItemV1(PermissiveModel):
    type_: Literal["screenshot"] = Field(..., validation_alias="type", serialization_alias="type", description="スクリーンショットを撮影します。リンクはレスポンスの `actions.screenshots` 配列に含まれます。")
    full_page: bool | None = Field(False, validation_alias="fullPage", serialization_alias="fullPage", description="ページ全体のスクリーンショットを取得するか、現在のビューポートに限定するかを指定します。")
    quality: int | None = Field(None, description="スクリーンショットの品質を1〜100で指定します。100が最高品質です。")

class SearchAndScrapeBodyScrapeOptionsActionsItemV2(PermissiveModel):
    type_: Literal["click"] = Field(..., validation_alias="type", serialization_alias="type", description="要素をクリックします")
    selector: str = Field(..., description="要素を検索するためのクエリセレクタ")
    all_: bool | None = Field(False, validation_alias="all", serialization_alias="all", description="セレクターに一致する要素を、最初のものだけでなくすべてクリックします。セレクターに一致する要素が存在しない場合でも、エラーは発生しません。")

class SearchAndScrapeBodyScrapeOptionsActionsItemV3(PermissiveModel):
    type_: Literal["write"] = Field(..., validation_alias="type", serialization_alias="type", description="入力フィールド、テキストエリア、または contenteditable 要素にテキストを入力します。注意: テキストを入力する前に、必ず「click」アクションで要素にフォーカスを当ててください。テキストはキーボード入力をシミュレートするため、1文字ずつタイプされます。")
    text: str = Field(..., description="入力するテキスト")

class SearchAndScrapeBodyScrapeOptionsActionsItemV4(PermissiveModel):
    """ページ上でキーを押してください。キーコードについては https://asawicki.info/nosense/doc/devices/keyboard/key_codes.html を参照してください。"""
    type_: Literal["press"] = Field(..., validation_alias="type", serialization_alias="type", description="このページでいずれかのキーを押してください")
    key: str = Field(..., description="押下するキー")

class SearchAndScrapeBodyScrapeOptionsActionsItemV5(PermissiveModel):
    type_: Literal["scroll"] = Field(..., validation_alias="type", serialization_alias="type", description="ページ全体または特定の要素をスクロールする")
    direction: Literal["up", "down"] | None = Field('down', description="スクロール方向")
    selector: str | None = Field(None, description="スクロール対象要素のクエリセレクター")

class SearchAndScrapeBodyScrapeOptionsActionsItemV6(PermissiveModel):
    type_: Literal["scrape"] = Field(..., validation_alias="type", serialization_alias="type", description="現在のページの内容をスクレイピングし、URL と HTML を返します。")

class SearchAndScrapeBodyScrapeOptionsActionsItemV7(PermissiveModel):
    type_: Literal["executeJavascript"] = Field(..., validation_alias="type", serialization_alias="type", description="ページ上で JavaScript コードを実行する")
    script: str = Field(..., description="実行する JavaScript コード")

class SearchAndScrapeBodyScrapeOptionsActionsItemV8(PermissiveModel):
    type_: Literal["pdf"] = Field(..., validation_alias="type", serialization_alias="type", description="現在のページの PDF を生成します。PDF はレスポンスの `actions.pdfs` 配列で返されます。")
    format_: Literal["A0", "A1", "A2", "A3", "A4", "A5", "A6", "Letter", "Legal", "Tabloid", "Ledger"] | None = Field('Letter', validation_alias="format", serialization_alias="format", description="出力されるPDFのページサイズ")
    landscape: bool | None = Field(False, description="PDF を横向きで生成するかどうか")
    scale: float | None = Field(1, description="生成される PDF の拡大縮小倍率")

class SearchAndScrapeBodyScrapeOptionsJsonOptions(PermissiveModel):
    """JSON オプションオブジェクト"""
    schema_: dict[str, Any] | None = Field(None, validation_alias="schema", serialization_alias="schema", description="抽出に使用するスキーマ（任意）。[JSON Schema](https://json-schema.org/) に準拠したものである必要があります。")
    system_prompt: str | None = Field(None, validation_alias="systemPrompt", serialization_alias="systemPrompt", description="抽出に使用するシステムプロンプト（任意）")
    prompt: str | None = Field(None, description="スキーマなしで抽出を行う際に使用するプロンプト（任意）")

class SearchAndScrapeBodyScrapeOptionsLocation(PermissiveModel):
    """リクエストに対するロケーション設定です。指定されている場合、利用可能であれば適切なプロキシを使用し、対応する言語およびタイムゾーン設定を再現します。指定されていない場合は、デフォルトで 'US' が使用されます。"""
    country: str | None = Field('US', description="ISO 3166-1 alpha-2国コード（例：「US」「AU」「DE」「JP」）", pattern="^[A-Z]{2}$")
    languages: list[str] | None = Field(None, description="リクエストに対して優先順位順に指定する言語およびロケール。指定がない場合は、指定された location の言語がデフォルトになります。詳細は https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language を参照してください。")

class SearchAndScrapeBodyScrapeOptions(PermissiveModel):
    """検索結果スクレイピングのオプション"""
    only_main_content: bool | None = Field(True, validation_alias="onlyMainContent", serialization_alias="onlyMainContent", description="ヘッダー、ナビゲーション、フッターなどを除き、ページのメインコンテンツのみを返します。")
    include_tags: list[str] | None = Field(None, validation_alias="includeTags", serialization_alias="includeTags", description="出力に含めるタグ。")
    exclude_tags: list[str] | None = Field(None, validation_alias="excludeTags", serialization_alias="excludeTags", description="出力結果から除外するタグ。")
    max_age: int | None = Field(0, validation_alias="maxAge", serialization_alias="maxAge", description="ページのキャッシュが、このミリ秒数以内に生成されたものであれば、そのキャッシュされたバージョンを返します。キャッシュされたページがこの値より古い場合は、ページをスクレイピングします。極めて最新のデータが不要な場合、これを有効にすることでスクレイピングを最大 500% 高速化できます。デフォルトは 0 で、この場合キャッシュは無効になります。")
    headers: dict[str, Any] | None = Field(None, description="リクエストに付与して送信するヘッダー。Cookie や User-Agent などを送るために使用できます。")
    wait_for: int | None = Field(0, validation_alias="waitFor", serialization_alias="waitFor", description="コンテンツを取得する前に待機する時間（ディレイ）をミリ秒単位で指定します。これにより、ページが十分に読み込まれるまでの時間を確保できます。")
    mobile: bool | None = Field(False, description="モバイル端末からのスクレイピングを模擬したい場合は true に設定してください。レスポンシブページのテストやモバイル画面のスクリーンショット取得に便利です。")
    skip_tls_verification: bool | None = Field(False, validation_alias="skipTlsVerification", serialization_alias="skipTlsVerification", description="リクエスト時に TLS 証明書の検証をスキップする")
    timeout: int | None = Field(30000, description="リクエストのタイムアウト（ミリ秒）")
    parse_pdf: bool | None = Field(True, validation_alias="parsePDF", serialization_alias="parsePDF", description="スクレイピング中のPDFファイルの処理方法を制御します。true の場合、PDFのコンテンツを抽出してMarkdown形式に変換し、課金はページ数に基づきます（1ページあたり1クレジット）。false の場合、PDFファイルはbase64エンコードされたデータとして返され、合計1クレジットの定額課金となります。")
    json_options: SearchAndScrapeBodyScrapeOptionsJsonOptions | None = Field(None, validation_alias="jsonOptions", serialization_alias="jsonOptions", description="JSON オプションオブジェクト")
    actions: list[SearchAndScrapeBodyScrapeOptionsActionsItemV0 | SearchAndScrapeBodyScrapeOptionsActionsItemV1 | SearchAndScrapeBodyScrapeOptionsActionsItemV2 | SearchAndScrapeBodyScrapeOptionsActionsItemV3 | SearchAndScrapeBodyScrapeOptionsActionsItemV4 | SearchAndScrapeBodyScrapeOptionsActionsItemV5 | SearchAndScrapeBodyScrapeOptionsActionsItemV6 | SearchAndScrapeBodyScrapeOptionsActionsItemV7 | SearchAndScrapeBodyScrapeOptionsActionsItemV8] | None = Field(None, description="ページからコンテンツを取得する前に実行するアクション")
    location: SearchAndScrapeBodyScrapeOptionsLocation | None = Field(None, description="リクエストに対するロケーション設定です。指定されている場合、利用可能であれば適切なプロキシを使用し、対応する言語およびタイムゾーン設定を再現します。指定されていない場合は、デフォルトで 'US' が使用されます。")
    remove_base64_images: bool | None = Field(True, validation_alias="removeBase64Images", serialization_alias="removeBase64Images", description="出力から、非常に長くなりがちな Base64 画像をすべて削除します。画像の alt テキストは出力内に残りますが、URL はプレースホルダーに置き換えられます。")
    block_ads: bool | None = Field(True, validation_alias="blockAds", serialization_alias="blockAds", description="広告とクッキーポップアップのブロックを有効にします。")
    proxy: Literal["basic", "enhanced", "auto"] | None = Field(None, description="使用するプロキシの種類を指定します。\n\n - **basic**: ボット対策がない、または基本的なボット対策のみが導入されているサイト向けのプロキシです。高速で、ほとんどの場合はこれで十分です。\n - **enhanced**: 高度なボット対策が導入されているサイト向けの強化プロキシです。速度は遅くなりますが、特定のサイトではより信頼性があります。1 リクエストあたり最大 5 クレジット消費します。\n - **auto**: basic プロキシでのスクレイピングが失敗した場合に、Firecrawl が自動的に enhanced プロキシで再試行します。enhanced での再試行が成功した場合、そのスクレイピングには 5 クレジットが請求されます。最初の basic での試行が成功した場合は、通常どおりのコストのみが請求されます。\n\nプロキシを指定しない場合、Firecrawl はデフォルトで basic を使用します。")
    store_in_cache: bool | None = Field(True, validation_alias="storeInCache", serialization_alias="storeInCache", description="true の場合、そのページは Firecrawl のインデックスおよびキャッシュに保存されます。スクレイピング内容がデータ保護上の懸念を伴う可能性がある場合は、これを false に設定するのが有効です。機密性の高いスクレイピングに関連する一部のパラメータ（アクションやヘッダーなど）を使用すると、このパラメータは強制的に false に設定されます。")
    formats: list[Literal["markdown", "html", "rawHtml", "links", "screenshot", "screenshot@fullPage", "json", "extract"]] | None = None


# Rebuild models to resolve forward references (required for circular refs)
BaseScrapeOptions.model_rebuild()
BaseScrapeOptionsActionsItemV0.model_rebuild()
BaseScrapeOptionsActionsItemV1.model_rebuild()
BaseScrapeOptionsActionsItemV2.model_rebuild()
BaseScrapeOptionsActionsItemV3.model_rebuild()
BaseScrapeOptionsActionsItemV4.model_rebuild()
BaseScrapeOptionsActionsItemV5.model_rebuild()
BaseScrapeOptionsActionsItemV6.model_rebuild()
BaseScrapeOptionsActionsItemV7.model_rebuild()
BaseScrapeOptionsActionsItemV8.model_rebuild()
BaseScrapeOptionsJsonOptions.model_rebuild()
BaseScrapeOptionsLocation.model_rebuild()
ScrapeAndExtractFromUrlBody.model_rebuild()
ScrapeAndExtractFromUrlBodyActionsItemV0.model_rebuild()
ScrapeAndExtractFromUrlBodyActionsItemV1.model_rebuild()
ScrapeAndExtractFromUrlBodyActionsItemV2.model_rebuild()
ScrapeAndExtractFromUrlBodyActionsItemV3.model_rebuild()
ScrapeAndExtractFromUrlBodyActionsItemV4.model_rebuild()
ScrapeAndExtractFromUrlBodyActionsItemV5.model_rebuild()
ScrapeAndExtractFromUrlBodyActionsItemV6.model_rebuild()
ScrapeAndExtractFromUrlBodyActionsItemV7.model_rebuild()
ScrapeAndExtractFromUrlBodyActionsItemV8.model_rebuild()
ScrapeAndExtractFromUrlBodyChangeTrackingOptions.model_rebuild()
ScrapeAndExtractFromUrlBodyJsonOptions.model_rebuild()
ScrapeAndExtractFromUrlBodyLocation.model_rebuild()
ScrapeAndExtractFromUrlsBody.model_rebuild()
ScrapeAndExtractFromUrlsBodyActionsItemV0.model_rebuild()
ScrapeAndExtractFromUrlsBodyActionsItemV1.model_rebuild()
ScrapeAndExtractFromUrlsBodyActionsItemV2.model_rebuild()
ScrapeAndExtractFromUrlsBodyActionsItemV3.model_rebuild()
ScrapeAndExtractFromUrlsBodyActionsItemV4.model_rebuild()
ScrapeAndExtractFromUrlsBodyActionsItemV5.model_rebuild()
ScrapeAndExtractFromUrlsBodyActionsItemV6.model_rebuild()
ScrapeAndExtractFromUrlsBodyActionsItemV7.model_rebuild()
ScrapeAndExtractFromUrlsBodyActionsItemV8.model_rebuild()
ScrapeAndExtractFromUrlsBodyChangeTrackingOptions.model_rebuild()
ScrapeAndExtractFromUrlsBodyJsonOptions.model_rebuild()
ScrapeAndExtractFromUrlsBodyLocation.model_rebuild()
ScrapeAndExtractFromUrlsBodyWebhook.model_rebuild()
ScrapeOptions.model_rebuild()
ScrapeOptionsActionsItemV0.model_rebuild()
ScrapeOptionsActionsItemV1.model_rebuild()
ScrapeOptionsActionsItemV2.model_rebuild()
ScrapeOptionsActionsItemV3.model_rebuild()
ScrapeOptionsActionsItemV4.model_rebuild()
ScrapeOptionsActionsItemV5.model_rebuild()
ScrapeOptionsActionsItemV6.model_rebuild()
ScrapeOptionsActionsItemV7.model_rebuild()
ScrapeOptionsActionsItemV8.model_rebuild()
ScrapeOptionsChangeTrackingOptions.model_rebuild()
ScrapeOptionsJsonOptions.model_rebuild()
ScrapeOptionsLocation.model_rebuild()
ScrapeOptionsV1ChangeTrackingOptions.model_rebuild()
SearchAndScrapeBodyScrapeOptions.model_rebuild()
SearchAndScrapeBodyScrapeOptionsActionsItemV0.model_rebuild()
SearchAndScrapeBodyScrapeOptionsActionsItemV1.model_rebuild()
SearchAndScrapeBodyScrapeOptionsActionsItemV2.model_rebuild()
SearchAndScrapeBodyScrapeOptionsActionsItemV3.model_rebuild()
SearchAndScrapeBodyScrapeOptionsActionsItemV4.model_rebuild()
SearchAndScrapeBodyScrapeOptionsActionsItemV5.model_rebuild()
SearchAndScrapeBodyScrapeOptionsActionsItemV6.model_rebuild()
SearchAndScrapeBodyScrapeOptionsActionsItemV7.model_rebuild()
SearchAndScrapeBodyScrapeOptionsActionsItemV8.model_rebuild()
SearchAndScrapeBodyScrapeOptionsJsonOptions.model_rebuild()
SearchAndScrapeBodyScrapeOptionsLocation.model_rebuild()

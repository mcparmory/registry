"""
Perplexity Ai Api MCP Server - Pydantic Models

Generated: 2026-05-05 15:53:17 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "ChatCompletionsChatCompletionsPostRequest",
    "ContextualizedEmbeddingsV1ContextualizedembeddingsPostRequest",
    "CreateAsyncChatCompletionsAsyncChatCompletionsPostRequest",
    "EmbeddingsV1EmbeddingsPostRequest",
    "GetAsyncChatCompletionResponseAsyncChatCompletionsApiRequestGetRequest",
    "SearchSearchPostRequest",
    "ApiSearchRequest",
    "ChatMessageInput",
    "ResponseFormatJsonSchema",
    "ResponseFormatText",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: create_chat_completion
class ChatCompletionsChatCompletionsPostRequestBodyWebSearchOptionsUserLocation(StrictModel):
    latitude: float | None = Field(default=None, validation_alias="latitude", serialization_alias="latitude", description="Latitude coordinate for location-aware search results, typically used with longitude, city, region, or country.")
    longitude: float | None = Field(default=None, validation_alias="longitude", serialization_alias="longitude", description="Longitude coordinate for location-aware search results, typically used with latitude, city, region, or country.")
    country: str | None = Field(default=None, validation_alias="country", serialization_alias="country", description="ISO 3166-1 alpha-2 country code (e.g., US, GB, FR) to localize search results and responses.")
    city: str | None = Field(default=None, validation_alias="city", serialization_alias="city", description="City name to provide geographic context for search results and localized responses.")
    region: str | None = Field(default=None, validation_alias="region", serialization_alias="region", description="State or region name to refine geographic context for search results.")
class ChatCompletionsChatCompletionsPostRequestBodyWebSearchOptions(StrictModel):
    search_context_size: Literal["low", "medium", "high"] | None = Field(default=None, validation_alias="search_context_size", serialization_alias="search_context_size", description="Controls the breadth of search context included in the response: low (minimal), medium (balanced), or high (comprehensive). Defaults to low.")
    search_type: Literal["fast", "pro", "auto"] | None = Field(default=None, validation_alias="search_type", serialization_alias="search_type", description="Search quality strategy: fast prioritizes speed, pro prioritizes result quality, auto lets the model decide based on the query.")
    image_results_enhanced_relevance: bool | None = Field(default=None, validation_alias="image_results_enhanced_relevance", serialization_alias="image_results_enhanced_relevance", description="When enabled, applies enhanced relevance filtering to image results to prioritize higher-quality matches.")
    user_location: ChatCompletionsChatCompletionsPostRequestBodyWebSearchOptionsUserLocation | None = None
class ChatCompletionsChatCompletionsPostRequestBody(StrictModel):
    max_tokens: int | None = Field(default=None, description="Maximum number of tokens to generate in the completion, between 1 and 128,000.", le=128000, gt=0)
    model: Literal["sonar", "sonar-pro", "sonar-deep-research", "sonar-reasoning-pro"] = Field(default=..., description="The model variant to use for generating the response. Choose from sonar (base), sonar-pro (enhanced), sonar-deep-research (comprehensive), or sonar-reasoning-pro (advanced reasoning).")
    stream: bool | None = Field(default=None, description="Enable server-sent event streaming to receive the response incrementally rather than waiting for the complete result.")
    stop: str | list[str] | None = Field(default=None, description="One or more strings that will cause generation to stop immediately when produced. Useful for controlling output length or format.")
    temperature: float | None = Field(default=None, description="Controls response randomness on a scale from 0 (deterministic) to 2 (highly random). Lower values produce more consistent outputs; higher values increase creativity.", ge=0, le=2)
    top_p: float | None = Field(default=None, description="Nucleus sampling parameter between 0 and 1 that controls output diversity by considering only the most likely tokens that sum to this probability.", ge=0, le=1)
    response_format: Annotated[ResponseFormatText | ResponseFormatJsonSchema, Field(discriminator="type_")] | None = Field(default=None, description="Specifies output format constraints. Set type to json_schema for structured JSON output, or omit for default text responses.")
    messages: list[ChatMessageInput] = Field(default=..., description="Array of message objects representing the conversation history, with each message containing role and content. Order matters—earlier messages provide context for later responses.")
    search_mode: Literal["web", "academic", "sec"] | None = Field(default=None, description="Restrict search results to a specific source: web (general internet), academic (scholarly articles), or sec (SEC filings and financial documents).")
    return_images: bool | None = Field(default=None, description="Include image results in the response alongside text results.")
    return_related_questions: bool | None = Field(default=None, description="Generate suggested follow-up questions based on the search results to facilitate deeper exploration of the topic.")
    enable_search_classifier: bool | None = Field(default=None, description="Enable automatic classification to determine whether web search is necessary for the query, optimizing performance for queries answerable from training data alone.")
    disable_search: bool | None = Field(default=None, description="Disable all web search capabilities and respond based exclusively on the model's training data.")
    search_domain_filter: list[str] | None = Field(default=None, description="Array of domain names (e.g., github.com, wikipedia.org) to limit search results to specific sources. Order is not significant.")
    search_language_filter: list[str] | None = Field(default=None, description="Array of ISO 639-1 language codes (e.g., en, fr, de) to filter results by language. Order is not significant.")
    search_recency_filter: Literal["hour", "day", "week", "month", "year"] | None = Field(default=None, description="Filter search results by publication recency: hour (last hour), day (last 24 hours), week (last 7 days), month (last 30 days), or year (last 365 days).")
    image_format_filter: list[str] | None = Field(default=None, description="Array of image file formats (e.g., png, jpg, gif) to filter image results. Order is not significant.")
    image_domain_filter: list[str] | None = Field(default=None, description="Array of domain names to limit image results to specific sources. Order is not significant.")
    stream_mode: Literal["full", "concise"] | None = Field(default=None, description="Controls streaming event format: full suppresses reasoning events and includes metadata inline for cleaner output; concise emits reasoning events separately for detailed insight. Defaults to full.")
    reasoning_effort: Literal["minimal", "low", "medium", "high"] | None = Field(default=None, description="Controls reasoning depth for models that support it: minimal (fastest), low (basic), medium (balanced), or high (most thorough). Only applicable to reasoning-capable models.")
    language_preference: str | None = Field(default=None, description="ISO 639-1 language code (e.g., en, fr, de) to specify the preferred language for the response.")
    web_search_options: ChatCompletionsChatCompletionsPostRequestBodyWebSearchOptions | None = None
class ChatCompletionsChatCompletionsPostRequest(StrictModel):
    """Generate a chat completion response using a specified Sonar model, with optional web search, streaming, and structured output capabilities. Supports conversation history, location context, and advanced search filtering."""
    body: ChatCompletionsChatCompletionsPostRequestBody

# Operation: search_web
class SearchSearchPostRequestBody(StrictModel):
    body: ApiSearchRequest = Field(default=..., description="Search query parameters including the search terms, optional filters, and result preferences. Specify your search query and any desired constraints for filtering results.")
class SearchSearchPostRequest(StrictModel):
    """Search the web and retrieve relevant content from web pages matching your query. Returns a curated list of results with page contents."""
    body: SearchSearchPostRequestBody

# Operation: create_embeddings
class EmbeddingsV1EmbeddingsPostRequestBody(StrictModel):
    input_: str | list[str] = Field(default=..., validation_alias="input", serialization_alias="input", description="Text or texts to embed as a string or array of strings. Submit up to 512 texts per request, with each text limited to 32K tokens and a combined total of 120,000 tokens across all inputs. Empty strings are not permitted.")
    model: Literal["pplx-embed-v1-0.6b", "pplx-embed-v1-4b"] = Field(default=..., description="The embedding model to use. Choose between pplx-embed-v1-0.6b (1024 dimensions) or pplx-embed-v1-4b (2560 dimensions).")
    dimensions: int | None = Field(default=None, description="Optional number of dimensions for the output embeddings using Matryoshka scaling. For pplx-embed-v1-0.6b, specify between 128 and 1024 dimensions; for pplx-embed-v1-4b, between 128 and 2560 dimensions. Defaults to the model's full dimension count if not specified.", ge=128, le=2560)
    encoding_format: Literal["base64_int8", "base64_binary"] | None = Field(default=None, description="Optional output encoding format for embeddings. Use base64_int8 for base64-encoded signed 8-bit integers, or base64_binary for base64-encoded packed binary (1 bit per dimension). Defaults to base64_int8.")
class EmbeddingsV1EmbeddingsPostRequest(StrictModel):
    """Generate vector embeddings for one or more texts to enable semantic search, clustering, and machine learning applications. Supports flexible output dimensions and encoding formats."""
    body: EmbeddingsV1EmbeddingsPostRequestBody

# Operation: create_contextualized_embeddings
class ContextualizedEmbeddingsV1ContextualizedembeddingsPostRequestBody(StrictModel):
    input_: list[list[str]] = Field(default=..., validation_alias="input", serialization_alias="input", description="Nested array where each inner array contains text chunks from a single document. Chunks within the same document are encoded together to maintain document-level context awareness. Supports up to 512 documents with a maximum of 16,000 total chunks across all documents, 32,000 tokens per document, and 120,000 tokens combined across the entire request. Empty strings are not permitted.", min_length=1, max_length=512)
    model: Literal["pplx-embed-context-v1-0.6b", "pplx-embed-context-v1-4b"] = Field(default=..., description="The contextualized embedding model to use. Choose between the 0.6B parameter model or the 4B parameter model based on your accuracy and performance requirements.")
    dimensions: int | None = Field(default=None, description="Optional number of dimensions for the output embeddings using Matryoshka scaling. Supported range is 128 to 1024 dimensions for the 0.6B model and 128 to 2560 dimensions for the 4B model. Defaults to the model's full dimensionality (1024 or 2560 respectively).", ge=128, le=2560)
    encoding_format: Literal["base64_int8", "base64_binary"] | None = Field(default=None, description="Optional output encoding format for embeddings. Use base64_int8 for base64-encoded signed 8-bit integers, or base64_binary for base64-encoded packed binary format with 1 bit per dimension. Defaults to base64_int8.")
class ContextualizedEmbeddingsV1ContextualizedembeddingsPostRequest(StrictModel):
    """Generate contextualized embeddings for document chunks where chunks from the same document share context awareness, improving retrieval quality for document-based applications."""
    body: ContextualizedEmbeddingsV1ContextualizedembeddingsPostRequestBody

# Operation: get_async_chat_completion_response
class GetAsyncChatCompletionResponseAsyncChatCompletionsApiRequestGetRequestPath(StrictModel):
    api_request: str = Field(default=..., description="The unique identifier of the asynchronous chat completion request whose response you want to retrieve.")
class GetAsyncChatCompletionResponseAsyncChatCompletionsApiRequestGetRequest(StrictModel):
    """Retrieve the completion response for a previously submitted asynchronous chat request using its request identifier."""
    path: GetAsyncChatCompletionResponseAsyncChatCompletionsApiRequestGetRequestPath

# Operation: create_async_chat_completion
class CreateAsyncChatCompletionsAsyncChatCompletionsPostRequestBodyRequestWebSearchOptionsUserLocation(StrictModel):
    latitude: float | None = Field(default=None, validation_alias="latitude", serialization_alias="latitude", description="Latitude coordinate for location-based search context. Use with longitude, city, region, or country to refine geographic relevance.")
    longitude: float | None = Field(default=None, validation_alias="longitude", serialization_alias="longitude", description="Longitude coordinate for location-based search context. Use with latitude, city, region, or country to refine geographic relevance.")
    country: str | None = Field(default=None, validation_alias="country", serialization_alias="country", description="ISO 3166-1 alpha-2 country code to provide geographic context for search results and localized responses.")
    city: str | None = Field(default=None, validation_alias="city", serialization_alias="city", description="City name to provide geographic context for location-aware search and response localization.")
    region: str | None = Field(default=None, validation_alias="region", serialization_alias="region", description="State or region name to provide geographic context for location-aware search and response localization.")
class CreateAsyncChatCompletionsAsyncChatCompletionsPostRequestBodyRequestWebSearchOptions(StrictModel):
    search_context_size: Literal["low", "medium", "high"] | None = Field(default=None, validation_alias="search_context_size", serialization_alias="search_context_size", description="Controls the breadth of search context included in the response. Choose 'low' for minimal context, 'medium' for balanced coverage, or 'high' for comprehensive search results. Defaults to 'low'.")
    search_type: Literal["fast", "pro", "auto"] | None = Field(default=None, validation_alias="search_type", serialization_alias="search_type", description="Determines search quality versus speed tradeoff. Use 'fast' for quick results, 'pro' for higher quality results, or 'auto' to let the model decide based on the query.")
    image_results_enhanced_relevance: bool | None = Field(default=None, validation_alias="image_results_enhanced_relevance", serialization_alias="image_results_enhanced_relevance", description="When enabled, applies enhanced relevance filtering to image results to prioritize higher-quality and more contextually relevant images.")
    user_location: CreateAsyncChatCompletionsAsyncChatCompletionsPostRequestBodyRequestWebSearchOptionsUserLocation | None = None
class CreateAsyncChatCompletionsAsyncChatCompletionsPostRequestBodyRequest(StrictModel):
    max_tokens: int | None = Field(default=None, validation_alias="max_tokens", serialization_alias="max_tokens", description="Maximum number of tokens to generate in the completion response. Must be greater than 0 and cannot exceed 128,000 tokens.", le=128000, gt=0)
    model: Literal["sonar", "sonar-pro", "sonar-deep-research", "sonar-reasoning-pro"] = Field(default=..., validation_alias="model", serialization_alias="model", description="The model variant to use for processing the request. Choose from sonar (base), sonar-pro (enhanced), sonar-deep-research (comprehensive), or sonar-reasoning-pro (advanced reasoning).")
    stream: bool | None = Field(default=None, validation_alias="stream", serialization_alias="stream", description="Enable server-sent event (SSE) streaming to receive response chunks in real-time as they are generated.")
    stop: str | list[str] | None = Field(default=None, validation_alias="stop", serialization_alias="stop", description="One or more stop sequences that will terminate generation when encountered. Provide as a list of strings.")
    temperature: float | None = Field(default=None, validation_alias="temperature", serialization_alias="temperature", description="Controls response randomness on a scale from 0 to 2. Lower values (closer to 0) produce more deterministic outputs; higher values increase creativity and variability.", ge=0, le=2)
    top_p: float | None = Field(default=None, validation_alias="top_p", serialization_alias="top_p", description="Nucleus sampling parameter between 0 and 1 that controls output diversity. Lower values focus on the most likely tokens; higher values allow more diverse token selection.", ge=0, le=1)
    response_format: Annotated[ResponseFormatText | ResponseFormatJsonSchema, Field(discriminator="type_")] | None = Field(default=None, validation_alias="response_format", serialization_alias="response_format", description="Specifies the output format structure. Set type to 'json_schema' to enforce structured JSON output; omit for default text responses.")
    messages: list[ChatMessageInput] = Field(default=..., validation_alias="messages", serialization_alias="messages", description="Array of message objects forming the conversation history. Each message should include role (user, assistant, system) and content fields.")
    search_mode: Literal["web", "academic", "sec"] | None = Field(default=None, validation_alias="search_mode", serialization_alias="search_mode", description="Specifies the source domain for search results. Choose 'web' for general internet search, 'academic' for scholarly articles, or 'sec' for SEC filings and financial documents.")
    return_images: bool | None = Field(default=None, validation_alias="return_images", serialization_alias="return_images", description="When enabled, includes relevant images in the response alongside text results.")
    return_related_questions: bool | None = Field(default=None, validation_alias="return_related_questions", serialization_alias="return_related_questions", description="When enabled, generates suggested follow-up questions based on the search results to facilitate deeper exploration of the topic.")
    enable_search_classifier: bool | None = Field(default=None, validation_alias="enable_search_classifier", serialization_alias="enable_search_classifier", description="When enabled, uses a classifier to intelligently determine whether web search is necessary for the query or if the model's training data is sufficient.")
    disable_search: bool | None = Field(default=None, validation_alias="disable_search", serialization_alias="disable_search", description="When enabled, completely disables web search functionality and the model responds exclusively based on its training data without accessing external sources.")
    search_domain_filter: list[str] | None = Field(default=None, validation_alias="search_domain_filter", serialization_alias="search_domain_filter", description="Restrict search results to specific domains by providing a list of domain names (e.g., github.com, wikipedia.org). Results will only include pages from these domains.")
    search_language_filter: list[str] | None = Field(default=None, validation_alias="search_language_filter", serialization_alias="search_language_filter", description="Filter search results by language using ISO 639-1 language codes (e.g., en for English, fr for French, de for German). Provide as a list of codes.")
    search_recency_filter: Literal["hour", "day", "week", "month", "year"] | None = Field(default=None, validation_alias="search_recency_filter", serialization_alias="search_recency_filter", description="Filter search results by publication recency. Choose from 'hour' (last hour), 'day' (last 24 hours), 'week' (last 7 days), 'month' (last 30 days), or 'year' (last 365 days).")
    image_format_filter: list[str] | None = Field(default=None, validation_alias="image_format_filter", serialization_alias="image_format_filter", description="Filter image results by file format. Provide a list of formats (e.g., png, jpg, gif, webp) to include only images in those formats.")
    image_domain_filter: list[str] | None = Field(default=None, validation_alias="image_domain_filter", serialization_alias="image_domain_filter", description="Restrict image results to specific domains by providing a list of domain names. Images will only be sourced from these domains.")
    stream_mode: Literal["full", "concise"] | None = Field(default=None, validation_alias="stream_mode", serialization_alias="stream_mode", description="Controls the format of streaming events when streaming is enabled. Use 'full' to suppress reasoning events and include metadata inline; use 'concise' to emit reasoning events separately. Defaults to 'full'.")
    reasoning_effort: Literal["minimal", "low", "medium", "high"] | None = Field(default=None, validation_alias="reasoning_effort", serialization_alias="reasoning_effort", description="Controls the computational effort allocated to reasoning. Choose 'minimal' for quick responses, 'low' or 'medium' for balanced reasoning, or 'high' for deep analytical reasoning.")
    language_preference: str | None = Field(default=None, validation_alias="language_preference", serialization_alias="language_preference", description="Specify the preferred response language using an ISO 639-1 language code (e.g., en, es, fr, de). The model will attempt to respond in this language when possible.")
    web_search_options: CreateAsyncChatCompletionsAsyncChatCompletionsPostRequestBodyRequestWebSearchOptions | None = None
class CreateAsyncChatCompletionsAsyncChatCompletionsPostRequestBody(StrictModel):
    request: CreateAsyncChatCompletionsAsyncChatCompletionsPostRequestBodyRequest
class CreateAsyncChatCompletionsAsyncChatCompletionsPostRequest(StrictModel):
    """Submit an asynchronous chat completion request with optional web search, structured output, and streaming capabilities. Supports multiple model variants and fine-grained control over search behavior, response format, and reasoning depth."""
    body: CreateAsyncChatCompletionsAsyncChatCompletionsPostRequestBody

# ============================================================================
# Component Models
# ============================================================================

class ChatMessageContentTextChunk(PermissiveModel):
    type_: Literal["text"] = Field(..., validation_alias="type", serialization_alias="type")
    text: str

class DateFilters(PermissiveModel):
    last_updated_after_filter: str | None = Field(None, description="Return results updated after this date (MM/DD/YYYY)")
    last_updated_before_filter: str | None = Field(None, description="Return results updated before this date (MM/DD/YYYY)")
    search_after_date_filter: str | None = Field(None, description="Return results published after this date (MM/DD/YYYY)")
    search_before_date_filter: str | None = Field(None, description="Return results published before this date (MM/DD/YYYY)")
    search_recency_filter: Literal["hour", "day", "week", "month", "year"] | None = Field(None, description="Filter by publication recency (hour/day/week/month/year)")

class JsonSchema(PermissiveModel):
    schema_: dict[str, Any] = Field(..., validation_alias="schema", serialization_alias="schema")
    name: str | None = 'schema'
    description: str | None = None
    strict: bool | None = True

class ResponseFormatJsonSchema(PermissiveModel):
    """Constrains the model output to match the provided JSON schema."""
    type_: Literal["json_schema"] = Field(..., validation_alias="type", serialization_alias="type", description="Must be `json_schema`.")
    json_schema: JsonSchema

class ResponseFormatText(PermissiveModel):
    type_: Literal["text"] = Field(..., validation_alias="type", serialization_alias="type", description="Must be `text`.")

class SearchDomainFilter(PermissiveModel):
    search_domain_filter: list[str] | None = Field(None, description="Limit search results to specific domains (max 20)", max_length=20)

class ApiSearchRequest(PermissiveModel):
    country: str | None = Field(None, description="ISO 3166-1 alpha-2 country code", min_length=2, max_length=2)
    max_results: int | None = Field(10, description="Maximum number of results to return", ge=1, le=20)
    max_tokens: int | None = Field(10000, description="Maximum tokens for context", ge=1, le=1000000)
    max_tokens_per_page: int | None = Field(4096, description="Maximum tokens per page", ge=1, le=1000000)
    query: str | list[str] = Field(..., description="Search query (required)")
    search_language_filter: list[str] | None = Field(None, description="ISO 639-1 language codes (2-character max)", max_length=20)
    search_domain_filter: list[str] | None = Field(None, description="Limit search results to specific domains (max 20)", max_length=20)
    last_updated_after_filter: str | None = Field(None, description="Return results updated after this date (MM/DD/YYYY)")
    last_updated_before_filter: str | None = Field(None, description="Return results updated before this date (MM/DD/YYYY)")
    search_after_date_filter: str | None = Field(None, description="Return results published after this date (MM/DD/YYYY)")
    search_before_date_filter: str | None = Field(None, description="Return results published before this date (MM/DD/YYYY)")
    search_recency_filter: Literal["hour", "day", "week", "month", "year"] | None = Field(None, description="Filter by publication recency (hour/day/week/month/year)")

class Url(PermissiveModel):
    url: str

class ChatMessageContentFileChunk(PermissiveModel):
    type_: Literal["file_url"] = Field(..., validation_alias="type", serialization_alias="type")
    file_url: Url | str
    file_name: str | None = None

class ChatMessageContentImageChunk(PermissiveModel):
    type_: Literal["image_url"] = Field(..., validation_alias="type", serialization_alias="type")
    image_url: Url | str

class ChatMessageContentPdfChunk(PermissiveModel):
    type_: Literal["pdf_url"] = Field(..., validation_alias="type", serialization_alias="type")
    pdf_url: Url | str

class VideoUrl(PermissiveModel):
    url: str
    frame_interval: str | int | None = None

class ChatMessageContentVideoChunk(PermissiveModel):
    type_: Literal["video_url"] = Field(..., validation_alias="type", serialization_alias="type")
    video_url: VideoUrl | str

class ChatMessageInput(PermissiveModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str | list[ChatMessageContentTextChunk | ChatMessageContentImageChunk | ChatMessageContentFileChunk | ChatMessageContentPdfChunk | ChatMessageContentVideoChunk] | None = Field(...)


# Rebuild models to resolve forward references (required for circular refs)
ApiSearchRequest.model_rebuild()
ChatMessageContentFileChunk.model_rebuild()
ChatMessageContentImageChunk.model_rebuild()
ChatMessageContentPdfChunk.model_rebuild()
ChatMessageContentTextChunk.model_rebuild()
ChatMessageContentVideoChunk.model_rebuild()
ChatMessageInput.model_rebuild()
DateFilters.model_rebuild()
JsonSchema.model_rebuild()
ResponseFormatJsonSchema.model_rebuild()
ResponseFormatText.model_rebuild()
SearchDomainFilter.model_rebuild()
Url.model_rebuild()
VideoUrl.model_rebuild()

"""
Ragie MCP Server - Pydantic Models

Generated: 2026-05-12 12:20:20 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "CreateAuthenticatorConnectionRequest",
    "CreateAuthenticatorRequest",
    "CreateConnectionRequest",
    "CreateDocumentFromUrlRequest",
    "CreateDocumentRawRequest",
    "CreateDocumentRequest",
    "CreateInstructionRequest",
    "CreateOauthRedirectUrlConnectionsOauthPostRequest",
    "CreatePartitionPartitionsPostRequest",
    "CreateResponseResponsesPostRequest",
    "DeleteAuthenticatorConnectionRequest",
    "DeleteConnectionConnectionsConnectionIdDeletePostRequest",
    "DeleteDocumentRequest",
    "DeleteInstructionRequest",
    "DeletePartitionPartitionsPartitionIdDeleteRequest",
    "GetConnectionConnectionsConnectionIdGetRequest",
    "GetConnectionStatsConnectionsConnectionIdStatsGetRequest",
    "GetDocumentChunkContentRequest",
    "GetDocumentChunkRequest",
    "GetDocumentChunksRequest",
    "GetDocumentContentRequest",
    "GetDocumentRequest",
    "GetDocumentSourceRequest",
    "GetDocumentSummaryRequest",
    "GetElementRequest",
    "GetPartitionPartitionsPartitionIdGetRequest",
    "GetResponseResponsesResponseIdGetRequest",
    "GetWebhookEndpointRequest",
    "ListAuthenticatorsRequest",
    "ListConnectionsConnectionsGetRequest",
    "ListDocumentsRequest",
    "ListElementsRequest",
    "ListEntitiesByDocumentRequest",
    "ListEntitiesByInstructionRequest",
    "ListInstructionEntityExtractionLogsRequest",
    "ListPartitionsPartitionsGetRequest",
    "ListWebhookEndpointsRequest",
    "PatchDocumentMetadataRequest",
    "PatchInstructionRequest",
    "RetrieveRequest",
    "SetConnectionEnabledConnectionsConnectionIdEnabledPutRequest",
    "SetConnectionLimitsConnectionsConnectionIdLimitPutRequest",
    "SetPartitionLimitsPartitionsPartitionIdLimitsPutRequest",
    "SyncConnectionRequest",
    "UpdateConnectionConnectionsConnectionIdPutRequest",
    "UpdateDocumentFileRequest",
    "UpdateDocumentFromUrlRequest",
    "UpdateDocumentRawRequest",
    "UpdatePartitionPartitionsPartitionIdPatchRequest",
    "UpdateWebhookEndpointRequest",
    "AuthenticatorConfluenceConnection",
    "AuthenticatorDropboxConnection",
    "AuthenticatorGmailConnection",
    "AuthenticatorGoogleDriveConnection",
    "AuthenticatorHubspotConnection",
    "AuthenticatorJiraConnection",
    "AuthenticatorNotionConnection",
    "AuthenticatorOnedriveConnection",
    "AuthenticatorSalesforceConnection",
    "AuthenticatorSharepointConnection",
    "AuthenticatorSlackConnection",
    "CreateDocumentBodyMode",
    "MediaModeParam",
    "PublicBackblazeConnection",
    "PublicFreshdeskConnection",
    "PublicGcsConnection",
    "PublicIntercomConnection",
    "PublicS3CompatibleConnection",
    "PublicWebcrawlerConnection",
    "PublicZendeskConnection",
    "Tool",
    "UpdateDocumentFileBodyMode",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_documents
class ListDocumentsRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of documents to return per page. Must be between 1 and 100 items. Defaults to 10 if not specified.", ge=1, le=100)
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Metadata filter expression to narrow results. Supports operators like $eq (equal), $ne (not equal), $gt/$gte (greater than), $lt/$lte (less than), $in/$nin (array membership), and logical AND/OR combinations. See documentation for syntax and examples.", examples=[{'department': {'$in': ['sales', 'marketing']}}])
class ListDocumentsRequest(StrictModel):
    """Retrieve a paginated list of all documents sorted by creation date (newest first). Use the page_size parameter to control results per page and the filter parameter to search by metadata. When more results are available, a cursor will be provided for fetching the next page."""
    query: ListDocumentsRequestQuery | None = None

# Operation: create_document
class CreateDocumentRequestBody(StrictModel):
    mode: CreateDocumentBodyMode | None = Field(default=None, description="Processing mode configuration for document ingestion. Accepts either an object with detailed mode settings or a scalar shorthand value.")
    metadata: dict[str, str | float | bool | list[str]] | None = Field(default=None, description="Custom metadata key-value pairs to attach to the document. Keys must be strings; values can be strings, numbers (integers or floats), booleans, or lists of strings. Up to 1000 total values are allowed across all metadata (each array item counts separately). Reserved keys like document_id, document_type, document_source, document_name, document_uploaded_at, start_time, end_time, and chunk_content_type are for internal use only.")
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. The binary file to upload and index. Supported formats include plain text (.txt, .md, .json, .html, .xml, .eml, .msg, .rst, .rtf), images (.png, .jpg, .jpeg, .webp, .tiff, .bmp, .heic), and documents (.pdf, .docx, .xlsx, .pptx, .csv, .epub, and others). PDF files exceeding 2000 pages are not supported in hi_res mode.", json_schema_extra={'format': 'byte'})
    external_id: str | None = Field(default=None, description="Optional external identifier for the document, such as an ID from an external system or the source URL where the file originates.")
    name: str | None = Field(default=None, description="Optional display name for the document. If provided, this name will be used; otherwise, the uploaded file's name will be used as the document name.")
    workflow: Literal["parse", "index"] | None = Field(default=None, description="Processing workflow to apply to the document. Choose 'parse' for document parsing or 'index' for indexing operations.")
class CreateDocumentRequest(StrictModel):
    """Upload and ingest a document for processing and retrieval. The document progresses through multiple processing stages (pending → partitioning → indexed → ready) and becomes available for retrieval once it reaches the ready state."""
    body: CreateDocumentRequestBody

# Operation: create_document_from_text
class CreateDocumentRawRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Optional human-readable name for the document. If not provided, defaults to the current timestamp.")
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(default=None, description="Optional key-value metadata to attach to the document. Keys must be strings; values can be strings, numbers, booleans, or lists of strings. Up to 1000 total values are allowed (each array item counts separately). Reserved keys like document_id, document_type, and document_source are for internal use only.")
    external_id: str | None = Field(default=None, description="Optional external identifier for cross-referencing with other systems, such as a database ID or source URL.")
    workflow: Literal["parse", "index"] | None = Field(default=None, description="Optional processing stage to stop at. Use 'parse' to extract elements only, or 'index' (or omit) to run the full processing pipeline including chunking and indexing.")
    data: str | dict[str, Any] = Field(default=..., description="The document content as raw text or JSON. Must contain at least 1 character.", min_length=1)
class CreateDocumentRawRequest(StrictModel):
    """Ingest a document as raw text for processing through an automated pipeline. The document progresses through multiple stages (pending → partitioning → indexed → ready) and becomes available for retrieval once it reaches the ready state."""
    body: CreateDocumentRawRequestBody

# Operation: ingest_document_from_url
class CreateDocumentFromUrlRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Optional human-readable name for the document. If not provided, a default name will be assigned.")
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(default=None, description="Optional key-value metadata to attach to the document. Keys must be strings; values can be strings, numbers, booleans, or lists of strings. Up to 1000 total values are allowed (each array item counts separately). Reserved keys like `document_id`, `document_type`, and `document_source` are for internal use only.")
    mode: Literal["hi_res", "fast", "agentic_ocr"] | MediaModeParam | None = Field(default=None, description="Partition strategy controlling how the document is processed. For text documents, use `'hi_res'` to extract images and tables (slower, ~20x), or `'fast'` for text only. For audio/video, specify processing preferences as a JSON object with keys like `'static'` (text), `'audio'`, and `'video'`. Use `'all'` for highest quality across all media types, or `'agentic_ocr'` for vision-model-based extraction (early access).")
    external_id: str | None = Field(default=None, description="Optional external identifier for the document, such as an ID from an external system or the source URL where the file originates.")
    workflow: Literal["parse", "index"] | None = Field(default=None, description="Optional processing stage to stop at. Set to `'parse'` to extract elements only, or `'index'` (default) to complete the full processing pipeline including indexing and summarization.")
    url: str = Field(default=..., description="URL of the file to ingest. Must be publicly accessible via HTTP or HTTPS, between 1 and 2083 characters in length, and a valid URI format.", min_length=1, max_length=2083, json_schema_extra={'format': 'uri'})
class CreateDocumentFromUrlRequest(StrictModel):
    """Ingest a document from a publicly accessible URL for processing and retrieval. The document progresses through multiple processing stages (pending → partitioning → indexed → ready) before becoming available for retrieval, with optional extraction of images, tables, and media content based on the selected partition strategy."""
    body: CreateDocumentFromUrlRequestBody

# Operation: get_document
class GetDocumentRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier of the document to retrieve, formatted as a UUID (universally unique identifier).", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class GetDocumentRequest(StrictModel):
    """Retrieve a specific document by its unique identifier. Returns the full document details including metadata and content."""
    path: GetDocumentRequestPath

# Operation: delete_document
class DeleteDocumentRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier of the document to delete, formatted as a UUID.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class DeleteDocumentRequestQuery(StrictModel):
    async_: bool | None = Field(default=None, validation_alias="async", serialization_alias="async", description="When true, the deletion is performed asynchronously and returns immediately without waiting for completion. Defaults to false for synchronous deletion.", examples=[False])
class DeleteDocumentRequest(StrictModel):
    """Permanently delete a document by its unique identifier. Supports both synchronous and asynchronous deletion modes."""
    path: DeleteDocumentRequestPath
    query: DeleteDocumentRequestQuery | None = None

# Operation: update_document_file
class UpdateDocumentFileRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier of the document to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class UpdateDocumentFileRequestBody(StrictModel):
    mode: UpdateDocumentFileBodyMode | None = Field(default=None, description="Optional processing mode configuration that controls how the file is extracted and indexed. Accepts either an object with detailed settings or a scalar shorthand value.")
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. The binary file to upload and process. Supported formats include text files (.txt, .md, .json, .html, .xml, .eml, .msg, .rst, .rtf), images (.png, .jpg, .jpeg, .webp, .tiff, .bmp, .heic), and documents (.pdf, .doc, .docx, .xlsx, .xls, .csv, .ppt, .pptx, .epub, .odt, .tsv). PDF files must not exceed 2000 pages.", json_schema_extra={'format': 'byte'})
class UpdateDocumentFileRequest(StrictModel):
    """Replace the file content of an existing document. The uploaded file will be extracted, processed, and indexed for retrieval. Supports text formats (plain text, markdown, email, HTML, XML, JSON, RST, RTF), images (PNG, WebP, JPEG, TIFF, BMP, HEIC), and documents (PDF, Word, Excel, PowerPoint, CSV, EPUB, ODT)."""
    path: UpdateDocumentFileRequestPath
    body: UpdateDocumentFileRequestBody

# Operation: update_document_raw
class UpdateDocumentRawRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier of the document to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class UpdateDocumentRawRequestBody(StrictModel):
    data: str | dict[str, Any] = Field(default=..., description="The new document content as text or JSON. Must contain at least one character.", min_length=1)
class UpdateDocumentRawRequest(StrictModel):
    """Replace the raw content of an existing document with new text or JSON data. This operation overwrites the entire document content."""
    path: UpdateDocumentRawRequestPath
    body: UpdateDocumentRawRequestBody

# Operation: update_document_from_url
class UpdateDocumentFromUrlRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier of the document to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class UpdateDocumentFromUrlRequestBody(StrictModel):
    mode: Literal["hi_res", "fast", "agentic_ocr"] | MediaModeParam | None = Field(default=None, description="Processing strategy for document ingestion. For text documents, use 'hi_res' to extract images and tables (slower, ~20x) or 'fast' for text-only extraction. For audio, use true/false to enable processing. For video, use 'audio_only', 'video_only', or 'audio_video'. For mixed media, provide a JSON object with keys 'static' (text), 'audio' (boolean), and/or 'video' (strategy). Use 'all' for highest quality across all media types. Defaults to 'fast'.")
    url: str = Field(default=..., description="Public HTTP or HTTPS URL of the file to ingest. Must be publicly accessible and between 1 and 2083 characters in length.", min_length=1, max_length=2083, json_schema_extra={'format': 'uri'})
class UpdateDocumentFromUrlRequest(StrictModel):
    """Update a document by ingesting content from a publicly accessible URL. The document progresses through multiple processing states (pending → indexed → ready) before becoming available for retrieval, with optional high-resolution processing for extracting images and tables."""
    path: UpdateDocumentFromUrlRequestPath
    body: UpdateDocumentFromUrlRequestBody

# Operation: update_document_metadata
class PatchDocumentMetadataRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The UUID identifier of the document to update.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class PatchDocumentMetadataRequestBody(StrictModel):
    metadata: dict[str, Any] = Field(default=..., description="A partial metadata object with string keys and values that are strings, numbers, booleans, or lists of strings. Set a key to null to delete it. Up to 1000 total values are allowed across all metadata (each array item counts separately). Numbers are converted to 64-bit floating point.", examples=[{'classified': 'null (setting null deletes key from metadata)', 'editors': ['Alice', 'Bob'], 'published': True, 'articleCount': 42, 'title': 'declassified report'}])
    async_: bool | None = Field(default=None, validation_alias="async", serialization_alias="async", description="If true, the update runs asynchronously in the background and returns a 202 response; if false (default), it runs synchronously and returns a 200 response.")
class PatchDocumentMetadataRequest(StrictModel):
    """Partially update a document's metadata with new or modified key-value pairs. Reserved keys (document_id, document_type, document_source, document_name, document_uploaded_at) cannot be modified. For connection-managed documents, updates create a metadata overlay applied on each sync."""
    path: PatchDocumentMetadataRequestPath
    body: PatchDocumentMetadataRequestBody

# Operation: list_document_chunks
class GetDocumentChunksRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier (UUID) of the document to retrieve chunks from.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class GetDocumentChunksRequestQuery(StrictModel):
    start_index: int | None = Field(default=None, description="The inclusive starting index for filtering chunks by range. If specified alone, returns only the chunk at this index. If both start_index and end_index are omitted, all chunks are returned without index filtering.", examples=[3])
    end_index: int | None = Field(default=None, description="The inclusive ending index for filtering chunks by range. If specified alone, returns only the chunk at this index. If both start_index and end_index are omitted, all chunks are returned without index filtering.", examples=[5])
    page_size: int | None = Field(default=None, description="Number of chunks to return per page, between 1 and 100 (defaults to 10). Use this with the cursor parameter to control pagination.", ge=1, le=100)
class GetDocumentChunksRequest(StrictModel):
    """Retrieve all chunks from a document, sorted by index in ascending order. Results are paginated with a maximum of 100 chunks per page; use the cursor parameter to fetch subsequent pages. Documents created before September 18, 2024 that haven't been updated may have chunks with index -1, sorted by ID instead."""
    path: GetDocumentChunksRequestPath
    query: GetDocumentChunksRequestQuery | None = None

# Operation: get_document_chunk
class GetDocumentChunkRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier of the document containing the chunk, formatted as a UUID.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
    chunk_id: str = Field(default=..., description="The unique identifier of the specific chunk to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class GetDocumentChunkRequest(StrictModel):
    """Retrieves a specific chunk from a document using both the document ID and chunk ID. Use this to fetch individual content segments within a larger document."""
    path: GetDocumentChunkRequestPath

# Operation: get_document_chunk_content
class GetDocumentChunkContentRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier (UUID) of the document containing the chunk.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
    chunk_id: str = Field(default=..., description="The unique identifier (UUID) of the specific chunk within the document.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class GetDocumentChunkContentRequestQuery(StrictModel):
    media_type: Literal["text/plain", "audio/mpeg", "video/mp4", "image/webp", "image/heic", "image/bmp", "image/png", "image/jpeg", "image/tiff"] | None = Field(default=None, description="The desired format for the returned content as a MIME type (e.g., text/plain, audio/mpeg, video/mp4, or various image formats). The requested format must be supported by the document type, or an error will be returned.", examples=['text/plain', 'audio/mpeg', 'video/mp4'])
    download: bool | None = Field(default=None, description="Whether to return the content as a downloadable file attachment or as a raw stream. Defaults to false (raw stream).")
class GetDocumentChunkContentRequest(StrictModel):
    """Retrieves the content of a specific document chunk in the requested format. Supports streaming media content for audio and video documents, with optional file download capability."""
    path: GetDocumentChunkContentRequestPath
    query: GetDocumentChunkContentRequestQuery | None = None

# Operation: get_document_content
class GetDocumentContentRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier of the document to retrieve, formatted as a UUID.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class GetDocumentContentRequestQuery(StrictModel):
    media_type: str | None = Field(default=None, description="The desired format for the returned content, specified as a MIME type (e.g., application/json, text/plain, audio/mpeg, video/mp4). If the document doesn't support the requested type, an error will be returned.")
    download: bool | None = Field(default=None, description="When true, the content is returned as a downloadable file with its original filename. When false (default), the content is returned as a raw stream.")
class GetDocumentContentRequest(StrictModel):
    """Retrieve the content of a document in your preferred format. Supports multiple media types including JSON (with metadata), plain text, and streaming formats for audio/video content. Non-textual media like images are returned as text descriptions."""
    path: GetDocumentContentRequestPath
    query: GetDocumentContentRequestQuery | None = None

# Operation: get_document_source
class GetDocumentSourceRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier of the document, formatted as a UUID.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class GetDocumentSourceRequest(StrictModel):
    """Retrieve the original source file of a document. The source varies by origin: uploaded files are returned as-is, URL-sourced documents return the fetched content, and connection-synced documents return the format specific to that connection type (e.g., file from Google Drive, JSON from Salesforce)."""
    path: GetDocumentSourceRequestPath

# Operation: search_document_chunks
class RetrieveRequestBody(StrictModel):
    query: str = Field(default=..., description="The search query used to find semantically relevant document chunks. Can be a natural language question or statement.", examples=['What is the best pizza place in SF?'])
    top_k: int | None = Field(default=None, description="Maximum number of chunks to return in the results. Defaults to 8 chunks.", examples=[8])
    filter_: dict[str, Any] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Metadata filter to narrow results to documents matching specific criteria. Supports equality, inequality, comparison, and array membership operators that can be combined with AND/OR logic.", examples=[{'department': {'$in': ['sales', 'marketing']}}])
    rerank: bool | None = Field(default=None, description="Enable semantic reranking of results for higher relevancy, improving accuracy and reducing hallucinations. Processing will be slower but returns a more focused set of highly relevant chunks.", examples=[True])
    max_chunks_per_document: int | None = Field(default=None, description="Limit the number of chunks retrieved from any single document. Use this to diversify results across multiple documents rather than concentrating chunks from one source.", examples=[0])
    recency_bias: bool | None = Field(default=None, description="Prioritize more recent documents over older ones in the ranking. Useful when document freshness is important for accuracy.", examples=[False])
class RetrieveRequest(StrictModel):
    """Search and retrieve relevant document chunks based on a semantic query, with optional filtering, reranking, and recency bias to support accurate LLM-based generation and reduce hallucinations."""
    body: RetrieveRequestBody

# Operation: get_document_summary
class GetDocumentSummaryRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier of the document, formatted as a UUID.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class GetDocumentSummaryRequest(StrictModel):
    """Retrieve an LLM-generated summary of a document. The summary is automatically created when the document is first uploaded or updated. Note: This feature is in beta and may change; data files (xls, xlsx, csv, json) and documents exceeding 1M tokens are not supported."""
    path: GetDocumentSummaryRequestPath

# Operation: create_instruction
class CreateInstructionRequestBody(StrictModel):
    name: str = Field(default=..., description="A unique name for the instruction that identifies its purpose (e.g., 'Find all pizzas'). Must not duplicate existing instruction names.", examples=['Find all pizzas'])
    active: bool | None = Field(default=None, description="Whether this instruction is immediately active and applied to new and updated documents. Defaults to true.", examples=[True])
    scope: Literal["document", "chunk"] | None = Field(default=None, description="Determines the granularity of analysis: 'document' analyzes the entire document (useful for summaries or sentiment), while 'chunk' analyzes individual document sections (useful for fine-grained search). Defaults to 'chunk'.", examples=['document'])
    prompt: str = Field(default=..., description="A natural language instruction describing what data to extract from documents. This prompt is applied to document content and results are stored as entities matching the entity_schema.", examples=['Find all pizzas described in the text.'])
    context_template: str | None = Field(default=None, description="An optional Mustache template that prepends document context (name, type, source, metadata) to the content before extraction. Use variables like {{document.name}} and {{document.metadata.key_name}} to include document details.", examples=['Document: {{document.name}} {{document.metadata.key_foo}}'])
    entity_schema: dict[str, Any] = Field(default=..., description="A JSON schema defining the structure of extracted entities. Must be an object type at the root. For multiple items, use an array property (e.g., 'emails' as an array of strings). For single values, wrap in an object with a single key (e.g., 'summary' as a string).", examples=[{'additionalProperties': False, 'properties': {'size': {'enum': ['small', 'medium', 'large'], 'type': 'string'}, 'crust': {'enum': ['thin', 'thick', 'stuffed'], 'type': 'string'}, 'sauce': {'enum': ['tomato', 'alfredo', 'pesto'], 'type': 'string'}, 'cheese': {'enum': ['mozzarella', 'cheddar', 'parmesan', 'vegan'], 'type': 'string'}, 'toppings': {'items': {'enum': ['pepperoni', 'mushrooms', 'onions', 'sausage', 'bacon', 'extra cheese', 'black olives', 'green peppers', 'pineapple', 'spinach'], 'type': 'string'}, 'type': 'array'}, 'extraInstructions': {'type': 'string'}}, 'required': ['size', 'crust', 'sauce', 'cheese'], 'title': 'Pizza', 'type': 'object'}])
    filter_: dict[str, Any] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="An optional metadata filter that restricts instruction application to matching documents. Supports operators like $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin, and can combine conditions with AND/OR logic.", examples=[{'toppings': {'$in': ['pizza', 'mushrooms']}}])
class CreateInstructionRequest(StrictModel):
    """Create a new instruction that automatically extracts structured data from documents as they are created or updated. Instructions apply natural language prompts to documents and store results according to a defined JSON schema."""
    body: CreateInstructionRequestBody

# Operation: update_instruction
class PatchInstructionRequestPath(StrictModel):
    instruction_id: str = Field(default=..., description="The unique identifier (UUID) of the instruction to update.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class PatchInstructionRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A unique name for the instruction. Must not conflict with existing instruction names.", examples=['Find all pizzas'])
    active: bool | None = Field(default=None, description="Whether the instruction is active. Active instructions are automatically applied when documents are created or their files are updated.", examples=[True])
    scope: Literal["document", "chunk"] | None = Field(default=None, description="The scope determines how the instruction is applied: 'document' analyzes the entire document (ideal for summaries or sentiment analysis), while 'chunk' analyzes individual document chunks (ideal for fine-grained search or extraction).", examples=['document'])
    prompt: str | None = Field(default=None, description="A natural language instruction that defines what entities or information to extract from documents. Results are stored as entities matching the schema defined in entity_schema.", examples=['Find all pizzas described in the text.'])
    context_template: str | None = Field(default=None, description="An optional Mustache template that prepends document context to the content sent for extraction. Supports variables like document.name, document.type, document.source, and nested metadata values (e.g., {{document.metadata.key_name}}).", examples=['Document: {{document.name}} {{document.metadata.key_foo}}'])
    entity_schema: dict[str, Any] | None = Field(default=None, description="A JSON schema (object type at root) that defines the structure of entities extracted by this instruction. For multiple items, use an array property. For single values, wrap in an object with a single key. All required fields must be listed in the schema's required array.", examples=[{'additionalProperties': False, 'properties': {'size': {'enum': ['small', 'medium', 'large'], 'type': 'string'}, 'crust': {'enum': ['thin', 'thick', 'stuffed'], 'type': 'string'}, 'sauce': {'enum': ['tomato', 'alfredo', 'pesto'], 'type': 'string'}, 'cheese': {'enum': ['mozzarella', 'cheddar', 'parmesan', 'vegan'], 'type': 'string'}, 'toppings': {'items': {'enum': ['pepperoni', 'mushrooms', 'onions', 'sausage', 'bacon', 'extra cheese', 'black olives', 'green peppers', 'pineapple', 'spinach'], 'type': 'string'}, 'type': 'array'}, 'extraInstructions': {'type': 'string'}}, 'required': ['size', 'crust', 'sauce', 'cheese'], 'title': 'Pizza', 'type': 'object'}])
    filter_: dict[str, Any] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="An optional metadata filter that restricts instruction application to documents matching the filter criteria. Supports operators: $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin, and can be combined with AND/OR logic.", examples=[{'toppings': {'$in': ['pizza', 'mushrooms']}}])
class PatchInstructionRequest(StrictModel):
    """Update an instruction's configuration, including its name, active status, scope, prompt, context template, entity schema, and metadata filters. Changes apply to documents created or updated after the patch is applied."""
    path: PatchInstructionRequestPath
    body: PatchInstructionRequestBody | None = None

# Operation: delete_instruction
class DeleteInstructionRequestPath(StrictModel):
    instruction_id: str = Field(default=..., description="The unique identifier of the instruction to delete, formatted as a UUID.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class DeleteInstructionRequest(StrictModel):
    """Permanently delete an instruction and all entities it generated. This operation cannot be undone."""
    path: DeleteInstructionRequestPath

# Operation: list_entities_by_instruction
class ListEntitiesByInstructionRequestPath(StrictModel):
    instruction_id: str = Field(default=..., description="The unique identifier (UUID) of the instruction whose extracted entities you want to retrieve.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class ListEntitiesByInstructionRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="The number of entities to return per page, between 1 and 100 items. Defaults to 10 if not specified.", ge=1, le=100)
class ListEntitiesByInstructionRequest(StrictModel):
    """Retrieve all entities that were extracted from a specific instruction. Results are paginated to allow efficient browsing of large entity sets."""
    path: ListEntitiesByInstructionRequestPath
    query: ListEntitiesByInstructionRequestQuery | None = None

# Operation: list_instruction_entity_extraction_logs
class ListInstructionEntityExtractionLogsRequestPath(StrictModel):
    instruction_id: str = Field(default=..., description="The UUID of the instruction for which to retrieve entity extraction logs.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class ListInstructionEntityExtractionLogsRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of results to return per page. Must be between 1 and 100 items. Defaults to 10 if not specified.", ge=1, le=100)
    document_ids: list[Annotated[str, Field(json_schema_extra={'format': 'uuid'})]] | None = Field(default=None, description="Optional list of document IDs to filter extraction logs. Only logs matching these document IDs will be included in results.")
    status: Literal["extracted", "not_found", "error"] | None = Field(default=None, description="Optional filter by extraction outcome status. Valid values are `extracted` (successful extraction), `not_found` (entity not found), or `error` (extraction failed).")
    created_after: str | None = Field(default=None, description="Optional ISO 8601 timestamp to include only logs created on or after this date and time.", json_schema_extra={'format': 'date-time'})
    created_before: str | None = Field(default=None, description="Optional ISO 8601 timestamp to include only logs created before this date and time.", json_schema_extra={'format': 'date-time'})
class ListInstructionEntityExtractionLogsRequest(StrictModel):
    """Retrieve entity extraction logs for a specific instruction, showing attempt-level results with both successful and unsuccessful outcomes. Results are sorted by creation date in descending order and paginated, with historical data available only from March 6, 2026 onwards."""
    path: ListInstructionEntityExtractionLogsRequestPath
    query: ListInstructionEntityExtractionLogsRequestQuery | None = None

# Operation: list_entities_by_document
class ListEntitiesByDocumentRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier (UUID) of the document from which to retrieve extracted entities.", json_schema_extra={'format': 'uuid'}, examples=['00000000-0000-0000-0000-000000000000'])
class ListEntitiesByDocumentRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of entities to return per page, between 1 and 100 items. Defaults to 10 if not specified.", ge=1, le=100)
class ListEntitiesByDocumentRequest(StrictModel):
    """Retrieve all entities extracted from a specific document. Returns a paginated list of entities identified during document processing."""
    path: ListEntitiesByDocumentRequestPath
    query: ListEntitiesByDocumentRequestQuery | None = None

# Operation: create_connection
class CreateConnectionRequestBodyPartitionStrategy(StrictModel):
    static: Literal["hi_res", "fast", "agentic_ocr"] | None = Field(default=None, validation_alias="static", serialization_alias="static", description="Processing mode for document extraction: 'hi_res' for high-resolution processing, 'fast' for quick processing, or 'agentic_ocr' for advanced OCR-based extraction.")
    audio: bool | None = Field(default=None, validation_alias="audio", serialization_alias="audio", description="Enable audio processing for documents that contain audio content.")
    video: Literal["audio_only", "video_only", "audio_video"] | None = Field(default=None, validation_alias="video", serialization_alias="video", description="Video processing mode: 'audio_only' to extract audio tracks, 'video_only' to process video frames, or 'audio_video' to process both.")
class CreateConnectionRequestBody(StrictModel):
    page_limit: int | None = Field(default=None, description="Maximum number of pages to process from each document. Omit or set to null for no limit.", examples=[None, 100])
    config: dict[str, Any] | None = Field(default=None, description="Source-specific configuration object containing connection details and credentials required by the data source type.", examples=[None])
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(default=None, description="Custom metadata to attach to documents processed through this connection. Keys must be strings; values can be strings, numbers, booleans, or lists of strings. Up to 1000 total values allowed (each array item counts separately). Reserved keys like 'document_id', 'document_type', 'document_source', 'document_name', 'document_uploaded_at', 'start_time', 'end_time', and 'chunk_content_type' are for internal use only.")
    workflow: Literal["parse", "index"] | None = Field(default=None, description="Processing workflow: 'parse' to extract and structure document content, or 'index' to prepare documents for search and retrieval.")
    connection: Annotated[PublicBackblazeConnection | PublicGcsConnection | PublicFreshdeskConnection | PublicIntercomConnection | PublicS3CompatibleConnection | PublicWebcrawlerConnection | PublicZendeskConnection, Field(discriminator="provider")] = Field(default=..., description="Connection configuration object specifying the data source type and authentication details.")
    partition_strategy: CreateConnectionRequestBodyPartitionStrategy | None = None
class CreateConnectionRequest(StrictModel):
    """Create a new connection for non-OAuth data sources such as S3-compatible storage, Freshdesk, or Zendesk. Configure the connection with source-specific settings and optional processing parameters."""
    body: CreateConnectionRequestBody

# Operation: list_connections
class ListConnectionsConnectionsGetRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of connections to return per page. Must be between 1 and 100 items; defaults to 10 if not specified.", ge=1, le=100)
    filter_: str | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="Filter connections by metadata using comparison operators ($eq, $ne, $gt, $gte, $lt, $lte, $in, $nin) combined with AND/OR logic. Returns only connections matching the filter criteria. Refer to the Metadata & Filters guide for syntax and examples.", examples=[{'department': {'$in': ['sales', 'marketing']}}])
class ListConnectionsConnectionsGetRequest(StrictModel):
    """Retrieve all connections sorted by creation date in descending order. Results are paginated with a maximum of 100 items per page; use the cursor parameter to fetch subsequent pages when available."""
    query: ListConnectionsConnectionsGetRequestQuery | None = None

# Operation: create_oauth_redirect_url
class CreateOauthRedirectUrlConnectionsOauthPostRequestBody(StrictModel):
    redirect_uri: str = Field(default=..., description="The URI where the user will be redirected after completing OAuth authentication. This must be a valid, accessible endpoint in your application.")
    source_type: Literal["backblaze", "confluence", "dropbox", "freshdesk", "onedrive", "google_drive", "gmail", "intercom", "notion", "salesforce", "sharepoint", "jira", "slack", "s3", "gcs", "hubspot", "webcrawler", "zendesk"] | None = Field(default=None, description="The connector type to initialize (e.g., google_drive, notion, hubspot). Defaults to google_drive if not specified. Choose from supported connectors like cloud storage (S3, GCS, Dropbox), productivity tools (Notion, Slack), CRM systems (Salesforce, HubSpot), and others.")
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(default=None, description="Custom key-value metadata to attach to synced documents. Keys must be strings; values can be strings, numbers, booleans, or lists of strings. Up to 1000 total values allowed (each array item counts separately). Reserved keys like document_id and document_source are managed internally.")
    mode: Literal["hi_res", "fast", "agentic_ocr"] | MediaModeParam | None = Field(default=None, description="Operational mode for the connector (specific behavior determined by connector type).")
    theme: Literal["light", "dark", "system"] | None = Field(default=None, description="Visual theme for the Ragie Web UI presented to the user. Choose 'light' for light mode, 'dark' for dark mode, or 'system' to match the user's system preference. Defaults to system.")
    page_limit: int | None = Field(default=None, description="Maximum number of pages the connection will sync before being automatically disabled. Must be at least 1 if specified. Set to null to remove any limit. In-progress documents may continue processing after the limit is reached.", ge=1, examples=[1000])
    config: dict[str, Any] | None = Field(default=None, description="Connector-specific configuration options provided as a JSON object. Structure varies by connector type.")
    authenticator_id: str | None = Field(default=None, description="UUID of the authenticator to use for this OAuth flow. Links the redirect URL to a specific authentication context.", json_schema_extra={'format': 'uuid'})
    workflow: Literal["parse", "index"] | None = Field(default=None, description="The workflow type for processing synced content. Choose 'parse' to extract and structure document content, or 'index' to prepare content for search and retrieval.")
class CreateOauthRedirectUrlConnectionsOauthPostRequest(StrictModel):
    """Generates an OAuth redirect URL for initializing an embedded connector, allowing users to authenticate with third-party services like Google Drive, Notion, Salesforce, and others."""
    body: CreateOauthRedirectUrlConnectionsOauthPostRequestBody

# Operation: update_connection_enabled_status
class SetConnectionEnabledConnectionsConnectionIdEnabledPutRequestPath(StrictModel):
    connection_id: str = Field(default=..., description="The unique identifier (UUID format) of the connection to modify.", json_schema_extra={'format': 'uuid'})
class SetConnectionEnabledConnectionsConnectionIdEnabledPutRequestBody(StrictModel):
    enabled: bool = Field(default=..., description="Boolean flag to enable (true) or disable (false) the connection.")
    reason: Literal["connection_over_total_page_limit", "authentication_failed"] | None = Field(default=None, description="Optional reason for disabling the connection. Valid values indicate specific failure conditions: 'connection_over_total_page_limit' when the connection exceeds page limits, or 'authentication_failed' when authentication credentials are invalid.")
class SetConnectionEnabledConnectionsConnectionIdEnabledPutRequest(StrictModel):
    """Enable or disable a connection to control whether it syncs data. Disabled connections will not perform synchronization operations."""
    path: SetConnectionEnabledConnectionsConnectionIdEnabledPutRequestPath
    body: SetConnectionEnabledConnectionsConnectionIdEnabledPutRequestBody

# Operation: get_connection
class GetConnectionConnectionsConnectionIdGetRequestPath(StrictModel):
    connection_id: str = Field(default=..., description="The unique identifier (UUID) of the connection to retrieve.", json_schema_extra={'format': 'uuid'})
class GetConnectionConnectionsConnectionIdGetRequest(StrictModel):
    """Retrieve a specific connection by its unique identifier. Returns the full connection details including configuration and metadata."""
    path: GetConnectionConnectionsConnectionIdGetRequestPath

# Operation: update_connection
class UpdateConnectionConnectionsConnectionIdPutRequestPath(StrictModel):
    connection_id: str = Field(default=..., description="The unique identifier (UUID) of the connection to update.", json_schema_extra={'format': 'uuid'})
class UpdateConnectionConnectionsConnectionIdPutRequestBody(StrictModel):
    partition_strategy: Literal["hi_res", "fast", "agentic_ocr"] | MediaModeParam = Field(default=..., description="The strategy for partitioning data during sync operations.")
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(default=None, description="Custom metadata as key-value pairs where keys are strings and values are strings, numbers, booleans, or lists of strings. Up to 1000 total values allowed (each array item counts separately). Reserved keys like `document_id`, `document_type`, `document_source`, `document_name`, `document_uploaded_at`, `start_time`, `end_time`, and `chunk_content_type` are for internal use only.")
    page_limit: int | None = Field(default=None, description="Maximum number of pages to sync for this connection; the connection will be disabled once this limit is reached. Set to `null` to remove any existing limit. Must be at least 1 if specified.", ge=1, examples=[1000])
class UpdateConnectionConnectionsConnectionIdPutRequest(StrictModel):
    """Update a connection's metadata or partition strategy. Changes take effect after the next sync operation."""
    path: UpdateConnectionConnectionsConnectionIdPutRequestPath
    body: UpdateConnectionConnectionsConnectionIdPutRequestBody

# Operation: get_connection_stats
class GetConnectionStatsConnectionsConnectionIdStatsGetRequestPath(StrictModel):
    connection_id: str = Field(default=..., description="The unique identifier (UUID) of the connection to retrieve statistics for.", json_schema_extra={'format': 'uuid'})
class GetConnectionStatsConnectionsConnectionIdStatsGetRequest(StrictModel):
    """Retrieves aggregated statistics for a specific connection, including total documents, active documents, and total active pages."""
    path: GetConnectionStatsConnectionsConnectionIdStatsGetRequestPath

# Operation: update_connection_page_limit
class SetConnectionLimitsConnectionsConnectionIdLimitPutRequestPath(StrictModel):
    connection_id: str = Field(default=..., description="The unique identifier of the connection to configure limits for.", json_schema_extra={'format': 'uuid'})
class SetConnectionLimitsConnectionsConnectionIdLimitPutRequestBody(StrictModel):
    page_limit: int | None = Field(default=None, description="The maximum number of pages this connection will synchronize before being disabled. Must be at least 1 if specified. Set to null to remove any existing limit.", ge=1, examples=[1000])
class SetConnectionLimitsConnectionsConnectionIdLimitPutRequest(StrictModel):
    """Set or remove page synchronization limits for a connection. When a limit is set, the connection automatically disables after syncing the specified number of pages, though some in-process documents may continue processing."""
    path: SetConnectionLimitsConnectionsConnectionIdLimitPutRequestPath
    body: SetConnectionLimitsConnectionsConnectionIdLimitPutRequestBody | None = None

# Operation: delete_connection
class DeleteConnectionConnectionsConnectionIdDeletePostRequestPath(StrictModel):
    connection_id: str = Field(default=..., description="The unique identifier (UUID) of the connection to delete.", json_schema_extra={'format': 'uuid'})
class DeleteConnectionConnectionsConnectionIdDeletePostRequestBody(StrictModel):
    keep_files: bool = Field(default=..., description="Whether to retain files associated with this connection. If true, files are preserved but disassociated; if false, all files are deleted with the connection.")
class DeleteConnectionConnectionsConnectionIdDeletePostRequest(StrictModel):
    """Schedules a connection for deletion. Optionally preserve associated files (they will be disassociated from the connection) or delete them along with the connection. Deletion is asynchronous and files may remain visible briefly after the request completes."""
    path: DeleteConnectionConnectionsConnectionIdDeletePostRequestPath
    body: DeleteConnectionConnectionsConnectionIdDeletePostRequestBody

# Operation: trigger_connection_sync
class SyncConnectionRequestPath(StrictModel):
    connection_id: str = Field(default=..., description="The unique identifier of the connection to sync, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class SyncConnectionRequest(StrictModel):
    """Immediately schedules a connector to begin syncing data. This operation queues the sync to run as soon as possible."""
    path: SyncConnectionRequestPath

# Operation: list_webhook_endpoints
class ListWebhookEndpointsRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of webhook endpoints to return per page. Must be between 1 and 100 items. Defaults to 10 if not specified.", ge=1, le=100)
class ListWebhookEndpointsRequest(StrictModel):
    """Retrieve all webhook endpoints sorted by creation date in descending order. Results are paginated with a maximum of 100 items per page, and a cursor is provided when additional endpoints are available."""
    query: ListWebhookEndpointsRequestQuery | None = None

# Operation: get_webhook_endpoint
class GetWebhookEndpointRequestPath(StrictModel):
    endpoint_id: str = Field(default=..., description="The unique identifier (UUID) of the webhook endpoint to retrieve.", json_schema_extra={'format': 'uuid'})
class GetWebhookEndpointRequest(StrictModel):
    """Retrieve a specific webhook endpoint by its unique identifier. Use this to fetch configuration and status details for a registered webhook."""
    path: GetWebhookEndpointRequestPath

# Operation: update_webhook_endpoint
class UpdateWebhookEndpointRequestPath(StrictModel):
    endpoint_id: str = Field(default=..., description="The unique identifier of the webhook endpoint to update, formatted as a UUID.", json_schema_extra={'format': 'uuid'})
class UpdateWebhookEndpointRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A new display name for the webhook endpoint.")
    url: str | None = Field(default=None, description="A new delivery URL for the webhook endpoint. Must be a valid URI between 1 and 2083 characters.", min_length=1, max_length=2083, json_schema_extra={'format': 'uri'})
    active: bool | None = Field(default=None, description="Whether the webhook endpoint is active and should receive event deliveries. Set to false to temporarily disable delivery without deleting the endpoint.")
    partition_pattern: str | None = Field(default=None, description="A pattern to partition webhook events for this endpoint.")
class UpdateWebhookEndpointRequest(StrictModel):
    """Update a webhook endpoint's configuration including its name, URL, or active status. Use this operation to rotate endpoints, change delivery URLs, or temporarily disable webhook delivery without deleting the endpoint."""
    path: UpdateWebhookEndpointRequestPath
    body: UpdateWebhookEndpointRequestBody | None = None

# Operation: list_partitions
class ListPartitionsPartitionsGetRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of partitions to return per page. Must be between 1 and 100 items; defaults to 10 if not specified.", ge=1, le=100)
class ListPartitionsPartitionsGetRequest(StrictModel):
    """Retrieve all partitions sorted alphabetically in ascending order. Results are paginated with a maximum of 100 items per page; use the cursor parameter to fetch subsequent pages when available."""
    query: ListPartitionsPartitionsGetRequestQuery | None = None

# Operation: create_partition
class CreatePartitionPartitionsPostRequestBody(StrictModel):
    name: str = Field(default=..., description="Unique identifier for the partition. Must be lowercase alphanumeric and may only contain underscores and hyphens.")
    description: str | None = Field(default=None, description="Human-readable description of the partition's purpose. Automatic description generation can be enabled in the web dashboard.")
    pages_hosted_limit_max: int | None = Field(default=None, description="Maximum number of pages allowed for hosted documents in this partition. Must be at least 1.", ge=1, examples=[1000])
    pages_processed_limit_max: int | None = Field(default=None, description="Maximum number of pages allowed for processed documents in this partition. Must be at least 1.", ge=1, examples=[1000])
    audio_processed_limit_max: int | None = Field(default=None, description="Maximum duration in minutes for audio processing in this partition. Must be at least 1.", ge=1, examples=[60])
    video_processed_limit_max: int | None = Field(default=None, description="Maximum duration in minutes for video processing in this partition. Must be at least 1.", ge=1, examples=[60])
    media_streamed_limit_max: int | None = Field(default=None, description="Maximum size in megabytes for media streamed from this partition. Must be at least 1.", ge=1, examples=[1024])
    media_hosted_limit_max: int | None = Field(default=None, description="Maximum size in megabytes for media hosted in this partition. Must be at least 1.", ge=1, examples=[1024])
    metadata_schema: dict[str, str | int | bool | list[str] | dict[str, Any]] | None = Field(default=None, description="JSON Schema defining optional metadata fields for documents in this partition. Include detailed field descriptions to assist LLMs in generating dynamic filters.")
class CreatePartitionPartitionsPostRequest(StrictModel):
    """Create a new partition to scope documents, connections, and instructions. Partition names must be lowercase alphanumeric with only underscores and hyphens allowed. Optional resource limits can be defined at creation time."""
    body: CreatePartitionPartitionsPostRequestBody

# Operation: get_partition
class GetPartitionPartitionsPartitionIdGetRequestPath(StrictModel):
    partition_id: str = Field(default=..., description="The unique identifier of the partition to retrieve.")
class GetPartitionPartitionsPartitionIdGetRequest(StrictModel):
    """Retrieve detailed information about a specific partition, including its usage metrics (document and page counts) and configured limits."""
    path: GetPartitionPartitionsPartitionIdGetRequestPath

# Operation: update_partition
class UpdatePartitionPartitionsPartitionIdPatchRequestPath(StrictModel):
    partition_id: str = Field(default=..., description="The unique identifier of the partition to update.")
class UpdatePartitionPartitionsPartitionIdPatchRequestBody(StrictModel):
    context_aware: bool | None = Field(default=None, description="Enable context-aware descriptions that provide additional semantic context for the partition to improve LLM understanding and filter generation.")
    description: str | None = Field(default=None, description="A human-readable description of the partition's purpose and contents.")
    metadata_schema: dict[str, str | int | bool | list[str] | dict[str, Any]] | None = Field(default=None, description="A JSON Schema definition describing the structure and types of metadata fields available in documents within this partition. Include detailed field descriptions to assist LLMs in generating accurate dynamic filters.")
class UpdatePartitionPartitionsPartitionIdPatchRequest(StrictModel):
    """Update a partition's configuration, including its description and metadata schema. The metadata schema defines an optional subset of document metadata as JSON Schema, useful for LLM-based filter generation."""
    path: UpdatePartitionPartitionsPartitionIdPatchRequestPath
    body: UpdatePartitionPartitionsPartitionIdPatchRequestBody | None = None

# Operation: delete_partition
class DeletePartitionPartitionsPartitionIdDeleteRequestPath(StrictModel):
    partition_id: str = Field(default=..., description="The unique identifier of the partition to delete.")
class DeletePartitionPartitionsPartitionIdDeleteRequestQuery(StrictModel):
    async_: bool | None = Field(default=None, validation_alias="async", serialization_alias="async", description="When set to true, the partition deletion is performed asynchronously, allowing the request to return immediately while the deletion completes in the background. Defaults to false for synchronous deletion.", examples=['true', 'false'])
class DeletePartitionPartitionsPartitionIdDeleteRequest(StrictModel):
    """Permanently deletes a partition and all associated data, including connections, documents, and partition-specific instructions. This operation cannot be undone."""
    path: DeletePartitionPartitionsPartitionIdDeleteRequestPath
    query: DeletePartitionPartitionsPartitionIdDeleteRequestQuery | None = None

# Operation: update_partition_limits
class SetPartitionLimitsPartitionsPartitionIdLimitsPutRequestPath(StrictModel):
    partition_id: str = Field(default=..., description="The unique identifier of the partition to configure limits for.")
class SetPartitionLimitsPartitionsPartitionIdLimitsPutRequestBody(StrictModel):
    pages_hosted_limit_max: int | None = Field(default=None, description="Maximum number of pages allowed for hosted documents in the partition. Must be at least 1 page.", ge=1, examples=[1000])
    pages_processed_limit_max: int | None = Field(default=None, description="Maximum number of pages allowed for processed documents in the partition. Must be at least 1 page.", ge=1, examples=[1000])
    video_processed_limit_max: int | None = Field(default=None, description="Maximum duration in minutes for video processing in the partition. Must be at least 1 minute.", ge=1, examples=[3600])
    audio_processed_limit_max: int | None = Field(default=None, description="Maximum duration in minutes for audio processing in the partition. Must be at least 1 minute.", ge=1, examples=[3600])
    media_streamed_limit_max: int | None = Field(default=None, description="Maximum size in megabytes for media streamed from the partition. Must be at least 1 MB.", ge=1, examples=[1024])
    media_hosted_limit_max: int | None = Field(default=None, description="Maximum size in megabytes for media hosted in the partition. Must be at least 1 MB.", ge=1, examples=[1024])
class SetPartitionLimitsPartitionsPartitionIdLimitsPutRequest(StrictModel):
    """Configure resource limits for a partition, including document hosting/processing capacity and media streaming/hosting quotas. When a limit is reached, the partition will be automatically disabled. Set any limit to null to remove it."""
    path: SetPartitionLimitsPartitionsPartitionIdLimitsPutRequestPath
    body: SetPartitionLimitsPartitionsPartitionIdLimitsPutRequestBody | None = None

# Operation: list_authenticators
class ListAuthenticatorsRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of authenticators to return per page. Must be between 1 and 100 items; defaults to 10 if not specified.", ge=1, le=100)
class ListAuthenticatorsRequest(StrictModel):
    """Retrieve a paginated list of all authenticators sorted by creation date in descending order. Use the cursor parameter to navigate through pages when more results are available."""
    query: ListAuthenticatorsRequestQuery | None = None

# Operation: create_authenticator
class CreateAuthenticatorRequestBody(StrictModel):
    provider: Literal["atlassian", "dropbox", "hubspot", "microsoft", "salesforce", "slack"] = Field(default=..., description="The provider service to authenticate with. Must be one of: Atlassian, Dropbox, HubSpot, Microsoft, Salesforce, or Slack.")
    name: str = Field(default=..., description="A unique identifier for this authenticator configuration. This name is used to reference and distinguish the authenticator from others. Names must be globally unique within your account.")
    client_id: str = Field(default=..., description="The OAuth 2.0 client ID issued by the provider's application registration or developer console.")
    client_secret: str = Field(default=..., description="The OAuth 2.0 client secret issued by the provider's application registration or developer console. Keep this value secure.")
    domain: str | None = Field(default=None, description="The domain or workspace identifier for the provider, if applicable. Required for certain providers that use domain-based authentication.")
    project_number: str | None = Field(default=None, description="The project number identifier for the provider, if applicable. Required for certain providers that use project-based authentication.")
class CreateAuthenticatorRequest(StrictModel):
    """Create white-labeled connector credentials for integrating with third-party services. This establishes authentication configuration that enables secure API access to supported providers."""
    body: CreateAuthenticatorRequestBody

# Operation: create_authenticator_connection
class CreateAuthenticatorConnectionRequestPath(StrictModel):
    authenticator_id: str = Field(default=..., description="The unique identifier (UUID) of the authenticator to create a connection for.", json_schema_extra={'format': 'uuid'})
class CreateAuthenticatorConnectionRequestBodyPartitionStrategy(StrictModel):
    static: Literal["hi_res", "fast", "agentic_ocr"] | None = Field(default=None, validation_alias="static", serialization_alias="static", description="OCR processing mode for static documents: 'hi_res' for high-resolution processing, 'fast' for quick processing, or 'agentic_ocr' for intelligent OCR.")
    audio: bool | None = Field(default=None, validation_alias="audio", serialization_alias="audio", description="Enable audio extraction and processing from documents.")
    video: Literal["audio_only", "video_only", "audio_video"] | None = Field(default=None, validation_alias="video", serialization_alias="video", description="Video processing mode: 'audio_only' to extract audio, 'video_only' to process video frames, or 'audio_video' to process both.")
class CreateAuthenticatorConnectionRequestBody(StrictModel):
    page_limit: int | None = Field(default=None, description="Maximum number of pages to process from the source. Omit or set to null for no limit.", examples=[None, 100])
    config: dict[str, Any] | None = Field(default=None, description="Provider-specific configuration object. Structure depends on the authenticator type.", examples=[None])
    metadata: dict[str, str | int | float | bool | list[str]] | None = Field(default=None, description="Custom metadata key-value pairs for document classification and filtering. Keys must be strings; values can be strings, numbers, booleans, or lists of strings. Up to 1000 total values allowed (each array item counts separately). Reserved keys: document_id, document_type, document_source, document_name, document_uploaded_at, start_time, end_time, chunk_content_type.")
    workflow: Literal["parse", "index"] | None = Field(default=None, description="Processing workflow: 'parse' to extract and structure content, or 'index' to prepare for search and retrieval.")
    connection: Annotated[AuthenticatorConfluenceConnection | AuthenticatorDropboxConnection | AuthenticatorGoogleDriveConnection | AuthenticatorGmailConnection | AuthenticatorHubspotConnection | AuthenticatorJiraConnection | AuthenticatorNotionConnection | AuthenticatorOnedriveConnection | AuthenticatorSalesforceConnection | AuthenticatorSharepointConnection | AuthenticatorSlackConnection, Field(discriminator="provider")] = Field(default=..., description="Connection credentials object. Structure and required fields depend on the authenticator provider type.")
    partition_strategy: CreateAuthenticatorConnectionRequestBodyPartitionStrategy | None = None
class CreateAuthenticatorConnectionRequest(StrictModel):
    """Establish a connector for a specified authenticator with provider-specific credentials (e.g., Google Drive refresh token). Configure document processing options like OCR mode, media handling, and metadata."""
    path: CreateAuthenticatorConnectionRequestPath
    body: CreateAuthenticatorConnectionRequestBody

# Operation: delete_authenticator
class DeleteAuthenticatorConnectionRequestPath(StrictModel):
    authenticator_id: str = Field(default=..., description="The unique identifier (UUID) of the authenticator to delete.", json_schema_extra={'format': 'uuid'})
class DeleteAuthenticatorConnectionRequest(StrictModel):
    """Delete an authenticator connection method. All connections created by this authenticator must be deleted before this operation can succeed."""
    path: DeleteAuthenticatorConnectionRequestPath

# Operation: create_response
class CreateResponseResponsesPostRequestBodyReasoning(StrictModel):
    effort: Literal["low", "medium", "high"] = Field(default=..., validation_alias="effort", serialization_alias="effort", description="The computational effort level for generating the response. Choose low for quick responses, medium for balanced quality and speed, or high for more thorough analysis.")
class CreateResponseResponsesPostRequestBody(StrictModel):
    input_: str = Field(default=..., validation_alias="input", serialization_alias="input", description="The query or question to generate a response for. This text is processed by the LLM agent to produce relevant answers.")
    instructions: str | None = Field(default=None, description="Custom instructions to inject into the agent's prompt, particularly during search and retrieval steps. Use this to guide the agent's behavior and response style.")
    tools: list[Tool] | None = Field(default=None, description="Array of tools available to the agent for generating responses. Currently supports the retrieve tool for document search. Each tool can specify which partitions to search; if omitted, the default partition is used. Defaults to retrieve tool with the default partition.")
    model: Literal["deep-search"] | None = Field(default=None, description="The LLM model powering the agent. Currently only deep-search is supported.")
    stream: bool | None = Field(default=None, description="Whether to stream the response as it's generated (true) or wait for the complete response (false). Streaming allows real-time consumption of results.")
    reasoning: CreateResponseResponsesPostRequestBodyReasoning
class CreateResponseResponsesPostRequest(StrictModel):
    """Generate an LLM-powered response to a query using the deep-search model. Responses can be streamed in real-time or returned synchronously, with optional access to document retrieval tools across specified partitions."""
    body: CreateResponseResponsesPostRequestBody

# Operation: get_response
class GetResponseResponsesResponseIdGetRequestPath(StrictModel):
    response_id: str = Field(default=..., description="The unique identifier (UUID) of the response to retrieve.", json_schema_extra={'format': 'uuid'})
class GetResponseResponsesResponseIdGetRequest(StrictModel):
    """Retrieve a response by its unique identifier. Returns the response data along with its current status: `in_progress` for ongoing processing, `completed` for finished responses, or `failed` for responses that encountered an error."""
    path: GetResponseResponsesResponseIdGetRequestPath

# Operation: list_document_elements
class ListElementsRequestPath(StrictModel):
    document_id: str = Field(default=..., description="The unique identifier (UUID) of the document containing the elements to retrieve.", json_schema_extra={'format': 'uuid'})
class ListElementsRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of elements to return per page. Must be between 1 and 100 items (defaults to 10 if not specified).", ge=1, le=100)
    type_: list[Literal["Caption", "Title", "Text", "UncategorizedText", "NarrativeText", "Image", "FigureCaption", "TableCaption", "ListItem", "Address", "EmailAddress", "PageBreak", "Formula", "Table", "Header", "Footer", "Json", "AudioTranscriptionSegment", "VideoSegment", "SubHeader", "SectionHeader", "Author", "CalendarDate", "Quote", "Comment", "UnorderedList", "OrderedList", "DefinitionList", "Figure", "Stamp", "Logo", "Watermark", "Barcode", "QrCode", "Signature", "KeyValue", "FormField", "Code", "Bibliography", "TableOfContents", "Footnote", "Time", "Button", "Video"]] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter results by element type(s). Accepts an array of type values to match against.")
    index_start: int | None = Field(default=None, description="Filter results to include only elements at or after this index position (inclusive).")
    index_end: int | None = Field(default=None, description="Filter results to include only elements at or before this index position (inclusive).")
class ListElementsRequest(StrictModel):
    """Retrieve paginated elements from a document, sorted by index in ascending order. Results are limited to 100 items per page, with cursor-based pagination for accessing subsequent pages."""
    path: ListElementsRequestPath
    query: ListElementsRequestQuery | None = None

# Operation: get_element
class GetElementRequestPath(StrictModel):
    element_id: str = Field(default=..., description="The unique identifier (UUID) of the element to retrieve.", json_schema_extra={'format': 'uuid'})
class GetElementRequest(StrictModel):
    """Retrieves a specific element from a document by its unique identifier. Use this to fetch detailed information about an individual element."""
    path: GetElementRequestPath

# ============================================================================
# Component Models
# ============================================================================

class AccessTokenCredentials(PermissiveModel):
    access_token: str

class AuthenticatorNotionConnection(PermissiveModel):
    provider: Literal["notion"]
    workspace_id: str
    workspace_name: str
    user_email: str = Field(..., description="The email of the Notion account this is for")
    credentials: AccessTokenCredentials

class BackblazeCredentials(PermissiveModel):
    key_id: str
    application_key: str
    region: str
    endpoint: str

class BucketData(PermissiveModel):
    bucket: str
    prefix: str | None = None
    import_file_metadata: bool | None = False

class Caption(PermissiveModel):
    content: str = Field(..., description="The text content")

class ConfluenceData(PermissiveModel):
    resource_id: str
    space_id: int
    space_key: str
    space_name: str

class Connection(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'uuid'})
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    metadata: dict[str, str | int | float | bool | list[str]]
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    name: str
    source: str | list[str] | dict[str, Any] | None = Field(...)
    enabled: bool
    disabled_by_system_reason: Literal["connection_over_total_page_limit", "authentication_failed"] | None = Field(...)
    last_synced_at: str | None = Field(None, json_schema_extra={'format': 'date-time'})
    syncing: bool | None = None
    partition: str | None = None
    page_limit: int | None = Field(...)
    disabled_by_system: bool

class CreateDocumentBodyMode(PermissiveModel):
    """Also accepts scalar shorthand."""
    static: Literal["hi_res", "fast"] | None = None
    audio: bool | None = None
    video: Literal["audio_only", "video_only", "audio_video"] | None = None

class Document(PermissiveModel):
    status: str
    id_: str = Field(..., validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'uuid'})
    created_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    updated_at: str = Field(..., json_schema_extra={'format': 'date-time'})
    name: str
    metadata: dict[str, str | int | float | bool | list[str]]
    partition: str
    chunk_count: int | None = None
    external_id: str | None = None
    page_count: float | None = None

class FolderData(PermissiveModel):
    folder_id: str
    folder_name: str

class FormOption(PermissiveModel):
    label: str = Field(..., description="The text label visible next to the checkbox/radio.")

class FreshdeskCredentials(PermissiveModel):
    domain: str
    api_key: str

class FreshdeskData(PermissiveModel):
    tickets: bool
    articles: bool

class GmailData(PermissiveModel):
    label: str | None = None

class GoogleFolderData(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str
    mime_type: str

class HubspotData(PermissiveModel):
    companies: bool
    contacts: bool
    contact_notes: bool
    deals: bool
    deal_notes: bool
    emails: bool
    tasks: bool

class IntercomCredentials(PermissiveModel):
    access_token: str
    app_name: str
    user_email: str = Field(..., description="The email of the Intercom account this is for")

class IntercomData(PermissiveModel):
    articles_help_center: bool | None = False
    admins: bool | None = False
    contacts: bool | None = False
    conversations: bool | None = False
    conversation_attachments: bool | None = False
    conversation_notes: bool | None = False
    tickets: bool | None = False
    ticket_attachments: bool | None = False
    ticket_comments: bool | None = False
    ticket_notes: bool | None = False
    filter_user_id: str | None = None

class MediaModeParam(PermissiveModel):
    static: Literal["hi_res", "fast", "agentic_ocr"] | None = None
    audio: bool | None = None
    video: Literal["audio_only", "video_only", "audio_video"] | None = None

class OAuthRefreshTokenCredentials(PermissiveModel):
    refresh_token: str

class AuthenticatorConfluenceConnection(PermissiveModel):
    provider: Literal["confluence"]
    data: list[ConfluenceData]
    credentials: OAuthRefreshTokenCredentials

class AuthenticatorDropboxConnection(PermissiveModel):
    provider: Literal["dropbox"]
    data: FolderData
    email: str = Field(..., description="The email of the Dropbox account this is for")
    credentials: OAuthRefreshTokenCredentials

class AuthenticatorGmailConnection(PermissiveModel):
    provider: Literal["gmail"]
    data: GmailData
    email: str = Field(..., description="The email of the Google Drive account this is for")
    credentials: OAuthRefreshTokenCredentials

class AuthenticatorGoogleDriveConnection(PermissiveModel):
    provider: Literal["google_drive"]
    data: list[GoogleFolderData]
    email: str = Field(..., description="The email of the Google Drive account this is for")
    credentials: OAuthRefreshTokenCredentials

class AuthenticatorHubspotConnection(PermissiveModel):
    provider: Literal["hubspot"]
    data: HubspotData
    hub_id: str
    hub_domain: str
    credentials: OAuthRefreshTokenCredentials

class AuthenticatorJiraConnection(PermissiveModel):
    provider: Literal["jira"]
    credentials: OAuthRefreshTokenCredentials

class AuthenticatorSalesforceConnection(PermissiveModel):
    provider: Literal["salesforce"]
    user_email: str = Field(..., description="The email of the Salesforce account this is for")
    url: str = Field(..., description="The url of your Salesforce instance, where you go to login.")
    credentials: OAuthRefreshTokenCredentials

class OnedriveData(PermissiveModel):
    drive_id: str
    folder_id: str
    folder_name: str

class AuthenticatorOnedriveConnection(PermissiveModel):
    provider: Literal["onedrive"]
    data: OnedriveData
    user_email: str = Field(..., description="The email of the Onedrive account this is for")
    credentials: OAuthRefreshTokenCredentials

class PartitionLimits(PermissiveModel):
    pages_processed_limit_monthly: int | None = Field(None, description="Monthly limit, in pages, for processed documents in the partition.", ge=0)
    pages_hosted_limit_monthly: int | None = Field(None, description="Monthly limit of hosted pages added in the current month in the partition.", ge=0)
    pages_processed_limit_max: int | None = Field(None, description="Maximum limit, in pages, for processed documents in the partition.", ge=0)
    pages_hosted_limit_max: int | None = Field(None, description="Maximum limit, in pages, for hosted documents in the partition.", ge=0)
    video_processed_limit_monthly: int | None = Field(None, description="Monthly limit, in minutes, for video processing in the partition.", ge=0)
    video_processed_limit_max: int | None = Field(None, description="Maximum limit, in minutes, for video processing in the partition.", ge=0)
    audio_processed_limit_monthly: int | None = Field(None, description="Monthly limit, in minutes, for audio processing in the partition.", ge=0)
    audio_processed_limit_max: int | None = Field(None, description="Maximum limit, in minutes, for audio processing in the partition.", ge=0)
    media_streamed_limit_monthly: int | None = Field(None, description="Monthly limit, in MBs, for media streamed from the partition.", ge=0)
    media_streamed_limit_max: int | None = Field(None, description="Maximum limit, in MBs, for media streamed from the partition.", ge=0)
    media_hosted_limit_monthly: int | None = Field(None, description="Monthly limit, in MBs, for media hosted in the partition.", ge=0)
    media_hosted_limit_max: int | None = Field(None, description="Maximum limit, in MBs, for media hosted in the partition.", ge=0)

class Partition(PermissiveModel):
    name: str
    is_default: bool
    limit_exceeded_at: str | None = Field(None, description="Timestamp when the partition exceeded its limits, if applicable.", json_schema_extra={'format': 'date-time'})
    description: str | None = Field(...)
    context_aware: bool
    metadata_schema: dict[str, str | int | bool | list[str] | dict[str, Any]] | None = Field(...)
    limits: PartitionLimits

class PublicBackblazeConnection(PermissiveModel):
    provider: Literal["backblaze"]
    data: BucketData
    credentials: BackblazeCredentials

class PublicFreshdeskConnection(PermissiveModel):
    provider: Literal["freshdesk"]
    data: FreshdeskData
    user_email: str = Field(..., description="The email the API key is associated with")
    credentials: FreshdeskCredentials

class PublicGcsConnection(PermissiveModel):
    provider: Literal["gcs"]
    data: BucketData
    credentials: dict[str, Any]

class PublicIntercomConnection(PermissiveModel):
    provider: Literal["intercom"]
    data: IntercomData
    credentials: IntercomCredentials

class S3CompatibleCredentials(PermissiveModel):
    access_key_id: str
    secret_access_key: str
    region: str
    endpoint: str | None = None

class PublicS3CompatibleConnection(PermissiveModel):
    provider: Literal["s3"]
    data: BucketData
    credentials: S3CompatibleCredentials

class Search(PermissiveModel):
    search_requests: list[str]

class SharepointDriveData(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str

class SharepointFileData(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str
    path: str
    type_: Literal["file", "folder"] = Field(..., validation_alias="type", serialization_alias="type")
    drive_id: str | None = Field(...)

class SharepointSiteData(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str
    display_name: str

class SharepointData(PermissiveModel):
    site: SharepointSiteData
    drive: SharepointDriveData | None = Field(...)
    files: list[SharepointFileData]

class AuthenticatorSharepointConnection(PermissiveModel):
    provider: Literal["sharepoint"]
    data: SharepointData
    user_email: str = Field(..., description="The email of the Sharepoint account this is for")
    credentials: OAuthRefreshTokenCredentials

class SlackData(PermissiveModel):
    channel_id: str
    channel_name: str

class AuthenticatorSlackConnection(PermissiveModel):
    provider: Literal["slack"]
    data: SlackData
    user_email: str = Field(..., description="The email of the Slack account this is for")
    credentials: AccessTokenCredentials

class Tool(PermissiveModel):
    type_: Literal["retrieve"] = Field(..., validation_alias="type", serialization_alias="type")
    partitions: list[str]

class UncategorizedText(PermissiveModel):
    content: str = Field(..., description="The text content")

class UpdateDocumentFileBodyMode(PermissiveModel):
    """Also accepts scalar shorthand."""
    static: Literal["hi_res", "fast"] | None = None
    audio: bool | None = None
    video: Literal["audio_only", "video_only", "audio_video"] | None = None

class VideoSegment(PermissiveModel):
    content: str | None = None

class WebcrawlerData(PermissiveModel):
    url: str
    restrict_domain: bool | None = True
    max_depth: int | None = None
    max_pages: int | None = None

class PublicWebcrawlerConnection(PermissiveModel):
    provider: Literal["webcrawler"]
    data: WebcrawlerData
    credentials: dict[str, Any] | None = {}

class WordModality(PermissiveModel):
    word: str
    probability: float
    start: float
    end: float

class AudioTranscriptionSegment(PermissiveModel):
    content: str | None = None
    modality_data: list[WordModality] = Field(..., description="A list of information per word that shows the word, start time, and end time")

class ZendeskCredentials(PermissiveModel):
    domain: str
    email: str
    api_token: str

class ZendeskData(PermissiveModel):
    articles: bool

class PublicZendeskConnection(PermissiveModel):
    provider: Literal["zendesk"]
    data: ZendeskData
    credentials: ZendeskCredentials

class Address(PermissiveModel):
    type_: Literal["Address"] | None = Field('Address', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class Author(PermissiveModel):
    type_: Literal["Author"] | None = Field('Author', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class Barcode(PermissiveModel):
    type_: Literal["Barcode"] | None = Field('Barcode', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The nearby text content of the barcode")

class Bibliography(PermissiveModel):
    type_: Literal["Bibliography"] | None = Field('Bibliography', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content of the bibliography.")

class Button(PermissiveModel):
    type_: Literal["Button"] | None = Field('Button', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content inside the button")

class CalendarDate(PermissiveModel):
    type_: Literal["CalendarDate"] | None = Field('CalendarDate', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class Code(PermissiveModel):
    type_: Literal["Code"] | None = Field('Code', validation_alias="type", serialization_alias="type")
    content: str | None = Field('', description="The content of the code")
    language: str | None = Field('', description="The language the code is written in")

class Comment(PermissiveModel):
    type_: Literal["Comment"] | None = Field('Comment', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class DefinitionList(PermissiveModel):
    type_: Literal["DefinitionList"] | None = Field('DefinitionList', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content of the list and each item.")

class EmailAddress(PermissiveModel):
    type_: Literal["EmailAddress"] | None = Field('EmailAddress', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class Figure(PermissiveModel):
    type_: Literal["Figure"] | None = Field('Figure', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text visible inside the visual (OCR)")
    description: str = Field(..., description="A detailed description of what the visual depicts.")
    base64_data: str | None = None

class FigureCaption(PermissiveModel):
    type_: Literal["FigureCaption"] | None = Field('FigureCaption', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class Footer(PermissiveModel):
    type_: Literal["Footer"] | None = Field('Footer', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class Footnote(PermissiveModel):
    type_: Literal["Footnote"] | None = Field('Footnote', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content inside the footnote")

class FormField(PermissiveModel):
    type_: Literal["FormField"] | None = Field('FormField', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content of the form field, including both the label and the value")
    input_type: Literal["text", "textarea", "checkbox", "radio", "checkbox-group", "radio-group", "date", "time", "date-time"] = Field(..., description="Type of input.")
    label: str = Field(..., description="The main question/label for the field.")
    value: str | None = Field(None, description="The filled text. For single checkbox: 'true'/'false'.")
    options: list[FormOption] | None = Field(None, description="List of available options.")
    selected_values: list[str] | None = Field(None, description="The 'label' of the selected option(s).")
    help_text: str | None = Field(None, description="The help text for the form field.")

class Formula(PermissiveModel):
    type_: Literal["Formula"] | None = Field('Formula', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The formula as plain text.")
    latex: str | None = Field(None, description="The LaTeX representation of the formula.")

class Header(PermissiveModel):
    type_: Literal["Header"] | None = Field('Header', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class Image(PermissiveModel):
    type_: Literal["Image"] | None = Field('Image', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text visible inside the visual (OCR)")
    description: str = Field(..., description="A detailed description of what the visual depicts.")

class Json(PermissiveModel):
    type_: Literal["Json"] | None = Field('Json', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class KeyValue(PermissiveModel):
    type_: Literal["KeyValue"] | None = Field('KeyValue', validation_alias="type", serialization_alias="type")
    key: str = Field(..., description="The label/attribute name (e.g. 'Date', 'Invoice #').")
    value: str = Field(..., description="The static text value found.")

class ListItem(PermissiveModel):
    type_: Literal["ListItem"] | None = Field('ListItem', validation_alias="type", serialization_alias="type")
    content: str

class Logo(PermissiveModel):
    type_: Literal["Logo"] | None = Field('Logo', validation_alias="type", serialization_alias="type")
    content: str | None = Field('', description="The text visible inside the logo (OCR)")
    description: str = Field(..., description="A detailed description of the logo")
    base64_data: str | None = None

class NarrativeText(PermissiveModel):
    type_: Literal["NarrativeText"] | None = Field('NarrativeText', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class OrderedList(PermissiveModel):
    type_: Literal["OrderedList"] | None = Field('OrderedList', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content of the list and each list item.")

class PageBreak(PermissiveModel):
    type_: Literal["PageBreak"] | None = Field('PageBreak', validation_alias="type", serialization_alias="type")

class QrCode(PermissiveModel):
    type_: Literal["QrCode"] | None = Field('QrCode', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The value the QR code represents")

class Quote(PermissiveModel):
    type_: Literal["Quote"] | None = Field('Quote', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class SectionHeader(PermissiveModel):
    type_: Literal["SectionHeader"] | None = Field('SectionHeader', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class Signature(PermissiveModel):
    type_: Literal["Signature"] | None = Field('Signature', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="Content of the signature.")
    description: str = Field(..., description="A detailed description of the signature.")
    label: str = Field(..., description="The printed text indicating who should sign (e.g., 'Driver Signature', 'Authorized By').")
    is_signed: bool = Field(..., description="True if a handwritten signature, digital signature, or stamp is present. False if blank.")
    signer_name: str | None = Field(None, description="The name of the signer")
    date: str | None = Field(None, description="The date of the signature if present")

class Stamp(PermissiveModel):
    type_: Literal["Stamp"] | None = Field('Stamp', validation_alias="type", serialization_alias="type")
    content: str | None = Field('', description="The text inside the stamp")
    description: str | None = Field('', description="A detailed description of what the visual depicts.")

class SubHeader(PermissiveModel):
    type_: Literal["SubHeader"] | None = Field('SubHeader', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class Table(PermissiveModel):
    type_: Literal["Table"] | None = Field('Table', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The Table in HTML.")
    description: str = Field(..., description="A brief summary of the content in the table.")
    header_range: str | None = Field(None, description="Optional normalized header rows range used for <thead> construction.")

class TableOfContents(PermissiveModel):
    type_: Literal["TableOfContents"] | None = Field('TableOfContents', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="Text content of the table of contents")

class Text(PermissiveModel):
    type_: Literal["Text"] | None = Field('Text', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")
    handwritten: bool | None = Field(False, description="True if handwritten, false otherwise")

class Time(PermissiveModel):
    type_: Literal["Time"] | None = Field('Time', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The time text content")

class Title(PermissiveModel):
    type_: Literal["Title"] | None = Field('Title', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")

class UnorderedList(PermissiveModel):
    type_: Literal["UnorderedList"] | None = Field('UnorderedList', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content of the list and each list item.")

class Video(PermissiveModel):
    type_: Literal["Video"] | None = Field('Video', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="A description of what the video shows.")

class Watermark(PermissiveModel):
    type_: Literal["Watermark"] | None = Field('Watermark', validation_alias="type", serialization_alias="type")
    content: str = Field(..., description="The text content")


# Rebuild models to resolve forward references (required for circular refs)
AccessTokenCredentials.model_rebuild()
Address.model_rebuild()
AudioTranscriptionSegment.model_rebuild()
AuthenticatorConfluenceConnection.model_rebuild()
AuthenticatorDropboxConnection.model_rebuild()
AuthenticatorGmailConnection.model_rebuild()
AuthenticatorGoogleDriveConnection.model_rebuild()
AuthenticatorHubspotConnection.model_rebuild()
AuthenticatorJiraConnection.model_rebuild()
AuthenticatorNotionConnection.model_rebuild()
AuthenticatorOnedriveConnection.model_rebuild()
AuthenticatorSalesforceConnection.model_rebuild()
AuthenticatorSharepointConnection.model_rebuild()
AuthenticatorSlackConnection.model_rebuild()
Author.model_rebuild()
BackblazeCredentials.model_rebuild()
Barcode.model_rebuild()
Bibliography.model_rebuild()
BucketData.model_rebuild()
Button.model_rebuild()
CalendarDate.model_rebuild()
Caption.model_rebuild()
Code.model_rebuild()
Comment.model_rebuild()
ConfluenceData.model_rebuild()
Connection.model_rebuild()
CreateDocumentBodyMode.model_rebuild()
DefinitionList.model_rebuild()
Document.model_rebuild()
EmailAddress.model_rebuild()
Figure.model_rebuild()
FigureCaption.model_rebuild()
FolderData.model_rebuild()
Footer.model_rebuild()
Footnote.model_rebuild()
FormField.model_rebuild()
FormOption.model_rebuild()
Formula.model_rebuild()
FreshdeskCredentials.model_rebuild()
FreshdeskData.model_rebuild()
GmailData.model_rebuild()
GoogleFolderData.model_rebuild()
Header.model_rebuild()
HubspotData.model_rebuild()
Image.model_rebuild()
IntercomCredentials.model_rebuild()
IntercomData.model_rebuild()
Json.model_rebuild()
KeyValue.model_rebuild()
ListItem.model_rebuild()
Logo.model_rebuild()
MediaModeParam.model_rebuild()
NarrativeText.model_rebuild()
OAuthRefreshTokenCredentials.model_rebuild()
OnedriveData.model_rebuild()
OrderedList.model_rebuild()
PageBreak.model_rebuild()
Partition.model_rebuild()
PartitionLimits.model_rebuild()
PublicBackblazeConnection.model_rebuild()
PublicFreshdeskConnection.model_rebuild()
PublicGcsConnection.model_rebuild()
PublicIntercomConnection.model_rebuild()
PublicS3CompatibleConnection.model_rebuild()
PublicWebcrawlerConnection.model_rebuild()
PublicZendeskConnection.model_rebuild()
QrCode.model_rebuild()
Quote.model_rebuild()
S3CompatibleCredentials.model_rebuild()
Search.model_rebuild()
SectionHeader.model_rebuild()
SharepointData.model_rebuild()
SharepointDriveData.model_rebuild()
SharepointFileData.model_rebuild()
SharepointSiteData.model_rebuild()
Signature.model_rebuild()
SlackData.model_rebuild()
Stamp.model_rebuild()
SubHeader.model_rebuild()
Table.model_rebuild()
TableOfContents.model_rebuild()
Text.model_rebuild()
Time.model_rebuild()
Title.model_rebuild()
Tool.model_rebuild()
UncategorizedText.model_rebuild()
UnorderedList.model_rebuild()
UpdateDocumentFileBodyMode.model_rebuild()
Video.model_rebuild()
VideoSegment.model_rebuild()
Watermark.model_rebuild()
WebcrawlerData.model_rebuild()
WordModality.model_rebuild()
ZendeskCredentials.model_rebuild()
ZendeskData.model_rebuild()

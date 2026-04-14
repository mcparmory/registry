"""
Pdf.co Api MCP Server - Pydantic Models

Generated: 2026-04-14 18:30:10 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "GetV1DocumentparserTemplatesIdRequest",
    "GetV1FileUploadGetPresignedUrlRequest",
    "GetV1FileUploadUrlRequest",
    "GetV1TemplatesHtmlIdRequest",
    "PostV1AiInvoiceParserRequest",
    "PostV1BarcodeGenerateRequest",
    "PostV1BarcodeReadFromUrlRequest",
    "PostV1EmailDecodeRequest",
    "PostV1EmailExtractAttachmentsRequest",
    "PostV1EmailSendRequest",
    "PostV1FileDeleteRequest",
    "PostV1FileUploadBase64Request",
    "PostV1FileUploadUrlRequest",
    "PostV1JobCheckRequest",
    "PostV1PdfAttachmentsExtractRequest",
    "PostV1PdfClassifierRequest",
    "PostV1PdfConvertFromCsvRequest",
    "PostV1PdfConvertFromDocRequest",
    "PostV1PdfConvertFromEmailRequest",
    "PostV1PdfConvertFromHtmlRequest",
    "PostV1PdfConvertFromImageRequest",
    "PostV1PdfConvertFromUrlRequest",
    "PostV1PdfConvertToCsvRequest",
    "PostV1PdfConvertToHtmlRequest",
    "PostV1PdfConvertToJpgRequest",
    "PostV1PdfConvertToJson2Request",
    "PostV1PdfConvertToJsonMetaRequest",
    "PostV1PdfConvertToPngRequest",
    "PostV1PdfConvertToTextRequest",
    "PostV1PdfConvertToTextSimpleRequest",
    "PostV1PdfConvertToTiffRequest",
    "PostV1PdfConvertToWebpRequest",
    "PostV1PdfConvertToXlsRequest",
    "PostV1PdfConvertToXlsxRequest",
    "PostV1PdfConvertToXmlRequest",
    "PostV1PdfDocumentparserRequest",
    "PostV1PdfEditAddRequest",
    "PostV1PdfEditDeletePagesRequest",
    "PostV1PdfEditDeleteTextRequest",
    "PostV1PdfEditReplaceTextRequest",
    "PostV1PdfEditReplaceTextWithImageRequest",
    "PostV1PdfEditRotateAutoRequest",
    "PostV1PdfEditRotateRequest",
    "PostV1PdfFindRequest",
    "PostV1PdfFindTableRequest",
    "PostV1PdfInfoFieldsRequest",
    "PostV1PdfInfoRequest",
    "PostV1PdfMakesearchableRequest",
    "PostV1PdfMakeunsearchableRequest",
    "PostV1PdfMerge2Request",
    "PostV1PdfMergeRequest",
    "PostV1PdfSecurityAddRequest",
    "PostV1PdfSecurityRemoveRequest",
    "PostV1PdfSplit2Request",
    "PostV1PdfSplitRequest",
    "PostV1XlsConvertToCsvRequest",
    "PostV1XlsConvertToHtmlRequest",
    "PostV1XlsConvertToJsonRequest",
    "PostV1XlsConvertToPdfRequest",
    "PostV1XlsConvertToTxtRequest",
    "PostV1XlsConvertToXmlRequest",
    "PostV2PdfCompressRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: extract_invoice_data
class PostV1AiInvoiceParserRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the invoice document to process. Accepts PDF and image formats. Defaults to a sample invoice if not provided.")
    customfield: str | None = Field(default=None, description="JSON string specifying custom field names to extract beyond standard invoice fields. Use camelCase for field names (e.g., storeNumber, deliveryDate) with multiple fields comma-separated.")
    callback: str | None = Field(default=None, description="Webhook URL for asynchronous delivery of parsing results. If provided, results will be sent to this endpoint upon completion instead of being returned directly.")
class PostV1AiInvoiceParserRequest(StrictModel):
    """Extract structured data from invoices using advanced AI. Automatically parse invoice content and return key fields regardless of layout or format, with optional support for custom field extraction."""
    body: PostV1AiInvoiceParserRequestBody

# Operation: extract_data_from_pdf_document
class PostV1PdfDocumentparserRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF document to parse. Can be a remote URL or a local file path accessible to the service.")
    template: str | None = Field(default=None, description="JSON template defining extraction rules, including field patterns (regex-based), table structures with multi-page support, and data type specifications. Defaults to a multi-page table extraction template if not provided.")
    outputformat: Literal["JSON", "YAML", "XML", "CSV"] | None = Field(default=None, description="Format for the extracted output data. Choose from JSON, YAML, XML, or CSV. Defaults to JSON.")
    generatecsvheaders: bool | None = Field(default=None, description="When true, includes column headers in CSV output. Only applicable when outputformat is CSV.")
    name: str | None = Field(default=None, description="Optional filename for the generated output file. If not specified, a default name will be assigned.")
    pages: str | None = Field(default=None, description="Specifies which pages to process using 0-based indices. Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7), open-ended ranges (e.g., 10-), and reverse indexing (e.g., !0 for last page). Items are comma-separated. If omitted, all pages are processed.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
class PostV1PdfDocumentparserRequest(StrictModel):
    """Extracts structured data from PDF documents using a customizable parser template. Supports extraction from form fields, tables, and multi-page documents with flexible output formatting."""
    body: PostV1PdfDocumentparserRequestBody

# Operation: get_document_parser_template
class GetV1DocumentparserTemplatesIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the document parser template to retrieve.")
class GetV1DocumentparserTemplatesIdRequest(StrictModel):
    """Retrieve detailed information about a specific document parser template using its unique identifier."""
    path: GetV1DocumentparserTemplatesIdRequestPath

# Operation: extract_pdf_attachments
class PostV1PdfAttachmentsExtractRequestBody(StrictModel):
    url: str = Field(default=..., description="The URL of the PDF file to extract attachments from. Defaults to a sample PDF file if not provided.")
class PostV1PdfAttachmentsExtractRequest(StrictModel):
    """Extracts all attachments embedded in a PDF file from the provided URL. Returns the extracted attachment data for processing or download."""
    body: PostV1PdfAttachmentsExtractRequestBody

# Operation: add_content_to_pdf
class PostV1PdfEditAddRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the source PDF file to edit. Defaults to a sample PDF if not provided.")
    name: str | None = Field(default=None, description="Name for the output document. Defaults to 'newDocument' if not specified.")
    annotations_string: str = Field(default=..., validation_alias="annotationsString", serialization_alias="annotationsString", description="One or more text annotations to add to the PDF. Each annotation is semicolon-delimited with parameters: x-coordinate, y-coordinate, page numbers, text content, font size, font name, font color, optional link URL, transparency setting, width, height, and text alignment.", json_schema_extra={'format': '{x};{y};{pages};{text};{fontsize};{fontname};{fontcolor};{link};{transparent};{width};{height};{alignment}'})
    images_string: str | None = Field(default=None, validation_alias="imagesString", serialization_alias="imagesString", description="One or more images or PDF objects to overlay on the source PDF. Each item is semicolon-delimited with parameters: x-coordinate, y-coordinate, page numbers, URL to the image or PDF file, optional link to open, width, and height.", json_schema_extra={'format': '{x};{y};{pages};{urltoimageOrPdf};{linkToOpen};{width};{height}'})
    fields_string: str | None = Field(default=None, validation_alias="fieldsString", serialization_alias="fieldsString", description="Values to populate in fillable PDF form fields. Each entry is semicolon-delimited with parameters: page number, field name, and field value.", json_schema_extra={'format': '{page};{fieldName};{value}'})
class PostV1PdfEditAddRequest(StrictModel):
    """Add or modify content in a PDF document by inserting text annotations, images, other PDFs, and filling form fields. Supports both native PDFs and scanned documents."""
    body: PostV1PdfEditAddRequestBody

# Operation: replace_text_in_pdf
class PostV1PdfEditReplaceTextRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to process. Defaults to a sample agreement template if not specified.")
    searchstrings: list[str] | None = Field(default=None, description="Array of text strings or patterns to search for in the PDF. Order corresponds to replacestrings array for paired replacements.")
    replacestrings: list[str] | None = Field(default=None, description="Array of replacement text strings corresponding to each search string. Must have the same length as searchstrings for proper pairing.")
    regex: bool | None = Field(default=None, description="Enable regular expression matching for search strings. When true, searchstrings are interpreted as regex patterns rather than literal text.")
    casesensitive: bool | None = Field(default=None, description="Perform case-sensitive text matching. When true, 'Hello' and 'hello' are treated as different strings.")
    replacementlimit: float | None = Field(default=None, description="Maximum number of replacements to perform per search string. Defaults to 1 replacement per string.")
    pages: str | None = Field(default=None, description="Comma-separated page indices or ranges to process (0-based indexing). Supports ranges (e.g., 3-7), open-ended ranges (e.g., 10-), and reverse indexing (e.g., !0 for last page). If omitted, all pages are processed.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Output filename for the processed PDF document.")
class PostV1PdfEditReplaceTextRequest(StrictModel):
    """Search for text patterns in a PDF document and replace them with new text. Supports literal string matching or regular expressions, with options for case sensitivity and replacement limits."""
    body: PostV1PdfEditReplaceTextRequestBody

# Operation: replace_text_with_image_in_pdf
class PostV1PdfEditReplaceTextWithImageRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to modify. Accepts publicly accessible URLs or data URIs.")
    replaceimage: str | None = Field(default=None, description="Base64-encoded image data (with data URI prefix) to use as the replacement. Supports PNG, JPEG, and other common image formats.")
    regex: bool | None = Field(default=None, description="Enable regular expression matching for the search string. When true, the search string is interpreted as a regex pattern; when false, performs literal text matching.")
    casesensitive: bool | None = Field(default=None, description="Perform case-sensitive text matching. When true, 'Text' and 'text' are treated as different; when false, they match regardless of case.")
    replacementlimit: float | None = Field(default=None, description="Maximum number of replacements to perform per search term. Use 0 to replace all occurrences; any positive integer limits replacements to that count.")
    pages: str | None = Field(default=None, description="Comma-separated page indices or ranges to process (0-based indexing). Supports ranges (e.g., 3-7), open-ended ranges (e.g., 10-), reverse indexing (e.g., !0 for last page), and individual pages. Omit to process all pages.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Custom filename for the generated output PDF. If not specified, a default name is assigned.")
    searchstring: str | None = None
class PostV1PdfEditReplaceTextWithImageRequest(StrictModel):
    """Search for specific text in a PDF document and replace it with an image. Supports regex patterns and case-sensitive matching with optional replacement limits and page range targeting."""
    body: PostV1PdfEditReplaceTextWithImageRequestBody

# Operation: delete_text_from_pdf
class PostV1PdfEditDeleteTextRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF document to process. Defaults to a sample agreement template if not provided.")
    searchstrings: list[str] | None = Field(default=None, description="Array of text strings to search for and delete from the PDF. Each string is treated as a literal match unless regex mode is enabled. Defaults to common placeholder tokens like [CLIENT-NAME], [CLIENT-COMPANY], etc.")
    regex: bool | None = Field(default=None, description="Enable regular expression matching for search strings. When true, searchstrings are interpreted as regex patterns instead of literal text.")
    casesensitive: bool | None = Field(default=None, description="Control case sensitivity for text matching. When true, searches are case-sensitive; when false, matches ignore case differences.")
    replacementlimit: float | None = Field(default=None, description="Maximum number of times each search string should be deleted per page. Defaults to 2 deletions per page.")
    pages: str | None = Field(default=None, description="Comma-separated page indices or ranges to process (0-based numbering). Use single numbers (e.g., 0, 5), ranges (e.g., 3-7), or open-ended ranges (e.g., 10-). If omitted, all pages are processed.")
    name: str | None = Field(default=None, description="Custom file name for the generated output PDF. If not specified, a default name will be assigned.")
class PostV1PdfEditDeleteTextRequest(StrictModel):
    """Remove specified text strings from a PDF document. Supports literal text matching or regex patterns, with options for case sensitivity and limiting replacements per page."""
    body: PostV1PdfEditDeleteTextRequestBody

# Operation: convert_pdf_to_csv
class PostV1PdfConvertToCsvRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Can be a direct file URL or a cloud storage link. Defaults to a sample PDF if not provided.")
    lang: str | None = Field(default=None, description="Language code for OCR processing of scanned images. Uses standard language codes (e.g., 'eng' for English). Defaults to English.")
    rect: str | None = Field(default=None, description="Rectangular region to extract from the PDF, specified as four space-separated values: x-coordinate, y-coordinate, width, and height. Use the PDF Edit Add Helper tool to measure coordinates. Only content within this region will be extracted.", json_schema_extra={'format': '{x} {y} {width} {height}'})
    unwrap: bool | None = Field(default=None, description="When enabled, unwraps multi-line text within table cells into single lines. Only applies when line grouping mode is set to 1.")
    linegrouping: Literal["1", "2", "3"] | None = Field(default=None, description="Controls how text lines are grouped within table cells during extraction. Choose from three modes (1, 2, or 3) to adjust grouping behavior. See documentation for detailed mode descriptions.", pattern='^[123]$')
    pages: str | None = Field(default=None, description="Specifies which pages to process using 0-based indices. Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7), open-ended ranges (e.g., 10-), and reverse indexing from the end (!0 for last page). Separate multiple selections with commas. Processes all pages by default.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Output filename for the generated CSV file. Defaults to 'result.csv'.")
class PostV1PdfConvertToCsvRequest(StrictModel):
    """Convert PDF documents and scanned images into CSV format, preserving table structure, columns, rows, and layout information. Supports selective page extraction and configurable text grouping strategies."""
    body: PostV1PdfConvertToCsvRequestBody

# Operation: convert_pdf_to_json
class PostV1PdfConvertToJson2RequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Accepts publicly accessible URLs pointing to PDF documents or scanned images.")
    lang: str | None = Field(default=None, description="Language code for OCR processing when extracting text from scanned PDFs, PNGs, and JPGs. Use ISO 639-3 three-letter language codes (e.g., 'eng' for English). Combine multiple languages with a plus sign (e.g., 'eng+deu') to process text in multiple languages simultaneously.", pattern='^[a-z]{3}(\\+[a-z]{3})*$')
    rect: str | None = Field(default=None, description="Rectangular region to extract from the PDF, specified as coordinates in the format: x-position, y-position, width, and height. Use the PDF Edit Add Helper tool to determine precise coordinates for targeted extraction.", json_schema_extra={'format': '{x} {y} {width} {height}'})
    unwrap: bool | None = Field(default=None, description="When enabled, unwraps multi-line text within table cells into single lines. Only applies when line grouping mode is set to 1.")
    linegrouping: Literal["1", "2", "3"] | None = Field(default=None, description="Controls how text lines are grouped during extraction. Choose from three modes (1, 2, or 3) to adjust line grouping behavior within table cells. Refer to line grouping options documentation for detailed behavior differences.", pattern='^[123]$')
    pages: str | None = Field(default=None, description="Specifies which pages to process using zero-based indices and ranges. Supports individual pages (e.g., '0'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing from the end (e.g., '!0' for last page). Separate multiple selections with commas. If omitted, all pages are processed.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Custom filename for the generated JSON output file.")
class PostV1PdfConvertToJson2Request(StrictModel):
    """Convert PDF documents and scanned images into structured JSON format, preserving text content, fonts, images, vectors, and formatting information. Supports OCR for scanned documents and flexible page selection."""
    body: PostV1PdfConvertToJson2RequestBody

# Operation: convert_pdf_to_json_with_ai
class PostV1PdfConvertToJsonMetaRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF, PNG, or JPG file to convert. Accepts publicly accessible URLs or file paths from supported cloud storage.")
    lang: str | None = Field(default=None, description="OCR language code for extracting text from scanned PDFs and images. Use 3-letter ISO 639-2 language codes (e.g., 'eng' for English). Combine multiple languages with '+' to process bilingual documents (e.g., 'eng+deu' for English and German).", pattern='^[a-z]{3}(\\+[a-z]{3})*$')
    rect: str | None = Field(default=None, description="Rectangular region coordinates for targeted extraction. Specify as four space-separated values: x-offset, y-offset, width, and height. Use the PDF Edit Add Helper tool to measure coordinates precisely.", json_schema_extra={'format': '{x} {y} {width} {height}'})
    unwrap: bool | None = Field(default=None, description="When enabled with line grouping mode 1, merges multi-line text within table cells into single lines for cleaner output.")
    linegrouping: Literal["1", "2", "3"] | None = Field(default=None, description="Controls text line grouping strategy during extraction. Mode 1 groups lines tightly, mode 2 uses standard grouping, and mode 3 applies loose grouping. Affects how text is organized in the JSON output.", pattern='^[123]$')
    pages: str | None = Field(default=None, description="Specifies which pages to process using 0-based indices. Supports individual pages (e.g., '0,2,5'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing from the end (e.g., '!0' for last page). Comma-separate multiple selections; whitespace is allowed.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Custom filename for the generated JSON output file.")
class PostV1PdfConvertToJsonMetaRequest(StrictModel):
    """Convert PDF documents and scanned images into structured JSON format using AI-powered extraction. Supports OCR for scanned content, coordinate-based region extraction, and configurable text grouping strategies."""
    body: PostV1PdfConvertToJsonMetaRequestBody

# Operation: convert_pdf_to_text
class PostV1PdfConvertToTextRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF or image file to convert. Accepts PDF, PNG, and JPG formats. Defaults to a sample PDF if not provided.")
    lang: str | None = Field(default=None, description="Language code for OCR processing when extracting text from scanned PDFs, images, or JPG documents. Use three-letter ISO 639-2 language codes (e.g., 'eng' for English). Combine multiple languages with a plus sign to process text in two languages simultaneously (e.g., 'eng+deu'). Defaults to English.", pattern='^[a-z]{3}(\\+[a-z]{3})*$')
    rect: str | None = Field(default=None, description="Rectangular region to extract text from, specified as coordinates in the format: x-offset, y-offset, width, height (all in points). Use the PDF Edit Add Helper tool to measure coordinates. If omitted, processes the entire document.", json_schema_extra={'format': '{x} {y} {width} {height}'})
    unwrap: bool | None = Field(default=None, description="When enabled with line grouping mode 1, unwraps multi-line text within table cells into single lines. Defaults to disabled.")
    linegrouping: Literal["1", "2", "3"] | None = Field(default=None, description="Controls how text lines are grouped during extraction, particularly within table cells. Choose from mode 1, 2, or 3 for different grouping behaviors. See documentation for detailed mode descriptions.", pattern='^[123]$')
    pages: str | None = Field(default=None, description="Specifies which pages to process using zero-based indices. Supports individual pages (e.g., '0'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing from the end (e.g., '!0' for last page). Separate multiple selections with commas. Processes all pages if omitted.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Custom filename for the generated text output file.")
class PostV1PdfConvertToTextRequest(StrictModel):
    """Convert PDF documents and scanned images to text while preserving layout. Uses OCR technology to extract text from both native PDFs and image-based documents."""
    body: PostV1PdfConvertToTextRequestBody

# Operation: convert_pdf_to_text_fast
class PostV1PdfConvertToTextSimpleRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Accepts publicly accessible PDF URLs.")
    pages: str | None = Field(default=None, description="Comma-separated page indices or ranges to extract (0-based indexing). Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing from the end (e.g., !0 for last page, !5-!2 for range from end). Whitespace around separators is allowed. Omit to process all pages.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Custom file name for the generated text output.")
class PostV1PdfConvertToTextSimpleRequest(StrictModel):
    """Convert a PDF document to plain text using fast, lightweight processing without AI-powered layout analysis or OCR. Use this for quick conversions when layout preservation and scanned page support are not required."""
    body: PostV1PdfConvertToTextSimpleRequestBody

# Operation: convert_pdf_to_xls
class PostV1PdfConvertToXlsRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Defaults to a sample PDF if not provided.")
    lang: str | None = Field(default=None, description="Language(s) for OCR processing when extracting text from scanned PDFs, images, or JPG documents. Use ISO 639-3 three-letter language codes, optionally combining two languages with a plus sign (e.g., eng+deu for English and German). Defaults to English.", pattern='^[a-z]{3}(\\+[a-z]{3})*$')
    rect: str | None = Field(default=None, description="Rectangular region to extract from the PDF, specified as four space-separated values: x-coordinate, y-coordinate, width, and height. Use the PDF Edit Add Helper tool to determine coordinates.", json_schema_extra={'format': '{x} {y} {width} {height}'})
    unwrap: bool | None = Field(default=None, description="When enabled, unwraps multi-line text within table cells into single lines. Only applies when line grouping mode is set to 1.")
    linegrouping: Literal["1", "2", "3"] | None = Field(default=None, description="Controls how text lines are grouped during extraction from table cells. Choose from three modes (1, 2, or 3) to adjust grouping behavior. See Line Grouping Options for details on each mode.", pattern='^[123]$')
    pages: str | None = Field(default=None, description="Specifies which pages to process using zero-based indices or ranges. Use comma-separated values with formats like: single page (0), range (3-7), open-ended range (10-), or reverse indexing (!0 for last page). If omitted, all pages are processed.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Custom file name for the generated Excel output file.")
class PostV1PdfConvertToXlsRequest(StrictModel):
    """Convert a PDF document to Excel (.xls) format while preserving layout, fonts, and table structure. Supports OCR for scanned documents and flexible page selection."""
    body: PostV1PdfConvertToXlsRequestBody

# Operation: convert_pdf_to_xlsx
class PostV1PdfConvertToXlsxRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Defaults to a sample PDF if not provided.")
    lang: str | None = Field(default=None, description="Language code for OCR processing of scanned PDFs, images, and JPG documents. Use ISO 639-3 three-letter codes (e.g., 'eng' for English). Combine multiple languages with '+' for simultaneous processing (e.g., 'eng+deu'). Defaults to English.", pattern='^[a-z]{3}(\\+[a-z]{3})*$')
    rect: str | None = Field(default=None, description="Rectangular region to extract from the PDF, specified as four space-separated values: x-coordinate, y-coordinate, width, and height. Use the PDF Edit Add Helper tool to determine coordinates. Omit to process the entire document.", json_schema_extra={'format': '{x} {y} {width} {height}'})
    unwrap: bool | None = Field(default=None, description="When enabled with line grouping mode 1, unwraps multi-line text within table cells into single lines. Defaults to disabled.")
    linegrouping: Literal["1", "2", "3"] | None = Field(default=None, description="Controls how text lines are grouped during extraction from table cells. Choose from mode 1, 2, or 3 for different grouping behaviors. See Line Grouping Options for detailed behavior differences.", pattern='^[123]$')
    pages: str | None = Field(default=None, description="Specifies which pages to process using zero-based indices. Supports individual pages (e.g., '0'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing (e.g., '!0' for last page). Separate multiple selections with commas. Omit to process all pages.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Custom filename for the generated Excel output file. If not specified, a default name will be assigned.")
class PostV1PdfConvertToXlsxRequest(StrictModel):
    """Convert a PDF document to Excel (.xlsx format) while preserving layout, fonts, and table structure. Supports OCR for scanned documents and flexible page selection."""
    body: PostV1PdfConvertToXlsxRequestBody

# Operation: convert_pdf_to_xml
class PostV1PdfConvertToXmlRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Accepts publicly accessible PDF URLs; defaults to a sample PDF if not provided.")
    lang: str | None = Field(default=None, description="OCR language code for text extraction from scanned PDFs, images, and documents. Use ISO 639-3 three-letter language codes (e.g., 'eng' for English). Combine multiple languages with '+' for simultaneous processing (e.g., 'eng+deu'). Defaults to English.", pattern='^[a-z]{3}(\\+[a-z]{3})*$')
    rect: str | None = Field(default=None, description="Rectangular region to extract from the PDF, specified as space-separated coordinates: x-offset, y-offset, width, and height. Use the PDF Edit Add Helper tool to determine precise coordinates for targeted extraction.", json_schema_extra={'format': '{x} {y} {width} {height}'})
    unwrap: bool | None = Field(default=None, description="When enabled with line grouping mode 1, unwraps multi-line text within table cells into single continuous lines. Defaults to disabled.")
    linegrouping: Literal["1", "2", "3"] | None = Field(default=None, description="Controls text line grouping behavior during extraction. Mode 1 groups lines within table cells, mode 2 applies alternative grouping, and mode 3 uses a third grouping strategy. See documentation for detailed behavior differences.", pattern='^[123]$')
    name: str | None = Field(default=None, description="Custom filename for the generated XML output file. If not specified, a default name is assigned.")
    pages: str | None = Field(default=None, description="Comma-separated list of pages to process (0-based indexing). Supports individual pages (e.g., '0,2,5'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing from end (!0 for last page, !5-!2 for range from end). Processes all pages if omitted.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
class PostV1PdfConvertToXmlRequest(StrictModel):
    """Convert a PDF document to XML format with detailed extraction of text content, table structures, font information, image references, and precise object positioning data."""
    body: PostV1PdfConvertToXmlRequestBody

# Operation: convert_pdf_to_html
class PostV1PdfConvertToHtmlRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Accepts publicly accessible URLs pointing to PDF documents or scanned images (PNG, JPG).")
    lang: str | None = Field(default=None, description="Language code for OCR processing when converting scanned PDFs or image files. Use three-letter ISO 639-2 language codes (e.g., 'eng' for English). Combine multiple languages with '+' to enable simultaneous multi-language OCR (e.g., 'eng+deu' for English and German). Defaults to English.", pattern='^[a-z]{3}(\\+[a-z]{3})*$')
    rect: str | None = Field(default=None, description="Rectangular region to extract, specified as four space-separated coordinates: x, y, width, and height. Use the PDF Edit Add Helper tool to measure coordinates. Only content within this region will be converted.", json_schema_extra={'format': '{x} {y} {width} {height}'})
    pages: str | None = Field(default=None, description="Page selection using zero-based indices and ranges. Specify individual pages (e.g., '0,2,5'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), or reverse indices from the end (e.g., '!0' for last page, '!5-!2' for pages from fifth-to-last to second-to-last). Comma-separate multiple selections. Omit to process all pages.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Custom filename for the generated HTML output file.")
class PostV1PdfConvertToHtmlRequest(StrictModel):
    """Convert PDF documents and scanned images into HTML format while preserving text, fonts, images, vectors, and formatting. Supports OCR for scanned documents and selective page/region extraction."""
    body: PostV1PdfConvertToHtmlRequestBody

# Operation: convert_pdf_to_jpg
class PostV1PdfConvertToJpgRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Can be a remote URL or a local file path. Defaults to a sample encrypted PDF for testing.")
    rect: str | None = Field(default=None, description="Optional rectangular region to extract from each page, specified as four space-separated values: x-coordinate, y-coordinate, width, and height (e.g., '10 20 300 400'). If omitted, the entire page is converted.", json_schema_extra={'format': '{x} {y} {width} {height}'})
    pages: str | None = Field(default=None, description="Optional comma-separated list of pages to convert (0-based indexing). Supports individual pages (e.g., '0,2,5'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), and reverse indexing where !0 is the last page (e.g., '!0, !5-!2'). If omitted, all pages are converted.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Output filename for the converted JPEG image. Defaults to 'result.jpg'.")
class PostV1PdfConvertToJpgRequest(StrictModel):
    """Convert a PDF document to high-quality JPEG images. Optionally extract specific pages or regions from the PDF."""
    body: PostV1PdfConvertToJpgRequestBody

# Operation: convert_pdf_to_png
class PostV1PdfConvertToPngRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Defaults to a sample PDF if not provided.")
    rect: str | None = Field(default=None, description="Optional rectangular region to extract from the PDF, specified as four space-separated values: x-coordinate, y-coordinate, width, and height (e.g., '10 20 300 400').", json_schema_extra={'format': '{x} {y} {width} {height}'})
    pages: str | None = Field(default=None, description="Optional page selection using 0-based indices and ranges. Specify individual pages (e.g., '0,2,5'), ranges (e.g., '3-7'), open-ended ranges (e.g., '10-'), or reverse indices from the end (e.g., '!0' for last page, '!5-!2' for pages in reverse). Items are comma-separated. If omitted, all pages are processed.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Optional custom file name for the generated PNG output file.")
class PostV1PdfConvertToPngRequest(StrictModel):
    """Convert a PDF document to high-quality PNG images. Optionally extract specific regions or pages from the PDF."""
    body: PostV1PdfConvertToPngRequestBody

# Operation: convert_pdf_to_webp
class PostV1PdfConvertToWebpRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Accepts publicly accessible PDF URLs or file paths. Defaults to a sample PDF if not specified.")
    rect: str | None = Field(default=None, description="Optional rectangular region to extract from the PDF, specified as four space-separated values: x-coordinate, y-coordinate, width, and height. Use this to crop a specific area of interest from the page.", json_schema_extra={'format': '{x} {y} {width} {height}'})
    pages: str | None = Field(default=None, description="Optional page selection using 0-based indices. Specify individual pages (e.g., 0, 2, 5), ranges (e.g., 3-7, 10-), or reverse indices from the end (e.g., !0 for last page, !5-!2 for range from fifth-to-last to third-to-last). Separate multiple selections with commas. Defaults to all pages if omitted.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Optional custom file name for the generated WebP output file.")
class PostV1PdfConvertToWebpRequest(StrictModel):
    """Convert a PDF document to high-quality WebP image format. Supports selective page extraction and region-based cropping for targeted conversions."""
    body: PostV1PdfConvertToWebpRequestBody

# Operation: convert_pdf_to_tiff
class PostV1PdfConvertToTiffRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Defaults to a sample PDF if not provided.")
    rect: str | None = Field(default=None, description="Rectangular region to extract from the PDF, specified as four space-separated coordinates: x y width height. Use the PDF Edit Add Helper tool to measure and obtain precise coordinates for your target region.", json_schema_extra={'format': '{x} {y} {width} {height}'})
    unwrap: bool | None = Field(default=None, description="When enabled with lineGrouping, unwraps text lines within table cells into single lines for cleaner extraction.")
    pages: str | None = Field(default=None, description="Comma-separated list of pages to convert (0-based indexing). Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing from the end (e.g., !0 for last page, !5-!2 for range from fifth-to-last to third-to-last). Whitespace is allowed. Defaults to all pages if not specified.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Custom file name for the generated TIFF output file.")
class PostV1PdfConvertToTiffRequest(StrictModel):
    """Convert a PDF document to high-quality TIFF image format. Optionally extract specific regions, select page ranges, and customize output file naming."""
    body: PostV1PdfConvertToTiffRequestBody

# Operation: convert_pdf_from_doc
class PostV1PdfConvertFromDocRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the source document file to convert. Must point to a valid DOC, DOCX, RTF, TXT, or XPS file accessible via HTTP(S).")
    name: str | None = Field(default=None, description="Optional filename for the output PDF file. Defaults to 'result.pdf' if not specified.")
class PostV1PdfConvertFromDocRequest(StrictModel):
    """Convert document files (DOC, DOCX, RTF, TXT, XPS) to PDF format. Accepts a URL pointing to the source document and returns the converted PDF."""
    body: PostV1PdfConvertFromDocRequestBody

# Operation: convert_pdf_from_csv
class PostV1PdfConvertFromCsvRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the CSV, XLS, or XLSX file to convert. Must be a publicly accessible HTTP(S) URL pointing to the spreadsheet file.")
    name: str | None = Field(default=None, description="Output filename for the generated PDF document. Defaults to 'result.pdf' if not specified.")
class PostV1PdfConvertFromCsvRequest(StrictModel):
    """Convert CSV, XLS, or XLSX spreadsheet files into PDF format. Accepts a file URL and returns a generated PDF document."""
    body: PostV1PdfConvertFromCsvRequestBody

# Operation: convert_pdf_from_image
class PostV1PdfConvertFromImageRequestBody(StrictModel):
    url: str = Field(default=..., description="One or more image URLs to convert into PDF, separated by commas. Supported formats are JPG, PNG, and TIFF. Images are processed in the order provided.")
    name: str | None = Field(default=None, description="Optional custom file name for the generated PDF output file.")
class PostV1PdfConvertFromImageRequest(StrictModel):
    """Convert image files (JPG, PNG, TIFF) into PDF format. Accepts one or more image URLs and generates a single PDF document."""
    body: PostV1PdfConvertFromImageRequestBody

# Operation: convert_pdf_from_url
class PostV1PdfConvertFromUrlRequestBody(StrictModel):
    url: str = Field(default=..., description="The URL of the webpage to convert to PDF. Defaults to the Wikipedia contact page if not specified.")
    margins: str | None = Field(default=None, description="Space around the page edges in the PDF output. Specified as a measurement value (e.g., millimeters). Defaults to 5mm.")
    papersize: Literal["Letter", "Legal", "Tabloid", "Ledger", "A0", "A1", "A2", "A3", "A4", "A5", "A6"] | str | None = Field(default=None, description="The paper size for the PDF document. Defaults to Letter size.")
    orientation: Literal["Portrait", "Landscape"] | None = Field(default=None, description="The page orientation for the PDF output. Defaults to Portrait orientation.")
    printbackground: bool | None = Field(default=None, description="Whether to include background colors and images in the PDF. Enabled by default.")
    mediatype: Literal["print", "screen", "none"] | None = Field(default=None, description="The rendering mode for the conversion. Defaults to print mode for optimal PDF formatting.")
    donotwaitfullload: bool | None = Field(default=None, description="When true, speeds up conversion by waiting only for minimal page loading instead of full page load completion. Defaults to false for thorough rendering.")
    header: str | None = Field(default=None, description="Custom HTML content to display at the top of every page in the PDF. Must be valid HTML format.", json_schema_extra={'format': 'html'})
    footer: str | None = Field(default=None, description="Custom HTML content to display at the bottom of every page in the PDF. Must be valid HTML format.", json_schema_extra={'format': 'html'})
    name: str | None = Field(default=None, description="The filename for the generated PDF file output.")
class PostV1PdfConvertFromUrlRequest(StrictModel):
    """Convert a webpage from a URL into a PDF document. The converter processes all JavaScript triggered during page load, including dynamic content and popups, with no option to disable scripting."""
    body: PostV1PdfConvertFromUrlRequestBody

# Operation: convert_pdf_from_html
class PostV1PdfConvertFromHtmlRequestBody(StrictModel):
    html: str = Field(default=..., description="The HTML code to convert to PDF. Can include inline styles, scripts, and other HTML elements.")
    templateid: int = Field(default=..., description="Template identifier that determines the PDF layout and styling template to apply. Defaults to template 1.")
    margins: str | None = Field(default=None, description="Page margins specified as top, right, bottom, and left values in pixels. Defaults to 40px top/bottom and 20px left/right.")
    papersize: Literal["Letter", "Legal", "Tabloid", "Ledger", "A0", "A1", "A2", "A3", "A4", "A5", "A6"] | str | None = Field(default=None, description="Paper size for the output PDF (e.g., Letter, A4, Legal). Defaults to Letter size.")
    orientation: Literal["Portrait", "Landscape"] | None = Field(default=None, description="Page orientation for the output PDF. Defaults to Portrait; can be set to Landscape for wider layouts.")
    printbackground: bool | None = Field(default=None, description="Whether to print background colors and images in the PDF. Enabled by default.")
    mediatype: Literal["print", "screen", "none"] | None = Field(default=None, description="Media type used for rendering, typically 'print' for print-optimized output or 'screen' for screen-optimized output. Defaults to print.")
    donotwaitfullload: bool | None = Field(default=None, description="When true, speeds up conversion by waiting only for minimal page load instead of full page load completion. Defaults to false for thorough rendering.")
    header: str | None = Field(default=None, description="Custom HTML content to display in the header of every page. Must be valid HTML format.", json_schema_extra={'format': 'html'})
    footer: str | None = Field(default=None, description="Custom HTML content to display in the footer of every page. Must be valid HTML format.", json_schema_extra={'format': 'html'})
    name: str | None = Field(default=None, description="Output filename for the generated PDF document. Defaults to 'multipagedInvoiceWithQRCode.pdf'.")
class PostV1PdfConvertFromHtmlRequest(StrictModel):
    """Convert HTML content into a PDF document. The converter processes JavaScript triggered during page load and includes dynamic content like popups in the output."""
    body: PostV1PdfConvertFromHtmlRequestBody

# Operation: get_html_template
class GetV1TemplatesHtmlIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the HTML template to retrieve.")
class GetV1TemplatesHtmlIdRequest(StrictModel):
    """Retrieve a specific HTML template by its unique identifier. Use this operation to fetch the full template content for rendering or editing purposes."""
    path: GetV1TemplatesHtmlIdRequestPath

# Operation: convert_email_to_pdf
class PostV1PdfConvertFromEmailRequestBody(StrictModel):
    url: str = Field(default=..., description="URL pointing to the email file (.msg or .eml) to convert. Defaults to a sample email file if not specified.")
    margins: str | None = Field(default=None, description="Custom page margins as space-separated values (top right bottom left). Supports px, mm, cm, or in units. A single value applies to all sides. Overrides default CSS margins.", json_schema_extra={'format': '{topMargin} {rightMargin} {bottomMargin} {leftMargin}'})
    papersize: str | None = Field(default=None, description="Paper size for the output PDF. Use standard sizes (Letter, Legal, A0–A6, etc.) or specify custom dimensions as width and height with optional units (px, mm, cm, or in).")
    orientation: Literal["Portrait", "Landscape"] | None = Field(default=None, description="Page orientation for the output PDF: Portrait for vertical layout or Landscape for horizontal layout. Defaults to Portrait.")
    name: str | None = Field(default=None, description="Output filename for the generated PDF document. Defaults to 'email-with-attachments' if not specified.")
    header: str | None = Field(default=None, description="Custom HTML content to display in the header of every page. Provide valid HTML markup.", json_schema_extra={'format': 'html'})
    footer: str | None = Field(default=None, description="Custom HTML content to display in the footer of every page. Provide valid HTML markup.", json_schema_extra={'format': 'html'})
class PostV1PdfConvertFromEmailRequest(StrictModel):
    """Convert email files (.msg or .eml format) to PDF documents, automatically extracting and embedding any attachments as PDF attachments within the output file."""
    body: PostV1PdfConvertFromEmailRequestBody

# Operation: convert_spreadsheet_to_csv
class PostV1XlsConvertToCsvRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the Excel file to convert. Must be a publicly accessible URL pointing to a valid xls or xlsx file.")
    worksheetindex: str | None = Field(default=None, description="Zero-based index of the worksheet to convert (first worksheet is index 1). If not specified, the first worksheet is used by default.", pattern='^\\d+$', json_schema_extra={'format': 'number'})
    name: str | None = Field(default=None, description="Custom filename for the generated CSV output file. If not provided, a default name will be assigned.")
class PostV1XlsConvertToCsvRequest(StrictModel):
    """Converts an Excel file (xls/xlsx format) to CSV format. Optionally specify which worksheet to convert and customize the output filename."""
    body: PostV1XlsConvertToCsvRequestBody

# Operation: convert_spreadsheet_to_json
class PostV1XlsConvertToJsonRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the spreadsheet file to convert. Must be a publicly accessible URL pointing to an xls, xlsx, or csv file.")
    worksheetindex: str | None = Field(default=None, description="Zero-based index of the worksheet to extract (e.g., 1 for the first sheet, 2 for the second). Only applicable to Excel files with multiple sheets. Omit to use the default sheet.", pattern='^\\d+$', json_schema_extra={'format': 'number'})
    name: str | None = Field(default=None, description="Custom name for the generated JSON output file. If not provided, a default name will be used.")
class PostV1XlsConvertToJsonRequest(StrictModel):
    """Converts Excel (xls/xlsx) or CSV files to JSON format. Supports selecting specific worksheets and customizing output file names."""
    body: PostV1XlsConvertToJsonRequestBody

# Operation: convert_spreadsheet_to_html
class PostV1XlsConvertToHtmlRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the spreadsheet file to convert. Must be a publicly accessible URL pointing to an xls, xlsx, or csv file.")
    worksheetindex: str | None = Field(default=None, description="Zero-based index of the worksheet to convert when the file contains multiple sheets. Defaults to the first worksheet if not specified.", pattern='^\\d+$', json_schema_extra={'format': 'number'})
    name: str | None = Field(default=None, description="Custom name for the generated HTML output file. If not provided, a default name will be used.")
class PostV1XlsConvertToHtmlRequest(StrictModel):
    """Converts Excel (xls/xlsx) or CSV files to HTML format. Supports selecting specific worksheets and customizing the output file name."""
    body: PostV1XlsConvertToHtmlRequestBody

# Operation: convert_spreadsheet_to_text
class PostV1XlsConvertToTxtRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the spreadsheet file to convert. Must be a publicly accessible URL pointing to an xls, xlsx, or csv file.")
    worksheetindex: str | None = Field(default=None, description="Zero-based index of the worksheet to convert (first worksheet is index 1). If not specified, the first worksheet is used by default.", pattern='^\\d+$', json_schema_extra={'format': 'number'})
    name: str | None = Field(default=None, description="Custom filename for the generated text output file. If not provided, a default name will be assigned.")
class PostV1XlsConvertToTxtRequest(StrictModel):
    """Converts Excel spreadsheets (xls, xlsx, or csv files) to plain text format. Optionally specify which worksheet to convert and customize the output filename."""
    body: PostV1XlsConvertToTxtRequestBody

# Operation: convert_spreadsheet_to_xml
class PostV1XlsConvertToXmlRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the spreadsheet file to convert. Must be a publicly accessible URL pointing to an xls, xlsx, or csv file.")
    worksheetindex: str | None = Field(default=None, description="Zero-based index of the worksheet to convert from multi-sheet workbooks. Use 1 for the first worksheet, 2 for the second, and so on. Only applicable to Excel files with multiple sheets.", pattern='^\\d+$', json_schema_extra={'format': 'number'})
    name: str | None = Field(default=None, description="Custom name for the generated XML output file. If not specified, a default name will be used.")
class PostV1XlsConvertToXmlRequest(StrictModel):
    """Converts Excel (xls/xlsx) or CSV files to XML format. Supports selecting a specific worksheet from multi-sheet workbooks."""
    body: PostV1XlsConvertToXmlRequestBody

# Operation: convert_spreadsheet_to_pdf
class PostV1XlsConvertToPdfRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the spreadsheet file to convert. Accepts XLS, XLSX, or CSV formats.")
    worksheetindex: str | None = Field(default=None, description="Zero-based index of the worksheet to convert when the file contains multiple sheets. Defaults to the first worksheet if not specified.", pattern='^\\d+$', json_schema_extra={'format': 'number'})
    name: str | None = Field(default=None, description="Custom filename for the generated PDF output file.")
    autosize: bool | None = Field(default=None, description="When enabled, automatically adjusts page dimensions to fit the content. When disabled, uses the worksheet's configured page setup settings.")
class PostV1XlsConvertToPdfRequest(StrictModel):
    """Converts Excel (XLS/XLSX) or CSV files to PDF format with optional worksheet selection and automatic page sizing."""
    body: PostV1XlsConvertToPdfRequestBody

# Operation: merge_pdfs
class PostV1PdfMergeRequestBody(StrictModel):
    url: str = Field(default=..., description="One or more URLs pointing to PDF files to merge, separated by commas. URLs must be accessible and point to valid PDF documents. Defaults to sample encrypted PDFs if not specified.")
    name: str | None = Field(default=None, description="The filename for the resulting merged PDF document. Defaults to 'result.pdf' if not specified.")
class PostV1PdfMergeRequest(StrictModel):
    """Merge multiple PDF files into a single consolidated PDF document. Provide one or more PDF URLs to combine them in the order specified."""
    body: PostV1PdfMergeRequestBody

# Operation: merge_documents_to_pdf
class PostV1PdfMerge2RequestBody(StrictModel):
    url: str = Field(default=..., description="Comma-separated URLs of source files to merge. Supports PDF, DOC, DOCX, XLS, XLSX, RTF, TXT, PNG, JPG, and ZIP files containing documents or images. Multiple files are merged in the order specified.")
    name: str | None = Field(default=None, description="Optional custom filename for the generated PDF output file.")
class PostV1PdfMerge2Request(StrictModel):
    """Merge multiple documents and images of various formats (PDF, DOC, DOCX, XLS, XLSX, RTF, TXT, PNG, JPG, or ZIP archives) into a single PDF file. This operation supports broader file type compatibility than standard PDF merge but consumes additional credits due to internal format conversions."""
    body: PostV1PdfMerge2RequestBody

# Operation: split_pdf
class PostV1PdfSplitRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to split. Accepts any publicly accessible PDF URL; defaults to a sample PDF if not provided.")
    pages: str | None = Field(default=None, description="Pages to extract from the PDF using 1-based indexing. Specify individual pages (e.g., 1,3,5), ranges (e.g., 1-5), or combinations (e.g., 1-3,5,7-9). Use !1 to reference the last page and !6-!2 for ranges from the end. Omit the end number in a range (e.g., 3-) to include all pages from that point onward.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Filename for the output PDF file. Defaults to 'result.pdf' if not specified.")
class PostV1PdfSplitRequest(StrictModel):
    """Split a PDF document into multiple separate PDF files by specifying which pages to extract using page numbers or ranges."""
    body: PostV1PdfSplitRequestBody

# Operation: split_pdf_by_text_search
class PostV1PdfSplit2RequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to split. Must be a publicly accessible URL pointing to a valid PDF document.")
    searchstring: str = Field(default=..., description="Text pattern or barcode format to search for within the PDF. Supports barcode syntax like [[barcode:qrcode,datamatrix /pattern/]] for barcode detection, or plain text strings for text search.")
    regexsearch: bool | None = Field(default=None, description="Enable regular expression matching for the search string. When enabled, the searchstring is interpreted as a regex pattern rather than literal text.")
    excludekeypages: bool | None = Field(default=None, description="Exclude pages containing the search match from the output files. When enabled, matching pages are removed; when disabled, they are included in the split results.")
    casesensitive: bool | None = Field(default=None, description="Perform case-sensitive text matching. When disabled, search is case-insensitive.")
    lang: str | None = Field(default=None, description="OCR language for extracting text from scanned PDFs, images, and documents. Use ISO 639-3 language codes (e.g., 'eng' for English). Combine multiple languages with '+' for simultaneous processing (e.g., 'eng+deu').", pattern='^[a-z]{3}(\\+[a-z]{3})*$')
    name: str | None = Field(default=None, description="Base name for the output PDF files. The system will append sequential numbering to create individual split file names.")
class PostV1PdfSplit2Request(StrictModel):
    """Split a PDF document into multiple files by searching for specific text patterns or barcodes. Pages containing the search term can be used as split points, with options to exclude or include those pages in the output."""
    body: PostV1PdfSplit2RequestBody

# Operation: get_pdf_form_fields
class PostV1PdfInfoFieldsRequestBody(StrictModel):
    url: str = Field(default=..., description="The URL of the PDF file to analyze. Must be a publicly accessible URL pointing to a valid PDF document containing form fields.")
class PostV1PdfInfoFieldsRequest(StrictModel):
    """Extract and retrieve metadata about all fillable form fields within a PDF document. Returns field names, types, and properties for programmatic form processing."""
    body: PostV1PdfInfoFieldsRequestBody

# Operation: search_pdf_text
class PostV1PdfFindRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to search. Defaults to a sample PDF if not specified.")
    searchstring: str = Field(default=..., description="Text or pattern to find in the PDF. When regex search is enabled, this accepts regular expression syntax (e.g., date patterns like \\d+/\\d+/\\d+).")
    regexsearch: bool | None = Field(default=None, description="Enable regular expression matching for the search string. When true, the search string is interpreted as a regex pattern; when false, performs literal string matching.")
    wordmatchingmode: str | None = Field(default=None, description="Word matching mode to control how text boundaries are handled during search (e.g., whole words only vs. partial matches).")
    casesensitive: bool | None = Field(default=None, description="Control search sensitivity to letter case. Set to false for case-insensitive matching; true for case-sensitive matching.")
    pages: str | None = Field(default=None, description="Specify which pages to search using 0-based indices. Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing (e.g., !0 for last page). Use comma-separated values for multiple selections. Omit to search all pages.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Name identifier for the output results.")
class PostV1PdfFindRequest(StrictModel):
    """Search for text patterns in a PDF document and retrieve their precise coordinates. Supports both literal string matching and regular expression patterns for flexible text discovery."""
    body: PostV1PdfFindRequestBody

# Operation: search_tables_in_pdf
class PostV1PdfFindTableRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to analyze. Defaults to a sample PDF if not provided.")
    pages: str | None = Field(default=None, description="Comma-separated page indices or ranges to scan (0-based indexing). Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing from the end (e.g., !0 for last page, !5-!2 for range from fifth-to-last to third-to-last). Whitespace is allowed. If omitted, all pages are processed.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Optional custom name for the generated output file.")
class PostV1PdfFindTableRequest(StrictModel):
    """Scan a PDF document using AI to detect and extract tables, returning their locations, coordinates, and column information for specified pages."""
    body: PostV1PdfFindTableRequestBody

# Operation: make_pdf_searchable
class PostV1PdfMakesearchableRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF or image file to process. Accepts remote URLs pointing to scanned documents or image files that need OCR conversion.")
    lang: str | None = Field(default=None, description="Language code for OCR processing (e.g., 'eng' for English). Defaults to English if not specified. Use standard ISO 639-3 language codes.")
    pages: str | None = Field(default=None, description="Comma-separated page indices or ranges to process (0-based indexing). Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing (e.g., !0 for last page). Whitespace is allowed. If omitted, all pages are processed.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Output filename for the resulting searchable PDF. Defaults to 'result.pdf' if not specified.")
    rect: str | None = Field(default=None, description="Rectangular region coordinates for targeted OCR processing, specified as four space-separated values: x y width height (in points). Use the PDF Edit Add Helper tool to measure coordinates. If omitted, the entire page is processed.", json_schema_extra={'format': '{x} {y} {width} {height}'})
class PostV1PdfMakesearchableRequest(StrictModel):
    """Convert scanned PDF documents or image files into text-searchable PDFs by running OCR and adding an invisible text layer for search and indexing capabilities."""
    body: PostV1PdfMakesearchableRequestBody

# Operation: convert_pdf_to_unsearchable
class PostV1PdfMakeunsearchableRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to convert. Can be a direct file URL or a cloud storage path (e.g., S3 URI).")
    pages: str | None = Field(default=None, description="Comma-separated page indices or ranges to process (0-based indexing). Supports individual pages (e.g., 0, 5), ranges (e.g., 3-7, 10-), and reverse indexing from the end (e.g., !0 for last page, !5-!2 for range from fifth-to-last to third-to-last). Whitespace is allowed. If omitted, all pages are processed.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Output filename for the resulting unsearchable PDF document.")
class PostV1PdfMakeunsearchableRequest(StrictModel):
    """Convert a PDF file into an unsearchable version by rendering it as a flat image, effectively creating a scanned PDF that prevents text extraction."""
    body: PostV1PdfMakeunsearchableRequestBody

# Operation: compress_pdf
class PostV2PdfCompressRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to compress. Defaults to a sample PDF if not provided.")
    name: str | None = Field(default=None, description="Optional file name for the compressed output PDF. If not specified, a default name will be generated.")
    config: dict[str, Any] | None = Field(default=None, description="Compression configuration object controlling image optimization strategies. Allows separate settings for color, grayscale, and monochrome images, including downsampling thresholds (in DPI), compression format selection (JPEG or CCITT G4), and quality parameters. Defaults to balanced compression settings optimized for file size reduction.")
class PostV2PdfCompressRequest(StrictModel):
    """Compress PDF files to reduce their size by optimizing images and content. Supports configurable downsampling, compression formats, and quality settings for color, grayscale, and monochrome images."""
    body: PostV2PdfCompressRequestBody

# Operation: get_pdf_info
class PostV1PdfInfoRequestBody(StrictModel):
    url: str = Field(default=..., description="The URL of the PDF document to analyze. Must be a valid, publicly accessible PDF file URL.")
class PostV1PdfInfoRequest(StrictModel):
    """Retrieve detailed metadata, properties, and security permissions for a PDF document from a specified URL."""
    body: PostV1PdfInfoRequestBody

# Operation: get_job_status
class PostV1JobCheckRequestBody(StrictModel):
    jobid: str = Field(default=..., description="The unique identifier of the asynchronous job whose status you want to check. This ID is returned when you initially create a background job.")
    force: bool | None = Field(default=None, description="When enabled, forces a fresh status check from the server rather than returning a cached result, ensuring you get the most current job state.")
class PostV1JobCheckRequest(StrictModel):
    """Retrieves the current status of an asynchronous background job that was previously initiated through the PDF.co API. Use this operation to poll and monitor the progress of long-running tasks."""
    body: PostV1JobCheckRequestBody

# Operation: classify_document
class PostV1PdfClassifierRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the document to classify. Accepts PDF, JPG, or PNG files. Defaults to a sample invoice if not provided.")
    casesensitive: bool | None = Field(default=None, description="Controls whether the classification search is case-sensitive. Set to false to ignore case differences during analysis; defaults to true for case-sensitive matching.")
class PostV1PdfClassifierRequest(StrictModel):
    """Analyzes the content of a PDF, JPG, or PNG document to automatically determine its classification using built-in AI or custom-defined classification rules."""
    body: PostV1PdfClassifierRequestBody

# Operation: send_email_with_attachment
class PostV1EmailSendRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the file to attach to the email. Defaults to a sample PDF from AWS S3.")
    from_: str = Field(default=..., validation_alias="from", serialization_alias="from", description="Sender email address in the format 'Name <email@domain.com>' or just 'email@domain.com'.")
    to: str = Field(default=..., description="Primary recipient email address. Use comma-separated values for multiple recipients.")
    replyto: str | None = Field(default=None, description="Reply-to email address. If specified, replies will be directed to this address instead of the sender.")
    cc: str | None = Field(default=None, description="Carbon copy recipient email address. Use comma-separated values for multiple recipients.")
    bcc: str | None = Field(default=None, description="Blind carbon copy recipient email address. Use comma-separated values for multiple recipients. Recipients in this field are hidden from other recipients.")
    subject: str = Field(default=..., description="Email subject line.")
    smtpserver: str = Field(default=..., description="SMTP server hostname (e.g., smtp.gmail.com for Gmail, smtp.office365.com for Outlook).")
    smtpusername: str = Field(default=..., description="Username or email address for SMTP authentication.")
    smtppassword: str = Field(default=..., description="Password or app-specific password for SMTP authentication. For Gmail, use an app-specific password rather than your account password.")
    name: str | None = Field(default=None, description="Custom filename for the attachment. If not specified, the original filename from the URL will be used.")
class PostV1EmailSendRequest(StrictModel):
    """Send an email message with optional file attachment. Supports multiple recipients and requires SMTP server credentials for delivery."""
    body: PostV1EmailSendRequestBody

# Operation: extract_email_components
class PostV1EmailDecodeRequestBody(StrictModel):
    url: str = Field(default=..., description="URL pointing to the email file (.eml format) to be decoded. Defaults to a sample email file if not provided.")
class PostV1EmailDecodeRequest(StrictModel):
    """Decode an email message file to extract and parse its components including headers, body, attachments, and metadata."""
    body: PostV1EmailDecodeRequestBody

# Operation: extract_email_attachments
class PostV1EmailExtractAttachmentsRequestBody(StrictModel):
    url: str = Field(default=..., description="The URL pointing to the EML email file to process. Must be a valid, accessible HTTP(S) URL. Defaults to a sample EML file if not provided.")
class PostV1EmailExtractAttachmentsRequest(StrictModel):
    """Extract all attachments from an email message. Provide the URL to an EML file to retrieve and process its attachments."""
    body: PostV1EmailExtractAttachmentsRequestBody

# Operation: delete_temporary_file
class PostV1FileDeleteRequestBody(StrictModel):
    url: str = Field(default=..., description="The S3 URL of the temporary file to delete. This should be a full URL path to the file in the temporary storage bucket.")
class PostV1FileDeleteRequest(StrictModel):
    """Permanently deletes a temporary file from cloud storage. This operation removes files that were previously uploaded by you or generated by the API."""
    body: PostV1FileDeleteRequestBody

# Operation: upload_file_from_url
class GetV1FileUploadUrlRequestQuery(StrictModel):
    url: str = Field(default=..., description="The source URL of the file to download and upload. Must be a valid, accessible HTTP or HTTPS URL.")
    name: str | None = Field(default=None, description="Optional custom name for the uploaded file. If not provided, the original filename from the source URL will be used.")
class GetV1FileUploadUrlRequest(StrictModel):
    """Downloads a file from a source URL and uploads it as a temporary file to the system. Temporary files are automatically deleted after 1 hour."""
    query: GetV1FileUploadUrlRequestQuery

# Operation: upload_file_from_url_direct
class PostV1FileUploadUrlRequestBody(StrictModel):
    name: str | None = Field(default=None, description="Optional custom name for the uploaded file. If not provided, the original filename from the source URL will be used.")
    url: str = Field(default=..., description="The remote URL pointing to the file to download and upload. Must be a valid URI format.", json_schema_extra={'format': 'uri'})
class PostV1FileUploadUrlRequest(StrictModel):
    """Downloads a file from a remote URL and uploads it as a temporary file to the system. The temporary file will be automatically deleted after 1 hour."""
    body: PostV1FileUploadUrlRequestBody

# Operation: create_file_from_base64
class PostV1FileUploadBase64RequestBody(StrictModel):
    name: str | None = Field(default=None, description="Optional name for the generated file. If not provided, a default name will be assigned.")
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="Base64-encoded file content to upload. Must be a valid base64 string representing the file bytes.", json_schema_extra={'format': 'byte'})
class PostV1FileUploadBase64Request(StrictModel):
    """Creates a temporary file from base64-encoded data that can be used with other API methods. The temporary file is automatically deleted after 1 hour."""
    body: PostV1FileUploadBase64RequestBody

# Operation: get_file_upload_presigned_url
class GetV1FileUploadGetPresignedUrlRequestQuery(StrictModel):
    name: str | None = Field(default=None, description="The name to assign to the uploaded file. Must be provided as a string.")
    contenttype: str | None = Field(default=None, description="The MIME type of the file being uploaded (e.g., application/pdf, image/png, text/plain).", json_schema_extra={'format': 'mime type'})
class GetV1FileUploadGetPresignedUrlRequest(StrictModel):
    """Generate a pre-signed URL for uploading a file. Use the returned URL with a PUT request to upload your file, then access it via the provided link."""
    query: GetV1FileUploadGetPresignedUrlRequestQuery | None = None

# Operation: add_password_to_pdf
class PostV1PdfSecurityAddRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to secure. Defaults to a sample PDF if not provided.")
    ownerpassword: str | None = Field(default=None, description="Password required to modify document permissions and security settings. Defaults to '12345' if not specified.")
    userpassword: str | None = Field(default=None, description="Password required for users to open and view the PDF document. Defaults to '54321' if not specified.")
    allowaccessibilitysupport: bool | None = Field(default=None, description="Whether to allow screen readers and accessibility tools to access the document content.")
    allowassemblydocument: bool | None = Field(default=None, description="Whether to allow users to assemble or reorganize pages within the document.")
    allowprintdocument: bool | None = Field(default=None, description="Whether to allow users to print the document. Disabled by default.")
    allowfillforms: bool | None = Field(default=None, description="Whether to allow users to fill in form fields within the document. Disabled by default.")
    allowmodifydocument: bool | None = Field(default=None, description="Whether to allow users to modify or edit the document content. Disabled by default.")
    allowcontentextraction: bool | None = Field(default=None, description="Whether to allow users to copy or extract text and graphics from the document. Disabled by default.")
    allowmodifyannotations: bool | None = Field(default=None, description="Whether to allow users to add, modify, or delete annotations and comments. Disabled by default.")
    printquality: str | None = Field(default=None, description="Quality level for printing permissions. Set to 'LowResolution' by default to restrict print quality.")
    name: str | None = Field(default=None, description="Output filename for the secured PDF document. Defaults to 'output-protected.pdf' if not specified.")
class PostV1PdfSecurityAddRequest(StrictModel):
    """Secure a PDF document by adding password protection and configurable access restrictions. Specify owner and user passwords along with granular permissions for printing, editing, copying, and other document operations."""
    body: PostV1PdfSecurityAddRequestBody

# Operation: remove_pdf_password
class PostV1PdfSecurityRemoveRequestBody(StrictModel):
    url: str = Field(default=..., description="The URL of the PDF file to remove password protection from. Can be a direct file URL or a cloud storage link.")
    name: str | None = Field(default=None, description="The desired filename for the unprotected PDF output. Defaults to 'unprotected' if not specified.")
class PostV1PdfSecurityRemoveRequest(StrictModel):
    """Remove password protection and access restrictions from a PDF file, making it fully accessible without authentication."""
    body: PostV1PdfSecurityRemoveRequestBody

# Operation: delete_pdf_pages
class PostV1PdfEditDeletePagesRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to process. Can be a direct file URL or a path to a PDF stored in cloud storage.")
    pages: str | None = Field(default=None, description="Comma-separated list of page numbers or ranges to delete, using 1-based indexing. Supports ranges (e.g., 3-5), individual pages (e.g., 2), and negative indices where !1 is the last page (e.g., !1 deletes the last page, !6-!2 deletes from the 6th-to-last to 2nd-to-last page). Whitespace around values is ignored.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    name: str | None = Field(default=None, description="Filename for the output PDF document. Defaults to 'result.pdf' if not specified.")
class PostV1PdfEditDeletePagesRequest(StrictModel):
    """Removes specified pages from a PDF file and returns the modified document. Pages are identified using 1-based indexing with support for ranges and negative indices (where !1 refers to the last page)."""
    body: PostV1PdfEditDeletePagesRequestBody

# Operation: rotate_pdf_pages
class PostV1PdfEditRotateRequestBody(StrictModel):
    url: str = Field(default=..., description="The URL of the PDF file to rotate. Can be a remote URL or a local file path.")
    pages: str | None = Field(default=None, description="Zero-based page indices or ranges to rotate, specified as comma-separated values. Supports individual pages (e.g., 0, 2, 5), ranges (e.g., 3-7, 10-), and reverse indexing from the end of the document (e.g., !0 for last page, !5-!2 for a range from the end). Whitespace around values is allowed. Omit to rotate all pages.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
    angle: str | None = Field(default=None, description="The rotation angle in degrees to apply to selected pages. Common values are 90, 180, and 270 for standard rotations.")
    name: str | None = Field(default=None, description="The filename for the output PDF document after rotation is applied.")
class PostV1PdfEditRotateRequest(StrictModel):
    """Rotates specified pages in a PDF document by a given angle. If no pages are specified, the operation rotates all pages in the document."""
    body: PostV1PdfEditRotateRequestBody

# Operation: auto_rotate_pdf_pages
class PostV1PdfEditRotateAutoRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the PDF file to auto-rotate. Accepts a publicly accessible PDF document URL.")
    lang: str | None = Field(default=None, description="Language(s) for text recognition during rotation analysis. Use a 3-letter language code (e.g., 'eng' for English). Combine multiple languages with a plus sign (e.g., 'eng+deu') for simultaneous multi-language support. Defaults to English.", pattern='^[a-z]{3}(\\+[a-z]{3})*$')
    name: str | None = Field(default=None, description="Output filename for the rotated PDF. Specify the desired name with .pdf extension for the returned document.")
class PostV1PdfEditRotateAutoRequest(StrictModel):
    """Automatically corrects the rotation of pages in a scanned PDF using AI-powered text analysis. Supports multiple languages for accurate text detection and orientation correction."""
    body: PostV1PdfEditRotateAutoRequestBody

# Operation: generate_barcode
class PostV1BarcodeGenerateRequestBody(StrictModel):
    value: str | None = Field(default=None, description="The data or text to encode in the barcode. Defaults to 'abcdef123456' if not provided.")
    type_: Literal["AustralianPostCode", "Aztec", "Codabar", "CodablockF", "Code128", "Code16K", "Code39", "Code39Extended", "Code39Mod43", "Code39Mod43Extended", "Code93", "DataMatrix", "DPMDataMatrix", "EAN13", "EAN2", "EAN5", "EAN8", "GS1DataBarExpanded", "GS1DataBarExpandedStacked", "GS1DataBarLimited", "GS1DataBarOmnidirectional", "GS1DataBarStacked", "GTIN12", "GTIN13", "GTIN14", "GTIN8", "IntelligentMail", "Interleaved2of5", "ITF14", "MaxiCode", "MICR", "MicroPDF", "MSI", "PatchCode", "PDF417", "Pharmacode", "PostNet", "PZN", "QRCode", "RoyalMail", "RoyalMailKIX", "Trioptic", "UPCA", "UPCE", "UPU"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The barcode format type to generate. Defaults to QR Code if not specified. Supports formats such as QR Code, Data Matrix, Code 39, Code 128, and PDF417.")
    decorationimage: str | None = Field(default=None, description="Optional image file to embed or overlay on the generated barcode for branding or decoration purposes.")
    name: str | None = Field(default=None, description="The output filename for the generated barcode image. Defaults to 'barcode.png' if not provided.")
class PostV1BarcodeGenerateRequest(StrictModel):
    """Generate high-quality barcode images in various formats including QR Code, Data Matrix, Code 39, Code 128, PDF417, and other standard barcode types."""
    body: PostV1BarcodeGenerateRequestBody | None = None

# Operation: read_barcodes_from_url
class PostV1BarcodeReadFromUrlRequestBody(StrictModel):
    url: str = Field(default=..., description="URL of the image or PDF document to scan for barcodes. Must be publicly accessible.")
    types: str = Field(default=..., description="Comma-separated list of barcode types to detect. Choose from 40+ supported formats including QRCode, Code128, EAN13, DataMatrix, PDF417, GS1, and others. Only specified types will be decoded.")
    pages: str | None = Field(default=None, description="Optional page indices or ranges to scan (0-based, applies to PDFs only). Specify individual pages (e.g., 0,2,5), ranges (e.g., 3-7 or 10-), or reverse indices (e.g., !0 for last page). Comma-separated with optional whitespace. If omitted, all pages are processed.", pattern='^\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*(?:,\\s*(?:!?\\d+\\s*-\\s*!?\\d+|!?\\d+\\s*-\\s*|!?\\d+)\\s*)*$')
class PostV1BarcodeReadFromUrlRequest(StrictModel):
    """Decode barcodes and QR codes from images or PDF documents accessible via URL. Supports 40+ barcode formats including QR Code, Code 128, EAN, DataMatrix, PDF417, and GS1 standards."""
    body: PostV1BarcodeReadFromUrlRequestBody

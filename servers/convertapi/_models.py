"""
Convertapi MCP Server - Pydantic Models

Generated: 2026-04-24 08:32:26 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import StrictModel
from pydantic import Field

__all__ = [
    "DeleteDRequest",
    "GetDRequest",
    "GetUserStatisticRequest",
    "HeadDRequest",
    "PostConvertAiToJpgRequest",
    "PostConvertAiToPngRequest",
    "PostConvertAiToPnmRequest",
    "PostConvertAiToSvgRequest",
    "PostConvertAiToTiffRequest",
    "PostConvertAiToWebpRequest",
    "PostConvertBmpToJpgRequest",
    "PostConvertBmpToPdfRequest",
    "PostConvertBmpToPngRequest",
    "PostConvertBmpToPnmRequest",
    "PostConvertBmpToSvgRequest",
    "PostConvertBmpToTiffRequest",
    "PostConvertBmpToWebpRequest",
    "PostConvertCsvToPdfRequest",
    "PostConvertCsvToXlsxRequest",
    "PostConvertDjvuToJpgRequest",
    "PostConvertDjvuToPdfRequest",
    "PostConvertDjvuToPngRequest",
    "PostConvertDjvuToTiffRequest",
    "PostConvertDjvuToWebpRequest",
    "PostConvertDocToDocxRequest",
    "PostConvertDocxToCompareRequest",
    "PostConvertDocxToHtmlRequest",
    "PostConvertDocxToJpgRequest",
    "PostConvertDocxToMdRequest",
    "PostConvertDocxToOdtRequest",
    "PostConvertDocxToPdfRequest",
    "PostConvertDocxToPngRequest",
    "PostConvertDocxToProtectRequest",
    "PostConvertDocxToRtfRequest",
    "PostConvertDocxToTiffRequest",
    "PostConvertDocxToTxtRequest",
    "PostConvertDocxToWebpRequest",
    "PostConvertDocxToXmlRequest",
    "PostConvertDotxToJpgRequest",
    "PostConvertDotxToPdfRequest",
    "PostConvertDwfToJpgRequest",
    "PostConvertDwfToPdfRequest",
    "PostConvertDwfToPngRequest",
    "PostConvertDwfToSvgRequest",
    "PostConvertDwfToTiffRequest",
    "PostConvertDwfToWebpRequest",
    "PostConvertDwgToJpgRequest",
    "PostConvertDwgToPdfRequest",
    "PostConvertDwgToPngRequest",
    "PostConvertDwgToSvgRequest",
    "PostConvertDwgToTiffRequest",
    "PostConvertDwgToWebpRequest",
    "PostConvertDxfToJpgRequest",
    "PostConvertDxfToPdfRequest",
    "PostConvertDxfToPngRequest",
    "PostConvertDxfToSvgRequest",
    "PostConvertDxfToTiffRequest",
    "PostConvertDxfToWebpRequest",
    "PostConvertEmailToExtractRequest",
    "PostConvertEmailToMetadataRequest",
    "PostConvertEmlToJpgRequest",
    "PostConvertEmlToPdfRequest",
    "PostConvertEmlToPngRequest",
    "PostConvertEmlToTiffRequest",
    "PostConvertEmlToWebpRequest",
    "PostConvertEpsToJpgRequest",
    "PostConvertEpsToPdfRequest",
    "PostConvertEpsToPngRequest",
    "PostConvertEpsToTiffRequest",
    "PostConvertEpubToJpgRequest",
    "PostConvertEpubToPdfRequest",
    "PostConvertEpubToPngRequest",
    "PostConvertEpubToTiffRequest",
    "PostConvertEpubToWebpRequest",
    "PostConvertFileToPdfRequest",
    "PostConvertFileToZipRequest",
    "PostConvertGifToGifRequest",
    "PostConvertGifToJpgRequest",
    "PostConvertGifToPdfRequest",
    "PostConvertGifToPngRequest",
    "PostConvertGifToPnmRequest",
    "PostConvertGifToSvgRequest",
    "PostConvertGifToTiffRequest",
    "PostConvertGifToWebpRequest",
    "PostConvertHeicToJpgRequest",
    "PostConvertHeicToJxlRequest",
    "PostConvertHeicToPdfRequest",
    "PostConvertHeicToPngRequest",
    "PostConvertHeicToPnmRequest",
    "PostConvertHeicToSvgRequest",
    "PostConvertHeicToTiffRequest",
    "PostConvertHeicToWebpRequest",
    "PostConvertHeifToJpgRequest",
    "PostConvertHeifToPdfRequest",
    "PostConvertHtmlToDocxRequest",
    "PostConvertHtmlToJpgRequest",
    "PostConvertHtmlToMdRequest",
    "PostConvertHtmlToPdfRequest",
    "PostConvertHtmlToPngRequest",
    "PostConvertHtmlToTxtRequest",
    "PostConvertHtmlToXlsRequest",
    "PostConvertHtmlToXlsxRequest",
    "PostConvertIcoToJpgRequest",
    "PostConvertIcoToPdfRequest",
    "PostConvertIcoToPngRequest",
    "PostConvertIcoToSvgRequest",
    "PostConvertIcoToWebpRequest",
    "PostConvertImagesToJoinRequest",
    "PostConvertImagesToPdfRequest",
    "PostConvertJfifToPdfRequest",
    "PostConvertJpgToCompressRequest",
    "PostConvertJpgToGifRequest",
    "PostConvertJpgToJpgRequest",
    "PostConvertJpgToJxlRequest",
    "PostConvertJpgToPdfRequest",
    "PostConvertJpgToPngRequest",
    "PostConvertJpgToPnmRequest",
    "PostConvertJpgToSvgRequest",
    "PostConvertJpgToTiffRequest",
    "PostConvertJpgToTxtRequest",
    "PostConvertJpgToWebpRequest",
    "PostConvertKeyToPptxRequest",
    "PostConvertLogToDocxRequest",
    "PostConvertLogToPdfRequest",
    "PostConvertLogToTxtRequest",
    "PostConvertMdToHtmlRequest",
    "PostConvertMdToPdfRequest",
    "PostConvertMhtmlToDocxRequest",
    "PostConvertMobiToJpgRequest",
    "PostConvertMobiToPdfRequest",
    "PostConvertMobiToPngRequest",
    "PostConvertMobiToTiffRequest",
    "PostConvertMsgToJpgRequest",
    "PostConvertMsgToPdfRequest",
    "PostConvertMsgToPngRequest",
    "PostConvertMsgToTiffRequest",
    "PostConvertMsgToWebpRequest",
    "PostConvertNumbersToCsvRequest",
    "PostConvertNumbersToXlsxRequest",
    "PostConvertOdcToJpgRequest",
    "PostConvertOdcToPdfRequest",
    "PostConvertOdcToPngRequest",
    "PostConvertOdfToJpgRequest",
    "PostConvertOdfToPdfRequest",
    "PostConvertOdfToPngRequest",
    "PostConvertOdgToPdfRequest",
    "PostConvertOdpToJpgRequest",
    "PostConvertOdpToPdfRequest",
    "PostConvertOdpToPngRequest",
    "PostConvertOdsToJpgRequest",
    "PostConvertOdsToPdfRequest",
    "PostConvertOdsToPngRequest",
    "PostConvertOdtToDocxRequest",
    "PostConvertOdtToJpgRequest",
    "PostConvertOdtToPdfRequest",
    "PostConvertOdtToPngRequest",
    "PostConvertOdtToTxtRequest",
    "PostConvertOdtToXmlRequest",
    "PostConvertOfficeToPdfRequest",
    "PostConvertPagesToDocxRequest",
    "PostConvertPagesToTxtRequest",
    "PostConvertPdfaToValidateRequest",
    "PostConvertPdfToCompressRequest",
    "PostConvertPdfToCropRequest",
    "PostConvertPdfToCsvRequest",
    "PostConvertPdfToDeletePagesRequest",
    "PostConvertPdfToDocxRequest",
    "PostConvertPdfToExtractImagesRequest",
    "PostConvertPdfToExtractRequest",
    "PostConvertPdfToFdfExtractRequest",
    "PostConvertPdfToFdfImportRequest",
    "PostConvertPdfToFlattenRequest",
    "PostConvertPdfToHtmlRequest",
    "PostConvertPdfToImageWatermarkRequest",
    "PostConvertPdfToJpgRequest",
    "PostConvertPdfToMergeRequest",
    "PostConvertPdfToMetaRequest",
    "PostConvertPdfToOcrRequest",
    "PostConvertPdfToPclRequest",
    "PostConvertPdfToPdfaRequest",
    "PostConvertPdfToPdfRequest",
    "PostConvertPdfToPdfuaRequest",
    "PostConvertPdfToPdfWatermarkRequest",
    "PostConvertPdfToPngRequest",
    "PostConvertPdfToPptxRequest",
    "PostConvertPdfToPrintRequest",
    "PostConvertPdfToProtectRequest",
    "PostConvertPdfToRasterizeRequest",
    "PostConvertPdfToRedactRequest",
    "PostConvertPdfToResizeRequest",
    "PostConvertPdfToRotateRequest",
    "PostConvertPdfToRtfRequest",
    "PostConvertPdfToSplitRequest",
    "PostConvertPdfToSvgRequest",
    "PostConvertPdfToTextWatermarkRequest",
    "PostConvertPdfToTiffFaxRequest",
    "PostConvertPdfToTiffRequest",
    "PostConvertPdfToTxtRequest",
    "PostConvertPdfToUnprotectRequest",
    "PostConvertPdfToWebpRequest",
    "PostConvertPdfToXlsxRequest",
    "PostConvertPngToGifRequest",
    "PostConvertPngToJpgRequest",
    "PostConvertPngToPdfRequest",
    "PostConvertPngToPnmRequest",
    "PostConvertPngToSvgRequest",
    "PostConvertPngToTiffRequest",
    "PostConvertPngToWebpRequest",
    "PostConvertPoToTranslateRequest",
    "PostConvertPotxToJpgRequest",
    "PostConvertPotxToPdfRequest",
    "PostConvertPotxToPngRequest",
    "PostConvertPotxToPptxRequest",
    "PostConvertPotxToTiffRequest",
    "PostConvertPotxToWebpRequest",
    "PostConvertPpsxToJpgRequest",
    "PostConvertPpsxToPdfRequest",
    "PostConvertPpsxToPngRequest",
    "PostConvertPpsxToPptxRequest",
    "PostConvertPpsxToTiffRequest",
    "PostConvertPpsxToWebpRequest",
    "PostConvertPptToPptxRequest",
    "PostConvertPptxToJpgRequest",
    "PostConvertPptxToPdfRequest",
    "PostConvertPptxToPngRequest",
    "PostConvertPptxToPptxRequest",
    "PostConvertPptxToProtectRequest",
    "PostConvertPptxToTiffRequest",
    "PostConvertPptxToWebpRequest",
    "PostConvertPrnToJpgRequest",
    "PostConvertPrnToPdfRequest",
    "PostConvertPrnToPngRequest",
    "PostConvertPrnToTiffRequest",
    "PostConvertPsdToJpgRequest",
    "PostConvertPsdToPngRequest",
    "PostConvertPsdToPnmRequest",
    "PostConvertPsdToSvgRequest",
    "PostConvertPsdToTiffRequest",
    "PostConvertPsdToWebpRequest",
    "PostConvertPsToJpgRequest",
    "PostConvertPsToPdfRequest",
    "PostConvertPsToPngRequest",
    "PostConvertPsToTiffRequest",
    "PostConvertPubToJpgRequest",
    "PostConvertPubToPdfRequest",
    "PostConvertPubToPngRequest",
    "PostConvertPubToTiffRequest",
    "PostConvertRtfToHtmlRequest",
    "PostConvertRtfToJpgRequest",
    "PostConvertRtfToPdfRequest",
    "PostConvertRtfToTxtRequest",
    "PostConvertSvgToJpgRequest",
    "PostConvertSvgToPdfRequest",
    "PostConvertSvgToPngRequest",
    "PostConvertSvgToPnmRequest",
    "PostConvertSvgToSvgRequest",
    "PostConvertSvgToTiffRequest",
    "PostConvertSvgToWebpRequest",
    "PostConvertTemplateToDocxRequest",
    "PostConvertTemplateToPdfRequest",
    "PostConvertTiffToJpgRequest",
    "PostConvertTiffToPdfRequest",
    "PostConvertTiffToPngRequest",
    "PostConvertTiffToPnmRequest",
    "PostConvertTiffToSvgRequest",
    "PostConvertTiffToTiffRequest",
    "PostConvertTiffToWebpRequest",
    "PostConvertTxtToJpgRequest",
    "PostConvertTxtToPdfRequest",
    "PostConvertVsdxToJpgRequest",
    "PostConvertVsdxToPdfRequest",
    "PostConvertVsdxToPngRequest",
    "PostConvertVsdxToTiffRequest",
    "PostConvertWebpToGifRequest",
    "PostConvertWebpToJpgRequest",
    "PostConvertWebpToPdfRequest",
    "PostConvertWebpToPngRequest",
    "PostConvertWebpToPnmRequest",
    "PostConvertWebpToSvgRequest",
    "PostConvertWebpToTiffRequest",
    "PostConvertWebpToWebpRequest",
    "PostConvertWebToJpgRequest",
    "PostConvertWebToPdfRequest",
    "PostConvertWebToPngRequest",
    "PostConvertWebToTxtRequest",
    "PostConvertWpdToPdfRequest",
    "PostConvertXlsbToCsvRequest",
    "PostConvertXlsbToPdfRequest",
    "PostConvertXlsToXlsRequest",
    "PostConvertXlsToXlsxRequest",
    "PostConvertXlsxToCsvRequest",
    "PostConvertXlsxToJpgRequest",
    "PostConvertXlsxToPdfRequest",
    "PostConvertXlsxToPngRequest",
    "PostConvertXlsxToProtectRequest",
    "PostConvertXlsxToTiffRequest",
    "PostConvertXlsxToWebpRequest",
    "PostConvertXlsxToXlsxRequest",
    "PostConvertXltxToPdfRequest",
    "PostConvertXmlToDocxRequest",
    "PostConvertZipToExtractRequest",
    "PostUploadRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: upload_file
class PostUploadRequestQuery(StrictModel):
    filename: str | None = Field(default=None, description="The name of the file being uploaded. Required unless the content-disposition header is provided.")
    url: str | None = Field(default=None, description="A remote URL pointing to the file to upload. If provided, the file will be downloaded and stored directly from this location instead of uploading file contents.", json_schema_extra={'format': 'uri'})
class PostUploadRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="The binary file content to upload. Provide the raw file data directly.", json_schema_extra={'format': 'binary'})
class PostUploadRequest(StrictModel):
    """Upload a file to ConvertAPI servers for temporary storage and reuse across multiple conversion operations. The file is securely stored for up to 3 hours and assigned a unique File ID for referencing in subsequent conversion requests."""
    query: PostUploadRequestQuery | None = None
    body: PostUploadRequestBody | None = None

# Operation: download_file
class GetDRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file to download. Must be exactly 32 characters long.", min_length=32, max_length=32)
class GetDRequestQuery(StrictModel):
    download: Literal["attachment", "inline"] | None = Field(default=None, description="Specifies how the file should be delivered: as an attachment for download or inline for viewing in a web browser.")
class GetDRequest(StrictModel):
    """Download or view a file by its ID. Specify whether to download as an attachment or view inline in a web browser."""
    path: GetDRequestPath
    query: GetDRequestQuery | None = None

# Operation: delete_file
class DeleteDRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file to delete. Must be exactly 32 characters.", min_length=32, max_length=32)
class DeleteDRequest(StrictModel):
    """Permanently delete a file from storage. Files are automatically deleted after 3 hours if not manually removed."""
    path: DeleteDRequestPath

# Operation: get_file_metadata
class HeadDRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file. This is a 32-character alphanumeric string that uniquely identifies the file in the system.", min_length=32, max_length=32)
class HeadDRequest(StrictModel):
    """Retrieve metadata and information about a file without downloading its contents. Use this to check file existence, properties, and availability."""
    path: HeadDRequestPath

# Operation: get_usage_statistics
class GetUserStatisticRequestQuery(StrictModel):
    start_date: str = Field(default=..., validation_alias="startDate", serialization_alias="startDate", description="The start date for the statistics query period in YYYY-MM-DD format (inclusive).")
    end_date: str = Field(default=..., validation_alias="endDate", serialization_alias="endDate", description="The end date for the statistics query period in YYYY-MM-DD format (inclusive).")
class GetUserStatisticRequest(StrictModel):
    """Retrieve usage statistics for a specified date range. Returns aggregated data about your account activity and consumption metrics within the provided time period."""
    query: GetUserStatisticRequestQuery

# Operation: convert_image_to_jpg
class PostConvertAiToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert, provided as either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output JPG file. The system automatically sanitizes the filename, appends the .jpg extension, and adds numeric indexing (e.g., image_0.jpg, image_1.jpg) if multiple files are generated.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Specify the color space for the output JPG image.")
class PostConvertAiToJpgRequest(StrictModel):
    """Convert an AI image file to JPG format with optional scaling and color space adjustments. Supports URL or file content input with customizable output naming and image properties."""
    body: PostConvertAiToJpgRequestBody | None = None

# Operation: convert_ai_to_png
class PostConvertAiToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert, provided either as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertAiToPngRequest(StrictModel):
    """Converts Adobe Illustrator (AI) files to PNG format with optional scaling and proportional constraints. Supports both file uploads and URL-based file sources."""
    body: PostConvertAiToPngRequestBody | None = None

# Operation: convert_image_to_pnm
class PostConvertAiToPnmRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert, provided as a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pnm, output_1.pnm) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertAiToPnmRequest(StrictModel):
    """Convert an Adobe Illustrator (AI) image file to Portable Anymap (PNM) format. Supports URL or file content input with optional scaling and proportional constraint controls."""
    body: PostConvertAiToPnmRequestBody | None = None

# Operation: convert_ai_to_svg
class PostConvertAiToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert, provided as either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output SVG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.svg, output_1.svg) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image.")
class PostConvertAiToSvgRequest(StrictModel):
    """Convert Adobe Illustrator (AI) files to Scalable Vector Graphics (SVG) format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""
    body: PostConvertAiToSvgRequestBody | None = None

# Operation: convert_ai_to_tiff
class PostConvertAiToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert, provided as either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output TIFF file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a single multi-page TIFF file instead of separate single-page files.")
class PostConvertAiToTiffRequest(StrictModel):
    """Convert Adobe Illustrator (AI) files to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""
    body: PostConvertAiToTiffRequestBody | None = None

# Operation: convert_image_to_webp
class PostConvertAiToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file. The API automatically sanitizes the filename, appends the correct .webp extension, and adds indexing (e.g., image_0.webp, image_1.webp) for multiple outputs.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Set the color space for the output image.")
class PostConvertAiToWebpRequest(StrictModel):
    """Convert an AI image file to WebP format with optional scaling and color space adjustments. Supports URL or file content input with configurable output naming and image properties."""
    body: PostConvertAiToWebpRequestBody | None = None

# Operation: convert_image_bmp_to_jpg
class PostConvertBmpToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Can be provided as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image.")
class PostConvertBmpToJpgRequest(StrictModel):
    """Convert a BMP image file to JPG format with optional scaling and color space adjustments. Supports both URL and direct file content input."""
    body: PostConvertBmpToJpgRequestBody | None = None

# Operation: convert_image_to_pdf
class PostConvertBmpToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotation angle in degrees to apply to the image. Leave empty to use automatic rotation based on EXIF data in TIFF and JPEG images.", ge=-360, le=360)
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output PDF. Defines how colors are represented in the converted document.")
    color_profile: Literal["default", "isocoatedv2"] | None = Field(default=None, validation_alias="ColorProfile", serialization_alias="ColorProfile", description="Color profile to apply to the output PDF. Some profiles override the ColorSpace setting.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Enable PDF/A-1b compliance for long-term archival and preservation of the output document.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in millimeters (mm).", ge=0, le=500)
    margin_vertical: int | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in millimeters (mm).", ge=0, le=500)
class PostConvertBmpToPdfRequest(StrictModel):
    """Convert BMP images to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input as URL or binary content and generates a named output PDF file."""
    body: PostConvertBmpToPdfRequestBody | None = None

# Operation: convert_image_bmp_to_png
class PostConvertBmpToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL pointing to a BMP file or the raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The system automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., image_0.png, image_1.png) if multiple files are generated.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertBmpToPngRequest(StrictModel):
    """Convert a BMP image file to PNG format with optional scaling and proportional constraint controls. Supports both URL-based and direct file content input."""
    body: PostConvertBmpToPngRequestBody | None = None

# Operation: convert_image_bmp_to_pnm
class PostConvertBmpToPnmRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert, provided either as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension for PNM format, and adds indexing (e.g., output_0.pnm, output_1.pnm) when multiple files are generated.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertBmpToPnmRequest(StrictModel):
    """Convert a BMP image file to PNM (Portable Anymap) format with optional scaling and proportion constraints. Supports both URL-based and direct file content input."""
    body: PostConvertBmpToPnmRequestBody | None = None

# Operation: convert_image_to_svg_bmp
class PostConvertBmpToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming.")
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(default=None, validation_alias="Preset", serialization_alias="Preset", description="A vectorization preset that applies pre-configured tracing settings optimized for different image types. When selected, presets override individual converter options except ColorMode, providing consistent and balanced SVG results.")
    color_mode: Literal["color", "bw"] | None = Field(default=None, validation_alias="ColorMode", serialization_alias="ColorMode", description="Controls whether the image is traced in full color or converted to black-and-white during vectorization.")
    layering: Literal["cutout", "stacked"] | None = Field(default=None, validation_alias="Layering", serialization_alias="Layering", description="Determines how color regions are arranged in the output SVG: cutout mode isolates regions as separate layers, while stacked mode overlays regions on top of each other.")
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(default=None, validation_alias="CurveMode", serialization_alias="CurveMode", description="Defines how shapes are approximated during tracing. Pixel mode follows exact pixel boundaries with minimal smoothing, Polygon mode creates straight-edged paths with sharp corners, and Spline mode generates smooth continuous curves for more natural shapes.")
class PostConvertBmpToSvgRequest(StrictModel):
    """Converts a BMP image to SVG vector format with configurable tracing presets and vectorization options. Supports color or black-and-white output with customizable curve approximation and layer arrangement."""
    body: PostConvertBmpToSvgRequestBody | None = None

# Operation: convert_image_bmp_to_tiff
class PostConvertBmpToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The BMP image file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a multi-page TIFF file combining all converted pages into a single output file.")
class PostConvertBmpToTiffRequest(StrictModel):
    """Convert a BMP image to TIFF format with optional scaling and multi-page output support. Supports both URL and direct file content input."""
    body: PostConvertBmpToTiffRequestBody | None = None

# Operation: convert_image_bmp_to_webp
class PostConvertBmpToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL pointing to a BMP file or the raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output WebP file. The system automatically sanitizes the name, appends the correct file extension, and adds indexing for multiple output files to ensure unique, safe filenames.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image. Choose from standard color profiles to optimize the image for different use cases.")
class PostConvertBmpToWebpRequest(StrictModel):
    """Convert a BMP image file to WebP format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads."""
    body: PostConvertBmpToWebpRequestBody | None = None

# Operation: convert_csv_to_pdf
class PostConvertCsvToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The CSV file to convert. Accepts either a URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input CSV file if it is password-protected.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="Preserve document metadata such as title, author, and keywords in the output PDF.")
    auto_column_fit: bool | None = Field(default=None, validation_alias="AutoColumnFit", serialization_alias="AutoColumnFit", description="Automatically adjust column widths to minimize empty space and optimize table layout in the PDF.")
    header_on_each_page: bool | None = Field(default=None, validation_alias="HeaderOnEachPage", serialization_alias="HeaderOnEachPage", description="Repeat the header row on every page when table content spans multiple pages in the PDF output.")
    thousands_separator: str | None = Field(default=None, validation_alias="ThousandsSeparator", serialization_alias="ThousandsSeparator", description="Character used to separate thousands in numeric values (e.g., comma for 1,000 or period for 1.000).")
    decimal_separator: str | None = Field(default=None, validation_alias="DecimalSeparator", serialization_alias="DecimalSeparator", description="Character used to separate decimal places in numeric values (e.g., period for 1.5 or comma for 1,5).")
    date_format: Literal["us", "iso", "eu", "german", "japanese"] | None = Field(default=None, validation_alias="DateFormat", serialization_alias="DateFormat", description="Date format standard to apply in the output PDF, overriding regional Excel settings to ensure consistency.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Generate a PDF/A-1b compliant document for long-term archival and preservation purposes.")
class PostConvertCsvToPdfRequest(StrictModel):
    """Converts CSV spreadsheet files to PDF format with support for formatting options, metadata preservation, and PDF/A compliance. Handles column fitting, header repetition across pages, and customizable number/date formatting."""
    body: PostConvertCsvToPdfRequestBody | None = None

# Operation: convert_csv_to_xlsx
class PostConvertCsvToXlsxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The CSV file to convert. Can be provided as a file upload or as a URL pointing to the CSV file.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated Excel output file. The system automatically sanitizes the filename, appends the .xlsx extension, and adds numeric suffixes (e.g., _0, _1) if multiple files are generated.")
    delimiter: str | None = Field(default=None, validation_alias="Delimiter", serialization_alias="Delimiter", description="The character used to separate fields in the CSV file. Specify the delimiter that matches your CSV format.")
    cell_type: Literal["general", "text"] | None = Field(default=None, validation_alias="CellType", serialization_alias="CellType", description="Determines how cell values are formatted in the output Excel file. Use 'text' to preserve CSV formatting for dates and numbers, or 'general' for automatic Excel formatting.")
class PostConvertCsvToXlsxRequest(StrictModel):
    """Converts a CSV file to Excel (XLSX) format with configurable field delimiters and cell type formatting. Supports both file uploads and URL-based file sources."""
    body: PostConvertCsvToXlsxRequestBody | None = None

# Operation: convert_djvu_to_jpg
class PostConvertDjvuToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DJVU file to convert. Can be provided as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The system sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., report_0.jpg, report_1.jpg).")
    jpg_type: Literal["jpeg", "jpegcmyk", "jpeggray"] | None = Field(default=None, validation_alias="JpgType", serialization_alias="JpgType", description="JPG encoding type for the output image. Choose between standard JPEG, CMYK color space, or grayscale.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size.")
class PostConvertDjvuToJpgRequest(StrictModel):
    """Converts a DJVU document to JPG image format with configurable output type and scaling options. Supports URL or file content input and generates uniquely named output files."""
    body: PostConvertDjvuToJpgRequestBody | None = None

# Operation: convert_djvu_to_pdf
class PostConvertDjvuToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DJVU file to convert. Can be provided as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming.")
    base_font_size: float | None = Field(default=None, validation_alias="BaseFontSize", serialization_alias="BaseFontSize", description="Base font size in points (pt) for the converted PDF. All text scaling is relative to this value.", ge=1, le=50)
    margin_left: float | None = Field(default=None, validation_alias="MarginLeft", serialization_alias="MarginLeft", description="Left margin in points (pt) for text content on the PDF page.", ge=0, le=200)
    margin_right: float | None = Field(default=None, validation_alias="MarginRight", serialization_alias="MarginRight", description="Right margin in points (pt) for text content on the PDF page.", ge=0, le=200)
    margin_top: float | None = Field(default=None, validation_alias="MarginTop", serialization_alias="MarginTop", description="Top margin in points (pt) for text content on the PDF page.", ge=0, le=200)
    margin_bottom: float | None = Field(default=None, validation_alias="MarginBottom", serialization_alias="MarginBottom", description="Bottom margin in points (pt) for text content on the PDF page.", ge=0, le=200)
class PostConvertDjvuToPdfRequest(StrictModel):
    """Converts a DJVU document to PDF format with customizable layout and typography settings. Supports file input via URL or direct file content with configurable margins and base font sizing."""
    body: PostConvertDjvuToPdfRequestBody | None = None

# Operation: convert_djvu_to_png
class PostConvertDjvuToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DJVU file to convert. Accepts either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to fit the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged.")
class PostConvertDjvuToPngRequest(StrictModel):
    """Convert a DJVU document or image file to PNG format. Supports URL-based or direct file input with optional scaling and proportional resizing controls."""
    body: PostConvertDjvuToPngRequestBody | None = None

# Operation: convert_djvu_to_tiff
class PostConvertDjvuToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DJVU file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions.")
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(default=None, validation_alias="TiffType", serialization_alias="TiffType", description="TIFF compression and color format. Choose from color variants (24-bit or 32-bit with no compression, LZW, or ZIP), grayscale options, or monochrome formats with various compression methods.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a single multi-page TIFF file containing all pages, or separate TIFF files for each page.")
    fill_order: Literal["0", "1"] | None = Field(default=None, validation_alias="FillOrder", serialization_alias="FillOrder", description="Bit order within each byte: 0 for most significant bit first (standard), 1 for least significant bit first.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, preserving quality for smaller images.")
class PostConvertDjvuToTiffRequest(StrictModel):
    """Convert DJVU documents to TIFF image format with configurable output settings including compression type, multi-page support, and scaling options."""
    body: PostConvertDjvuToTiffRequestBody | None = None

# Operation: convert_djvu_to_webp
class PostConvertDjvuToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert, provided as either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct .webp extension, and adds numeric indexing (e.g., output_0.webp, output_1.webp) when multiple files are generated.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions.")
class PostConvertDjvuToWebpRequest(StrictModel):
    """Convert a DJVU document or image to WebP format. Supports URL or file content input with optional scaling and proportional constraint controls."""
    body: PostConvertDjvuToWebpRequestBody | None = None

# Operation: convert_document_to_docx
class PostConvertDocToDocxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct .docx extension, and adds numeric indexing (e.g., document_0.docx, document_1.docx) if multiple files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input document if it is password-protected.")
    update_toc: bool | None = Field(default=None, validation_alias="UpdateToc", serialization_alias="UpdateToc", description="When enabled, automatically updates all tables of content in the converted document to reflect current document structure.")
    update_references: bool | None = Field(default=None, validation_alias="UpdateReferences", serialization_alias="UpdateReferences", description="When enabled, automatically updates all reference fields (cross-references, citations, etc.) in the converted document.")
class PostConvertDocToDocxRequest(StrictModel):
    """Converts a document file to Microsoft Word (.docx) format. Supports password-protected documents and can optionally update tables of content and reference fields in the output."""
    body: PostConvertDocToDocxRequestBody | None = None

# Operation: compare_docx_documents
class PostConvertDocxToCompareRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The primary Word document to be compared. Accepts either a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output comparison file. The system automatically sanitizes the filename, appends the appropriate extension, and adds indexing for multiple output files to ensure unique, safe file naming.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the primary document if it is password-protected.")
    compare_file: str | None = Field(default=None, validation_alias="CompareFile", serialization_alias="CompareFile", description="The Word document to compare against the primary document. Accepts either a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    compare_level: Literal["Word", "Character"] | None = Field(default=None, validation_alias="CompareLevel", serialization_alias="CompareLevel", description="Specifies the granularity level for identifying differences between documents. Word-level comparison detects changes at word boundaries, while character-level comparison identifies changes at individual character positions.")
    compare_formatting: bool | None = Field(default=None, validation_alias="CompareFormatting", serialization_alias="CompareFormatting", description="Include formatting variations such as font, size, color, and style differences in the comparison results.")
    compare_case_changes: bool | None = Field(default=None, validation_alias="CompareCaseChanges", serialization_alias="CompareCaseChanges", description="Include capitalization and case differences in the comparison results.")
    compare_whitespace: bool | None = Field(default=None, validation_alias="CompareWhitespace", serialization_alias="CompareWhitespace", description="Include whitespace differences such as spaces, tabs, and paragraph breaks in the comparison results.")
    compare_tables: bool | None = Field(default=None, validation_alias="CompareTables", serialization_alias="CompareTables", description="Include differences in table content and structure in the comparison results.")
    compare_headers: bool | None = Field(default=None, validation_alias="CompareHeaders", serialization_alias="CompareHeaders", description="Include differences in document headers and footers in the comparison results.")
    compare_footnotes: bool | None = Field(default=None, validation_alias="CompareFootnotes", serialization_alias="CompareFootnotes", description="Include differences in footnotes and endnotes in the comparison results.")
    compare_textboxes: bool | None = Field(default=None, validation_alias="CompareTextboxes", serialization_alias="CompareTextboxes", description="Include differences in text box content in the comparison results.")
    compare_fields: bool | None = Field(default=None, validation_alias="CompareFields", serialization_alias="CompareFields", description="Include differences in document fields in the comparison results.")
    compare_comments: bool | None = Field(default=None, validation_alias="CompareComments", serialization_alias="CompareComments", description="Include differences in comments and annotations in the comparison results.")
    compare_moves: bool | None = Field(default=None, validation_alias="CompareMoves", serialization_alias="CompareMoves", description="Track and report content that has been moved between locations within the documents.")
    accept_revisions: bool | None = Field(default=None, validation_alias="AcceptRevisions", serialization_alias="AcceptRevisions", description="Automatically accept all tracked revisions in the primary document before performing the comparison.")
    revision_author: str | None = Field(default=None, validation_alias="RevisionAuthor", serialization_alias="RevisionAuthor", description="Author name to attribute to the comparison operation in the revision history.")
class PostConvertDocxToCompareRequest(StrictModel):
    """Compare two Word documents and generate a detailed comparison report highlighting differences in content, formatting, and structure. Supports granular comparison options for specific document elements like tables, headers, comments, and more."""
    body: PostConvertDocxToCompareRequestBody | None = None

# Operation: convert_document_to_html
class PostConvertDocxToHtmlRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a file upload (binary content) or a URL pointing to a DOCX file.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated HTML output file. The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.html, document_1.html) if multiple files are generated.")
    inline_images: bool | None = Field(default=None, validation_alias="InlineImages", serialization_alias="InlineImages", description="Whether to embed images from the document directly into the HTML output as inline content, or reference them externally.")
class PostConvertDocxToHtmlRequest(StrictModel):
    """Converts a DOCX document to HTML format with optional inline image embedding. Supports both file uploads and URL-based document sources."""
    body: PostConvertDocxToHtmlRequestBody | None = None

# Operation: convert_document_to_image
class PostConvertDocxToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The API automatically sanitizes the filename, appends the correct JPG extension, and adds numeric indexing (e.g., report_0.jpg, report_1.jpg) when multiple files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password for opening password-protected DOCX documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10 inclusive).")
class PostConvertDocxToJpgRequest(StrictModel):
    """Converts DOCX documents to JPG image format. Supports password-protected documents and selective page range conversion."""
    body: PostConvertDocxToJpgRequestBody | None = None

# Operation: convert_document_to_markdown
class PostConvertDocxToMdRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DOCX file to convert. Can be provided as a URL reference or as binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output Markdown file. The API automatically sanitizes the filename, appends the .md extension, and adds numeric suffixes (e.g., document_0.md, document_1.md) when generating multiple output files.")
class PostConvertDocxToMdRequest(StrictModel):
    """Converts a DOCX document to Markdown format. Accepts a DOCX file via URL or direct file content and returns the converted Markdown output with a customizable filename."""
    body: PostConvertDocxToMdRequestBody | None = None

# Operation: convert_document_docx_to_odt
class PostConvertDocxToOdtRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct .odt extension, and adds numeric indexing (e.g., document_0.odt, document_1.odt) if multiple files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input document if it is password-protected.")
    update_toc: bool | None = Field(default=None, validation_alias="UpdateToc", serialization_alias="UpdateToc", description="When enabled, automatically updates all tables of content in the document during conversion.")
    update_references: bool | None = Field(default=None, validation_alias="UpdateReferences", serialization_alias="UpdateReferences", description="When enabled, automatically updates all reference fields in the document during conversion.")
class PostConvertDocxToOdtRequest(StrictModel):
    """Converts a DOCX document to ODT (OpenDocument Text) format. Supports password-protected documents and can optionally update tables of content and reference fields during conversion."""
    body: PostConvertDocxToOdtRequestBody | None = None

# Operation: convert_document_to_pdf
class PostConvertDocxToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected DOCX documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to include in the output PDF using a range format (e.g., 1-10 for pages 1 through 10).")
    convert_markups: bool | None = Field(default=None, validation_alias="ConvertMarkups", serialization_alias="ConvertMarkups", description="When enabled, includes document markups such as revisions and comments in the converted PDF.")
    convert_tags: bool | None = Field(default=None, validation_alias="ConvertTags", serialization_alias="ConvertTags", description="When enabled, converts document structure tags to improve PDF accessibility for screen readers and assistive technologies.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="When enabled, preserves document metadata (Title, Author, Keywords) as PDF metadata properties.")
    bookmark_mode: Literal["none", "headings", "bookmarks"] | None = Field(default=None, validation_alias="BookmarkMode", serialization_alias="BookmarkMode", description="Controls how bookmarks are generated in the PDF: 'none' disables bookmarks, 'headings' creates bookmarks from document headings, and 'bookmarks' uses existing bookmarks from the source document.")
    update_toc: bool | None = Field(default=None, validation_alias="UpdateToc", serialization_alias="UpdateToc", description="When enabled, automatically updates all tables of content in the document before conversion.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="When enabled, creates a PDF/A-3a compliant document for long-term archival and preservation.")
class PostConvertDocxToPdfRequest(StrictModel):
    """Converts DOCX documents to PDF format with support for advanced formatting options, metadata preservation, and accessibility features. Handles password-protected documents and allows customization of bookmarks, page ranges, and PDF/A compliance."""
    body: PostConvertDocxToPdfRequestBody | None = None

# Operation: convert_document_to_image_png
class PostConvertDocxToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The API sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., report_0.png, report_1.png).")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open protected or encrypted documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using range notation (e.g., 1-10 converts pages 1 through 10).")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintains aspect ratio when scaling the output image to prevent distortion.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotates the output image by the specified angle in degrees.", ge=-360, le=360)
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertDocxToPngRequest(StrictModel):
    """Converts DOCX documents to PNG images with support for page range selection, scaling, and rotation. Handles password-protected documents and generates uniquely named output files."""
    body: PostConvertDocxToPngRequestBody | None = None

# Operation: convert_document_to_protected_word
class PostConvertDocxToProtectRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output file. The system automatically sanitizes the filename, appends the correct file extension, and adds indexing (e.g., filename_0, filename_1) when multiple files are produced from a single input.")
    encrypt_password: str | None = Field(default=None, validation_alias="EncryptPassword", serialization_alias="EncryptPassword", description="Password to encrypt the output Word document. When set, the password will be required to open and view the document content.")
class PostConvertDocxToProtectRequest(StrictModel):
    """Converts a document file to a password-protected Word format. The output file can be encrypted with a password to restrict access and viewing of the document content."""
    body: PostConvertDocxToProtectRequestBody | None = None

# Operation: convert_document_docx_to_rtf
class PostConvertDocxToRtfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert, provided as a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output RTF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.rtf, filename_1.rtf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected DOCX documents.")
    update_toc: bool | None = Field(default=None, validation_alias="UpdateToc", serialization_alias="UpdateToc", description="Automatically update all tables of content in the document during conversion.")
    update_references: bool | None = Field(default=None, validation_alias="UpdateReferences", serialization_alias="UpdateReferences", description="Automatically update all reference fields in the document during conversion.")
class PostConvertDocxToRtfRequest(StrictModel):
    """Converts a DOCX document to RTF format with optional support for password-protected files and automatic updates to tables of content and reference fields."""
    body: PostConvertDocxToRtfRequestBody | None = None

# Operation: convert_document_to_tiff
class PostConvertDocxToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multi-file outputs.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected DOCX documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10).")
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(default=None, validation_alias="TiffType", serialization_alias="TiffType", description="Defines the TIFF compression type and color depth. Options range from color formats (24/32-bit with various compression) to grayscale and monochrome variants.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="When enabled, combines all converted pages into a single multi-page TIFF file. When disabled, generates separate TIFF files for each page.")
    fill_order: Literal["0", "1"] | None = Field(default=None, validation_alias="FillOrder", serialization_alias="FillOrder", description="Specifies the logical bit order within each byte of the TIFF data. Value 0 represents MSB-first (most significant bit first), while 1 represents LSB-first (least significant bit first).")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image to fit specified dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="When enabled, applies scaling only if the input image dimensions exceed the target output dimensions. Prevents upscaling of smaller images.")
class PostConvertDocxToTiffRequest(StrictModel):
    """Converts DOCX documents to TIFF image format with configurable compression, color depth, and page range options. Supports password-protected documents and multi-page TIFF generation."""
    body: PostConvertDocxToTiffRequestBody | None = None

# Operation: convert_document_to_text
class PostConvertDocxToTxtRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output text file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.txt, output_1.txt) for multiple files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input document if it is password-protected.")
    substitutions: bool | None = Field(default=None, validation_alias="Substitutions", serialization_alias="Substitutions", description="When enabled, replaces special symbols with their text equivalents (e.g., © becomes (c)).")
    end_line_char: Literal["crlf", "cr", "lfcr", "lf"] | None = Field(default=None, validation_alias="EndLineChar", serialization_alias="EndLineChar", description="Specifies the line ending character to use in the output text file.")
class PostConvertDocxToTxtRequest(StrictModel):
    """Converts a DOCX document to plain text format with optional character substitutions and configurable line ending styles. Supports password-protected documents and customizable output file naming."""
    body: PostConvertDocxToTxtRequestBody | None = None

# Operation: convert_document_to_webp
class PostConvertDocxToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The system sanitizes the filename, appends the correct extension automatically, and adds indexing (e.g., filename_0.webp, filename_1.webp) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected DOCX documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10).")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image to prevent distortion.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="When enabled, scaling is applied only if the input image dimensions exceed the output dimensions, preventing unnecessary upscaling.")
class PostConvertDocxToWebpRequest(StrictModel):
    """Converts DOCX documents to WebP image format with configurable page range, scaling, and output naming. Supports password-protected documents and flexible scaling options."""
    body: PostConvertDocxToWebpRequestBody | None = None

# Operation: convert_docx_to_xml
class PostConvertDocxToXmlRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Word document to convert. Accepts either a file URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output XML file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.xml, report_1.xml) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input document if it is password-protected.")
    update_toc: bool | None = Field(default=None, validation_alias="UpdateToc", serialization_alias="UpdateToc", description="Whether to automatically update all tables of content in the document during conversion.")
    update_references: bool | None = Field(default=None, validation_alias="UpdateReferences", serialization_alias="UpdateReferences", description="Whether to automatically update all reference fields in the document during conversion.")
    xml_type: Literal["word2003", "flatWordXml", "strictOpenXml"] | None = Field(default=None, validation_alias="XmlType", serialization_alias="XmlType", description="The XML schema type to use when saving the Word document. Word2003 uses legacy XML format, flatWordXml uses a single flat structure, and strictOpenXml uses the modern Office Open XML standard.")
class PostConvertDocxToXmlRequest(StrictModel):
    """Converts a Word document (.docx) to XML format with support for multiple XML schema types. Optionally updates tables of content and reference fields, and supports password-protected documents."""
    body: PostConvertDocxToXmlRequestBody | None = None

# Operation: convert_document_to_jpg
class PostConvertDotxToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The API automatically sanitizes the filename, appends the correct JPG extension, and adds numeric indexing (e.g., document_0.jpg, document_1.jpg) when multiple output files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range format. Only the specified pages will be included in the output.")
class PostConvertDotxToJpgRequest(StrictModel):
    """Converts a DOTX (Word template) document to JPG image format. Supports password-protected documents and selective page range conversion."""
    body: PostConvertDotxToJpgRequestBody | None = None

# Operation: convert_dotx_to_pdf
class PostConvertDotxToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Word document file to convert. Accepts either a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple outputs.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected Word documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10).")
    convert_markups: bool | None = Field(default=None, validation_alias="ConvertMarkups", serialization_alias="ConvertMarkups", description="When enabled, includes document markups such as revisions and comments in the PDF output.")
    convert_tags: bool | None = Field(default=None, validation_alias="ConvertTags", serialization_alias="ConvertTags", description="When enabled, converts document structure tags to improve PDF accessibility for screen readers and assistive technologies.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="When enabled, preserves document metadata (Title, Author, Keywords) as PDF metadata properties.")
    bookmark_mode: Literal["none", "headings", "bookmarks"] | None = Field(default=None, validation_alias="BookmarkMode", serialization_alias="BookmarkMode", description="Controls bookmark generation in the PDF: 'none' disables bookmarks, 'headings' creates bookmarks from document headings, and 'bookmarks' uses existing bookmarks from the source document.")
    update_toc: bool | None = Field(default=None, validation_alias="UpdateToc", serialization_alias="UpdateToc", description="When enabled, automatically updates all tables of content in the document before conversion.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="When enabled, generates a PDF/A-3a compliant document for long-term archival and preservation.")
class PostConvertDotxToPdfRequest(StrictModel):
    """Converts a Word document (.dotx) to PDF format with support for advanced options including markup conversion, accessibility tags, metadata preservation, and PDF/A compliance."""
    body: PostConvertDotxToPdfRequestBody | None = None

# Operation: convert_dwf_to_jpg
class PostConvertDwfToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert, provided as either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple output files.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="The color space for the output image, affecting color representation and file size.")
class PostConvertDwfToJpgRequest(StrictModel):
    """Converts AutoCAD DWF files to JPG image format with support for layer export and color space customization. Accepts file input as URL or binary content and generates optimized image output."""
    body: PostConvertDwfToJpgRequestBody | None = None

# Operation: convert_dwf_to_pdf
class PostConvertDwfToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DWF file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct .pdf extension, and adds numeric indexing (e.g., output_0.pdf, output_1.pdf) when multiple files are produced from a single input.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to preserve and export AutoCAD layers in the PDF output, maintaining the layer structure from the original DWF file.")
    auto_fit: bool | None = Field(default=None, validation_alias="AutoFit", serialization_alias="AutoFit", description="Automatically detects the drawing dimensions and adjusts the output to fit the page size, optionally rotating the page orientation to accommodate the drawing without clipping.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Specifies the color space for the PDF output. Choose truecolors for full color reproduction, grayscale for reduced file size with gray tones, or monochrome for black and white only.")
class PostConvertDwfToPdfRequest(StrictModel):
    """Converts AutoCAD DWF (Design Web Format) files to PDF format with support for layer export and automatic page fitting. The conversion intelligently handles drawing dimensions and color space preferences to produce optimized PDF output."""
    body: PostConvertDwfToPdfRequestBody | None = None

# Operation: convert_dwf_to_png
class PostConvertDwfToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DWF file to convert. Can be provided as a URL or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files to ensure unique identification.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output PNG image. Truecolors preserves full color information, grayscale converts to 256 shades of gray, and monochrome converts to pure black and white.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertDwfToPngRequest(StrictModel):
    """Converts AutoCAD DWF files to PNG image format with support for layer export and color space customization. Accepts file input as URL or binary content and generates uniquely named output files."""
    body: PostConvertDwfToPngRequestBody | None = None

# Operation: convert_dwf_to_svg
class PostConvertDwfToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DWF file to convert. Provide either a publicly accessible URL or the binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output SVG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indices for multiple output files to ensure unique, safe naming.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the SVG output.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output SVG. Choose between full color, grayscale, or monochrome rendering.")
class PostConvertDwfToSvgRequest(StrictModel):
    """Converts AutoCAD DWF files to SVG format with support for layer export and color space customization. Accepts file input as URL or binary content and generates properly named output files."""
    body: PostConvertDwfToSvgRequestBody | None = None

# Operation: convert_dwf_to_tiff
class PostConvertDwfToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DWF file to convert. Provide either a publicly accessible URL or the binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., filename_0.tiff, filename_1.tiff) when multiple files are generated.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output TIFF.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output TIFF image. Choose truecolors for full color output, grayscale for reduced color depth, or monochrome for black and white only.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Whether to combine all pages into a single multi-page TIFF file or generate separate TIFF files for each page.")
class PostConvertDwfToTiffRequest(StrictModel):
    """Converts AutoCAD DWF files to TIFF format with support for layer export, color space configuration, and multi-page output. Accepts file input as URL or binary content and generates sanitized output files with automatic extension handling."""
    body: PostConvertDwfToTiffRequestBody | None = None

# Operation: convert_dwf_to_webp
class PostConvertDwfToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert, provided as either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct WebP extension, and adds numeric indexing (e.g., output_0.webp, output_1.webp) when multiple files are generated from a single input.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="The color space for the output image.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertDwfToWebpRequest(StrictModel):
    """Converts AutoCAD DWF files to WebP format with support for layer export and color space customization. Accepts file input as URL or binary content and generates optimized WebP output."""
    body: PostConvertDwfToWebpRequestBody | None = None

# Operation: convert_dwg_to_jpg
class PostConvertDwgToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DWG file to convert. Provide either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output JPG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple output files.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output JPG image. Choose between full color, grayscale, or monochrome rendering.")
class PostConvertDwgToJpgRequest(StrictModel):
    """Converts AutoCAD DWG files to JPG image format with support for layer export and color space customization. Accepts file input via URL or direct file content."""
    body: PostConvertDwgToJpgRequestBody | None = None

# Operation: convert_dwg_to_pdf
class PostConvertDwgToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DWG file to convert. Can be provided as a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the PDF output.")
    auto_fit: bool | None = Field(default=None, validation_alias="AutoFit", serialization_alias="AutoFit", description="Automatically detects and adjusts the drawing to fit the current page size, including automatic page orientation adjustment if needed.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Specifies the color space for the output PDF. Choose from true color, grayscale, or monochrome rendering.")
class PostConvertDwgToPdfRequest(StrictModel):
    """Converts AutoCAD DWG files to PDF format with support for layer export, automatic page fitting, and color space configuration. Accepts file input as URL or binary content."""
    body: PostConvertDwgToPdfRequestBody | None = None

# Operation: convert_dwg_to_png
class PostConvertDwgToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DWG file to convert. Provide either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.png, filename_1.png) for multiple output files.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output PNG image. Choose between full color, grayscale, or monochrome rendering.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertDwgToPngRequest(StrictModel):
    """Converts AutoCAD DWG files to PNG image format with support for layer export and color space customization. Accepts file input via URL or direct file content."""
    body: PostConvertDwgToPngRequestBody | None = None

# Operation: convert_dwg_to_svg
class PostConvertDwgToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DWG file to convert, provided as either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.svg, output_1.svg) for multiple generated files.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate SVG elements in the output.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="The color space for the output SVG, affecting how colors are rendered.")
class PostConvertDwgToSvgRequest(StrictModel):
    """Converts AutoCAD DWG files to SVG format with support for layer export and color space configuration. Accepts file input via URL or direct file content."""
    body: PostConvertDwgToSvgRequestBody | None = None

# Operation: convert_dwg_to_tiff
class PostConvertDwgToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DWG file to convert. Provide either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multiple output files.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output TIFF image.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Whether to create a multi-page TIFF file combining all content, or separate single-page files.")
class PostConvertDwgToTiffRequest(StrictModel):
    """Converts AutoCAD DWG files to TIFF format with support for layer export, color space configuration, and multi-page output. Accepts file input via URL or direct file content."""
    body: PostConvertDwgToTiffRequestBody | None = None

# Operation: convert_dwg_to_webp
class PostConvertDwgToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DWG file to convert. Provide either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output WebP file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.webp, filename_1.webp) for multiple output files.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output WebP image. Choose between full color, grayscale, or monochrome rendering.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertDwgToWebpRequest(StrictModel):
    """Converts AutoCAD DWG files to WebP format with support for layer export and color space customization. Accepts file input via URL or direct file content."""
    body: PostConvertDwgToWebpRequestBody | None = None

# Operation: convert_dxf_to_jpg
class PostConvertDxfToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DXF file to convert. Provide either a publicly accessible URL or the binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output JPG file. The system automatically sanitizes the name, appends the correct file extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple output files.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="The color space for the output JPG image. Choose between full color, grayscale, or monochrome rendering.")
class PostConvertDxfToJpgRequest(StrictModel):
    """Converts AutoCAD DXF files to JPG image format with support for layer export and color space customization. Accepts file input as URL or binary content and generates optimized image output."""
    body: PostConvertDxfToJpgRequestBody | None = None

# Operation: convert_dxf_to_pdf
class PostConvertDxfToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DXF file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices for multiple output files to ensure unique, safe naming.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to preserve and export AutoCAD layers in the output PDF.")
    auto_fit: bool | None = Field(default=None, validation_alias="AutoFit", serialization_alias="AutoFit", description="Automatically detects the drawing dimensions and adjusts the page size and orientation to fit the content without clipping.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Specifies the color space for the output PDF. Choose truecolors for full color output, grayscale for reduced file size, or monochrome for black and white only.")
class PostConvertDxfToPdfRequest(StrictModel):
    """Converts AutoCAD DXF drawings to PDF format with support for layer export, automatic page fitting, and color space configuration. The conversion intelligently handles multi-page outputs and ensures proper file naming."""
    body: PostConvertDxfToPdfRequestBody | None = None

# Operation: convert_dxf_to_png
class PostConvertDxfToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DXF file to convert, provided either as a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.png, filename_1.png) for multiple output files.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output image.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="The color space for the output PNG image. Choose truecolors for full RGB output, grayscale for 8-bit grayscale, or monochrome for black and white.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertDxfToPngRequest(StrictModel):
    """Converts AutoCAD DXF files to PNG image format with support for layer export and color space customization. Accepts file input as URL or binary content and generates optimized raster images."""
    body: PostConvertDxfToPngRequestBody | None = None

# Operation: convert_dxf_to_svg
class PostConvertDxfToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DXF file to convert. Provide either a publicly accessible URL or the binary file content directly.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.svg, filename_1.svg) for multiple output files.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to preserve and export AutoCAD layer information in the output SVG file.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output SVG. Choose between full color, grayscale, or monochrome rendering.")
class PostConvertDxfToSvgRequest(StrictModel):
    """Converts AutoCAD DXF files to SVG format with support for layer export and color space configuration. Accepts file input as URL or binary content and generates optimized vector graphics output."""
    body: PostConvertDxfToSvgRequestBody | None = None

# Operation: convert_dxf_to_tiff
class PostConvertDxfToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DXF file to convert. Accepts either a URL reference or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., `filename_0.tiff`, `filename_1.tiff`) when generating multiple files.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output TIFF.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output image. Choose between full color, grayscale, or black-and-white rendering.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Whether to combine all output into a single multi-page TIFF file or create separate TIFF files for each page.")
class PostConvertDxfToTiffRequest(StrictModel):
    """Converts DXF (AutoCAD drawing) files to TIFF image format with support for layer export and multi-page output. Useful for archiving technical drawings or sharing CAD designs as raster images."""
    body: PostConvertDxfToTiffRequestBody | None = None

# Operation: convert_dxf_to_webp
class PostConvertDxfToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The DXF file to convert. Can be provided as a URL or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output WebP file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming.")
    export_layers: bool | None = Field(default=None, validation_alias="ExportLayers", serialization_alias="ExportLayers", description="Whether to export AutoCAD layers as separate elements in the output.")
    color_space: Literal["truecolors", "grayscale", "monochrome"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output WebP image. Choose between full color, grayscale, or monochrome rendering.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertDxfToWebpRequest(StrictModel):
    """Converts AutoCAD DXF files to WebP image format with support for layer export and color space customization. Accepts file input as URL or binary content and generates optimized WebP output."""
    body: PostConvertDxfToWebpRequestBody | None = None

# Operation: extract_email_attachments
class PostConvertEmailToExtractRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The email file to process. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output file(s). The system automatically sanitizes the name, appends the appropriate file extension, and adds numeric suffixes (e.g., _0, _1) when multiple files are generated from a single input.")
    use_cid_as_file_name: bool | None = Field(default=None, validation_alias="UseCIDAsFileName", serialization_alias="UseCIDAsFileName", description="When enabled, uses the Content ID (CID) of attachments as the filename instead of the original filename.")
    ignore_inline_attachments: bool | None = Field(default=None, validation_alias="IgnoreInlineAttachments", serialization_alias="IgnoreInlineAttachments", description="When enabled, skips inline attachments such as embedded images and logos, processing only standalone attachments.")
class PostConvertEmailToExtractRequest(StrictModel):
    """Extracts attachments and metadata from email files (EML, MSG, etc.) into structured data. Supports filtering of inline attachments and customizable output file naming."""
    body: PostConvertEmailToExtractRequestBody | None = None

# Operation: extract_email_metadata
class PostConvertEmailToMetadataRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The email file to process. Accepts either a file URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output metadata file. The system automatically sanitizes the filename, appends the appropriate extension, and adds numeric indexing (e.g., metadata_0, metadata_1) when multiple output files are generated from a single input.")
    ignore_inline_attachments: bool | None = Field(default=None, validation_alias="IgnoreInlineAttachments", serialization_alias="IgnoreInlineAttachments", description="When enabled, skips inline attachments such as embedded images and logos during processing, extracting only non-inline attachments.")
class PostConvertEmailToMetadataRequest(StrictModel):
    """Extracts structured metadata from email files, converting email content into organized metadata format. Supports both file uploads and direct content input, with optional filtering of inline attachments."""
    body: PostConvertEmailToMetadataRequestBody | None = None

# Operation: convert_email_to_image
class PostConvertEmlToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The email file to convert. Accepts either a URL reference or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices (e.g., output_0.jpg, output_1.jpg) when multiple files are produced.")
    ignore_attachment_errors: bool | None = Field(default=None, validation_alias="IgnoreAttachmentErrors", serialization_alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors are suppressed and the email is still converted to the target format. Only applies when attachments are being processed.")
    merge: bool | None = Field(default=None, validation_alias="Merge", serialization_alias="Merge", description="When enabled, merges the email body content with converted attachments into a single output. Only applies when attachments are being processed.")
class PostConvertEmlToJpgRequest(StrictModel):
    """Convert an email message (EML format) to JPG image format. Optionally process attachments and merge them with the email body in the output."""
    body: PostConvertEmlToJpgRequestBody | None = None

# Operation: convert_eml_to_pdf
class PostConvertEmlToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The EML file to convert. Accepts either a URL reference or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., report_0.pdf, report_1.pdf) when multiple files are produced.")
    ignore_attachment_errors: bool | None = Field(default=None, validation_alias="IgnoreAttachmentErrors", serialization_alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors are ignored and the email body is still converted to PDF. Only applies when attachments are being converted.")
    merge: bool | None = Field(default=None, validation_alias="Merge", serialization_alias="Merge", description="When enabled, merges the email body with converted attachments into a single PDF document. Only applies when attachments are being converted.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="When enabled, creates a PDF/A-1b compliant document, which is an ISO-standardized archival format suitable for long-term preservation.")
    margin_top: dict | None = Field(default=None, validation_alias="MarginTop", serialization_alias="MarginTop", description="Set the page top margin in millimeters (mm).", ge=0, le=500)
    margin_right: int | None = Field(default=None, validation_alias="MarginRight", serialization_alias="MarginRight", description="Set the page right margin in millimeters (mm).", ge=0, le=500)
    margin_bottom: int | None = Field(default=None, validation_alias="MarginBottom", serialization_alias="MarginBottom", description="Set the page bottom margin in millimeters (mm).", ge=0, le=500)
    margin_left: int | None = Field(default=None, validation_alias="MarginLeft", serialization_alias="MarginLeft", description="Set the page left margin in millimeters (mm).", ge=0, le=500)
class PostConvertEmlToPdfRequest(StrictModel):
    """Converts an EML (email) file to PDF format, with optional support for embedding attachments and creating PDF/A-1b compliant documents."""
    body: PostConvertEmlToPdfRequestBody | None = None

# Operation: convert_email_to_png
class PostConvertEmlToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The email file to convert. Accepts either a URL reference or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices (e.g., output_0.png, output_1.png) when multiple files are generated.")
    ignore_attachment_errors: bool | None = Field(default=None, validation_alias="IgnoreAttachmentErrors", serialization_alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors are ignored and the email is still converted to PNG. Only applies when attachments are being converted.")
    merge: bool | None = Field(default=None, validation_alias="Merge", serialization_alias="Merge", description="When enabled, merges the email body with converted attachments into the final PNG output. Only applies when attachments are being converted.")
class PostConvertEmlToPngRequest(StrictModel):
    """Converts an email message (EML format) to PNG image format, with optional support for converting and merging attachments into the output."""
    body: PostConvertEmlToPngRequestBody | None = None

# Operation: convert_eml_to_tiff
class PostConvertEmlToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The email file to convert. Accepts either a URL reference or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., `document_0.tiff`, `document_1.tiff`) when multiple files are generated.")
    ignore_attachment_errors: bool | None = Field(default=None, validation_alias="IgnoreAttachmentErrors", serialization_alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors are ignored and the email body is still converted to TIFF. Only applies when attachments are being converted.")
    merge: bool | None = Field(default=None, validation_alias="Merge", serialization_alias="Merge", description="When enabled, merges the email body with converted attachments into the output TIFF file(s). Only applies when attachments are being converted.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="When enabled, creates a single multi-page TIFF file containing all content. When disabled, generates separate TIFF files for each page.")
class PostConvertEmlToTiffRequest(StrictModel):
    """Converts email messages (EML format) to TIFF image files, with optional support for merging email body with attachments into a single or multi-page document."""
    body: PostConvertEmlToTiffRequestBody | None = None

# Operation: convert_eml_to_webp
class PostConvertEmlToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The EML file to convert, provided as either a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output WebP file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.webp, output_1.webp) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the output dimensions.")
class PostConvertEmlToWebpRequest(StrictModel):
    """Converts an EML (email) file to WebP image format. Supports URL or file content input with optional scaling and proportional constraint controls."""
    body: PostConvertEmlToWebpRequestBody | None = None

# Operation: convert_eps_to_jpg
class PostConvertEpsToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The EPS file to convert, provided either as a URL or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output JPG file. The API automatically sanitizes the filename, appends the correct .jpg extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) when multiple files are generated from a single input.")
class PostConvertEpsToJpgRequest(StrictModel):
    """Converts an EPS (Encapsulated PostScript) file to JPG format. Accepts file input as a URL or binary content and generates a converted JPG output file with automatic naming."""
    body: PostConvertEpsToJpgRequestBody | None = None

# Operation: convert_eps_to_pdf
class PostConvertEpsToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The EPS file to convert. Provide either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system sanitizes the filename, appends the correct extension, and adds indexing for multiple output files (e.g., report_0.pdf, report_1.pdf).")
    pdf_version: Literal["1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "2.0"] | None = Field(default=None, validation_alias="PdfVersion", serialization_alias="PdfVersion", description="PDF specification version to use for the output document.")
    pdf_resolution: int | None = Field(default=None, validation_alias="PdfResolution", serialization_alias="PdfResolution", description="Output resolution in dots per inch (DPI). Higher values produce better quality but larger file sizes.", ge=10, le=2400)
    pdf_title: str | None = Field(default=None, validation_alias="PdfTitle", serialization_alias="PdfTitle", description="Custom title for the PDF document metadata. Use a single quote and space (' ') to remove the title entirely.")
    pdf_subject: str | None = Field(default=None, validation_alias="PdfSubject", serialization_alias="PdfSubject", description="Custom subject for the PDF document metadata. Use a single quote and space (' ') to remove the subject entirely.")
    pdf_author: str | None = Field(default=None, validation_alias="PdfAuthor", serialization_alias="PdfAuthor", description="Custom author name for the PDF document metadata. Use a single quote and space (' ') to remove the author entirely.")
    pdf_keywords: str | None = Field(default=None, validation_alias="PdfKeywords", serialization_alias="PdfKeywords", description="Custom keywords for the PDF document metadata, typically used for searchability. Use a single quote and space (' ') to remove keywords entirely.")
    open_page: int | None = Field(default=None, validation_alias="OpenPage", serialization_alias="OpenPage", description="Page number where the PDF should open when first displayed in a viewer.", ge=1, le=3000)
    open_zoom: Literal["Default", "ActualSize", "FitPage", "FitWidth", "FitHeight", "FitVisible", "25", "50", "75", "100", "125", "150", "200", "400", "800", "1600", "2400", "3200", "6400"] | None = Field(default=None, validation_alias="OpenZoom", serialization_alias="OpenZoom", description="Default zoom level when opening the PDF in a viewer. Choose from preset percentages or fit-to-page options.")
    color_space: Literal["Default", "RGB", "CMYK", "Gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the PDF output. RGB is suitable for screen viewing, CMYK for professional printing, and Gray for grayscale documents.")
class PostConvertEpsToPdfRequest(StrictModel):
    """Convert EPS (Encapsulated PostScript) files to PDF format with customizable output properties including resolution, metadata, and viewer settings."""
    body: PostConvertEpsToPdfRequestBody | None = None

# Operation: convert_eps_to_png
class PostConvertEpsToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The EPS file to convert, provided either as a URL or as binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output PNG file. The API automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., output_0.png, output_1.png) when multiple files are generated from a single input.")
class PostConvertEpsToPngRequest(StrictModel):
    """Converts an EPS (Encapsulated PostScript) file to PNG format. Accepts file input as a URL or binary file content and generates a PNG output file with optional custom naming."""
    body: PostConvertEpsToPngRequestBody | None = None

# Operation: convert_eps_to_tiff
class PostConvertEpsToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The EPS file to convert, provided either as a URL reference or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output TIFF file. The system automatically sanitizes the filename, appends the correct .tiff extension, and adds numeric indexing (e.g., output_0.tiff, output_1.tiff) when multiple files are generated from a single input.")
class PostConvertEpsToTiffRequest(StrictModel):
    """Converts an EPS (Encapsulated PostScript) file to TIFF (Tagged Image File Format) image format. Accepts file input as a URL or binary content and generates a properly named output file."""
    body: PostConvertEpsToTiffRequestBody | None = None

# Operation: convert_epub_to_jpg
class PostConvertEpubToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The EPUB file to convert. Accepts either a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices for multiple outputs (e.g., report_0.jpg, report_1.jpg).")
    jpg_type: Literal["jpeg", "jpegcmyk", "jpeggray"] | None = Field(default=None, validation_alias="JpgType", serialization_alias="JpgType", description="Color mode for the output JPG image. Choose between standard RGB (jpeg), CMYK for print (jpegcmyk), or grayscale (jpeggray).")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to specified dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output size, preventing upscaling of smaller images.")
class PostConvertEpubToJpgRequest(StrictModel):
    """Convert EPUB documents to JPG image format with configurable output settings. Supports multiple JPG color modes and optional image scaling to optimize file size and dimensions."""
    body: PostConvertEpubToJpgRequestBody | None = None

# Operation: convert_epub_to_pdf
class PostConvertEpubToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The EPUB file to convert. Accepts either a direct file upload or a URL pointing to the EPUB file.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output PDF file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric suffixes if multiple files are generated.")
    base_font_size: float | None = Field(default=None, validation_alias="BaseFontSize", serialization_alias="BaseFontSize", description="Base font size in points (pt) for the PDF. All text scales relative to this value.", ge=1, le=50)
    margin_left: float | None = Field(default=None, validation_alias="MarginLeft", serialization_alias="MarginLeft", description="Left margin width in points (pt) for the PDF page content.", ge=0, le=200)
    margin_right: float | None = Field(default=None, validation_alias="MarginRight", serialization_alias="MarginRight", description="Right margin width in points (pt) for the PDF page content.", ge=0, le=200)
    margin_top: float | None = Field(default=None, validation_alias="MarginTop", serialization_alias="MarginTop", description="Top margin width in points (pt) for the PDF page content.", ge=0, le=200)
    margin_bottom: float | None = Field(default=None, validation_alias="MarginBottom", serialization_alias="MarginBottom", description="Bottom margin width in points (pt) for the PDF page content.", ge=0, le=200)
class PostConvertEpubToPdfRequest(StrictModel):
    """Converts an EPUB file to PDF format with customizable typography and page layout settings. Supports both file uploads and URL-based sources with options to control font sizing and margins."""
    body: PostConvertEpubToPdfRequestBody | None = None

# Operation: convert_epub_to_png
class PostConvertEpubToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The EPUB file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., output_0.png, output_1.png) when multiple files are generated from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
class PostConvertEpubToPngRequest(StrictModel):
    """Convert EPUB documents to PNG image format. Supports URL or file content input with optional scaling and proportional constraint controls."""
    body: PostConvertEpubToPngRequestBody | None = None

# Operation: convert_epub_to_tiff
class PostConvertEpubToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The EPUB file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions.")
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(default=None, validation_alias="TiffType", serialization_alias="TiffType", description="TIFF compression and color format. Choose between color variants (24-bit or 32-bit with no compression, LZW, or ZIP), grayscale options, or monochrome formats with various compression methods.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a single multi-page TIFF file containing all pages, or separate TIFF files for each page.")
    fill_order: Literal["0", "1"] | None = Field(default=None, validation_alias="FillOrder", serialization_alias="FillOrder", description="Bit order within each byte: 0 for most significant bit first (MSB), 1 for least significant bit first (LSB).")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to fit specified dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged.")
class PostConvertEpubToTiffRequest(StrictModel):
    """Convert EPUB documents to TIFF image format with configurable output settings including multi-page support, compression type, and scaling options."""
    body: PostConvertEpubToTiffRequestBody | None = None

# Operation: convert_epub_to_webp
class PostConvertEpubToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The EPUB file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The API sanitizes the filename, appends the correct extension automatically, and adds indexing (e.g., output_0.webp, output_1.webp) for multiple files from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
class PostConvertEpubToWebpRequest(StrictModel):
    """Convert EPUB documents to WebP image format. Supports URL or file content input with optional scaling and proportional constraint controls."""
    body: PostConvertEpubToWebpRequestBody | None = None

# Operation: convert_file_to_pdf
class PostConvertFileToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert, provided either as a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The API automatically sanitizes the filename, appends the .pdf extension, and adds numeric indexing (e.g., filename_0.pdf, filename_1.pdf) when multiple output files are generated from a single input.")
class PostConvertFileToPdfRequest(StrictModel):
    """Converts a file to PDF format from a provided file or URL. Supports various input formats and generates uniquely named output files with automatic extension handling."""
    body: PostConvertFileToPdfRequestBody | None = None

# Operation: compress_files_to_archive
class PostConvertFileToZipRequestBody(StrictModel):
    files: list[str] | None = Field(default=None, validation_alias="Files", serialization_alias="Files", description="Files to compress into the archive. Each file can be provided as a URL or raw file content. When using query or multipart parameters, append an index suffix to each file parameter (e.g., Files[0], Files[1]).")
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output ZIP archive file. The system automatically sanitizes the filename to remove unsafe characters and appends the .zip extension. For multiple input files, output files are automatically indexed (e.g., archive_0.zip, archive_1.zip).")
    compression_level: Literal["Optimal", "Medium", "Fastest", "NoCompression"] | None = Field(default=None, validation_alias="CompressionLevel", serialization_alias="CompressionLevel", description="Compression algorithm intensity for the archive. Controls the trade-off between file size and compression speed.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Optional password to encrypt and protect the ZIP archive. When set, the archive requires this password to extract.")
class PostConvertFileToZipRequest(StrictModel):
    """Converts and compresses multiple files into a single ZIP archive with optional password protection. Supports files provided as URLs or direct content."""
    body: PostConvertFileToZipRequestBody | None = None

# Operation: convert_gif_animation
class PostConvertGifToGifRequestBody(StrictModel):
    files: list[str] | None = Field(default=None, validation_alias="Files", serialization_alias="Files", description="GIF files to convert. Accepts URLs or file content. When using query or multipart parameters, append an index suffix (e.g., Files[0], Files[1]) to distinguish multiple files.")
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output file(s). The API sanitizes the filename, appends the appropriate extension, and automatically indexes multiple outputs (e.g., output_0.gif, output_1.gif) to ensure unique identifiers.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    animation_delay: int | None = Field(default=None, validation_alias="AnimationDelay", serialization_alias="AnimationDelay", description="Time interval between animation frames, specified in hundredths of a second. Controls playback speed of the GIF animation.", ge=0, le=20000)
    animation_iterations: int | None = Field(default=None, validation_alias="AnimationIterations", serialization_alias="AnimationIterations", description="Number of times the animation loops. Set to zero for infinite looping.", ge=0, le=1000)
class PostConvertGifToGifRequest(StrictModel):
    """Convert GIF files with customizable animation settings including frame delay and loop iterations. Supports URL or file content input with optional output filename specification."""
    body: PostConvertGifToGifRequestBody | None = None

# Operation: convert_gif_to_jpg
class PostConvertGifToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The GIF image file to convert. Accepts either a file upload or a URL pointing to the source image.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when resizing the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only resize the image if the input dimensions exceed the target output dimensions.")
    alpha_color: str | None = Field(default=None, validation_alias="AlphaColor", serialization_alias="AlphaColor", description="Replace transparent areas with a solid color. Accepts RGBA or CMYK hex color codes, or standard color names.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image.")
class PostConvertGifToJpgRequest(StrictModel):
    """Convert GIF images to JPG format with optional scaling, color space adjustment, and transparency handling. Supports both file uploads and URL-based inputs."""
    body: PostConvertGifToJpgRequestBody | None = None

# Operation: convert_gif_to_pdf
class PostConvertGifToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The GIF image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pdf, output_1.pdf) for multiple files.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotation angle in degrees for the output image. Use a value between -360 and 360, or leave empty to apply automatic rotation based on EXIF data if available.", ge=-360, le=360)
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output PDF. Defines how colors are represented in the converted document.")
    color_profile: Literal["default", "isocoatedv2"] | None = Field(default=None, validation_alias="ColorProfile", serialization_alias="ColorProfile", description="Color profile for the output PDF. Some profiles override the ColorSpace setting. Use 'isocoatedv2' for ISO Coated v2 profile compliance.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Enable PDF/A-1b compliance for long-term archival and preservation of the output PDF document.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in millimeters (mm).", ge=0, le=500)
    margin_vertical: int | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in millimeters (mm).", ge=0, le=500)
class PostConvertGifToPdfRequest(StrictModel):
    """Convert GIF images to PDF format with support for rotation, color space configuration, and PDF/A compliance. Handles single or multiple image conversions with automatic file naming."""
    body: PostConvertGifToPdfRequestBody | None = None

# Operation: convert_gif_to_png
class PostConvertGifToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The GIF image file to convert. Accepts either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The system automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., output_0.png, output_1.png) when generating multiple files from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertGifToPngRequest(StrictModel):
    """Convert a GIF image to PNG format with optional scaling and proportional constraint controls. Supports both URL-based and direct file content input."""
    body: PostConvertGifToPngRequestBody | None = None

# Operation: convert_gif_to_pnm
class PostConvertGifToPnmRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The GIF image file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNM file. The system automatically sanitizes the filename, appends the correct .pnm extension, and adds numeric indexing (e.g., output_0.pnm, output_1.pnm) if multiple files are generated.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output size, leaving smaller images unchanged.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertGifToPnmRequest(StrictModel):
    """Convert a GIF image file to PNM (Portable Anymap) format with optional scaling and proportion constraints. Supports both URL-based and direct file content input."""
    body: PostConvertGifToPnmRequestBody | None = None

# Operation: convert_gif_to_svg
class PostConvertGifToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The GIF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated SVG output file. The system automatically sanitizes the filename, appends the correct .svg extension, and adds numeric indexing if multiple files are produced.")
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(default=None, validation_alias="Preset", serialization_alias="Preset", description="Vectorization preset that applies pre-configured tracing settings optimized for different image types. When selected, presets override all other converter options except ColorMode.")
    color_mode: Literal["color", "bw"] | None = Field(default=None, validation_alias="ColorMode", serialization_alias="ColorMode", description="Output color mode for the traced SVG. Choose between full color or black-and-white vectorization.")
    layering: Literal["cutout", "stacked"] | None = Field(default=None, validation_alias="Layering", serialization_alias="Layering", description="Arrangement method for color regions in the output SVG. Cutout mode creates isolated layers, while stacked mode overlays regions on top of each other.")
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(default=None, validation_alias="CurveMode", serialization_alias="CurveMode", description="Shape approximation method during vectorization. Pixel mode traces exact pixel boundaries with minimal smoothing, Polygon creates straight-edged paths with sharp corners, and Spline generates smooth continuous curves.")
class PostConvertGifToSvgRequest(StrictModel):
    """Converts GIF images to scalable vector graphics (SVG) format using configurable vectorization presets and tracing options. Supports both color and black-and-white output with customizable layering and curve approximation modes."""
    body: PostConvertGifToSvgRequestBody | None = None

# Operation: convert_gif_to_tiff
class PostConvertGifToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The GIF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a single multi-page TIFF file instead of separate files for each frame.")
class PostConvertGifToTiffRequest(StrictModel):
    """Convert GIF images to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""
    body: PostConvertGifToTiffRequestBody | None = None

# Operation: convert_gif_to_webp
class PostConvertGifToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The GIF image file to convert. Accepts either a file upload or a URL pointing to the source image.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output WebP file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image. Use 'default' to preserve the source color space, or specify a target color space for conversion.")
class PostConvertGifToWebpRequest(StrictModel):
    """Convert GIF images to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""
    body: PostConvertGifToWebpRequestBody | None = None

# Operation: convert_heic_to_jpg
class PostConvertHeicToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple outputs.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions.")
    alpha_color: str | None = Field(default=None, validation_alias="AlphaColor", serialization_alias="AlphaColor", description="Color to apply to transparent areas. Accepts RGBA or CMYK hex strings, or standard color names.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output image.")
class PostConvertHeicToJpgRequest(StrictModel):
    """Convert HEIC image files to JPG format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads with customizable output naming and image properties."""
    body: PostConvertHeicToJpgRequestBody | None = None

# Operation: convert_image_heic_to_jxl
class PostConvertHeicToJxlRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a file upload or a URL pointing to the source image.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output file. The API automatically sanitizes the name, appends the correct file extension, and adds indexing for multiple output files to ensure unique, safe filenames.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image. Choose from standard color profiles or use the default setting.")
class PostConvertHeicToJxlRequest(StrictModel):
    """Convert HEIC image files to JXL (JPEG XL) format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""
    body: PostConvertHeicToJxlRequestBody | None = None

# Operation: convert_heic_to_pdf
class PostConvertHeicToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The HEIC image file to convert. Provide either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotate the output image by the specified degrees. Leave empty to use automatic rotation based on EXIF data if available.", ge=-360, le=360)
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Set the color space for the output PDF. Choose from standard color space options or use default for automatic selection.")
    color_profile: Literal["default", "isocoatedv2"] | None = Field(default=None, validation_alias="ColorProfile", serialization_alias="ColorProfile", description="Apply a specific color profile to the output PDF. Some profiles may override the ColorSpace setting.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Generate a PDF/A-1b compliant document for long-term archival and preservation.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in millimeters (mm).", ge=0, le=500)
    margin_vertical: int | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in millimeters (mm).", ge=0, le=500)
class PostConvertHeicToPdfRequest(StrictModel):
    """Convert HEIC image files to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input via URL or direct file content."""
    body: PostConvertHeicToPdfRequestBody | None = None

# Operation: convert_heic_to_png
class PostConvertHeicToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert, provided either as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.png, image_1.png) for multiple outputs from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertHeicToPngRequest(StrictModel):
    """Convert HEIC image files to PNG format with optional scaling and proportional constraints. Supports both URL-based and direct file content input."""
    body: PostConvertHeicToPngRequestBody | None = None

# Operation: convert_image_heic_to_pnm
class PostConvertHeicToPnmRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct .pnm extension, and adds numeric indexing (e.g., output_0.pnm, output_1.pnm) when multiple files are generated.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertHeicToPnmRequest(StrictModel):
    """Convert HEIC image files to PNM (Portable Anymap) format with optional scaling and proportional constraint controls."""
    body: PostConvertHeicToPnmRequestBody | None = None

# Operation: convert_heic_to_svg
class PostConvertHeicToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The HEIC image file to convert. Accepts either a URL pointing to the image or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output SVG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.svg, image_1.svg) for multiple outputs.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to fit specified dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output SVG image.")
class PostConvertHeicToSvgRequest(StrictModel):
    """Convert HEIC image files to SVG vector format. Supports URL or direct file content input with optional scaling and color space configuration."""
    body: PostConvertHeicToSvgRequestBody | None = None

# Operation: convert_heic_to_tiff
class PostConvertHeicToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the name, appends the correct extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multiple output files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a multi-page TIFF file when converting. If disabled, creates a single-page TIFF.")
class PostConvertHeicToTiffRequest(StrictModel):
    """Convert HEIC image files to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""
    body: PostConvertHeicToTiffRequestBody | None = None

# Operation: convert_image_heic_to_webp
class PostConvertHeicToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., image_0.webp, image_1.webp).")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image.")
class PostConvertHeicToWebpRequest(StrictModel):
    """Convert HEIC image files to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""
    body: PostConvertHeicToWebpRequestBody | None = None

# Operation: convert_heif_to_jpg
class PostConvertHeifToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.jpg, image_1.jpg) for multiple outputs from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size.")
    alpha_color: str | None = Field(default=None, validation_alias="AlphaColor", serialization_alias="AlphaColor", description="Specify a color to replace transparent areas in the image. Accepts RGBA or CMYK hex color codes, or standard color names.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image.")
class PostConvertHeifToJpgRequest(StrictModel):
    """Convert HEIF image files to JPG format with optional scaling and color space adjustments. Supports both URL and direct file content input."""
    body: PostConvertHeifToJpgRequestBody | None = None

# Operation: convert_heif_to_pdf
class PostConvertHeifToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The HEIF image file to convert. Provide either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric indexing (e.g., output_0.pdf, output_1.pdf) when multiple files are generated.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotation angle in degrees for the output image. Specify a value between -360 and 360, or leave empty to automatically rotate based on EXIF data in TIFF and JPEG images.", ge=-360, le=360)
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output PDF. Choose from standard color spaces or use the default setting.")
    color_profile: Literal["default", "isocoatedv2"] | None = Field(default=None, validation_alias="ColorProfile", serialization_alias="ColorProfile", description="Color profile to apply to the output PDF. Some profiles may override the ColorSpace setting.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Enable PDF/A-1b compliance for the output document, ensuring long-term archival compatibility.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in millimeters (mm).", ge=0, le=500)
    margin_vertical: int | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in millimeters (mm).", ge=0, le=500)
class PostConvertHeifToPdfRequest(StrictModel):
    """Convert HEIF image files to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input as URL or binary content and generates a properly named output PDF file."""
    body: PostConvertHeifToPdfRequestBody | None = None

# Operation: convert_html_to_docx
class PostConvertHtmlToDocxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The HTML content to convert, provided either as a publicly accessible URL or as raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The desired name for the output DOCX file. The API automatically sanitizes the filename, appends the correct .docx extension, and adds numeric suffixes (e.g., _0, _1) if multiple files are generated from a single input.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in inches (in).", ge=0, le=500)
    margin_vertical: float | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in inches (in).", ge=0, le=500)
class PostConvertHtmlToDocxRequest(StrictModel):
    """Converts HTML content to DOCX format. Accepts HTML as a URL or raw file content and generates a properly formatted Word document with the specified output filename."""
    body: PostConvertHtmlToDocxRequestBody | None = None

# Operation: convert_html_to_jpg
class PostConvertHtmlToJpgRequestBody(StrictModel):
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output JPG file(s). The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple files to ensure unique identification.")
    ad_block: bool | None = Field(default=None, validation_alias="AdBlock", serialization_alias="AdBlock", description="Block advertisements from appearing in the converted page.")
    cookie_consent_block: bool | None = Field(default=None, validation_alias="CookieConsentBlock", serialization_alias="CookieConsentBlock", description="Automatically remove EU cookie consent warnings and related cookie banners from web pages before conversion.")
    cookies: str | None = Field(default=None, validation_alias="Cookies", serialization_alias="Cookies", description="Set additional cookies to include in the page request. Separate multiple cookies with semicolons.")
    java_script: bool | None = Field(default=None, validation_alias="JavaScript", serialization_alias="JavaScript", description="Enable JavaScript execution during page rendering. When enabled, scripts will run before conversion begins.")
    wait_element: str | None = Field(default=None, validation_alias="WaitElement", serialization_alias="WaitElement", description="CSS selector for a DOM element. The converter will wait for this element to appear in the DOM before starting the conversion process.")
    user_css: str | None = Field(default=None, validation_alias="UserCss", serialization_alias="UserCss", description="Custom CSS rules to apply to the page before conversion. These styles are injected into the page rendering context.")
    css_media_type: str | None = Field(default=None, validation_alias="CssMediaType", serialization_alias="CssMediaType", description="CSS media type to use during conversion. Supports standard types (screen, print) and custom media types.")
    headers: str | None = Field(default=None, validation_alias="Headers", serialization_alias="Headers", description="Custom HTTP headers to include in the page request. Separate multiple headers with pipe characters (|) and use colon (:) to separate header names from values.")
    zoom: float | None = Field(default=None, validation_alias="Zoom", serialization_alias="Zoom", description="Set the default zoom level for webpage rendering. Values between 0.1 and 10 are supported.", ge=0.1, le=10)
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The HTML content or URL to convert. Accepts either a web URL or raw HTML file content.", json_schema_extra={'format': 'binary'})
class PostConvertHtmlToJpgRequest(StrictModel):
    """Convert HTML content or web pages to JPG image format. Supports URL-based or direct HTML content conversion with advanced rendering options including JavaScript execution, CSS customization, and DOM element waiting."""
    body: PostConvertHtmlToJpgRequestBody | None = None

# Operation: convert_html_to_markdown
class PostConvertHtmlToMdRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The HTML content to convert. Provide either a URL pointing to an HTML file or the raw HTML content as a string.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated Markdown output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming.")
    github_flavored: bool | None = Field(default=None, validation_alias="GithubFlavored", serialization_alias="GithubFlavored", description="Enable GitHub-flavored Markdown (GFM) syntax in the output for enhanced compatibility with GitHub platforms.")
    remove_comments: bool | None = Field(default=None, validation_alias="RemoveComments", serialization_alias="RemoveComments", description="Remove HTML comment tags from the output Markdown document.")
    unsupported_tags: Literal["PassThrough", "Drop", "Bypass", "Fail"] | None = Field(default=None, validation_alias="UnsupportedTags", serialization_alias="UnsupportedTags", description="Define how to handle HTML tags that are not supported in Markdown conversion. Choose to pass through as-is, drop entirely, bypass processing, or fail on unsupported tags.")
    pass_through_tags: str | None = Field(default=None, validation_alias="PassThroughTags", serialization_alias="PassThroughTags", description="Specify HTML tags to pass through unchanged to the Markdown output. Provide tag names as a comma-separated list. Only applies when UnsupportedTags is set to PassThrough.")
    list_bullet_char: str | None = Field(default=None, validation_alias="ListBulletChar", serialization_alias="ListBulletChar", description="Set the character used for bullet points in unordered lists within the Markdown output.")
class PostConvertHtmlToMdRequest(StrictModel):
    """Convert HTML content or files to Markdown format with customizable formatting options including GitHub-flavored markdown support and tag handling rules."""
    body: PostConvertHtmlToMdRequestBody | None = None

# Operation: convert_html_to_pdf
class PostConvertHtmlToPdfRequestBody(StrictModel):
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the generated PDF output file. The system sanitizes the filename, appends the .pdf extension automatically, and adds numeric suffixes (e.g., report_0.pdf, report_1.pdf) when multiple files are generated.")
    ad_block: bool | None = Field(default=None, validation_alias="AdBlock", serialization_alias="AdBlock", description="Block advertisements from appearing in the converted PDF.")
    cookie_consent_block: bool | None = Field(default=None, validation_alias="CookieConsentBlock", serialization_alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and related warnings from the page before conversion.")
    cookies: str | None = Field(default=None, validation_alias="Cookies", serialization_alias="Cookies", description="Set additional cookies to include in the page request. Separate multiple cookies with semicolons.")
    java_script: bool | None = Field(default=None, validation_alias="JavaScript", serialization_alias="JavaScript", description="Enable JavaScript execution during page rendering. Disable if the page contains problematic scripts.")
    wait_element: str | None = Field(default=None, validation_alias="WaitElement", serialization_alias="WaitElement", description="CSS selector for a DOM element that must appear before conversion begins. Useful for waiting on dynamically loaded content.")
    user_css: str | None = Field(default=None, validation_alias="UserCss", serialization_alias="UserCss", description="Custom CSS rules to apply to the page before conversion. Useful for hiding elements or adjusting layout.")
    css_media_type: str | None = Field(default=None, validation_alias="CssMediaType", serialization_alias="CssMediaType", description="CSS media type to use during conversion. Controls how stylesheets are applied (e.g., screen, print, or custom types).")
    headers: str | None = Field(default=None, validation_alias="Headers", serialization_alias="Headers", description="Custom HTTP headers to include in the page request. Separate multiple headers with pipe characters and use colon to separate header names from values.")
    load_lazy_content: bool | None = Field(default=None, validation_alias="LoadLazyContent", serialization_alias="LoadLazyContent", description="Load images that are only visible when scrolled into view (lazy-loaded images).")
    viewport_width: int | None = Field(default=None, validation_alias="ViewportWidth", serialization_alias="ViewportWidth", description="Browser viewport width in pixels. Affects how the page is rendered and reflowed.", ge=200, le=4000)
    viewport_height: int | None = Field(default=None, validation_alias="ViewportHeight", serialization_alias="ViewportHeight", description="Browser viewport height in pixels. Affects how the page is rendered and reflowed.", ge=200, le=4000)
    respect_viewport: bool | None = Field(default=None, validation_alias="RespectViewport", serialization_alias="RespectViewport", description="If true, the PDF renders as it appears in the browser. If false, uses Chrome's print-to-PDF behavior which may adjust layout.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specify which pages to convert using ranges (e.g., 1-10) or individual page numbers (e.g., 1,2,5).")
    background: bool | None = Field(default=None, validation_alias="Background", serialization_alias="Background", description="Include background colors and images from the page in the PDF output.")
    fixed_elements: Literal["fixed", "absolute", "relative", "hide"] | None = Field(default=None, validation_alias="FixedElements", serialization_alias="FixedElements", description="Change how fixed-position elements are handled during conversion. Use 'hide' to remove them, or change their CSS position property.")
    header: str | None = Field(default=None, validation_alias="Header", serialization_alias="Header", description="HTML content to insert as a header on each page. Use CSS classes pageNumber, totalPages, title, and date for dynamic content injection. Supports inline CSS styling.")
    footer: str | None = Field(default=None, validation_alias="Footer", serialization_alias="Footer", description="HTML content to insert as a footer on each page. Use CSS classes pageNumber, totalPages, title, and date for dynamic content injection. Supports inline CSS styling.")
    show_elements: str | None = Field(default=None, validation_alias="ShowElements", serialization_alias="ShowElements", description="CSS selector for DOM elements that should remain visible. All other elements will be hidden during conversion.")
    avoid_break_elements: str | None = Field(default=None, validation_alias="AvoidBreakElements", serialization_alias="AvoidBreakElements", description="CSS selector for elements where page breaks should be avoided. Prevents breaking content within these elements.")
    break_before_elements: str | None = Field(default=None, validation_alias="BreakBeforeElements", serialization_alias="BreakBeforeElements", description="CSS selector for elements that should trigger a page break before them.")
    break_after_elements: str | None = Field(default=None, validation_alias="BreakAfterElements", serialization_alias="BreakAfterElements", description="CSS selector for elements that should trigger a page break after them.")
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The HTML content or URL to convert to PDF. Can be a full URL (http/https) or raw HTML file content.", json_schema_extra={'format': 'binary'})
    margin_top: dict | None = Field(default=None, validation_alias="MarginTop", serialization_alias="MarginTop", description="Set the page top margin in millimeters (mm).", ge=0, le=500)
    margin_right: int | None = Field(default=None, validation_alias="MarginRight", serialization_alias="MarginRight", description="Set the page right margin in millimeters (mm).", ge=0, le=500)
    margin_bottom: int | None = Field(default=None, validation_alias="MarginBottom", serialization_alias="MarginBottom", description="Set the page bottom margin in millimeters (mm).", ge=0, le=500)
    margin_left: int | None = Field(default=None, validation_alias="MarginLeft", serialization_alias="MarginLeft", description="Set the page left margin in millimeters (mm).", ge=0, le=500)
class PostConvertHtmlToPdfRequest(StrictModel):
    """Converts HTML content from a URL or file to PDF format with advanced rendering options, including JavaScript execution, custom styling, headers/footers, and page layout control."""
    body: PostConvertHtmlToPdfRequestBody | None = None

# Operation: convert_html_to_png
class PostConvertHtmlToPngRequestBody(StrictModel):
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PNG file. The system sanitizes the filename, appends the .png extension automatically, and adds numeric suffixes (e.g., _0, _1) when generating multiple files from a single input.")
    ad_block: bool | None = Field(default=None, validation_alias="AdBlock", serialization_alias="AdBlock", description="Block advertisements from appearing in the converted page.")
    cookie_consent_block: bool | None = Field(default=None, validation_alias="CookieConsentBlock", serialization_alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and related warnings from the page before conversion.")
    cookies: str | None = Field(default=None, validation_alias="Cookies", serialization_alias="Cookies", description="Set additional cookies to include in the page request. Provide multiple cookies as name-value pairs separated by semicolons.")
    java_script: bool | None = Field(default=None, validation_alias="JavaScript", serialization_alias="JavaScript", description="Enable JavaScript execution on the page during conversion, allowing dynamic content to render.")
    wait_element: str | None = Field(default=None, validation_alias="WaitElement", serialization_alias="WaitElement", description="CSS selector for a DOM element. The converter will wait for this element to appear before starting the conversion, useful for pages with delayed content loading.")
    user_css: str | None = Field(default=None, validation_alias="UserCss", serialization_alias="UserCss", description="Custom CSS rules to apply to the page before conversion begins.")
    css_media_type: str | None = Field(default=None, validation_alias="CssMediaType", serialization_alias="CssMediaType", description="CSS media type to use during conversion. Common values include 'screen' and 'print', but custom media types are also supported.")
    headers: str | None = Field(default=None, validation_alias="Headers", serialization_alias="Headers", description="Custom HTTP headers to include in the page request. Provide headers as name-value pairs separated by pipes, with each pair separated by a colon.")
    zoom: float | None = Field(default=None, validation_alias="Zoom", serialization_alias="Zoom", description="Zoom level for rendering the webpage. Values below 1 zoom out, values above 1 zoom in.", ge=0.1, le=10)
    transparent_background: bool | None = Field(default=None, validation_alias="TransparentBackground", serialization_alias="TransparentBackground", description="Use a transparent background instead of the default white background. The source HTML body background color must also be set to 'none' for transparency to work.")
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The HTML content or URL to convert. Provide either a web URL or raw HTML content.", json_schema_extra={'format': 'binary'})
class PostConvertHtmlToPngRequest(StrictModel):
    """Converts HTML content or web pages to PNG image format. Supports JavaScript execution, custom styling, cookie handling, and DOM element waiting for dynamic content rendering."""
    body: PostConvertHtmlToPngRequestBody | None = None

# Operation: convert_html_to_text
class PostConvertHtmlToTxtRequestBody(StrictModel):
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output text file. The API sanitizes the filename, appends the correct extension, and uses indexing (e.g., output_0.txt, output_1.txt) for multiple files.")
    ad_block: bool | None = Field(default=None, validation_alias="AdBlock", serialization_alias="AdBlock", description="Remove advertisements from the HTML content during conversion.")
    cookie_consent_block: bool | None = Field(default=None, validation_alias="CookieConsentBlock", serialization_alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and related warnings from the page.")
    cookies: str | None = Field(default=None, validation_alias="Cookies", serialization_alias="Cookies", description="Include additional cookies in the page request. Separate multiple cookies with semicolons.")
    java_script: bool | None = Field(default=None, validation_alias="JavaScript", serialization_alias="JavaScript", description="Enable JavaScript execution on the page during conversion.")
    wait_element: str | None = Field(default=None, validation_alias="WaitElement", serialization_alias="WaitElement", description="CSS selector for a DOM element. The converter will wait for this element to appear before starting the conversion.")
    user_css: str | None = Field(default=None, validation_alias="UserCss", serialization_alias="UserCss", description="Custom CSS rules to apply to the page before conversion begins.")
    css_media_type: str | None = Field(default=None, validation_alias="CssMediaType", serialization_alias="CssMediaType", description="CSS media type to use during conversion (e.g., screen, print, or custom types).")
    headers: str | None = Field(default=None, validation_alias="Headers", serialization_alias="Headers", description="Custom HTTP headers to include in the request. Separate multiple headers with pipes and use colons to delimit header names from values.")
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="HTML content to convert. Provide either a URL or raw HTML file content.", json_schema_extra={'format': 'binary'})
    extract_elements: str | None = Field(default=None, validation_alias="ExtractElements", serialization_alias="ExtractElements", description="CSS selector to extract specific DOM elements instead of converting the entire page. Use class selectors (.classname), ID selectors (#id), or tag names.")
class PostConvertHtmlToTxtRequest(StrictModel):
    """Converts HTML content from a URL or file to plain text format. Supports advanced options like JavaScript execution, element extraction, custom styling, and cookie/ad handling for flexible web content processing."""
    body: PostConvertHtmlToTxtRequestBody | None = None

# Operation: convert_html_to_spreadsheet
class PostConvertHtmlToXlsRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The HTML content to convert, provided either as a publicly accessible URL or as raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output spreadsheet file. The system automatically sanitizes the filename, appends the correct .xls extension, and adds numeric indexing (e.g., report_0.xls, report_1.xls) if multiple files are generated from a single input.")
class PostConvertHtmlToXlsRequest(StrictModel):
    """Converts HTML content or files to Excel spreadsheet format. Accepts HTML input as a URL or raw file content and generates a formatted XLS output file."""
    body: PostConvertHtmlToXlsRequestBody | None = None

# Operation: convert_html_to_xlsx
class PostConvertHtmlToXlsxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The HTML content to convert, provided either as a publicly accessible URL or as raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output Excel file. The system automatically sanitizes the filename, appends the .xlsx extension, and adds numeric suffixes (e.g., _0, _1) if multiple files are generated from a single input.")
class PostConvertHtmlToXlsxRequest(StrictModel):
    """Converts HTML content or files to Excel spreadsheet format. Accepts HTML input as a URL or raw file content and generates a formatted XLSX output file."""
    body: PostConvertHtmlToXlsxRequestBody | None = None

# Operation: convert_image_ico_to_jpg
class PostConvertIcoToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only scale the image if the input is larger than the desired output dimensions.")
    alpha_color: str | None = Field(default=None, validation_alias="AlphaColor", serialization_alias="AlphaColor", description="Replace transparent areas with a specific color. Accepts RGBA or CMYK hex strings, or standard color names.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Set the color space for the output image.")
class PostConvertIcoToJpgRequest(StrictModel):
    """Convert ICO (icon) image files to JPG format with optional scaling, color space adjustment, and alpha channel handling."""
    body: PostConvertIcoToJpgRequestBody | None = None

# Operation: convert_ico_to_pdf
class PostConvertIcoToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ICO image file to convert. Provide either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotation angle in degrees to apply to the image. For automatic rotation based on EXIF metadata in TIFF and JPEG images, leave empty.", ge=-360, le=360)
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output PDF. Defines how colors are represented in the converted document.")
    color_profile: Literal["default", "isocoatedv2"] | None = Field(default=None, validation_alias="ColorProfile", serialization_alias="ColorProfile", description="Color profile to apply to the output PDF. Some profiles override the ColorSpace setting.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Enable PDF/A-1b compliance for the output document, ensuring long-term archival compatibility.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in millimeters (mm).", ge=0, le=500)
    margin_vertical: int | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in millimeters (mm).", ge=0, le=500)
class PostConvertIcoToPdfRequest(StrictModel):
    """Convert ICO (icon) image files to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input as URL or binary content and generates a properly named output PDF file."""
    body: PostConvertIcoToPdfRequestBody | None = None

# Operation: convert_image_ico_to_png
class PostConvertIcoToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert, provided as either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the output dimensions.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertIcoToPngRequest(StrictModel):
    """Convert an ICO (icon) image file to PNG format. Supports URL or file content input with optional scaling and proportional resizing."""
    body: PostConvertIcoToPngRequestBody | None = None

# Operation: convert_icon_to_svg
class PostConvertIcoToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ICO file to convert. Accepts either a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming.")
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(default=None, validation_alias="Preset", serialization_alias="Preset", description="Vectorization preset that applies pre-configured tracing settings optimized for specific image types. When selected, presets override individual converter options except ColorMode. Use 'none' for custom configuration.")
    color_mode: Literal["color", "bw"] | None = Field(default=None, validation_alias="ColorMode", serialization_alias="ColorMode", description="Color processing mode for tracing. Choose 'color' for full-color output or 'bw' for black-and-white conversion.")
    layering: Literal["cutout", "stacked"] | None = Field(default=None, validation_alias="Layering", serialization_alias="Layering", description="Arrangement method for color regions in the output SVG. 'cutout' creates isolated layers, while 'stacked' overlays regions on top of each other.")
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(default=None, validation_alias="CurveMode", serialization_alias="CurveMode", description="Shape approximation method during tracing. 'pixel' follows exact pixel boundaries with minimal smoothing, 'polygon' creates straight-edged paths with sharp corners, and 'spline' generates smooth continuous curves.")
class PostConvertIcoToSvgRequest(StrictModel):
    """Converts ICO (icon) files to SVG (Scalable Vector Graphics) format with customizable vectorization settings. Supports preset configurations for different image types and offers fine-grained control over color mode, layering, and curve approximation."""
    body: PostConvertIcoToSvgRequestBody | None = None

# Operation: convert_image_ico_to_webp
class PostConvertIcoToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., image_0.webp, image_1.webp).")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output image. Choose from standard color profiles or use default for automatic detection.")
class PostConvertIcoToWebpRequest(StrictModel):
    """Convert ICO image files to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based sources."""
    body: PostConvertIcoToWebpRequestBody | None = None

# Operation: join_images
class PostConvertImagesToJoinRequestBody(StrictModel):
    files: list[str] | None = Field(default=None, validation_alias="Files", serialization_alias="Files", description="Images to combine into a single composite image. Each item can be provided as a URL or file content. When using query or multipart parameters, append an index suffix (e.g., Files[0], Files[1]).")
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output composite image file. The system automatically sanitizes the filename, appends the appropriate extension based on the target format, and adds indexing for multiple outputs to ensure unique, safe filenames.")
    join_direction: Literal["vertical", "horizontal"] | None = Field(default=None, validation_alias="JoinDirection", serialization_alias="JoinDirection", description="Direction in which images are arranged in the composite. Choose vertical to stack images top-to-bottom or horizontal to arrange them left-to-right.")
    image_spacing: int | None = Field(default=None, validation_alias="ImageSpacing", serialization_alias="ImageSpacing", description="Space in pixels between individual images in the composite. Specify a value between 0 and 200 pixels.", ge=0, le=200)
    spacing_color: str | None = Field(default=None, validation_alias="SpacingColor", serialization_alias="SpacingColor", description="Color of the spacing area between images. Works in conjunction with ImageSpacing to customize the visual appearance of gaps in the composite image.")
    image_output_format: Literal["auto", "jpg", "png", "tiff"] | None = Field(default=None, validation_alias="ImageOutputFormat", serialization_alias="ImageOutputFormat", description="Output format for the final composite image. Select a specific format (jpg, png, tiff) or use auto-detection to match the format of the input images.")
class PostConvertImagesToJoinRequest(StrictModel):
    """Combines multiple images into a single composite image with configurable layout direction, spacing, and output format. Supports vertical or horizontal arrangement with customizable spacing color and format conversion."""
    body: PostConvertImagesToJoinRequestBody | None = None

# Operation: convert_images_to_pdf
class PostConvertImagesToPdfRequestBody(StrictModel):
    files: list[str] | None = Field(default=None, validation_alias="Files", serialization_alias="Files", description="Images to convert to PDF. Each item can be provided as a URL or file content. When using query or multipart parameters, append an index to each parameter name (e.g., Files[0], Files[1]).")
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds an index suffix for multiple output files to ensure unique, safe naming.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotate images by the specified number of degrees. Leave empty to automatically rotate based on EXIF orientation data in TIFF and JPEG images.", ge=-360, le=360)
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Set the color space for the output PDF. Use 'default' to preserve original image colors, or specify a standard color space for consistent output.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Generate a PDF/A-1b compliant document suitable for long-term archival and preservation.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in millimeters (mm).", ge=0, le=500)
    margin_vertical: int | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in millimeters (mm).", ge=0, le=500)
class PostConvertImagesToPdfRequest(StrictModel):
    """Convert one or more images to a PDF document with optional image processing capabilities including rotation and color space adjustment. Supports PDF/A-1b compliance for archival purposes."""
    body: PostConvertImagesToPdfRequestBody | None = None

# Operation: convert_jfif_to_pdf
class PostConvertJfifToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Provide either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple outputs to ensure unique, safe file naming.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotation angle in degrees for the output image. Specify a value between -360 and 360, or leave empty to automatically rotate based on EXIF data in TIFF and JPEG images.", ge=-360, le=360)
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output PDF. Select from standard color space options to control how colors are represented in the final document.")
    color_profile: Literal["default", "isocoatedv2"] | None = Field(default=None, validation_alias="ColorProfile", serialization_alias="ColorProfile", description="Color profile to apply to the output PDF. Some profiles override the ColorSpace setting. Use 'isocoatedv2' for ISO Coated v2 standard compliance.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Enable PDF/A-1b compliance for the output document. When true, creates an archival-grade PDF suitable for long-term preservation.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in millimeters (mm).", ge=0, le=500)
    margin_vertical: int | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in millimeters (mm).", ge=0, le=500)
class PostConvertJfifToPdfRequest(StrictModel):
    """Convert JFIF image files to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input as URL or binary content and generates a properly named output PDF file."""
    body: PostConvertJfifToPdfRequestBody | None = None

# Operation: compress_jpg_image
class PostConvertJpgToCompressRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The JPG image file to compress. Can be provided as a URL or as binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output compressed image file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique and safe file naming.")
    compression_level: Literal["Lossless", "Good", "Extreme"] | None = Field(default=None, validation_alias="CompressionLevel", serialization_alias="CompressionLevel", description="The compression quality level to apply to the image. Lossless preserves all image data, Good provides balanced compression, and Extreme maximizes file size reduction.")
class PostConvertJpgToCompressRequest(StrictModel):
    """Compress a JPG image file with configurable compression levels. Accepts image files via URL or direct upload and generates an optimized output file with the specified compression quality."""
    body: PostConvertJpgToCompressRequestBody | None = None

# Operation: convert_image_to_gif
class PostConvertJpgToGifRequestBody(StrictModel):
    files: list[str] | None = Field(default=None, validation_alias="Files", serialization_alias="Files", description="Image files to convert, provided as URLs or file content. When using query or multipart parameters, append an index to each file parameter (e.g., Files[0], Files[1]).")
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output GIF file(s). The API sanitizes the filename, appends the correct extension, and automatically indexes multiple output files to ensure unique naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only scale the output if the input image dimensions exceed the target size.")
    animation_delay: int | None = Field(default=None, validation_alias="AnimationDelay", serialization_alias="AnimationDelay", description="Delay between animation frames, specified in hundredths of a second (e.g., 100 = 1 second).", ge=0, le=20000)
    animation_iterations: int | None = Field(default=None, validation_alias="AnimationIterations", serialization_alias="AnimationIterations", description="Number of times the animation loops. Set to 0 for infinite looping.", ge=0, le=1000)
class PostConvertJpgToGifRequest(StrictModel):
    """Convert one or more JPG images to animated GIF format with customizable animation timing and looping behavior."""
    body: PostConvertJpgToGifRequestBody | None = None

# Operation: convert_image_format
class PostConvertJpgToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple outputs to ensure unique, safe file naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Set the color space profile for the output image.")
class PostConvertJpgToJpgRequest(StrictModel):
    """Convert a JPG image to JPG format with optional scaling and color space adjustments. Useful for optimizing image properties such as dimensions and color profile while maintaining the same format."""
    body: PostConvertJpgToJpgRequestBody | None = None

# Operation: convert_image_jpg_to_jxl
class PostConvertJpgToJxlRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL pointing to the image or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output file. The system automatically sanitizes the name, appends the correct file extension, and adds indexing for multiple outputs to ensure unique, safe filenames.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image. Use 'default' for automatic detection, or specify a particular color space.")
class PostConvertJpgToJxlRequest(StrictModel):
    """Convert a JPG image to JXL (JPEG XL) format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads."""
    body: PostConvertJpgToJxlRequestBody | None = None

# Operation: convert_image_to_pdf_jpeg
class PostConvertJpgToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) when multiple files are generated.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotation angle in degrees to apply to the image. Leave empty to automatically detect and apply rotation from EXIF metadata in JPEG and TIFF images.", ge=-360, le=360)
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="The color space to apply to the output PDF. Determines how colors are represented in the final document.")
    color_profile: Literal["default", "isocoatedv2"] | None = Field(default=None, validation_alias="ColorProfile", serialization_alias="ColorProfile", description="The color profile to embed in the output PDF. Some profiles may override the ColorSpace setting.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Enable PDF/A-1b compliance for long-term archival and preservation of the document.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in millimeters (mm).", ge=0, le=500)
    margin_vertical: int | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in millimeters (mm).", ge=0, le=500)
class PostConvertJpgToPdfRequest(StrictModel):
    """Convert JPG images to PDF format with optional image processing capabilities including rotation, color space adjustment, and PDF/A compliance."""
    body: PostConvertJpgToPdfRequestBody | None = None

# Operation: convert_image_jpg_to_png
class PostConvertJpgToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert, provided either as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.png, image_1.png) for multiple outputs from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertJpgToPngRequest(StrictModel):
    """Convert a JPG image to PNG format with optional scaling and proportional constraints. Supports both URL-based and direct file content input."""
    body: PostConvertJpgToPngRequestBody | None = None

# Operation: convert_image_jpg_to_pnm
class PostConvertJpgToPnmRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL pointing to the JPG file or the raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNM file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.pnm, image_1.pnm) for multiple outputs from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output size, leaving smaller images unchanged.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertJpgToPnmRequest(StrictModel):
    """Convert a JPG image to PNM (Portable Anymap) format with optional scaling and proportional constraints. Supports both URL-based and direct file uploads."""
    body: PostConvertJpgToPnmRequestBody | None = None

# Operation: convert_image_to_svg_jpg
class PostConvertJpgToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.svg, filename_1.svg) for multiple output files.")
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(default=None, validation_alias="Preset", serialization_alias="Preset", description="A vectorization preset that applies pre-configured tracing settings optimized for specific image types. When selected, presets override individual converter options except ColorMode, ensuring consistent and balanced SVG output.")
    color_mode: Literal["color", "bw"] | None = Field(default=None, validation_alias="ColorMode", serialization_alias="ColorMode", description="Determines whether the image is traced in full color or converted to black-and-white during vectorization.")
    layering: Literal["cutout", "stacked"] | None = Field(default=None, validation_alias="Layering", serialization_alias="Layering", description="Controls how color regions are arranged in the output SVG: cutout mode isolates regions as separate layers, while stacked mode overlays regions for blending effects.")
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(default=None, validation_alias="CurveMode", serialization_alias="CurveMode", description="Defines the shape approximation method during tracing. Pixel mode follows exact pixel boundaries with minimal smoothing, Polygon creates straight-edged paths with sharp corners, and Spline generates smooth continuous curves for natural-looking shapes.")
class PostConvertJpgToSvgRequest(StrictModel):
    """Converts a JPG image to scalable vector graphics (SVG) format using configurable tracing and vectorization settings. Supports preset configurations for different image types and offers fine-grained control over color handling, layering, and curve approximation."""
    body: PostConvertJpgToSvgRequestBody | None = None

# Operation: convert_image_to_tiff
class PostConvertJpgToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL pointing to the JPG file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multi-file outputs.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a multi-page TIFF file when processing multiple images or pages.")
class PostConvertJpgToTiffRequest(StrictModel):
    """Convert a JPG image to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""
    body: PostConvertJpgToTiffRequestBody | None = None

# Operation: extract_text_from_image
class PostConvertJpgToTxtRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output text file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.txt, output_1.txt) for multiple files.")
    preprocessing: bool | None = Field(default=None, validation_alias="Preprocessing", serialization_alias="Preprocessing", description="Enable advanced image preprocessing techniques such as deskew, thresholding, resizing, and sharpening to improve text extraction accuracy. Increases processing time when enabled.")
    ocr_language: Literal["ar", "ca", "zh-cn", "zh-tw", "da", "nl", "en", "fi", "fa", "de", "el", "he", "it", "ja", "ko", "lt", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(default=None, validation_alias="OcrLanguage", serialization_alias="OcrLanguage", description="The language to use for OCR text recognition. Supports multiple languages; contact support to request additional language support.")
class PostConvertJpgToTxtRequest(StrictModel):
    """Converts a JPG image to text by performing optical character recognition (OCR). Supports optional image preprocessing to enhance text clarity and multiple language recognition."""
    body: PostConvertJpgToTxtRequestBody | None = None

# Operation: convert_image_jpg_to_webp
class PostConvertJpgToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a file upload or a URL pointing to the source image.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output file. The API automatically sanitizes the filename, appends the correct .webp extension, and adds numeric indexing for multiple output files to ensure unique, safe filenames.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image.")
class PostConvertJpgToWebpRequest(StrictModel):
    """Convert JPG images to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""
    body: PostConvertJpgToWebpRequestBody | None = None

# Operation: convert_presentation_to_pptx
class PostConvertKeyToPptxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Keynote presentation file to convert. Can be provided as a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output file. The system automatically sanitizes the filename, appends the correct .pptx extension, and adds numeric indexing (e.g., output_0.pptx, output_1.pptx) if multiple files are generated.")
class PostConvertKeyToPptxRequest(StrictModel):
    """Converts a Keynote presentation file to PowerPoint format (PPTX). Accepts file input as a URL or binary content and generates a properly named output file."""
    body: PostConvertKeyToPptxRequestBody | None = None

# Operation: convert_log_to_docx
class PostConvertLogToDocxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The log file to convert. Provide either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output file. The API automatically sanitizes the filename, appends the .docx extension, and adds numeric indexing (e.g., report_0.docx, report_1.docx) if multiple files are generated.")
class PostConvertLogToDocxRequest(StrictModel):
    """Converts a log file to Microsoft Word (.docx) format. Accepts log file content or URL and generates a formatted Word document with the specified output filename."""
    body: PostConvertLogToDocxRequestBody | None = None

# Operation: convert_log_to_pdf
class PostConvertLogToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The log file to convert. Accepts either a file URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the generated output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `report_0.pdf`, `report_1.pdf`) for multiple output files.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to include in the output PDF using a range format (e.g., 1-10 for pages 1 through 10). Defaults to the first 6000 pages.")
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(default=None, validation_alias="PdfaVersion", serialization_alias="PdfaVersion", description="Sets the PDF/A compliance version for archival-grade PDF output. Use 'none' for standard PDF without compliance requirements.")
class PostConvertLogToPdfRequest(StrictModel):
    """Converts log files to PDF format with optional page range selection and PDF/A compliance. Supports both file uploads and URL-based file sources."""
    body: PostConvertLogToPdfRequestBody | None = None

# Operation: convert_log_to_text
class PostConvertLogToTxtRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The log file to convert. Accepts either a URL reference or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the generated output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., file_0.txt, file_1.txt) for multiple outputs to ensure unique, safe file identification.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected log files.")
    substitutions: bool | None = Field(default=None, validation_alias="Substitutions", serialization_alias="Substitutions", description="Enable replacement of special symbols with their text equivalents (e.g., © becomes (c)) in the output text.")
    end_line_char: Literal["crlf", "cr", "lfcr", "lf"] | None = Field(default=None, validation_alias="EndLineChar", serialization_alias="EndLineChar", description="Specifies the line ending character(s) to use when breaking lines in the output text file.")
class PostConvertLogToTxtRequest(StrictModel):
    """Converts log files to plain text format with optional symbol substitution and configurable line ending characters. Supports protected documents via password and customizable output file naming."""
    body: PostConvertLogToTxtRequestBody | None = None

# Operation: convert_markdown_to_html
class PostConvertMdToHtmlRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Markdown content to convert, provided either as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated HTML output file. The system automatically sanitizes the filename, appends the .html extension, and adds numeric suffixes (e.g., output_0.html, output_1.html) when generating multiple files from a single input.")
class PostConvertMdToHtmlRequest(StrictModel):
    """Converts Markdown content to HTML format. Accepts Markdown input as file content or URL and generates corresponding HTML output."""
    body: PostConvertMdToHtmlRequestBody | None = None

# Operation: convert_markdown_to_pdf
class PostConvertMdToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Markdown file to convert. Provide either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric suffixes (e.g., _0, _1) if multiple files are generated.")
    margin_top: int | None = Field(default=None, validation_alias="MarginTop", serialization_alias="MarginTop", description="Top margin of the PDF page in millimeters. Valid range is 0-500 mm.", ge=0, le=500)
    margin_right: int | None = Field(default=None, validation_alias="MarginRight", serialization_alias="MarginRight", description="Right margin of the PDF page in millimeters. Valid range is 0-500 mm.", ge=0, le=500)
    margin_bottom: int | None = Field(default=None, validation_alias="MarginBottom", serialization_alias="MarginBottom", description="Bottom margin of the PDF page in millimeters. Valid range is 0-500 mm.", ge=0, le=500)
    margin_left: int | None = Field(default=None, validation_alias="MarginLeft", serialization_alias="MarginLeft", description="Left margin of the PDF page in millimeters. Valid range is 0-500 mm.", ge=0, le=500)
class PostConvertMdToPdfRequest(StrictModel):
    """Converts Markdown documents to PDF format with customizable page margins. Accepts Markdown content via URL or file upload and generates a formatted PDF output."""
    body: PostConvertMdToPdfRequestBody | None = None

# Operation: convert_mhtml_to_docx
class PostConvertMhtmlToDocxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The MHTML file to convert, provided either as a URL or as binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output DOCX file. The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.docx, document_1.docx) when multiple files are generated from a single input.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in inches (in).", ge=0, le=500)
    margin_vertical: float | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in inches (in).", ge=0, le=500)
class PostConvertMhtmlToDocxRequest(StrictModel):
    """Converts an MHTML (MIME HTML) file to DOCX format. Accepts file input as a URL or binary content and generates a properly named output document."""
    body: PostConvertMhtmlToDocxRequestBody | None = None

# Operation: convert_mobi_to_jpg
class PostConvertMobiToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The MOBI file to convert. Accepts either a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple output files.")
    jpg_type: Literal["jpeg", "jpegcmyk", "jpeggray"] | None = Field(default=None, validation_alias="JpgType", serialization_alias="JpgType", description="JPG color mode for the output image. Choose between standard JPEG, CMYK for print-ready output, or grayscale for reduced file size.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when resizing the output image to prevent distortion.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions, preserving quality for smaller images.")
class PostConvertMobiToJpgRequest(StrictModel):
    """Converts MOBI eBook files to JPG image format with configurable output quality and scaling options. Supports multiple JPG color modes and intelligent scaling to optimize output file size."""
    body: PostConvertMobiToJpgRequestBody | None = None

# Operation: convert_mobi_to_pdf
class PostConvertMobiToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The MOBI file to convert, provided either as a URL or as binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct .pdf extension, and adds numeric indexing (e.g., output_0.pdf, output_1.pdf) when multiple files are generated from a single input.")
    base_font_size: float | None = Field(default=None, validation_alias="BaseFontSize", serialization_alias="BaseFontSize", description="The base font size in points (pt) for the converted PDF. All text scaling is relative to this value.", ge=1, le=50)
    margin_left: float | None = Field(default=None, validation_alias="MarginLeft", serialization_alias="MarginLeft", description="Sets the left margin in points (pt) for text on the PDF page.", ge=0, le=200)
    margin_right: float | None = Field(default=None, validation_alias="MarginRight", serialization_alias="MarginRight", description="Sets the right margin in points (pt) for text on the PDF page.", ge=0, le=200)
    margin_top: dict | None = Field(default=None, validation_alias="MarginTop", serialization_alias="MarginTop", description="Sets the top margin in points (pt) for text on the PDF page.", ge=0, le=200)
    margin_bottom: float | None = Field(default=None, validation_alias="MarginBottom", serialization_alias="MarginBottom", description="Sets the bottom margin in points (pt) for text on the PDF page.", ge=0, le=200)
class PostConvertMobiToPdfRequest(StrictModel):
    """Converts MOBI eBook files to PDF format with customizable font sizing. Accepts file input as URL or binary content and generates a properly named output PDF file."""
    body: PostConvertMobiToPdfRequestBody | None = None

# Operation: convert_mobi_to_png
class PostConvertMobiToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The MOBI file to convert. Accepts either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PNG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when resizing the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size.")
class PostConvertMobiToPngRequest(StrictModel):
    """Convert MOBI eBook files to PNG image format. Supports URL or file content input with optional scaling and proportional resizing controls."""
    body: PostConvertMobiToPngRequestBody | None = None

# Operation: convert_mobi_to_tiff
class PostConvertMobiToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The MOBI file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions.")
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(default=None, validation_alias="TiffType", serialization_alias="TiffType", description="Specifies the TIFF color type and compression method. Choose from color variants (24/32-bit with no compression, LZW, or ZIP), grayscale options, or monochrome formats.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="When enabled, combines all pages into a single multi-page TIFF file. When disabled, generates separate TIFF files for each page.")
    fill_order: Literal["0", "1"] | None = Field(default=None, validation_alias="FillOrder", serialization_alias="FillOrder", description="Defines the bit order within each byte of the TIFF data. Use 0 for most standard applications or 1 for specific compatibility requirements.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when resizing the output image to fit specified dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="When enabled, only applies scaling if the input image dimensions exceed the target output dimensions. Prevents upscaling of smaller images.")
class PostConvertMobiToTiffRequest(StrictModel):
    """Converts MOBI eBook files to TIFF image format with configurable output options including color depth, compression, and multi-page support."""
    body: PostConvertMobiToTiffRequestBody | None = None

# Operation: convert_email_to_jpg
class PostConvertMsgToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The email message file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output JPG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) when multiple files are generated.")
    ignore_attachment_errors: bool | None = Field(default=None, validation_alias="IgnoreAttachmentErrors", serialization_alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors will not prevent the email body from being converted to JPG. Only applies when attachments are being processed.")
    merge: bool | None = Field(default=None, validation_alias="Merge", serialization_alias="Merge", description="When enabled, merges the email body content with extracted attachments during conversion. Only applies when attachments are being processed.")
class PostConvertMsgToJpgRequest(StrictModel):
    """Converts an email message file (MSG format) to JPG image format, with optional support for extracting and merging attachments into the output."""
    body: PostConvertMsgToJpgRequestBody | None = None

# Operation: convert_msg_to_pdf
class PostConvertMsgToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The MSG file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) when multiple files are produced.")
    ignore_attachment_errors: bool | None = Field(default=None, validation_alias="IgnoreAttachmentErrors", serialization_alias="IgnoreAttachmentErrors", description="When enabled, attachment conversion errors are ignored and the email body is still converted to PDF. Only applies when attachments are being converted.")
    merge: bool | None = Field(default=None, validation_alias="Merge", serialization_alias="Merge", description="When enabled, merges the email body with converted attachments into a single PDF document. Only applies when attachments are being converted.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="When enabled, creates a PDF/A-1b compliant document for long-term archival and preservation.")
    margin_top: dict | None = Field(default=None, validation_alias="MarginTop", serialization_alias="MarginTop", description="Set the page top margin in millimeters (mm).", ge=0, le=500)
    margin_right: int | None = Field(default=None, validation_alias="MarginRight", serialization_alias="MarginRight", description="Set the page right margin in millimeters (mm).", ge=0, le=500)
    margin_bottom: int | None = Field(default=None, validation_alias="MarginBottom", serialization_alias="MarginBottom", description="Set the page bottom margin in millimeters (mm).", ge=0, le=500)
    margin_left: int | None = Field(default=None, validation_alias="MarginLeft", serialization_alias="MarginLeft", description="Set the page left margin in millimeters (mm).", ge=0, le=500)
class PostConvertMsgToPdfRequest(StrictModel):
    """Converts MSG (Outlook email) files to PDF format with optional attachment handling and PDF/A compliance. Supports file input via URL or binary content."""
    body: PostConvertMsgToPdfRequestBody | None = None

# Operation: convert_email_to_png_outlook
class PostConvertMsgToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The email message file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices (e.g., email_0.png, email_1.png) when multiple files are generated.")
    ignore_attachment_errors: bool | None = Field(default=None, validation_alias="IgnoreAttachmentErrors", serialization_alias="IgnoreAttachmentErrors", description="When enabled, the conversion process will continue even if errors occur while processing email attachments. Only applies when attachments are being converted.")
    merge: bool | None = Field(default=None, validation_alias="Merge", serialization_alias="Merge", description="When enabled, email body content and attachments are combined into a single output during conversion. Only applies when attachments are being converted.")
class PostConvertMsgToPngRequest(StrictModel):
    """Converts an email message file (MSG format) to PNG image format, with optional support for embedding attachments into the output. Useful for archiving, sharing, or preserving email content as images."""
    body: PostConvertMsgToPngRequestBody | None = None

# Operation: convert_msg_to_tiff
class PostConvertMsgToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The MSG file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The API automatically sanitizes the name, appends the correct extension, and adds numeric suffixes (e.g., _0, _1) when multiple files are generated.")
    ignore_attachment_errors: bool | None = Field(default=None, validation_alias="IgnoreAttachmentErrors", serialization_alias="IgnoreAttachmentErrors", description="If enabled, attachment conversion errors will not prevent the email body from being converted. Only applies when attachments are being converted.")
    merge: bool | None = Field(default=None, validation_alias="Merge", serialization_alias="Merge", description="If enabled, merges the email body with converted attachments into the output. Only applies when attachments are being converted.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="If enabled, creates a single multi-page TIFF file containing all content. If disabled, generates separate TIFF files for each page.")
class PostConvertMsgToTiffRequest(StrictModel):
    """Converts MSG email files to TIFF image format, with support for embedding attachments and creating multi-page documents. Useful for archiving emails as image files or integrating with document management systems."""
    body: PostConvertMsgToTiffRequestBody | None = None

# Operation: convert_message_to_webp
class PostConvertMsgToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The message file to convert. Accepts either a URL reference or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output WebP file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.webp, output_1.webp) for multiple files to ensure unique, safe filenames.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size.")
class PostConvertMsgToWebpRequest(StrictModel):
    """Convert a message file to WebP image format with optional scaling and proportional constraints. Supports both URL and file content input."""
    body: PostConvertMsgToWebpRequestBody | None = None

# Operation: convert_numbers_to_csv
class PostConvertNumbersToCsvRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert, provided either as a URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated CSV output file. The system automatically sanitizes the filename, appends the .csv extension, and adds numeric indexing (e.g., output_0.csv, output_1.csv) if multiple files are generated.")
class PostConvertNumbersToCsvRequest(StrictModel):
    """Converts a numbers file to CSV format. Accepts file input as a URL or file content and generates a properly named CSV output file."""
    body: PostConvertNumbersToCsvRequestBody | None = None

# Operation: convert_numbers_to_xlsx
class PostConvertNumbersToXlsxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Numbers file to convert, provided either as a URL or as binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output file. The system automatically sanitizes the filename, appends the correct .xlsx extension, and adds numeric indexing (e.g., report_0.xlsx, report_1.xlsx) if multiple files are generated.")
class PostConvertNumbersToXlsxRequest(StrictModel):
    """Converts a Numbers spreadsheet file to Excel (XLSX) format. Accepts file input as a URL or binary content and generates a properly named output file."""
    body: PostConvertNumbersToXlsxRequestBody | None = None

# Operation: convert_document_to_jpg_spreadsheet
class PostConvertOdcToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert, provided either as a URL reference or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple generated files.")
class PostConvertOdcToJpgRequest(StrictModel):
    """Converts an ODC (OpenDocument Chart) file to JPG image format. Accepts file input as a URL or binary content and generates a JPG output file with optional custom naming."""
    body: PostConvertOdcToJpgRequestBody | None = None

# Operation: convert_odc_to_pdf
class PostConvertOdcToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ODC file to convert. Accepts either a file upload or a URL pointing to the source file.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `report_0.pdf`, `report_1.pdf`) for multiple output files.")
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(default=None, validation_alias="PdfaVersion", serialization_alias="PdfaVersion", description="Specifies the PDF/A compliance version for the output file. Use 'none' for standard PDF, or select a PDF/A version for archival compliance.")
class PostConvertOdcToPdfRequest(StrictModel):
    """Converts an ODC (OpenDocument Chart) file to PDF format with optional PDF/A compliance. Supports both file uploads and URL-based sources."""
    body: PostConvertOdcToPdfRequestBody | None = None

# Operation: convert_odc_to_png
class PostConvertOdcToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ODC file to convert, provided as either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `output_0.png`, `output_1.png`) for multiple files to ensure unique, safe naming.")
    background_color: str | None = Field(default=None, validation_alias="BackgroundColor", serialization_alias="BackgroundColor", description="Background color applied to transparent areas in the converted image. Accepts color names (e.g., `white`, `black`), RGB format (e.g., `255,0,0`), HEX format (e.g., `#FF0000`), or `transparent` to preserve transparency.")
class PostConvertOdcToPngRequest(StrictModel):
    """Converts ODC (OpenDocument Chart) files to PNG image format. Supports URL or file content input with optional background color customization for transparent areas."""
    body: PostConvertOdcToPngRequestBody | None = None

# Operation: convert_document_to_jpg_formula
class PostConvertOdfToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert, provided either as a URL or as binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output JPG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.jpg, document_1.jpg) when multiple output files are generated from a single input.")
class PostConvertOdfToJpgRequest(StrictModel):
    """Converts ODF (OpenDocument Format) documents to JPG image format. Supports both file uploads and URL-based file sources."""
    body: PostConvertOdfToJpgRequestBody | None = None

# Operation: convert_document_to_pdf_odf
class PostConvertOdfToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Can be provided as a file upload (binary content) or as a URL pointing to the source file.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., `report_0.pdf`, `report_1.pdf`) when multiple files are generated from a single input.")
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(default=None, validation_alias="PdfaVersion", serialization_alias="PdfaVersion", description="Specifies the PDF/A compliance version for the output file. PDF/A formats ensure long-term archival compatibility. Use 'none' for standard PDF output without archival compliance.")
class PostConvertOdfToPdfRequest(StrictModel):
    """Converts ODF (Open Document Format) files to PDF format with optional PDF/A compliance. Supports both file uploads and URL-based file sources."""
    body: PostConvertOdfToPdfRequestBody | None = None

# Operation: convert_document_to_png
class PostConvertOdfToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `_0`, `_1`) when multiple files are generated from a single input.")
    background_color: str | None = Field(default=None, validation_alias="BackgroundColor", serialization_alias="BackgroundColor", description="The background color applied to transparent areas in the converted images. Accepts color names, RGB values (comma-separated), HEX codes, or the value `transparent` to preserve transparency.")
class PostConvertOdfToPngRequest(StrictModel):
    """Converts ODF (OpenDocument Format) documents to PNG images. Supports customization of output filename and background color for transparent areas."""
    body: PostConvertOdfToPngRequestBody | None = None

# Operation: convert_odg_to_pdf
class PostConvertOdgToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ODG file to convert. Can be provided as a file upload (binary content) or as a URL pointing to the source file.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `document_0.pdf`, `document_1.pdf`) when multiple files are generated.")
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(default=None, validation_alias="PdfaVersion", serialization_alias="PdfaVersion", description="Specifies the PDF/A compliance version for the output file. Use 'none' for standard PDF, or select a PDF/A version for archival compliance.")
class PostConvertOdgToPdfRequest(StrictModel):
    """Converts an ODG (OpenDocument Graphics) file to PDF format with optional PDF/A compliance. Supports both file uploads and URL-based file sources."""
    body: PostConvertOdgToPdfRequestBody | None = None

# Operation: convert_presentation_to_jpg
class PostConvertOdpToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a file upload (binary content) or a URL pointing to the ODP file.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output JPG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., presentation_0.jpg, presentation_1.jpg) when multiple images are generated from slides.")
class PostConvertOdpToJpgRequest(StrictModel):
    """Converts an ODP (OpenDocument Presentation) file to JPG image format. Supports both file uploads and URL-based sources, generating one or more JPG images from the presentation slides."""
    body: PostConvertOdpToJpgRequestBody | None = None

# Operation: convert_odp_to_pdf
class PostConvertOdpToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ODP file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `_0`, `_1`) if multiple files are generated from a single input.")
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(default=None, validation_alias="PdfaVersion", serialization_alias="PdfaVersion", description="Specifies the PDF/A compliance version for the output file. Use 'none' for standard PDF, or select a PDF/A version for archival compliance.")
class PostConvertOdpToPdfRequest(StrictModel):
    """Converts an ODP (OpenDocument Presentation) file to PDF format with optional PDF/A compliance. Supports file input via URL or direct file content and allows customization of output filename and PDF/A version."""
    body: PostConvertOdpToPdfRequestBody | None = None

# Operation: convert_presentation_to_png
class PostConvertOdpToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ODP file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output PNG file(s). The system automatically sanitizes the name, appends the correct file extension, and adds numeric indexing (e.g., `presentation_0.png`, `presentation_1.png`) when multiple files are generated from a single input.")
    background_color: str | None = Field(default=None, validation_alias="BackgroundColor", serialization_alias="BackgroundColor", description="Background color applied to transparent areas in the generated PNG images. Accepts color names (e.g., `white`, `black`), RGB format (comma-separated values 0-255), HEX format (with # prefix), or `transparent` to preserve transparency.")
class PostConvertOdpToPngRequest(StrictModel):
    """Converts ODP (OpenDocument Presentation) files to PNG image format. Supports file input via URL or direct file content, with optional background color customization for transparent areas."""
    body: PostConvertOdpToPngRequestBody | None = None

# Operation: convert_spreadsheet_to_image
class PostConvertOdsToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The spreadsheet file to convert, provided either as a URL or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output image file. The system automatically sanitizes the filename, appends the correct JPG extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) if multiple images are generated from a single input.")
class PostConvertOdsToJpgRequest(StrictModel):
    """Converts an ODS (OpenDocument Spreadsheet) file to JPG image format. Accepts file input as a URL or binary content and generates a named output image file."""
    body: PostConvertOdsToJpgRequestBody | None = None

# Operation: convert_ods_to_pdf
class PostConvertOdsToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ODS file to convert. Can be provided as a file upload or as a URL pointing to the source file.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `report_0.pdf`, `report_1.pdf`) when multiple files are generated from a single input.")
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(default=None, validation_alias="PdfaVersion", serialization_alias="PdfaVersion", description="Specifies the PDF/A compliance version for the output file. PDF/A versions provide long-term archival compatibility. Use 'none' for standard PDF output without PDF/A compliance.")
class PostConvertOdsToPdfRequest(StrictModel):
    """Converts an ODS (OpenDocument Spreadsheet) file to PDF format with optional PDF/A compliance. Supports both file uploads and URL-based file sources."""
    body: PostConvertOdsToPdfRequestBody | None = None

# Operation: convert_ods_to_png
class PostConvertOdsToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ODS file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output PNG file(s). The system automatically sanitizes the name, appends the correct file extension, and adds numeric indexing (e.g., `report_0.png`, `report_1.png`) when multiple files are generated from a single input.")
    background_color: str | None = Field(default=None, validation_alias="BackgroundColor", serialization_alias="BackgroundColor", description="Background color for the generated PNG image. Specify a color name (e.g., `white`, `black`), RGB format (e.g., `255,0,0`), or HEX format (e.g., `#FF0000`). Use `transparent` to preserve transparency.")
class PostConvertOdsToPngRequest(StrictModel):
    """Converts an ODS (OpenDocument Spreadsheet) file to PNG image format. Supports file input via URL or direct content, with customizable output naming and background color options."""
    body: PostConvertOdsToPngRequestBody | None = None

# Operation: convert_document_odt_to_docx
class PostConvertOdtToDocxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output DOCX file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.docx, filename_1.docx) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input document if it is password-protected.")
    update_toc: bool | None = Field(default=None, validation_alias="UpdateToc", serialization_alias="UpdateToc", description="Whether to automatically update all tables of content in the converted document.")
    update_references: bool | None = Field(default=None, validation_alias="UpdateReferences", serialization_alias="UpdateReferences", description="Whether to automatically update all reference fields in the converted document.")
class PostConvertOdtToDocxRequest(StrictModel):
    """Converts an ODT (OpenDocument Text) document to DOCX (Microsoft Word) format. Supports password-protected documents and optional updates to tables of content and reference fields."""
    body: PostConvertOdtToDocxRequestBody | None = None

# Operation: convert_document_to_jpg_text
class PostConvertOdtToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Can be provided as a URL reference or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output JPG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.jpg, document_1.jpg) when multiple output files are generated from a single input.")
class PostConvertOdtToJpgRequest(StrictModel):
    """Converts an ODT (OpenDocument Text) document to JPG image format. Supports both file uploads and URL-based file sources."""
    body: PostConvertOdtToJpgRequestBody | None = None

# Operation: convert_document_to_pdf_odt
class PostConvertOdtToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Can be provided as a file upload (binary content) or as a URL pointing to the source document.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the generated output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., filename_0.pdf, filename_1.pdf) when multiple files are generated from a single input.")
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(default=None, validation_alias="PdfaVersion", serialization_alias="PdfaVersion", description="PDF/A compliance version for the output file. Select 'none' for standard PDF, or choose a PDF/A version (1b, 2b, or 3b) for long-term archival compliance.")
class PostConvertOdtToPdfRequest(StrictModel):
    """Converts an ODT (OpenDocument Text) document to PDF format with optional PDF/A compliance. Supports both file uploads and URL-based sources, with customizable output naming and PDF/A version selection."""
    body: PostConvertOdtToPdfRequestBody | None = None

# Operation: convert_document_to_png_text
class PostConvertOdtToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ODT file to convert. Accepts either a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output PNG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `output_0.png`, `output_1.png`) for multiple files to ensure unique, safe naming.")
    background_color: str | None = Field(default=None, validation_alias="BackgroundColor", serialization_alias="BackgroundColor", description="Background color for transparent areas in the converted images. Accepts color names (e.g., `white`, `black`), RGB format (e.g., `255,0,0`), HEX format (e.g., `#FF0000`), or `transparent` to preserve transparency.")
class PostConvertOdtToPngRequest(StrictModel):
    """Converts ODT (OpenDocument Text) files to PNG images. Supports file input via URL or direct content, with optional background color customization for transparent areas."""
    body: PostConvertOdtToPngRequestBody | None = None

# Operation: convert_document_odt_to_txt
class PostConvertOdtToTxtRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ODT document to convert. Accepts either a file URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output text file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.txt, output_1.txt) for multiple files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected ODT documents.")
    substitutions: bool | None = Field(default=None, validation_alias="Substitutions", serialization_alias="Substitutions", description="When enabled, replaces special symbols with their text equivalents (e.g., © becomes (c)).")
    end_line_char: Literal["crlf", "cr", "lfcr", "lf"] | None = Field(default=None, validation_alias="EndLineChar", serialization_alias="EndLineChar", description="Specifies the line ending character to use in the output text file.")
class PostConvertOdtToTxtRequest(StrictModel):
    """Converts ODT (OpenDocument Text) documents to plain text format. Supports password-protected documents, symbol substitution, and configurable line ending characters."""
    body: PostConvertOdtToTxtRequestBody | None = None

# Operation: convert_document_to_xml
class PostConvertOdtToXmlRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a file URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output XML file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., document_0.xml, document_1.xml) when multiple files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input document if it is password-protected.")
    update_toc: bool | None = Field(default=None, validation_alias="UpdateToc", serialization_alias="UpdateToc", description="When enabled, automatically updates all tables of content in the document during conversion.")
    update_references: bool | None = Field(default=None, validation_alias="UpdateReferences", serialization_alias="UpdateReferences", description="When enabled, automatically updates all reference fields in the document during conversion.")
    xml_type: Literal["word2003", "flatWordXml", "strictOpenXml"] | None = Field(default=None, validation_alias="XmlType", serialization_alias="XmlType", description="Specifies the XML schema format to use for the output. Word2003 uses legacy XML, flatWordXml uses a flat structure, and strictOpenXml uses the modern Office Open XML standard.")
class PostConvertOdtToXmlRequest(StrictModel):
    """Converts an ODT (OpenDocument Text) document to XML format with optional support for updating tables of content and reference fields. Supports password-protected documents and multiple XML output formats."""
    body: PostConvertOdtToXmlRequestBody | None = None

# Operation: convert_office_document_to_pdf
class PostConvertOfficeToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Can be provided as a file upload (binary content) or as a URL pointing to the document.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., _0, _1) when multiple files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected documents. Only needed if the input document is encrypted.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="When enabled, generates a PDF/A-1b compliant document suitable for long-term archival and preservation.")
class PostConvertOfficeToPdfRequest(StrictModel):
    """Converts office documents (Word, Excel, PowerPoint, etc.) to PDF format with optional password protection and PDF/A compliance. Supports both file uploads and URL-based document sources."""
    body: PostConvertOfficeToPdfRequestBody | None = None

# Operation: convert_pages_to_docx
class PostConvertPagesToDocxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Pages document to convert, provided as either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated DOCX output file. The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.docx, document_1.docx) when multiple files are produced from a single input.")
class PostConvertPagesToDocxRequest(StrictModel):
    """Converts a Pages document to DOCX format. Accepts file input as a URL or binary content and generates a properly named output file."""
    body: PostConvertPagesToDocxRequestBody | None = None

# Operation: convert_pages_to_text
class PostConvertPagesToTxtRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Can be provided as a URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output file(s). The system automatically sanitizes the filename, appends the correct extension for the target format, and adds numeric indexing (e.g., `output_0.txt`, `output_1.txt`) when multiple files are generated from a single input.")
class PostConvertPagesToTxtRequest(StrictModel):
    """Converts document pages to plain text format. Supports file uploads via URL or direct file content and generates appropriately named output files."""
    body: PostConvertPagesToTxtRequestBody | None = None

# Operation: compress_pdf
class PostConvertPdfToCompressRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to compress. Accepts either a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output compressed PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the PDF if it is password-protected.")
    preset: Literal["none", "lossless", "text", "archive", "web", "ebook", "printer"] | None = Field(default=None, validation_alias="Preset", serialization_alias="Preset", description="Predefined compression profile optimized for specific use cases. When selected, all other compression options are ignored. Choose 'none' for no compression or select a preset tailored to your needs (lossless preserves quality, text optimizes for documents, web reduces file size for online sharing, etc.).")
    unembed_base_fonts: bool | None = Field(default=None, validation_alias="UnembedBaseFonts", serialization_alias="UnembedBaseFonts", description="Remove standard base fonts from the PDF to reduce file size. Embedded fonts will be substituted with system fonts on viewing.")
    subset_embedded_fonts: bool | None = Field(default=None, validation_alias="SubsetEmbeddedFonts", serialization_alias="SubsetEmbeddedFonts", description="Subset embedded fonts to include only characters actually used in the document, removing unused glyphs to reduce file size.")
    remove_forms: bool | None = Field(default=None, validation_alias="RemoveForms", serialization_alias="RemoveForms", description="Remove all interactive form fields from the PDF document.")
    remove_duplicates: bool | None = Field(default=None, validation_alias="RemoveDuplicates", serialization_alias="RemoveDuplicates", description="Remove duplicate font definitions and color profiles to eliminate redundant data.")
    optimize: bool | None = Field(default=None, validation_alias="Optimize", serialization_alias="Optimize", description="Optimize page content streams to reduce file size and improve rendering efficiency.")
    remove_piece_information: bool | None = Field(default=None, validation_alias="RemovePieceInformation", serialization_alias="RemovePieceInformation", description="Remove private metadata dictionaries from design applications (Adobe Illustrator, Photoshop, etc.) that are not essential for document display.")
    remove_embedded_files: bool | None = Field(default=None, validation_alias="RemoveEmbeddedFiles", serialization_alias="RemoveEmbeddedFiles", description="Remove embedded files and attachments from the PDF document.")
    remove_structure_information: bool | None = Field(default=None, validation_alias="RemoveStructureInformation", serialization_alias="RemoveStructureInformation", description="Remove all structural information and tagging used for accessibility and document organization.")
    remove_metadata: bool | None = Field(default=None, validation_alias="RemoveMetadata", serialization_alias="RemoveMetadata", description="Remove XMP metadata and document properties embedded in the PDF catalog and marked content.")
    remove_unused_resources: bool | None = Field(default=None, validation_alias="RemoveUnusedResources", serialization_alias="RemoveUnusedResources", description="Remove unused resource references such as fonts, images, and patterns that are defined but not displayed in the document.")
    linearize: bool | None = Field(default=None, validation_alias="Linearize", serialization_alias="Linearize", description="Linearize the PDF structure and optimize for fast web viewing, enabling progressive rendering as the file downloads.")
    preserve_pdfa: bool | None = Field(default=None, validation_alias="PreservePdfa", serialization_alias="PreservePdfa", description="Maintain PDF/A compliance standards during compression to ensure long-term archival compatibility.")
class PostConvertPdfToCompressRequest(StrictModel):
    """Compress a PDF file using configurable optimization techniques to reduce file size while preserving document quality. Supports preset compression profiles or granular control over specific compression options."""
    body: PostConvertPdfToCompressRequestBody | None = None

# Operation: crop_pdf
class PostConvertPdfToCropRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to crop. Accepts a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The API sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., report_0.pdf, report_1.pdf).")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password to unlock a protected PDF file.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to crop using page numbers, ranges, or keywords. Supports comma-separated values and ranges (e.g., 1,2,5-last).")
    crop_mode: Literal["auto", "size", "margins"] | None = Field(default=None, validation_alias="CropMode", serialization_alias="CropMode", description="Cropping strategy: automatic content detection, fixed margins, or exact dimensions.")
    measurement_unit: Literal["pt", "in", "mm", "cm"] | None = Field(default=None, validation_alias="MeasurementUnit", serialization_alias="MeasurementUnit", description="Unit of measurement for width, height, and margin values.")
    auto_strategy: Literal["perPage", "uniform"] | None = Field(default=None, validation_alias="AutoStrategy", serialization_alias="AutoStrategy", description="Determines whether automatic cropping is applied individually per page or uniformly across all pages. Only applies when CropMode is set to auto.")
    auto_padding: float | None = Field(default=None, validation_alias="AutoPadding", serialization_alias="AutoPadding", description="Padding distance to add around automatically detected content, using the selected measurement unit. Only applies when CropMode is set to auto.", ge=0, le=30000)
    anchor: Literal["center", "topleft", "top", "topright", "left", "right", "bottom", "bottomright"] | None = Field(default=None, validation_alias="Anchor", serialization_alias="Anchor", description="Reference point for positioning the crop rectangle when using fixed width and height dimensions.")
    vertical_margin: float | None = Field(default=None, validation_alias="VerticalMargin", serialization_alias="VerticalMargin", description="Top and bottom margin distances to apply when cropping with margins, using the selected measurement unit. Only applies when CropMode is set to margins.", ge=0, le=30000)
    horizontal_margin: float | None = Field(default=None, validation_alias="HorizontalMargin", serialization_alias="HorizontalMargin", description="Left and right margin distances to apply when cropping with margins, using the selected measurement unit. Only applies when CropMode is set to margins.", ge=0, le=30000)
class PostConvertPdfToCropRequest(StrictModel):
    """Crop PDF pages by automatically detecting content, applying margins, or resizing to specific dimensions. Supports selective page ranges and multiple cropping strategies."""
    body: PostConvertPdfToCropRequestBody | None = None

# Operation: convert_pdf_to_csv
class PostConvertPdfToCsvRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output CSV file. The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.csv, report_1.csv) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5).")
    enable_ocr: Literal["Scanned", "All", "None"] | None = Field(default=None, validation_alias="EnableOcr", serialization_alias="EnableOcr", description="Controls optical character recognition behavior. Use 'Scanned' for OCR on scanned pages only, 'All' for all pages, or 'None' to disable OCR.")
    ocr_language: Literal["ar", "ca", "zh-cn", "zh-tw", "da", "nl", "en", "fi", "fa", "de", "el", "he", "it", "ja", "ko", "lt", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(default=None, validation_alias="OcrLanguage", serialization_alias="OcrLanguage", description="Language for OCR processing. Supports multiple languages including English, Spanish, Chinese, Arabic, and others. Contact support to request additional languages.")
    delimiter: str | None = Field(default=None, validation_alias="Delimiter", serialization_alias="Delimiter", description="Character used to separate fields in the output CSV file.")
class PostConvertPdfToCsvRequest(StrictModel):
    """Converts a PDF document to CSV format with support for password-protected files, selective page ranges, and optical character recognition. Automatically handles file naming and delimiter configuration for structured data extraction."""
    body: PostConvertPdfToCsvRequestBody | None = None

# Operation: delete_pdf_pages
class PostConvertPdfToDeletePagesRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to process. Accepts a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., document_0.pdf, document_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Pages to delete specified as a range (e.g., 1-10) or comma-separated individual page numbers (e.g., 1,2,5).")
    delete_blank_pages: bool | None = Field(default=None, validation_alias="DeleteBlankPages", serialization_alias="DeleteBlankPages", description="Automatically detect and remove blank pages from the PDF.")
class PostConvertPdfToDeletePagesRequest(StrictModel):
    """Remove specified pages from a PDF document. Supports deletion by page range, individual pages, or automatic blank page detection."""
    body: PostConvertPdfToDeletePagesRequestBody | None = None

# Operation: convert_pdf_to_docx
class PostConvertPdfToDocxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output DOCX file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.docx, filename_1.docx) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to the first 2000 pages.")
    wysiwyg: bool | None = Field(default=None, validation_alias="Wysiwyg", serialization_alias="Wysiwyg", description="When enabled, preserves exact PDF formatting by converting layout elements to editable text boxes in the DOCX output.")
    ocr_mode: Literal["auto", "force", "never"] | None = Field(default=None, validation_alias="OcrMode", serialization_alias="OcrMode", description="Controls OCR application during conversion. Use 'auto' to apply OCR only when needed, 'force' to OCR all pages, or 'never' to disable OCR entirely.")
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(default=None, validation_alias="OcrLanguage", serialization_alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use 'auto' for automatic detection, or manually select a language code if auto-detection fails.")
    annotations_: Literal["textBox", "comment", "none"] | None = Field(default=None, validation_alias="Annotations", serialization_alias="Annotations", description="Determines how PDF annotations are handled in the output. Use 'textBox' to convert annotations to editable text boxes, 'comment' to convert them to Word comments, or 'none' to exclude annotations.")
class PostConvertPdfToDocxRequest(StrictModel):
    """Converts a PDF document to DOCX format with support for password-protected files, selective page ranges, OCR processing, and annotation handling. Preserves formatting through text box conversion and supports multiple OCR languages for accurate text recognition."""
    body: PostConvertPdfToDocxRequestBody | None = None

# Operation: extract_data_from_pdf
class PostConvertPdfToExtractRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to process. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The system sanitizes the filename, appends the appropriate extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple outputs to ensure unique, safe file naming.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    document_type: Literal["auto", "invoice", "receipt", "contract", "identification", "financial", "form", "manual"] | None = Field(default=None, validation_alias="DocumentType", serialization_alias="DocumentType", description="Document category to apply optimized extraction rules. Use 'Auto' for automatic detection, select a specific type (Invoice, Receipt, Contract, etc.) for improved accuracy, or choose 'Manual' to use only custom extraction fields.")
    custom_extraction_data: str | None = Field(default=None, validation_alias="CustomExtractionData", serialization_alias="CustomExtractionData", description="JSON array of custom field definitions for extraction. Each object specifies a FieldName (output key) and Extract (description of what to extract). Used when DocumentType is 'Manual' or to supplement predefined extraction.")
    minimum_confidence: float | None = Field(default=None, validation_alias="MinimumConfidence", serialization_alias="MinimumConfidence", description="Minimum confidence score (0.01 to 0.99) for AI-based sensitive data detection. Higher values reduce false positives but may miss subtle matches.", ge=0.01, le=0.99)
class PostConvertPdfToExtractRequest(StrictModel):
    """Extract structured data from PDF documents using AI-powered recognition. Supports predefined document types (invoices, receipts, contracts, etc.) or custom field extraction with configurable confidence thresholds."""
    body: PostConvertPdfToExtractRequestBody | None = None

# Operation: extract_images_from_pdf
class PostConvertPdfToExtractImagesRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to process. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The API sanitizes the filename, appends the appropriate extension, and adds indexing (e.g., filename_0, filename_1) for multiple outputs.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password for opening password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to process. Use ranges (e.g., 1-10) or comma-separated individual pages (e.g., 1,2,5).")
    image_output_format: Literal["default", "jpg", "png", "tiff"] | None = Field(default=None, validation_alias="ImageOutputFormat", serialization_alias="ImageOutputFormat", description="Output format for extracted images. Use 'default' to automatically select the most suitable format and extract all images including hidden ones; other formats apply the MinimumImageWidth and MinimumImageHeight filters.")
    minimum_image_width: int | None = Field(default=None, validation_alias="MinimumImageWidth", serialization_alias="MinimumImageWidth", description="Minimum width in pixels for extracted images. Images narrower than this threshold are excluded.", ge=0, le=1000)
    minimum_image_height: int | None = Field(default=None, validation_alias="MinimumImageHeight", serialization_alias="MinimumImageHeight", description="Minimum height in pixels for extracted images. Images shorter than this threshold are excluded.", ge=0, le=1000)
class PostConvertPdfToExtractImagesRequest(StrictModel):
    """Extract images from PDF documents with configurable filtering by size and page range. Supports password-protected PDFs and multiple output formats."""
    body: PostConvertPdfToExtractImagesRequestBody | None = None

# Operation: extract_pdf_form_fields
class PostConvertPdfToFdfExtractRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output FDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.fdf, output_1.fdf) for multiple files to ensure unique, safe naming.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    include_alternate_names: bool | None = Field(default=None, validation_alias="IncludeAlternateNames", serialization_alias="IncludeAlternateNames", description="When enabled, includes alternate field names (tooltip text) from the PDF in the FDF output for better field identification.")
class PostConvertPdfToFdfExtractRequest(StrictModel):
    """Converts a PDF document to FDF (Forms Data Format) while extracting form field data. Optionally includes alternate field names as tooltips in the output."""
    body: PostConvertPdfToFdfExtractRequestBody | None = None

# Operation: import_pdf_with_fdf_form_data
class PostConvertPdfToFdfImportRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to be converted. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    fdf_file: str | None = Field(default=None, validation_alias="FdfFile", serialization_alias="FdfFile", description="The FDF (Forms Data Format) file containing structured form field data to be imported into the PDF. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s) generated by the conversion. The system automatically sanitizes the filename, appends the appropriate file extension, and adds numeric indexing (e.g., `_0`, `_1`) when multiple output files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents. Only needed if the input PDF is encrypted.")
class PostConvertPdfToFdfImportRequest(StrictModel):
    """Convert a PDF document by importing and merging structured form data from an FDF file. This operation combines a PDF with FDF form data to populate form fields and generate the merged output."""
    body: PostConvertPdfToFdfImportRequestBody | None = None

# Operation: flatten_pdf
class PostConvertPdfToFlattenRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to be flattened. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files to ensure unique and safe file naming.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open a protected or encrypted PDF document.")
    flatten_controls: bool | None = Field(default=None, validation_alias="FlattenControls", serialization_alias="FlattenControls", description="Convert form controls (text fields, checkboxes, dropdowns) into static content, preventing editing while maintaining their original visual appearance.")
    flatten_widgets: bool | None = Field(default=None, validation_alias="FlattenWidgets", serialization_alias="FlattenWidgets", description="Convert widget annotations (buttons, list boxes, signature fields) into static content, removing interactivity while preserving their original visual appearance.")
    flatten_text: bool | None = Field(default=None, validation_alias="FlattenText", serialization_alias="FlattenText", description="Convert text into vectorial paths to prevent text selection, copying, and extraction, making the PDF read-only while maintaining original vector quality.")
class PostConvertPdfToFlattenRequest(StrictModel):
    """Convert a PDF document into a flattened format by removing interactivity from form controls, widgets, and text elements. This operation transforms editable and interactive PDF components into static page content while preserving visual appearance."""
    body: PostConvertPdfToFlattenRequestBody | None = None

# Operation: convert_pdf_to_html
class PostConvertPdfToHtmlRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output HTML file(s). The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.html, report_1.html) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to the first 2000 pages.")
    wysiwyg: bool | None = Field(default=None, validation_alias="Wysiwyg", serialization_alias="Wysiwyg", description="When enabled, preserves exact PDF formatting by converting text to HTML text boxes. Maintains visual layout fidelity during conversion.")
    ocr_mode: Literal["auto", "force", "never"] | None = Field(default=None, validation_alias="OcrMode", serialization_alias="OcrMode", description="Controls OCR application during conversion. Auto applies OCR only when needed, Force applies OCR to all pages, and Never disables OCR entirely.")
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(default=None, validation_alias="OcrLanguage", serialization_alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use auto-detection by default, or manually select a language if auto-detection fails.")
class PostConvertPdfToHtmlRequest(StrictModel):
    """Converts PDF documents to HTML format with support for password-protected files, selective page ranges, and optical character recognition. Preserves formatting using text boxes and offers flexible OCR configuration for accurate text extraction."""
    body: PostConvertPdfToHtmlRequestBody | None = None

# Operation: add_watermark_to_pdf
class PostConvertPdfToImageWatermarkRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output image file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    image_file: str | None = Field(default=None, validation_alias="ImageFile", serialization_alias="ImageFile", description="Image file to use as the watermark. Accepts a file URL or binary image content.", json_schema_extra={'format': 'binary'})
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to process. Use ranges (e.g., 1-10) or comma-separated page numbers (e.g., 1,2,5).")
    opacity: int | None = Field(default=None, validation_alias="Opacity", serialization_alias="Opacity", description="Controls the transparency of the watermark, where 0 is fully transparent and 100 is fully opaque.", ge=0, le=100)
    style: Literal["stamp", "watermark"] | None = Field(default=None, validation_alias="Style", serialization_alias="Style", description="Determines watermark placement: 'stamp' overlays the watermark on top of page content, while 'watermark' places it behind the content.")
    go_to_link: str | None = Field(default=None, validation_alias="GoToLink", serialization_alias="GoToLink", description="Web address to navigate to when the watermark is clicked.")
    go_to_page: str | None = Field(default=None, validation_alias="GoToPage", serialization_alias="GoToPage", description="Page number to navigate to when the watermark is clicked.")
    page_rotation: bool | None = Field(default=None, validation_alias="PageRotation", serialization_alias="PageRotation", description="When enabled, the watermark rotates with the PDF page. When disabled, the watermark maintains its original orientation regardless of page rotation.")
    page_box: Literal["mediabox", "trimbox", "bleedbox", "cropbox"] | None = Field(default=None, validation_alias="PageBox", serialization_alias="PageBox", description="Defines the PDF page area used as the reference for watermark placement (mediabox is the full page, trimbox excludes margins, bleedbox is for printing, cropbox is the visible area).")
    horizontal_alignment: Literal["left", "center", "right"] | None = Field(default=None, validation_alias="HorizontalAlignment", serialization_alias="HorizontalAlignment", description="Horizontal alignment of the watermark on the page.")
    vertical_alignment: Literal["top", "center", "bottom"] | None = Field(default=None, validation_alias="VerticalAlignment", serialization_alias="VerticalAlignment", description="Vertical alignment of the watermark on the page.")
    measurement_unit: Literal["pt", "in", "mm", "cm"] | None = Field(default=None, validation_alias="MeasurementUnit", serialization_alias="MeasurementUnit", description="Unit of measurement used for watermark position and size parameters.")
    offset_x: dict | None = Field(default=None, validation_alias="OffsetX", serialization_alias="OffsetX", description="Specifies the watermark offset along the X-axis. Positive values move the watermark to the right, while negative values move it to the left, using the selected `MeasurementUnit`.", ge=-10000, le=10000)
    offset_y: float | None = Field(default=None, validation_alias="OffsetY", serialization_alias="OffsetY", description="Specifies the watermark offset along the Y-axis. Positive values move the watermark downward, while negative values move it upward, using the selected `MeasurementUnit`.", ge=-10000, le=10000)
class PostConvertPdfToImageWatermarkRequest(StrictModel):
    """Convert a PDF document to images with an optional watermark overlay or stamp. Supports customizable watermark positioning, styling, opacity, and interactive click-through functionality."""
    body: PostConvertPdfToImageWatermarkRequestBody | None = None

# Operation: convert_pdf_to_jpg
class PostConvertPdfToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output JPG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multi-page conversions.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open a password-protected PDF document.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to first 2000 pages.")
    rotate: Literal["default", "none", "rotate90", "rotate180", "rotate270"] | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Applies rotation to PDF pages before conversion. Select 'default' to use the PDF's embedded rotation settings, or specify a fixed rotation angle.")
    crop_to: Literal["BoundingBox", "TrimBox", "MediaBox", "ArtBox", "BleedBox"] | None = Field(default=None, validation_alias="CropTo", serialization_alias="CropTo", description="Defines which page boundary to use for cropping during conversion. Different box types represent different content areas within the PDF page.")
    color_space: Literal["rgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Sets the color space for the output JPG image. Choose RGB for standard color, CMYK for print-ready output, or grayscale for black and white.")
class PostConvertPdfToJpgRequest(StrictModel):
    """Convert PDF documents to JPG image format with support for page selection, rotation, cropping, and color space customization. Handles password-protected PDFs and generates multiple images for multi-page documents."""
    body: PostConvertPdfToJpgRequestBody | None = None

# Operation: merge_pdfs
class PostConvertPdfToMergeRequestBody(StrictModel):
    files: list[str] | None = Field(default=None, validation_alias="Files", serialization_alias="Files", description="Array of PDF files to merge. Each file can be provided as a URL or file content. Files are merged in the order provided.")
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output merged PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing if multiple output files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the source PDF files if they are password-protected.")
    remove_duplicate_fonts: bool | None = Field(default=None, validation_alias="RemoveDuplicateFonts", serialization_alias="RemoveDuplicateFonts", description="When enabled, prevents duplicate fonts from being included in the merged PDF, reducing file size.")
    bookmarks_toc: Literal["disabled", "filename", "title"] | None = Field(default=None, validation_alias="BookmarksToc", serialization_alias="BookmarksToc", description="Adds a top-level bookmark for each merged file using either the filename or the PDF title from metadata.")
    open_page: int | None = Field(default=None, validation_alias="OpenPage", serialization_alias="OpenPage", description="Specifies the page number where the merged PDF document should open when first displayed.", ge=1, le=3000)
class PostConvertPdfToMergeRequest(StrictModel):
    """Merge multiple PDF files into a single document with optional font deduplication, table of contents bookmarks, and password protection support."""
    body: PostConvertPdfToMergeRequestBody | None = None

# Operation: convert_pdf_to_metadata
class PostConvertPdfToMetaRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., _0, _1) when multiple files are generated to ensure unique, safe file naming.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="The password required to open the PDF if it is password-protected. Only needed for encrypted documents.")
class PostConvertPdfToMetaRequest(StrictModel):
    """Converts a PDF document to metadata format, extracting structured information from the file. Supports password-protected documents and customizable output file naming."""
    body: PostConvertPdfToMetaRequestBody | None = None

# Operation: extract_text_from_pdf
class PostConvertPdfToOcrRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to process. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output file(s). The system automatically sanitizes the name, appends the appropriate file extension based on output format, and adds numeric suffixes for multiple files to ensure unique, safe filenames.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to process. Use ranges (e.g., 1-10) or comma-separated individual pages (e.g., 1,2,5).")
    ocr_mode: Literal["auto", "always", "reprocess"] | None = Field(default=None, validation_alias="OcrMode", serialization_alias="OcrMode", description="Controls how OCR is applied to pages. Auto skips pages with existing text, Always adds OCR while preserving existing text, and Reprocess regenerates the text layer for all pages.")
    ocr_language: Literal["ar", "ca", "zh-cn", "zh-tw", "da", "nl", "en", "fi", "fa", "de", "el", "he", "it", "ja", "ko", "lt", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(default=None, validation_alias="OcrLanguage", serialization_alias="OcrLanguage", description="Language for text recognition. Supports multiple languages including English, Spanish, Chinese, Arabic, and others. Contact support to request additional languages.")
    output_type: Literal["pdf", "txt"] | None = Field(default=None, validation_alias="OutputType", serialization_alias="OutputType", description="Format for the extracted text. PDF embeds the OCR text layer into the document for searchability, while TXT returns plain text content only.")
    page_segmentation_mode: Literal["sparseText", "sparseTextOsd", "auto", "autoOsd", "singleLine", "singleColumn", "singleWord"] | None = Field(default=None, validation_alias="PageSegmentationMode", serialization_alias="PageSegmentationMode", description="Determines how the OCR engine analyzes document layout and detects text. SparseText finds scattered text without ordering, SparseTextOsd adds orientation detection, Auto selects the best mode automatically, AutoOsd combines auto-detection with orientation handling, SingleColumn assumes single-column layouts, SingleLine treats content as one line, and SingleWord recognizes isolated words.")
class PostConvertPdfToOcrRequest(StrictModel):
    """Converts a PDF document to searchable text using OCR (Optical Character Recognition). Supports multiple languages, flexible page ranges, and configurable text extraction modes to handle various document layouts and existing text layers."""
    body: PostConvertPdfToOcrRequestBody | None = None

# Operation: convert_pdf_to_pcl
class PostConvertPdfToPclRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PCL file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pcl, output_1.pcl) for multiple output files.")
    color_mode: Literal["color", "monochrome"] | None = Field(default=None, validation_alias="ColorMode", serialization_alias="ColorMode", description="The color mode for the output document. Choose between full color or monochrome rendering.")
    resolution: int | None = Field(default=None, validation_alias="Resolution", serialization_alias="Resolution", description="The output resolution in dots per inch (DPI). Higher values improve image quality but increase file size. Valid range is 10 to 1000 DPI.", ge=10, le=1000)
class PostConvertPdfToPclRequest(StrictModel):
    """Converts a PDF document to PCL (Printer Command Language) format with customizable output settings. Supports color mode selection and resolution adjustment for optimal print quality and file size balance."""
    body: PostConvertPdfToPclRequestBody | None = None

# Operation: convert_pdf_to_pdf
class PostConvertPdfToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `report_0.pdf`, `report_1.pdf`) for multiple output files.")
    pdf_version: Literal["1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "2.0"] | None = Field(default=None, validation_alias="PdfVersion", serialization_alias="PdfVersion", description="The PDF specification version to use for the output document.")
    pdf_title: str | None = Field(default=None, validation_alias="PdfTitle", serialization_alias="PdfTitle", description="Custom title for the PDF document metadata. Use a single quote and space (' ') to remove the title entirely.")
    pdf_subject: str | None = Field(default=None, validation_alias="PdfSubject", serialization_alias="PdfSubject", description="Custom subject for the PDF document metadata. Use a single quote and space (' ') to remove the subject entirely.")
    pdf_author: str | None = Field(default=None, validation_alias="PdfAuthor", serialization_alias="PdfAuthor", description="Custom author name for the PDF document metadata. Use a single quote and space (' ') to remove the author entirely.")
    pdf_creator: str | None = Field(default=None, validation_alias="PdfCreator", serialization_alias="PdfCreator", description="Custom creator application name for the PDF document metadata. Use a single quote and space (' ') to remove the creator entirely.")
    pdf_keywords: str | None = Field(default=None, validation_alias="PdfKeywords", serialization_alias="PdfKeywords", description="Custom keywords for the PDF document metadata, typically used for searchability. Use a single quote and space (' ') to remove the keywords entirely.")
    open_page: int | None = Field(default=None, validation_alias="OpenPage", serialization_alias="OpenPage", description="The page number where the PDF should open when first displayed. Must be between 1 and 3000.", ge=1, le=3000)
    open_zoom: Literal["Default", "ActualSize", "FitPage", "FitWidth", "FitHeight", "FitVisible", "25", "50", "75", "100", "125", "150", "200", "400", "800", "1600", "2400", "3200", "6400"] | None = Field(default=None, validation_alias="OpenZoom", serialization_alias="OpenZoom", description="The default zoom level applied when opening the PDF. Choose from preset percentages or fit-to-page options.")
    color_space: Literal["Default", "RGB", "CMYK", "Gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="The color space model for the output PDF. RGB is suitable for screen display, CMYK for professional printing, and Gray for grayscale documents.")
class PostConvertPdfToPdfRequest(StrictModel):
    """Convert a PDF document while optionally customizing metadata, viewer settings, and color space properties. Useful for updating PDF versions, embedding document information, or adjusting display preferences."""
    body: PostConvertPdfToPdfRequestBody | None = None

# Operation: add_watermark_to_pdf_document
class PostConvertPdfToPdfWatermarkRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to be watermarked. Can be provided as a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output watermarked PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input PDF if it is password-protected.")
    overlay_file: str | None = Field(default=None, validation_alias="OverlayFile", serialization_alias="OverlayFile", description="PDF file to use as the watermark overlay. Can be provided as a URL or binary file content.", json_schema_extra={'format': 'binary'})
    overlay_page: int | None = Field(default=None, validation_alias="OverlayPage", serialization_alias="OverlayPage", description="Page number from the overlay file to use as the watermark. Must be a valid page within the overlay document.", ge=1, le=2000)
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Pages to apply the watermark to, specified as a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to all pages.")
    opacity: int | None = Field(default=None, validation_alias="Opacity", serialization_alias="Opacity", description="Watermark transparency level as a percentage. Lower values make the watermark more transparent.", ge=0, le=100)
    style: Literal["stamp", "watermark"] | None = Field(default=None, validation_alias="Style", serialization_alias="Style", description="Watermark placement style. Stamp places the watermark over page content, while watermark places it beneath page content.")
    go_to_link: str | None = Field(default=None, validation_alias="GoToLink", serialization_alias="GoToLink", description="Web address to navigate to when the watermark is clicked. Creates an interactive link on the watermark.")
    go_to_page: str | None = Field(default=None, validation_alias="GoToPage", serialization_alias="GoToPage", description="Page number to navigate to when the watermark is clicked. Creates an internal document link on the watermark.")
    page_rotation: bool | None = Field(default=None, validation_alias="PageRotation", serialization_alias="PageRotation", description="Whether the watermark should rotate together with the PDF page. When enabled, watermark orientation matches page rotation; when disabled, watermark maintains fixed orientation.")
    page_box: Literal["mediabox", "trimbox", "bleedbox", "cropbox"] | None = Field(default=None, validation_alias="PageBox", serialization_alias="PageBox", description="PDF page box used as the reference area for watermark positioning. Different boxes define different page boundaries (media, trim, bleed, or crop).")
    measurement_unit: Literal["pt", "in", "mm", "cm"] | None = Field(default=None, validation_alias="MeasurementUnit", serialization_alias="MeasurementUnit", description="Unit of measurement for watermark position and size parameters.")
    horizontal_alignment: Literal["left", "center", "right"] | None = Field(default=None, validation_alias="HorizontalAlignment", serialization_alias="HorizontalAlignment", description="Horizontal alignment of the watermark relative to the page.")
    vertical_alignment: Literal["top", "center", "bottom"] | None = Field(default=None, validation_alias="VerticalAlignment", serialization_alias="VerticalAlignment", description="Vertical alignment of the watermark relative to the page.")
    offset_x: dict | None = Field(default=None, validation_alias="OffsetX", serialization_alias="OffsetX", description="Specifies the watermark offset along the X-axis. Positive values move the watermark to the right, while negative values move it to the left, using the selected `MeasurementUnit`.", ge=-10000, le=10000)
    offset_y: float | None = Field(default=None, validation_alias="OffsetY", serialization_alias="OffsetY", description="Specifies the watermark offset along the Y-axis. Positive values move the watermark downward, while negative values move it upward, using the selected `MeasurementUnit`.", ge=-10000, le=10000)
class PostConvertPdfToPdfWatermarkRequest(StrictModel):
    """Add a watermark or stamp overlay to a PDF document with customizable positioning, opacity, and interactive elements. Supports applying watermarks across specified page ranges with flexible alignment and styling options."""
    body: PostConvertPdfToPdfWatermarkRequestBody | None = None

# Operation: convert_pdf_to_pdfa
class PostConvertPdfToPdfaRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF/A file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open a password-protected PDF document.")
    pdfa_version: Literal["pdfA1a", "pdfA1b", "pdfA2a", "pdfA2b", "pdfA2u", "pdfA3a", "pdfA3b", "pdfA3u", "pdfA4", "pdfA4e", "pdfA4f"] | None = Field(default=None, validation_alias="PdfaVersion", serialization_alias="PdfaVersion", description="The PDF/A compliance version to target for the output document.")
    invoice_format: Literal["none", "facturX", "zugferd1", "zugferd2"] | None = Field(default=None, validation_alias="InvoiceFormat", serialization_alias="InvoiceFormat", description="E-invoice format to embed in the PDF. When specified, overrides the PdfaVersion setting and outputs PDF/A-3 format. Requires a valid structured invoice XML file.")
    invoice_file: str | None = Field(default=None, validation_alias="InvoiceFile", serialization_alias="InvoiceFile", description="Structured invoice XML file (ZUGFeRD or Factur-X format) to embed for hybrid-invoice compatibility. Required when InvoiceFormat is set to a value other than 'none'.", json_schema_extra={'format': 'binary'})
    linearize: bool | None = Field(default=None, validation_alias="Linearize", serialization_alias="Linearize", description="Linearize the PDF structure and optimize for fast web viewing and streaming.")
class PostConvertPdfToPdfaRequest(StrictModel):
    """Converts a PDF document to PDF/A format for long-term archival compliance. Supports optional password-protected PDFs, e-invoice embedding (ZUGFeRD/Factur-X), and web optimization."""
    body: PostConvertPdfToPdfaRequestBody | None = None

# Operation: convert_pdf_to_pdfua
class PostConvertPdfToPdfuaRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input PDF if it is password-protected.")
    linearize: bool | None = Field(default=None, validation_alias="Linearize", serialization_alias="Linearize", description="Enables linearization of the PDF file to optimize for fast web viewing and streaming.")
class PostConvertPdfToPdfuaRequest(StrictModel):
    """Converts a standard PDF file to PDF/UA (Universal Accessibility) format, ensuring compliance with accessibility standards. Optionally linearizes the output for optimized web viewing performance."""
    body: PostConvertPdfToPdfuaRequestBody | None = None

# Operation: convert_pdf_to_png
class PostConvertPdfToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds an index suffix for multiple output files to ensure unique identification.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open a protected or encrypted PDF document.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range or comma-separated list format. Allows selective conversion of specific pages from the PDF.")
    rotate: Literal["default", "none", "rotate90", "rotate180", "rotate270"] | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Applies rotation to PDF pages before conversion to PNG. Select from predefined rotation angles or use the default orientation.")
    crop_to: Literal["BoundingBox", "TrimBox", "MediaBox", "ArtBox", "BleedBox"] | None = Field(default=None, validation_alias="CropTo", serialization_alias="CropTo", description="Defines which PDF box boundary to use for cropping the page during conversion. Different box types capture different content areas of the PDF page.")
    background_color: str | None = Field(default=None, validation_alias="BackgroundColor", serialization_alias="BackgroundColor", description="Sets the background color for transparent areas in the PDF. Accepts color names, RGB values, or hexadecimal color codes. Use 'transparent' to preserve transparency in the output PNG.")
class PostConvertPdfToPngRequest(StrictModel):
    """Converts PDF documents to PNG image format with support for page selection, rotation, cropping, and background color customization. Handles password-protected PDFs and generates multiple output images for multi-page documents."""
    body: PostConvertPdfToPngRequestBody | None = None

# Operation: convert_pdf_to_pptx
class PostConvertPdfToPptxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PowerPoint file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., report_0.pptx, report_1.pptx) when generating multiple files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5).")
    ocr_mode: Literal["auto", "force", "never"] | None = Field(default=None, validation_alias="OcrMode", serialization_alias="OcrMode", description="Controls when optical character recognition is applied during conversion. Auto applies OCR only when needed, Force applies it to all pages, and Never disables it entirely.")
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(default=None, validation_alias="OcrLanguage", serialization_alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use auto-detection by default, or manually select a language if auto-detection fails.")
    text_recovery_mode: Literal["auto", "always", "never"] | None = Field(default=None, validation_alias="TextRecoveryMode", serialization_alias="TextRecoveryMode", description="Determines how text is recovered from PDFs with non-standard encodings. Auto detects and recovers text only when needed, Always forces recovery for all text, and Never disables recovery.")
class PostConvertPdfToPptxRequest(StrictModel):
    """Converts a PDF document to PowerPoint (PPTX) format with support for password-protected files, selective page ranges, and optical character recognition (OCR) for text extraction."""
    body: PostConvertPdfToPptxRequestBody | None = None

# Operation: convert_pdf_to_print
class PostConvertPdfToPrintRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The system sanitizes the filename, appends the appropriate extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open a protected or encrypted PDF document.")
    trim_size: Literal["default", "a2", "a3", "a4", "a5", "a6", "letter", "legal", "custom"] | None = Field(default=None, validation_alias="TrimSize", serialization_alias="TrimSize", description="Page size to apply to every page in the output. Select 'default' to preserve each page's current size, or 'custom' to specify exact dimensions via TrimWidth and TrimHeight.")
    trim_width: int | None = Field(default=None, validation_alias="TrimWidth", serialization_alias="TrimWidth", description="Width of the trim box in millimeters when TrimSize is set to 'custom'. Must be between 10 and 1000 mm.", ge=10, le=1000)
    bleed_mode: Literal["none", "mirror", "stretch"] | None = Field(default=None, validation_alias="BleedMode", serialization_alias="BleedMode", description="Controls how bleed content is generated. 'Mirror' reflects page content outward for full-bleed preview, 'Stretch' extends edge pixels into the bleed area, or 'None' disables bleed fabrication.")
    trim_marks: bool | None = Field(default=None, validation_alias="TrimMarks", serialization_alias="TrimMarks", description="When enabled, adds crop marks positioned outside the bleed box to indicate trim boundaries.")
    registration_marks: bool | None = Field(default=None, validation_alias="RegistrationMarks", serialization_alias="RegistrationMarks", description="When enabled, adds registration targets (crosshairs) centered at least 3mm outside the bleed box on each edge for color registration alignment.")
    slug: str | None = Field(default=None, validation_alias="Slug", serialization_alias="Slug", description="Text to display at the bottom of the media box, typically used for printed file names, order numbers, or customer information.")
    tint_bars: bool | None = Field(default=None, validation_alias="TintBars", serialization_alias="TintBars", description="When enabled, adds grayscale and color control bars at the top of the page, positioned outside the trim box for quality verification.")
    color_space: Literal["default", "rgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Defines the color space for the output PDF. 'Default' preserves the original color space, or specify RGB, CMYK, or grayscale conversion.")
    output_intent: Literal["none", "fogra39", "fogra51", "gracol2013", "swop2013", "japancolor2011", "custom"] | None = Field(default=None, validation_alias="OutputIntent", serialization_alias="OutputIntent", description="Embeds an ICC color profile as the PDF's output intent for color management. Select 'custom' to provide a custom ICC profile file via OutputIntentIccFile.")
    output_intent_icc_file: str | None = Field(default=None, validation_alias="OutputIntentIccFile", serialization_alias="OutputIntentIccFile", description="Custom ICC profile file to embed as the PDF output intent. Required when OutputIntent is set to 'custom'.", json_schema_extra={'format': 'binary'})
    downsample_images: bool | None = Field(default=None, validation_alias="DownsampleImages", serialization_alias="DownsampleImages", description="When enabled, reduces resolution of images exceeding the target resolution to minimize file size while maintaining quality.")
    resolution: int | None = Field(default=None, validation_alias="Resolution", serialization_alias="Resolution", description="Target resolution in pixels per inch (PPI) used for rasterization tasks such as bleed fabrication and image downsampling. Valid range is 10 to 800 PPI.", ge=10, le=800)
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a comma-separated range (e.g., 1,2,5-last). Supports keywords 'even', 'odd', and 'last'. Maximum of 100 pages will be processed per conversion.")
class PostConvertPdfToPrintRequest(StrictModel):
    """Converts a PDF document to print-ready format with support for professional print specifications including trim sizes, bleed modes, color spaces, and registration marks. Supports page range selection and ICC profile embedding for color-managed workflows."""
    body: PostConvertPdfToPrintRequestBody | None = None

# Operation: protect_pdf
class PostConvertPdfToProtectRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to protect. Accepts either a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output protected PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., document_0.pdf, document_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the protected PDF document. Used when the document has existing protection that needs to be processed.")
    encryption_algorithm: Literal["Standard40Bit", "Standard128Bit", "Aes128Bit", "Aes256Bit"] | None = Field(default=None, validation_alias="EncryptionAlgorithm", serialization_alias="EncryptionAlgorithm", description="Algorithm used to encrypt the PDF document. Determines the strength and type of encryption applied.")
    encrypt_meta: bool | None = Field(default=None, validation_alias="EncryptMeta", serialization_alias="EncryptMeta", description="Whether to encrypt the PDF metadata (document properties, author, title, etc.) in addition to the content.")
    user_password: str | None = Field(default=None, validation_alias="UserPassword", serialization_alias="UserPassword", description="User password (document open password) that recipients must enter to view the PDF in Acrobat Reader. Distinct from owner password.")
    owner_password: str | None = Field(default=None, validation_alias="OwnerPassword", serialization_alias="OwnerPassword", description="Owner password (permissions password) that controls restrictions on printing, editing, and copying. Recipients can open the document without this password but cannot modify restrictions.")
    respect_owner_password: bool | None = Field(default=None, validation_alias="RespectOwnerPassword", serialization_alias="RespectOwnerPassword", description="Whether to preserve the original document's owner password and permissions. When enabled, requires the correct owner password in the Password field. When disabled, existing restrictions are removed.")
    assemble_document: bool | None = Field(default=None, validation_alias="AssembleDocument", serialization_alias="AssembleDocument", description="Whether to allow assembly operations such as inserting, rotating, or deleting pages, and creating bookmarks or thumbnail images.")
    modify_contents: bool | None = Field(default=None, validation_alias="ModifyContents", serialization_alias="ModifyContents", description="Whether to allow modifications to the document content.")
    extract_contents: bool | None = Field(default=None, validation_alias="ExtractContents", serialization_alias="ExtractContents", description="Whether to allow extraction of text and graphics from the document.")
    modify_annotations: bool | None = Field(default=None, validation_alias="ModifyAnnotations", serialization_alias="ModifyAnnotations", description="Whether to allow adding or modifying text annotations and filling interactive form fields.")
    fill_form_fields: bool | None = Field(default=None, validation_alias="FillFormFields", serialization_alias="FillFormFields", description="Whether to allow filling in existing interactive form fields, including signature fields.")
    print_document: bool | None = Field(default=None, validation_alias="PrintDocument", serialization_alias="PrintDocument", description="Whether to allow printing the document.")
    print_faithful_copy: bool | None = Field(default=None, validation_alias="PrintFaithfulCopy", serialization_alias="PrintFaithfulCopy", description="Whether to allow printing the document to a representation from which a faithful digital copy of the PDF content could be generated.")
class PostConvertPdfToProtectRequest(StrictModel):
    """Convert and protect a PDF document by applying encryption, setting access passwords, and configuring user permissions. Supports multiple encryption algorithms and granular control over document operations like printing, editing, and content extraction."""
    body: PostConvertPdfToProtectRequestBody | None = None

# Operation: convert_pdf_to_rasterized_image
class PostConvertPdfToRasterizeRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the appropriate image extension, and adds numeric indexing (e.g., filename_0.png, filename_1.png) when multiple output files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    resolution: int | None = Field(default=None, validation_alias="Resolution", serialization_alias="Resolution", description="Resolution for rasterized output measured in dots per inch (DPI). Higher values produce sharper images but increase file size. Valid range is 10 to 800 DPI.", ge=10, le=800)
class PostConvertPdfToRasterizeRequest(StrictModel):
    """Convert PDF documents to rasterized image files at a specified resolution. Supports password-protected PDFs and allows customization of output image quality through DPI settings."""
    body: PostConvertPdfToRasterizeRequestBody | None = None

# Operation: redact_pdf
class PostConvertPdfToRedactRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to redact. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The API sanitizes the filename, appends the correct extension, and adds indexing for multiple output files (e.g., report_0.pdf, report_1.pdf).")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password to open a protected PDF document.")
    preset: Literal["auto", "gdpr", "hipaa", "ferpa", "foia", "glba", "ccpa", "manual"] | None = Field(default=None, validation_alias="Preset", serialization_alias="Preset", description="Compliance preset that determines which categories of sensitive data the AI detects and redacts. Use 'manual' to rely exclusively on custom redaction parameters (PII, PHI, Financial).")
    context_size: Literal["balanced", "page"] | None = Field(default=None, validation_alias="ContextSize", serialization_alias="ContextSize", description="Defines how the AI processes document context. 'Page' processes each page independently for structured data and high-volume detections. 'Balanced' maintains cross-page context for large documents while optimizing performance.")
    redaction_color: str | None = Field(default=None, validation_alias="RedactionColor", serialization_alias="RedactionColor", description="Color used to mask redacted text. Accepts hexadecimal (e.g., #FFFFFF), RGB with optional alpha channel (e.g., 255,255,255), or named colors (e.g., white, red, blue).")
    redaction_thickness: float | None = Field(default=None, validation_alias="RedactionThickness", serialization_alias="RedactionThickness", description="Height of the redaction stroke relative to the original line height. A value of 1 matches the original height; values below 1 reduce height, values above 1 increase it.", ge=0.5, le=2)
    pii: bool | None = Field(default=None, validation_alias="PII", serialization_alias="PII", description="Enable detection and redaction of Personally Identifiable Information (PII) such as names, email addresses, phone numbers, birthdates, and home addresses.")
    phi: bool | None = Field(default=None, validation_alias="PHI", serialization_alias="PHI", description="Enable detection and redaction of Patient Health Information (PHI) such as patient names, medical records, insurance details, and prescription data.")
    financial: bool | None = Field(default=None, validation_alias="Financial", serialization_alias="Financial", description="Enable detection and redaction of financial data including credit card numbers, bank account numbers, and financial transaction details.")
    minimum_confidence: float | None = Field(default=None, validation_alias="MinimumConfidence", serialization_alias="MinimumConfidence", description="Minimum confidence threshold for AI-based detection of sensitive data. Higher values reduce false positives but may miss subtle matches.", ge=0.01, le=0.99)
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Pages to redact, specified as a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5).")
    redaction_data: list[dict] | None = Field(default=None, validation_alias="RedactionData", serialization_alias="RedactionData", description="A JSON array defining specific values for redaction. Supports three methods:\r\n\r\n- **Text** – Exact text to be redacted.\r\n- **Regex** – *Escaped* regular expression patterns for flexible text matching.\r\n- **Detect** – AI-based detection using a description of what to find.\r\n\r\nIf `RedactionData` is passed, it forces: `Preset` is set to `manual`, and all built-in detection options (such as `PII`, `PHI`, `Financial`, `Legal`, `Confidential`) are disabled. In this mode, only the values defined in RedactionData are applied.\r\n\r\n#### Example JSON\r\n\r\n```json\r\n[\r\n  {\r\n    \"Text\": \"john@domain.com\"\r\n  },\r\n  {\r\n    \"Detect\": \"Bank account number\"\r\n  },\r\n  {\r\n    \"Regex\": \"\\\\b100\\\\s*(€|\\\\$)\\\\b\"\r\n  }\r\n]\r\n```")
class PostConvertPdfToRedactRequest(StrictModel):
    """Convert and redact sensitive data from a PDF document based on compliance presets or custom detection rules. Supports automatic AI-based detection of PII, financial, and health information, or manual redaction configuration."""
    body: PostConvertPdfToRedactRequestBody | None = None

# Operation: resize_pdf_pages
class PostConvertPdfToResizeRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to resize. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pdf, output_1.pdf) for multiple files to ensure unique identification.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open a protected or encrypted PDF file.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using page numbers and keywords. Supports comma-separated values, ranges with hyphens, and keywords like 'even', 'odd', and 'last' to select specific pages.")
    measurement_unit: Literal["pt", "in", "mm", "cm"] | None = Field(default=None, validation_alias="MeasurementUnit", serialization_alias="MeasurementUnit", description="The unit of measurement for page dimensions (height and width).")
class PostConvertPdfToResizeRequest(StrictModel):
    """Resize PDF pages to specified dimensions. Supports selective page conversion with customizable measurement units and password-protected PDF handling."""
    body: PostConvertPdfToResizeRequestBody | None = None

# Operation: rotate_pdf_pages
class PostConvertPdfToRotateRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to rotate. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., document_0.pdf, document_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open a protected or encrypted PDF document.")
    auto_rotate: bool | None = Field(default=None, validation_alias="AutoRotate", serialization_alias="AutoRotate", description="Enable automatic detection and correction of page orientation to the optimal reading angle.")
    angle: Literal["0", "90", "180", "270"] | None = Field(default=None, validation_alias="Angle", serialization_alias="Angle", description="Rotation angle in degrees to apply to selected pages.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specify which pages to rotate using page numbers, ranges, or keywords. Use comma-separated values for multiple selections and hyphens for ranges (e.g., 1,2,5-last or even, odd).")
class PostConvertPdfToRotateRequest(StrictModel):
    """Rotate pages in a PDF document by a specified angle or automatically detect optimal orientation. Supports selective page ranges and password-protected PDFs."""
    body: PostConvertPdfToRotateRequestBody | None = None

# Operation: convert_pdf_to_rtf
class PostConvertPdfToRtfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output RTF file. The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., document_0.rtf, document_1.rtf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to pages 1-2000.")
    wysiwyg: bool | None = Field(default=None, validation_alias="Wysiwyg", serialization_alias="Wysiwyg", description="When enabled, preserves exact formatting from the source PDF by using text boxes in the output RTF.")
    ocr_mode: Literal["auto", "force", "never"] | None = Field(default=None, validation_alias="OcrMode", serialization_alias="OcrMode", description="Controls OCR (Optical Character Recognition) behavior during conversion. Auto applies OCR only when needed, Force applies to all pages, and Never disables OCR entirely.")
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(default=None, validation_alias="OcrLanguage", serialization_alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use auto-detection by default, or manually select a language if auto-detection fails.")
class PostConvertPdfToRtfRequest(StrictModel):
    """Converts PDF documents to RTF (Rich Text Format) with support for password-protected files, selective page ranges, and OCR capabilities. Preserves formatting and enables text recognition for scanned documents."""
    body: PostConvertPdfToRtfRequestBody | None = None

# Operation: split_pdf
class PostConvertPdfToSplitRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to be split. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The API sanitizes the filename, appends the appropriate extension, and adds numeric indices (e.g., `report_0.pdf`, `report_1.pdf`) when multiple files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    split_by_pattern: str | None = Field(default=None, validation_alias="SplitByPattern", serialization_alias="SplitByPattern", description="A comma-separated sequence of positive integers that defines the page count for each split segment. The pattern repeats cyclically until all pages are consumed. For example, a pattern of `3,2` creates segments of 3 pages, then 2 pages, repeating as needed.")
    split_by_text_pattern: str | None = Field(default=None, validation_alias="SplitByTextPattern", serialization_alias="SplitByTextPattern", description="A regular expression pattern that triggers a new document split whenever matching text is found on a page. For example, `Chapter\\s+\\d+` splits at pages containing \"Chapter 1\", \"Chapter 2\", etc. Pages before the first match are grouped together, and any remaining pages after the last match form a final segment.")
    split_by_bookmark: bool | None = Field(default=None, validation_alias="SplitByBookmark", serialization_alias="SplitByBookmark", description="When enabled, automatically splits the PDF at each bookmarked page. For nested bookmarks, splitting occurs at the deepest level, and output filenames reflect the full bookmark hierarchy (e.g., `ParentBookmark-ChildBookmark.pdf`). PDFs without bookmarks are returned unchanged.")
    merge_output: bool | None = Field(default=None, validation_alias="MergeOutput", serialization_alias="MergeOutput", description="When enabled, merges all split segments back into a single PDF file instead of returning separate files for each segment.")
class PostConvertPdfToSplitRequest(StrictModel):
    """Splits a PDF document into multiple files based on page ranges, text patterns, or bookmarks. Optionally merges the split segments back into a single file."""
    body: PostConvertPdfToSplitRequestBody | None = None

# Operation: convert_pdf_to_svg
class PostConvertPdfToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output SVG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.svg, output_1.svg) for multiple files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert. Use ranges (e.g., 1-10) or comma-separated individual pages (e.g., 1,2,5).")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="When enabled, maintains the aspect ratio of the output image during scaling operations.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotates the output image by the specified angle in degrees.", ge=-360, le=360)
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertPdfToSvgRequest(StrictModel):
    """Converts PDF documents to SVG (Scalable Vector Graphics) format, with support for page range selection, rotation, and password-protected documents. Useful for extracting vector-based graphics from PDFs while maintaining scalability."""
    body: PostConvertPdfToSvgRequestBody | None = None

# Operation: convert_pdf_to_text_with_watermark
class PostConvertPdfToTextWatermarkRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.txt, report_1.txt) for multiple outputs.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    text: str | None = Field(default=None, validation_alias="Text", serialization_alias="Text", description="Text content for the watermark. Supports dynamic variables like %PAGE%, %FILENAME%, %DATE%, %TIME%, %DATETIME%, document metadata (%AUTHOR%, %TITLE%, %SUBJECT%, %KEYWORDS%), and %N% for line breaks.")
    style: Literal["stamp", "watermark"] | None = Field(default=None, validation_alias="Style", serialization_alias="Style", description="Watermark display style. Stamp places the watermark over page content; watermark places it beneath.")
    font_size: int | None = Field(default=None, validation_alias="FontSize", serialization_alias="FontSize", description="Font size for the watermark text in points.", ge=1, le=200)
    text_rendering_mode: Literal["filltext", "stroketext", "fillstroke", "invisible"] | None = Field(default=None, validation_alias="TextRenderingMode", serialization_alias="TextRenderingMode", description="Text rendering mode controlling how the watermark text is drawn (filled, stroked, both, or invisible).")
    font_color: str | None = Field(default=None, validation_alias="FontColor", serialization_alias="FontColor", description="Color of the watermark text. Specify as a color value (e.g., hex code or color name).")
    stroke_color: str | None = Field(default=None, validation_alias="StrokeColor", serialization_alias="StrokeColor", description="Color of the text stroke/outline.")
    stroke_width: int | None = Field(default=None, validation_alias="StrokeWidth", serialization_alias="StrokeWidth", description="Width of the text stroke in points.", ge=0, le=200)
    font_name: Literal["arial", "bahnschrift", "calibri", "cambria", "consolas", "constantia", "courierNew", "georgia", "tahoma", "timesNewRoman", "verdana"] | None = Field(default=None, validation_alias="FontName", serialization_alias="FontName", description="Font family for the watermark text. Contact support for additional font availability.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotation angle of the watermark in degrees (0-360).", ge=0, le=360)
    opacity: int | None = Field(default=None, validation_alias="Opacity", serialization_alias="Opacity", description="Transparency level of the watermark as a percentage (0=fully transparent, 100=fully opaque).", ge=0, le=100)
    go_to_link: str | None = Field(default=None, validation_alias="GoToLink", serialization_alias="GoToLink", description="Web URL to navigate to when the watermark is clicked.")
    go_to_page: str | None = Field(default=None, validation_alias="GoToPage", serialization_alias="GoToPage", description="Page number to navigate to when the watermark is clicked.")
    page_box: Literal["mediabox", "trimbox", "bleedbox", "cropbox"] | None = Field(default=None, validation_alias="PageBox", serialization_alias="PageBox", description="PDF page box type used as the reference area for watermark positioning (mediabox is the full page, others define trimmed/bleed/crop areas).")
    horizontal_alignment: Literal["left", "center", "right"] | None = Field(default=None, validation_alias="HorizontalAlignment", serialization_alias="HorizontalAlignment", description="Horizontal alignment of the watermark within its container.")
    vertical_alignment: Literal["top", "center", "bottom"] | None = Field(default=None, validation_alias="VerticalAlignment", serialization_alias="VerticalAlignment", description="Vertical alignment of the watermark within its container.")
    measurement_unit: Literal["pt", "in", "mm", "cm"] | None = Field(default=None, validation_alias="MeasurementUnit", serialization_alias="MeasurementUnit", description="Unit of measurement for width, height, and position parameters.")
    width: float | None = Field(default=None, validation_alias="Width", serialization_alias="Width", description="Width of the watermark text box in the specified measurement unit. A value of 0 means the width is automatically determined.", ge=0, le=10000)
    height: float | None = Field(default=None, validation_alias="Height", serialization_alias="Height", description="Height of the watermark text box in the specified measurement unit. A value of 0 means the height is automatically determined.", ge=0, le=10000)
    line_spacing: int | None = Field(default=None, validation_alias="LineSpacing", serialization_alias="LineSpacing", description="Line spacing adjustment for multi-line watermark text in points.", ge=-30, le=30)
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Pages to apply the watermark to. Specify as a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5).")
    font_embed: bool | None = Field(default=None, validation_alias="FontEmbed", serialization_alias="FontEmbed", description="Whether to embed fonts in the output document for consistent rendering across systems.")
    font_subset: bool | None = Field(default=None, validation_alias="FontSubset", serialization_alias="FontSubset", description="Whether to subset fonts (include only used characters) to reduce file size.")
    offset_x: dict | None = Field(default=None, validation_alias="OffsetX", serialization_alias="OffsetX", description="Specifies the watermark offset along the X-axis. Positive values move the watermark to the right, while negative values move it to the left, using the selected `MeasurementUnit`.", ge=-10000, le=10000)
    offset_y: float | None = Field(default=None, validation_alias="OffsetY", serialization_alias="OffsetY", description="Specifies the watermark offset along the Y-axis. Positive values move the watermark downward, while negative values move it upward, using the selected `MeasurementUnit`.", ge=-10000, le=10000)
class PostConvertPdfToTextWatermarkRequest(StrictModel):
    """Converts a PDF document to text format while applying customizable watermark or stamp overlays. Supports dynamic watermark text with variables, advanced styling options, and precise positioning control."""
    body: PostConvertPdfToTextWatermarkRequestBody | None = None

# Operation: convert_pdf_to_tiff
class PostConvertPdfToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open a password-protected PDF document.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5).")
    rotate: Literal["default", "none", "rotate90", "rotate180", "rotate270"] | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Applies rotation to PDF pages before conversion.")
    crop_to: Literal["BoundingBox", "TrimBox", "MediaBox", "ArtBox", "BleedBox"] | None = Field(default=None, validation_alias="CropTo", serialization_alias="CropTo", description="Defines which PDF box area to use when cropping pages during conversion.")
    background_color: str | None = Field(default=None, validation_alias="BackgroundColor", serialization_alias="BackgroundColor", description="Sets the background color for transparent areas in the PDF. Accepts color names (white, black), RGB format (255,0,0), HEX format (#FF0000), or 'transparent' to preserve transparency.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="When enabled, creates a single multi-page TIFF file containing all converted pages. When disabled, generates separate TIFF files for each page.")
    color_mode: Literal["default", "cmyk", "grayscale", "bitonal"] | None = Field(default=None, validation_alias="ColorMode", serialization_alias="ColorMode", description="Specifies the color mode for the output TIFF image.")
class PostConvertPdfToTiffRequest(StrictModel):
    """Converts PDF documents to TIFF image format with support for page selection, rotation, cropping, and color mode customization. Handles password-protected PDFs and can generate single or multi-page TIFF files."""
    body: PostConvertPdfToTiffRequestBody | None = None

# Operation: convert_pdf_to_tiff_fax
class PostConvertPdfToTiffFaxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    tiff_type: Literal["monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(default=None, validation_alias="TiffType", serialization_alias="TiffType", description="Compression type for the TIFF FAX output. Determines the encoding method used in the resulting file.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="When enabled, combines all converted pages into a single multi-page TIFF file. When disabled, generates separate TIFF files for each page.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert from the PDF. Use hyphen for ranges (e.g., 1-10) or comma-separated values for individual pages (e.g., 1,2,5).")
    crop_to: Literal["BoundingBox", "TrimBox", "MediaBox", "ArtBox", "BleedBox"] | None = Field(default=None, validation_alias="CropTo", serialization_alias="CropTo", description="Defines which page boundary box to use for cropping during conversion. Different box types capture different content areas of the PDF page.")
class PostConvertPdfToTiffFaxRequest(StrictModel):
    """Converts PDF documents to TIFF FAX format with support for multi-page output, custom compression types, and selective page range processing. Ideal for fax transmission and archival purposes."""
    body: PostConvertPdfToTiffFaxRequestBody | None = None

# Operation: convert_pdf_to_text
class PostConvertPdfToTxtRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output text file(s). The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.txt, output_1.txt) when multiple files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specify which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5).")
    ocr_mode: Literal["auto", "force", "never"] | None = Field(default=None, validation_alias="OcrMode", serialization_alias="OcrMode", description="Controls OCR application during conversion. Auto applies OCR only when needed, Force applies OCR to all pages, and Never disables OCR entirely.")
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(default=None, validation_alias="OcrLanguage", serialization_alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use auto-detection by default, or manually select a language if auto-detection fails.")
    include_formatting: bool | None = Field(default=None, validation_alias="IncludeFormatting", serialization_alias="IncludeFormatting", description="Preserve text formatting (fonts, spacing, alignment) during extraction. Only effective when headers/footers and footnotes removal are disabled.")
    split_pages: bool | None = Field(default=None, validation_alias="SplitPages", serialization_alias="SplitPages", description="Generate a separate output file for each page instead of combining all pages into a single file.")
    remove_headers_footers: bool | None = Field(default=None, validation_alias="RemoveHeadersFooters", serialization_alias="RemoveHeadersFooters", description="Exclude headers and footers from the extracted text output.")
    remove_footnotes: bool | None = Field(default=None, validation_alias="RemoveFootnotes", serialization_alias="RemoveFootnotes", description="Exclude footnotes from the extracted text output.")
    remove_tables: bool | None = Field(default=None, validation_alias="RemoveTables", serialization_alias="RemoveTables", description="Exclude tables from the extracted text output.")
class PostConvertPdfToTxtRequest(StrictModel):
    """Convert PDF documents to plain text format with optional OCR, formatting preservation, and content filtering. Supports password-protected files, page range selection, and multi-language text recognition."""
    body: PostConvertPdfToTxtRequestBody | None = None

# Operation: unprotect_pdf
class PostConvertPdfToUnprotectRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to unprotect. Provide either a publicly accessible URL or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., `document_0.pdf`, `document_1.pdf`) if multiple files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="The password protecting the PDF. Provide the user password to remove user-level protection, or leave empty to remove owner-level protection.")
class PostConvertPdfToUnprotectRequest(StrictModel):
    """Remove password protection from a PDF file. Specify a user password to remove user-level protection, or leave the password empty to remove owner-level protection."""
    body: PostConvertPdfToUnprotectRequestBody | None = None

# Operation: convert_pdf_to_webp
class PostConvertPdfToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The system sanitizes the filename, appends the correct extension automatically, and adds indexing (e.g., filename_0.webp, filename_1.webp) for multiple outputs.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specify which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5).")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to prevent distortion.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotate the output image by the specified angle in degrees.", ge=-360, le=360)
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertPdfToWebpRequest(StrictModel):
    """Convert PDF documents to WebP image format with support for page selection, rotation, and scaling options. Handles password-protected PDFs and generates uniquely named output files."""
    body: PostConvertPdfToWebpRequestBody | None = None

# Operation: convert_pdf_to_xlsx
class PostConvertPdfToXlsxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated Excel output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.xlsx, report_1.xlsx) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PDF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to extract from the PDF. Use ranges (e.g., 1-10) or comma-separated page numbers (e.g., 1,2,5).")
    ocr_mode: Literal["auto", "force", "never"] | None = Field(default=None, validation_alias="OcrMode", serialization_alias="OcrMode", description="Controls when Optical Character Recognition is applied. Auto applies OCR only when needed, Force applies it to all pages, and Never disables OCR entirely.")
    ocr_language: Literal["auto", "ar", "ca", "zh", "da", "nl", "en", "fi", "fr", "de", "el", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "ua", "th"] | None = Field(default=None, validation_alias="OcrLanguage", serialization_alias="OcrLanguage", description="Specifies the language for OCR text recognition. Use auto-detection by default, or manually select a language if auto-detection fails.")
    include_formatting: bool | None = Field(default=None, validation_alias="IncludeFormatting", serialization_alias="IncludeFormatting", description="When enabled, includes non-table content such as images and paragraphs in the Excel output alongside extracted tables.")
    single_sheet: bool | None = Field(default=None, validation_alias="SingleSheet", serialization_alias="SingleSheet", description="When enabled, combines all extracted tables into a single worksheet instead of creating separate sheets.")
    decimal_separator: Literal["auto", "period", "comma"] | None = Field(default=None, validation_alias="DecimalSeparator", serialization_alias="DecimalSeparator", description="Specifies the character used as a decimal separator in numeric values. Auto-detection uses the formatting from the document, or you can force a specific separator.")
    thousands_separator: Literal["auto", "period", "comma", "space"] | None = Field(default=None, validation_alias="ThousandsSeparator", serialization_alias="ThousandsSeparator", description="Specifies the character used as a thousands separator in numeric values. Auto-detection uses the formatting from the document, or you can force a specific separator.")
class PostConvertPdfToXlsxRequest(StrictModel):
    """Converts PDF documents to Excel spreadsheet format, with support for OCR text recognition, table extraction, and numeric formatting customization."""
    body: PostConvertPdfToXlsxRequestBody | None = None

# Operation: validate_pdfa_conformance
class PostConvertPdfaToValidateRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PDF file to validate. Can be provided as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output validation report file. The system sanitizes the filename, appends the appropriate extension, and adds indexing for multiple output files to ensure unique and safe file naming.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the PDF if it is password-protected.")
    expected_conformance: Literal["auto", "pdfA1a", "pdfA1b", "pdfA2a", "pdfA2b", "pdfA2u", "pdfA3a", "pdfA3b", "pdfA3u", "pdfA4", "pdfA4e", "pdfA4f"] | None = Field(default=None, validation_alias="ExpectedConformance", serialization_alias="ExpectedConformance", description="The PDF/A conformance level to validate against. Use 'auto' to automatically detect the document's claimed conformance level, or specify a particular PDF/A version.")
class PostConvertPdfaToValidateRequest(StrictModel):
    """Validates a PDF file against PDF/A conformance standards. Analyzes the document to ensure it meets the specified PDF/A version requirements, with support for password-protected files and automatic conformance level detection."""
    body: PostConvertPdfaToValidateRequestBody | None = None

# Operation: convert_png_to_gif
class PostConvertPngToGifRequestBody(StrictModel):
    files: list[str] | None = Field(default=None, validation_alias="Files", serialization_alias="Files", description="PNG image files to convert to GIF format. Accepts file URLs or direct file content. When using query or multipart parameters, each file must be indexed (Files[0], Files[1], etc.).")
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output GIF file(s). The system automatically sanitizes the filename, appends the .gif extension, and adds numeric suffixes for multiple outputs (e.g., animation_0.gif, animation_1.gif) to ensure unique, safe filenames.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions.")
    animation_delay: int | None = Field(default=None, validation_alias="AnimationDelay", serialization_alias="AnimationDelay", description="Time interval between animation frames, specified in hundredths of a second. Controls the playback speed of the animated GIF.", ge=0, le=20000)
    animation_iterations: int | None = Field(default=None, validation_alias="AnimationIterations", serialization_alias="AnimationIterations", description="Number of times the animation loops. Set to 0 for infinite looping.", ge=0, le=1000)
class PostConvertPngToGifRequest(StrictModel):
    """Convert PNG image files to animated GIF format with customizable animation settings. Supports single or batch file conversion with optional scaling and frame delay control."""
    body: PostConvertPngToGifRequestBody | None = None

# Operation: convert_image_png_to_jpg
class PostConvertPngToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Can be provided as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) for multiple outputs.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size.")
    alpha_color: str | None = Field(default=None, validation_alias="AlphaColor", serialization_alias="AlphaColor", description="Replace transparent areas with a specific color. Accepts RGBA or CMYK hex strings, or standard color names.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image.")
class PostConvertPngToJpgRequest(StrictModel):
    """Convert a PNG image to JPG format with optional scaling, color space adjustment, and alpha channel handling. Supports both URL and file content input."""
    body: PostConvertPngToJpgRequestBody | None = None

# Operation: convert_image_to_pdf_png
class PostConvertPngToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pdf, output_1.pdf) for multiple files.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotation angle in degrees for the image. Leave empty to automatically detect and apply rotation from EXIF metadata in TIFF and JPEG images.", ge=-360, le=360)
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output PDF. Defines how colors are represented in the document.")
    color_profile: Literal["default", "isocoatedv2"] | None = Field(default=None, validation_alias="ColorProfile", serialization_alias="ColorProfile", description="Color profile for the output PDF. Some profiles override the ColorSpace setting.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Enable PDF/A-1b compliance for long-term archival and preservation of the document.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in millimeters (mm).", ge=0, le=500)
    margin_vertical: int | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in millimeters (mm).", ge=0, le=500)
class PostConvertPngToPdfRequest(StrictModel):
    """Convert PNG images to PDF format with optional image processing capabilities including rotation, color space adjustment, and PDF/A compliance."""
    body: PostConvertPngToPdfRequestBody | None = None

# Operation: convert_image_png_to_pnm
class PostConvertPngToPnmRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct .pnm extension, and adds numeric indexing (e.g., image_0.pnm, image_1.pnm) when multiple files are generated.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output size, leaving smaller images unchanged.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertPngToPnmRequest(StrictModel):
    """Convert a PNG image to PNM (Portable Anymap) format with optional scaling and proportional constraint controls. Supports both URL-based and direct file content input."""
    body: PostConvertPngToPnmRequestBody | None = None

# Operation: convert_image_to_svg
class PostConvertPngToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.svg, filename_1.svg) for multiple output files.")
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(default=None, validation_alias="Preset", serialization_alias="Preset", description="A vectorization preset that applies pre-configured tracing settings optimized for specific image types. When selected, presets override all other converter options except ColorMode, ensuring consistent and balanced SVG output.")
    color_mode: Literal["color", "bw"] | None = Field(default=None, validation_alias="ColorMode", serialization_alias="ColorMode", description="Determines whether the image is traced in black-and-white or full color mode.")
    layering: Literal["cutout", "stacked"] | None = Field(default=None, validation_alias="Layering", serialization_alias="Layering", description="Specifies how color regions are arranged in the output SVG: cutout layers isolate each color region separately, while stacked overlays layer regions on top of each other.")
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(default=None, validation_alias="CurveMode", serialization_alias="CurveMode", description="Defines the shape approximation method during tracing. Pixel mode follows exact pixel boundaries with minimal smoothing, Polygon creates straight-edged paths with sharp corners, and Spline generates smooth continuous curves for more natural shapes.")
class PostConvertPngToSvgRequest(StrictModel):
    """Converts a PNG image to scalable vector graphics (SVG) format using configurable tracing and vectorization settings. Supports preset configurations for different image types and offers fine-grained control over color handling, layering, and curve approximation."""
    body: PostConvertPngToSvgRequestBody | None = None

# Operation: convert_png_to_tiff
class PostConvertPngToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PNG image file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a multi-page TIFF file when converting multiple images or pages.")
class PostConvertPngToTiffRequest(StrictModel):
    """Convert PNG images to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""
    body: PostConvertPngToTiffRequestBody | None = None

# Operation: convert_image_png_to_webp
class PostConvertPngToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a file upload or a URL pointing to the PNG image.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output WebP file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image. Choose from standard color profiles or use the default setting.")
class PostConvertPngToWebpRequest(StrictModel):
    """Convert PNG images to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""
    body: PostConvertPngToWebpRequestBody | None = None

# Operation: translate_po_file
class PostConvertPoToTranslateRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PO file to be converted and translated. Accepts either a file URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The API sanitizes the filename, appends the appropriate extension, and adds indexing (e.g., output_0.po, output_1.po) for multiple files to ensure unique, safe naming.")
    overwrite_translations: bool | None = Field(default=None, validation_alias="OverwriteTranslations", serialization_alias="OverwriteTranslations", description="When enabled, re-translates strings that already have existing translations in the PO file. Useful for updating outdated or low-quality translations.")
    translation_context: str | None = Field(default=None, validation_alias="TranslationContext", serialization_alias="TranslationContext", description="Optional context to guide the translation engine. Provide a brief description of the product, audience, or domain to improve tone, terminology, and translation accuracy.")
    source_language: Literal["auto", "ar", "ca", "zh-cn", "zh-tw", "da", "nl", "en", "fi", "fr", "de", "el", "he", "hi", "id", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "uk", "vi", "th"] | None = Field(default=None, validation_alias="SourceLanguage", serialization_alias="SourceLanguage", description="The source language for translation. Use 'auto' to automatically detect the language from the PO file content, or specify a concrete language code.")
    target_language: Literal["auto", "ar", "ca", "zh-cn", "zh-tw", "da", "nl", "en", "fi", "fr", "de", "el", "he", "hi", "id", "ko", "it", "ja", "no", "pl", "pt", "ro", "ru", "sl", "es", "sv", "tr", "uk", "vi", "th"] | None = Field(default=None, validation_alias="TargetLanguage", serialization_alias="TargetLanguage", description="The target language for translation. Use 'auto' to preserve the language already defined in the PO file, or specify a concrete language code to override it.")
class PostConvertPoToTranslateRequest(StrictModel):
    """Converts a PO (Portable Object) localization file and translates its strings to a target language. Supports automatic language detection, selective translation of untranslated strings, and optional context guidance for improved translation accuracy."""
    body: PostConvertPoToTranslateRequestBody | None = None

# Operation: convert_presentation_to_jpg_template
class PostConvertPotxToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., presentation_0.jpg, presentation_1.jpg).")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to pages 1-2000.")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output. Defaults to false.")
class PostConvertPotxToJpgRequest(StrictModel):
    """Converts PowerPoint presentations (POTX format) to JPG images. Supports password-protected files, selective page ranges, and optional inclusion of hidden slides."""
    body: PostConvertPotxToJpgRequestBody | None = None

# Operation: convert_presentation_template_to_pdf
class PostConvertPotxToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to converting the first 2000 pages.")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the PDF output. Defaults to false.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="When enabled, preserves document metadata such as title, author, and keywords in the PDF output. Defaults to true.")
    convert_speaker_notes: Literal["Disabled", "SeparatePage", "PageComments"] | None = Field(default=None, validation_alias="ConvertSpeakerNotes", serialization_alias="ConvertSpeakerNotes", description="Determines how speaker notes are handled during conversion. Choose Disabled to exclude notes, SeparatePage to add notes on separate pages, or PageComments to embed notes as PDF comments.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="When enabled, creates a PDF/A-3a compliant document for long-term archival. Defaults to false.")
class PostConvertPotxToPdfRequest(StrictModel):
    """Converts PowerPoint presentations (POTX format) to PDF documents with support for selective page ranges, speaker notes handling, and PDF/A compliance options."""
    body: PostConvertPotxToPdfRequestBody | None = None

# Operation: convert_presentation_to_png_template
class PostConvertPotxToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which slides to convert using page numbers. Use ranges (e.g., 1-10) or comma-separated individual pages (e.g., 1,2,5).")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output images.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotates the output images by the specified angle in degrees.", ge=-360, le=360)
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertPotxToPngRequest(StrictModel):
    """Converts PowerPoint presentations (POTX format) to PNG images. Supports page range selection, hidden slide inclusion, image scaling, and rotation adjustments."""
    body: PostConvertPotxToPngRequestBody | None = None

# Operation: convert_potx_to_pptx
class PostConvertPotxToPptxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert, provided either as a URL or as binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension for the target format, and adds indexing (e.g., _0, _1) when multiple output files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="The password required to open the input file if it is password-protected.")
class PostConvertPotxToPptxRequest(StrictModel):
    """Converts a PowerPoint template file (POTX format) to a standard PowerPoint presentation (PPTX format). Supports both file uploads and URL-based file sources, with optional password protection for encrypted documents."""
    body: PostConvertPotxToPptxRequestBody | None = None

# Operation: convert_presentation_template_to_tiff
class PostConvertPotxToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a file URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range or comma-separated list format.")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="Whether to include hidden slides in the conversion output.")
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(default=None, validation_alias="TiffType", serialization_alias="TiffType", description="Specifies the TIFF compression type and color depth for the output image.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Whether to combine all converted pages into a single multi-page TIFF file or create separate files per page.")
    fill_order: Literal["0", "1"] | None = Field(default=None, validation_alias="FillOrder", serialization_alias="FillOrder", description="Defines the bit order within each byte in the TIFF output.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions.")
class PostConvertPotxToTiffRequest(StrictModel):
    """Converts PowerPoint presentations (POTX format) to TIFF image files with support for selective page ranges, hidden slides, and customizable image compression and scaling options."""
    body: PostConvertPotxToTiffRequestBody | None = None

# Operation: convert_presentation_to_webp_template
class PostConvertPotxToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a file URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5).")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="When enabled, applies scaling only if the input image dimensions exceed the output dimensions.")
class PostConvertPotxToWebpRequest(StrictModel):
    """Converts PowerPoint presentations (POTX format) to WebP images. Supports page range selection, hidden slide inclusion, and image scaling options for flexible output control."""
    body: PostConvertPotxToWebpRequestBody | None = None

# Operation: convert_presentation_to_jpg_slideshow
class PostConvertPpsxToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected presentation documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to pages 1-2000.")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output. Defaults to false.")
class PostConvertPpsxToJpgRequest(StrictModel):
    """Converts PPSX presentation files to JPG image format. Supports password-protected documents, selective page ranges, and optional inclusion of hidden slides."""
    body: PostConvertPpsxToJpgRequestBody | None = None

# Operation: convert_presentation_slideshow_to_pdf
class PostConvertPpsxToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to converting the first 2000 pages.")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the PDF output.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="When enabled, preserves document metadata such as title, author, and keywords in the PDF output.")
    convert_speaker_notes: Literal["Disabled", "SeparatePage", "PageComments"] | None = Field(default=None, validation_alias="ConvertSpeakerNotes", serialization_alias="ConvertSpeakerNotes", description="Determines how speaker notes are handled during conversion: Disabled (omitted), SeparatePage (on separate pages), or PageComments (as PDF comments).")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="When enabled, creates a PDF/A-3a compliant document for long-term archival purposes.")
class PostConvertPpsxToPdfRequest(StrictModel):
    """Converts PowerPoint presentations (PPSX format) to PDF documents with support for selective page ranges, speaker notes handling, and PDF/A compliance options."""
    body: PostConvertPpsxToPdfRequestBody | None = None

# Operation: convert_presentation_to_png_slideshow
class PostConvertPpsxToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open protected presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which slides to convert using a range or comma-separated list (e.g., 1-10 or 1,2,5).")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotates the output image by the specified angle in degrees.", ge=-360, le=360)
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertPpsxToPngRequest(StrictModel):
    """Converts PPSX presentation files to PNG image format, with support for selective slide conversion, hidden slide inclusion, and image transformation options."""
    body: PostConvertPpsxToPngRequestBody | None = None

# Operation: convert_presentation_ppsx_to_pptx
class PostConvertPpsxToPptxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert, provided either as a URL reference or as direct binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the converted output file. The system automatically sanitizes the filename, appends the correct PPTX extension, and adds numeric indexing (e.g., filename_0.pptx, filename_1.pptx) when multiple output files are generated from a single input.")
class PostConvertPpsxToPptxRequest(StrictModel):
    """Converts a PowerPoint Show file (PPSX) to PowerPoint Presentation format (PPTX). Accepts file input via URL or direct file content and generates a properly named output file."""
    body: PostConvertPpsxToPptxRequestBody | None = None

# Operation: convert_presentation_slideshow_to_tiff
class PostConvertPpsxToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique identification.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5).")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output.")
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(default=None, validation_alias="TiffType", serialization_alias="TiffType", description="Specifies the TIFF compression type and color depth. Options range from color formats with various compression algorithms to grayscale and monochrome variants.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="When enabled, combines all slides into a single multi-page TIFF file. When disabled, generates separate TIFF files for each slide.")
    fill_order: Literal["0", "1"] | None = Field(default=None, validation_alias="FillOrder", serialization_alias="FillOrder", description="Defines the bit order within each byte in the TIFF file. Use 0 for least-significant-bit-first or 1 for most-significant-bit-first.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="When enabled, applies scaling only if the input image dimensions exceed the target output dimensions.")
class PostConvertPpsxToTiffRequest(StrictModel):
    """Converts PPSX presentation files to TIFF image format with support for selective slide ranges, hidden slides, and customizable TIFF compression and color settings."""
    body: PostConvertPpsxToTiffRequestBody | None = None

# Operation: convert_presentation_to_webp_slideshow
class PostConvertPpsxToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs (e.g., presentation_0.webp, presentation_1.webp).")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which slides to convert using page numbers or ranges. Separate multiple selections with commas.")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="When enabled, maintains the aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="When enabled, scales the image only if the input is larger than the target output size.")
class PostConvertPpsxToWebpRequest(StrictModel):
    """Converts PowerPoint presentations (PPSX format) to WebP image format. Supports selective page conversion, hidden slide inclusion, and image scaling options."""
    body: PostConvertPpsxToWebpRequestBody | None = None

# Operation: convert_presentation_ppt_to_pptx
class PostConvertPptToPptxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert, provided either as a URL or as binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PPTX file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., presentation_0.pptx, presentation_1.pptx) if multiple files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input presentation if it is password-protected.")
class PostConvertPptToPptxRequest(StrictModel):
    """Converts a PowerPoint presentation from legacy PPT format to modern PPTX format. Supports password-protected documents and accepts file input via URL or direct file content."""
    body: PostConvertPptToPptxRequestBody | None = None

# Operation: convert_presentation_to_images
class PostConvertPptxToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PowerPoint file to convert. Accepts either a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indices for multiple output files to ensure unique identification.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PowerPoint documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specify which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to the first 2000 slides.")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the conversion output. Defaults to false.")
class PostConvertPptxToJpgRequest(StrictModel):
    """Convert PowerPoint presentations to individual JPG image files. Supports password-protected documents, selective page ranges, and optional inclusion of hidden slides."""
    body: PostConvertPptxToJpgRequestBody | None = None

# Operation: convert_presentation_to_pdf
class PostConvertPptxToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to converting the first 2000 pages.")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="When enabled, includes hidden slides in the PDF output. Defaults to false.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="When enabled, converts document metadata (title, author, keywords) to PDF metadata properties. Defaults to true.")
    convert_speaker_notes: Literal["Disabled", "SeparatePage", "PageComments"] | None = Field(default=None, validation_alias="ConvertSpeakerNotes", serialization_alias="ConvertSpeakerNotes", description="Determines how speaker notes are handled during conversion. Choose Disabled to exclude notes, SeparatePage to append notes on separate pages, or PageComments to embed notes as PDF comments.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="When enabled, creates a PDF/A-3a compliant document for long-term archival. Defaults to false.")
class PostConvertPptxToPdfRequest(StrictModel):
    """Converts PowerPoint presentations (PPTX) to PDF format with support for selective page ranges, speaker notes handling, and PDF/A compliance. Allows customization of metadata conversion, hidden slide inclusion, and password-protected document access."""
    body: PostConvertPptxToPdfRequestBody | None = None

# Operation: convert_presentation_to_images_png
class PostConvertPptxToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PowerPoint file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system sanitizes the filename, appends the correct extension automatically, and adds indexing (e.g., report_0.png, report_1.png) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open protected or encrypted presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specify which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5).")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="Include hidden slides in the conversion output.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output images.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotate the output images by the specified angle in degrees.", ge=-360, le=360)
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Make pixels matching the specified color transparent by adding an alpha channel. Accepts RGBA or CMYK hex strings, color names, or RGB format (e.g., 255,255,255 or 255,255,255,150 with alpha channel).")
class PostConvertPptxToPngRequest(StrictModel):
    """Convert PowerPoint presentations to PNG images with support for selective slide ranges, hidden slides, image transformations, and transparency settings."""
    body: PostConvertPptxToPngRequestBody | None = None

# Operation: convert_presentation
class PostConvertPptxToPptxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The presentation file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output presentation file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., presentation_0.pptx, presentation_1.pptx) if multiple files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input presentation if it is password-protected.")
class PostConvertPptxToPptxRequest(StrictModel):
    """Converts a PowerPoint presentation to PowerPoint format, with support for password-protected documents. Useful for standardizing presentation formats or re-encoding existing presentations."""
    body: PostConvertPptxToPptxRequestBody | None = None

# Operation: encrypt_presentation
class PostConvertPptxToProtectRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PowerPoint file to encrypt. Accepts either a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output encrypted presentation file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing if multiple files are generated.")
    encrypt_password: str | None = Field(default=None, validation_alias="EncryptPassword", serialization_alias="EncryptPassword", description="Password to encrypt the presentation. Only users with this password can open and view the file.")
class PostConvertPptxToProtectRequest(StrictModel):
    """Convert and encrypt a PowerPoint presentation with password protection. The output file is automatically named and formatted for secure distribution."""
    body: PostConvertPptxToProtectRequestBody | None = None

# Operation: convert_presentation_to_tiff
class PostConvertPptxToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PowerPoint file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected presentations.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5).")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="Whether to include hidden slides in the conversion.")
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(default=None, validation_alias="TiffType", serialization_alias="TiffType", description="The TIFF compression and color format to use for output images.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Whether to combine all slides into a single multi-page TIFF file or create separate TIFF files for each slide.")
    fill_order: Literal["0", "1"] | None = Field(default=None, validation_alias="FillOrder", serialization_alias="FillOrder", description="The logical order of bits within each byte in the TIFF output.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Whether to apply scaling only when the input image is larger than the target output dimensions.")
class PostConvertPptxToTiffRequest(StrictModel):
    """Converts PowerPoint presentations (PPTX) to TIFF image format with support for multi-page output, custom compression, and selective slide inclusion. Useful for creating archival-quality image files or preparing presentations for systems that require TIFF format."""
    body: PostConvertPptxToTiffRequestBody | None = None

# Operation: convert_presentation_to_webp
class PostConvertPptxToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PowerPoint file to convert. Accepts either a file URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output WebP file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., presentation_0.webp, presentation_1.webp) when multiple slides are converted.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected PowerPoint documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specify which slides to convert using a range (e.g., 1-10) or comma-separated list (e.g., 1,2,5). Defaults to converting the first 2000 slides.")
    convert_hidden_slides: bool | None = Field(default=None, validation_alias="ConvertHiddenSlides", serialization_alias="ConvertHiddenSlides", description="Include hidden slides in the conversion output. By default, hidden slides are excluded.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image dimensions. Enabled by default to prevent image distortion.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the output dimensions. Prevents upscaling of smaller images.")
class PostConvertPptxToWebpRequest(StrictModel):
    """Convert PowerPoint presentations to WebP image format with support for selective slide conversion, scaling options, and hidden slide inclusion. Each slide is converted to a separate WebP image file."""
    body: PostConvertPptxToWebpRequestBody | None = None

# Operation: convert_prn_to_jpg
class PostConvertPrnToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PRN file to convert, provided as either a publicly accessible URL or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The desired name for the output JPG file. The API automatically sanitizes the filename, appends the .jpg extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) if multiple files are generated from a single input.")
class PostConvertPrnToJpgRequest(StrictModel):
    """Converts a PRN (printer) file to JPG image format. Accepts file input as either a URL or raw file content and generates a JPG output file with sanitized naming."""
    body: PostConvertPrnToJpgRequestBody | None = None

# Operation: convert_prn_to_pdf
class PostConvertPrnToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PRN file to convert. Accepts either a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric suffixes (e.g., report_0.pdf, report_1.pdf) when generating multiple files from a single input.")
    pdf_version: Literal["1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "2.0"] | None = Field(default=None, validation_alias="PdfVersion", serialization_alias="PdfVersion", description="PDF specification version to use for the output document.")
    pdf_resolution: int | None = Field(default=None, validation_alias="PdfResolution", serialization_alias="PdfResolution", description="Output resolution in dots per inch (DPI). Higher values produce better quality but larger file sizes.", ge=10, le=2400)
    pdf_title: str | None = Field(default=None, validation_alias="PdfTitle", serialization_alias="PdfTitle", description="Custom title for the PDF document metadata. Use a single quote and space (' ') to omit the title.")
    pdf_subject: str | None = Field(default=None, validation_alias="PdfSubject", serialization_alias="PdfSubject", description="Custom subject for the PDF document metadata. Use a single quote and space (' ') to omit the subject.")
    pdf_author: str | None = Field(default=None, validation_alias="PdfAuthor", serialization_alias="PdfAuthor", description="Custom author name for the PDF document metadata. Use a single quote and space (' ') to omit the author.")
    pdf_keywords: str | None = Field(default=None, validation_alias="PdfKeywords", serialization_alias="PdfKeywords", description="Custom keywords for the PDF document metadata, typically used for searchability. Use a single quote and space (' ') to omit keywords.")
    open_page: int | None = Field(default=None, validation_alias="OpenPage", serialization_alias="OpenPage", description="Page number where the PDF should open when first displayed in a viewer.", ge=1, le=3000)
    open_zoom: Literal["Default", "ActualSize", "FitPage", "FitWidth", "FitHeight", "FitVisible", "25", "50", "75", "100", "125", "150", "200", "400", "800", "1600", "2400", "3200", "6400"] | None = Field(default=None, validation_alias="OpenZoom", serialization_alias="OpenZoom", description="Default zoom level applied when opening the PDF in a viewer. Select from preset percentages or fit-to-page options.")
    color_space: Literal["Default", "RGB", "CMYK", "Gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space model for the PDF output. RGB is standard for screen viewing, CMYK for print production, and Gray for monochrome documents.")
class PostConvertPrnToPdfRequest(StrictModel):
    """Converts PRN (printer) files to PDF format with customizable metadata, resolution, and viewing preferences. Supports PDF version selection, color space configuration, and document properties customization."""
    body: PostConvertPrnToPdfRequestBody | None = None

# Operation: convert_prn_to_png
class PostConvertPrnToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PRN file to convert, provided as either a publicly accessible URL or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the .png extension, and adds numeric indexing (e.g., output_0.png, output_1.png) if multiple files are generated from a single input.")
class PostConvertPrnToPngRequest(StrictModel):
    """Converts a PRN (printer) file to PNG image format. Accepts file input as either a URL or raw file content and generates a PNG output file with automatic naming."""
    body: PostConvertPrnToPngRequestBody | None = None

# Operation: convert_prn_to_tiff
class PostConvertPrnToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PRN file to convert, provided either as a URL reference or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output TIFF file. The system automatically sanitizes the filename, appends the correct .tiff extension, and adds numeric indexing (e.g., output_0.tiff, output_1.tiff) when multiple files are generated from a single input.")
class PostConvertPrnToTiffRequest(StrictModel):
    """Converts a PRN (printer) file to TIFF image format. Accepts file input as a URL or binary content and generates a TIFF output file with automatic naming and extension handling."""
    body: PostConvertPrnToTiffRequestBody | None = None

# Operation: convert_postscript_to_jpg
class PostConvertPsToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PostScript file to convert. Can be provided as a URL or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output JPG file. The system automatically sanitizes the filename, appends the correct .jpg extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) when multiple files are generated from a single input.")
class PostConvertPsToJpgRequest(StrictModel):
    """Converts PostScript (PS) files to JPG image format. Accepts file input as a URL or binary content and generates a uniquely named output file."""
    body: PostConvertPsToJpgRequestBody | None = None

# Operation: convert_postscript_to_pdf
class PostConvertPsToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PostScript file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple output files.")
    pdf_version: Literal["1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "2.0"] | None = Field(default=None, validation_alias="PdfVersion", serialization_alias="PdfVersion", description="PDF specification version to use for the output document.")
    pdf_resolution: int | None = Field(default=None, validation_alias="PdfResolution", serialization_alias="PdfResolution", description="Output resolution in dots per inch (DPI). Higher values produce better quality but larger file sizes.", ge=10, le=2400)
    pdf_title: str | None = Field(default=None, validation_alias="PdfTitle", serialization_alias="PdfTitle", description="Custom title for the PDF document metadata. Use a single quote and space (' ') to omit the title.")
    pdf_subject: str | None = Field(default=None, validation_alias="PdfSubject", serialization_alias="PdfSubject", description="Custom subject for the PDF document metadata. Use a single quote and space (' ') to omit the subject.")
    pdf_author: str | None = Field(default=None, validation_alias="PdfAuthor", serialization_alias="PdfAuthor", description="Custom author name for the PDF document metadata. Use a single quote and space (' ') to omit the author.")
    pdf_keywords: str | None = Field(default=None, validation_alias="PdfKeywords", serialization_alias="PdfKeywords", description="Custom keywords for the PDF document metadata, typically used for searchability. Use a single quote and space (' ') to omit keywords.")
    open_page: int | None = Field(default=None, validation_alias="OpenPage", serialization_alias="OpenPage", description="Page number where the PDF should open when first viewed.", ge=1, le=3000)
    open_zoom: Literal["Default", "ActualSize", "FitPage", "FitWidth", "FitHeight", "FitVisible", "25", "50", "75", "100", "125", "150", "200", "400", "800", "1600", "2400", "3200", "6400"] | None = Field(default=None, validation_alias="OpenZoom", serialization_alias="OpenZoom", description="Default zoom level when opening the PDF. Choose from preset percentages or fit-to-page options.")
    color_space: Literal["Default", "RGB", "CMYK", "Gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the PDF output. RGB is suitable for screen viewing, CMYK for professional printing, and Gray for monochrome documents.")
class PostConvertPsToPdfRequest(StrictModel):
    """Converts PostScript files to PDF format with customizable metadata, resolution, and viewer settings. Supports URL or file content input with options to control PDF version, color space, and initial document appearance."""
    body: PostConvertPsToPdfRequestBody | None = None

# Operation: convert_postscript_to_png
class PostConvertPsToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PostScript file to convert. Can be provided as a URL reference or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output PNG file. The system automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., output_0.png, output_1.png) when multiple files are generated from a single input.")
class PostConvertPsToPngRequest(StrictModel):
    """Converts a PostScript file to PNG image format. Accepts file input as a URL or binary content and generates a PNG output file with optional custom naming."""
    body: PostConvertPsToPngRequestBody | None = None

# Operation: convert_postscript_to_tiff
class PostConvertPsToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PostScript file to convert. Provide either a publicly accessible URL or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output TIFF file(s). The system automatically sanitizes the name, appends the .tiff extension, and adds numeric indexing (e.g., document_0.tiff, document_1.tiff) if multiple files are generated.")
class PostConvertPsToTiffRequest(StrictModel):
    """Converts PostScript (PS) files to TIFF image format. Accepts file input via URL or direct file content and generates output with sanitized, uniquely-named TIFF file(s)."""
    body: PostConvertPsToTiffRequestBody | None = None

# Operation: convert_psd_to_jpg
class PostConvertPsdToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PSD file to convert. Accepts either a file upload or a URL pointing to the source file.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output JPG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions.")
    alpha_color: str | None = Field(default=None, validation_alias="AlphaColor", serialization_alias="AlphaColor", description="Specify a color to replace transparent areas in the image. Accepts RGBA or CMYK hex strings, or standard color names.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image.")
class PostConvertPsdToJpgRequest(StrictModel):
    """Convert a PSD (Photoshop) file to JPG format with optional scaling, color space, and transparency handling. Supports both file uploads and URL-based sources."""
    body: PostConvertPsdToJpgRequestBody | None = None

# Operation: convert_image_psd_to_png
class PostConvertPsdToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PSD image file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PNG file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing for multiple output files to ensure unique, safe file naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output size, preserving quality for smaller source images.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertPsdToPngRequest(StrictModel):
    """Convert a PSD (Photoshop) image file to PNG format with optional scaling and proportional constraints. Supports both URL-based and direct file uploads."""
    body: PostConvertPsdToPngRequestBody | None = None

# Operation: convert_image_psd_to_pnm
class PostConvertPsdToPnmRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension for the target format, and adds indexing (e.g., filename_0.pnm, filename_1.pnm) when multiple files are generated.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the desired output dimensions.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertPsdToPnmRequest(StrictModel):
    """Convert a PSD (Photoshop) image file to PNM (Portable Anymap) format with optional scaling and proportional constraints."""
    body: PostConvertPsdToPnmRequestBody | None = None

# Operation: convert_psd_to_svg
class PostConvertPsdToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PSD file to convert. Accepts either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output SVG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.svg, output_1.svg) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only if the input image dimensions exceed the output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image.")
class PostConvertPsdToSvgRequest(StrictModel):
    """Convert a PSD (Photoshop) file to SVG (Scalable Vector Graphics) format. Supports URL or file content input with optional scaling and color space configuration."""
    body: PostConvertPsdToSvgRequestBody | None = None

# Operation: convert_psd_to_tiff
class PostConvertPsdToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The PSD file to convert. Accepts either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the name, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to fit the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a single multi-page TIFF file containing all layers or pages from the input PSD, rather than separate single-page files.")
class PostConvertPsdToTiffRequest(StrictModel):
    """Convert PSD (Photoshop) files to TIFF format with optional scaling and multi-page support. Supports both URL-based and direct file uploads."""
    body: PostConvertPsdToTiffRequestBody | None = None

# Operation: convert_image_psd_to_webp
class PostConvertPsdToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output file. The system automatically sanitizes the name, appends the correct .webp extension, and adds indexing (e.g., output_0.webp, output_1.webp) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image. Use 'default' for automatic detection, or specify a particular color model.")
class PostConvertPsdToWebpRequest(StrictModel):
    """Convert a PSD (Photoshop) image file to WebP format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads."""
    body: PostConvertPsdToWebpRequestBody | None = None

# Operation: convert_publication_to_jpg
class PostConvertPubToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The publication file to convert. Accepts either a URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output JPG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.jpg, filename_1.jpg) when multiple files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the publication file if it is password-protected.")
    jpg_type: Literal["jpeg", "jpegcmyk", "jpeggray"] | None = Field(default=None, validation_alias="JpgType", serialization_alias="JpgType", description="The JPG color mode and encoding type for the output image.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions.")
class PostConvertPubToJpgRequest(StrictModel):
    """Converts a publication file (PUB format) to JPG image format with configurable output quality, color mode, and scaling options. Supports password-protected documents and customizable output file naming."""
    body: PostConvertPubToJpgRequestBody | None = None

# Operation: convert_pub_to_pdf
class PostConvertPubToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Publisher file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the source document if it is password-protected.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="Whether to preserve document metadata (title, author, keywords) in the output PDF.")
    pdf_version: Literal["1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8", "2.0"] | None = Field(default=None, validation_alias="PdfVersion", serialization_alias="PdfVersion", description="PDF specification version to use for the output document.")
    pdf_resolution: int | None = Field(default=None, validation_alias="PdfResolution", serialization_alias="PdfResolution", description="Output resolution in dots per inch (DPI). Higher values improve quality but increase file size.", ge=10, le=2400)
    pdf_title: str | None = Field(default=None, validation_alias="PdfTitle", serialization_alias="PdfTitle", description="Custom title for the PDF document. Use a single quote and space (' ') to remove the title entirely.")
    pdf_subject: str | None = Field(default=None, validation_alias="PdfSubject", serialization_alias="PdfSubject", description="Custom subject for the PDF document. Use a single quote and space (' ') to remove the subject entirely.")
    pdf_author: str | None = Field(default=None, validation_alias="PdfAuthor", serialization_alias="PdfAuthor", description="Custom author name for the PDF document. Use a single quote and space (' ') to remove the author entirely.")
    pdf_keywords: str | None = Field(default=None, validation_alias="PdfKeywords", serialization_alias="PdfKeywords", description="Custom keywords for the PDF document. Use a single quote and space (' ') to remove the keywords entirely.")
    open_page: int | None = Field(default=None, validation_alias="OpenPage", serialization_alias="OpenPage", description="Page number where the PDF should open when first displayed.", ge=1, le=3000)
    open_zoom: Literal["Default", "ActualSize", "FitPage", "FitWidth", "FitHeight", "FitVisible", "25", "50", "75", "100", "125", "150", "200", "400", "800", "1600", "2400", "3200", "6400"] | None = Field(default=None, validation_alias="OpenZoom", serialization_alias="OpenZoom", description="Default zoom level when opening the PDF. Choose from preset percentages or fit-to-page options.")
    rotate_page: Literal["Disabled", "ByPage", "All"] | None = Field(default=None, validation_alias="RotatePage", serialization_alias="RotatePage", description="Automatically rotate pages based on text orientation. 'ByPage' rotates each page individually, 'All' rotates based on the majority text direction, 'Disabled' skips rotation.")
    color_space: Literal["Default", "RGB", "CMYK", "Gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the PDF output. RGB is standard for screen viewing, CMYK for professional printing, and Gray for monochrome documents.")
class PostConvertPubToPdfRequest(StrictModel):
    """Converts a Publisher document to PDF format with customizable metadata, resolution, and viewer settings. Supports password-protected documents and automatic page rotation based on text orientation."""
    body: PostConvertPubToPdfRequestBody | None = None

# Operation: convert_pub_to_png
class PostConvertPubToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Publisher file to convert. Accepts either a URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the .png extension, and adds numeric suffixes (e.g., output_0.png, output_1.png) if multiple files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the Publisher file if it is password-protected.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintains the original aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Applies scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged.")
class PostConvertPubToPngRequest(StrictModel):
    """Converts a Microsoft Publisher (.pub) file to PNG image format. Supports password-protected documents and provides scaling options to control output image dimensions."""
    body: PostConvertPubToPngRequestBody | None = None

# Operation: convert_pub_to_tiff
class PostConvertPubToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct .tiff extension, and adds numeric suffixes (e.g., _0, _1) for multi-page outputs to ensure unique identification.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected Publisher documents.")
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(default=None, validation_alias="TiffType", serialization_alias="TiffType", description="Specifies the TIFF compression type and color depth. Options range from color formats (24/32-bit with various compression) to grayscale and monochrome variants.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="When enabled, combines all pages into a single multi-page TIFF file. When disabled, generates separate TIFF files for each page.")
    fill_order: Literal["0", "1"] | None = Field(default=None, validation_alias="FillOrder", serialization_alias="FillOrder", description="Defines the logical bit order within each byte of the TIFF data. Use 0 for most standard applications or 1 for specific compatibility requirements.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when resizing the output image. When disabled, allows free scaling without proportion constraints.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="When enabled, scaling is applied only if the input image dimensions exceed the target output dimensions. When disabled, scaling is applied regardless of input size.")
class PostConvertPubToTiffRequest(StrictModel):
    """Converts Microsoft Publisher (.pub) files to TIFF image format with configurable compression, color depth, and scaling options. Supports password-protected documents and multi-page output."""
    body: PostConvertPubToTiffRequestBody | None = None

# Operation: convert_rtf_to_html
class PostConvertRtfToHtmlRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The RTF file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated HTML output file. The API automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., `document_0.html`, `document_1.html`) when multiple files are produced from a single input.")
    inline_images: bool | None = Field(default=None, validation_alias="InlineImages", serialization_alias="InlineImages", description="Whether to embed images directly into the HTML output as base64-encoded data URIs, creating a single self-contained file without external image dependencies.")
class PostConvertRtfToHtmlRequest(StrictModel):
    """Converts RTF (Rich Text Format) documents to HTML format. Optionally embeds images inline within the HTML output for self-contained documents."""
    body: PostConvertRtfToHtmlRequestBody | None = None

# Operation: convert_rtf_to_jpg
class PostConvertRtfToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The RTF file to convert. Accepts either a URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the RTF document if it is password-protected.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range format. Only pages within this range will be included in the output.")
class PostConvertRtfToJpgRequest(StrictModel):
    """Converts RTF (Rich Text Format) documents to JPG image format. Supports password-protected documents and allows specifying which pages to convert."""
    body: PostConvertRtfToJpgRequestBody | None = None

# Operation: convert_rtf_to_pdf
class PostConvertRtfToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The RTF file to convert. Accepts either a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected RTF documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10).")
    convert_markups: bool | None = Field(default=None, validation_alias="ConvertMarkups", serialization_alias="ConvertMarkups", description="When enabled, includes document markups such as revisions and comments in the converted PDF.")
    convert_tags: bool | None = Field(default=None, validation_alias="ConvertTags", serialization_alias="ConvertTags", description="When enabled, converts document structure tags to improve PDF accessibility for screen readers and assistive technologies.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="When enabled, preserves document metadata (Title, Author, Keywords, etc.) in the PDF metadata.")
    bookmark_mode: Literal["none", "headings", "bookmarks"] | None = Field(default=None, validation_alias="BookmarkMode", serialization_alias="BookmarkMode", description="Controls bookmark generation in the output PDF. Use 'none' to disable bookmarks, 'headings' to generate from document headings, or 'bookmarks' to use existing bookmarks from the source document.")
    update_toc: bool | None = Field(default=None, validation_alias="UpdateToc", serialization_alias="UpdateToc", description="When enabled, automatically updates all tables of content in the document before conversion.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="When enabled, creates a PDF/A-3a compliant document for long-term archival and preservation.")
class PostConvertRtfToPdfRequest(StrictModel):
    """Converts RTF (Rich Text Format) documents to PDF format with support for advanced features like bookmarks, metadata preservation, and PDF/A compliance. Handles protected documents, page range selection, and document structure conversion."""
    body: PostConvertRtfToPdfRequestBody | None = None

# Operation: convert_rtf_to_text
class PostConvertRtfToTxtRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The RTF file to convert. Accepts either a file URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output text file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.txt, output_1.txt) for multiple files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected RTF documents.")
    substitutions: bool | None = Field(default=None, validation_alias="Substitutions", serialization_alias="Substitutions", description="When enabled, replaces special symbols with their text equivalents (e.g., © becomes (c)).")
    end_line_char: Literal["crlf", "cr", "lfcr", "lf"] | None = Field(default=None, validation_alias="EndLineChar", serialization_alias="EndLineChar", description="Specifies the line ending character to use in the output text file.")
class PostConvertRtfToTxtRequest(StrictModel):
    """Converts RTF (Rich Text Format) documents to plain text format. Supports password-protected files, symbol substitution, and configurable line ending characters."""
    body: PostConvertRtfToTxtRequestBody | None = None

# Operation: convert_svg_to_jpg
class PostConvertSvgToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The SVG file to convert. Accepts either a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output JPG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    alpha_color: str | None = Field(default=None, validation_alias="AlphaColor", serialization_alias="AlphaColor", description="Replace transparent areas with a specific color. Accepts RGBA or CMYK hex strings, or standard color names.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image.")
class PostConvertSvgToJpgRequest(StrictModel):
    """Convert SVG vector graphics to JPG raster format with customizable scaling, color space, and transparency handling options."""
    body: PostConvertSvgToJpgRequestBody | None = None

# Operation: convert_svg_to_pdf
class PostConvertSvgToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The SVG file to convert. Can be provided as a file upload or as a URL pointing to the SVG resource.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric suffixes if multiple files are generated.")
    horizontal_alignment: Literal["left", "center", "right"] | None = Field(default=None, validation_alias="HorizontalAlignment", serialization_alias="HorizontalAlignment", description="Controls how the SVG image is positioned horizontally within the PDF page.")
    vertical_alignment: Literal["top", "center", "bottom"] | None = Field(default=None, validation_alias="VerticalAlignment", serialization_alias="VerticalAlignment", description="Controls how the SVG image is positioned vertically within the PDF page.")
    background_color: str | None = Field(default=None, validation_alias="BackgroundColor", serialization_alias="BackgroundColor", description="Sets the background color of the PDF page. Accepts hexadecimal color codes (e.g., #FFFFFF), RGB values, HSL values, or standard color names.")
    use_image_page_size: bool | None = Field(default=None, validation_alias="UseImagePageSize", serialization_alias="UseImagePageSize", description="When enabled, uses the SVG image's intrinsic width and height to determine the PDF page size, overriding any explicit page size settings.")
class PostConvertSvgToPdfRequest(StrictModel):
    """Converts SVG (Scalable Vector Graphics) files to PDF format with customizable layout, alignment, and styling options. Supports both file uploads and URL-based inputs."""
    body: PostConvertSvgToPdfRequestBody | None = None

# Operation: convert_svg_to_png
class PostConvertSvgToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The SVG file to convert. Accepts either a URL pointing to an SVG file or the raw SVG file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple files from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertSvgToPngRequest(StrictModel):
    """Convert SVG (Scalable Vector Graphics) files to PNG (Portable Network Graphics) format. Supports both URL-based and direct file content input with optional scaling controls."""
    body: PostConvertSvgToPngRequestBody | None = None

# Operation: convert_svg_to_pnm
class PostConvertSvgToPnmRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The SVG file to convert. Accepts either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct .pnm extension, and adds numeric indexing (e.g., output_0.pnm, output_1.pnm) when multiple files are generated.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintains the original aspect ratio when scaling the output image to prevent distortion.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Applies scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertSvgToPnmRequest(StrictModel):
    """Converts SVG (Scalable Vector Graphics) files to PNM (Portable Anymap) format. Supports URL or file content input with optional scaling and proportional constraint controls."""
    body: PostConvertSvgToPnmRequestBody | None = None

# Operation: convert_svg_image
class PostConvertSvgToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The SVG file to convert. Accepts either a URL reference or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.svg, filename_1.svg) for multiple outputs to ensure unique, safe file naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling transformations only when the input image dimensions exceed the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image. Use 'default' to preserve the source color space, or specify a target color space for conversion.")
class PostConvertSvgToSvgRequest(StrictModel):
    """Convert an SVG image file with optional scaling and color space adjustments. Supports URL or direct file content input and produces a new SVG file with customizable output naming."""
    body: PostConvertSvgToSvgRequestBody | None = None

# Operation: convert_svg_to_tiff
class PostConvertSvgToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The SVG file to convert. Accepts either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions to ensure unique, safe file naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions, leaving smaller images unchanged.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a single multi-page TIFF file containing all converted pages, or create separate TIFF files for each page when disabled.")
class PostConvertSvgToTiffRequest(StrictModel):
    """Convert SVG (Scalable Vector Graphics) files to TIFF (Tagged Image File Format) with configurable scaling and multi-page output options. Supports both URL-based and direct file content input."""
    body: PostConvertSvgToTiffRequestBody | None = None

# Operation: convert_svg_to_webp
class PostConvertSvgToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The SVG file to convert. Accepts either a file upload or a URL pointing to the SVG resource.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output WebP file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output WebP image. Choose from standard color profiles to optimize for different use cases.")
class PostConvertSvgToWebpRequest(StrictModel):
    """Convert SVG images to WebP format with optional scaling and color space adjustments. Supports both file uploads and URL-based inputs."""
    body: PostConvertSvgToWebpRequestBody | None = None

# Operation: fill_template_to_docx
class PostConvertTemplateToDocxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Word template file to be converted. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.docx, filename_1.docx) for multiple outputs.")
    binding_method: Literal["properties", "placeholders"] | None = Field(default=None, validation_alias="BindingMethod", serialization_alias="BindingMethod", description="Specifies how data values are bound to the template. Use 'properties' to fill Word document custom property fields, or 'placeholders' to search for and replace named placeholders within the document text.")
    json_payload: str | None = Field(default=None, validation_alias="JsonPayload", serialization_alias="JsonPayload", description="JSON array of key-value pairs to populate the template. Structure varies by binding method: for properties, include Name, Value, and Type fields; for placeholders, supports strings, integers, images, tables, HTML, and conditional values with optional dimensions and links.")
class PostConvertTemplateToDocxRequest(StrictModel):
    """Converts a Word document template to DOCX format by populating it with data values. Supports binding data to either document properties or text placeholders, enabling dynamic document generation from templates."""
    body: PostConvertTemplateToDocxRequestBody | None = None

# Operation: convert_template_to_pdf
class PostConvertTemplateToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The template document to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the .pdf extension, and adds numeric suffixes (e.g., report_0.pdf, report_1.pdf) when multiple files are generated.")
    json_payload: str | None = Field(default=None, validation_alias="JsonPayload", serialization_alias="JsonPayload", description="JSON array of data to populate into the template. Supports custom document properties (string, integer, datetime, boolean types) and placeholders (string, image, table, html, conditional types). Images should be provided as base64-encoded strings with optional dimensions and links.")
    binding_method: Literal["properties", "placeholders"] | None = Field(default=None, validation_alias="BindingMethod", serialization_alias="BindingMethod", description="Specifies how data is bound to the template. Use 'properties' to fill Word document custom properties fields, or 'placeholders' to search for and replace named placeholders within the document text.")
class PostConvertTemplateToPdfRequest(StrictModel):
    """Converts a template document to PDF format while populating custom properties or placeholders with provided data. Supports dynamic content injection including text, images, tables, and HTML elements."""
    body: PostConvertTemplateToPdfRequestBody | None = None

# Operation: convert_tiff_to_jpg
class PostConvertTiffToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Can be provided as a file upload or as a URL pointing to a TIFF image.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., image_0.jpg, image_1.jpg) for multiple outputs from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions.")
    alpha_color: str | None = Field(default=None, validation_alias="AlphaColor", serialization_alias="AlphaColor", description="Specify a color to replace transparent areas in the image. Accepts RGBA or CMYK hex color codes, or standard color names.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image. Use 'default' for automatic detection, or specify a particular color model.")
class PostConvertTiffToJpgRequest(StrictModel):
    """Convert TIFF image files to JPG format with optional scaling, color space adjustment, and transparency handling. Supports both file uploads and URL-based inputs."""
    body: PostConvertTiffToJpgRequestBody | None = None

# Operation: convert_tiff_to_pdf
class PostConvertTiffToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The TIFF image file to convert. Accepts either a file URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pdf, output_1.pdf) when multiple files are generated from a single input.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotation angle in degrees for the image. Specify a value between -360 and 360, or leave empty to automatically rotate based on EXIF data in TIFF and JPEG images.", ge=-360, le=360)
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Color space for the output image. Choose from standard color spaces or use default for automatic detection.")
    color_profile: Literal["default", "isocoatedv2"] | None = Field(default=None, validation_alias="ColorProfile", serialization_alias="ColorProfile", description="Color profile to apply to the output image. Some profiles may override the ColorSpace setting.")
    margin_horizontal: int | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Horizontal margin for the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500)
    margin_vertical: int | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Vertical margin for the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500)
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Enable PDF/A-1b compliance for long-term archival and preservation of the output PDF document.")
    alpha_channel: bool | None = Field(default=None, validation_alias="AlphaChannel", serialization_alias="AlphaChannel", description="Enable or disable the alpha channel (transparency) in the output image if available in the source TIFF.")
class PostConvertTiffToPdfRequest(StrictModel):
    """Convert TIFF image files to PDF format with support for color space management, page margins, rotation, and PDF/A compliance. Handles single or multiple TIFF images and produces properly formatted PDF output."""
    body: PostConvertTiffToPdfRequestBody | None = None

# Operation: convert_tiff_to_png
class PostConvertTiffToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert, provided either as a URL or as binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., image_0.png, image_1.png) when multiple files are generated from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertTiffToPngRequest(StrictModel):
    """Convert TIFF image files to PNG format with optional scaling and proportional constraint controls. Supports both URL-based and direct file content input."""
    body: PostConvertTiffToPngRequestBody | None = None

# Operation: convert_tiff_to_pnm
class PostConvertTiffToPnmRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The TIFF image file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNM file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., output_0.pnm, output_1.pnm) when multiple files are generated.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertTiffToPnmRequest(StrictModel):
    """Convert a TIFF image file to PNM (Portable Anymap) format. Supports optional image scaling with proportional constraints and conditional scaling based on input dimensions."""
    body: PostConvertTiffToPnmRequestBody | None = None

# Operation: convert_tiff_to_svg
class PostConvertTiffToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The TIFF image file to convert. Can be provided as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output SVG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming.")
    preset: Literal["none", "detailed", "crisp", "graphic", "illustration", "noisyScan"] | None = Field(default=None, validation_alias="Preset", serialization_alias="Preset", description="Vectorization preset that applies pre-configured tracing settings optimized for specific image types. When selected, presets override individual converter options except ColorMode, providing consistent and balanced SVG results.")
    color_mode: Literal["color", "bw"] | None = Field(default=None, validation_alias="ColorMode", serialization_alias="ColorMode", description="Color processing mode for tracing the image. Choose between full color vectorization or black-and-white conversion.")
    layering: Literal["cutout", "stacked"] | None = Field(default=None, validation_alias="Layering", serialization_alias="Layering", description="Arrangement method for color regions in the output SVG. Cutout mode creates isolated layers, while stacked mode overlays regions for blending effects.")
    curve_mode: Literal["pixel", "polygon", "spline"] | None = Field(default=None, validation_alias="CurveMode", serialization_alias="CurveMode", description="Shape approximation method during tracing. Pixel mode follows exact boundaries with minimal smoothing, Polygon creates straight-edged paths with sharp corners, and Spline generates smooth continuous curves for natural-looking shapes.")
class PostConvertTiffToSvgRequest(StrictModel):
    """Converts TIFF raster images to scalable SVG vector format using configurable tracing and vectorization settings. Supports preset configurations for different image types, color modes, and curve approximation methods."""
    body: PostConvertTiffToSvgRequestBody | None = None

# Operation: convert_tiff_image
class PostConvertTiffToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output file. The system automatically sanitizes the name, appends the correct file extension, and adds indexing (e.g., filename_0.tiff, filename_1.tiff) for multiple output files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a multi-page TIFF file when processing multiple images or pages.")
class PostConvertTiffToTiffRequest(StrictModel):
    """Convert and optimize TIFF images with scaling and multi-page support. Accepts file input as URL or binary content and generates output with customizable naming and formatting options."""
    body: PostConvertTiffToTiffRequestBody | None = None

# Operation: convert_image_tiff_to_webp
class PostConvertTiffToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL pointing to a TIFF file or raw binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output WebP file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing for multiple output files to ensure unique, safe file naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image to a different size.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions are larger than the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image. Choose from standard color profiles or use the default setting.")
class PostConvertTiffToWebpRequest(StrictModel):
    """Convert TIFF image files to WebP format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads."""
    body: PostConvertTiffToWebpRequestBody | None = None

# Operation: convert_text_to_image
class PostConvertTxtToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The text document to convert. Accepts either a file URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output JPG file(s). The API automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., document_0.jpg, document_1.jpg) when multiple files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10 inclusive).")
class PostConvertTxtToJpgRequest(StrictModel):
    """Converts text documents to JPG image format. Supports file uploads or URLs, with optional password protection for secured documents and configurable page range selection."""
    body: PostConvertTxtToJpgRequestBody | None = None

# Operation: convert_text_to_pdf
class PostConvertTxtToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The text file to convert. Accepts either a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.pdf, filename_1.pdf) for multiple outputs.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to include in the output using a range format (e.g., 1-10 for pages 1 through 10).")
    font_name: Literal["Arial", "Bahnschrift", "Calibri", "Cambria", "Consolas", "Constantia", "CourierNew", "Georgia", "Tahoma", "TimesNewRoman", "Verdana"] | None = Field(default=None, validation_alias="FontName", serialization_alias="FontName", description="The font to use for text rendering in the PDF. Select from available system fonts.")
    font_size: int | None = Field(default=None, validation_alias="FontSize", serialization_alias="FontSize", description="The font size in points for text in the PDF.", ge=4, le=72)
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="When enabled, creates a PDF/A-1b compliant document suitable for long-term archival and preservation.")
    margin_left: dict | None = Field(default=None, validation_alias="MarginLeft", serialization_alias="MarginLeft", description="Set the page left margin in millimeters (mm).", ge=0, le=500)
    margin_right: int | None = Field(default=None, validation_alias="MarginRight", serialization_alias="MarginRight", description="Set the page right margin in millimeters (mm).", ge=0, le=500)
    margin_top: int | None = Field(default=None, validation_alias="MarginTop", serialization_alias="MarginTop", description="Set the page top margin in millimeters (mm).", ge=0, le=500)
    margin_bottom: int | None = Field(default=None, validation_alias="MarginBottom", serialization_alias="MarginBottom", description="Set the page bottom margin in millimeters (mm).", ge=0, le=500)
class PostConvertTxtToPdfRequest(StrictModel):
    """Converts text files to PDF format with customizable formatting options including font selection, size, and page range specification. Supports PDF/A-1b compliance for archival purposes."""
    body: PostConvertTxtToPdfRequestBody | None = None

# Operation: convert_vsdx_to_jpg
class PostConvertVsdxToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Visio file to convert, provided either as a publicly accessible URL or as binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output JPEG file. The system automatically sanitizes the filename, appends the correct .jpg extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) if multiple files are generated from a single input.")
class PostConvertVsdxToJpgRequest(StrictModel):
    """Converts a Visio diagram file (VSDX format) to JPEG image format. Accepts file input as a URL or binary content and generates optimized JPEG output with customizable naming."""
    body: PostConvertVsdxToJpgRequestBody | None = None

# Operation: convert_vsdx_to_pdf
class PostConvertVsdxToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Visio file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `document_0.pdf`, `document_1.pdf`) when multiple files are produced.")
    pdfa_version: Literal["none", "pdfA1b", "pdfA2b", "pdfA3b"] | None = Field(default=None, validation_alias="PdfaVersion", serialization_alias="PdfaVersion", description="PDF/A compliance version for the output file. Use 'none' for standard PDF, or specify a PDF/A version for long-term archival compliance.")
class PostConvertVsdxToPdfRequest(StrictModel):
    """Converts a Visio diagram file (VSDX format) to PDF format. Supports optional PDF/A compliance versions for archival purposes."""
    body: PostConvertVsdxToPdfRequestBody | None = None

# Operation: convert_vsdx_to_png
class PostConvertVsdxToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Visio file to convert. Provide either a URL pointing to the file or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PNG output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `diagram_0.png`, `diagram_1.png`) for multiple output files.")
    background_color: str | None = Field(default=None, validation_alias="BackgroundColor", serialization_alias="BackgroundColor", description="Background color for the generated PNG image. Specify a color name, RGB values (comma-separated), or HEX code. Use `transparent` to preserve transparency.")
class PostConvertVsdxToPngRequest(StrictModel):
    """Converts a Visio diagram file (VSDX format) to PNG image format. Supports file input via URL or direct file content, with optional background color customization."""
    body: PostConvertVsdxToPngRequestBody | None = None

# Operation: convert_vsdx_to_tiff
class PostConvertVsdxToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Visio file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., `diagram_0.tiff`, `diagram_1.tiff`) for multi-page outputs to ensure unique, safe file naming.")
    background_color: str | None = Field(default=None, validation_alias="BackgroundColor", serialization_alias="BackgroundColor", description="Background color for the generated TIFF images. Specify a color name (e.g., `white`, `black`), RGB values (comma-separated), HEX code, or `transparent` to preserve transparency.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Whether to generate a single multi-page TIFF file or separate single-page files. When enabled, all pages are combined into one TIFF; when disabled, each page becomes a separate file.")
class PostConvertVsdxToTiffRequest(StrictModel):
    """Converts Visio diagram files (VSDX format) to TIFF image format. Supports single or multi-page TIFF output with customizable background color handling."""
    body: PostConvertVsdxToTiffRequestBody | None = None

# Operation: convert_webpage_to_jpg
class PostConvertWebToJpgRequestBody(StrictModel):
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output JPG file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., output_0.jpg, output_1.jpg) when multiple files are generated.")
    ad_block: bool | None = Field(default=None, validation_alias="AdBlock", serialization_alias="AdBlock", description="Block advertisements from rendering on the webpage during conversion.")
    cookie_consent_block: bool | None = Field(default=None, validation_alias="CookieConsentBlock", serialization_alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and warnings from the webpage before conversion.")
    cookies: str | None = Field(default=None, validation_alias="Cookies", serialization_alias="Cookies", description="Set additional cookies to include in the page request. Provide multiple cookies as semicolon-separated name=value pairs.")
    java_script: bool | None = Field(default=None, validation_alias="JavaScript", serialization_alias="JavaScript", description="Enable JavaScript execution on the webpage during conversion. Disable if the page should be rendered without running scripts.")
    wait_element: str | None = Field(default=None, validation_alias="WaitElement", serialization_alias="WaitElement", description="CSS selector for a DOM element. The converter will wait for this element to appear in the page before starting the conversion process.")
    user_css: str | None = Field(default=None, validation_alias="UserCss", serialization_alias="UserCss", description="Custom CSS rules to apply to the webpage before conversion begins.")
    css_media_type: str | None = Field(default=None, validation_alias="CssMediaType", serialization_alias="CssMediaType", description="CSS media type to use during conversion (e.g., screen, print, or custom media types). Controls how stylesheets are applied.")
    headers: str | None = Field(default=None, validation_alias="Headers", serialization_alias="Headers", description="Custom HTTP headers to include in the page request. Provide headers as pipe-separated pairs with colon-delimited name and value.")
    zoom: float | None = Field(default=None, validation_alias="Zoom", serialization_alias="Zoom", description="Set the zoom level for webpage rendering. Values below 1.0 zoom out, values above 1.0 zoom in.", ge=0.1, le=10)
    url: str | None = Field(default=None, validation_alias="Url", serialization_alias="Url", description="The URL of the webpage to convert. Special characters in the URL must be properly encoded.", json_schema_extra={'format': 'uri'})
class PostConvertWebToJpgRequest(StrictModel):
    """Converts a webpage to a JPG image file with support for JavaScript rendering, ad blocking, cookie consent removal, and custom styling. Allows fine-grained control over page rendering behavior including element waiting, custom CSS, HTTP headers, and zoom levels."""
    body: PostConvertWebToJpgRequestBody | None = None

# Operation: convert_webpage_to_pdf
class PostConvertWebToPdfRequestBody(StrictModel):
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the generated PDF output file. The system sanitizes the filename, appends the .pdf extension automatically, and adds numeric suffixes (e.g., report_0.pdf, report_1.pdf) when multiple files are generated from a single conversion.")
    ad_block: bool | None = Field(default=None, validation_alias="AdBlock", serialization_alias="AdBlock", description="Enable ad blocking to remove advertisements from the web page during conversion.")
    cookie_consent_block: bool | None = Field(default=None, validation_alias="CookieConsentBlock", serialization_alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and warnings from the web page before conversion.")
    cookies: str | None = Field(default=None, validation_alias="Cookies", serialization_alias="Cookies", description="Provide additional cookies to include in the page request. Format as semicolon-separated key-value pairs.")
    java_script: bool | None = Field(default=None, validation_alias="JavaScript", serialization_alias="JavaScript", description="Allow JavaScript execution on the web page during conversion. Disable if the page contains scripts that interfere with rendering.")
    wait_element: str | None = Field(default=None, validation_alias="WaitElement", serialization_alias="WaitElement", description="CSS selector for a DOM element that must be present before conversion begins. Useful for waiting until dynamic content loads.")
    user_css: str | None = Field(default=None, validation_alias="UserCss", serialization_alias="UserCss", description="Custom CSS rules to apply to the page before conversion. Useful for hiding elements, adjusting styles, or overriding page formatting.")
    css_media_type: str | None = Field(default=None, validation_alias="CssMediaType", serialization_alias="CssMediaType", description="CSS media type to use during conversion. Controls how stylesheets are applied (e.g., screen for on-screen rendering, print for print-optimized output).")
    headers: str | None = Field(default=None, validation_alias="Headers", serialization_alias="Headers", description="Custom HTTP headers to include in the page request. Format as pipe-separated header pairs with colon-delimited names and values.")
    load_lazy_content: bool | None = Field(default=None, validation_alias="LoadLazyContent", serialization_alias="LoadLazyContent", description="Load images that are initially hidden and only appear when scrolled into view. Enables conversion of lazy-loaded image content.")
    viewport_width: int | None = Field(default=None, validation_alias="ViewportWidth", serialization_alias="ViewportWidth", description="Browser viewport width in pixels. Affects how the page layout renders. Valid range is 200 to 4000 pixels.", ge=200, le=4000)
    viewport_height: int | None = Field(default=None, validation_alias="ViewportHeight", serialization_alias="ViewportHeight", description="Browser viewport height in pixels. Affects how the page layout renders. Valid range is 200 to 4000 pixels.", ge=200, le=4000)
    respect_viewport: bool | None = Field(default=None, validation_alias="RespectViewport", serialization_alias="RespectViewport", description="When enabled, the PDF renders as it appears in the browser. When disabled, uses Chrome's print-to-PDF behavior which may adjust layout for printing.")
    margin_top: int | None = Field(default=None, validation_alias="MarginTop", serialization_alias="MarginTop", description="Top margin of the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500)
    margin_right: int | None = Field(default=None, validation_alias="MarginRight", serialization_alias="MarginRight", description="Right margin of the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500)
    margin_bottom: int | None = Field(default=None, validation_alias="MarginBottom", serialization_alias="MarginBottom", description="Bottom margin of the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500)
    margin_left: int | None = Field(default=None, validation_alias="MarginLeft", serialization_alias="MarginLeft", description="Left margin of the PDF page in millimeters. Valid range is 0 to 500 mm.", ge=0, le=500)
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specify which pages to include in the output PDF. Use ranges (e.g., 1-10) or comma-separated page numbers (e.g., 1,2,5).")
    background: bool | None = Field(default=None, validation_alias="Background", serialization_alias="Background", description="Include background colors and images from the web page in the PDF output.")
    fixed_elements: Literal["fixed", "absolute", "relative", "hide"] | None = Field(default=None, validation_alias="FixedElements", serialization_alias="FixedElements", description="Modify how fixed-position elements are handled during conversion. Choose how to adapt fixed elements for PDF layout.")
    show_elements: str | None = Field(default=None, validation_alias="ShowElements", serialization_alias="ShowElements", description="CSS selector for DOM elements that must remain visible during conversion. All other elements will be hidden.")
    avoid_break_elements: str | None = Field(default=None, validation_alias="AvoidBreakElements", serialization_alias="AvoidBreakElements", description="CSS selector for elements that should not be split across page breaks. Keeps these elements intact on a single page.")
    break_before_elements: str | None = Field(default=None, validation_alias="BreakBeforeElements", serialization_alias="BreakBeforeElements", description="CSS selector for elements that should trigger a page break before them. Useful for forcing section starts on new pages.")
    break_after_elements: str | None = Field(default=None, validation_alias="BreakAfterElements", serialization_alias="BreakAfterElements", description="CSS selector for elements that should trigger a page break after them. Useful for forcing content separation across pages.")
    url: str | None = Field(default=None, validation_alias="Url", serialization_alias="Url", description="The web page URL to convert to PDF. Special characters in the URL must be properly encoded.", json_schema_extra={'format': 'uri'})
    header: str | None = Field(default=None, validation_alias="Header", serialization_alias="Header", description="This property will insert an HTML header into each page. HTML tags containing the classes `pageNumber`, `totalPages`, `title`, and `date` will be filled in with the metadata relevant to each individual page. Inline CSS could be utilized to style the HTML provided.\r\n\r\n```html\r\n<style>\r\n    .right {\r\n        float: right;\r\n    }\r\n\r\n    .left {\r\n        float: left;\r\n    }\r\n</style>\r\n<span class='left'>\r\n    page number \r\n    <span class='pageNumber'></span>\r\n</span>\r\n<span class='right'>\r\n    date \r\n    <span class='date'></span>\r\n</span>\r\n```")
    footer: str | None = Field(default=None, validation_alias="Footer", serialization_alias="Footer", description="This property will insert an HTML footer into each page. HTML tags containing the classes `pageNumber`, `totalPages`, `title`, and `date` will be filled in with the metadata relevant to each individual page. Inline CSS could be utilized to style the HTML provided.\r\n\r\n```html\r\n<style>\r\n    .right {\r\n        float: right;\r\n    }\r\n\r\n    .left {\r\n        float: left;\r\n    }\r\n</style>\r\n<span class='left'>\r\n    page number \r\n    <span class='pageNumber'></span>\r\n</span>\r\n<span class='right'>\r\n    date \r\n    <span class='date'></span>\r\n</span>\r\n```")
class PostConvertWebToPdfRequest(StrictModel):
    """Converts a web page to PDF format with advanced rendering options including JavaScript execution, custom styling, viewport configuration, and page layout controls. Supports ad blocking, cookie consent removal, lazy content loading, and granular page break management."""
    body: PostConvertWebToPdfRequestBody | None = None

# Operation: convert_webpage_to_png
class PostConvertWebToPngRequestBody(StrictModel):
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PNG file. The system sanitizes the filename, appends the .png extension automatically, and adds numeric suffixes (e.g., _0, _1) when generating multiple files from a single conversion.")
    ad_block: bool | None = Field(default=None, validation_alias="AdBlock", serialization_alias="AdBlock", description="Block advertisements from appearing in the converted page.")
    cookie_consent_block: bool | None = Field(default=None, validation_alias="CookieConsentBlock", serialization_alias="CookieConsentBlock", description="Automatically remove EU cookie consent banners and warnings from the web page before conversion.")
    cookies: str | None = Field(default=None, validation_alias="Cookies", serialization_alias="Cookies", description="Provide additional cookies to include in the page request. Separate multiple cookies with semicolons.")
    java_script: bool | None = Field(default=None, validation_alias="JavaScript", serialization_alias="JavaScript", description="Enable JavaScript execution during page rendering. Disable if the page contains problematic scripts.")
    wait_element: str | None = Field(default=None, validation_alias="WaitElement", serialization_alias="WaitElement", description="CSS selector for a DOM element. The converter will wait for this element to appear before starting the conversion, useful for pages with dynamic content.")
    user_css: str | None = Field(default=None, validation_alias="UserCss", serialization_alias="UserCss", description="Custom CSS rules to apply to the page before conversion begins.")
    css_media_type: str | None = Field(default=None, validation_alias="CssMediaType", serialization_alias="CssMediaType", description="CSS media type to use during rendering. Common values are 'screen' and 'print', but custom media types are also supported.")
    headers: str | None = Field(default=None, validation_alias="Headers", serialization_alias="Headers", description="Custom HTTP headers to include in the page request. Separate multiple headers with pipe characters, with each header formatted as name:value.")
    zoom: float | None = Field(default=None, validation_alias="Zoom", serialization_alias="Zoom", description="Zoom level for rendering the webpage. Values below 1.0 zoom out, values above 1.0 zoom in.", ge=0.1, le=10)
    transparent_background: bool | None = Field(default=None, validation_alias="TransparentBackground", serialization_alias="TransparentBackground", description="Use a transparent background instead of the default white background. The source HTML body element should have its background color set to 'none' for this to work effectively.")
    url: str | None = Field(default=None, validation_alias="Url", serialization_alias="Url", description="The URL of the web page to convert. Special characters in the URL must be properly encoded.", json_schema_extra={'format': 'uri'})
class PostConvertWebToPngRequest(StrictModel):
    """Converts a web page to a PNG image with support for JavaScript rendering, ad blocking, cookie consent removal, and custom styling. Allows fine-grained control over rendering behavior through CSS media types, zoom levels, and DOM element waiting."""
    body: PostConvertWebToPngRequestBody | None = None

# Operation: convert_webpage_to_text
class PostConvertWebToTxtRequestBody(StrictModel):
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output text file. The API sanitizes the filename, appends the correct extension, and uses indexing (e.g., output_0.txt, output_1.txt) for multiple files to ensure unique, safe file naming.")
    ad_block: bool | None = Field(default=None, validation_alias="AdBlock", serialization_alias="AdBlock", description="Block advertisements and ad-related content from appearing in the converted text output.")
    cookie_consent_block: bool | None = Field(default=None, validation_alias="CookieConsentBlock", serialization_alias="CookieConsentBlock", description="Automatically remove EU cookie consent notices and related warnings from the web page before conversion.")
    cookies: str | None = Field(default=None, validation_alias="Cookies", serialization_alias="Cookies", description="Set additional cookies to include in the page request. Provide multiple cookies as name-value pairs separated by semicolons.")
    java_script: bool | None = Field(default=None, validation_alias="JavaScript", serialization_alias="JavaScript", description="Enable JavaScript execution on the web page during conversion. Required for pages with dynamic content.")
    wait_element: str | None = Field(default=None, validation_alias="WaitElement", serialization_alias="WaitElement", description="CSS selector for a DOM element that must appear before conversion begins. Useful for waiting on dynamically loaded content.")
    user_css: str | None = Field(default=None, validation_alias="UserCss", serialization_alias="UserCss", description="Custom CSS rules to apply to the page before conversion. Allows styling adjustments that affect the text output.")
    css_media_type: str | None = Field(default=None, validation_alias="CssMediaType", serialization_alias="CssMediaType", description="CSS media type to use during conversion (e.g., screen, print, or custom types). Affects which styles are applied.")
    headers: str | None = Field(default=None, validation_alias="Headers", serialization_alias="Headers", description="Custom HTTP headers to include in the page request. Provide headers as name-value pairs separated by pipe characters, with each pair separated by a colon.")
    url: str | None = Field(default=None, validation_alias="Url", serialization_alias="Url", description="URL of the web page to convert. Special characters such as query parameters must be properly URL-encoded.", json_schema_extra={'format': 'uri'})
    extract_elements: str | None = Field(default=None, validation_alias="ExtractElements", serialization_alias="ExtractElements", description="CSS selector to extract specific DOM elements instead of converting the entire page. Use class selectors (.class-name), ID selectors (#elementId), or tag names for targeted content retrieval.")
class PostConvertWebToTxtRequest(StrictModel):
    """Converts a web page to plain text format with optional content filtering, JavaScript execution, and targeted element extraction. Supports custom headers, cookies, CSS styling, and DOM element waiting for dynamic content."""
    body: PostConvertWebToTxtRequestBody | None = None

# Operation: convert_webp_to_gif
class PostConvertWebpToGifRequestBody(StrictModel):
    files: list[str] | None = Field(default=None, validation_alias="Files", serialization_alias="Files", description="WebP image file(s) to convert. Accept file uploads or URLs pointing to WebP images. When providing multiple files, each is converted independently to GIF format.")
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output GIF file(s). The system automatically sanitizes the filename, appends the .gif extension, and adds numeric suffixes (e.g., image_0.gif, image_1.gif) when converting multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when resizing the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only resize the image if the input dimensions are larger than the target output size.")
    animation_delay: int | None = Field(default=None, validation_alias="AnimationDelay", serialization_alias="AnimationDelay", description="Time interval between animation frames, specified in hundredths of a second. Controls animation playback speed.", ge=0, le=20000)
    animation_iterations: int | None = Field(default=None, validation_alias="AnimationIterations", serialization_alias="AnimationIterations", description="Number of times the animation loops. Set to 0 for infinite looping.", ge=0, le=1000)
class PostConvertWebpToGifRequest(StrictModel):
    """Convert WebP image files to animated GIF format with customizable animation settings. Supports single or batch file conversion with optional scaling and frame delay control."""
    body: PostConvertWebpToGifRequestBody | None = None

# Operation: convert_webp_to_jpg
class PostConvertWebpToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL pointing to a WebP image or the raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output JPG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple outputs to ensure unique, safe file naming.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    alpha_color: str | None = Field(default=None, validation_alias="AlphaColor", serialization_alias="AlphaColor", description="Replace transparent areas with a solid color. Accepts RGBA or CMYK hex strings, or standard color names.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output image.")
class PostConvertWebpToJpgRequest(StrictModel):
    """Convert WebP image files to JPG format with optional scaling and color space adjustments. Supports both URL-based and direct file uploads."""
    body: PostConvertWebpToJpgRequestBody | None = None

# Operation: convert_webp_to_pdf
class PostConvertWebpToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The WebP image file to convert. Provide either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the output PDF file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing for multiple output files to ensure unique, safe file naming.")
    rotate: int | None = Field(default=None, validation_alias="Rotate", serialization_alias="Rotate", description="Rotate the output image by the specified degrees. Use a value between -360 and 360. Leave empty to apply automatic rotation based on EXIF data in TIFF and JPEG images.", ge=-360, le=360)
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Set the color space for the output PDF. Choose from standard color space options to control how colors are represented in the final document.")
    color_profile: Literal["default", "isocoatedv2"] | None = Field(default=None, validation_alias="ColorProfile", serialization_alias="ColorProfile", description="Apply a specific color profile to the output PDF. Some profiles may override the ColorSpace setting. Use 'isocoatedv2' for ISO Coated v2 profile compliance.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Enable PDF/A-1b compliance for the output document. When true, creates an archival-grade PDF suitable for long-term preservation.")
    margin_horizontal: dict | None = Field(default=None, validation_alias="MarginHorizontal", serialization_alias="MarginHorizontal", description="Set the page horizontal margin in millimeters (mm).", ge=0, le=500)
    margin_vertical: int | None = Field(default=None, validation_alias="MarginVertical", serialization_alias="MarginVertical", description="Set the page vertical margin in millimeters (mm).", ge=0, le=500)
class PostConvertWebpToPdfRequest(StrictModel):
    """Convert WebP image files to PDF format with support for rotation, color space configuration, and PDF/A compliance. Accepts file input as URL or binary content and generates a properly named output PDF file."""
    body: PostConvertWebpToPdfRequestBody | None = None

# Operation: convert_webp_to_png
class PostConvertWebpToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert, provided either as a URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The API automatically sanitizes the filename, appends the correct .png extension, and adds numeric indexing (e.g., image_0.png, image_1.png) when multiple files are generated from a single input.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the target output dimensions.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertWebpToPngRequest(StrictModel):
    """Convert WebP image files to PNG format with optional scaling and proportional constraints. Supports both URL-based and direct file content input."""
    body: PostConvertWebpToPngRequestBody | None = None

# Operation: convert_webp_to_pnm
class PostConvertWebpToPnmRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert, provided as a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.pnm, output_1.pnm) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Apply scaling only when the input image dimensions exceed the target output dimensions.")
    transparent_color: str | None = Field(default=None, validation_alias="TransparentColor", serialization_alias="TransparentColor", description="Add alpha channel to image, setting pixels matching color to transparent. Values accepted are RGBA, CMYK hex string, color name or RGB format like this 255,255,255 (RED=255, GREEN=255, BLUE=255) or 255,255,255,150 with alpha chanel.")
class PostConvertWebpToPnmRequest(StrictModel):
    """Convert a WebP image to PNM (Portable Anymap) format with optional scaling and proportional constraint controls."""
    body: PostConvertWebpToPnmRequestBody | None = None

# Operation: convert_webp_to_svg
class PostConvertWebpToSvgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The WebP image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output SVG file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.svg, output_1.svg) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="Define the color space for the output SVG image.")
class PostConvertWebpToSvgRequest(StrictModel):
    """Convert WebP image files to SVG vector format. Supports URL or file content input with optional scaling and color space configuration."""
    body: PostConvertWebpToSvgRequestBody | None = None

# Operation: convert_webp_to_tiff
class PostConvertWebpToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The WebP image file to convert. Provide either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output TIFF file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multiple files.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="Generate a multi-page TIFF file when converting. If disabled, creates a single-page TIFF.")
class PostConvertWebpToTiffRequest(StrictModel):
    """Convert WebP image files to TIFF format with optional scaling and multi-page support. Accepts file input as URL or binary content and generates properly named output file(s)."""
    body: PostConvertWebpToTiffRequestBody | None = None

# Operation: convert_webp_image
class PostConvertWebpToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The image file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.webp, filename_1.webp) for multiple outputs to ensure unique identification.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Only apply scaling if the input image dimensions exceed the target output dimensions.")
    color_space: Literal["default", "rgb", "srgb", "cmyk", "gray"] | None = Field(default=None, validation_alias="ColorSpace", serialization_alias="ColorSpace", description="The color space to apply to the output image.")
class PostConvertWebpToWebpRequest(StrictModel):
    """Convert a WebP image to WebP format with optional scaling and color space adjustments. Supports URL or file content input and generates a uniquely named output file."""
    body: PostConvertWebpToWebpRequestBody | None = None

# Operation: convert_wpd_to_pdf
class PostConvertWpdToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The document file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the generated output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected documents.")
    page_range: str | None = Field(default=None, validation_alias="PageRange", serialization_alias="PageRange", description="Specifies which pages to convert using a range format (e.g., 1-10 converts pages 1 through 10).")
    convert_markups: bool | None = Field(default=None, validation_alias="ConvertMarkups", serialization_alias="ConvertMarkups", description="Includes document markups such as revisions and comments in the converted PDF.")
    convert_tags: bool | None = Field(default=None, validation_alias="ConvertTags", serialization_alias="ConvertTags", description="Preserves document structure tags in the PDF for improved accessibility and screen reader compatibility.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="Transfers document metadata (title, author, keywords) from the source document to PDF metadata properties.")
    bookmark_mode: Literal["none", "headings", "bookmarks"] | None = Field(default=None, validation_alias="BookmarkMode", serialization_alias="BookmarkMode", description="Controls bookmark generation in the output PDF. Use 'none' to disable bookmarks, 'headings' to auto-generate from document headings, or 'bookmarks' to use existing bookmarks from the source file.")
    update_toc: bool | None = Field(default=None, validation_alias="UpdateToc", serialization_alias="UpdateToc", description="Automatically updates all tables of content in the document before conversion to ensure accuracy in the PDF output.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Generates a PDF/A-3a compliant document for long-term archival and compliance requirements.")
class PostConvertWpdToPdfRequest(StrictModel):
    """Converts WordPerfect documents (.wpd) to PDF format with support for metadata preservation, accessibility tags, and PDF/A compliance. Handles protected documents and allows selective page range conversion."""
    body: PostConvertWpdToPdfRequestBody | None = None

# Operation: convert_spreadsheet_format
class PostConvertXlsToXlsRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The spreadsheet file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file(s). The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., `report_0.xlsx`, `report_1.xlsx`) when multiple files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input file if it is password-protected.")
class PostConvertXlsToXlsRequest(StrictModel):
    """Converts an Excel spreadsheet file to Excel format, with support for password-protected documents. Useful for standardizing file formats or re-encoding existing spreadsheets."""
    body: PostConvertXlsToXlsRequestBody | None = None

# Operation: convert_spreadsheet_xls_to_xlsx
class PostConvertXlsToXlsxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The spreadsheet file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct XLSX extension, and adds numeric indexing (e.g., report_0.xlsx, report_1.xlsx) when multiple files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="The password required to open the input file if it is password-protected.")
class PostConvertXlsToXlsxRequest(StrictModel):
    """Converts Microsoft Excel files from the legacy XLS format to the modern XLSX format. Supports password-protected documents and generates uniquely named output files."""
    body: PostConvertXlsToXlsxRequestBody | None = None

# Operation: convert_xlsb_to_csv
class PostConvertXlsbToCsvRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The XLSB file to convert. Can be provided as a file upload or as a URL pointing to the source file.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output CSV file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., output_0.csv, output_1.csv) if multiple files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the XLSB file if it is password-protected.")
class PostConvertXlsbToCsvRequest(StrictModel):
    """Converts an Excel Binary Workbook (XLSB) file to CSV format. Supports both file uploads and URL-based sources, with optional password protection for encrypted documents."""
    body: PostConvertXlsbToCsvRequestBody | None = None

# Operation: convert_xlsb_to_pdf
class PostConvertXlsbToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The file to convert, provided as a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PDF file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected XLSB documents.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="Preserves document metadata such as Title, Author, and Keywords in the PDF output.")
    auto_column_fit: bool | None = Field(default=None, validation_alias="AutoColumnFit", serialization_alias="AutoColumnFit", description="Automatically adjusts column widths to minimize unnecessary empty space in tables.")
    header_on_each_page: bool | None = Field(default=None, validation_alias="HeaderOnEachPage", serialization_alias="HeaderOnEachPage", description="Repeats the header row on every page when spreadsheet content spans multiple pages. Uses the table header if detected, otherwise treats the first data row as the header.")
    thousands_separator: str | None = Field(default=None, validation_alias="ThousandsSeparator", serialization_alias="ThousandsSeparator", description="Character used to separate thousands in numeric values.")
    decimal_separator: str | None = Field(default=None, validation_alias="DecimalSeparator", serialization_alias="DecimalSeparator", description="Character used to separate decimal places in numeric values.")
    date_format: Literal["us", "iso", "eu", "german", "japanese"] | None = Field(default=None, validation_alias="DateFormat", serialization_alias="DateFormat", description="Sets the date format for the output document, overriding the default US locale to ensure consistency across regional Excel settings.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Creates a PDF/A-1b compliant document for long-term archival and preservation.")
class PostConvertXlsbToPdfRequest(StrictModel):
    """Converts Excel Binary Workbook (XLSB) files to PDF format with support for metadata preservation, formatting options, and PDF/A compliance. Handles protected documents and provides flexible control over layout, number formatting, and date localization."""
    body: PostConvertXlsbToPdfRequestBody | None = None

# Operation: convert_spreadsheet_to_csv
class PostConvertXlsxToCsvRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Excel file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output CSV file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., report_0.csv, report_1.csv) if multiple files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the Excel file if it is password-protected.")
class PostConvertXlsxToCsvRequest(StrictModel):
    """Converts an Excel spreadsheet (XLSX) file to CSV format. Supports password-protected documents and customizable output file naming."""
    body: PostConvertXlsxToCsvRequestBody | None = None

# Operation: convert_spreadsheet_to_image_xlsx
class PostConvertXlsxToJpgRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Excel file to convert. Accepts either a file URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output JPG file(s). The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.jpg, output_1.jpg) for multiple files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected Excel documents.")
    jpg_type: Literal["jpeg", "jpegcmyk", "jpeggray"] | None = Field(default=None, validation_alias="JpgType", serialization_alias="JpgType", description="The JPG color format to use for the output image.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Whether to maintain the original aspect ratio when scaling the output image.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Whether to apply scaling only when the input image dimensions exceed the output dimensions.")
class PostConvertXlsxToJpgRequest(StrictModel):
    """Converts an Excel spreadsheet file to JPG image format. Supports password-protected documents and provides options for image type, scaling, and proportional resizing."""
    body: PostConvertXlsxToJpgRequestBody | None = None

# Operation: convert_spreadsheet_to_pdf
class PostConvertXlsxToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Excel file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric suffixes (e.g., report_0.pdf, report_1.pdf) when multiple files are produced from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected Excel documents.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="Preserves document metadata such as title, author, and keywords in the PDF output.")
    auto_column_fit: bool | None = Field(default=None, validation_alias="AutoColumnFit", serialization_alias="AutoColumnFit", description="Automatically adjusts column widths to minimize unnecessary whitespace in tables.")
    header_on_each_page: bool | None = Field(default=None, validation_alias="HeaderOnEachPage", serialization_alias="HeaderOnEachPage", description="Repeats the header row on every page when spreadsheet content spans multiple pages. Uses the detected table header row, or the first data row if no table is present.")
    thousands_separator: str | None = Field(default=None, validation_alias="ThousandsSeparator", serialization_alias="ThousandsSeparator", description="Character used to separate thousands in numeric values (e.g., comma for 1,000 or period for 1.000).")
    decimal_separator: str | None = Field(default=None, validation_alias="DecimalSeparator", serialization_alias="DecimalSeparator", description="Character used to separate decimal places in numeric values (e.g., period for 1.5 or comma for 1,5).")
    date_format: Literal["us", "iso", "eu", "german", "japanese"] | None = Field(default=None, validation_alias="DateFormat", serialization_alias="DateFormat", description="Date format standard for the output PDF. Overrides the default US locale format to ensure consistent date representation regardless of regional Excel settings.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Generates a PDF/A-1b compliant document for long-term archival and preservation purposes.")
class PostConvertXlsxToPdfRequest(StrictModel):
    """Converts Excel spreadsheets (XLSX format) to PDF documents with support for formatting options, metadata preservation, and PDF/A compliance. Handles protected documents, customizable number/date formatting, and multi-page layout control."""
    body: PostConvertXlsxToPdfRequestBody | None = None

# Operation: convert_spreadsheet_to_image_png
class PostConvertXlsxToPngRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Excel file to convert. Accepts either a URL pointing to the file or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output PNG file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.png, output_1.png) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the Excel file if it is password-protected.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintains the original aspect ratio when scaling the output image to fit the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Applies scaling only when the input image dimensions exceed the target output dimensions, preventing upscaling of smaller images.")
class PostConvertXlsxToPngRequest(StrictModel):
    """Converts an Excel spreadsheet file to PNG image format. Supports URL or file content input with optional scaling and password protection for secured documents."""
    body: PostConvertXlsxToPngRequestBody | None = None

# Operation: encrypt_xlsx_workbook
class PostConvertXlsxToProtectRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Excel file to encrypt. Accepts either a file URL or raw file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output encrypted file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., `report_0.xlsx`, `report_1.xlsx`) if multiple files are generated.")
    encrypt_password: str | None = Field(default=None, validation_alias="EncryptPassword", serialization_alias="EncryptPassword", description="The password required to open the encrypted Excel workbook. Users must enter this password to access the file.")
class PostConvertXlsxToProtectRequest(StrictModel):
    """Convert an Excel workbook to a password-protected format. Encrypts the file with a specified password that must be entered to open it."""
    body: PostConvertXlsxToProtectRequestBody | None = None

# Operation: convert_spreadsheet_to_tiff
class PostConvertXlsxToTiffRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Excel file to convert. Accepts either a file URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output TIFF file(s). The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., output_0.tiff, output_1.tiff) for multi-page conversions to ensure unique, safe file naming.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the Excel file if it is password-protected.")
    tiff_type: Literal["color24nc", "color32nc", "color24lzw", "color32lzw", "color24zip", "color32zip", "grayscale", "grayscalelzw", "grayscalezip", "monochromeg3", "monochromeg32d", "monochromeg4", "monochromelzw", "monochromepackbits"] | None = Field(default=None, validation_alias="TiffType", serialization_alias="TiffType", description="Specifies the TIFF compression type and color depth. Choose from color variants (24-bit or 32-bit with no compression, LZW, or ZIP), grayscale options, or monochrome formats with various compression algorithms.")
    multi_page: bool | None = Field(default=None, validation_alias="MultiPage", serialization_alias="MultiPage", description="When enabled, combines all spreadsheet pages into a single multi-page TIFF file. When disabled, each page is saved as a separate TIFF file.")
    fill_order: Literal["0", "1"] | None = Field(default=None, validation_alias="FillOrder", serialization_alias="FillOrder", description="Defines the bit order within each byte: use 0 for most significant bit first (standard), or 1 for least significant bit first.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="When enabled, maintains the original aspect ratio when scaling the output image to fit specified dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="When enabled, scaling is applied only if the input image dimensions exceed the target output dimensions. Smaller images are not enlarged.")
class PostConvertXlsxToTiffRequest(StrictModel):
    """Converts Excel spreadsheet files to TIFF image format with configurable compression, color depth, and multi-page support. Supports password-protected documents and optional image scaling."""
    body: PostConvertXlsxToTiffRequestBody | None = None

# Operation: convert_spreadsheet_to_image_webp
class PostConvertXlsxToWebpRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The Excel file to convert. Accepts either a URL or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="Custom name for the output file. The system automatically sanitizes the filename, appends the .webp extension, and adds numeric indexing (e.g., output_0.webp, output_1.webp) if multiple files are generated.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected Excel documents.")
    scale_proportions: bool | None = Field(default=None, validation_alias="ScaleProportions", serialization_alias="ScaleProportions", description="Maintains the original aspect ratio when scaling the output image to fit the target dimensions.")
    scale_if_larger: bool | None = Field(default=None, validation_alias="ScaleIfLarger", serialization_alias="ScaleIfLarger", description="Applies scaling only when the input image dimensions exceed the output dimensions, preserving quality for smaller images.")
class PostConvertXlsxToWebpRequest(StrictModel):
    """Converts an Excel spreadsheet file to WebP image format. Supports password-protected documents and configurable image scaling options."""
    body: PostConvertXlsxToWebpRequestBody | None = None

# Operation: convert_spreadsheet_format_modern
class PostConvertXlsxToXlsxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The spreadsheet file to convert. Accepts either a URL pointing to the file or the raw file content as binary data.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output file. The system automatically sanitizes the filename, appends the correct extension, and adds numeric indexing (e.g., filename_0, filename_1) when multiple files are generated from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="The password required to open password-protected spreadsheets. Only needed if the input file is encrypted.")
class PostConvertXlsxToXlsxRequest(StrictModel):
    """Converts an Excel spreadsheet to Excel format, with support for password-protected documents. Useful for standardizing file formats or re-encoding existing spreadsheets."""
    body: PostConvertXlsxToXlsxRequestBody | None = None

# Operation: convert_spreadsheet_template_to_pdf
class PostConvertXltxToPdfRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The spreadsheet file to convert. Accepts either a URL reference or binary file content.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the generated PDF output file. The system automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., report_0.pdf, report_1.pdf) when multiple files are produced from a single input.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open password-protected spreadsheet documents.")
    convert_metadata: bool | None = Field(default=None, validation_alias="ConvertMetadata", serialization_alias="ConvertMetadata", description="Preserves document metadata such as title, author, and keywords in the PDF output.")
    auto_column_fit: bool | None = Field(default=None, validation_alias="AutoColumnFit", serialization_alias="AutoColumnFit", description="Automatically adjusts column widths to minimize unnecessary whitespace in tables.")
    header_on_each_page: bool | None = Field(default=None, validation_alias="HeaderOnEachPage", serialization_alias="HeaderOnEachPage", description="Repeats the header row on every page when spreadsheet content spans multiple pages. Uses the table header if detected, otherwise treats the first data row as the header.")
    thousands_separator: str | None = Field(default=None, validation_alias="ThousandsSeparator", serialization_alias="ThousandsSeparator", description="Character used to separate thousands in numeric values.")
    decimal_separator: str | None = Field(default=None, validation_alias="DecimalSeparator", serialization_alias="DecimalSeparator", description="Character used to separate decimal places in numeric values.")
    date_format: Literal["us", "iso", "eu", "german", "japanese"] | None = Field(default=None, validation_alias="DateFormat", serialization_alias="DateFormat", description="Date format standard for the output document, overriding the default US locale format to ensure consistency across regional Excel settings.")
    pdfa: bool | None = Field(default=None, validation_alias="Pdfa", serialization_alias="Pdfa", description="Generates a PDF/A-1b compliant document for long-term archival and preservation.")
class PostConvertXltxToPdfRequest(StrictModel):
    """Converts Excel spreadsheet files (XLTX format) to PDF documents with customizable formatting, metadata handling, and locale-specific number/date formatting options."""
    body: PostConvertXltxToPdfRequestBody | None = None

# Operation: convert_xml_to_docx
class PostConvertXmlToDocxRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The XML file to convert. Accepts either a URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    file_name: str | None = Field(default=None, validation_alias="FileName", serialization_alias="FileName", description="The name for the output DOCX file. The API automatically sanitizes the filename, appends the correct extension, and adds indexing (e.g., filename_0.docx, filename_1.docx) for multiple output files.")
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password required to open the input XML file if it is password-protected.")
    update_toc: bool | None = Field(default=None, validation_alias="UpdateToc", serialization_alias="UpdateToc", description="Automatically updates all tables of content in the converted document.")
    update_references: bool | None = Field(default=None, validation_alias="UpdateReferences", serialization_alias="UpdateReferences", description="Automatically updates all reference fields in the converted document.")
class PostConvertXmlToDocxRequest(StrictModel):
    """Converts XML documents to DOCX format with optional support for password-protected files and automatic updates to tables of content and reference fields."""
    body: PostConvertXmlToDocxRequestBody | None = None

# Operation: extract_archive
class PostConvertZipToExtractRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="File", serialization_alias="File", description="The ZIP archive file to extract. Can be provided as a URL or raw file content in binary format.", json_schema_extra={'format': 'binary'})
    password: str | None = Field(default=None, validation_alias="Password", serialization_alias="Password", description="Password for opening password-protected ZIP archives. Required only if the archive is encrypted.")
class PostConvertZipToExtractRequest(StrictModel):
    """Extracts contents from a ZIP archive file. Supports password-protected archives by providing the required password."""
    body: PostConvertZipToExtractRequestBody | None = None

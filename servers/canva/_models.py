"""
Canva MCP Server - Pydantic Models

Generated: 2026-05-05 14:33:15 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "CreateAssetUploadJobRequest",
    "CreateDesignAutofillJobRequest",
    "CreateDesignExportJobRequest",
    "CreateDesignImportJobRequest",
    "CreateDesignRequest",
    "CreateDesignResizeJobRequest",
    "CreateFolderRequest",
    "CreateReplyRequest",
    "CreateThreadRequest",
    "CreateUrlAssetUploadJobRequest",
    "CreateUrlImportJobRequest",
    "DeleteAssetRequest",
    "DeleteFolderRequest",
    "GetAssetRequest",
    "GetAssetUploadJobRequest",
    "GetBrandTemplateDatasetRequest",
    "GetBrandTemplateRequest",
    "GetDesignAutofillJobRequest",
    "GetDesignExportFormatsRequest",
    "GetDesignExportJobRequest",
    "GetDesignImportJobRequest",
    "GetDesignPagesRequest",
    "GetDesignRequest",
    "GetDesignResizeJobRequest",
    "GetFolderRequest",
    "GetReplyRequest",
    "GetThreadRequest",
    "GetUrlAssetUploadJobRequest",
    "GetUrlImportJobRequest",
    "ListBrandTemplatesRequest",
    "ListDesignsRequest",
    "ListFolderItemsRequest",
    "ListRepliesRequest",
    "MoveFolderItemRequest",
    "UpdateAssetRequest",
    "UpdateFolderRequest",
    "CreateAssetUploadJobHeaderAssetUploadMetadata",
    "CreateDesignImportJobHeaderImportMetadata",
    "CustomDesignTypeInput",
    "DatasetValue",
    "GifExportFormat",
    "JpgExportFormat",
    "Mp4ExportFormat",
    "PdfExportFormat",
    "PngExportFormat",
    "PptxExportFormat",
    "PresetDesignTypeInput",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_asset
class GetAssetRequestPath(StrictModel):
    asset_id: str = Field(default=..., validation_alias="assetId", serialization_alias="assetId", description="The unique identifier of the asset to retrieve. Must be alphanumeric with hyphens and underscores allowed.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetAssetRequest(StrictModel):
    """Retrieve detailed metadata for a specific asset by its unique identifier. Use this operation to fetch asset information such as properties, status, and configuration details."""
    path: GetAssetRequestPath

# Operation: update_asset
class UpdateAssetRequestPath(StrictModel):
    asset_id: str = Field(default=..., validation_alias="assetId", serialization_alias="assetId", description="The unique identifier of the asset to update. Must be alphanumeric with hyphens and underscores.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class UpdateAssetRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the asset as displayed in the Canva UI. Leave undefined or empty to skip updating the name.", max_length=50)
    tags: list[str] | None = Field(default=None, description="Replacement tags for the asset. All existing tags are replaced when provided. Leave undefined to skip updating tags.", max_length=50)
class UpdateAssetRequest(StrictModel):
    """Update an asset's name and tags by asset ID. Tags are replaced entirely when provided, allowing you to manage asset metadata in the Canva UI."""
    path: UpdateAssetRequestPath
    body: UpdateAssetRequestBody | None = None

# Operation: delete_asset
class DeleteAssetRequestPath(StrictModel):
    asset_id: str = Field(default=..., validation_alias="assetId", serialization_alias="assetId", description="The unique identifier of the asset to delete.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class DeleteAssetRequest(StrictModel):
    """Delete an asset by its ID, moving it to trash. This mirrors the Canva UI behavior and does not remove the asset from designs that already use it."""
    path: DeleteAssetRequestPath

# Operation: upload_asset
class CreateAssetUploadJobRequestHeader(StrictModel):
    asset_upload_metadata: CreateAssetUploadJobHeaderAssetUploadMetadata = Field(default=..., validation_alias="Asset-Upload-Metadata", serialization_alias="Asset-Upload-Metadata", description="Metadata describing the asset being uploaded, including asset name, type, and other identifying information.")
class CreateAssetUploadJobRequestBody(StrictModel):
    """Binary of the asset to upload."""
    body: str = Field(default=..., description="The raw binary file content to upload as an asset. The file must be in a supported format as documented in the Assets API overview.", json_schema_extra={'format': 'binary'})
class CreateAssetUploadJobRequest(StrictModel):
    """Initiates an asynchronous job to upload an asset file to the user's content library. Use the returned job ID to poll for completion status and retrieve the uploaded asset details."""
    header: CreateAssetUploadJobRequestHeader
    body: CreateAssetUploadJobRequestBody

# Operation: get_asset_upload_job
class GetAssetUploadJobRequestPath(StrictModel):
    job_id: str = Field(default=..., validation_alias="jobId", serialization_alias="jobId", description="The unique identifier of the asset upload job to retrieve status for.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetAssetUploadJobRequest(StrictModel):
    """Retrieve the status and result of an asset upload job. Use this to poll for completion after creating an upload job, as the operation is asynchronous and may require multiple requests until a success or failed status is returned."""
    path: GetAssetUploadJobRequestPath

# Operation: initiate_url_asset_upload
class CreateUrlAssetUploadJobRequestBody(StrictModel):
    name: str = Field(default=..., description="A descriptive name for the asset being uploaded. Must be between 1 and 255 characters.", min_length=1, max_length=255)
    url: str = Field(default=..., description="The publicly accessible URL of the file to import. The URL must be reachable from the internet and support direct file access. Must be between 8 and 2048 characters.", min_length=8, max_length=2048)
class CreateUrlAssetUploadJobRequest(StrictModel):
    """Starts an asynchronous job to upload an asset from a publicly accessible URL to the user's content library. Supported file types are documented in the Assets API overview, with video assets limited to 100MB maximum file size."""
    body: CreateUrlAssetUploadJobRequestBody

# Operation: get_asset_upload_job_from_url
class GetUrlAssetUploadJobRequestPath(StrictModel):
    job_id: str = Field(default=..., validation_alias="jobId", serialization_alias="jobId", description="The unique identifier of the asset upload job to retrieve status for.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetUrlAssetUploadJobRequest(StrictModel):
    """Retrieve the status and result of an asset upload job created via URL. Poll this endpoint until the job reaches a terminal state (success or failed)."""
    path: GetUrlAssetUploadJobRequestPath

# Operation: autofill_design
class CreateDesignAutofillJobRequestBody(StrictModel):
    brand_template_id: str = Field(default=..., description="The ID of the brand template to use for autofilling. Brand template IDs were migrated to a new format in September 2025; old IDs remain supported for 6 months.")
    title: str | None = Field(default=None, description="Optional title for the autofilled design. If not provided, the design will use the brand template's title.", min_length=1, max_length=255)
    data: dict[str, DatasetValue] = Field(default=..., description="Data object containing field names mapped to their values. Supports images (via asset_id), text strings, and chart data with typed rows and cells.")
class CreateDesignAutofillJobRequest(StrictModel):
    """Starts an asynchronous job to autofill a Canva design using a brand template and input data. Requires membership in a Canva Enterprise organization."""
    body: CreateDesignAutofillJobRequestBody

# Operation: get_autofill_job
class GetDesignAutofillJobRequestPath(StrictModel):
    job_id: str = Field(default=..., validation_alias="jobId", serialization_alias="jobId", description="The unique identifier of the design autofill job to retrieve.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetDesignAutofillJobRequest(StrictModel):
    """Retrieve the result of a design autofill job. Poll this endpoint until the job reaches a `success` or `failed` status to get the final result."""
    path: GetDesignAutofillJobRequestPath

# Operation: list_brand_templates
class ListBrandTemplatesRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="Search brand templates by one or more search terms to filter the results.")
    limit: int | None = Field(default=None, description="The maximum number of brand templates to return in the response.", json_schema_extra={'format': 'int32'})
    ownership: Literal["any", "owned", "shared"] | None = Field(default=None, description="Filter brand templates based on the user's ownership relationship to them.")
    sort_by: Literal["relevance", "modified_descending", "modified_ascending", "title_descending", "title_ascending"] | None = Field(default=None, description="Sort the returned brand templates by relevance, modification date, or title in ascending or descending order.")
    dataset: Literal["any", "non_empty"] | None = Field(default=None, description="Filter brand templates based on whether they have dataset definitions configured for use with Autofill APIs.")
class ListBrandTemplatesRequest(StrictModel):
    """Retrieve a list of brand templates that the user has access to within their Canva Enterprise organization. Supports searching, filtering by ownership and dataset definitions, and sorting options."""
    query: ListBrandTemplatesRequestQuery | None = None

# Operation: get_brand_template
class GetBrandTemplateRequestPath(StrictModel):
    brand_template_id: str = Field(default=..., validation_alias="brandTemplateId", serialization_alias="brandTemplateId", description="The unique identifier for the brand template. Must be 1-50 characters long and contain only alphanumeric characters, hyphens, or underscores.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetBrandTemplateRequest(StrictModel):
    """Retrieves metadata for a brand template. Note: Brand template IDs were migrated to a new format in September 2025; old IDs remain valid for 6 months. Requires the user to be a member of a Canva Enterprise organization."""
    path: GetBrandTemplateRequestPath

# Operation: get_brand_template_dataset
class GetBrandTemplateDatasetRequestPath(StrictModel):
    brand_template_id: str = Field(default=..., validation_alias="brandTemplateId", serialization_alias="brandTemplateId", description="The unique identifier of the brand template. Brand template IDs were migrated to a new format in September 2025; old IDs remain valid for 6 months.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetBrandTemplateDatasetRequest(StrictModel):
    """Retrieves the dataset definition for a brand template, including any autofill data fields and their accepted types (images, text, or charts). Use this to understand what data can be populated when creating a design autofill job."""
    path: GetBrandTemplateDatasetRequestPath

# Operation: list_comment_replies
class ListRepliesRequestPath(StrictModel):
    design_id: str = Field(default=..., validation_alias="designId", serialization_alias="designId", description="The unique identifier of the design containing the comment thread.", pattern='^[a-zA-Z0-9_-]{1,50}$')
    thread_id: str = Field(default=..., validation_alias="threadId", serialization_alias="threadId", description="The unique identifier of the comment thread for which to retrieve replies.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class ListRepliesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of replies to return in the response. Defaults to 50 if not specified.", ge=1, le=100)
class ListRepliesRequest(StrictModel):
    """Retrieves all replies for a specific comment or suggestion thread on a design. This preview API allows you to access threaded discussions within design comments."""
    path: ListRepliesRequestPath
    query: ListRepliesRequestQuery | None = None

# Operation: create_comment_reply
class CreateReplyRequestPath(StrictModel):
    design_id: str = Field(default=..., validation_alias="designId", serialization_alias="designId", description="The unique identifier of the design containing the comment thread.", pattern='^[a-zA-Z0-9_-]{1,50}$')
    thread_id: str = Field(default=..., validation_alias="threadId", serialization_alias="threadId", description="The unique identifier of the comment thread to reply to. This ID is returned when a thread is created or can be obtained from existing replies in the thread.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class CreateReplyRequestBody(StrictModel):
    message_plaintext: str = Field(default=..., description="The reply message in plaintext format. You can mention users by including their User ID and Team ID using the format [user_id:team_id].", min_length=1, max_length=2048)
class CreateReplyRequest(StrictModel):
    """Creates a reply to a comment or suggestion thread on a design. Each thread supports a maximum of 100 replies, and you can mention users by including their User ID and Team ID in the message."""
    path: CreateReplyRequestPath
    body: CreateReplyRequestBody

# Operation: get_comment_thread
class GetThreadRequestPath(StrictModel):
    design_id: str = Field(default=..., validation_alias="designId", serialization_alias="designId", description="The unique identifier of the design containing the comment thread.", pattern='^[a-zA-Z0-9_-]{1,50}$')
    thread_id: str = Field(default=..., validation_alias="threadId", serialization_alias="threadId", description="The unique identifier of the comment thread to retrieve.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetThreadRequest(StrictModel):
    """Retrieves a comment or suggestion thread on a design. Use this to fetch details about a specific comment thread; for replies within a thread, use the get_reply operation instead."""
    path: GetThreadRequestPath

# Operation: get_comment_reply
class GetReplyRequestPath(StrictModel):
    design_id: str = Field(default=..., validation_alias="designId", serialization_alias="designId", description="The unique identifier of the design containing the comment thread.", pattern='^[a-zA-Z0-9_-]{1,50}$')
    thread_id: str = Field(default=..., validation_alias="threadId", serialization_alias="threadId", description="The unique identifier of the comment thread containing the reply.", pattern='^[a-zA-Z0-9_-]{1,50}$')
    reply_id: str = Field(default=..., validation_alias="replyId", serialization_alias="replyId", description="The unique identifier of the specific reply to retrieve.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetReplyRequest(StrictModel):
    """Retrieves a specific reply to a comment or suggestion thread on a design. This API is currently in preview and may have unannounced breaking changes."""
    path: GetReplyRequestPath

# Operation: create_comment
class CreateThreadRequestPath(StrictModel):
    design_id: str = Field(default=..., validation_alias="designId", serialization_alias="designId", description="The unique identifier of the design where the comment will be created.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class CreateThreadRequestBody(StrictModel):
    message_plaintext: str = Field(default=..., description="The comment message in plaintext. You can mention users by including their User ID and Team ID in the format [user_id:team_id]. If assigning the comment to a user, you must mention them in this message.", min_length=1, max_length=2048)
    assignee_id: str | None = Field(default=None, description="Optionally assign the comment to a Canva user by their User ID. The assigned user must be mentioned in the message_plaintext parameter.")
class CreateThreadRequest(StrictModel):
    """Creates a new comment thread on a design. Comments enable collaboration and feedback within Canva designs, with optional user assignment and mentions."""
    path: CreateThreadRequestPath
    body: CreateThreadRequestBody

# Operation: list_designs
class ListDesignsRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="Search term or terms to filter designs by title or content. Searches across both user-created and shared designs.", max_length=255)
    ownership: Literal["any", "owned", "shared"] | None = Field(default=None, description="Filter designs based on ownership status. Use 'owned' for designs created by the user, 'shared' for designs shared with the user, or 'any' to include both.")
    sort_by: Literal["relevance", "modified_descending", "modified_ascending", "title_descending", "title_ascending"] | None = Field(default=None, description="Sort the returned designs by relevance to search query, modification date, or title in ascending or descending order.")
    limit: int | None = Field(default=None, description="Maximum number of designs to return in the response. Useful for pagination and controlling response size.", json_schema_extra={'format': 'int32'})
class ListDesignsRequest(StrictModel):
    """Retrieve metadata for all designs in a Canva user's projects. Supports filtering by search terms, ownership status, and sorting options to help users find and organize their designs."""
    query: ListDesignsRequestQuery | None = None

# Operation: create_design
class CreateDesignRequestBody(StrictModel):
    design_type: Annotated[PresetDesignTypeInput | CustomDesignTypeInput, Field(discriminator="type_")] | None = Field(default=None, description="The preset design type to use for the new design. Either specify a design_type or provide custom height and width dimensions.")
    asset_id: str | None = Field(default=None, description="The ID of an image asset from the user's projects to insert into the created design. Currently supports image assets only.")
    title: str | None = Field(default=None, description="The name of the design. Must be between 1 and 255 characters.", min_length=1, max_length=255)
class CreateDesignRequest(StrictModel):
    """Creates a new Canva design using either a preset design type or custom dimensions. Optionally add an image asset to the design. Note: Blank designs are automatically deleted after 7 days if not edited."""
    body: CreateDesignRequestBody | None = None

# Operation: get_design
class GetDesignRequestPath(StrictModel):
    design_id: str = Field(default=..., validation_alias="designId", serialization_alias="designId", description="The unique identifier for the design to retrieve. Must be alphanumeric with hyphens and underscores allowed, between 1 and 50 characters in length.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetDesignRequest(StrictModel):
    """Retrieves comprehensive metadata for a specific design, including owner information, editing and viewing URLs, and thumbnail details."""
    path: GetDesignRequestPath

# Operation: list_design_pages
class GetDesignPagesRequestPath(StrictModel):
    design_id: str = Field(default=..., validation_alias="designId", serialization_alias="designId", description="The unique identifier of the design containing the pages to retrieve.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetDesignPagesRequestQuery(StrictModel):
    offset: int | None = Field(default=None, description="The page index to start retrieving from. Pages use one-based numbering, where the first page has index 1.", json_schema_extra={'format': 'int32'})
    limit: int | None = Field(default=None, description="The maximum number of pages to return in this request, starting from the offset index.", json_schema_extra={'format': 'int32'})
class GetDesignPagesRequest(StrictModel):
    """Retrieves metadata for pages in a design, including page-specific thumbnails. Use offset and limit parameters to paginate through pages. Note: Some design types (such as Canva docs) do not have pages."""
    path: GetDesignPagesRequestPath
    query: GetDesignPagesRequestQuery | None = None

# Operation: list_design_export_formats
class GetDesignExportFormatsRequestPath(StrictModel):
    design_id: str = Field(default=..., validation_alias="designId", serialization_alias="designId", description="The unique identifier of the design whose export formats you want to retrieve.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetDesignExportFormatsRequest(StrictModel):
    """Retrieves the available file formats for exporting a design. The returned formats depend on the design type and page types within the design, showing only formats supported by all pages."""
    path: GetDesignExportFormatsRequestPath

# Operation: import_design
class CreateDesignImportJobRequestHeader(StrictModel):
    import_metadata: CreateDesignImportJobHeaderImportMetadata = Field(default=..., validation_alias="Import-Metadata", serialization_alias="Import-Metadata", description="Metadata describing the design being imported, including details about the source file and import configuration. Provided as an HTTP header parameter.")
class CreateDesignImportJobRequestBody(StrictModel):
    """Binary of the file to import."""
    body: str = Field(default=..., description="The binary file content to import as a design. The file must be in a supported format for design imports.", json_schema_extra={'format': 'binary'})
class CreateDesignImportJobRequest(StrictModel):
    """Initiates an asynchronous job to import an external file as a new design in Canva. Supported file types include various design formats; use the Get design import job API to check job status and retrieve results."""
    header: CreateDesignImportJobRequestHeader
    body: CreateDesignImportJobRequestBody

# Operation: get_design_import_job
class GetDesignImportJobRequestPath(StrictModel):
    job_id: str = Field(default=..., validation_alias="jobId", serialization_alias="jobId", description="The unique identifier of the design import job to retrieve status for.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetDesignImportJobRequest(StrictModel):
    """Retrieves the status and result of a design import job. Use this to poll for completion after creating an import job, as the operation is asynchronous and may require multiple requests until a success or failed status is returned."""
    path: GetDesignImportJobRequestPath

# Operation: import_design_from_url
class CreateUrlImportJobRequestBody(StrictModel):
    title: str = Field(default=..., description="The title for the imported design. Must be between 1 and 255 characters.", min_length=1, max_length=255)
    url: str = Field(default=..., description="The publicly accessible URL of the file to import. The URL must be reachable from the internet and support direct file access.", min_length=1, max_length=2048)
    mime_type: str | None = Field(default=None, description="The MIME type of the file being imported. If omitted, Canva will automatically detect the file type. Useful for improving import speed when the file type is known.", min_length=1, max_length=100)
class CreateUrlImportJobRequest(StrictModel):
    """Starts an asynchronous job to import an external file from a URL as a new design in Canva. Supports multiple file types and allows optional MIME type specification for faster processing."""
    body: CreateUrlImportJobRequestBody

# Operation: get_url_import_job
class GetUrlImportJobRequestPath(StrictModel):
    job_id: str = Field(default=..., validation_alias="jobId", serialization_alias="jobId", description="The unique identifier of the URL import job to retrieve status for.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetUrlImportJobRequest(StrictModel):
    """Retrieves the status and result of a URL import job. Use this to poll for completion of an asynchronous import operation, which will return a `success` or `failed` status once processing is complete."""
    path: GetUrlImportJobRequestPath

# Operation: start_design_export
class CreateDesignExportJobRequestBody(StrictModel):
    design_id: str = Field(default=..., description="The unique identifier of the design to export.")
    format_: Annotated[PdfExportFormat | JpgExportFormat | PngExportFormat | PptxExportFormat | GifExportFormat | Mp4ExportFormat, Field(discriminator="type_")] = Field(default=..., validation_alias="format", serialization_alias="format", description="The desired export file format and associated configuration options.")
class CreateDesignExportJobRequest(StrictModel):
    """Initiates an asynchronous job to export a design file in the specified format (PDF, JPG, PNG, GIF, PPTX, or MP4). Download URLs are provided upon completion and remain valid for 24 hours."""
    body: CreateDesignExportJobRequestBody

# Operation: get_design_export_job
class GetDesignExportJobRequestPath(StrictModel):
    export_id: str = Field(default=..., validation_alias="exportId", serialization_alias="exportId", description="The unique identifier of the export job to retrieve status and results for.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetDesignExportJobRequest(StrictModel):
    """Retrieves the status and results of a design export job. When successful, returns download URLs for each page of the exported design (valid for 24 hours). You may need to poll this endpoint until the job reaches a terminal status (success or failed)."""
    path: GetDesignExportJobRequestPath

# Operation: get_folder
class GetFolderRequestPath(StrictModel):
    folder_id: str = Field(default=..., validation_alias="folderId", serialization_alias="folderId", description="The unique identifier of the folder to retrieve. Must be 1-50 characters containing alphanumeric characters, hyphens, or underscores.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetFolderRequest(StrictModel):
    """Retrieves the name and metadata details of a specific folder by its folder ID."""
    path: GetFolderRequestPath

# Operation: rename_folder
class UpdateFolderRequestPath(StrictModel):
    folder_id: str = Field(default=..., validation_alias="folderId", serialization_alias="folderId", description="The unique identifier of the folder to rename.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class UpdateFolderRequestBody(StrictModel):
    name: str = Field(default=..., description="The new name for the folder as it will appear in the Canva UI. Must be between 1 and 255 characters.", min_length=1, max_length=255)
class UpdateFolderRequest(StrictModel):
    """Rename a folder in Canva by updating its name. The folder is identified by its unique folder ID."""
    path: UpdateFolderRequestPath
    body: UpdateFolderRequestBody

# Operation: delete_folder
class DeleteFolderRequestPath(StrictModel):
    folder_id: str = Field(default=..., validation_alias="folderId", serialization_alias="folderId", description="The unique identifier of the folder to delete.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class DeleteFolderRequest(StrictModel):
    """Permanently deletes a folder by moving its contents to Trash. Content owned by the folder owner goes to Trash, while content owned by other users is moved to the top level of their projects."""
    path: DeleteFolderRequestPath

# Operation: list_folder_items
class ListFolderItemsRequestPath(StrictModel):
    folder_id: str = Field(default=..., validation_alias="folderId", serialization_alias="folderId", description="The unique identifier of the folder to list items from.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class ListFolderItemsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of folder items to return in the response. Defaults to 50 items.", json_schema_extra={'format': 'int32'})
    item_types: list[Literal["design", "folder", "image"]] | None = Field(default=None, description="Filter results to only include specified item types. Provide a comma-separated list to filter for multiple types. Available types are: design, folder, and image.")
    sort_by: Literal["created_ascending", "created_descending", "modified_ascending", "modified_descending", "title_ascending", "title_descending"] | None = Field(default=None, description="Sort the returned items by creation date, modification date, or title in ascending or descending order. Defaults to most recently modified first.")
    pin_status: Literal["any", "pinned"] | None = Field(default=None, description="Filter items by their pinned status. Use 'pinned' to show only pinned items, or 'any' to show all items regardless of pin status.")
class ListFolderItemsRequest(StrictModel):
    """Retrieves all items contained in a folder, including nested folders, designs (such as presentations and documents), and image assets. Use optional filters to narrow results by item type, sort order, or pinned status."""
    path: ListFolderItemsRequestPath
    query: ListFolderItemsRequestQuery | None = None

# Operation: move_item
class MoveFolderItemRequestBody(StrictModel):
    to_folder_id: str = Field(default=..., description="The ID of the destination folder. Use the special ID `root` to move the item to the top level of the user's projects.", min_length=1, max_length=50)
    item_id: str = Field(default=..., description="The ID of the item to move. Video assets are not supported.", min_length=1, max_length=50)
class MoveFolderItemRequest(StrictModel):
    """Moves an item (design, folder, or asset) to a different folder. Note: If the item exists in multiple folders, use the Canva UI to move it instead."""
    body: MoveFolderItemRequestBody

# Operation: create_folder
class CreateFolderRequestBody(StrictModel):
    name: str = Field(default=..., description="The name for the new folder. Must be between 1 and 255 characters.", min_length=1, max_length=255)
    parent_folder_id: str = Field(default=..., description="The ID of the parent folder where this folder will be created. Use `root` for top-level projects, `uploads` for the Uploads folder, or provide a specific folder ID.", min_length=1, max_length=50)
class CreateFolderRequest(StrictModel):
    """Creates a new folder in a user's Canva workspace at the specified location (top-level projects, Uploads folder, or within another folder). Returns the folder ID and metadata upon successful creation."""
    body: CreateFolderRequestBody

# Operation: start_design_resize_job
class CreateDesignResizeJobRequestBody(StrictModel):
    design_id: str = Field(default=..., description="The unique identifier of the design to be resized.")
    design_type: Annotated[PresetDesignTypeInput | CustomDesignTypeInput, Field(discriminator="type_")] = Field(default=..., description="The target design type for the resized design. Can be either a preset design type or a custom design with specified height and width dimensions.")
class CreateDesignResizeJobRequest(StrictModel):
    """Initiates an asynchronous job to create a resized copy of a design. The resized design is added to the user's root folder and can be sized using either a preset design type or custom dimensions."""
    body: CreateDesignResizeJobRequestBody

# Operation: get_resize_job
class GetDesignResizeJobRequestPath(StrictModel):
    job_id: str = Field(default=..., validation_alias="jobId", serialization_alias="jobId", description="The unique identifier of the design resize job to retrieve status for.", pattern='^[a-zA-Z0-9_-]{1,50}$')
class GetDesignResizeJobRequest(StrictModel):
    """Retrieves the status and result of an asynchronous design resize job. Use this to poll for job completion after initiating a resize operation, which will include the resized design metadata upon success."""
    path: GetDesignResizeJobRequestPath

# ============================================================================
# Component Models
# ============================================================================

class BooleanDataTableCell(PermissiveModel):
    """A boolean tabular data cell."""
    type_: Literal["boolean"] = Field(..., validation_alias="type", serialization_alias="type")
    value: bool | None = None

class CreateAssetUploadJobHeaderAssetUploadMetadata(PermissiveModel):
    """Metadata for the asset being uploaded."""
    name_base64: str = Field(..., description="The asset's name, encoded in Base64.\n\nThe maximum length of an asset name in Canva (unencoded) is 50 characters.\n\nBase64 encoding allows names containing emojis and other special\ncharacters to be sent using HTTP headers.\nFor example, \"My Awesome Upload 🚀\" Base64 encoded\nis `TXkgQXdlc29tZSBVcGxvYWQg8J+agA==`.", min_length=1)

class CreateDesignImportJobHeaderImportMetadata(PermissiveModel):
    """Metadata about the design that you include as a header parameter when importing a design."""
    title_base64: str = Field(..., description="The design's title, encoded in Base64.\n\nThe maximum length of a design title in Canva (unencoded) is 50 characters.\n\nBase64 encoding allows titles containing emojis and other special\ncharacters to be sent using HTTP headers.\nFor example, \"My Awesome Design 😍\" Base64 encoded\nis `TXkgQXdlc29tZSBEZXNpZ24g8J+YjQ==`.", min_length=1)
    mime_type: str | None = Field(None, description="The MIME type of the file being imported. If not provided, Canva attempts to automatically detect the type of the file.")

class CustomDesignTypeInput(PermissiveModel):
    """Provide the width and height to define a custom design type."""
    type_: Literal["custom"] = Field(..., validation_alias="type", serialization_alias="type")
    width: int = Field(..., description="The width of the design, in pixels.", ge=40, le=8000)
    height: int = Field(..., description="The height of the design, in pixels.", ge=40, le=8000)

class DatasetImageValue(PermissiveModel):
    """If the data field is an image field."""
    type_: Literal["image"] = Field(..., validation_alias="type", serialization_alias="type")
    asset_id: str = Field(..., description="`asset_id` of the image to insert into the template element.")

class DatasetTextValue(PermissiveModel):
    """If the data field is a text field."""
    type_: Literal["text"] = Field(..., validation_alias="type", serialization_alias="type")
    text: str = Field(..., description="Text to insert into the template element.")

class DateDataTableCell(PermissiveModel):
    """A date tabular data cell.

Specified as a Unix timestamp (in seconds since the Unix Epoch)."""
    type_: Literal["date"] = Field(..., validation_alias="type", serialization_alias="type")
    value: int | None = Field(None, json_schema_extra={'format': 'int64'})

class DesignCommentObjectInput(PermissiveModel):
    """If the comment is attached to a Canva Design."""
    type_: Literal["design"] = Field(..., validation_alias="type", serialization_alias="type")
    design_id: str = Field(..., description="The ID of the design you want to attach this comment to.")

class CommentObjectInput(RootModel[Annotated[
    DesignCommentObjectInput,
    Field(discriminator="type_")
]]):
    pass

class GifExportFormat(PermissiveModel):
    """Export the design as a GIF. Height or width (or both) may be specified, otherwise the file
will be exported at it's default size. Large designs will be scaled down, and aspect ratio
will always be maintained."""
    type_: Literal["gif"] = Field(..., validation_alias="type", serialization_alias="type")
    export_quality: Literal["regular", "pro"] | None = None
    height: int | None = Field(None, description="Specify the height in pixels of the exported image. Note the following behavior:\n\n- If no height or width is specified, the image is exported using the dimensions of the design.\n- If only one of height or width is specified, then the image is scaled to match that dimension, respecting the design's aspect ratio.\n- If both the height and width are specified, but the values don't match the design's aspect ratio, the export defaults to the larger dimension.", ge=40, le=25000, json_schema_extra={'format': 'int32'})
    width: int | None = Field(None, description="Specify the width in pixels of the exported image. Note the following behavior:\n\n- If no width or height is specified, the image is exported using the dimensions of the design.\n- If only one of width or height is specified, then the image is scaled to match that dimension, respecting the design's aspect ratio.\n- If both the width and height are specified, but the values don't match the design's aspect ratio, the export defaults to the larger dimension.", ge=40, le=25000, json_schema_extra={'format': 'int32'})
    pages: list[int] | None = Field(None, description="To specify which pages to export in a multi-page design, provide the page numbers as\nan array. The first page in a design is page `1`.\nIf `pages` isn't specified, all the pages are exported.")

class ImportErrorModel(PermissiveModel):
    """If the import fails, this object provides details about the error."""
    code: Literal["file_too_big", "import_failed"]
    message: str = Field(..., description="A human-readable description of what went wrong.")

class ImportStatus(PermissiveModel):
    """The import status of the asset."""
    state: Literal["failed", "in_progress", "success"]
    error: ImportErrorModel | None = None

class JpgExportFormat(PermissiveModel):
    """Export the design as a JPEG. Compression quality must be provided. Height or width (or both)
may be specified, otherwise the file will be exported at it's default size.

If the user is on the Canva Free plan, the export height and width for a fixed-dimension design can't be upscaled by more than a factor of `1.125`."""
    type_: Literal["jpg"] = Field(..., validation_alias="type", serialization_alias="type")
    export_quality: Literal["regular", "pro"] | None = None
    quality: int = Field(..., description="For the `jpg` type, the `quality` of the exported JPEG determines how compressed the exported file should be. A _low_ `quality` value will create a file with a smaller file size, but the resulting file will have pixelated artifacts when compared to a file created with a _high_ `quality` value.", ge=1, le=100)
    height: int | None = Field(None, description="Specify the height in pixels of the exported image. Note the following behavior:\n\n- If no height or width is specified, the image is exported using the dimensions of the design.\n- If only one of height or width is specified, then the image is scaled to match that dimension, respecting the design's aspect ratio.\n- If both the height and width are specified, but the values don't match the design's aspect ratio, the export defaults to the larger dimension.", ge=40, le=25000, json_schema_extra={'format': 'int32'})
    width: int | None = Field(None, description="Specify the width in pixels of the exported image. Note the following behavior:\n\n- If no width or height is specified, the image is exported using the dimensions of the design.\n- If only one of width or height is specified, then the image is scaled to match that dimension, respecting the design's aspect ratio.\n- If both the width and height are specified, but the values don't match the design's aspect ratio, the export defaults to the larger dimension.", ge=40, le=25000, json_schema_extra={'format': 'int32'})
    pages: list[int] | None = Field(None, description="To specify which pages to export in a multi-page design, provide the page numbers as\nan array. The first page in a design is page `1`.\nIf `pages` isn't specified, all the pages are exported.")

class Mp4ExportFormat(PermissiveModel):
    """Export the design as an MP4. You must specify the quality of the exported video."""
    type_: Literal["mp4"] = Field(..., validation_alias="type", serialization_alias="type")
    export_quality: Literal["regular", "pro"] | None = None
    quality: Literal["horizontal_480p", "horizontal_720p", "horizontal_1080p", "horizontal_4k", "vertical_480p", "vertical_720p", "vertical_1080p", "vertical_4k"]
    pages: list[int] | None = Field(None, description="To specify which pages to export in a multi-page design, provide the page numbers as\nan array. The first page in a design is page `1`.\nIf `pages` isn't specified, all the pages are exported.")

class NumberDataTableCell(PermissiveModel):
    """A number tabular data cell."""
    type_: Literal["number"] = Field(..., validation_alias="type", serialization_alias="type")
    value: float | None = Field(None, json_schema_extra={'format': 'double'})

class PdfExportFormat(PermissiveModel):
    """Export the design as a PDF. Providing a paper size is optional."""
    type_: Literal["pdf"] = Field(..., validation_alias="type", serialization_alias="type")
    export_quality: Literal["regular", "pro"] | None = None
    size: Literal["a4", "a3", "letter", "legal"] | None = None
    pages: list[int] | None = Field(None, description="To specify which pages to export in a multi-page design, provide the page numbers as\nan array. The first page in a design is page `1`.\nIf `pages` isn't specified, all the pages are exported.")

class PngExportFormat(PermissiveModel):
    """Export the design as a PNG. Height or width (or both) may be specified, otherwise
the file will be exported at it's default size. You may also specify whether to export the
file losslessly, and whether to export a multi-page design as a single image.

If the user is on the Canva Free plan, the export height and width for a fixed-dimension design can't be upscaled by more than a factor of `1.125`."""
    type_: Literal["png"] = Field(..., validation_alias="type", serialization_alias="type")
    export_quality: Literal["regular", "pro"] | None = None
    height: int | None = Field(None, description="Specify the height in pixels of the exported image. Note the following behavior:\n\n- If no height or width is specified, the image is exported using the dimensions of the design.\n- If only one of height or width is specified, then the image is scaled to match that dimension, respecting the design's aspect ratio.\n- If both the height and width are specified, but the values don't match the design's aspect ratio, the export defaults to the larger dimension.", ge=40, le=25000, json_schema_extra={'format': 'int32'})
    width: int | None = Field(None, description="Specify the width in pixels of the exported image. Note the following behavior:\n\n- If no width or height is specified, the image is exported using the dimensions of the design.\n- If only one of width or height is specified, then the image is scaled to match that dimension, respecting the design's aspect ratio.\n- If both the width and height are specified, but the values don't match the design's aspect ratio, the export defaults to the larger dimension.", ge=40, le=25000, json_schema_extra={'format': 'int32'})
    lossless: bool | None = Field(True, description="If set to `true` (default), the PNG is exported without compression.\n\nIf set to `false`, the PNG is compressed using a lossy compression algorithm.\n\nAVAILABILITY: Lossy PNG compression is only available to users on a Canva plan that has premium features, such as Canva Pro. If the user is on the Canva Free plan and this parameter is set to `false`, the export operation will fail.")
    transparent_background: bool | None = Field(False, description="If set to `true`, the PNG is exported with a transparent background.\n\nAVAILABILITY: This option is only available to users on a Canva plan that has premium features, such as Canva Pro. If the user is on the Canva Free plan and this parameter is set to `true`, the export operation will fail.")
    as_single_image: bool | None = Field(False, description="When `true`, multi-page designs are merged into a single image.\nWhen `false` (default), each page is exported as a separate image.")
    pages: list[int] | None = Field(None, description="To specify which pages to export in a multi-page design, provide the page numbers as\nan array. The first page in a design is page `1`.\nIf `pages` isn't specified, all the pages are exported.")

class PptxExportFormat(PermissiveModel):
    """Export the design as a PPTX."""
    type_: Literal["pptx"] = Field(..., validation_alias="type", serialization_alias="type")
    pages: list[int] | None = Field(None, description="To specify which pages to export in a multi-page design, provide the page numbers as\nan array. The first page in a design is page `1`.\nIf `pages` isn't specified, all the pages are exported.")

class ExportFormat(RootModel[Annotated[
    PdfExportFormat
    | JpgExportFormat
    | PngExportFormat
    | PptxExportFormat
    | GifExportFormat
    | Mp4ExportFormat,
    Field(discriminator="type_")
]]):
    pass

class PresetDesignTypeInput(PermissiveModel):
    """Provide the common design type."""
    type_: Literal["preset"] = Field(..., validation_alias="type", serialization_alias="type")
    name: Literal["doc", "whiteboard", "presentation"]

class DesignTypeInput(RootModel[Annotated[
    PresetDesignTypeInput
    | CustomDesignTypeInput,
    Field(discriminator="type_")
]]):
    pass

class StringDataTableCell(PermissiveModel):
    """A string tabular data cell."""
    type_: Literal["string"] = Field(..., validation_alias="type", serialization_alias="type")
    value: str | None = None

class DataTableCell(RootModel[Annotated[
    StringDataTableCell
    | NumberDataTableCell
    | BooleanDataTableCell
    | DateDataTableCell,
    Field(discriminator="type_")
]]):
    pass

class DataTableRow(PermissiveModel):
    """A single row of tabular data."""
    cells: list[DataTableCell] = Field(..., description="Cells of data in row.\n\nAll rows must have the same number of cells.", max_length=20)

class DataTable(PermissiveModel):
    """Tabular data, structured in rows of cells.

- The first row usually contains column headers.
- Each cell must have a data type configured.
- All rows must have the same number of cells.
- Maximum of 100 rows and 20 columns.

WARNING: Chart data fields are a [preview feature](https://www.canva.dev/docs/connect/#preview-apis). There might be unannounced breaking changes to this feature which won't produce a new API version."""
    rows: list[DataTableRow] = Field(..., description="Rows of data.\n\nThe first row usually contains column headers.", max_length=100)

class DatasetChartValue(PermissiveModel):
    """If the data field is a chart.

 WARNING: Chart data fields are a [preview feature](https://www.canva.dev/docs/connect/#preview-apis). There might be unannounced breaking changes to this feature which won't produce a new API version."""
    type_: Literal["chart"] = Field(..., validation_alias="type", serialization_alias="type")
    chart_data: DataTable

class DatasetValue(RootModel[Annotated[
    DatasetImageValue
    | DatasetTextValue
    | DatasetChartValue,
    Field(discriminator="type_")
]]):
    pass

class Team(PermissiveModel):
    """Metadata for the Canva Team, consisting of the Team ID,
display name, and whether it's an external Canva Team."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the Canva Team.")
    display_name: str = Field(..., description="The name of the Canva Team as shown in the Canva UI.")
    external: bool = Field(..., description="Is the user making the API call (the authenticated user) from the Canva Team shown?\n\n- When `true`, the user isn't in the Canva Team shown.\n- When `false`, the user is in the Canva Team shown.")

class TeamUserSummary(PermissiveModel):
    """Metadata for the user, consisting of the User ID and Team ID."""
    user_id: str = Field(..., description="The ID of the user.")
    team_id: str = Field(..., description="The ID of the user's Canva Team.")

class Thumbnail(PermissiveModel):
    """A thumbnail image representing the object."""
    width: int = Field(..., description="The width of the thumbnail image in pixels.")
    height: int = Field(..., description="The height of the thumbnail image in pixels.")
    url: str = Field(..., description="A URL for retrieving the thumbnail image.\nThis URL expires after 15 minutes. This URL includes a query string\nthat's required for retrieving the thumbnail.")

class Asset(PermissiveModel):
    """The asset object, which contains metadata about the asset."""
    type_: Literal["image", "video"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the asset.")
    name: str = Field(..., description="The name of the asset.")
    tags: list[str] = Field(..., description="The user-facing tags attached to the asset.\nUsers can add these tags to their uploaded assets, and they can search their uploaded\nassets in the Canva UI by searching for these tags. For information on how users use\ntags, see the\n[Canva Help Center page on asset tags](https://www.canva.com/help/add-edit-tags/).")
    import_status: ImportStatus | None = None
    created_at: int = Field(..., description="When the asset was added to Canva, as a Unix timestamp (in seconds since the Unix\nEpoch).", json_schema_extra={'format': 'int64'})
    updated_at: int = Field(..., description="When the asset was last updated in Canva, as a Unix timestamp (in seconds since the\nUnix Epoch).", json_schema_extra={'format': 'int64'})
    owner: TeamUserSummary
    thumbnail: Thumbnail | None = None

class User(PermissiveModel):
    """Metadata for the user, consisting of the User ID and display name."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the user.")
    display_name: str | None = Field(None, description="The name of the user as shown in the Canva UI.")


# Rebuild models to resolve forward references (required for circular refs)
Asset.model_rebuild()
BooleanDataTableCell.model_rebuild()
CommentObjectInput.model_rebuild()
CreateAssetUploadJobHeaderAssetUploadMetadata.model_rebuild()
CreateDesignImportJobHeaderImportMetadata.model_rebuild()
CustomDesignTypeInput.model_rebuild()
DatasetChartValue.model_rebuild()
DatasetImageValue.model_rebuild()
DatasetTextValue.model_rebuild()
DatasetValue.model_rebuild()
DataTable.model_rebuild()
DataTableCell.model_rebuild()
DataTableRow.model_rebuild()
DateDataTableCell.model_rebuild()
DesignCommentObjectInput.model_rebuild()
DesignTypeInput.model_rebuild()
ExportFormat.model_rebuild()
GifExportFormat.model_rebuild()
ImportErrorModel.model_rebuild()
ImportStatus.model_rebuild()
JpgExportFormat.model_rebuild()
Mp4ExportFormat.model_rebuild()
NumberDataTableCell.model_rebuild()
PdfExportFormat.model_rebuild()
PngExportFormat.model_rebuild()
PptxExportFormat.model_rebuild()
PresetDesignTypeInput.model_rebuild()
StringDataTableCell.model_rebuild()
Team.model_rebuild()
TeamUserSummary.model_rebuild()
Thumbnail.model_rebuild()
User.model_rebuild()

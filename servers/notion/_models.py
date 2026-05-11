"""
Notion MCP Server - Pydantic Models

Generated: 2026-05-11 19:56:55 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

__all__ = [
    "CompleteFileUploadRequest",
    "CreateACommentRequest",
    "CreateADatabaseRequest",
    "CreateDatabaseRequest",
    "CreateFileRequest",
    "CreateViewQueryRequest",
    "CreateViewRequest",
    "DeleteABlockRequest",
    "DeleteViewQueryRequest",
    "DeleteViewRequest",
    "GetBlockChildrenRequest",
    "GetSelfRequest",
    "GetUserRequest",
    "GetUsersRequest",
    "GetViewQueryResultsRequest",
    "ListCommentsRequest",
    "ListCustomEmojisRequest",
    "ListDataSourceTemplatesRequest",
    "ListFileUploadsRequest",
    "ListViewsRequest",
    "MovePageRequest",
    "PatchBlockChildrenRequest",
    "PatchPageRequest",
    "PostDatabaseQueryRequest",
    "PostPageRequest",
    "PostSearchRequest",
    "RetrieveABlockRequest",
    "RetrieveADataSourceRequest",
    "RetrieveAPagePropertyRequest",
    "RetrieveAPageRequest",
    "RetrieveAViewRequest",
    "RetrieveCommentRequest",
    "RetrieveDatabaseRequest",
    "RetrieveFileUploadRequest",
    "RetrievePageMarkdownRequest",
    "UpdateABlockRequest",
    "UpdateADataSourceRequest",
    "UpdateAViewRequest",
    "UpdateDatabaseRequest",
    "UpdatePageMarkdownRequest",
    "UploadFileRequest",
    "BlockObjectRequest",
    "BoardViewConfigRequest",
    "CalendarViewConfigRequest",
    "ChartViewConfigRequest",
    "ContentPositionSchema",
    "CreateACommentBody",
    "CreateDatabaseBodyParent",
    "CreateViewBodyPlacement",
    "CreateViewBodyPosition",
    "CustomEmojiPageIconRequest",
    "EmojiPageIconRequest",
    "ExternalPageCoverRequest",
    "ExternalPageIconRequest",
    "FileUploadPageCoverRequest",
    "FileUploadPageIconRequest",
    "FormViewConfigRequest",
    "GalleryViewConfigRequest",
    "IconPageIconRequest",
    "ListViewConfigRequest",
    "MapViewConfigRequest",
    "MovePageBodyParentV0",
    "MovePageBodyParentV1",
    "PagePositionSchema",
    "PatchPageBodyPropertiesValueV0",
    "PatchPageBodyPropertiesValueV1",
    "PatchPageBodyPropertiesValueV10",
    "PatchPageBodyPropertiesValueV11",
    "PatchPageBodyPropertiesValueV12",
    "PatchPageBodyPropertiesValueV13",
    "PatchPageBodyPropertiesValueV14",
    "PatchPageBodyPropertiesValueV15",
    "PatchPageBodyPropertiesValueV2",
    "PatchPageBodyPropertiesValueV3",
    "PatchPageBodyPropertiesValueV4",
    "PatchPageBodyPropertiesValueV5",
    "PatchPageBodyPropertiesValueV6",
    "PatchPageBodyPropertiesValueV7",
    "PatchPageBodyPropertiesValueV8",
    "PatchPageBodyPropertiesValueV9",
    "PatchPageBodyTemplate",
    "PostDatabaseQueryBodyFilterV0V0",
    "PostDatabaseQueryBodyFilterV0V1",
    "PostDatabaseQueryBodySortsItemV0",
    "PostDatabaseQueryBodySortsItemV1",
    "PostPageBodyParentV0",
    "PostPageBodyParentV1",
    "PostPageBodyParentV2",
    "PostPageBodyParentV3",
    "PostPageBodyPropertiesValueV0",
    "PostPageBodyPropertiesValueV1",
    "PostPageBodyPropertiesValueV10",
    "PostPageBodyPropertiesValueV11",
    "PostPageBodyPropertiesValueV12",
    "PostPageBodyPropertiesValueV13",
    "PostPageBodyPropertiesValueV14",
    "PostPageBodyPropertiesValueV15",
    "PostPageBodyPropertiesValueV2",
    "PostPageBodyPropertiesValueV3",
    "PostPageBodyPropertiesValueV4",
    "PostPageBodyPropertiesValueV5",
    "PostPageBodyPropertiesValueV6",
    "PostPageBodyPropertiesValueV7",
    "PostPageBodyPropertiesValueV8",
    "PostPageBodyPropertiesValueV9",
    "PostPageBodyTemplate",
    "PropertyConfigurationRequest",
    "PropertyFilter",
    "QuickFilterConditionRequest",
    "RichTextItemRequest",
    "TableViewConfigRequest",
    "TimelineViewConfigRequest",
    "TimestampCreatedTimeFilter",
    "TimestampLastEditedTimeFilter",
    "UpdateABlockBodyV0V0",
    "UpdateABlockBodyV0V1",
    "UpdateABlockBodyV0V10",
    "UpdateABlockBodyV0V11",
    "UpdateABlockBodyV0V12",
    "UpdateABlockBodyV0V13",
    "UpdateABlockBodyV0V14",
    "UpdateABlockBodyV0V15",
    "UpdateABlockBodyV0V16",
    "UpdateABlockBodyV0V17",
    "UpdateABlockBodyV0V18",
    "UpdateABlockBodyV0V19",
    "UpdateABlockBodyV0V2",
    "UpdateABlockBodyV0V20",
    "UpdateABlockBodyV0V21",
    "UpdateABlockBodyV0V22",
    "UpdateABlockBodyV0V23",
    "UpdateABlockBodyV0V24",
    "UpdateABlockBodyV0V25",
    "UpdateABlockBodyV0V26",
    "UpdateABlockBodyV0V27",
    "UpdateABlockBodyV0V28",
    "UpdateABlockBodyV0V29",
    "UpdateABlockBodyV0V3",
    "UpdateABlockBodyV0V4",
    "UpdateABlockBodyV0V5",
    "UpdateABlockBodyV0V6",
    "UpdateABlockBodyV0V7",
    "UpdateABlockBodyV0V8",
    "UpdateABlockBodyV0V9",
    "UpdateABlockBodyV1",
    "UpdateADataSourceBodyPropertiesValueV0",
    "UpdateADataSourceBodyPropertiesValueV1",
    "UpdateDatabaseBodyParent",
    "UpdatePageMarkdownBodyInsertContent",
    "UpdatePageMarkdownBodyReplaceContent",
    "UpdatePageMarkdownBodyReplaceContentRange",
    "UpdatePageMarkdownBodyUpdateContent",
    "ViewPropertySortRequest",
    "ViewSortRequest",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_self
class GetSelfRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11.")
class GetSelfRequest(StrictModel):
    """Retrieve the bot user associated with your API token. This returns information about the authenticated user making the request."""
    header: GetSelfRequestHeader

# Operation: get_user
class GetUserRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to retrieve.")
class GetUserRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11.")
class GetUserRequest(StrictModel):
    """Retrieve a specific user by their ID. Returns the user's profile information and details."""
    path: GetUserRequestPath
    header: GetUserRequestHeader

# Operation: list_users
class GetUsersRequestQuery(StrictModel):
    page_size: float | None = Field(default=None, description="Number of users to return per page for pagination. Controls the batch size of results in the response.")
class GetUsersRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="API version to use for this request. Must be set to the latest version 2026-03-11 to ensure compatibility with current API behavior.")
class GetUsersRequest(StrictModel):
    """Retrieve a paginated list of all users in the system. Use pagination parameters to control result size and navigate through user records."""
    query: GetUsersRequestQuery | None = None
    header: GetUsersRequestHeader

# Operation: create_page
class PostPageRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11.")
class PostPageRequestBody(StrictModel):
    parent: PostPageBodyParentV0 | PostPageBodyParentV1 | PostPageBodyParentV2 | PostPageBodyParentV3 | None = Field(default=None, description="The parent location where the page will be created, typically a database or another page.")
    properties: dict[str, PostPageBodyPropertiesValueV0 | PostPageBodyPropertiesValueV1 | PostPageBodyPropertiesValueV2 | PostPageBodyPropertiesValueV3 | PostPageBodyPropertiesValueV4 | PostPageBodyPropertiesValueV5 | PostPageBodyPropertiesValueV6 | PostPageBodyPropertiesValueV7 | PostPageBodyPropertiesValueV8 | PostPageBodyPropertiesValueV9 | PostPageBodyPropertiesValueV10 | PostPageBodyPropertiesValueV11 | PostPageBodyPropertiesValueV12 | PostPageBodyPropertiesValueV13 | PostPageBodyPropertiesValueV14 | PostPageBodyPropertiesValueV15] | None = Field(default=None, description="The page properties (title, custom fields, etc.) to set on the new page.")
    icon: FileUploadPageIconRequest | EmojiPageIconRequest | ExternalPageIconRequest | CustomEmojiPageIconRequest | IconPageIconRequest | None = Field(default=None, description="An optional icon to display for the page (emoji, file reference, or external URL).")
    cover: FileUploadPageCoverRequest | ExternalPageCoverRequest | None = Field(default=None, description="An optional cover image to display at the top of the page (file reference or external URL).")
    children: list[BlockObjectRequest] | None = Field(default=None, description="An optional array of child blocks to add to the page during creation. Maximum of 100 blocks allowed.", max_length=100)
    template: PostPageBodyTemplate | None = Field(default=None, description="An optional template configuration to apply to the page upon creation.")
    position: PagePositionSchema | None = Field(default=None, description="An optional position specification to control where the page appears relative to siblings (e.g., before/after another page).")
class PostPageRequest(StrictModel):
    """Creates a new page in Notion. Specify the parent location, page properties, and optional visual elements like icons and covers. You can also include child blocks and apply templates during creation."""
    header: PostPageRequestHeader
    body: PostPageRequestBody | None = None

# Operation: get_page
class RetrieveAPageRequestPath(StrictModel):
    page_id: str = Field(default=..., description="The unique identifier of the page to retrieve.")
class RetrieveAPageRequestQuery(StrictModel):
    filter_properties: list[str] | None = Field(default=None, description="Optional list of property IDs to include in the response. Only properties that exist on the page will be returned; up to 100 properties can be specified. Properties not in this list will be excluded from the response.", max_length=100)
class RetrieveAPageRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11.")
class RetrieveAPageRequest(StrictModel):
    """Retrieve a single page by its ID from Notion. Optionally filter the response to include only specified properties."""
    path: RetrieveAPageRequestPath
    query: RetrieveAPageRequestQuery | None = None
    header: RetrieveAPageRequestHeader

# Operation: update_page
class PatchPageRequestPath(StrictModel):
    page_id: str = Field(default=..., description="The unique identifier of the page to update.")
class PatchPageRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11.")
class PatchPageRequestBody(StrictModel):
    properties: dict[str, PatchPageBodyPropertiesValueV0 | PatchPageBodyPropertiesValueV1 | PatchPageBodyPropertiesValueV2 | PatchPageBodyPropertiesValueV3 | PatchPageBodyPropertiesValueV4 | PatchPageBodyPropertiesValueV5 | PatchPageBodyPropertiesValueV6 | PatchPageBodyPropertiesValueV7 | PatchPageBodyPropertiesValueV8 | PatchPageBodyPropertiesValueV9 | PatchPageBodyPropertiesValueV10 | PatchPageBodyPropertiesValueV11 | PatchPageBodyPropertiesValueV12 | PatchPageBodyPropertiesValueV13 | PatchPageBodyPropertiesValueV14 | PatchPageBodyPropertiesValueV15] | None = Field(default=None, description="Page properties to update, such as title and custom property values. Structure depends on the page's database schema.")
    icon: FileUploadPageIconRequest | EmojiPageIconRequest | ExternalPageIconRequest | CustomEmojiPageIconRequest | IconPageIconRequest | None = Field(default=None, description="The page's icon, which can be an emoji, external URL, or file reference.")
    cover: FileUploadPageCoverRequest | ExternalPageCoverRequest | None = Field(default=None, description="The page's cover image, which can be an external URL or file reference.")
    is_locked: bool | None = Field(default=None, description="Whether to lock the page from editing in the Notion app UI. If not provided, the current lock state remains unchanged.")
    template: PatchPageBodyTemplate | None = Field(default=None, description="A template object containing content to apply to the page. When combined with erase_content, the template content replaces existing content.")
    erase_content: bool | None = Field(default=None, description="Whether to erase all existing page content. When used with a template, the template content replaces the erased content. When used alone, simply clears the page.")
    in_trash: bool | None = Field(default=None, description="Whether to move the page to or restore it from trash.")
    is_archived: bool | None = Field(default=None, description="Whether to archive the page, hiding it from the workspace while preserving its content.")
class PatchPageRequest(StrictModel):
    """Update a Notion page's properties, appearance, content, and metadata. Supports modifying page title/properties, icon, cover image, lock status, archived state, and content via template replacement or erasure."""
    path: PatchPageRequestPath
    header: PatchPageRequestHeader
    body: PatchPageRequestBody | None = None

# Operation: move_page
class MovePageRequestPath(StrictModel):
    page_id: str = Field(default=..., description="The unique identifier of the page to move.")
class MovePageRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11.")
class MovePageRequestBody(StrictModel):
    parent: MovePageBodyParentV0 | MovePageBodyParentV1 = Field(default=..., description="The new parent location for the page. This specifies where the page will be moved to in the hierarchy.")
class MovePageRequest(StrictModel):
    """Move a page to a new parent location within Notion. The page will be relocated under the specified parent, updating its position in the page hierarchy."""
    path: MovePageRequestPath
    header: MovePageRequestHeader
    body: MovePageRequestBody

# Operation: get_page_property
class RetrieveAPagePropertyRequestPath(StrictModel):
    page_id: str = Field(default=..., description="The unique identifier of the Notion page containing the property.")
    property_id: str = Field(default=..., description="The unique identifier of the property to retrieve from the page.")
class RetrieveAPagePropertyRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="The maximum number of items to return in the response. Controls pagination size for the property results.")
class RetrieveAPagePropertyRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to 2026-03-11 or later for compatibility with current API features.")
class RetrieveAPagePropertyRequest(StrictModel):
    """Retrieve a specific property item from a Notion page. Use this to fetch individual property values associated with a page."""
    path: RetrieveAPagePropertyRequestPath
    query: RetrieveAPagePropertyRequestQuery | None = None
    header: RetrieveAPagePropertyRequestHeader

# Operation: get_page_markdown
class RetrievePageMarkdownRequestPath(StrictModel):
    page_id: str = Field(default=..., description="The unique identifier of the Notion page to retrieve.")
class RetrievePageMarkdownRequestQuery(StrictModel):
    include_transcript: bool | None = Field(default=None, description="Whether to include full meeting note transcripts in the markdown output. When false (default), meeting notes are represented as placeholders with URLs instead of full transcript text.")
class RetrievePageMarkdownRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11.")
class RetrievePageMarkdownRequest(StrictModel):
    """Retrieve a Notion page in markdown format. Optionally include meeting note transcripts or use placeholder URLs instead."""
    path: RetrievePageMarkdownRequestPath
    query: RetrievePageMarkdownRequestQuery | None = None
    header: RetrievePageMarkdownRequestHeader

# Operation: update_page_markdown
class UpdatePageMarkdownRequestPath(StrictModel):
    page_id: str = Field(default=..., description="The unique identifier of the page to update.")
class UpdatePageMarkdownRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version: 2026-03-11.")
class UpdatePageMarkdownRequestBody(StrictModel):
    type_: Literal["insert_content"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The operation type. Must always be set to 'insert_content' to specify the content modification mode.")
    insert_content: UpdatePageMarkdownBodyInsertContent | None = Field(default=None, description="Configuration for inserting new markdown content into the page at a specified location.")
    replace_content_range: UpdatePageMarkdownBodyReplaceContentRange | None = Field(default=None, description="Configuration for replacing a specific range of content within the page using markdown.")
    update_content: UpdatePageMarkdownBodyUpdateContent | None = Field(default=None, description="Configuration for updating content using search-and-replace operations to find and modify specific text.")
    replace_content: UpdatePageMarkdownBodyReplaceContent | None = Field(default=None, description="Configuration for replacing the entire page content with new markdown, removing all existing content.")
class UpdatePageMarkdownRequest(StrictModel):
    """Update a Notion page's content using markdown. Supports inserting new content, replacing specific ranges, performing search-and-replace operations, or replacing the entire page content."""
    path: UpdatePageMarkdownRequestPath
    header: UpdatePageMarkdownRequestHeader
    body: UpdatePageMarkdownRequestBody

# Operation: get_block
class RetrieveABlockRequestPath(StrictModel):
    block_id: str = Field(default=..., description="The unique identifier of the block to retrieve.")
class RetrieveABlockRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to 2026-03-11 (the latest version).")
class RetrieveABlockRequest(StrictModel):
    """Retrieve a specific block by its ID from Notion. Returns the block's properties and content."""
    path: RetrieveABlockRequestPath
    header: RetrieveABlockRequestHeader

# Operation: update_block
class UpdateABlockRequestPath(StrictModel):
    block_id: str = Field(default=..., description="The unique identifier of the block to update.")
class UpdateABlockRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11.")
class UpdateABlockRequestBody(StrictModel):
    body: UpdateABlockBodyV0V0 | UpdateABlockBodyV0V1 | UpdateABlockBodyV0V2 | UpdateABlockBodyV0V3 | UpdateABlockBodyV0V4 | UpdateABlockBodyV0V5 | UpdateABlockBodyV0V6 | UpdateABlockBodyV0V7 | UpdateABlockBodyV0V8 | UpdateABlockBodyV0V9 | UpdateABlockBodyV0V10 | UpdateABlockBodyV0V11 | UpdateABlockBodyV0V12 | UpdateABlockBodyV0V13 | UpdateABlockBodyV0V14 | UpdateABlockBodyV0V15 | UpdateABlockBodyV0V16 | UpdateABlockBodyV0V17 | UpdateABlockBodyV0V18 | UpdateABlockBodyV0V19 | UpdateABlockBodyV0V20 | UpdateABlockBodyV0V21 | UpdateABlockBodyV0V22 | UpdateABlockBodyV0V23 | UpdateABlockBodyV0V24 | UpdateABlockBodyV0V25 | UpdateABlockBodyV0V26 | UpdateABlockBodyV0V27 | UpdateABlockBodyV0V28 | UpdateABlockBodyV0V29 | UpdateABlockBodyV1 = Field(default=..., description="The block update payload containing the properties to modify.")
class UpdateABlockRequest(StrictModel):
    """Update the properties of an existing block in Notion. Modify block content, formatting, or other attributes using the provided block ID."""
    path: UpdateABlockRequestPath
    header: UpdateABlockRequestHeader
    body: UpdateABlockRequestBody

# Operation: delete_block
class DeleteABlockRequestPath(StrictModel):
    block_id: str = Field(default=..., description="The unique identifier of the block to delete.")
class DeleteABlockRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11.")
class DeleteABlockRequest(StrictModel):
    """Permanently delete a block from a Notion workspace. This action cannot be undone."""
    path: DeleteABlockRequestPath
    header: DeleteABlockRequestHeader

# Operation: list_block_children
class GetBlockChildrenRequestPath(StrictModel):
    block_id: str = Field(default=..., description="The unique identifier of the parent block whose children you want to retrieve.")
class GetBlockChildrenRequestQuery(StrictModel):
    page_size: float | None = Field(default=None, description="The maximum number of child blocks to return in a single response. Use pagination to retrieve additional results if needed.")
class GetBlockChildrenRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to 2026-03-11 or later for compatibility with current API features.")
class GetBlockChildrenRequest(StrictModel):
    """Retrieve all child blocks contained within a specified parent block. Use this to navigate the hierarchical structure of Notion blocks and access nested content."""
    path: GetBlockChildrenRequestPath
    query: GetBlockChildrenRequestQuery | None = None
    header: GetBlockChildrenRequestHeader

# Operation: append_block_children
class PatchBlockChildrenRequestPath(StrictModel):
    block_id: str = Field(default=..., description="The unique identifier of the parent block to which children will be appended.")
class PatchBlockChildrenRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11.")
class PatchBlockChildrenRequestBody(StrictModel):
    children: list[BlockObjectRequest] = Field(default=..., description="An array of child block objects to append. Maximum of 100 blocks per request. Order in the array determines the sequence of appended blocks.", max_length=100)
    position: ContentPositionSchema | None = Field(default=None, description="Optional positioning configuration that specifies where the child blocks should be inserted relative to existing children.")
class PatchBlockChildrenRequest(StrictModel):
    """Append child blocks to a parent block. Allows adding up to 100 child blocks in a single request, with optional positioning control."""
    path: PatchBlockChildrenRequestPath
    header: PatchBlockChildrenRequestHeader
    body: PatchBlockChildrenRequestBody

# Operation: get_data_source
class RetrieveADataSourceRequestPath(StrictModel):
    data_source_id: str = Field(default=..., description="The unique identifier of the data source to retrieve.")
class RetrieveADataSourceRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11.")
class RetrieveADataSourceRequest(StrictModel):
    """Retrieve a specific data source by its ID. Returns the complete configuration and metadata for the requested data source."""
    path: RetrieveADataSourceRequestPath
    header: RetrieveADataSourceRequestHeader

# Operation: update_data_source
class UpdateADataSourceRequestPath(StrictModel):
    data_source_id: str = Field(default=..., description="The unique identifier of the data source to update.")
class UpdateADataSourceRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11.")
class UpdateADataSourceRequestBodyParent(StrictModel):
    database_id: str = Field(default=..., validation_alias="database_id", serialization_alias="database_id", description="The unique identifier of the parent database containing this data source. Accepts the ID with or without dashes (e.g., 195de9221179449fab8075a27c979105).")
class UpdateADataSourceRequestBody(StrictModel):
    title: list[RichTextItemRequest] | None = Field(default=None, description="The display title of the data source as it appears in Notion. Maximum length is 100 characters.", max_length=100)
    icon: FileUploadPageIconRequest | EmojiPageIconRequest | ExternalPageIconRequest | CustomEmojiPageIconRequest | IconPageIconRequest | None = Field(default=None, description="The icon to display for the data source page.")
    properties: dict[str, UpdateADataSourceBodyPropertiesValueV0 | UpdateADataSourceBodyPropertiesValueV1] | None = Field(default=None, description="The property schema configuration for the data source. Provide an object where keys are property names or IDs and values are property configuration objects. Set a property to null to remove it.")
    in_trash: bool | None = Field(default=None, description="Whether to move the data source to or from the trash. If not provided, the trash status remains unchanged.")
    parent: UpdateADataSourceRequestBodyParent
class UpdateADataSourceRequest(StrictModel):
    """Update a data source in Notion, including its title, icon, properties, and trash status. Use the database_id to specify the parent database containing this data source."""
    path: UpdateADataSourceRequestPath
    header: UpdateADataSourceRequestHeader
    body: UpdateADataSourceRequestBody

# Operation: query_data_source
class PostDatabaseQueryRequestPath(StrictModel):
    data_source_id: str = Field(default=..., description="The unique identifier of the data source to query.")
class PostDatabaseQueryRequestQuery(StrictModel):
    filter_properties: list[str] | None = Field(default=None, description="An array of properties to filter results by. Order and format depend on the data source schema.")
class PostDatabaseQueryRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version: 2026-03-11.")
class PostDatabaseQueryRequestBody(StrictModel):
    sorts: list[PostDatabaseQueryBodySortsItemV0 | PostDatabaseQueryBodySortsItemV1] | None = Field(default=None, description="An array of sort specifications to order results. Order of array elements determines sort priority.")
    filter_: PostDatabaseQueryBodyFilterV0V0 | PostDatabaseQueryBodyFilterV0V1 | PropertyFilter | TimestampCreatedTimeFilter | TimestampLastEditedTimeFilter | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="A filter object to narrow results based on data source properties and values.")
    page_size: float | None = Field(default=None, description="The maximum number of results to return per request. Used for pagination control.")
    in_trash: bool | None = Field(default=None, description="If true, include only items in the trash. If false or omitted, exclude trashed items.")
    result_type: Literal["page", "data_source"] | None = Field(default=None, description="Optionally restrict results to a specific type: 'page' for pages only, or 'data_source' for data sources only. Defaults to returning both types (wiki databases only).")
class PostDatabaseQueryRequest(StrictModel):
    """Execute a query against a data source to retrieve filtered, sorted results. Supports pagination and optional filtering by result type (pages or data sources)."""
    path: PostDatabaseQueryRequestPath
    query: PostDatabaseQueryRequestQuery | None = None
    header: PostDatabaseQueryRequestHeader
    body: PostDatabaseQueryRequestBody | None = None

# Operation: create_data_source
class CreateADatabaseRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11.")
class CreateADatabaseRequestBodyParent(StrictModel):
    database_id: str = Field(default=..., validation_alias="database_id", serialization_alias="database_id", description="The unique identifier of the parent Notion database where the data source will be created. Accepts the ID with or without dashes (e.g., 195de9221179449fab8075a27c979105).")
class CreateADatabaseRequestBody(StrictModel):
    properties: dict[str, PropertyConfigurationRequest] = Field(default=..., description="The property schema object that defines the structure and types of properties for this data source.")
    title: list[RichTextItemRequest] | None = Field(default=None, description="The display name for the data source as it will appear in Notion. Limited to a maximum of 100 characters.", max_length=100)
    icon: FileUploadPageIconRequest | EmojiPageIconRequest | ExternalPageIconRequest | CustomEmojiPageIconRequest | IconPageIconRequest | None = Field(default=None, description="An icon to visually represent the data source in the Notion interface.")
    parent: CreateADatabaseRequestBodyParent
class CreateADatabaseRequest(StrictModel):
    """Create a new data source within a Notion database by defining its property schema. This establishes the structure and metadata for how data will be organized in the specified parent database."""
    header: CreateADatabaseRequestHeader
    body: CreateADatabaseRequestBody

# Operation: list_data_source_templates
class ListDataSourceTemplatesRequestPath(StrictModel):
    data_source_id: str = Field(default=..., description="The unique identifier of the data source containing the templates to list.")
class ListDataSourceTemplatesRequestQuery(StrictModel):
    name: str | None = Field(default=None, description="Filter templates by name using case-insensitive substring matching. Only templates whose names contain this value will be returned.")
    page_size: int | None = Field(default=None, description="The maximum number of templates to return in the response. Must be between 1 and 100 items.", ge=1, le=100)
class ListDataSourceTemplatesRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Currently supports version 2026-03-11.")
class ListDataSourceTemplatesRequest(StrictModel):
    """Retrieve a paginated list of templates available within a specific data source, with optional filtering by name."""
    path: ListDataSourceTemplatesRequestPath
    query: ListDataSourceTemplatesRequestQuery | None = None
    header: ListDataSourceTemplatesRequestHeader

# Operation: get_database
class RetrieveDatabaseRequestPath(StrictModel):
    database_id: str = Field(default=..., description="The unique identifier of the database to retrieve.")
class RetrieveDatabaseRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11.")
class RetrieveDatabaseRequest(StrictModel):
    """Retrieve detailed information about a specific database by its ID. Returns the database's properties, configuration, and metadata."""
    path: RetrieveDatabaseRequestPath
    header: RetrieveDatabaseRequestHeader

# Operation: update_database
class UpdateDatabaseRequestPath(StrictModel):
    database_id: str = Field(default=..., description="The unique identifier of the database to update.")
class UpdateDatabaseRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11.")
class UpdateDatabaseRequestBody(StrictModel):
    parent: UpdateDatabaseBodyParent | None = Field(default=None, description="The parent page or workspace to move the database to. If omitted, the database location remains unchanged.")
    title: list[RichTextItemRequest] | None = Field(default=None, description="The new title for the database. Must not exceed 100 characters. If omitted, the current title is preserved.", max_length=100)
    description: list[RichTextItemRequest] | None = Field(default=None, description="The new description for the database. Must not exceed 100 characters. If omitted, the current description is preserved.", max_length=100)
    is_inline: bool | None = Field(default=None, description="Whether the database should be displayed inline within its parent page. If omitted, the current inline status is preserved.")
    icon: FileUploadPageIconRequest | EmojiPageIconRequest | ExternalPageIconRequest | CustomEmojiPageIconRequest | IconPageIconRequest | None = Field(default=None, description="The new icon for the database. If omitted, the current icon is preserved.")
    cover: FileUploadPageCoverRequest | ExternalPageCoverRequest | None = Field(default=None, description="The new cover image for the database. If omitted, the current cover is preserved.")
    in_trash: bool | None = Field(default=None, description="Whether to move the database to trash (true) or restore it from trash (false). If omitted, the current trash status is preserved.")
    is_locked: bool | None = Field(default=None, description="Whether to lock the database from editing in the Notion app UI. If omitted, the current lock state is preserved.")
class UpdateDatabaseRequest(StrictModel):
    """Update properties of an existing database in Notion, including its title, description, icon, cover, parent location, inline display status, trash status, and lock state. Only provided fields will be updated; omitted fields remain unchanged."""
    path: UpdateDatabaseRequestPath
    header: UpdateDatabaseRequestHeader
    body: UpdateDatabaseRequestBody | None = None

# Operation: create_database
class CreateDatabaseRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version 2026-03-11.")
class CreateDatabaseRequestBodyInitialDataSource(StrictModel):
    properties: dict[str, PropertyConfigurationRequest] | None = Field(default=None, validation_alias="properties", serialization_alias="properties", description="The property schema defining the initial columns and data structure for the database. Use this to pre-configure database fields when creating the database.")
class CreateDatabaseRequestBody(StrictModel):
    parent: CreateDatabaseBodyParent = Field(default=..., description="The parent page or workspace where the database will be created. This determines the location and context of the new database.")
    title: list[RichTextItemRequest] | None = Field(default=None, description="The title of the database. Limited to 100 characters maximum.", max_length=100)
    description: list[RichTextItemRequest] | None = Field(default=None, description="A description of the database's purpose or contents. Limited to 100 characters maximum.", max_length=100)
    is_inline: bool | None = Field(default=None, description="Whether the database should be displayed inline within the parent page rather than as a separate entity. Defaults to false.")
    icon: FileUploadPageIconRequest | EmojiPageIconRequest | ExternalPageIconRequest | CustomEmojiPageIconRequest | IconPageIconRequest | None = Field(default=None, description="An icon to visually represent the database in the Notion interface.")
    cover: FileUploadPageCoverRequest | ExternalPageCoverRequest | None = Field(default=None, description="A cover image displayed at the top of the database page.")
    initial_data_source: CreateDatabaseRequestBodyInitialDataSource | None = None
class CreateDatabaseRequest(StrictModel):
    """Creates a new database in Notion within a specified parent page or workspace. Optionally configure the database with a title, description, properties schema, icon, and cover image."""
    header: CreateDatabaseRequestHeader
    body: CreateDatabaseRequestBody

# Operation: search_pages_by_property
class PostSearchRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11.")
class PostSearchRequestBodySort(StrictModel):
    timestamp: Literal["last_edited_time"] = Field(default=..., validation_alias="timestamp", serialization_alias="timestamp", description="The property to sort results by. Currently supports sorting by last_edited_time.")
    direction: Literal["ascending", "descending"] = Field(default=..., validation_alias="direction", serialization_alias="direction", description="The sort direction for results: ascending (oldest first) or descending (newest first).")
class PostSearchRequestBodyFilter(StrictModel):
    property_: Literal["object"] = Field(default=..., validation_alias="property", serialization_alias="property", description="The type of object to search within. Currently limited to searching within pages.")
    value: Literal["page", "data_source"] = Field(default=..., validation_alias="value", serialization_alias="value", description="The type of result to return: page (for Notion pages) or data_source (for connected data sources).")
class PostSearchRequestBody(StrictModel):
    query: str | None = Field(default=None, description="The search query text to filter pages by title or content. Leave empty to retrieve all results without text filtering.")
    page_size: float | None = Field(default=None, description="The maximum number of results to return per request. Use for pagination control.")
    sort: PostSearchRequestBodySort
    filter_: PostSearchRequestBodyFilter = Field(default=..., validation_alias="filter", serialization_alias="filter")
class PostSearchRequest(StrictModel):
    """Search for pages in Notion by filtering on a specific property value, with results sorted by last edited time in your preferred direction."""
    header: PostSearchRequestHeader
    body: PostSearchRequestBody

# Operation: list_comments
class ListCommentsRequestQuery(StrictModel):
    block_id: str = Field(default=..., description="The unique identifier of the block for which to retrieve comments.")
    page_size: int | None = Field(default=None, description="The maximum number of comments to return in the response. Must be between 1 and 100 items.", ge=1, le=100)
class ListCommentsRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11.")
class ListCommentsRequest(StrictModel):
    """Retrieve a paginated list of comments for a specific block in Notion. Use pagination parameters to control the number of results returned."""
    query: ListCommentsRequestQuery
    header: ListCommentsRequestHeader

# Operation: create_comment
class CreateACommentRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to `2026-03-11`, which is the latest supported version.")
class CreateACommentRequestBody(StrictModel):
    body: CreateACommentBody = Field(default=..., description="The request body containing the comment data to be created, including content and any required metadata fields.")
class CreateACommentRequest(StrictModel):
    """Creates a new comment in Notion. The request body should contain the comment content and metadata required by the Notion API."""
    header: CreateACommentRequestHeader
    body: CreateACommentRequestBody

# Operation: get_comment
class RetrieveCommentRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to retrieve.")
class RetrieveCommentRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version 2026-03-11.")
class RetrieveCommentRequest(StrictModel):
    """Retrieve a specific comment by its ID from the Notion API. Returns the full comment object with all associated metadata."""
    path: RetrieveCommentRequestPath
    header: RetrieveCommentRequestHeader

# Operation: list_file_uploads
class ListFileUploadsRequestQuery(StrictModel):
    status: Literal["pending", "uploaded", "expired", "failed"] | None = Field(default=None, description="Filter results to only include file uploads with a specific status: pending (awaiting processing), uploaded (successfully completed), expired (no longer available), or failed (encountered an error).")
    page_size: int | None = Field(default=None, description="Number of file uploads to return per page, between 1 and 100 items. Use this to control pagination size for large result sets.", ge=1, le=100)
class ListFileUploadsRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="API version to use for this request. Must be set to the latest version: 2026-03-11.")
class ListFileUploadsRequest(StrictModel):
    """Retrieve a paginated list of file uploads with optional filtering by status. Use this to monitor the progress and state of files being uploaded to the system."""
    query: ListFileUploadsRequestQuery | None = None
    header: ListFileUploadsRequestHeader

# Operation: create_file_upload
class CreateFileRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to `2026-03-11` or later.")
class CreateFileRequestBody(StrictModel):
    mode: Literal["single_part", "multi_part", "external_url"] | None = Field(default=None, description="Upload mode: `single_part` for files under 20MB (default), `multi_part` for larger files, or `external_url` to import from a public HTTPS URL.")
    filename: str | None = Field(default=None, description="The filename for the uploaded file, including file extension. Required when using `multi_part` mode; optional otherwise to override the original filename.", examples=['business_summary.pdf'])
    content_type: str | None = Field(default=None, description="MIME type of the file (e.g., `application/pdf`, `image/png`). Recommended for multi-part uploads and must match both the file being sent and the filename extension if provided.", examples=['application/pdf'])
    number_of_parts: int | None = Field(default=None, description="For multi-part uploads, specify the total number of parts you will upload. Must be between 1 and 10,000 and match the final part number sent.", ge=1, le=10000)
    external_url: str | None = Field(default=None, description="When using `external_url` mode, provide the HTTPS URL of a publicly accessible file to import into your workspace.")
class CreateFileRequest(StrictModel):
    """Initiate a file upload to Notion, supporting single-part uploads for files under 20MB, multi-part uploads for larger files, or external URL imports for publicly hosted files."""
    header: CreateFileRequestHeader
    body: CreateFileRequestBody | None = None

# Operation: send_file_upload
class UploadFileRequestPath(StrictModel):
    file_upload_id: str = Field(default=..., description="The unique identifier for the file upload session to which the file contents are being sent.")
class UploadFileRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be `2026-03-11` or later.")
class UploadFileRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="Base64-encoded file content for upload. The raw binary file contents to upload.", json_schema_extra={'format': 'byte'})
    part_number: str | None = Field(default=None, description="The current part number when uploading files in multiple parts (required for files larger than 20MB). Must be an integer between 1 and 1,000.")
class UploadFileRequest(StrictModel):
    """Upload file contents to a file upload session, supporting multipart uploads for files larger than 20MB."""
    path: UploadFileRequestPath
    header: UploadFileRequestHeader
    body: UploadFileRequestBody

# Operation: complete_file_upload
class CompleteFileUploadRequestPath(StrictModel):
    file_upload_id: str = Field(default=..., description="The unique identifier of the file upload session to complete.")
class CompleteFileUploadRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to `2026-03-11` or later for compatibility with current API features.")
class CompleteFileUploadRequest(StrictModel):
    """Finalize a multi-part file upload by marking it as complete. This operation signals that all file chunks have been uploaded and the file is ready for processing."""
    path: CompleteFileUploadRequestPath
    header: CompleteFileUploadRequestHeader

# Operation: get_file_upload
class RetrieveFileUploadRequestPath(StrictModel):
    file_upload_id: str = Field(default=..., description="The unique identifier of the file upload to retrieve.")
class RetrieveFileUploadRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to `2026-03-11` for the latest version.")
class RetrieveFileUploadRequest(StrictModel):
    """Retrieve details about a specific file upload by its ID. Use this to check the status and metadata of a previously initiated file upload."""
    path: RetrieveFileUploadRequestPath
    header: RetrieveFileUploadRequestHeader

# Operation: list_custom_emojis
class ListCustomEmojisRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Maximum number of custom emojis to return in the response, between 1 and 100 items.", ge=1, le=100)
    name: str | None = Field(default=None, description="Filter results to a custom emoji with an exact name match. Useful for looking up a specific emoji's ID by name.")
class ListCustomEmojisRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version: 2026-03-11.")
class ListCustomEmojisRequest(StrictModel):
    """Retrieve a list of custom emojis from your Notion workspace. Optionally filter by exact name match to resolve a specific emoji to its ID."""
    query: ListCustomEmojisRequestQuery | None = None
    header: ListCustomEmojisRequestHeader

# Operation: list_views
class ListViewsRequestQuery(StrictModel):
    database_id: str | None = Field(default=None, description="Filter results to views belonging to a specific database. Omit to include views from all databases.")
    data_source_id: str | None = Field(default=None, description="Filter results to views associated with a specific data source. Omit to include views from all data sources.")
    page_size: int | None = Field(default=None, description="Number of views to return per page. Must be between 1 and 100 items. Defaults to a server-determined limit if not specified.", ge=1, le=100)
class ListViewsRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="API version to use for this request. Must be set to the latest version (2026-03-11) to ensure compatibility with current features.")
class ListViewsRequest(StrictModel):
    """Retrieve a paginated list of views, optionally filtered by database or data source. Use this to discover available views in your workspace."""
    query: ListViewsRequestQuery | None = None
    header: ListViewsRequestHeader

# Operation: create_view
class CreateViewRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be the latest version 2026-03-11.")
class CreateViewRequestBodyCreateDatabaseParent(StrictModel):
    type_: Literal["page_id"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The parent container type for the new database. Must be 'page_id' when creating a database.")
    page_id: str = Field(default=..., validation_alias="page_id", serialization_alias="page_id", description="The ID of the page where the new database should be created. Required when using create_database.")
class CreateViewRequestBodyCreateDatabasePosition(StrictModel):
    type_: Literal["after_block"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The positioning strategy for the new database. Use 'after_block' to place it after a specified block in the page.")
    block_id: str = Field(default=..., validation_alias="block_id", serialization_alias="block_id", description="The ID of an existing block in the page after which the new database will be positioned. Required when using create_database.")
class CreateViewRequestBodyCreateDatabase(StrictModel):
    parent: CreateViewRequestBodyCreateDatabaseParent
    position: CreateViewRequestBodyCreateDatabasePosition
class CreateViewRequestBody(StrictModel):
    data_source_id: str = Field(default=..., description="The ID of the data source (database or view) that this view should be scoped to.")
    name: str = Field(default=..., description="The display name for the view.")
    type_: Literal["table", "board", "list", "calendar", "timeline", "gallery", "form", "chart", "map", "dashboard"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The view type to create: table, board, list, calendar, timeline, gallery, form, chart, map, or dashboard.")
    database_id: str | None = Field(default=None, description="The ID of an existing database to create this view in. Cannot be used together with view_id or create_database.")
    view_id: str | None = Field(default=None, description="The ID of a dashboard view to add this view to as a widget. Cannot be used together with database_id or create_database.")
    filter_: dict[str, Any] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="A filter condition to apply to the view using the same format as data source query filters.")
    sorts: list[ViewSortRequest] | None = Field(default=None, description="An ordered array of sort conditions to apply to the view using the same format as data source query sorts. Maximum 100 sorts allowed.", max_length=100)
    quick_filters: dict[str, QuickFilterConditionRequest] | None = Field(default=None, description="Quick filter conditions to pin in the view's filter bar. Keys are property names or IDs; values are filter conditions that appear as clickable pills independent of the advanced filter.")
    configuration: TableViewConfigRequest | BoardViewConfigRequest | CalendarViewConfigRequest | TimelineViewConfigRequest | GalleryViewConfigRequest | ListViewConfigRequest | MapViewConfigRequest | FormViewConfigRequest | ChartViewConfigRequest | None = Field(default=None, description="View-specific presentation configuration. The configuration type must match the specified view type.")
    position: CreateViewBodyPosition | None = Field(default=None, description="The position where this view should appear in the database's view tab bar. Only applicable when database_id is provided. Defaults to appending at the end.")
    placement: CreateViewBodyPlacement | None = Field(default=None, description="The placement location for this widget within a dashboard view. Only applicable when view_id is provided. Defaults to creating a new row at the end.")
    create_database: CreateViewRequestBodyCreateDatabase
class CreateViewRequest(StrictModel):
    """Create a new view within a database, dashboard, or as a new database on a page. Views can be tables, boards, lists, calendars, timelines, galleries, forms, charts, maps, or dashboards with optional filtering, sorting, and quick filters."""
    header: CreateViewRequestHeader
    body: CreateViewRequestBody

# Operation: get_view
class RetrieveAViewRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the view to retrieve.")
class RetrieveAViewRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version 2026-03-11.")
class RetrieveAViewRequest(StrictModel):
    """Retrieve a specific view by its ID from Notion. Returns the view's configuration and metadata."""
    path: RetrieveAViewRequestPath
    header: RetrieveAViewRequestHeader

# Operation: update_view
class UpdateAViewRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the view to update.")
class UpdateAViewRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version: 2026-03-11.")
class UpdateAViewRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new display name for the view.")
    filter_: dict[str, Any] | None = Field(default=None, validation_alias="filter", serialization_alias="filter", description="A filter condition to apply to the view using the same format as data source query filters. Pass null to remove any existing filter.")
    sorts: list[ViewPropertySortRequest] | None = Field(default=None, description="An ordered list of property-based sorts to apply to the view (up to 100 sorts). Pass null to clear all sorts.", max_length=100)
    quick_filters: dict[str, QuickFilterConditionRequest] | None = Field(default=None, description="Quick filter definitions for the view's filter bar, keyed by property name or ID. Set a key to a filter condition to add or update that quick filter, set it to null to remove it, or pass null for the entire field to clear all quick filters. Unspecified quick filters are preserved.")
    configuration: TableViewConfigRequest | BoardViewConfigRequest | CalendarViewConfigRequest | TimelineViewConfigRequest | GalleryViewConfigRequest | ListViewConfigRequest | MapViewConfigRequest | FormViewConfigRequest | ChartViewConfigRequest | None = Field(default=None, description="View presentation configuration object. The type field must match the view's type. Individual fields within the configuration can be set to null to clear them.")
class UpdateAViewRequest(StrictModel):
    """Update a view's configuration, including its name, filters, sorts, quick filters, and presentation settings. Changes are applied to the specified view."""
    path: UpdateAViewRequestPath
    header: UpdateAViewRequestHeader
    body: UpdateAViewRequestBody | None = None

# Operation: delete_view
class DeleteViewRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the view to delete.")
class DeleteViewRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to the latest version 2026-03-11.")
class DeleteViewRequest(StrictModel):
    """Permanently delete a view by its ID. This operation removes the view and cannot be undone."""
    path: DeleteViewRequestPath
    header: DeleteViewRequestHeader

# Operation: create_view_query
class CreateViewQueryRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the view where the query will be created.")
class CreateViewQueryRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Currently supports version 2026-03-11.")
class CreateViewQueryRequestBody(StrictModel):
    page_size: int | None = Field(default=None, description="The maximum number of results to return per page, between 1 and 100 items.", ge=1, le=100)
class CreateViewQueryRequest(StrictModel):
    """Create a new query within a Notion view to retrieve filtered or sorted results. Specify pagination preferences to control the number of results returned per request."""
    path: CreateViewQueryRequestPath
    header: CreateViewQueryRequestHeader
    body: CreateViewQueryRequestBody | None = None

# Operation: get_view_query_results
class GetViewQueryResultsRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the Notion view containing the query.")
    query_id: str = Field(default=..., description="The unique identifier of the query whose results should be retrieved.")
class GetViewQueryResultsRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, description="Number of results to return per page, between 1 and 100 inclusive. Defaults to a standard page size if not specified.", ge=1, le=100)
class GetViewQueryResultsRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The Notion API version to use for this request. Must be set to 2026-03-11 or later.")
class GetViewQueryResultsRequest(StrictModel):
    """Retrieve the results of a query executed against a Notion view. Returns paginated results from the specified view and query."""
    path: GetViewQueryResultsRequestPath
    query: GetViewQueryResultsRequestQuery | None = None
    header: GetViewQueryResultsRequestHeader

# Operation: delete_view_query
class DeleteViewQueryRequestPath(StrictModel):
    view_id: str = Field(default=..., description="The unique identifier of the view containing the query to delete.")
    query_id: str = Field(default=..., description="The unique identifier of the query to delete.")
class DeleteViewQueryRequestHeader(StrictModel):
    notion_version: Literal["2026-03-11"] = Field(default=..., validation_alias="Notion-Version", serialization_alias="Notion-Version", description="The API version to use for this request. Must be set to the latest version: 2026-03-11.")
class DeleteViewQueryRequest(StrictModel):
    """Permanently delete a specific query from a view. This operation removes the query and cannot be undone."""
    path: DeleteViewQueryRequestPath
    header: DeleteViewQueryRequestHeader

# ============================================================================
# Component Models
# ============================================================================

class AnnotationRequest(PermissiveModel):
    bold: bool | None = Field(None, description="Whether the text is formatted as bold.")
    italic: bool | None = Field(None, description="Whether the text is formatted as italic.")
    strikethrough: bool | None = Field(None, description="Whether the text is formatted with a strikethrough.")
    underline: bool | None = Field(None, description="Whether the text is formatted with an underline.")
    code: bool | None = Field(None, description="Whether the text is formatted as code.")
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = Field(None, description="The color of the text.")

class BlockObjectRequestV12TableOfContents(StrictModel):
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None

class BlockObjectRequestV12(StrictModel):
    table_of_contents: BlockObjectRequestV12TableOfContents
    type_: Literal["table_of_contents"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV13LinkToPageV0(StrictModel):
    page_id: str
    type_: Literal["page_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BlockObjectRequestV13LinkToPageV1(StrictModel):
    database_id: str
    type_: Literal["database_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BlockObjectRequestV13LinkToPageV2(StrictModel):
    comment_id: str
    type_: Literal["comment_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BlockObjectRequestV13(StrictModel):
    link_to_page: BlockObjectRequestV13LinkToPageV0 | BlockObjectRequestV13LinkToPageV1 | BlockObjectRequestV13LinkToPageV2
    type_: Literal["link_to_page"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV30SyncedBlockSyncedFrom(StrictModel):
    block_id: str
    type_: Literal["block_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BlockObjectRequestWithoutChildrenV12TableOfContents(StrictModel):
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None

class BlockObjectRequestWithoutChildrenV12(StrictModel):
    table_of_contents: BlockObjectRequestWithoutChildrenV12TableOfContents
    type_: Literal["table_of_contents"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV13LinkToPageV0(StrictModel):
    page_id: str
    type_: Literal["page_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BlockObjectRequestWithoutChildrenV13LinkToPageV1(StrictModel):
    database_id: str
    type_: Literal["database_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BlockObjectRequestWithoutChildrenV13LinkToPageV2(StrictModel):
    comment_id: str
    type_: Literal["comment_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BlockObjectRequestWithoutChildrenV13(StrictModel):
    link_to_page: BlockObjectRequestWithoutChildrenV13LinkToPageV0 | BlockObjectRequestWithoutChildrenV13LinkToPageV1 | BlockObjectRequestWithoutChildrenV13LinkToPageV2
    type_: Literal["link_to_page"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV27SyncedBlockSyncedFrom(StrictModel):
    block_id: str
    type_: Literal["block_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BlockObjectRequestWithoutChildrenV27SyncedBlock(StrictModel):
    synced_from: BlockObjectRequestWithoutChildrenV27SyncedBlockSyncedFrom | None = Field(...)

class BlockObjectRequestWithoutChildrenV27(StrictModel):
    synced_block: BlockObjectRequestWithoutChildrenV27SyncedBlock
    type_: Literal["synced_block"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV12TableOfContents(StrictModel):
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None

class BlockObjectWithSingleLevelOfChildrenRequestV12(StrictModel):
    table_of_contents: BlockObjectWithSingleLevelOfChildrenRequestV12TableOfContents
    type_: Literal["table_of_contents"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV13LinkToPageV0(StrictModel):
    page_id: str
    type_: Literal["page_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BlockObjectWithSingleLevelOfChildrenRequestV13LinkToPageV1(StrictModel):
    database_id: str
    type_: Literal["database_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BlockObjectWithSingleLevelOfChildrenRequestV13LinkToPageV2(StrictModel):
    comment_id: str
    type_: Literal["comment_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class BlockObjectWithSingleLevelOfChildrenRequestV13(StrictModel):
    link_to_page: BlockObjectWithSingleLevelOfChildrenRequestV13LinkToPageV0 | BlockObjectWithSingleLevelOfChildrenRequestV13LinkToPageV1 | BlockObjectWithSingleLevelOfChildrenRequestV13LinkToPageV2
    type_: Literal["link_to_page"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV28SyncedBlockSyncedFrom(StrictModel):
    block_id: str
    type_: Literal["block_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class ChartAggregationRequest(PermissiveModel):
    aggregator: Literal["count", "count_values", "sum", "average", "median", "min", "max", "range", "unique", "empty", "not_empty", "percent_empty", "percent_not_empty", "checked", "unchecked", "percent_checked", "percent_unchecked", "earliest_date", "latest_date", "date_range"] = Field(..., description="The aggregation operator. \"count\" counts all rows and does not require a property_id. All other operators require a property_id.")
    property_id: str | None = Field(None, description="The property to aggregate on. Required for all operators except \"count\".")

class ChartReferenceLineRequest(PermissiveModel):
    value: float = Field(..., description="The y-axis value where the reference line is drawn.")
    label: str = Field(..., description="Label displayed alongside the reference line.")
    color: Literal["gray", "lightgray", "brown", "yellow", "orange", "green", "blue", "purple", "pink", "red"] = Field(..., description="Color of the reference line.")
    dash_style: Literal["solid", "dash"] = Field(..., description="Line style: \"solid\" for a continuous line, \"dash\" for a dashed line.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Unique identifier for the reference line. Auto-generated if omitted.")

class CheckboxPropertyFilterV0(PermissiveModel):
    equals: bool

class CheckboxPropertyFilterV1(PermissiveModel):
    does_not_equal: bool

class CheckboxPropertyFilter(PermissiveModel):
    checkbox_property_filter: CheckboxPropertyFilterV0 | CheckboxPropertyFilterV1

class ContentPositionSchemaV0AfterBlock(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class ContentPositionSchemaV0(PermissiveModel):
    type_: Literal["after_block"] = Field(..., validation_alias="type", serialization_alias="type")
    after_block: ContentPositionSchemaV0AfterBlock

class ContentPositionSchemaV1(PermissiveModel):
    type_: Literal["start"] = Field(..., validation_alias="type", serialization_alias="type")

class ContentPositionSchemaV2(PermissiveModel):
    type_: Literal["end"] = Field(..., validation_alias="type", serialization_alias="type")

class ContentPositionSchema(PermissiveModel):
    content_position_schema: ContentPositionSchemaV0 | ContentPositionSchemaV1 | ContentPositionSchemaV2

class ContentWithExpressionRequest(StrictModel):
    expression: str

class BlockObjectRequestV8(StrictModel):
    equation: ContentWithExpressionRequest
    type_: Literal["equation"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV8(StrictModel):
    equation: ContentWithExpressionRequest
    type_: Literal["equation"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV8(StrictModel):
    equation: ContentWithExpressionRequest
    type_: Literal["equation"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class CoverConfigRequest(PermissiveModel):
    type_: Literal["page_cover", "page_content", "property"] = Field(..., validation_alias="type", serialization_alias="type", description="Source of the cover image.")
    property_id: str | None = Field(None, description="Property ID when type is \"property\".")

class CreateACommentBodyAttachmentsItem(PermissiveModel):
    file_upload_id: str = Field(..., description="ID of a FileUpload object that has the status `uploaded`.")
    type_: Literal["file_upload"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `file_upload`")

class CreateACommentBodyDisplayNameV0(PermissiveModel):
    type_: Literal["integration"] = Field(..., validation_alias="type", serialization_alias="type", description="Always `integration`")

class CreateACommentBodyDisplayNameV1(PermissiveModel):
    type_: Literal["user"] = Field(..., validation_alias="type", serialization_alias="type", description="Always `user`")

class CreateACommentBodyDisplayNameV2Custom(PermissiveModel):
    name: str = Field(..., description="The custom display name to use", min_length=1)

class CreateACommentBodyDisplayNameV2(PermissiveModel):
    type_: Literal["custom"] = Field(..., validation_alias="type", serialization_alias="type", description="Always `custom`")
    custom: CreateACommentBodyDisplayNameV2Custom

class CreateACommentBodyV1V0ParentV01(PermissiveModel):
    page_id: str = Field(..., description="The ID of the parent page (with or without dashes), for example, 195de9221179449fab8075a27c979105")
    type_: Literal["page_id"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `page_id`")

class CreateACommentBodyV1V0ParentV11(PermissiveModel):
    block_id: str = Field(..., description="The ID of the parent block (with or without dashes), for example, 195de9221179449fab8075a27c979105")
    type_: Literal["block_id"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `block_id`")

class CreateACommentBodyV1V01(PermissiveModel):
    parent: CreateACommentBodyV1V0ParentV01 | CreateACommentBodyV1V0ParentV11 = Field(..., description="The parent of the comment. This can be a page or a block.")

class CreateACommentBodyV1V11(PermissiveModel):
    discussion_id: str = Field(..., description="The ID of the discussion to comment on.")

class CreateDatabaseBodyParentV1V01(PermissiveModel):
    type_: Literal["page_id"] = Field(..., validation_alias="type", serialization_alias="type", description="Always `page_id`")
    page_id: str

class CreateDatabaseBodyParentV1V11(PermissiveModel):
    type_: Literal["workspace"] = Field(..., validation_alias="type", serialization_alias="type", description="Always `workspace`")
    workspace: Literal[True] = Field(..., description="Always `true`")

class CreateDatabaseBodyParent(PermissiveModel):
    """The parent page or workspace where the database will be created."""
    type_: Literal["page_id", "workspace"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of parent.")
    v1: CreateDatabaseBodyParentV1V01 | CreateDatabaseBodyParentV1V11 | None = None

class CreateDatabaseForViewRequestParent(PermissiveModel):
    """The parent page for the new linked database block."""
    type_: Literal["page_id"] = Field(..., validation_alias="type", serialization_alias="type", description="The parent type. Must be \"page_id\".")
    page_id: str = Field(..., description="The ID of the page to create the database on.")

class CreateDatabaseForViewRequestPosition(PermissiveModel):
    """Where to place the new database block within the parent page. Defaults to appending at the end."""
    type_: Literal["after_block"] = Field(..., validation_alias="type", serialization_alias="type", description="Position type. \"after_block\" places the new database after the specified block in the page.")
    block_id: str = Field(..., description="The ID of an existing block in the page. The new database will be placed after this block.")

class CreateDatabaseForViewRequest(PermissiveModel):
    parent: CreateDatabaseForViewRequestParent = Field(..., description="The parent page for the new linked database block.")
    position: CreateDatabaseForViewRequestPosition | None = Field(None, description="Where to place the new database block within the parent page. Defaults to appending at the end.")

class CreateViewBodyPlacement(PermissiveModel):
    """Where to place the new widget in a dashboard view. Only applicable when view_id is provided. Defaults to creating a new row at the end."""
    type_: Literal["new_row"] = Field(..., validation_alias="type", serialization_alias="type", description="Placement type. \"new_row\" creates a new row containing the widget.")
    row_index: int | None = Field(None, description="The 0-based row position to insert the new row at. If omitted, the new row is appended at the end.", ge=0)

class CreateViewBodyPosition(PermissiveModel):
    """Where to place the new view in the database's view tab bar. Only applicable when database_id is provided. Defaults to "end" (append)."""
    type_: Literal["start"] = Field(..., validation_alias="type", serialization_alias="type", description="Position type. \"start\" places the view as the first tab.")
    view_id: str | None = Field(None, description="The ID of an existing view in the database. The new view will be placed after this view.")

class CustomEmojiPageIconRequestCustomEmoji(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the custom emoji.")
    name: str | None = Field(None, description="The name of the custom emoji.")
    url: str | None = Field(None, description="The URL of the custom emoji.")

class CustomEmojiPageIconRequest(PermissiveModel):
    type_: Literal["custom_emoji"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `custom_emoji`")
    custom_emoji: CustomEmojiPageIconRequestCustomEmoji

class DateRequest(StrictModel):
    start: str = Field(..., description="The start date of the date object.", json_schema_extra={'format': 'date'})
    end: str | None = Field(None, description="The end date of the date object, if any.", json_schema_extra={'format': 'date'})
    time_zone: str | None = Field(None, description="The time zone of the date object, if any. E.g. America/Los_Angeles, Europe/London, etc.")

class EmojiPageIconRequest(PermissiveModel):
    type_: Literal["emoji"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `emoji`")
    emoji: str = Field(..., description="An emoji character.")

class EmptyObject(RootModel[dict[str, Any]]):
    pass

class BlockObjectRequestV10(StrictModel):
    breadcrumb: EmptyObject
    type_: Literal["breadcrumb"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV9(StrictModel):
    divider: EmptyObject
    type_: Literal["divider"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV10(StrictModel):
    breadcrumb: EmptyObject
    type_: Literal["breadcrumb"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV11(StrictModel):
    tab: EmptyObject
    type_: Literal["tab"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV9(StrictModel):
    divider: EmptyObject
    type_: Literal["divider"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV10(StrictModel):
    breadcrumb: EmptyObject
    type_: Literal["breadcrumb"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV9(StrictModel):
    divider: EmptyObject
    type_: Literal["divider"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class ButtonPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["button"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `button`")
    button: EmptyObject

class CheckboxPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["checkbox"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `checkbox`")
    checkbox: EmptyObject

class CreatedByPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["created_by"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `created_by`")
    created_by: EmptyObject

class CreatedTimePropertyConfigurationRequest(PermissiveModel):
    type_: Literal["created_time"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `created_time`")
    created_time: EmptyObject

class DatePropertyConfigurationRequest(PermissiveModel):
    type_: Literal["date"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `date`")
    date: EmptyObject

class EmailPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["email"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `email`")
    email: EmptyObject

class EquationRichTextItemRequestEquation(PermissiveModel):
    """Notion supports inline LaTeX equations as rich text objects with a type value of `equation`."""
    expression: str = Field(..., description="A KaTeX compatible string.")

class EquationRichTextItemRequest(PermissiveModel):
    type_: Literal["equation"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `equation`")
    equation: EquationRichTextItemRequestEquation = Field(..., description="Notion supports inline LaTeX equations as rich text objects with a type value of `equation`.")

class ExistencePropertyFilterV0(PermissiveModel):
    is_empty: Literal[True]

class ExistencePropertyFilterV1(PermissiveModel):
    is_not_empty: Literal[True]

class ExistencePropertyFilter(PermissiveModel):
    existence_property_filter: ExistencePropertyFilterV0 | ExistencePropertyFilterV1

class ExternalFileRequest(StrictModel):
    url: str

class ExternalPageCoverRequestExternal(PermissiveModel):
    """External URL for the cover."""
    url: str = Field(..., description="The URL of the external file.")

class ExternalPageCoverRequest(PermissiveModel):
    type_: Literal["external"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `external`")
    external: ExternalPageCoverRequestExternal = Field(..., description="External URL for the cover.")

class ExternalPageIconRequestExternal(PermissiveModel):
    url: str = Field(..., description="The URL of the external file.")

class ExternalPageIconRequest(PermissiveModel):
    type_: Literal["external"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `external`")
    external: ExternalPageIconRequestExternal

class FileUploadIdRequest(StrictModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class FileUploadPageCoverRequestFileUpload(PermissiveModel):
    """The file upload for the cover."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="ID of a FileUpload object that has the status `uploaded`.")

class FileUploadPageCoverRequest(PermissiveModel):
    type_: Literal["file_upload"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `file_upload`")
    file_upload: FileUploadPageCoverRequestFileUpload = Field(..., description="The file upload for the cover.")

class FileUploadPageIconRequestFileUpload(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="ID of a FileUpload object that has the status `uploaded`.")

class FileUploadPageIconRequest(PermissiveModel):
    type_: Literal["file_upload"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `file_upload`")
    file_upload: FileUploadPageIconRequestFileUpload

class FileUploadWithOptionalNameRequest(StrictModel):
    file_upload: FileUploadIdRequest
    type_: Literal["file_upload"] | None = Field(None, validation_alias="type", serialization_alias="type")
    name: str | None = None

class FilesPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["files"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `files`")
    files: EmptyObject

class FormViewConfigRequest(PermissiveModel):
    type_: Literal["form"] = Field(..., validation_alias="type", serialization_alias="type", description="The view type. Must be \"form\".")
    is_form_closed: bool | None = Field(None, description="Whether the form is closed for submissions. Pass null to clear.")
    anonymous_submissions: bool | None = Field(None, description="Whether anonymous (non-logged-in) submissions are allowed. Pass null to clear.")
    submission_permissions: Literal["none", "comment_only", "reader", "read_and_write", "editor"] | None = Field(None, description="Permission level granted to the submitter on the created page after form submission. Pass null to clear.")

class FormulaPropertyConfigurationRequestFormula(PermissiveModel):
    expression: str | None = None

class FormulaPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["formula"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `formula`")
    formula: FormulaPropertyConfigurationRequestFormula

class FormulaPropertyFilterV0(PermissiveModel):
    string: ExistencePropertyFilter

class FormulaPropertyFilterV1(PermissiveModel):
    checkbox: CheckboxPropertyFilter

class FormulaPropertyFilterV2(PermissiveModel):
    number: ExistencePropertyFilter

class FormulaPropertyFilterV3(PermissiveModel):
    date: ExistencePropertyFilter

class FormulaPropertyFilter(PermissiveModel):
    formula_property_filter: FormulaPropertyFilterV0 | FormulaPropertyFilterV1 | FormulaPropertyFilterV2 | FormulaPropertyFilterV3

class GroupObjectRequest(StrictModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None
    object_: Literal["group"] | None = Field(None, validation_alias="object", serialization_alias="object")

class GroupSortRequest(PermissiveModel):
    type_: Literal["manual", "ascending", "descending"] = Field(..., validation_alias="type", serialization_alias="type", description="Sort direction for groups.")

class CheckboxGroupByConfigRequest(PermissiveModel):
    type_: Literal["checkbox"] = Field(..., validation_alias="type", serialization_alias="type", description="The property type for grouping.")
    property_id: str = Field(..., description="Property ID to group by.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")
    hide_empty_groups: bool | None = Field(None, description="Whether to hide groups that have no items.")

class DateGroupByConfigRequest(PermissiveModel):
    type_: Literal["date", "created_time", "last_edited_time"] = Field(..., validation_alias="type", serialization_alias="type", description="The property type for grouping.")
    property_id: str = Field(..., description="Property ID to group by.")
    group_by: Literal["relative", "day", "week", "month", "year"] = Field(..., description="Granularity for date grouping.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")
    hide_empty_groups: bool | None = Field(None, description="Whether to hide groups that have no items.")
    start_day_of_week: Literal[0, 1] | None = Field(None, description="Start day of week for week grouping (0 = Sunday, 1 = Monday).")

class FormulaCheckboxSubGroupByRequest(PermissiveModel):
    type_: Literal["checkbox"] = Field(..., validation_alias="type", serialization_alias="type", description="The formula result type for grouping.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")

class FormulaDateSubGroupByRequest(PermissiveModel):
    type_: Literal["date"] = Field(..., validation_alias="type", serialization_alias="type", description="The formula result type for grouping.")
    group_by: Literal["relative", "day", "week", "month", "year"] = Field(..., description="Granularity for date grouping.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")
    start_day_of_week: Literal[0, 1] | None = Field(None, description="Start day of week for week grouping (0 = Sunday, 1 = Monday).")

class FormulaNumberSubGroupByRequest(PermissiveModel):
    type_: Literal["number"] = Field(..., validation_alias="type", serialization_alias="type", description="The formula result type for grouping.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")
    range_start: int | None = Field(None, description="Start of the range for number grouping buckets.")
    range_end: int | None = Field(None, description="End of the range for number grouping buckets.")
    range_size: int | None = Field(None, description="Size of each bucket in number grouping.", ge=1)

class FormulaTextSubGroupByRequest(PermissiveModel):
    type_: Literal["text"] = Field(..., validation_alias="type", serialization_alias="type", description="The formula result type for grouping.")
    group_by: Literal["exact", "alphabet_prefix"] = Field(..., description="How to group text values. \"exact\" = exact match, \"alphabet_prefix\" = first letter.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")

class FormulaGroupByConfigRequest(PermissiveModel):
    type_: Literal["formula"] = Field(..., validation_alias="type", serialization_alias="type", description="The property type for grouping.")
    property_id: str = Field(..., description="Property ID of the formula to group by.")
    group_by: FormulaDateSubGroupByRequest | FormulaTextSubGroupByRequest | FormulaNumberSubGroupByRequest | FormulaCheckboxSubGroupByRequest = Field(..., description="Sub-group-by configuration based on the formula result type.")
    hide_empty_groups: bool | None = Field(None, description="Whether to hide groups that have no items.")

class IconPageIconRequestIcon(PermissiveModel):
    """A Notion native icon, specified by name and optional color."""
    name: str = Field(..., description="The name of the Notion icon (e.g. pizza, meeting, home). See the Notion icon picker for valid names.")
    color: Literal["gray", "lightgray", "brown", "yellow", "orange", "green", "blue", "purple", "pink", "red"] | None = Field(None, description="The color variant of the icon. Defaults to gray if not specified. Valid values: gray, lightgray, brown, yellow, orange, green, blue, purple, pink, red.")

class IconPageIconRequest(PermissiveModel):
    type_: Literal["icon"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `icon`")
    icon: IconPageIconRequestIcon = Field(..., description="A Notion native icon, specified by name and optional color.")

class InternalFileRequest(StrictModel):
    url: str
    expiry_time: str | None = Field(None, json_schema_extra={'format': 'date-time'})

class InternalOrExternalFileWithNameRequestV0(StrictModel):
    file_: InternalFileRequest = Field(..., validation_alias="file", serialization_alias="file")
    name: str
    type_: Literal["file"] | None = Field(None, validation_alias="type", serialization_alias="type")

class InternalOrExternalFileWithNameRequestV1(StrictModel):
    external: ExternalFileRequest
    name: str
    type_: Literal["external"] | None = Field(None, validation_alias="type", serialization_alias="type")

class InternalOrExternalFileWithNameRequest(PermissiveModel):
    internal_or_external_file_with_name_request: InternalOrExternalFileWithNameRequestV0 | InternalOrExternalFileWithNameRequestV1

class LastEditedByPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["last_edited_by"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `last_edited_by`")
    last_edited_by: EmptyObject

class LastEditedTimePropertyConfigurationRequest(PermissiveModel):
    type_: Literal["last_edited_time"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `last_edited_time`")
    last_edited_time: EmptyObject

class LastVisitedTimePropertyConfigurationRequest(PermissiveModel):
    type_: Literal["last_visited_time"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `last_visited_time`")
    last_visited_time: EmptyObject

class LocationPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["location"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `location`")
    location: EmptyObject

class MentionRichTextItemRequestMentionV1(PermissiveModel):
    type_: Literal["date"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `date`")
    date: DateRequest = Field(..., description="Details of the date mention.")

class MentionRichTextItemRequestMentionV2Page(PermissiveModel):
    """Details of the page mention."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the page in the mention.")

class MentionRichTextItemRequestMentionV2(PermissiveModel):
    type_: Literal["page"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `page`")
    page: MentionRichTextItemRequestMentionV2Page = Field(..., description="Details of the page mention.")

class MentionRichTextItemRequestMentionV3Database(PermissiveModel):
    """Details of the database mention."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the database in the mention.")

class MentionRichTextItemRequestMentionV3(PermissiveModel):
    type_: Literal["database"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `database`")
    database: MentionRichTextItemRequestMentionV3Database = Field(..., description="Details of the database mention.")

class MentionRichTextItemRequestMentionV5CustomEmoji(PermissiveModel):
    """Details of the custom emoji mention."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the custom emoji.")
    name: str | None = Field(None, description="The name of the custom emoji.")
    url: str | None = Field(None, description="The URL of the custom emoji.")

class MentionRichTextItemRequestMentionV5(PermissiveModel):
    type_: Literal["custom_emoji"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `custom_emoji`")
    custom_emoji: MentionRichTextItemRequestMentionV5CustomEmoji = Field(..., description="Details of the custom emoji mention.")

class MovePageBodyParentV0(PermissiveModel):
    page_id: str = Field(..., description="The ID of the parent page (with or without dashes), for example, 195de9221179449fab8075a27c979105")
    type_: Literal["page_id"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `page_id`")

class MovePageBodyParentV1(PermissiveModel):
    data_source_id: str = Field(..., description="The ID of the parent data source (collection), with or without dashes. For example, f336d0bc-b841-465b-8045-024475c079dd")
    type_: Literal["data_source_id"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `data_source_id`")

class MultiSelectPropertyConfigurationRequestMultiSelectOptionsItem(PermissiveModel):
    name: str
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class MultiSelectPropertyConfigurationRequestMultiSelect(PermissiveModel):
    options: list[MultiSelectPropertyConfigurationRequestMultiSelectOptionsItem] | None = Field(None, max_length=100)

class MultiSelectPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["multi_select"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `multi_select`")
    multi_select: MultiSelectPropertyConfigurationRequestMultiSelect

class NumberGroupByConfigRequest(PermissiveModel):
    type_: Literal["number"] = Field(..., validation_alias="type", serialization_alias="type", description="The property type for grouping.")
    property_id: str = Field(..., description="Property ID to group by.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")
    hide_empty_groups: bool | None = Field(None, description="Whether to hide groups that have no items.")
    range_start: int | None = Field(None, description="Start of the range for number grouping buckets.")
    range_end: int | None = Field(None, description="End of the range for number grouping buckets.")
    range_size: int | None = Field(None, description="Size of each bucket in number grouping.", ge=1)

class NumberPropertyConfigurationRequestNumber(PermissiveModel):
    format_: str | None = Field(None, validation_alias="format", serialization_alias="format")

class NumberPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["number"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `number`")
    number: NumberPropertyConfigurationRequestNumber

class PageIconRequest(PermissiveModel):
    page_icon_request: FileUploadPageIconRequest | EmojiPageIconRequest | ExternalPageIconRequest | CustomEmojiPageIconRequest | IconPageIconRequest

class PagePositionSchemaV0AfterBlock(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PagePositionSchemaV0(PermissiveModel):
    type_: Literal["after_block"] = Field(..., validation_alias="type", serialization_alias="type")
    after_block: PagePositionSchemaV0AfterBlock

class PagePositionSchemaV1(PermissiveModel):
    type_: Literal["page_start"] = Field(..., validation_alias="type", serialization_alias="type")

class PagePositionSchemaV2(PermissiveModel):
    type_: Literal["page_end"] = Field(..., validation_alias="type", serialization_alias="type")

class PagePositionSchema(PermissiveModel):
    page_position_schema: PagePositionSchemaV0 | PagePositionSchemaV1 | PagePositionSchemaV2

class PartialUserObjectRequest(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the user.")
    object_: Literal["user"] | None = Field(None, validation_alias="object", serialization_alias="object", description="The user object type name.")

class MentionRichTextItemRequestMentionV0(PermissiveModel):
    type_: Literal["user"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `user`")
    user: PartialUserObjectRequest = Field(..., description="Details of the user mention.")

class PatchPageBodyPropertiesValueV10(StrictModel):
    checkbox: bool
    type_: Literal["checkbox"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV12(StrictModel):
    files: list[InternalOrExternalFileWithNameRequest | FileUploadWithOptionalNameRequest] = Field(..., max_length=100)
    type_: Literal["files"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV13StatusV0(StrictModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PatchPageBodyPropertiesValueV13StatusV1(StrictModel):
    name: str
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PatchPageBodyPropertiesValueV13(StrictModel):
    status: PatchPageBodyPropertiesValueV13StatusV0 | PatchPageBodyPropertiesValueV13StatusV1 | None = Field(...)
    type_: Literal["status"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV14Place(PermissiveModel):
    lat: float
    lon: float
    name: str | None = None
    address: str | None = None
    aws_place_id: str | None = None
    google_place_id: str | None = None

class PatchPageBodyPropertiesValueV14(StrictModel):
    place: PatchPageBodyPropertiesValueV14Place | None = Field(...)
    type_: Literal["place"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV15VerificationV0(PermissiveModel):
    state: Literal["verified"]
    date: DateRequest | None = None

class PatchPageBodyPropertiesValueV15VerificationV1(PermissiveModel):
    state: Literal["unverified"]

class PatchPageBodyPropertiesValueV15(StrictModel):
    verification: PatchPageBodyPropertiesValueV15VerificationV0 | PatchPageBodyPropertiesValueV15VerificationV1
    type_: Literal["verification"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV2(StrictModel):
    number: float | None = Field(...)
    type_: Literal["number"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV3(StrictModel):
    url: str | None = Field(...)
    type_: Literal["url"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV4SelectV0(StrictModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PatchPageBodyPropertiesValueV4SelectV1(StrictModel):
    name: str
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PatchPageBodyPropertiesValueV4(StrictModel):
    select: PatchPageBodyPropertiesValueV4SelectV0 | PatchPageBodyPropertiesValueV4SelectV1 | None = Field(...)
    type_: Literal["select"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV5MultiSelectItemV0(StrictModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PatchPageBodyPropertiesValueV5MultiSelectItemV1(StrictModel):
    name: str
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PatchPageBodyPropertiesValueV5(StrictModel):
    multi_select: list[PatchPageBodyPropertiesValueV5MultiSelectItemV0 | PatchPageBodyPropertiesValueV5MultiSelectItemV1] = Field(..., max_length=100)
    type_: Literal["multi_select"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV6(StrictModel):
    people: list[PartialUserObjectRequest | GroupObjectRequest] = Field(..., max_length=100)
    type_: Literal["people"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV7(StrictModel):
    email: str | None = Field(...)
    type_: Literal["email"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV8(StrictModel):
    phone_number: str | None = Field(...)
    type_: Literal["phone_number"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV9(StrictModel):
    date: DateRequest | None = Field(...)
    type_: Literal["date"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyTemplate(PermissiveModel):
    type_: Literal["default"] = Field(..., validation_alias="type", serialization_alias="type")
    timezone_: str | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="IANA timezone to use when resolving template variables like @now and @today (e.g. 'America/New_York'). Defaults to the authorizing user's timezone for public integrations, or UTC for internal integrations.")
    template_id: str | None = None

class PeoplePropertyConfigurationRequest(PermissiveModel):
    type_: Literal["people"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `people`")
    people: EmptyObject

class PersonGroupByConfigRequest(PermissiveModel):
    type_: Literal["person", "created_by", "last_edited_by"] = Field(..., validation_alias="type", serialization_alias="type", description="The property type for grouping.")
    property_id: str = Field(..., description="Property ID to group by.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")
    hide_empty_groups: bool | None = Field(None, description="Whether to hide groups that have no items.")

class PhoneNumberPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["phone_number"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `phone_number`")
    phone_number: EmptyObject

class PlacePropertyConfigurationRequest(PermissiveModel):
    type_: Literal["place"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `place`")
    place: EmptyObject

class PostDatabaseQueryBodySortsItemV0(PermissiveModel):
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    direction: Literal["ascending", "descending"]

class PostDatabaseQueryBodySortsItemV1(PermissiveModel):
    timestamp: Literal["created_time", "last_edited_time"]
    direction: Literal["ascending", "descending"]

class PostPageBodyParentV0(StrictModel):
    page_id: str
    type_: Literal["page_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyParentV1(StrictModel):
    database_id: str
    type_: Literal["database_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyParentV2(StrictModel):
    data_source_id: str
    type_: Literal["data_source_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyParentV3(StrictModel):
    workspace: Literal[True]
    type_: Literal["workspace"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV10(StrictModel):
    checkbox: bool
    type_: Literal["checkbox"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV12(StrictModel):
    files: list[InternalOrExternalFileWithNameRequest | FileUploadWithOptionalNameRequest] = Field(..., max_length=100)
    type_: Literal["files"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV13StatusV0(StrictModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PostPageBodyPropertiesValueV13StatusV1(StrictModel):
    name: str
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PostPageBodyPropertiesValueV13(StrictModel):
    status: PostPageBodyPropertiesValueV13StatusV0 | PostPageBodyPropertiesValueV13StatusV1 | None = Field(...)
    type_: Literal["status"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV14Place(PermissiveModel):
    lat: float
    lon: float
    name: str | None = None
    address: str | None = None
    aws_place_id: str | None = None
    google_place_id: str | None = None

class PostPageBodyPropertiesValueV14(StrictModel):
    place: PostPageBodyPropertiesValueV14Place | None = Field(...)
    type_: Literal["place"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV15VerificationV0(PermissiveModel):
    state: Literal["verified"]
    date: DateRequest | None = None

class PostPageBodyPropertiesValueV15VerificationV1(PermissiveModel):
    state: Literal["unverified"]

class PostPageBodyPropertiesValueV15(StrictModel):
    verification: PostPageBodyPropertiesValueV15VerificationV0 | PostPageBodyPropertiesValueV15VerificationV1
    type_: Literal["verification"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV2(StrictModel):
    number: float | None = Field(...)
    type_: Literal["number"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV3(StrictModel):
    url: str | None = Field(...)
    type_: Literal["url"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV4SelectV0(StrictModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PostPageBodyPropertiesValueV4SelectV1(StrictModel):
    name: str
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PostPageBodyPropertiesValueV4(StrictModel):
    select: PostPageBodyPropertiesValueV4SelectV0 | PostPageBodyPropertiesValueV4SelectV1 | None = Field(...)
    type_: Literal["select"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV5MultiSelectItemV0(StrictModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PostPageBodyPropertiesValueV5MultiSelectItemV1(StrictModel):
    name: str
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class PostPageBodyPropertiesValueV5(StrictModel):
    multi_select: list[PostPageBodyPropertiesValueV5MultiSelectItemV0 | PostPageBodyPropertiesValueV5MultiSelectItemV1] = Field(..., max_length=100)
    type_: Literal["multi_select"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV6(StrictModel):
    people: list[PartialUserObjectRequest | GroupObjectRequest] = Field(..., max_length=100)
    type_: Literal["people"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV7(StrictModel):
    email: str | None = Field(...)
    type_: Literal["email"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV8(StrictModel):
    phone_number: str | None = Field(...)
    type_: Literal["phone_number"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV9(StrictModel):
    date: DateRequest | None = Field(...)
    type_: Literal["date"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyTemplate(PermissiveModel):
    type_: Literal["none"] = Field(..., validation_alias="type", serialization_alias="type")
    timezone_: str | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="IANA timezone to use when resolving template variables like @now and @today (e.g. 'America/New_York'). Defaults to the authorizing user's timezone for public integrations, or UTC for internal integrations.")
    template_id: str | None = None

class PropertyConfigurationRequestCommon(PermissiveModel):
    description: str | None = Field(None, description="The description of the property.")

class PropertyFilterV0(StrictModel):
    title: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["title"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV1(StrictModel):
    rich_text: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["rich_text"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV10(StrictModel):
    url: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["url"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV11(StrictModel):
    email: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["email"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV12(StrictModel):
    phone_number: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["phone_number"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV13(StrictModel):
    relation: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["relation"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV14(StrictModel):
    created_by: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["created_by"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV15(StrictModel):
    created_time: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["created_time"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV16(StrictModel):
    last_edited_by: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["last_edited_by"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV17(StrictModel):
    last_edited_time: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["last_edited_time"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV18(StrictModel):
    formula: FormulaPropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["formula"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV19(StrictModel):
    unique_id: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["unique_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV2(StrictModel):
    number: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["number"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV3(StrictModel):
    checkbox: CheckboxPropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["checkbox"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV4(StrictModel):
    select: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["select"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV5(StrictModel):
    multi_select: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["multi_select"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV6(StrictModel):
    status: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["status"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV7(StrictModel):
    date: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["date"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV8(StrictModel):
    people: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["people"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilterV9(StrictModel):
    files: ExistencePropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["files"] | None = Field(None, validation_alias="type", serialization_alias="type")

class QuickFilterConditionRequest(RootModel[dict[str, Any]]):
    pass

class RelationGroupByConfigRequest(PermissiveModel):
    type_: Literal["relation"] = Field(..., validation_alias="type", serialization_alias="type", description="The property type for grouping.")
    property_id: str = Field(..., description="Property ID to group by.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")
    hide_empty_groups: bool | None = Field(None, description="Whether to hide groups that have no items.")

class RelationItemPropertyValueResponse(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")

class PatchPageBodyPropertiesValueV11(StrictModel):
    relation: list[RelationItemPropertyValueResponse] = Field(..., max_length=100)
    type_: Literal["relation"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV11(StrictModel):
    relation: list[RelationItemPropertyValueResponse] = Field(..., max_length=100)
    type_: Literal["relation"] | None = Field(None, validation_alias="type", serialization_alias="type")

class RelationPropertyConfigurationRequestRelationV1V0(PermissiveModel):
    type_: Literal["single_property"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `single_property`")
    single_property: EmptyObject

class RelationPropertyConfigurationRequestRelationV1V01(PermissiveModel):
    type_: Literal["single_property"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `single_property`")
    single_property: EmptyObject

class RelationPropertyConfigurationRequestRelationV1V1DualProperty(PermissiveModel):
    synced_property_id: str | None = None
    synced_property_name: str | None = None

class RelationPropertyConfigurationRequestRelationV1V1(PermissiveModel):
    type_: Literal["dual_property"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `dual_property`")
    dual_property: RelationPropertyConfigurationRequestRelationV1V1DualProperty

class RelationPropertyConfigurationRequestRelationV1V1DualProperty1(PermissiveModel):
    synced_property_id: str | None = None
    synced_property_name: str | None = None

class RelationPropertyConfigurationRequestRelationV1V11(PermissiveModel):
    type_: Literal["dual_property"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `dual_property`")
    dual_property: RelationPropertyConfigurationRequestRelationV1V1DualProperty1

class RelationPropertyConfigurationRequestRelation(PermissiveModel):
    data_source_id: str
    v1: RelationPropertyConfigurationRequestRelationV1V01 | RelationPropertyConfigurationRequestRelationV1V11 | None = None

class RelationPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["relation"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `relation`")
    relation: RelationPropertyConfigurationRequestRelation

class RichTextItemRequestCommon(PermissiveModel):
    annotations_: AnnotationRequest | None = Field(None, validation_alias="annotations", serialization_alias="annotations", description="All rich text objects contain an annotations object that sets the styling for the rich text.")

class RichTextPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["rich_text"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `rich_text`")
    rich_text: EmptyObject

class RollupPropertyConfigurationRequestRollupV1V0(PermissiveModel):
    relation_property_name: str
    rollup_property_name: str

class RollupPropertyConfigurationRequestRollupV1V01(PermissiveModel):
    relation_property_name: str
    rollup_property_name: str

class RollupPropertyConfigurationRequestRollupV1V1(PermissiveModel):
    relation_property_id: str
    rollup_property_name: str

class RollupPropertyConfigurationRequestRollupV1V11(PermissiveModel):
    relation_property_id: str
    rollup_property_name: str

class RollupPropertyConfigurationRequestRollupV1V2(PermissiveModel):
    relation_property_name: str
    rollup_property_id: str

class RollupPropertyConfigurationRequestRollupV1V21(PermissiveModel):
    relation_property_name: str
    rollup_property_id: str

class RollupPropertyConfigurationRequestRollupV1V3(PermissiveModel):
    relation_property_id: str
    rollup_property_id: str

class RollupPropertyConfigurationRequestRollupV1V31(PermissiveModel):
    relation_property_id: str
    rollup_property_id: str

class RollupPropertyConfigurationRequestRollup(PermissiveModel):
    function: Literal["count", "count_values", "empty", "not_empty", "unique", "show_unique", "percent_empty", "percent_not_empty", "sum", "average", "median", "min", "max", "range", "earliest_date", "latest_date", "date_range", "checked", "unchecked", "percent_checked", "percent_unchecked", "count_per_group", "percent_per_group", "show_original"] = Field(..., description="The function to use for the rollup, e.g. count, count_values, percent_not_empty, max.")
    v1: RollupPropertyConfigurationRequestRollupV1V01 | RollupPropertyConfigurationRequestRollupV1V11 | RollupPropertyConfigurationRequestRollupV1V21 | RollupPropertyConfigurationRequestRollupV1V31 | None = None

class RollupPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["rollup"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `rollup`")
    rollup: RollupPropertyConfigurationRequestRollup

class RollupPropertyFilterV3(PermissiveModel):
    date: ExistencePropertyFilter

class RollupPropertyFilterV4(PermissiveModel):
    number: ExistencePropertyFilter

class RollupSubfilterPropertyFilterV0(PermissiveModel):
    rich_text: ExistencePropertyFilter

class RollupSubfilterPropertyFilterV1(PermissiveModel):
    number: ExistencePropertyFilter

class RollupSubfilterPropertyFilterV2(PermissiveModel):
    checkbox: CheckboxPropertyFilter

class RollupSubfilterPropertyFilterV3(PermissiveModel):
    select: ExistencePropertyFilter

class RollupSubfilterPropertyFilterV4(PermissiveModel):
    multi_select: ExistencePropertyFilter

class RollupSubfilterPropertyFilterV5(PermissiveModel):
    relation: ExistencePropertyFilter

class RollupSubfilterPropertyFilterV6(PermissiveModel):
    date: ExistencePropertyFilter

class RollupSubfilterPropertyFilterV7(PermissiveModel):
    people: ExistencePropertyFilter

class RollupSubfilterPropertyFilterV8(PermissiveModel):
    files: ExistencePropertyFilter

class RollupSubfilterPropertyFilterV9(PermissiveModel):
    status: ExistencePropertyFilter

class RollupSubfilterPropertyFilter(PermissiveModel):
    rollup_subfilter_property_filter: RollupSubfilterPropertyFilterV0 | RollupSubfilterPropertyFilterV1 | RollupSubfilterPropertyFilterV2 | RollupSubfilterPropertyFilterV3 | RollupSubfilterPropertyFilterV4 | RollupSubfilterPropertyFilterV5 | RollupSubfilterPropertyFilterV6 | RollupSubfilterPropertyFilterV7 | RollupSubfilterPropertyFilterV8 | RollupSubfilterPropertyFilterV9

class RollupPropertyFilterV0(PermissiveModel):
    any_: RollupSubfilterPropertyFilter = Field(..., validation_alias="any", serialization_alias="any")

class RollupPropertyFilterV1(PermissiveModel):
    none: RollupSubfilterPropertyFilter

class RollupPropertyFilterV2(PermissiveModel):
    every: RollupSubfilterPropertyFilter

class RollupPropertyFilter(PermissiveModel):
    rollup_property_filter: RollupPropertyFilterV0 | RollupPropertyFilterV1 | RollupPropertyFilterV2 | RollupPropertyFilterV3 | RollupPropertyFilterV4

class PropertyFilterV20(StrictModel):
    rollup: RollupPropertyFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["rollup"] | None = Field(None, validation_alias="type", serialization_alias="type")

class SelectGroupByConfigRequest(PermissiveModel):
    type_: Literal["select", "multi_select"] = Field(..., validation_alias="type", serialization_alias="type", description="The property type for grouping.")
    property_id: str = Field(..., description="Property ID to group by.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")
    hide_empty_groups: bool | None = Field(None, description="Whether to hide groups that have no items.")

class SelectPropertyConfigurationRequestSelectOptionsItem(PermissiveModel):
    name: str
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class SelectPropertyConfigurationRequestSelect(PermissiveModel):
    options: list[SelectPropertyConfigurationRequestSelectOptionsItem] | None = Field(None, max_length=100)

class SelectPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["select"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `select`")
    select: SelectPropertyConfigurationRequestSelect

class StatusGroupByConfigRequest(PermissiveModel):
    type_: Literal["status"] = Field(..., validation_alias="type", serialization_alias="type", description="The property type for grouping.")
    property_id: str = Field(..., description="Property ID to group by.")
    group_by: Literal["group", "option"] = Field(..., description="How to group status values. \"group\" groups by status group (To Do/In Progress/Done), \"option\" groups by individual option.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")
    hide_empty_groups: bool | None = Field(None, description="Whether to hide groups that have no items.")

class StatusPropertyConfigRequestOptionsItem(PermissiveModel):
    name: str
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None

class StatusPropertyConfigRequest(PermissiveModel):
    options: list[StatusPropertyConfigRequestOptionsItem] | None = Field(None, description="The initial status options. If not provided, defaults are created.", max_length=100)

class StatusPropertyConfigUpdateRequestOptionsItemV1V0(PermissiveModel):
    name: str
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class StatusPropertyConfigUpdateRequestOptionsItemV1V01(PermissiveModel):
    name: str
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class StatusPropertyConfigUpdateRequestOptionsItemV1V1(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None

class StatusPropertyConfigUpdateRequestOptionsItemV1V11(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None

class StatusPropertyConfigUpdateRequestOptionsItem(PermissiveModel):
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None
    v1: StatusPropertyConfigUpdateRequestOptionsItemV1V01 | StatusPropertyConfigUpdateRequestOptionsItemV1V11 | None = None

class StatusPropertyConfigUpdateRequest(PermissiveModel):
    options: list[StatusPropertyConfigUpdateRequestOptionsItem] | None = Field(None, description="Status options to add or update. New options are assigned to the To-do group.", max_length=100)

class StatusPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["status"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `status`")
    status: StatusPropertyConfigRequest

class SubtaskConfigRequest(PermissiveModel):
    property_id: str | None = Field(None, description="Relation property ID used for parent-child nesting.")
    display_mode: Literal["show", "hidden", "flattened", "disabled"] | None = Field(None, description="How sub-items are displayed. \"show\" renders hierarchically with toggles, \"hidden\" shows parents with a count, \"flattened\" shows sub-items with a parent indicator, \"disabled\" turns off sub-item rendering.")
    filter_scope: Literal["parents", "parents_and_subitems", "subitems"] | None = Field(None, description="Which items are included when filtering. \"parents\" includes parent items only, \"parents_and_subitems\" includes both, \"subitems\" includes sub-items only.")
    toggle_column_id: str | None = Field(None, description="Property ID of the column showing the sub-item expand/collapse toggle.")

class TemplateMentionDateTemplateMentionRequest(StrictModel):
    type_: Literal["template_mention_date"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `template_mention_date`")
    template_mention_date: Literal["today", "now"] = Field(..., description="The date of the template mention.")

class TemplateMentionUserTemplateMentionRequest(StrictModel):
    type_: Literal["template_mention_user"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `template_mention_user`")
    template_mention_user: Literal["me"] = Field(..., description="The user of the template mention.")

class TemplateMentionRequest(PermissiveModel):
    template_mention_request: TemplateMentionDateTemplateMentionRequest | TemplateMentionUserTemplateMentionRequest

class MentionRichTextItemRequestMentionV4(PermissiveModel):
    type_: Literal["template_mention"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `template_mention`")
    template_mention: TemplateMentionRequest = Field(..., description="Details of the template mention.")

class MentionRichTextItemRequest(PermissiveModel):
    type_: Literal["mention"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `mention`")
    mention: MentionRichTextItemRequestMentionV0 | MentionRichTextItemRequestMentionV1 | MentionRichTextItemRequestMentionV2 | MentionRichTextItemRequestMentionV3 | MentionRichTextItemRequestMentionV4 | MentionRichTextItemRequestMentionV5 = Field(..., description="Mention objects represent an inline mention of a database, date, link preview mention, page, template mention, or user. A mention is created in the Notion UI when a user types `@` followed by the name of the reference.")

class TextGroupByConfigRequest(PermissiveModel):
    type_: Literal["text", "title", "url", "email", "phone_number"] = Field(..., validation_alias="type", serialization_alias="type", description="The property type for grouping.")
    property_id: str = Field(..., description="Property ID to group by.")
    group_by: Literal["exact", "alphabet_prefix"] = Field(..., description="How to group text values. \"exact\" = exact match, \"alphabet_prefix\" = first letter.")
    sort: GroupSortRequest = Field(..., description="Sort order for groups.")
    hide_empty_groups: bool | None = Field(None, description="Whether to hide groups that have no items.")

class GroupByConfigRequest(PermissiveModel):
    """Group-by configuration based on property type."""
    group_by_config_request: SelectGroupByConfigRequest | StatusGroupByConfigRequest | PersonGroupByConfigRequest | RelationGroupByConfigRequest | DateGroupByConfigRequest | TextGroupByConfigRequest | NumberGroupByConfigRequest | CheckboxGroupByConfigRequest | FormulaGroupByConfigRequest

class ChartViewConfigRequest(PermissiveModel):
    type_: Literal["chart"] = Field(..., validation_alias="type", serialization_alias="type", description="The view type. Must be \"chart\".")
    chart_type: Literal["column", "bar", "line", "donut", "number"] = Field(..., description="The chart type.")
    x_axis: GroupByConfigRequest | None = Field(None, description="X-axis grouping configuration for grouped data mode. Pass null to clear.")
    y_axis: ChartAggregationRequest | None = Field(None, description="Y-axis aggregation for grouped data mode. Pass null to clear.")
    x_axis_property_id: str | None = Field(None, description="Property ID for x-axis values in results mode. Pass null to clear.")
    y_axis_property_id: str | None = Field(None, description="Property ID for y-axis values in results mode. Pass null to clear.")
    value: ChartAggregationRequest | None = Field(None, description="Aggregation for number charts. Pass null to clear.")
    sort: Literal["manual", "x_ascending", "x_descending", "y_ascending", "y_descending"] | None = Field(None, description="Sort order for chart data. Pass null to clear.")
    color_theme: Literal["gray", "blue", "yellow", "green", "purple", "teal", "orange", "pink", "red", "auto", "colorful"] | None = Field(None, description="Color theme. Pass null to clear.")
    height: Literal["small", "medium", "large", "extra_large"] | None = Field(None, description="Chart height. Pass null to clear.")
    hide_empty_groups: bool | None = Field(None, description="Whether to hide groups with no data. Pass null to clear.")
    legend_position: Literal["off", "bottom", "side"] | None = Field(None, description="Legend position. Pass null to clear.")
    show_data_labels: bool | None = Field(None, description="Whether to show data labels. Pass null to clear.")
    axis_labels: Literal["none", "x_axis", "y_axis", "both"] | None = Field(None, description="Which axis labels to show. Pass null to clear.")
    grid_lines: Literal["none", "horizontal", "vertical", "both"] | None = Field(None, description="Which grid lines to show. Pass null to clear.")
    cumulative: bool | None = Field(None, description="Cumulative values (line only). Pass null to clear.")
    smooth_line: bool | None = Field(None, description="Smooth line curves (line only). Pass null to clear.")
    hide_line_fill_area: bool | None = Field(None, description="Hide area fill (line only). Pass null to clear.")
    group_style: Literal["normal", "percent", "side_by_side"] | None = Field(None, description="Grouped/stacked bar display style. Pass null to clear.")
    y_axis_min: float | None = Field(None, description="Custom y-axis minimum. Pass null to clear.")
    y_axis_max: float | None = Field(None, description="Custom y-axis maximum. Pass null to clear.")
    donut_labels: Literal["none", "value", "name", "name_and_value"] | None = Field(None, description="Donut slice labels. Pass null to clear.")
    hide_title: bool | None = Field(None, description="Hide title (number only). Pass null to clear.")
    stack_by: GroupByConfigRequest | None = Field(None, description="Stack-by grouping for stacked/grouped bar charts. Pass null to clear.")
    reference_lines: list[ChartReferenceLineRequest] | None = Field(None, description="Reference lines on the chart. Pass null to clear.", max_length=100)
    caption: str | None = Field(None, description="Chart caption text. Pass null to clear.")
    color_by_value: bool | None = Field(None, description="Whether to color chart elements by their numeric value (gradient coloring). Pass null to clear.")

class TextRichTextItemRequestTextLink(PermissiveModel):
    """An object with information about any inline link in this text, if included."""
    url: str = Field(..., description="The URL of the link.")

class TextRichTextItemRequestText(StrictModel):
    """If a rich text object's type value is `text`, then the corresponding text field contains an object including the text content and any inline link."""
    content: str = Field(..., description="The actual text content of the text.", max_length=2000)
    link: TextRichTextItemRequestTextLink | None = Field(None, description="An object with information about any inline link in this text, if included.")

class TextRichTextItemRequest(PermissiveModel):
    type_: Literal["text"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `text`")
    text: TextRichTextItemRequestText = Field(..., description="If a rich text object's type value is `text`, then the corresponding text field contains an object including the text content and any inline link.")

class RichTextItemRequest(PermissiveModel):
    annotations_: AnnotationRequest | None = Field(None, validation_alias="annotations", serialization_alias="annotations", description="All rich text objects contain an annotations object that sets the styling for the rich text.")
    v1: TextRichTextItemRequest | MentionRichTextItemRequest | EquationRichTextItemRequest | None = None

class BlockObjectRequestV7Code(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    language: Literal["abap", "abc", "agda", "arduino", "ascii art", "assembly", "bash", "basic", "bnf", "c", "c#", "c++", "clojure", "coffeescript", "coq", "css", "dart", "dhall", "diff", "docker", "ebnf", "elixir", "elm", "erlang", "f#", "flow", "fortran", "gherkin", "glsl", "go", "graphql", "groovy", "haskell", "hcl", "html", "idris", "java", "javascript", "json", "julia", "kotlin", "latex", "less", "lisp", "livescript", "llvm ir", "lua", "makefile", "markdown", "markup", "matlab", "mathematica", "mermaid", "nix", "notion formula", "objective-c", "ocaml", "pascal", "perl", "php", "plain text", "powershell", "prolog", "protobuf", "purescript", "python", "r", "racket", "reason", "ruby", "rust", "sass", "scala", "scheme", "scss", "shell", "smalltalk", "solidity", "sql", "swift", "toml", "typescript", "vb.net", "verilog", "vhdl", "visual basic", "webassembly", "xml", "yaml", "java/c/c++/c#"]
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV7(StrictModel):
    code: BlockObjectRequestV7Code
    type_: Literal["code"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV23ToDo(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    checked: bool | None = None
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None

class BlockObjectRequestWithoutChildrenV23(StrictModel):
    to_do: BlockObjectRequestWithoutChildrenV23ToDo
    type_: Literal["to_do"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV26Callout(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    icon: PageIconRequest | None = None
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None

class BlockObjectRequestWithoutChildrenV26(StrictModel):
    callout: BlockObjectRequestWithoutChildrenV26Callout
    type_: Literal["callout"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV7Code(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    language: Literal["abap", "abc", "agda", "arduino", "ascii art", "assembly", "bash", "basic", "bnf", "c", "c#", "c++", "clojure", "coffeescript", "coq", "css", "dart", "dhall", "diff", "docker", "ebnf", "elixir", "elm", "erlang", "f#", "flow", "fortran", "gherkin", "glsl", "go", "graphql", "groovy", "haskell", "hcl", "html", "idris", "java", "javascript", "json", "julia", "kotlin", "latex", "less", "lisp", "livescript", "llvm ir", "lua", "makefile", "markdown", "markup", "matlab", "mathematica", "mermaid", "nix", "notion formula", "objective-c", "ocaml", "pascal", "perl", "php", "plain text", "powershell", "prolog", "protobuf", "purescript", "python", "r", "racket", "reason", "ruby", "rust", "sass", "scala", "scheme", "scss", "shell", "smalltalk", "solidity", "sql", "swift", "toml", "typescript", "vb.net", "verilog", "vhdl", "visual basic", "webassembly", "xml", "yaml", "java/c/c++/c#"]
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)

class BlockObjectRequestWithoutChildrenV7(StrictModel):
    code: BlockObjectRequestWithoutChildrenV7Code
    type_: Literal["code"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV7Code(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    language: Literal["abap", "abc", "agda", "arduino", "ascii art", "assembly", "bash", "basic", "bnf", "c", "c#", "c++", "clojure", "coffeescript", "coq", "css", "dart", "dhall", "diff", "docker", "ebnf", "elixir", "elm", "erlang", "f#", "flow", "fortran", "gherkin", "glsl", "go", "graphql", "groovy", "haskell", "hcl", "html", "idris", "java", "javascript", "json", "julia", "kotlin", "latex", "less", "lisp", "livescript", "llvm ir", "lua", "makefile", "markdown", "markup", "matlab", "mathematica", "mermaid", "nix", "notion formula", "objective-c", "ocaml", "pascal", "perl", "php", "plain text", "powershell", "prolog", "protobuf", "purescript", "python", "r", "racket", "reason", "ruby", "rust", "sass", "scala", "scheme", "scss", "shell", "smalltalk", "solidity", "sql", "swift", "toml", "typescript", "vb.net", "verilog", "vhdl", "visual basic", "webassembly", "xml", "yaml", "java/c/c++/c#"]
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)

class BlockObjectWithSingleLevelOfChildrenRequestV7(StrictModel):
    code: BlockObjectWithSingleLevelOfChildrenRequestV7Code
    type_: Literal["code"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class ContentWithRichTextAndColorRequest(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None

class BlockObjectRequestWithoutChildrenV20(StrictModel):
    bulleted_list_item: ContentWithRichTextAndColorRequest
    type_: Literal["bulleted_list_item"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV21(StrictModel):
    numbered_list_item: ContentWithRichTextAndColorRequest
    type_: Literal["numbered_list_item"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV22(StrictModel):
    quote: ContentWithRichTextAndColorRequest
    type_: Literal["quote"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV24(StrictModel):
    toggle: ContentWithRichTextAndColorRequest
    type_: Literal["toggle"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class ContentWithRichTextColorAndIconRequest(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    icon: PageIconRequest | None = None

class BlockObjectRequestWithoutChildrenV19(StrictModel):
    paragraph: ContentWithRichTextColorAndIconRequest
    type_: Literal["paragraph"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class ContentWithRichTextColorAndIconUpdateRequest(PermissiveModel):
    rich_text: list[RichTextItemRequest] | None = Field(None, max_length=100)
    icon: PageIconRequest | None = None
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None

class ContentWithRichTextRequest(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)

class BlockObjectRequestWithoutChildrenV25(StrictModel):
    template: ContentWithRichTextRequest
    type_: Literal["template"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class ContentWithTableRowRequest(StrictModel):
    cells: list[list[RichTextItemRequest]] = Field(..., max_length=100)

class BlockObjectRequestV14(StrictModel):
    table_row: ContentWithTableRowRequest
    type_: Literal["table_row"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV14(StrictModel):
    table_row: ContentWithTableRowRequest
    type_: Literal["table_row"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV14(StrictModel):
    table_row: ContentWithTableRowRequest
    type_: Literal["table_row"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class CreateACommentBody(PermissiveModel):
    rich_text: list[RichTextItemRequest] = Field(..., description="An array of rich text objects that represent the content of the comment.", max_length=100)
    attachments: list[CreateACommentBodyAttachmentsItem] | None = Field(None, description="An array of files to attach to the comment. Maximum of 3 allowed.", max_length=3)
    display_name: CreateACommentBodyDisplayNameV0 | CreateACommentBodyDisplayNameV1 | CreateACommentBodyDisplayNameV2 | None = Field(None, description="Display name for the comment.")
    v1: CreateACommentBodyV1V01 | CreateACommentBodyV1V11 | None = None

class HeaderContentWithRichTextAndColorRequest(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    is_toggleable: bool | None = None

class BlockObjectRequestWithoutChildrenV15(StrictModel):
    heading_1: HeaderContentWithRichTextAndColorRequest
    type_: Literal["heading_1"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV16(StrictModel):
    heading_2: HeaderContentWithRichTextAndColorRequest
    type_: Literal["heading_2"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV17(StrictModel):
    heading_3: HeaderContentWithRichTextAndColorRequest
    type_: Literal["heading_3"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV18(StrictModel):
    heading_4: HeaderContentWithRichTextAndColorRequest
    type_: Literal["heading_4"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class MediaContentWithFileAndCaptionRequestV0(StrictModel):
    external: ExternalFileRequest
    type_: Literal["external"] | None = Field(None, validation_alias="type", serialization_alias="type")
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)

class MediaContentWithFileAndCaptionRequestV1(StrictModel):
    file_upload: FileUploadIdRequest
    type_: Literal["file_upload"] | None = Field(None, validation_alias="type", serialization_alias="type")
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)

class MediaContentWithFileAndCaptionRequest(PermissiveModel):
    media_content_with_file_and_caption_request: MediaContentWithFileAndCaptionRequestV0 | MediaContentWithFileAndCaptionRequestV1

class BlockObjectRequestV2(StrictModel):
    image: MediaContentWithFileAndCaptionRequest
    type_: Literal["image"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV3(StrictModel):
    video: MediaContentWithFileAndCaptionRequest
    type_: Literal["video"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV4(StrictModel):
    pdf: MediaContentWithFileAndCaptionRequest
    type_: Literal["pdf"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV6(StrictModel):
    audio: MediaContentWithFileAndCaptionRequest
    type_: Literal["audio"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV2(StrictModel):
    image: MediaContentWithFileAndCaptionRequest
    type_: Literal["image"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV3(StrictModel):
    video: MediaContentWithFileAndCaptionRequest
    type_: Literal["video"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV4(StrictModel):
    pdf: MediaContentWithFileAndCaptionRequest
    type_: Literal["pdf"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV6(StrictModel):
    audio: MediaContentWithFileAndCaptionRequest
    type_: Literal["audio"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV2(StrictModel):
    image: MediaContentWithFileAndCaptionRequest
    type_: Literal["image"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV3(StrictModel):
    video: MediaContentWithFileAndCaptionRequest
    type_: Literal["video"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV4(StrictModel):
    pdf: MediaContentWithFileAndCaptionRequest
    type_: Literal["pdf"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV6(StrictModel):
    audio: MediaContentWithFileAndCaptionRequest
    type_: Literal["audio"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class MediaContentWithFileNameAndCaptionRequestV0(StrictModel):
    external: ExternalFileRequest
    type_: Literal["external"] | None = Field(None, validation_alias="type", serialization_alias="type")
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)
    name: str | None = None

class MediaContentWithFileNameAndCaptionRequestV1(StrictModel):
    file_upload: FileUploadIdRequest
    type_: Literal["file_upload"] | None = Field(None, validation_alias="type", serialization_alias="type")
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)
    name: str | None = None

class MediaContentWithFileNameAndCaptionRequest(PermissiveModel):
    media_content_with_file_name_and_caption_request: MediaContentWithFileNameAndCaptionRequestV0 | MediaContentWithFileNameAndCaptionRequestV1

class BlockObjectRequestV5(StrictModel):
    file_: MediaContentWithFileNameAndCaptionRequest = Field(..., validation_alias="file", serialization_alias="file")
    type_: Literal["file"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV5(StrictModel):
    file_: MediaContentWithFileNameAndCaptionRequest = Field(..., validation_alias="file", serialization_alias="file")
    type_: Literal["file"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV5(StrictModel):
    file_: MediaContentWithFileNameAndCaptionRequest = Field(..., validation_alias="file", serialization_alias="file")
    type_: Literal["file"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class MediaContentWithUrlAndCaptionRequest(StrictModel):
    url: str
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV0(StrictModel):
    embed: MediaContentWithUrlAndCaptionRequest
    type_: Literal["embed"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV1(StrictModel):
    bookmark: MediaContentWithUrlAndCaptionRequest
    type_: Literal["bookmark"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV0(StrictModel):
    embed: MediaContentWithUrlAndCaptionRequest
    type_: Literal["embed"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildrenV1(StrictModel):
    bookmark: MediaContentWithUrlAndCaptionRequest
    type_: Literal["bookmark"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestWithoutChildren(PermissiveModel):
    block_object_request_without_children: BlockObjectRequestWithoutChildrenV0 | BlockObjectRequestWithoutChildrenV1 | BlockObjectRequestWithoutChildrenV2 | BlockObjectRequestWithoutChildrenV3 | BlockObjectRequestWithoutChildrenV4 | BlockObjectRequestWithoutChildrenV5 | BlockObjectRequestWithoutChildrenV6 | BlockObjectRequestWithoutChildrenV7 | BlockObjectRequestWithoutChildrenV8 | BlockObjectRequestWithoutChildrenV9 | BlockObjectRequestWithoutChildrenV10 | BlockObjectRequestWithoutChildrenV11 | BlockObjectRequestWithoutChildrenV12 | BlockObjectRequestWithoutChildrenV13 | BlockObjectRequestWithoutChildrenV14 | BlockObjectRequestWithoutChildrenV15 | BlockObjectRequestWithoutChildrenV16 | BlockObjectRequestWithoutChildrenV17 | BlockObjectRequestWithoutChildrenV18 | BlockObjectRequestWithoutChildrenV19 | BlockObjectRequestWithoutChildrenV20 | BlockObjectRequestWithoutChildrenV21 | BlockObjectRequestWithoutChildrenV22 | BlockObjectRequestWithoutChildrenV23 | BlockObjectRequestWithoutChildrenV24 | BlockObjectRequestWithoutChildrenV25 | BlockObjectRequestWithoutChildrenV26 | BlockObjectRequestWithoutChildrenV27

class BlockObjectWithSingleLevelOfChildrenRequestV0(StrictModel):
    embed: MediaContentWithUrlAndCaptionRequest
    type_: Literal["embed"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV1(StrictModel):
    bookmark: MediaContentWithUrlAndCaptionRequest
    type_: Literal["bookmark"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV24ToDo(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    children: list[BlockObjectRequestWithoutChildren] | None = Field(None, max_length=100)
    checked: bool | None = None

class BlockObjectWithSingleLevelOfChildrenRequestV24(StrictModel):
    to_do: BlockObjectWithSingleLevelOfChildrenRequestV24ToDo
    type_: Literal["to_do"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV26Template(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    children: list[BlockObjectRequestWithoutChildren] | None = Field(None, max_length=100)

class BlockObjectWithSingleLevelOfChildrenRequestV26(StrictModel):
    template: BlockObjectWithSingleLevelOfChildrenRequestV26Template
    type_: Literal["template"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV27Callout(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    children: list[BlockObjectRequestWithoutChildren] | None = Field(None, max_length=100)
    icon: PageIconRequest | None = None

class BlockObjectWithSingleLevelOfChildrenRequestV27(StrictModel):
    callout: BlockObjectWithSingleLevelOfChildrenRequestV27Callout
    type_: Literal["callout"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV28SyncedBlock(StrictModel):
    synced_from: BlockObjectWithSingleLevelOfChildrenRequestV28SyncedBlockSyncedFrom | None = Field(...)
    children: list[BlockObjectRequestWithoutChildren] | None = Field(None, max_length=100)

class BlockObjectWithSingleLevelOfChildrenRequestV28(StrictModel):
    synced_block: BlockObjectWithSingleLevelOfChildrenRequestV28SyncedBlock
    type_: Literal["synced_block"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class ContentWithSingleLevelOfChildrenRequest(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    children: list[BlockObjectRequestWithoutChildren] | None = Field(None, max_length=100)

class BlockObjectWithSingleLevelOfChildrenRequestV20(StrictModel):
    bulleted_list_item: ContentWithSingleLevelOfChildrenRequest
    type_: Literal["bulleted_list_item"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV21(StrictModel):
    numbered_list_item: ContentWithSingleLevelOfChildrenRequest
    type_: Literal["numbered_list_item"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV22(StrictModel):
    quote: ContentWithSingleLevelOfChildrenRequest
    type_: Literal["quote"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV25(StrictModel):
    toggle: ContentWithSingleLevelOfChildrenRequest
    type_: Literal["toggle"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class HeaderContentWithSingleLevelOfChildrenRequest(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    is_toggleable: bool | None = None
    children: list[BlockObjectRequestWithoutChildren] | None = Field(None, max_length=100)

class BlockObjectWithSingleLevelOfChildrenRequestV15(StrictModel):
    heading_1: HeaderContentWithSingleLevelOfChildrenRequest
    type_: Literal["heading_1"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV16(StrictModel):
    heading_2: HeaderContentWithSingleLevelOfChildrenRequest
    type_: Literal["heading_2"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV17(StrictModel):
    heading_3: HeaderContentWithSingleLevelOfChildrenRequest
    type_: Literal["heading_3"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV18(StrictModel):
    heading_4: HeaderContentWithSingleLevelOfChildrenRequest
    type_: Literal["heading_4"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class ParagraphWithSingleLevelOfChildrenRequest(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    icon: PageIconRequest | None = None
    children: list[BlockObjectRequestWithoutChildren] | None = Field(None, max_length=100)

class BlockObjectWithSingleLevelOfChildrenRequestV19(StrictModel):
    paragraph: ParagraphWithSingleLevelOfChildrenRequest
    type_: Literal["paragraph"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class PatchPageBodyPropertiesValueV0(StrictModel):
    title: list[RichTextItemRequest] = Field(..., max_length=100)
    type_: Literal["title"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PatchPageBodyPropertiesValueV1(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    type_: Literal["rich_text"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV0(StrictModel):
    title: list[RichTextItemRequest] = Field(..., max_length=100)
    type_: Literal["title"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PostPageBodyPropertiesValueV1(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    type_: Literal["rich_text"] | None = Field(None, validation_alias="type", serialization_alias="type")

class TabItemRequestWithSingleLevelOfChildren(StrictModel):
    paragraph: ParagraphWithSingleLevelOfChildrenRequest
    type_: Literal["paragraph"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class TabItemRequestWithoutChildren(StrictModel):
    paragraph: ContentWithRichTextColorAndIconRequest
    type_: Literal["paragraph"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class TabRequestWithNestedTabItemChildren(StrictModel):
    children: list[TabItemRequestWithSingleLevelOfChildren] = Field(..., min_length=1, max_length=100)

class BlockObjectRequestV11(StrictModel):
    tab: TabRequestWithNestedTabItemChildren
    type_: Literal["tab"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class TabRequestWithTabItemChildren(StrictModel):
    children: list[TabItemRequestWithoutChildren] = Field(..., min_length=1, max_length=100)

class BlockObjectWithSingleLevelOfChildrenRequestV11(StrictModel):
    tab: TabRequestWithTabItemChildren
    type_: Literal["tab"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class TableRowRequest(StrictModel):
    table_row: ContentWithTableRowRequest
    type_: Literal["table_row"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class TableRequestWithTableRowChildren(StrictModel):
    table_width: int = Field(..., ge=1)
    children: list[TableRowRequest] = Field(..., min_length=1, max_length=100)
    has_column_header: bool | None = None
    has_row_header: bool | None = None

class BlockObjectRequestV15(StrictModel):
    table: TableRequestWithTableRowChildren
    type_: Literal["table"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequestV23(StrictModel):
    table: TableRequestWithTableRowChildren
    type_: Literal["table"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectWithSingleLevelOfChildrenRequest(PermissiveModel):
    block_object_with_single_level_of_children_request: BlockObjectWithSingleLevelOfChildrenRequestV0 | BlockObjectWithSingleLevelOfChildrenRequestV1 | BlockObjectWithSingleLevelOfChildrenRequestV2 | BlockObjectWithSingleLevelOfChildrenRequestV3 | BlockObjectWithSingleLevelOfChildrenRequestV4 | BlockObjectWithSingleLevelOfChildrenRequestV5 | BlockObjectWithSingleLevelOfChildrenRequestV6 | BlockObjectWithSingleLevelOfChildrenRequestV7 | BlockObjectWithSingleLevelOfChildrenRequestV8 | BlockObjectWithSingleLevelOfChildrenRequestV9 | BlockObjectWithSingleLevelOfChildrenRequestV10 | BlockObjectWithSingleLevelOfChildrenRequestV11 | BlockObjectWithSingleLevelOfChildrenRequestV12 | BlockObjectWithSingleLevelOfChildrenRequestV13 | BlockObjectWithSingleLevelOfChildrenRequestV14 | BlockObjectWithSingleLevelOfChildrenRequestV15 | BlockObjectWithSingleLevelOfChildrenRequestV16 | BlockObjectWithSingleLevelOfChildrenRequestV17 | BlockObjectWithSingleLevelOfChildrenRequestV18 | BlockObjectWithSingleLevelOfChildrenRequestV19 | BlockObjectWithSingleLevelOfChildrenRequestV20 | BlockObjectWithSingleLevelOfChildrenRequestV21 | BlockObjectWithSingleLevelOfChildrenRequestV22 | BlockObjectWithSingleLevelOfChildrenRequestV23 | BlockObjectWithSingleLevelOfChildrenRequestV24 | BlockObjectWithSingleLevelOfChildrenRequestV25 | BlockObjectWithSingleLevelOfChildrenRequestV26 | BlockObjectWithSingleLevelOfChildrenRequestV27 | BlockObjectWithSingleLevelOfChildrenRequestV28

class BlockObjectRequestV18Heading1(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    is_toggleable: bool | None = None
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV18(StrictModel):
    heading_1: BlockObjectRequestV18Heading1
    type_: Literal["heading_1"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV19Heading2(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    is_toggleable: bool | None = None
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV19(StrictModel):
    heading_2: BlockObjectRequestV19Heading2
    type_: Literal["heading_2"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV20Heading3(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    is_toggleable: bool | None = None
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV20(StrictModel):
    heading_3: BlockObjectRequestV20Heading3
    type_: Literal["heading_3"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV21Heading4(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    is_toggleable: bool | None = None
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV21(StrictModel):
    heading_4: BlockObjectRequestV21Heading4
    type_: Literal["heading_4"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV22Paragraph(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    icon: PageIconRequest | None = None
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV22(StrictModel):
    paragraph: BlockObjectRequestV22Paragraph
    type_: Literal["paragraph"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV23BulletedListItem(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV23(StrictModel):
    bulleted_list_item: BlockObjectRequestV23BulletedListItem
    type_: Literal["bulleted_list_item"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV24NumberedListItem(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV24(StrictModel):
    numbered_list_item: BlockObjectRequestV24NumberedListItem
    type_: Literal["numbered_list_item"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV25Quote(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV25(StrictModel):
    quote: BlockObjectRequestV25Quote
    type_: Literal["quote"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV26ToDo(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)
    checked: bool | None = None

class BlockObjectRequestV26(StrictModel):
    to_do: BlockObjectRequestV26ToDo
    type_: Literal["to_do"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV27Toggle(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV27(StrictModel):
    toggle: BlockObjectRequestV27Toggle
    type_: Literal["toggle"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV28Template(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV28(StrictModel):
    template: BlockObjectRequestV28Template
    type_: Literal["template"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV29Callout(StrictModel):
    rich_text: list[RichTextItemRequest] = Field(..., max_length=100)
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)
    icon: PageIconRequest | None = None

class BlockObjectRequestV29(StrictModel):
    callout: BlockObjectRequestV29Callout
    type_: Literal["callout"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequestV30SyncedBlock(StrictModel):
    synced_from: BlockObjectRequestV30SyncedBlockSyncedFrom | None = Field(...)
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] | None = Field(None, max_length=100)

class BlockObjectRequestV30(StrictModel):
    synced_block: BlockObjectRequestV30SyncedBlock
    type_: Literal["synced_block"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class ColumnWithChildrenRequest(StrictModel):
    children: list[BlockObjectWithSingleLevelOfChildrenRequest] = Field(..., max_length=100)
    width_ratio: float | None = Field(None, description="Ratio between 0 and 1 of the width of this column relative to all columns in the list. If not provided, uses an equal width.", gt=0, lt=1)

class BlockObjectRequestV17(StrictModel):
    column: ColumnWithChildrenRequest
    type_: Literal["column"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class ColumnBlockWithChildrenRequest(StrictModel):
    column: ColumnWithChildrenRequest
    type_: Literal["column"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class ColumnListRequest(StrictModel):
    children: list[ColumnBlockWithChildrenRequest] = Field(..., min_length=2, max_length=100)

class BlockObjectRequestV16(StrictModel):
    column_list: ColumnListRequest
    type_: Literal["column_list"] | None = Field(None, validation_alias="type", serialization_alias="type")
    object_: Literal["block"] | None = Field(None, validation_alias="object", serialization_alias="object")

class BlockObjectRequest(PermissiveModel):
    block_object_request: BlockObjectRequestV0 | BlockObjectRequestV1 | BlockObjectRequestV2 | BlockObjectRequestV3 | BlockObjectRequestV4 | BlockObjectRequestV5 | BlockObjectRequestV6 | BlockObjectRequestV7 | BlockObjectRequestV8 | BlockObjectRequestV9 | BlockObjectRequestV10 | BlockObjectRequestV11 | BlockObjectRequestV12 | BlockObjectRequestV13 | BlockObjectRequestV14 | BlockObjectRequestV15 | BlockObjectRequestV16 | BlockObjectRequestV17 | BlockObjectRequestV18 | BlockObjectRequestV19 | BlockObjectRequestV20 | BlockObjectRequestV21 | BlockObjectRequestV22 | BlockObjectRequestV23 | BlockObjectRequestV24 | BlockObjectRequestV25 | BlockObjectRequestV26 | BlockObjectRequestV27 | BlockObjectRequestV28 | BlockObjectRequestV29 | BlockObjectRequestV30

class TimelineArrowsByRequest(PermissiveModel):
    property_id: str | None = Field(None, description="Relation property ID used for dependency arrows, or null to disable arrows.")

class TimelinePreferenceRequest(PermissiveModel):
    zoom_level: Literal["hours", "day", "week", "bi_week", "month", "quarter", "year", "5_years"] = Field(..., description="Zoom level for the timeline.")
    center_timestamp: int | None = Field(None, description="Timestamp (ms) to center the timeline view on.")

class TimestampCreatedTimeFilter(StrictModel):
    created_time: ExistencePropertyFilter
    timestamp: Literal["created_time"]
    type_: Literal["created_time"] | None = Field(None, validation_alias="type", serialization_alias="type")

class TimestampLastEditedTimeFilter(StrictModel):
    last_edited_time: ExistencePropertyFilter
    timestamp: Literal["last_edited_time"]
    type_: Literal["last_edited_time"] | None = Field(None, validation_alias="type", serialization_alias="type")

class TitlePropertyConfigurationRequest(PermissiveModel):
    type_: Literal["title"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `title`")
    title: EmptyObject

class UniqueIdPropertyConfigurationRequestUniqueId(PermissiveModel):
    prefix: str | None = None

class UniqueIdPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["unique_id"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `unique_id`")
    unique_id: UniqueIdPropertyConfigurationRequestUniqueId

class UpdateABlockBodyV0V10(StrictModel):
    breadcrumb: EmptyObject
    type_: Literal["breadcrumb"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V11(StrictModel):
    tab: EmptyObject
    type_: Literal["tab"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V12TableOfContents(StrictModel):
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None

class UpdateABlockBodyV0V12(StrictModel):
    table_of_contents: UpdateABlockBodyV0V12TableOfContents
    type_: Literal["table_of_contents"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V13LinkToPageV0(StrictModel):
    page_id: str
    type_: Literal["page_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class UpdateABlockBodyV0V13LinkToPageV1(StrictModel):
    database_id: str
    type_: Literal["database_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class UpdateABlockBodyV0V13LinkToPageV2(StrictModel):
    comment_id: str
    type_: Literal["comment_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class UpdateABlockBodyV0V13(StrictModel):
    link_to_page: UpdateABlockBodyV0V13LinkToPageV0 | UpdateABlockBodyV0V13LinkToPageV1 | UpdateABlockBodyV0V13LinkToPageV2
    type_: Literal["link_to_page"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V14(StrictModel):
    table_row: ContentWithTableRowRequest
    type_: Literal["table_row"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V15(StrictModel):
    heading_1: HeaderContentWithRichTextAndColorRequest
    type_: Literal["heading_1"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V16(StrictModel):
    heading_2: HeaderContentWithRichTextAndColorRequest
    type_: Literal["heading_2"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V17(StrictModel):
    heading_3: HeaderContentWithRichTextAndColorRequest
    type_: Literal["heading_3"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V18(StrictModel):
    heading_4: HeaderContentWithRichTextAndColorRequest
    type_: Literal["heading_4"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V19(StrictModel):
    paragraph: ContentWithRichTextColorAndIconUpdateRequest
    type_: Literal["paragraph"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V20(StrictModel):
    bulleted_list_item: ContentWithRichTextAndColorRequest
    type_: Literal["bulleted_list_item"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V21(StrictModel):
    numbered_list_item: ContentWithRichTextAndColorRequest
    type_: Literal["numbered_list_item"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V22(StrictModel):
    quote: ContentWithRichTextAndColorRequest
    type_: Literal["quote"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V23ToDo(PermissiveModel):
    rich_text: list[RichTextItemRequest] | None = Field(None, max_length=100)
    checked: bool | None = None
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None

class UpdateABlockBodyV0V23(StrictModel):
    to_do: UpdateABlockBodyV0V23ToDo
    type_: Literal["to_do"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V24(StrictModel):
    toggle: ContentWithRichTextAndColorRequest
    type_: Literal["toggle"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V25(StrictModel):
    template: ContentWithRichTextRequest
    type_: Literal["template"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V26Callout(PermissiveModel):
    rich_text: list[RichTextItemRequest] | None = Field(None, max_length=100)
    icon: PageIconRequest | None = None
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red", "default_background", "gray_background", "brown_background", "orange_background", "yellow_background", "green_background", "blue_background", "purple_background", "pink_background", "red_background"] | None = None

class UpdateABlockBodyV0V26(StrictModel):
    callout: UpdateABlockBodyV0V26Callout
    type_: Literal["callout"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V27SyncedBlockSyncedFrom(StrictModel):
    block_id: str
    type_: Literal["block_id"] | None = Field(None, validation_alias="type", serialization_alias="type")

class UpdateABlockBodyV0V27SyncedBlock(StrictModel):
    synced_from: UpdateABlockBodyV0V27SyncedBlockSyncedFrom | None = Field(...)

class UpdateABlockBodyV0V27(StrictModel):
    synced_block: UpdateABlockBodyV0V27SyncedBlock
    type_: Literal["synced_block"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V28Table(StrictModel):
    has_column_header: bool | None = None
    has_row_header: bool | None = None

class UpdateABlockBodyV0V28(StrictModel):
    table: UpdateABlockBodyV0V28Table
    type_: Literal["table"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V29Column(StrictModel):
    width_ratio: float | None = Field(None, description="Ratio between 0 and 1 of the width of this column relative to all columns in the list. If not provided, uses an equal width.", gt=0, lt=1)

class UpdateABlockBodyV0V29(StrictModel):
    column: UpdateABlockBodyV0V29Column
    type_: Literal["column"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V7Code(StrictModel):
    rich_text: list[RichTextItemRequest] | None = Field(None, max_length=100)
    language: Literal["abap", "abc", "agda", "arduino", "ascii art", "assembly", "bash", "basic", "bnf", "c", "c#", "c++", "clojure", "coffeescript", "coq", "css", "dart", "dhall", "diff", "docker", "ebnf", "elixir", "elm", "erlang", "f#", "flow", "fortran", "gherkin", "glsl", "go", "graphql", "groovy", "haskell", "hcl", "html", "idris", "java", "javascript", "json", "julia", "kotlin", "latex", "less", "lisp", "livescript", "llvm ir", "lua", "makefile", "markdown", "markup", "matlab", "mathematica", "mermaid", "nix", "notion formula", "objective-c", "ocaml", "pascal", "perl", "php", "plain text", "powershell", "prolog", "protobuf", "purescript", "python", "r", "racket", "reason", "ruby", "rust", "sass", "scala", "scheme", "scss", "shell", "smalltalk", "solidity", "sql", "swift", "toml", "typescript", "vb.net", "verilog", "vhdl", "visual basic", "webassembly", "xml", "yaml", "java/c/c++/c#"] | None = None
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)

class UpdateABlockBodyV0V7(StrictModel):
    code: UpdateABlockBodyV0V7Code
    type_: Literal["code"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V8(StrictModel):
    equation: ContentWithExpressionRequest
    type_: Literal["equation"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V9(StrictModel):
    divider: EmptyObject
    type_: Literal["divider"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV1(StrictModel):
    in_trash: bool | None = None

class UpdateADataSourceBodyPropertiesValueV0V1V0Number1(PermissiveModel):
    format_: str | None = Field(None, validation_alias="format", serialization_alias="format")

class UpdateADataSourceBodyPropertiesValueV0V1V01(PermissiveModel):
    type_: Literal["number"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `number`")
    number: UpdateADataSourceBodyPropertiesValueV0V1V0Number1

class UpdateADataSourceBodyPropertiesValueV0V1V101(PermissiveModel):
    type_: Literal["url"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `url`")
    url: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V111(PermissiveModel):
    type_: Literal["people"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `people`")
    people: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V121(PermissiveModel):
    type_: Literal["files"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `files`")
    files: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V131(PermissiveModel):
    type_: Literal["email"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `email`")
    email: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V141(PermissiveModel):
    type_: Literal["phone_number"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `phone_number`")
    phone_number: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V151(PermissiveModel):
    type_: Literal["date"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `date`")
    date: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V161(PermissiveModel):
    type_: Literal["checkbox"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `checkbox`")
    checkbox: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V171(PermissiveModel):
    type_: Literal["created_by"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `created_by`")
    created_by: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V181(PermissiveModel):
    type_: Literal["created_time"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `created_time`")
    created_time: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V191(PermissiveModel):
    type_: Literal["last_edited_by"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `last_edited_by`")
    last_edited_by: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V1Formula1(PermissiveModel):
    expression: str | None = None

class UpdateADataSourceBodyPropertiesValueV0V1V110(PermissiveModel):
    type_: Literal["formula"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `formula`")
    formula: UpdateADataSourceBodyPropertiesValueV0V1V1Formula1

class UpdateADataSourceBodyPropertiesValueV0V1V201(PermissiveModel):
    type_: Literal["last_edited_time"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `last_edited_time`")
    last_edited_time: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V211(PermissiveModel):
    type_: Literal["place"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `place`")
    place: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V2SelectOptionsItemV1V03(PermissiveModel):
    name: str
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class UpdateADataSourceBodyPropertiesValueV0V1V2SelectOptionsItemV1V13(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateADataSourceBodyPropertiesValueV0V1V2SelectOptionsItem1(PermissiveModel):
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None
    v1: UpdateADataSourceBodyPropertiesValueV0V1V2SelectOptionsItemV1V03 | UpdateADataSourceBodyPropertiesValueV0V1V2SelectOptionsItemV1V13 | None = None

class UpdateADataSourceBodyPropertiesValueV0V1V2Select1(PermissiveModel):
    options: list[UpdateADataSourceBodyPropertiesValueV0V1V2SelectOptionsItem1] | None = Field(None, max_length=100)

class UpdateADataSourceBodyPropertiesValueV0V1V22(PermissiveModel):
    type_: Literal["select"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `select`")
    select: UpdateADataSourceBodyPropertiesValueV0V1V2Select1

class UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelectOptionsItemV1V03(PermissiveModel):
    name: str
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelectOptionsItemV1V13(PermissiveModel):
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    name: str | None = None

class UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelectOptionsItem1(PermissiveModel):
    color: Literal["default", "gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"] | None = None
    description: str | None = None
    v1: UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelectOptionsItemV1V03 | UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelectOptionsItemV1V13 | None = None

class UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelect1(PermissiveModel):
    options: list[UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelectOptionsItem1] | None = Field(None, max_length=100)

class UpdateADataSourceBodyPropertiesValueV0V1V31(PermissiveModel):
    type_: Literal["multi_select"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `multi_select`")
    multi_select: UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelect1

class UpdateADataSourceBodyPropertiesValueV0V1V41(PermissiveModel):
    type_: Literal["status"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `status`")
    status: StatusPropertyConfigUpdateRequest

class UpdateADataSourceBodyPropertiesValueV0V1V5RelationV1V03(PermissiveModel):
    type_: Literal["single_property"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `single_property`")
    single_property: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V5RelationV1V1DualProperty3(PermissiveModel):
    synced_property_id: str | None = None
    synced_property_name: str | None = None

class UpdateADataSourceBodyPropertiesValueV0V1V5RelationV1V13(PermissiveModel):
    type_: Literal["dual_property"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `dual_property`")
    dual_property: UpdateADataSourceBodyPropertiesValueV0V1V5RelationV1V1DualProperty3

class UpdateADataSourceBodyPropertiesValueV0V1V5Relation1(PermissiveModel):
    data_source_id: str
    v1: UpdateADataSourceBodyPropertiesValueV0V1V5RelationV1V03 | UpdateADataSourceBodyPropertiesValueV0V1V5RelationV1V13 | None = None

class UpdateADataSourceBodyPropertiesValueV0V1V51(PermissiveModel):
    type_: Literal["relation"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `relation`")
    relation: UpdateADataSourceBodyPropertiesValueV0V1V5Relation1

class UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V03(PermissiveModel):
    relation_property_name: str
    rollup_property_name: str

class UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V13(PermissiveModel):
    relation_property_id: str
    rollup_property_name: str

class UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V23(PermissiveModel):
    relation_property_name: str
    rollup_property_id: str

class UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V33(PermissiveModel):
    relation_property_id: str
    rollup_property_id: str

class UpdateADataSourceBodyPropertiesValueV0V1V6Rollup1(PermissiveModel):
    function: Literal["count", "count_values", "empty", "not_empty", "unique", "show_unique", "percent_empty", "percent_not_empty", "sum", "average", "median", "min", "max", "range", "earliest_date", "latest_date", "date_range", "checked", "unchecked", "percent_checked", "percent_unchecked", "count_per_group", "percent_per_group", "show_original"] = Field(..., description="The function to use for the rollup, e.g. count, count_values, percent_not_empty, max.")
    v1: UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V03 | UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V13 | UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V23 | UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V33 | None = None

class UpdateADataSourceBodyPropertiesValueV0V1V61(PermissiveModel):
    type_: Literal["rollup"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `rollup`")
    rollup: UpdateADataSourceBodyPropertiesValueV0V1V6Rollup1

class UpdateADataSourceBodyPropertiesValueV0V1V7UniqueId1(PermissiveModel):
    prefix: str | None = None

class UpdateADataSourceBodyPropertiesValueV0V1V71(PermissiveModel):
    type_: Literal["unique_id"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `unique_id`")
    unique_id: UpdateADataSourceBodyPropertiesValueV0V1V7UniqueId1

class UpdateADataSourceBodyPropertiesValueV0V1V81(PermissiveModel):
    type_: Literal["title"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `title`")
    title: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0V1V91(PermissiveModel):
    type_: Literal["rich_text"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `rich_text`")
    rich_text: EmptyObject

class UpdateADataSourceBodyPropertiesValueV0(PermissiveModel):
    name: str | None = Field(None, description="The name of the property.")
    description: str | None = Field(None, description="The description of the property.")
    v1: UpdateADataSourceBodyPropertiesValueV0V1V01 | UpdateADataSourceBodyPropertiesValueV0V1V110 | UpdateADataSourceBodyPropertiesValueV0V1V22 | UpdateADataSourceBodyPropertiesValueV0V1V31 | UpdateADataSourceBodyPropertiesValueV0V1V41 | UpdateADataSourceBodyPropertiesValueV0V1V51 | UpdateADataSourceBodyPropertiesValueV0V1V61 | UpdateADataSourceBodyPropertiesValueV0V1V71 | UpdateADataSourceBodyPropertiesValueV0V1V81 | UpdateADataSourceBodyPropertiesValueV0V1V91 | UpdateADataSourceBodyPropertiesValueV0V1V101 | UpdateADataSourceBodyPropertiesValueV0V1V111 | UpdateADataSourceBodyPropertiesValueV0V1V121 | UpdateADataSourceBodyPropertiesValueV0V1V131 | UpdateADataSourceBodyPropertiesValueV0V1V141 | UpdateADataSourceBodyPropertiesValueV0V1V151 | UpdateADataSourceBodyPropertiesValueV0V1V161 | UpdateADataSourceBodyPropertiesValueV0V1V171 | UpdateADataSourceBodyPropertiesValueV0V1V181 | UpdateADataSourceBodyPropertiesValueV0V1V191 | UpdateADataSourceBodyPropertiesValueV0V1V201 | UpdateADataSourceBodyPropertiesValueV0V1V211 | None = None

class UpdateADataSourceBodyPropertiesValueV1(PermissiveModel):
    name: str = Field(..., description="The new name of the property.")

class UpdateDatabaseBodyParentV1V01(PermissiveModel):
    type_: Literal["page_id"] = Field(..., validation_alias="type", serialization_alias="type", description="Always `page_id`")
    page_id: str

class UpdateDatabaseBodyParentV1V11(PermissiveModel):
    type_: Literal["workspace"] = Field(..., validation_alias="type", serialization_alias="type", description="Always `workspace`")
    workspace: Literal[True] = Field(..., description="Always `true`")

class UpdateDatabaseBodyParent(PermissiveModel):
    """The parent page or workspace to move the database to. If not provided, the database will not be moved."""
    type_: Literal["page_id", "workspace"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of parent.")
    v1: UpdateDatabaseBodyParentV1V01 | UpdateDatabaseBodyParentV1V11 | None = None

class UpdateMediaContentWithFileAndCaptionRequest(StrictModel):
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)
    external: ExternalFileRequest | None = None
    file_upload: FileUploadIdRequest | None = None

class UpdateABlockBodyV0V2(StrictModel):
    image: UpdateMediaContentWithFileAndCaptionRequest
    type_: Literal["image"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V3(StrictModel):
    video: UpdateMediaContentWithFileAndCaptionRequest
    type_: Literal["video"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V4(StrictModel):
    pdf: UpdateMediaContentWithFileAndCaptionRequest
    type_: Literal["pdf"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V6(StrictModel):
    audio: UpdateMediaContentWithFileAndCaptionRequest
    type_: Literal["audio"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateMediaContentWithFileNameAndCaptionRequest(StrictModel):
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)
    external: ExternalFileRequest | None = None
    file_upload: FileUploadIdRequest | None = None
    name: str | None = None

class UpdateABlockBodyV0V5(StrictModel):
    file_: UpdateMediaContentWithFileNameAndCaptionRequest = Field(..., validation_alias="file", serialization_alias="file")
    type_: Literal["file"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateMediaContentWithUrlAndCaptionRequest(StrictModel):
    url: str | None = None
    caption: list[RichTextItemRequest] | None = Field(None, max_length=100)

class UpdateABlockBodyV0V0(StrictModel):
    embed: UpdateMediaContentWithUrlAndCaptionRequest
    type_: Literal["embed"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdateABlockBodyV0V1(StrictModel):
    bookmark: UpdateMediaContentWithUrlAndCaptionRequest
    type_: Literal["bookmark"] | None = Field(None, validation_alias="type", serialization_alias="type")
    in_trash: bool | None = None

class UpdatePageMarkdownBodyInsertContent(PermissiveModel):
    """Insert new content into the page."""
    content: str = Field(..., description="The enhanced markdown content to insert into the page.")
    after: str | None = Field(None, description="Selection of existing content to insert after, using the ellipsis format (\"start text...end text\"). Omit to append at the end of the page.")

class UpdatePageMarkdownBodyReplaceContent(PermissiveModel):
    """Replace the entire page content with new markdown."""
    new_str: str = Field(..., description="The new enhanced markdown content to replace the entire page content.")
    allow_deleting_content: bool | None = Field(None, description="Set to true to allow the operation to delete child pages or databases. Defaults to false.")

class UpdatePageMarkdownBodyReplaceContentRange(PermissiveModel):
    """Replace a range of content in the page."""
    content: str = Field(..., description="The new enhanced markdown content to replace the matched range.")
    content_range: str = Field(..., description="Selection of existing content to replace, using the ellipsis format (\"start text...end text\").")
    allow_deleting_content: bool | None = Field(None, description="Set to true to allow the operation to delete child pages or databases. Defaults to false.")

class UpdatePageMarkdownBodyUpdateContentContentUpdatesItem(PermissiveModel):
    old_str: str = Field(..., description="The existing content string to find and replace. Must exactly match the page content.")
    new_str: str = Field(..., description="The new content string to replace old_str with.")
    replace_all_matches: bool | None = Field(None, description="If true, replaces all occurrences of old_str. If false (default), the operation fails if there are multiple matches.")

class UpdatePageMarkdownBodyUpdateContent(PermissiveModel):
    """Update specific content using search-and-replace operations."""
    content_updates: list[UpdatePageMarkdownBodyUpdateContentContentUpdatesItem] = Field(..., description="An array of search-and-replace operations, each with old_str (content to find) and new_str (replacement content).", max_length=100)
    allow_deleting_content: bool | None = Field(None, description="Set to true to allow the operation to delete child pages or databases. Defaults to false.")

class UrlPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["url"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `url`")
    url: EmptyObject

class VerificationPropertyConfigurationRequest(PermissiveModel):
    type_: Literal["verification"] | None = Field(None, validation_alias="type", serialization_alias="type", description="Always `verification`")
    verification: EmptyObject

class PropertyConfigurationRequest(PermissiveModel):
    description: str | None = Field(None, description="The description of the property.")
    v1: NumberPropertyConfigurationRequest | FormulaPropertyConfigurationRequest | SelectPropertyConfigurationRequest | MultiSelectPropertyConfigurationRequest | StatusPropertyConfigurationRequest | RelationPropertyConfigurationRequest | RollupPropertyConfigurationRequest | UniqueIdPropertyConfigurationRequest | TitlePropertyConfigurationRequest | RichTextPropertyConfigurationRequest | UrlPropertyConfigurationRequest | PeoplePropertyConfigurationRequest | FilesPropertyConfigurationRequest | EmailPropertyConfigurationRequest | PhoneNumberPropertyConfigurationRequest | DatePropertyConfigurationRequest | CheckboxPropertyConfigurationRequest | CreatedByPropertyConfigurationRequest | CreatedTimePropertyConfigurationRequest | LastEditedByPropertyConfigurationRequest | LastEditedTimePropertyConfigurationRequest | ButtonPropertyConfigurationRequest | LocationPropertyConfigurationRequest | VerificationPropertyConfigurationRequest | LastVisitedTimePropertyConfigurationRequest | PlacePropertyConfigurationRequest | None = None

class VerificationPropertyStatusFilter(StrictModel):
    status: Literal["verified", "expired", "none"]

class PropertyFilterV21(StrictModel):
    verification: VerificationPropertyStatusFilter
    property_: str = Field(..., validation_alias="property", serialization_alias="property")
    type_: Literal["verification"] | None = Field(None, validation_alias="type", serialization_alias="type")

class PropertyFilter(PermissiveModel):
    property_filter: PropertyFilterV0 | PropertyFilterV1 | PropertyFilterV2 | PropertyFilterV3 | PropertyFilterV4 | PropertyFilterV5 | PropertyFilterV6 | PropertyFilterV7 | PropertyFilterV8 | PropertyFilterV9 | PropertyFilterV10 | PropertyFilterV11 | PropertyFilterV12 | PropertyFilterV13 | PropertyFilterV14 | PropertyFilterV15 | PropertyFilterV16 | PropertyFilterV17 | PropertyFilterV18 | PropertyFilterV19 | PropertyFilterV20 | PropertyFilterV21

class PropertyOrTimestampFilterArray(RootModel[list[PropertyFilter | TimestampCreatedTimeFilter | TimestampLastEditedTimeFilter]]):
    pass

class GroupFilterOperatorArrayItemV1V0(PermissiveModel):
    or_: PropertyOrTimestampFilterArray = Field(..., validation_alias="or", serialization_alias="or")

class GroupFilterOperatorArrayItemV1V1(PermissiveModel):
    and_: PropertyOrTimestampFilterArray = Field(..., validation_alias="and", serialization_alias="and")

class GroupFilterOperatorArray(RootModel[list[PropertyFilter | TimestampCreatedTimeFilter | TimestampLastEditedTimeFilter | GroupFilterOperatorArrayItemV1V0 | GroupFilterOperatorArrayItemV1V1]]):
    pass

class PostDatabaseQueryBodyFilterV0V0(PermissiveModel):
    or_: GroupFilterOperatorArray = Field(..., validation_alias="or", serialization_alias="or")

class PostDatabaseQueryBodyFilterV0V1(PermissiveModel):
    and_: GroupFilterOperatorArray = Field(..., validation_alias="and", serialization_alias="and")

class ViewFilterRequest(RootModel[dict[str, Any]]):
    pass

class ViewPositionRequestV0(PermissiveModel):
    type_: Literal["start"] = Field(..., validation_alias="type", serialization_alias="type", description="Position type. \"start\" places the view as the first tab.")

class ViewPositionRequestV1(PermissiveModel):
    type_: Literal["end"] = Field(..., validation_alias="type", serialization_alias="type", description="Position type. \"end\" places the view as the last tab.")

class ViewPositionRequestV2(PermissiveModel):
    type_: Literal["after_view"] = Field(..., validation_alias="type", serialization_alias="type", description="Position type. \"after_view\" places the new view immediately after the specified view.")
    view_id: str = Field(..., description="The ID of an existing view in the database. The new view will be placed after this view.")

class ViewPositionRequest(PermissiveModel):
    """Position of the new view in the database's view tab bar."""
    view_position_request: ViewPositionRequestV0 | ViewPositionRequestV1 | ViewPositionRequestV2

class ViewPropertyConfigRequest(PermissiveModel):
    property_id: str = Field(..., description="Property ID (stable identifier).")
    visible: bool | None = Field(None, description="Whether this property is visible in the view.")
    width: int | None = Field(None, description="Width of the property column in pixels (table view only).", ge=1)
    wrap: bool | None = Field(None, description="Whether to wrap content in this property cell/card.")
    status_show_as: Literal["select", "checkbox"] | None = Field(None, description="How to display status properties (select dropdown or checkbox).")
    card_property_width_mode: Literal["full_line", "inline"] | None = Field(None, description="Property width mode in compact card layouts (board/gallery).")
    date_format: Literal["full", "short", "month_day_year", "day_month_year", "year_month_day", "relative"] | None = Field(None, description="Date display format (date properties only).")
    time_format: Literal["12_hour", "24_hour", "hidden"] | None = Field(None, description="Time display format (date properties only).")

class BoardViewConfigRequest(PermissiveModel):
    type_: Literal["board"] = Field(..., validation_alias="type", serialization_alias="type", description="The view type. Must be \"board\".")
    group_by: GroupByConfigRequest = Field(..., description="Group-by configuration for board columns.")
    sub_group_by: GroupByConfigRequest | None = Field(None, description="Secondary group-by configuration for sub-grouping within columns. Pass null to remove sub-grouping.")
    properties: list[ViewPropertyConfigRequest] | None = Field(None, description="Property visibility and display configuration on cards. Pass null to clear.", max_length=100)
    cover: CoverConfigRequest | None = Field(None, description="Cover image configuration for cards. Pass null to clear.")
    cover_size: Literal["small", "medium", "large"] | None = Field(None, description="Size of the cover image on cards. Pass null to clear.")
    cover_aspect: Literal["contain", "cover"] | None = Field(None, description="Aspect ratio mode for cover images. \"contain\" fits the image, \"cover\" fills the area. Pass null to clear.")
    card_layout: Literal["list", "compact"] | None = Field(None, description="Card layout mode. \"list\" shows full cards, \"compact\" shows condensed cards. Pass null to clear.")

class CalendarViewConfigRequest(PermissiveModel):
    type_: Literal["calendar"] = Field(..., validation_alias="type", serialization_alias="type", description="The view type. Must be \"calendar\".")
    date_property_id: str = Field(..., description="Property ID of the date property used to position items on the calendar.")
    properties: list[ViewPropertyConfigRequest] | None = Field(None, description="Property visibility and display configuration on calendar cards. Pass null to clear.", max_length=100)
    view_range: Literal["week", "month"] | None = Field(None, description="Default calendar range. \"week\" shows a week view, \"month\" shows a month view. Pass null to clear.")
    show_weekends: bool | None = Field(None, description="Whether to show weekend days. Pass null to clear.")

class GalleryViewConfigRequest(PermissiveModel):
    type_: Literal["gallery"] = Field(..., validation_alias="type", serialization_alias="type", description="The view type. Must be \"gallery\".")
    properties: list[ViewPropertyConfigRequest] | None = Field(None, description="Property visibility and display configuration on gallery cards. Pass null to clear.", max_length=100)
    cover: CoverConfigRequest | None = Field(None, description="Cover image configuration for cards. Pass null to clear.")
    cover_size: Literal["small", "medium", "large"] | None = Field(None, description="Size of the cover image on cards. Pass null to clear.")
    cover_aspect: Literal["contain", "cover"] | None = Field(None, description="Aspect ratio mode for cover images. \"contain\" fits the image, \"cover\" fills the area. Pass null to clear.")
    card_layout: Literal["list", "compact"] | None = Field(None, description="Card layout mode. \"list\" shows full cards, \"compact\" shows condensed cards. Pass null to clear.")

class ListViewConfigRequest(PermissiveModel):
    type_: Literal["list"] = Field(..., validation_alias="type", serialization_alias="type", description="The view type. Must be \"list\".")
    properties: list[ViewPropertyConfigRequest] | None = Field(None, description="Property visibility and display configuration. Pass null to clear.", max_length=100)

class MapViewConfigRequest(PermissiveModel):
    type_: Literal["map"] = Field(..., validation_alias="type", serialization_alias="type", description="The view type. Must be \"map\".")
    height: Literal["small", "medium", "large", "extra_large"] | None = Field(None, description="Map display height. Pass null to clear.")
    map_by: str | None = Field(None, description="Property ID of the location property used to position items on the map. Pass null to clear.")
    properties: list[ViewPropertyConfigRequest] | None = Field(None, description="Property visibility and display configuration on map pin cards. Pass null to clear.", max_length=100)

class TableViewConfigRequest(PermissiveModel):
    type_: Literal["table"] = Field(..., validation_alias="type", serialization_alias="type", description="The view type. Must be \"table\".")
    properties: list[ViewPropertyConfigRequest] | None = Field(None, description="Property visibility and display configuration. Pass null to clear.", max_length=100)
    group_by: GroupByConfigRequest | None = Field(None, description="Group-by configuration for the table. Pass null to remove grouping.")
    subtasks: SubtaskConfigRequest | None = Field(None, description="Subtask (sub-item) configuration. Pass null to reset subtask config to defaults (which may show subtasks). Use `{ \"display_mode\": \"disabled\" }` to explicitly disable subtasks.")
    wrap_cells: bool | None = Field(None, description="Whether to wrap cell content in the table.")
    frozen_column_index: int | None = Field(None, description="Number of columns frozen from the left side of the table.", ge=0)
    show_vertical_lines: bool | None = Field(None, description="Whether to show vertical grid lines between columns.")

class TimelineViewConfigRequest(PermissiveModel):
    type_: Literal["timeline"] = Field(..., validation_alias="type", serialization_alias="type", description="The view type. Must be \"timeline\".")
    date_property_id: str = Field(..., description="Property ID of the date property used for the start of timeline items.")
    end_date_property_id: str | None = Field(None, description="Property ID of the date property used for the end of timeline items. Pass null to clear.")
    properties: list[ViewPropertyConfigRequest] | None = Field(None, description="Property visibility and display configuration on timeline items. Pass null to clear.", max_length=100)
    show_table: bool | None = Field(None, description="Whether to show the table panel alongside the timeline. Pass null to clear.")
    table_properties: list[ViewPropertyConfigRequest] | None = Field(None, description="Property configuration for the table panel (when show_table is true). Pass null to clear.", max_length=100)
    preference: TimelinePreferenceRequest | None = Field(None, description="Timeline display preferences (zoom level and center position). Pass null to clear.")
    arrows_by: TimelineArrowsByRequest | None = Field(None, description="Configuration for dependency arrows between timeline items. Pass null to clear.")
    color_by: bool | None = Field(None, description="Whether to color timeline items by a property. Pass null to clear.")

class ViewConfigRequest(PermissiveModel):
    """View configuration, discriminated by the type field."""
    view_config_request: TableViewConfigRequest | BoardViewConfigRequest | CalendarViewConfigRequest | TimelineViewConfigRequest | GalleryViewConfigRequest | ListViewConfigRequest | MapViewConfigRequest | FormViewConfigRequest | ChartViewConfigRequest

class ViewPropertySortRequest(PermissiveModel):
    property_: str = Field(..., validation_alias="property", serialization_alias="property", description="Property name or ID to sort by.")
    direction: Literal["ascending", "descending"] = Field(..., description="Sort direction.")

class ViewSortRequest(RootModel[dict[str, Any]]):
    pass

class ViewSortsRequest(RootModel[list[ViewSortRequest]]):
    pass

class WidgetPlacementRequestV0(PermissiveModel):
    type_: Literal["new_row"] = Field(..., validation_alias="type", serialization_alias="type", description="Placement type. \"new_row\" creates a new row containing the widget.")
    row_index: int | None = Field(None, description="The 0-based row position to insert the new row at. If omitted, the new row is appended at the end.", ge=0)

class WidgetPlacementRequestV1(PermissiveModel):
    type_: Literal["existing_row"] = Field(..., validation_alias="type", serialization_alias="type", description="Placement type. \"existing_row\" adds the widget to an existing row (side-by-side with other widgets).")
    row_index: int = Field(..., description="The 0-based index of the existing row to add the widget to.", ge=0)

class WidgetPlacementRequest(PermissiveModel):
    """Where to place the new widget in the dashboard. "new_row" creates a new row, "existing_row" adds to an existing row side-by-side with other widgets."""
    widget_placement_request: WidgetPlacementRequestV0 | WidgetPlacementRequestV1


# Rebuild models to resolve forward references (required for circular refs)
AnnotationRequest.model_rebuild()
BlockObjectRequest.model_rebuild()
BlockObjectRequestV0.model_rebuild()
BlockObjectRequestV1.model_rebuild()
BlockObjectRequestV10.model_rebuild()
BlockObjectRequestV11.model_rebuild()
BlockObjectRequestV12.model_rebuild()
BlockObjectRequestV12TableOfContents.model_rebuild()
BlockObjectRequestV13.model_rebuild()
BlockObjectRequestV13LinkToPageV0.model_rebuild()
BlockObjectRequestV13LinkToPageV1.model_rebuild()
BlockObjectRequestV13LinkToPageV2.model_rebuild()
BlockObjectRequestV14.model_rebuild()
BlockObjectRequestV15.model_rebuild()
BlockObjectRequestV16.model_rebuild()
BlockObjectRequestV17.model_rebuild()
BlockObjectRequestV18.model_rebuild()
BlockObjectRequestV18Heading1.model_rebuild()
BlockObjectRequestV19.model_rebuild()
BlockObjectRequestV19Heading2.model_rebuild()
BlockObjectRequestV2.model_rebuild()
BlockObjectRequestV20.model_rebuild()
BlockObjectRequestV20Heading3.model_rebuild()
BlockObjectRequestV21.model_rebuild()
BlockObjectRequestV21Heading4.model_rebuild()
BlockObjectRequestV22.model_rebuild()
BlockObjectRequestV22Paragraph.model_rebuild()
BlockObjectRequestV23.model_rebuild()
BlockObjectRequestV23BulletedListItem.model_rebuild()
BlockObjectRequestV24.model_rebuild()
BlockObjectRequestV24NumberedListItem.model_rebuild()
BlockObjectRequestV25.model_rebuild()
BlockObjectRequestV25Quote.model_rebuild()
BlockObjectRequestV26.model_rebuild()
BlockObjectRequestV26ToDo.model_rebuild()
BlockObjectRequestV27.model_rebuild()
BlockObjectRequestV27Toggle.model_rebuild()
BlockObjectRequestV28.model_rebuild()
BlockObjectRequestV28Template.model_rebuild()
BlockObjectRequestV29.model_rebuild()
BlockObjectRequestV29Callout.model_rebuild()
BlockObjectRequestV3.model_rebuild()
BlockObjectRequestV30.model_rebuild()
BlockObjectRequestV30SyncedBlock.model_rebuild()
BlockObjectRequestV30SyncedBlockSyncedFrom.model_rebuild()
BlockObjectRequestV4.model_rebuild()
BlockObjectRequestV5.model_rebuild()
BlockObjectRequestV6.model_rebuild()
BlockObjectRequestV7.model_rebuild()
BlockObjectRequestV7Code.model_rebuild()
BlockObjectRequestV8.model_rebuild()
BlockObjectRequestV9.model_rebuild()
BlockObjectRequestWithoutChildren.model_rebuild()
BlockObjectRequestWithoutChildrenV0.model_rebuild()
BlockObjectRequestWithoutChildrenV1.model_rebuild()
BlockObjectRequestWithoutChildrenV10.model_rebuild()
BlockObjectRequestWithoutChildrenV11.model_rebuild()
BlockObjectRequestWithoutChildrenV12.model_rebuild()
BlockObjectRequestWithoutChildrenV12TableOfContents.model_rebuild()
BlockObjectRequestWithoutChildrenV13.model_rebuild()
BlockObjectRequestWithoutChildrenV13LinkToPageV0.model_rebuild()
BlockObjectRequestWithoutChildrenV13LinkToPageV1.model_rebuild()
BlockObjectRequestWithoutChildrenV13LinkToPageV2.model_rebuild()
BlockObjectRequestWithoutChildrenV14.model_rebuild()
BlockObjectRequestWithoutChildrenV15.model_rebuild()
BlockObjectRequestWithoutChildrenV16.model_rebuild()
BlockObjectRequestWithoutChildrenV17.model_rebuild()
BlockObjectRequestWithoutChildrenV18.model_rebuild()
BlockObjectRequestWithoutChildrenV19.model_rebuild()
BlockObjectRequestWithoutChildrenV2.model_rebuild()
BlockObjectRequestWithoutChildrenV20.model_rebuild()
BlockObjectRequestWithoutChildrenV21.model_rebuild()
BlockObjectRequestWithoutChildrenV22.model_rebuild()
BlockObjectRequestWithoutChildrenV23.model_rebuild()
BlockObjectRequestWithoutChildrenV23ToDo.model_rebuild()
BlockObjectRequestWithoutChildrenV24.model_rebuild()
BlockObjectRequestWithoutChildrenV25.model_rebuild()
BlockObjectRequestWithoutChildrenV26.model_rebuild()
BlockObjectRequestWithoutChildrenV26Callout.model_rebuild()
BlockObjectRequestWithoutChildrenV27.model_rebuild()
BlockObjectRequestWithoutChildrenV27SyncedBlock.model_rebuild()
BlockObjectRequestWithoutChildrenV27SyncedBlockSyncedFrom.model_rebuild()
BlockObjectRequestWithoutChildrenV3.model_rebuild()
BlockObjectRequestWithoutChildrenV4.model_rebuild()
BlockObjectRequestWithoutChildrenV5.model_rebuild()
BlockObjectRequestWithoutChildrenV6.model_rebuild()
BlockObjectRequestWithoutChildrenV7.model_rebuild()
BlockObjectRequestWithoutChildrenV7Code.model_rebuild()
BlockObjectRequestWithoutChildrenV8.model_rebuild()
BlockObjectRequestWithoutChildrenV9.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequest.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV0.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV1.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV10.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV11.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV12.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV12TableOfContents.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV13.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV13LinkToPageV0.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV13LinkToPageV1.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV13LinkToPageV2.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV14.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV15.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV16.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV17.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV18.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV19.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV2.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV20.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV21.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV22.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV23.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV24.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV24ToDo.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV25.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV26.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV26Template.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV27.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV27Callout.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV28.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV28SyncedBlock.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV28SyncedBlockSyncedFrom.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV3.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV4.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV5.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV6.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV7.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV7Code.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV8.model_rebuild()
BlockObjectWithSingleLevelOfChildrenRequestV9.model_rebuild()
BoardViewConfigRequest.model_rebuild()
ButtonPropertyConfigurationRequest.model_rebuild()
CalendarViewConfigRequest.model_rebuild()
ChartAggregationRequest.model_rebuild()
ChartReferenceLineRequest.model_rebuild()
ChartViewConfigRequest.model_rebuild()
CheckboxGroupByConfigRequest.model_rebuild()
CheckboxPropertyConfigurationRequest.model_rebuild()
CheckboxPropertyFilter.model_rebuild()
CheckboxPropertyFilterV0.model_rebuild()
CheckboxPropertyFilterV1.model_rebuild()
ColumnBlockWithChildrenRequest.model_rebuild()
ColumnListRequest.model_rebuild()
ColumnWithChildrenRequest.model_rebuild()
ContentPositionSchema.model_rebuild()
ContentPositionSchemaV0.model_rebuild()
ContentPositionSchemaV0AfterBlock.model_rebuild()
ContentPositionSchemaV1.model_rebuild()
ContentPositionSchemaV2.model_rebuild()
ContentWithExpressionRequest.model_rebuild()
ContentWithRichTextAndColorRequest.model_rebuild()
ContentWithRichTextColorAndIconRequest.model_rebuild()
ContentWithRichTextColorAndIconUpdateRequest.model_rebuild()
ContentWithRichTextRequest.model_rebuild()
ContentWithSingleLevelOfChildrenRequest.model_rebuild()
ContentWithTableRowRequest.model_rebuild()
CoverConfigRequest.model_rebuild()
CreateACommentBody.model_rebuild()
CreateACommentBodyAttachmentsItem.model_rebuild()
CreateACommentBodyDisplayNameV0.model_rebuild()
CreateACommentBodyDisplayNameV1.model_rebuild()
CreateACommentBodyDisplayNameV2.model_rebuild()
CreateACommentBodyDisplayNameV2Custom.model_rebuild()
CreateACommentBodyV1V01.model_rebuild()
CreateACommentBodyV1V0ParentV01.model_rebuild()
CreateACommentBodyV1V0ParentV11.model_rebuild()
CreateACommentBodyV1V11.model_rebuild()
CreateDatabaseBodyParent.model_rebuild()
CreateDatabaseBodyParentV1V01.model_rebuild()
CreateDatabaseBodyParentV1V11.model_rebuild()
CreateDatabaseForViewRequest.model_rebuild()
CreateDatabaseForViewRequestParent.model_rebuild()
CreateDatabaseForViewRequestPosition.model_rebuild()
CreatedByPropertyConfigurationRequest.model_rebuild()
CreatedTimePropertyConfigurationRequest.model_rebuild()
CreateViewBodyPlacement.model_rebuild()
CreateViewBodyPosition.model_rebuild()
CustomEmojiPageIconRequest.model_rebuild()
CustomEmojiPageIconRequestCustomEmoji.model_rebuild()
DateGroupByConfigRequest.model_rebuild()
DatePropertyConfigurationRequest.model_rebuild()
DateRequest.model_rebuild()
EmailPropertyConfigurationRequest.model_rebuild()
EmojiPageIconRequest.model_rebuild()
EmptyObject.model_rebuild()
EquationRichTextItemRequest.model_rebuild()
EquationRichTextItemRequestEquation.model_rebuild()
ExistencePropertyFilter.model_rebuild()
ExistencePropertyFilterV0.model_rebuild()
ExistencePropertyFilterV1.model_rebuild()
ExternalFileRequest.model_rebuild()
ExternalPageCoverRequest.model_rebuild()
ExternalPageCoverRequestExternal.model_rebuild()
ExternalPageIconRequest.model_rebuild()
ExternalPageIconRequestExternal.model_rebuild()
FilesPropertyConfigurationRequest.model_rebuild()
FileUploadIdRequest.model_rebuild()
FileUploadPageCoverRequest.model_rebuild()
FileUploadPageCoverRequestFileUpload.model_rebuild()
FileUploadPageIconRequest.model_rebuild()
FileUploadPageIconRequestFileUpload.model_rebuild()
FileUploadWithOptionalNameRequest.model_rebuild()
FormulaCheckboxSubGroupByRequest.model_rebuild()
FormulaDateSubGroupByRequest.model_rebuild()
FormulaGroupByConfigRequest.model_rebuild()
FormulaNumberSubGroupByRequest.model_rebuild()
FormulaPropertyConfigurationRequest.model_rebuild()
FormulaPropertyConfigurationRequestFormula.model_rebuild()
FormulaPropertyFilter.model_rebuild()
FormulaPropertyFilterV0.model_rebuild()
FormulaPropertyFilterV1.model_rebuild()
FormulaPropertyFilterV2.model_rebuild()
FormulaPropertyFilterV3.model_rebuild()
FormulaTextSubGroupByRequest.model_rebuild()
FormViewConfigRequest.model_rebuild()
GalleryViewConfigRequest.model_rebuild()
GroupByConfigRequest.model_rebuild()
GroupFilterOperatorArray.model_rebuild()
GroupFilterOperatorArrayItemV1V0.model_rebuild()
GroupFilterOperatorArrayItemV1V1.model_rebuild()
GroupObjectRequest.model_rebuild()
GroupSortRequest.model_rebuild()
HeaderContentWithRichTextAndColorRequest.model_rebuild()
HeaderContentWithSingleLevelOfChildrenRequest.model_rebuild()
IconPageIconRequest.model_rebuild()
IconPageIconRequestIcon.model_rebuild()
InternalFileRequest.model_rebuild()
InternalOrExternalFileWithNameRequest.model_rebuild()
InternalOrExternalFileWithNameRequestV0.model_rebuild()
InternalOrExternalFileWithNameRequestV1.model_rebuild()
LastEditedByPropertyConfigurationRequest.model_rebuild()
LastEditedTimePropertyConfigurationRequest.model_rebuild()
LastVisitedTimePropertyConfigurationRequest.model_rebuild()
ListViewConfigRequest.model_rebuild()
LocationPropertyConfigurationRequest.model_rebuild()
MapViewConfigRequest.model_rebuild()
MediaContentWithFileAndCaptionRequest.model_rebuild()
MediaContentWithFileAndCaptionRequestV0.model_rebuild()
MediaContentWithFileAndCaptionRequestV1.model_rebuild()
MediaContentWithFileNameAndCaptionRequest.model_rebuild()
MediaContentWithFileNameAndCaptionRequestV0.model_rebuild()
MediaContentWithFileNameAndCaptionRequestV1.model_rebuild()
MediaContentWithUrlAndCaptionRequest.model_rebuild()
MentionRichTextItemRequest.model_rebuild()
MentionRichTextItemRequestMentionV0.model_rebuild()
MentionRichTextItemRequestMentionV1.model_rebuild()
MentionRichTextItemRequestMentionV2.model_rebuild()
MentionRichTextItemRequestMentionV2Page.model_rebuild()
MentionRichTextItemRequestMentionV3.model_rebuild()
MentionRichTextItemRequestMentionV3Database.model_rebuild()
MentionRichTextItemRequestMentionV4.model_rebuild()
MentionRichTextItemRequestMentionV5.model_rebuild()
MentionRichTextItemRequestMentionV5CustomEmoji.model_rebuild()
MovePageBodyParentV0.model_rebuild()
MovePageBodyParentV1.model_rebuild()
MultiSelectPropertyConfigurationRequest.model_rebuild()
MultiSelectPropertyConfigurationRequestMultiSelect.model_rebuild()
MultiSelectPropertyConfigurationRequestMultiSelectOptionsItem.model_rebuild()
NumberGroupByConfigRequest.model_rebuild()
NumberPropertyConfigurationRequest.model_rebuild()
NumberPropertyConfigurationRequestNumber.model_rebuild()
PageIconRequest.model_rebuild()
PagePositionSchema.model_rebuild()
PagePositionSchemaV0.model_rebuild()
PagePositionSchemaV0AfterBlock.model_rebuild()
PagePositionSchemaV1.model_rebuild()
PagePositionSchemaV2.model_rebuild()
ParagraphWithSingleLevelOfChildrenRequest.model_rebuild()
PartialUserObjectRequest.model_rebuild()
PatchPageBodyPropertiesValueV0.model_rebuild()
PatchPageBodyPropertiesValueV1.model_rebuild()
PatchPageBodyPropertiesValueV10.model_rebuild()
PatchPageBodyPropertiesValueV11.model_rebuild()
PatchPageBodyPropertiesValueV12.model_rebuild()
PatchPageBodyPropertiesValueV13.model_rebuild()
PatchPageBodyPropertiesValueV13StatusV0.model_rebuild()
PatchPageBodyPropertiesValueV13StatusV1.model_rebuild()
PatchPageBodyPropertiesValueV14.model_rebuild()
PatchPageBodyPropertiesValueV14Place.model_rebuild()
PatchPageBodyPropertiesValueV15.model_rebuild()
PatchPageBodyPropertiesValueV15VerificationV0.model_rebuild()
PatchPageBodyPropertiesValueV15VerificationV1.model_rebuild()
PatchPageBodyPropertiesValueV2.model_rebuild()
PatchPageBodyPropertiesValueV3.model_rebuild()
PatchPageBodyPropertiesValueV4.model_rebuild()
PatchPageBodyPropertiesValueV4SelectV0.model_rebuild()
PatchPageBodyPropertiesValueV4SelectV1.model_rebuild()
PatchPageBodyPropertiesValueV5.model_rebuild()
PatchPageBodyPropertiesValueV5MultiSelectItemV0.model_rebuild()
PatchPageBodyPropertiesValueV5MultiSelectItemV1.model_rebuild()
PatchPageBodyPropertiesValueV6.model_rebuild()
PatchPageBodyPropertiesValueV7.model_rebuild()
PatchPageBodyPropertiesValueV8.model_rebuild()
PatchPageBodyPropertiesValueV9.model_rebuild()
PatchPageBodyTemplate.model_rebuild()
PeoplePropertyConfigurationRequest.model_rebuild()
PersonGroupByConfigRequest.model_rebuild()
PhoneNumberPropertyConfigurationRequest.model_rebuild()
PlacePropertyConfigurationRequest.model_rebuild()
PostDatabaseQueryBodyFilterV0V0.model_rebuild()
PostDatabaseQueryBodyFilterV0V1.model_rebuild()
PostDatabaseQueryBodySortsItemV0.model_rebuild()
PostDatabaseQueryBodySortsItemV1.model_rebuild()
PostPageBodyParentV0.model_rebuild()
PostPageBodyParentV1.model_rebuild()
PostPageBodyParentV2.model_rebuild()
PostPageBodyParentV3.model_rebuild()
PostPageBodyPropertiesValueV0.model_rebuild()
PostPageBodyPropertiesValueV1.model_rebuild()
PostPageBodyPropertiesValueV10.model_rebuild()
PostPageBodyPropertiesValueV11.model_rebuild()
PostPageBodyPropertiesValueV12.model_rebuild()
PostPageBodyPropertiesValueV13.model_rebuild()
PostPageBodyPropertiesValueV13StatusV0.model_rebuild()
PostPageBodyPropertiesValueV13StatusV1.model_rebuild()
PostPageBodyPropertiesValueV14.model_rebuild()
PostPageBodyPropertiesValueV14Place.model_rebuild()
PostPageBodyPropertiesValueV15.model_rebuild()
PostPageBodyPropertiesValueV15VerificationV0.model_rebuild()
PostPageBodyPropertiesValueV15VerificationV1.model_rebuild()
PostPageBodyPropertiesValueV2.model_rebuild()
PostPageBodyPropertiesValueV3.model_rebuild()
PostPageBodyPropertiesValueV4.model_rebuild()
PostPageBodyPropertiesValueV4SelectV0.model_rebuild()
PostPageBodyPropertiesValueV4SelectV1.model_rebuild()
PostPageBodyPropertiesValueV5.model_rebuild()
PostPageBodyPropertiesValueV5MultiSelectItemV0.model_rebuild()
PostPageBodyPropertiesValueV5MultiSelectItemV1.model_rebuild()
PostPageBodyPropertiesValueV6.model_rebuild()
PostPageBodyPropertiesValueV7.model_rebuild()
PostPageBodyPropertiesValueV8.model_rebuild()
PostPageBodyPropertiesValueV9.model_rebuild()
PostPageBodyTemplate.model_rebuild()
PropertyConfigurationRequest.model_rebuild()
PropertyConfigurationRequestCommon.model_rebuild()
PropertyFilter.model_rebuild()
PropertyFilterV0.model_rebuild()
PropertyFilterV1.model_rebuild()
PropertyFilterV10.model_rebuild()
PropertyFilterV11.model_rebuild()
PropertyFilterV12.model_rebuild()
PropertyFilterV13.model_rebuild()
PropertyFilterV14.model_rebuild()
PropertyFilterV15.model_rebuild()
PropertyFilterV16.model_rebuild()
PropertyFilterV17.model_rebuild()
PropertyFilterV18.model_rebuild()
PropertyFilterV19.model_rebuild()
PropertyFilterV2.model_rebuild()
PropertyFilterV20.model_rebuild()
PropertyFilterV21.model_rebuild()
PropertyFilterV3.model_rebuild()
PropertyFilterV4.model_rebuild()
PropertyFilterV5.model_rebuild()
PropertyFilterV6.model_rebuild()
PropertyFilterV7.model_rebuild()
PropertyFilterV8.model_rebuild()
PropertyFilterV9.model_rebuild()
PropertyOrTimestampFilterArray.model_rebuild()
QuickFilterConditionRequest.model_rebuild()
RelationGroupByConfigRequest.model_rebuild()
RelationItemPropertyValueResponse.model_rebuild()
RelationPropertyConfigurationRequest.model_rebuild()
RelationPropertyConfigurationRequestRelation.model_rebuild()
RelationPropertyConfigurationRequestRelationV1V0.model_rebuild()
RelationPropertyConfigurationRequestRelationV1V01.model_rebuild()
RelationPropertyConfigurationRequestRelationV1V1.model_rebuild()
RelationPropertyConfigurationRequestRelationV1V11.model_rebuild()
RelationPropertyConfigurationRequestRelationV1V1DualProperty.model_rebuild()
RelationPropertyConfigurationRequestRelationV1V1DualProperty1.model_rebuild()
RichTextItemRequest.model_rebuild()
RichTextItemRequestCommon.model_rebuild()
RichTextPropertyConfigurationRequest.model_rebuild()
RollupPropertyConfigurationRequest.model_rebuild()
RollupPropertyConfigurationRequestRollup.model_rebuild()
RollupPropertyConfigurationRequestRollupV1V0.model_rebuild()
RollupPropertyConfigurationRequestRollupV1V01.model_rebuild()
RollupPropertyConfigurationRequestRollupV1V1.model_rebuild()
RollupPropertyConfigurationRequestRollupV1V11.model_rebuild()
RollupPropertyConfigurationRequestRollupV1V2.model_rebuild()
RollupPropertyConfigurationRequestRollupV1V21.model_rebuild()
RollupPropertyConfigurationRequestRollupV1V3.model_rebuild()
RollupPropertyConfigurationRequestRollupV1V31.model_rebuild()
RollupPropertyFilter.model_rebuild()
RollupPropertyFilterV0.model_rebuild()
RollupPropertyFilterV1.model_rebuild()
RollupPropertyFilterV2.model_rebuild()
RollupPropertyFilterV3.model_rebuild()
RollupPropertyFilterV4.model_rebuild()
RollupSubfilterPropertyFilter.model_rebuild()
RollupSubfilterPropertyFilterV0.model_rebuild()
RollupSubfilterPropertyFilterV1.model_rebuild()
RollupSubfilterPropertyFilterV2.model_rebuild()
RollupSubfilterPropertyFilterV3.model_rebuild()
RollupSubfilterPropertyFilterV4.model_rebuild()
RollupSubfilterPropertyFilterV5.model_rebuild()
RollupSubfilterPropertyFilterV6.model_rebuild()
RollupSubfilterPropertyFilterV7.model_rebuild()
RollupSubfilterPropertyFilterV8.model_rebuild()
RollupSubfilterPropertyFilterV9.model_rebuild()
SelectGroupByConfigRequest.model_rebuild()
SelectPropertyConfigurationRequest.model_rebuild()
SelectPropertyConfigurationRequestSelect.model_rebuild()
SelectPropertyConfigurationRequestSelectOptionsItem.model_rebuild()
StatusGroupByConfigRequest.model_rebuild()
StatusPropertyConfigRequest.model_rebuild()
StatusPropertyConfigRequestOptionsItem.model_rebuild()
StatusPropertyConfigUpdateRequest.model_rebuild()
StatusPropertyConfigUpdateRequestOptionsItem.model_rebuild()
StatusPropertyConfigUpdateRequestOptionsItemV1V0.model_rebuild()
StatusPropertyConfigUpdateRequestOptionsItemV1V01.model_rebuild()
StatusPropertyConfigUpdateRequestOptionsItemV1V1.model_rebuild()
StatusPropertyConfigUpdateRequestOptionsItemV1V11.model_rebuild()
StatusPropertyConfigurationRequest.model_rebuild()
SubtaskConfigRequest.model_rebuild()
TabItemRequestWithoutChildren.model_rebuild()
TabItemRequestWithSingleLevelOfChildren.model_rebuild()
TableRequestWithTableRowChildren.model_rebuild()
TableRowRequest.model_rebuild()
TableViewConfigRequest.model_rebuild()
TabRequestWithNestedTabItemChildren.model_rebuild()
TabRequestWithTabItemChildren.model_rebuild()
TemplateMentionDateTemplateMentionRequest.model_rebuild()
TemplateMentionRequest.model_rebuild()
TemplateMentionUserTemplateMentionRequest.model_rebuild()
TextGroupByConfigRequest.model_rebuild()
TextRichTextItemRequest.model_rebuild()
TextRichTextItemRequestText.model_rebuild()
TextRichTextItemRequestTextLink.model_rebuild()
TimelineArrowsByRequest.model_rebuild()
TimelinePreferenceRequest.model_rebuild()
TimelineViewConfigRequest.model_rebuild()
TimestampCreatedTimeFilter.model_rebuild()
TimestampLastEditedTimeFilter.model_rebuild()
TitlePropertyConfigurationRequest.model_rebuild()
UniqueIdPropertyConfigurationRequest.model_rebuild()
UniqueIdPropertyConfigurationRequestUniqueId.model_rebuild()
UpdateABlockBodyV0V0.model_rebuild()
UpdateABlockBodyV0V1.model_rebuild()
UpdateABlockBodyV0V10.model_rebuild()
UpdateABlockBodyV0V11.model_rebuild()
UpdateABlockBodyV0V12.model_rebuild()
UpdateABlockBodyV0V12TableOfContents.model_rebuild()
UpdateABlockBodyV0V13.model_rebuild()
UpdateABlockBodyV0V13LinkToPageV0.model_rebuild()
UpdateABlockBodyV0V13LinkToPageV1.model_rebuild()
UpdateABlockBodyV0V13LinkToPageV2.model_rebuild()
UpdateABlockBodyV0V14.model_rebuild()
UpdateABlockBodyV0V15.model_rebuild()
UpdateABlockBodyV0V16.model_rebuild()
UpdateABlockBodyV0V17.model_rebuild()
UpdateABlockBodyV0V18.model_rebuild()
UpdateABlockBodyV0V19.model_rebuild()
UpdateABlockBodyV0V2.model_rebuild()
UpdateABlockBodyV0V20.model_rebuild()
UpdateABlockBodyV0V21.model_rebuild()
UpdateABlockBodyV0V22.model_rebuild()
UpdateABlockBodyV0V23.model_rebuild()
UpdateABlockBodyV0V23ToDo.model_rebuild()
UpdateABlockBodyV0V24.model_rebuild()
UpdateABlockBodyV0V25.model_rebuild()
UpdateABlockBodyV0V26.model_rebuild()
UpdateABlockBodyV0V26Callout.model_rebuild()
UpdateABlockBodyV0V27.model_rebuild()
UpdateABlockBodyV0V27SyncedBlock.model_rebuild()
UpdateABlockBodyV0V27SyncedBlockSyncedFrom.model_rebuild()
UpdateABlockBodyV0V28.model_rebuild()
UpdateABlockBodyV0V28Table.model_rebuild()
UpdateABlockBodyV0V29.model_rebuild()
UpdateABlockBodyV0V29Column.model_rebuild()
UpdateABlockBodyV0V3.model_rebuild()
UpdateABlockBodyV0V4.model_rebuild()
UpdateABlockBodyV0V5.model_rebuild()
UpdateABlockBodyV0V6.model_rebuild()
UpdateABlockBodyV0V7.model_rebuild()
UpdateABlockBodyV0V7Code.model_rebuild()
UpdateABlockBodyV0V8.model_rebuild()
UpdateABlockBodyV0V9.model_rebuild()
UpdateABlockBodyV1.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V01.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V0Number1.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V101.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V110.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V111.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V121.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V131.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V141.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V151.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V161.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V171.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V181.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V191.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V1Formula1.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V201.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V211.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V22.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V2Select1.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V2SelectOptionsItem1.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V2SelectOptionsItemV1V03.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V2SelectOptionsItemV1V13.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V31.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelect1.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelectOptionsItem1.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelectOptionsItemV1V03.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V3MultiSelectOptionsItemV1V13.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V41.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V51.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V5Relation1.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V5RelationV1V03.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V5RelationV1V13.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V5RelationV1V1DualProperty3.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V61.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V6Rollup1.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V03.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V13.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V23.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V6RollupV1V33.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V71.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V7UniqueId1.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V81.model_rebuild()
UpdateADataSourceBodyPropertiesValueV0V1V91.model_rebuild()
UpdateADataSourceBodyPropertiesValueV1.model_rebuild()
UpdateDatabaseBodyParent.model_rebuild()
UpdateDatabaseBodyParentV1V01.model_rebuild()
UpdateDatabaseBodyParentV1V11.model_rebuild()
UpdateMediaContentWithFileAndCaptionRequest.model_rebuild()
UpdateMediaContentWithFileNameAndCaptionRequest.model_rebuild()
UpdateMediaContentWithUrlAndCaptionRequest.model_rebuild()
UpdatePageMarkdownBodyInsertContent.model_rebuild()
UpdatePageMarkdownBodyReplaceContent.model_rebuild()
UpdatePageMarkdownBodyReplaceContentRange.model_rebuild()
UpdatePageMarkdownBodyUpdateContent.model_rebuild()
UpdatePageMarkdownBodyUpdateContentContentUpdatesItem.model_rebuild()
UrlPropertyConfigurationRequest.model_rebuild()
VerificationPropertyConfigurationRequest.model_rebuild()
VerificationPropertyStatusFilter.model_rebuild()
ViewConfigRequest.model_rebuild()
ViewFilterRequest.model_rebuild()
ViewPositionRequest.model_rebuild()
ViewPositionRequestV0.model_rebuild()
ViewPositionRequestV1.model_rebuild()
ViewPositionRequestV2.model_rebuild()
ViewPropertyConfigRequest.model_rebuild()
ViewPropertySortRequest.model_rebuild()
ViewSortRequest.model_rebuild()
ViewSortsRequest.model_rebuild()
WidgetPlacementRequest.model_rebuild()
WidgetPlacementRequestV0.model_rebuild()
WidgetPlacementRequestV1.model_rebuild()

"""
Atlassian Confluence MCP Server - Pydantic Models

Generated: 2026-04-23 20:59:52 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypeAlias

from _validators import PermissiveModel, StrictModel
from pydantic import Field, RootModel

# Type aliases for circular dependencies
if TYPE_CHECKING:
    CircularTypeAlias: TypeAlias = "Content | ContentArray | ContentChildren | ContentHistory | ContentHistoryContributors | ContentMetadata | ContentMetadataCurrentuser | ContentMetadataCurrentuserLastmodified | ContentRestriction | ContentRestrictionRestrictions | ContentRestrictions | Space | SpaceHistory | SpacePermission | SpacePermissionSubjects | SpacePermissionSubjectsUser | User | UserArray | UsersUserKeys | Version"
else:
    CircularTypeAlias: TypeAlias = Any


__all__ = [
    "AddContentWatcherRequest",
    "AddCustomContentPermissionsRequest",
    "AddGroupToContentRestrictionByGroupIdRequest",
    "AddLabelsToContentRequest",
    "AddLabelsToSpaceRequest",
    "AddLabelWatcherRequest",
    "AddRestrictionsRequest",
    "AddSpaceWatcherRequest",
    "AddUserToContentRestrictionRequest",
    "AddUserToGroupByGroupIdRequest",
    "ArchivePagesRequest",
    "AsyncConvertContentBodyRequest",
    "AsyncConvertContentBodyResponseRequest",
    "BulkAsyncConvertContentBodyRequest",
    "BulkAsyncConvertContentBodyResponseRequest",
    "CheckContentPermissionRequest",
    "CopyPageHierarchyRequest",
    "CopyPageRequest",
    "CreateAttachmentRequest",
    "CreateContentTemplateRequest",
    "CreateGroupRequest",
    "CreateOrUpdateAttachmentsRequest",
    "CreatePrivateSpaceRequest",
    "CreateRelationshipRequest",
    "CreateSpaceRequest",
    "CreateUserPropertyRequest",
    "DeleteContentVersionRequest",
    "DeleteLabelFromSpaceRequest",
    "DeletePageTreeRequest",
    "DeleteRelationshipRequest",
    "DeleteRestrictionsRequest",
    "DeleteSpaceRequest",
    "DeleteUserPropertyRequest",
    "DownloadAttatchmentRequest",
    "FindSourcesForTargetRequest",
    "FindTargetFromSourceRequest",
    "GetAllLabelContentRequest",
    "GetAndAsyncConvertMacroBodyByMacroIdRequest",
    "GetAndConvertMacroBodyByMacroIdRequest",
    "GetAuditRecordsRequest",
    "GetAvailableContentStatesRequest",
    "GetBlueprintTemplatesRequest",
    "GetBulkUserLookupRequest",
    "GetContentRestrictionStatusForUserRequest",
    "GetContentStateRequest",
    "GetContentsWithStateRequest",
    "GetContentTemplateRequest",
    "GetContentTemplatesRequest",
    "GetContentWatchStatusRequest",
    "GetGroupByGroupIdRequest",
    "GetGroupMembersByGroupIdRequest",
    "GetGroupMembershipsForUserRequest",
    "GetGroupsRequest",
    "GetIndividualGroupRestrictionStatusByGroupIdRequest",
    "GetLabelsForSpaceRequest",
    "GetMacroBodyByMacroIdRequest",
    "GetPrivacyUnsafeUserEmailBulkRequest",
    "GetRelationshipRequest",
    "GetRestrictionsByOperationRequest",
    "GetRestrictionsForOperationRequest",
    "GetRestrictionsRequest",
    "GetSpaceContentStatesRequest",
    "GetSpaceThemeRequest",
    "GetTaskRequest",
    "GetUserPropertiesRequest",
    "GetUserPropertyRequest",
    "GetUserRequest",
    "GetViewersRequest",
    "GetViewsRequest",
    "GetWatchersForSpaceRequest",
    "GetWatchesForPageRequest",
    "GetWatchesForSpaceRequest",
    "IsWatchingLabelRequest",
    "IsWatchingSpaceRequest",
    "MovePageRequest",
    "PublishLegacyDraftRequest",
    "PublishSharedDraftRequest",
    "RemoveContentStateRequest",
    "RemoveContentWatcherRequest",
    "RemoveGroupByIdRequest",
    "RemoveGroupFromContentRestrictionRequest",
    "RemoveLabelFromContentRequest",
    "RemoveLabelFromContentUsingQueryParameterRequest",
    "RemoveLabelWatcherRequest",
    "RemoveMemberFromGroupByGroupIdRequest",
    "RemovePermissionRequest",
    "RemoveSpaceWatchRequest",
    "RemoveTemplateRequest",
    "RemoveUserFromContentRestrictionRequest",
    "RestoreContentVersionRequest",
    "SearchByCqlRequest",
    "SearchContentByCqlRequest",
    "SearchGroupsRequest",
    "SearchUserRequest",
    "SetContentStateRequest",
    "SetSpaceThemeRequest",
    "UpdateAttachmentDataRequest",
    "UpdateContentTemplateRequest",
    "UpdateRestrictionsRequest",
    "UpdateSpaceRequest",
    "UpdateUserPropertyRequest",
    "AddCustomContentPermissionsBodyOperationsItem",
    "AddRestrictionsBodyV0",
    "ArchivePagesBodyPagesItem",
    "ContentBodyConversionInput",
    "ContentRestrictionUpdate",
    "LabelCreate",
    "LabelCreateArray",
    "SpacePermissionCreate",
    "UpdateRestrictionsBodyV0",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: list_audit_records
class GetAuditRecordsRequestQuery(StrictModel):
    start_date: str | None = Field(default=None, validation_alias="startDate", serialization_alias="startDate", description="Filter results to records on or after this date. Specify as epoch time in milliseconds.")
    end_date: str | None = Field(default=None, validation_alias="endDate", serialization_alias="endDate", description="Filter results to records on or before this date. Specify as epoch time in milliseconds.")
    search_string: str | None = Field(default=None, validation_alias="searchString", serialization_alias="searchString", description="Filter results to records with string property values matching this search term.")
    limit: int | None = Field(default=None, description="Maximum number of records to return per page. System limits may restrict the actual number returned.", json_schema_extra={'format': 'int32'})
class GetAuditRecordsRequest(StrictModel):
    """Retrieve audit log records for administrative events such as space exports, group membership changes, and app installations. Requires Confluence Administrator global permission."""
    query: GetAuditRecordsRequestQuery | None = None

# Operation: archive_pages
class ArchivePagesRequestBody(StrictModel):
    """The pages to be archived."""
    pages: list[ArchivePagesBodyPagesItem] | None = Field(default=None, description="List of content IDs identifying the pages to archive. Each ID must resolve to a page object that is not already archived. Pages can belong to different spaces. Requires 'Archive' permission in each page's corresponding space.")
class ArchivePagesRequest(StrictModel):
    """Archives a list of pages by their content IDs. The archival process is asynchronous; use the /longtask/<taskId> endpoint to monitor progress."""
    body: ArchivePagesRequestBody | None = None

# Operation: publish_blueprint_draft
class PublishLegacyDraftRequestPath(StrictModel):
    draft_id: str = Field(default=..., validation_alias="draftId", serialization_alias="draftId", description="The unique identifier of the draft page created from a blueprint. This ID can be found in the page URL when viewing the draft in Confluence.")
class PublishLegacyDraftRequestQuery(StrictModel):
    status: str | None = Field(default=None, description="The current status of the draft being published. Defaults to 'draft' and typically does not need to be specified.")
class PublishLegacyDraftRequestBodyVersion(StrictModel):
    number: int = Field(default=..., validation_alias="number", serialization_alias="number", description="The version number of the content being published. Set this to 1 for new drafts.", json_schema_extra={'format': 'int32'})
class PublishLegacyDraftRequestBodySpace(StrictModel):
    key: str = Field(default=..., validation_alias="key", serialization_alias="key", description="The space key where the published page will be created. This identifies the target Confluence space.", json_schema_extra={'format': 'int32'})
class PublishLegacyDraftRequestBody(StrictModel):
    status: Literal["current"] | None = Field(default=None, description="The target status for the published content. Set to 'current' to publish the draft as a live page, or omit to use the default.")
    title: str = Field(default=..., description="The title of the published page. If you do not want to change the title, use the current draft title. Maximum length is 255 characters.", max_length=255)
    type_: Literal["page"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The content type being published. Must be set to 'page' for blueprint drafts.")
    version: PublishLegacyDraftRequestBodyVersion
    space: PublishLegacyDraftRequestBodySpace
class PublishLegacyDraftRequest(StrictModel):
    """Publishes a legacy blueprint draft page to make it live in Confluence. Requires permission to view the draft and 'Add' permission for the target space."""
    path: PublishLegacyDraftRequestPath
    query: PublishLegacyDraftRequestQuery | None = None
    body: PublishLegacyDraftRequestBody

# Operation: publish_blueprint_draft_shared
class PublishSharedDraftRequestPath(StrictModel):
    draft_id: str = Field(default=..., validation_alias="draftId", serialization_alias="draftId", description="The unique identifier of the draft page created from a blueprint. This ID can be found in the Confluence application by opening the draft page and checking its URL.")
class PublishSharedDraftRequestQuery(StrictModel):
    status: str | None = Field(default=None, description="The current status of the draft content. This should remain set to 'draft' and typically does not need to be modified.")
class PublishSharedDraftRequestBodyVersion(StrictModel):
    number: int = Field(default=..., validation_alias="number", serialization_alias="number", description="The version number of the content being published. Set this to 1 for new draft publications.", json_schema_extra={'format': 'int32'})
class PublishSharedDraftRequestBodySpace(StrictModel):
    key: str = Field(default=..., validation_alias="key", serialization_alias="key", description="The key identifier of the space where the content will be published.", json_schema_extra={'format': 'int32'})
class PublishSharedDraftRequestBody(StrictModel):
    status: Literal["current"] | None = Field(default=None, description="The target status for the published content. Set to 'current' to publish the draft as active content.")
    title: str = Field(default=..., description="The title of the published page. If you do not want to change the title, use the current title of the draft.", max_length=255)
    type_: Literal["page"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The content type being published. Must be set to 'page' for blueprint-based content.")
    version: PublishSharedDraftRequestBodyVersion
    space: PublishSharedDraftRequestBodySpace
class PublishSharedDraftRequest(StrictModel):
    """Publishes a shared draft page created from a blueprint template. Requires permission to view the draft and 'Add' permission for the target space."""
    path: PublishSharedDraftRequestPath
    query: PublishSharedDraftRequestQuery | None = None
    body: PublishSharedDraftRequestBody

# Operation: search_content
class SearchContentByCqlRequestQuery(StrictModel):
    cql: str = Field(default=..., description="A CQL query string that specifies the search criteria. CQL supports filtering by content type, space, author, date, and other properties. Refer to Advanced searching using CQL documentation for syntax and available operators.")
    limit: int | None = Field(default=None, description="The maximum number of content items to return in a single response page. When using expand with body.export_view or body.styled_view, this is restricted to a maximum of 25.", json_schema_extra={'format': 'int32'})
    cqlcontext: dict | None = Field(default=None, description="The space, content, and content status to execute the search against.\nSpecify this as an object with the following properties:\n\n- `spaceKey` Key of the space to search against. Optional.\n- `contentId` ID of the content to search against. Optional. Must\nbe in the space spacified by `spaceKey`.\n- `contentStatuses` Content statuses to search against. Optional.")
class SearchContentByCqlRequest(StrictModel):
    """Search Confluence content using CQL (Confluence Query Language) to find pages, blog posts, and other content matching your query criteria. Results are paginated and support cursor-based navigation for retrieving additional pages."""
    query: SearchContentByCqlRequestQuery

# Operation: delete_page_tree
class DeletePageTreeRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The content ID of the root page whose entire tree (including all descendant pages) should be deleted.")
class DeletePageTreeRequest(StrictModel):
    """Asynchronously delete a page and all its descendants by moving them to the space's trash. Only supported for pages with current status. Returns a task ID to track the deletion progress."""
    path: DeletePageTreeRequestPath

# Operation: move_page
class MovePageRequestPath(StrictModel):
    page_id: str = Field(default=..., validation_alias="pageId", serialization_alias="pageId", description="The ID of the page to be moved.")
    position: Literal["before", "after", "append"] = Field(default=..., description="The position to move the page relative to the target page. Use 'before' or 'after' to place the page as a sibling, or 'append' to make it a child of the target.")
    target_id: str = Field(default=..., validation_alias="targetId", serialization_alias="targetId", description="The ID of the target page that serves as the reference point for the move operation. Avoid using 'before' or 'after' positions when the target is a top-level page, as this can create pages that are difficult to locate in the UI.")
class MovePageRequest(StrictModel):
    """Move a page to a new location in the wiki hierarchy relative to a target page. Supports positioning before, after, or as a child of the target page."""
    path: MovePageRequestPath

# Operation: add_attachment
class CreateAttachmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the content to which the attachment will be added.")
class CreateAttachmentRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The file to attach. The file will be uploaded as binary data.", json_schema_extra={'format': 'binary'})
    minor_edit: str = Field(default=..., validation_alias="minorEdit", serialization_alias="minorEdit", description="Set to 'true' to suppress notification emails and activity stream updates when the attachment is added. Set to 'false' or omit to generate notifications.", json_schema_extra={'format': 'binary'})
class CreateAttachmentRequest(StrictModel):
    """Adds a new attachment to a piece of content. To update an existing attachment instead, use the create or update attachments operation. Requires X-Atlassian-Token: nocheck header to prevent XSRF attacks."""
    path: CreateAttachmentRequestPath
    body: CreateAttachmentRequestBody

# Operation: upload_attachment
class CreateOrUpdateAttachmentsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the content to attach the file to.")
class CreateOrUpdateAttachmentsRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The file to upload as an attachment. The file will be sent as binary data in the multipart request.", json_schema_extra={'format': 'binary'})
    minor_edit: str = Field(default=..., validation_alias="minorEdit", serialization_alias="minorEdit", description="Set to 'true' to suppress notification emails and activity stream updates when the attachment is added or updated.", json_schema_extra={'format': 'binary'})
class CreateOrUpdateAttachmentsRequest(StrictModel):
    """Uploads a new attachment to content or creates a new version of an existing attachment. Supports optional minor edit mode to suppress notifications."""
    path: CreateOrUpdateAttachmentsRequestPath
    body: CreateOrUpdateAttachmentsRequestBody

# Operation: replace_attachment_data
class UpdateAttachmentDataRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the content that contains the attachment to be updated.")
    attachment_id: str = Field(default=..., validation_alias="attachmentId", serialization_alias="attachmentId", description="The ID of the attachment whose data will be replaced.")
class UpdateAttachmentDataRequestBody(StrictModel):
    file_: str = Field(default=..., validation_alias="file", serialization_alias="file", description="The binary file data to upload as the new attachment content.", json_schema_extra={'format': 'binary'})
    minor_edit: str = Field(default=..., validation_alias="minorEdit", serialization_alias="minorEdit", description="Set to 'true' to suppress notification emails and activity stream updates when the attachment is updated.", json_schema_extra={'format': 'binary'})
class UpdateAttachmentDataRequest(StrictModel):
    """Replace the binary data of an attachment by its ID. Optionally include a comment and mark as a minor edit to suppress notifications."""
    path: UpdateAttachmentDataRequestPath
    body: UpdateAttachmentDataRequestBody

# Operation: download_attachment
class DownloadAttatchmentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content object to which the attachment is associated.")
    attachment_id: str = Field(default=..., validation_alias="attachmentId", serialization_alias="attachmentId", description="The unique identifier of the attachment to download.")
class DownloadAttatchmentRequest(StrictModel):
    """Retrieves a download URI for an attachment associated with a piece of content. The client is redirected to a URL that serves the attachment's binary data."""
    path: DownloadAttatchmentRequestPath

# Operation: get_macro_body
class GetMacroBodyByMacroIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the content that contains the macro.")
    version: int = Field(default=..., description="The version of the content containing the macro. Use 0 to retrieve the macro body from the latest content version.", json_schema_extra={'format': 'int32'})
    macro_id: str = Field(default=..., validation_alias="macroId", serialization_alias="macroId", description="The ID of the macro to retrieve. This is typically a UUID generated by Confluence (e.g., 50884bd9-0cb8-41d5-98be-f80943c14f96) or the local ID of a Forge macro node. Query the content with expanded storage format body to locate the macro ID if unknown.")
class GetMacroBodyByMacroIdRequest(StrictModel):
    """Retrieves the body of a macro in storage format, including macro name, body content, and parameters. Returns macro metadata for the specified macro ID within a particular content version."""
    path: GetMacroBodyByMacroIdRequestPath

# Operation: get_macro_body_converted
class GetAndConvertMacroBodyByMacroIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the content that contains the macro.")
    version: int = Field(default=..., description="The version of the content containing the macro. Use 0 to retrieve the macro body from the latest content version.", json_schema_extra={'format': 'int32'})
    macro_id: str = Field(default=..., validation_alias="macroId", serialization_alias="macroId", description="The ID of the macro to retrieve. For Forge macros, this is the local ID of the ADF node. For other macros, this is a UUID-format identifier generated by Confluence. Query the content with expanded body storage format to find the macro ID if needed.")
    to: str = Field(default=..., description="The content representation format to return the macro body in.")
class GetAndConvertMacroBodyByMacroIdRequestQuery(StrictModel):
    embedded_content_render: Literal["current", "version-at-save"] | None = Field(default=None, validation_alias="embeddedContentRender", serialization_alias="embeddedContentRender", description="Controls how embedded content (such as attachments) is rendered. Use 'current' to render with the latest version, or 'version-at-save' to render with the version that existed at the time of save.")
class GetAndConvertMacroBodyByMacroIdRequest(StrictModel):
    """Retrieves the body of a macro in a specified content representation format. Returns macro metadata including name, body, and parameters for a given macro ID and content version."""
    path: GetAndConvertMacroBodyByMacroIdRequestPath
    query: GetAndConvertMacroBodyByMacroIdRequestQuery | None = None

# Operation: convert_macro_body_async
class GetAndAsyncConvertMacroBodyByMacroIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the content that contains the macro to be converted.")
    version: int = Field(default=..., description="The version of the content containing the macro. Use 0 to retrieve the macro from the latest content version.", json_schema_extra={'format': 'int32'})
    macro_id: str = Field(default=..., validation_alias="macroId", serialization_alias="macroId", description="The ID of the macro to convert. For Forge macros, this is the local ID from the ADF node parameters. For other macros, this is the randomly generated ID persisted across versions (format: UUID-like string).")
    to: Literal["export_view", "view", "styled_view"] = Field(default=..., description="The target content representation format for the macro conversion.")
class GetAndAsyncConvertMacroBodyByMacroIdRequestQuery(StrictModel):
    allow_cache: bool | None = Field(default=None, validation_alias="allowCache", serialization_alias="allowCache", description="Whether to cache and reuse conversion results for identical requests. When enabled, identical requests return the same task ID and reuse cached results if available.")
    embedded_content_render: Literal["current", "version-at-save"] | None = Field(default=None, validation_alias="embeddedContentRender", serialization_alias="embeddedContentRender", description="Determines which version of embedded content (such as attachments) to render: the current version or the version at the time of save.")
class GetAndAsyncConvertMacroBodyByMacroIdRequest(StrictModel):
    """Asynchronously converts a macro body to a specified content representation format. Returns a task ID that can be used to retrieve the conversion result, which remains available for 5 minutes after completion."""
    path: GetAndAsyncConvertMacroBodyByMacroIdRequestPath
    query: GetAndAsyncConvertMacroBodyByMacroIdRequestQuery | None = None

# Operation: add_labels_to_content
class AddLabelsToContentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content item to which labels will be added.")
class AddLabelsToContentRequestBody(StrictModel):
    """The labels to add to the content."""
    body: LabelCreateArray | LabelCreate = Field(default=..., description="A collection of labels to add to the content. Each label is a key-value pair where the key identifies the label namespace and the value specifies the label name.")
class AddLabelsToContentRequest(StrictModel):
    """Adds one or more labels to existing content without removing previously assigned labels. This operation is additive and preserves all existing labels on the content."""
    path: AddLabelsToContentRequestPath
    body: AddLabelsToContentRequestBody

# Operation: remove_label_from_content
class RemoveLabelFromContentUsingQueryParameterRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content from which the label will be removed.")
class RemoveLabelFromContentUsingQueryParameterRequestQuery(StrictModel):
    name: str = Field(default=..., description="The name of the label to remove from the content. This parameter supports label names containing forward slashes.")
class RemoveLabelFromContentUsingQueryParameterRequest(StrictModel):
    """Remove a label from content by specifying the label name as a query parameter. Use this method when the label name contains forward slashes, which are not supported in the path-based removal endpoint."""
    path: RemoveLabelFromContentUsingQueryParameterRequestPath
    query: RemoveLabelFromContentUsingQueryParameterRequestQuery

# Operation: remove_label_from_content_by_path
class RemoveLabelFromContentRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content item from which the label will be removed.")
    label: str = Field(default=..., description="The name of the label to remove from the content. This method does not support label names containing forward slashes due to path parameter security restrictions.")
class RemoveLabelFromContentRequest(StrictModel):
    """Removes a label from a piece of content by specifying the label name as a path parameter. Use this method when the label name contains no forward slashes; otherwise use the query parameter variant."""
    path: RemoveLabelFromContentRequestPath

# Operation: list_page_watches
class GetWatchesForPageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the page whose watches you want to retrieve.")
class GetWatchesForPageRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of watch records to return in a single response. The system may apply additional limits regardless of this value.", json_schema_extra={'format': 'int32'})
class GetWatchesForPageRequest(StrictModel):
    """Retrieves all watches for a specific page. Users who watch a page receive notifications when the page is updated."""
    path: GetWatchesForPageRequestPath
    query: GetWatchesForPageRequestQuery | None = None

# Operation: list_space_watches
class GetWatchesForSpaceRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content whose parent space watches should be retrieved.")
class GetWatchesForSpaceRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of watch records to return in a single response page. The system may enforce additional limits on this value.", json_schema_extra={'format': 'int32'})
class GetWatchesForSpaceRequest(StrictModel):
    """Retrieves all space watches for the space containing the specified content. Users who watch a space receive notifications when any content in that space is updated."""
    path: GetWatchesForSpaceRequestPath
    query: GetWatchesForSpaceRequestQuery | None = None

# Operation: copy_page_hierarchy
class CopyPageHierarchyRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The content ID of the source page whose hierarchy will be copied.")
class CopyPageHierarchyRequestBody(StrictModel):
    """Request object from json post body"""
    copy_attachments: bool | None = Field(default=None, validation_alias="copyAttachments", serialization_alias="copyAttachments", description="Whether to copy all attachments from the source page and its descendants to the destination hierarchy.")
    copy_permissions: bool | None = Field(default=None, validation_alias="copyPermissions", serialization_alias="copyPermissions", description="Whether to copy page-level permissions from the source page and its descendants to the destination hierarchy.")
    copy_properties: bool | None = Field(default=None, validation_alias="copyProperties", serialization_alias="copyProperties", description="Whether to copy content properties from the source page and its descendants to the destination hierarchy.")
    copy_labels: bool | None = Field(default=None, validation_alias="copyLabels", serialization_alias="copyLabels", description="Whether to copy labels from the source page and its descendants to the destination hierarchy.")
    copy_custom_contents: bool | None = Field(default=None, validation_alias="copyCustomContents", serialization_alias="copyCustomContents", description="Whether to copy custom contents from the source page and its descendants to the destination hierarchy.")
    copy_descendants: bool | None = Field(default=None, validation_alias="copyDescendants", serialization_alias="copyDescendants", description="Whether to copy all descendant pages in the hierarchy. When false, only the source page is copied without its children.")
    destination_page_id: str = Field(default=..., validation_alias="destinationPageId", serialization_alias="destinationPageId", description="The content ID of the destination page under which the copied page hierarchy will be placed as a child.")
class CopyPageHierarchyRequest(StrictModel):
    """Copy an entire page hierarchy including all descendant pages, with optional copying of attachments, permissions, properties, labels, and custom contents. Returns a long-running task ID to track the copy operation progress."""
    path: CopyPageHierarchyRequestPath
    body: CopyPageHierarchyRequestBody

# Operation: copy_page
class CopyPageRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The content ID of the page to copy.")
class CopyPageRequestBodyDestination(StrictModel):
    type_: Literal["space", "existing_page", "parent_page", "parent_content"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The destination type for the copied page: 'space' copies as a root page, 'parent_page' or 'parent_content' copies as a child, 'existing_page' replaces the target page.")
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The destination identifier: space key for 'space' type, or content ID for 'parent_page', 'parent_content', and 'existing_page' types.")
class CopyPageRequestBodyBodyStorage(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The page content body in storage format representation.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content format type for the storage body representation.")
class CopyPageRequestBodyBodyEditor2(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The page content body in editor2 format representation.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content format type for the editor2 body representation.")
class CopyPageRequestBodyBody(StrictModel):
    storage: CopyPageRequestBodyBodyStorage
    editor2: CopyPageRequestBodyBodyEditor2
class CopyPageRequestBody(StrictModel):
    """Request object from json post body"""
    copy_attachments: bool | None = Field(default=None, validation_alias="copyAttachments", serialization_alias="copyAttachments", description="Whether to copy attachments from the source page to the destination page.")
    copy_permissions: bool | None = Field(default=None, validation_alias="copyPermissions", serialization_alias="copyPermissions", description="Whether to copy page permissions from the source page to the destination page.")
    copy_properties: bool | None = Field(default=None, validation_alias="copyProperties", serialization_alias="copyProperties", description="Whether to copy content properties from the source page to the destination page.")
    copy_labels: bool | None = Field(default=None, validation_alias="copyLabels", serialization_alias="copyLabels", description="Whether to copy labels from the source page to the destination page.")
    copy_custom_contents: bool | None = Field(default=None, validation_alias="copyCustomContents", serialization_alias="copyCustomContents", description="Whether to copy custom contents from the source page to the destination page.")
    page_title: str | None = Field(default=None, validation_alias="pageTitle", serialization_alias="pageTitle", description="Optional title to replace the source page title in the destination page.")
    destination: CopyPageRequestBodyDestination
    body: CopyPageRequestBodyBody
class CopyPageRequest(StrictModel):
    """Copies a single page with its associated properties, permissions, attachments, and custom contents to a specified destination (space, parent page, parent content, or existing page)."""
    path: CopyPageRequestPath
    body: CopyPageRequestBody

# Operation: verify_content_permission
class CheckContentPermissionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content to check permissions against.")
class CheckContentPermissionRequestBodySubject(StrictModel):
    type_: Literal["user", "group"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The subject type being checked: either a user or group.")
    identifier: str = Field(default=..., validation_alias="identifier", serialization_alias="identifier", description="The subject identifier. For users, provide the account ID or 'anonymous' for unauthenticated users. For groups, provide the group ID.")
class CheckContentPermissionRequestBody(StrictModel):
    """The content permission request."""
    operation: Literal["read", "update", "delete"] = Field(default=..., description="The content operation to verify permission for.")
    subject: CheckContentPermissionRequestBodySubject
class CheckContentPermissionRequest(StrictModel):
    """Verify if a user or group has permission to perform a specific operation on content. Checks site permissions, space permissions, and content restrictions to determine access."""
    path: CheckContentPermissionRequestPath
    body: CheckContentPermissionRequestBody

# Operation: list_content_restrictions
class GetRestrictionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content whose restrictions you want to retrieve.")
class GetRestrictionsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of users and groups to return per page in the restrictions list. System limits may further restrict this value.", json_schema_extra={'format': 'int32'})
class GetRestrictionsRequest(StrictModel):
    """Retrieves all access restrictions applied to a piece of content, including user and group-level permissions. Requires permission to view the content."""
    path: GetRestrictionsRequestPath
    query: GetRestrictionsRequestQuery | None = None

# Operation: add_content_restrictions
class AddRestrictionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content to which restrictions will be added.")
class AddRestrictionsRequestBody(StrictModel):
    """The restrictions to be added to the content."""
    body: AddRestrictionsBodyV0 | list[ContentRestrictionUpdate] = Field(default=..., description="The restriction configuration object specifying the users or groups to restrict and the restriction type to apply.")
class AddRestrictionsRequest(StrictModel):
    """Adds access restrictions to a piece of content. This operation appends new restrictions without modifying any existing ones. Requires permission to edit the target content."""
    path: AddRestrictionsRequestPath
    body: AddRestrictionsRequestBody

# Operation: replace_content_restrictions
class UpdateRestrictionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content whose restrictions should be updated.")
class UpdateRestrictionsRequestBody(StrictModel):
    """The updated restrictions for the content."""
    body: UpdateRestrictionsBodyV0 | list[ContentRestrictionUpdate] = Field(default=..., description="The restriction configuration object containing the new restrictions to apply. This replaces all existing restrictions for the content.")
class UpdateRestrictionsRequest(StrictModel):
    """Replace all existing restrictions for a piece of content with new restrictions. This operation removes current restrictions and applies the restrictions specified in the request body."""
    path: UpdateRestrictionsRequestPath
    body: UpdateRestrictionsRequestBody

# Operation: remove_content_restrictions
class DeleteRestrictionsRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content whose restrictions should be removed.")
class DeleteRestrictionsRequest(StrictModel):
    """Removes all read and update restrictions from a piece of content, making it accessible according to default permissions. Requires permission to edit the content."""
    path: DeleteRestrictionsRequestPath

# Operation: list_content_restrictions_by_operation
class GetRestrictionsByOperationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content whose restrictions are being queried.")
class GetRestrictionsByOperationRequest(StrictModel):
    """Retrieves restrictions on content organized by operation type. Returns restriction details with operations as properties rather than array items, requiring permission to view the specified content."""
    path: GetRestrictionsByOperationRequestPath

# Operation: get_content_restriction_for_operation
class GetRestrictionsForOperationRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content item to query for restrictions.")
    operation_key: Literal["read", "update"] = Field(default=..., validation_alias="operationKey", serialization_alias="operationKey", description="The type of operation for which to retrieve restrictions.")
class GetRestrictionsForOperationRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of users and groups to return per page in the restrictions list. System limits may further restrict this value.", json_schema_extra={'format': 'int32'})
class GetRestrictionsForOperationRequest(StrictModel):
    """Retrieves access restrictions for a specific content item based on the operation type (read or update). Returns the users and groups with restrictions applied to that content."""
    path: GetRestrictionsForOperationRequestPath
    query: GetRestrictionsForOperationRequestQuery | None = None

# Operation: check_group_content_restriction
class GetIndividualGroupRestrictionStatusByGroupIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content item to check restrictions for.")
    operation_key: Literal["read", "update"] = Field(default=..., validation_alias="operationKey", serialization_alias="operationKey", description="The type of operation the restriction applies to.")
    group_id: str = Field(default=..., validation_alias="groupId", serialization_alias="groupId", description="The unique identifier of the group to check for the content restriction.")
class GetIndividualGroupRestrictionStatusByGroupIdRequest(StrictModel):
    """Checks whether a content restriction applies to a specific group. Returns true if the group has the specified restriction (read or update) on the content, though this does not guarantee group access due to other permission factors."""
    path: GetIndividualGroupRestrictionStatusByGroupIdRequestPath

# Operation: grant_group_content_restriction
class AddGroupToContentRestrictionByGroupIdRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The ID of the content to which the restriction applies.")
    operation_key: Literal["read", "update"] = Field(default=..., validation_alias="operationKey", serialization_alias="operationKey", description="The operation type that the restriction applies to, determining whether the group gains read or update access.")
    group_id: str = Field(default=..., validation_alias="groupId", serialization_alias="groupId", description="The ID of the group to add to the content restriction.")
class AddGroupToContentRestrictionByGroupIdRequest(StrictModel):
    """Grant read or update permission to a group for a piece of content by adding the group to the content restriction. Requires permission to edit the content."""
    path: AddGroupToContentRestrictionByGroupIdRequestPath

# Operation: revoke_group_content_restriction
class RemoveGroupFromContentRestrictionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content to which the restriction applies.")
    operation_key: Literal["read", "update"] = Field(default=..., validation_alias="operationKey", serialization_alias="operationKey", description="The type of operation for which the group restriction is being removed.")
    group_id: str = Field(default=..., validation_alias="groupId", serialization_alias="groupId", description="The unique identifier of the group to remove from the content restriction.")
class RemoveGroupFromContentRestrictionRequest(StrictModel):
    """Revoke a group's access restriction for a piece of content by removing them from a specific operation restriction (read or update). Requires permission to edit the content."""
    path: RemoveGroupFromContentRestrictionRequestPath

# Operation: check_content_restriction_for_user
class GetContentRestrictionStatusForUserRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content (page, blog post, etc.) to check restrictions for.")
    operation_key: str = Field(default=..., validation_alias="operationKey", serialization_alias="operationKey", description="The type of operation being restricted (e.g., 'read', 'update', 'delete'). Determines which restriction rule to evaluate.")
class GetContentRestrictionStatusForUserRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The unique account ID of the user across all Atlassian products. Used to determine if the restriction applies to this specific user.")
class GetContentRestrictionStatusForUserRequest(StrictModel):
    """Checks whether a specific content restriction applies to a user. Returns true if the restriction is enforced for that user, though this does not guarantee access due to inherited restrictions, space permissions, or product access levels."""
    path: GetContentRestrictionStatusForUserRequestPath
    query: GetContentRestrictionStatusForUserRequestQuery | None = None

# Operation: grant_user_content_restriction
class AddUserToContentRestrictionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content to which the restriction applies.")
    operation_key: str = Field(default=..., validation_alias="operationKey", serialization_alias="operationKey", description="The operation type that the restriction applies to (e.g., read, update).")
class AddUserToContentRestrictionRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user to grant permission to. This uniquely identifies the user across all Atlassian products.")
class AddUserToContentRestrictionRequest(StrictModel):
    """Grant a user read or update permission for content by adding them to a content restriction. Requires permission to edit the content."""
    path: AddUserToContentRestrictionRequestPath
    query: AddUserToContentRestrictionRequestQuery | None = None

# Operation: revoke_user_content_restriction
class RemoveUserFromContentRestrictionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content item from which the user restriction will be removed.")
    operation_key: Literal["read", "update"] = Field(default=..., validation_alias="operationKey", serialization_alias="operationKey", description="The type of permission restriction to remove from the user.")
class RemoveUserFromContentRestrictionRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user whose restriction will be removed. This uniquely identifies the user across all Atlassian products.")
class RemoveUserFromContentRestrictionRequest(StrictModel):
    """Revoke a user's content restriction by removing their read or update permission for a specific piece of content. Requires permission to edit the content."""
    path: RemoveUserFromContentRestrictionRequestPath
    query: RemoveUserFromContentRestrictionRequestQuery | None = None

# Operation: get_content_state
class GetContentStateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content item whose state you want to retrieve.")
class GetContentStateRequest(StrictModel):
    """Retrieves the current state of a content item, supporting draft, current, or archived versions. Requires permission to view the specified content."""
    path: GetContentStateRequestPath

# Operation: publish_content_with_state
class SetContentStateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content whose state will be updated.")
class SetContentStateRequestQuery(StrictModel):
    status: Literal["current", "draft"] = Field(default=..., description="Whether the state should be applied to the draft version or published as a new current version. Draft applies the state to unpublished changes; current publishes a new version with the same body as the previous version.")
class SetContentStateRequestBody(StrictModel):
    """Content state fields for state. Pass in id for an existing state, or new name and color for best matching existing state, or new state if allowed in space."""
    id_2: int | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The numeric identifier of the state to apply. Use 0, 1, or 2 for default space states, or provide the ID of a custom state. If provided along with name and color, this ID takes precedence.", json_schema_extra={'format': 'int64'})
    name: str | None = Field(default=None, description="The display name for a custom state. If a custom state with this name and color already exists for the current user, that existing state will be reused. Maximum 20 characters.")
    color: str | None = Field(default=None, description="The color for a custom state in 6-digit hexadecimal format (e.g., #ff7452 for red). Must be paired with a name to create or reuse a custom state.")
class SetContentStateRequest(StrictModel):
    """Set the content state for a piece of content and publish a new version with that state. This creates a new version without modifying the content body, allowing you to apply state changes (default or custom) to either draft or current versions."""
    path: SetContentStateRequestPath
    query: SetContentStateRequestQuery
    body: SetContentStateRequestBody | None = None

# Operation: publish_content_without_state
class RemoveContentStateRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content whose state should be removed and republished.")
class RemoveContentStateRequest(StrictModel):
    """Removes the content state and publishes a new version of the content without modifying its body. This operation creates a new version with an updated status while preserving the existing content."""
    path: RemoveContentStateRequestPath

# Operation: list_available_content_states
class GetAvailableContentStatesRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content for which to retrieve available state transitions. Requires permission to edit the content.")
class GetAvailableContentStatesRequest(StrictModel):
    """Retrieves the content states available for a specific piece of content to transition to. Returns all enabled space content states plus up to 3 most recently published custom content states; use the content-states endpoint to retrieve all custom states."""
    path: GetAvailableContentStatesRequestPath

# Operation: restore_content_version
class RestoreContentVersionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content whose version will be restored.")
class RestoreContentVersionRequestBodyParams(StrictModel):
    version_number: int = Field(default=..., validation_alias="versionNumber", serialization_alias="versionNumber", description="The version number to restore as the current version. Must be a positive integer representing a historical version.", json_schema_extra={'format': 'int32'})
    message: str = Field(default=..., validation_alias="message", serialization_alias="message", description="A descriptive message or changelog entry for the restored version.")
    restore_title: bool | None = Field(default=None, validation_alias="restoreTitle", serialization_alias="restoreTitle", description="When true, the restored version's title will become the current content title. When false, only the content body is restored while preserving the current title.")
class RestoreContentVersionRequestBody(StrictModel):
    """The content version to be restored."""
    operation_key: Literal["restore"] = Field(default=..., validation_alias="operationKey", serialization_alias="operationKey", description="Operation type identifier that must be set to 'restore' to indicate a version restoration action.")
    params: RestoreContentVersionRequestBodyParams
class RestoreContentVersionRequest(StrictModel):
    """Restores a historical version of content as the latest version by creating a new version with the content from the specified historical version. Requires permission to update the content."""
    path: RestoreContentVersionRequestPath
    body: RestoreContentVersionRequestBody

# Operation: delete_content_version
class DeleteContentVersionRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the content from which the version will be deleted.")
    version_number: int = Field(default=..., validation_alias="versionNumber", serialization_alias="versionNumber", description="The version number to delete, starting from 1 up to the current version number.", json_schema_extra={'format': 'int32'})
class DeleteContentVersionRequest(StrictModel):
    """Delete a historical version of content. The changes from the deleted version are automatically rolled up into the next version. Note that the current version cannot be deleted."""
    path: DeleteContentVersionRequestPath

# Operation: convert_content_body_async
class AsyncConvertContentBodyRequestPath(StrictModel):
    to: Literal["export_view"] = Field(default=..., description="Target format for the converted content body.")
class AsyncConvertContentBodyRequestQuery(StrictModel):
    content_id_context: str | None = Field(default=None, validation_alias="contentIdContext", serialization_alias="contentIdContext", description="Content ID used to resolve embedded content (page includes, files, links) within the same space. When provided, takes precedence over spaceKeyContext for context resolution.")
    allow_cache: bool | None = Field(default=None, validation_alias="allowCache", serialization_alias="allowCache", description="Enable caching to reuse conversion results for identical requests. When true, identical requests return the same task ID and reuse cached results; when false, each request creates a new conversion task.")
    embedded_content_render: Literal["current", "version-at-save"] | None = Field(default=None, validation_alias="embeddedContentRender", serialization_alias="embeddedContentRender", description="Rendering mode for embedded content. Use 'current' for the latest version or 'version-at-save' for the version at the time of save.")
class AsyncConvertContentBodyRequestBody(StrictModel):
    """The content body to convert."""
    value: str = Field(default=..., description="The content body in the source format specified by the representation parameter.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., description="Source content format type. Must match the format of the provided content body value.")
class AsyncConvertContentBodyRequest(StrictModel):
    """Asynchronously convert content body between different formats (storage, editor, atlas_doc_format, view variants). Returns an asyncId to retrieve the conversion result, which remains available for 5 minutes after completion."""
    path: AsyncConvertContentBodyRequestPath
    query: AsyncConvertContentBodyRequestQuery | None = None
    body: AsyncConvertContentBodyRequestBody

# Operation: get_async_content_conversion
class AsyncConvertContentBodyResponseRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the asynchronous conversion task whose result or status you want to retrieve.")
class AsyncConvertContentBodyResponseRequest(StrictModel):
    """Retrieve the converted content body for a completed asynchronous conversion task, or check the current status if the task is still processing. Completed results are available for up to 5 minutes or until a new conversion request is made with caching disabled."""
    path: AsyncConvertContentBodyResponseRequestPath

# Operation: get_bulk_content_conversion_results
class BulkAsyncConvertContentBodyResponseRequestQuery(StrictModel):
    ids: list[str] = Field(default=..., description="List of asyncIds from conversion tasks to retrieve results for. Maximum 50 task IDs per request. Order is preserved in the response.")
class BulkAsyncConvertContentBodyResponseRequest(StrictModel):
    """Retrieve completed content body conversion results for multiple asynchronous tasks. Results are available for up to 5 minutes after task completion or until a new conversion request is made with caching disabled."""
    query: BulkAsyncConvertContentBodyResponseRequestQuery

# Operation: convert_content_bodies_async_bulk
class BulkAsyncConvertContentBodyRequestBody(StrictModel):
    """An array of parameters to create content body conversion tasks."""
    conversion_inputs: list[ContentBodyConversionInput] | None = Field(default=None, validation_alias="conversionInputs", serialization_alias="conversionInputs", description="Array of content body conversion specifications. Each item defines a source content body and target format. Order is preserved in the response. Maximum 10 items per request.")
class BulkAsyncConvertContentBodyRequest(StrictModel):
    """Asynchronously converts multiple content bodies between supported formats in bulk, with a maximum of 10 conversions per request. Conversion tasks remain available for polling for up to 5 minutes after completion."""
    body: BulkAsyncConvertContentBodyRequestBody | None = None

# Operation: list_label_contents
class GetAllLabelContentRequestQuery(StrictModel):
    name: str = Field(default=..., description="The name of the label to query for associated contents.")
    type_: Literal["page", "blogpost", "attachment", "page_template"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filter results to only include specific content types.")
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response.", json_schema_extra={'format': 'int32'})
class GetAllLabelContentRequest(StrictModel):
    """Retrieve label information and all contents associated with that label. Only contents the user has permission to view are returned."""
    query: GetAllLabelContentRequestQuery

# Operation: list_groups
class GetGroupsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of groups to return per page. The system may enforce fixed limits below the requested value.", json_schema_extra={'format': 'int32'})
    access_type: Literal["user", "admin", "site-admin"] | None = Field(default=None, validation_alias="accessType", serialization_alias="accessType", description="Filter results by group permission level within the Confluence site.")
class GetGroupsRequest(StrictModel):
    """Retrieve all user groups from the Confluence site, ordered alphabetically by group name. Requires 'Can use' global permission to access the Confluence site."""
    query: GetGroupsRequestQuery | None = None

# Operation: create_group
class CreateGroupRequestBody(StrictModel):
    """Name of the group that is to be created."""
    name: str = Field(default=..., description="The name of the user group to create. Must be unique within the Confluence instance.")
class CreateGroupRequest(StrictModel):
    """Creates a new user group in Confluence. Requires site administrator permissions."""
    body: CreateGroupRequestBody

# Operation: get_group
class GetGroupByGroupIdRequestQuery(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the group to retrieve.")
class GetGroupByGroupIdRequest(StrictModel):
    """Retrieve a user group by its unique identifier. Requires permission to access the Confluence site."""
    query: GetGroupByGroupIdRequestQuery

# Operation: delete_group
class RemoveGroupByIdRequestQuery(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the group to delete.")
class RemoveGroupByIdRequest(StrictModel):
    """Delete a user group from the Confluence instance. Requires site administrator permissions."""
    query: RemoveGroupByIdRequestQuery

# Operation: search_groups
class SearchGroupsRequestQuery(StrictModel):
    query: str = Field(default=..., description="The search term used to find matching groups. Supports partial matching against group names and identifiers.")
    limit: int | None = Field(default=None, description="The maximum number of groups to return in the results. Limited to a maximum of 200 groups per request.", json_schema_extra={'format': 'int32'})
class SearchGroupsRequest(StrictModel):
    """Search for groups using a partial query string. Returns matching groups up to the specified limit."""
    query: SearchGroupsRequestQuery

# Operation: list_group_members
class GetGroupMembersByGroupIdRequestPath(StrictModel):
    group_id: str = Field(default=..., validation_alias="groupId", serialization_alias="groupId", description="The unique identifier of the group whose members you want to retrieve.")
class GetGroupMembersByGroupIdRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of users to return per page of results. The system may apply fixed limits that restrict this value.", json_schema_extra={'format': 'int32'})
class GetGroupMembersByGroupIdRequest(StrictModel):
    """Retrieves all users that are members of a specified group. Requires permission to access the Confluence site."""
    path: GetGroupMembersByGroupIdRequestPath
    query: GetGroupMembersByGroupIdRequestQuery | None = None

# Operation: add_user_to_group
class AddUserToGroupByGroupIdRequestQuery(StrictModel):
    group_id: str = Field(default=..., validation_alias="groupId", serialization_alias="groupId", description="The unique identifier of the group to which the user will be added.")
class AddUserToGroupByGroupIdRequestBody(StrictModel):
    """AccountId of the user who needs to be added as member."""
    account_id: str = Field(default=..., validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user to be added to the group.")
class AddUserToGroupByGroupIdRequest(StrictModel):
    """Adds a user as a member to a group by its groupId. Requires site admin permissions."""
    query: AddUserToGroupByGroupIdRequestQuery
    body: AddUserToGroupByGroupIdRequestBody

# Operation: remove_user_from_group
class RemoveMemberFromGroupByGroupIdRequestQuery(StrictModel):
    group_id: str = Field(default=..., validation_alias="groupId", serialization_alias="groupId", description="The unique identifier of the group from which the user will be removed.")
    account_id: str = Field(default=..., validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user to remove from the group. This uniquely identifies the user across all Atlassian products.")
class RemoveMemberFromGroupByGroupIdRequest(StrictModel):
    """Remove a user from a group by group ID. Requires site admin permissions."""
    query: RemoveMemberFromGroupByGroupIdRequestQuery

# Operation: get_longtask
class GetTaskRequestPath(StrictModel):
    id_: str = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the long-running task to retrieve status information for.")
class GetTaskRequest(StrictModel):
    """Retrieve the status of an active long-running task such as a space export, including elapsed time and completion percentage. Requires 'Can use' global permission to access the Confluence site."""
    path: GetTaskRequestPath

# Operation: list_related_entities
class FindTargetFromSourceRequestPath(StrictModel):
    relation_name: str = Field(default=..., validation_alias="relationName", serialization_alias="relationName", description="The name of the relationship type to query. Custom relationship types are supported, but 'like' and 'favourite' relationships are not available through this operation.")
    source_type: Literal["user", "content", "space"] = Field(default=..., validation_alias="sourceType", serialization_alias="sourceType", description="The type of the source entity in the relationship.")
    source_key: str = Field(default=..., validation_alias="sourceKey", serialization_alias="sourceKey", description="The identifier for the source entity. For users, use 'current' for the logged-in user, an account ID, or a deprecated user key. For content, use the content ID. For spaces, use the space key.")
    target_type: Literal["user", "content", "space"] = Field(default=..., validation_alias="targetType", serialization_alias="targetType", description="The type of the target entity in the relationship.")
class FindTargetFromSourceRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of relationships to return per page. The system may enforce additional limits on this value.", json_schema_extra={'format': 'int32'})
class FindTargetFromSourceRequest(StrictModel):
    """Retrieves all target entities that have a specific relationship type with a source entity. Relationships are directional, so results depend on the relationship direction defined."""
    path: FindTargetFromSourceRequestPath
    query: FindTargetFromSourceRequestQuery | None = None

# Operation: check_relationship
class GetRelationshipRequestPath(StrictModel):
    relation_name: str = Field(default=..., validation_alias="relationName", serialization_alias="relationName", description="The name of the relationship type to check (e.g., 'favourite' for save-for-later, or custom relationship types).")
    source_type: Literal["user", "content", "space"] = Field(default=..., validation_alias="sourceType", serialization_alias="sourceType", description="The type of the source entity in the relationship. Must be 'user' if checking a 'favourite' relationship.")
    source_key: str = Field(default=..., validation_alias="sourceKey", serialization_alias="sourceKey", description="The identifier for the source entity. Use 'current' for the logged-in user, an account ID or user key for users, a content ID for content, or a space key for spaces.")
    target_type: Literal["user", "content", "space"] = Field(default=..., validation_alias="targetType", serialization_alias="targetType", description="The type of the target entity in the relationship. Must be 'space' or 'content' if checking a 'favourite' relationship.")
    target_key: str = Field(default=..., validation_alias="targetKey", serialization_alias="targetKey", description="The identifier for the target entity. Use 'current' for the logged-in user, an account ID or user key for users, a content ID for content, or a space key for spaces.")
class GetRelationshipRequest(StrictModel):
    """Check whether a specific relationship exists between two entities. Relationships are directional, so the source and target entities matter. For example, you can check if a user has marked a page as a favorite."""
    path: GetRelationshipRequestPath

# Operation: create_relationship
class CreateRelationshipRequestPath(StrictModel):
    relation_name: str = Field(default=..., validation_alias="relationName", serialization_alias="relationName", description="The name of the relationship to create. Use 'favourite' for the built-in save-for-later relationship, or specify any custom relationship type name.")
    source_type: Literal["user", "content", "space"] = Field(default=..., validation_alias="sourceType", serialization_alias="sourceType", description="The type of the source entity in the relationship. Must be 'user' when creating a 'favourite' relationship.")
    source_key: str = Field(default=..., validation_alias="sourceKey", serialization_alias="sourceKey", description="The identifier for the source entity. For users, specify 'current' (logged-in user), account ID, or deprecated user key. For content, specify the content ID. For spaces, specify the space key.")
    target_type: Literal["user", "content", "space"] = Field(default=..., validation_alias="targetType", serialization_alias="targetType", description="The type of the target entity in the relationship. Must be 'space' or 'content' when creating a 'favourite' relationship.")
    target_key: str = Field(default=..., validation_alias="targetKey", serialization_alias="targetKey", description="The identifier for the target entity. For users, specify 'current' (logged-in user), account ID, or deprecated user key. For content, specify the content ID. For spaces, specify the space key.")
class CreateRelationshipRequest(StrictModel):
    """Creates a relationship between two Confluence entities (user, space, or content). Supports built-in relationships like 'favourite' (save for later) as well as custom relationship types."""
    path: CreateRelationshipRequestPath

# Operation: delete_relationship
class DeleteRelationshipRequestPath(StrictModel):
    relation_name: str = Field(default=..., validation_alias="relationName", serialization_alias="relationName", description="The name of the relationship to delete (e.g., 'favourite', 'relates_to').")
    source_type: Literal["user", "content", "space"] = Field(default=..., validation_alias="sourceType", serialization_alias="sourceType", description="The type of the source entity in the relationship. Must be 'user' for favourite relationships.")
    source_key: str = Field(default=..., validation_alias="sourceKey", serialization_alias="sourceKey", description="The identifier for the source entity. Use 'current' for the logged-in user, account ID or user key for users, content ID for content, or space key for spaces.")
    target_type: Literal["user", "content", "space"] = Field(default=..., validation_alias="targetType", serialization_alias="targetType", description="The type of the target entity in the relationship. Must be 'space' or 'content' for favourite relationships.")
    target_key: str = Field(default=..., validation_alias="targetKey", serialization_alias="targetKey", description="The identifier for the target entity. Use 'current' for the logged-in user, account ID or user key for users, content ID for content, or space key for spaces.")
class DeleteRelationshipRequest(StrictModel):
    """Removes a relationship between two Confluence entities (user, space, or content). For favourite relationships, users can only delete their own, while space administrators can delete any user's favourites."""
    path: DeleteRelationshipRequestPath

# Operation: list_related_sources
class FindSourcesForTargetRequestPath(StrictModel):
    relation_name: str = Field(default=..., validation_alias="relationName", serialization_alias="relationName", description="The name of the relationship type to query. Custom relationship types are supported, but 'like' and 'favourite' relationships are not available through this operation.")
    source_type: Literal["user", "content", "space"] = Field(default=..., validation_alias="sourceType", serialization_alias="sourceType", description="The entity type of the sources to retrieve.")
    target_type: Literal["user", "content", "space"] = Field(default=..., validation_alias="targetType", serialization_alias="targetType", description="The entity type of the target entity.")
    target_key: str = Field(default=..., validation_alias="targetKey", serialization_alias="targetKey", description="The identifier of the target entity. For users, provide 'current' for the logged-in user, a user key, or an account ID. For content, provide the content ID. For spaces, provide the space key.")
class FindSourcesForTargetRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of relationships to return per page. The system may enforce additional limits on this value.", json_schema_extra={'format': 'int32'})
class FindSourcesForTargetRequest(StrictModel):
    """Retrieve all source entities that have a specific relationship type to a target entity. Relationships are directional, so this finds sources pointing to the specified target."""
    path: FindSourcesForTargetRequestPath
    query: FindSourcesForTargetRequestQuery | None = None

# Operation: search_content_global
class SearchByCqlRequestQuery(StrictModel):
    cqlcontext: str | None = Field(default=None, description="CQL query string to filter search results. Specify the space key, content ID, and/or content statuses to narrow the search scope. Note: User-specific fields (user, user.fullname, user.accountid, user.userkey) are no longer supported.")
    limit: int | None = Field(default=None, description="Maximum number of content objects to return per page. System limits may further restrict this value. When using body.export_view or body.styled_view expansion, the maximum is 25.", json_schema_extra={'format': 'int32'})
    include_archived_spaces: bool | None = Field(default=None, validation_alias="includeArchivedSpaces", serialization_alias="includeArchivedSpaces", description="Include content from archived spaces in the search results.")
    exclude_current_spaces: bool | None = Field(default=None, validation_alias="excludeCurrentSpaces", serialization_alias="excludeCurrentSpaces", description="Exclude current spaces from results and only return content from archived spaces.")
    excerpt: Literal["highlight", "indexed", "none", "highlight_unescaped", "indexed_unescaped"] | None = Field(default=None, description="Strategy for generating text excerpts in search results. Highlight shows matched terms in context, indexed uses pre-computed excerpts, and none omits excerpts entirely. Unescaped variants return HTML without entity encoding.")
    site_permission_type_filter: Literal["all", "externalCollaborator", "none"] | None = Field(default=None, validation_alias="sitePermissionTypeFilter", serialization_alias="sitePermissionTypeFilter", description="Filter results by user permission type. Use 'none' for licensed users only, 'externalCollaborator' for external/guest users, or 'all' to include all permission types.")
    cql: str | None = Field(default=None, description="The CQL query to be used for the search. See\n[Advanced Searching using CQL](https://developer.atlassian.com/cloud/confluence/advanced-searching-using-cql/)\nfor instructions on how to build a CQL query.")
class SearchByCqlRequest(StrictModel):
    """Search Confluence content using Confluence Query Language (CQL). Returns matching pages, blog posts, and other content objects with support for pagination via cursor-based navigation."""
    query: SearchByCqlRequestQuery | None = None

# Operation: search_users
class SearchUserRequestQuery(StrictModel):
    cql: str = Field(default=..., description="CQL query string to filter users. Supports user-specific fields including user, user.fullname, user.accountid, and user.userkey. Use operators like IN, NOT IN, and != for advanced filtering.")
    limit: int | None = Field(default=None, description="Maximum number of user objects to return per page. System limits may restrict the actual number returned.", json_schema_extra={'format': 'int32'})
    site_permission_type_filter: Literal["all", "externalCollaborator", "none"] | None = Field(default=None, validation_alias="sitePermissionTypeFilter", serialization_alias="sitePermissionTypeFilter", description="Filter users by permission type. Use 'none' for licensed users, 'externalCollaborator' for external/guest users, or 'all' to include all permission types.")
class SearchUserRequest(StrictModel):
    """Search for Confluence users using Confluence Query Language (CQL) with support for user-specific fields like account ID, full name, and user key. Some user fields may be null depending on privacy settings."""
    query: SearchUserRequestQuery

# Operation: create_space
class CreateSpaceRequestBodyDescriptionPlain(StrictModel):
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The space description.")
class CreateSpaceRequestBodyDescription(StrictModel):
    plain: CreateSpaceRequestBodyDescriptionPlain | None = None
class CreateSpaceRequestBody(StrictModel):
    """The space to be created."""
    name: str = Field(default=..., description="The name of the new space. Must be unique and descriptive for identifying the space.", max_length=200)
    key: str | None = Field(default=None, description="The key for the new space. Format: See [Space\nkeys](https://confluence.atlassian.com/x/lqNMMQ). If `alias` is not provided, this is required.")
    alias: str | None = Field(default=None, description="This field will be used as the new identifier for the space in confluence page URLs.\nIf the property is not provided the alias will be the provided key.\nThis property is experimental and may be changed or removed in the future.")
    permissions: list[SpacePermissionCreate] | None = Field(default=None, description="The permissions for the new space. If no permissions are provided, the\n[Confluence default space permissions](https://confluence.atlassian.com/x/UAgzKw#CreateaSpace-Spacepermissions)\nare applied. Note that if permissions are provided, the space is\ncreated with only the provided set of permissions, not\nincluding the default space permissions. Space permissions\ncan be modified after creation using the space permissions\nendpoints, and a private space can be created using the\ncreate private space endpoint.")
    description: CreateSpaceRequestBodyDescription | None = None
class CreateSpaceRequest(StrictModel):
    """Creates a new space in Confluence. Requires 'Create Space(s)' global permission. Note that space labels cannot be set during creation."""
    body: CreateSpaceRequestBody

# Operation: create_private_space
class CreatePrivateSpaceRequestBodyDescriptionPlain(StrictModel):
    value: str | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The space description.")
class CreatePrivateSpaceRequestBodyDescription(StrictModel):
    plain: CreatePrivateSpaceRequestBodyDescriptionPlain | None = None
class CreatePrivateSpaceRequestBody(StrictModel):
    """The space to be created."""
    name: str = Field(default=..., description="The name for the new private space. Must not exceed 200 characters.", max_length=200)
    key: str | None = Field(default=None, description="The key for the new space. Format: See [Space\nkeys](https://confluence.atlassian.com/x/lqNMMQ). If `alias` is not provided, this is required.")
    alias: str | None = Field(default=None, description="This field will be used as the new identifier for the space in confluence page URLs.\nIf the property is not provided the alias will be the provided key.\nThis property is experimental and may be changed or removed in the future.")
    permissions: list[SpacePermissionCreate] | None = Field(default=None, description="The permissions for the new space. If no permissions are provided, the\n[Confluence default space permissions](https://confluence.atlassian.com/x/UAgzKw#CreateaSpace-Spacepermissions)\nare applied. Note that if permissions are provided, the space is\ncreated with only the provided set of permissions, not\nincluding the default space permissions. Space permissions\ncan be modified after creation using the space permissions\nendpoints, and a private space can be created using the\ncreate private space endpoint.")
    description: CreatePrivateSpaceRequestBodyDescription | None = None
class CreatePrivateSpaceRequest(StrictModel):
    """Creates a new private space visible only to the creator. Requires 'Create Space(s)' global permission."""
    body: CreatePrivateSpaceRequestBody

# Operation: update_space
class UpdateSpaceRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique key identifier of the space to update.")
class UpdateSpaceRequestBody(StrictModel):
    """The updated space."""
    name: str | None = Field(default=None, description="The new name for the space.", max_length=200)
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The new type classification for the space.")
class UpdateSpaceRequest(StrictModel):
    """Updates a space's name, description, or homepage. Requires 'Admin' permission for the space. Note that permissions and space labels cannot be modified through this API."""
    path: UpdateSpaceRequestPath
    body: UpdateSpaceRequestBody | None = None

# Operation: delete_space
class DeleteSpaceRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique key identifier of the space to delete. This is the space's short name used in URLs and references.")
class DeleteSpaceRequest(StrictModel):
    """Permanently deletes a space without sending it to trash. The deletion occurs as a long-running task, so the space may not be immediately deleted when the response is returned. Poll the status link in the response to monitor task completion."""
    path: DeleteSpaceRequestPath

# Operation: grant_custom_content_permission
class AddCustomContentPermissionsRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique key identifier of the Confluence space where the permission will be granted.")
class AddCustomContentPermissionsRequestBodySubject(StrictModel):
    type_: Literal["user", "group"] = Field(default=..., validation_alias="type", serialization_alias="type", description="The type of principal receiving the permission: either a user account or a group.")
    identifier: str = Field(default=..., validation_alias="identifier", serialization_alias="identifier", description="The unique identifier of the principal. For users, provide the accountId or 'anonymous' for anonymous access. For groups, provide the groupId.")
class AddCustomContentPermissionsRequestBody(StrictModel):
    """The permissions to be created."""
    operations: list[AddCustomContentPermissionsBodyOperationsItem] = Field(default=..., description="An array of permission operations to grant to the specified principal. Each operation defines what actions are permitted on custom content within the space.")
    subject: AddCustomContentPermissionsRequestBodySubject
class AddCustomContentPermissionsRequest(StrictModel):
    """Grants a new custom content permission to a user or group within a Confluence space. Only apps can modify app-specific permissions, and the requesting user must have Admin permission for the space."""
    path: AddCustomContentPermissionsRequestPath
    body: AddCustomContentPermissionsRequestBody

# Operation: delete_space_permission
class RemovePermissionRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique key identifier of the space from which the permission will be removed.")
    id_: int = Field(default=..., validation_alias="id", serialization_alias="id", description="The unique identifier of the permission record to be deleted.")
class RemovePermissionRequest(StrictModel):
    """Removes a specific permission from a space. Deleting Read Space permission for a user or group will cascade and remove all other space permissions for that user or group."""
    path: RemovePermissionRequestPath

# Operation: list_space_content_states
class GetSpaceContentStatesRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique identifier key of the space whose suggested content states should be retrieved.")
class GetSpaceContentStatesRequest(StrictModel):
    """Retrieve the content states that are suggested for use within a specific Confluence space. Requires 'View' permission for the space."""
    path: GetSpaceContentStatesRequestPath

# Operation: list_space_content_by_state
class GetContentsWithStateRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The key identifier of the space to query for content with the specified state.")
class GetContentsWithStateRequestQuery(StrictModel):
    state_id: int = Field(default=..., validation_alias="state-id", serialization_alias="state-id", description="The numeric identifier of the content state to filter results by.", json_schema_extra={'format': 'int32'})
    limit: int | None = Field(default=None, description="Maximum number of results to return in the response.", json_schema_extra={'format': 'int32'})
class GetContentsWithStateRequest(StrictModel):
    """Retrieve all content in a space filtered by a specific content state. Requires 'View' permission for the space. Note: When using expand parameter with body.export_view and/or body.styled_view, the limit is restricted to a maximum of 25."""
    path: GetContentsWithStateRequestPath
    query: GetContentsWithStateRequestQuery

# Operation: get_space_theme
class GetSpaceThemeRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique identifier key of the space whose theme should be retrieved.")
class GetSpaceThemeRequest(StrictModel):
    """Retrieves the theme configuration for a space. If no custom theme is set, the space inherits the global look and feel settings."""
    path: GetSpaceThemeRequestPath

# Operation: apply_space_theme
class SetSpaceThemeRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique identifier key of the space where the theme will be applied.")
class SetSpaceThemeRequestBody(StrictModel):
    theme_key: str = Field(default=..., validation_alias="themeKey", serialization_alias="themeKey", description="The unique identifier key of the theme to apply to the space.")
class SetSpaceThemeRequest(StrictModel):
    """Apply a theme to a Confluence space. Requires 'Admin' permission for the space. To reset to the default theme, use the reset_space_theme operation instead."""
    path: SetSpaceThemeRequestPath
    body: SetSpaceThemeRequestBody

# Operation: list_space_watchers
class GetWatchersForSpaceRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique identifier key of the space for which to retrieve watchers.")
class GetWatchersForSpaceRequestQuery(StrictModel):
    limit: str | None = Field(default=None, description="The maximum number of watchers to return in the response. The actual limit may be restricted by system configuration.")
class GetWatchersForSpaceRequest(StrictModel):
    """Retrieves a list of users watching a specific space. Use this to see who is monitoring updates to a space."""
    path: GetWatchersForSpaceRequestPath
    query: GetWatchersForSpaceRequestQuery | None = None

# Operation: list_space_labels
class GetLabelsForSpaceRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique identifier key of the space from which to retrieve labels.")
class GetLabelsForSpaceRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of labels to return in a single page of results. The system may enforce additional limits on this value.", json_schema_extra={'format': 'int32'})
class GetLabelsForSpaceRequest(StrictModel):
    """Retrieves all labels associated with a Confluence space, with optional filtering and pagination support."""
    path: GetLabelsForSpaceRequestPath
    query: GetLabelsForSpaceRequestQuery | None = None

# Operation: add_space_labels
class AddLabelsToSpaceRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique key identifier of the space where labels will be added.")
class AddLabelsToSpaceRequestBody(StrictModel):
    """The labels to add to the content."""
    body: list[LabelCreate] = Field(default=..., description="An array of label objects to add to the space. Each label in the array will be appended to the space's existing labels.")
class AddLabelsToSpaceRequest(StrictModel):
    """Adds one or more labels to a space without removing existing labels. This operation appends new labels to the space's current label set."""
    path: AddLabelsToSpaceRequestPath
    body: AddLabelsToSpaceRequestBody

# Operation: remove_label_from_space
class DeleteLabelFromSpaceRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique identifier (key) of the space from which the label should be removed.")
class DeleteLabelFromSpaceRequestQuery(StrictModel):
    name: str = Field(default=..., description="The name of the label to remove from the space.")
class DeleteLabelFromSpaceRequest(StrictModel):
    """Remove a label from a space. This operation deletes the association between a specific label and the space identified by its key."""
    path: DeleteLabelFromSpaceRequestPath
    query: DeleteLabelFromSpaceRequestQuery

# Operation: create_template
class CreateContentTemplateRequestBodyBodyView(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in view format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the view body.")
class CreateContentTemplateRequestBodyBodyExportView(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in export_view format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the export_view body.")
class CreateContentTemplateRequestBodyBodyStyledView(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in styled_view format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the styled_view body.")
class CreateContentTemplateRequestBodyBodyStorage(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in storage format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the storage body.")
class CreateContentTemplateRequestBodyBodyEditor(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in editor format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the editor body.")
class CreateContentTemplateRequestBodyBodyEditor2(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in editor2 format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the editor2 body.")
class CreateContentTemplateRequestBodyBodyWiki(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in wiki format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the wiki body.")
class CreateContentTemplateRequestBodyBodyAtlasDocFormat(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in atlas_doc_format format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the atlas_doc_format body.")
class CreateContentTemplateRequestBodyBodyAnonymousExportView(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in anonymous_export_view format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the anonymous_export_view body.")
class CreateContentTemplateRequestBodyBody(StrictModel):
    view: CreateContentTemplateRequestBodyBodyView
    export_view: CreateContentTemplateRequestBodyBodyExportView
    styled_view: CreateContentTemplateRequestBodyBodyStyledView
    storage: CreateContentTemplateRequestBodyBodyStorage
    editor: CreateContentTemplateRequestBodyBodyEditor
    editor2: CreateContentTemplateRequestBodyBodyEditor2
    wiki: CreateContentTemplateRequestBodyBodyWiki
    atlas_doc_format: CreateContentTemplateRequestBodyBodyAtlasDocFormat
    anonymous_export_view: CreateContentTemplateRequestBodyBodyAnonymousExportView
class CreateContentTemplateRequestBodySpace(StrictModel):
    key: str = Field(default=..., validation_alias="key", serialization_alias="key", description="The unique key identifier for the template.")
class CreateContentTemplateRequestBody(StrictModel):
    """The content template to be created.
The content body must be in 'storage' format."""
    name: str = Field(default=..., description="The name of the template to create.")
    template_type: str = Field(default=..., validation_alias="templateType", serialization_alias="templateType", description="The type of template being created.")
    body: CreateContentTemplateRequestBodyBody
    space: CreateContentTemplateRequestBodySpace
class CreateContentTemplateRequest(StrictModel):
    """Creates a new content template for a space or globally. Requires 'Admin' permission for the space or 'Confluence Administrator' global permission. Note: blueprint templates cannot be created via this API."""
    body: CreateContentTemplateRequestBody

# Operation: update_template
class UpdateContentTemplateRequestBodyBodyView(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in view format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the view body.")
class UpdateContentTemplateRequestBodyBodyExportView(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in export_view format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the export_view body.")
class UpdateContentTemplateRequestBodyBodyStyledView(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in styled_view format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the styled_view body.")
class UpdateContentTemplateRequestBodyBodyStorage(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in storage format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the storage body.")
class UpdateContentTemplateRequestBodyBodyEditor(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in editor format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the editor body.")
class UpdateContentTemplateRequestBodyBodyEditor2(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in editor2 format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the editor2 body.")
class UpdateContentTemplateRequestBodyBodyWiki(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in wiki format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the wiki body.")
class UpdateContentTemplateRequestBodyBodyAtlasDocFormat(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in atlas_doc_format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the atlas_doc_format body.")
class UpdateContentTemplateRequestBodyBodyAnonymousExportView(StrictModel):
    value: str = Field(default=..., validation_alias="value", serialization_alias="value", description="The template body content in anonymous_export_view format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(default=..., validation_alias="representation", serialization_alias="representation", description="The content representation format for the anonymous_export_view body.")
class UpdateContentTemplateRequestBodyBody(StrictModel):
    view: UpdateContentTemplateRequestBodyBodyView
    export_view: UpdateContentTemplateRequestBodyBodyExportView
    styled_view: UpdateContentTemplateRequestBodyBodyStyledView
    storage: UpdateContentTemplateRequestBodyBodyStorage
    editor: UpdateContentTemplateRequestBodyBodyEditor
    editor2: UpdateContentTemplateRequestBodyBodyEditor2
    wiki: UpdateContentTemplateRequestBodyBodyWiki
    atlas_doc_format: UpdateContentTemplateRequestBodyBodyAtlasDocFormat
    anonymous_export_view: UpdateContentTemplateRequestBodyBodyAnonymousExportView
class UpdateContentTemplateRequestBodySpace(StrictModel):
    key: str = Field(default=..., validation_alias="key", serialization_alias="key", description="The template key identifier used for internal reference.")
class UpdateContentTemplateRequestBody(StrictModel):
    """The updated content template."""
    template_id: str = Field(default=..., validation_alias="templateId", serialization_alias="templateId", description="The unique identifier of the template to update.")
    name: str = Field(default=..., description="The display name of the template. Retain the current name if not being changed.")
    template_type: Literal["page"] = Field(default=..., validation_alias="templateType", serialization_alias="templateType", description="The template type. Must be set to 'page' for content templates.")
    body: UpdateContentTemplateRequestBodyBody
    space: UpdateContentTemplateRequestBodySpace
class UpdateContentTemplateRequest(StrictModel):
    """Updates an existing content template with new content and metadata. Requires 'Admin' permission for space templates or 'Confluence Administrator' global permission for global templates. Blueprint templates cannot be updated via this API."""
    body: UpdateContentTemplateRequestBody

# Operation: list_blueprint_templates
class GetBlueprintTemplatesRequestQuery(StrictModel):
    space_key: str | None = Field(default=None, validation_alias="spaceKey", serialization_alias="spaceKey", description="The space key to query for templates. Omit this parameter to retrieve global blueprint templates instead of space-specific ones.")
    limit: int | None = Field(default=None, description="The maximum number of templates to return in a single response. The system may enforce additional limits on this value.", json_schema_extra={'format': 'int32'})
class GetBlueprintTemplatesRequest(StrictModel):
    """Retrieve all blueprint templates available globally or within a specific space. Global templates are inherited by all spaces, while space-specific templates can be customized independently."""
    query: GetBlueprintTemplatesRequestQuery | None = None

# Operation: list_templates
class GetContentTemplatesRequestQuery(StrictModel):
    space_key: str | None = Field(default=None, validation_alias="spaceKey", serialization_alias="spaceKey", description="The space key to retrieve templates from. Omit this parameter to retrieve global templates instead of space-specific templates.")
    limit: int | None = Field(default=None, description="The maximum number of templates to return per page. The system may enforce lower limits than requested.", json_schema_extra={'format': 'int32'})
class GetContentTemplatesRequest(StrictModel):
    """Retrieve all content templates, either globally or within a specific space. Requires 'View' permission for space templates or 'Can use' global permission for global templates."""
    query: GetContentTemplatesRequestQuery | None = None

# Operation: get_template
class GetContentTemplateRequestPath(StrictModel):
    content_template_id: str = Field(default=..., validation_alias="contentTemplateId", serialization_alias="contentTemplateId", description="The unique identifier of the content template to retrieve.")
class GetContentTemplateRequest(StrictModel):
    """Retrieves a content template with its metadata, including name, space or blueprint location, and template body. Requires 'View' permission for space templates or 'Can use' global permission for global templates."""
    path: GetContentTemplateRequestPath

# Operation: delete_template
class RemoveTemplateRequestPath(StrictModel):
    content_template_id: str = Field(default=..., validation_alias="contentTemplateId", serialization_alias="contentTemplateId", description="The unique identifier of the template to be deleted.")
class RemoveTemplateRequest(StrictModel):
    """Deletes a template, with behavior varying by template type: content templates are removed, modified space-level or global-level blueprint templates revert to their parent templates, and unmodified blueprint templates cannot be deleted. Requires 'Admin' permission for space templates or 'Confluence Administrator' global permission for global templates."""
    path: RemoveTemplateRequestPath

# Operation: get_user
class GetUserRequestQuery(StrictModel):
    account_id: str = Field(default=..., validation_alias="accountId", serialization_alias="accountId", description="The unique account ID that identifies the user across all Atlassian products. This is a required identifier to retrieve the specific user's information.")
class GetUserRequest(StrictModel):
    """Retrieve detailed information about a specific user, including display name, account ID, profile picture, and other profile data. Information returned may be restricted based on the user's profile visibility settings."""
    query: GetUserRequestQuery

# Operation: list_user_groups
class GetGroupMembershipsForUserRequestQuery(StrictModel):
    account_id: str = Field(default=..., validation_alias="accountId", serialization_alias="accountId", description="The account ID that uniquely identifies the user across all Atlassian products.")
    limit: int | None = Field(default=None, description="The maximum number of groups to return per page. This value may be restricted by system limits.", json_schema_extra={'format': 'int32'})
class GetGroupMembershipsForUserRequest(StrictModel):
    """Retrieves all groups that a user is a member of. Requires permission to access the Confluence site."""
    query: GetGroupMembershipsForUserRequestQuery

# Operation: list_users
class GetBulkUserLookupRequestQuery(StrictModel):
    account_id: str = Field(default=..., validation_alias="accountId", serialization_alias="accountId", description="Comma-separated list of account IDs identifying the users to retrieve. Maximum of 100 IDs per request; excess IDs are ignored.")
class GetBulkUserLookupRequest(StrictModel):
    """Retrieve detailed information for multiple users by their account IDs. Returns up to 100 user records per request; additional IDs beyond the limit are ignored."""
    query: GetBulkUserLookupRequestQuery

# Operation: check_content_watch_status
class GetContentWatchStatusRequestPath(StrictModel):
    content_id: str = Field(default=..., validation_alias="contentId", serialization_alias="contentId", description="The unique identifier of the content to check watch status for.")
class GetContentWatchStatusRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user whose watch status should be checked. If not provided, the currently authenticated user's status is returned. The accountId uniquely identifies the user across all Atlassian products.")
class GetContentWatchStatusRequest(StrictModel):
    """Check whether a user is watching a specific piece of content. Requires 'Confluence Administrator' permission if checking another user's status, otherwise only 'Can use' permission is needed."""
    path: GetContentWatchStatusRequestPath
    query: GetContentWatchStatusRequestQuery | None = None

# Operation: watch_content
class AddContentWatcherRequestPath(StrictModel):
    content_id: str = Field(default=..., validation_alias="contentId", serialization_alias="contentId", description="The unique identifier of the content to add the watcher to.")
class AddContentWatcherRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user to add as a watcher. If not provided, the currently logged-in user will be used. Requires 'Confluence Administrator' global permission when specified.")
class AddContentWatcherRequest(StrictModel):
    """Add a user as a watcher to a piece of content in Confluence. The watcher can be specified by account ID, or if not specified, the currently logged-in user will be added as a watcher."""
    path: AddContentWatcherRequestPath
    query: AddContentWatcherRequestQuery | None = None

# Operation: unwatch_content
class RemoveContentWatcherRequestPath(StrictModel):
    content_id: str = Field(default=..., validation_alias="contentId", serialization_alias="contentId", description="The unique identifier of the content from which to remove the watcher.")
class RemoveContentWatcherRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user to remove as a watcher. If not provided, the currently logged-in user is removed. The accountId uniquely identifies the user across all Atlassian products.")
class RemoveContentWatcherRequestHeader(StrictModel):
    x_atlassian_token: str = Field(default=..., validation_alias="X-Atlassian-Token", serialization_alias="X-Atlassian-Token", description="XSRF protection token required for this DELETE operation.")
class RemoveContentWatcherRequest(StrictModel):
    """Remove a user as a watcher from content. Specify a user by accountId, or omit to remove the currently logged-in user. Requires 'Confluence Administrator' permission if specifying another user, otherwise standard site access permission."""
    path: RemoveContentWatcherRequestPath
    query: RemoveContentWatcherRequestQuery | None = None
    header: RemoveContentWatcherRequestHeader

# Operation: check_label_watch_status
class IsWatchingLabelRequestPath(StrictModel):
    label_name: str = Field(default=..., validation_alias="labelName", serialization_alias="labelName", description="The name of the label to check watch status for.")
class IsWatchingLabelRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user to check. If not provided, the currently logged-in user is used. Required if checking another user's watch status.")
class IsWatchingLabelRequest(StrictModel):
    """Check whether a user is watching a specific label in Confluence. If no user is specified, the currently logged-in user is checked."""
    path: IsWatchingLabelRequestPath
    query: IsWatchingLabelRequestQuery | None = None

# Operation: watch_label
class AddLabelWatcherRequestPath(StrictModel):
    label_name: str = Field(default=..., validation_alias="labelName", serialization_alias="labelName", description="The name of the label to watch.")
class AddLabelWatcherRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user to add as a watcher. If not provided, the currently authenticated user is used. Required only if you have 'Confluence Administrator' permission; otherwise, the authenticated user is assumed.")
class AddLabelWatcherRequestHeader(StrictModel):
    x_atlassian_token: str = Field(default=..., validation_alias="X-Atlassian-Token", serialization_alias="X-Atlassian-Token", description="XSRF protection token. Must be set to 'no-check' for this operation.")
class AddLabelWatcherRequest(StrictModel):
    """Subscribe a user as a watcher to a label in Confluence. The watcher will receive notifications for changes to the label. If no user is specified, the currently authenticated user is subscribed."""
    path: AddLabelWatcherRequestPath
    query: AddLabelWatcherRequestQuery | None = None
    header: AddLabelWatcherRequestHeader

# Operation: unwatch_label
class RemoveLabelWatcherRequestPath(StrictModel):
    label_name: str = Field(default=..., validation_alias="labelName", serialization_alias="labelName", description="The name of the label from which to remove the watcher.")
class RemoveLabelWatcherRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user to remove as a watcher. If not specified, the currently logged-in user will be used. Required only if removing a different user (requires Confluence Administrator permission).")
class RemoveLabelWatcherRequest(StrictModel):
    """Remove a user as a watcher from a label in Confluence. If no user is specified, the currently logged-in user will be removed as a watcher."""
    path: RemoveLabelWatcherRequestPath
    query: RemoveLabelWatcherRequestQuery | None = None

# Operation: check_space_watch_status
class IsWatchingSpaceRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The unique identifier key of the space to check watch status for.")
class IsWatchingSpaceRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user to check watch status for. If not provided, the currently logged-in user is used. Requires 'Confluence Administrator' permission when specified.")
class IsWatchingSpaceRequest(StrictModel):
    """Check whether a user is watching a specific space. Identifies the user via account ID query parameter or uses the currently logged-in user if not specified."""
    path: IsWatchingSpaceRequestPath
    query: IsWatchingSpaceRequestQuery | None = None

# Operation: watch_space
class AddSpaceWatcherRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The key identifier of the space to add the watcher to.")
class AddSpaceWatcherRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user to add as a watcher. If not provided, the currently logged-in user will be used. Required only when adding a watcher other than yourself.")
class AddSpaceWatcherRequestHeader(StrictModel):
    x_atlassian_token: str = Field(default=..., validation_alias="X-Atlassian-Token", serialization_alias="X-Atlassian-Token", description="XSRF protection token. Must be set to 'no-check' for this operation.")
class AddSpaceWatcherRequest(StrictModel):
    """Adds a user as a watcher to a Confluence space. If no user is specified, the currently logged-in user will be added as a watcher."""
    path: AddSpaceWatcherRequestPath
    query: AddSpaceWatcherRequestQuery | None = None
    header: AddSpaceWatcherRequestHeader

# Operation: unwatch_space
class RemoveSpaceWatchRequestPath(StrictModel):
    space_key: str = Field(default=..., validation_alias="spaceKey", serialization_alias="spaceKey", description="The key that uniquely identifies the space from which to remove the watcher.")
class RemoveSpaceWatchRequestQuery(StrictModel):
    account_id: str | None = Field(default=None, validation_alias="accountId", serialization_alias="accountId", description="The account ID of the user to remove as a watcher. If not provided, the currently logged-in user will be removed. The accountId uniquely identifies the user across all Atlassian products.")
class RemoveSpaceWatchRequest(StrictModel):
    """Remove a user as a watcher from a space. Specify a user by accountId, or omit to remove the currently logged-in user. Requires 'Confluence Administrator' permission if removing another user, otherwise requires site access permission."""
    path: RemoveSpaceWatchRequestPath
    query: RemoveSpaceWatchRequestQuery | None = None

# Operation: fetch_user_emails_bulk
class GetPrivacyUnsafeUserEmailBulkRequestQuery(StrictModel):
    account_id: list[str] = Field(default=..., validation_alias="accountId", serialization_alias="accountId", description="An array of account IDs identifying the users whose email addresses should be retrieved. Users with unavailable accounts will be excluded from the results.")
class GetPrivacyUnsafeUserEmailBulkRequest(StrictModel):
    """Retrieve email addresses for multiple users in a single batch request, bypassing profile visibility restrictions. This operation requires appropriate permissions and is subject to app approval guidelines for Connect apps or asApp() context for Forge apps."""
    query: GetPrivacyUnsafeUserEmailBulkRequestQuery

# Operation: get_content_views
class GetViewsRequestPath(StrictModel):
    content_id: str = Field(default=..., validation_alias="contentId", serialization_alias="contentId", description="The unique identifier of the content whose view count should be retrieved.")
class GetViewsRequestQuery(StrictModel):
    from_date: str | None = Field(default=None, validation_alias="fromDate", serialization_alias="fromDate", description="Filter results to include only views from this date forward. Specify in ISO 8601 format.")
class GetViewsRequest(StrictModel):
    """Retrieve the total number of views for a specific piece of content, optionally filtered from a given date onwards."""
    path: GetViewsRequestPath
    query: GetViewsRequestQuery | None = None

# Operation: get_content_viewers
class GetViewersRequestPath(StrictModel):
    content_id: str = Field(default=..., validation_alias="contentId", serialization_alias="contentId", description="The unique identifier of the content to retrieve viewer analytics for.")
class GetViewersRequestQuery(StrictModel):
    from_date: str | None = Field(default=None, validation_alias="fromDate", serialization_alias="fromDate", description="Filter results to include only views from this date forward. Use ISO 8601 format for the timestamp.")
class GetViewersRequest(StrictModel):
    """Retrieve the total number of distinct viewers for a specific piece of content, optionally filtered by a start date."""
    path: GetViewersRequestPath
    query: GetViewersRequestQuery | None = None

# Operation: list_user_properties
class GetUserPropertiesRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The account ID of the user whose properties you want to retrieve.")
class GetUserPropertiesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of properties to return in a single page of results. The system may enforce stricter limits than the specified maximum.", json_schema_extra={'format': 'int32'})
class GetUserPropertiesRequest(StrictModel):
    """Retrieves all properties associated with a user account on the Confluence site. User properties are stored at the site level and provide metadata about the user."""
    path: GetUserPropertiesRequestPath
    query: GetUserPropertiesRequestQuery | None = None

# Operation: get_user_property
class GetUserPropertyRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The account ID of the user whose property you want to retrieve.")
    key: str = Field(default=..., description="The key identifying which user property to retrieve. Keys must contain only alphanumeric characters, hyphens, and underscores.", pattern='^[-_a-zA-Z0-9]+$')
class GetUserPropertyRequest(StrictModel):
    """Retrieves a specific property for a Confluence user by its key. User properties are stored at the site level and require 'Can use' global permission to access."""
    path: GetUserPropertyRequestPath

# Operation: set_user_property
class CreateUserPropertyRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The account ID of the user. This uniquely identifies the user across all Atlassian products.")
    key: str = Field(default=..., description="The key identifying this user property. Keys must contain only alphanumeric characters, hyphens, and underscores.", pattern='^[-_a-zA-Z0-9]+$')
class CreateUserPropertyRequestBody(StrictModel):
    """The user property to be created."""
    value: dict[str, Any] = Field(default=..., description="The value to store for this user property. Can be any JSON-serializable object.")
class CreateUserPropertyRequest(StrictModel):
    """Set a custom property for a user at the Confluence site level. User properties enable storing arbitrary metadata associated with user accounts across the Confluence instance."""
    path: CreateUserPropertyRequestPath
    body: CreateUserPropertyRequestBody

# Operation: set_user_property_value
class UpdateUserPropertyRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The account ID of the user. This uniquely identifies the user across all Atlassian products.")
    key: str = Field(default=..., description="The key identifier for the user property. Must contain only alphanumeric characters, hyphens, and underscores.", pattern='^[-_a-zA-Z0-9]+$')
class UpdateUserPropertyRequestBody(StrictModel):
    """The user property to be updated."""
    value: dict[str, Any] = Field(default=..., description="The new value to assign to the user property. Can be any JSON-serializable object.")
class UpdateUserPropertyRequest(StrictModel):
    """Updates or sets a property value for a user on the Confluence site. The property key cannot be changed, only its value can be modified."""
    path: UpdateUserPropertyRequestPath
    body: UpdateUserPropertyRequestBody

# Operation: remove_user_property
class DeleteUserPropertyRequestPath(StrictModel):
    user_id: str = Field(default=..., validation_alias="userId", serialization_alias="userId", description="The account ID that uniquely identifies the user across all Atlassian products.")
    key: str = Field(default=..., description="The key identifying which user property to delete. Must contain only alphanumeric characters, hyphens, and underscores.", pattern='^[-_a-zA-Z0-9]+$')
class DeleteUserPropertyRequest(StrictModel):
    """Removes a custom property from a user account on the Confluence site. User properties are stored at the site level and are distinct from space or content-level properties."""
    path: DeleteUserPropertyRequestPath

# ============================================================================
# Component Models
# ============================================================================

class AccountId(PermissiveModel):
    account_id: str = Field(..., validation_alias="accountId", serialization_alias="accountId")

class AddCustomContentPermissionsBodyOperationsItem(PermissiveModel):
    key: Literal["read", "create", "delete"] = Field(..., description="The operation type")
    target: str = Field(..., description="The custom content type")
    access: bool = Field(..., description="Grant or restrict access")

class ArchivePagesBodyPagesItem(PermissiveModel):
    id_: int = Field(..., validation_alias="id", serialization_alias="id", description="The `id` of the page to be archived.", json_schema_extra={'format': 'int64'})

class ButtonLookAndFeel(PermissiveModel):
    background_color: str = Field(..., validation_alias="backgroundColor", serialization_alias="backgroundColor")
    color: str

class Container(RootModel[dict[str, Any]]):
    pass

class ContainerLookAndFeel(PermissiveModel):
    background: str
    background_attachment: str | None = Field(None, validation_alias="backgroundAttachment", serialization_alias="backgroundAttachment")
    background_blend_mode: str | None = Field(None, validation_alias="backgroundBlendMode", serialization_alias="backgroundBlendMode")
    background_clip: str | None = Field(None, validation_alias="backgroundClip", serialization_alias="backgroundClip")
    background_color: str | None = Field(..., validation_alias="backgroundColor", serialization_alias="backgroundColor")
    background_image: str | None = Field(..., validation_alias="backgroundImage", serialization_alias="backgroundImage")
    background_origin: str | None = Field(None, validation_alias="backgroundOrigin", serialization_alias="backgroundOrigin")
    background_position: str | None = Field(None, validation_alias="backgroundPosition", serialization_alias="backgroundPosition")
    background_repeat: str | None = Field(None, validation_alias="backgroundRepeat", serialization_alias="backgroundRepeat")
    background_size: str | None = Field(..., validation_alias="backgroundSize", serialization_alias="backgroundSize")
    padding: str
    border_radius: str = Field(..., validation_alias="borderRadius", serialization_alias="borderRadius")

class ContentBodyCreate(PermissiveModel):
    """This object is used when creating or updating content."""
    value: str = Field(..., description="The body of the content in the relevant format.")
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "plain", "raw"] = Field(..., description="The content format type. Set the value of this property to\nthe name of the format being used, e.g. 'storage'.")

class ContentBodyConversionInput(PermissiveModel):
    to: str = Field(..., description="The name of the target format for the content body conversion.")
    allow_cache: bool | None = Field(False, validation_alias="allowCache", serialization_alias="allowCache", description="Controls whether conversion results are cached and reused for identical requests.\n\n- `false`: Each request creates a new conversion task, even if an identical request was made previously.\n- `true`: Enables caching behavior for identical requests from the same user.\n  - If no cached result exists, a new conversion task is created\n  - If a cached result exists, the existing task is marked as RERUNNING and will complete with status COMPLETED\n  - Returns the same task ID for identical requests, allowing you to retrieve the cached result")
    space_key_context: str | None = Field(None, validation_alias="spaceKeyContext", serialization_alias="spaceKeyContext", description="The space key used for resolving embedded content (page includes, files, and links) in the content body. For example, if the source content contains the link `<ac:link><ri:page ri:content-title=\"Example page\" /><ac:link>` and the `spaceKeyContext=TEST` parameter is provided, then the link will be converted into a link to the \"Example page\" page in the \"TEST\" space.")
    content_id_context: str | None = Field(None, validation_alias="contentIdContext", serialization_alias="contentIdContext", description="The content ID used to find the space for resolving embedded content (page includes, files, and links) in the content body. For example, if the source content contains the link `<ac:link><ri:page ri:content-title=\"Example page\" /><ac:link>` and the `contentIdContext=123` parameter is provided, then the link will be converted into a link to the \"Example page\" page in the same space that has the content with ID=123. Note that `spaceKeyContext` will be ignored if this parameter is provided.")
    embedded_content_render: Literal["current", "version-at-save"] | None = Field('current', validation_alias="embeddedContentRender", serialization_alias="embeddedContentRender", description="Mode used for rendering embedded content, such as attachments. - `current` renders the embedded content using the latest version. - `version-at-save` renders the embedded content using the version at the time of save.")
    expand: list[str] | None = Field(None, description="A multi-value, comma-separated parameter indicating which properties of the content to expand and populate. Expands are dependent\non the `to` conversion format and may be irrelevant for certain conversions (e.g. `macroRenderedOutput` is redundant when\nconverting to `view` format). \n\nIf rendering to `view` format, and the body content being converted includes arbitrary nested content (such as macros); then it is \nnecessary to include webresource expands in the request. Webresources for content body are the batched JS and CSS dependencies for\nany nested dynamic content (i.e. macros).\n\n- `embeddedContent` returns metadata for nested content (e.g. page included using page include macro)\n- `mediaToken` returns JWT token for retrieving attachment data from Media API\n- `macroRenderedOutput` additionally converts body to view format\n- `webresource.superbatch.uris.js` returns all common JS dependencies as static URLs\n- `webresource.superbatch.uris.css` returns all common CSS dependencies as static URLs...")
    body: ContentBodyCreate

class ContentBodyExpandable(PermissiveModel):
    editor: str | None = None
    view: str | None = None
    export_view: str | None = None
    styled_view: str | None = None
    storage: str | None = None
    editor2: str | None = None
    anonymous_export_view: str | None = None
    atlas_doc_format: str | None = None
    wiki: str | None = None
    dynamic: str | None = None
    raw: str | None = None

class ContentBodyExpandable1(PermissiveModel):
    content: str | None = None
    embedded_content: str | None = Field(None, validation_alias="embeddedContent", serialization_alias="embeddedContent")
    webresource: str | None = None
    media_token: str | None = Field(None, validation_alias="mediaToken", serialization_alias="mediaToken")

class ContentBodyMediaToken(PermissiveModel):
    collection_ids: list[str] | None = Field(None, validation_alias="collectionIds", serialization_alias="collectionIds")
    content_id: str | None = Field(None, validation_alias="contentId", serialization_alias="contentId")
    expiry_date_time: str | None = Field(None, validation_alias="expiryDateTime", serialization_alias="expiryDateTime")
    file_ids: list[str] | None = Field(None, validation_alias="fileIds", serialization_alias="fileIds")
    token: str | None = None

class ContentChildTypeExpandable(PermissiveModel):
    all_: str | None = Field(None, validation_alias="all", serialization_alias="all")
    attachment: str | None = None
    comment: str | None = None
    page: str | None = None
    whiteboard: str | None = None
    database: str | None = None
    embed: str | None = None
    folder: str | None = None

class ContentChildrenExpandable(PermissiveModel):
    attachment: str | None = None
    comment: str | None = None
    page: str | None = None
    whiteboard: str | None = None
    database: str | None = None
    embed: str | None = None
    folder: str | None = None

class ContentExpandable(PermissiveModel):
    child_types: str | None = Field(None, validation_alias="childTypes", serialization_alias="childTypes")
    container: str | None = None
    metadata: str | None = None
    operations: str | None = None
    children: str | None = None
    restrictions: str | None = None
    history: str | None = None
    ancestors: str | None = None
    body: str | None = None
    version: str | None = None
    descendants: str | None = None
    space: str | None = None
    extensions: str | None = None
    schedule_publish_date: str | None = Field(None, validation_alias="schedulePublishDate", serialization_alias="schedulePublishDate")
    schedule_publish_info: str | None = Field(None, validation_alias="schedulePublishInfo", serialization_alias="schedulePublishInfo")
    macro_rendered_output: str | None = Field(None, validation_alias="macroRenderedOutput", serialization_alias="macroRenderedOutput")

class ContentHistoryExpandable(PermissiveModel):
    last_updated: str | None = Field(None, validation_alias="lastUpdated", serialization_alias="lastUpdated")
    previous_version: str | None = Field(None, validation_alias="previousVersion", serialization_alias="previousVersion")
    contributors: str | None = None
    next_version: str | None = Field(None, validation_alias="nextVersion", serialization_alias="nextVersion")
    owned_by: str | None = Field(None, validation_alias="ownedBy", serialization_alias="ownedBy")
    last_owned_by: str | None = Field(None, validation_alias="lastOwnedBy", serialization_alias="lastOwnedBy")

class ContentMetadataCurrentuserExpandable(PermissiveModel):
    favourited: str | None = None
    lastmodified: str | None = None
    lastcontributed: str | None = None
    viewed: str | None = None
    scheduled: str | None = None

class ContentMetadataCurrentuserFavourited(PermissiveModel):
    is_favourite: bool | None = Field(None, validation_alias="isFavourite", serialization_alias="isFavourite")
    favourited_date: str | None = Field(None, validation_alias="favouritedDate", serialization_alias="favouritedDate", json_schema_extra={'format': 'date-time'})

class ContentMetadataCurrentuserLastcontributed(PermissiveModel):
    status: str | None = None
    when: str | None = Field(None, json_schema_extra={'format': 'date-time'})

class ContentMetadataCurrentuserViewed(PermissiveModel):
    last_seen: str | None = Field(None, validation_alias="lastSeen", serialization_alias="lastSeen", json_schema_extra={'format': 'date-time'})
    friendly_last_seen: str | None = Field(None, validation_alias="friendlyLastSeen", serialization_alias="friendlyLastSeen")

class ContentRestrictionExpandable(PermissiveModel):
    restrictions: str | None = None
    content: str | None = None

class ContentRestrictionRestrictionsExpandable(PermissiveModel):
    user: str | None = None
    group: str | None = None

class ContentRestrictionUpdateRestrictionsGroupItem(PermissiveModel):
    """A group that the restriction will be applied to."""
    type_: Literal["group"] = Field(..., validation_alias="type", serialization_alias="type", description="Set to 'group'.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The id of the group.")

class ContentRestrictionsExpandable(PermissiveModel):
    read: str | None = None
    update: str | None = None

class CopyPageHierarchyTitleOptions(PermissiveModel):
    """Required for copying page in the same space."""
    prefix: str | None = None
    replace: str | None = None
    search: str | None = None

class CopyPageRequestDestination(PermissiveModel):
    """Defines where the page will be copied to, and can be one of the following types.

  - `parent_page`: page will be copied as a child of the specified parent page
  - `parent_content`: page will be copied as a child of the specified parent content
  - `space`: page will be copied to the specified space as a root page on the space
  - `existing_page`: page will be copied and replace the specified page"""
    type_: Literal["space", "existing_page", "parent_page", "parent_content"] = Field(..., validation_alias="type", serialization_alias="type")
    value: str = Field(..., description="The space key for `space` type, and content id for `parent_page`, `parent_content`, and `existing_page`")

class Embeddable(RootModel[dict[str, Any]]):
    pass

class EmbeddedContent(PermissiveModel):
    entity_id: int | None = Field(None, validation_alias="entityId", serialization_alias="entityId", json_schema_extra={'format': 'int64'})
    entity_type: str | None = Field(None, validation_alias="entityType", serialization_alias="entityType")
    entity: Embeddable | None = None

class GenericLinks(RootModel[dict[str, dict[str, Any] | str]]):
    pass

class ContentChildTypeAttachment(PermissiveModel):
    value: bool
    links: GenericLinks = Field(..., validation_alias="_links", serialization_alias="_links")

class ContentChildTypeComment(PermissiveModel):
    value: bool
    links: GenericLinks = Field(..., validation_alias="_links", serialization_alias="_links")

class ContentChildTypePage(PermissiveModel):
    value: bool
    links: GenericLinks = Field(..., validation_alias="_links", serialization_alias="_links")

class ContentChildType(PermissiveModel):
    """Shows whether a piece of content has attachments, comments, or child pages/whiteboards.
Note, this doesn't actually contain the child objects."""
    attachment: ContentChildTypeAttachment | None = None
    comment: ContentChildTypeComment | None = None
    page: ContentChildTypePage | None = None
    expandable: ContentChildTypeExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")

class Group(PermissiveModel):
    type_: Literal["group"] = Field(..., validation_alias="type", serialization_alias="type")
    name: str
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    usage_type: Literal["USERBASE_GROUP", "TEAM_COLLABORATION"] | None = Field('USERBASE_GROUP', validation_alias="usageType", serialization_alias="usageType", description="This property represents how this collection of users is used:\n  - `USERBASE_GROUP`: This value indicates that the collection of users is used as a group.\n  - `TEAM_COLLABORATION`: This value indicates that the collection of users is used as a team.")
    managed_by: Literal["ADMINS", "EXTERNAL", "TEAM_MEMBERS", "OPEN"] | None = Field('ADMINS', validation_alias="managedBy", serialization_alias="managedBy", description="This property represents how this collection of users is managed:\n  - `ADMINS`: This value indicates that the collection of users is managed by org, site or product admins.\n  - `EXTERNAL`: This value indicates that the collection of users is managed externally (through SCIM, HRIS, etc.).\n  - `TEAM_MEMBERS`: This value indicates that the collection of users is managed by its members.\n  - `OPEN`: This value indicates that the collection of users is not actively managed by any users.")
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class GroupArray(PermissiveModel):
    results: list[Group]
    start: int = Field(..., json_schema_extra={'format': 'int32'})
    limit: int = Field(..., json_schema_extra={'format': 'int32'})
    size: int = Field(..., json_schema_extra={'format': 'int32'})

class GroupCreate(PermissiveModel):
    type_: Literal["group"] = Field(..., validation_alias="type", serialization_alias="type")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")

class Icon(PermissiveModel):
    """This object represents an icon. If used as a profilePicture, this may be returned as null, depending on the user's privacy setting."""
    path: str
    width: int = Field(..., json_schema_extra={'format': 'int32'})
    height: int = Field(..., json_schema_extra={'format': 'int32'})
    is_default: bool = Field(..., validation_alias="isDefault", serialization_alias="isDefault")

class Label(PermissiveModel):
    prefix: str
    name: str
    id_: str = Field(..., validation_alias="id", serialization_alias="id")
    label: str

class LabelArray(PermissiveModel):
    results: list[Label]
    start: int | None = Field(None, json_schema_extra={'format': 'int32'})
    limit: int | None = Field(None, json_schema_extra={'format': 'int32'})
    size: int = Field(..., json_schema_extra={'format': 'int32'})
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class LabelCreate(PermissiveModel):
    prefix: str = Field(..., description="The prefix for the label. `global`, `my` `team`, etc.")
    name: str = Field(..., description="The name of the label, which will be shown in the UI.")

class LabelCreateArray(RootModel[list[LabelCreate]]):
    pass

class LookAndFeelBordersAndDividers(PermissiveModel):
    color: str

class LookAndFeelHeadings(PermissiveModel):
    color: str

class LookAndFeelLinks(PermissiveModel):
    color: str

class MenusLookAndFeelHoverOrFocus(PermissiveModel):
    background_color: str = Field(..., validation_alias="backgroundColor", serialization_alias="backgroundColor")

class MenusLookAndFeel(PermissiveModel):
    hover_or_focus: MenusLookAndFeelHoverOrFocus = Field(..., validation_alias="hoverOrFocus", serialization_alias="hoverOrFocus")
    color: str

class NavigationLookAndFeelHoverOrFocus(PermissiveModel):
    background_color: str = Field(..., validation_alias="backgroundColor", serialization_alias="backgroundColor")
    color: str

class NavigationLookAndFeel(PermissiveModel):
    color: str
    highlight_color: str | None = Field(None, validation_alias="highlightColor", serialization_alias="highlightColor")
    hover_or_focus: NavigationLookAndFeelHoverOrFocus = Field(..., validation_alias="hoverOrFocus", serialization_alias="hoverOrFocus")

class OperationCheckResult(PermissiveModel):
    """An operation and the target entity that it applies to, e.g. create page."""
    operation: Literal["administer", "archive", "clear_permissions", "copy", "create", "create_space", "delete", "export", "move", "purge", "purge_version", "read", "restore", "restrict_content", "update", "use"] = Field(..., description="The operation itself.")
    target_type: str = Field(..., validation_alias="targetType", serialization_alias="targetType", description="The space or content type that the operation applies to. Could be one of- - application - page - blogpost - comment - attachment - space")

class ScreenLookAndFeelLayer(PermissiveModel):
    width: str | None = None
    height: str | None = None

class ScreenLookAndFeel(PermissiveModel):
    background: str
    background_attachment: str | None = Field(None, validation_alias="backgroundAttachment", serialization_alias="backgroundAttachment")
    background_blend_mode: str | None = Field(None, validation_alias="backgroundBlendMode", serialization_alias="backgroundBlendMode")
    background_clip: str | None = Field(None, validation_alias="backgroundClip", serialization_alias="backgroundClip")
    background_color: str | None = Field(None, validation_alias="backgroundColor", serialization_alias="backgroundColor")
    background_image: str | None = Field(None, validation_alias="backgroundImage", serialization_alias="backgroundImage")
    background_origin: str | None = Field(None, validation_alias="backgroundOrigin", serialization_alias="backgroundOrigin")
    background_position: str | None = Field(None, validation_alias="backgroundPosition", serialization_alias="backgroundPosition")
    background_repeat: str | None = Field(None, validation_alias="backgroundRepeat", serialization_alias="backgroundRepeat")
    background_size: str | None = Field(None, validation_alias="backgroundSize", serialization_alias="backgroundSize")
    layer: ScreenLookAndFeelLayer | None = None
    gutter_top: str | None = Field(None, validation_alias="gutterTop", serialization_alias="gutterTop")
    gutter_right: str | None = Field(None, validation_alias="gutterRight", serialization_alias="gutterRight")
    gutter_bottom: str | None = Field(None, validation_alias="gutterBottom", serialization_alias="gutterBottom")
    gutter_left: str | None = Field(None, validation_alias="gutterLeft", serialization_alias="gutterLeft")

class ContentLookAndFeel(PermissiveModel):
    screen: ScreenLookAndFeel | None = None
    container: ContainerLookAndFeel | None = None
    header: ContainerLookAndFeel | None = None
    body: ContainerLookAndFeel | None = None

class SearchFieldLookAndFeel(PermissiveModel):
    background_color: str = Field(..., validation_alias="backgroundColor", serialization_alias="backgroundColor")
    color: str

class HeaderLookAndFeel(PermissiveModel):
    background_color: str = Field(..., validation_alias="backgroundColor", serialization_alias="backgroundColor")
    button: ButtonLookAndFeel
    primary_navigation: NavigationLookAndFeel = Field(..., validation_alias="primaryNavigation", serialization_alias="primaryNavigation")
    secondary_navigation: NavigationLookAndFeel = Field(..., validation_alias="secondaryNavigation", serialization_alias="secondaryNavigation")
    search: SearchFieldLookAndFeel

class SpaceDescription(PermissiveModel):
    value: str
    representation: Literal["plain", "view"]
    embedded_content: list[dict[str, Any]] = Field(..., validation_alias="embeddedContent", serialization_alias="embeddedContent")

class SpaceDescriptionExpandable(PermissiveModel):
    view: str | None = None
    plain: str | None = None

class SpaceExpandable(PermissiveModel):
    settings: str | None = None
    metadata: str | None = None
    operations: str | None = None
    look_and_feel: str | None = Field(None, validation_alias="lookAndFeel", serialization_alias="lookAndFeel")
    permissions: str | None = None
    icon: str | None = None
    description: str | None = None
    theme: str | None = None
    history: str | None = None
    homepage: str | None = None
    identifiers: str | None = None

class SpaceMetadata(PermissiveModel):
    labels: LabelArray | None = None
    expandable: dict[str, Any] | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")

class SpacePermissionCreateSubjectsGroup(PermissiveModel):
    results: list[GroupCreate]
    size: int = Field(..., json_schema_extra={'format': 'int32'})

class SpacePermissionSubjectsExpandable(PermissiveModel):
    user: str | None = None
    group: str | None = None

class SpacePermissionSubjectsGroup(PermissiveModel):
    results: list[Group]
    size: int = Field(..., json_schema_extra={'format': 'int32'})
    start: int | None = Field(None, json_schema_extra={'format': 'int32'})
    limit: int | None = Field(None, json_schema_extra={'format': 'int32'})

class SpaceSettingsEditor(PermissiveModel):
    page: str
    blogpost: str
    default: str

class SpaceSettings(PermissiveModel):
    route_override_enabled: bool = Field(..., validation_alias="routeOverrideEnabled", serialization_alias="routeOverrideEnabled", description="Defines whether an override for the space home should be used. This is\nused in conjunction with a space theme provided by an app. For\nexample, if this property is set to true, a theme can display a page\nother than the space homepage when users visit the root URL for a\nspace. This property allows apps to provide content-only theming\nwithout overriding the space home.")
    editor: SpaceSettingsEditor | None = None
    space_key: str | None = Field(None, validation_alias="spaceKey", serialization_alias="spaceKey")
    links: GenericLinks = Field(..., validation_alias="_links", serialization_alias="_links")

class SuperBatchWebResourcesTags(PermissiveModel):
    all_: str | None = Field(None, validation_alias="all", serialization_alias="all")
    css: str | None = None
    data: str | None = None
    js: str | None = None

class SuperBatchWebResourcesUris(PermissiveModel):
    all_: list[str] | str | None = Field(None, validation_alias="all", serialization_alias="all")
    css: list[str] | str | None = None
    js: list[str] | str | None = None

class SuperBatchWebResources(PermissiveModel):
    uris: SuperBatchWebResourcesUris | None = None
    tags: SuperBatchWebResourcesTags | None = None
    metatags: str | None = None
    expandable: dict[str, Any] | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")

class Theme(PermissiveModel):
    theme_key: str = Field(..., validation_alias="themeKey", serialization_alias="themeKey")
    name: str | None = None
    description: str | None = None
    icon: Icon | None = None
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class TopNavigationLookAndFeelHoverOrFocus(PermissiveModel):
    background_color: str | None = Field(None, validation_alias="backgroundColor", serialization_alias="backgroundColor")
    color: str | None = None

class TopNavigationLookAndFeel(PermissiveModel):
    color: str | None = None
    highlight_color: str = Field(..., validation_alias="highlightColor", serialization_alias="highlightColor")
    hover_or_focus: TopNavigationLookAndFeelHoverOrFocus | None = Field(None, validation_alias="hoverOrFocus", serialization_alias="hoverOrFocus")

class HorizontalHeaderLookAndFeel(PermissiveModel):
    background_color: str = Field(..., validation_alias="backgroundColor", serialization_alias="backgroundColor")
    button: ButtonLookAndFeel | None = None
    primary_navigation: TopNavigationLookAndFeel = Field(..., validation_alias="primaryNavigation", serialization_alias="primaryNavigation")
    secondary_navigation: NavigationLookAndFeel | None = Field(None, validation_alias="secondaryNavigation", serialization_alias="secondaryNavigation")
    search: SearchFieldLookAndFeel | None = None

class LookAndFeel(PermissiveModel):
    headings: LookAndFeelHeadings
    links: LookAndFeelLinks
    menus: MenusLookAndFeel
    header: HeaderLookAndFeel
    horizontal_header: HorizontalHeaderLookAndFeel | None = Field(None, validation_alias="horizontalHeader", serialization_alias="horizontalHeader")
    content: ContentLookAndFeel
    borders_and_dividers: LookAndFeelBordersAndDividers = Field(..., validation_alias="bordersAndDividers", serialization_alias="bordersAndDividers")
    space_reference: dict[str, Any] | None = Field(None, validation_alias="spaceReference", serialization_alias="spaceReference")

class UserDetailsBusiness(PermissiveModel):
    position: str | None = Field(None, description="This property has been deprecated due to privacy changes. There is no replacement. See the\n[migration guide](https://developer.atlassian.com/cloud/confluence/deprecation-notice-user-privacy-api-migration-guide/)\nfor details.")
    department: str | None = Field(None, description="This property has been deprecated due to privacy changes. There is no replacement. See the\n[migration guide](https://developer.atlassian.com/cloud/confluence/deprecation-notice-user-privacy-api-migration-guide/)\nfor details.")
    location: str | None = Field(None, description="This property has been deprecated due to privacy changes. There is no replacement. See the\n[migration guide](https://developer.atlassian.com/cloud/confluence/deprecation-notice-user-privacy-api-migration-guide/)\nfor details.")

class UserDetailsPersonal(PermissiveModel):
    phone: str | None = Field(None, description="This property has been deprecated due to privacy changes. There is no replacement. See the\n[migration guide](https://developer.atlassian.com/cloud/confluence/deprecation-notice-user-privacy-api-migration-guide/)\nfor details.")
    im: str | None = Field(None, description="This property has been deprecated due to privacy changes. There is no replacement. See the\n[migration guide](https://developer.atlassian.com/cloud/confluence/deprecation-notice-user-privacy-api-migration-guide/)\nfor details.")
    website: str | None = Field(None, description="This property has been deprecated due to privacy changes. There is no replacement. See the\n[migration guide](https://developer.atlassian.com/cloud/confluence/deprecation-notice-user-privacy-api-migration-guide/)\nfor details.")
    email: str | None = Field(None, description="This property has been deprecated due to privacy changes. Use the `User.email` property instead. See the\n[migration guide](https://developer.atlassian.com/cloud/confluence/deprecation-notice-user-privacy-api-migration-guide/)\nfor details.")

class UserDetails(PermissiveModel):
    business: UserDetailsBusiness | None = None
    personal: UserDetailsPersonal | None = None

class UserExpandable(PermissiveModel):
    operations: str | None = None
    details: str | None = None
    personal_space: str | None = Field(None, validation_alias="personalSpace", serialization_alias="personalSpace")

class VersionExpandable(PermissiveModel):
    content: str | None = None
    collaborators: str | None = None

class WebResourceDependenciesExpandable(PermissiveModel):
    uris: str | dict[str, Any] | None = None

class WebResourceDependenciesTags(PermissiveModel):
    all_: str | None = Field(None, validation_alias="all", serialization_alias="all")
    css: str | None = None
    data: str | None = None
    js: str | None = None
    expandable: dict[str, Any] | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")

class WebResourceDependenciesUrisExpandable(PermissiveModel):
    css: list[str] | str | None = None
    js: list[str] | str | None = None

class WebResourceDependenciesUris(PermissiveModel):
    all_: list[str] | str | None = Field(None, validation_alias="all", serialization_alias="all")
    css: list[str] | str | None = None
    js: list[str] | str | None = None
    expandable: WebResourceDependenciesUrisExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")

class WebResourceDependencies(PermissiveModel):
    expandable: WebResourceDependenciesExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")
    keys: list[str] | None = None
    contexts: list[str] | None = None
    uris: WebResourceDependenciesUris | None = None
    tags: WebResourceDependenciesTags | None = None
    superbatch: SuperBatchWebResources | None = None

class ContentBody(PermissiveModel):
    value: str
    representation: Literal["view", "export_view", "styled_view", "storage", "editor", "editor2", "anonymous_export_view", "wiki", "atlas_doc_format", "raw"]
    embedded_content: list[EmbeddedContent] | None = Field(None, validation_alias="embeddedContent", serialization_alias="embeddedContent")
    webresource: WebResourceDependencies | None = None
    media_token: ContentBodyMediaToken | None = Field(None, validation_alias="mediaToken", serialization_alias="mediaToken")
    expandable: ContentBodyExpandable1 | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class AddRestrictionsBodyV0(PermissiveModel):
    results: list[ContentRestrictionUpdate]
    start: int | None = Field(None, json_schema_extra={'format': 'int32'})
    limit: int | None = Field(None, json_schema_extra={'format': 'int32'})
    size: int | None = Field(None, json_schema_extra={'format': 'int32'})
    restrictions_hash: str | None = Field(None, validation_alias="restrictionsHash", serialization_alias="restrictionsHash", description="This property is used by the UI to figure out whether a set of restrictions\nhas changed.")
    links: dict[str, dict[str, Any] | str] | None = Field(None, validation_alias="_links", serialization_alias="_links")

class Content(PermissiveModel):
    """Base object for all content types."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id")
    type_: str = Field(..., validation_alias="type", serialization_alias="type", description="Can be \"page\", \"blogpost\", \"attachment\" or \"content\"")
    status: str
    title: str | None = None
    space: Space | None = None
    history: ContentHistory | None = None
    version: Version | None = None
    ancestors: list[Content] | None = None
    operations: list[OperationCheckResult] | None = None
    children: ContentChildren | None = None
    child_types: ContentChildType | None = Field(None, validation_alias="childTypes", serialization_alias="childTypes")
    descendants: ContentChildren | None = None
    container: Container | None = None
    body: ContentBody | None = None
    restrictions: ContentRestrictions | None = None
    metadata: ContentMetadata | None = None
    macro_rendered_output: dict[str, dict[str, Any]] | None = Field(None, validation_alias="macroRenderedOutput", serialization_alias="macroRenderedOutput")
    extensions: dict[str, Any] | None = None
    expandable: ContentExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class ContentArray(PermissiveModel):
    results: list[Content]
    start: int | None = Field(None, json_schema_extra={'format': 'int32'})
    limit: int | None = Field(None, json_schema_extra={'format': 'int32'})
    size: int = Field(..., json_schema_extra={'format': 'int32'})
    links: GenericLinks = Field(..., validation_alias="_links", serialization_alias="_links")

class ContentChildren(PermissiveModel):
    attachment: ContentArray | None = None
    comment: ContentArray | None = None
    page: ContentArray | None = None
    whiteboard: ContentArray | None = None
    database: ContentArray | None = None
    embed: ContentArray | None = None
    folder: ContentArray | None = None
    expandable: ContentChildrenExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class ContentHistory(PermissiveModel):
    latest: bool
    created_by: User | None = Field(None, validation_alias="createdBy", serialization_alias="createdBy")
    owned_by: User | None = Field(None, validation_alias="ownedBy", serialization_alias="ownedBy")
    last_owned_by: User | None = Field(None, validation_alias="lastOwnedBy", serialization_alias="lastOwnedBy")
    created_date: str | None = Field(None, validation_alias="createdDate", serialization_alias="createdDate", json_schema_extra={'format': 'date-time'})
    last_updated: Version | None = Field(None, validation_alias="lastUpdated", serialization_alias="lastUpdated")
    previous_version: Version | None = Field(None, validation_alias="previousVersion", serialization_alias="previousVersion")
    contributors: ContentHistoryContributors | None = None
    next_version: Version | None = Field(None, validation_alias="nextVersion", serialization_alias="nextVersion")
    expandable: ContentHistoryExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class ContentHistoryContributors(PermissiveModel):
    publishers: UsersUserKeys | None = None

class ContentMetadata(PermissiveModel):
    """Metadata object for page, blogpost, comment content"""
    currentuser: ContentMetadataCurrentuser | None = None
    properties: GenericLinks | None = None
    frontend: dict[str, Any] | None = None
    labels: LabelArray | list[Label] | None = None

class ContentMetadataCurrentuser(PermissiveModel):
    favourited: ContentMetadataCurrentuserFavourited | None = None
    lastmodified: ContentMetadataCurrentuserLastmodified | None = None
    lastcontributed: ContentMetadataCurrentuserLastcontributed | None = None
    viewed: ContentMetadataCurrentuserViewed | None = None
    scheduled: dict[str, Any] | None = None
    expandable: ContentMetadataCurrentuserExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")

class ContentMetadataCurrentuserLastmodified(PermissiveModel):
    version: Version | None = None
    friendly_last_modified: str | None = Field(None, validation_alias="friendlyLastModified", serialization_alias="friendlyLastModified")

class ContentRestriction(PermissiveModel):
    operation: Literal["administer", "copy", "create", "delete", "export", "move", "purge", "purge_version", "read", "restore", "update", "use"]
    restrictions: ContentRestrictionRestrictions | None = None
    content: Content | None = None
    expandable: ContentRestrictionExpandable = Field(..., validation_alias="_expandable", serialization_alias="_expandable")
    links: GenericLinks = Field(..., validation_alias="_links", serialization_alias="_links")

class ContentRestrictionRestrictions(PermissiveModel):
    user: UserArray | None = None
    group: GroupArray | None = None
    expandable: ContentRestrictionRestrictionsExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")

class ContentRestrictionUpdate(PermissiveModel):
    operation: Literal["administer", "copy", "create", "delete", "export", "move", "purge", "purge_version", "read", "restore", "update", "use"] = Field(..., description="The restriction operation applied to content.")
    restrictions: ContentRestrictionUpdateRestrictions = Field(..., description="The users/groups that the restrictions will be applied to. At least one of\n`user` or `group` must be specified for this object.")
    content: Content | None = None

class ContentRestrictionUpdateRestrictions(PermissiveModel):
    """The users/groups that the restrictions will be applied to. At least one of
`user` or `group` must be specified for this object."""
    group: list[ContentRestrictionUpdateRestrictionsGroupItem] | None = Field(None, description="The groups that the restrictions will be applied to. This array must\nhave at least one item, otherwise it should be omitted.")
    user: list[User] | UserArray | None = None

class ContentRestrictions(PermissiveModel):
    read: ContentRestriction | None = None
    update: ContentRestriction | None = None
    expandable: ContentRestrictionsExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class Space(PermissiveModel):
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    key: str
    alias: str | None = None
    name: str
    icon: Icon | None = None
    description: SpaceDescription | None = None
    homepage: Content | None = None
    type_: str = Field(..., validation_alias="type", serialization_alias="type")
    metadata: SpaceMetadata | None = None
    operations: list[OperationCheckResult] | None = None
    permissions: list[SpacePermission] | None = None
    status: str
    settings: SpaceSettings | None = None
    theme: Theme | None = None
    look_and_feel: LookAndFeel | None = Field(None, validation_alias="lookAndFeel", serialization_alias="lookAndFeel")
    history: SpaceHistory | None = None
    expandable: SpaceExpandable = Field(..., validation_alias="_expandable", serialization_alias="_expandable")
    links: GenericLinks = Field(..., validation_alias="_links", serialization_alias="_links")

class SpaceHistory(PermissiveModel):
    created_date: str = Field(..., validation_alias="createdDate", serialization_alias="createdDate", json_schema_extra={'format': 'date-time'})
    created_by: User | None = Field(None, validation_alias="createdBy", serialization_alias="createdBy")

class SpacePermission(PermissiveModel):
    """This object represents a permission for given space. Permissions consist of
at least one operation object with an accompanying subjects object.

The following combinations of `operation` and `targetType` values are
valid for the `operation` object:

  - 'create': 'page', 'blogpost', 'comment', 'attachment'
  - 'read': 'space'
  - 'delete': 'page', 'blogpost', 'comment', 'attachment'
  - 'export': 'space'
  - 'administer': 'space'"""
    id_: int | None = Field(None, validation_alias="id", serialization_alias="id", json_schema_extra={'format': 'int64'})
    subjects: SpacePermissionSubjects | None = Field(None, description="The users and/or groups that the permission applies to.")
    operation: OperationCheckResult
    anonymous_access: bool = Field(..., validation_alias="anonymousAccess", serialization_alias="anonymousAccess", description="Grant anonymous users permission to use the operation.")
    unlicensed_access: bool = Field(..., validation_alias="unlicensedAccess", serialization_alias="unlicensedAccess", description="Grants access to unlicensed users from JIRA Service Desk when used\nwith the 'read space' operation.")

class SpacePermissionCreate(PermissiveModel):
    """This object represents a permission for given space. Permissions consist of
at least one operation object with an accompanying subjects object.

The following combinations of `operation` and `targetType` values are
valid for the `operation` object:

  - 'create': 'page', 'blogpost', 'comment', 'attachment'
  - 'read': 'space'
  - 'delete': 'page', 'blogpost', 'comment', 'attachment'
  - 'export': 'space'
  - 'administer': 'space'"""
    subjects: SpacePermissionCreateSubjects | None = Field(None, description="The users and/or groups that the permission applies to.")
    operation: OperationCheckResult
    anonymous_access: bool = Field(..., validation_alias="anonymousAccess", serialization_alias="anonymousAccess", description="Grant anonymous users permission to use the operation.")
    unlicensed_access: bool = Field(..., validation_alias="unlicensedAccess", serialization_alias="unlicensedAccess", description="Grants access to unlicensed users from JIRA Service Desk when used\nwith the 'read space' operation.")

class SpacePermissionCreateSubjects(PermissiveModel):
    """The users and/or groups that the permission applies to."""
    user: SpacePermissionCreateSubjectsUser | None = None
    group: SpacePermissionCreateSubjectsGroup | None = None

class SpacePermissionCreateSubjectsUser(PermissiveModel):
    results: list[User]
    size: int = Field(..., json_schema_extra={'format': 'int32'})

class SpacePermissionSubjects(PermissiveModel):
    """The users and/or groups that the permission applies to."""
    user: SpacePermissionSubjectsUser | None = None
    group: SpacePermissionSubjectsGroup | None = None
    expandable: SpacePermissionSubjectsExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")

class SpacePermissionSubjectsUser(PermissiveModel):
    results: list[User]
    size: int = Field(..., json_schema_extra={'format': 'int32'})
    start: int | None = Field(None, json_schema_extra={'format': 'int32'})
    limit: int | None = Field(None, json_schema_extra={'format': 'int32'})

class UpdateRestrictionsBodyV0(PermissiveModel):
    results: list[ContentRestrictionUpdate]
    start: int | None = Field(None, json_schema_extra={'format': 'int32'})
    limit: int | None = Field(None, json_schema_extra={'format': 'int32'})
    size: int | None = Field(None, json_schema_extra={'format': 'int32'})
    restrictions_hash: str | None = Field(None, validation_alias="restrictionsHash", serialization_alias="restrictionsHash", description="This property is used by the UI to figure out whether a set of restrictions\nhas changed.")
    links: dict[str, dict[str, Any] | str] | None = Field(None, validation_alias="_links", serialization_alias="_links")

class User(PermissiveModel):
    type_: Literal["known", "unknown", "anonymous", "user"] = Field(..., validation_alias="type", serialization_alias="type")
    username: str | None = None
    user_key: str | None = Field(None, validation_alias="userKey", serialization_alias="userKey")
    account_id: str | None = Field(None, validation_alias="accountId", serialization_alias="accountId")
    account_type: Literal["atlassian", "app", ""] | None = Field(None, validation_alias="accountType", serialization_alias="accountType", description="The account type of the user, may return empty string if unavailable. App is if the user is a bot user created on behalf of an Atlassian app.")
    email: str | None = Field(None, description="The email address of the user. Depending on the user's privacy setting, this may return an empty string.")
    public_name: str | None = Field(None, validation_alias="publicName", serialization_alias="publicName", description="The public name or nickname of the user. Will always contain a value.")
    profile_picture: Icon | None = Field(None, validation_alias="profilePicture", serialization_alias="profilePicture")
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName", description="The displays name of the user. Depending on the user's privacy setting, this may be the same as publicName.")
    time_zone: str | None = Field(None, validation_alias="timeZone", serialization_alias="timeZone", description="This displays user time zone. Depending on the user's privacy setting, this may return null.")
    external_collaborator: bool | None = Field(None, validation_alias="externalCollaborator", serialization_alias="externalCollaborator", description="This is deprecated. Use `isGuest` instead to find out whether the user is a guest user.")
    is_external_collaborator: bool | None = Field(None, validation_alias="isExternalCollaborator", serialization_alias="isExternalCollaborator", description="This is deprecated. Use `isGuest` instead to find out whether the user is a guest user.")
    is_guest: bool | None = Field(None, validation_alias="isGuest", serialization_alias="isGuest", description="Whether the user is a guest user")
    operations: list[OperationCheckResult] | None = None
    details: UserDetails | None = None
    personal_space: Space | None = Field(None, validation_alias="personalSpace", serialization_alias="personalSpace")
    expandable: UserExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class UserArray(PermissiveModel):
    results: list[User]
    start: int | None = Field(None, json_schema_extra={'format': 'int32'})
    limit: int | None = Field(None, json_schema_extra={'format': 'int32'})
    size: int | None = Field(None, json_schema_extra={'format': 'int32'})
    total_size: int | None = Field(0, validation_alias="totalSize", serialization_alias="totalSize", description="This property will return total count of the objects before pagination is applied.\nThis value is returned if `shouldReturnTotalSize` is set to `true`.", json_schema_extra={'format': 'int64'})
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class UsersUserKeys(PermissiveModel):
    users: list[User] | None = None
    user_keys: list[str] | None = Field(None, validation_alias="userKeys", serialization_alias="userKeys")
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")

class Version(PermissiveModel):
    by: User | None = None
    when: str | None = Field(..., json_schema_extra={'format': 'date-time'})
    friendly_when: str | None = Field(None, validation_alias="friendlyWhen", serialization_alias="friendlyWhen")
    message: str | None = None
    number: int = Field(..., description="Set this to the current version number incremented by one", json_schema_extra={'format': 'int32'})
    minor_edit: bool = Field(..., validation_alias="minorEdit", serialization_alias="minorEdit", description="If `minorEdit` is set to 'true', no notification email or activity\nstream will be generated for the change.")
    content: Content | None = None
    collaborators: UsersUserKeys | None = None
    expandable: VersionExpandable | None = Field(None, validation_alias="_expandable", serialization_alias="_expandable")
    links: GenericLinks | None = Field(None, validation_alias="_links", serialization_alias="_links")
    content_type_modified: bool | None = Field(None, validation_alias="contentTypeModified", serialization_alias="contentTypeModified", description="True if content type is modifed in this version (e.g. page to blog)")
    conf_rev: str | None = Field(None, validation_alias="confRev", serialization_alias="confRev", description="The revision id provided by confluence to be used as a revision in Synchrony")
    sync_rev: str | None = Field(None, validation_alias="syncRev", serialization_alias="syncRev", description="The revision id provided by Synchrony")
    sync_rev_source: str | None = Field(None, validation_alias="syncRevSource", serialization_alias="syncRevSource", description="Source of the synchrony revision")


# Rebuild models to resolve forward references (required for circular refs)
AccountId.model_rebuild()
AddCustomContentPermissionsBodyOperationsItem.model_rebuild()
AddRestrictionsBodyV0.model_rebuild()
ArchivePagesBodyPagesItem.model_rebuild()
ButtonLookAndFeel.model_rebuild()
Container.model_rebuild()
ContainerLookAndFeel.model_rebuild()
Content.model_rebuild()
ContentArray.model_rebuild()
ContentBody.model_rebuild()
ContentBodyConversionInput.model_rebuild()
ContentBodyCreate.model_rebuild()
ContentBodyExpandable.model_rebuild()
ContentBodyExpandable1.model_rebuild()
ContentBodyMediaToken.model_rebuild()
ContentChildren.model_rebuild()
ContentChildrenExpandable.model_rebuild()
ContentChildType.model_rebuild()
ContentChildTypeAttachment.model_rebuild()
ContentChildTypeComment.model_rebuild()
ContentChildTypeExpandable.model_rebuild()
ContentChildTypePage.model_rebuild()
ContentExpandable.model_rebuild()
ContentHistory.model_rebuild()
ContentHistoryContributors.model_rebuild()
ContentHistoryExpandable.model_rebuild()
ContentLookAndFeel.model_rebuild()
ContentMetadata.model_rebuild()
ContentMetadataCurrentuser.model_rebuild()
ContentMetadataCurrentuserExpandable.model_rebuild()
ContentMetadataCurrentuserFavourited.model_rebuild()
ContentMetadataCurrentuserLastcontributed.model_rebuild()
ContentMetadataCurrentuserLastmodified.model_rebuild()
ContentMetadataCurrentuserViewed.model_rebuild()
ContentRestriction.model_rebuild()
ContentRestrictionExpandable.model_rebuild()
ContentRestrictionRestrictions.model_rebuild()
ContentRestrictionRestrictionsExpandable.model_rebuild()
ContentRestrictions.model_rebuild()
ContentRestrictionsExpandable.model_rebuild()
ContentRestrictionUpdate.model_rebuild()
ContentRestrictionUpdateRestrictions.model_rebuild()
ContentRestrictionUpdateRestrictionsGroupItem.model_rebuild()
CopyPageHierarchyTitleOptions.model_rebuild()
CopyPageRequestDestination.model_rebuild()
Embeddable.model_rebuild()
EmbeddedContent.model_rebuild()
GenericLinks.model_rebuild()
Group.model_rebuild()
GroupArray.model_rebuild()
GroupCreate.model_rebuild()
HeaderLookAndFeel.model_rebuild()
HorizontalHeaderLookAndFeel.model_rebuild()
Icon.model_rebuild()
Label.model_rebuild()
LabelArray.model_rebuild()
LabelCreate.model_rebuild()
LabelCreateArray.model_rebuild()
LookAndFeel.model_rebuild()
LookAndFeelBordersAndDividers.model_rebuild()
LookAndFeelHeadings.model_rebuild()
LookAndFeelLinks.model_rebuild()
MenusLookAndFeel.model_rebuild()
MenusLookAndFeelHoverOrFocus.model_rebuild()
NavigationLookAndFeel.model_rebuild()
NavigationLookAndFeelHoverOrFocus.model_rebuild()
OperationCheckResult.model_rebuild()
ScreenLookAndFeel.model_rebuild()
ScreenLookAndFeelLayer.model_rebuild()
SearchFieldLookAndFeel.model_rebuild()
Space.model_rebuild()
SpaceDescription.model_rebuild()
SpaceDescriptionExpandable.model_rebuild()
SpaceExpandable.model_rebuild()
SpaceHistory.model_rebuild()
SpaceMetadata.model_rebuild()
SpacePermission.model_rebuild()
SpacePermissionCreate.model_rebuild()
SpacePermissionCreateSubjects.model_rebuild()
SpacePermissionCreateSubjectsGroup.model_rebuild()
SpacePermissionCreateSubjectsUser.model_rebuild()
SpacePermissionSubjects.model_rebuild()
SpacePermissionSubjectsExpandable.model_rebuild()
SpacePermissionSubjectsGroup.model_rebuild()
SpacePermissionSubjectsUser.model_rebuild()
SpaceSettings.model_rebuild()
SpaceSettingsEditor.model_rebuild()
SuperBatchWebResources.model_rebuild()
SuperBatchWebResourcesTags.model_rebuild()
SuperBatchWebResourcesUris.model_rebuild()
Theme.model_rebuild()
TopNavigationLookAndFeel.model_rebuild()
TopNavigationLookAndFeelHoverOrFocus.model_rebuild()
UpdateRestrictionsBodyV0.model_rebuild()
User.model_rebuild()
UserArray.model_rebuild()
UserDetails.model_rebuild()
UserDetailsBusiness.model_rebuild()
UserDetailsPersonal.model_rebuild()
UserExpandable.model_rebuild()
UsersUserKeys.model_rebuild()
Version.model_rebuild()
VersionExpandable.model_rebuild()
WebResourceDependencies.model_rebuild()
WebResourceDependenciesExpandable.model_rebuild()
WebResourceDependenciesTags.model_rebuild()
WebResourceDependenciesUris.model_rebuild()
WebResourceDependenciesUrisExpandable.model_rebuild()

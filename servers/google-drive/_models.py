"""
Google Drive MCP Server - Pydantic Models

Generated: 2026-04-14 18:23:24 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Literal

from _validators import PermissiveModel, StrictModel
from pydantic import Field

__all__ = [
    "AboutGetRequest",
    "AccessproposalsGetRequest",
    "AccessproposalsListRequest",
    "AccessproposalsResolveRequest",
    "ApprovalsGetRequest",
    "ApprovalsListRequest",
    "ChangesListRequest",
    "CommentsCreateRequest",
    "CommentsDeleteRequest",
    "CommentsGetRequest",
    "CommentsListRequest",
    "CommentsUpdateRequest",
    "DrivesCreateRequest",
    "DrivesDeleteRequest",
    "DrivesGetRequest",
    "DrivesHideRequest",
    "DrivesListRequest",
    "DrivesUnhideRequest",
    "DrivesUpdateRequest",
    "FilesCopyRequest",
    "FilesCreateRequest",
    "FilesDeleteRequest",
    "FilesDownloadRequest",
    "FilesExportRequest",
    "FilesGenerateIdsRequest",
    "FilesGetRequest",
    "FilesListLabelsRequest",
    "FilesListRequest",
    "FilesModifyLabelsRequest",
    "FilesUpdateRequest",
    "PermissionsCreateRequest",
    "PermissionsDeleteRequest",
    "PermissionsGetRequest",
    "PermissionsListRequest",
    "PermissionsUpdateRequest",
    "RepliesCreateRequest",
    "RepliesDeleteRequest",
    "RepliesGetRequest",
    "RepliesListRequest",
    "RepliesUpdateRequest",
    "RevisionsDeleteRequest",
    "RevisionsGetRequest",
    "RevisionsListRequest",
    "RevisionsUpdateRequest",
    "ContentRestriction",
    "LabelModification",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_user_info
class AboutGetRequestQuery(StrictModel):
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class AboutGetRequest(StrictModel):
    """Retrieves information about the authenticated user, their Drive, and system capabilities. Use the `fields` parameter to specify which user properties and Drive details to return."""
    query: AboutGetRequestQuery | None = None

# Operation: get_access_proposal
class AccessproposalsGetRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file or item associated with the access proposal.")
    proposal_id: str = Field(default=..., validation_alias="proposalId", serialization_alias="proposalId", description="The unique identifier of the access proposal to retrieve.")
class AccessproposalsGetRequest(StrictModel):
    """Retrieves a specific access proposal for a file by its ID. Use this to check the status and details of pending access requests."""
    path: AccessproposalsGetRequestPath

# Operation: list_access_proposals
class AccessproposalsListRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file for which to list access proposals.")
class AccessproposalsListRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="The maximum number of access proposals to return per page. Defaults to a server-defined limit if not specified.")
    page_token: str | None = Field(default=None, validation_alias="pageToken", serialization_alias="pageToken", description="A continuation token from a previous paginated response to retrieve the next set of results.")
class AccessproposalsListRequest(StrictModel):
    """Retrieve pending access proposals for a file. Only users with approver permissions can list access proposals; other users will receive a 403 error."""
    path: AccessproposalsListRequestPath
    query: AccessproposalsListRequestQuery | None = None

# Operation: resolve_access_proposal
class AccessproposalsResolveRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The ID of the file associated with the access proposal.")
    proposal_id: str = Field(default=..., validation_alias="proposalId", serialization_alias="proposalId", description="The ID of the access proposal to resolve.")
class AccessproposalsResolveRequestBody(StrictModel):
    action: Literal["ACTION_UNSPECIFIED", "ACCEPT", "DENY"] | None = Field(default=None, description="The action to take on the access proposal: accept to grant access, deny to reject it, or unspecified for no action.")
    role: list[str] | None = Field(default=None, description="The roles to grant the requester when accepting the proposal. Required when action is ACCEPT. Specify as an array of role identifiers.")
    send_notification: bool | None = Field(default=None, validation_alias="sendNotification", serialization_alias="sendNotification", description="Whether to send an email notification to the requester when the proposal is accepted or denied.")
    view: str | None = Field(default=None, description="The view context for this proposal, if it belongs to a view. Only the published view is supported.")
class AccessproposalsResolveRequest(StrictModel):
    """Approves or denies a pending access proposal for a file. The approver can specify allowed roles when accepting and optionally notify the requester of the decision."""
    path: AccessproposalsResolveRequestPath
    body: AccessproposalsResolveRequestBody | None = None

# Operation: get_approval
class ApprovalsGetRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the approval.")
    approval_id: str = Field(default=..., validation_alias="approvalId", serialization_alias="approvalId", description="The unique identifier of the approval to retrieve.")
class ApprovalsGetRequest(StrictModel):
    """Retrieves a specific approval by its ID from a file. Use this to fetch details about an approval request or decision."""
    path: ApprovalsGetRequestPath

# Operation: list_approvals
class ApprovalsListRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file for which to retrieve approvals.")
class ApprovalsListRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="The maximum number of approvals to return per page. Defaults to 100 if not specified.")
    page_token: str | None = Field(default=None, validation_alias="pageToken", serialization_alias="pageToken", description="A pagination token from a previous response's nextPageToken field to retrieve the next page of results.")
class ApprovalsListRequest(StrictModel):
    """Retrieves a paginated list of approvals associated with a specific file. Use pagination parameters to control result size and navigate through multiple pages."""
    path: ApprovalsListRequestPath
    query: ApprovalsListRequestQuery | None = None

# Operation: list_changes
class ChangesListRequestQuery(StrictModel):
    page_token: str = Field(default=..., validation_alias="pageToken", serialization_alias="pageToken", description="Pagination token from the previous response's nextPageToken field or from getStartPageToken to continue listing changes on the next page.")
    include_corpus_removals: bool | None = Field(default=None, validation_alias="includeCorpusRemovals", serialization_alias="includeCorpusRemovals", description="Include the file resource in results even when removed from the changes list, provided the file remains accessible to the user at request time.")
    include_items_from_all_drives: bool | None = Field(default=None, validation_alias="includeItemsFromAllDrives", serialization_alias="includeItemsFromAllDrives", description="Include changes from both My Drive and shared drives in the results.")
    include_labels: str | None = Field(default=None, validation_alias="includeLabels", serialization_alias="includeLabels", description="Comma-separated list of label IDs to include detailed label information in the response.")
    include_permissions_for_view: str | None = Field(default=None, validation_alias="includePermissionsForView", serialization_alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response.")
    include_removed: bool | None = Field(default=None, validation_alias="includeRemoved", serialization_alias="includeRemoved", description="Include change entries indicating items have been removed, such as through deletion or loss of access.")
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Maximum number of changes to return per page.", ge=1, le=1000)
    restrict_to_my_drive: bool | None = Field(default=None, validation_alias="restrictToMyDrive", serialization_alias="restrictToMyDrive", description="Restrict results to changes within the My Drive hierarchy, excluding changes to application data or shared files not added to My Drive.")
class ChangesListRequest(StrictModel):
    """Retrieves a list of changes for a user's My Drive or shared drive, enabling tracking of file modifications, deletions, and access changes. Use page tokens to iterate through results."""
    query: ChangesListRequestQuery

# Operation: list_comments
class CommentsListRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file whose comments should be retrieved.")
class CommentsListRequestQuery(StrictModel):
    include_deleted: bool | None = Field(default=None, validation_alias="includeDeleted", serialization_alias="includeDeleted", description="Whether to include deleted comments in the results. Deleted comments will not contain their original content.")
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="The maximum number of comments to return in a single page of results.", ge=1, le=100)
    page_token: str | None = Field(default=None, validation_alias="pageToken", serialization_alias="pageToken", description="A pagination token from a previous response's `nextPageToken` field to retrieve the next page of results.")
    start_modified_time: str | None = Field(default=None, validation_alias="startModifiedTime", serialization_alias="startModifiedTime", description="Filter results to only include comments modified on or after this timestamp, specified in RFC 3339 date-time format.")
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class CommentsListRequest(StrictModel):
    """Retrieves all comments on a file, with options to filter by modification time and include deleted comments. The `fields` parameter must be specified to define which comment fields to return."""
    path: CommentsListRequestPath
    query: CommentsListRequestQuery | None = None

# Operation: create_comment
class CommentsCreateRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file on which to create the comment.")
class CommentsCreateRequestQuery(StrictModel):
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class CommentsCreateRequestBody(StrictModel):
    content: str | None = Field(default=None, description="The plain text content of the comment. HTML content will be generated from this plain text for display purposes.")
    anchor: str | None = Field(default=None, description="A region of the document represented as a JSON string. For details on defining anchor properties, refer to [Manage comments and replies](https://developers.google.com/workspace/drive/api/v3/manage-comments).")
class CommentsCreateRequest(StrictModel):
    """Creates a comment on a file in Google Drive. The `fields` parameter must be set to specify which fields to return in the response."""
    path: CommentsCreateRequestPath
    query: CommentsCreateRequestQuery | None = None
    body: CommentsCreateRequestBody | None = None

# Operation: get_comment
class CommentsGetRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the comment.")
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="The unique identifier of the comment to retrieve.")
class CommentsGetRequestQuery(StrictModel):
    include_deleted: bool | None = Field(default=None, validation_alias="includeDeleted", serialization_alias="includeDeleted", description="Whether to include deleted comments in the response. Deleted comments will be returned without their original content.")
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class CommentsGetRequest(StrictModel):
    """Retrieves a specific comment from a file by its ID. Supports optional retrieval of deleted comments, which will have their original content removed."""
    path: CommentsGetRequestPath
    query: CommentsGetRequestQuery | None = None

# Operation: update_comment
class CommentsUpdateRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the comment to update.")
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="The unique identifier of the comment to update.")
class CommentsUpdateRequestQuery(StrictModel):
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class CommentsUpdateRequestBody(StrictModel):
    content: str | None = Field(default=None, description="The plain text content to set for the comment. This field updates the comment's text content.")
    anchor: str | None = Field(default=None, description="A region of the document represented as a JSON string. For details on defining anchor properties, refer to [Manage comments and replies](https://developers.google.com/workspace/drive/api/v3/manage-comments).")
class CommentsUpdateRequest(StrictModel):
    """Updates an existing comment in a file using patch semantics, allowing you to modify the comment's content. The `fields` parameter must be set to specify which fields to return in the response."""
    path: CommentsUpdateRequestPath
    query: CommentsUpdateRequestQuery | None = None
    body: CommentsUpdateRequestBody | None = None

# Operation: delete_comment
class CommentsDeleteRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the comment to delete.")
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="The unique identifier of the comment to delete.")
class CommentsDeleteRequestQuery(StrictModel):
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class CommentsDeleteRequest(StrictModel):
    """Deletes a comment from a file. The comment and all associated replies will be permanently removed."""
    path: CommentsDeleteRequestPath
    query: CommentsDeleteRequestQuery | None = None

# Operation: list_shared_drives
class DrivesListRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Maximum number of shared drives to return in a single page of results. Useful for controlling response size and implementing pagination.", ge=1, le=100)
    page_token: str | None = Field(default=None, validation_alias="pageToken", serialization_alias="pageToken", description="Token for retrieving the next page of results. Use the pageToken from the previous response to continue pagination.")
    q: str | None = Field(default=None, description="Search query to filter shared drives by name, description, or other attributes. Supports combining multiple search terms for refined results.")
    use_domain_admin_access: bool | None = Field(default=None, validation_alias="useDomainAdminAccess", serialization_alias="useDomainAdminAccess", description="When set to true, issues the request with domain administrator privileges to retrieve all shared drives within the administrator's domain, rather than only user-accessible drives.")
class DrivesListRequest(StrictModel):
    """Retrieves a list of shared drives accessible to the user, with optional filtering by search query and pagination support. Domain administrators can retrieve all shared drives within their domain by setting useDomainAdminAccess to true."""
    query: DrivesListRequestQuery | None = None

# Operation: create_shared_drive
class DrivesCreateRequestQuery(StrictModel):
    request_id: str = Field(default=..., validation_alias="requestId", serialization_alias="requestId", description="A unique identifier (such as a UUID) that ensures idempotent creation. If the same requestId is used in a repeated request, the operation will not create a duplicate shared drive; instead, it will return a 409 error if the drive already exists.")
class DrivesCreateRequestBodyRestrictions(StrictModel):
    admin_managed_restrictions: bool | None = Field(default=None, validation_alias="adminManagedRestrictions", serialization_alias="adminManagedRestrictions", description="Whether administrative privileges are required to modify restrictions on this shared drive.")
    copy_requires_writer_permission: bool | None = Field(default=None, validation_alias="copyRequiresWriterPermission", serialization_alias="copyRequiresWriterPermission", description="Whether copying, printing, and downloading files inside this shared drive should be disabled for readers and commenters. When enabled, this overrides the same restriction setting for individual files within the drive.")
    domain_users_only: bool | None = Field(default=None, validation_alias="domainUsersOnly", serialization_alias="domainUsersOnly", description="Whether access to this shared drive and its contents is restricted to users of the domain that owns the drive. Other sharing policies outside this drive may override this restriction.")
    drive_members_only: bool | None = Field(default=None, validation_alias="driveMembersOnly", serialization_alias="driveMembersOnly", description="Whether access to items inside this shared drive is restricted exclusively to its members.")
    sharing_folders_requires_organizer_permission: bool | None = Field(default=None, validation_alias="sharingFoldersRequiresOrganizerPermission", serialization_alias="sharingFoldersRequiresOrganizerPermission", description="Whether only users with the organizer role can share folders. If false, both organizer and file organizer roles can share folders.")
class DrivesCreateRequestBody(StrictModel):
    color_rgb: str | None = Field(default=None, validation_alias="colorRgb", serialization_alias="colorRgb", description="The color of the shared drive as an RGB hex string. Can only be set when themeId is not specified.")
    hidden: bool | None = Field(default=None, description="Whether the shared drive should be hidden from the default view in the user interface.")
    name: str | None = Field(default=None, description="The display name of the shared drive.")
    theme_id: str | None = Field(default=None, validation_alias="themeId", serialization_alias="themeId", description="The ID of a predefined theme that sets the background image and color for the shared drive. Available themes can be retrieved from the drive.about.get endpoint. Cannot be used together with colorRgb or backgroundImageFile.")
    restrictions: DrivesCreateRequestBodyRestrictions | None = None
class DrivesCreateRequest(StrictModel):
    """Creates a new shared drive with specified configuration and access restrictions. Use a unique requestId to ensure idempotent creation and avoid duplicates."""
    query: DrivesCreateRequestQuery
    body: DrivesCreateRequestBody | None = None

# Operation: get_shared_drive
class DrivesGetRequestPath(StrictModel):
    drive_id: str = Field(default=..., validation_alias="driveId", serialization_alias="driveId", description="The unique identifier of the shared drive to retrieve.")
class DrivesGetRequestQuery(StrictModel):
    use_domain_admin_access: bool | None = Field(default=None, validation_alias="useDomainAdminAccess", serialization_alias="useDomainAdminAccess", description="If true, issues the request with domain administrator privileges, allowing access to shared drives within your domain even if you're not a direct member.")
class DrivesGetRequest(StrictModel):
    """Retrieves metadata for a shared drive by its ID. Use domain administrator access to retrieve drives belonging to your organization's domain."""
    path: DrivesGetRequestPath
    query: DrivesGetRequestQuery | None = None

# Operation: update_shared_drive
class DrivesUpdateRequestPath(StrictModel):
    drive_id: str = Field(default=..., validation_alias="driveId", serialization_alias="driveId", description="The unique identifier of the shared drive to update.")
class DrivesUpdateRequestQuery(StrictModel):
    use_domain_admin_access: bool | None = Field(default=None, validation_alias="useDomainAdminAccess", serialization_alias="useDomainAdminAccess", description="If true, allows a domain administrator to update the shared drive even if they are not a member, provided they administer the domain to which the shared drive belongs.")
class DrivesUpdateRequestBodyBackgroundImageFile(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The ID of an image file stored in Google Drive to set as the shared drive's background image. The image must be accessible to the requester.")
class DrivesUpdateRequestBodyRestrictions(StrictModel):
    admin_managed_restrictions: bool | None = Field(default=None, validation_alias="adminManagedRestrictions", serialization_alias="adminManagedRestrictions", description="If true, only administrators of the shared drive can modify access restrictions and other administrative settings.")
    copy_requires_writer_permission: bool | None = Field(default=None, validation_alias="copyRequiresWriterPermission", serialization_alias="copyRequiresWriterPermission", description="If true, disables copy, print, and download options for readers and commenters on all files within the shared drive. This restriction overrides file-level settings.")
    domain_users_only: bool | None = Field(default=None, validation_alias="domainUsersOnly", serialization_alias="domainUsersOnly", description="If true, restricts access to the shared drive and all its contents to users belonging to the same domain as the shared drive. Other sharing policies may override this restriction.")
    drive_members_only: bool | None = Field(default=None, validation_alias="driveMembersOnly", serialization_alias="driveMembersOnly", description="If true, restricts access to items within the shared drive to its members only, preventing external sharing.")
    sharing_folders_requires_organizer_permission: bool | None = Field(default=None, validation_alias="sharingFoldersRequiresOrganizerPermission", serialization_alias="sharingFoldersRequiresOrganizerPermission", description="If true, only users with the organizer role can share folders within the shared drive. If false, both organizer and file organizer roles can share folders.")
class DrivesUpdateRequestBody(StrictModel):
    color_rgb: str | None = Field(default=None, validation_alias="colorRgb", serialization_alias="colorRgb", description="The color of the shared drive as a hexadecimal RGB value. Cannot be used together with themeId in the same request.")
    hidden: bool | None = Field(default=None, description="If true, hides the shared drive from the default view in Google Drive, though it remains accessible via direct links and search.")
    name: str | None = Field(default=None, description="The display name of the shared drive. This is the name visible to all members.")
    theme_id: str | None = Field(default=None, validation_alias="themeId", serialization_alias="themeId", description="The ID of a predefined theme to apply to the shared drive, which sets both the background image and color. Available themes can be retrieved from the drive.about.get endpoint. This is a write-only field and cannot be used together with colorRgb or backgroundImageFile in the same request.")
    background_image_file: DrivesUpdateRequestBodyBackgroundImageFile | None = Field(default=None, validation_alias="backgroundImageFile", serialization_alias="backgroundImageFile")
    restrictions: DrivesUpdateRequestBodyRestrictions | None = None
class DrivesUpdateRequest(StrictModel):
    """Updates the metadata and settings for a shared drive, including name, appearance, visibility, and access restrictions. Requires the shared drive ID and appropriate permissions to modify the specified properties."""
    path: DrivesUpdateRequestPath
    query: DrivesUpdateRequestQuery | None = None
    body: DrivesUpdateRequestBody | None = None

# Operation: delete_shared_drive
class DrivesDeleteRequestPath(StrictModel):
    drive_id: str = Field(default=..., validation_alias="driveId", serialization_alias="driveId", description="The unique identifier of the shared drive to delete.")
class DrivesDeleteRequestQuery(StrictModel):
    allow_item_deletion: bool | None = Field(default=None, validation_alias="allowItemDeletion", serialization_alias="allowItemDeletion", description="Whether to automatically delete all items contained within the shared drive. This option requires domain admin access to be enabled and is only applicable when the requester has domain administrator privileges.")
    use_domain_admin_access: bool | None = Field(default=None, validation_alias="useDomainAdminAccess", serialization_alias="useDomainAdminAccess", description="Whether to issue the request with domain administrator privileges. When enabled, the requester must be an administrator of the domain to which the shared drive belongs, granting access to perform administrative operations.")
class DrivesDeleteRequest(StrictModel):
    """Permanently deletes a shared drive for which the user is an organizer. The shared drive must not contain any untrashed items unless item deletion is explicitly enabled with domain admin access."""
    path: DrivesDeleteRequestPath
    query: DrivesDeleteRequestQuery | None = None

# Operation: hide_shared_drive
class DrivesHideRequestPath(StrictModel):
    drive_id: str = Field(default=..., validation_alias="driveId", serialization_alias="driveId", description="The unique identifier of the shared drive to hide.")
class DrivesHideRequest(StrictModel):
    """Hides a shared drive from the default view, removing it from the user's primary shared drive list. The drive remains accessible but is no longer displayed in standard navigation."""
    path: DrivesHideRequestPath

# Operation: unhide_shared_drive
class DrivesUnhideRequestPath(StrictModel):
    drive_id: str = Field(default=..., validation_alias="driveId", serialization_alias="driveId", description="The unique identifier of the shared drive to restore to the default view.")
class DrivesUnhideRequest(StrictModel):
    """Restores a shared drive to the default view, making it visible in the shared drives list. Use this operation to unhide a shared drive that was previously hidden from view."""
    path: DrivesUnhideRequestPath

# Operation: copy_file
class FilesCopyRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file to copy.")
class FilesCopyRequestQuery(StrictModel):
    ignore_default_visibility: bool | None = Field(default=None, validation_alias="ignoreDefaultVisibility", serialization_alias="ignoreDefaultVisibility", description="Whether to bypass the domain's default visibility settings for the copied file. When enabled, the file's visibility is not automatically set to domain-wide visibility, though parent folder permissions are still inherited.")
    include_labels: str | None = Field(default=None, validation_alias="includeLabels", serialization_alias="includeLabels", description="A comma-separated list of label IDs to include in the labelInfo section of the response.")
    include_permissions_for_view: str | None = Field(default=None, validation_alias="includePermissionsForView", serialization_alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response. Only the published view is currently supported.")
    keep_revision_forever: bool | None = Field(default=None, validation_alias="keepRevisionForever", serialization_alias="keepRevisionForever", description="Whether to mark the new head revision to be kept forever. Only applicable to files with binary content. A maximum of 200 revisions per file can be kept permanently; delete pinned revisions if this limit is reached.")
    ocr_language: str | None = Field(default=None, validation_alias="ocrLanguage", serialization_alias="ocrLanguage", description="A language hint for OCR processing during image import, specified as an ISO 639-1 language code.")
class FilesCopyRequestBodyContentHintsThumbnail(StrictModel):
    image: str | None = Field(default=None, validation_alias="image", serialization_alias="image", description="The thumbnail image data encoded using URL-safe Base64 format.", json_schema_extra={'format': 'byte'})
    mime_type: str | None = Field(default=None, validation_alias="mimeType", serialization_alias="mimeType", description="The MIME type of the thumbnail image.")
class FilesCopyRequestBodyContentHints(StrictModel):
    indexable_text: str | None = Field(default=None, validation_alias="indexableText", serialization_alias="indexableText", description="Text content to be indexed for improved fullText search results. Limited to 128 KB and may contain HTML elements.")
    thumbnail: FilesCopyRequestBodyContentHintsThumbnail | None = None
class FilesCopyRequestBodyDownloadRestrictionsItemDownloadRestriction(StrictModel):
    restricted_for_readers: bool | None = Field(default=None, validation_alias="restrictedForReaders", serialization_alias="restrictedForReaders", description="Whether download and copy operations are restricted for readers.")
    restricted_for_writers: bool | None = Field(default=None, validation_alias="restrictedForWriters", serialization_alias="restrictedForWriters", description="Whether download and copy operations are restricted for writers. When enabled, download is also restricted for readers.")
class FilesCopyRequestBodyDownloadRestrictions(StrictModel):
    item_download_restriction: FilesCopyRequestBodyDownloadRestrictionsItemDownloadRestriction | None = Field(default=None, validation_alias="itemDownloadRestriction", serialization_alias="itemDownloadRestriction")
class FilesCopyRequestBodyShortcutDetails(StrictModel):
    target_id: str | None = Field(default=None, validation_alias="targetId", serialization_alias="targetId", description="The ID of the file that this shortcut points to. Only applicable to shortcut creation requests.")
class FilesCopyRequestBodyVideoMediaMetadata(StrictModel):
    height: int | None = Field(default=None, validation_alias="height", serialization_alias="height", description="Output only. The height of the video in pixels.", json_schema_extra={'format': 'int32'})
    width: int | None = Field(default=None, validation_alias="width", serialization_alias="width", description="Output only. The width of the video in pixels.", json_schema_extra={'format': 'int32'})
class FilesCopyRequestBody(StrictModel):
    app_properties: dict[str, str] | None = Field(default=None, validation_alias="appProperties", serialization_alias="appProperties", description="Custom key-value pairs private to the requesting application. Entries with null values are cleared during copy operations. Requires OAuth 2 authentication to retrieve; API keys cannot access private properties.")
    mime_type: str | None = Field(default=None, validation_alias="mimeType", serialization_alias="mimeType", description="The MIME type of the file. Google Drive automatically detects an appropriate MIME type from uploaded content if not provided. The value cannot be changed unless a new revision is uploaded. Files created with Google Doc MIME types have their content imported if supported.")
    content_restrictions: list[ContentRestriction] | None = Field(default=None, validation_alias="contentRestrictions", serialization_alias="contentRestrictions", description="Restrictions applied to file content access. Only populated when content restrictions are in effect.")
    copy_requires_writer_permission: bool | None = Field(default=None, validation_alias="copyRequiresWriterPermission", serialization_alias="copyRequiresWriterPermission", description="Whether copying, printing, and downloading options are disabled for readers and commenters.")
    description: str | None = Field(default=None, description="A brief description or summary of the file's contents.")
    folder_color_rgb: str | None = Field(default=None, validation_alias="folderColorRgb", serialization_alias="folderColorRgb", description="The color for a folder or folder shortcut as an RGB hex string. Supported colors are published in the folderColorPalette field of the about resource; unsupported colors are replaced with the closest available color.")
    inherited_permissions_disabled: bool | None = Field(default=None, validation_alias="inheritedPermissionsDisabled", serialization_alias="inheritedPermissionsDisabled", description="Whether inherited permissions are disabled for this file. Inherited permissions are enabled by default.")
    name: str | None = Field(default=None, description="The display name of the file. Not necessarily unique within a folder. For immutable items like shared drive roots and system folders, the name is constant.")
    parents: list[str] | None = Field(default=None, description="The ID of the parent folder containing the copied file. A file can have only one parent folder. If not specified, the file inherits the discoverable parent of the source file or is placed in the user's My Drive.")
    properties: dict[str, str] | None = Field(default=None, description="Custom key-value pairs visible to all applications. Entries with null values are cleared during copy operations.")
    starred: bool | None = Field(default=None, description="Whether the file is marked as starred by the user.")
    trashed: bool | None = Field(default=None, description="Whether the file is in the trash, either directly or through a trashed parent folder. Only the file owner can trash files; other users cannot view files in the owner's trash.")
    writers_can_share: bool | None = Field(default=None, validation_alias="writersCanShare", serialization_alias="writersCanShare", description="Whether users with writer-only permission can modify the file's sharing permissions. Not applicable to files in shared drives.")
    content_hints: FilesCopyRequestBodyContentHints | None = Field(default=None, validation_alias="contentHints", serialization_alias="contentHints")
    download_restrictions: FilesCopyRequestBodyDownloadRestrictions | None = Field(default=None, validation_alias="downloadRestrictions", serialization_alias="downloadRestrictions")
    shortcut_details: FilesCopyRequestBodyShortcutDetails | None = Field(default=None, validation_alias="shortcutDetails", serialization_alias="shortcutDetails")
    video_media_metadata: FilesCopyRequestBodyVideoMediaMetadata | None = Field(default=None, validation_alias="videoMediaMetadata", serialization_alias="videoMediaMetadata")
class FilesCopyRequest(StrictModel):
    """Creates a copy of a file with optional updates applied using patch semantics. The copied file inherits permissions from its parent folder unless otherwise specified."""
    path: FilesCopyRequestPath
    query: FilesCopyRequestQuery | None = None
    body: FilesCopyRequestBody | None = None

# Operation: list_files
class FilesListRequestQuery(StrictModel):
    include_items_from_all_drives: bool | None = Field(default=None, validation_alias="includeItemsFromAllDrives", serialization_alias="includeItemsFromAllDrives", description="Whether to include items from both My Drive and shared drives in the results.")
    include_labels: str | None = Field(default=None, validation_alias="includeLabels", serialization_alias="includeLabels", description="A comma-separated list of label IDs to include detailed label information in the response.")
    include_permissions_for_view: str | None = Field(default=None, validation_alias="includePermissionsForView", serialization_alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response.")
    order_by: str | None = Field(default=None, validation_alias="orderBy", serialization_alias="orderBy", description="A comma-separated list of sort keys to order results. Each key sorts ascending by default; append 'desc' to reverse order. Valid keys include createdTime, folder, modifiedByMeTime, modifiedTime, name, name_natural, quotaBytesUsed, recency, sharedWithMeTime, starred, and viewedByMeTime.")
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="The maximum number of files to return per page. Partial or empty result pages may be returned before reaching the end of the file list.", ge=1, le=1000)
    page_token: str | None = Field(default=None, validation_alias="pageToken", serialization_alias="pageToken", description="The pagination token from a previous response's nextPageToken field to retrieve the next page of results.")
    q: str | None = Field(default=None, description="A search query to filter file results using supported search syntax for files and folders.")
class FilesListRequest(StrictModel):
    """Retrieves a list of the user's files with support for searching, filtering, and sorting. By default, all files including trashed items are returned; use the trashed parameter to exclude deleted files."""
    query: FilesListRequestQuery | None = None

# Operation: create_file
class FilesCreateRequestQuery(StrictModel):
    ignore_default_visibility: bool | None = Field(default=None, validation_alias="ignoreDefaultVisibility", serialization_alias="ignoreDefaultVisibility", description="Bypass the domain's default visibility settings for this file. When enabled, the file's visibility is not automatically set to domain-wide; permissions are still inherited from parent folders.")
    include_labels: str | None = Field(default=None, validation_alias="includeLabels", serialization_alias="includeLabels", description="Comma-separated list of label IDs to include in the response's labelInfo section.")
    include_permissions_for_view: str | None = Field(default=None, validation_alias="includePermissionsForView", serialization_alias="includePermissionsForView", description="Include additional view permissions in the response. Currently only 'published' is supported.")
    keep_revision_forever: bool | None = Field(default=None, validation_alias="keepRevisionForever", serialization_alias="keepRevisionForever", description="Preserve the current file revision indefinitely. Only applicable to files with binary content; limited to 200 pinned revisions per file.")
    ocr_language: str | None = Field(default=None, validation_alias="ocrLanguage", serialization_alias="ocrLanguage", description="Language hint for optical character recognition during image import, specified as an ISO 639-1 language code.")
    use_content_as_indexable_text: bool | None = Field(default=None, validation_alias="useContentAsIndexableText", serialization_alias="useContentAsIndexableText", description="Use the uploaded file content as searchable indexable text to improve full-text query results.")
class FilesCreateRequestBodyContentHintsThumbnail(StrictModel):
    image: str | None = Field(default=None, validation_alias="image", serialization_alias="image", description="Thumbnail image data encoded as URL-safe Base64.", json_schema_extra={'format': 'byte'})
    mime_type: str | None = Field(default=None, validation_alias="mimeType", serialization_alias="mimeType", description="MIME type of the thumbnail image.")
class FilesCreateRequestBodyContentHints(StrictModel):
    indexable_text: str | None = Field(default=None, validation_alias="indexableText", serialization_alias="indexableText", description="Text content to index for improved full-text search results. Limited to 128 KB and may contain HTML elements.")
    thumbnail: FilesCreateRequestBodyContentHintsThumbnail | None = None
class FilesCreateRequestBodyDownloadRestrictionsItemDownloadRestriction(StrictModel):
    restricted_for_readers: bool | None = Field(default=None, validation_alias="restrictedForReaders", serialization_alias="restrictedForReaders", description="Restrict download and copy access for readers.")
    restricted_for_writers: bool | None = Field(default=None, validation_alias="restrictedForWriters", serialization_alias="restrictedForWriters", description="Restrict download and copy access for writers. When enabled, download is also restricted for readers.")
class FilesCreateRequestBodyDownloadRestrictions(StrictModel):
    item_download_restriction: FilesCreateRequestBodyDownloadRestrictionsItemDownloadRestriction | None = Field(default=None, validation_alias="itemDownloadRestriction", serialization_alias="itemDownloadRestriction")
class FilesCreateRequestBodyImageMediaMetadata(StrictModel):
    height: int | None = Field(default=None, validation_alias="height", serialization_alias="height", description="Height of the image in pixels.", json_schema_extra={'format': 'int32'})
    width: int | None = Field(default=None, validation_alias="width", serialization_alias="width", description="Width of the image in pixels.", json_schema_extra={'format': 'int32'})
class FilesCreateRequestBodyVideoMediaMetadata(StrictModel):
    height: int | None = Field(default=None, validation_alias="height", serialization_alias="height", description="Height of the video in pixels.", json_schema_extra={'format': 'int32'})
    width: int | None = Field(default=None, validation_alias="width", serialization_alias="width", description="Width of the video in pixels.", json_schema_extra={'format': 'int32'})
class FilesCreateRequestBodyShortcutDetails(StrictModel):
    target_id: str | None = Field(default=None, validation_alias="targetId", serialization_alias="targetId", description="ID of the file this shortcut points to. Only applicable when creating shortcuts with MIME type 'application/vnd.google-apps.shortcut'.")
class FilesCreateRequestBody(StrictModel):
    app_properties: dict[str, str] | None = Field(default=None, validation_alias="appProperties", serialization_alias="appProperties", description="Custom key-value pairs private to your application. Entries with null values are removed during updates. Requires OAuth 2 authentication to retrieve.")
    mime_type: str | None = Field(default=None, validation_alias="mimeType", serialization_alias="mimeType", description="MIME type of the file. Google Drive automatically detects an appropriate type from uploaded content if not specified. Cannot be changed unless a new revision is uploaded. Google Docs MIME types trigger content import if supported.")
    content_restrictions: list[ContentRestriction] | None = Field(default=None, validation_alias="contentRestrictions", serialization_alias="contentRestrictions", description="Content access restrictions applied to the file. Only populated if restrictions exist.")
    copy_requires_writer_permission: bool | None = Field(default=None, validation_alias="copyRequiresWriterPermission", serialization_alias="copyRequiresWriterPermission", description="Disable copy, print, and download options for readers and commenters.")
    description: str | None = Field(default=None, description="Brief description or summary of the file's contents.")
    folder_color_rgb: str | None = Field(default=None, validation_alias="folderColorRgb", serialization_alias="folderColorRgb", description="RGB hex color code for folder or folder shortcut appearance. Supported colors are available in the about resource's folderColorPalette; unsupported colors default to the closest available option.")
    inherited_permissions_disabled: bool | None = Field(default=None, validation_alias="inheritedPermissionsDisabled", serialization_alias="inheritedPermissionsDisabled", description="Disable inherited permissions for this file. By default, files inherit permissions from their parent folder.")
    name: str | None = Field(default=None, description="Display name of the file. Not required to be unique within a folder. For immutable items like shared drive roots, this value is constant.")
    parents: list[str] | None = Field(default=None, description="ID of the parent folder containing the file. A file can have only one parent. If omitted during creation, the file is placed in the user's My Drive root folder.")
    properties: dict[str, str] | None = Field(default=None, description="Custom key-value pairs visible to all applications. Entries with null values are removed during updates.")
    starred: bool | None = Field(default=None, description="Mark the file as starred in the user's Drive.")
    trashed: bool | None = Field(default=None, description="Move the file to trash. Only the file owner can trash files; other users cannot see trashed files in the owner's trash.")
    writers_can_share: bool | None = Field(default=None, validation_alias="writersCanShare", serialization_alias="writersCanShare", description="Allow users with writer permission to modify the file's sharing permissions. Not applicable to files in shared drives.")
    content_hints: FilesCreateRequestBodyContentHints | None = Field(default=None, validation_alias="contentHints", serialization_alias="contentHints")
    download_restrictions: FilesCreateRequestBodyDownloadRestrictions | None = Field(default=None, validation_alias="downloadRestrictions", serialization_alias="downloadRestrictions")
    image_media_metadata: FilesCreateRequestBodyImageMediaMetadata | None = Field(default=None, validation_alias="imageMediaMetadata", serialization_alias="imageMediaMetadata")
    video_media_metadata: FilesCreateRequestBodyVideoMediaMetadata | None = Field(default=None, validation_alias="videoMediaMetadata", serialization_alias="videoMediaMetadata")
    shortcut_details: FilesCreateRequestBodyShortcutDetails | None = Field(default=None, validation_alias="shortcutDetails", serialization_alias="shortcutDetails")
class FilesCreateRequest(StrictModel):
    """Creates a new file in Google Drive with optional metadata, content restrictions, and organizational properties. Supports file uploads up to 5,120 GB with any valid MIME type, and allows creation of shortcuts to existing files."""
    query: FilesCreateRequestQuery | None = None
    body: FilesCreateRequestBody | None = None

# Operation: get_file
class FilesGetRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file to retrieve.")
class FilesGetRequestQuery(StrictModel):
    include_labels: str | None = Field(default=None, validation_alias="includeLabels", serialization_alias="includeLabels", description="Comma-separated list of label IDs to include in the labelInfo section of the response.")
    include_permissions_for_view: str | None = Field(default=None, validation_alias="includePermissionsForView", serialization_alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response.")
class FilesGetRequest(StrictModel):
    """Retrieve a file's metadata or content by ID. Use alt=media to download file contents, or use the export operation for Google Docs, Sheets, and Slides formats."""
    path: FilesGetRequestPath
    query: FilesGetRequestQuery | None = None

# Operation: update_file
class FilesUpdateRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file to update.")
class FilesUpdateRequestQuery(StrictModel):
    add_parents: str | None = Field(default=None, validation_alias="addParents", serialization_alias="addParents", description="Comma-separated list of parent folder IDs to add to the file.")
    include_labels: str | None = Field(default=None, validation_alias="includeLabels", serialization_alias="includeLabels", description="Comma-separated list of label IDs to include in the labelInfo section of the response.")
    include_permissions_for_view: str | None = Field(default=None, validation_alias="includePermissionsForView", serialization_alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response.")
    keep_revision_forever: bool | None = Field(default=None, validation_alias="keepRevisionForever", serialization_alias="keepRevisionForever", description="Whether to set the keepForever field in the new head revision for binary files. Limited to 200 revisions per file; delete pinned revisions if limit is reached.")
    ocr_language: str | None = Field(default=None, validation_alias="ocrLanguage", serialization_alias="ocrLanguage", description="Language hint for OCR processing during image import, specified as an ISO 639-1 code.")
    remove_parents: str | None = Field(default=None, validation_alias="removeParents", serialization_alias="removeParents", description="Comma-separated list of parent folder IDs to remove from the file.")
    use_content_as_indexable_text: bool | None = Field(default=None, validation_alias="useContentAsIndexableText", serialization_alias="useContentAsIndexableText", description="Whether to use the uploaded content as indexable text for fullText search queries.")
class FilesUpdateRequestBodyContentHintsThumbnail(StrictModel):
    image: str | None = Field(default=None, validation_alias="image", serialization_alias="image", description="Thumbnail data encoded with URL-safe Base64.", json_schema_extra={'format': 'byte'})
    mime_type: str | None = Field(default=None, validation_alias="mimeType", serialization_alias="mimeType", description="The MIME type of the thumbnail image.")
class FilesUpdateRequestBodyContentHints(StrictModel):
    indexable_text: str | None = Field(default=None, validation_alias="indexableText", serialization_alias="indexableText", description="Text to be indexed for improved fullText search queries. Limited to 128 KB and may contain HTML elements.")
    thumbnail: FilesUpdateRequestBodyContentHintsThumbnail | None = None
class FilesUpdateRequestBodyDownloadRestrictionsItemDownloadRestriction(StrictModel):
    restricted_for_readers: bool | None = Field(default=None, validation_alias="restrictedForReaders", serialization_alias="restrictedForReaders", description="Whether download and copy are restricted for readers.")
    restricted_for_writers: bool | None = Field(default=None, validation_alias="restrictedForWriters", serialization_alias="restrictedForWriters", description="Whether download and copy are restricted for writers. If true, download is also restricted for readers.")
class FilesUpdateRequestBodyDownloadRestrictions(StrictModel):
    item_download_restriction: FilesUpdateRequestBodyDownloadRestrictionsItemDownloadRestriction | None = Field(default=None, validation_alias="itemDownloadRestriction", serialization_alias="itemDownloadRestriction")
class FilesUpdateRequestBodyShortcutDetails(StrictModel):
    target_id: str | None = Field(default=None, validation_alias="targetId", serialization_alias="targetId", description="The ID of the file that this shortcut points to. Can only be set during file creation.")
class FilesUpdateRequestBody(StrictModel):
    app_properties: dict[str, str] | None = Field(default=None, validation_alias="appProperties", serialization_alias="appProperties", description="Arbitrary key-value pairs private to the requesting app. Entries with null values are cleared. Requires OAuth 2 authentication; API keys cannot retrieve private properties.")
    mime_type: str | None = Field(default=None, validation_alias="mimeType", serialization_alias="mimeType", description="The MIME type of the file. Google Drive auto-detects if not provided. Cannot be changed unless a new revision is uploaded. Google Doc MIME types trigger content import if supported.")
    content_restrictions: list[ContentRestriction] | None = Field(default=None, validation_alias="contentRestrictions", serialization_alias="contentRestrictions", description="Restrictions for accessing the file's content. Only populated if restrictions exist.")
    copy_requires_writer_permission: bool | None = Field(default=None, validation_alias="copyRequiresWriterPermission", serialization_alias="copyRequiresWriterPermission", description="Whether copying, printing, or downloading should be disabled for readers and commenters.")
    description: str | None = Field(default=None, description="A short description of the file's purpose or content.")
    folder_color_rgb: str | None = Field(default=None, validation_alias="folderColorRgb", serialization_alias="folderColorRgb", description="The color for a folder or folder shortcut as an RGB hex string. Uses the closest supported color if an unsupported color is specified.")
    inherited_permissions_disabled: bool | None = Field(default=None, validation_alias="inheritedPermissionsDisabled", serialization_alias="inheritedPermissionsDisabled", description="Whether inherited permissions are disabled for this file. Inherited permissions are enabled by default.")
    name: str | None = Field(default=None, description="The name of the file. Not necessarily unique within a folder. Immutable for top-level shared drive folders, My Drive root, and Application Data folder.")
    parents: list[str] | None = Field(default=None, description="The ID of the parent folder containing the file. A file can have only one parent. Use addParents and removeParents parameters to modify the parents list in update requests.")
    properties: dict[str, str] | None = Field(default=None, description="Arbitrary key-value pairs visible to all apps. Entries with null values are cleared in update requests.")
    starred: bool | None = Field(default=None, description="Whether the user has starred the file.")
    trashed: bool | None = Field(default=None, description="Whether the file has been trashed, either explicitly or from a trashed parent folder. Only the owner can trash files; other users cannot see files in the owner's trash.")
    writers_can_share: bool | None = Field(default=None, validation_alias="writersCanShare", serialization_alias="writersCanShare", description="Whether users with writer permission can modify the file's permissions. Not populated for items in shared drives.")
    content_hints: FilesUpdateRequestBodyContentHints | None = Field(default=None, validation_alias="contentHints", serialization_alias="contentHints")
    download_restrictions: FilesUpdateRequestBodyDownloadRestrictions | None = Field(default=None, validation_alias="downloadRestrictions", serialization_alias="downloadRestrictions")
    shortcut_details: FilesUpdateRequestBodyShortcutDetails | None = Field(default=None, validation_alias="shortcutDetails", serialization_alias="shortcutDetails")
class FilesUpdateRequest(StrictModel):
    """Updates a file's metadata, content, or both using patch semantics. Only populate fields you want to modify; some fields like modifiedDate are updated automatically. Supports file uploads up to 5,120 GB."""
    path: FilesUpdateRequestPath
    query: FilesUpdateRequestQuery | None = None
    body: FilesUpdateRequestBody | None = None

# Operation: delete_file
class FilesDeleteRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file to delete.")
class FilesDeleteRequest(StrictModel):
    """Permanently deletes a file owned by the user without moving it to trash. If the file is a folder, all descendants owned by the user are also deleted. For shared drives, the user must be an organizer on the parent folder."""
    path: FilesDeleteRequestPath

# Operation: download_file
class FilesDownloadRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file to download.")
class FilesDownloadRequestQuery(StrictModel):
    revision_id: str | None = Field(default=None, validation_alias="revisionId", serialization_alias="revisionId", description="The specific revision of the file to download. Only applicable for blob files, Google Docs, and Google Sheets. Returns an error if the file type does not support revision-specific downloads.")
class FilesDownloadRequest(StrictModel):
    """Downloads the content of a file from Google Drive. Operations are valid for 24 hours from the time of creation."""
    path: FilesDownloadRequestPath
    query: FilesDownloadRequestQuery | None = None

# Operation: export_document
class FilesExportRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file to export.")
class FilesExportRequestQuery(StrictModel):
    mime_type: str = Field(default=..., validation_alias="mimeType", serialization_alias="mimeType", description="The MIME type format for the exported document. Refer to the supported export formats for Google Workspace documents to determine valid MIME types for your file type.")
class FilesExportRequest(StrictModel):
    """Exports a Google Workspace document to a specified format and returns the exported content as bytes. The exported content is limited to 10 MB."""
    path: FilesExportRequestPath
    query: FilesExportRequestQuery

# Operation: generate_file_ids
class FilesGenerateIdsRequestQuery(StrictModel):
    count: int | None = Field(default=None, description="The number of file IDs to generate. Must be between 1 and 1000 IDs per request.", ge=1, le=1000)
    space: str | None = Field(default=None, description="The storage space where generated IDs can be used to create files. Defaults to 'drive' for standard Google Drive storage.")
class FilesGenerateIdsRequest(StrictModel):
    """Generates a batch of file IDs for use in subsequent file creation or copy operations. These pre-generated IDs enable efficient file management workflows in Google Drive or App Data Folder."""
    query: FilesGenerateIdsRequestQuery | None = None

# Operation: list_file_labels
class FilesListLabelsRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file whose labels you want to retrieve.")
class FilesListLabelsRequestQuery(StrictModel):
    max_results: int | None = Field(default=None, validation_alias="maxResults", serialization_alias="maxResults", description="The maximum number of labels to return in a single page of results. Defaults to 100 if not specified.", ge=1, le=100)
    page_token: str | None = Field(default=None, validation_alias="pageToken", serialization_alias="pageToken", description="A pagination token from a previous response's nextPageToken field to retrieve the next page of results.")
class FilesListLabelsRequest(StrictModel):
    """Retrieves all labels applied to a specific file. Supports pagination to handle large label sets across multiple pages."""
    path: FilesListLabelsRequestPath
    query: FilesListLabelsRequestQuery | None = None

# Operation: update_file_labels
class FilesModifyLabelsRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file whose labels should be modified.")
class FilesModifyLabelsRequestBody(StrictModel):
    label_modifications: list[LabelModification] | None = Field(default=None, validation_alias="labelModifications", serialization_alias="labelModifications", description="An ordered list of label modifications to apply to the file. Each modification specifies a label field and the values to set, add, or remove.")
class FilesModifyLabelsRequest(StrictModel):
    """Updates the labels applied to a file by adding, modifying, or removing label fields. Returns the list of labels that were successfully added or modified."""
    path: FilesModifyLabelsRequestPath
    body: FilesModifyLabelsRequestBody | None = None

# Operation: list_file_permissions
class PermissionsListRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file or shared drive whose permissions you want to retrieve.")
class PermissionsListRequestQuery(StrictModel):
    include_permissions_for_view: str | None = Field(default=None, validation_alias="includePermissionsForView", serialization_alias="includePermissionsForView", description="Specifies which additional view's permissions to include in the response. Use 'published' to include permissions for the published view of the file.")
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="The maximum number of permissions to return per page. For shared drive files, defaults to 100 if not specified; for other files, returns the entire list.", ge=1, le=100)
    page_token: str | None = Field(default=None, validation_alias="pageToken", serialization_alias="pageToken", description="The pagination token from a previous response's nextPageToken field. Use this to retrieve the next page of results.")
    use_domain_admin_access: bool | None = Field(default=None, validation_alias="useDomainAdminAccess", serialization_alias="useDomainAdminAccess", description="When set to true, issues the request with domain administrator privileges. Only applicable when the fileId refers to a shared drive and the requester is a domain administrator.")
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class PermissionsListRequest(StrictModel):
    """Retrieves all permissions for a file or shared drive, including access levels and sharing settings. Supports pagination and optional filtering for published views."""
    path: PermissionsListRequestPath
    query: PermissionsListRequestQuery | None = None

# Operation: create_file_permission
class PermissionsCreateRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The ID of the file or shared drive to which the permission applies.")
class PermissionsCreateRequestQuery(StrictModel):
    email_message: str | None = Field(default=None, validation_alias="emailMessage", serialization_alias="emailMessage", description="Custom message text to include in the sharing notification email sent to recipients.")
    move_to_new_owners_root: bool | None = Field(default=None, validation_alias="moveToNewOwnersRoot", serialization_alias="moveToNewOwnersRoot", description="When transferring ownership of a file outside a shared drive, set to true to move the file to the new owner's root folder and remove all previous parent folders. Set to false to preserve the folder hierarchy.")
    send_notification_email: bool | None = Field(default=None, validation_alias="sendNotificationEmail", serialization_alias="sendNotificationEmail", description="Whether to send a notification email to the recipient. Defaults to true for users and groups. Cannot be disabled for ownership transfers.")
    transfer_ownership: bool | None = Field(default=None, validation_alias="transferOwnership", serialization_alias="transferOwnership", description="Whether to transfer file ownership to the specified user and downgrade the current owner to a writer role. Required as an acknowledgment of the ownership change side effects.")
    use_domain_admin_access: bool | None = Field(default=None, validation_alias="useDomainAdminAccess", serialization_alias="useDomainAdminAccess", description="When set to true, issue the request as a domain administrator. Only applicable when the file ID refers to a shared drive and the requester is a domain administrator.")
class PermissionsCreateRequestBody(StrictModel):
    allow_file_discovery: bool | None = Field(default=None, validation_alias="allowFileDiscovery", serialization_alias="allowFileDiscovery", description="Whether the permission allows the file to be discovered through search results. Only applies to permissions with type domain or anyone.")
    domain: str | None = Field(default=None, description="The domain name to which this permission applies. Used when granting access to an entire domain.")
    email_address: str | None = Field(default=None, validation_alias="emailAddress", serialization_alias="emailAddress", description="The email address of the user or group receiving this permission.")
    expiration_time: str | None = Field(default=None, validation_alias="expirationTime", serialization_alias="expirationTime", description="The date and time when this permission automatically expires. Must be a future date no more than one year away. Only applicable to user and group permissions.", json_schema_extra={'format': 'date-time'})
    inherited_permissions_disabled: bool | None = Field(default=None, validation_alias="inheritedPermissionsDisabled", serialization_alias="inheritedPermissionsDisabled", description="When set to true, only organizers, owners, and users with direct permissions can access the item. Inherited permissions from parent folders are disabled.")
    role: str | None = Field(default=None, description="The access level granted by this permission. Common roles include owner, organizer, fileOrganizer, writer, commenter, and reader.")
    view: str | None = Field(default=None, description="The view scope for this permission. Published indicates a publishedReader role; metadata indicates the item is visible only in the metadata view with limited access. Metadata view is only supported on folders.")
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of the grantee. Supported values include: * `user` * `group` * `domain` * `anyone` When creating a permission, if `type` is `user` or `group`, you must provide an `emailAddress` for the user or group. If `type` is `domain`, you must provide a `domain`. If `type` is `anyone`, no extra information is required.")
class PermissionsCreateRequest(StrictModel):
    """Grants access to a file or shared drive by creating a new permission. Supports sharing with users, groups, domains, or the public, with optional ownership transfer and notification settings."""
    path: PermissionsCreateRequestPath
    query: PermissionsCreateRequestQuery | None = None
    body: PermissionsCreateRequestBody | None = None

# Operation: get_permission
class PermissionsGetRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file for which you want to retrieve the permission.")
    permission_id: str = Field(default=..., validation_alias="permissionId", serialization_alias="permissionId", description="The unique identifier of the permission to retrieve.")
class PermissionsGetRequestQuery(StrictModel):
    use_domain_admin_access: bool | None = Field(default=None, validation_alias="useDomainAdminAccess", serialization_alias="useDomainAdminAccess", description="If true, issues the request as a domain administrator, granting access when the file is a shared drive and the requester is an administrator of that shared drive's domain.")
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class PermissionsGetRequest(StrictModel):
    """Retrieves a specific permission for a file by its ID. Use this to inspect sharing settings and access details for a particular file permission."""
    path: PermissionsGetRequestPath
    query: PermissionsGetRequestQuery | None = None

# Operation: update_file_permission
class PermissionsUpdateRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The ID of the file or shared drive containing the permission to update.")
    permission_id: str = Field(default=..., validation_alias="permissionId", serialization_alias="permissionId", description="The ID of the permission to update.")
class PermissionsUpdateRequestQuery(StrictModel):
    remove_expiration: bool | None = Field(default=None, validation_alias="removeExpiration", serialization_alias="removeExpiration", description="Whether to remove the expiration date from this permission.")
    transfer_ownership: bool | None = Field(default=None, validation_alias="transferOwnership", serialization_alias="transferOwnership", description="Whether to transfer ownership of the file to the specified user and downgrade the current owner to a writer role. This parameter must be explicitly set to acknowledge the ownership change side effect.")
    use_domain_admin_access: bool | None = Field(default=None, validation_alias="useDomainAdminAccess", serialization_alias="useDomainAdminAccess", description="Whether to issue this request as a domain administrator. Only applicable when the file ID refers to a shared drive and the requester is an administrator of that domain.")
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class PermissionsUpdateRequestBody(StrictModel):
    allow_file_discovery: bool | None = Field(default=None, validation_alias="allowFileDiscovery", serialization_alias="allowFileDiscovery", description="Whether this permission allows the file to be discovered through search. Only applicable for permissions of type 'domain' or 'anyone'.")
    domain: str | None = Field(default=None, description="The domain to which this permission applies.")
    email_address: str | None = Field(default=None, validation_alias="emailAddress", serialization_alias="emailAddress", description="The email address of the user or group to which this permission applies.")
    expiration_time: str | None = Field(default=None, validation_alias="expirationTime", serialization_alias="expirationTime", description="The expiration date and time for this permission in RFC 3339 format. Can only be set on user and group permissions, must be in the future, and cannot exceed one year from now.", json_schema_extra={'format': 'date-time'})
    inherited_permissions_disabled: bool | None = Field(default=None, validation_alias="inheritedPermissionsDisabled", serialization_alias="inheritedPermissionsDisabled", description="When true, restricts access to only organizers, owners, and users with permissions added directly on the item. Inherited permissions are disabled.")
    role: str | None = Field(default=None, description="The role granted by this permission. Valid roles include: owner, organizer, fileOrganizer, writer, commenter, and reader.")
    view: str | None = Field(default=None, description="The view scope for this permission. Supported values are 'published' (permission role is publishedReader) and 'metadata' (item visible only to metadata view with limited access). The metadata view is only supported on folders.")
class PermissionsUpdateRequest(StrictModel):
    """Updates a file or shared drive permission using patch semantics. Supports modifying role, expiration, ownership transfer, and access settings. Note: Concurrent operations on the same file are not supported; only the last update applies."""
    path: PermissionsUpdateRequestPath
    query: PermissionsUpdateRequestQuery | None = None
    body: PermissionsUpdateRequestBody | None = None

# Operation: delete_permission
class PermissionsDeleteRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file or shared drive from which the permission will be removed.")
    permission_id: str = Field(default=..., validation_alias="permissionId", serialization_alias="permissionId", description="The unique identifier of the permission to be deleted.")
class PermissionsDeleteRequestQuery(StrictModel):
    use_domain_admin_access: bool | None = Field(default=None, validation_alias="useDomainAdminAccess", serialization_alias="useDomainAdminAccess", description="When set to true, issues the request with domain administrator privileges. Requires the file to be a shared drive and the requester to be a domain administrator of the domain owning that shared drive.")
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class PermissionsDeleteRequest(StrictModel):
    """Removes a specific permission from a file or shared drive. Note that concurrent permission operations on the same file are not supported; only the last update will be applied."""
    path: PermissionsDeleteRequestPath
    query: PermissionsDeleteRequestQuery | None = None

# Operation: list_replies
class RepliesListRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the comment.")
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="The unique identifier of the comment whose replies should be listed.")
class RepliesListRequestQuery(StrictModel):
    include_deleted: bool | None = Field(default=None, validation_alias="includeDeleted", serialization_alias="includeDeleted", description="Whether to include deleted replies in the results. Deleted replies will not contain their original content.")
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="Maximum number of replies to return in a single page of results.", ge=1, le=100)
    page_token: str | None = Field(default=None, validation_alias="pageToken", serialization_alias="pageToken", description="Pagination token from the previous response's nextPageToken field to retrieve the next page of results.")
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class RepliesListRequest(StrictModel):
    """Retrieves all replies to a specific comment on a file. Supports pagination and optional inclusion of deleted replies."""
    path: RepliesListRequestPath
    query: RepliesListRequestQuery | None = None

# Operation: create_comment_reply
class RepliesCreateRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the comment.")
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="The unique identifier of the comment to which the reply is being added.")
class RepliesCreateRequestQuery(StrictModel):
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class RepliesCreateRequestBody(StrictModel):
    action: str | None = Field(default=None, description="The action to perform on the parent comment. Use this to resolve or reopen a comment instead of adding reply content.")
    content: str | None = Field(default=None, description="The plain text content of the reply. Required if no action is specified. The content will be displayed as plain text in the API response.")
class RepliesCreateRequest(StrictModel):
    """Creates a reply to an existing comment on a file. Replies can either add content or perform actions like resolving or reopening the parent comment."""
    path: RepliesCreateRequestPath
    query: RepliesCreateRequestQuery | None = None
    body: RepliesCreateRequestBody | None = None

# Operation: get_reply
class RepliesGetRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the comment and reply.")
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="The unique identifier of the comment that contains the reply.")
    reply_id: str = Field(default=..., validation_alias="replyId", serialization_alias="replyId", description="The unique identifier of the reply to retrieve.")
class RepliesGetRequestQuery(StrictModel):
    include_deleted: bool | None = Field(default=None, validation_alias="includeDeleted", serialization_alias="includeDeleted", description="Whether to include deleted replies in the response. Deleted replies are returned without their original content.")
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class RepliesGetRequest(StrictModel):
    """Retrieves a specific reply to a comment on a file. Optionally includes deleted replies, which are returned without their original content."""
    path: RepliesGetRequestPath
    query: RepliesGetRequestQuery | None = None

# Operation: update_reply
class RepliesUpdateRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the comment and reply.")
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="The unique identifier of the comment that contains the reply being updated.")
    reply_id: str = Field(default=..., validation_alias="replyId", serialization_alias="replyId", description="The unique identifier of the reply to update.")
class RepliesUpdateRequestQuery(StrictModel):
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class RepliesUpdateRequestBody(StrictModel):
    action: str | None = Field(default=None, description="The action this reply performs on the parent comment. Use to resolve or reopen a comment thread.")
    content: str | None = Field(default=None, description="The plain text content of the reply. Required if no action is specified. Note: use htmlContent for display purposes.")
class RepliesUpdateRequest(StrictModel):
    """Updates a reply on a comment in a file using patch semantics. Supports modifying reply content or changing the reply's action status (resolve/reopen) relative to the parent comment."""
    path: RepliesUpdateRequestPath
    query: RepliesUpdateRequestQuery | None = None
    body: RepliesUpdateRequestBody | None = None

# Operation: delete_reply
class RepliesDeleteRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the comment with the reply to delete.")
    comment_id: str = Field(default=..., validation_alias="commentId", serialization_alias="commentId", description="The unique identifier of the comment containing the reply to delete.")
    reply_id: str = Field(default=..., validation_alias="replyId", serialization_alias="replyId", description="The unique identifier of the reply to delete.")
class RepliesDeleteRequestQuery(StrictModel):
    fields: str | None = Field(default=None, description="Selector specifying which fields to include in a partial response.")
class RepliesDeleteRequest(StrictModel):
    """Deletes a reply from a comment on a file. This operation permanently removes the specified reply and cannot be undone."""
    path: RepliesDeleteRequestPath
    query: RepliesDeleteRequestQuery | None = None

# Operation: get_file_revision
class RevisionsGetRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the revision.")
    revision_id: str = Field(default=..., validation_alias="revisionId", serialization_alias="revisionId", description="The unique identifier of the specific revision to retrieve.")
class RevisionsGetRequest(StrictModel):
    """Retrieves a specific file revision's metadata or content by its ID. Use this to access historical versions of a file for review, recovery, or comparison purposes."""
    path: RevisionsGetRequestPath

# Operation: update_file_revision
class RevisionsUpdateRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the revision to update.")
    revision_id: str = Field(default=..., validation_alias="revisionId", serialization_alias="revisionId", description="The unique identifier of the revision to update.")
class RevisionsUpdateRequestBody(StrictModel):
    keep_forever: bool | None = Field(default=None, validation_alias="keepForever", serialization_alias="keepForever", description="Whether to permanently retain this revision in the file's history. When enabled, the revision will not be automatically deleted after 30 days. Limited to a maximum of 200 retained revisions per file. Only applicable to files with binary content in Drive.")
    publish_auto: bool | None = Field(default=None, validation_alias="publishAuto", serialization_alias="publishAuto", description="Whether to automatically republish subsequent revisions of this file. Only applicable to Google Docs, Sheets, and Slides files.")
class RevisionsUpdateRequest(StrictModel):
    """Updates a file revision's metadata using patch semantics, allowing you to preserve revisions indefinitely or configure auto-republishing behavior for Docs Editors files."""
    path: RevisionsUpdateRequestPath
    body: RevisionsUpdateRequestBody | None = None

# Operation: delete_file_revision
class RevisionsDeleteRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file containing the revision to delete.")
    revision_id: str = Field(default=..., validation_alias="revisionId", serialization_alias="revisionId", description="The unique identifier of the specific file revision to permanently delete.")
class RevisionsDeleteRequest(StrictModel):
    """Permanently deletes a specific version of a file. Only binary files (images, videos, etc.) support revision deletion; revisions for Google Docs, Sheets, and the last remaining file version cannot be deleted."""
    path: RevisionsDeleteRequestPath

# Operation: list_file_revisions
class RevisionsListRequestPath(StrictModel):
    file_id: str = Field(default=..., validation_alias="fileId", serialization_alias="fileId", description="The unique identifier of the file whose revisions you want to list.")
class RevisionsListRequestQuery(StrictModel):
    page_size: int | None = Field(default=None, validation_alias="pageSize", serialization_alias="pageSize", description="The maximum number of revisions to return in a single page of results.", ge=1, le=1000)
    page_token: str | None = Field(default=None, validation_alias="pageToken", serialization_alias="pageToken", description="A pagination token from a previous response to retrieve the next page of results. Use the 'nextPageToken' value returned from the prior request.")
class RevisionsListRequest(StrictModel):
    """Retrieves a list of revisions for a specified file. Note that the revision history may be incomplete for files with extensive revision histories, and older revisions might be omitted from the response."""
    path: RevisionsListRequestPath
    query: RevisionsListRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class AppIcons(PermissiveModel):
    category: str | None = Field(None, description="Category of the icon. Allowed values are: * `application` - The icon for the application. * `document` - The icon for a file associated with the app. * `documentShared` - The icon for a shared file associated with the app.")
    icon_url: str | None = Field(None, validation_alias="iconUrl", serialization_alias="iconUrl", description="URL for the icon.")
    size: int | None = Field(None, description="Size of the icon. Represented as the maximum of the width and height.", json_schema_extra={'format': 'int32'})

class App(PermissiveModel):
    """The `apps` resource provides a list of apps that a user has installed, with information about each app's supported MIME types, file extensions, and other details. Some resource methods (such as `apps.get`) require an `appId`. Use the `apps.list` method to retrieve the ID for an installed application."""
    authorized: bool | None = Field(None, description="Whether the app is authorized to access data on the user's Drive.")
    create_in_folder_template: str | None = Field(None, validation_alias="createInFolderTemplate", serialization_alias="createInFolderTemplate", description="The template URL to create a file with this app in a given folder. The template contains the {folderId} to be replaced by the folder ID house the new file.")
    create_url: str | None = Field(None, validation_alias="createUrl", serialization_alias="createUrl", description="The URL to create a file with this app.")
    has_drive_wide_scope: bool | None = Field(None, validation_alias="hasDriveWideScope", serialization_alias="hasDriveWideScope", description="Whether the app has Drive-wide scope. An app with Drive-wide scope can access all files in the user's Drive.")
    icons: list[AppIcons] | None = Field(None, description="The various icons for the app.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of the app.")
    installed: bool | None = Field(None, description="Whether the app is installed.")
    kind: str | None = Field('drive#app', description="Output only. Identifies what kind of resource this is. Value: the fixed string \"drive#app\".")
    long_description: str | None = Field(None, validation_alias="longDescription", serialization_alias="longDescription", description="A long description of the app.")
    name: str | None = Field(None, description="The name of the app.")
    object_type: str | None = Field(None, validation_alias="objectType", serialization_alias="objectType", description="The type of object this app creates such as a Chart. If empty, the app name should be used instead.")
    open_url_template: str | None = Field(None, validation_alias="openUrlTemplate", serialization_alias="openUrlTemplate", description="The template URL for opening files with this app. The template contains {ids} or {exportIds} to be replaced by the actual file IDs. For more information, see Open Files for the full documentation.")
    primary_file_extensions: list[str] | None = Field(None, validation_alias="primaryFileExtensions", serialization_alias="primaryFileExtensions", description="The list of primary file extensions.")
    primary_mime_types: list[str] | None = Field(None, validation_alias="primaryMimeTypes", serialization_alias="primaryMimeTypes", description="The list of primary MIME types.")
    product_id: str | None = Field(None, validation_alias="productId", serialization_alias="productId", description="The ID of the product listing for this app.")
    product_url: str | None = Field(None, validation_alias="productUrl", serialization_alias="productUrl", description="A link to the product listing for this app.")
    secondary_file_extensions: list[str] | None = Field(None, validation_alias="secondaryFileExtensions", serialization_alias="secondaryFileExtensions", description="The list of secondary file extensions.")
    secondary_mime_types: list[str] | None = Field(None, validation_alias="secondaryMimeTypes", serialization_alias="secondaryMimeTypes", description="The list of secondary MIME types.")
    short_description: str | None = Field(None, validation_alias="shortDescription", serialization_alias="shortDescription", description="A short description of the app.")
    supports_create: bool | None = Field(None, validation_alias="supportsCreate", serialization_alias="supportsCreate", description="Whether this app supports creating objects.")
    supports_import: bool | None = Field(None, validation_alias="supportsImport", serialization_alias="supportsImport", description="Whether this app supports importing from Google Docs.")
    supports_multi_open: bool | None = Field(None, validation_alias="supportsMultiOpen", serialization_alias="supportsMultiOpen", description="Whether this app supports opening more than one file.")
    supports_offline_create: bool | None = Field(None, validation_alias="supportsOfflineCreate", serialization_alias="supportsOfflineCreate", description="Whether this app supports creating files when offline.")
    use_by_default: bool | None = Field(None, validation_alias="useByDefault", serialization_alias="useByDefault", description="Whether the app is selected as the default handler for the types it supports.")

class DownloadRestriction(PermissiveModel):
    """A restriction for copy and download of the file."""
    restricted_for_readers: bool | None = Field(None, validation_alias="restrictedForReaders", serialization_alias="restrictedForReaders", description="Whether download and copy is restricted for readers.")
    restricted_for_writers: bool | None = Field(None, validation_alias="restrictedForWriters", serialization_alias="restrictedForWriters", description="Whether download and copy is restricted for writers. If `true`, download is also restricted for readers.")

class DriveBackgroundImageFile(PermissiveModel):
    """An image file and cropping parameters from which a background image for this shared drive is set. This is a write only field; it can only be set on `drive.drives.update` requests that don't set `themeId`. When specified, all fields of the `backgroundImageFile` must be set."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of an image file in Google Drive to use for the background image.")
    width: float | None = Field(None, description="The width of the cropped image in the closed range of 0 to 1. This value represents the width of the cropped image divided by the width of the entire image. The height is computed by applying a width to height aspect ratio of 80 to 9. The resulting image must be at least 1280 pixels wide and 144 pixels high.", json_schema_extra={'format': 'float'})
    x_coordinate: float | None = Field(None, validation_alias="xCoordinate", serialization_alias="xCoordinate", description="The X coordinate of the upper left corner of the cropping area in the background image. This is a value in the closed range of 0 to 1. This value represents the horizontal distance from the left side of the entire image to the left side of the cropping area divided by the width of the entire image.", json_schema_extra={'format': 'float'})
    y_coordinate: float | None = Field(None, validation_alias="yCoordinate", serialization_alias="yCoordinate", description="The Y coordinate of the upper left corner of the cropping area in the background image. This is a value in the closed range of 0 to 1. This value represents the vertical distance from the top side of the entire image to the top side of the cropping area divided by the height of the entire image.", json_schema_extra={'format': 'float'})

class DriveCapabilities(PermissiveModel):
    """Output only. Capabilities the current user has on this shared drive."""
    can_add_children: bool | None = Field(None, validation_alias="canAddChildren", serialization_alias="canAddChildren", description="Output only. Whether the current user can add children to folders in this shared drive.")
    can_change_copy_requires_writer_permission_restriction: bool | None = Field(None, validation_alias="canChangeCopyRequiresWriterPermissionRestriction", serialization_alias="canChangeCopyRequiresWriterPermissionRestriction", description="Output only. Whether the current user can change the `copyRequiresWriterPermission` restriction of this shared drive.")
    can_change_domain_users_only_restriction: bool | None = Field(None, validation_alias="canChangeDomainUsersOnlyRestriction", serialization_alias="canChangeDomainUsersOnlyRestriction", description="Output only. Whether the current user can change the `domainUsersOnly` restriction of this shared drive.")
    can_change_download_restriction: bool | None = Field(None, validation_alias="canChangeDownloadRestriction", serialization_alias="canChangeDownloadRestriction", description="Output only. Whether the current user can change organizer-applied download restrictions of this shared drive.")
    can_change_drive_background: bool | None = Field(None, validation_alias="canChangeDriveBackground", serialization_alias="canChangeDriveBackground", description="Output only. Whether the current user can change the background of this shared drive.")
    can_change_drive_members_only_restriction: bool | None = Field(None, validation_alias="canChangeDriveMembersOnlyRestriction", serialization_alias="canChangeDriveMembersOnlyRestriction", description="Output only. Whether the current user can change the `driveMembersOnly` restriction of this shared drive.")
    can_change_sharing_folders_requires_organizer_permission_restriction: bool | None = Field(None, validation_alias="canChangeSharingFoldersRequiresOrganizerPermissionRestriction", serialization_alias="canChangeSharingFoldersRequiresOrganizerPermissionRestriction", description="Output only. Whether the current user can change the `sharingFoldersRequiresOrganizerPermission` restriction of this shared drive.")
    can_comment: bool | None = Field(None, validation_alias="canComment", serialization_alias="canComment", description="Output only. Whether the current user can comment on files in this shared drive.")
    can_copy: bool | None = Field(None, validation_alias="canCopy", serialization_alias="canCopy", description="Output only. Whether the current user can copy files in this shared drive.")
    can_delete_children: bool | None = Field(None, validation_alias="canDeleteChildren", serialization_alias="canDeleteChildren", description="Output only. Whether the current user can delete children from folders in this shared drive.")
    can_delete_drive: bool | None = Field(None, validation_alias="canDeleteDrive", serialization_alias="canDeleteDrive", description="Output only. Whether the current user can delete this shared drive. Attempting to delete the shared drive may still fail if there are untrashed items inside the shared drive.")
    can_download: bool | None = Field(None, validation_alias="canDownload", serialization_alias="canDownload", description="Output only. Whether the current user can download files in this shared drive.")
    can_edit: bool | None = Field(None, validation_alias="canEdit", serialization_alias="canEdit", description="Output only. Whether the current user can edit files in this shared drive")
    can_list_children: bool | None = Field(None, validation_alias="canListChildren", serialization_alias="canListChildren", description="Output only. Whether the current user can list the children of folders in this shared drive.")
    can_manage_members: bool | None = Field(None, validation_alias="canManageMembers", serialization_alias="canManageMembers", description="Output only. Whether the current user can add members to this shared drive or remove them or change their role.")
    can_read_revisions: bool | None = Field(None, validation_alias="canReadRevisions", serialization_alias="canReadRevisions", description="Output only. Whether the current user can read the revisions resource of files in this shared drive.")
    can_rename: bool | None = Field(None, validation_alias="canRename", serialization_alias="canRename", description="Output only. Whether the current user can rename files or folders in this shared drive.")
    can_rename_drive: bool | None = Field(None, validation_alias="canRenameDrive", serialization_alias="canRenameDrive", description="Output only. Whether the current user can rename this shared drive.")
    can_reset_drive_restrictions: bool | None = Field(None, validation_alias="canResetDriveRestrictions", serialization_alias="canResetDriveRestrictions", description="Output only. Whether the current user can reset the shared drive restrictions to defaults.")
    can_share: bool | None = Field(None, validation_alias="canShare", serialization_alias="canShare", description="Output only. Whether the current user can share files or folders in this shared drive.")
    can_trash_children: bool | None = Field(None, validation_alias="canTrashChildren", serialization_alias="canTrashChildren", description="Output only. Whether the current user can trash children from folders in this shared drive.")

class DriveRestrictions(PermissiveModel):
    """A set of restrictions that apply to this shared drive or items inside this shared drive. Note that restrictions can't be set when creating a shared drive. To add a restriction, first create a shared drive and then use `drives.update` to add restrictions."""
    admin_managed_restrictions: bool | None = Field(None, validation_alias="adminManagedRestrictions", serialization_alias="adminManagedRestrictions", description="Whether administrative privileges on this shared drive are required to modify restrictions.")
    copy_requires_writer_permission: bool | None = Field(None, validation_alias="copyRequiresWriterPermission", serialization_alias="copyRequiresWriterPermission", description="Whether the options to copy, print, or download files inside this shared drive, should be disabled for readers and commenters. When this restriction is set to `true`, it will override the similarly named field to `true` for any file inside this shared drive.")
    domain_users_only: bool | None = Field(None, validation_alias="domainUsersOnly", serialization_alias="domainUsersOnly", description="Whether access to this shared drive and items inside this shared drive is restricted to users of the domain to which this shared drive belongs. This restriction may be overridden by other sharing policies controlled outside of this shared drive.")
    download_restriction: DownloadRestriction | None = Field(None, validation_alias="downloadRestriction", serialization_alias="downloadRestriction", description="Download restrictions applied by shared drive managers.")
    drive_members_only: bool | None = Field(None, validation_alias="driveMembersOnly", serialization_alias="driveMembersOnly", description="Whether access to items inside this shared drive is restricted to its members.")
    sharing_folders_requires_organizer_permission: bool | None = Field(None, validation_alias="sharingFoldersRequiresOrganizerPermission", serialization_alias="sharingFoldersRequiresOrganizerPermission", description="If true, only users with the organizer role can share folders. If false, users with either the organizer role or the file organizer role can share folders.")

class Drive(PermissiveModel):
    """Representation of a shared drive. Some resource methods (such as `drives.update`) require a `driveId`. Use the `drives.list` method to retrieve the ID for a shared drive."""
    background_image_file: DriveBackgroundImageFile | None = Field(None, validation_alias="backgroundImageFile", serialization_alias="backgroundImageFile", description="An image file and cropping parameters from which a background image for this shared drive is set. This is a write only field; it can only be set on `drive.drives.update` requests that don't set `themeId`. When specified, all fields of the `backgroundImageFile` must be set.")
    background_image_link: str | None = Field(None, validation_alias="backgroundImageLink", serialization_alias="backgroundImageLink", description="Output only. A short-lived link to this shared drive's background image.")
    capabilities: DriveCapabilities | None = Field(None, description="Output only. Capabilities the current user has on this shared drive.")
    color_rgb: str | None = Field(None, validation_alias="colorRgb", serialization_alias="colorRgb", description="The color of this shared drive as an RGB hex string. It can only be set on a `drive.drives.update` request that does not set `themeId`.")
    created_time: str | None = Field(None, validation_alias="createdTime", serialization_alias="createdTime", description="The time at which the shared drive was created (RFC 3339 date-time).", json_schema_extra={'format': 'date-time'})
    hidden: bool | None = Field(None, description="Whether the shared drive is hidden from default view.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="Output only. The ID of this shared drive which is also the ID of the top level folder of this shared drive.")
    kind: str | None = Field('drive#drive', description="Output only. Identifies what kind of resource this is. Value: the fixed string `\"drive#drive\"`.")
    name: str | None = Field(None, description="The name of this shared drive.")
    org_unit_id: str | None = Field(None, validation_alias="orgUnitId", serialization_alias="orgUnitId", description="Output only. The organizational unit of this shared drive. This field is only populated on `drives.list` responses when the `useDomainAdminAccess` parameter is set to `true`.")
    restrictions: DriveRestrictions | None = Field(None, description="A set of restrictions that apply to this shared drive or items inside this shared drive. Note that restrictions can't be set when creating a shared drive. To add a restriction, first create a shared drive and then use `drives.update` to add restrictions.")
    theme_id: str | None = Field(None, validation_alias="themeId", serialization_alias="themeId", description="The ID of the theme from which the background image and color will be set. The set of possible `driveThemes` can be retrieved from a `drive.about.get` response. When not specified on a `drive.drives.create` request, a random theme is chosen from which the background image and color are set. This is a write-only field; it can only be set on requests that don't set `colorRgb` or `backgroundImageFile`.")

class LabelFieldModification(PermissiveModel):
    """A modification to a label's field."""
    field_id: str | None = Field(None, validation_alias="fieldId", serialization_alias="fieldId", description="The ID of the field to be modified.")
    kind: str | None = Field(None, description="This is always `\"drive#labelFieldModification\"`.")
    set_date_values: list[str] | None = Field(None, validation_alias="setDateValues", serialization_alias="setDateValues", description="Replaces the value of a dateString Field with these new values. The string must be in the RFC 3339 full-date format: YYYY-MM-DD.")
    set_integer_values: list[str] | None = Field(None, validation_alias="setIntegerValues", serialization_alias="setIntegerValues", description="Replaces the value of an `integer` field with these new values.")
    set_selection_values: list[str] | None = Field(None, validation_alias="setSelectionValues", serialization_alias="setSelectionValues", description="Replaces a `selection` field with these new values.")
    set_text_values: list[str] | None = Field(None, validation_alias="setTextValues", serialization_alias="setTextValues", description="Sets the value of a `text` field.")
    set_user_values: list[str] | None = Field(None, validation_alias="setUserValues", serialization_alias="setUserValues", description="Replaces a `user` field with these new values. The values must be a valid email addresses.")
    unset_values: bool | None = Field(None, validation_alias="unsetValues", serialization_alias="unsetValues", description="Unsets the values for this field.")

class LabelModification(PermissiveModel):
    """A modification to a label on a file. A `LabelModification` can be used to apply a label to a file, update an existing label on a file, or remove a label from a file."""
    field_modifications: list[LabelFieldModification] | None = Field(None, validation_alias="fieldModifications", serialization_alias="fieldModifications", description="The list of modifications to this label's fields.")
    kind: str | None = Field(None, description="This is always `\"drive#labelModification\"`.")
    label_id: str | None = Field(None, validation_alias="labelId", serialization_alias="labelId", description="The ID of the label to modify.")
    remove_label: bool | None = Field(None, validation_alias="removeLabel", serialization_alias="removeLabel", description="If true, the label will be removed from the file.")

class User(PermissiveModel):
    """Information about a Drive user."""
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName", description="Output only. A plain text displayable name for this user.")
    email_address: str | None = Field(None, validation_alias="emailAddress", serialization_alias="emailAddress", description="Output only. The email address of the user. This may not be present in certain contexts if the user has not made their email address visible to the requester.")
    kind: str | None = Field('drive#user', description="Output only. Identifies what kind of resource this is. Value: the fixed string `drive#user`.")
    me: bool | None = Field(None, description="Output only. Whether this user is the requesting user.")
    permission_id: str | None = Field(None, validation_alias="permissionId", serialization_alias="permissionId", description="Output only. The user's ID as visible in Permission resources.")
    photo_link: str | None = Field(None, validation_alias="photoLink", serialization_alias="photoLink", description="Output only. A link to the user's profile photo, if available.")

class ContentRestriction(PermissiveModel):
    """A restriction for accessing the content of the file."""
    owner_restricted: bool | None = Field(None, validation_alias="ownerRestricted", serialization_alias="ownerRestricted", description="Whether the content restriction can only be modified or removed by a user who owns the file. For files in shared drives, any user with `organizer` capabilities can modify or remove this content restriction.")
    read_only: bool | None = Field(None, validation_alias="readOnly", serialization_alias="readOnly", description="Whether the content of the file is read-only. If a file is read-only, a new revision of the file may not be added, comments may not be added or modified, and the title of the file may not be modified.")
    reason: str | None = Field(None, description="Reason for why the content of the file is restricted. This is only mutable on requests that also set `readOnly=true`.")
    restricting_user: User | None = Field(None, validation_alias="restrictingUser", serialization_alias="restrictingUser", description="Output only. The user who set the content restriction. Only populated if `readOnly=true`.")
    restriction_time: str | None = Field(None, validation_alias="restrictionTime", serialization_alias="restrictionTime", description="The time at which the content restriction was set (formatted RFC 3339 timestamp). Only populated if readOnly is true.", json_schema_extra={'format': 'date-time'})
    system_restricted: bool | None = Field(None, validation_alias="systemRestricted", serialization_alias="systemRestricted", description="Output only. Whether the content restriction was applied by the system, for example due to an esignature. Users cannot modify or remove system restricted content restrictions.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="Output only. The type of the content restriction. Currently the only possible value is `globalContentRestriction`.")


# Rebuild models to resolve forward references (required for circular refs)
App.model_rebuild()
AppIcons.model_rebuild()
ContentRestriction.model_rebuild()
DownloadRestriction.model_rebuild()
Drive.model_rebuild()
DriveBackgroundImageFile.model_rebuild()
DriveCapabilities.model_rebuild()
DriveRestrictions.model_rebuild()
LabelFieldModification.model_rebuild()
LabelModification.model_rebuild()
User.model_rebuild()

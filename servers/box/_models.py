"""
Box MCP Server - Pydantic Models

Generated: 2026-04-14 18:16:26 UTC
Generator: MCP Blacksmith v1.1.0 (https://mcpblacksmith.com)
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from _validators import PermissiveModel, StrictModel
from pydantic import AfterValidator, Field


def _check_unique_items(v: list) -> list:
    """Validate that array items are unique (OAS uniqueItems: true)."""
    seen = []
    for item in v:
        if item in seen:
            raise ValueError("array items must be unique")
        seen.append(item)
    return v


__all__ = [
    "DeleteCollaborationsIdRequest",
    "DeleteCommentsIdRequest",
    "DeleteDevicePinnersIdRequest",
    "DeleteFileRequestsIdRequest",
    "DeleteFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest",
    "DeleteFilesIdMetadataGlobalBoxSkillsCardsRequest",
    "DeleteFilesIdMetadataIdIdRequest",
    "DeleteFilesIdRequest",
    "DeleteFilesIdTrashRequest",
    "DeleteFilesIdVersionsIdRequest",
    "DeleteFilesIdWatermarkRequest",
    "DeleteFilesUploadSessionsIdRequest",
    "DeleteFolderLocksIdRequest",
    "DeleteFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest",
    "DeleteFoldersIdMetadataIdIdRequest",
    "DeleteFoldersIdRequest",
    "DeleteFoldersIdTrashRequest",
    "DeleteFoldersIdWatermarkRequest",
    "DeleteGroupMembershipsIdRequest",
    "DeleteGroupsIdRequest",
    "DeleteLegalHoldPoliciesIdRequest",
    "DeleteLegalHoldPolicyAssignmentsIdRequest",
    "DeleteMetadataTaxonomiesIdIdNodesIdRequest",
    "DeleteMetadataTemplatesIdIdSchemaRequest",
    "DeleteRetentionPoliciesIdRequest",
    "DeleteRetentionPolicyAssignmentsIdRequest",
    "DeleteShieldInformationBarrierSegmentMembersIdRequest",
    "DeleteShieldInformationBarrierSegmentsIdRequest",
    "DeleteStoragePolicyAssignmentsIdRequest",
    "DeleteTaskAssignmentsIdRequest",
    "DeleteTasksIdRequest",
    "DeleteUsersIdAvatarRequest",
    "DeleteUsersIdEmailAliasesIdRequest",
    "DeleteUsersIdRequest",
    "DeleteWebhooksIdRequest",
    "DeleteWebLinksIdRequest",
    "DeleteWebLinksIdTrashRequest",
    "GetAiAgentsIdRequest",
    "GetAiAgentsRequest",
    "GetCollaborationsIdRequest",
    "GetCollaborationsRequest",
    "GetCollaborationWhitelistEntriesIdRequest",
    "GetCollectionsIdItemsRequest",
    "GetCollectionsIdRequest",
    "GetCollectionsRequest",
    "GetCommentsIdRequest",
    "GetDevicePinnersIdRequest",
    "GetEnterprisesIdDevicePinnersRequest",
    "GetEventsRequest",
    "GetFileRequestsIdRequest",
    "GetFilesIdAppItemAssociationsRequest",
    "GetFilesIdCollaborationsRequest",
    "GetFilesIdCommentsRequest",
    "GetFilesIdContentRequest",
    "GetFilesIdGetSharedLinkRequest",
    "GetFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest",
    "GetFilesIdMetadataGlobalBoxSkillsCardsRequest",
    "GetFilesIdMetadataIdIdRequest",
    "GetFilesIdMetadataRequest",
    "GetFilesIdRequest",
    "GetFilesIdTasksRequest",
    "GetFilesIdThumbnailIdRequest",
    "GetFilesIdTrashRequest",
    "GetFilesIdVersionsIdRequest",
    "GetFilesIdVersionsRequest",
    "GetFilesIdWatermarkRequest",
    "GetFilesUploadSessionsIdPartsRequest",
    "GetFilesUploadSessionsIdRequest",
    "GetFileVersionLegalHoldsIdRequest",
    "GetFileVersionLegalHoldsRequest",
    "GetFolderLocksRequest",
    "GetFoldersIdAppItemAssociationsRequest",
    "GetFoldersIdCollaborationsRequest",
    "GetFoldersIdGetSharedLinkRequest",
    "GetFoldersIdItemsRequest",
    "GetFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest",
    "GetFoldersIdMetadataIdIdRequest",
    "GetFoldersIdMetadataRequest",
    "GetFoldersIdRequest",
    "GetFoldersIdTrashRequest",
    "GetFoldersIdWatermarkRequest",
    "GetFoldersTrashItemsRequest",
    "GetGroupMembershipsIdRequest",
    "GetGroupsIdCollaborationsRequest",
    "GetGroupsIdMembershipsRequest",
    "GetGroupsIdRequest",
    "GetGroupsRequest",
    "GetIntegrationMappingsSlackRequest",
    "GetIntegrationMappingsTeamsRequest",
    "GetInvitesIdRequest",
    "GetLegalHoldPoliciesIdRequest",
    "GetLegalHoldPoliciesRequest",
    "GetLegalHoldPolicyAssignmentsIdFilesOnHoldRequest",
    "GetLegalHoldPolicyAssignmentsIdFileVersionsOnHoldRequest",
    "GetLegalHoldPolicyAssignmentsIdRequest",
    "GetLegalHoldPolicyAssignmentsRequest",
    "GetMetadataCascadePoliciesIdRequest",
    "GetMetadataCascadePoliciesRequest",
    "GetMetadataTaxonomiesIdIdNodesIdRequest",
    "GetMetadataTaxonomiesIdIdNodesRequest",
    "GetMetadataTaxonomiesIdIdRequest",
    "GetMetadataTaxonomiesIdRequest",
    "GetMetadataTemplatesEnterpriseRequest",
    "GetMetadataTemplatesGlobalRequest",
    "GetMetadataTemplatesIdIdFieldsIdOptionsRequest",
    "GetMetadataTemplatesIdIdSchemaRequest",
    "GetMetadataTemplatesIdRequest",
    "GetMetadataTemplatesRequest",
    "GetRecentItemsRequest",
    "GetRetentionPoliciesIdAssignmentsRequest",
    "GetRetentionPoliciesIdRequest",
    "GetRetentionPoliciesRequest",
    "GetRetentionPolicyAssignmentsIdFilesUnderRetentionRequest",
    "GetRetentionPolicyAssignmentsIdFileVersionsUnderRetentionRequest",
    "GetRetentionPolicyAssignmentsIdRequest",
    "GetSearchRequest",
    "GetSharedItemsAppItemsRequest",
    "GetSharedItemsFoldersRequest",
    "GetSharedItemsRequest",
    "GetSharedItemsWebLinksRequest",
    "GetShieldInformationBarrierReportsIdRequest",
    "GetShieldInformationBarrierReportsRequest",
    "GetShieldInformationBarrierSegmentMembersIdRequest",
    "GetShieldInformationBarrierSegmentMembersRequest",
    "GetShieldInformationBarrierSegmentRestrictionsIdRequest",
    "GetShieldInformationBarrierSegmentRestrictionsRequest",
    "GetShieldInformationBarrierSegmentsIdRequest",
    "GetShieldInformationBarrierSegmentsRequest",
    "GetShieldInformationBarriersIdRequest",
    "GetShieldInformationBarriersRequest",
    "GetSignRequestsIdRequest",
    "GetSignRequestsRequest",
    "GetSignTemplatesIdRequest",
    "GetSignTemplatesRequest",
    "GetStoragePolicyAssignmentsIdRequest",
    "GetStoragePolicyAssignmentsRequest",
    "GetTaskAssignmentsIdRequest",
    "GetTasksIdAssignmentsRequest",
    "GetTasksIdRequest",
    "GetTermsOfServiceUserStatusesRequest",
    "GetUsersIdAvatarRequest",
    "GetUsersIdEmailAliasesRequest",
    "GetUsersIdMembershipsRequest",
    "GetUsersIdRequest",
    "GetUsersRequest",
    "GetWebhooksIdRequest",
    "GetWebhooksRequest",
    "GetWebLinksIdGetSharedLinkRequest",
    "GetWebLinksIdRequest",
    "GetWebLinksIdTrashRequest",
    "GetWorkflowsRequest",
    "GetZipDownloadsIdContentRequest",
    "GetZipDownloadsIdStatusRequest",
    "PostAiAgentsRequest",
    "PostAiExtractRequest",
    "PostAiExtractStructuredRequest",
    "PostCollaborationsRequest",
    "PostCommentsRequest",
    "PostFileRequestsIdCopyRequest",
    "PostFilesContentRequest",
    "PostFilesIdContentRequest",
    "PostFilesIdCopyRequest",
    "PostFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest",
    "PostFilesIdMetadataGlobalBoxSkillsCardsRequest",
    "PostFilesIdMetadataIdIdRequest",
    "PostFilesIdRequest",
    "PostFilesIdUploadSessionsRequest",
    "PostFilesIdVersionsCurrentRequest",
    "PostFilesUploadSessionsIdCommitRequest",
    "PostFilesUploadSessionsRequest",
    "PostFolderLocksRequest",
    "PostFoldersIdCopyRequest",
    "PostFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest",
    "PostFoldersIdMetadataIdIdRequest",
    "PostFoldersIdRequest",
    "PostFoldersRequest",
    "PostGroupMembershipsRequest",
    "PostGroupsRequest",
    "PostGroupsTerminateSessionsRequest",
    "PostIntegrationMappingsTeamsRequest",
    "PostInvitesRequest",
    "PostLegalHoldPolicyAssignmentsRequest",
    "PostMetadataCascadePoliciesIdApplyRequest",
    "PostMetadataCascadePoliciesRequest",
    "PostMetadataQueriesExecuteReadRequest",
    "PostMetadataTemplatesSchemaClassificationsRequest",
    "PostMetadataTemplatesSchemaRequest",
    "PostRetentionPolicyAssignmentsRequest",
    "PostShieldInformationBarrierReportsRequest",
    "PostShieldInformationBarriersChangeStatusRequest",
    "PostShieldInformationBarrierSegmentMembersRequest",
    "PostShieldInformationBarrierSegmentsRequest",
    "PostShieldInformationBarriersRequest",
    "PostSignRequestsIdCancelRequest",
    "PostSignRequestsIdResendRequest",
    "PostSignRequestsRequest",
    "PostStoragePolicyAssignmentsRequest",
    "PostTaskAssignmentsRequest",
    "PostTasksRequest",
    "PostTermsOfServiceUserStatusesRequest",
    "PostUsersIdAvatarRequest",
    "PostUsersIdEmailAliasesRequest",
    "PostUsersRequest",
    "PostUsersTerminateSessionsRequest",
    "PostWebLinksIdRequest",
    "PostWebLinksRequest",
    "PostWorkflowsIdStartRequest",
    "PostZipDownloadsRequest",
    "PutCollaborationsIdRequest",
    "PutCommentsIdRequest",
    "PutFileRequestsIdRequest",
    "PutFilesIdAddSharedLinkRequest",
    "PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest",
    "PutFilesIdMetadataGlobalBoxSkillsCardsRequest",
    "PutFilesIdMetadataIdIdRequest",
    "PutFilesIdRemoveSharedLinkRequest",
    "PutFilesIdRequest",
    "PutFilesIdUpdateSharedLinkRequest",
    "PutFilesIdVersionsIdRequest",
    "PutFilesIdWatermarkRequest",
    "PutFilesUploadSessionsIdRequest",
    "PutFoldersIdAddSharedLinkRequest",
    "PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest",
    "PutFoldersIdMetadataIdIdRequest",
    "PutFoldersIdRemoveSharedLinkRequest",
    "PutFoldersIdRequest",
    "PutFoldersIdUpdateSharedLinkRequest",
    "PutFoldersIdWatermarkRequest",
    "PutGroupMembershipsIdRequest",
    "PutGroupsIdRequest",
    "PutLegalHoldPoliciesIdRequest",
    "PutMetadataTemplatesIdIdSchemaRequest",
    "PutRetentionPoliciesIdRequest",
    "PutShieldInformationBarrierSegmentsIdRequest",
    "PutSkillInvocationsIdRequest",
    "PutTaskAssignmentsIdRequest",
    "PutTasksIdRequest",
    "PutTermsOfServiceUserStatusesIdRequest",
    "PutUsersIdFolders0Request",
    "PutUsersIdRequest",
    "PutWebLinksIdAddSharedLinkRequest",
    "PutWebLinksIdRemoveSharedLinkRequest",
    "PutWebLinksIdRequest",
    "PutWebLinksIdUpdateSharedLinkRequest",
    "AiAgentExtract",
    "AiAgentExtractStructured",
    "AiAgentReference",
    "AiItemBase",
    "FileRequestCopyRequest",
    "GroupBase",
    "MetadataFilter",
    "Outcome",
    "PostAiAgentsBodyAskBasicImage",
    "PostAiAgentsBodyAskBasicImageMulti",
    "PostAiAgentsBodyAskBasicText",
    "PostAiAgentsBodyAskBasicTextMulti",
    "PostAiAgentsBodyAskLongText",
    "PostAiAgentsBodyAskLongTextMulti",
    "PostAiAgentsBodyAskSpreadsheet",
    "PostAiAgentsBodyExtractBasicImage",
    "PostAiAgentsBodyExtractBasicText",
    "PostAiAgentsBodyExtractLongText",
    "PostAiAgentsBodyTextGenBasicGen",
    "PostAiExtractStructuredBodyFieldsItem",
    "PostFilesIdBodyParent",
    "PostFoldersBodyFolderUploadEmail",
    "PostFoldersIdBodyParent",
    "PostIntegrationMappingsTeamsBodyBoxItem",
    "PostIntegrationMappingsTeamsBodyPartnerItem",
    "PostMetadataQueriesExecuteReadBodyOrderByItem",
    "PostMetadataTemplatesSchemaBodyFieldsItem",
    "PostMetadataTemplatesSchemaClassificationsBodyFieldsItem",
    "PostRetentionPolicyAssignmentsBodyFilterFieldsItem",
    "PostShieldInformationBarriersBodyEnterprise",
    "PostShieldInformationBarrierSegmentMembersBodyUser",
    "PostWebLinksIdBodyParent",
    "PostWorkflowsIdStartBodyFilesItem",
    "PostZipDownloadsBodyItemsItem",
    "PutFilesIdBodyCollectionsItem",
    "PutFilesIdBodyParent",
    "PutFilesIdBodySharedLink",
    "PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoBodyItem",
    "PutFilesIdMetadataGlobalBoxSkillsCardsBodyItem",
    "PutFilesIdMetadataIdIdBodyItem",
    "PutFoldersIdBodyCollectionsItem",
    "PutFoldersIdBodyFolderUploadEmail",
    "PutFoldersIdBodyParent",
    "PutFoldersIdBodySharedLink",
    "PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoBodyItem",
    "PutFoldersIdMetadataIdIdBodyItem",
    "PutMetadataTemplatesIdIdSchemaBodyItem",
    "PutWebLinksIdBodyParent",
    "SignRequestCreateRequest",
    "SkillCard",
    "TrackingCode",
    "UploadPart",
    "UserBase",
]

# ============================================================================
# Request Models
# ============================================================================

# Operation: get_file
class GetFilesIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to retrieve. The file ID can be found in the Box web app URL when viewing the file.")
class GetFilesIdRequestHeader(StrictModel):
    boxapi: str | None = Field(default=None, description="A shared link URL and optional password used to access files that have not been explicitly shared with the authenticated user. Use the format `shared_link=[link]` or `shared_link=[link]&shared_link_password=[password]` for password-protected links.")
class GetFilesIdRequest(StrictModel):
    """Retrieves metadata and details for a specific file by its unique identifier. Optionally supports accessing files via a shared link, including password-protected ones."""
    path: GetFilesIdRequestPath
    header: GetFilesIdRequestHeader | None = None

# Operation: restore_file
class PostFilesIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to restore from the trash. The file ID can be found in the Box web app URL when viewing the file.")
class PostFilesIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="An optional new name to assign to the file upon restoration, useful if a naming conflict exists in the destination folder.")
    parent: PostFilesIdBodyParent | None = Field(default=None, description="An optional parent folder object specifying where the file should be restored to, used when the original parent folder has been deleted.")
class PostFilesIdRequest(StrictModel):
    """Restores a file from the trash back to its original location or a specified parent folder. An optional new parent folder can be provided if the original folder no longer exists."""
    path: PostFilesIdRequestPath
    body: PostFilesIdRequestBody | None = None

# Operation: update_file
class PutFilesIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to update. Find this ID in the Box web app by opening the file and copying the numeric ID from the URL.")
class PutFilesIdRequestBodyLock(StrictModel):
    access: Literal["lock"] | None = Field(default=None, validation_alias="access", serialization_alias="access", description="The type of lock to apply to the file. Must be set to 'lock' to lock the file and restrict editing by other users.")
    expires_at: str | None = Field(default=None, validation_alias="expires_at", serialization_alias="expires_at", description="The date and time at which the file lock automatically expires, in ISO 8601 format.", json_schema_extra={'format': 'date-time'})
    is_download_prevented: bool | None = Field(default=None, validation_alias="is_download_prevented", serialization_alias="is_download_prevented", description="Whether downloading the file is prevented while the lock is active. Set to true to block downloads during the lock period.")
class PutFilesIdRequestBodyPermissions(StrictModel):
    can_download: Literal["open", "company"] | None = Field(default=None, validation_alias="can_download", serialization_alias="can_download", description="Controls who can download the file: 'open' allows anyone with access, while 'company' restricts downloads to members of the owner's enterprise, overriding collaboration role permissions.")
class PutFilesIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A new name for the file. Must be unique within the parent folder; the uniqueness check is case-insensitive.")
    description: str | None = Field(default=None, description="A text description for the file, visible in the Box web app sidebar and included in search indexing. Maximum 256 characters.", max_length=256)
    parent: PutFilesIdBodyParent | None = Field(default=None, description="The parent folder to move the file into. Provide an object with the target folder's ID to relocate the file.")
    shared_link: PutFilesIdBodySharedLink | None = Field(default=None, description="Shared link settings for the file. Provide an object with access level and permission options to create or update the file's shared link.")
    disposition_at: str | None = Field(default=None, description="The retention expiration timestamp for the file in ISO 8601 format. Once set, this date can only be extended, never shortened.", json_schema_extra={'format': 'date-time'})
    collections_: list[PutFilesIdBodyCollectionsItem] | None = Field(default=None, validation_alias="collections", serialization_alias="collections", description="An array of collection objects (each with an 'id') to assign the file to. Currently only the favorites collection is supported. Pass an empty array or null to remove the file from all collections.")
    tags: list[str] | None = Field(default=None, description="An array of string tags to associate with the file, visible in the Box web and mobile apps. To modify tags, retrieve the current list, apply changes, and submit the full updated array. Maximum 100 tags per item, each tag between 1 and 100 characters.", min_length=1, max_length=100)
    lock: PutFilesIdRequestBodyLock | None = None
    permissions: PutFilesIdRequestBodyPermissions | None = None
class PutFilesIdRequest(StrictModel):
    """Updates a file's metadata or settings, including renaming, moving to a new parent folder, managing shared links, applying locks, updating tags, and modifying collection membership."""
    path: PutFilesIdRequestPath
    body: PutFilesIdRequestBody | None = None

# Operation: delete_file
class DeleteFilesIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to delete. Visible in the file's URL on the Box web application.")
class DeleteFilesIdRequest(StrictModel):
    """Deletes a specified file from Box, either permanently or by moving it to the trash depending on enterprise settings."""
    path: DeleteFilesIdRequestPath

# Operation: list_file_app_item_associations
class GetFilesIdAppItemAssociationsRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose app item associations should be retrieved. The file ID appears in the Box web app URL when viewing the file.")
class GetFilesIdAppItemAssociationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of app item associations to return per page. Must be between 1 and 1000.", json_schema_extra={'format': 'int64'})
    application_type: str | None = Field(default=None, description="Filters results to only include app items belonging to the specified application type. When omitted, associations for all application types are returned.")
class GetFilesIdAppItemAssociationsRequest(StrictModel):
    """Retrieves all app items associated with a file, including associations inherited from ancestor folders. Association type and ID are returned even if the requesting user lacks View permission on the app item."""
    path: GetFilesIdAppItemAssociationsRequestPath
    query: GetFilesIdAppItemAssociationsRequestQuery | None = None

# Operation: download_file
class GetFilesIdContentRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to download. Visible in the Box web app URL when viewing the file.")
class GetFilesIdContentRequestQuery(StrictModel):
    version: str | None = Field(default=None, description="The specific version ID of the file to download. If omitted, the latest version is returned.")
class GetFilesIdContentRequestHeader(StrictModel):
    range_: str | None = Field(default=None, validation_alias="range", serialization_alias="range", description="Specifies a partial byte range of the file to download, using the format bytes={start_byte}-{end_byte}. Useful for resumable downloads or streaming large files.")
    boxapi: str | None = Field(default=None, description="The shared link URL and optional password for accessing a file that has not been explicitly shared with the authenticated user. Use the format shared_link=[link] or shared_link=[link]&shared_link_password=[password] for password-protected links.")
class GetFilesIdContentRequest(StrictModel):
    """Downloads the binary content of a file from Box. Supports partial downloads via byte ranges, specific version retrieval, and access to shared link items."""
    path: GetFilesIdContentRequestPath
    query: GetFilesIdContentRequestQuery | None = None
    header: GetFilesIdContentRequestHeader | None = None

# Operation: upload_file_version
class PostFilesIdContentRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to update. Visible in the Box web app URL when viewing the file.")
class PostFilesIdContentRequestBodyAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="An optional new name to rename the file when this new version is uploaded. If omitted, the existing file name is retained.")
    content_modified_at: str | None = Field(default=None, validation_alias="content_modified_at", serialization_alias="content_modified_at", description="The date and time the file content was last modified, in ISO 8601 format. If omitted, the time of upload is used as the modification time.", json_schema_extra={'format': 'date-time'})
class PostFilesIdContentRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="The binary content of the file to upload. This part must appear after the attributes part in the multipart request body; reversing the order will result in a 400 error.", json_schema_extra={'format': 'binary'})
    attributes: PostFilesIdContentRequestBodyAttributes | None = None
class PostFilesIdContentRequest(StrictModel):
    """Uploads a new version of an existing file's content, optionally renaming it or setting a custom last-modified timestamp. For files over 50MB, use the Chunk Upload APIs instead."""
    path: PostFilesIdContentRequestPath
    body: PostFilesIdContentRequestBody | None = None

# Operation: upload_file
class PostFilesContentRequestBodyAttributesParent(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The ID of the parent folder where the file will be uploaded. Use `0` to upload to the user's root folder.")
class PostFilesContentRequestBodyAttributes(StrictModel):
    name: str | None = Field(default=None, validation_alias="name", serialization_alias="name", description="The name to assign to the uploaded file. Must be unique (case-insensitive) within the destination folder.")
    content_created_at: str | None = Field(default=None, validation_alias="content_created_at", serialization_alias="content_created_at", description="The original creation timestamp of the file in ISO 8601 format. Defaults to the upload time if not provided.", json_schema_extra={'format': 'date-time'})
    content_modified_at: str | None = Field(default=None, validation_alias="content_modified_at", serialization_alias="content_modified_at", description="The last modified timestamp of the file in ISO 8601 format. Defaults to the upload time if not provided.", json_schema_extra={'format': 'date-time'})
    parent: PostFilesContentRequestBodyAttributesParent | None = None
class PostFilesContentRequestBody(StrictModel):
    file_: str | None = Field(default=None, validation_alias="file", serialization_alias="file", description="The binary content of the file to upload. Must appear after the attributes part in the multipart request body.", json_schema_extra={'format': 'binary'})
    attributes: PostFilesContentRequestBodyAttributes | None = None
class PostFilesContentRequest(StrictModel):
    """Uploads a small file (under 50MB) to a specified Box folder. The attributes must be sent before the file content in the request body, or a 400 error will be returned."""
    body: PostFilesContentRequestBody | None = None

# Operation: create_upload_session
class PostFilesUploadSessionsRequestBody(StrictModel):
    folder_id: str | None = Field(default=None, description="The ID of the destination folder where the new file will be stored upon upload completion.")
    file_name: str | None = Field(default=None, description="The name to assign to the new file once the upload session is complete.")
class PostFilesUploadSessionsRequest(StrictModel):
    """Initiates a chunked upload session for uploading a new file, returning a session ID and upload URLs to use for subsequent chunk uploads."""
    body: PostFilesUploadSessionsRequestBody | None = None

# Operation: create_file_upload_session
class PostFilesIdUploadSessionsRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the existing file for which the upload session will be created. The file ID can be found in the file's URL in the Box web application.")
class PostFilesIdUploadSessionsRequestBody(StrictModel):
    file_name: str | None = Field(default=None, description="An optional new name to assign to the file upon completing the upload session, replacing the current file name.")
class PostFilesIdUploadSessionsRequest(StrictModel):
    """Creates a chunked upload session for an existing file, enabling large file uploads to be split into multiple parts. Use the returned session to upload individual chunks and complete the upload."""
    path: PostFilesIdUploadSessionsRequestPath
    body: PostFilesIdUploadSessionsRequestBody | None = None

# Operation: get_upload_session
class GetFilesUploadSessionsIdRequestPath(StrictModel):
    upload_session_id: str = Field(default=..., description="The unique identifier of the upload session to retrieve, obtained when the upload session was created.")
class GetFilesUploadSessionsIdRequest(StrictModel):
    """Retrieve the current status and details of an active chunked file upload session. The upload session ID is obtained from the Create upload session endpoint."""
    path: GetFilesUploadSessionsIdRequestPath

# Operation: upload_file_part
class PutFilesUploadSessionsIdRequestPath(StrictModel):
    upload_session_id: str = Field(default=..., description="The unique identifier of the upload session to which this file part belongs.")
class PutFilesUploadSessionsIdRequestHeader(StrictModel):
    digest: str = Field(default=..., description="The RFC 3230 message digest of the uploaded chunk used to verify integrity. Must be a base64-encoded SHA1 hash formatted as `sha=<BASE64_ENCODED_DIGEST>`.")
    content_range: str = Field(default=..., validation_alias="content-range", serialization_alias="content-range", description="The inclusive byte range of this chunk within the full file, formatted as `bytes <start>-<end>/<total>`. The start must be a multiple of the session's part size, the end must be a multiple of the part size minus one, and ranges must not overlap with any previously uploaded part.")
class PutFilesUploadSessionsIdRequestBody(StrictModel):
    body: str | None = Field(default=None, description="The raw binary content of the file chunk being uploaded for this part.", json_schema_extra={'format': 'binary'})
class PutFilesUploadSessionsIdRequest(StrictModel):
    """Uploads a single binary chunk of a file as part of an active chunked upload session. Each part must conform to the byte range and part size defined when the upload session was created."""
    path: PutFilesUploadSessionsIdRequestPath
    header: PutFilesUploadSessionsIdRequestHeader
    body: PutFilesUploadSessionsIdRequestBody | None = None

# Operation: abort_upload_session
class DeleteFilesUploadSessionsIdRequestPath(StrictModel):
    upload_session_id: str = Field(default=..., description="The unique identifier of the upload session to abort, as returned by the Create or Get upload session endpoints.")
class DeleteFilesUploadSessionsIdRequest(StrictModel):
    """Permanently aborts an active upload session and discards all uploaded data. This action is irreversible and cannot be undone."""
    path: DeleteFilesUploadSessionsIdRequestPath

# Operation: list_upload_session_parts
class GetFilesUploadSessionsIdPartsRequestPath(StrictModel):
    upload_session_id: str = Field(default=..., description="The unique identifier of the upload session whose uploaded parts you want to list.")
class GetFilesUploadSessionsIdPartsRequestQuery(StrictModel):
    offset: int | None = Field(default=None, description="The zero-based index of the first item to return, enabling pagination through large result sets. Must not exceed 10000; requests beyond this limit will be rejected with a 400 error.", json_schema_extra={'format': 'int64'})
    limit: int | None = Field(default=None, description="The maximum number of uploaded parts to return in a single response. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetFilesUploadSessionsIdPartsRequest(StrictModel):
    """Retrieves a paginated list of all file chunks uploaded so far within a specific upload session, allowing you to track multipart upload progress."""
    path: GetFilesUploadSessionsIdPartsRequestPath
    query: GetFilesUploadSessionsIdPartsRequestQuery | None = None

# Operation: commit_upload_session
class PostFilesUploadSessionsIdCommitRequestPath(StrictModel):
    upload_session_id: str = Field(default=..., description="The unique identifier of the upload session to commit.")
class PostFilesUploadSessionsIdCommitRequestHeader(StrictModel):
    digest: str = Field(default=..., description="The RFC 3230 message digest of the entire file used to verify integrity. Must be a Base64-encoded SHA1 hash formatted as `sha=<BASE64_ENCODED_DIGEST>`.")
class PostFilesUploadSessionsIdCommitRequestBody(StrictModel):
    parts: list[UploadPart] | None = Field(default=None, description="An ordered list of part details representing all uploaded chunks that should be assembled into the final file. Each item should describe a previously uploaded part.")
class PostFilesUploadSessionsIdCommitRequest(StrictModel):
    """Finalizes an upload session by assembling all uploaded chunks into a complete file. Must be called after all parts have been uploaded to close the session and persist the file."""
    path: PostFilesUploadSessionsIdCommitRequestPath
    header: PostFilesUploadSessionsIdCommitRequestHeader
    body: PostFilesUploadSessionsIdCommitRequestBody | None = None

# Operation: copy_file
class PostFilesIdCopyRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to copy. Visible in the Box web app URL when viewing the file.")
class PostFilesIdCopyRequestBodyParent(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The ID of the destination folder where the copied file will be placed. Use '0' to copy the file to the root folder.")
class PostFilesIdCopyRequestBody(StrictModel):
    name: str | None = Field(default=None, description="An optional new name for the copied file. Must not exceed 255 characters; non-printable ASCII characters, forward/backward slashes, and reserved names like '.' and '..' are automatically sanitized.", max_length=255)
    version: str | None = Field(default=None, description="The ID of a specific file version to copy. If omitted, the latest version of the file is copied.")
    parent: PostFilesIdCopyRequestBodyParent | None = None
class PostFilesIdCopyRequest(StrictModel):
    """Creates a copy of an existing file, optionally placing it in a different folder, renaming it, or copying a specific version. Returns the metadata of the newly created file copy."""
    path: PostFilesIdCopyRequestPath
    body: PostFilesIdCopyRequestBody | None = None

# Operation: get_file_thumbnail
class GetFilesIdThumbnailIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file for which to retrieve a thumbnail. The file ID can be found in the URL when viewing the file in the Box web application.")
    extension: Literal["png", "jpg"] = Field(default=..., description="The image format for the thumbnail. PNG supports sizes up to 256x256; JPG supports sizes up to 320x320.")
class GetFilesIdThumbnailIdRequestQuery(StrictModel):
    min_height: int | None = Field(default=None, description="The minimum desired height of the thumbnail in pixels. The returned thumbnail will be at least this tall, within the supported size range of 32 to 320 pixels.", ge=32, le=320)
    min_width: int | None = Field(default=None, description="The minimum desired width of the thumbnail in pixels. The returned thumbnail will be at least this wide, within the supported size range of 32 to 320 pixels.", ge=32, le=320)
    max_height: int | None = Field(default=None, description="The maximum desired height of the thumbnail in pixels. The returned thumbnail will not exceed this height, within the supported size range of 32 to 320 pixels.", ge=32, le=320)
    max_width: int | None = Field(default=None, description="The maximum desired width of the thumbnail in pixels. The returned thumbnail will not exceed this width, within the supported size range of 32 to 320 pixels.", ge=32, le=320)
class GetFilesIdThumbnailIdRequest(StrictModel):
    """Retrieves a scaled-down thumbnail image of a file in PNG or JPG format. Supports various sizes for image and video file types."""
    path: GetFilesIdThumbnailIdRequestPath
    query: GetFilesIdThumbnailIdRequestQuery | None = None

# Operation: list_file_collaborations
class GetFilesIdCollaborationsRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose collaborations you want to retrieve. You can find this ID in the file's URL in the Box web application.")
class GetFilesIdCollaborationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of collaboration records to return per page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetFilesIdCollaborationsRequest(StrictModel):
    """Retrieves all pending and active collaborations for a specific file, including users who currently have access or have been invited to collaborate."""
    path: GetFilesIdCollaborationsRequestPath
    query: GetFilesIdCollaborationsRequestQuery | None = None

# Operation: list_file_comments
class GetFilesIdCommentsRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose comments you want to retrieve. Find this ID in the file's URL on the Box web application.")
class GetFilesIdCommentsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of comments to return per page. Must be between 1 and 1000.", json_schema_extra={'format': 'int64'})
    offset: int | None = Field(default=None, description="The zero-based index of the first item to include in the response, used for paginating through results. Offset values exceeding 10000 are not supported.", json_schema_extra={'format': 'int64'})
class GetFilesIdCommentsRequest(StrictModel):
    """Retrieves a paginated list of comments posted on a specific file. Useful for reviewing user feedback or discussion threads associated with a file."""
    path: GetFilesIdCommentsRequestPath
    query: GetFilesIdCommentsRequestQuery | None = None

# Operation: list_file_tasks
class GetFilesIdTasksRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose tasks you want to retrieve. You can find this ID in the file's URL in the Box web application.")
class GetFilesIdTasksRequest(StrictModel):
    """Retrieves all tasks associated with a specific file, returning the complete list in a single response. Note that this endpoint does not support pagination."""
    path: GetFilesIdTasksRequestPath

# Operation: get_trashed_file
class GetFilesIdTrashRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to retrieve from the trash. The file ID appears in the Box web app URL when viewing the file.")
class GetFilesIdTrashRequest(StrictModel):
    """Retrieves metadata for a file that was directly moved to the trash. Note: if a parent folder was trashed instead, use the trashed folder endpoint to inspect it."""
    path: GetFilesIdTrashRequestPath

# Operation: permanently_delete_trashed_file
class DeleteFilesIdTrashRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the trashed file to permanently delete. The file ID can be found in the URL when viewing the file in the Box web application.")
class DeleteFilesIdTrashRequest(StrictModel):
    """Permanently deletes a file that is currently in the trash, freeing storage and removing it from Box entirely. This action is irreversible and cannot be undone."""
    path: DeleteFilesIdTrashRequestPath

# Operation: list_file_versions
class GetFilesIdVersionsRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose version history you want to retrieve. The file ID can be found in the URL when viewing the file in the Box web application.")
class GetFilesIdVersionsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of file versions to return per page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
    offset: int | None = Field(default=None, description="The zero-based index of the item at which to start the response, used for paginating through results. Offset values exceeding 10000 will result in a 400 error.", json_schema_extra={'format': 'int64'})
class GetFilesIdVersionsRequest(StrictModel):
    """Retrieves the version history of a specific file, returning all past versions in paginated results. Version tracking is available only for Box premium accounts; use the get_file operation to retrieve the current version ID."""
    path: GetFilesIdVersionsRequestPath
    query: GetFilesIdVersionsRequestQuery | None = None

# Operation: get_file_version
class GetFilesIdVersionsIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose version you want to retrieve. Visible in the file's URL in the Box web application.")
    file_version_id: str = Field(default=..., description="The unique identifier of the specific file version to retrieve.")
class GetFilesIdVersionsIdRequest(StrictModel):
    """Retrieves metadata for a specific version of a file by its version ID. Version history is only available for Box accounts with premium subscriptions."""
    path: GetFilesIdVersionsIdRequestPath

# Operation: restore_file_version
class PutFilesIdVersionsIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose version you want to restore. Visible in the file's URL in the Box web application.")
    file_version_id: str = Field(default=..., description="The unique identifier of the specific file version to restore.")
class PutFilesIdVersionsIdRequest(StrictModel):
    """Restores a previously deleted version of a file, making it the current version. Supports standard file formats such as PDF, DOC, and PPTX, but not Box Notes."""
    path: PutFilesIdVersionsIdRequestPath

# Operation: delete_file_version
class DeleteFilesIdVersionsIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose version will be deleted. The file ID can be found in the URL when viewing the file in the Box web application.")
    file_version_id: str = Field(default=..., description="The unique identifier of the specific file version to delete. This targets a single version entry within the file's version history.")
class DeleteFilesIdVersionsIdRequest(StrictModel):
    """Moves a specific version of a file to the trash, effectively removing it from the version history. Version tracking is only available for Box accounts with premium subscriptions."""
    path: DeleteFilesIdVersionsIdRequestPath

# Operation: promote_file_version
class PostFilesIdVersionsCurrentRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose version you want to promote. Visible in the file's URL in the Box web application.")
class PostFilesIdVersionsCurrentRequestBody(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the specific file version to promote to the top of the version history.")
    type_: Literal["file_version"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The resource type being promoted. Must be set to 'file_version' to indicate a file version promotion.")
class PostFilesIdVersionsCurrentRequest(StrictModel):
    """Promotes an older version of a file to the top of its version history by creating a new copy with the same contents, hash, etag, and name. Suitable for file formats like PDF, DOC, and PPTX, but not for Box Notes."""
    path: PostFilesIdVersionsCurrentRequestPath
    body: PostFilesIdVersionsCurrentRequestBody | None = None

# Operation: list_file_metadata
class GetFilesIdMetadataRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose metadata instances will be retrieved. The file ID can be found in the URL when viewing the file in the Box web application.")
class GetFilesIdMetadataRequestQuery(StrictModel):
    view: str | None = Field(default=None, description="Controls how taxonomy field values are represented in the response. When set to 'hydrated', taxonomy values include full taxonomy node details rather than just node identifiers.")
class GetFilesIdMetadataRequest(StrictModel):
    """Retrieves all metadata instances attached to a specific file. Optionally returns full taxonomy node details instead of node identifiers."""
    path: GetFilesIdMetadataRequestPath
    query: GetFilesIdMetadataRequestQuery | None = None

# Operation: get_file_classification
class GetFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose security classification you want to retrieve. Visible in the file's Box web URL after '/files/'.")
class GetFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(StrictModel):
    """Retrieves the security classification metadata applied to a specific file. Returns the classification instance associated with the file's enterprise security policy."""
    path: GetFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath

# Operation: add_file_classification
class PostFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to classify. The file ID can be found in the file's URL in the Box web application.")
class PostFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody(StrictModel):
    box__security__classification__key: str | None = Field(default=None, validation_alias="Box__Security__Classification__Key", serialization_alias="Box__Security__Classification__Key", description="The classification label to apply to the file. Must match one of the available classification keys defined in the enterprise's classification template; retrieve valid keys from the classification template endpoint.")
class PostFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(StrictModel):
    """Adds a security classification label to a file in Box. Use this to apply an enterprise-defined classification (e.g., Confidential, Sensitive) to control how the file is handled and shared."""
    path: PostFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath
    body: PostFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody | None = None

# Operation: update_file_classification
class PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose classification will be updated. The file ID can be found in the file's URL in the Box web application.")
class PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody(StrictModel):
    body: list[PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoBodyItem] | None = Field(default=None, description="A list containing exactly one change operation object that specifies the update to apply to the classification label. Order is significant; only a single item describing the classification change should be included.")
class PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(StrictModel):
    """Updates the security classification label on a file that already has a classification applied. Only classification values defined for the enterprise are accepted."""
    path: PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath
    body: PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody | None = None

# Operation: remove_file_classification
class DeleteFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file from which the classification will be removed. The file ID can be found in the URL when viewing the file in the Box web application.")
class DeleteFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(StrictModel):
    """Removes any existing security classification from a specified file. This permanently strips the classification metadata, and can also be called using an explicit enterprise ID in the endpoint path."""
    path: DeleteFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath

# Operation: get_file_metadata_instance
class GetFilesIdMetadataIdIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose metadata instance you want to retrieve. Find this ID in the file's URL in the Box web application.")
    scope: Literal["global", "enterprise"] = Field(default=..., description="The scope of the metadata template to retrieve, either globally available templates or templates specific to your enterprise.")
    template_key: str = Field(default=..., description="The unique key name of the metadata template whose instance you want to retrieve from the file.")
class GetFilesIdMetadataIdIdRequestQuery(StrictModel):
    view: str | None = Field(default=None, description="Controls how taxonomy field values are represented in the response. Set to 'hydrated' to receive full taxonomy node details instead of the default node identifiers.")
class GetFilesIdMetadataIdIdRequest(StrictModel):
    """Retrieves a specific metadata template instance applied to a file, identified by its scope and template key. Optionally returns full taxonomy node details instead of raw node identifiers."""
    path: GetFilesIdMetadataIdIdRequestPath
    query: GetFilesIdMetadataIdIdRequestQuery | None = None

# Operation: create_file_metadata
class PostFilesIdMetadataIdIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to which the metadata instance will be applied. Visible in the file's URL in the Box web application.")
    scope: Literal["global", "enterprise"] = Field(default=..., description="The scope of the metadata template to apply, either global (Box-provided templates) or enterprise (custom templates defined by your organization).")
    template_key: str = Field(default=..., description="The unique key identifying the metadata template within the given scope, corresponding to the template's defined name.")
class PostFilesIdMetadataIdIdRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="A JSON object containing the metadata field key-value pairs to populate on the template instance. Keys must match those defined in the template, unless using the global.properties template.")
class PostFilesIdMetadataIdIdRequest(StrictModel):
    """Applies an instance of a metadata template to a file, associating structured key-value data with it. Only keys defined in the specified template are accepted, except for the global.properties template which allows arbitrary key-value pairs."""
    path: PostFilesIdMetadataIdIdRequestPath
    body: PostFilesIdMetadataIdIdRequestBody | None = None

# Operation: update_file_metadata
class PutFilesIdMetadataIdIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose metadata instance will be updated. Visible in the file's URL in the Box web application.")
    scope: Literal["global", "enterprise"] = Field(default=..., description="The scope of the metadata template to update, either globally defined templates or enterprise-specific ones.")
    template_key: str = Field(default=..., description="The unique key identifying the metadata template whose instance will be updated on the file.")
class PutFilesIdMetadataIdIdRequestBody(StrictModel):
    body: list[PutFilesIdMetadataIdIdBodyItem] | None = Field(default=None, description="An ordered array of JSON Patch operation objects describing the changes to apply to the metadata instance. Operations are applied in sequence and must conform to RFC 6902 JSON Patch syntax.")
class PutFilesIdMetadataIdIdRequest(StrictModel):
    """Updates an existing metadata instance on a file using JSON Patch operations. The metadata template must already be applied to the file, and all changes are applied atomically — if any operation fails, no changes are made."""
    path: PutFilesIdMetadataIdIdRequestPath
    body: PutFilesIdMetadataIdIdRequestBody | None = None

# Operation: delete_file_metadata
class DeleteFilesIdMetadataIdIdRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file from which metadata will be removed. The file ID can be found in the URL when viewing the file in the Box web application.")
    scope: Literal["global", "enterprise"] = Field(default=..., description="The scope of the metadata template to delete, either 'global' for Box-wide templates or 'enterprise' for templates specific to your organization.")
    template_key: str = Field(default=..., description="The unique key identifying the metadata template to remove from the file, corresponding to the template's defined key within the specified scope.")
class DeleteFilesIdMetadataIdIdRequest(StrictModel):
    """Removes a specific metadata instance from a file by deleting the metadata template applied under the given scope. This permanently detaches the metadata from the file without affecting the file itself."""
    path: DeleteFilesIdMetadataIdIdRequestPath

# Operation: list_file_skills_cards
class GetFilesIdMetadataGlobalBoxSkillsCardsRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose Box Skills cards you want to retrieve. Visible in the file's URL on the Box web application.")
class GetFilesIdMetadataGlobalBoxSkillsCardsRequest(StrictModel):
    """Retrieves all Box Skills metadata cards attached to a specific file. Useful for inspecting AI-generated insights such as transcripts, topics, or keywords extracted by Box Skills."""
    path: GetFilesIdMetadataGlobalBoxSkillsCardsRequestPath

# Operation: create_skill_cards
class PostFilesIdMetadataGlobalBoxSkillsCardsRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to which Box Skill cards will be applied. The file ID can be found in the URL when viewing the file in the Box web application.")
class PostFilesIdMetadataGlobalBoxSkillsCardsRequestBody(StrictModel):
    cards: list[SkillCard] | None = Field(default=None, description="An array of Box Skill card objects to attach to the file. Each item should represent a valid skill card type (e.g., keyword, transcript, timeline, or status card); order is not significant.")
class PostFilesIdMetadataGlobalBoxSkillsCardsRequest(StrictModel):
    """Applies one or more Box Skills metadata cards to a specified file, enabling AI-generated insights such as transcripts, topics, or keywords to be attached as structured metadata."""
    path: PostFilesIdMetadataGlobalBoxSkillsCardsRequestPath
    body: PostFilesIdMetadataGlobalBoxSkillsCardsRequestBody | None = None

# Operation: update_skill_cards
class PutFilesIdMetadataGlobalBoxSkillsCardsRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose Box Skills metadata cards will be updated. Visible in the file's URL on the Box web application.")
class PutFilesIdMetadataGlobalBoxSkillsCardsRequestBody(StrictModel):
    body: list[PutFilesIdMetadataGlobalBoxSkillsCardsBodyItem] | None = Field(default=None, description="An array of JSON-Patch operation objects describing the changes to apply to the Box Skills metadata cards. Each object follows the RFC 6902 JSON-Patch specification, with order of operations being significant.")
class PutFilesIdMetadataGlobalBoxSkillsCardsRequest(StrictModel):
    """Updates one or more Box Skills metadata cards on a specified file using JSON-Patch operations, allowing targeted modifications to existing skill card data."""
    path: PutFilesIdMetadataGlobalBoxSkillsCardsRequestPath
    body: PutFilesIdMetadataGlobalBoxSkillsCardsRequestBody | None = None

# Operation: remove_file_skills_cards
class DeleteFilesIdMetadataGlobalBoxSkillsCardsRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file from which Box Skills cards will be removed. The file ID can be found in the file's URL in the Box web application.")
class DeleteFilesIdMetadataGlobalBoxSkillsCardsRequest(StrictModel):
    """Removes all Box Skills cards metadata from a specified file. This clears any AI-generated skill annotations (such as transcripts, topics, or faces) associated with the file."""
    path: DeleteFilesIdMetadataGlobalBoxSkillsCardsRequestPath

# Operation: get_file_watermark
class GetFilesIdWatermarkRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose watermark you want to retrieve. Visible in the file's URL on the Box web application.")
class GetFilesIdWatermarkRequest(StrictModel):
    """Retrieves the watermark applied to a specific file. Returns watermark details if one exists, or an error if no watermark has been applied."""
    path: GetFilesIdWatermarkRequestPath

# Operation: apply_file_watermark
class PutFilesIdWatermarkRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to watermark. Found in the file's URL in the Box web application.")
class PutFilesIdWatermarkRequestBodyWatermark(StrictModel):
    imprint: Literal["default"] | None = Field(default=None, validation_alias="imprint", serialization_alias="imprint", description="The type of watermark to apply to the file. Currently only the default imprint style is supported.")
class PutFilesIdWatermarkRequestBody(StrictModel):
    watermark: PutFilesIdWatermarkRequestBodyWatermark | None = None
class PutFilesIdWatermarkRequest(StrictModel):
    """Applies or updates a watermark on a specified file in Box. Use this to protect file content by overlaying a visible watermark when the file is viewed or downloaded."""
    path: PutFilesIdWatermarkRequestPath
    body: PutFilesIdWatermarkRequestBody | None = None

# Operation: remove_file_watermark
class DeleteFilesIdWatermarkRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file from which the watermark will be removed. Found in the file's URL in the Box web application.")
class DeleteFilesIdWatermarkRequest(StrictModel):
    """Removes an existing watermark from a specified file in Box. Use this to revoke watermark protection previously applied to a file."""
    path: DeleteFilesIdWatermarkRequestPath

# Operation: get_file_request
class GetFileRequestsIdRequestPath(StrictModel):
    file_request_id: str = Field(default=..., description="The unique identifier of the file request to retrieve. This ID can be found in the URL of the file request builder in the Box web application.")
class GetFileRequestsIdRequest(StrictModel):
    """Retrieves detailed information about a specific file request, including its configuration and status. Use this to inspect an existing file request created via the Box web application."""
    path: GetFileRequestsIdRequestPath

# Operation: update_file_request
class PutFileRequestsIdRequestPath(StrictModel):
    file_request_id: str = Field(default=..., description="The unique identifier of the file request to update. Find this ID in the URL of the file request builder in the Box web application.")
class PutFileRequestsIdRequestBody(StrictModel):
    title: str | None = Field(default=None, description="The new title for the file request. If omitted, the existing title is preserved.")
    description: str | None = Field(default=None, description="The new description for the file request, displayed to submitters on the form. If omitted, the existing description is preserved.")
    status: Literal["active", "inactive"] | None = Field(default=None, description="The new status of the file request. Setting to 'inactive' stops accepting submissions and returns HTTP 404 to visitors; 'active' resumes acceptance. If omitted, the existing status is preserved.")
    is_email_required: bool | None = Field(default=None, description="Whether submitters must provide their email address on the file request form. If omitted, the existing setting is preserved.")
    is_description_required: bool | None = Field(default=None, description="Whether submitters must provide a description of the files they are uploading on the file request form. If omitted, the existing setting is preserved.")
    expires_at: str | None = Field(default=None, description="The expiration date and time after which the file request will no longer accept submissions and its status will automatically become inactive. Provide as an ISO 8601 date-time string. If omitted, the existing expiration is preserved.", json_schema_extra={'format': 'date-time'})
class PutFileRequestsIdRequest(StrictModel):
    """Updates the properties of an existing file request, such as its title, description, status, and submission requirements. Use this to activate or deactivate a file request or modify its configuration."""
    path: PutFileRequestsIdRequestPath
    body: PutFileRequestsIdRequestBody | None = None

# Operation: delete_file_request
class DeleteFileRequestsIdRequestPath(StrictModel):
    file_request_id: str = Field(default=..., description="The unique identifier of the file request to delete. This ID can be found in the URL of the file request builder in the Box web application.")
class DeleteFileRequestsIdRequest(StrictModel):
    """Permanently deletes a specified file request from Box. This action is irreversible and removes the file request and its associated upload link."""
    path: DeleteFileRequestsIdRequestPath

# Operation: copy_file_request
class PostFileRequestsIdCopyRequestPath(StrictModel):
    file_request_id: str = Field(default=..., description="The unique identifier of the file request to copy. Find this ID in the URL when viewing a file request in the Box web application's file request builder.")
class PostFileRequestsIdCopyRequestBody(StrictModel):
    body: FileRequestCopyRequest | None = Field(default=None, description="The request body specifying the destination folder and any overrides to apply to the copied file request, such as a new title or description.")
class PostFileRequestsIdCopyRequest(StrictModel):
    """Copies an existing file request from one folder and applies it to another folder, duplicating its settings and configuration. Useful for reusing file request templates across multiple folders without manual recreation."""
    path: PostFileRequestsIdCopyRequestPath
    body: PostFileRequestsIdCopyRequestBody | None = None

# Operation: get_folder
class GetFoldersIdRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder to retrieve. The root folder of any Box account is always ID '0'; other folder IDs can be found in the URL when viewing the folder in the Box web app.")
class GetFoldersIdRequestQuery(StrictModel):
    sort: Literal["id", "name", "date", "size"] | None = Field(default=None, description="The secondary attribute by which folder items are sorted. Items are always grouped by type first (folders, then files, then web links); this parameter controls ordering within those groups. Not supported for marker-based pagination on the root folder.")
    direction: Literal["ASC", "DESC"] | None = Field(default=None, description="The sort order for returned items, either ascending (ASC) or descending (DESC) alphabetically.")
    offset: int | None = Field(default=None, description="The zero-based index of the first item to include in the response, used for offset-based pagination. Note that very high offset values may be unreliable for large folders; consider restructuring large folders if pagination fails.", json_schema_extra={'format': 'int64'})
    limit: int | None = Field(default=None, description="The maximum number of folder items to return in a single response, up to a maximum of 1000.", json_schema_extra={'format': 'int64'})
class GetFoldersIdRequest(StrictModel):
    """Retrieves metadata and the first 100 items for a specified folder. Use the sort, direction, offset, and limit parameters to control item ordering and pagination within the folder."""
    path: GetFoldersIdRequestPath
    query: GetFoldersIdRequestQuery | None = None

# Operation: restore_folder
class PostFoldersIdRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder to restore from trash. The folder ID can be found in the Box web app URL when viewing the folder.")
class PostFoldersIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="An optional new name to assign to the folder upon restoration, useful if a naming conflict exists at the destination.")
    parent: PostFoldersIdBodyParent | None = Field(default=None, description="An optional parent folder object specifying where the folder should be restored to, used when the original parent folder no longer exists.")
class PostFoldersIdRequest(StrictModel):
    """Restores a folder from the trash to its original location or an optional new parent folder. During the operation, the source folder, its descendants, and the destination folder are locked to prevent concurrent move, copy, delete, or restore actions."""
    path: PostFoldersIdRequestPath
    body: PostFoldersIdRequestBody | None = None

# Operation: update_folder
class PutFoldersIdRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder to update. Find this ID in the Box web app URL when viewing the folder. The root folder of any Box account always has the ID `0`.")
class PutFoldersIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name for the folder. Names must be unique within the parent folder (case-insensitive) and cannot contain non-printable ASCII characters, forward or backward slashes, trailing spaces, or be `.` or `..`.")
    description: str | None = Field(default=None, description="An optional human-readable description for the folder, up to 256 characters.", max_length=256)
    sync_state: Literal["synced", "not_synced", "partially_synced"] | None = Field(default=None, description="Controls whether the folder is synced to a user's device. Applicable only to Box Sync (discontinued); not used by Box Drive.")
    can_non_owners_invite: bool | None = Field(default=None, description="When set to `true`, users who are not the folder owner are allowed to invite new collaborators. When `false`, only the owner can invite collaborators.")
    parent: PutFoldersIdBodyParent | None = Field(default=None, description="The parent folder to move this folder into. Provide an object with the `id` of the destination parent folder to relocate the folder.")
    shared_link: PutFoldersIdBodySharedLink | None = Field(default=None, description="Shared link settings for the folder. Provide a shared link object to create or update the shared link, or set to `null` to remove it.")
    folder_upload_email: PutFoldersIdBodyFolderUploadEmail | None = Field(default=None, description="The email address configuration that allows files to be uploaded to this folder by sending an email. Provide an object with the desired access level, or set to `null` to disable.")
    tags: list[str] | None = Field(default=None, description="A list of tags to associate with the folder, visible in the Box web and mobile apps. To modify tags, retrieve the current list, apply changes, and submit the full updated list. Maximum of 100 tags per item.", min_length=1, max_length=100)
    is_collaboration_restricted_to_enterprise: bool | None = Field(default=None, description="When set to `true`, new collaboration invitations for this folder are restricted to users within the same enterprise. Existing collaborations are not affected.")
    collections_: list[PutFoldersIdBodyCollectionsItem] | None = Field(default=None, validation_alias="collections", serialization_alias="collections", description="A list of collection objects to add this folder to. Currently only the `favorites` collection is supported. Pass an empty array or `null` to remove the folder from all collections. Retrieve collection IDs using the List all collections endpoint.")
    can_non_owners_view_collaborators: bool | None = Field(default=None, description="When set to `false`, non-owner collaborators are prevented from viewing other collaborators on the folder and from inviting new ones. If setting this to `false`, `can_non_owners_invite` must also be set to `false`.")
class PutFoldersIdRequest(StrictModel):
    """Updates a folder's properties such as name, description, tags, and sharing settings. Can also be used to move the folder to a new parent, manage shared links, and control collaboration permissions."""
    path: PutFoldersIdRequestPath
    body: PutFoldersIdRequestBody | None = None

# Operation: delete_folder
class DeleteFoldersIdRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder to delete. The folder ID can be found in the URL when viewing the folder in the Box web app, and the root folder is always ID `0`.")
class DeleteFoldersIdRequestQuery(StrictModel):
    recursive: bool | None = Field(default=None, description="When set to true, allows deletion of a non-empty folder by recursively deleting all of its contents along with the folder itself. If omitted or false, the request will fail if the folder contains any items.")
class DeleteFoldersIdRequest(StrictModel):
    """Deletes a Box folder either permanently or by moving it to the trash. Supports recursive deletion to remove folders that contain content."""
    path: DeleteFoldersIdRequestPath
    query: DeleteFoldersIdRequestQuery | None = None

# Operation: list_folder_app_item_associations
class GetFoldersIdAppItemAssociationsRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose app item associations you want to retrieve. The folder ID appears in the URL when viewing the folder in the Box web app. The root folder is always ID 0.")
class GetFoldersIdAppItemAssociationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of app item associations to return per page. Must be between 1 and 1000.", json_schema_extra={'format': 'int64'})
    application_type: str | None = Field(default=None, description="Filters results to only include app items belonging to the specified application type. When omitted, associations for all application types are returned.")
class GetFoldersIdAppItemAssociationsRequest(StrictModel):
    """Retrieves all app items associated with a folder, including associations inherited from ancestor folders. App item type and ID are visible to any user with folder access, regardless of View permission on the app item."""
    path: GetFoldersIdAppItemAssociationsRequestPath
    query: GetFoldersIdAppItemAssociationsRequestQuery | None = None

# Operation: list_folder_items
class GetFoldersIdItemsRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose contents you want to list. The root folder of any Box account always uses the ID '0'; for other folders, find the ID in the URL when viewing the folder in the Box web app.")
class GetFoldersIdItemsRequestQuery(StrictModel):
    usemarker: bool | None = Field(default=None, description="Set to true to enable marker-based pagination, which returns a 'marker' token in the response to fetch the next page. Cannot be combined with offset-based pagination; use one method consistently throughout a paginated sequence.")
    offset: int | None = Field(default=None, description="The zero-based index of the first item to include in the response, used for offset-based pagination. Avoid high offset values on large datasets as reliability is not guaranteed; prefer marker-based pagination in those cases.", json_schema_extra={'format': 'int64'})
    limit: int | None = Field(default=None, description="The maximum number of items to return in a single page of results. Accepted values range from 1 to 1000.", json_schema_extra={'format': 'int64'})
    sort: Literal["id", "name", "date", "size"] | None = Field(default=None, description="The secondary attribute by which to sort items within their type grouping — items are always sorted by type first (folders, then files, then web links). Sorting by this field is not supported for marker-based pagination on the root folder (ID '0').")
    direction: Literal["ASC", "DESC"] | None = Field(default=None, description="The sort direction for results, either ascending or descending alphabetical/numerical order.")
class GetFoldersIdItemsRequest(StrictModel):
    """Retrieves a paginated list of files, folders, and web links contained within a specified folder. Use the dedicated Get Folder endpoint if you need metadata about the folder itself, such as its size."""
    path: GetFoldersIdItemsRequestPath
    query: GetFoldersIdItemsRequestQuery | None = None

# Operation: create_folder
class PostFoldersRequestBodyParent(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique ID of the parent folder in which the new folder will be created. Use '0' to create the folder at the root level of the user's account.")
class PostFoldersRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the new folder. Must be between 1 and 255 characters, must not contain non-printable ASCII characters, forward or backward slashes, or trailing spaces, and cannot be '.' or '..'. Names are checked case-insensitively for uniqueness within the parent folder.", min_length=1, max_length=255)
    folder_upload_email: PostFoldersBodyFolderUploadEmail | None = Field(default=None, description="Optional email upload configuration for the folder, allowing files to be uploaded by sending an email to a folder-specific address.")
    sync_state: Literal["synced", "not_synced", "partially_synced"] | None = Field(default=None, description="Specifies the sync state of the folder for Box Sync (discontinued). Accepted values are 'synced' (fully synced), 'not_synced' (not synced), or 'partially_synced' (some contents synced). Not applicable to Box Drive.")
    parent: PostFoldersRequestBodyParent | None = None
class PostFoldersRequest(StrictModel):
    """Creates a new empty folder inside a specified parent folder. The folder name must be unique within the parent (case-insensitive) and must not contain invalid characters or trailing spaces."""
    body: PostFoldersRequestBody | None = None

# Operation: copy_folder
class PostFoldersIdCopyRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder to copy. The folder ID can be found in the Box web app URL when viewing the folder. The root folder (ID '0') cannot be copied.")
class PostFoldersIdCopyRequestBodyParent(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The ID of the destination parent folder where the copied folder will be placed.")
class PostFoldersIdCopyRequestBody(StrictModel):
    name: str | None = Field(default=None, description="An optional name for the copied folder. If omitted, the original folder name is used. Names must be between 1 and 255 characters, cannot contain non-printable ASCII characters, forward or backward slashes, trailing spaces, or be exactly '.' or '..'.", min_length=1, max_length=255)
    parent: PostFoldersIdCopyRequestBodyParent | None = None
class PostFoldersIdCopyRequest(StrictModel):
    """Creates a copy of an existing folder and places it inside a specified destination folder. The original folder and its contents remain unchanged."""
    path: PostFoldersIdCopyRequestPath
    body: PostFoldersIdCopyRequestBody | None = None

# Operation: list_folder_collaborations
class GetFoldersIdCollaborationsRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose collaborations you want to retrieve. Find this ID in the Box web app by opening the folder and copying the numeric ID from the URL.")
class GetFoldersIdCollaborationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of collaboration records to return in a single page of results. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetFoldersIdCollaborationsRequest(StrictModel):
    """Retrieves all active and pending collaborations for a specified folder, returning details on users who currently have access or have been invited to collaborate."""
    path: GetFoldersIdCollaborationsRequestPath
    query: GetFoldersIdCollaborationsRequestQuery | None = None

# Operation: get_trashed_folder
class GetFoldersIdTrashRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the trashed folder to retrieve. Only folders directly moved to the trash are accessible; folders implicitly trashed via a parent cannot be retrieved by their own ID.")
class GetFoldersIdTrashRequest(StrictModel):
    """Retrieves metadata for a specific folder that has been directly moved to the trash. Note: if a parent folder was trashed instead, only that parent folder can be retrieved via this endpoint."""
    path: GetFoldersIdTrashRequestPath

# Operation: permanently_delete_trashed_folder
class DeleteFoldersIdTrashRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder to permanently delete from trash. The folder ID can be found in the URL when viewing the folder in the Box web application.")
class DeleteFoldersIdTrashRequest(StrictModel):
    """Permanently deletes a folder that is currently in the trash, freeing storage and removing it from Box entirely. This action is irreversible and cannot be undone."""
    path: DeleteFoldersIdTrashRequestPath

# Operation: list_folder_metadata
class GetFoldersIdMetadataRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose metadata instances will be retrieved. Find this ID in the Box web app URL when viewing the folder.")
class GetFoldersIdMetadataRequestQuery(StrictModel):
    view: str | None = Field(default=None, description="Controls how taxonomy field values are represented in the response. By default, taxonomy values are returned as node identifiers (API view); set to `hydrated` to return full taxonomy node details instead.")
class GetFoldersIdMetadataRequest(StrictModel):
    """Retrieves all metadata instances attached to a given folder. Cannot be used on the root folder (ID `0`)."""
    path: GetFoldersIdMetadataRequestPath
    query: GetFoldersIdMetadataRequestQuery | None = None

# Operation: get_folder_classification
class GetFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose classification metadata you want to retrieve. The root folder of a Box account is always ID '0'; other folder IDs can be found in the URL when viewing the folder in the Box web application.")
class GetFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(StrictModel):
    """Retrieves the security classification metadata applied to a specific folder. Returns the classification instance associated with the folder's enterprise security policy."""
    path: GetFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath

# Operation: add_folder_classification
class PostFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder to classify. The ID can be found in the folder's URL in the Box web app; the root folder is always ID '0'.")
class PostFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody(StrictModel):
    box__security__classification__key: str | None = Field(default=None, validation_alias="Box__Security__Classification__Key", serialization_alias="Box__Security__Classification__Key", description="The classification label to apply to the folder. Must match an existing classification key from the enterprise's security classification template.")
class PostFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(StrictModel):
    """Applies a security classification label to a specified folder. The classification must exist in the enterprise's classification template."""
    path: PostFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath
    body: PostFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody | None = None

# Operation: update_folder_classification
class PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose classification will be updated. The folder ID can be found in the URL when viewing the folder in the Box web app. The root folder is always ID '0'.")
class PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody(StrictModel):
    body: list[PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoBodyItem] | None = Field(default=None, description="A list containing exactly one JSON Patch operation object describing the change to apply to the classification label. Only a single update operation is supported per request.")
class PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(StrictModel):
    """Updates the security classification label on a folder that already has a classification applied. Only classification values defined for the enterprise are accepted."""
    path: PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath
    body: PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestBody | None = None

# Operation: remove_folder_classification
class DeleteFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder from which the classification will be removed. The root folder of a Box account is always represented by ID '0'.")
class DeleteFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequest(StrictModel):
    """Removes any existing security classification from a specified folder. This operation clears all classification metadata applied via the enterprise security classification schema."""
    path: DeleteFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoRequestPath

# Operation: get_folder_metadata_instance
class GetFoldersIdMetadataIdIdRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose metadata instance you want to retrieve. Find this ID in the Box web app URL when viewing the folder. The root folder is always ID `0`, but is not supported by this operation.")
    scope: Literal["global", "enterprise"] = Field(default=..., description="The scope of the metadata template to retrieve, either `global` for Box-wide templates or `enterprise` for templates defined within your organization.")
    template_key: str = Field(default=..., description="The unique key name of the metadata template whose instance you want to retrieve from the folder.")
class GetFoldersIdMetadataIdIdRequest(StrictModel):
    """Retrieves a specific metadata template instance applied to a folder, returning its field values and associated metadata. Cannot be used on the root folder (ID `0`)."""
    path: GetFoldersIdMetadataIdIdRequestPath

# Operation: create_folder_metadata
class PostFoldersIdMetadataIdIdRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder to which the metadata instance will be applied. The root folder of a Box account always uses ID `0`; other folder IDs can be found in the URL when viewing the folder in the Box web app.")
    scope: Literal["global", "enterprise"] = Field(default=..., description="The scope of the metadata template to apply, either `global` for Box-wide templates or `enterprise` for templates defined within your enterprise.")
    template_key: str = Field(default=..., description="The unique key name of the metadata template to apply to the folder. Use `properties` for the global free-form key-value template, which accepts any key-value pair.")
class PostFoldersIdMetadataIdIdRequestBody(StrictModel):
    body: dict[str, Any] | None = Field(default=None, description="The metadata key-value pairs to store on the folder, conforming to the fields defined in the specified template. The `global.properties` template accepts any arbitrary key-value pairs.")
class PostFoldersIdMetadataIdIdRequest(StrictModel):
    """Applies an instance of a metadata template to a folder, attaching structured key-value data based on the specified template. Note that the enterprise must have Cascading Folder Level Metadata enabled in the admin console for the metadata to appear in the Box web app."""
    path: PostFoldersIdMetadataIdIdRequestPath
    body: PostFoldersIdMetadataIdIdRequestBody | None = None

# Operation: update_folder_metadata
class PutFoldersIdMetadataIdIdRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder to update metadata on. The ID appears in the folder's URL in the Box web app, and the root folder is always ID `0`.")
    scope: Literal["global", "enterprise"] = Field(default=..., description="The scope of the metadata template, either globally defined or specific to the enterprise account.")
    template_key: str = Field(default=..., description="The unique key name of the metadata template to update on the folder.")
class PutFoldersIdMetadataIdIdRequestBody(StrictModel):
    body: list[PutFoldersIdMetadataIdIdBodyItem] | None = Field(default=None, description="A JSON Patch array of operation objects describing the changes to apply to the metadata instance. Operations are applied atomically — if any operation fails, no changes are made.")
class PutFoldersIdMetadataIdIdRequest(StrictModel):
    """Updates a metadata instance on a folder using JSON Patch operations, applied atomically. The metadata template must already be applied to the folder, and all changes must conform to the template schema."""
    path: PutFoldersIdMetadataIdIdRequestPath
    body: PutFoldersIdMetadataIdIdRequestBody | None = None

# Operation: delete_folder_metadata
class DeleteFoldersIdMetadataIdIdRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder from which metadata will be removed. The root folder of a Box account is always represented by ID '0'; other folder IDs can be found in the URL when viewing the folder in the web application.")
    scope: Literal["global", "enterprise"] = Field(default=..., description="The scope of the metadata template, determining whether it is a globally available template or one specific to the enterprise account.")
    template_key: str = Field(default=..., description="The unique key name of the metadata template instance to remove from the folder, identifying which template's data should be deleted.")
class DeleteFoldersIdMetadataIdIdRequest(StrictModel):
    """Removes a specific metadata instance from a folder by deleting the metadata template instance identified by its scope and template key. This action permanently detaches the metadata from the folder."""
    path: DeleteFoldersIdMetadataIdIdRequestPath

# Operation: list_trash_items
class GetFoldersTrashItemsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of items to return per page. Must be between 1 and 1000.", json_schema_extra={'format': 'int64'})
    offset: int | None = Field(default=None, description="The zero-based index of the first item to include in the response, used for offset-based pagination. Offsets exceeding 10000 will result in a 400 error.", json_schema_extra={'format': 'int64'})
    direction: Literal["ASC", "DESC"] | None = Field(default=None, description="The sort direction for results, either ascending or descending alphabetical order. Items are always grouped by type first (folders, then files, then web links) before this ordering is applied.")
    sort: Literal["name", "date", "size"] | None = Field(default=None, description="The secondary attribute by which to sort items within each type group. Items are always sorted by type first; this parameter is not supported when using marker-based pagination.")
class GetFoldersTrashItemsRequest(StrictModel):
    """Retrieves all files and folders currently in the trash. Supports offset-based and marker-based pagination, and allows sorting and filtering by specific attributes using the fields parameter."""
    query: GetFoldersTrashItemsRequestQuery | None = None

# Operation: get_folder_watermark
class GetFoldersIdWatermarkRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose watermark you want to retrieve. The root folder of a Box account is always represented by the ID '0'; other folder IDs can be found in the URL when viewing the folder in the Box web application.")
class GetFoldersIdWatermarkRequest(StrictModel):
    """Retrieves the watermark applied to a specific folder in Box. Returns watermark details if one exists, or a 404 if no watermark has been applied."""
    path: GetFoldersIdWatermarkRequestPath

# Operation: apply_folder_watermark
class PutFoldersIdWatermarkRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder to watermark. The folder ID can be found in the URL when viewing the folder in the Box web app. The root folder of any Box account is always ID `0`.")
class PutFoldersIdWatermarkRequestBodyWatermark(StrictModel):
    imprint: Literal["default"] | None = Field(default=None, validation_alias="imprint", serialization_alias="imprint", description="The type of watermark imprint to apply to the folder. Currently only the default imprint style is supported.")
class PutFoldersIdWatermarkRequestBody(StrictModel):
    watermark: PutFoldersIdWatermarkRequestBodyWatermark | None = None
class PutFoldersIdWatermarkRequest(StrictModel):
    """Applies or updates a watermark on a specified folder in Box. Use this to protect folder contents by overlaying a visible watermark imprint."""
    path: PutFoldersIdWatermarkRequestPath
    body: PutFoldersIdWatermarkRequestBody | None = None

# Operation: remove_folder_watermark
class DeleteFoldersIdWatermarkRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder from which the watermark will be removed. The root folder of a Box account is always represented by the ID '0'.")
class DeleteFoldersIdWatermarkRequest(StrictModel):
    """Removes the watermark from a specified folder in Box. Once removed, the folder's content will no longer display watermark overlays."""
    path: DeleteFoldersIdWatermarkRequestPath

# Operation: list_folder_locks
class GetFolderLocksRequestQuery(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose locks you want to retrieve. You can find this ID in the folder's URL in the Box web application; the root folder is always ID `0`.")
class GetFolderLocksRequest(StrictModel):
    """Retrieves all lock details for a specified folder, including lock type and restrictions. You must be authenticated as the owner or co-owner of the folder to use this endpoint."""
    query: GetFolderLocksRequestQuery

# Operation: lock_folder
class PostFolderLocksRequestBodyLockedOperations(StrictModel):
    move: bool | None = Field(default=None, validation_alias="move", serialization_alias="move", description="Whether to lock the folder against move operations, preventing it from being relocated within the file system.")
    delete: bool | None = Field(default=None, validation_alias="delete", serialization_alias="delete", description="Whether to lock the folder against deletion, preventing it from being permanently removed.")
class PostFolderLocksRequestBodyFolder(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the folder on which to apply the lock.")
class PostFolderLocksRequestBody(StrictModel):
    locked_operations: PostFolderLocksRequestBodyLockedOperations | None = None
    folder: PostFolderLocksRequestBodyFolder | None = None
class PostFolderLocksRequest(StrictModel):
    """Creates a lock on a folder to prevent it from being moved and/or deleted. You must be the owner or co-owner of the folder to perform this action."""
    body: PostFolderLocksRequestBody | None = None

# Operation: delete_folder_lock
class DeleteFolderLocksIdRequestPath(StrictModel):
    folder_lock_id: str = Field(default=..., description="The unique identifier of the folder lock to delete.")
class DeleteFolderLocksIdRequest(StrictModel):
    """Deletes a specific folder lock, removing any restrictions it imposed on the folder. You must be authenticated as the owner or co-owner of the folder to perform this action."""
    path: DeleteFolderLocksIdRequestPath

# Operation: find_metadata_template_by_instance
class GetMetadataTemplatesRequestQuery(StrictModel):
    metadata_instance_id: str = Field(default=..., description="The unique UUID of a metadata template instance used to identify and retrieve the associated template definition.", json_schema_extra={'format': 'uuid'})
    limit: int | None = Field(default=None, description="The maximum number of metadata templates to return in a single page of results. Must be between 1 and 1000.", json_schema_extra={'format': 'int64'})
class GetMetadataTemplatesRequest(StrictModel):
    """Finds a metadata template by looking up the ID of one of its existing instances. Useful when you have an instance ID and need to retrieve the template definition it was created from."""
    query: GetMetadataTemplatesRequestQuery

# Operation: get_metadata_template
class GetMetadataTemplatesIdIdSchemaRequestPath(StrictModel):
    scope: Literal["global", "enterprise"] = Field(default=..., description="The scope of the metadata template, either 'global' for Box-wide templates or 'enterprise' for templates specific to your organization.")
    template_key: str = Field(default=..., description="The unique key identifying the metadata template within its scope. To discover available template keys, list all templates for an enterprise or globally, or list templates applied to a file or folder.")
class GetMetadataTemplatesIdIdSchemaRequest(StrictModel):
    """Retrieves a specific metadata template by its scope and template key. Use this to fetch full template details including its fields and configuration."""
    path: GetMetadataTemplatesIdIdSchemaRequestPath

# Operation: update_metadata_template
class PutMetadataTemplatesIdIdSchemaRequestPath(StrictModel):
    scope: Literal["global", "enterprise"] = Field(default=..., description="The scope of the metadata template, determining its visibility and ownership — either globally available or restricted to the enterprise.")
    template_key: str = Field(default=..., description="The unique key identifying the metadata template within the given scope.")
class PutMetadataTemplatesIdIdSchemaRequestBody(StrictModel):
    body: list[PutMetadataTemplatesIdIdSchemaBodyItem] | None = Field(default=None, description="An ordered array of JSON-Patch (RFC 6902) operation objects describing the changes to apply to the metadata template. Each item specifies an operation type, target path, and value as needed.")
class PutMetadataTemplatesIdIdSchemaRequest(StrictModel):
    """Updates an existing metadata template by applying a series of JSON-Patch operations atomically. All changes succeed or fail together — no partial updates are applied if any operation encounters an error."""
    path: PutMetadataTemplatesIdIdSchemaRequestPath
    body: PutMetadataTemplatesIdIdSchemaRequestBody | None = None

# Operation: delete_metadata_template
class DeleteMetadataTemplatesIdIdSchemaRequestPath(StrictModel):
    scope: Literal["global", "enterprise"] = Field(default=..., description="The scope of the metadata template, determining whether it applies globally across all enterprises or is specific to your enterprise.")
    template_key: str = Field(default=..., description="The unique key name identifying the metadata template within the specified scope.")
class DeleteMetadataTemplatesIdIdSchemaRequest(StrictModel):
    """Permanently deletes a metadata template and all of its associated instances. This action is irreversible and removes the template across all content it was applied to."""
    path: DeleteMetadataTemplatesIdIdSchemaRequestPath

# Operation: get_metadata_template_by_id
class GetMetadataTemplatesIdRequestPath(StrictModel):
    template_id: str = Field(default=..., description="The unique identifier of the metadata template to retrieve.")
class GetMetadataTemplatesIdRequest(StrictModel):
    """Retrieves a specific metadata template by its unique ID. Use this to inspect template structure, fields, and configuration for a known template."""
    path: GetMetadataTemplatesIdRequestPath

# Operation: list_global_metadata_templates
class GetMetadataTemplatesGlobalRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of metadata templates to return per page. Accepts values up to 1000; omit to use the default page size.", json_schema_extra={'format': 'int64'})
class GetMetadataTemplatesGlobalRequest(StrictModel):
    """Retrieves all generic, global metadata templates available to every enterprise using Box. These templates are not organization-specific and can be applied universally across all Box accounts."""
    query: GetMetadataTemplatesGlobalRequestQuery | None = None

# Operation: list_enterprise_metadata_templates
class GetMetadataTemplatesEnterpriseRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of metadata templates to return per page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetMetadataTemplatesEnterpriseRequest(StrictModel):
    """Retrieves all metadata templates created for use within the authenticated user's enterprise. Returns a paginated list of enterprise-scoped templates available for applying structured metadata to content."""
    query: GetMetadataTemplatesEnterpriseRequestQuery | None = None

# Operation: create_metadata_template
class PostMetadataTemplatesSchemaRequestBody(StrictModel):
    scope: str | None = Field(default=None, description="The scope under which the metadata template will be created. Must be set to 'enterprise', as global-scoped templates cannot be created via the API.")
    template_key: str | None = Field(default=None, validation_alias="templateKey", serialization_alias="templateKey", description="A unique identifier for the template across the enterprise, used to reference it programmatically. Must start with a letter or underscore, followed by letters, digits, hyphens, or underscores, up to 64 characters. If omitted, the API auto-generates one from the display name.", max_length=64, pattern='^[a-zA-Z_][-a-zA-Z0-9_]*$')
    display_name: str | None = Field(default=None, validation_alias="displayName", serialization_alias="displayName", description="The human-readable name of the template shown in the Box UI and API responses, up to 4096 characters.", max_length=4096)
    hidden: bool | None = Field(default=None, description="Controls whether the template is visible in the Box web app UI. Set to true to hide it and restrict usage to API access only.")
    fields: list[PostMetadataTemplatesSchemaBodyFieldsItem] | None = Field(default=None, description="An ordered list of field definitions that make up the template. Each field can be of type text, date, number, single-select, or multi-select list, and the order provided determines display order.")
    copy_instance_on_item_copy: bool | None = Field(default=None, validation_alias="copyInstanceOnItemCopy", serialization_alias="copyInstanceOnItemCopy", description="Determines whether metadata instances attached to a file or folder are automatically copied when that item is copied. Defaults to false, meaning metadata is not copied.")
class PostMetadataTemplatesSchemaRequest(StrictModel):
    """Creates a new metadata template that can be applied to files and folders within an enterprise, defining custom fields for organizing and categorizing content."""
    body: PostMetadataTemplatesSchemaRequestBody | None = None

# Operation: initialize_classifications
class PostMetadataTemplatesSchemaClassificationsRequestBody(StrictModel):
    hidden: bool | None = Field(default=None, description="Controls whether the classification template is hidden from users on web and mobile devices. Set to true to restrict visibility, or false to make classifications available for selection.")
    copy_instance_on_item_copy: bool | None = Field(default=None, validation_alias="copyInstanceOnItemCopy", serialization_alias="copyInstanceOnItemCopy", description="Controls whether the assigned classification is automatically copied to a new item when a file or folder is copied. Set to true to propagate classifications on copy, or false to leave the copy unclassified.")
    fields: list[PostMetadataTemplatesSchemaClassificationsBodyFieldsItem] | None = Field(default=None, description="Defines the classification values available in the template. Exactly one field object must be provided, containing all valid classification options as enumerated values within that field.")
class PostMetadataTemplatesSchemaClassificationsRequest(StrictModel):
    """Initializes the classification metadata template for an enterprise with an initial set of classifications. Use this only when no classification template exists yet; if one already exists, use the add classifications endpoint instead."""
    body: PostMetadataTemplatesSchemaClassificationsRequestBody | None = None

# Operation: list_metadata_cascade_policies
class GetMetadataCascadePoliciesRequestQuery(StrictModel):
    folder_id: str = Field(default=..., description="The ID of the folder for which to retrieve metadata cascade policies. Must be a valid non-root folder; the root folder with ID `0` is not supported.")
    owner_enterprise_id: str | None = Field(default=None, description="The ID of the enterprise whose metadata cascade policies should be returned. Defaults to the currently authenticated enterprise if not provided.")
    offset: int | None = Field(default=None, description="The zero-based index of the first item to include in the response, used for paginating through results. Must not exceed 10000; requests with a higher offset will be rejected with a 400 error.", json_schema_extra={'format': 'int64'})
class GetMetadataCascadePoliciesRequest(StrictModel):
    """Retrieves all metadata cascade policies applied to a specific folder, which automatically apply metadata templates to items within that folder. Cannot be used on the root folder (ID `0`)."""
    query: GetMetadataCascadePoliciesRequestQuery

# Operation: create_metadata_cascade_policy
class PostMetadataCascadePoliciesRequestBody(StrictModel):
    folder_id: str | None = Field(default=None, description="The unique identifier of the folder to which the cascade policy will be applied. The folder must already have an instance of the target metadata template applied to it.")
    scope: dict | None = Field(default=None, description="The scope of the targeted metadata template. This template will\nneed to already have an instance applied to the targeted folder.")
    template_key: str | None = Field(default=None, validation_alias="templateKey", serialization_alias="templateKey", description="The key of the targeted metadata template. This template will\nneed to already have an instance applied to the targeted folder.\n\nIn many cases the template key is automatically derived\nof its display name, for example `Contract Template` would\nbecome `contractTemplate`. In some cases the creator of the\ntemplate will have provided its own template key.\n\nPlease [list the templates for an enterprise][list], or\nget all instances on a [file][file] or [folder][folder]\nto inspect a template's key.\n\n[list]: https://developer.box.com/reference/get-metadata-templates-enterprise\n[file]: https://developer.box.com/reference/get-files-id-metadata\n[folder]: https://developer.box.com/reference/get-folders-id-metadata")
class PostMetadataCascadePoliciesRequest(StrictModel):
    """Creates a metadata cascade policy that automatically applies a metadata template from a specified folder down to all files within it. The folder must already have an instance of the target metadata template applied before the policy can take effect."""
    body: PostMetadataCascadePoliciesRequestBody | None = None

# Operation: get_metadata_cascade_policy
class GetMetadataCascadePoliciesIdRequestPath(StrictModel):
    metadata_cascade_policy_id: str = Field(default=..., description="The unique identifier of the metadata cascade policy to retrieve.")
class GetMetadataCascadePoliciesIdRequest(StrictModel):
    """Retrieves the details of a specific metadata cascade policy assigned to a folder. Use this to inspect how metadata templates are being propagated from a folder to its contents."""
    path: GetMetadataCascadePoliciesIdRequestPath

# Operation: apply_metadata_cascade_policy
class PostMetadataCascadePoliciesIdApplyRequestPath(StrictModel):
    metadata_cascade_policy_id: str = Field(default=..., description="The unique identifier of the metadata cascade policy to force-apply to the folder's children.")
class PostMetadataCascadePoliciesIdApplyRequestBody(StrictModel):
    conflict_resolution: Literal["none", "overwrite"] | None = Field(default=None, description="Determines how to handle conflicts when a child file already has an instance of the metadata template applied. Use 'none' to preserve existing values on the child, or 'overwrite' to replace them with the cascaded values from the folder.")
class PostMetadataCascadePoliciesIdApplyRequest(StrictModel):
    """Force-applies a metadata cascade policy to all existing children within a folder, ensuring inherited metadata values are propagated down. Useful after creating a new cascade policy to retroactively enforce metadata on files already present in the folder."""
    path: PostMetadataCascadePoliciesIdApplyRequestPath
    body: PostMetadataCascadePoliciesIdApplyRequestBody | None = None

# Operation: query_items_by_metadata
class PostMetadataQueriesExecuteReadRequestBody(StrictModel):
    from_: str | None = Field(default=None, validation_alias="from", serialization_alias="from", description="The metadata template to query against, specified as `scope.templateKey`. Built-in Box-provided classification templates are not supported.")
    query: str | None = Field(default=None, description="A SQL-like logical expression used to filter items by their metadata field values. Use named placeholders (e.g., `:paramName`) to reference values defined in `query_params`.")
    query_params: dict[str, Any] | None = Field(default=None, description="A key-value map of named parameters referenced in the `query` expression. Each value's type must match the corresponding metadata template field type.")
    ancestor_folder_id: str | None = Field(default=None, description="The ID of the folder to scope the query to. Use `0` to search across all accessible folders, or provide a specific folder ID to restrict results to that folder and its subfolders.")
    order_by: list[PostMetadataQueriesExecuteReadBodyOrderByItem] | None = Field(default=None, description="An ordered list of metadata template fields and sort directions to apply to the results. All items in the array must use the same sort direction.")
    limit: int | None = Field(default=None, description="The maximum number of results to return in a single request, between 0 and 100. This is an upper boundary and does not guarantee a minimum number of results.", ge=0, le=100)
class PostMetadataQueriesExecuteReadRequest(StrictModel):
    """Search for files and folders using SQL-like syntax against a specific metadata template. Use the `fields` attribute to include additional metadata fields in the results."""
    body: PostMetadataQueriesExecuteReadRequestBody | None = None

# Operation: get_comment
class GetCommentsIdRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to retrieve.")
class GetCommentsIdRequest(StrictModel):
    """Retrieves the message, metadata, and author information for a specific comment. Use this to fetch the full details of a single comment by its unique identifier."""
    path: GetCommentsIdRequestPath

# Operation: update_comment
class PutCommentsIdRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to update.")
class PutCommentsIdRequestBody(StrictModel):
    message: str | None = Field(default=None, description="The new text content to replace the comment's existing message.")
class PutCommentsIdRequest(StrictModel):
    """Updates the message text of an existing comment. Use this to edit or correct the content of a previously posted comment."""
    path: PutCommentsIdRequestPath
    body: PutCommentsIdRequestBody | None = None

# Operation: delete_comment
class DeleteCommentsIdRequestPath(StrictModel):
    comment_id: str = Field(default=..., description="The unique identifier of the comment to permanently delete.")
class DeleteCommentsIdRequest(StrictModel):
    """Permanently deletes a comment by its unique identifier. This action is irreversible and cannot be undone."""
    path: DeleteCommentsIdRequestPath

# Operation: create_comment
class PostCommentsRequestBodyItem(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the file or comment this comment will be attached to.")
    type_: Literal["file", "comment"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Specifies whether the comment is being placed on a file or as a reply to an existing comment.")
class PostCommentsRequestBody(StrictModel):
    tagged_message: str | None = Field(default=None, description="The text of the comment using mention syntax to tag another user, formatted as `@[user_id:display_name]` anywhere in the message. Use the plain `message` parameter instead if no user mentions are needed.")
    item: PostCommentsRequestBodyItem | None = None
class PostCommentsRequest(StrictModel):
    """Creates a new comment on a file or as a reply to an existing comment. Supports mentioning other users via a tagged message syntax to trigger email notifications."""
    body: PostCommentsRequestBody | None = None

# Operation: get_collaboration
class GetCollaborationsIdRequestPath(StrictModel):
    collaboration_id: str = Field(default=..., description="The unique identifier of the collaboration to retrieve.")
class GetCollaborationsIdRequest(StrictModel):
    """Retrieves the details of a single collaboration by its unique identifier. Use this to inspect collaboration settings, permissions, and associated users or groups."""
    path: GetCollaborationsIdRequestPath

# Operation: update_collaboration
class PutCollaborationsIdRequestPath(StrictModel):
    collaboration_id: str = Field(default=..., description="The unique identifier of the collaboration to update.")
class PutCollaborationsIdRequestBody(StrictModel):
    role: Literal["editor", "viewer", "previewer", "uploader", "previewer uploader", "viewer uploader", "co-owner", "owner"] | None = Field(default=None, description="The permission level to grant the collaborator. Not required when accepting a collaboration invitation. Valid values range from read-only access (viewer, previewer) to full ownership (owner).")
    status: Literal["pending", "accepted", "rejected"] | None = Field(default=None, description="Sets the status of a pending collaboration invitation to accept or reject it. Only applicable to collaborations currently in a pending state.")
    expires_at: str | None = Field(default=None, description="The date and time at which the collaboration will be automatically removed from the item, specified in ISO 8601 format. Requires the 'Automatically remove invited collaborators' setting to be enabled in the Admin Console, and the collaboration must have been created after that setting was enabled.", json_schema_extra={'format': 'date-time'})
    can_view_path: bool | None = Field(default=None, description="When true, allows the invited collaborator to see the full parent folder path to the collaborated item without gaining access to parent folder contents. Only applicable to folder collaborations; only an owner can update this setting on existing collaborations, and it is recommended to limit collaborations with this enabled to 1,000 per user.")
class PutCollaborationsIdRequest(StrictModel):
    """Updates an existing collaboration on a Box item, allowing you to change the collaborator's role, accept or reject a pending invitation, set an expiration date, or toggle parent path visibility."""
    path: PutCollaborationsIdRequestPath
    body: PutCollaborationsIdRequestBody | None = None

# Operation: delete_collaboration
class DeleteCollaborationsIdRequestPath(StrictModel):
    collaboration_id: str = Field(default=..., description="The unique identifier of the collaboration to delete.")
class DeleteCollaborationsIdRequest(StrictModel):
    """Permanently removes a collaboration by its unique identifier. This action cannot be undone and will revoke the associated access or shared relationship."""
    path: DeleteCollaborationsIdRequestPath

# Operation: list_pending_collaborations
class GetCollaborationsRequestQuery(StrictModel):
    status: Literal["pending"] = Field(default=..., description="Filters collaborations by their current status. Only pending invites are supported by this endpoint.")
    offset: int | None = Field(default=None, description="Zero-based index of the first item to include in the response, used for paginating through results. Must not exceed 10,000; requests beyond this limit will return a 400 error.", json_schema_extra={'format': 'int64'})
    limit: int | None = Field(default=None, description="Limits the number of collaboration records returned in a single page. Accepts values up to 1,000.", json_schema_extra={'format': 'int64'})
class GetCollaborationsRequest(StrictModel):
    """Retrieves all pending collaboration invites for the authenticated user. Returns a paginated list of collaborations awaiting the user's response."""
    query: GetCollaborationsRequestQuery

# Operation: create_collaboration
class PostCollaborationsRequestQuery(StrictModel):
    notify: bool | None = Field(default=None, description="Whether to send an email notification to the invited collaborator when the collaboration is created.")
class PostCollaborationsRequestBodyItem(StrictModel):
    type_: Literal["file", "folder"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of Box item the collaboration will be granted access to, either a file or a folder.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique Box ID of the file or folder to which access is being granted.")
class PostCollaborationsRequestBodyAccessibleBy(StrictModel):
    type_: Literal["user", "group"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Specifies whether the collaborator being invited is an individual user or a group. Group invitations depend on the group's invite permissions.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique Box ID of the user or group being invited. Use this or the email-based login field to identify a user, but not both.")
    login: str | None = Field(default=None, validation_alias="login", serialization_alias="login", description="The email address of the user to invite as a collaborator. Use this or the user ID field to identify a user, but not both.")
class PostCollaborationsRequestBody(StrictModel):
    role: Literal["editor", "viewer", "previewer", "uploader", "previewer uploader", "viewer uploader", "co-owner"] | None = Field(default=None, description="The permission level granted to the collaborator, controlling what actions they can perform on the item.")
    is_access_only: bool | None = Field(default=None, description="When true, the collaborator can access the shared item but it will not appear in their All Files list and the root folder path will be hidden.")
    can_view_path: bool | None = Field(default=None, description="When true, allows the collaborator to see the full parent folder path to the shared folder without gaining access to parent folder contents. Only applicable to folder collaborations, and only owners or co-owners can set this. Limit use to 1,000 collaborations per user to avoid performance impact.")
    expires_at: str | None = Field(default=None, description="The date and time at which the collaboration will be automatically removed from the item, provided in ISO 8601 format. Requires the expiry extension setting to be enabled in the Admin Console Enterprise Settings.", json_schema_extra={'format': 'date-time'})
    item: PostCollaborationsRequestBodyItem | None = None
    accessible_by: PostCollaborationsRequestBodyAccessibleBy | None = None
class PostCollaborationsRequest(StrictModel):
    """Grants a single user or group access to a file or folder by creating a collaboration with a specified role. Collaborators can be identified by user ID, group ID, or email address."""
    query: PostCollaborationsRequestQuery | None = None
    body: PostCollaborationsRequestBody | None = None

# Operation: search_content
class GetSearchRequestQuery(StrictModel):
    query: str | None = Field(default=None, description="The text to search for, matched against item names, descriptions, file content, and other fields. Supports boolean operators AND, OR, and NOT (uppercase only), and exact phrase matching using double quotes.")
    scope: Literal["user_content", "enterprise_content"] | None = Field(default=None, description="Restricts search results to content accessible by the current user (`user_content`) or all content across the entire enterprise (`enterprise_content`). Enterprise scope requires admin enablement via support.")
    file_extensions: list[str] | None = Field(default=None, description="Restricts results to files matching any of the specified file extensions. Provide extensions without leading dots as an array.")
    created_at_range: list[str] | None = Field(default=None, description="Restricts results to items created within a date range, provided as an array of two RFC3339 timestamp strings representing start and end dates. Either bound may be omitted to create an open-ended range.")
    updated_at_range: list[str] | None = Field(default=None, description="Restricts results to items last updated within a date range, provided as an array of two RFC3339 timestamp strings representing start and end dates. Either bound may be omitted to create an open-ended range.")
    size_range: list[int] | None = Field(default=None, description="Restricts results to items whose file size falls within a byte range, provided as an array of two integers representing the lower and upper bounds (inclusive). Either bound may be omitted to create an open-ended range.")
    owner_user_ids: list[str] | None = Field(default=None, description="Restricts results to items owned by the specified users, provided as an array of user ID strings. Items must still be accessible to the authenticated user; inaccessible owners yield empty results.")
    recent_updater_user_ids: list[str] | None = Field(default=None, description="Restricts results to items most recently updated by the specified users, provided as an array of user ID strings. Only the last 10 versions of each item are considered.")
    ancestor_folder_ids: list[str] | None = Field(default=None, description="Restricts results to items located within the specified folders or their subfolders, provided as an array of folder ID strings. Folders must be accessible to the authenticated user; inaccessible or nonexistent folders return HTTP 404.")
    content_types: list[Literal["name", "description", "file_content", "comments", "tag"]] | None = Field(default=None, description="Restricts the search to specific parts of an item, such as its name, description, file content, comments, or tags. Provide as an array of recognized content type strings.")
    type_: Literal["file", "folder", "web_link"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Restricts results to a single item type: `file`, `folder`, or `web_link`. When omitted, all item types are returned.")
    trash_content: Literal["non_trashed_only", "trashed_only", "all_items"] | None = Field(default=None, description="Controls whether results include items in the trash, items not in the trash, or both. Defaults to returning only non-trashed items.")
    mdfilters: list[MetadataFilter] | None = Field(default=None, description="Restricts results to items whose metadata matches a specific metadata template filter. Accepts exactly one metadata filter object; required when `query` is not provided.", min_length=1, max_length=1)
    sort: Literal["modified_at", "relevance"] | None = Field(default=None, description="Determines the ordering of search results. Use `relevance` to rank by match quality or `modified_at` to order by most recently modified first.")
    direction: Literal["DESC", "ASC"] | None = Field(default=None, description="Sets the sort direction for results as ascending (`ASC`) or descending (`DESC`). Ignored when `sort` is set to `relevance`, which always returns results in descending relevance order.")
    limit: int | None = Field(default=None, description="Maximum number of items to return per page of results. Must be between 1 and 200.", json_schema_extra={'format': 'int64'})
    include_recent_shared_links: bool | None = Field(default=None, description="When set to true, includes items the user recently accessed via a shared link in the results. Enabling this changes the response format to include shared link metadata.")
    deleted_user_ids: list[str] | None = Field(default=None, description="Restricts results to items deleted by the specified users, provided as an array of user ID strings. Requires `trash_content` to be set to `trashed_only`. Only available for data from 2023-02-01 onwards.")
    deleted_at_range: list[str] | None = Field(default=None, description="Restricts results to items deleted within a date range, provided as an array of two RFC3339 timestamp strings representing start and end dates. Requires `trash_content` to be set to `trashed_only`. Only available for data from 2023-02-01 onwards.")
class GetSearchRequest(StrictModel):
    """Search for files, folders, web links, and shared files across the authenticated user's content or the entire enterprise, with support for rich filtering by metadata, date ranges, file type, ownership, and more."""
    query: GetSearchRequestQuery | None = None

# Operation: create_task
class PostTasksRequestBodyItem(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the file on which the task will be created.")
    type_: Literal["file"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of item the task is being created on; must always be set to 'file'.")
class PostTasksRequestBody(StrictModel):
    action: Literal["review", "complete"] | None = Field(default=None, description="The action assignees will be prompted to perform: 'review' creates an approval task that can be approved or rejected, while 'complete' creates a general task that can simply be marked as done.")
    message: str | None = Field(default=None, description="An optional message displayed to task assignees providing context or instructions for the task.")
    due_at: str | None = Field(default=None, description="The deadline by which the task should be completed, specified as an ISO 8601 date-time string. Defaults to null if omitted.", json_schema_extra={'format': 'date-time'})
    completion_rule: Literal["all_assignees", "any_assignee"] | None = Field(default=None, description="Determines how many assignees must act on the task before it is considered complete: 'all_assignees' requires every assignee to respond, while 'any_assignee' requires only one.")
    item: PostTasksRequestBodyItem | None = None
class PostTasksRequest(StrictModel):
    """Creates a new task on a specified file, optionally configuring the action type, due date, message, and completion rules. The task must be assigned to users separately after creation."""
    body: PostTasksRequestBody | None = None

# Operation: get_task
class GetTasksIdRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to retrieve.")
class GetTasksIdRequest(StrictModel):
    """Retrieves detailed information about a specific task by its unique identifier. Use this to fetch the current state, metadata, and attributes of a single task."""
    path: GetTasksIdRequestPath

# Operation: update_task
class PutTasksIdRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to update.")
class PutTasksIdRequestBody(StrictModel):
    action: Literal["review", "complete"] | None = Field(default=None, description="The type of action assignees are prompted to perform: 'review' creates an approval task that can be approved or rejected, while 'complete' creates a general task that can be marked done.")
    message: str | None = Field(default=None, description="The instructional message displayed to task assignees describing what they need to do.")
    due_at: str | None = Field(default=None, description="The deadline by which the task should be completed, specified as an ISO 8601 date-time string.", json_schema_extra={'format': 'date-time'})
    completion_rule: Literal["all_assignees", "any_assignee"] | None = Field(default=None, description="Determines how many assignees must complete the task before it is marked as completed: 'all_assignees' requires every assignee to act, while 'any_assignee' requires only one.")
class PutTasksIdRequest(StrictModel):
    """Updates an existing task's configuration or completion state, including its action type, message, due date, and assignee completion rules."""
    path: PutTasksIdRequestPath
    body: PutTasksIdRequestBody | None = None

# Operation: delete_task
class DeleteTasksIdRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task to be deleted.")
class DeleteTasksIdRequest(StrictModel):
    """Permanently removes a task from its associated file. This action cannot be undone."""
    path: DeleteTasksIdRequestPath

# Operation: list_task_assignments
class GetTasksIdAssignmentsRequestPath(StrictModel):
    task_id: str = Field(default=..., description="The unique identifier of the task whose assignments you want to retrieve.")
class GetTasksIdAssignmentsRequest(StrictModel):
    """Retrieves all assignments associated with a specific task, returning the list of users or groups assigned to it."""
    path: GetTasksIdAssignmentsRequestPath

# Operation: assign_task
class PostTaskAssignmentsRequestBodyTask(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the task to be assigned.")
    type_: Literal["task"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of the item being assigned. Must always be set to 'task'.")
class PostTaskAssignmentsRequestBodyAssignTo(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the user to assign the task to. Use the `login` parameter instead to specify the user by email address.")
    login: str | None = Field(default=None, validation_alias="login", serialization_alias="login", description="The email address of the user to assign the task to. Use the `id` parameter instead to specify the user by their unique user ID.")
class PostTaskAssignmentsRequestBody(StrictModel):
    task: PostTaskAssignmentsRequestBodyTask | None = None
    assign_to: PostTaskAssignmentsRequestBodyAssignTo | None = None
class PostTaskAssignmentsRequest(StrictModel):
    """Assigns a task to a specific user by user ID or email address. A task can be assigned to multiple users by creating separate assignments."""
    body: PostTaskAssignmentsRequestBody | None = None

# Operation: get_task_assignment
class GetTaskAssignmentsIdRequestPath(StrictModel):
    task_assignment_id: str = Field(default=..., description="The unique identifier of the task assignment to retrieve.")
class GetTaskAssignmentsIdRequest(StrictModel):
    """Retrieves detailed information about a specific task assignment, including its status, assignee, and associated task. Use this to inspect the current state of a single task assignment by its unique identifier."""
    path: GetTaskAssignmentsIdRequestPath

# Operation: update_task_assignment
class PutTaskAssignmentsIdRequestPath(StrictModel):
    task_assignment_id: str = Field(default=..., description="The unique identifier of the task assignment to update.")
class PutTaskAssignmentsIdRequestBody(StrictModel):
    message: str | None = Field(default=None, description="An optional message from the assignee to accompany the task assignment update.")
    resolution_state: Literal["completed", "incomplete", "approved", "rejected"] | None = Field(default=None, description="The resolution state to set for the task assignment. For tasks with action type 'complete', valid values are 'incomplete' or 'completed'. For tasks with action type 'review', valid values are 'incomplete', 'approved', or 'rejected'.")
class PutTaskAssignmentsIdRequest(StrictModel):
    """Updates a task assignment for a specific user, allowing changes to the resolution state or an optional assignee message. Supported resolution states depend on the task's action type (complete or review)."""
    path: PutTaskAssignmentsIdRequestPath
    body: PutTaskAssignmentsIdRequestBody | None = None

# Operation: delete_task_assignment
class DeleteTaskAssignmentsIdRequestPath(StrictModel):
    task_assignment_id: str = Field(default=..., description="The unique identifier of the task assignment to delete.")
class DeleteTaskAssignmentsIdRequest(StrictModel):
    """Removes a specific task assignment, unassigning the user from the associated task. This action permanently deletes the assignment record."""
    path: DeleteTaskAssignmentsIdRequestPath

# Operation: get_shared_link_file
class GetSharedItemsRequestHeader(StrictModel):
    boxapi: str = Field(default=..., description="Authorization header value containing the shared link URL and an optional password, formatted as a key-value pair string using the shared_link and shared_link_password keys.")
class GetSharedItemsRequest(StrictModel):
    """Retrieves file information for a given shared link, supporting links originating from within or outside the current enterprise. Optionally returns shared link permission options when requested via the fields query parameter."""
    header: GetSharedItemsRequestHeader

# Operation: get_file_shared_link
class GetFilesIdGetSharedLinkRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose shared link information you want to retrieve. The file ID can be found in the file's URL in the Box web application.")
class GetFilesIdGetSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="Specifies which fields to include in the response; must be set to request shared link data to be returned for the file.")
class GetFilesIdGetSharedLinkRequest(StrictModel):
    """Retrieves the shared link details for a specific file, including its URL, access level, and permissions. Use this to inspect or confirm the sharing configuration of a file."""
    path: GetFilesIdGetSharedLinkRequestPath
    query: GetFilesIdGetSharedLinkRequestQuery

# Operation: add_file_shared_link
class PutFilesIdAddSharedLinkRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file to add a shared link to. Visible in the file's URL in the Box web application.")
class PutFilesIdAddSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="A comma-separated list of fields to include in the response. Must include 'shared_link' to return shared link details in the response.")
class PutFilesIdAddSharedLinkRequestBodySharedLinkPermissions(StrictModel):
    can_download: bool | None = Field(default=None, validation_alias="can_download", serialization_alias="can_download", description="Whether the shared link permits downloading the file. Can only be set when access is 'open' or 'company'.")
    can_preview: bool | None = Field(default=None, validation_alias="can_preview", serialization_alias="can_preview", description="Whether the shared link permits previewing the file. This value is always true and applies to all items within a folder when set on a folder shared link.")
    can_edit: bool | None = Field(default=None, validation_alias="can_edit", serialization_alias="can_edit", description="Whether the shared link permits editing the file. Can only be set when access is 'open' or 'company', and requires can_download to also be true.")
class PutFilesIdAddSharedLinkRequestBodySharedLink(StrictModel):
    access: Literal["open", "company", "collaborators"] | None = Field(default=None, validation_alias="access", serialization_alias="access", description="The visibility level of the shared link. Use 'open' for anyone with the link, 'company' for internal users only (paid accounts only), or 'collaborators' for explicitly invited users only. Defaults to the enterprise admin setting if omitted.")
    password: str | None = Field(default=None, validation_alias="password", serialization_alias="password", description="An optional password required to access the shared link. Must be at least eight characters and include a number, uppercase letter, or non-alphanumeric character. Can only be set when access is 'open'. Set to null to remove an existing password.")
    vanity_name: str | None = Field(default=None, validation_alias="vanity_name", serialization_alias="vanity_name", description="A custom vanity slug appended to the shared link URL (e.g., https://app.box.com/v/{vanity_name}). Must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess.", min_length=12)
    unshared_at: str | None = Field(default=None, validation_alias="unshared_at", serialization_alias="unshared_at", description="The ISO 8601 datetime at which the shared link expires and becomes inaccessible. Must be a future datetime. Only available to paid account users.", json_schema_extra={'format': 'date-time'})
    permissions: PutFilesIdAddSharedLinkRequestBodySharedLinkPermissions | None = None
class PutFilesIdAddSharedLinkRequestBody(StrictModel):
    shared_link: PutFilesIdAddSharedLinkRequestBodySharedLink | None = None
class PutFilesIdAddSharedLinkRequest(StrictModel):
    """Creates or updates a shared link on a file, controlling access level, permissions, expiration, and optional password protection. Returns the file with the shared link fields populated."""
    path: PutFilesIdAddSharedLinkRequestPath
    query: PutFilesIdAddSharedLinkRequestQuery
    body: PutFilesIdAddSharedLinkRequestBody | None = None

# Operation: update_file_shared_link
class PutFilesIdUpdateSharedLinkRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file whose shared link will be updated. The file ID can be found in the URL when viewing the file in the Box web application.")
class PutFilesIdUpdateSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="A comma-separated list of fields to include in the response. Must include 'shared_link' to ensure the updated shared link details are returned.")
class PutFilesIdUpdateSharedLinkRequestBodySharedLinkPermissions(StrictModel):
    can_download: bool | None = Field(default=None, validation_alias="can_download", serialization_alias="can_download", description="Whether the shared link permits downloading of the file. Can only be set when access is 'open' or 'company'.")
    can_preview: bool | None = Field(default=None, validation_alias="can_preview", serialization_alias="can_preview", description="Whether the shared link permits previewing of the file. This value is always true and applies to all items within a folder when set on a folder shared link.")
    can_edit: bool | None = Field(default=None, validation_alias="can_edit", serialization_alias="can_edit", description="Whether the shared link permits editing of the file. Can only be set when access is 'open' or 'company', and requires can_download to also be true.")
class PutFilesIdUpdateSharedLinkRequestBodySharedLink(StrictModel):
    access: Literal["open", "company", "collaborators"] | None = Field(default=None, validation_alias="access", serialization_alias="access", description="The visibility level of the shared link. Use 'open' for anyone with the link, 'company' for internal users only (paid accounts only), or 'collaborators' for explicitly invited users only. Defaults to the enterprise admin setting if omitted.")
    password: str | None = Field(default=None, validation_alias="password", serialization_alias="password", description="An optional password required to access the shared link. Set to null to remove an existing password. Passwords must be at least 8 characters and include a number, uppercase letter, or special character. Can only be set when access is 'open'.")
    vanity_name: str | None = Field(default=None, validation_alias="vanity_name", serialization_alias="vanity_name", description="A custom vanity name to use in the shared link URL path. Must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess than standard shared links.", min_length=12)
    unshared_at: str | None = Field(default=None, validation_alias="unshared_at", serialization_alias="unshared_at", description="The ISO 8601 datetime at which the shared link will expire and become inaccessible. Must be a future date and time. Only available to paid account users.", json_schema_extra={'format': 'date-time'})
    permissions: PutFilesIdUpdateSharedLinkRequestBodySharedLinkPermissions | None = None
class PutFilesIdUpdateSharedLinkRequestBody(StrictModel):
    shared_link: PutFilesIdUpdateSharedLinkRequestBodySharedLink | None = None
class PutFilesIdUpdateSharedLinkRequest(StrictModel):
    """Updates the shared link settings on a specific file, including access level, password protection, expiration, and permissions. Use this to modify an existing shared link or configure a new one on the file."""
    path: PutFilesIdUpdateSharedLinkRequestPath
    query: PutFilesIdUpdateSharedLinkRequestQuery
    body: PutFilesIdUpdateSharedLinkRequestBody | None = None

# Operation: remove_file_shared_link
class PutFilesIdRemoveSharedLinkRequestPath(StrictModel):
    file_id: str = Field(default=..., description="The unique identifier of the file from which the shared link will be removed. The file ID can be found in the URL when viewing the file in the Box web application.")
class PutFilesIdRemoveSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="A comma-separated list of fields to include in the response. Must include 'shared_link' to confirm the shared link has been removed and retrieve the updated link state.")
class PutFilesIdRemoveSharedLinkRequestBody(StrictModel):
    shared_link: dict[str, Any] | None = Field(default=None, description="Set this field to null to remove the shared link from the file. Omitting this field or providing any non-null value will not remove the link.")
class PutFilesIdRemoveSharedLinkRequest(StrictModel):
    """Removes an existing shared link from a file, revoking any previously granted public or shared access. Returns the updated file metadata with the shared link field cleared."""
    path: PutFilesIdRemoveSharedLinkRequestPath
    query: PutFilesIdRemoveSharedLinkRequestQuery
    body: PutFilesIdRemoveSharedLinkRequestBody | None = None

# Operation: get_folder_from_shared_link
class GetSharedItemsFoldersRequestHeader(StrictModel):
    boxapi: str = Field(default=..., description="Authorization header containing the shared link URL and an optional password, formatted as a key-value string using the pattern shared_link=[link]&shared_link_password=[password].")
class GetSharedItemsFoldersRequest(StrictModel):
    """Retrieves folder metadata using a shared link, supporting links from within the current enterprise or external ones. Useful when only a shared link is available and full folder details are needed."""
    header: GetSharedItemsFoldersRequestHeader

# Operation: get_folder_shared_link
class GetFoldersIdGetSharedLinkRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose shared link you want to retrieve. The root folder of a Box account is always ID '0'; other folder IDs can be found in the URL when viewing the folder in the Box web app.")
class GetFoldersIdGetSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="Must be set to 'shared_link' to explicitly request that shared link fields are included in the response. This field is required by the API to return shared link data.")
class GetFoldersIdGetSharedLinkRequest(StrictModel):
    """Retrieves the shared link details for a specific folder, including its URL, access level, and permissions. Use this to inspect or verify the sharing configuration of a folder."""
    path: GetFoldersIdGetSharedLinkRequestPath
    query: GetFoldersIdGetSharedLinkRequestQuery

# Operation: add_folder_shared_link
class PutFoldersIdAddSharedLinkRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder to add a shared link to. The ID appears in the folder's URL in the Box web app, and the root folder is always ID `0`.")
class PutFoldersIdAddSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="A comma-separated list of fields to include in the response. Must include `shared_link` to return the shared link details in the response.")
class PutFoldersIdAddSharedLinkRequestBodySharedLinkPermissions(StrictModel):
    can_download: bool | None = Field(default=None, validation_alias="can_download", serialization_alias="can_download", description="Whether recipients of the shared link are permitted to download files in the folder. Can only be set when access is `open` or `company`.")
    can_preview: bool | None = Field(default=None, validation_alias="can_preview", serialization_alias="can_preview", description="Whether recipients of the shared link are permitted to preview files in the folder. This value is always `true` and applies to all items within the folder.")
    can_edit: bool | None = Field(default=None, validation_alias="can_edit", serialization_alias="can_edit", description="Whether recipients of the shared link are permitted to edit items. For folders, this value can only be `false`.")
class PutFoldersIdAddSharedLinkRequestBodySharedLink(StrictModel):
    access: Literal["open", "company", "collaborators"] | None = Field(default=None, validation_alias="access", serialization_alias="access", description="The visibility level of the shared link: `open` for anyone with the link, `company` for users within the enterprise (paid accounts only), or `collaborators` for only invited collaborators. Omitting this field uses the enterprise admin's default access setting.")
    password: str | None = Field(default=None, validation_alias="password", serialization_alias="password", description="An optional password required to access the shared link. Must be at least 8 characters and include a number, uppercase letter, or non-alphanumeric character. Can only be set when access is `open`; set to `null` to remove an existing password.")
    vanity_name: str | None = Field(default=None, validation_alias="vanity_name", serialization_alias="vanity_name", description="A custom vanity name to use in the shared link URL path. Must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess than standard shared links.", min_length=12)
    unshared_at: str | None = Field(default=None, validation_alias="unshared_at", serialization_alias="unshared_at", description="The ISO 8601 datetime at which the shared link expires and becomes inaccessible. Must be a future date and time, and can only be set by users on paid accounts.", json_schema_extra={'format': 'date-time'})
    permissions: PutFoldersIdAddSharedLinkRequestBodySharedLinkPermissions | None = None
class PutFoldersIdAddSharedLinkRequestBody(StrictModel):
    shared_link: PutFoldersIdAddSharedLinkRequestBodySharedLink | None = None
class PutFoldersIdAddSharedLinkRequest(StrictModel):
    """Adds or updates a shared link on a folder, controlling access level, password protection, expiration, and permissions for viewing or downloading folder contents."""
    path: PutFoldersIdAddSharedLinkRequestPath
    query: PutFoldersIdAddSharedLinkRequestQuery
    body: PutFoldersIdAddSharedLinkRequestBody | None = None

# Operation: update_folder_shared_link
class PutFoldersIdUpdateSharedLinkRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose shared link will be updated. The ID can be found in the folder's URL in the Box web app. The root folder is always ID `0`.")
class PutFoldersIdUpdateSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="A comma-separated list of fields to include in the response. Must include `shared_link` to return the updated shared link details.")
class PutFoldersIdUpdateSharedLinkRequestBodySharedLinkPermissions(StrictModel):
    can_download: bool | None = Field(default=None, validation_alias="can_download", serialization_alias="can_download", description="Whether the shared link permits downloading of files. Can only be enabled when access is set to `open` or `company`.")
    can_preview: bool | None = Field(default=None, validation_alias="can_preview", serialization_alias="can_preview", description="Whether the shared link permits previewing of files. This value is always `true` for folders and applies to all items within the folder.")
    can_edit: bool | None = Field(default=None, validation_alias="can_edit", serialization_alias="can_edit", description="Whether the shared link permits editing of items. For folders, this value can only be set to `false`.")
class PutFoldersIdUpdateSharedLinkRequestBodySharedLink(StrictModel):
    access: Literal["open", "company", "collaborators"] | None = Field(default=None, validation_alias="access", serialization_alias="access", description="The access level for the shared link. Use `open` for anyone with the link, `company` for users within the enterprise (paid accounts only), or `collaborators` for only invited users. Defaults to the enterprise admin setting if omitted.")
    password: str | None = Field(default=None, validation_alias="password", serialization_alias="password", description="An optional password required to access the shared link. Must be at least 8 characters and include a number, uppercase letter, or special character. Can only be set when access is `open`. Set to `null` to remove an existing password.")
    vanity_name: str | None = Field(default=None, validation_alias="vanity_name", serialization_alias="vanity_name", description="A custom vanity name to use in the shared link URL path. Must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess than standard shared links.", min_length=12)
    unshared_at: str | None = Field(default=None, validation_alias="unshared_at", serialization_alias="unshared_at", description="The ISO 8601 datetime at which the shared link will expire and become inaccessible. Must be a future date and time. Only available to paid account users.", json_schema_extra={'format': 'date-time'})
    permissions: PutFoldersIdUpdateSharedLinkRequestBodySharedLinkPermissions | None = None
class PutFoldersIdUpdateSharedLinkRequestBody(StrictModel):
    shared_link: PutFoldersIdUpdateSharedLinkRequestBodySharedLink | None = None
class PutFoldersIdUpdateSharedLinkRequest(StrictModel):
    """Updates the shared link settings on a specific folder, allowing you to configure access level, password protection, expiration, and permissions for the link."""
    path: PutFoldersIdUpdateSharedLinkRequestPath
    query: PutFoldersIdUpdateSharedLinkRequestQuery
    body: PutFoldersIdUpdateSharedLinkRequestBody | None = None

# Operation: remove_folder_shared_link
class PutFoldersIdRemoveSharedLinkRequestPath(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder from which the shared link will be removed. The root folder of a Box account is always represented by the ID '0'.")
class PutFoldersIdRemoveSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="A comma-separated list of fields to include in the response. Must include 'shared_link' to confirm the shared link has been removed from the folder.")
class PutFoldersIdRemoveSharedLinkRequestBody(StrictModel):
    shared_link: dict[str, Any] | None = Field(default=None, description="The shared link configuration object. Set this to null to remove the shared link from the folder and revoke any previously granted access.")
class PutFoldersIdRemoveSharedLinkRequest(StrictModel):
    """Removes an existing shared link from a folder, revoking public or shared access. The shared_link field must be set to null to complete the removal."""
    path: PutFoldersIdRemoveSharedLinkRequestPath
    query: PutFoldersIdRemoveSharedLinkRequestQuery
    body: PutFoldersIdRemoveSharedLinkRequestBody | None = None

# Operation: create_web_link
class PostWebLinksRequestBodyParent(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The ID of the parent folder where the web link will be created. Use '0' to target the root folder.")
class PostWebLinksRequestBody(StrictModel):
    url: str | None = Field(default=None, description="The full URL the web link points to. Must begin with 'http://' or 'https://'.")
    name: str | None = Field(default=None, description="A display name for the web link as it appears in the folder. If omitted, the URL is used as the name.")
    description: str | None = Field(default=None, description="An optional human-readable description providing additional context about the web link's destination or purpose.")
    parent: PostWebLinksRequestBodyParent | None = None
class PostWebLinksRequest(StrictModel):
    """Creates a web link object inside a specified folder, storing a URL as a navigable item within Box. Useful for bookmarking external resources directly within a folder hierarchy."""
    body: PostWebLinksRequestBody | None = None

# Operation: get_web_link
class GetWebLinksIdRequestPath(StrictModel):
    web_link_id: str = Field(default=..., description="The unique identifier of the web link to retrieve.")
class GetWebLinksIdRequest(StrictModel):
    """Retrieves detailed information about a specific web link, including its URL, name, and associated metadata. Useful for inspecting or displaying a saved web link by its unique identifier."""
    path: GetWebLinksIdRequestPath

# Operation: restore_web_link
class PostWebLinksIdRequestPath(StrictModel):
    web_link_id: str = Field(default=..., description="The unique identifier of the web link to restore from the trash.")
class PostWebLinksIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="An optional new name to assign to the web link upon restoration, useful if a naming conflict exists in the destination folder.")
    parent: PostWebLinksIdBodyParent | None = Field(default=None, description="An optional parent folder object specifying an alternative destination to restore the web link into, used when the original parent folder has been deleted.")
class PostWebLinksIdRequest(StrictModel):
    """Restores a web link from the trash back to its original location or an alternative parent folder. An optional new name and parent folder can be specified if the original folder no longer exists."""
    path: PostWebLinksIdRequestPath
    body: PostWebLinksIdRequestBody | None = None

# Operation: update_web_link
class PutWebLinksIdRequestPath(StrictModel):
    web_link_id: str = Field(default=..., description="The unique identifier of the web link to update.")
class PutWebLinksIdRequestBodySharedLink(StrictModel):
    access: Literal["open", "company", "collaborators"] | None = Field(default=None, validation_alias="access", serialization_alias="access", description="The visibility level for the shared link. Use 'open' for anyone with the link, 'company' for internal users only (paid accounts), or 'collaborators' for invited users only. Omitting this field applies the enterprise default.")
    password: str | None = Field(default=None, validation_alias="password", serialization_alias="password", description="A password required to access the shared link. Must be at least eight characters and include a number, uppercase letter, or non-alphanumeric character. Can only be set when access is 'open'; set to null to remove an existing password.")
    vanity_name: str | None = Field(default=None, validation_alias="vanity_name", serialization_alias="vanity_name", description="A custom vanity slug appended to the shared link URL path. Must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess than standard shared links.", min_length=12)
    unshared_at: str | None = Field(default=None, validation_alias="unshared_at", serialization_alias="unshared_at", description="The ISO 8601 datetime at which the shared link expires and becomes inaccessible. Must be a future datetime and can only be set by users on paid accounts.", json_schema_extra={'format': 'date-time'})
class PutWebLinksIdRequestBody(StrictModel):
    url: str | None = Field(default=None, description="The new destination URL for the web link. Must begin with 'http://' or 'https://'.")
    parent: PutWebLinksIdBodyParent | None = Field(default=None, description="The parent folder to move the web link into. Provide the target folder's identifier to relocate the web link.")
    name: str | None = Field(default=None, description="A new display name for the web link. If omitted, the name defaults to the URL.")
    description: str | None = Field(default=None, description="A new human-readable description for the web link to provide additional context about its destination.")
    shared_link: PutWebLinksIdRequestBodySharedLink | None = None
class PutWebLinksIdRequest(StrictModel):
    """Updates an existing web link object, allowing changes to its URL, name, description, parent location, and shared link settings such as access level, password, vanity name, and expiration."""
    path: PutWebLinksIdRequestPath
    body: PutWebLinksIdRequestBody | None = None

# Operation: delete_web_link
class DeleteWebLinksIdRequestPath(StrictModel):
    web_link_id: str = Field(default=..., description="The unique identifier of the web link to delete.")
class DeleteWebLinksIdRequest(StrictModel):
    """Permanently deletes a web link by its unique identifier. This action cannot be undone."""
    path: DeleteWebLinksIdRequestPath

# Operation: get_trashed_web_link
class GetWebLinksIdTrashRequestPath(StrictModel):
    web_link_id: str = Field(default=..., description="The unique identifier of the web link to retrieve from the trash.")
class GetWebLinksIdTrashRequest(StrictModel):
    """Retrieves the details of a web link that has been moved to the trash. Useful for inspecting or restoring a trashed web link before permanent deletion."""
    path: GetWebLinksIdTrashRequestPath

# Operation: permanently_delete_web_link
class DeleteWebLinksIdTrashRequestPath(StrictModel):
    web_link_id: str = Field(default=..., description="The unique identifier of the web link to permanently delete from the trash.")
class DeleteWebLinksIdTrashRequest(StrictModel):
    """Permanently deletes a web link that is currently in the trash, removing it from Box entirely. This action is irreversible and cannot be undone."""
    path: DeleteWebLinksIdTrashRequestPath

# Operation: get_web_link_from_shared_link
class GetSharedItemsWebLinksRequestHeader(StrictModel):
    boxapi: str = Field(default=..., description="Authorization header containing the shared link URL and an optional password, formatted as a key-value string. Both the shared link and password fields must follow the prescribed header format.")
class GetSharedItemsWebLinksRequest(StrictModel):
    """Retrieves web link details using only a shared link URL, supporting links originating from within or outside the current enterprise. Useful when the web link ID is unknown and only the shared link is available."""
    header: GetSharedItemsWebLinksRequestHeader

# Operation: get_web_link_shared_link
class GetWebLinksIdGetSharedLinkRequestPath(StrictModel):
    web_link_id: str = Field(default=..., description="The unique identifier of the web link whose shared link information you want to retrieve.")
class GetWebLinksIdGetSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="Specifies which fields to include in the response; must be set to request shared link data to be returned for the web link.")
class GetWebLinksIdGetSharedLinkRequest(StrictModel):
    """Retrieves the shared link details for a specific web link item. Use this to inspect sharing settings, permissions, and access information for a web link."""
    path: GetWebLinksIdGetSharedLinkRequestPath
    query: GetWebLinksIdGetSharedLinkRequestQuery

# Operation: add_web_link_shared_link
class PutWebLinksIdAddSharedLinkRequestPath(StrictModel):
    web_link_id: str = Field(default=..., description="The unique identifier of the web link to which the shared link will be added.")
class PutWebLinksIdAddSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="A comma-separated list of fields to include in the response; must include 'shared_link' to return the shared link details.")
class PutWebLinksIdAddSharedLinkRequestBodySharedLinkPermissions(StrictModel):
    can_download: bool | None = Field(default=None, validation_alias="can_download", serialization_alias="can_download", description="Whether recipients of the shared link are permitted to download the web link. Can only be set when access is 'open' or 'company'.")
    can_preview: bool | None = Field(default=None, validation_alias="can_preview", serialization_alias="can_preview", description="Whether recipients of the shared link are permitted to preview the web link. This value is always true and also applies to items within a shared folder.")
    can_edit: bool | None = Field(default=None, validation_alias="can_edit", serialization_alias="can_edit", description="Whether recipients of the shared link are permitted to edit the item. Can only be true when the item type is a file.")
class PutWebLinksIdAddSharedLinkRequestBodySharedLink(StrictModel):
    access: Literal["open", "company", "collaborators"] | None = Field(default=None, validation_alias="access", serialization_alias="access", description="The visibility level of the shared link: 'open' allows anyone with the link, 'company' restricts to users within the enterprise (paid accounts only), and 'collaborators' restricts to explicitly invited users. Defaults to the enterprise admin setting if omitted.")
    password: str | None = Field(default=None, validation_alias="password", serialization_alias="password", description="An optional password required to access the shared link; set to null to remove an existing password. Must be at least eight characters and include a number, uppercase letter, or non-alphanumeric character. Can only be set when access is 'open'.")
    vanity_name: str | None = Field(default=None, validation_alias="vanity_name", serialization_alias="vanity_name", description="A custom vanity name used in the shared link URL path, forming a human-readable URL. Must be at least 12 characters; avoid using vanity names for sensitive content as they are easier to guess.", min_length=12)
    unshared_at: str | None = Field(default=None, validation_alias="unshared_at", serialization_alias="unshared_at", description="The ISO 8601 datetime at which the shared link will automatically expire and become inaccessible. Must be a future datetime and can only be set by users on paid accounts.", json_schema_extra={'format': 'date-time'})
    permissions: PutWebLinksIdAddSharedLinkRequestBodySharedLinkPermissions | None = None
class PutWebLinksIdAddSharedLinkRequestBody(StrictModel):
    shared_link: PutWebLinksIdAddSharedLinkRequestBodySharedLink | None = None
class PutWebLinksIdAddSharedLinkRequest(StrictModel):
    """Adds or updates a shared link on a web link item, controlling access level, password protection, expiration, and permissions. Returns the web link with the shared link fields populated."""
    path: PutWebLinksIdAddSharedLinkRequestPath
    query: PutWebLinksIdAddSharedLinkRequestQuery
    body: PutWebLinksIdAddSharedLinkRequestBody | None = None

# Operation: update_web_link_shared_link
class PutWebLinksIdUpdateSharedLinkRequestPath(StrictModel):
    web_link_id: str = Field(default=..., description="The unique identifier of the web link whose shared link settings will be updated.")
class PutWebLinksIdUpdateSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="A comma-separated list of fields to include in the response; must include 'shared_link' to return shared link details.")
class PutWebLinksIdUpdateSharedLinkRequestBodySharedLinkPermissions(StrictModel):
    can_download: bool | None = Field(default=None, validation_alias="can_download", serialization_alias="can_download", description="Whether the shared link permits downloading of the web link. Can only be set when access is 'open' or 'company'.")
    can_preview: bool | None = Field(default=None, validation_alias="can_preview", serialization_alias="can_preview", description="Whether the shared link permits previewing of the web link; this value is always true and also applies to items within a shared folder.")
    can_edit: bool | None = Field(default=None, validation_alias="can_edit", serialization_alias="can_edit", description="Whether the shared link permits editing; can only be true when the item type is a file.")
class PutWebLinksIdUpdateSharedLinkRequestBodySharedLink(StrictModel):
    access: Literal["open", "company", "collaborators"] | None = Field(default=None, validation_alias="access", serialization_alias="access", description="The visibility level of the shared link: 'open' allows anyone with the link, 'company' restricts to users within the enterprise (paid accounts only), and 'collaborators' restricts to invited collaborators only. Defaults to the enterprise admin setting if omitted.")
    password: str | None = Field(default=None, validation_alias="password", serialization_alias="password", description="An optional password required to access the shared link; set to null to remove an existing password. Must be at least eight characters and include a number, uppercase letter, or non-alphanumeric character. Can only be set when access is 'open'.")
    vanity_name: str | None = Field(default=None, validation_alias="vanity_name", serialization_alias="vanity_name", description="A custom vanity name to use in the shared link URL path; must be at least 12 characters. Avoid using vanity names for sensitive content as they are easier to guess than standard shared links.", min_length=12)
    unshared_at: str | None = Field(default=None, validation_alias="unshared_at", serialization_alias="unshared_at", description="The ISO 8601 datetime at which the shared link will expire and become inaccessible; must be a future date and time. Only available to paid account users.", json_schema_extra={'format': 'date-time'})
    permissions: PutWebLinksIdUpdateSharedLinkRequestBodySharedLinkPermissions | None = None
class PutWebLinksIdUpdateSharedLinkRequestBody(StrictModel):
    shared_link: PutWebLinksIdUpdateSharedLinkRequestBodySharedLink | None = None
class PutWebLinksIdUpdateSharedLinkRequest(StrictModel):
    """Updates the shared link settings on an existing web link, allowing you to control access level, password protection, expiration, and permissions."""
    path: PutWebLinksIdUpdateSharedLinkRequestPath
    query: PutWebLinksIdUpdateSharedLinkRequestQuery
    body: PutWebLinksIdUpdateSharedLinkRequestBody | None = None

# Operation: remove_web_link_shared_link
class PutWebLinksIdRemoveSharedLinkRequestPath(StrictModel):
    web_link_id: str = Field(default=..., description="The unique identifier of the web link from which the shared link will be removed.")
class PutWebLinksIdRemoveSharedLinkRequestQuery(StrictModel):
    fields: str = Field(default=..., description="A comma-separated list of fields to include in the response; must include 'shared_link' to confirm the shared link has been removed.")
class PutWebLinksIdRemoveSharedLinkRequestBody(StrictModel):
    shared_link: dict[str, Any] | None = Field(default=None, description="Set this field to null to remove the shared link from the web link; omitting or providing any other value will not revoke the link.")
class PutWebLinksIdRemoveSharedLinkRequest(StrictModel):
    """Removes the shared link from a specified web link, revoking any previously granted public or shared access. The updated web link object is returned with the shared link field reflected."""
    path: PutWebLinksIdRemoveSharedLinkRequestPath
    query: PutWebLinksIdRemoveSharedLinkRequestQuery
    body: PutWebLinksIdRemoveSharedLinkRequestBody | None = None

# Operation: get_app_item_from_shared_link
class GetSharedItemsAppItemsRequestHeader(StrictModel):
    boxapi: str = Field(default=..., description="A header value containing the shared link URL and an optional password, formatted as a key-value pair string using the pattern `shared_link=[link]&shared_link_password=[password]`.")
class GetSharedItemsAppItemsRequest(StrictModel):
    """Retrieves the app item associated with a given shared link, which may originate from the current enterprise or an external one. Requires the shared link URL and an optional password passed as a formatted header value."""
    header: GetSharedItemsAppItemsRequestHeader

# Operation: list_users
class GetUsersRequestQuery(StrictModel):
    filter_term: str | None = Field(default=None, description="Narrows results to users whose name or login starts with the given term. For externally managed users, the term must be an exact match and will return at most one result.")
    user_type: Literal["all", "managed", "external"] | None = Field(default=None, description="Filters results by user category: 'all' includes every user type with partial name/login matching (exact match required for external users), 'managed' returns only managed and app users with partial matching, and 'external' returns only external users whose login exactly matches the filter term.")
    external_app_user_id: str | None = Field(default=None, description="Restricts results to app users that were created with the specified external_app_user_id value, allowing lookup of app users by your own identifier assigned at creation time.")
    offset: int | None = Field(default=None, description="Zero-based index of the first item to include in the response, used for paginating through large result sets. Must not exceed 10000.", json_schema_extra={'format': 'int64'})
    limit: int | None = Field(default=None, description="Maximum number of users to return in a single response page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetUsersRequest(StrictModel):
    """Retrieves a paginated list of all enterprise users, including their user ID, public name, and login. Requires the authenticated user and application to have enterprise-wide user lookup permissions."""
    query: GetUsersRequestQuery | None = None

# Operation: create_user
class PostUsersRequestBody(StrictModel):
    is_platform_access_only: bool | None = Field(default=None, description="When set to true, designates this user as a platform (app) user rather than a standard managed enterprise user.")
    role: Literal["coadmin", "user"] | None = Field(default=None, description="The user's role within the enterprise, either a co-administrator with elevated privileges or a standard user.")
    language: str | None = Field(default=None, description="The display language for the user's Box interface, formatted as a modified ISO 639-1 language code.")
    is_sync_enabled: bool | None = Field(default=None, description="Whether the user is permitted to use Box Sync to synchronize files to their local device.")
    job_title: str | None = Field(default=None, description="The user's job title as displayed in their profile, limited to 100 characters.", max_length=100)
    phone: str | None = Field(default=None, description="The user's phone number as displayed in their profile, limited to 100 characters.", max_length=100)
    address: str | None = Field(default=None, description="The user's physical address as displayed in their profile, limited to 255 characters.", max_length=255)
    space_amount: int | None = Field(default=None, description="The total storage quota allocated to the user in bytes. Use -1 to grant unlimited storage.", json_schema_extra={'format': 'int64'})
    tracking_codes: list[TrackingCode] | None = Field(default=None, description="A list of tracking code objects (each with a name and value) used to categorize users for admin reporting. This feature must be enabled for the enterprise before use; order is not significant.")
    can_see_managed_users: bool | None = Field(default=None, description="Whether the user can view and search other managed users within the enterprise in their contact list.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="The user's local timezone, used for scheduling and display purposes, specified as a timezone identifier string.", json_schema_extra={'format': 'timezone'})
    is_external_collab_restricted: bool | None = Field(default=None, description="When set to true, restricts the user from collaborating on content with users outside the enterprise.")
    is_exempt_from_device_limits: bool | None = Field(default=None, description="When set to true, exempts the user from the enterprise-wide limit on the number of devices they can log in from.")
    is_exempt_from_login_verification: bool | None = Field(default=None, description="When set to true, exempts the user from the enterprise's two-factor authentication requirement at login.")
    status: Literal["active", "inactive", "cannot_delete_edit", "cannot_delete_edit_upload"] | None = Field(default=None, description="The initial account status for the user, controlling their ability to log in and interact with content.")
    external_app_user_id: str | None = Field(default=None, description="A custom identifier from an external identity provider that can be used to look up and map this Box user to an external system's user record.")
    name: dict | None = Field(default=None, description="The name of the user.", max_length=50)
    login: str | None = Field(default=None, description="The email address the user uses to log in\n\nRequired, unless `is_platform_access_only`\nis set to `true`.")
class PostUsersRequest(StrictModel):
    """Creates a new managed or app user within a Box enterprise account. Requires admin-level permissions on the calling user or application."""
    body: PostUsersRequestBody | None = None

# Operation: terminate_user_sessions
class PostUsersTerminateSessionsRequestBody(StrictModel):
    user_ids: list[str] | None = Field(default=None, description="A list of unique user IDs identifying the accounts whose sessions should be terminated. Order is not significant; each entry should be a valid numeric user ID string.")
    user_logins: list[str] | None = Field(default=None, description="A list of user login email addresses identifying the accounts whose sessions should be terminated. Order is not significant; each entry should be a valid email address associated with a user account.")
class PostUsersTerminateSessionsRequest(StrictModel):
    """Terminates active sessions for one or more users by dispatching asynchronous jobs, after validating the caller's roles and permissions. Accepts user IDs, user logins, or both to identify the target accounts."""
    body: PostUsersTerminateSessionsRequestBody | None = None

# Operation: get_user
class GetUsersIdRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose information you want to retrieve.")
class GetUsersIdRequest(StrictModel):
    """Retrieves profile and account information for a specific user within the enterprise. Also returns a limited set of fields for external collaborators, with restricted fields returning null."""
    path: GetUsersIdRequestPath

# Operation: update_user
class PutUsersIdRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to update.")
class PutUsersIdRequestBodyNotificationEmail(StrictModel):
    email: str | None = Field(default=None, validation_alias="email", serialization_alias="email", description="The email address to which enterprise notifications for this user will be sent.")
class PutUsersIdRequestBody(StrictModel):
    enterprise: str | None = Field(default=None, description="Set to null to remove the user from the enterprise and convert them to a free user.")
    notify: bool | None = Field(default=None, description="Whether the user should receive an email notification when they are rolled out of the enterprise.")
    name: str | None = Field(default=None, description="The display name of the user. Maximum 50 characters.", max_length=50)
    login: str | None = Field(default=None, description="The primary email address the user uses to log in. Cannot be changed if the target user's email address has not been confirmed.")
    role: Literal["coadmin", "user"] | None = Field(default=None, description="The user's role within the enterprise. Use 'coadmin' to grant co-administrator privileges or 'user' for a standard role.")
    language: str | None = Field(default=None, description="The user's preferred language, specified as a modified ISO 639-1 language code.")
    is_sync_enabled: bool | None = Field(default=None, description="Whether the user is permitted to use Box Sync to synchronize files to their local device.")
    job_title: str | None = Field(default=None, description="The user's job title as displayed on their profile. Maximum 100 characters.", max_length=100)
    phone: str | None = Field(default=None, description="The user's phone number. Maximum 100 characters.", max_length=100)
    address: str | None = Field(default=None, description="The user's physical address. Maximum 255 characters.", max_length=255)
    tracking_codes: list[TrackingCode] | None = Field(default=None, description="A list of tracking code objects assigned to the user, used by admins to generate reports and group users by attributes. This feature must be enabled for the enterprise before use.")
    can_see_managed_users: bool | None = Field(default=None, description="Whether the user can see other enterprise users in their contact list.")
    timezone_: str | None = Field(default=None, validation_alias="timezone", serialization_alias="timezone", description="The user's timezone, specified as a valid IANA timezone identifier.", json_schema_extra={'format': 'timezone'})
    is_external_collab_restricted: bool | None = Field(default=None, description="Whether the user is restricted from collaborating with users outside the enterprise. Set to true to block external collaboration.")
    is_exempt_from_device_limits: bool | None = Field(default=None, description="Whether the user is exempt from the enterprise-wide limit on the number of devices they can log in from.")
    is_exempt_from_login_verification: bool | None = Field(default=None, description="Whether the user is exempt from two-factor authentication requirements. Set to true to bypass login verification.")
    is_password_reset_required: bool | None = Field(default=None, description="Whether the user will be required to reset their password on their next login.")
    status: Literal["active", "inactive", "cannot_delete_edit", "cannot_delete_edit_upload"] | None = Field(default=None, description="The user's account status. Use 'inactive' to deactivate the account, or 'cannot_delete_edit'/'cannot_delete_edit_upload' to apply restrictions.")
    space_amount: int | None = Field(default=None, description="The user's total available storage quota in bytes. Set to -1 to grant unlimited storage.", json_schema_extra={'format': 'int64'})
    external_app_user_id: str | None = Field(default=None, description="An external identifier linking this Box app user to a user in an external identity provider. Can only be updated using a token from the application that originally created the app user.")
    notification_email: PutUsersIdRequestBodyNotificationEmail | None = None
class PutUsersIdRequest(StrictModel):
    """Updates profile, permissions, and account settings for a managed or app user within an enterprise. Requires admin-level permissions to execute."""
    path: PutUsersIdRequestPath
    body: PutUsersIdRequestBody | None = None

# Operation: delete_user
class DeleteUsersIdRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user to delete.")
class DeleteUsersIdRequestQuery(StrictModel):
    notify: bool | None = Field(default=None, description="Whether to send the user an email notification informing them of their account deletion.")
    force: bool | None = Field(default=None, description="When set to true, bypasses deletion safeguards and removes the user even if they still own files, were recently active, or recently joined the enterprise from a free account; their owned files will also be deleted.")
class DeleteUsersIdRequest(StrictModel):
    """Permanently deletes a user account from the enterprise. By default, deletion is blocked if the user owns content, was recently active, or recently joined from a free account; use the force parameter to override these safeguards or move owned content beforehand."""
    path: DeleteUsersIdRequestPath
    query: DeleteUsersIdRequestQuery | None = None

# Operation: get_user_avatar
class GetUsersIdAvatarRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose avatar image should be retrieved.")
class GetUsersIdAvatarRequest(StrictModel):
    """Retrieves the avatar image for a specified user. Returns the user's profile picture as an image resource."""
    path: GetUsersIdAvatarRequestPath

# Operation: upload_user_avatar
class PostUsersIdAvatarRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose avatar is being added or updated.")
class PostUsersIdAvatarRequestBody(StrictModel):
    pic: str | None = Field(default=None, description="The image file to upload as the user's avatar. Must be a JPG or PNG file and cannot exceed 1MB in size.", json_schema_extra={'format': 'binary'})
class PostUsersIdAvatarRequest(StrictModel):
    """Adds or replaces the avatar image for a specified user. Accepts JPG or PNG files up to 1MB in size."""
    path: PostUsersIdAvatarRequestPath
    body: PostUsersIdAvatarRequestBody | None = None

# Operation: delete_user_avatar
class DeleteUsersIdAvatarRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose avatar will be permanently deleted.")
class DeleteUsersIdAvatarRequest(StrictModel):
    """Permanently removes the avatar image for the specified user. This action is irreversible and cannot be undone."""
    path: DeleteUsersIdAvatarRequestPath

# Operation: transfer_user_folders
class PutUsersIdFolders0RequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose root folder and all owned content will be transferred.")
class PutUsersIdFolders0RequestQuery(StrictModel):
    notify: bool | None = Field(default=None, description="Whether to send email notifications to relevant users about the transfer action being performed.")
class PutUsersIdFolders0RequestBodyOwnedBy(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the destination user who will receive ownership of the transferred folders and files.")
class PutUsersIdFolders0RequestBody(StrictModel):
    owned_by: PutUsersIdFolders0RequestBodyOwnedBy | None = None
class PutUsersIdFolders0Request(StrictModel):
    """Transfers all files, folders, and workflows owned by a specified user into another user's account by moving the root folder. Requires administrative permissions; large transfers run asynchronously, and admins receive an email upon completion."""
    path: PutUsersIdFolders0RequestPath
    query: PutUsersIdFolders0RequestQuery | None = None
    body: PutUsersIdFolders0RequestBody | None = None

# Operation: list_user_email_aliases
class GetUsersIdEmailAliasesRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose email aliases should be retrieved.")
class GetUsersIdEmailAliasesRequest(StrictModel):
    """Retrieves all secondary email aliases associated with a specific user account. Note that the user's primary login email is not included in the returned collection."""
    path: GetUsersIdEmailAliasesRequestPath

# Operation: create_email_alias
class PostUsersIdEmailAliasesRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user account to which the email alias will be added.")
class PostUsersIdEmailAliasesRequestBody(StrictModel):
    email: str | None = Field(default=None, description="The email address to register as an alias on the user account. The domain portion must be verified and registered to your enterprise before use.")
class PostUsersIdEmailAliasesRequest(StrictModel):
    """Adds a new email alias to an existing user account, allowing the user to send and receive email under an additional address. The alias domain must be registered and verified under your enterprise."""
    path: PostUsersIdEmailAliasesRequestPath
    body: PostUsersIdEmailAliasesRequestBody | None = None

# Operation: remove_user_email_alias
class DeleteUsersIdEmailAliasesIdRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose email alias will be removed.")
    email_alias_id: str = Field(default=..., description="The unique identifier of the email alias to remove from the user.")
class DeleteUsersIdEmailAliasesIdRequest(StrictModel):
    """Removes a specific email alias from a user's account. Once removed, the alias can no longer be used to identify or contact the user."""
    path: DeleteUsersIdEmailAliasesIdRequestPath

# Operation: list_user_memberships
class GetUsersIdMembershipsRequestPath(StrictModel):
    user_id: str = Field(default=..., description="The unique identifier of the user whose group memberships are being retrieved.")
class GetUsersIdMembershipsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of group memberships to return per page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetUsersIdMembershipsRequest(StrictModel):
    """Retrieves all group memberships for a specified user. Accessible only to members of the same group or users with admin-level permissions."""
    path: GetUsersIdMembershipsRequestPath
    query: GetUsersIdMembershipsRequestQuery | None = None

# Operation: invite_enterprise_user
class PostInvitesRequestBodyEnterprise(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the enterprise to which the user is being invited.")
class PostInvitesRequestBodyActionableBy(StrictModel):
    login: str | None = Field(default=None, validation_alias="login", serialization_alias="login", description="The email address (login) of the existing Box user to invite to the enterprise.")
class PostInvitesRequestBody(StrictModel):
    enterprise: PostInvitesRequestBodyEnterprise | None = None
    actionable_by: PostInvitesRequestBodyActionableBy | None = None
class PostInvitesRequest(StrictModel):
    """Invites an existing Box user to join an enterprise by sending them an email prompt to accept within the Box web application. The user must already have a Box account and must not currently belong to another enterprise."""
    body: PostInvitesRequestBody | None = None

# Operation: get_invite
class GetInvitesIdRequestPath(StrictModel):
    invite_id: str = Field(default=..., description="The unique identifier of the invite whose status you want to retrieve.")
class GetInvitesIdRequest(StrictModel):
    """Retrieves the current status of a specific user invite. Useful for checking whether an invite has been accepted, is pending, or has expired."""
    path: GetInvitesIdRequestPath

# Operation: list_groups
class GetGroupsRequestQuery(StrictModel):
    filter_term: str | None = Field(default=None, description="Narrows results to only groups whose name begins with the specified search term. Omitting this parameter returns all groups.")
    limit: int | None = Field(default=None, description="Maximum number of groups to return in a single page of results. Accepts values between 1 and 1000.", json_schema_extra={'format': 'int64'})
    offset: int | None = Field(default=None, description="Zero-based index of the first item to include in the response, used for paginating through results. Offsets greater than 10000 are not permitted and will return a 400 error.", json_schema_extra={'format': 'int64'})
class GetGroupsRequest(StrictModel):
    """Retrieves all groups belonging to the enterprise, with optional filtering by name. Requires admin permissions to access enterprise group data."""
    query: GetGroupsRequestQuery | None = None

# Operation: create_group
class PostGroupsRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The display name for the new group, which must be unique across the entire enterprise.")
    provenance: str | None = Field(default=None, description="Identifies the external source system this group originates from (e.g., Active Directory or Okta). Setting this prevents Box admins from editing the group name or members via the Box web app, enabling one-way sync. Maximum 255 characters.", max_length=255)
    external_sync_identifier: str | None = Field(default=None, description="An arbitrary identifier used to link this Box group to a corresponding group in an external system, such as an Active Directory Object ID or Google Group ID. Using this field is recommended to prevent sync issues when group names change.")
    description: str | None = Field(default=None, description="A human-readable description providing additional context about the group's purpose or origin. Maximum 255 characters.", max_length=255)
    invitability_level: Literal["admins_only", "admins_and_members", "all_managed_users"] | None = Field(default=None, description="Controls who can invite this group to collaborate on folders. Use `admins_only` to restrict invitations to enterprise admins, co-admins, and the group's admin; `admins_and_members` to also allow group members; or `all_managed_users` to allow any managed user in the enterprise.")
    member_viewability_level: Literal["admins_only", "admins_and_members", "all_managed_users"] | None = Field(default=None, description="Controls who can view the membership list of this group. Use `admins_only` to restrict visibility to enterprise admins, co-admins, and the group's admin; `admins_and_members` to also allow group members; or `all_managed_users` to allow any managed user in the enterprise.")
class PostGroupsRequest(StrictModel):
    """Creates a new user group within an enterprise account. Requires admin permissions; supports linking to external directory systems like Active Directory or Okta for one-way sync."""
    body: PostGroupsRequestBody | None = None

# Operation: terminate_group_sessions
class PostGroupsTerminateSessionsRequestBody(StrictModel):
    group_ids: list[str] | None = Field(default=None, description="A list of group IDs whose sessions should be terminated. Order is not significant; each item should be a valid group ID string.")
class PostGroupsTerminateSessionsRequest(StrictModel):
    """Terminates all active sessions for one or more user groups by creating asynchronous jobs after validating group roles and permissions. Returns the status of the termination request."""
    body: PostGroupsTerminateSessionsRequestBody | None = None

# Operation: get_group
class GetGroupsIdRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group to retrieve.")
class GetGroupsIdRequest(StrictModel):
    """Retrieves detailed information about a specific group by its ID. Only group members or users with admin-level permissions can access this endpoint."""
    path: GetGroupsIdRequestPath

# Operation: update_group
class PutGroupsIdRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group to update.")
class PutGroupsIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The updated display name for the group, which must remain unique across the enterprise.")
    provenance: str | None = Field(default=None, description="Identifies the external source system this group originates from (e.g., Active Directory or Okta). Setting this value prevents Box admins from editing the group name or members directly in the Box web application, enabling one-way sync behavior. Maximum 255 characters.", max_length=255)
    external_sync_identifier: str | None = Field(default=None, description="An arbitrary identifier used to link this Box group to a corresponding group in an external system, such as an Active Directory Object ID or Google Group ID. Using this field is recommended to prevent sync issues when group names change in either system.")
    description: str | None = Field(default=None, description="A human-readable description providing additional context about the group's purpose or origin. Maximum 255 characters.", max_length=255)
    invitability_level: Literal["admins_only", "admins_and_members", "all_managed_users"] | None = Field(default=None, description="Controls who can invite this group to collaborate on folders. Use `admins_only` to restrict invitations to enterprise and group admins, `admins_and_members` to also allow group members, or `all_managed_users` to allow any managed user in the enterprise.")
    member_viewability_level: Literal["admins_only", "admins_and_members", "all_managed_users"] | None = Field(default=None, description="Controls who can view the membership list of this group. Use `admins_only` to restrict visibility to enterprise and group admins, `admins_and_members` to also allow group members, or `all_managed_users` to allow any managed user in the enterprise.")
class PutGroupsIdRequest(StrictModel):
    """Updates the properties of an existing group, such as its name, description, sync identifiers, and visibility settings. Only group admins or enterprise admins have permission to perform this operation."""
    path: PutGroupsIdRequestPath
    body: PutGroupsIdRequestBody | None = None

# Operation: delete_group
class DeleteGroupsIdRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group to be permanently deleted.")
class DeleteGroupsIdRequest(StrictModel):
    """Permanently deletes a group and all associated data. Requires admin-level permissions to perform this action."""
    path: DeleteGroupsIdRequestPath

# Operation: list_group_members
class GetGroupsIdMembershipsRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group whose members you want to retrieve.")
class GetGroupsIdMembershipsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of membership records to return per page. Accepts values up to 1000; omit to use the API default.", json_schema_extra={'format': 'int64'})
class GetGroupsIdMembershipsRequest(StrictModel):
    """Retrieves all membership records for a specified group, including details about each member. Accessible only to members of the group or users with admin-level permissions."""
    path: GetGroupsIdMembershipsRequestPath
    query: GetGroupsIdMembershipsRequestQuery | None = None

# Operation: list_group_collaborations
class GetGroupsIdCollaborationsRequestPath(StrictModel):
    group_id: str = Field(default=..., description="The unique identifier of the group whose collaborations you want to retrieve.")
class GetGroupsIdCollaborationsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of collaboration records to return per page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
    offset: int | None = Field(default=None, description="The zero-based index of the first item to include in the response, used for paginating through results. Offset values exceeding 10000 will result in a 400 error.", json_schema_extra={'format': 'int64'})
class GetGroupsIdCollaborationsRequest(StrictModel):
    """Retrieves all collaborations for a specified group, showing which files or folders the group can access and with what role. Requires admin permissions to inspect enterprise groups."""
    path: GetGroupsIdCollaborationsRequestPath
    query: GetGroupsIdCollaborationsRequestQuery | None = None

# Operation: add_user_to_group
class PostGroupMembershipsRequestBodyUser(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the user to be added to the group.")
class PostGroupMembershipsRequestBodyGroup(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the group the user will be added to.")
class PostGroupMembershipsRequestBody(StrictModel):
    role: Literal["member", "admin"] | None = Field(default=None, description="The role assigned to the user within the group. Use 'member' for standard access or 'admin' for elevated group management privileges.")
    configurable_permissions: dict[str, bool] | None = Field(default=None, description="Custom permission overrides for group admins only; has no effect on members with the 'member' role. Pass null to disable all configurable permissions, or specify individual permissions — any omitted permissions will default to enabled.")
    user: PostGroupMembershipsRequestBodyUser | None = None
    group: PostGroupMembershipsRequestBodyGroup | None = None
class PostGroupMembershipsRequest(StrictModel):
    """Adds a user to a group with a specified role and optional custom admin permissions. Requires admin-level permissions to perform this action."""
    body: PostGroupMembershipsRequestBody | None = None

# Operation: get_group_membership
class GetGroupMembershipsIdRequestPath(StrictModel):
    group_membership_id: str = Field(default=..., description="The unique identifier of the group membership record to retrieve.")
class GetGroupMembershipsIdRequest(StrictModel):
    """Retrieves details of a specific group membership by its unique ID. Only group admins or users with admin-level permissions can access this endpoint."""
    path: GetGroupMembershipsIdRequestPath

# Operation: update_group_membership
class PutGroupMembershipsIdRequestPath(StrictModel):
    group_membership_id: str = Field(default=..., description="The unique identifier of the group membership record to update.")
class PutGroupMembershipsIdRequestBody(StrictModel):
    role: Literal["member", "admin"] | None = Field(default=None, description="The role to assign to the user within the group. Accepted values are 'member' for standard access or 'admin' for elevated group management privileges.")
    configurable_permissions: dict[str, bool] | None = Field(default=None, description="A map of specific permission overrides for a group admin, replacing their default access levels. Only applies to users with the 'admin' role; has no effect on members. Pass null to disable all configurable permissions; omitted permissions default to enabled.")
class PutGroupMembershipsIdRequest(StrictModel):
    """Updates a user's role or permissions within a specific group membership. Only group admins or users with admin-level permissions can perform this action."""
    path: PutGroupMembershipsIdRequestPath
    body: PutGroupMembershipsIdRequestBody | None = None

# Operation: remove_group_member
class DeleteGroupMembershipsIdRequestPath(StrictModel):
    group_membership_id: str = Field(default=..., description="The unique identifier of the group membership record to delete, representing the association between a specific user and group.")
class DeleteGroupMembershipsIdRequest(StrictModel):
    """Removes a user from a group by deleting the specified group membership. Only group admins or users with admin-level permissions can perform this action."""
    path: DeleteGroupMembershipsIdRequestPath

# Operation: list_webhooks
class GetWebhooksRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of webhooks to return in a single page of results. Must be between 1 and 1000.", json_schema_extra={'format': 'int64'})
class GetWebhooksRequest(StrictModel):
    """Retrieves all webhooks defined for the authenticated application, scoped to files and folders owned by the requesting user. Note that admins cannot view webhooks created by service accounts unless they have explicit access to those folders, and vice versa."""
    query: GetWebhooksRequestQuery | None = None

# Operation: get_webhook
class GetWebhooksIdRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook to retrieve.")
class GetWebhooksIdRequest(StrictModel):
    """Retrieves the configuration and details of a specific webhook by its unique identifier. Useful for inspecting webhook settings, target URLs, and event subscriptions."""
    path: GetWebhooksIdRequestPath

# Operation: delete_webhook
class DeleteWebhooksIdRequestPath(StrictModel):
    webhook_id: str = Field(default=..., description="The unique identifier of the webhook to delete.")
class DeleteWebhooksIdRequest(StrictModel):
    """Permanently deletes a webhook by its unique identifier, stopping all future event notifications associated with it."""
    path: DeleteWebhooksIdRequestPath

# Operation: update_skill_cards_on_file
class PutSkillInvocationsIdRequestPath(StrictModel):
    skill_id: str = Field(default=..., description="The unique identifier of the Box Skill to apply metadata for. This determines which skill's cards are overwritten on the file.")
class PutSkillInvocationsIdRequestBodyMetadata(StrictModel):
    cards: list[SkillCard] | None = Field(default=None, validation_alias="cards", serialization_alias="cards", description="An ordered list of Box Skill cards to apply to the file. Each item should be a valid Skill card object (e.g., keyword, timeline, transcript, or status card); order determines how cards are stored and displayed.")
class PutSkillInvocationsIdRequestBodyFile(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the file on which the Skill cards will be applied.")
class PutSkillInvocationsIdRequestBodyFileVersion(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the specific file version to associate the Skill cards with. Use this to target a particular version rather than the current version of the file.")
class PutSkillInvocationsIdRequestBodyUsage(StrictModel):
    unit: str | None = Field(default=None, validation_alias="unit", serialization_alias="unit", description="The type of resource unit being referenced. This value is always 'file' for file-level Skill card operations.")
    value: float | None = Field(default=None, validation_alias="value", serialization_alias="value", description="The number of resources affected by this skill invocation. Typically reflects how many files or items the skill operation applies to.")
class PutSkillInvocationsIdRequestBody(StrictModel):
    status: Literal["invoked", "processing", "success", "transient_failure", "permanent_failure"] | None = Field(default=None, description="The current processing status of this skill invocation. Set to 'success' when providing completed Skill cards; use failure or processing states to reflect intermediate or error conditions. Accepted values are 'invoked', 'processing', 'success', 'transient_failure', or 'permanent_failure'.")
    metadata: PutSkillInvocationsIdRequestBodyMetadata | None = None
    file_: PutSkillInvocationsIdRequestBodyFile | None = Field(default=None, validation_alias="file", serialization_alias="file")
    file_version: PutSkillInvocationsIdRequestBodyFileVersion | None = None
    usage: PutSkillInvocationsIdRequestBodyUsage | None = None
class PutSkillInvocationsIdRequest(StrictModel):
    """Overwrites and updates all Box Skill metadata cards on a file for a given skill. Use this method to replace existing Skill cards with new ones in a single operation."""
    path: PutSkillInvocationsIdRequestPath
    body: PutSkillInvocationsIdRequestBody | None = None

# Operation: list_events
class GetEventsRequestQuery(StrictModel):
    stream_type: Literal["all", "changes", "sync", "admin_logs", "admin_logs_streaming"] | None = Field(default=None, description="Controls the scope and type of events returned. Use 'all' for the authenticated user's full event history, 'changes' or 'sync' for file-tree-affecting events, 'admin_logs' for paginated historical enterprise-wide events within a date range, or 'admin_logs_streaming' for low-latency polling of recent enterprise-wide events. Admin privileges are required for the 'admin_logs' and 'admin_logs_streaming' types.")
    stream_position: str | None = Field(default=None, description="The cursor position in the event stream from which to begin returning events. Use 'now' to initialize a stream and receive only the latest position with no events, or '0' / null to retrieve all available events from the beginning.")
    limit: int | None = Field(default=None, description="Maximum number of events to return per request, up to 500. Fewer events than requested may be returned even when more exist, as the API may return already-retrieved events rather than waiting for additional results.", json_schema_extra={'format': 'int64'})
    event_type: list[Literal["ACCESS_GRANTED", "ACCESS_REVOKED", "ADD_DEVICE_ASSOCIATION", "ADD_LOGIN_ACTIVITY_DEVICE", "ADMIN_LOGIN", "APPLICATION_CREATED", "APPLICATION_PUBLIC_KEY_ADDED", "APPLICATION_PUBLIC_KEY_DELETED", "CHANGE_ADMIN_ROLE", "CHANGE_FOLDER_PERMISSION", "COLLABORATION_ACCEPT", "COLLABORATION_EXPIRATION", "COLLABORATION_INVITE", "COLLABORATION_REMOVE", "COLLABORATION_ROLE_CHANGE", "COMMENT_CREATE", "COMMENT_DELETE", "CONTENT_WORKFLOW_ABNORMAL_DOWNLOAD_ACTIVITY", "CONTENT_WORKFLOW_AUTOMATION_ADD", "CONTENT_WORKFLOW_AUTOMATION_DELETE", "CONTENT_WORKFLOW_POLICY_ADD", "CONTENT_WORKFLOW_SHARING_POLICY_VIOLATION", "CONTENT_WORKFLOW_UPLOAD_POLICY_VIOLATION", "COPY", "DATA_RETENTION_CREATE_RETENTION", "DATA_RETENTION_REMOVE_RETENTION", "DELETE", "DELETE_USER", "DEVICE_TRUST_CHECK_FAILED", "DOWNLOAD", "EDIT", "EDIT_USER", "EMAIL_ALIAS_CONFIRM", "EMAIL_ALIAS_REMOVE", "ENTERPRISE_APP_AUTHORIZATION_UPDATE", "EXTERNAL_COLLAB_SECURITY_SETTINGS", "FAILED_LOGIN", "FILE_MARKED_MALICIOUS", "FILE_WATERMARKED_DOWNLOAD", "GROUP_ADD_ITEM", "GROUP_ADD_USER", "GROUP_CREATION", "GROUP_DELETION", "GROUP_EDITED", "GROUP_REMOVE_ITEM", "GROUP_REMOVE_USER", "ITEM_EMAIL_SEND", "ITEM_MODIFY", "ITEM_OPEN", "ITEM_SHARED_UPDATE", "ITEM_SYNC", "ITEM_UNSYNC", "LEGAL_HOLD_ASSIGNMENT_CREATE", "LEGAL_HOLD_ASSIGNMENT_DELETE", "LEGAL_HOLD_POLICY_CREATE", "LEGAL_HOLD_POLICY_DELETE", "LEGAL_HOLD_POLICY_UPDATE", "LOCK", "LOGIN", "METADATA_INSTANCE_CREATE", "METADATA_INSTANCE_DELETE", "METADATA_INSTANCE_UPDATE", "METADATA_TEMPLATE_CREATE", "METADATA_TEMPLATE_DELETE", "METADATA_TEMPLATE_UPDATE", "MOVE", "NEW_USER", "OAUTH2_ACCESS_TOKEN_REVOKE", "PREVIEW", "REMOVE_DEVICE_ASSOCIATION", "REMOVE_LOGIN_ACTIVITY_DEVICE", "RENAME", "RETENTION_POLICY_ASSIGNMENT_ADD", "SHARE", "SHARED_LINK_SEND", "SHARE_EXPIRATION", "SHIELD_ALERT", "SHIELD_EXTERNAL_COLLAB_ACCESS_BLOCKED", "SHIELD_EXTERNAL_COLLAB_ACCESS_BLOCKED_MISSING_JUSTIFICATION", "SHIELD_EXTERNAL_COLLAB_INVITE_BLOCKED", "SHIELD_EXTERNAL_COLLAB_INVITE_BLOCKED_MISSING_JUSTIFICATION", "SHIELD_JUSTIFICATION_APPROVAL", "SHIELD_SHARED_LINK_ACCESS_BLOCKED", "SHIELD_SHARED_LINK_STATUS_RESTRICTED_ON_CREATE", "SHIELD_SHARED_LINK_STATUS_RESTRICTED_ON_UPDATE", "SIGN_DOCUMENT_ASSIGNED", "SIGN_DOCUMENT_CANCELLED", "SIGN_DOCUMENT_COMPLETED", "SIGN_DOCUMENT_CONVERTED", "SIGN_DOCUMENT_CREATED", "SIGN_DOCUMENT_DECLINED", "SIGN_DOCUMENT_EXPIRED", "SIGN_DOCUMENT_SIGNED", "SIGN_DOCUMENT_VIEWED_BY_SIGNED", "SIGNER_DOWNLOADED", "SIGNER_FORWARDED", "STORAGE_EXPIRATION", "TASK_ASSIGNMENT_CREATE", "TASK_ASSIGNMENT_DELETE", "TASK_ASSIGNMENT_UPDATE", "TASK_CREATE", "TASK_UPDATE", "TERMS_OF_SERVICE_ACCEPT", "TERMS_OF_SERVICE_REJECT", "UNDELETE", "UNLOCK", "UNSHARE", "UPDATE_COLLABORATION_EXPIRATION", "UPDATE_SHARE_EXPIRATION", "UPLOAD", "USER_AUTHENTICATE_OAUTH2_ACCESS_TOKEN_CREATE", "WATERMARK_LABEL_CREATE", "WATERMARK_LABEL_DELETE"]] | None = Field(default=None, description="A list of specific event type strings to filter results by. Only applicable when 'stream_type' is 'admin_logs' or 'admin_logs_streaming'; ignored for all other stream types. Each item should be a valid Box event type identifier.")
    created_after: str | None = Field(default=None, description="The earliest date and time (inclusive) for which to return events, specified in ISO 8601 format. Only applicable when 'stream_type' is 'admin_logs'; ignored for all other stream types.", json_schema_extra={'format': 'date-time'})
    created_before: str | None = Field(default=None, description="The latest date and time (inclusive) for which to return events, specified in ISO 8601 format. Only applicable when 'stream_type' is 'admin_logs'; ignored for all other stream types.", json_schema_extra={'format': 'date-time'})
class GetEventsRequest(StrictModel):
    """Retrieves up to one year of past events for the authenticated user or, with admin privileges, for the entire enterprise. Supports both real-time polling and historical querying via configurable stream types."""
    query: GetEventsRequestQuery | None = None

# Operation: list_collections
class GetCollectionsRequestQuery(StrictModel):
    offset: int | None = Field(default=None, description="The zero-based index of the first item to include in the response, enabling pagination through large result sets. Offset values exceeding 10,000 will result in a 400 error.", json_schema_extra={'format': 'int64'})
    limit: int | None = Field(default=None, description="The maximum number of collections to return in a single response page. Accepts values up to 1,000.", json_schema_extra={'format': 'int64'})
class GetCollectionsRequest(StrictModel):
    """Retrieves all collections belonging to the authenticated user. Currently, only the favorites collection is supported."""
    query: GetCollectionsRequestQuery | None = None

# Operation: list_collection_items
class GetCollectionsIdItemsRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection whose items you want to retrieve.")
class GetCollectionsIdItemsRequestQuery(StrictModel):
    offset: int | None = Field(default=None, description="The zero-based index of the first item to return, enabling pagination through results. Must not exceed 10000; requests beyond this limit will be rejected with a 400 error.", json_schema_extra={'format': 'int64'})
    limit: int | None = Field(default=None, description="The maximum number of items to return in a single response page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetCollectionsIdItemsRequest(StrictModel):
    """Retrieves the files and folders contained within a specified collection. Supports pagination to navigate large result sets."""
    path: GetCollectionsIdItemsRequestPath
    query: GetCollectionsIdItemsRequestQuery | None = None

# Operation: get_collection
class GetCollectionsIdRequestPath(StrictModel):
    collection_id: str = Field(default=..., description="The unique identifier of the collection to retrieve.")
class GetCollectionsIdRequest(StrictModel):
    """Retrieves the details of a specific collection by its unique identifier. Use this to fetch metadata and contents associated with a single collection."""
    path: GetCollectionsIdRequestPath

# Operation: list_recent_items
class GetRecentItemsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of recently accessed items to return. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetRecentItemsRequest(StrictModel):
    """Retrieves a list of items recently accessed by the current user, covering activity from the last 90 days or up to the last 1000 items accessed, whichever limit is reached first."""
    query: GetRecentItemsRequestQuery | None = None

# Operation: list_retention_policies
class GetRetentionPoliciesRequestQuery(StrictModel):
    policy_name: str | None = Field(default=None, description="Filters results to only retention policies whose names begin with the specified string. The match is case-sensitive and prefix-based, so partial names from the start of the policy name are supported.")
    policy_type: Literal["finite", "indefinite"] | None = Field(default=None, description="Filters results by the retention policy type. Use 'finite' for policies with a defined expiration period, or 'indefinite' for policies that retain content without a set end date.")
    created_by_user_id: str | None = Field(default=None, description="Filters results to only policies created by the user with the specified user ID. Useful for auditing or managing policies owned by a particular administrator.")
    limit: int | None = Field(default=None, description="Limits the number of retention policies returned per page. Accepts values up to 1000; omitting this parameter returns the default page size.", json_schema_extra={'format': 'int64'})
class GetRetentionPoliciesRequest(StrictModel):
    """Retrieves all retention policies configured for the enterprise, with optional filtering by name, type, or creator. Useful for auditing data governance rules or locating specific policies before applying or modifying them."""
    query: GetRetentionPoliciesRequestQuery | None = None

# Operation: get_retention_policy
class GetRetentionPoliciesIdRequestPath(StrictModel):
    retention_policy_id: str = Field(default=..., description="The unique identifier of the retention policy to retrieve.")
class GetRetentionPoliciesIdRequest(StrictModel):
    """Retrieves the details of a specific retention policy by its unique identifier. Use this to inspect policy settings such as retention duration, disposition action, and assignment scope."""
    path: GetRetentionPoliciesIdRequestPath

# Operation: update_retention_policy
class PutRetentionPoliciesIdRequestPath(StrictModel):
    retention_policy_id: str = Field(default=..., description="The unique identifier of the retention policy to update.")
class PutRetentionPoliciesIdRequestBody(StrictModel):
    policy_name: str | None = Field(default=None, description="The updated display name for the retention policy.")
    description: str | None = Field(default=None, description="An optional extended text description providing additional context or purpose for the retention policy.")
    disposition_action: Literal["permanently_delete", "remove_retention"] | str | None = Field(default=None, description="The action taken when the retention period expires. Use 'permanently_delete' to destroy retained content or 'remove_retention' to lift the policy and allow user-initiated deletion. Pass null to leave the current disposition action unchanged.")
    retention_type: str | None = Field(default=None, description="The modifiability type of the retention policy. Only 'non-modifiable' can be set when updating; you may convert a modifiable policy to non-modifiable, but not the reverse. Non-modifiable policies support only limited changes to ensure regulatory compliance.")
    retention_length: str | None | float | None = Field(default=None, description="The number of days the retention policy remains active after being assigned to content. For indefinite policies, this value should also be 'indefinite'.")
    status: str | None = Field(default=None, description="Set to 'retired' to retire the retention policy. Omit this parameter or pass null if you are not retiring the policy.")
    can_owner_extend_retention: bool | None = Field(default=None, description="Whether the owner of items under this policy is permitted to extend the retention period as it approaches expiration.")
    are_owners_notified: bool | None = Field(default=None, description="Whether owners and co-owners of items under this policy receive notifications as the retention period approaches its end.")
    custom_notification_recipients: list[UserBase] | None = Field(default=None, description="An explicit list of additional users to notify when the retention duration is nearing expiration. Each item should represent a user recipient; order is not significant.")
class PutRetentionPoliciesIdRequest(StrictModel):
    """Updates an existing retention policy's settings, including its name, duration, disposition action, and notification preferences. You can also use this operation to retire a policy or convert it from modifiable to non-modifiable."""
    path: PutRetentionPoliciesIdRequestPath
    body: PutRetentionPoliciesIdRequestBody | None = None

# Operation: delete_retention_policy
class DeleteRetentionPoliciesIdRequestPath(StrictModel):
    retention_policy_id: str = Field(default=..., description="The unique identifier of the retention policy to permanently delete.")
class DeleteRetentionPoliciesIdRequest(StrictModel):
    """Permanently deletes a retention policy by its unique identifier. This action is irreversible and removes the policy and its associated settings."""
    path: DeleteRetentionPoliciesIdRequestPath

# Operation: list_retention_policy_assignments
class GetRetentionPoliciesIdAssignmentsRequestPath(StrictModel):
    retention_policy_id: str = Field(default=..., description="The unique identifier of the retention policy whose assignments you want to retrieve.")
class GetRetentionPoliciesIdAssignmentsRequestQuery(StrictModel):
    type_: Literal["folder", "enterprise", "metadata_template"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Filters the results to only return assignments of a specific type. Accepted values are 'folder', 'enterprise', or 'metadata_template'.")
    limit: int | None = Field(default=None, description="The maximum number of assignments to return in a single page of results. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetRetentionPoliciesIdAssignmentsRequest(StrictModel):
    """Retrieves all assignments for a specified retention policy, showing which folders, enterprise, or metadata templates the policy is applied to. Optionally filter results by assignment type and control page size."""
    path: GetRetentionPoliciesIdAssignmentsRequestPath
    query: GetRetentionPoliciesIdAssignmentsRequestQuery | None = None

# Operation: assign_retention_policy
class PostRetentionPolicyAssignmentsRequestBodyAssignTo(StrictModel):
    type_: Literal["enterprise", "folder", "metadata_template"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The category of item the retention policy will be assigned to. Use 'enterprise' to apply policy-wide, 'folder' for a specific folder, or 'metadata_template' to target items matching a metadata template.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the specific folder or metadata template to assign the policy to. Omit or set to null when assigning to the entire enterprise.")
class PostRetentionPolicyAssignmentsRequestBody(StrictModel):
    policy_id: str | None = Field(default=None, description="The unique identifier of the retention policy to assign to the target item.")
    filter_fields: list[PostRetentionPolicyAssignmentsBodyFilterFieldsItem] | None = Field(default=None, description="An array of field-value filter objects used to narrow the assignment when the target type is 'metadata_template'. Each object must contain a 'field' key and a 'value' key; currently only one filter object is supported.")
    start_date_field: str | None = Field(default=None, description="The date from which the retention policy assignment takes effect. When the target type is 'metadata_template', this can reference a date-type metadata attribute key ID to dynamically determine the start date.")
    assign_to: PostRetentionPolicyAssignmentsRequestBodyAssignTo | None = None
class PostRetentionPolicyAssignmentsRequest(StrictModel):
    """Assigns a retention policy to a specific target, such as a folder, enterprise, or metadata template. Use this to enforce data retention rules on content within Box."""
    body: PostRetentionPolicyAssignmentsRequestBody | None = None

# Operation: get_retention_policy_assignment
class GetRetentionPolicyAssignmentsIdRequestPath(StrictModel):
    retention_policy_assignment_id: str = Field(default=..., description="The unique identifier of the retention policy assignment to retrieve.")
class GetRetentionPolicyAssignmentsIdRequest(StrictModel):
    """Retrieves the details of a specific retention policy assignment by its unique ID. Use this to inspect how a retention policy has been applied to a particular content target."""
    path: GetRetentionPolicyAssignmentsIdRequestPath

# Operation: delete_retention_policy_assignment
class DeleteRetentionPolicyAssignmentsIdRequestPath(StrictModel):
    retention_policy_assignment_id: str = Field(default=..., description="The unique identifier of the retention policy assignment to remove.")
class DeleteRetentionPolicyAssignmentsIdRequest(StrictModel):
    """Removes a retention policy assignment, detaching the retention policy from the previously assigned content. This action stops the policy from being enforced on that content going forward."""
    path: DeleteRetentionPolicyAssignmentsIdRequestPath

# Operation: list_files_under_retention
class GetRetentionPolicyAssignmentsIdFilesUnderRetentionRequestPath(StrictModel):
    retention_policy_assignment_id: str = Field(default=..., description="The unique identifier of the retention policy assignment whose retained files you want to retrieve.")
class GetRetentionPolicyAssignmentsIdFilesUnderRetentionRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of files to return per page. Accepts values up to 1000; omit to use the API default.", json_schema_extra={'format': 'int64'})
class GetRetentionPolicyAssignmentsIdFilesUnderRetentionRequest(StrictModel):
    """Retrieves a paginated list of files currently under retention for a specific retention policy assignment. Useful for auditing which files are actively governed by a given retention rule."""
    path: GetRetentionPolicyAssignmentsIdFilesUnderRetentionRequestPath
    query: GetRetentionPolicyAssignmentsIdFilesUnderRetentionRequestQuery | None = None

# Operation: list_file_versions_under_retention
class GetRetentionPolicyAssignmentsIdFileVersionsUnderRetentionRequestPath(StrictModel):
    retention_policy_assignment_id: str = Field(default=..., description="The unique identifier of the retention policy assignment whose retained file versions you want to retrieve.")
class GetRetentionPolicyAssignmentsIdFileVersionsUnderRetentionRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of file version records to return per page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetRetentionPolicyAssignmentsIdFileVersionsUnderRetentionRequest(StrictModel):
    """Retrieves a paginated list of file versions currently under retention for a specific retention policy assignment. Useful for auditing which file versions are being preserved by a given policy."""
    path: GetRetentionPolicyAssignmentsIdFileVersionsUnderRetentionRequestPath
    query: GetRetentionPolicyAssignmentsIdFileVersionsUnderRetentionRequestQuery | None = None

# Operation: list_legal_hold_policies
class GetLegalHoldPoliciesRequestQuery(StrictModel):
    policy_name: str | None = Field(default=None, description="Filters results to only include policies whose names begin with this search term. The match is case-insensitive.")
    limit: int | None = Field(default=None, description="The maximum number of legal hold policies to return in a single page of results. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetLegalHoldPoliciesRequest(StrictModel):
    """Retrieves all legal hold policies belonging to the enterprise. Supports filtering by policy name prefix to narrow results."""
    query: GetLegalHoldPoliciesRequestQuery | None = None

# Operation: get_legal_hold_policy
class GetLegalHoldPoliciesIdRequestPath(StrictModel):
    legal_hold_policy_id: str = Field(default=..., description="The unique identifier of the legal hold policy to retrieve.")
class GetLegalHoldPoliciesIdRequest(StrictModel):
    """Retrieves the details of a specific legal hold policy by its unique identifier. Use this to inspect policy configuration, status, and associated metadata."""
    path: GetLegalHoldPoliciesIdRequestPath

# Operation: update_legal_hold_policy
class PutLegalHoldPoliciesIdRequestPath(StrictModel):
    legal_hold_policy_id: str = Field(default=..., description="The unique identifier of the legal hold policy to update.")
class PutLegalHoldPoliciesIdRequestBody(StrictModel):
    policy_name: str | None = Field(default=None, description="The updated display name for the legal hold policy. Must not exceed 254 characters.", max_length=254)
    description: str | None = Field(default=None, description="An updated human-readable description of the legal hold policy's purpose or scope. Must not exceed 500 characters.", max_length=500)
    release_notes: str | None = Field(default=None, description="Notes explaining the reason or context for releasing this legal hold policy. Must not exceed 500 characters.", max_length=500)
class PutLegalHoldPoliciesIdRequest(StrictModel):
    """Updates the name, description, or release notes of an existing legal hold policy. Use this to modify policy details after creation without affecting associated holds."""
    path: PutLegalHoldPoliciesIdRequestPath
    body: PutLegalHoldPoliciesIdRequestBody | None = None

# Operation: delete_legal_hold_policy
class DeleteLegalHoldPoliciesIdRequestPath(StrictModel):
    legal_hold_policy_id: str = Field(default=..., description="The unique identifier of the legal hold policy to delete.")
class DeleteLegalHoldPoliciesIdRequest(StrictModel):
    """Deletes an existing legal hold policy by its ID. This is an asynchronous operation, so the policy may not be fully removed immediately when the response is returned."""
    path: DeleteLegalHoldPoliciesIdRequestPath

# Operation: list_legal_hold_policy_assignments
class GetLegalHoldPolicyAssignmentsRequestQuery(StrictModel):
    policy_id: str = Field(default=..., description="The unique identifier of the legal hold policy whose assignments you want to retrieve.")
    assign_to_type: Literal["file", "file_version", "folder", "user", "ownership", "interactions"] | None = Field(default=None, description="Narrows results to only assignments targeting a specific item type. Accepted values are 'file', 'file_version', 'folder', 'user', 'ownership', or 'interactions'.")
    assign_to_id: str | None = Field(default=None, description="Narrows results to only assignments targeting a specific item by its unique ID. Best used in combination with assign_to_type for precise filtering.")
    limit: int | None = Field(default=None, description="The maximum number of assignments to return in a single page of results. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetLegalHoldPolicyAssignmentsRequest(StrictModel):
    """Retrieves a list of all items (files, folders, users, etc.) that a specific legal hold policy has been assigned to. Supports filtering by item type and item ID for targeted lookups."""
    query: GetLegalHoldPolicyAssignmentsRequestQuery

# Operation: assign_legal_hold_policy
class PostLegalHoldPolicyAssignmentsRequestBodyAssignTo(StrictModel):
    type_: Literal["file", "file_version", "folder", "user", "ownership", "interactions"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The category of item to which the legal hold policy will be applied. Must be one of: file, file_version, folder, user, ownership, or interactions.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the specific item (file, folder, user, etc.) to which the legal hold policy will be assigned.")
class PostLegalHoldPolicyAssignmentsRequestBody(StrictModel):
    policy_id: str | None = Field(default=None, description="The unique identifier of the legal hold policy to assign to the target item.")
    assign_to: PostLegalHoldPolicyAssignmentsRequestBodyAssignTo | None = None
class PostLegalHoldPolicyAssignmentsRequest(StrictModel):
    """Assigns a legal hold policy to a specific item, such as a file, file version, folder, user, ownership, or interactions. Use this to enforce legal holds across different content types within Box."""
    body: PostLegalHoldPolicyAssignmentsRequestBody | None = None

# Operation: get_legal_hold_policy_assignment
class GetLegalHoldPolicyAssignmentsIdRequestPath(StrictModel):
    legal_hold_policy_assignment_id: str = Field(default=..., description="The unique identifier of the legal hold policy assignment to retrieve.")
class GetLegalHoldPolicyAssignmentsIdRequest(StrictModel):
    """Retrieves the details of a specific legal hold policy assignment by its unique ID. Use this to inspect which users, folders, or files are bound to a particular legal hold policy."""
    path: GetLegalHoldPolicyAssignmentsIdRequestPath

# Operation: remove_legal_hold_policy_assignment
class DeleteLegalHoldPolicyAssignmentsIdRequestPath(StrictModel):
    legal_hold_policy_assignment_id: str = Field(default=..., description="The unique identifier of the legal hold policy assignment to remove.")
class DeleteLegalHoldPolicyAssignmentsIdRequest(StrictModel):
    """Removes a legal hold policy assignment from an item, unlinking the policy from the associated content. This is an asynchronous operation; the hold may not be fully released by the time the response is returned."""
    path: DeleteLegalHoldPolicyAssignmentsIdRequestPath

# Operation: list_legal_hold_assignment_files
class GetLegalHoldPolicyAssignmentsIdFilesOnHoldRequestPath(StrictModel):
    legal_hold_policy_assignment_id: str = Field(default=..., description="The unique identifier of the legal hold policy assignment whose held files you want to retrieve.")
class GetLegalHoldPolicyAssignmentsIdFilesOnHoldRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of files to return per page, up to a maximum of 1000.", json_schema_extra={'format': 'int64'})
class GetLegalHoldPolicyAssignmentsIdFilesOnHoldRequest(StrictModel):
    """Retrieves a paginated list of files with their current file versions held under a specific legal hold policy assignment. For previous file versions on hold, use the file versions on hold endpoint instead."""
    path: GetLegalHoldPolicyAssignmentsIdFilesOnHoldRequestPath
    query: GetLegalHoldPolicyAssignmentsIdFilesOnHoldRequestQuery | None = None

# Operation: list_legal_hold_assignment_file_versions
class GetLegalHoldPolicyAssignmentsIdFileVersionsOnHoldRequestPath(StrictModel):
    legal_hold_policy_assignment_id: str = Field(default=..., description="The unique identifier of the legal hold policy assignment whose past file versions on hold should be retrieved.")
class GetLegalHoldPolicyAssignmentsIdFileVersionsOnHoldRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of file version records to return per page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetLegalHoldPolicyAssignmentsIdFileVersionsOnHoldRequest(StrictModel):
    """Retrieves a paginated list of previous (past) file versions placed on hold for a specific legal hold policy assignment. Use this endpoint for historical file versions; for current file versions on hold, use the files_on_hold endpoint instead."""
    path: GetLegalHoldPolicyAssignmentsIdFileVersionsOnHoldRequestPath
    query: GetLegalHoldPolicyAssignmentsIdFileVersionsOnHoldRequestQuery | None = None

# Operation: get_file_version_legal_hold
class GetFileVersionLegalHoldsIdRequestPath(StrictModel):
    file_version_legal_hold_id: str = Field(default=..., description="The unique identifier of the file version legal hold record to retrieve.")
class GetFileVersionLegalHoldsIdRequest(StrictModel):
    """Retrieves details about the legal hold policies assigned to a specific file version. Use this to inspect which legal holds are actively applied to a given file version."""
    path: GetFileVersionLegalHoldsIdRequestPath

# Operation: list_file_version_legal_holds
class GetFileVersionLegalHoldsRequestQuery(StrictModel):
    policy_id: str = Field(default=..., description="The unique identifier of the legal hold policy whose file version holds you want to retrieve.")
    limit: int | None = Field(default=None, description="The maximum number of file version legal hold records to return in a single page of results; must be between 1 and 1000.", json_schema_extra={'format': 'int64'})
class GetFileVersionLegalHoldsRequest(StrictModel):
    """Retrieves file versions currently held under a specific legal hold policy, covering legacy-architecture holds only. For holds in the new architecture, use the legal hold policy assignment endpoints instead."""
    query: GetFileVersionLegalHoldsRequestQuery

# Operation: get_information_barrier
class GetShieldInformationBarriersIdRequestPath(StrictModel):
    shield_information_barrier_id: str = Field(default=..., description="The unique identifier of the shield information barrier to retrieve.")
class GetShieldInformationBarriersIdRequest(StrictModel):
    """Retrieves details of a specific shield information barrier by its unique ID. Useful for inspecting the configuration and status of an existing barrier between user groups."""
    path: GetShieldInformationBarriersIdRequestPath

# Operation: update_shield_barrier_status
class PostShieldInformationBarriersChangeStatusRequestBody(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the shield information barrier whose status you want to change.")
    status: Literal["pending", "disabled"] | None = Field(default=None, description="The target status to apply to the shield information barrier. Accepted values are 'pending' (barrier is queued for activation) or 'disabled' (barrier is turned off).")
class PostShieldInformationBarriersChangeStatusRequest(StrictModel):
    """Changes the status of a shield information barrier to control its enforcement state. Use this to activate, suspend, or disable an existing barrier by its unique ID."""
    body: PostShieldInformationBarriersChangeStatusRequestBody | None = None

# Operation: list_shield_information_barriers
class GetShieldInformationBarriersRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of shield information barrier records to return in a single page of results. Must be between 1 and 1000.", json_schema_extra={'format': 'int64'})
class GetShieldInformationBarriersRequest(StrictModel):
    """Retrieves all shield information barriers configured for the enterprise associated with the JWT token. Shield information barriers restrict communication and data access between internal groups."""
    query: GetShieldInformationBarriersRequestQuery | None = None

# Operation: create_shield_information_barrier
class PostShieldInformationBarriersRequestBody(StrictModel):
    enterprise: PostShieldInformationBarriersBodyEnterprise | None = Field(default=None, description="The type and ID of the enterprise under which this shield information barrier will be created.")
class PostShieldInformationBarriersRequest(StrictModel):
    """Creates a shield information barrier within an enterprise to separate individuals or groups and prevent confidential information from passing between them. Use this to enforce ethical walls or compliance boundaries within the same firm."""
    body: PostShieldInformationBarriersRequestBody | None = None

# Operation: list_barrier_reports
class GetShieldInformationBarrierReportsRequestQuery(StrictModel):
    shield_information_barrier_id: str = Field(default=..., description="The unique identifier of the shield information barrier whose reports should be listed.")
    limit: int | None = Field(default=None, description="The maximum number of reports to return per page. Accepts values up to 1000; omit to use the server default.", json_schema_extra={'format': 'int64'})
class GetShieldInformationBarrierReportsRequest(StrictModel):
    """Retrieves a paginated list of shield information barrier reports associated with a specific barrier. Use this to audit or review compliance reports generated for a given information barrier."""
    query: GetShieldInformationBarrierReportsRequestQuery

# Operation: create_barrier_report
class PostShieldInformationBarrierReportsRequestBodyShieldInformationBarrier(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the shield information barrier for which the report will be generated.")
    type_: Literal["shield_information_barrier"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The resource type of the shield information barrier being referenced. Must be set to the designated barrier type value.")
class PostShieldInformationBarrierReportsRequestBody(StrictModel):
    shield_information_barrier: PostShieldInformationBarrierReportsRequestBodyShieldInformationBarrier | None = None
class PostShieldInformationBarrierReportsRequest(StrictModel):
    """Generates a compliance report for a specified shield information barrier, providing a snapshot of the barrier's configuration and activity. Useful for auditing and regulatory review of information separation policies."""
    body: PostShieldInformationBarrierReportsRequestBody | None = None

# Operation: get_barrier_report
class GetShieldInformationBarrierReportsIdRequestPath(StrictModel):
    shield_information_barrier_report_id: str = Field(default=..., description="The unique identifier of the shield information barrier report to retrieve.")
class GetShieldInformationBarrierReportsIdRequest(StrictModel):
    """Retrieves a specific shield information barrier report by its unique ID. Use this to fetch the status and details of a previously created compliance barrier report."""
    path: GetShieldInformationBarrierReportsIdRequestPath

# Operation: get_barrier_segment
class GetShieldInformationBarrierSegmentsIdRequestPath(StrictModel):
    shield_information_barrier_segment_id: str = Field(default=..., description="The unique identifier of the shield information barrier segment to retrieve.")
class GetShieldInformationBarrierSegmentsIdRequest(StrictModel):
    """Retrieves the details of a specific shield information barrier segment by its unique ID. Shield information barrier segments define the boundaries that restrict information flow between groups within an organization."""
    path: GetShieldInformationBarrierSegmentsIdRequestPath

# Operation: update_barrier_segment
class PutShieldInformationBarrierSegmentsIdRequestPath(StrictModel):
    shield_information_barrier_segment_id: str = Field(default=..., description="The unique identifier of the shield information barrier segment to update.")
class PutShieldInformationBarrierSegmentsIdRequestBody(StrictModel):
    name: str | None = Field(default=None, description="The new name to assign to the barrier segment. Must contain at least one non-whitespace character.", pattern='\\S+')
    description: str | None = Field(default=None, description="The new description to assign to the barrier segment, providing context about its purpose or the division it represents.")
class PutShieldInformationBarrierSegmentsIdRequest(StrictModel):
    """Updates the name and/or description of a specific shield information barrier segment by its ID. Use this to modify segment metadata without affecting its underlying barrier configuration."""
    path: PutShieldInformationBarrierSegmentsIdRequestPath
    body: PutShieldInformationBarrierSegmentsIdRequestBody | None = None

# Operation: delete_barrier_segment
class DeleteShieldInformationBarrierSegmentsIdRequestPath(StrictModel):
    shield_information_barrier_segment_id: str = Field(default=..., description="The unique identifier of the shield information barrier segment to delete.")
class DeleteShieldInformationBarrierSegmentsIdRequest(StrictModel):
    """Permanently deletes a shield information barrier segment by its unique ID. This action removes the segment and its associated configurations from the information barrier."""
    path: DeleteShieldInformationBarrierSegmentsIdRequestPath

# Operation: list_barrier_segments
class GetShieldInformationBarrierSegmentsRequestQuery(StrictModel):
    shield_information_barrier_id: str = Field(default=..., description="The unique identifier of the shield information barrier whose segments you want to retrieve.")
    limit: int | None = Field(default=None, description="The maximum number of barrier segment objects to return in a single page of results. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetShieldInformationBarrierSegmentsRequest(StrictModel):
    """Retrieves all shield information barrier segments associated with a specified information barrier. Segments define the groups or users separated by the barrier."""
    query: GetShieldInformationBarrierSegmentsRequestQuery

# Operation: create_barrier_segment
class PostShieldInformationBarrierSegmentsRequestBodyShieldInformationBarrier(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the parent shield information barrier under which this segment will be created.")
    type_: Literal["shield_information_barrier"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The resource type of the associated shield information barrier; must be set to the designated barrier type value.")
class PostShieldInformationBarrierSegmentsRequestBody(StrictModel):
    name: str | None = Field(default=None, description="A human-readable name for the barrier segment that identifies the division or group being isolated.")
    description: str | None = Field(default=None, description="An optional narrative description providing additional context about the barrier segment's purpose or the division it represents.")
    shield_information_barrier: PostShieldInformationBarrierSegmentsRequestBodyShieldInformationBarrier | None = None
class PostShieldInformationBarrierSegmentsRequest(StrictModel):
    """Creates a named segment within an existing shield information barrier, allowing organizations to define distinct groups or divisions for information separation and compliance purposes."""
    body: PostShieldInformationBarrierSegmentsRequestBody | None = None

# Operation: get_barrier_segment_member
class GetShieldInformationBarrierSegmentMembersIdRequestPath(StrictModel):
    shield_information_barrier_segment_member_id: str = Field(default=..., description="The unique identifier of the shield information barrier segment member to retrieve.")
class GetShieldInformationBarrierSegmentMembersIdRequest(StrictModel):
    """Retrieves a specific shield information barrier segment member by its unique ID. Useful for inspecting the details of an individual member assigned to a barrier segment."""
    path: GetShieldInformationBarrierSegmentMembersIdRequestPath

# Operation: delete_barrier_segment_member
class DeleteShieldInformationBarrierSegmentMembersIdRequestPath(StrictModel):
    shield_information_barrier_segment_member_id: str = Field(default=..., description="The unique identifier of the shield information barrier segment member to delete.")
class DeleteShieldInformationBarrierSegmentMembersIdRequest(StrictModel):
    """Permanently removes a specific member from a shield information barrier segment. Use this to revoke a user's association with a segment when access restrictions need to be updated."""
    path: DeleteShieldInformationBarrierSegmentMembersIdRequestPath

# Operation: list_barrier_segment_members
class GetShieldInformationBarrierSegmentMembersRequestQuery(StrictModel):
    shield_information_barrier_segment_id: str = Field(default=..., description="The unique identifier of the shield information barrier segment whose members you want to retrieve.")
    limit: int | None = Field(default=None, description="The maximum number of segment members to return in a single page of results. Must be between 1 and 1000.", json_schema_extra={'format': 'int64'})
class GetShieldInformationBarrierSegmentMembersRequest(StrictModel):
    """Retrieves a paginated list of members belonging to a specific shield information barrier segment. Use this to audit or review which users are assigned to a given segment."""
    query: GetShieldInformationBarrierSegmentMembersRequestQuery

# Operation: add_barrier_segment_member
class PostShieldInformationBarrierSegmentMembersRequestBodyShieldInformationBarrier(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the shield information barrier that the target segment belongs to.")
class PostShieldInformationBarrierSegmentMembersRequestBodyShieldInformationBarrierSegment(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the shield information barrier segment to which the user will be added as a member.")
class PostShieldInformationBarrierSegmentMembersRequestBody(StrictModel):
    user: PostShieldInformationBarrierSegmentMembersBodyUser | None = Field(default=None, description="The user object representing the individual to whom the segment's information barrier restrictions will be applied.")
    shield_information_barrier: PostShieldInformationBarrierSegmentMembersRequestBodyShieldInformationBarrier | None = None
    shield_information_barrier_segment: PostShieldInformationBarrierSegmentMembersRequestBodyShieldInformationBarrierSegment | None = None
class PostShieldInformationBarrierSegmentMembersRequest(StrictModel):
    """Adds a user as a member of a shield information barrier segment, applying the segment's information restrictions to that user."""
    body: PostShieldInformationBarrierSegmentMembersRequestBody | None = None

# Operation: get_barrier_segment_restriction
class GetShieldInformationBarrierSegmentRestrictionsIdRequestPath(StrictModel):
    shield_information_barrier_segment_restriction_id: str = Field(default=..., description="The unique identifier of the shield information barrier segment restriction to retrieve.")
class GetShieldInformationBarrierSegmentRestrictionsIdRequest(StrictModel):
    """Retrieves a specific shield information barrier segment restriction by its unique ID. Use this to inspect the details of an existing restriction between two information barrier segments."""
    path: GetShieldInformationBarrierSegmentRestrictionsIdRequestPath

# Operation: list_barrier_segment_restrictions
class GetShieldInformationBarrierSegmentRestrictionsRequestQuery(StrictModel):
    shield_information_barrier_segment_id: str = Field(default=..., description="The unique identifier of the shield information barrier segment whose restrictions you want to list.")
    limit: int | None = Field(default=None, description="The maximum number of restriction records to return in a single page of results. Must be between 1 and 1000.", json_schema_extra={'format': 'int64'})
class GetShieldInformationBarrierSegmentRestrictionsRequest(StrictModel):
    """Retrieves all shield information barrier segment restrictions associated with a specific segment. Use this to audit or review access restrictions applied to a given barrier segment."""
    query: GetShieldInformationBarrierSegmentRestrictionsRequestQuery

# Operation: get_device_pin
class GetDevicePinnersIdRequestPath(StrictModel):
    device_pinner_id: str = Field(default=..., description="The unique identifier of the device pin to retrieve.")
class GetDevicePinnersIdRequest(StrictModel):
    """Retrieves detailed information about a specific device pin by its unique identifier. Useful for inspecting the status and metadata of an individual device pinning record."""
    path: GetDevicePinnersIdRequestPath

# Operation: delete_device_pin
class DeleteDevicePinnersIdRequestPath(StrictModel):
    device_pinner_id: str = Field(default=..., description="The unique identifier of the device pin to delete.")
class DeleteDevicePinnersIdRequest(StrictModel):
    """Permanently removes a specific device pin, revoking the trusted device association for the corresponding user. This action cannot be undone."""
    path: DeleteDevicePinnersIdRequestPath

# Operation: list_enterprise_device_pins
class GetEnterprisesIdDevicePinnersRequestPath(StrictModel):
    enterprise_id: str = Field(default=..., description="The unique identifier of the enterprise whose device pins you want to retrieve.")
class GetEnterprisesIdDevicePinnersRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of device pins to return per page, up to a maximum of 1000.", json_schema_extra={'format': 'int64'})
    direction: Literal["ASC", "DESC"] | None = Field(default=None, description="The sort order for the returned results, either ascending (ASC) or descending (DESC) alphabetical order.")
class GetEnterprisesIdDevicePinnersRequest(StrictModel):
    """Retrieves all device pins registered within a specified enterprise. Requires admin privileges and the 'manage enterprise' application scope."""
    path: GetEnterprisesIdDevicePinnersRequestPath
    query: GetEnterprisesIdDevicePinnersRequestQuery | None = None

# Operation: list_terms_of_service_user_statuses
class GetTermsOfServiceUserStatusesRequestQuery(StrictModel):
    tos_id: str = Field(default=..., description="The unique identifier of the terms of service whose user acceptance statuses should be retrieved.")
    user_id: str | None = Field(default=None, description="When provided, restricts the results to the acceptance status of a single user matching this ID.")
class GetTermsOfServiceUserStatusesRequest(StrictModel):
    """Retrieves the acceptance status of users for a specific terms of service, including whether each user has accepted the terms and the timestamp of their response. Optionally filter results to a single user."""
    query: GetTermsOfServiceUserStatusesRequestQuery

# Operation: create_terms_of_service_user_status
class PostTermsOfServiceUserStatusesRequestBodyTos(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the terms of service document to associate with the user status.")
class PostTermsOfServiceUserStatusesRequestBodyUser(StrictModel):
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the user whose terms of service acceptance status is being recorded.")
class PostTermsOfServiceUserStatusesRequestBody(StrictModel):
    is_accepted: bool | None = Field(default=None, description="Indicates whether the user has accepted the terms of service; set to true if accepted, false if declined.")
    tos: PostTermsOfServiceUserStatusesRequestBodyTos | None = None
    user: PostTermsOfServiceUserStatusesRequestBodyUser | None = None
class PostTermsOfServiceUserStatusesRequest(StrictModel):
    """Creates or sets the acceptance status of a terms of service agreement for a specific user. Use this to record whether a new user has accepted or declined a given terms of service."""
    body: PostTermsOfServiceUserStatusesRequestBody | None = None

# Operation: update_terms_of_service_user_status
class PutTermsOfServiceUserStatusesIdRequestPath(StrictModel):
    terms_of_service_user_status_id: str = Field(default=..., description="The unique identifier of the terms of service user status record to update.")
class PutTermsOfServiceUserStatusesIdRequestBody(StrictModel):
    is_accepted: bool | None = Field(default=None, description="Indicates whether the user has accepted the terms of service; set to true to mark acceptance or false to mark rejection.")
class PutTermsOfServiceUserStatusesIdRequest(StrictModel):
    """Updates the acceptance status of a terms of service agreement for a specific user. Use this to record whether a user has accepted or declined a terms of service."""
    path: PutTermsOfServiceUserStatusesIdRequestPath
    body: PutTermsOfServiceUserStatusesIdRequestBody | None = None

# Operation: get_collaboration_whitelist_entry
class GetCollaborationWhitelistEntriesIdRequestPath(StrictModel):
    collaboration_whitelist_entry_id: str = Field(default=..., description="The unique identifier of the collaboration whitelist entry to retrieve.")
class GetCollaborationWhitelistEntriesIdRequest(StrictModel):
    """Retrieves a specific domain that has been approved for external collaborations within the current enterprise. Use this to inspect the details of a single whitelisted domain entry by its unique ID."""
    path: GetCollaborationWhitelistEntriesIdRequestPath

# Operation: list_storage_policy_assignments
class GetStoragePolicyAssignmentsRequestQuery(StrictModel):
    resolved_for_type: Literal["user", "enterprise"] = Field(default=..., description="The type of entity to retrieve storage policy assignments for, either a specific user or an entire enterprise.")
    resolved_for_id: str = Field(default=..., description="The unique identifier of the user or enterprise whose storage policy assignments should be retrieved. Must correspond to the entity type specified in resolved_for_type.")
class GetStoragePolicyAssignmentsRequest(StrictModel):
    """Retrieves all storage policy assignments for a specified enterprise or user. Returns the storage policies currently assigned to the given target."""
    query: GetStoragePolicyAssignmentsRequestQuery

# Operation: assign_storage_policy
class PostStoragePolicyAssignmentsRequestBodyStoragePolicy(StrictModel):
    type_: Literal["storage_policy"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The resource type being assigned as the storage policy; must always be 'storage_policy'.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the storage policy to assign to the target entity.")
class PostStoragePolicyAssignmentsRequestBodyAssignedTo(StrictModel):
    type_: Literal["user", "enterprise"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="The type of entity receiving the storage policy assignment, either an individual user or an entire enterprise.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the user or enterprise to which the storage policy will be assigned.")
class PostStoragePolicyAssignmentsRequestBody(StrictModel):
    storage_policy: PostStoragePolicyAssignmentsRequestBodyStoragePolicy | None = None
    assigned_to: PostStoragePolicyAssignmentsRequestBodyAssignedTo | None = None
class PostStoragePolicyAssignmentsRequest(StrictModel):
    """Assigns a storage policy to a specific user or enterprise, controlling where their content is stored. Use this to enforce data residency or storage tier requirements."""
    body: PostStoragePolicyAssignmentsRequestBody | None = None

# Operation: get_storage_policy_assignment
class GetStoragePolicyAssignmentsIdRequestPath(StrictModel):
    storage_policy_assignment_id: str = Field(default=..., description="The unique identifier of the storage policy assignment to retrieve.")
class GetStoragePolicyAssignmentsIdRequest(StrictModel):
    """Retrieves the details of a specific storage policy assignment by its unique identifier. Useful for inspecting which storage policy is applied to a particular user or enterprise."""
    path: GetStoragePolicyAssignmentsIdRequestPath

# Operation: delete_storage_policy_assignment
class DeleteStoragePolicyAssignmentsIdRequestPath(StrictModel):
    storage_policy_assignment_id: str = Field(default=..., description="The unique identifier of the storage policy assignment to delete.")
class DeleteStoragePolicyAssignmentsIdRequest(StrictModel):
    """Removes a storage policy assignment, causing the affected user to inherit the enterprise's default storage policy. Note: this endpoint is rate-limited to two calls per user within any 24-hour period."""
    path: DeleteStoragePolicyAssignmentsIdRequestPath

# Operation: create_zip_download
class PostZipDownloadsRequestBody(StrictModel):
    items: list[PostZipDownloadsBodyItemsItem] | None = Field(default=None, description="A list of files and folders to include in the zip archive. Order is not significant; each item should specify its type and identifier.")
    download_file_name: str | None = Field(default=None, description="The base name for the generated zip archive file, without the file extension. The `.zip` extension will be appended automatically.")
class PostZipDownloadsRequest(StrictModel):
    """Initiates a zip archive download request for multiple files and folders, validating access permissions and returning a download URL and status URL. The archive is limited to 10,000 files or the account's upload limit, with a recommended maximum total size of 25GB."""
    body: PostZipDownloadsRequestBody | None = None

# Operation: download_zip_archive
class GetZipDownloadsIdContentRequestPath(StrictModel):
    zip_download_id: str = Field(default=..., description="The unique identifier for the zip archive, obtained from the `download_url` field returned by the Create Zip Download API.")
class GetZipDownloadsIdContentRequest(StrictModel):
    """Downloads the binary contents of a previously created zip archive using the download URL provided when the archive was requested. This endpoint requires no authentication and is intended for direct browser-based downloads; the URL is time-limited and a new zip download request must be created if the session expires."""
    path: GetZipDownloadsIdContentRequestPath

# Operation: get_zip_download_status
class GetZipDownloadsIdStatusRequestPath(StrictModel):
    zip_download_id: str = Field(default=..., description="The unique identifier for the zip archive whose status is being checked, obtained from the response of the Create zip download API.")
class GetZipDownloadsIdStatusRequest(StrictModel):
    """Retrieves the current download progress and status of a zip archive, including any items that were skipped. This endpoint is accessible only after the download has started and remains valid for 12 hours from initiation."""
    path: GetZipDownloadsIdStatusRequestPath

# Operation: cancel_sign_request
class PostSignRequestsIdCancelRequestPath(StrictModel):
    sign_request_id: str = Field(default=..., description="The unique identifier of the sign request to cancel.")
class PostSignRequestsIdCancelRequestBody(StrictModel):
    reason: str | None = Field(default=None, description="An optional explanation for why the sign request is being cancelled, useful for audit trails and notifying stakeholders.")
class PostSignRequestsIdCancelRequest(StrictModel):
    """Cancels an active Box Sign request, preventing further signing actions by any recipients. An optional reason can be provided to document why the request was cancelled."""
    path: PostSignRequestsIdCancelRequestPath
    body: PostSignRequestsIdCancelRequestBody | None = None

# Operation: resend_sign_request
class PostSignRequestsIdResendRequestPath(StrictModel):
    sign_request_id: str = Field(default=..., description="The unique identifier of the signature request to resend notifications for.")
class PostSignRequestsIdResendRequest(StrictModel):
    """Resends the signature request email to all outstanding signers who have not yet completed signing. Useful for following up on pending signatures without creating a new request."""
    path: PostSignRequestsIdResendRequestPath

# Operation: get_sign_request
class GetSignRequestsIdRequestPath(StrictModel):
    sign_request_id: str = Field(default=..., description="The unique identifier of the Box Sign request to retrieve.")
class GetSignRequestsIdRequest(StrictModel):
    """Retrieves the details of a specific Box Sign request by its unique ID. Use this to check the status, signers, and configuration of an existing signature request."""
    path: GetSignRequestsIdRequestPath

# Operation: list_sign_requests
class GetSignRequestsRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of signature requests to return per page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
    senders: list[str] | None = Field(default=None, description="Filters results to only include signature requests sent by the specified email addresses. Requires `shared_requests` to be set to `true` when used. Order is not significant; each item should be a valid email address.")
    shared_requests: bool | None = Field(default=None, description="When `true`, returns only signature requests where the authenticated user is a collaborator (not the owner); collaborator access is determined by the user's access level on the associated sign files. Must be `true` if `senders` is provided; defaults to `false`.")
class GetSignRequestsRequest(StrictModel):
    """Retrieves all Box Sign signature requests created by the authenticated user. Requests associated with deleted sign files or parent folders are excluded from results."""
    query: GetSignRequestsRequestQuery | None = None

# Operation: create_sign_request
class PostSignRequestsRequestBody(StrictModel):
    body: SignRequestCreateRequest | None = Field(default=None, description="The request body containing all details needed to create the signature request, including the document to be signed, signer information, and any signing configuration options.")
class PostSignRequestsRequest(StrictModel):
    """Creates a Box Sign signature request by preparing a document for signing and dispatching it to one or more signers. Use this to initiate a new e-signature workflow on a document stored in Box."""
    body: PostSignRequestsRequestBody | None = None

# Operation: list_workflows
class GetWorkflowsRequestQuery(StrictModel):
    folder_id: str = Field(default=..., description="The unique identifier of the folder whose associated workflows you want to retrieve. The root folder of a Box account is always ID 0; other folder IDs can be found in the URL when viewing the folder in the Box web app.")
    trigger_type: str | None = Field(default=None, description="Filters workflows by their trigger type, returning only workflows that match the specified trigger. Use to narrow results to a specific trigger category.")
    limit: int | None = Field(default=None, description="The maximum number of workflows to return in a single response, up to a limit of 1000.", json_schema_extra={'format': 'int64'})
class GetWorkflowsRequest(StrictModel):
    """Retrieves all workflows associated with a specific folder that have a manually triggerable flow. Requires the Manage Box Relay application scope to be enabled in the developer console."""
    query: GetWorkflowsRequestQuery

# Operation: start_workflow
class PostWorkflowsIdStartRequestPath(StrictModel):
    workflow_id: str = Field(default=..., description="The unique identifier of the workflow to start.")
class PostWorkflowsIdStartRequestBodyFlow(StrictModel):
    type_: str | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Identifies the type of the flow object being referenced within the parameters.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the specific flow within the workflow to trigger.")
class PostWorkflowsIdStartRequestBodyFolder(StrictModel):
    type_: Literal["folder"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Identifies the type of the folder object being referenced; must be set to 'folder'.")
    id_: str | None = Field(default=None, validation_alias="id", serialization_alias="id", description="The unique identifier of the folder configured for this workflow; all provided files must reside within this folder.")
class PostWorkflowsIdStartRequestBody(StrictModel):
    type_: Literal["workflow_parameters"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Identifies the type of the top-level parameters object being submitted; must be set to 'workflow_parameters'.")
    files: list[PostWorkflowsIdStartBodyFilesItem] | None = Field(default=None, description="An array of file objects for which the workflow should be started; each file must already exist within the workflow's configured folder. Order is not significant.")
    outcomes: list[Outcome] | None = Field(default=None, description="An array of configurable outcome objects that the workflow should complete as part of its execution. Order is not significant.")
    flow: PostWorkflowsIdStartRequestBodyFlow | None = None
    folder: PostWorkflowsIdStartRequestBodyFolder | None = None
class PostWorkflowsIdStartRequest(StrictModel):
    """Manually triggers a Box Relay workflow with a WORKFLOW_MANUAL_START trigger type for a specified folder and optional files. Requires the Manage Box Relay application scope to be authorized in the developer console."""
    path: PostWorkflowsIdStartRequestPath
    body: PostWorkflowsIdStartRequestBody | None = None

# Operation: list_sign_templates
class GetSignTemplatesRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of sign templates to return per page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
class GetSignTemplatesRequest(StrictModel):
    """Retrieves all Box Sign templates created by the authenticated user. Returns a paginated list of templates available for use in signing workflows."""
    query: GetSignTemplatesRequestQuery | None = None

# Operation: get_sign_template
class GetSignTemplatesIdRequestPath(StrictModel):
    template_id: str = Field(default=..., description="The unique identifier of the Box Sign template to retrieve.")
class GetSignTemplatesIdRequest(StrictModel):
    """Retrieves the full details of a specific Box Sign template by its unique ID. Use this to inspect template configuration, fields, and signers before initiating a signing request."""
    path: GetSignTemplatesIdRequestPath

# Operation: list_slack_integration_mappings
class GetIntegrationMappingsSlackRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="Maximum number of integration mappings to return per page. Accepts values up to 1000.", json_schema_extra={'format': 'int64'})
    partner_item_type: Literal["channel"] | None = Field(default=None, description="Filters results to only return mappings for the specified Slack item type. Currently only 'channel' is supported.")
    partner_item_id: str | None = Field(default=None, description="Filters results to only return mappings associated with the specified Slack partner item ID, such as a specific Slack channel ID.")
    box_item_id: str | None = Field(default=None, description="Filters results to only return mappings associated with the specified Box item ID.")
    box_item_type: Literal["folder"] | None = Field(default=None, description="Filters results to only return mappings for the specified Box item type. Currently only 'folder' is supported.")
    is_manually_created: bool | None = Field(default=None, description="Filters results to only return mappings that were manually created (true) or automatically created (false).")
class GetIntegrationMappingsSlackRequest(StrictModel):
    """Retrieves all Slack integration mappings for the enterprise, showing how Box folders are linked to Slack channels. Requires Admin or Co-Admin role."""
    query: GetIntegrationMappingsSlackRequestQuery | None = None

# Operation: list_teams_integration_mappings
class GetIntegrationMappingsTeamsRequestQuery(StrictModel):
    partner_item_type: Literal["channel", "team"] | None = Field(default=None, description="Filters results to only return mappings for the specified Microsoft Teams item type, either a channel or a team.")
    partner_item_id: str | None = Field(default=None, description="Filters results to only return mappings associated with the specified Microsoft Teams item ID.")
    box_item_id: str | None = Field(default=None, description="Filters results to only return mappings associated with the specified Box item ID.")
    box_item_type: Literal["folder"] | None = Field(default=None, description="Filters results to only return mappings for the specified Box item type. Currently only folder mappings are supported.")
class GetIntegrationMappingsTeamsRequest(StrictModel):
    """Retrieves a list of Box for Teams integration mappings within an enterprise, showing how Box items are linked to Microsoft Teams channels or teams. Requires Admin or Co-Admin role."""
    query: GetIntegrationMappingsTeamsRequestQuery | None = None

# Operation: create_teams_integration_mapping
class PostIntegrationMappingsTeamsRequestBody(StrictModel):
    partner_item: PostIntegrationMappingsTeamsBodyPartnerItem | None = Field(default=None, description="The Microsoft Teams channel to map, identifying the partner-side resource in the integration.")
    box_item: PostIntegrationMappingsTeamsBodyBoxItem | None = Field(default=None, description="The Box item (such as a folder) to map to the Teams channel, identifying the Box-side resource in the integration.")
class PostIntegrationMappingsTeamsRequest(StrictModel):
    """Creates a Teams integration mapping by linking a Microsoft Teams channel to a Box item. Requires Admin or Co-Admin role."""
    body: PostIntegrationMappingsTeamsRequestBody | None = None

# Operation: extract_metadata_freeform
class PostAiExtractRequestBody(StrictModel):
    prompt: str | None = Field(default=None, description="The freeform prompt instructing the LLM on what metadata to extract and how. Supports XML or JSON schema format and can be up to 10,000 characters long.")
    items: Annotated[list[AiItemBase], AfterValidator(_check_unique_items)] | None = Field(default=None, description="The list of files the LLM will process for metadata extraction. Order is not significant; each item must reference a valid file. Between 1 and 25 files may be included.", min_length=1, max_length=25)
    ai_agent: AiAgentReference | AiAgentExtract | None = Field(default=None, description="Optional AI agent configuration to override the default LLM settings used for this extraction request.")
class PostAiExtractRequest(StrictModel):
    """Sends a freeform prompt to an LLM to extract key-value metadata from one or more files, without requiring a predefined metadata template. Both the prompt structure and the output format are flexible, supporting XML or JSON schema prompts."""
    body: PostAiExtractRequestBody | None = None

# Operation: extract_structured_metadata
class PostAiExtractStructuredRequestBodyMetadataTemplate(StrictModel):
    template_key: str | None = Field(default=None, validation_alias="template_key", serialization_alias="template_key", description="The unique key identifying the metadata template to use for extraction. Required when using a metadata template instead of a custom fields list.")
    type_: Literal["metadata_template"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Specifies the extraction structure type. Must always be set to `metadata_template` when using a template-based extraction.")
    scope: str | None = Field(default=None, validation_alias="scope", serialization_alias="scope", description="The scope of the metadata template, either global (available to all Box enterprises) or enterprise-scoped (prefixed with the enterprise ID). Maximum 40 characters.", max_length=40)
class PostAiExtractStructuredRequestBody(StrictModel):
    items: Annotated[list[AiItemBase], AfterValidator(_check_unique_items)] | None = Field(default=None, description="The list of files to be processed by the LLM. Accepts between 1 and 25 file items; order does not affect extraction results.", min_length=1, max_length=25)
    fields: Annotated[list[PostAiExtractStructuredBodyFieldsItem], AfterValidator(_check_unique_items)] | None = Field(default=None, description="A custom list of fields to extract from the provided files. Use this instead of a metadata template — exactly one of `fields` or a metadata template must be provided, not both. Requires at least one field.", min_length=1)
    include_confidence_score: bool | None = Field(default=None, description="When set to true, the response will include a confidence score for each extracted field, indicating the LLM's certainty about the extracted value.")
    include_reference: bool | None = Field(default=None, description="When set to true, the response will include source references for each extracted field, indicating where in the file the value was found.")
    ai_agent: AiAgentReference | AiAgentExtractStructured | None = Field(default=None, description="Optional AI agent configuration to override the default extraction agent settings, such as model selection or prompt behavior.")
    metadata_template: PostAiExtractStructuredRequestBodyMetadataTemplate | None = None
class PostAiExtractStructuredRequest(StrictModel):
    """Sends files to a Box AI-supported LLM and returns extracted metadata as structured key-value pairs. Define the extraction structure using either a metadata template or a custom list of fields."""
    body: PostAiExtractStructuredRequestBody | None = None

# Operation: list_ai_agents
class GetAiAgentsRequestQuery(StrictModel):
    mode: list[str] | None = Field(default=None, description="Filters results to only return agents configured for the specified modes. Accepts one or more of the following values: `ask`, `text_gen`, or `extract`. Order is not significant.")
    agent_state: list[str] | None = Field(default=None, description="Filters results to only return agents in the specified states. Accepts one or more of the following values: `enabled`, `disabled`, or `enabled_for_selected_users`. Order is not significant.")
    include_box_default: bool | None = Field(default=None, description="When set to true, includes Box-provided default agents in the response alongside any custom agents.")
    limit: int | None = Field(default=None, description="The maximum number of agents to return in a single response. Accepts a value between 1 and 1000.", json_schema_extra={'format': 'int64'})
class GetAiAgentsRequest(StrictModel):
    """Retrieves a list of AI agents configured in the account, with optional filtering by mode, state, and whether to include Box default agents."""
    query: GetAiAgentsRequestQuery | None = None

# Operation: create_ai_agent
class PostAiAgentsRequestBodyAsk(StrictModel):
    type_: Literal["ai_agent_ask"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Identifies the ask capability block as an AI agent ask handler.")
    access_state: str | None = Field(default=None, validation_alias="access_state", serialization_alias="access_state", description="Controls whether the ask capability is active. Set to `enabled` to allow users to ask questions, or `disabled` to turn it off.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Human-readable description of the ask capability, explaining its purpose or behavior to users.")
    custom_instructions: str | None = Field(default=None, validation_alias="custom_instructions", serialization_alias="custom_instructions", description="Custom behavioral instructions that guide how the ask capability responds, allowing tailored tone, scope, or domain-specific rules.")
    suggested_questions: list[str] | None = Field(default=None, validation_alias="suggested_questions", serialization_alias="suggested_questions", description="Up to 4 pre-defined questions surfaced to users when interacting with the ask capability. Pass null to auto-generate suggestions, or an empty array to show none.", max_length=4)
    long_text: PostAiAgentsBodyAskLongText | None = Field(default=None, validation_alias="long_text", serialization_alias="long_text", description="Configuration for the processor that handles long-form text content within the ask capability, such as chunking strategy and model settings.")
    basic_text: PostAiAgentsBodyAskBasicText | None = Field(default=None, validation_alias="basic_text", serialization_alias="basic_text", description="Configuration for the processor that handles standard-length text content within the ask capability, including model and prompt settings.")
    basic_image: PostAiAgentsBodyAskBasicImage | None = Field(default=None, validation_alias="basic_image", serialization_alias="basic_image", description="Configuration for the processor that handles image content within the ask capability, including model and prompt settings.")
    spreadsheet: PostAiAgentsBodyAskSpreadsheet | None = Field(default=None, validation_alias="spreadsheet", serialization_alias="spreadsheet", description="Configuration for the tool that processes spreadsheet and tabular data, controlling how structured data is interpreted by the agent.")
    long_text_multi: PostAiAgentsBodyAskLongTextMulti | None = Field(default=None, validation_alias="long_text_multi", serialization_alias="long_text_multi", description="Configuration for the processor that handles long-form text across multiple documents or segments, used for multi-document ask scenarios.")
    basic_text_multi: PostAiAgentsBodyAskBasicTextMulti | None = Field(default=None, validation_alias="basic_text_multi", serialization_alias="basic_text_multi", description="Configuration for the processor that handles standard-length text across multiple documents or segments, used for multi-document ask scenarios.")
    basic_image_multi: PostAiAgentsBodyAskBasicImageMulti | None = Field(default=None, validation_alias="basic_image_multi", serialization_alias="basic_image_multi", description="Configuration for the processor that handles images across multiple documents or segments, used for multi-document ask scenarios.")
class PostAiAgentsRequestBodyTextGen(StrictModel):
    type_: Literal["ai_agent_text_gen"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Identifies the text generation capability block as an AI agent text generator.")
    access_state: str | None = Field(default=None, validation_alias="access_state", serialization_alias="access_state", description="Controls whether the text generation capability is active. Set to `enabled` to allow text generation, or `disabled` to turn it off.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Human-readable description of the text generation capability, explaining its purpose or behavior to users.")
    custom_instructions: str | None = Field(default=None, validation_alias="custom_instructions", serialization_alias="custom_instructions", description="Custom behavioral instructions that guide how the text generation capability produces output, allowing tailored tone, scope, or domain-specific rules.")
    suggested_questions: list[str] | None = Field(default=None, validation_alias="suggested_questions", serialization_alias="suggested_questions", description="Up to 4 pre-defined questions surfaced to users when interacting with the text generation capability. Pass null to auto-generate suggestions, or an empty array to show none.", max_length=4)
    basic_gen: PostAiAgentsBodyTextGenBasicGen | None = Field(default=None, validation_alias="basic_gen", serialization_alias="basic_gen", description="Configuration for the basic text generation tool used by the text_gen capability, controlling model behavior and prompt structure for content generation.")
class PostAiAgentsRequestBodyExtract(StrictModel):
    type_: Literal["ai_agent_extract"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Identifies the extract capability block as an AI agent metadata extractor.")
    access_state: str | None = Field(default=None, validation_alias="access_state", serialization_alias="access_state", description="Controls whether the metadata extraction capability is active. Set to `enabled` to allow extraction, or `disabled` to turn it off.")
    description: str | None = Field(default=None, validation_alias="description", serialization_alias="description", description="Human-readable description of the extract capability, explaining its purpose or behavior to users.")
    custom_instructions: str | None = Field(default=None, validation_alias="custom_instructions", serialization_alias="custom_instructions", description="Custom behavioral instructions that guide how the extract capability identifies and pulls metadata, allowing tailored scope or domain-specific rules.")
    long_text: PostAiAgentsBodyExtractLongText | None = Field(default=None, validation_alias="long_text", serialization_alias="long_text", description="Configuration for the processor that handles long-form text content within the extract capability, such as chunking strategy and model settings.")
    basic_text: PostAiAgentsBodyExtractBasicText | None = Field(default=None, validation_alias="basic_text", serialization_alias="basic_text", description="Configuration for the processor that handles standard-length text content within the extract capability, including model and prompt settings.")
    basic_image: PostAiAgentsBodyExtractBasicImage | None = Field(default=None, validation_alias="basic_image", serialization_alias="basic_image", description="Configuration for the processor that handles image content within the extract capability, including model and prompt settings.")
class PostAiAgentsRequestBody(StrictModel):
    type_: Literal["ai_agent"] | None = Field(default=None, validation_alias="type", serialization_alias="type", description="Identifies this configuration as an AI agent resource.")
    name: str | None = Field(default=None, description="Human-readable display name for the AI agent, shown in the UI and used to identify the agent.")
    access_state: str | None = Field(default=None, description="Controls the overall availability of the AI agent. Use `enabled` to make it available to all, `disabled` to deactivate it, or `enabled_for_selected_users` to restrict access to specific users.")
    icon_reference: str | None = Field(default=None, description="URL pointing to the avatar icon displayed for this AI agent in the UI. Must be a valid Box CDN URL using one of the supported avatar filenames.", min_length=1)
    allowed_entities: list[UserBase | GroupBase] | None = Field(default=None, description="List of users or groups permitted to use this AI agent when access is restricted to selected entities. Each item should reference a valid user or group.")
    ask: PostAiAgentsRequestBodyAsk | None = None
    text_gen: PostAiAgentsRequestBodyTextGen | None = None
    extract_: PostAiAgentsRequestBodyExtract | None = Field(default=None, validation_alias="extract", serialization_alias="extract")
class PostAiAgentsRequest(StrictModel):
    """Creates a new AI agent with one or more capabilities (ask, text_gen, or extract). At least one capability must be configured when creating the agent."""
    body: PostAiAgentsRequestBody | None = None

# Operation: get_ai_agent
class GetAiAgentsIdRequestPath(StrictModel):
    agent_id: str = Field(default=..., description="The unique identifier of the AI agent to retrieve.")
class GetAiAgentsIdRequest(StrictModel):
    """Retrieves a specific AI agent by its unique identifier. Returns the full agent configuration and metadata for the specified agent."""
    path: GetAiAgentsIdRequestPath

# Operation: list_metadata_taxonomies
class GetMetadataTaxonomiesIdRequestPath(StrictModel):
    namespace: str = Field(default=..., description="The namespace that scopes the metadata taxonomies to retrieve, typically representing an enterprise or organizational boundary.")
class GetMetadataTaxonomiesIdRequestQuery(StrictModel):
    limit: int | None = Field(default=None, description="The maximum number of taxonomy items to return in a single page of results, up to a maximum of 1000.", json_schema_extra={'format': 'int64'})
class GetMetadataTaxonomiesIdRequest(StrictModel):
    """Retrieves all metadata taxonomies within a specified namespace, enabling discovery of available taxonomy structures for organizing and classifying content metadata."""
    path: GetMetadataTaxonomiesIdRequestPath
    query: GetMetadataTaxonomiesIdRequestQuery | None = None

# Operation: get_metadata_taxonomy
class GetMetadataTaxonomiesIdIdRequestPath(StrictModel):
    namespace: str = Field(default=..., description="The namespace that scopes the metadata taxonomy, typically representing an enterprise or organizational unit.")
    taxonomy_key: str = Field(default=..., description="The unique key identifying the metadata taxonomy to retrieve within the specified namespace.")
class GetMetadataTaxonomiesIdIdRequest(StrictModel):
    """Retrieves a specific metadata taxonomy by its unique key within a given namespace. Use this to inspect the structure and configuration of a taxonomy for organizing and classifying metadata."""
    path: GetMetadataTaxonomiesIdIdRequestPath

# Operation: list_taxonomy_nodes
class GetMetadataTaxonomiesIdIdNodesRequestPath(StrictModel):
    namespace: str = Field(default=..., description="The namespace that owns the metadata taxonomy, used to scope the taxonomy to a specific organization or enterprise.")
    taxonomy_key: str = Field(default=..., description="The unique key identifying the metadata taxonomy within the given namespace.")
class GetMetadataTaxonomiesIdIdNodesRequestQuery(StrictModel):
    level: list[int] | None = Field(default=None, description="Filters nodes to only those at the specified depth level(s) within the taxonomy hierarchy. Multiple values may be provided; nodes matching any specified level are returned.")
    parent: list[str] | None = Field(default=None, description="Filters nodes to only those whose immediate parent matches the specified node identifier(s). Multiple values may be provided; nodes matching any specified parent are returned.")
    ancestor: list[str] | None = Field(default=None, description="Filters nodes to only those that are descendants of the specified ancestor node identifier(s) at any depth. Multiple values may be provided; nodes matching any specified ancestor are returned.")
    query: str | None = Field(default=None, description="Free-text search string to find matching taxonomy nodes by name or content. When provided, results are ranked by relevance rather than lexicographic order.")
    include_total_result_count: bool | None = Field(default=None, validation_alias="include-total-result-count", serialization_alias="include-total-result-count", description="When set to true, includes the total count of matching nodes in the response. Counts are computed for up to 10,000 matching elements; defaults to false.")
    limit: int | None = Field(default=None, description="The maximum number of taxonomy nodes to return in a single page of results. Must be between 1 and 1,000.", json_schema_extra={'format': 'int64'})
class GetMetadataTaxonomiesIdIdNodesRequest(StrictModel):
    """Retrieves nodes within a specific metadata taxonomy, supporting filtering by level, parent, or ancestor relationships. Results are sorted lexicographically by default, or by relevance when a search query is provided."""
    path: GetMetadataTaxonomiesIdIdNodesRequestPath
    query: GetMetadataTaxonomiesIdIdNodesRequestQuery | None = None

# Operation: get_taxonomy_node
class GetMetadataTaxonomiesIdIdNodesIdRequestPath(StrictModel):
    namespace: str = Field(default=..., description="The namespace that scopes the metadata taxonomy, typically representing an enterprise or organizational unit.")
    taxonomy_key: str = Field(default=..., description="The unique key identifying the metadata taxonomy within the namespace, representing a classification domain such as geography or department.")
    node_id: str = Field(default=..., description="The unique identifier of the taxonomy node to retrieve, formatted as a UUID.")
class GetMetadataTaxonomiesIdIdNodesIdRequest(StrictModel):
    """Retrieves a single metadata taxonomy node by its unique identifier within a specified namespace and taxonomy. Useful for inspecting the details of a specific classification node in a hierarchical metadata structure."""
    path: GetMetadataTaxonomiesIdIdNodesIdRequestPath

# Operation: delete_taxonomy_node
class DeleteMetadataTaxonomiesIdIdNodesIdRequestPath(StrictModel):
    namespace: str = Field(default=..., description="The namespace that scopes the metadata taxonomy, typically representing an organization or enterprise account.")
    taxonomy_key: str = Field(default=..., description="The unique key identifying the metadata taxonomy within the namespace.")
    node_id: str = Field(default=..., description="The unique identifier of the taxonomy node to delete. The node must have no children before it can be removed.")
class DeleteMetadataTaxonomiesIdIdNodesIdRequest(StrictModel):
    """Permanently deletes a specific node from a metadata taxonomy. Only leaf nodes (those without children) can be deleted, and this action cannot be undone."""
    path: DeleteMetadataTaxonomiesIdIdNodesIdRequestPath

# Operation: list_taxonomy_field_options
class GetMetadataTemplatesIdIdFieldsIdOptionsRequestPath(StrictModel):
    namespace: str = Field(default=..., description="The namespace that scopes the metadata taxonomy, typically tied to an enterprise account.")
    template_key: str = Field(default=..., description="The unique key identifying the metadata template that contains the taxonomy field.")
    field_key: str = Field(default=..., description="The key identifying the specific taxonomy field within the metadata template whose options are being retrieved.")
class GetMetadataTemplatesIdIdFieldsIdOptionsRequestQuery(StrictModel):
    level: list[int] | None = Field(default=None, description="Filters results to taxonomy nodes at the specified depth levels. Multiple values may be provided; nodes matching any specified level are included.")
    parent: list[str] | None = Field(default=None, description="Filters results to nodes that are direct children of the specified parent node identifiers. Multiple values may be provided; nodes matching any specified parent are included.")
    ancestor: list[str] | None = Field(default=None, description="Filters results to nodes that are descendants of the specified ancestor node identifiers at any depth. Multiple values may be provided; nodes matching any specified ancestor are included.")
    query: str | None = Field(default=None, description="Free-text search string to find matching taxonomy nodes by name or label. When provided, results are ranked by relevance rather than lexicographic order.")
    include_total_result_count: bool | None = Field(default=None, validation_alias="include-total-result-count", serialization_alias="include-total-result-count", description="When set to true, the response includes the total count of nodes matching the query, computed for up to 10,000 results. Defaults to false.")
    only_selectable_options: bool | None = Field(default=None, validation_alias="only-selectable-options", serialization_alias="only-selectable-options", description="When set to true, restricts results to only those taxonomy nodes that are valid selectable options for this field. When false, all taxonomy nodes are returned regardless of selectability. Defaults to true.")
    limit: int | None = Field(default=None, description="The maximum number of taxonomy nodes to return in a single page of results. Must be between 1 and 1000.", json_schema_extra={'format': 'int64'})
class GetMetadataTemplatesIdIdFieldsIdOptionsRequest(StrictModel):
    """Retrieves available taxonomy nodes for a specific taxonomy field within a metadata template, filtered by level, parent, ancestor, or search query. Results are sorted lexicographically by default, or by relevance when a query is provided."""
    path: GetMetadataTemplatesIdIdFieldsIdOptionsRequestPath
    query: GetMetadataTemplatesIdIdFieldsIdOptionsRequestQuery | None = None

# ============================================================================
# Component Models
# ============================================================================

class AiAgentLongTextToolEmbeddingsStrategy(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The strategy used for the AI agent for calculating embeddings.")
    num_tokens_per_chunk: int | None = Field(None, description="The number of tokens per chunk.", ge=1, le=512)

class AiAgentLongTextToolEmbeddings(PermissiveModel):
    model: str | None = Field(None, description="The model used for the AI agent for calculating embeddings.")
    strategy: AiAgentLongTextToolEmbeddingsStrategy | None = None

class AiAgentLongTextToolV1EmbeddingsStrategy(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The strategy used for the AI agent for calculating embeddings.")
    num_tokens_per_chunk: int | None = Field(None, description="The number of tokens per chunk.", ge=1, le=512)

class AiAgentLongTextToolV1Embeddings(PermissiveModel):
    model: str | None = Field(None, description="The model used for the AI agent for calculating embeddings.")
    strategy: AiAgentLongTextToolV1EmbeddingsStrategy | None = None

class AiAgentReference(PermissiveModel):
    """The AI agent used to handle queries."""
    type_: Literal["ai_agent_id"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of AI agent used to handle queries.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of an Agent. This can be a numeric ID for custom agents (for example, `14031`)\nor a unique identifier for pre-built agents (for example, `enhanced_extract_agent`\nfor the [Enhanced Extract Agent](https://developer.box.com/guides/box-ai/ai-tutorials/extract-metadata-structured#enhanced-extract-agent)).")

class AiItemBase(PermissiveModel):
    """The item to be processed by the LLM."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the file.")
    type_: Literal["file"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the item. Currently the value can be `file` only.")
    content: str | None = Field(None, description="The content of the item, often the text representation.")

class AiLlmEndpointParamsAws(PermissiveModel):
    """AI LLM endpoint params AWS object."""
    type_: Literal["aws_params"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the AI LLM endpoint params object for AWS.\nThis parameter is **required**.")
    temperature: float | None = Field(None, description="What sampling temperature to use, between 0 and 1. Higher values like 0.8 will make the output more random, \nwhile lower values like 0.2 will make it more focused and deterministic. \nWe generally recommend altering this or `top_p` but not both.", ge=0, le=1)
    top_p: float | None = Field(None, description="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results \nof the tokens with `top_p` probability mass. So 0.1 means only the tokens comprising the top 10% probability \nmass are considered. We generally recommend altering this or temperature but not both.", ge=0, le=1)

class AiLlmEndpointParamsGoogle(PermissiveModel):
    """AI LLM endpoint params Google object."""
    type_: Literal["google_params"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the AI LLM endpoint params object for Google.\nThis parameter is **required**.")
    temperature: float | None = Field(None, description="The temperature is used for sampling during response generation, which occurs when `top-P` and `top-K` are applied. Temperature controls the degree of randomness in the token selection.", ge=0, le=2)
    top_p: float | None = Field(None, description="`Top-P` changes how the model selects tokens for output. Tokens are selected from the most (see `top-K`) to least probable until the sum of their probabilities equals the `top-P` value.", ge=0.1, le=2)
    top_k: float | None = Field(None, description="`Top-K` changes how the model selects tokens for output. A low `top-K` means the next selected token is\nthe most probable among all tokens in the model's vocabulary (also called greedy decoding),\nwhile a high `top-K` means that the next token is selected from among the three most probable tokens by using temperature.", ge=0.1, le=2)

class AiLlmEndpointParamsIbm(PermissiveModel):
    """AI LLM endpoint params IBM object."""
    type_: Literal["ibm_params"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the AI LLM endpoint params object for IBM.\nThis parameter is **required**.")
    temperature: float | None = Field(None, description="What sampling temperature to use, between 0 and 1. Higher values like 0.8 will make the output more random, \nwhile lower values like 0.2 will make it more focused and deterministic. \nWe generally recommend altering this or `top_p` but not both.")
    top_p: float | None = Field(None, description="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results \nof the tokens with `top_p` probability mass. So 0.1 means only the tokens comprising the top 10% probability \nmass are considered. We generally recommend altering this or temperature but not both.", ge=0.1, le=1)
    top_k: float | None = Field(None, description="`Top-K` changes how the model selects tokens for output. A low `top-K` means the next selected token is\nthe most probable among all tokens in the model's vocabulary (also called greedy decoding),\nwhile a high `top-K` means that the next token is selected from among the three most probable tokens by using temperature.")

class AiLlmEndpointParamsOpenAi(PermissiveModel):
    """AI LLM endpoint params OpenAI object."""
    type_: Literal["openai_params"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the AI LLM endpoint params object for OpenAI.\nThis parameter is **required**.")
    temperature: float | None = Field(None, description="What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, \nwhile lower values like 0.2 will make it more focused and deterministic. \nWe generally recommend altering this or `top_p` but not both.", ge=0, le=2)
    top_p: float | None = Field(None, description="An alternative to sampling with temperature, called nucleus sampling, where the model considers the results \nof the tokens with `top_p` probability mass. So 0.1 means only the tokens comprising the top 10% probability \nmass are considered. We generally recommend altering this or temperature but not both.", ge=0.1, le=1)
    frequency_penalty: float | None = Field(None, description="A number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the \ntext so far, decreasing the model's likelihood to repeat the same line verbatim.", ge=-2, le=2)
    presence_penalty: float | None = Field(None, description="A number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.", ge=-2, le=2)
    stop: str | None = Field(None, description="Up to 4 sequences where the API will stop generating further tokens.")

class AiLlmEndpointParams(PermissiveModel):
    """The parameters for the LLM endpoint specific to a model."""
    ai_llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm

class AiAgentBasicTextToolBase(PermissiveModel):
    """AI agent processor used to handle basic text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParams | None = None

class AiAgentBasicTextTool(PermissiveModel):
    """AI agent processor used to handle basic text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParams | None = None
    system_message: str | None = Field(None, description="System messages try to help the LLM \"understand\" its role and what it is supposed to do.")
    prompt_template: str | None = Field(None, description="The prompt template contains contextual information of the request and the user prompt.\nWhen passing `prompt_template` parameters, you **must include** inputs for `{user_question}` and `{content}`.\n`{current_date}` is optional, depending on the use.", max_length=10000, pattern="(\\{user_question\\}[\\s\\S]*?\\{content\\}|\\{content\\}[\\s\\S]*?\\{user_question\\})")

class AiAgentLongTextTool(PermissiveModel):
    """AI agent processor used to to handle longer text."""
    embeddings: AiAgentLongTextToolEmbeddings | None = None

class AiAgentExtract(PermissiveModel):
    """The AI agent to be used for extraction."""
    type_: Literal["ai_agent_extract"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of AI agent to be used for extraction.")
    long_text: AiAgentLongTextTool | None = None
    basic_text: AiAgentBasicTextTool | None = None
    basic_image: AiAgentBasicTextTool | None = None

class AiAgentExtractStructured(PermissiveModel):
    """The AI agent to be used for structured extraction."""
    type_: Literal["ai_agent_extract_structured"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of AI agent to be used for extraction.")
    long_text: AiAgentLongTextTool | None = None
    basic_text: AiAgentBasicTextTool | None = None
    basic_image: AiAgentBasicTextTool | None = None

class Classification(PermissiveModel):
    """An instance of the classification metadata template, containing
the classification applied to the file or folder.

To get more details about the classification applied to an item,
request the classification metadata template."""
    box__security__classification__key: str | None = Field(None, validation_alias="Box__Security__Classification__Key", serialization_alias="Box__Security__Classification__Key", description="The name of the classification applied to the item.")
    parent: str | None = Field(None, validation_alias="$parent", serialization_alias="$parent", description="The identifier of the item that this metadata instance\nhas been attached to. This combines the `type` and the `id`\nof the parent in the form `{type}_{id}`.")
    template: Literal["securityClassification-6VMVochwUWo"] | None = Field(None, validation_alias="$template", serialization_alias="$template", description="The value will always be `securityClassification-6VMVochwUWo`.")
    scope: str | None = Field(None, validation_alias="$scope", serialization_alias="$scope", description="The scope of the enterprise that this classification has been\napplied for.\n\nThis will be in the format `enterprise_{enterprise_id}`.")
    version: int | None = Field(None, validation_alias="$version", serialization_alias="$version", description="The version of the metadata instance. This version starts at 0 and\nincreases every time a classification is updated.")
    type_: str | None = Field(None, validation_alias="$type", serialization_alias="$type", description="The unique ID of this classification instance. This will be include\nthe name of the classification template and a unique ID.")
    type_version: float | None = Field(None, validation_alias="$typeVersion", serialization_alias="$typeVersion", description="The version of the metadata template. This version starts at 0 and\nincreases every time the template is updated. This is mostly for internal\nuse.")
    can_edit: bool | None = Field(None, validation_alias="$canEdit", serialization_alias="$canEdit", description="Whether an end user can change the classification.")

class CollaboratorVariableVariableValueItem(PermissiveModel):
    """User variable used
in workflow outcomes."""
    type_: Literal["user"] = Field(..., validation_alias="type", serialization_alias="type", description="The object type.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="User's ID.")

class CollaboratorVariable(PermissiveModel):
    """A collaborator
object. Allows to
specify a list of user
ID's that are affected
by the workflow result."""
    type_: Literal["variable"] = Field(..., validation_alias="type", serialization_alias="type", description="Collaborator\nobject type.")
    variable_type: Literal["user_list"] = Field(..., description="Variable type \nfor the Collaborator\nobject.")
    variable_value: list[CollaboratorVariableVariableValueItem] = Field(..., description="A list of user IDs.")

class CompletionRuleVariable(PermissiveModel):
    """A completion
rule object. Determines
if an action should be completed
by all or any assignees."""
    type_: Literal["variable"] = Field(..., validation_alias="type", serialization_alias="type", description="Completion\nRule object type.")
    variable_type: Literal["task_completion_rule"] = Field(..., description="Variable type\nfor the Completion\nRule object.")
    variable_value: Literal["all_assignees", "any_assignees"] = Field(..., description="Variable\nvalues for a completion\nrule.")

class FileBase(PermissiveModel):
    """The bare basic representation of a file, the minimal
amount of fields returned when using the `fields` query
parameter."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier that represent a file.\n\nThe ID for any file can be determined\nby visiting a file in the web application\nand copying the ID from the URL. For example,\nfor the URL `https://*.app.box.com/files/123`\nthe `file_id` is `123`.")
    etag: str | None = Field(None, description="The HTTP `etag` of this file. This can be used within some API\nendpoints in the `If-Match` and `If-None-Match` headers to only\nperform changes on the file if (no) changes have happened.")
    type_: Literal["file"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `file`.")

class FileFullClassification(PermissiveModel):
    name: str | None = Field(None, description="The name of the classification.")
    definition: str | None = Field(None, description="An explanation of the meaning of this classification.")
    color: str | None = Field(None, description="The color that is used to display the\nclassification label in a user-interface. Colors are defined by the admin\nor co-admin who created the classification in the Box web app.")

class FileFullPermissions(PermissiveModel):
    can_delete: bool = Field(..., description="Specifies if the current user can delete this item.")
    can_download: bool = Field(..., description="Specifies if the current user can download this item.")
    can_invite_collaborator: bool = Field(..., description="Specifies if the current user can invite new\nusers to collaborate on this item, and if the user can\nupdate the role of a user already collaborated on this\nitem.")
    can_rename: bool = Field(..., description="Specifies if the user can rename this item.")
    can_set_share_access: bool = Field(..., description="Specifies if the user can change the access level of an\nexisting shared link on this item.")
    can_share: bool = Field(..., description="Specifies if the user can create a shared link for this item.")
    can_annotate: bool = Field(..., description="Specifies if the user can place annotations on this file.")
    can_comment: bool = Field(..., description="Specifies if the user can place comments on this file.")
    can_preview: bool = Field(..., description="Specifies if the user can preview this file.")
    can_upload: bool = Field(..., description="Specifies if the user can upload a new version of this file.")
    can_view_annotations_all: bool = Field(..., description="Specifies if the user view all annotations placed on this file.")
    can_view_annotations_self: bool = Field(..., description="Specifies if the user view annotations placed by themselves\non this file.")
    can_apply_watermark: bool | None = Field(None, description="Specifies if the user can apply a watermark to this file.")

class FileFullRepresentationsEntriesItemContent(PermissiveModel):
    """An object containing the URL that can be used to actually fetch
the representation."""
    url_template: str | None = Field(None, description="The download URL that can be used to fetch the representation.\nMake sure to make an authenticated API call to this endpoint.\n\nThis URL is a template and will require the `{+asset_path}` to\nbe replaced by a path. In general, for unpaged representations\nit can be replaced by an empty string.\n\nFor paged representations, replace the `{+asset_path}` with the\npage to request plus the extension for the file, for example\n`1.pdf`.\n\nWhen requesting the download URL the following additional\nquery params can be passed along.\n\n* `set_content_disposition_type` - Sets the\n`Content-Disposition` header in the API response with the\nspecified disposition type of either `inline` or `attachment`.\nIf not supplied, the `Content-Disposition` header is not\nincluded in the response.\n\n* `set_content_disposition_filename` - Allows the application to\n  define the representation's file name used in the\n  `Content-Disposition` header.  If not defined, the filename\n  is derived from the source file name in Box comb...")

class FileFullRepresentationsEntriesItemInfo(PermissiveModel):
    """An object containing the URL that can be used to fetch more info
on this representation."""
    url: str | None = Field(None, description="The API URL that can be used to get more info on this file\nrepresentation. Make sure to make an authenticated API call\nto this endpoint.")

class FileFullRepresentationsEntriesItemProperties(PermissiveModel):
    """An object containing the size and type of this presentation."""
    dimensions: str | None = Field(None, description="The width by height size of this representation in pixels.", json_schema_extra={'format': '<width>x<height>'})
    paged: str | None = Field(None, description="Indicates if the representation is build up out of multiple\npages.")
    thumb: str | None = Field(None, description="Indicates if the representation can be used as a thumbnail of\nthe file.")

class FileFullRepresentationsEntriesItemStatus(PermissiveModel):
    """An object containing the status of this representation."""
    state: Literal["success", "viewable", "pending", "none"] | None = Field(None, description="The status of the representation.\n\n* `success` defines the representation as ready to be viewed.\n* `viewable` defines a video to be ready for viewing.\n* `pending` defines the representation as to be generated. Retry\n  this endpoint to re-check the status.\n* `none` defines that the representation will be created when\n  requested. Request the URL defined in the `info` object to\n  trigger this generation.")

class FileFullRepresentationsEntriesItem(PermissiveModel):
    """A file representation."""
    content: FileFullRepresentationsEntriesItemContent | None = Field(None, description="An object containing the URL that can be used to actually fetch\nthe representation.")
    info: FileFullRepresentationsEntriesItemInfo | None = Field(None, description="An object containing the URL that can be used to fetch more info\non this representation.")
    properties: FileFullRepresentationsEntriesItemProperties | None = Field(None, description="An object containing the size and type of this presentation.")
    representation: str | None = Field(None, description="Indicates the file type of the returned representation.")
    status: FileFullRepresentationsEntriesItemStatus | None = Field(None, description="An object containing the status of this representation.")

class FileFullRepresentations(PermissiveModel):
    entries: list[FileFullRepresentationsEntriesItem] | None = Field(None, description="A list of files.")

class FileFullRepresentationsV0EntriesItemContent(PermissiveModel):
    """An object containing the URL that can be used to actually fetch
the representation."""
    url_template: str | None = Field(None, description="The download URL that can be used to fetch the representation.\nMake sure to make an authenticated API call to this endpoint.\n\nThis URL is a template and will require the `{+asset_path}` to\nbe replaced by a path. In general, for unpaged representations\nit can be replaced by an empty string.\n\nFor paged representations, replace the `{+asset_path}` with the\npage to request plus the extension for the file, for example\n`1.pdf`.\n\nWhen requesting the download URL the following additional\nquery params can be passed along.\n\n* `set_content_disposition_type` - Sets the\n`Content-Disposition` header in the API response with the\nspecified disposition type of either `inline` or `attachment`.\nIf not supplied, the `Content-Disposition` header is not\nincluded in the response.\n\n* `set_content_disposition_filename` - Allows the application to\n  define the representation's file name used in the\n  `Content-Disposition` header.  If not defined, the filename\n  is derived from the source file name in Box comb...")

class FileFullRepresentationsV0EntriesItemInfo(PermissiveModel):
    """An object containing the URL that can be used to fetch more info
on this representation."""
    url: str | None = Field(None, description="The API URL that can be used to get more info on this file\nrepresentation. Make sure to make an authenticated API call\nto this endpoint.")

class FileFullRepresentationsV0EntriesItemProperties(PermissiveModel):
    """An object containing the size and type of this presentation."""
    dimensions: str | None = Field(None, description="The width by height size of this representation in pixels.", json_schema_extra={'format': '<width>x<height>'})
    paged: str | None = Field(None, description="Indicates if the representation is build up out of multiple\npages.")
    thumb: str | None = Field(None, description="Indicates if the representation can be used as a thumbnail of\nthe file.")

class FileFullRepresentationsV0EntriesItemStatus(PermissiveModel):
    """An object containing the status of this representation."""
    state: Literal["success", "viewable", "pending", "none"] | None = Field(None, description="The status of the representation.\n\n* `success` defines the representation as ready to be viewed.\n* `viewable` defines a video to be ready for viewing.\n* `pending` defines the representation as to be generated. Retry\n  this endpoint to re-check the status.\n* `none` defines that the representation will be created when\n  requested. Request the URL defined in the `info` object to\n  trigger this generation.")

class FileFullRepresentationsV0EntriesItem(PermissiveModel):
    """A file representation."""
    content: FileFullRepresentationsV0EntriesItemContent | None = Field(None, description="An object containing the URL that can be used to actually fetch\nthe representation.")
    info: FileFullRepresentationsV0EntriesItemInfo | None = Field(None, description="An object containing the URL that can be used to fetch more info\non this representation.")
    properties: FileFullRepresentationsV0EntriesItemProperties | None = Field(None, description="An object containing the size and type of this presentation.")
    representation: str | None = Field(None, description="Indicates the file type of the returned representation.")
    status: FileFullRepresentationsV0EntriesItemStatus | None = Field(None, description="An object containing the status of this representation.")

class FileFullV1Classification(PermissiveModel):
    name: str | None = Field(None, description="The name of the classification.")
    definition: str | None = Field(None, description="An explanation of the meaning of this classification.")
    color: str | None = Field(None, description="The color that is used to display the\nclassification label in a user-interface. Colors are defined by the admin\nor co-admin who created the classification in the Box web app.")

class FileFullV1Permissions(PermissiveModel):
    can_delete: bool = Field(..., description="Specifies if the current user can delete this item.")
    can_download: bool = Field(..., description="Specifies if the current user can download this item.")
    can_invite_collaborator: bool = Field(..., description="Specifies if the current user can invite new\nusers to collaborate on this item, and if the user can\nupdate the role of a user already collaborated on this\nitem.")
    can_rename: bool = Field(..., description="Specifies if the user can rename this item.")
    can_set_share_access: bool = Field(..., description="Specifies if the user can change the access level of an\nexisting shared link on this item.")
    can_share: bool = Field(..., description="Specifies if the user can create a shared link for this item.")
    can_annotate: bool = Field(..., description="Specifies if the user can place annotations on this file.")
    can_comment: bool = Field(..., description="Specifies if the user can place comments on this file.")
    can_preview: bool = Field(..., description="Specifies if the user can preview this file.")
    can_upload: bool = Field(..., description="Specifies if the user can upload a new version of this file.")
    can_view_annotations_all: bool = Field(..., description="Specifies if the user view all annotations placed on this file.")
    can_view_annotations_self: bool = Field(..., description="Specifies if the user view annotations placed by themselves\non this file.")
    can_apply_watermark: bool | None = Field(None, description="Specifies if the user can apply a watermark to this file.")

class FileFullV1RepresentationsEntriesItemContent(PermissiveModel):
    """An object containing the URL that can be used to actually fetch
the representation."""
    url_template: str | None = Field(None, description="The download URL that can be used to fetch the representation.\nMake sure to make an authenticated API call to this endpoint.\n\nThis URL is a template and will require the `{+asset_path}` to\nbe replaced by a path. In general, for unpaged representations\nit can be replaced by an empty string.\n\nFor paged representations, replace the `{+asset_path}` with the\npage to request plus the extension for the file, for example\n`1.pdf`.\n\nWhen requesting the download URL the following additional\nquery params can be passed along.\n\n* `set_content_disposition_type` - Sets the\n`Content-Disposition` header in the API response with the\nspecified disposition type of either `inline` or `attachment`.\nIf not supplied, the `Content-Disposition` header is not\nincluded in the response.\n\n* `set_content_disposition_filename` - Allows the application to\n  define the representation's file name used in the\n  `Content-Disposition` header.  If not defined, the filename\n  is derived from the source file name in Box comb...")

class FileFullV1RepresentationsEntriesItemInfo(PermissiveModel):
    """An object containing the URL that can be used to fetch more info
on this representation."""
    url: str | None = Field(None, description="The API URL that can be used to get more info on this file\nrepresentation. Make sure to make an authenticated API call\nto this endpoint.")

class FileFullV1RepresentationsEntriesItemProperties(PermissiveModel):
    """An object containing the size and type of this presentation."""
    dimensions: str | None = Field(None, description="The width by height size of this representation in pixels.", json_schema_extra={'format': '<width>x<height>'})
    paged: str | None = Field(None, description="Indicates if the representation is build up out of multiple\npages.")
    thumb: str | None = Field(None, description="Indicates if the representation can be used as a thumbnail of\nthe file.")

class FileFullV1RepresentationsEntriesItemStatus(PermissiveModel):
    """An object containing the status of this representation."""
    state: Literal["success", "viewable", "pending", "none"] | None = Field(None, description="The status of the representation.\n\n* `success` defines the representation as ready to be viewed.\n* `viewable` defines a video to be ready for viewing.\n* `pending` defines the representation as to be generated. Retry\n  this endpoint to re-check the status.\n* `none` defines that the representation will be created when\n  requested. Request the URL defined in the `info` object to\n  trigger this generation.")

class FileFullV1RepresentationsEntriesItem(PermissiveModel):
    """A file representation."""
    content: FileFullV1RepresentationsEntriesItemContent | None = Field(None, description="An object containing the URL that can be used to actually fetch\nthe representation.")
    info: FileFullV1RepresentationsEntriesItemInfo | None = Field(None, description="An object containing the URL that can be used to fetch more info\non this representation.")
    properties: FileFullV1RepresentationsEntriesItemProperties | None = Field(None, description="An object containing the size and type of this presentation.")
    representation: str | None = Field(None, description="Indicates the file type of the returned representation.")
    status: FileFullV1RepresentationsEntriesItemStatus | None = Field(None, description="An object containing the status of this representation.")

class FileFullV1Representations(PermissiveModel):
    entries: list[FileFullV1RepresentationsEntriesItem] | None = Field(None, description="A list of files.")

class FileFullV1RepresentationsV0EntriesItemContent(PermissiveModel):
    """An object containing the URL that can be used to actually fetch
the representation."""
    url_template: str | None = Field(None, description="The download URL that can be used to fetch the representation.\nMake sure to make an authenticated API call to this endpoint.\n\nThis URL is a template and will require the `{+asset_path}` to\nbe replaced by a path. In general, for unpaged representations\nit can be replaced by an empty string.\n\nFor paged representations, replace the `{+asset_path}` with the\npage to request plus the extension for the file, for example\n`1.pdf`.\n\nWhen requesting the download URL the following additional\nquery params can be passed along.\n\n* `set_content_disposition_type` - Sets the\n`Content-Disposition` header in the API response with the\nspecified disposition type of either `inline` or `attachment`.\nIf not supplied, the `Content-Disposition` header is not\nincluded in the response.\n\n* `set_content_disposition_filename` - Allows the application to\n  define the representation's file name used in the\n  `Content-Disposition` header.  If not defined, the filename\n  is derived from the source file name in Box comb...")

class FileFullV1RepresentationsV0EntriesItemInfo(PermissiveModel):
    """An object containing the URL that can be used to fetch more info
on this representation."""
    url: str | None = Field(None, description="The API URL that can be used to get more info on this file\nrepresentation. Make sure to make an authenticated API call\nto this endpoint.")

class FileFullV1RepresentationsV0EntriesItemProperties(PermissiveModel):
    """An object containing the size and type of this presentation."""
    dimensions: str | None = Field(None, description="The width by height size of this representation in pixels.", json_schema_extra={'format': '<width>x<height>'})
    paged: str | None = Field(None, description="Indicates if the representation is build up out of multiple\npages.")
    thumb: str | None = Field(None, description="Indicates if the representation can be used as a thumbnail of\nthe file.")

class FileFullV1RepresentationsV0EntriesItemStatus(PermissiveModel):
    """An object containing the status of this representation."""
    state: Literal["success", "viewable", "pending", "none"] | None = Field(None, description="The status of the representation.\n\n* `success` defines the representation as ready to be viewed.\n* `viewable` defines a video to be ready for viewing.\n* `pending` defines the representation as to be generated. Retry\n  this endpoint to re-check the status.\n* `none` defines that the representation will be created when\n  requested. Request the URL defined in the `info` object to\n  trigger this generation.")

class FileFullV1RepresentationsV0EntriesItem(PermissiveModel):
    """A file representation."""
    content: FileFullV1RepresentationsV0EntriesItemContent | None = Field(None, description="An object containing the URL that can be used to actually fetch\nthe representation.")
    info: FileFullV1RepresentationsV0EntriesItemInfo | None = Field(None, description="An object containing the URL that can be used to fetch more info\non this representation.")
    properties: FileFullV1RepresentationsV0EntriesItemProperties | None = Field(None, description="An object containing the size and type of this presentation.")
    representation: str | None = Field(None, description="Indicates the file type of the returned representation.")
    status: FileFullV1RepresentationsV0EntriesItemStatus | None = Field(None, description="An object containing the status of this representation.")

class FileFullV1WatermarkInfo(PermissiveModel):
    is_watermarked: bool | None = Field(None, description="Specifies if this item has a watermark applied.")
    is_watermark_inherited: bool | None = Field(None, description="Specifies if the watermark is inherited from any parent folder in the hierarchy.")
    is_watermarked_by_access_policy: bool | None = Field(None, description="Specifies if the watermark is enforced by an access policy.")

class FileFullWatermarkInfo(PermissiveModel):
    is_watermarked: bool | None = Field(None, description="Specifies if this item has a watermark applied.")
    is_watermark_inherited: bool | None = Field(None, description="Specifies if the watermark is inherited from any parent folder in the hierarchy.")
    is_watermarked_by_access_policy: bool | None = Field(None, description="Specifies if the watermark is enforced by an access policy.")

class FileModelSharedLinkPermissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")

class FileModelSharedLink(PermissiveModel):
    url: str = Field(..., description="The URL that can be used to access the item on Box.\n\nThis URL will display the item in Box's preview UI where the file\ncan be downloaded if allowed.\n\nThis URL will continue to work even when a custom `vanity_url`\nhas been set for this shared link.", json_schema_extra={'format': 'url'})
    download_url: str | None = Field(None, description="A URL that can be used to download the file. This URL can be used in\na browser to download the file. This URL includes the file\nextension so that the file will be saved with the right file type.\n\nThis property will be `null` for folders.", json_schema_extra={'format': 'url'})
    vanity_url: str | None = Field(None, description="The \"Custom URL\" that can also be used to preview the item on Box.  Custom\nURLs can only be created or modified in the Box Web application.", json_schema_extra={'format': 'url'})
    vanity_name: str | None = Field(None, description="The custom name of a shared link, as used in the `vanity_url` field.")
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The access level for this shared link.\n\n* `open` - provides access to this item to anyone with this link\n* `company` - only provides access to this item to people the same company\n* `collaborators` - only provides access to this item to people who are\n   collaborators on this item\n\nIf this field is omitted when creating the shared link, the access level\nwill be set to the default access level specified by the enterprise admin.")
    effective_access: Literal["open", "company", "collaborators"] = Field(..., description="The effective access level for the shared link. This can be a more\nrestrictive access level than the value in the `access` field when the\nenterprise settings restrict the allowed access levels.")
    effective_permission: Literal["can_edit", "can_download", "can_preview", "no_access"] = Field(..., description="The effective permissions for this shared link.\nThese result in the more restrictive combination of\nthe share link permissions and the item permissions set\nby the administrator, the owner, and any ancestor item\nsuch as a folder.")
    unshared_at: str | None = Field(None, description="The date and time when this link will be unshared. This field can only be\nset by users with paid accounts.", json_schema_extra={'format': 'date-time'})
    is_password_enabled: bool = Field(..., description="Defines if the shared link requires a password to access the item.")
    permissions: FileModelSharedLinkPermissions | None = Field(None, description="Defines if this link allows a user to preview, edit, and download an item.\nThese permissions refer to the shared link only and\ndo not supersede permissions applied to the item itself.")
    download_count: int = Field(..., description="The number of times this item has been downloaded.")
    preview_count: int = Field(..., description="The number of times this item has been previewed.")

class FileModelSharedLinkV0Permissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")

class FileModelV1SharedLinkPermissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")

class FileModelV1SharedLink(PermissiveModel):
    url: str = Field(..., description="The URL that can be used to access the item on Box.\n\nThis URL will display the item in Box's preview UI where the file\ncan be downloaded if allowed.\n\nThis URL will continue to work even when a custom `vanity_url`\nhas been set for this shared link.", json_schema_extra={'format': 'url'})
    download_url: str | None = Field(None, description="A URL that can be used to download the file. This URL can be used in\na browser to download the file. This URL includes the file\nextension so that the file will be saved with the right file type.\n\nThis property will be `null` for folders.", json_schema_extra={'format': 'url'})
    vanity_url: str | None = Field(None, description="The \"Custom URL\" that can also be used to preview the item on Box.  Custom\nURLs can only be created or modified in the Box Web application.", json_schema_extra={'format': 'url'})
    vanity_name: str | None = Field(None, description="The custom name of a shared link, as used in the `vanity_url` field.")
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The access level for this shared link.\n\n* `open` - provides access to this item to anyone with this link\n* `company` - only provides access to this item to people the same company\n* `collaborators` - only provides access to this item to people who are\n   collaborators on this item\n\nIf this field is omitted when creating the shared link, the access level\nwill be set to the default access level specified by the enterprise admin.")
    effective_access: Literal["open", "company", "collaborators"] = Field(..., description="The effective access level for the shared link. This can be a more\nrestrictive access level than the value in the `access` field when the\nenterprise settings restrict the allowed access levels.")
    effective_permission: Literal["can_edit", "can_download", "can_preview", "no_access"] = Field(..., description="The effective permissions for this shared link.\nThese result in the more restrictive combination of\nthe share link permissions and the item permissions set\nby the administrator, the owner, and any ancestor item\nsuch as a folder.")
    unshared_at: str | None = Field(None, description="The date and time when this link will be unshared. This field can only be\nset by users with paid accounts.", json_schema_extra={'format': 'date-time'})
    is_password_enabled: bool = Field(..., description="Defines if the shared link requires a password to access the item.")
    permissions: FileModelV1SharedLinkPermissions | None = Field(None, description="Defines if this link allows a user to preview, edit, and download an item.\nThese permissions refer to the shared link only and\ndo not supersede permissions applied to the item itself.")
    download_count: int = Field(..., description="The number of times this item has been downloaded.")
    preview_count: int = Field(..., description="The number of times this item has been previewed.")

class FileModelV1SharedLinkV0Permissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")

class FileRequestCopyRequestFolder(PermissiveModel):
    """The folder to associate the new file request to."""
    type_: Literal["folder"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The value will always be `folder`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the folder to associate the new\nfile request to.")

class FileRequestCopyRequestV1Folder(PermissiveModel):
    """The folder to associate the new file request to."""
    type_: Literal["folder"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The value will always be `folder`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The ID of the folder to associate the new\nfile request to.")

class FileRequestUpdateRequest(PermissiveModel):
    """The request body to update a file request."""
    title: str | None = Field(None, description="An optional new title for the file request. This can be\nused to change the title of the file request.\n\nThis will default to the value on the existing file request.")
    description: str | None = Field(None, description="An optional new description for the file request. This can be\nused to change the description of the file request.\n\nThis will default to the value on the existing file request.")
    status: Literal["active", "inactive"] | None = Field(None, description="An optional new status of the file request.\n\nWhen the status is set to `inactive`, the file request\nwill no longer accept new submissions, and any visitor\nto the file request URL will receive a `HTTP 404` status\ncode.\n\nThis will default to the value on the existing file request.")
    is_email_required: bool | None = Field(None, description="Whether a file request submitter is required to provide\ntheir email address.\n\nWhen this setting is set to true, the Box UI will show\nan email field on the file request form.\n\nThis will default to the value on the existing file request.")
    is_description_required: bool | None = Field(None, description="Whether a file request submitter is required to provide\na description of the files they are submitting.\n\nWhen this setting is set to true, the Box UI will show\na description field on the file request form.\n\nThis will default to the value on the existing file request.")
    expires_at: str | None = Field(None, description="The date after which a file request will no longer accept new\nsubmissions.\n\nAfter this date, the `status` will automatically be set to\n`inactive`.\n\nThis will default to the value on the existing file request.", json_schema_extra={'format': 'date-time'})

class FileRequestCopyRequest(PermissiveModel):
    """The request body to copy a file request."""
    title: str | None = Field(None, description="An optional new title for the file request. This can be\nused to change the title of the file request.\n\nThis will default to the value on the existing file request.")
    description: str | None = Field(None, description="An optional new description for the file request. This can be\nused to change the description of the file request.\n\nThis will default to the value on the existing file request.")
    status: Literal["active", "inactive"] | None = Field(None, description="An optional new status of the file request.\n\nWhen the status is set to `inactive`, the file request\nwill no longer accept new submissions, and any visitor\nto the file request URL will receive a `HTTP 404` status\ncode.\n\nThis will default to the value on the existing file request.")
    is_email_required: bool | None = Field(None, description="Whether a file request submitter is required to provide\ntheir email address.\n\nWhen this setting is set to true, the Box UI will show\nan email field on the file request form.\n\nThis will default to the value on the existing file request.")
    is_description_required: bool | None = Field(None, description="Whether a file request submitter is required to provide\na description of the files they are submitting.\n\nWhen this setting is set to true, the Box UI will show\na description field on the file request form.\n\nThis will default to the value on the existing file request.")
    expires_at: str | None = Field(None, description="The date after which a file request will no longer accept new\nsubmissions.\n\nAfter this date, the `status` will automatically be set to\n`inactive`.\n\nThis will default to the value on the existing file request.", json_schema_extra={'format': 'date-time'})
    folder: FileRequestCopyRequestFolder = Field(..., description="The folder to associate the new file request to.")

class FileVersionBase(PermissiveModel):
    """The bare basic representation of a file version, the minimal
amount of fields returned when using the `fields` query
parameter."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier that represent a file version.")
    type_: Literal["file_version"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `file_version`.")

class FileVersionMini(PermissiveModel):
    """A mini representation of a file version, used when
nested within another resource."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier that represent a file version.")
    type_: Literal["file_version"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `file_version`.")
    sha1: str | None = Field(None, description="The SHA1 hash of this version of the file.")

class FileMini(PermissiveModel):
    """A mini representation of a file, used when
nested under another resource."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier that represent a file.\n\nThe ID for any file can be determined\nby visiting a file in the web application\nand copying the ID from the URL. For example,\nfor the URL `https://*.app.box.com/files/123`\nthe `file_id` is `123`.")
    etag: str | None = Field(None, description="The HTTP `etag` of this file. This can be used within some API\nendpoints in the `If-Match` and `If-None-Match` headers to only\nperform changes on the file if (no) changes have happened.")
    type_: Literal["file"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `file`.")
    sequence_id: str | None | Any | None = None
    name: str | None = Field(None, description="The name of the file.")
    sha1: str | None = Field(None, description="The SHA1 hash of the file. This can be used to compare the contents\nof a file on Box with a local file.", json_schema_extra={'format': 'digest'})
    file_version: FileVersionMini | None = None

class FolderBase(PermissiveModel):
    """The bare basic representation of a folder, the minimal
amount of fields returned when using the `fields` query
parameter."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier that represent a folder.\n\nThe ID for any folder can be determined\nby visiting a folder in the web application\nand copying the ID from the URL. For example,\nfor the URL `https://*.app.box.com/folders/123`\nthe `folder_id` is `123`.")
    etag: str | None = Field(None, description="The HTTP `etag` of this folder. This can be used within some API\nendpoints in the `If-Match` and `If-None-Match` headers to only\nperform changes on the folder if (no) changes have happened.")
    type_: Literal["folder"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `folder`.")

class FolderFolderUploadEmail(PermissiveModel):
    """The `folder_upload_email` parameter is not `null` if one of the following options is **true**:

  * The **Allow uploads to this folder via email** and the **Only allow email uploads from collaborators in this folder** are [enabled for a folder in the Admin Console](https://support.box.com/hc/en-us/articles/360043697534-Upload-to-Box-Through-Email), and the user has at least **Upload** permissions granted.

  * The **Allow uploads to this folder via email** setting is enabled for a folder in the Admin Console, and the **Only allow email uploads from collaborators in this folder** setting is deactivated (unchecked).

If the conditions are not met, the parameter will have the following value: `folder_upload_email: null`."""
    access: Literal["open", "collaborators"] | None = Field(None, description="When this parameter has been set, users can email files\nto the email address that has been automatically\ncreated for this folder.\n\nTo create an email address, set this property either when\ncreating or updating the folder.\n\nWhen set to `collaborators`, only emails from registered email\naddresses for collaborators will be accepted. This includes\nany email aliases a user might have registered.\n\nWhen set to `open` it will accept emails from any email\naddress.")
    email: str | None = Field(None, description="The optional upload email address for this folder.", json_schema_extra={'format': 'email'})

class FolderMini(PermissiveModel):
    """A mini representation of a file version, used when
nested under another resource."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier that represent a folder.\n\nThe ID for any folder can be determined\nby visiting a folder in the web application\nand copying the ID from the URL. For example,\nfor the URL `https://*.app.box.com/folders/123`\nthe `folder_id` is `123`.")
    etag: str | None = Field(None, description="The HTTP `etag` of this folder. This can be used within some API\nendpoints in the `If-Match` and `If-None-Match` headers to only\nperform changes on the folder if (no) changes have happened.")
    type_: Literal["folder"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `folder`.")
    sequence_id: str | None | Any | None = None
    name: str | None = Field(None, description="The name of the folder.")

class FileModelPathCollection(PermissiveModel):
    total_count: int = Field(..., description="The number of folders in this list.", json_schema_extra={'format': 'int64'})
    entries: list[FolderMini] = Field(..., description="The parent folders for this item.")

class FileModelV1PathCollection(PermissiveModel):
    total_count: int = Field(..., description="The number of folders in this list.", json_schema_extra={'format': 'int64'})
    entries: list[FolderMini] = Field(..., description="The parent folders for this item.")

class FolderPathCollection(PermissiveModel):
    total_count: int = Field(..., description="The number of folders in this list.", json_schema_extra={'format': 'int64'})
    entries: list[FolderMini] = Field(..., description="The parent folders for this item.")

class FolderSharedLinkPermissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")

class FolderSharedLink(PermissiveModel):
    url: str = Field(..., description="The URL that can be used to access the item on Box.\n\nThis URL will display the item in Box's preview UI where the file\ncan be downloaded if allowed.\n\nThis URL will continue to work even when a custom `vanity_url`\nhas been set for this shared link.", json_schema_extra={'format': 'url'})
    download_url: str | None = Field(None, description="A URL that can be used to download the file. This URL can be used in\na browser to download the file. This URL includes the file\nextension so that the file will be saved with the right file type.\n\nThis property will be `null` for folders.", json_schema_extra={'format': 'url'})
    vanity_url: str | None = Field(None, description="The \"Custom URL\" that can also be used to preview the item on Box.  Custom\nURLs can only be created or modified in the Box Web application.", json_schema_extra={'format': 'url'})
    vanity_name: str | None = Field(None, description="The custom name of a shared link, as used in the `vanity_url` field.")
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The access level for this shared link.\n\n* `open` - provides access to this item to anyone with this link\n* `company` - only provides access to this item to people the same company\n* `collaborators` - only provides access to this item to people who are\n   collaborators on this item\n\nIf this field is omitted when creating the shared link, the access level\nwill be set to the default access level specified by the enterprise admin.")
    effective_access: Literal["open", "company", "collaborators"] = Field(..., description="The effective access level for the shared link. This can be a more\nrestrictive access level than the value in the `access` field when the\nenterprise settings restrict the allowed access levels.")
    effective_permission: Literal["can_edit", "can_download", "can_preview", "no_access"] = Field(..., description="The effective permissions for this shared link.\nThese result in the more restrictive combination of\nthe share link permissions and the item permissions set\nby the administrator, the owner, and any ancestor item\nsuch as a folder.")
    unshared_at: str | None = Field(None, description="The date and time when this link will be unshared. This field can only be\nset by users with paid accounts.", json_schema_extra={'format': 'date-time'})
    is_password_enabled: bool = Field(..., description="Defines if the shared link requires a password to access the item.")
    permissions: FolderSharedLinkPermissions | None = Field(None, description="Defines if this link allows a user to preview, edit, and download an item.\nThese permissions refer to the shared link only and\ndo not supersede permissions applied to the item itself.")
    download_count: int = Field(..., description="The number of times this item has been downloaded.")
    preview_count: int = Field(..., description="The number of times this item has been previewed.")

class FolderSharedLinkV0Permissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")

class FolderV1FolderUploadEmail(PermissiveModel):
    """The `folder_upload_email` parameter is not `null` if one of the following options is **true**:

  * The **Allow uploads to this folder via email** and the **Only allow email uploads from collaborators in this folder** are [enabled for a folder in the Admin Console](https://support.box.com/hc/en-us/articles/360043697534-Upload-to-Box-Through-Email), and the user has at least **Upload** permissions granted.

  * The **Allow uploads to this folder via email** setting is enabled for a folder in the Admin Console, and the **Only allow email uploads from collaborators in this folder** setting is deactivated (unchecked).

If the conditions are not met, the parameter will have the following value: `folder_upload_email: null`."""
    access: Literal["open", "collaborators"] | None = Field(None, description="When this parameter has been set, users can email files\nto the email address that has been automatically\ncreated for this folder.\n\nTo create an email address, set this property either when\ncreating or updating the folder.\n\nWhen set to `collaborators`, only emails from registered email\naddresses for collaborators will be accepted. This includes\nany email aliases a user might have registered.\n\nWhen set to `open` it will accept emails from any email\naddress.")
    email: str | None = Field(None, description="The optional upload email address for this folder.", json_schema_extra={'format': 'email'})

class FolderV1PathCollection(PermissiveModel):
    total_count: int = Field(..., description="The number of folders in this list.", json_schema_extra={'format': 'int64'})
    entries: list[FolderMini] = Field(..., description="The parent folders for this item.")

class FolderV1SharedLinkPermissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")

class FolderV1SharedLink(PermissiveModel):
    url: str = Field(..., description="The URL that can be used to access the item on Box.\n\nThis URL will display the item in Box's preview UI where the file\ncan be downloaded if allowed.\n\nThis URL will continue to work even when a custom `vanity_url`\nhas been set for this shared link.", json_schema_extra={'format': 'url'})
    download_url: str | None = Field(None, description="A URL that can be used to download the file. This URL can be used in\na browser to download the file. This URL includes the file\nextension so that the file will be saved with the right file type.\n\nThis property will be `null` for folders.", json_schema_extra={'format': 'url'})
    vanity_url: str | None = Field(None, description="The \"Custom URL\" that can also be used to preview the item on Box.  Custom\nURLs can only be created or modified in the Box Web application.", json_schema_extra={'format': 'url'})
    vanity_name: str | None = Field(None, description="The custom name of a shared link, as used in the `vanity_url` field.")
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The access level for this shared link.\n\n* `open` - provides access to this item to anyone with this link\n* `company` - only provides access to this item to people the same company\n* `collaborators` - only provides access to this item to people who are\n   collaborators on this item\n\nIf this field is omitted when creating the shared link, the access level\nwill be set to the default access level specified by the enterprise admin.")
    effective_access: Literal["open", "company", "collaborators"] = Field(..., description="The effective access level for the shared link. This can be a more\nrestrictive access level than the value in the `access` field when the\nenterprise settings restrict the allowed access levels.")
    effective_permission: Literal["can_edit", "can_download", "can_preview", "no_access"] = Field(..., description="The effective permissions for this shared link.\nThese result in the more restrictive combination of\nthe share link permissions and the item permissions set\nby the administrator, the owner, and any ancestor item\nsuch as a folder.")
    unshared_at: str | None = Field(None, description="The date and time when this link will be unshared. This field can only be\nset by users with paid accounts.", json_schema_extra={'format': 'date-time'})
    is_password_enabled: bool = Field(..., description="Defines if the shared link requires a password to access the item.")
    permissions: FolderV1SharedLinkPermissions | None = Field(None, description="Defines if this link allows a user to preview, edit, and download an item.\nThese permissions refer to the shared link only and\ndo not supersede permissions applied to the item itself.")
    download_count: int = Field(..., description="The number of times this item has been downloaded.")
    preview_count: int = Field(..., description="The number of times this item has been previewed.")

class FolderV1SharedLinkV0Permissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")

class GroupBase(PermissiveModel):
    """A base representation of a group."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier for this object.")
    type_: Literal["group"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `group`.")

class GroupMini(PermissiveModel):
    """Mini representation of a group, including id and name of
group."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier for this object.")
    type_: Literal["group"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `group`.")
    name: str | None = Field(None, description="The name of the group.")
    group_type: Literal["managed_group", "all_users_group"] | None = Field(None, description="The type of the group.")

class Group(PermissiveModel):
    """A standard representation of a group, as returned from any
group API endpoints by default."""
    created_at: str | None = Field(None, description="When the group object was created.", json_schema_extra={'format': 'date-time'})
    modified_at: str | None = Field(None, description="When the group object was last modified.", json_schema_extra={'format': 'date-time'})

class ItemsOrderItem(PermissiveModel):
    """The order in which a pagination is ordered."""
    by: str | None = Field(None, description="The field to order by.")
    direction: Literal["ASC", "DESC"] | None = Field(None, description="The direction to order by, either ascending or descending.")

class ItemsV1OrderItem(PermissiveModel):
    """The order in which a pagination is ordered."""
    by: str | None = Field(None, description="The field to order by.")
    direction: Literal["ASC", "DESC"] | None = Field(None, description="The direction to order by, either ascending or descending.")

class KeywordSkillCardEntriesItem(PermissiveModel):
    """An entry in the `entries` attribute of a metadata card."""
    text: str | None = Field(None, description="The text of the keyword.")

class KeywordSkillCardInvocation(PermissiveModel):
    """The invocation of this service, used to track
which instance of a service applied the metadata."""
    type_: Literal["skill_invocation"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `skill_invocation`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A custom identifier that represent the instance of\nthe service that applied this metadata. For example,\nif your `image-recognition-service` runs on multiple\nnodes, this field can be used to identify the ID of\nthe node that was used to apply the metadata.")

class KeywordSkillCardSkill(PermissiveModel):
    """The service that applied this metadata."""
    type_: Literal["service"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `service`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A custom identifier that represent the service that\napplied this metadata.")

class KeywordSkillCardSkillCardTitle(PermissiveModel):
    """The title of the card."""
    code: str | None = Field(None, description="An optional identifier for the title.")
    message: str = Field(..., description="The actual title to show in the UI.")

class KeywordSkillCard(PermissiveModel):
    """A skill card that contains a set of keywords."""
    created_at: str | None = Field(None, description="The optional date and time this card was created at.", json_schema_extra={'format': 'date-time'})
    type_: Literal["skill_card"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `skill_card`.")
    skill_card_type: Literal["keyword"] = Field(..., description="The value will always be `keyword`.")
    skill_card_title: KeywordSkillCardSkillCardTitle | None = Field(None, description="The title of the card.")
    skill: KeywordSkillCardSkill = Field(..., description="The service that applied this metadata.")
    invocation: KeywordSkillCardInvocation = Field(..., description="The invocation of this service, used to track\nwhich instance of a service applied the metadata.")
    entries: list[KeywordSkillCardEntriesItem] = Field(..., description="An list of entries in the metadata card.")

class MetadataBase(PermissiveModel):
    """The base representation of a metadata instance."""
    parent: str | None = Field(None, validation_alias="$parent", serialization_alias="$parent", description="The identifier of the item that this metadata instance\nhas been attached to. This combines the `type` and the `id`\nof the parent in the form `{type}_{id}`.")
    template: str | None = Field(None, validation_alias="$template", serialization_alias="$template", description="The name of the template.")
    scope: str | None = Field(None, validation_alias="$scope", serialization_alias="$scope", description="An ID for the scope in which this template\nhas been applied. This will be `enterprise_{enterprise_id}` for templates\ndefined for use in this enterprise, and `global` for general templates\nthat are available to all enterprises using Box.")
    version: int | None = Field(None, validation_alias="$version", serialization_alias="$version", description="The version of the metadata instance. This version starts at 0 and\nincreases every time a user-defined property is modified.")

class Metadata(PermissiveModel):
    """An instance of a metadata template, which has been applied to a file or
folder."""
    parent: str | None = Field(None, validation_alias="$parent", serialization_alias="$parent", description="The identifier of the item that this metadata instance\nhas been attached to. This combines the `type` and the `id`\nof the parent in the form `{type}_{id}`.")
    template: str | None = Field(None, validation_alias="$template", serialization_alias="$template", description="The name of the template.")
    scope: str | None = Field(None, validation_alias="$scope", serialization_alias="$scope", description="An ID for the scope in which this template\nhas been applied. This will be `enterprise_{enterprise_id}` for templates\ndefined for use in this enterprise, and `global` for general templates\nthat are available to all enterprises using Box.")
    version: int | None = Field(None, validation_alias="$version", serialization_alias="$version", description="The version of the metadata instance. This version starts at 0 and\nincreases every time a user-defined property is modified.")

class MetadataFieldFilterDateRange(PermissiveModel):
    """Specifies which `date` field on the template to filter the search
results by, specifying a range of dates that can match."""
    lt: str | None = Field(None, description="Specifies the (inclusive) upper bound for the metadata field\nvalue. The value of a field must be lower than (`lt`) or\nequal to this value for the search query to match this\ntemplate.", json_schema_extra={'format': 'date-time'})
    gt: str | None = Field(None, description="Specifies the (inclusive) lower bound for the metadata field\nvalue. The value of a field must be greater than (`gt`) or\nequal to this value for the search query to match this\ntemplate.", json_schema_extra={'format': 'date-time'})

class MetadataFieldFilterFloatRange(PermissiveModel):
    """Specifies which `float` field on the template to filter the search
results by, specifying a range of values that can match."""
    lt: float | None = Field(None, description="Specifies the (inclusive) upper bound for the metadata field\nvalue. The value of a field must be lower than (`lt`) or\nequal to this value for the search query to match this\ntemplate.")
    gt: float | None = Field(None, description="Specifies the (inclusive) lower bound for the metadata field\nvalue. The value of a field must be greater than (`gt`) or\nequal to this value for the search query to match this\ntemplate.")

class MetadataFilter(PermissiveModel):
    """A metadata template used to filter the search results."""
    scope: Literal["global", "enterprise", "enterprise_{enterprise_id}"] | None = Field(None, description="Specifies the scope of the template to filter search results by.\n\nThis will be `enterprise_{enterprise_id}` for templates defined\nfor use in this enterprise, and `global` for general templates\nthat are available to all enterprises using Box.")
    template_key: str | None = Field(None, validation_alias="templateKey", serialization_alias="templateKey", description="The key of the template used to filter search results.\n\nIn many cases the template key is automatically derived\nof its display name, for example `Contract Template` would\nbecome `contractTemplate`. In some cases the creator of the\ntemplate will have provided its own template key.\n\nPlease [list the templates for an enterprise][list], or\nget all instances on a [file][file] or [folder][folder]\nto inspect a template's key.\n\n[list]: https://developer.box.com/reference/get-metadata-templates-enterprise\n[file]: https://developer.box.com/reference/get-files-id-metadata\n[folder]: https://developer.box.com/reference/get-folders-id-metadata")
    filters: dict[str, str | float | list[str] | MetadataFieldFilterFloatRange | MetadataFieldFilterDateRange] | None = Field(None, description="Specifies which fields on the template to filter the search\nresults by. When more than one field is specified, the query\nperforms a logical `AND` to ensure that the instance of the\ntemplate matches each of the fields specified.")

class MetadataFull(PermissiveModel):
    """An instance of a metadata template, which has been applied to a file or
folder."""
    can_edit: bool | None = Field(None, validation_alias="$canEdit", serialization_alias="$canEdit", description="Whether the user can edit this metadata instance.")
    id_: str | None = Field(None, validation_alias="$id", serialization_alias="$id", description="A UUID to identify the metadata instance.", max_length=36, json_schema_extra={'format': 'uuid'})
    type_: str | None = Field(None, validation_alias="$type", serialization_alias="$type", description="A unique identifier for the \"type\" of this instance. This is an\ninternal system property and should not be used by a client\napplication.")
    type_version: int | None = Field(None, validation_alias="$typeVersion", serialization_alias="$typeVersion", description="The last-known version of the template of the object. This is an\ninternal system property and should not be used by a client\napplication.")

class PostAiAgentsBodyAskBasicImage(PermissiveModel):
    """AI agent processor used to handle basic text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm | None = Field(None, description="The parameters for the LLM endpoint specific to a model.")
    system_message: str | None = Field(None, description="System messages try to help the LLM \"understand\" its role and what it is supposed to do.")
    prompt_template: str | None = Field(None, description="The prompt template contains contextual information of the request and the user prompt.\nWhen passing `prompt_template` parameters, you **must include** inputs for `{user_question}` and `{content}`.\n`{current_date}` is optional, depending on the use.", max_length=10000, pattern="(\\{user_question\\}[\\s\\S]*?\\{content\\}|\\{content\\}[\\s\\S]*?\\{user_question\\})")
    is_custom_instructions_included: bool | None = Field(None, description="True if system message contains custom instructions placeholder, false otherwise.")

class PostAiAgentsBodyAskBasicImageMulti(PermissiveModel):
    """AI agent processor used to handle basic text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm | None = Field(None, description="The parameters for the LLM endpoint specific to a model.")
    system_message: str | None = Field(None, description="System messages try to help the LLM \"understand\" its role and what it is supposed to do.")
    prompt_template: str | None = Field(None, description="The prompt template contains contextual information of the request and the user prompt.\nWhen passing `prompt_template` parameters, you **must include** inputs for `{user_question}` and `{content}`.\n`{current_date}` is optional, depending on the use.", max_length=10000, pattern="(\\{user_question\\}[\\s\\S]*?\\{content\\}|\\{content\\}[\\s\\S]*?\\{user_question\\})")
    is_custom_instructions_included: bool | None = Field(None, description="True if system message contains custom instructions placeholder, false otherwise.")

class PostAiAgentsBodyAskBasicText(PermissiveModel):
    """AI agent processor used to handle basic text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm | None = Field(None, description="The parameters for the LLM endpoint specific to a model.")
    system_message: str | None = Field(None, description="System messages try to help the LLM \"understand\" its role and what it is supposed to do.")
    prompt_template: str | None = Field(None, description="The prompt template contains contextual information of the request and the user prompt.\nWhen passing `prompt_template` parameters, you **must include** inputs for `{user_question}` and `{content}`.\n`{current_date}` is optional, depending on the use.", max_length=10000, pattern="(\\{user_question\\}[\\s\\S]*?\\{content\\}|\\{content\\}[\\s\\S]*?\\{user_question\\})")
    is_custom_instructions_included: bool | None = Field(None, description="True if system message contains custom instructions placeholder, false otherwise.")

class PostAiAgentsBodyAskBasicTextMulti(PermissiveModel):
    """AI agent processor used to handle basic text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm | None = Field(None, description="The parameters for the LLM endpoint specific to a model.")
    system_message: str | None = Field(None, description="System messages try to help the LLM \"understand\" its role and what it is supposed to do.")
    prompt_template: str | None = Field(None, description="The prompt template contains contextual information of the request and the user prompt.\nWhen passing `prompt_template` parameters, you **must include** inputs for `{user_question}` and `{content}`.\n`{current_date}` is optional, depending on the use.", max_length=10000, pattern="(\\{user_question\\}[\\s\\S]*?\\{content\\}|\\{content\\}[\\s\\S]*?\\{user_question\\})")
    is_custom_instructions_included: bool | None = Field(None, description="True if system message contains custom instructions placeholder, false otherwise.")

class PostAiAgentsBodyAskLongTextEmbeddingsStrategy(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The strategy used for the AI agent for calculating embeddings.")
    num_tokens_per_chunk: int | None = Field(None, description="The number of tokens per chunk.", ge=1, le=512)

class PostAiAgentsBodyAskLongTextEmbeddings(PermissiveModel):
    model: str | None = Field(None, description="The model used for the AI agent for calculating embeddings.")
    strategy: PostAiAgentsBodyAskLongTextEmbeddingsStrategy | None = None

class PostAiAgentsBodyAskLongText(PermissiveModel):
    """AI agent processor used to to handle longer text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm | None = Field(None, description="The parameters for the LLM endpoint specific to a model.")
    system_message: str | None = Field(None, description="System messages try to help the LLM \"understand\" its role and what it is supposed to do.")
    prompt_template: str | None = Field(None, description="The prompt template contains contextual information of the request and the user prompt.\nWhen passing `prompt_template` parameters, you **must include** inputs for `{user_question}` and `{content}`.\n`{current_date}` is optional, depending on the use.", max_length=10000, pattern="(\\{user_question\\}[\\s\\S]*?\\{content\\}|\\{content\\}[\\s\\S]*?\\{user_question\\})")
    embeddings: PostAiAgentsBodyAskLongTextEmbeddings | None = None
    is_custom_instructions_included: bool | None = Field(None, description="True if system message contains custom instructions placeholder, false otherwise.")

class PostAiAgentsBodyAskLongTextMultiEmbeddingsStrategy(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The strategy used for the AI agent for calculating embeddings.")
    num_tokens_per_chunk: int | None = Field(None, description="The number of tokens per chunk.", ge=1, le=512)

class PostAiAgentsBodyAskLongTextMultiEmbeddings(PermissiveModel):
    model: str | None = Field(None, description="The model used for the AI agent for calculating embeddings.")
    strategy: PostAiAgentsBodyAskLongTextMultiEmbeddingsStrategy | None = None

class PostAiAgentsBodyAskLongTextMulti(PermissiveModel):
    """AI agent processor used to to handle longer text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm | None = Field(None, description="The parameters for the LLM endpoint specific to a model.")
    system_message: str | None = Field(None, description="System messages try to help the LLM \"understand\" its role and what it is supposed to do.")
    prompt_template: str | None = Field(None, description="The prompt template contains contextual information of the request and the user prompt.\nWhen passing `prompt_template` parameters, you **must include** inputs for `{user_question}` and `{content}`.\n`{current_date}` is optional, depending on the use.", max_length=10000, pattern="(\\{user_question\\}[\\s\\S]*?\\{content\\}|\\{content\\}[\\s\\S]*?\\{user_question\\})")
    embeddings: PostAiAgentsBodyAskLongTextMultiEmbeddings | None = None
    is_custom_instructions_included: bool | None = Field(None, description="True if system message contains custom instructions placeholder, false otherwise.")

class PostAiAgentsBodyAskSpreadsheet(PermissiveModel):
    """The AI agent tool used to handle spreadsheets and tabular data."""
    model: str | None = Field(None, description="The model used for the AI agent for spreadsheets. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm | None = Field(None, description="The parameters for the LLM endpoint specific to a model.")

class PostAiAgentsBodyExtractBasicImage(PermissiveModel):
    """AI agent processor used to handle basic text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm | None = Field(None, description="The parameters for the LLM endpoint specific to a model.")
    system_message: str | None = Field(None, description="System messages try to help the LLM \"understand\" its role and what it is supposed to do.")
    prompt_template: str | None = Field(None, description="The prompt template contains contextual information of the request and the user prompt.\nWhen passing `prompt_template` parameters, you **must include** inputs for `{user_question}` and `{content}`.\n`{current_date}` is optional, depending on the use.", max_length=10000, pattern="(\\{user_question\\}[\\s\\S]*?\\{content\\}|\\{content\\}[\\s\\S]*?\\{user_question\\})")
    is_custom_instructions_included: bool | None = Field(None, description="True if system message contains custom instructions placeholder, false otherwise.")

class PostAiAgentsBodyExtractBasicText(PermissiveModel):
    """AI agent processor used to handle basic text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm | None = Field(None, description="The parameters for the LLM endpoint specific to a model.")
    system_message: str | None = Field(None, description="System messages try to help the LLM \"understand\" its role and what it is supposed to do.")
    prompt_template: str | None = Field(None, description="The prompt template contains contextual information of the request and the user prompt.\nWhen passing `prompt_template` parameters, you **must include** inputs for `{user_question}` and `{content}`.\n`{current_date}` is optional, depending on the use.", max_length=10000, pattern="(\\{user_question\\}[\\s\\S]*?\\{content\\}|\\{content\\}[\\s\\S]*?\\{user_question\\})")
    is_custom_instructions_included: bool | None = Field(None, description="True if system message contains custom instructions placeholder, false otherwise.")

class PostAiAgentsBodyExtractLongTextEmbeddingsStrategy(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The strategy used for the AI agent for calculating embeddings.")
    num_tokens_per_chunk: int | None = Field(None, description="The number of tokens per chunk.", ge=1, le=512)

class PostAiAgentsBodyExtractLongTextEmbeddings(PermissiveModel):
    model: str | None = Field(None, description="The model used for the AI agent for calculating embeddings.")
    strategy: PostAiAgentsBodyExtractLongTextEmbeddingsStrategy | None = None

class PostAiAgentsBodyExtractLongText(PermissiveModel):
    """AI agent processor used to to handle longer text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm | None = Field(None, description="The parameters for the LLM endpoint specific to a model.")
    system_message: str | None = Field(None, description="System messages try to help the LLM \"understand\" its role and what it is supposed to do.")
    prompt_template: str | None = Field(None, description="The prompt template contains contextual information of the request and the user prompt.\nWhen passing `prompt_template` parameters, you **must include** inputs for `{user_question}` and `{content}`.\n`{current_date}` is optional, depending on the use.", max_length=10000, pattern="(\\{user_question\\}[\\s\\S]*?\\{content\\}|\\{content\\}[\\s\\S]*?\\{user_question\\})")
    embeddings: PostAiAgentsBodyExtractLongTextEmbeddings | None = None
    is_custom_instructions_included: bool | None = Field(None, description="True if system message contains custom instructions placeholder, false otherwise.")

class PostAiAgentsBodyTextGenBasicGenEmbeddingsStrategy(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The strategy used for the AI agent for calculating embeddings.")
    num_tokens_per_chunk: int | None = Field(None, description="The number of tokens per chunk.", ge=1, le=512)

class PostAiAgentsBodyTextGenBasicGenEmbeddings(PermissiveModel):
    model: str | None = Field(None, description="The model used for the AI agent for calculating embeddings.")
    strategy: PostAiAgentsBodyTextGenBasicGenEmbeddingsStrategy | None = None

class PostAiAgentsBodyTextGenBasicGen(PermissiveModel):
    """AI agent basic tool used to generate text."""
    model: str | None = Field(None, description="The model used for the AI agent for basic text. For specific model values, see the [available models list](https://developer.box.com/guides/box-ai/ai-models).")
    num_tokens_for_completion: int | None = Field(None, description="The number of tokens for completion.", ge=1)
    llm_endpoint_params: AiLlmEndpointParamsOpenAi | AiLlmEndpointParamsGoogle | AiLlmEndpointParamsAws | AiLlmEndpointParamsIbm | None = Field(None, description="The parameters for the LLM endpoint specific to a model.")
    system_message: str | None = Field(None, description="System messages aim at helping the LLM understand its role and what it is supposed to do.\nThe input for `{current_date}` is optional, depending on the use.")
    prompt_template: str | None = Field(None, description="The prompt template contains contextual information of the request and the user prompt.\n\nWhen using the `prompt_template` parameter, you **must include** input for `{user_question}`.\nInputs for `{current_date}` and `{content}` are optional, depending on the use.", max_length=10000, pattern="\\{user_question\\}")
    embeddings: PostAiAgentsBodyTextGenBasicGenEmbeddings | None = None
    content_template: str | None = Field(None, description="How the content should be included in a request to the LLM.\nInput for `{content}` is optional, depending on the use.")
    is_custom_instructions_included: bool | None = Field(None, description="True if system message contains custom instructions placeholder, false otherwise.")

class PostAiExtractStructuredBodyFieldsItemOptionsItem(PermissiveModel):
    key: str = Field(..., description="A unique identifier for the field.")

class PostAiExtractStructuredBodyFieldsItem(PermissiveModel):
    """The fields to be extracted from the provided items."""
    key: str = Field(..., description="A unique identifier for the field.")
    description: str | None = Field(None, description="A description of the field.")
    display_name: str | None = Field(None, validation_alias="displayName", serialization_alias="displayName", description="The display name of the field.")
    prompt: str | None = Field(None, description="The context about the key that may include how to find and format it.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the field. It include but is not limited to string, float, date, enum, and multiSelect.")
    options: list[PostAiExtractStructuredBodyFieldsItemOptionsItem] | None = Field(None, description="A list of options for this field. This is most often used in combination with the enum and multiSelect field types.")

class PostFilesIdBodyParent(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of parent item.")

class PostFoldersBodyFolderUploadEmail(PermissiveModel):
    access: Literal["open", "collaborators"] | None = Field(None, description="When this parameter has been set, users can email files\nto the email address that has been automatically\ncreated for this folder.\n\nTo create an email address, set this property either when\ncreating or updating the folder.\n\nWhen set to `collaborators`, only emails from registered email\naddresses for collaborators will be accepted. This includes\nany email aliases a user might have registered.\n\nWhen set to `open` it will accept emails from any email\naddress.")

class PostFoldersIdBodyParent(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of parent item.")

class PostIntegrationMappingsTeamsBodyBoxItem(PermissiveModel):
    type_: Literal["folder"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `folder`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="ID of the folder.")

class PostIntegrationMappingsTeamsBodyPartnerItem(PermissiveModel):
    type_: Literal["channel", "team"] = Field(..., validation_alias="type", serialization_alias="type", description="Type of the mapped item referenced in `id`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="ID of the mapped item (of type referenced in `type`).")
    tenant_id: str = Field(..., description="ID of the tenant that is registered with Microsoft Teams.")
    team_id: str = Field(..., description="ID of the team that is registered with Microsoft Teams.")

class PostMetadataQueriesExecuteReadBodyOrderByItem(PermissiveModel):
    """An object representing one of the metadata template fields to sort the
metadata query results by."""
    field_key: str | None = Field(None, description="The metadata template field to order by.\n\nThe `field_key` represents the `key` value of a field from the\nmetadata template being searched for.")
    direction: Literal["ASC", "DESC", "asc", "desc"] | None = Field(None, description="The direction to order by, either ascending or descending.\n\nThe `ordering` direction must be the same for each item in the\narray.")

class PostMetadataTemplatesSchemaBodyFieldsItemOptionsItem(PermissiveModel):
    """An option for a Metadata Template Field.

Options only need to be provided for fields of type `enum` and `multiSelect`.
Options represent the value(s) a user can select for the field either through
the UI or through the API."""
    key: str = Field(..., description="The text value of the option. This represents both the display name of the\noption and the internal key used when updating templates.")

class PostMetadataTemplatesSchemaBodyFieldsItemOptionsRules(PermissiveModel):
    """An object defining additional rules for the options of the taxonomy field.
This property is required when the field `type` is set to `taxonomy`."""
    multi_select: bool | None = Field(None, validation_alias="multiSelect", serialization_alias="multiSelect", description="Whether to allow users to select multiple values.")
    selectable_levels: list[int] | None = Field(None, validation_alias="selectableLevels", serialization_alias="selectableLevels", description="An array of integers defining which levels of the taxonomy are\nselectable by users.")

class PostMetadataTemplatesSchemaBodyFieldsItem(PermissiveModel):
    """A field within a metadata template. Fields can be a basic text, date, or
number field, a list of options, or a taxonomy."""
    type_: Literal["string", "float", "date", "enum", "multiSelect", "taxonomy"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of field. The basic fields are a `string` field for text, a\n`float` field for numbers, and a `date` field to present the user with a\ndate-time picker.\n\nAdditionally, metadata templates support an `enum` field for a basic list\nof items, and ` multiSelect` field for a similar list of items where the\nuser can select more than one value.\n\nMetadata taxonomies are also supported as a `taxonomy` field type \nwith a specific set of additional properties, which describe its structure.")
    key: str = Field(..., description="A unique identifier for the field. The identifier must\nbe unique within the template to which it belongs.", max_length=256)
    display_name: str = Field(..., validation_alias="displayName", serialization_alias="displayName", description="The display name of the field as it is shown to the user in the web and\nmobile apps.", max_length=4096)
    description: str | None = Field(None, description="A description of the field. This is not shown to the user.", max_length=4096)
    hidden: bool | None = Field(None, description="Whether this field is hidden in the UI for the user and can only be set\nthrough the API instead.")
    options: list[PostMetadataTemplatesSchemaBodyFieldsItemOptionsItem] | None = Field(None, description="A list of options for this field. This is used in combination with the\n`enum` and `multiSelect` field types.")
    taxonomy_key: str | None = Field(None, validation_alias="taxonomyKey", serialization_alias="taxonomyKey", description="The unique key of the metadata taxonomy to use for this taxonomy field.\nThis property is required when the field `type` is set to `taxonomy`.")
    namespace: str | None = Field(None, description="The namespace of the metadata taxonomy to use for this taxonomy field.\nThis property is required when the field `type` is set to `taxonomy`.")
    options_rules: PostMetadataTemplatesSchemaBodyFieldsItemOptionsRules | None = Field(None, validation_alias="optionsRules", serialization_alias="optionsRules", description="An object defining additional rules for the options of the taxonomy field.\nThis property is required when the field `type` is set to `taxonomy`.")

class PostMetadataTemplatesSchemaClassificationsBodyFieldsItemOptionsItemStaticConfigClassification(PermissiveModel):
    """Additional information about the classification."""
    classification_definition: str | None = Field(None, validation_alias="classificationDefinition", serialization_alias="classificationDefinition", description="A longer description of the classification.")
    color_id: int | None = Field(None, validation_alias="colorID", serialization_alias="colorID", description="An identifier used to assign a color to\na classification label.\n\nMapping between a `colorID` and a color may\nchange without notice. Currently, the color\nmappings are as follows.\n\n* `0`: Yellow.\n* `1`: Orange.\n* `2`: Watermelon red.\n* `3`: Purple rain.\n* `4`: Light blue.\n* `5`: Dark blue.\n* `6`: Light green.\n* `7`: Gray.", json_schema_extra={'format': 'int64'})

class PostMetadataTemplatesSchemaClassificationsBodyFieldsItemOptionsItemStaticConfig(PermissiveModel):
    """Additional information about the classification."""
    classification: PostMetadataTemplatesSchemaClassificationsBodyFieldsItemOptionsItemStaticConfigClassification | None = Field(None, description="Additional information about the classification.")

class PostMetadataTemplatesSchemaClassificationsBodyFieldsItemOptionsItem(PermissiveModel):
    """An individual classification."""
    key: str = Field(..., description="The display name and key this classification. This\nwill be show in the Box UI.")
    static_config: PostMetadataTemplatesSchemaClassificationsBodyFieldsItemOptionsItemStaticConfig | None = Field(None, validation_alias="staticConfig", serialization_alias="staticConfig", description="Additional information about the classification.")

class PostMetadataTemplatesSchemaClassificationsBodyFieldsItem(PermissiveModel):
    """The `enum` field which holds all the valid classification
values."""
    type_: Literal["enum"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the field\nthat is always enum.")
    key: Literal["Box__Security__Classification__Key"] = Field(..., description="Defines classifications \navailable in the enterprise.")
    display_name: Literal["Classification"] = Field(..., validation_alias="displayName", serialization_alias="displayName", description="A display name for the classification.")
    hidden: bool | None = Field(None, description="Determines if the classification\ntemplate is\nhidden or available on\nweb and mobile\ndevices.")
    options: list[PostMetadataTemplatesSchemaClassificationsBodyFieldsItemOptionsItem] = Field(..., description="The actual list of classifications that are present on\nthis template.")

class PostRetentionPolicyAssignmentsBodyFilterFieldsItem(PermissiveModel):
    field: str | None = Field(None, description="The metadata attribute key id.")
    value: str | None = Field(None, description="The metadata attribute field id. For value, only\nenum and multiselect types are supported.")

class PostShieldInformationBarrierSegmentMembersBodyUser(PermissiveModel):
    """User to which restriction will be applied."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier for this user.")
    type_: Literal["user"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `user`.")

class PostShieldInformationBarriersBodyEnterprise(PermissiveModel):
    """The `type` and `id` of enterprise this barrier is under."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The unique identifier for this enterprise.")
    type_: Literal["enterprise"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The value will always be `enterprise`.")

class PostWebLinksIdBodyParent(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of parent item.")

class PostWorkflowsIdStartBodyFilesItem(PermissiveModel):
    """A file the workflow should start for."""
    type_: Literal["file"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The type of the file object.")
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The id of the file.")

class PostZipDownloadsBodyItemsItem(PermissiveModel):
    """An item to add to the `zip` archive. This can be a file or a folder."""
    type_: Literal["file", "folder"] = Field(..., validation_alias="type", serialization_alias="type", description="The type of the item to add to the archive.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The identifier of the item to add to the archive. When this item is\na folder then this can not be the root folder with ID `0`.")

class PutFilesIdBodyCollectionsItem(PermissiveModel):
    """The bare basic reference for an object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The unique identifier for this object.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type for this object.")

class PutFilesIdBodyParent(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of parent item.")
    user_id: str | None = Field(None, description="The input for `user_id` is optional. Moving to non-root folder is not allowed when `user_id` is present. Parent folder id should be zero when `user_id` is provided.")

class PutFilesIdBodySharedLinkPermissions(PermissiveModel):
    can_download: bool | None = Field(None, description="If the shared link allows for downloading of files.\nThis can only be set when `access` is set to\n`open` or `company`.")

class PutFilesIdBodySharedLink(PermissiveModel):
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The level of access for the shared link. This can be\nrestricted to anyone with the link (`open`), only people\nwithin the company (`company`) and only those who\nhave been invited to the folder (`collaborators`).\n\nIf not set, this field defaults to the access level specified\nby the enterprise admin. To create a shared link with this\ndefault setting pass the `shared_link` object with\nno `access` field, for example `{ \"shared_link\": {} }`.\n\nThe `company` access level is only available to paid\naccounts.")
    password: str | None = Field(None, description="The password required to access the shared link. Set the\npassword to `null` to remove it.\nPasswords must now be at least eight characters\nlong and include a number, upper case letter, or\na non-numeric or non-alphabetic character.\nA password can only be set when `access` is set to `open`.")
    vanity_name: str | None = Field(None, description="Defines a custom vanity name to use in the shared link URL,\nfor example `https://app.box.com/v/my-shared-link`.\n\nCustom URLs should not be used when sharing sensitive content\nas vanity URLs are a lot easier to guess than regular shared links.")
    unshared_at: str | None = Field(None, description="The timestamp at which this shared link will\nexpire. This field can only be set by\nusers with paid accounts.", json_schema_extra={'format': 'date-time'})
    permissions: PutFilesIdBodySharedLinkPermissions | None = None

class PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoBodyItem(PermissiveModel):
    """The operation to perform on the classification
metadata template instance. In this case, it use
used to replace the value stored for the
`Box__Security__Classification__Key` field with a new
value."""
    op: Literal["replace"] = Field(..., description="The value will always be `replace`.")
    path: Literal["/Box__Security__Classification__Key"] = Field(..., description="Defines classifications\navailable in the enterprise.")
    value: str = Field(..., description="The name of the classification to apply to this file.\n\nTo list the available classifications in an enterprise,\nuse the classification API to retrieve the\n[classification template](https://developer.box.com/reference/get-metadata-templates-enterprise-securityClassification-6VMVochwUWo-schema)\nwhich lists all available classification keys.")

class PutFilesIdMetadataIdIdBodyItem(PermissiveModel):
    """A [JSON-Patch](https://tools.ietf.org/html/rfc6902) operation for a
change to make to the metadata instance."""
    op: Literal["add", "replace", "remove", "test", "move", "copy"] | None = Field(None, description="The type of change to perform on the template. Some\nof these are hazardous as they will change existing templates.")
    path: str | None = Field(None, description="The location in the metadata JSON object\nto apply the changes to, in the format of a\n[JSON-Pointer](https://tools.ietf.org/html/rfc6901).\n\nThe path must always be prefixed with a `/` to represent the root\nof the template. The characters `~` and `/` are reserved\ncharacters and must be escaped in the key.")
    value: str | int | float | list[str] | None = None
    from_: str | None = Field(None, validation_alias="from", serialization_alias="from", description="The location in the metadata JSON object to move or copy a value\nfrom. Required for `move` or `copy` operations and must be in the\nformat of a [JSON-Pointer](https://tools.ietf.org/html/rfc6901).")

class PutFoldersIdBodyCollectionsItem(PermissiveModel):
    """The bare basic reference for an object."""
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The unique identifier for this object.")
    type_: str | None = Field(None, validation_alias="type", serialization_alias="type", description="The type for this object.")

class PutFoldersIdBodyFolderUploadEmail(PermissiveModel):
    access: Literal["open", "collaborators"] | None = Field(None, description="When this parameter has been set, users can email files\nto the email address that has been automatically\ncreated for this folder.\n\nTo create an email address, set this property either when\ncreating or updating the folder.\n\nWhen set to `collaborators`, only emails from registered email\naddresses for collaborators will be accepted. This includes\nany email aliases a user might have registered.\n\nWhen set to `open` it will accept emails from any email\naddress.")

class PutFoldersIdBodyParent(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of parent item.")
    user_id: str | None = Field(None, description="The input for `user_id` is optional. Moving to non-root folder is not allowed when `user_id` is present. Parent folder id should be zero when `user_id` is provided.")

class PutFoldersIdBodySharedLinkPermissions(PermissiveModel):
    can_download: bool | None = Field(None, description="If the shared link allows for downloading of files.\nThis can only be set when `access` is set to\n`open` or `company`.")

class PutFoldersIdBodySharedLink(PermissiveModel):
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The level of access for the shared link. This can be\nrestricted to anyone with the link (`open`), only people\nwithin the company (`company`) and only those who\nhave been invited to the folder (`collaborators`).\n\nIf not set, this field defaults to the access level specified\nby the enterprise admin. To create a shared link with this\ndefault setting pass the `shared_link` object with\nno `access` field, for example `{ \"shared_link\": {} }`.\n\nThe `company` access level is only available to paid\naccounts.")
    password: str | None = Field(None, description="The password required to access the shared link. Set the\npassword to `null` to remove it.\nPasswords must now be at least eight characters\nlong and include a number, upper case letter, or\na non-numeric or non-alphabetic character.\nA password can only be set when `access` is set to `open`.")
    vanity_name: str | None = Field(None, description="Defines a custom vanity name to use in the shared link URL,\nfor example `https://app.box.com/v/my-shared-link`.\n\nCustom URLs should not be used when sharing sensitive content\nas vanity URLs are a lot easier to guess than regular shared links.")
    unshared_at: str | None = Field(None, description="The timestamp at which this shared link will\nexpire. This field can only be set by\nusers with paid accounts.", json_schema_extra={'format': 'date-time'})
    permissions: PutFoldersIdBodySharedLinkPermissions | None = None

class PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoBodyItem(PermissiveModel):
    """The operation to perform on the classification
metadata template instance. In this case, it use
used to replace the value stored for the
`Box__Security__Classification__Key` field with a new
value."""
    op: Literal["replace"] = Field(..., description="The value will always be `replace`.")
    path: Literal["/Box__Security__Classification__Key"] = Field(..., description="Defines classifications\navailable in the enterprise.")
    value: str = Field(..., description="The name of the classification to apply to this folder.\n\nTo list the available classifications in an enterprise,\nuse the classification API to retrieve the\n[classification template](https://developer.box.com/reference/get-metadata-templates-enterprise-securityClassification-6VMVochwUWo-schema)\nwhich lists all available classification keys.")

class PutFoldersIdMetadataIdIdBodyItem(PermissiveModel):
    """A [JSON-Patch](https://tools.ietf.org/html/rfc6902) operation for a
change to make to the metadata instance."""
    op: Literal["add", "replace", "remove", "test", "move", "copy"] | None = Field(None, description="The type of change to perform on the template. Some\nof these are hazardous as they will change existing templates.")
    path: str | None = Field(None, description="The location in the metadata JSON object\nto apply the changes to, in the format of a\n[JSON-Pointer](https://tools.ietf.org/html/rfc6901).\n\nThe path must always be prefixed with a `/` to represent the root\nof the template. The characters `~` and `/` are reserved\ncharacters and must be escaped in the key.")
    value: str | int | float | list[str] | None = None
    from_: str | None = Field(None, validation_alias="from", serialization_alias="from", description="The location in the metadata JSON object to move or copy a value\nfrom. Required for `move` or `copy` operations and must be in the\nformat of a [JSON-Pointer](https://tools.ietf.org/html/rfc6901).")

class PutMetadataTemplatesIdIdSchemaBodyItem(PermissiveModel):
    """A [JSON-Patch](https://tools.ietf.org/html/rfc6902) operation for a
change to make to the metadata instance."""
    op: Literal["editTemplate", "addField", "reorderFields", "addEnumOption", "reorderEnumOptions", "reorderMultiSelectOptions", "addMultiSelectOption", "editField", "removeField", "editEnumOption", "removeEnumOption", "editMultiSelectOption", "removeMultiSelectOption"] = Field(..., description="The type of change to perform on the template. Some\nof these are hazardous as they will change existing templates.")
    data: dict[str, Any] | None = Field(None, description="The data for the operation. This will vary depending on the\noperation being performed.")
    field_key: str | None = Field(None, validation_alias="fieldKey", serialization_alias="fieldKey", description="For operations that affect a single field this defines the key of\nthe field that is affected.")
    field_keys: list[str] | None = Field(None, validation_alias="fieldKeys", serialization_alias="fieldKeys", description="For operations that affect multiple fields this defines the keys\nof the fields that are affected.")
    enum_option_key: str | None = Field(None, validation_alias="enumOptionKey", serialization_alias="enumOptionKey", description="For operations that affect a single `enum` option this defines\nthe key of the option that is affected.")
    enum_option_keys: list[str] | None = Field(None, validation_alias="enumOptionKeys", serialization_alias="enumOptionKeys", description="For operations that affect multiple `enum` options this defines\nthe keys of the options that are affected.")
    multi_select_option_key: str | None = Field(None, validation_alias="multiSelectOptionKey", serialization_alias="multiSelectOptionKey", description="For operations that affect a single multi select option this\ndefines the key of the option that is affected.")
    multi_select_option_keys: list[str] | None = Field(None, validation_alias="multiSelectOptionKeys", serialization_alias="multiSelectOptionKeys", description="For operations that affect multiple multi select options this\ndefines the keys of the options that are affected.")

class PutWebLinksIdBodyParent(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The ID of parent item.")
    user_id: str | None = Field(None, description="The input for `user_id` is optional. Moving to non-root folder is not allowed when `user_id` is present. Parent folder id should be zero when `user_id` is provided.")

class ResourceScope(PermissiveModel):
    """A relation between a resource (file or folder) and the scopes for which the resource can be accessed."""
    scope: Literal["annotation_edit", "annotation_view_all", "annotation_view_self", "base_explorer", "base_picker", "base_preview", "base_upload", "item_delete", "item_download", "item_preview", "item_rename", "item_share", "item_upload", "item_read"] | None = Field(None, description="The scopes for the resource access.")
    object_: FolderMini | FileMini | None = Field(None, validation_alias="object", serialization_alias="object")

class FileFullExpiringEmbedLink(PermissiveModel):
    access_token: str | None = Field(None, description="The requested access token.", json_schema_extra={'format': 'token'})
    expires_in: int | None = Field(None, description="The time in seconds by which this token will expire.", json_schema_extra={'format': 'int64'})
    token_type: Literal["bearer"] | None = Field(None, description="The type of access token returned.")
    restricted_to: list[ResourceScope] | None = Field(None, description="The permissions that this access token permits,\nproviding a list of resources (files, folders, etc)\nand the scopes permitted for each of those resources.")
    url: str | None = Field(None, description="The actual expiring embed URL for this file, constructed\nfrom the file ID and access tokens specified in this object.", json_schema_extra={'format': 'url'})

class FileFullV1ExpiringEmbedLink(PermissiveModel):
    access_token: str | None = Field(None, description="The requested access token.", json_schema_extra={'format': 'token'})
    expires_in: int | None = Field(None, description="The time in seconds by which this token will expire.", json_schema_extra={'format': 'int64'})
    token_type: Literal["bearer"] | None = Field(None, description="The type of access token returned.")
    restricted_to: list[ResourceScope] | None = Field(None, description="The permissions that this access token permits,\nproviding a list of resources (files, folders, etc)\nand the scopes permitted for each of those resources.")
    url: str | None = Field(None, description="The actual expiring embed URL for this file, constructed\nfrom the file ID and access tokens specified in this object.", json_schema_extra={'format': 'url'})

class RoleVariable(PermissiveModel):
    """Determines if the
workflow outcome
affects a specific
collaborator role."""
    type_: Literal["variable"] = Field(..., validation_alias="type", serialization_alias="type", description="Role object type.")
    variable_type: Literal["collaborator_role"] = Field(..., description="The variable type used\nby the object.")
    variable_value: Literal["editor", "viewer", "previewer", "uploader", "previewer uploader", "viewer uploader", "co-owner"]

class Outcome(PermissiveModel):
    """An instance of an outcome."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="ID of a specific outcome.")
    collaborators: CollaboratorVariable | None = None
    completion_rule: CompletionRuleVariable | None = None
    file_collaborator_role: RoleVariable | None = None
    task_collaborators: CollaboratorVariable | None = None
    role: RoleVariable | None = None

class SignRequestCreateSigner(PermissiveModel):
    """The schema for a Signer object used in
for creating a Box Sign request object."""
    email: str | None = Field(None, description="Email address of the signer.\nThe email address of the signer is required when making signature requests, except when using templates that are configured to include emails.")
    role: Literal["signer", "approver", "final_copy_reader"] | None = Field('signer', description="Defines the role of the signer in the signature request. A `signer`\nmust sign the document and an `approver` must approve the document. A\n`final_copy_reader` only receives the final signed document and signing\nlog.")
    is_in_person: bool | None = Field(None, description="Used in combination with an embed URL for a sender. After the\nsender signs, they are redirected to the next `in_person` signer.")
    order: int | None = Field(None, description="Order of the signer.", ge=0)
    embed_url_external_user_id: str | None = Field(None, description="User ID for the signer in an external application responsible\nfor authentication when accessing the embed URL.")
    redirect_url: str | None = Field(None, description="The URL that a signer will be redirected\nto after signing a document. Defining this URL\noverrides default or global redirect URL\nsettings for a specific signer.\nIf no declined redirect URL is specified,\nthis URL will be used for decline actions as well.")
    declined_redirect_url: str | None = Field(None, description="The URL that a signer will be redirect\nto after declining to sign a document.\nDefining this URL overrides default or global\ndeclined redirect URL settings for a specific signer.")
    login_required: bool | None = Field(None, description="If set to true, the signer will need to log in to a Box account\nbefore signing the request. If the signer does not have\nan existing account, they will have the option to create\na free Box account.")
    verification_phone_number: str | None = Field(None, description="If set, this phone number will be used to verify the signer\nvia two-factor authentication before they are able to sign the document.\nCannot be selected in combination with `login_required`.")
    password: str | None = Field(None, description="If set, the signer is required to enter the password before they are able\nto sign a document. This field is write only.")
    signer_group_id: str | None = Field(None, description="If set, signers who have the same value will be assigned to the same input and to the same signer group.\nA signer group is not a Box Group. It is an entity that belongs to a Sign Request and can only be\nused/accessed within this Sign Request. A signer group is expected to have more than one signer.\nIf the provided value is only used for one signer, this value will be ignored and request will be handled\nas it was intended for an individual signer. The value provided can be any string and only used to\ndetermine which signers belongs to same group. A successful response will provide a generated UUID value\ninstead for signers in the same signer group.")
    suppress_notifications: bool | None = Field(None, description="If true, no emails about the sign request will be sent.")
    language: str | None = Field(None, description="The language of the user, formatted in modified version of the\n[ISO 639-1](https://developer.box.com/guides/api-calls/language-codes) format.")

class SignRequestPrefillTag(PermissiveModel):
    """Prefill tags are used to prefill placeholders with signer input data. Only
one value field can be included."""
    document_tag_id: str | None = Field(None, description="This references the ID of a specific tag contained in a file of the signature request.")
    text_value: str | None = Field(None, description="Text prefill value.")
    checkbox_value: bool | None = Field(None, description="Checkbox prefill value.")
    date_value: str | None = Field(None, description="Date prefill value.", json_schema_extra={'format': 'date'})

class SignRequestBase(PermissiveModel):
    """A standard representation of a signature request object."""
    is_document_preparation_needed: bool | None = Field(None, description="Indicates if the sender should receive a `prepare_url` in the response to complete document preparation using the UI.")
    redirect_url: str | None = Field(None, description="When specified, the signature request will be redirected to this url when a document is signed.")
    declined_redirect_url: str | None = Field(None, description="The uri that a signer will be redirected to after declining to sign a document.")
    are_text_signatures_enabled: bool | None = Field(True, description="Disables the usage of signatures generated by typing (text).")
    email_subject: str | None = Field(None, description="Subject of sign request email. This is cleaned by sign request. If this field is not passed, a default subject will be used.")
    email_message: str | None = Field(None, description="Message to include in sign request email. The field is cleaned through sanitization of specific characters. However, some html tags are allowed. Links included in the message are also converted to hyperlinks in the email. The message may contain the following html tags including `a`, `abbr`, `acronym`, `b`, `blockquote`, `code`, `em`, `i`, `ul`, `li`, `ol`, and `strong`. Be aware that when the text to html ratio is too high, the email may end up in spam filters. Custom styles on these tags are not allowed. If this field is not passed, a default message will be used.")
    are_reminders_enabled: bool | None = Field(None, description="Reminds signers to sign a document on day 3, 8, 13 and 18. Reminders are only sent to outstanding signers.")
    name: str | None = Field(None, description="Name of the signature request.")
    prefill_tags: list[SignRequestPrefillTag] | None = Field(None, description="When a document contains sign-related tags in the content, you can prefill them using this `prefill_tags` by referencing the 'id' of the tag as the `external_id` field of the prefill tag.")
    days_valid: int | None = Field(None, description="Set the number of days after which the created signature request will automatically expire if not completed. By default, we do not apply any expiration date on signature requests, and the signature request does not expire.", ge=0, le=730)
    external_id: str | None = Field(None, description="This can be used to reference an ID in an external system that the sign request is related to.")
    template_id: str | None = Field(None, description="When a signature request is created from a template this field will indicate the id of that template.")
    external_system_name: str | None = Field(None, description="Used as an optional system name to appear in the signature log next to the signers who have been assigned the `embed_url_external_id`.")

class SignRequestCreateRequest(PermissiveModel):
    """Creates a Box Sign request object."""
    is_document_preparation_needed: bool | None = Field(None, description="Indicates if the sender should receive a `prepare_url` in the response to complete document preparation using the UI.")
    redirect_url: str | None = Field(None, description="When specified, the signature request will be redirected to this url when a document is signed.")
    declined_redirect_url: str | None = Field(None, description="The uri that a signer will be redirected to after declining to sign a document.")
    are_text_signatures_enabled: bool | None = Field(True, description="Disables the usage of signatures generated by typing (text).")
    email_subject: str | None = Field(None, description="Subject of sign request email. This is cleaned by sign request. If this field is not passed, a default subject will be used.")
    email_message: str | None = Field(None, description="Message to include in sign request email. The field is cleaned through sanitization of specific characters. However, some html tags are allowed. Links included in the message are also converted to hyperlinks in the email. The message may contain the following html tags including `a`, `abbr`, `acronym`, `b`, `blockquote`, `code`, `em`, `i`, `ul`, `li`, `ol`, and `strong`. Be aware that when the text to html ratio is too high, the email may end up in spam filters. Custom styles on these tags are not allowed. If this field is not passed, a default message will be used.")
    are_reminders_enabled: bool | None = Field(None, description="Reminds signers to sign a document on day 3, 8, 13 and 18. Reminders are only sent to outstanding signers.")
    name: str | None = Field(None, description="Name of the signature request.")
    prefill_tags: list[SignRequestPrefillTag] | None = Field(None, description="When a document contains sign-related tags in the content, you can prefill them using this `prefill_tags` by referencing the 'id' of the tag as the `external_id` field of the prefill tag.")
    days_valid: int | None = Field(None, description="Set the number of days after which the created signature request will automatically expire if not completed. By default, we do not apply any expiration date on signature requests, and the signature request does not expire.", ge=0, le=730)
    external_id: str | None = Field(None, description="This can be used to reference an ID in an external system that the sign request is related to.")
    template_id: str | None = Field(None, description="When a signature request is created from a template this field will indicate the id of that template.")
    external_system_name: str | None = Field(None, description="Used as an optional system name to appear in the signature log next to the signers who have been assigned the `embed_url_external_id`.")
    source_files: list[FileBase] | None = Field(None, description="List of files to create a signing document from. This is currently limited to ten files. Only the ID and type fields are required for each file.", max_length=10)
    signature_color: Literal["blue", "black", "red"] | None = Field(None, description="Force a specific color for the signature (blue, black, or red).")
    signers: list[SignRequestCreateSigner] = Field(..., description="Array of signers for the signature request. 35 is the\nmax number of signers permitted.\n\n**Note**: It may happen that some signers belong to conflicting [segments](https://developer.box.com/reference/resources/shield-information-barrier-segment-member) (user groups).\nThis means that due to the security policies, users are assigned to segments to prevent exchanges or communication that could lead to ethical conflicts.\nIn such a case, an attempt to send the sign request will result in an error.\n\nRead more about [segments and ethical walls](https://support.box.com/hc/en-us/articles/9920431507603-Understanding-Information-Barriers#h_01GFVJEHQA06N7XEZ4GCZ9GFAQ).")
    parent_folder: FolderMini | None = None

class StatusSkillCardInvocation(PermissiveModel):
    """The invocation of this service, used to track
which instance of a service applied the metadata."""
    type_: Literal["skill_invocation"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `skill_invocation`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A custom identifier that represent the instance of\nthe service that applied this metadata. For example,\nif your `image-recognition-service` runs on multiple\nnodes, this field can be used to identify the ID of\nthe node that was used to apply the metadata.")

class StatusSkillCardSkill(PermissiveModel):
    """The service that applied this metadata."""
    type_: Literal["service"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `service`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A custom identifier that represent the service that\napplied this metadata.")

class StatusSkillCardSkillCardTitle(PermissiveModel):
    """The title of the card."""
    code: str | None = Field(None, description="An optional identifier for the title.")
    message: str = Field(..., description="The actual title to show in the UI.")

class StatusSkillCardStatus(PermissiveModel):
    """Sets the status of the skill. This can be used to show a message to the user while the Skill is processing the data, or if it was not able to process the file."""
    code: Literal["invoked", "processing", "success", "transient_failure", "permanent_failure"] = Field(..., description="A code for the status of this Skill invocation. By\ndefault each of these will have their own accompanied\nmessages. These can be adjusted by setting the `message`\nvalue on this object.")
    message: str | None = Field(None, description="A custom message that can be provided with this status.\nThis will be shown in the web app to the end user.")

class StatusSkillCard(PermissiveModel):
    """A Box Skill metadata card that puts a status message in the metadata sidebar."""
    created_at: str | None = Field(None, description="The optional date and time this card was created at.", json_schema_extra={'format': 'date-time'})
    type_: Literal["skill_card"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `skill_card`.")
    skill_card_type: Literal["status"] = Field(..., description="The value will always be `status`.")
    skill_card_title: StatusSkillCardSkillCardTitle | None = Field(None, description="The title of the card.")
    status: StatusSkillCardStatus = Field(..., description="Sets the status of the skill. This can be used to show a message to the user while the Skill is processing the data, or if it was not able to process the file.")
    skill: StatusSkillCardSkill = Field(..., description="The service that applied this metadata.")
    invocation: StatusSkillCardInvocation = Field(..., description="The invocation of this service, used to track\nwhich instance of a service applied the metadata.")

class TimelineSkillCardEntriesItemAppearsItem(PermissiveModel):
    """The timestamp for an entry."""
    start: int | None = Field(None, description="The time in seconds when an\nentry should start appearing on a timeline.")
    end: int | None = Field(None, description="The time in seconds when an\nentry should stop appearing on a timeline.")

class TimelineSkillCardEntriesItem(PermissiveModel):
    """An single item that's placed on multiple items on the timeline."""
    text: str | None = Field(None, description="The text of the entry. This would be the display\nname for an item being placed on the timeline, for example the name\nof the person who was detected in a video.")
    appears: list[TimelineSkillCardEntriesItemAppearsItem] | None = Field(None, description="Defines a list of timestamps for when this item should appear on the\ntimeline.")
    image_url: str | None = Field(None, description="The image to show on a for an entry that appears\non a timeline. This image URL is required for every entry.\n\nThe image will be shown in a\nlist of items (for example faces), and clicking\nthe image will show the user where that entry\nappears during the duration of this entry.")

class TimelineSkillCardInvocation(PermissiveModel):
    """The invocation of this service, used to track
which instance of a service applied the metadata."""
    type_: Literal["skill_invocation"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `skill_invocation`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A custom identifier that represent the instance of\nthe service that applied this metadata. For example,\nif your `image-recognition-service` runs on multiple\nnodes, this field can be used to identify the ID of\nthe node that was used to apply the metadata.")

class TimelineSkillCardSkill(PermissiveModel):
    """The service that applied this metadata."""
    type_: Literal["service"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `service`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A custom identifier that represent the service that\napplied this metadata.")

class TimelineSkillCardSkillCardTitle(PermissiveModel):
    """The title of the card."""
    code: str | None = Field(None, description="An optional identifier for the title.")
    message: str = Field(..., description="The actual title to show in the UI.")

class TimelineSkillCard(PermissiveModel):
    """A Box Skill metadata card that places a list of images on a
timeline."""
    created_at: str | None = Field(None, description="The optional date and time this card was created at.", json_schema_extra={'format': 'date-time'})
    type_: Literal["skill_card"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `skill_card`.")
    skill_card_type: Literal["timeline"] = Field(..., description="The value will always be `timeline`.")
    skill_card_title: TimelineSkillCardSkillCardTitle | None = Field(None, description="The title of the card.")
    skill: TimelineSkillCardSkill = Field(..., description="The service that applied this metadata.")
    invocation: TimelineSkillCardInvocation = Field(..., description="The invocation of this service, used to track\nwhich instance of a service applied the metadata.")
    duration: int | None = Field(None, description="An total duration in seconds of the timeline.")
    entries: list[TimelineSkillCardEntriesItem] = Field(..., description="A list of entries on the timeline.")

class TrackingCode(PermissiveModel):
    """Tracking codes allow an admin to generate reports from the admin console
and assign an attribute to a specific group of users.
This setting must be enabled for an enterprise before it can be used."""
    type_: Literal["tracking_code"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The value will always be `tracking_code`.")
    name: str | None = Field(None, description="The name of the tracking code, which must be preconfigured in\nthe Admin Console.")
    value: str | None = Field(None, description="The value of the tracking code.")

class TranscriptSkillCardEntriesItemAppearsItem(PermissiveModel):
    """The timestamp for an entry."""
    start: int | None = Field(None, description="The time in seconds when an\nentry should start appearing on a timeline.")

class TranscriptSkillCardEntriesItem(PermissiveModel):
    """An entry in the `entries` attribute of a metadata card."""
    text: str | None = Field(None, description="The text of the entry. This would be the transcribed text assigned\nto the entry on the timeline.")
    appears: list[TranscriptSkillCardEntriesItemAppearsItem] | None = Field(None, description="Defines when a transcribed bit of text appears. This only includes a\nstart time and no end time.")

class TranscriptSkillCardInvocation(PermissiveModel):
    """The invocation of this service, used to track
which instance of a service applied the metadata."""
    type_: Literal["skill_invocation"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `skill_invocation`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A custom identifier that represent the instance of\nthe service that applied this metadata. For example,\nif your `image-recognition-service` runs on multiple\nnodes, this field can be used to identify the ID of\nthe node that was used to apply the metadata.")

class TranscriptSkillCardSkill(PermissiveModel):
    """The service that applied this metadata."""
    type_: Literal["service"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `service`.")
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="A custom identifier that represent the service that\napplied this metadata.")

class TranscriptSkillCardSkillCardTitle(PermissiveModel):
    """The title of the card."""
    code: str | None = Field(None, description="An optional identifier for the title.")
    message: str = Field(..., description="The actual title to show in the UI.")

class TranscriptSkillCard(PermissiveModel):
    """A Box Skill metadata card that adds a transcript to a file."""
    created_at: str | None = Field(None, description="The optional date and time this card was created at.", json_schema_extra={'format': 'date-time'})
    type_: Literal["skill_card"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `skill_card`.")
    skill_card_type: Literal["transcript"] = Field(..., description="The value will always be `transcript`.")
    skill_card_title: TranscriptSkillCardSkillCardTitle | None = Field(None, description="The title of the card.")
    skill: TranscriptSkillCardSkill = Field(..., description="The service that applied this metadata.")
    invocation: TranscriptSkillCardInvocation = Field(..., description="The invocation of this service, used to track\nwhich instance of a service applied the metadata.")
    duration: int | None = Field(None, description="An optional total duration in seconds.\n\nUsed with a `skill_card_type` of `transcript` or\n`timeline`.")
    entries: list[TranscriptSkillCardEntriesItem] = Field(..., description="An list of entries for the card. This represents the individual entries of\nthe transcription.")

class SkillCard(PermissiveModel):
    """Box Skill card."""
    skill_card: KeywordSkillCard | TimelineSkillCard | TranscriptSkillCard | StatusSkillCard

class PutFilesIdMetadataGlobalBoxSkillsCardsBodyItem(PermissiveModel):
    """An operation that replaces an existing card."""
    op: Literal["replace"] | None = Field(None, description="The value will always be `replace`.")
    path: str | None = Field(None, description="The JSON Path that represents the card to replace. In most cases\nthis will be in the format `/cards/{index}` where `index` is the\nzero-indexed position of the card in the list of cards.")
    value: SkillCard | None = None

class UploadPartMini(PermissiveModel):
    """The basic representation of an upload
session chunk."""
    part_id: str | None = Field(None, description="The unique ID of the chunk.")
    offset: int | None = Field(None, description="The offset of the chunk within the file\nin bytes. The lower bound of the position\nof the chunk within the file.", json_schema_extra={'format': 'int64'})
    size: int | None = Field(None, description="The size of the chunk in bytes.", json_schema_extra={'format': 'int64'})

class UploadPart(PermissiveModel):
    """The representation of an upload
session chunk."""
    part_id: str | None = Field(None, description="The unique ID of the chunk.")
    offset: int | None = Field(None, description="The offset of the chunk within the file\nin bytes. The lower bound of the position\nof the chunk within the file.", json_schema_extra={'format': 'int64'})
    size: int | None = Field(None, description="The size of the chunk in bytes.", json_schema_extra={'format': 'int64'})
    sha1: str | None = Field(None, description="The SHA1 hash of the chunk.")

class UserBase(PermissiveModel):
    """A mini representation of a user, used when
nested within another resource."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier for this user.")
    type_: Literal["user"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `user`.")

class UserMini(PermissiveModel):
    """A mini representation of a user, as can be returned when nested within other
resources."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier for this user.")
    type_: Literal["user"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `user`.")
    name: str | None = Field(None, description="The display name of this user.", max_length=50)
    login: str | None = Field(None, description="The primary email address of this user.", json_schema_extra={'format': 'email'})

class FileFullLock(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The unique identifier for this lock.")
    type_: Literal["lock"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The value will always be `lock`.")
    created_by: UserMini | None = None
    created_at: str | None = Field(None, description="The time this lock was created at.", json_schema_extra={'format': 'date-time'})
    expired_at: str | None = Field(None, description="The time this lock is to expire at, which might be in the past.", json_schema_extra={'format': 'date-time'})
    is_download_prevented: bool | None = Field(None, description="Whether or not the file can be downloaded while locked.")
    app_type: Literal["gsuite", "office_wopi", "office_wopiplus", "other"] | None = Field(None, description="If the lock is managed by an application rather than a user, this\nfield identifies the type of the application that holds the lock.\nThis is an open enum and may be extended with additional values in\nthe future.")

class FileFullV1Lock(PermissiveModel):
    id_: str | None = Field(None, validation_alias="id", serialization_alias="id", description="The unique identifier for this lock.")
    type_: Literal["lock"] | None = Field(None, validation_alias="type", serialization_alias="type", description="The value will always be `lock`.")
    created_by: UserMini | None = None
    created_at: str | None = Field(None, description="The time this lock was created at.", json_schema_extra={'format': 'date-time'})
    expired_at: str | None = Field(None, description="The time this lock is to expire at, which might be in the past.", json_schema_extra={'format': 'date-time'})
    is_download_prevented: bool | None = Field(None, description="Whether or not the file can be downloaded while locked.")
    app_type: Literal["gsuite", "office_wopi", "office_wopiplus", "other"] | None = Field(None, description="If the lock is managed by an application rather than a user, this\nfield identifies the type of the application that holds the lock.\nThis is an open enum and may be extended with additional values in\nthe future.")

class FileModel(PermissiveModel):
    """A standard representation of a file, as returned from any
file API endpoints by default."""
    description: str | None = Field(None, description="The optional description of this file.\nIf the description exceeds 255 characters, the first 255 characters\nare set as a file description and the rest of it is ignored.", max_length=255)
    size: int | None = Field(None, description="The file size in bytes. Be careful parsing this integer as it can\nget very large and cause an integer overflow.")
    path_collection: FileModelPathCollection | None = None
    created_at: str | None = Field(None, description="The date and time when the file was created on Box.", json_schema_extra={'format': 'date-time'})
    modified_at: str | None = Field(None, description="The date and time when the file was last updated on Box.", json_schema_extra={'format': 'date-time'})
    trashed_at: str | None = Field(None, description="The time at which this file was put in the trash.", json_schema_extra={'format': 'date-time'})
    purged_at: str | None = Field(None, description="The time at which this file is expected to be purged\nfrom the trash.", json_schema_extra={'format': 'date-time'})
    content_created_at: str | None = Field(None, description="The date and time at which this file was originally\ncreated, which might be before it was uploaded to Box.", json_schema_extra={'format': 'date-time'})
    content_modified_at: str | None = Field(None, description="The date and time at which this file was last updated,\nwhich might be before it was uploaded to Box.", json_schema_extra={'format': 'date-time'})
    created_by: UserMini | None = None
    modified_by: UserMini | Any | None = None
    owned_by: UserMini | Any | None = None
    shared_link: FileModelSharedLink | None = None
    parent: FolderMini | None = None
    item_status: Literal["active", "trashed", "deleted"] | None = Field(None, description="Defines if this item has been deleted or not.\n\n* `active` when the item has is not in the trash\n* `trashed` when the item has been moved to the trash but not deleted\n* `deleted` when the item has been permanently deleted.")

class FileFull(PermissiveModel):
    """A full representation of a file, as can be returned from any
file API endpoints by default."""
    version_number: str | None = Field(None, description="The version number of this file.")
    comment_count: int | None = Field(None, description="The number of comments on this file.")
    permissions: FileFullPermissions | None = None
    tags: list[str] | Any | None = None
    lock: FileFullLock | None = None
    extension: str | None = Field(None, description="Indicates the (optional) file extension for this file. By default,\nthis is set to an empty string.")
    is_package: bool | None = Field(None, description="Indicates if the file is a package. Packages are commonly used\nby Mac Applications and can include iWork files.")
    expiring_embed_link: FileFullExpiringEmbedLink | None = None
    watermark_info: FileFullWatermarkInfo | None = None
    is_accessible_via_shared_link: bool | None = Field(None, description="Specifies if the file can be accessed\nvia the direct shared link or a shared link\nto a parent folder.")
    allowed_invitee_roles: list[Literal["editor", "viewer", "previewer", "uploader", "previewer uploader", "viewer uploader", "co-owner"]] | None = Field(None, description="A list of the types of roles that user can be invited at\nwhen sharing this file.")
    is_externally_owned: bool | None = Field(None, description="Specifies if this file is owned by a user outside of the\nauthenticated enterprise.")
    has_collaborations: bool | None = Field(None, description="Specifies if this file has any other collaborators.")
    metadata: dict[str, dict[str, MetadataFull]] | None = None
    expires_at: str | None = Field(None, description="When the file will automatically be deleted.", json_schema_extra={'format': 'date-time'})
    representations: FileFullRepresentations | None = None
    classification: FileFullClassification | None = None
    uploader_display_name: str | None = None
    disposition_at: str | None = Field(None, description="The retention expiration timestamp for the given file.", json_schema_extra={'format': 'date-time'})
    shared_link_permission_options: list[Literal["can_preview", "can_download", "can_edit"]] | None = Field(None, description="A list of the types of roles that user can be invited at\nwhen sharing this file.")
    is_associated_with_app_item: bool | None = Field(None, description="This field will return true if the file or any ancestor of the file\nis associated with at least one app item. Note that this will return\ntrue even if the context user does not have access to the app item(s)\nassociated with the file.")

class Files(PermissiveModel):
    """A list of files."""
    total_count: int | None = Field(None, description="The number of files.", json_schema_extra={'format': 'int64'})
    entries: list[FileFull] | None = Field(None, description="A list of files.")

class UserNotificationEmail(PermissiveModel):
    """An alternate notification email address to which email
notifications are sent. When it's confirmed, this will be
the email address to which notifications are sent instead of
to the primary email address."""
    email: str | None = Field(None, description="The email address to send the notifications to.")
    is_confirmed: bool | None = Field(None, description="Specifies if this email address has been confirmed.")

class User(PermissiveModel):
    """A standard representation of a user, as returned from any
user API endpoints by default."""
    created_at: str | None = Field(None, description="When the user object was created.", json_schema_extra={'format': 'date-time'})
    modified_at: str | None = Field(None, description="When the user object was last modified.", json_schema_extra={'format': 'date-time'})
    language: str | None = Field(None, description="The language of the user, formatted in modified version of the\n[ISO 639-1](https://developer.box.com/guides/api-calls/language-codes) format.")
    timezone_: str | None = Field(None, validation_alias="timezone", serialization_alias="timezone", description="The user's timezone.", json_schema_extra={'format': 'timezone'})
    space_amount: int | None = Field(None, description="The user’s total available space amount in bytes.", json_schema_extra={'format': 'int64'})
    space_used: int | None = Field(None, description="The amount of space in use by the user.", json_schema_extra={'format': 'int64'})
    max_upload_size: int | None = Field(None, description="The maximum individual file size in bytes the user can have.", json_schema_extra={'format': 'int64'})
    status: Literal["active", "inactive", "cannot_delete_edit", "cannot_delete_edit_upload"] | None = Field(None, description="The user's account status.")
    job_title: str | None = Field(None, description="The user’s job title.", max_length=100)
    phone: str | None = Field(None, description="The user’s phone number.", max_length=100)
    address: str | None = Field(None, description="The user’s address.", max_length=255)
    avatar_url: str | None = Field(None, description="URL of the user’s avatar image.")
    notification_email: UserNotificationEmail | None = Field(None, description="An alternate notification email address to which email\nnotifications are sent. When it's confirmed, this will be\nthe email address to which notifications are sent instead of\nto the primary email address.")

class UserV1NotificationEmail(PermissiveModel):
    """An alternate notification email address to which email
notifications are sent. When it's confirmed, this will be
the email address to which notifications are sent instead of
to the primary email address."""
    email: str | None = Field(None, description="The email address to send the notifications to.")
    is_confirmed: bool | None = Field(None, description="Specifies if this email address has been confirmed.")

class WebLinkBase(PermissiveModel):
    """Web links are objects that point to URLs. These objects
are also known as bookmarks within the Box web application.

Web link objects are treated similarly to file objects,
they will also support most actions that apply to regular files."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier for this web link.")
    type_: Literal["web_link"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `web_link`.")
    etag: str | None = Field(None, description="The entity tag of this web link. Used with `If-Match`\nheaders.")

class WebLinkMini(PermissiveModel):
    """Web links are objects that point to URLs. These objects
are also known as bookmarks within the Box web application.

Web link objects are treated similarly to file objects,
they will also support most actions that apply to regular files."""
    id_: str = Field(..., validation_alias="id", serialization_alias="id", description="The unique identifier for this web link.")
    type_: Literal["web_link"] = Field(..., validation_alias="type", serialization_alias="type", description="The value will always be `web_link`.")
    etag: str | None = Field(None, description="The entity tag of this web link. Used with `If-Match`\nheaders.")
    url: str | None = Field(None, description="The URL this web link points to.")
    sequence_id: str | None | Any | None = None
    name: str | None = Field(None, description="The name of the web link.")

class WebLinkPathCollection(PermissiveModel):
    total_count: int = Field(..., description="The number of folders in this list.", json_schema_extra={'format': 'int64'})
    entries: list[FolderMini] = Field(..., description="The parent folders for this item.")

class WebLinkSharedLinkPermissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")

class WebLinkSharedLink(PermissiveModel):
    url: str = Field(..., description="The URL that can be used to access the item on Box.\n\nThis URL will display the item in Box's preview UI where the file\ncan be downloaded if allowed.\n\nThis URL will continue to work even when a custom `vanity_url`\nhas been set for this shared link.", json_schema_extra={'format': 'url'})
    download_url: str | None = Field(None, description="A URL that can be used to download the file. This URL can be used in\na browser to download the file. This URL includes the file\nextension so that the file will be saved with the right file type.\n\nThis property will be `null` for folders.", json_schema_extra={'format': 'url'})
    vanity_url: str | None = Field(None, description="The \"Custom URL\" that can also be used to preview the item on Box.  Custom\nURLs can only be created or modified in the Box Web application.", json_schema_extra={'format': 'url'})
    vanity_name: str | None = Field(None, description="The custom name of a shared link, as used in the `vanity_url` field.")
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The access level for this shared link.\n\n* `open` - provides access to this item to anyone with this link\n* `company` - only provides access to this item to people the same company\n* `collaborators` - only provides access to this item to people who are\n   collaborators on this item\n\nIf this field is omitted when creating the shared link, the access level\nwill be set to the default access level specified by the enterprise admin.")
    effective_access: Literal["open", "company", "collaborators"] = Field(..., description="The effective access level for the shared link. This can be a more\nrestrictive access level than the value in the `access` field when the\nenterprise settings restrict the allowed access levels.")
    effective_permission: Literal["can_edit", "can_download", "can_preview", "no_access"] = Field(..., description="The effective permissions for this shared link.\nThese result in the more restrictive combination of\nthe share link permissions and the item permissions set\nby the administrator, the owner, and any ancestor item\nsuch as a folder.")
    unshared_at: str | None = Field(None, description="The date and time when this link will be unshared. This field can only be\nset by users with paid accounts.", json_schema_extra={'format': 'date-time'})
    is_password_enabled: bool = Field(..., description="Defines if the shared link requires a password to access the item.")
    permissions: WebLinkSharedLinkPermissions | None = Field(None, description="Defines if this link allows a user to preview, edit, and download an item.\nThese permissions refer to the shared link only and\ndo not supersede permissions applied to the item itself.")
    download_count: int = Field(..., description="The number of times this item has been downloaded.")
    preview_count: int = Field(..., description="The number of times this item has been previewed.")

class WebLink(PermissiveModel):
    """Web links are objects that point to URLs. These objects
are also known as bookmarks within the Box web application.

Web link objects are treated similarly to file objects,
they will also support most actions that apply to regular files."""
    parent: FolderMini | None = None
    description: str | None = Field(None, description="The description accompanying the web link. This is\nvisible within the Box web application.")
    path_collection: WebLinkPathCollection | None = None
    created_at: str | None = Field(None, description="When this file was created on Box’s servers.", json_schema_extra={'format': 'date-time'})
    modified_at: str | None = Field(None, description="When this file was last updated on the Box\nservers.", json_schema_extra={'format': 'date-time'})
    trashed_at: str | None = Field(None, description="When this file was moved to the trash.", json_schema_extra={'format': 'date-time'})
    purged_at: str | None = Field(None, description="When this file will be permanently deleted.", json_schema_extra={'format': 'date-time'})
    created_by: UserMini | None = None
    modified_by: UserMini | None = None
    owned_by: UserMini | None = None
    shared_link: WebLinkSharedLink | None = None
    item_status: Literal["active", "trashed", "deleted"] | None = Field(None, description="Whether this item is deleted or not. Values include `active`,\n`trashed` if the file has been moved to the trash, and `deleted` if\nthe file has been permanently deleted.")

class Items(PermissiveModel):
    """A list of files, folders, and web links in
their mini representation."""
    limit: int | None = Field(None, description="The limit that was used for these entries. This will be the same as the\n`limit` query parameter unless that value exceeded the maximum value\nallowed. The maximum value varies by API.", json_schema_extra={'format': 'int64'})
    next_marker: str | None = Field(None, description="The marker for the start of the next page of results.")
    prev_marker: str | None = Field(None, description="The marker for the start of the previous page of results.")
    total_count: int | None = Field(None, description="One greater than the offset of the last entry in the entire collection.\nThe total number of entries in the collection may be less than\n`total_count`.\n\nThis field is only returned for calls that use offset-based pagination.\nFor marker-based paginated APIs, this field will be omitted.", json_schema_extra={'format': 'int64'})
    offset: int | None = Field(None, description="The 0-based offset of the first entry in this set. This will be the same\nas the `offset` query parameter.\n\nThis field is only returned for calls that use offset-based pagination.\nFor marker-based paginated APIs, this field will be omitted.", json_schema_extra={'format': 'int64'})
    order: list[ItemsOrderItem] | None = Field(None, description="The order by which items are returned.\n\nThis field is only returned for calls that use offset-based pagination.\nFor marker-based paginated APIs, this field will be omitted.")
    entries: list[FileFull | FolderMini | WebLink] | None = Field(None, description="The items in this collection.")

class Folder(PermissiveModel):
    """A standard representation of a folder, as returned from any
folder API endpoints by default."""
    created_at: str | None = Field(None, description="The date and time when the folder was created. This value may\nbe `null` for some folders such as the root folder or the trash\nfolder.", json_schema_extra={'format': 'date-time'})
    modified_at: str | None = Field(None, description="The date and time when the folder was last updated. This value may\nbe `null` for some folders such as the root folder or the trash\nfolder.", json_schema_extra={'format': 'date-time'})
    description: str | Any | None = None
    size: int | None = Field(None, description="The folder size in bytes.\n\nBe careful parsing this integer as its\nvalue can get very large.", json_schema_extra={'format': 'int64'})
    path_collection: FolderPathCollection | None = None
    created_by: UserMini | Any | None = None
    modified_by: UserMini | Any | None = None
    trashed_at: str | None = Field(None, description="The time at which this folder was put in the trash.", json_schema_extra={'format': 'date-time'})
    purged_at: str | None = Field(None, description="The time at which this folder is expected to be purged\nfrom the trash.", json_schema_extra={'format': 'date-time'})
    content_created_at: str | None = Field(None, description="The date and time at which this folder was originally\ncreated.", json_schema_extra={'format': 'date-time'})
    content_modified_at: str | None = Field(None, description="The date and time at which this folder was last updated.", json_schema_extra={'format': 'date-time'})
    owned_by: UserMini | Any | None = None
    shared_link: FolderSharedLink | None = None
    folder_upload_email: FolderFolderUploadEmail | None = Field(None, description="The `folder_upload_email` parameter is not `null` if one of the following options is **true**:\n\n  * The **Allow uploads to this folder via email** and the **Only allow email uploads from collaborators in this folder** are [enabled for a folder in the Admin Console](https://support.box.com/hc/en-us/articles/360043697534-Upload-to-Box-Through-Email), and the user has at least **Upload** permissions granted.\n\n  * The **Allow uploads to this folder via email** setting is enabled for a folder in the Admin Console, and the **Only allow email uploads from collaborators in this folder** setting is deactivated (unchecked).\n\nIf the conditions are not met, the parameter will have the following value: `folder_upload_email: null`.")
    parent: FolderMini | None = None
    item_status: Literal["active", "trashed", "deleted"] | None = Field(None, description="Defines if this item has been deleted or not.\n\n* `active` when the item has is not in the trash\n* `trashed` when the item has been moved to the trash but not deleted\n* `deleted` when the item has been permanently deleted.")
    item_collection: Items | Any | None = None

class WebLinkSharedLinkV0Permissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")

class WebLinkV1PathCollection(PermissiveModel):
    total_count: int = Field(..., description="The number of folders in this list.", json_schema_extra={'format': 'int64'})
    entries: list[FolderMini] = Field(..., description="The parent folders for this item.")

class WebLinkV1SharedLinkPermissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")

class WebLinkV1SharedLink(PermissiveModel):
    url: str = Field(..., description="The URL that can be used to access the item on Box.\n\nThis URL will display the item in Box's preview UI where the file\ncan be downloaded if allowed.\n\nThis URL will continue to work even when a custom `vanity_url`\nhas been set for this shared link.", json_schema_extra={'format': 'url'})
    download_url: str | None = Field(None, description="A URL that can be used to download the file. This URL can be used in\na browser to download the file. This URL includes the file\nextension so that the file will be saved with the right file type.\n\nThis property will be `null` for folders.", json_schema_extra={'format': 'url'})
    vanity_url: str | None = Field(None, description="The \"Custom URL\" that can also be used to preview the item on Box.  Custom\nURLs can only be created or modified in the Box Web application.", json_schema_extra={'format': 'url'})
    vanity_name: str | None = Field(None, description="The custom name of a shared link, as used in the `vanity_url` field.")
    access: Literal["open", "company", "collaborators"] | None = Field(None, description="The access level for this shared link.\n\n* `open` - provides access to this item to anyone with this link\n* `company` - only provides access to this item to people the same company\n* `collaborators` - only provides access to this item to people who are\n   collaborators on this item\n\nIf this field is omitted when creating the shared link, the access level\nwill be set to the default access level specified by the enterprise admin.")
    effective_access: Literal["open", "company", "collaborators"] = Field(..., description="The effective access level for the shared link. This can be a more\nrestrictive access level than the value in the `access` field when the\nenterprise settings restrict the allowed access levels.")
    effective_permission: Literal["can_edit", "can_download", "can_preview", "no_access"] = Field(..., description="The effective permissions for this shared link.\nThese result in the more restrictive combination of\nthe share link permissions and the item permissions set\nby the administrator, the owner, and any ancestor item\nsuch as a folder.")
    unshared_at: str | None = Field(None, description="The date and time when this link will be unshared. This field can only be\nset by users with paid accounts.", json_schema_extra={'format': 'date-time'})
    is_password_enabled: bool = Field(..., description="Defines if the shared link requires a password to access the item.")
    permissions: WebLinkV1SharedLinkPermissions | None = Field(None, description="Defines if this link allows a user to preview, edit, and download an item.\nThese permissions refer to the shared link only and\ndo not supersede permissions applied to the item itself.")
    download_count: int = Field(..., description="The number of times this item has been downloaded.")
    preview_count: int = Field(..., description="The number of times this item has been previewed.")

class WebLinkV1SharedLinkV0Permissions(PermissiveModel):
    """Defines if this link allows a user to preview, edit, and download an item.
These permissions refer to the shared link only and
do not supersede permissions applied to the item itself."""
    can_download: bool = Field(..., description="Defines if the shared link allows for the item to be downloaded. For\nshared links on folders, this also applies to any items in the folder.\n\nThis value can be set to `true` when the effective access level is\nset to `open` or `company`, not `collaborators`.")
    can_preview: bool = Field(..., description="Defines if the shared link allows for the item to be previewed.\n\nThis value is always `true`. For shared links on folders this also\napplies to any items in the folder.")
    can_edit: bool = Field(..., description="Defines if the shared link allows for the item to be edited.\n\nThis value can only be `true` if `can_download` is also `true` and if\nthe item has a type of `file`.")


# Rebuild models to resolve forward references (required for circular refs)
AiAgentBasicTextTool.model_rebuild()
AiAgentBasicTextToolBase.model_rebuild()
AiAgentExtract.model_rebuild()
AiAgentExtractStructured.model_rebuild()
AiAgentLongTextTool.model_rebuild()
AiAgentLongTextToolEmbeddings.model_rebuild()
AiAgentLongTextToolEmbeddingsStrategy.model_rebuild()
AiAgentLongTextToolV1Embeddings.model_rebuild()
AiAgentLongTextToolV1EmbeddingsStrategy.model_rebuild()
AiAgentReference.model_rebuild()
AiItemBase.model_rebuild()
AiLlmEndpointParams.model_rebuild()
AiLlmEndpointParamsAws.model_rebuild()
AiLlmEndpointParamsGoogle.model_rebuild()
AiLlmEndpointParamsIbm.model_rebuild()
AiLlmEndpointParamsOpenAi.model_rebuild()
Classification.model_rebuild()
CollaboratorVariable.model_rebuild()
CollaboratorVariableVariableValueItem.model_rebuild()
CompletionRuleVariable.model_rebuild()
FileBase.model_rebuild()
FileFull.model_rebuild()
FileFullClassification.model_rebuild()
FileFullExpiringEmbedLink.model_rebuild()
FileFullLock.model_rebuild()
FileFullPermissions.model_rebuild()
FileFullRepresentations.model_rebuild()
FileFullRepresentationsEntriesItem.model_rebuild()
FileFullRepresentationsEntriesItemContent.model_rebuild()
FileFullRepresentationsEntriesItemInfo.model_rebuild()
FileFullRepresentationsEntriesItemProperties.model_rebuild()
FileFullRepresentationsEntriesItemStatus.model_rebuild()
FileFullRepresentationsV0EntriesItem.model_rebuild()
FileFullRepresentationsV0EntriesItemContent.model_rebuild()
FileFullRepresentationsV0EntriesItemInfo.model_rebuild()
FileFullRepresentationsV0EntriesItemProperties.model_rebuild()
FileFullRepresentationsV0EntriesItemStatus.model_rebuild()
FileFullV1Classification.model_rebuild()
FileFullV1ExpiringEmbedLink.model_rebuild()
FileFullV1Lock.model_rebuild()
FileFullV1Permissions.model_rebuild()
FileFullV1Representations.model_rebuild()
FileFullV1RepresentationsEntriesItem.model_rebuild()
FileFullV1RepresentationsEntriesItemContent.model_rebuild()
FileFullV1RepresentationsEntriesItemInfo.model_rebuild()
FileFullV1RepresentationsEntriesItemProperties.model_rebuild()
FileFullV1RepresentationsEntriesItemStatus.model_rebuild()
FileFullV1RepresentationsV0EntriesItem.model_rebuild()
FileFullV1RepresentationsV0EntriesItemContent.model_rebuild()
FileFullV1RepresentationsV0EntriesItemInfo.model_rebuild()
FileFullV1RepresentationsV0EntriesItemProperties.model_rebuild()
FileFullV1RepresentationsV0EntriesItemStatus.model_rebuild()
FileFullV1WatermarkInfo.model_rebuild()
FileFullWatermarkInfo.model_rebuild()
FileMini.model_rebuild()
FileModel.model_rebuild()
FileModelPathCollection.model_rebuild()
FileModelSharedLink.model_rebuild()
FileModelSharedLinkPermissions.model_rebuild()
FileModelSharedLinkV0Permissions.model_rebuild()
FileModelV1PathCollection.model_rebuild()
FileModelV1SharedLink.model_rebuild()
FileModelV1SharedLinkPermissions.model_rebuild()
FileModelV1SharedLinkV0Permissions.model_rebuild()
FileRequestCopyRequest.model_rebuild()
FileRequestCopyRequestFolder.model_rebuild()
FileRequestCopyRequestV1Folder.model_rebuild()
FileRequestUpdateRequest.model_rebuild()
Files.model_rebuild()
FileVersionBase.model_rebuild()
FileVersionMini.model_rebuild()
Folder.model_rebuild()
FolderBase.model_rebuild()
FolderFolderUploadEmail.model_rebuild()
FolderMini.model_rebuild()
FolderPathCollection.model_rebuild()
FolderSharedLink.model_rebuild()
FolderSharedLinkPermissions.model_rebuild()
FolderSharedLinkV0Permissions.model_rebuild()
FolderV1FolderUploadEmail.model_rebuild()
FolderV1PathCollection.model_rebuild()
FolderV1SharedLink.model_rebuild()
FolderV1SharedLinkPermissions.model_rebuild()
FolderV1SharedLinkV0Permissions.model_rebuild()
Group.model_rebuild()
GroupBase.model_rebuild()
GroupMini.model_rebuild()
Items.model_rebuild()
ItemsOrderItem.model_rebuild()
ItemsV1OrderItem.model_rebuild()
KeywordSkillCard.model_rebuild()
KeywordSkillCardEntriesItem.model_rebuild()
KeywordSkillCardInvocation.model_rebuild()
KeywordSkillCardSkill.model_rebuild()
KeywordSkillCardSkillCardTitle.model_rebuild()
Metadata.model_rebuild()
MetadataBase.model_rebuild()
MetadataFieldFilterDateRange.model_rebuild()
MetadataFieldFilterFloatRange.model_rebuild()
MetadataFilter.model_rebuild()
MetadataFull.model_rebuild()
Outcome.model_rebuild()
PostAiAgentsBodyAskBasicImage.model_rebuild()
PostAiAgentsBodyAskBasicImageMulti.model_rebuild()
PostAiAgentsBodyAskBasicText.model_rebuild()
PostAiAgentsBodyAskBasicTextMulti.model_rebuild()
PostAiAgentsBodyAskLongText.model_rebuild()
PostAiAgentsBodyAskLongTextEmbeddings.model_rebuild()
PostAiAgentsBodyAskLongTextEmbeddingsStrategy.model_rebuild()
PostAiAgentsBodyAskLongTextMulti.model_rebuild()
PostAiAgentsBodyAskLongTextMultiEmbeddings.model_rebuild()
PostAiAgentsBodyAskLongTextMultiEmbeddingsStrategy.model_rebuild()
PostAiAgentsBodyAskSpreadsheet.model_rebuild()
PostAiAgentsBodyExtractBasicImage.model_rebuild()
PostAiAgentsBodyExtractBasicText.model_rebuild()
PostAiAgentsBodyExtractLongText.model_rebuild()
PostAiAgentsBodyExtractLongTextEmbeddings.model_rebuild()
PostAiAgentsBodyExtractLongTextEmbeddingsStrategy.model_rebuild()
PostAiAgentsBodyTextGenBasicGen.model_rebuild()
PostAiAgentsBodyTextGenBasicGenEmbeddings.model_rebuild()
PostAiAgentsBodyTextGenBasicGenEmbeddingsStrategy.model_rebuild()
PostAiExtractStructuredBodyFieldsItem.model_rebuild()
PostAiExtractStructuredBodyFieldsItemOptionsItem.model_rebuild()
PostFilesIdBodyParent.model_rebuild()
PostFoldersBodyFolderUploadEmail.model_rebuild()
PostFoldersIdBodyParent.model_rebuild()
PostIntegrationMappingsTeamsBodyBoxItem.model_rebuild()
PostIntegrationMappingsTeamsBodyPartnerItem.model_rebuild()
PostMetadataQueriesExecuteReadBodyOrderByItem.model_rebuild()
PostMetadataTemplatesSchemaBodyFieldsItem.model_rebuild()
PostMetadataTemplatesSchemaBodyFieldsItemOptionsItem.model_rebuild()
PostMetadataTemplatesSchemaBodyFieldsItemOptionsRules.model_rebuild()
PostMetadataTemplatesSchemaClassificationsBodyFieldsItem.model_rebuild()
PostMetadataTemplatesSchemaClassificationsBodyFieldsItemOptionsItem.model_rebuild()
PostMetadataTemplatesSchemaClassificationsBodyFieldsItemOptionsItemStaticConfig.model_rebuild()
PostMetadataTemplatesSchemaClassificationsBodyFieldsItemOptionsItemStaticConfigClassification.model_rebuild()
PostRetentionPolicyAssignmentsBodyFilterFieldsItem.model_rebuild()
PostShieldInformationBarriersBodyEnterprise.model_rebuild()
PostShieldInformationBarrierSegmentMembersBodyUser.model_rebuild()
PostWebLinksIdBodyParent.model_rebuild()
PostWorkflowsIdStartBodyFilesItem.model_rebuild()
PostZipDownloadsBodyItemsItem.model_rebuild()
PutFilesIdBodyCollectionsItem.model_rebuild()
PutFilesIdBodyParent.model_rebuild()
PutFilesIdBodySharedLink.model_rebuild()
PutFilesIdBodySharedLinkPermissions.model_rebuild()
PutFilesIdMetadataEnterpriseSecurityClassification6VmVochwUWoBodyItem.model_rebuild()
PutFilesIdMetadataGlobalBoxSkillsCardsBodyItem.model_rebuild()
PutFilesIdMetadataIdIdBodyItem.model_rebuild()
PutFoldersIdBodyCollectionsItem.model_rebuild()
PutFoldersIdBodyFolderUploadEmail.model_rebuild()
PutFoldersIdBodyParent.model_rebuild()
PutFoldersIdBodySharedLink.model_rebuild()
PutFoldersIdBodySharedLinkPermissions.model_rebuild()
PutFoldersIdMetadataEnterpriseSecurityClassification6VmVochwUWoBodyItem.model_rebuild()
PutFoldersIdMetadataIdIdBodyItem.model_rebuild()
PutMetadataTemplatesIdIdSchemaBodyItem.model_rebuild()
PutWebLinksIdBodyParent.model_rebuild()
ResourceScope.model_rebuild()
RoleVariable.model_rebuild()
SignRequestBase.model_rebuild()
SignRequestCreateRequest.model_rebuild()
SignRequestCreateSigner.model_rebuild()
SignRequestPrefillTag.model_rebuild()
SkillCard.model_rebuild()
StatusSkillCard.model_rebuild()
StatusSkillCardInvocation.model_rebuild()
StatusSkillCardSkill.model_rebuild()
StatusSkillCardSkillCardTitle.model_rebuild()
StatusSkillCardStatus.model_rebuild()
TimelineSkillCard.model_rebuild()
TimelineSkillCardEntriesItem.model_rebuild()
TimelineSkillCardEntriesItemAppearsItem.model_rebuild()
TimelineSkillCardInvocation.model_rebuild()
TimelineSkillCardSkill.model_rebuild()
TimelineSkillCardSkillCardTitle.model_rebuild()
TrackingCode.model_rebuild()
TranscriptSkillCard.model_rebuild()
TranscriptSkillCardEntriesItem.model_rebuild()
TranscriptSkillCardEntriesItemAppearsItem.model_rebuild()
TranscriptSkillCardInvocation.model_rebuild()
TranscriptSkillCardSkill.model_rebuild()
TranscriptSkillCardSkillCardTitle.model_rebuild()
UploadPart.model_rebuild()
UploadPartMini.model_rebuild()
User.model_rebuild()
UserBase.model_rebuild()
UserMini.model_rebuild()
UserNotificationEmail.model_rebuild()
UserV1NotificationEmail.model_rebuild()
WebLink.model_rebuild()
WebLinkBase.model_rebuild()
WebLinkMini.model_rebuild()
WebLinkPathCollection.model_rebuild()
WebLinkSharedLink.model_rebuild()
WebLinkSharedLinkPermissions.model_rebuild()
WebLinkSharedLinkV0Permissions.model_rebuild()
WebLinkV1PathCollection.model_rebuild()
WebLinkV1SharedLink.model_rebuild()
WebLinkV1SharedLinkPermissions.model_rebuild()
WebLinkV1SharedLinkV0Permissions.model_rebuild()
